"""Account reconciliation & monitoring — §D of the agentic-execution spec.

Read-only, deterministic, stdlib only. Account state arrives as an explicit
JSON payload (Claude pulls it with MCP READ tools in attended sessions —
O1 answered NO 2026-08-09, so there is no headless fetch path; this script
never talks to the network and never places orders).

Outputs:
  tracking/live/recon/snapshot-{date}.json   full fidelity (GITIGNORED, §E)
  tracking/live/trading-halt.flag            created on anomalies; never sells
  tracking/live-status.json                  COMMITTED — sanitized: booleans,
                                             dates, counts, tickers only
  tracking/live-vs-model.json                COMMITTED — relative % only

Usage (attended session):
  python3 scripts/reconcile_account.py --account-json state.json
  python3 scripts/reconcile_account.py --account-json state.json \
      --external-flow 500.00   # declare a deposit (withdrawal: negative)

External cash flows (deposits/withdrawals) are DECLARED, never inferred: an
undeclared equity jump is indistinguishable from an executor bug, so it halts
(D3). A declared flow goes to the append-only ledger
tracking/live/recon/flows.jsonl (gitignored, §E) where every later run — the
attended session and the launchd cron alike — can explain the same move, and
the live-vs-model baseline is divisor-adjusted so a deposit doesn't print as
performance.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
LIVE_DIR = _REPO_ROOT / 'tracking' / 'live'
STATUS_PATH = _REPO_ROOT / 'tracking' / 'live-status.json'
LVM_PATH = _REPO_ROOT / 'tracking' / 'live-vs-model.json'
SERIES_PATH = _REPO_ROOT / 'tracking' / 'performance-series.json'

DRIFT_ALERT = 0.05        # relative drift threshold (D2)
EQUITY_TOL = 0.03         # unexplained-equity tolerance (D3)
OPEN_STATES = ('queued', 'confirmed', 'unconfirmed', 'partially_filled')
DEAD_STATES = ('cancelled', 'expired', 'rejected', 'failed', 'voided')


# §E sanitizer gates — called before EVERY committed write; fail closed on any
# unknown field. Same standing as the site privacy gate: never weaken.
_STATUS_SCHEMA = {'as_of': str, 'halted': bool, 'positions': int,
                  'open_orders': int, 'drift_flags': list,
                  'regen_needed': list, 'anomaly_count': int,
                  'cap_exceeded': bool, 'unrepaired_legs': list}
_NUM = (float, int, type(None))
_LVM_ENTRY_SCHEMA = {'date': str, 'live_pct': _NUM, 'model_pct': _NUM,
                     'shortfall_pct': _NUM,
                     # second line, anchored at first full deployment (§4)
                     'live_since_deploy_pct': _NUM,
                     'model_since_deploy_pct': _NUM,
                     'shortfall_since_deploy_pct': _NUM}

# A snapshot counts as "fully deployed" at/above this invested fraction. The
# anchor is the FIRST snapshot to reach it, and is then frozen forever.
DEPLOYED_MIN = 0.95


def assert_sanitized_status(status: dict) -> None:
    for key, val in status.items():
        if key not in _STATUS_SCHEMA:
            raise ValueError(f'live-status field {key!r} not in the sanitized '
                             f'allowlist (§E) — refusing to commit it')
        if not isinstance(val, _STATUS_SCHEMA[key]):
            raise ValueError(f'live-status field {key!r} has type '
                             f'{type(val).__name__}, expected '
                             f'{_STATUS_SCHEMA[key]}')
    for lst in (status.get('drift_flags', []), status.get('regen_needed', []),
                status.get('unrepaired_legs', [])):
        for item in lst:
            if not isinstance(item, str):
                raise ValueError(f'{item!r}: ticker lists may contain only '
                                 f'ticker strings (§E)')


def assert_sanitized_lvm(doc: dict) -> None:
    allowed = {'baseline_date', 'series', 'deployment_date'}
    if not {'baseline_date', 'series'} <= set(doc) or not set(doc) <= allowed:
        raise ValueError(f'live-vs-model keys {sorted(doc)} outside '
                         f'{sorted(allowed)} (§E)')
    if not isinstance(doc.get('deployment_date', ''), str):
        raise ValueError('deployment_date must be a date string (§E)')
    for entry in doc['series']:
        for key, val in entry.items():
            if key not in _LVM_ENTRY_SCHEMA:
                raise ValueError(f'live-vs-model field {key!r} not in the '
                                 f'relative-percentages allowlist (§E)')
            if not isinstance(val, _LVM_ENTRY_SCHEMA[key]):
                raise ValueError(f'live-vs-model field {key!r}: bad type')


# §D external-flow ledger — Dom-declared deposits/withdrawals. Append-only,
# gitignored (real dollars). Declarations are idempotent per (date, amount) so
# the attended run and the cron's same-day recon can't double-count one flow.

def _flows_path(live_dir: Path) -> Path:
    return Path(live_dir) / 'recon' / 'flows.jsonl'


def read_flows(live_dir: Path) -> list[dict]:
    path = _flows_path(live_dir)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines()
            if line.strip()]


def declare_flow(live_dir: Path, date: str, amount: float) -> None:
    """Record an external cash flow (deposit > 0, withdrawal < 0), dated to
    the recon that first sees it. No-op on zero or on an exact duplicate."""
    if not amount:
        return
    entry = {'date': date, 'amount': round(float(amount), 2)}
    if entry in read_flows(live_dir):
        print(f'external flow already declared for {date} — ledger unchanged')
        return
    path = _flows_path(live_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as fh:
        fh.write(json.dumps(entry) + '\n')
    print(f'external flow declared: {amount:+.2f} on {date}')


def cap_exceeded(live_dir: Path, equity: float) -> bool:
    """True when account equity has outgrown the executor's ACCOUNT_CAP.

    The cap is the ceiling on how much money this system is authorised to
    manage. A deposit can push equity past it, after which execute_ticket
    refuses EVERY ticket — but nothing announced that: the halt flag and the
    anomaly check both stayed quiet, and model events are rare, so on
    2026-08-17 the condition only surfaced days later when a rebalance
    happened to be attempted. Surfacing it at recon closes that gap.

    FLAG, never halt: the executor already fails closed on its own, so a halt
    would add no safety while blocking unrelated work and requiring a manual
    clear. Missing config means the cap is unknown — claim nothing (rule 3).
    """
    path = Path(live_dir) / 'executor-config.json'
    if not path.exists():
        return False
    try:
        cap = float(json.loads(path.read_text())['ACCOUNT_CAP'])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return False
    return float(equity) > cap


def guard_flow_is_delta(flow: float, cash: float, prior: dict | None) -> None:
    """Refuse a declared flow that looks like a BALANCE rather than a DELTA.

    --external-flow wants the amount that moved. A resulting cash balance
    passed by mistake is also a float of dollars, so nothing catches it: on
    2026-08-14 a deposit was declared as the post-deposit balance, over-stating
    the flow by the pre-existing cash. That over-declaration then inflated the
    baseline divisor and printed a large phantom negative live return. The
    fingerprint is the declared deposit equalling current cash while the
    account already held cash. Prior cash ~0 is the honest case (balance ==
    delta) — no guard there.
    """
    if flow <= 0 or not prior:
        return
    prior_cash = float(prior.get('cash', 0.0))
    if prior_cash < 0.01 or abs(flow - float(cash)) >= 0.01:
        return
    raise ValueError(
        f'declared flow {flow:,.2f} equals the resulting cash balance — '
        f'--external-flow takes the amount that MOVED, not the resulting '
        f'balance. The account already held {prior_cash:,.2f} in cash before '
        f'this recon; did you mean {float(cash) - prior_cash:,.2f}? '
        f'(rule 3: flagged, not guessed)')


def flows_between(live_dir: Path, after: str, through: str) -> float:
    """Sum of declared flows dated in (after, through] — the window between
    the prior snapshot and the current recon."""
    return sum(f['amount'] for f in read_flows(live_dir)
               if after < f['date'] <= through)


def _receipts(live_dir: Path) -> list[dict]:
    rdir = live_dir / 'receipts'
    if not rdir.is_dir():
        return []
    return [json.loads(p.read_text()) for p in sorted(rdir.glob('receipt-*.json'))]


def verify_fills(receipts: list[dict], orders: list[dict]):
    """Match receipt orders to live order states by order_id (D1)."""
    by_id = {o.get('order_id'): o for o in orders}
    fills: dict[str, dict[str, str]] = {}
    regen: list[str] = []
    for r in receipts:
        states: dict[str, str] = {}
        for o in r.get('orders', []):
            live = by_id.get(o.get('order_id'))
            state = (live or {}).get('state') or o.get('state', 'unknown')
            states[o['ticker']] = state
            if state in DEAD_STATES:
                regen.append(o['ticker'])   # unfilled + dead → regenerate
        fills[r['ticket_id']] = states
    return fills, sorted(set(regen))


def drift_check(state: dict, target_weights: dict[str, float],
                threshold: float = DRIFT_ALERT) -> list[dict]:
    """Relative per-name drift of actual vs target weight (D2). Flags only —
    drift never halts; it feeds B2's delta-from-actuals rule."""
    equity = state['equity']
    out = []
    for t, tw in sorted(target_weights.items()):
        if not tw or not equity:
            continue
        pos = state['positions'].get(t, {})
        actual = pos.get('shares', 0.0) * pos.get('price', 0.0) / equity
        rel = abs(actual - tw) / tw
        if rel > threshold:
            out.append({'ticker': t, 'rel_drift_pct': round(rel * 100, 1)})
    return out


