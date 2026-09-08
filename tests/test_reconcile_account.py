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


def test_undeclared_deposit_halts(live_dir, tmp_path):
    """A cash deposit that nobody declared is indistinguishable from an
    executor bug — it must halt (the 2026-08-14 deploy-cash scenario)."""
    run(STATE, live_dir, tmp_path)
    dep = 500.0
    nxt = dict(STATE, as_of='2026-08-14', cash=CASH + dep,
               equity=round(EQUITY + dep, 2))
    res = run(nxt, live_dir, tmp_path)
    assert res['halted'] is True
    assert 'external-flow' in (live_dir / 'trading-halt.flag').read_text()


def test_declared_deposit_no_halt_and_flat_lvm(live_dir, tmp_path):
    run(STATE, live_dir, tmp_path)                       # prior + baseline
    dep = 500.0
    nxt = dict(STATE, as_of='2026-08-14', cash=CASH + dep,
               equity=round(EQUITY + dep, 2))
    res = ra.run(nxt, live_dir=live_dir, target_weights=TARGETS,
                 model_series_path=tmp_path / 'performance-series.json',
                 status_path=tmp_path / 'live-status.json',
                 lvm_path=tmp_path / 'live-vs-model.json',
                 external_flow=dep)
    assert res['halted'] is False
    assert res['anomalies'] == []
    # The deposit is not performance: live_pct stays ~0.
    lvm = json.loads((tmp_path / 'live-vs-model.json').read_text())
    assert lvm['series'][-1]['live_pct'] == pytest.approx(0.0, abs=0.05)
    # Privacy: the flow amount never reaches committed artifacts.
    for text in ((tmp_path / 'live-vs-model.json').read_text(),
                 (tmp_path / 'live-status.json').read_text()):
        assert '500' not in text


def test_declared_flow_persists_for_later_undeclared_runs(live_dir, tmp_path):
    """The launchd cron recons WITHOUT the flag — the ledger must keep
    explaining the same deposit against the same pre-deposit prior."""
    run(STATE, live_dir, tmp_path)
    dep = 500.0
    nxt = dict(STATE, as_of='2026-08-14', cash=CASH + dep,
               equity=round(EQUITY + dep, 2))
    ra.run(nxt, live_dir=live_dir, target_weights=TARGETS,
           model_series_path=tmp_path / 'performance-series.json',
           status_path=tmp_path / 'live-status.json',
           lvm_path=tmp_path / 'live-vs-model.json', external_flow=dep)
    res = run(nxt, live_dir, tmp_path)   # same-day re-run, no flag (cron)
    assert res['halted'] is False
    # ...and the baseline was divisor-adjusted exactly once.
    base = json.loads((live_dir / 'recon' / 'baseline.json').read_text())
    assert len(base['applied_flows']) == 1
    lvm = json.loads((tmp_path / 'live-vs-model.json').read_text())
    assert lvm['series'][-1]['live_pct'] == pytest.approx(0.0, abs=0.05)


def test_declare_flow_idempotent_per_date_amount(live_dir, tmp_path):
    ra.declare_flow(live_dir, '2026-08-14', 500.0)
    ra.declare_flow(live_dir, '2026-08-14', 500.0)
    assert len(ra.read_flows(live_dir)) == 1
    ra.declare_flow(live_dir, '2026-08-14', -100.0)      # distinct entry
    assert len(ra.read_flows(live_dir)) == 2
    assert ra.flows_between(live_dir, '2026-08-12', '2026-08-14') == 400.0


