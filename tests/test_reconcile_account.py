"""Reconciliation & monitoring (§D of the 2026-08-09 agentic-execution spec).

Anomaly matrix: unknown-provenance position → HALT; drift → flag, not halt;
negative cash → HALT; unexplained equity move → HALT. Snapshot full-fidelity
(gitignored); committed status strictly sanitized (no dollars, no shares).
"""
import json

import pytest

import reconcile_account as ra

# Distinctive planted dollar/share values — must never reach committed output.
CASH, EQUITY, NVDA_PX, NVDA_SH = 137.53, 512.44, 187.31, 2.0017

STATE = {
    'as_of': '2026-08-13',
    'cash': CASH, 'equity': EQUITY,
    'positions': {'NVDA': {'shares': NVDA_SH, 'price': NVDA_PX}},
    'orders': [],
}
TARGETS = {'NVDA': 0.75}          # weights of equity (rest cash)


@pytest.fixture
def live_dir(tmp_path):
    d = tmp_path / 'live'
    (d / 'recon').mkdir(parents=True)
    (d / 'receipts').mkdir()
    return d


def run(state, live_dir, tmp_path, targets=TARGETS, model_series=None):
    series = tmp_path / 'performance-series.json'
    if not series.exists():
        series.write_text(json.dumps(model_series or {
            'dates': ['2026-08-12', '2026-08-13'],
            'model': [10000.0, 10100.0]}))
    status = tmp_path / 'live-status.json'
    lvm = tmp_path / 'live-vs-model.json'
    return ra.run(state, live_dir=live_dir, target_weights=targets,
                  model_series_path=series, status_path=status, lvm_path=lvm)


# ---- D2: drift flags (not halts) ----

def test_drift_beyond_band_flagged_not_halted(live_dir, tmp_path):
    # actual NVDA weight = 2.0017*187.31/512.44 ≈ 73.2%; target 75% → ~2.5% rel
    res = run(STATE, live_dir, tmp_path, targets={'NVDA': 0.85})
    assert any(d['ticker'] == 'NVDA' for d in res['drift'])
    assert res['halted'] is False
    assert not (live_dir / 'trading-halt.flag').exists()


def test_drift_within_band_clean(live_dir, tmp_path):
    res = run(STATE, live_dir, tmp_path, targets={'NVDA': 0.735})
    assert res['drift'] == []


# ---- D3: anomaly halts ----

def test_unknown_provenance_position_halts(live_dir, tmp_path):
    state = json.loads(json.dumps(STATE))
    state['positions']['XYZ'] = {'shares': 1.0, 'price': 10.0}
    res = run(state, live_dir, tmp_path)
    assert res['halted'] is True
    flag_text = (live_dir / 'trading-halt.flag').read_text()
    assert 'XYZ' in flag_text and 'provenance' in flag_text


def test_receipt_known_position_does_not_halt(live_dir, tmp_path):
    (live_dir / 'receipts' / 'receipt-t1.json').write_text(json.dumps(
        {'ticket_id': 't1', 'orders': [{'ticker': 'XYZ', 'side': 'buy',
                                        'order_id': 'rh-1', 'state': 'queued'}]}))
    state = json.loads(json.dumps(STATE))
    state['positions']['XYZ'] = {'shares': 1.0, 'price': 10.0}
    res = run(state, live_dir, tmp_path)
    assert res['halted'] is False


def test_negative_cash_halts(live_dir, tmp_path):
    state = dict(STATE, cash=-3.21)
    res = run(state, live_dir, tmp_path)
    assert res['halted'] is True
    assert 'cash' in (live_dir / 'trading-halt.flag').read_text()


def test_unexplained_equity_move_halts(live_dir, tmp_path):
    run(STATE, live_dir, tmp_path)                       # prior snapshot
    nxt = dict(STATE, as_of='2026-08-14', equity=900.0)  # +76% same prices
    res = run(nxt, live_dir, tmp_path)
    assert res['halted'] is True
    assert 'unexplained' in (live_dir / 'trading-halt.flag').read_text()