def unrepaired_legs(receipts: list[dict], drift: list[dict]) -> list[str]:
    """Tickers whose most recent order never reached the broker AND which are
    still outside their drift band — a trade that did not happen, not price
    drift (added 2026-09-08, spec §3b).

    Why this exists: on 2026-08-17 VRT's leg was rejected at transmit ("You
    can only purchase 0 shares") while the other 14 legs went through. The
    receipt recorded it and drift flagged it on every run for three weeks, but
    nothing joined the two facts, so a trade that never happened was
    indistinguishable from ordinary price drift. This is the join.

    Deliberately NOT an anomaly: every entry in detect_anomalies raises the
    kill switch, and halting would block unrelated correct trades to fix a
    position that is merely the wrong size. Loud, never blocking.

    The LAST receipt mentioning a ticker wins — a later successful ticket
    repairs an earlier failure, and this must go quiet when it does.
    """
    latest: dict[str, str] = {}
    for r in receipts:                     # _receipts() returns sorted order
        for o in r.get('orders', []):
            if o.get('ticker'):
                latest[o['ticker']] = o.get('state', 'unknown')
    drifting = {d['ticker'] for d in drift}
    return sorted(t for t, st in latest.items()
                  if st == 'transmit_error' and t in drifting)


def _prior_snapshot(live_dir: Path, as_of: str) -> dict | None:
    snaps = sorted((live_dir / 'recon').glob('snapshot-*.json'))
    prior = [p for p in snaps if p.stem.split('snapshot-')[1] < as_of]
    return json.loads(prior[-1].read_text()) if prior else None