def test_flow_equal_to_cash_balance_refused(live_dir, tmp_path):
    """--external-flow takes the amount that MOVED, not the resulting balance.

    The 2026-08-14 incident: a deposit onto an account that already held cash
    was declared as the post-deposit balance. Both are dollars, so nothing
    caught it; the over-declaration then poisoned the baseline divisor and
    printed a phantom negative live return. Fail closed, like the executor
    gates. (Figures here are the fixture's fictional values, not live ones.)
    """
    run(STATE, live_dir, tmp_path)                       # prior: cash = CASH
    dep = 500.0
    nxt = dict(STATE, as_of='2026-08-14', cash=round(CASH + dep, 2),
               equity=round(EQUITY + dep, 2))
    with pytest.raises(ValueError, match='resulting balance'):
        ra.run(nxt, live_dir=live_dir, target_weights=TARGETS,
               model_series_path=tmp_path / 'performance-series.json',
               status_path=tmp_path / 'live-status.json',
               lvm_path=tmp_path / 'live-vs-model.json',
               external_flow=round(CASH + dep, 2))       # the balance, not the delta
    assert ra.read_flows(live_dir) == []                  # ledger untouched


def test_refusal_names_the_probable_intended_amount(live_dir, tmp_path):
    """The refusal must be actionable: say what the flow probably was."""
    run(STATE, live_dir, tmp_path)
    dep = 500.0
    nxt = dict(STATE, as_of='2026-08-14', cash=round(CASH + dep, 2),
               equity=round(EQUITY + dep, 2))
    with pytest.raises(ValueError, match=r'500\.00'):
        ra.run(nxt, live_dir=live_dir, target_weights=TARGETS,
               model_series_path=tmp_path / 'performance-series.json',
               status_path=tmp_path / 'live-status.json',
               lvm_path=tmp_path / 'live-vs-model.json',
               external_flow=round(CASH + dep, 2))


def test_flow_equal_to_cash_balance_allowed_when_prior_cash_zero(live_dir,
                                                                 tmp_path):
    """A deposit into a fully-deployed account legitimately EQUALS the
    resulting balance — the guard must not fire on the honest case."""
    zero = dict(STATE, cash=0.0, equity=round(EQUITY - CASH, 2))
    run(zero, live_dir, tmp_path)
    dep = 500.0
    nxt = dict(zero, as_of='2026-08-14', cash=dep,
               equity=round(EQUITY - CASH + dep, 2))
    res = ra.run(nxt, live_dir=live_dir, target_weights=TARGETS,
                 model_series_path=tmp_path / 'performance-series.json',
                 status_path=tmp_path / 'live-status.json',
                 lvm_path=tmp_path / 'live-vs-model.json', external_flow=dep)
    assert res['halted'] is False
    assert ra.read_flows(live_dir) == [{'date': '2026-08-14', 'amount': dep}]


def test_declared_withdrawal_no_halt(live_dir, tmp_path):
    run(STATE, live_dir, tmp_path)
    wd = -60.0
    nxt = dict(STATE, as_of='2026-08-14', cash=round(CASH + wd, 2),
               equity=round(EQUITY + wd, 2))
    res = ra.run(nxt, live_dir=live_dir, target_weights=TARGETS,
                 model_series_path=tmp_path / 'performance-series.json',
                 status_path=tmp_path / 'live-status.json',
                 lvm_path=tmp_path / 'live-vs-model.json', external_flow=wd)
    assert res['halted'] is False


def test_market_move_after_deposit_still_measured(live_dir, tmp_path):
    """Divisor math: the deposit is invisible but the subsequent rally is not."""
    run(STATE, live_dir, tmp_path)
    dep = 500.0
    d1 = dict(STATE, as_of='2026-08-14', cash=CASH + dep,
              equity=round(EQUITY + dep, 2))
    ra.run(d1, live_dir=live_dir, target_weights=TARGETS,
           model_series_path=tmp_path / 'performance-series.json',
           status_path=tmp_path / 'live-status.json',
           lvm_path=tmp_path / 'live-vs-model.json', external_flow=dep)
    px = NVDA_PX * 1.10                                  # +10% on the position
    gain = NVDA_SH * (px - NVDA_PX)
    d2 = {'as_of': '2026-08-15', 'cash': CASH + dep,
          'equity': round(EQUITY + dep + gain, 2),
          'positions': {'NVDA': {'shares': NVDA_SH, 'price': px}},
          'orders': []}
    ra.run(d2, live_dir=live_dir, target_weights={'NVDA': 0.40},
           model_series_path=tmp_path / 'performance-series.json',
           status_path=tmp_path / 'live-status.json',
           lvm_path=tmp_path / 'live-vs-model.json')
    lvm = json.loads((tmp_path / 'live-vs-model.json').read_text())
    expected = (d2['equity'] / (EQUITY + dep) - 1) * 100
    assert lvm['series'][-1]['live_pct'] == pytest.approx(expected, abs=0.05)


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


