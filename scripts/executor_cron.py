"""Phase-3 scheduled executor — §C5 of the agentic-execution spec (2026-08-09).

Dom-activated (launchctl), never activated by Claude. Safety posture under
scheduling (per C5: with the human gone, kill switch + caps are the only
control left):
  - notification on EVERY execution attempt outcome
  - auto-halt on ANY validation failure (not just investigate-later flags)
  - full-turnover tickets are NEVER auto-executed (no --allow-full-turnover
    here, deliberately — a full redeploy is a sit-up-and-look event)
  - expired / already-receipted tickets are skipped silently
  - after a successful send, reconcile immediately via the transport's READ
    methods and notify on any anomaly

Config: launchd/com.dom.aistocks.executor.plist (weekdays 06:35 PT).
Activation + rollback: docs/superpowers/specs/2026-08-09-phase3-activation.md.
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
LIVE_DIR = _REPO_ROOT / 'tracking' / 'live'


def _parse_iso(ts: str) -> dt.datetime:
    return dt.datetime.fromisoformat(ts.replace('Z', '+00:00'))


def pick_ticket(live_dir: Path, now: str) -> Path | None:
    """Newest ticket that is neither expired nor already executed."""
    live_dir = Path(live_dir)
    candidates = []
    for p in sorted((live_dir / 'tickets').glob('ticket-*.json')):
        tk = json.loads(p.read_text())
        receipt = live_dir / 'receipts' / f"receipt-{tk['ticket_id']}.json"
        if receipt.exists():
            continue
        if _parse_iso(now) > _parse_iso(tk['expires_at']):
            continue
        candidates.append((p.stat().st_mtime, p))
    return max(candidates)[1] if candidates else None


def macos_notify(msg: str) -> None:
    print(msg)
    try:
        subprocess.run(
            ['osascript', '-e',
             f'display notification {json.dumps(msg)} '
             f'with title "AI-stocks executor" sound name "Submarine"'],
            timeout=10, capture_output=True)
    except Exception:
        pass   # notification is best-effort; the log line above always lands


def cron_run(live_dir: Path, runner, notifier, now: str) -> int:
    """One scheduled pass. runner(ticket_path) -> execute_ticket.run result."""
    live_dir = Path(live_dir)
    ticket = pick_ticket(live_dir, now)
    if ticket is None:
        return 0                                  # quiet no-op (normal case)
    try:
        res = runner(ticket)
    except (SystemExit, Exception) as e:          # token/network — nothing sent
        notifier(f'executor cron: transport error, nothing sent — {e} '
                 f'(check token: ROBINHOOD_MCP_TOKEN / Claude Code OAuth)')
        return 1
    if res['failures']:
        # C5: any validation failure under scheduling raises the kill switch.
        halt = live_dir / 'trading-halt.flag'
        halt.write_text(
            f'{now} auto-halt (scheduled executor, C5): ticket {ticket.name} '
            f'refused:\n' + '\n'.join(f'- {f}' for f in res['failures']) + '\n')
        notifier(f'executor cron: HALT raised — ticket {ticket.name} refused '
                 f'({len(res["failures"])} gate failures). Clear '
                 f'trading-halt.flag deliberately after investigating.')
        return 1
    if res['sent']:
        notifier(f'executor cron: ticket {ticket.name} executed — receipt '
                 f'written. Reconciling.')
    return 0


def wait_for_network(host: str = 'agent.robinhood.com', attempts: int = 5,
                     delay: float = 3.0, resolver=None, sleeper=None) -> bool:
    """True once `host` resolves, retrying between attempts.

    launchd fires this job during DarkWake (a display-off maintenance wake).
    On battery, Power Nap restricts network access for user processes, so DNS
    fails instantly (Errno 8) and the machine returns to sleep ~2s later —
    2026-08-12..14, where every scheduled recon AND every benchmark fetch
    failed while attended runs worked fine. Retrying rides out a wake race;
    a genuinely restricted DarkWake still fails, but now says so plainly.
    """
    if resolver is None:
        import socket
        resolver = socket.gethostbyname
    if sleeper is None:
        import time
        sleeper = time.sleep
    for i in range(attempts):
        try:
            resolver(host)
            return True
        except OSError:
            if i < attempts - 1:
                sleeper(delay)
    return False


def _reconcile_via_transport(transport, notifier) -> None:
    """Post-execution recon using READ methods only (D). Failure here is
    flagged, never fatal — the orders are already safely receipted."""
    if not wait_for_network():
        notifier('recon skipped: network unavailable (likely a DarkWake '
                 'maintenance wake on battery — see plist caffeinate note) — '
                 'run reconcile_account.py in an attended session')
        return
    try:
        import reconcile_account as ra
        positions = transport.positions()
        prices = transport.quotes(sorted(positions)) if positions else {}
        pf = transport.portfolio()
        state = {
            'as_of': dt.date.today().isoformat(),
            'cash': pf['cash'], 'equity': pf['equity'],
            'positions': {t: {'shares': sh, 'price': prices.get(t, 0.0)}
                          for t, sh in positions.items()},
            'orders': transport.orders(),
        }
        res = ra.run(state, live_dir=LIVE_DIR,
                     target_weights=ra._targets_from_workbook())
        if res['halted'] or res['anomalies']:
            notifier(f'recon after execution: HALTED — '
                     f'{"; ".join(res["anomalies"]) or "pre-existing halt"}')
    except Exception as e:
        notifier(f'recon after execution FAILED ({e}) — run '
                 f'reconcile_account.py in an attended session')


# ---------------------------------------------------------------- heartbeat

def heartbeat_stamp(live_dir: Path, job: str, today: str | None = None) -> None:
    """Record that `job` completed today. Local-only (inside the privacy
    boundary): autonomy needs a liveness record, not a committed artifact."""
    p = Path(live_dir) / 'heartbeat.json'
    try:
        hb = json.loads(p.read_text())
    except (OSError, ValueError):
        hb = {}
    hb[job] = today or dt.date.today().isoformat()
    p.write_text(json.dumps(hb, indent=2) + '\n')


def stale_jobs(live_dir: Path, jobs: list[str], today: str | None = None,
               max_age_days: int = 3) -> list[str]:
    """Jobs that never ran or haven't run within max_age_days — the weekly
    scan surfaces these so silent failures become visible flags."""
    p = Path(live_dir) / 'heartbeat.json'
    try:
        hb = json.loads(p.read_text())
    except (OSError, ValueError):
        hb = {}
    ref = dt.date.fromisoformat(today or dt.date.today().isoformat())
    out = []
    for job in jobs:
        last = hb.get(job)
        if last is None or (ref - dt.date.fromisoformat(last)).days > max_age_days:
            out.append(job)
    return out


# ------------------------------------------------------------- daily runner

def ticket_gen_if_stale(live_dir: Path, last_event: dict, gen) -> bool:
    """Generate a ticket when the newest model event isn't covered by any
    existing ticket (closes the cloud-fired-event gap: cloud sessions log
    events but can't see tracking/live/, so ticket generation happens here,
    on the machine that has the snapshots)."""
    live_dir = Path(live_dir)
    newest = ''
    for p in (live_dir / 'tickets').glob('ticket-*.json'):
        basis = json.loads(p.read_text()).get('basis_event', {})
        newest = max(newest, basis.get('date', ''))
    if last_event.get('date', '') > newest:
        gen(last_event)
        return True
    return False


def daily_run(live_dir: Path, steps: list[tuple], notifier,
              today: str | None = None) -> int:
    """Run named steps in order; a failure notifies and moves on (isolated),
    a success stamps the heartbeat. Exit 1 if anything failed."""
    rc = 0
    for name, fn in steps:
        try:
            fn()
            heartbeat_stamp(live_dir, name, today=today)
        except (SystemExit, Exception) as e:
            notifier(f'pipeline step {name} FAILED: {e}')
            rc = 1
    return rc


SERIES_FILE = 'tracking/performance-series.json'


def _series_step(run=None, notifier=None) -> None:
    """Rebuild the performance series and push it if it changed — from this
    machine (residential IP, real git creds), replacing dependence on the
    flaky GH cron (which stays as an idempotent backstop).

    Commits ONLY on main. This runs on a schedule, so it lands on whatever
    branch happens to be checked out: on 2026-08-17 it committed the series
    onto an in-flight feature branch (bare `git push` pushes the current
    branch), which then conflicted with main's copy of the same day and
    carried different values, because the series is recomputed from the
    model's current composition. Off main, rebuild and flag — the next run on
    main, or the GH backstop, publishes it.
    """
    run = run or subprocess.run
    notifier = notifier or print
    run([sys.executable, 'scripts/track_performance.py', '--series-only'],
        cwd=_REPO_ROOT, check=True, timeout=600)
    if run(['git', 'diff', '--quiet', '--', SERIES_FILE],
           cwd=_REPO_ROOT).returncode == 0:
        return                               # unchanged (holiday/weekend)
    branch = (run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=_REPO_ROOT,
                  capture_output=True, text=True).stdout or '').strip()
    if branch != 'main':
        notifier(f'series rebuilt but NOT committed: on branch {branch!r}, '
                 f'not main — commit it from main (or let the GH backstop)')
        return
    run(['git', 'add', SERIES_FILE], cwd=_REPO_ROOT, check=True)
    # `--` scopes the commit to this path: a bare `git commit` would also
    # sweep in whatever else happened to be staged in the working tree.
    run(['git', 'commit', '-m',
         f'chore(data): daily performance series '
         f'{dt.date.today().isoformat()} (local pipeline runner)',
         '--', SERIES_FILE], cwd=_REPO_ROOT, check=True)
    run(['git', 'push', 'origin', 'main'], cwd=_REPO_ROOT, check=True,
        timeout=120)


def main(mode: str = 'auto') -> int:
    from execute_ticket import RobinhoodTransport, _load_roster, run as exec_run
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    if mode == 'auto':   # launchd fires 06:35 PT (open) and 13:35 PT (close)
        mode = 'open' if dt.datetime.now().hour < 12 else 'close'
    transport = RobinhoodTransport()

    def execute_step():
        def runner(ticket_path):
            return exec_run(ticket_path, live_dir=LIVE_DIR,
                            roster=_load_roster(), transport=transport,
                            confirm=True, now=now)
        if cron_run(LIVE_DIR, runner, macos_notify, now) != 0:
            raise RuntimeError('execution refused or transport error (see log)')

    def ticket_step():
        from generate_trade_ticket import generate, _targets_weights
        from portfolio_model import load_cfg
        last_ev = load_cfg()['events'][-1]
        event = {'date': last_ev['date'],
                 'kind': last_ev.get('kind', 'membership'),
                 'reason': last_ev.get('reason', '')}
        if ticket_gen_if_stale(
                LIVE_DIR, event,
                gen=lambda ev: generate(_targets_weights()[0], ev)):
            macos_notify(f'pipeline: generated ticket for uncovered model '
                         f'event {event["date"]}-{event["kind"]}')

    def recon_step():
        _reconcile_via_transport(transport, macos_notify)

    if mode == 'open':
        steps = [('ticket_gen', ticket_step), ('execute', execute_step),
                 ('recon', recon_step)]
    else:
        steps = [('series', _series_step), ('recon', recon_step)]
    return daily_run(LIVE_DIR, steps, macos_notify)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Daily local pipeline runner (§C5)')
    ap.add_argument('--mode', choices=['auto', 'open', 'close'], default='auto')
    ap.add_argument('--heartbeat-check', action='store_true',
                    help='print stale pipeline jobs and exit (weekly-scan step)')
    args = ap.parse_args()
    if args.heartbeat_check:
        stale = stale_jobs(LIVE_DIR, ['series', 'recon', 'execute',
                                      'ticket_gen'])
        if stale:
            print(f'STALE pipeline jobs (no successful run in >3d): '
                  f'{", ".join(stale)}')
            sys.exit(1)
        print('all pipeline heartbeats fresh ✓')
        sys.exit(0)
    sys.exit(main(args.mode))