def detect_anomalies(state: dict, target_weights: dict, receipts: list[dict],
                     prior: dict | None, declared_flow: float = 0.0) -> list[str]:
    """D3 halt conditions. Any entry here raises the kill switch (which stops
    future EXECUTIONS only — it never sells anything). declared_flow: net
    Dom-declared external cash flow since the prior snapshot (ledger above) —
    an EXPLAINED equity move; undeclared moves still halt."""
    anomalies = []
    known = set(target_weights) | {o['ticker'] for r in receipts
                                   for o in r.get('orders', [])}
    for t in sorted(state['positions']):
        if t not in known:
            anomalies.append(
                f'position {t} has unknown provenance (not in roster, not in '
                f'any receipt) — possible executor bug or account misuse')
    if state['cash'] < 0:
        anomalies.append('cash negative')
    if prior is not None:
        # Expected equity: prior shares marked at today's prices + prior cash.
        # Composition changes (fills since prior) make this ill-posed — skip
        # honestly rather than false-alarm (rule 3).
        filled_since = any(o.get('state') == 'filled'
                           for o in state.get('orders', []))
        if not filled_since:
            expected = prior['cash'] + declared_flow
            for t, pos in prior['positions'].items():
                px = state['positions'].get(t, {}).get('price', pos.get('price'))
                expected += pos['shares'] * px
            if expected > 0:
                gap = abs(state['equity'] - expected) / expected
                if gap > EQUITY_TOL:
                    anomalies.append(
                        f'equity move unexplained by market moves of held '
                        f'names ({gap:.1%} vs expected) — if this is a '
                        f'deposit/withdrawal, declare it with --external-flow')
    return anomalies