# ---- ACCOUNT_CAP staleness (2026-08-17: a deposit silently outgrew the cap) ----

def _cfg(live_dir, cap):
    (live_dir / 'executor-config.json').write_text(json.dumps({'ACCOUNT_CAP': cap}))


def test_equity_over_account_cap_flags_without_halting(live_dir, tmp_path):
    """A deposit can push equity past ACCOUNT_CAP, after which every execution
    refuses — but nothing said so until a rebalance happened to be attempted.
    Surface it at recon. FLAG, never halt: the executor already fails closed,
    and a halt would block unrelated work and need manual clearing.
    """
    _cfg(live_dir, EQUITY - 100)                 # equity above the cap
    res = run(STATE, live_dir, tmp_path)
    assert res['cap_exceeded'] is True
    assert res['halted'] is False
    assert res['anomalies'] == []


def test_equity_under_account_cap_not_flagged(live_dir, tmp_path):
    _cfg(live_dir, EQUITY + 100)
    assert run(STATE, live_dir, tmp_path)['cap_exceeded'] is False


def test_no_executor_config_means_no_cap_claim(live_dir, tmp_path):
    """No config = the cap is unknown. Don't invent a verdict (rule 3)."""
    assert run(STATE, live_dir, tmp_path)['cap_exceeded'] is False


def test_cap_flag_reaches_committed_status_without_dollars(live_dir, tmp_path):
    """§E: the committed artifact may carry the boolean, never the figures."""
    _cfg(live_dir, EQUITY - 100)
    run(STATE, live_dir, tmp_path)
    text = (tmp_path / 'live-status.json').read_text()
    assert json.loads(text)['cap_exceeded'] is True
    for planted in (str(EQUITY), str(EQUITY - 100), str(CASH)):
        assert planted not in text


# ---- 3b (2026-09-08): a transmit_error leg still out of band ----------------
# The 2026-08-17 VRT leg was rejected at transmit while 14 legs went through.
# The receipt recorded it, drift flagged it every run for three weeks, and
# nothing ever connected the two — so the underweight read as ordinary price
# drift rather than as a trade that never happened. This channel is loud but
# deliberately NON-HALTING: raising the kill switch would block unrelated
# correct trades to fix a position that is merely the wrong size.

def _receipt(live_dir, ticker, state, ticket_id='2026-08-17-manual_resize'):
    (live_dir / 'receipts' / f'receipt-{ticket_id}.json').write_text(json.dumps({
        'ticket_id': ticket_id, 'sent_at': '2026-08-17T13:40:00Z',
        'checksum': 'x',
        'orders': [{'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0,
                    'order_id': 'rh-1', 'state': 'queued'},
                   {'ticker': ticker, 'side': 'buy', 'shares': 1.0,
                    'order_id': None, 'state': state,
                    **({'error': 'You can only purchase 0 shares'}
                       if state == 'transmit_error' else {})}]}))


def test_transmit_error_leg_still_out_of_band_is_surfaced(live_dir, tmp_path):
    _receipt(live_dir, 'VRT', 'transmit_error')
    state = {**STATE, 'positions': {**STATE['positions'],
                                    'VRT': {'shares': 0.1, 'price': 10.0}}}
    res = run(state, live_dir, tmp_path, targets={'NVDA': 0.70, 'VRT': 0.25})
    assert 'VRT' in res['unrepaired_legs']