def test_price_explained_equity_move_no_halt(live_dir, tmp_path):
    run(STATE, live_dir, tmp_path)
    px = 250.0                                           # NVDA rallied
    nxt = {'as_of': '2026-08-14', 'cash': CASH,
           'equity': round(CASH + NVDA_SH * px, 2),
           'positions': {'NVDA': {'shares': NVDA_SH, 'price': px}},
           'orders': []}
    res = run(nxt, live_dir, tmp_path, targets={'NVDA': 0.79})
    assert res['halted'] is False


# ---- D1: fill verification ----

def test_fill_states_and_unfilled_expired_flag(live_dir, tmp_path):
    (live_dir / 'receipts' / 'receipt-t1.json').write_text(json.dumps(
        {'ticket_id': 't1', 'orders': [
            {'ticker': 'NVDA', 'order_id': 'rh-1', 'state': 'queued'},
            {'ticker': 'TSM', 'order_id': 'rh-2', 'state': 'queued'}]}))
    state = json.loads(json.dumps(STATE))
    state['orders'] = [
        {'order_id': 'rh-1', 'state': 'filled'},
        {'order_id': 'rh-2', 'state': 'cancelled'},   # expired unfilled
    ]
    res = run(state, live_dir, tmp_path)
    fills = res['fills']['t1']
    assert fills['NVDA'] == 'filled'
    assert fills['TSM'] == 'cancelled'
    assert 'TSM' in res['regen_needed']


# ---- D4: snapshot + sanitized committed status ----

def test_snapshot_written_full_fidelity(live_dir, tmp_path):
    run(STATE, live_dir, tmp_path)
    snap = json.loads(
        (live_dir / 'recon' / 'snapshot-2026-08-13.json').read_text())
    assert snap['equity'] == EQUITY
    assert snap['positions']['NVDA']['shares'] == NVDA_SH


def test_committed_status_sanitized_no_dollars_no_shares(live_dir, tmp_path):
    run(STATE, live_dir, tmp_path)
    text = (tmp_path / 'live-status.json').read_text()
    for planted in (str(CASH), str(EQUITY), str(NVDA_PX), str(NVDA_SH)):
        assert planted not in text
    status = json.loads(text)
    assert status['as_of'] == '2026-08-13'
    assert status['halted'] is False
    assert status['positions'] == 1                 # count, not values
    assert isinstance(status['drift_flags'], list)


# ---- D5: live-vs-model line (relative % only) ----

def test_live_vs_model_baseline_then_relative(live_dir, tmp_path):
    run(STATE, live_dir, tmp_path)                       # baseline run
    nxt = {'as_of': '2026-08-14', 'cash': CASH,
           'equity': round(EQUITY * 1.02, 2),            # +2% live
           'positions': {'NVDA': {'shares': NVDA_SH,
                                  'price': NVDA_PX * 1.027}},
           'orders': []}
    series = tmp_path / 'performance-series.json'
    series.write_text(json.dumps({
        'dates': ['2026-08-13', '2026-08-14'],
        'model': [10000.0, 10100.0]}))                   # +1% model
    res = run(nxt, live_dir, tmp_path, targets={'NVDA': 0.755})
    lvm = json.loads((tmp_path / 'live-vs-model.json').read_text())
    assert lvm['baseline_date'] == '2026-08-13'
    last = lvm['series'][-1]
    assert last['live_pct'] == pytest.approx(2.0, abs=0.05)
    assert last['model_pct'] == pytest.approx(1.0, abs=0.05)
    assert last['shortfall_pct'] == pytest.approx(1.0, abs=0.1)
    text = (tmp_path / 'live-vs-model.json').read_text()
    for planted in (str(EQUITY), str(CASH)):
        assert planted not in text                       # relative % only
    assert res['halted'] is False