def _invested_frac(snap: dict) -> float:
    eq = snap.get('equity') or 0.0
    if not eq:
        return 0.0
    return sum(p['shares'] * p['price']
               for p in snap.get('positions', {}).values()) / eq


def deployment_baseline(live_dir: Path, state: dict) -> dict | None:
    """The second anchor (§4): the FIRST snapshot at/above DEPLOYED_MIN
    invested. Written once and never revised.

    Why a second anchor at all: the since-inception line was struck on
    2026-08-09 with the account 100% cash while the model was already fully
    invested, and a deposit on 08-14 left it 27% invested for three days. That
    cost -3.69pts of a -4.53pt shortfall — real, one-time, and permanent in a
    cumulative metric, which made the ongoing tracking signal unreadable. The
    inception line is NEVER restated (that would discard experienced cost);
    this line runs beside it, and the gap between the two IS the deployment
    cost, stated rather than hidden.

    Immutable on purpose, for the reason rule 17 freezes created_date: an
    adjustable anchor can be nudged until the tracking looks good.
    """
    path = Path(live_dir) / 'recon' / 'deployment-baseline.json'
    if path.exists():
        return json.loads(path.read_text())
    snaps = sorted((Path(live_dir) / 'recon').glob('snapshot-*.json'))
    candidates = [json.loads(p.read_text()) for p in snaps]
    if _invested_frac(state) >= DEPLOYED_MIN:
        candidates.append(state)
    for snap in sorted(candidates, key=lambda s: s.get('as_of', '')):
        if _invested_frac(snap) >= DEPLOYED_MIN:
            base = {'date': snap['as_of'], 'equity': snap['equity'],
                    'applied_flows': []}
            path.write_text(json.dumps(base) + '\n')
            return base
    return None