def test_unrepaired_leg_does_not_halt(live_dir, tmp_path):
    """Loud, never blocking — the halt flag stops unrelated correct trades."""
    _receipt(live_dir, 'VRT', 'transmit_error')
    state = {**STATE, 'positions': {**STATE['positions'],
                                    'VRT': {'shares': 0.1, 'price': 10.0}}}
    res = run(state, live_dir, tmp_path, targets={'NVDA': 0.70, 'VRT': 0.25})
    assert res['halted'] is False
    assert not (live_dir / 'trading-halt.flag').exists()


def test_transmit_error_leg_back_in_band_is_not_surfaced(live_dir, tmp_path):
    """Repaired by a later ticket → the receipt is history, not a live gap."""
    _receipt(live_dir, 'VRT', 'transmit_error')
    # VRT now sits essentially on its target weight
    state = {**STATE, 'positions': {**STATE['positions'],
                                    'VRT': {'shares': 6.8, 'price': 10.0}}}
    res = run(state, live_dir, tmp_path, targets={'NVDA': 0.70, 'VRT': 0.1327})
    assert res['unrepaired_legs'] == []


def test_successful_leg_out_of_band_is_only_drift(live_dir, tmp_path):
    """Ordinary price drift on a leg that DID transmit must not be escalated."""
    _receipt(live_dir, 'VRT', 'queued')
    state = {**STATE, 'positions': {**STATE['positions'],
                                    'VRT': {'shares': 0.1, 'price': 10.0}}}
    res = run(state, live_dir, tmp_path, targets={'NVDA': 0.70, 'VRT': 0.25})
    assert res['unrepaired_legs'] == []
    assert any(d['ticker'] == 'VRT' for d in res['drift'])


def test_unrepaired_legs_are_sanitized_into_committed_status(live_dir, tmp_path):
    _receipt(live_dir, 'VRT', 'transmit_error')
    state = {**STATE, 'positions': {**STATE['positions'],
                                    'VRT': {'shares': 0.1, 'price': 10.0}}}
    run(state, live_dir, tmp_path, targets={'NVDA': 0.70, 'VRT': 0.25})
    status = json.loads((tmp_path / 'live-status.json').read_text())
    assert status['unrepaired_legs'] == ['VRT']          # tickers only
    blob = json.dumps(status)
    for planted in (str(CASH), str(EQUITY), str(NVDA_PX), str(NVDA_SH)):
        assert planted not in blob


# ---- §4 (2026-09-08): report BOTH lines, discard nothing --------------------
# The since-inception shortfall carried two meanings at once: a permanent
# one-time deployment lag (-3.69pts of the -4.53 accrued 2026-08-09..08-17,
# when the baseline was struck at 100% cash and a deposit left the account 27%
# invested for three days while the model was fully invested) and ongoing
# implementation shortfall. Summed, neither is readable. The inception series
# is NEVER restated; a second anchor is added at first-full-deployment and
# reported alongside it. Forward-only — existing entries are not backfilled.

def _snap(live_dir, date, cash, positions, equity):
    (live_dir / 'recon' / f'snapshot-{date}.json').write_text(json.dumps(
        {'as_of': date, 'cash': cash, 'equity': equity,
         'positions': positions, 'orders': [], 'fills': [], 'anomalies': []}))


def test_deployment_anchor_is_first_fully_deployed_snapshot(live_dir, tmp_path):
    _snap(live_dir, '2026-08-14', 73.0, {'NVDA': {'shares': 1.0, 'price': 27.0}},
          100.0)                                        # 27% invested
    _snap(live_dir, '2026-08-17', 4.0, {'NVDA': {'shares': 1.0, 'price': 96.0}},
          100.0)                                        # 96% invested
    state = {'as_of': '2026-08-18', 'cash': 4.0, 'equity': 100.0,
             'positions': {'NVDA': {'shares': 1.0, 'price': 96.0}}, 'orders': []}
    run(state, live_dir, tmp_path, targets={'NVDA': 0.96})
    doc = json.loads((tmp_path / 'live-vs-model.json').read_text())
    assert doc['deployment_date'] == '2026-08-17'


