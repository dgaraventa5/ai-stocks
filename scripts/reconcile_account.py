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
                  'regen_needed': list, 'anomaly_count': int}
_LVM_ENTRY_SCHEMA = {'date': str, 'live_pct': (float, int, type(None)),
                     'model_pct': (float, int, type(None)),
                     'shortfall_pct': (float, int, type(None))}


def assert_sanitized_status(status: dict) -> None:
    for key, val in status.items():
        if key not in _STATUS_SCHEMA:
            raise ValueError(f'live-status field {key!r} not in the sanitized '
                             f'allowlist (§E) — refusing to commit it')
        if not isinstance(val, _STATUS_SCHEMA[key]):
            raise ValueError(f'live-status field {key!r} has type '
                             f'{type(val).__name__}, expected '
                             f'{_STATUS_SCHEMA[key]}')
    for lst in (status.get('drift_flags', []), status.get('regen_needed', [])):
        for item in lst:
            if not isinstance(item, str):
                raise ValueError(f'{item!r}: ticker lists may contain only '
                                 f'ticker strings (§E)')


def assert_sanitized_lvm(doc: dict) -> None:
    if set(doc) != {'baseline_date', 'series'}:
        raise ValueError(f'live-vs-model keys {sorted(doc)} != '
                         f"['baseline_date', 'series'] (§E)")
    for entry in doc['series']:
        for key, val in entry.items():
            if key not in _LVM_ENTRY_SCHEMA:
                raise ValueError(f'live-vs-model field {key!r} not in the '
                                 f'relative-percentages allowlist (§E)')
            if not isinstance(val, _LVM_ENTRY_SCHEMA[key]):
                raise ValueError(f'live-vs-model field {key!r}: bad type')


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


def _prior_snapshot(live_dir: Path, as_of: str) -> dict | None:
    snaps = sorted((live_dir / 'recon').glob('snapshot-*.json'))
    prior = [p for p in snaps if p.stem.split('snapshot-')[1] < as_of]
    return json.loads(prior[-1].read_text()) if prior else None


def detect_anomalies(state: dict, target_weights: dict, receipts: list[dict],
                     prior: dict | None) -> list[str]:
    """D3 halt conditions. Any entry here raises the kill switch (which stops
    future EXECUTIONS only — it never sells anything)."""
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
            expected = prior['cash']
            for t, pos in prior['positions'].items():
                px = state['positions'].get(t, {}).get('price', pos.get('price'))
                expected += pos['shares'] * px
            if expected > 0:
                gap = abs(state['equity'] - expected) / expected
                if gap > EQUITY_TOL:
                    anomalies.append(
                        f'equity move unexplained by market moves of held '
                        f'names ({gap:.1%} vs expected)')
    return anomalies


def live_vs_model(state: dict, live_dir: Path, model_series_path: Path,
                  lvm_path: Path) -> None:
    """Implementation-shortfall line (D5): cumulative live vs model return
    since the live baseline. COMMITTED — relative percentages only."""
    base_path = live_dir / 'recon' / 'baseline.json'
    if not base_path.exists():
        base_path.write_text(json.dumps(
            {'date': state['as_of'], 'equity': state['equity']}) + '\n')
    base = json.loads(base_path.read_text())
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
    try:
        doc = json.loads(Path(lvm_path).read_text())
    except (OSError, ValueError):
        doc = {'baseline_date': base['date'], 'series': []}
    doc['series'] = [e for e in doc['series'] if e['date'] != entry['date']]
    doc['series'].append(entry)
    doc['series'].sort(key=lambda e: e['date'])
    assert_sanitized_lvm(doc)                    # §E gate before committed write
    Path(lvm_path).write_text(json.dumps(doc, indent=2) + '\n')


def run(state: dict, *, live_dir: Path, target_weights: dict[str, float],
        model_series_path: Path = SERIES_PATH,
        status_path: Path = STATUS_PATH, lvm_path: Path = LVM_PATH) -> dict:
    live_dir = Path(live_dir)
    (live_dir / 'recon').mkdir(parents=True, exist_ok=True)
    receipts = _receipts(live_dir)
    prior = _prior_snapshot(live_dir, state['as_of'])

    fills, regen = verify_fills(receipts, state.get('orders', []))
    drift = drift_check(state, target_weights)
    anomalies = detect_anomalies(state, target_weights, receipts, prior)

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
    status = {
        'as_of': state['as_of'],
        'halted': halted,
        'positions': len(state['positions']),
        'open_orders': open_orders,
        'drift_flags': [d['ticker'] for d in drift],
        'regen_needed': regen,
        'anomaly_count': len(anomalies),
    }
    assert_sanitized_status(status)              # §E gate before committed write
    Path(status_path).write_text(json.dumps(status, indent=2) + '\n')

    for d in drift:
        print(f'drift flag: {d["ticker"]} {d["rel_drift_pct"]}% from target '
              f'(> {DRIFT_ALERT:.0%} relative)')
    for t in regen:
        print(f'unfilled order dead: {t} — regenerate on next model event '
              f'or --regen-unfilled')
    print(f'recon {state["as_of"]}: {len(state["positions"])} positions, '
          f'{open_orders} open orders, halted={halted}')
    return {'halted': halted, 'drift': drift, 'fills': fills,
            'regen_needed': regen, 'anomalies': anomalies,
            'snapshot': snap_path}


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
    args = ap.parse_args()
    payload = json.loads(Path(args.account_json).read_text())
    run(payload, live_dir=LIVE_DIR, target_weights=_targets_from_workbook())