def live_vs_model(state: dict, live_dir: Path, model_series_path: Path,
                  lvm_path: Path) -> None:
    """Implementation-shortfall line (D5): cumulative live vs model return
    since the live baseline. COMMITTED — relative percentages only."""
    base_path = live_dir / 'recon' / 'baseline.json'
    flows = read_flows(live_dir)
    if not base_path.exists():
        # Flows dated at/before creation are embedded in the creation equity.
        base_path.write_text(json.dumps(
            {'date': state['as_of'], 'equity': state['equity'],
             'applied_flows': [f for f in flows
                               if f['date'] <= state['as_of']]}) + '\n')
    base = json.loads(base_path.read_text())
    base.setdefault('applied_flows', [])

    # Divisor adjustment (index-style): a declared external flow F at current
    # equity E scales the baseline by E/(E−F), so live_pct is unchanged by the
    # flow itself and later market moves compound correctly. Applied exactly
    # once per ledger entry (applied_flows), whichever run sees it first.
    pending = [f for f in flows
               if f['date'] > base['date'] and f not in base['applied_flows']]
    if pending:
        total = sum(f['amount'] for f in pending)
        if state['equity'] - total > 0:
            base['equity'] = round(
                base['equity'] * state['equity'] / (state['equity'] - total), 4)
        else:
            print(f'FLAG: declared flow {total:+.2f} >= current equity — '
                  f'baseline NOT adjusted; live-vs-model needs a manual '
                  f'baseline reset (rule 3: flagged, not guessed)')
        base['applied_flows'].extend(pending)
        base_path.write_text(json.dumps(base) + '\n')
    live_pct = round((state['equity'] / base['equity'] - 1) * 100, 2)

    model_pct = None
    try:
        series = json.loads(Path(model_series_path).read_text())
        idx = {d: v for d, v in zip(series['dates'], series['model'])}

        def at_or_before(day):
            past = [d for d in series['dates'] if d <= day]
            return idx[past[-1]] if past else None
        m0, m1 = at_or_before(base['date']), at_or_before(state['as_of'])
        if m0 and m1:
            model_pct = round((m1 / m0 - 1) * 100, 2)
    except (OSError, ValueError, KeyError):
        pass   # model series unavailable → model_pct stays None (flagged below)

    entry = {'date': state['as_of'], 'live_pct': live_pct,
             'model_pct': model_pct,
             'shortfall_pct': (round(live_pct - model_pct, 2)
                               if model_pct is not None else None)}

    # Second line, anchored at first full deployment (§4). Additive: the
    # inception fields above are computed and written exactly as before.
    deploy = deployment_baseline(live_dir, state)
    if deploy and state['as_of'] >= deploy['date']:
        d_pending = [f for f in flows if f['date'] > deploy['date']
                     and f not in deploy['applied_flows']]
        if d_pending:
            total = sum(f['amount'] for f in d_pending)
            if state['equity'] - total > 0:
                deploy['equity'] = round(
                    deploy['equity'] * state['equity']
                    / (state['equity'] - total), 4)
                deploy['applied_flows'].extend(d_pending)
                (Path(live_dir) / 'recon' / 'deployment-baseline.json'
                 ).write_text(json.dumps(deploy) + '\n')
            else:
                print('FLAG: declared flow >= equity — deployment baseline '
                      'NOT adjusted (rule 3: flagged, not guessed)')
        d_live = round((state['equity'] / deploy['equity'] - 1) * 100, 2)
        d_model = None
        if model_pct is not None:
            m_d = at_or_before(deploy['date'])
            if m_d and m1:
                d_model = round((m1 / m_d - 1) * 100, 2)
        entry.update({
            'live_since_deploy_pct': d_live,
            'model_since_deploy_pct': d_model,
            'shortfall_since_deploy_pct': (round(d_live - d_model, 2)
                                           if d_model is not None else None)})

    try:
        doc = json.loads(Path(lvm_path).read_text())
    except (OSError, ValueError):
        doc = {'baseline_date': base['date'], 'series': []}
    if deploy:
        doc['deployment_date'] = deploy['date']
    doc['series'] = [e for e in doc['series'] if e['date'] != entry['date']]
    doc['series'].append(entry)
    doc['series'].sort(key=lambda e: e['date'])
    assert_sanitized_lvm(doc)                    # §E gate before committed write
    Path(lvm_path).write_text(json.dumps(doc, indent=2) + '\n')