def test_deployment_anchor_is_immutable_once_written(live_dir, tmp_path):
    """An adjustable anchor could be tuned until tracking looks good — the
    same reason rule 17 freezes created_date."""
    _snap(live_dir, '2026-08-17', 4.0, {'NVDA': {'shares': 1.0, 'price': 96.0}},
          100.0)
    state = {'as_of': '2026-08-18', 'cash': 4.0, 'equity': 100.0,
             'positions': {'NVDA': {'shares': 1.0, 'price': 96.0}}, 'orders': []}
    run(state, live_dir, tmp_path, targets={'NVDA': 0.96})
    first = json.loads((tmp_path / 'live-vs-model.json').read_text())['deployment_date']
    _snap(live_dir, '2026-08-19', 1.0, {'NVDA': {'shares': 1.0, 'price': 99.0}},
          100.0)                                        # even more invested
    state2 = {**state, 'as_of': '2026-08-20'}
    run(state2, live_dir, tmp_path, targets={'NVDA': 0.96})
    doc = json.loads((tmp_path / 'live-vs-model.json').read_text())
    assert doc['deployment_date'] == first == '2026-08-17'


def test_no_anchor_while_never_fully_deployed(live_dir, tmp_path):
    _snap(live_dir, '2026-08-14', 73.0, {'NVDA': {'shares': 1.0, 'price': 27.0}},
          100.0)
    state = {'as_of': '2026-08-15', 'cash': 73.0, 'equity': 100.0,
             'positions': {'NVDA': {'shares': 1.0, 'price': 27.0}}, 'orders': []}
    run(state, live_dir, tmp_path, targets={'NVDA': 0.27})
    doc = json.loads((tmp_path / 'live-vs-model.json').read_text())
    assert doc.get('deployment_date') is None
    assert doc['series'][-1].get('shortfall_since_deploy_pct') is None


def test_inception_line_is_never_restated(live_dir, tmp_path):
    """The whole point of (c): nothing is discarded."""
    _snap(live_dir, '2026-08-17', 4.0, {'NVDA': {'shares': 1.0, 'price': 96.0}},
          100.0)
    state = {'as_of': '2026-08-18', 'cash': 4.0, 'equity': 100.0,
             'positions': {'NVDA': {'shares': 1.0, 'price': 96.0}}, 'orders': []}
    run(state, live_dir, tmp_path, targets={'NVDA': 0.96})
    doc = json.loads((tmp_path / 'live-vs-model.json').read_text())
    e = doc['series'][-1]
    assert e['live_pct'] is not None and 'shortfall_pct' in e
    assert doc['baseline_date'] == '2026-08-18'   # inception anchor untouched


def test_since_deploy_entries_are_forward_only(live_dir, tmp_path):
    """Pre-existing entries keep exactly the fields they were written with."""
    lvm = tmp_path / 'live-vs-model.json'
    lvm.write_text(json.dumps({'baseline_date': '2026-08-09', 'series': [
        {'date': '2026-08-13', 'live_pct': 0.05, 'model_pct': 1.97,
         'shortfall_pct': -1.92}]}))
    _snap(live_dir, '2026-08-17', 4.0, {'NVDA': {'shares': 1.0, 'price': 96.0}},
          100.0)
    state = {'as_of': '2026-08-18', 'cash': 4.0, 'equity': 100.0,
             'positions': {'NVDA': {'shares': 1.0, 'price': 96.0}}, 'orders': []}
    run(state, live_dir, tmp_path, targets={'NVDA': 0.96})
    doc = json.loads(lvm.read_text())
    old = [e for e in doc['series'] if e['date'] == '2026-08-13'][0]
    assert set(old) == {'date', 'live_pct', 'model_pct', 'shortfall_pct'}
    assert old['shortfall_pct'] == -1.92          # not recomputed


def test_lvm_sanitizer_still_rejects_an_unknown_field(live_dir, tmp_path):
    with pytest.raises(ValueError):
        ra.assert_sanitized_lvm({'baseline_date': '2026-08-09', 'series': [
            {'date': '2026-08-13', 'equity_usd': 13800.0}]})
