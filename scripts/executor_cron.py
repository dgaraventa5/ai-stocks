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


def _reconcile_via_transport(transport, notifier) -> None:
    """Post-execution recon using READ methods only (D). Failure here is
    flagged, never fatal — the orders are already safely receipted."""
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


def main() -> int:
    from execute_ticket import RobinhoodTransport, _load_roster, run as exec_run
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    transport = RobinhoodTransport()

    def runner(ticket_path):
        return exec_run(ticket_path, live_dir=LIVE_DIR, roster=_load_roster(),
                        transport=transport, confirm=True, now=now)

    def receipt_count():
        return len(list((LIVE_DIR / 'receipts').glob('receipt-*.json')))

    before = receipt_count()
    rc = cron_run(LIVE_DIR, runner, macos_notify, now)
    if rc == 0 and receipt_count() > before:      # something actually sent
        _reconcile_via_transport(transport, macos_notify)
    return rc


if __name__ == '__main__':
    sys.exit(main())