def run(state: dict, *, live_dir: Path, target_weights: dict[str, float],
        model_series_path: Path = SERIES_PATH,
        status_path: Path = STATUS_PATH, lvm_path: Path = LVM_PATH,
        external_flow: float = 0.0) -> dict:
    live_dir = Path(live_dir)
    (live_dir / 'recon').mkdir(parents=True, exist_ok=True)
    prior = _prior_snapshot(live_dir, state['as_of'])
    if external_flow:
        guard_flow_is_delta(external_flow, state['cash'], prior)
        declare_flow(live_dir, state['as_of'], external_flow)
    receipts = _receipts(live_dir)
    declared = flows_between(live_dir, prior['as_of'] if prior else '',
                             state['as_of'])

    fills, regen = verify_fills(receipts, state.get('orders', []))
    drift = drift_check(state, target_weights)
    unrepaired = unrepaired_legs(receipts, drift)
    anomalies = detect_anomalies(state, target_weights, receipts, prior,
                                 declared_flow=declared)

    halt_path = live_dir / 'trading-halt.flag'
    if anomalies:
        halt_path.write_text(
            f'{state["as_of"]} auto-halt (reconcile_account.py):\n'
            + '\n'.join(f'- {a}' for a in anomalies) + '\n')
        print(f'TRADING HALT raised: {"; ".join(anomalies)}')
    halted = halt_path.exists()

    # Full-fidelity snapshot — gitignored (§E). This is the actuals source for
    # the next ticket's share deltas (B2).
    snap_path = live_dir / 'recon' / f'snapshot-{state["as_of"]}.json'
    snap_path.write_text(json.dumps(
        {**state, 'fills': fills, 'anomalies': anomalies}, indent=2) + '\n')

    live_vs_model(state, live_dir, model_series_path, lvm_path)

    # Committed status — SANITIZED: booleans, dates, counts, tickers, relative
    # percentages. No dollars, no share counts, no order ids (§E).
    open_orders = sum(1 for o in state.get('orders', [])
                      if o.get('state') in OPEN_STATES)
    over_cap = cap_exceeded(live_dir, state['equity'])
    status = {
        'as_of': state['as_of'],
        'halted': halted,
        'positions': len(state['positions']),
        'open_orders': open_orders,
        'drift_flags': [d['ticker'] for d in drift],
        'regen_needed': regen,
        'anomaly_count': len(anomalies),
        'cap_exceeded': over_cap,
        'unrepaired_legs': unrepaired,
    }
    assert_sanitized_status(status)              # §E gate before committed write
    Path(status_path).write_text(json.dumps(status, indent=2) + '\n')

    for d in drift:
        print(f'drift flag: {d["ticker"]} {d["rel_drift_pct"]}% from target '
              f'(> {DRIFT_ALERT:.0%} relative)')
    for t in regen:
        print(f'unfilled order dead: {t} — regenerate on next model event '
              f'or --regen-unfilled')
    for t in unrepaired:
        print(f'UNREPAIRED LEG: {t} never reached the broker on its last '
              f'ticket and is still outside its drift band — this is a trade '
              f'that did not happen, not price drift. Regenerate a ticket for '
              f'it; do NOT re-run the original (spec §3b).')
    if over_cap:
        print('[FLAG] account equity exceeds ACCOUNT_CAP — execute_ticket will '
              'REFUSE every ticket until the cap is raised in '
              'tracking/live/executor-config.json (deliberate edit, §C2)')
    print(f'recon {state["as_of"]}: {len(state["positions"])} positions, '
          f'{open_orders} open orders, halted={halted}')
    return {'halted': halted, 'drift': drift, 'fills': fills,
            'regen_needed': regen, 'anomalies': anomalies,
            'unrepaired_legs': unrepaired,
            'cap_exceeded': over_cap, 'snapshot': snap_path}


def _targets_from_workbook() -> dict[str, float]:
    from openpyxl import load_workbook   # lazy (minimal-CI convention)
    wb = load_workbook(_REPO_ROOT / '00-master' / 'portfolio.xlsx')
    ws = wb['Targets']
    hdr = [c.value for c in ws[2]]
    col = {name: i for i, name in enumerate(hdr)}
    out = {}
    for row in ws.iter_rows(min_row=3, values_only=True):
        if row[0] and row[0] != 'TOTAL' and row[col['Include?']] == 'Y':
            out[row[0]] = (row[col['Target %']] or 0) / 100.0
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Reconcile live account state against the model')
    ap.add_argument('--account-json', required=True,
                    help='account state JSON pulled via MCP READ tools '
                         '(attended session — O1: no headless OAuth)')
    ap.add_argument('--external-flow', type=float, default=0.0,
                    metavar='AMOUNT',
                    help='declare an external cash flow since the prior '
                         'snapshot (deposit > 0, withdrawal < 0): explains '
                         'the equity move to the D3 anomaly check and '
                         'divisor-adjusts the live-vs-model baseline')
    args = ap.parse_args()
    payload = json.loads(Path(args.account_json).read_text())
    run(payload, live_dir=LIVE_DIR, target_weights=_targets_from_workbook(),
        external_flow=args.external_flow)
