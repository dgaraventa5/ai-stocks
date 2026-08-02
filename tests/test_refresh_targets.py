"""refresh() gate + freeze-snapshot behaviour, over a temp workbook with
recalc / network / log_rebalance mocked."""
import sys
from pathlib import Path

import openpyxl
import pytest

pytest.importorskip('yfinance')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import refresh_targets as rt


def _build_portfolio(path, holdings, aux_sheets=True):
    """holdings: [(ticker, layer, score, tier)] written as Include?=Y rows.
    aux_sheets=False omits Reconciliation + Positions, mirroring the slimmed
    workbook the notional privacy pass (PR #9) left behind."""
    wb = openpyxl.Workbook()
    sz = wb.active
    sz.title = 'Sizing Rules'
    sz.append(['Portfolio Sizing Rules'])
    sz.append(['Parameter', 'Value', 'Notes'])
    sz.append(['Cash buffer %', 0, ''])
    sz.append(['Max single position %', 1.0, ''])  # no cap: let tier ordering show
    sz.append(['Tier-based base weight', None, None, None, None])
    sz.append(['Tier', 'Score Floor', 'Weight @ Floor', 'Weight @ Ceiling',
               'Score Ceiling'])
    sz.append(['✓✓✓', 85, 0.12, 0.12, 100])
    sz.append(['✓✓', 70, 0.03, 0.10, 85])
    sz.append(['✓', 55, 0.01, 0.03, 70])
    sz.append(['?', 40, 0, 0, 55])
    sz.append(['✗', 0, 0, 0, 40])
    sz.append(['Portfolio Value ($)', 10000, ''])
    tg = wb.create_sheet('Targets')
    tg.append(['Target Portfolio (test)'])
    tg.append(['Ticker', 'Layer', 'TOTAL', 'Tier', 'Rank', 'Status',
               'Include?', 'Override', 'Target %', 'Notes'])
    for i, (t, lay, sc, tier) in enumerate(holdings, 1):
        tg.append([t, lay, sc, tier, i, 'HOLD', 'Y', None,
                   round(100 / len(holdings), 2), None])
    if aux_sheets:
        wb.create_sheet('Reconciliation')
        wb.create_sheet('Positions').append(['Ticker', 'Company', 'Shares'])
    wb.create_sheet('README').append(['Last built', 'old'])
    wb.save(path)


def _mock_env(monkeypatch, live, cfg):
    monkeypatch.setattr(rt, 'recalc', lambda: live)
    monkeypatch.setattr(rt, 'last_trade_age_days', lambda t: 1)
    monkeypatch.setattr(rt, 'current_price', lambda t: 100.0)
    monkeypatch.setattr(rt.time, 'sleep', lambda *_a, **_k: None)
    monkeypatch.setattr(rt, 'load_cfg', lambda: cfg)
    calls, saves = [], []

    def fake_log(cfg_, w, reason, tiers=None):
        calls.append({'reason': reason, 'tiers': tiers, 'weights': dict(w)})
        return {'allocations': {k: v * 10000 for k, v in w.items()}, 'cash': 0.0}

    monkeypatch.setattr(rt, 'log_rebalance', fake_log)
    # Capture config saves (frozen-run pending-clock persistence) so tests can
    # assert on them AND so no test can ever write the real config file.
    monkeypatch.setattr(rt, 'save_cfg',
                        lambda cfg_: saves.append(dict(cfg_.get('exit_pending', {}))),
                        raising=False)
    return calls, saves


def test_refresh_fires_on_tier_change(monkeypatch, tmp_path):
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 78.0, '✓✓')])
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 78.0, 'Tier': '✓✓'}]
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓', 'TSM': '✓✓'}}]}   # NVDA was ✓✓, now ✓✓✓
    calls, _saves = _mock_env(monkeypatch, live, cfg)

    rt.refresh(portfolio=str(path))

    assert len(calls) == 1
    assert calls[0]['tiers'] == {'NVDA': '✓✓✓', 'TSM': '✓✓'}
    assert 'tier: NVDA ✓✓→✓✓✓' in calls[0]['reason']
    # Targets rewritten: NVDA (✓✓✓) now outweighs TSM (✓✓).
    tg = openpyxl.load_workbook(path)['Targets']
    w = {r[0]: r[8] for r in tg.iter_rows(min_row=3, values_only=True) if r[0]}
    assert w['NVDA'] > w['TSM']


def test_refresh_frozen_when_unchanged(monkeypatch, tmp_path):
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 78.0, '✓✓')])
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 78.0, 'Tier': '✓✓'}]
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓✓', 'TSM': '✓✓'}}]}   # tiers already match → no change
    calls, _saves = _mock_env(monkeypatch, live, cfg)
    before = path.read_bytes()

    rt.refresh(portfolio=str(path))

    assert calls == []                     # no rebalance event logged
    assert path.read_bytes() == before     # workbook untouched (frozen snapshot)


def test_pending_rebalance_true_on_tier_change(monkeypatch, tmp_path):
    """The rule-25 gate signal: pending_rebalance() is True when a held name's tier
    moved since the last event — and, being a dry run, writes NOTHING (a read-only
    probe, safe to call from a test/CI gate)."""
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 78.0, '✓✓')])
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 78.0, 'Tier': '✓✓'}]
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓', 'TSM': '✓✓'}}]}   # NVDA was ✓✓, now ✓✓✓
    calls, _saves = _mock_env(monkeypatch, live, cfg)
    before = path.read_bytes()

    assert rt.pending_rebalance(portfolio=str(path)) is True
    assert calls == []                     # dry run: nothing logged
    assert path.read_bytes() == before     # dry run: workbook untouched


def test_pending_rebalance_false_when_frozen(monkeypatch, tmp_path):
    """False when tiers/membership match the last event — so the gate passes exactly
    when the committed Targets already reflect the live scores (the steady state)."""
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 78.0, '✓✓')])
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 78.0, 'Tier': '✓✓'}]
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓✓', 'TSM': '✓✓'}}]}   # tiers already match
    _mock_env(monkeypatch, live, cfg)

    assert rt.pending_rebalance(portfolio=str(path)) is False


def test_refresh_tolerates_missing_recon_and_positions(monkeypatch, tmp_path):
    """The notional privacy pass (PR #9) removed Reconciliation + Positions.
    refresh() must run on the slim workbook (Sizing Rules + Targets only),
    writing just the Targets snapshot — not crash on a missing sheet (the crash
    that forced the ad-hoc Targets hand-edits this whole change replaces)."""
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 78.0, '✓✓')], aux_sheets=False)
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 78.0, 'Tier': '✓✓'}]
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓', 'TSM': '✓✓'}}]}   # NVDA ✓✓ → ✓✓✓ fires
    calls, _saves = _mock_env(monkeypatch, live, cfg)

    rt.refresh(portfolio=str(path))            # must not raise

    assert len(calls) == 1                     # rebalance still logged
    wb = openpyxl.load_workbook(path)
    assert 'Reconciliation' not in wb.sheetnames   # not recreated (kept slim)
    w = {r[0]: r[8] for r in wb['Targets'].iter_rows(min_row=3, values_only=True)
         if r[0]}
    assert w['NVDA'] > w['TSM']                # Targets snapshot still written


# ---- exit-pending clock persistence (2026-08-02 design) --------------------
# The 2-run exit confirm clock lives in performance-config.json (top-level
# `exit_pending` map), NOT the Targets sheet Status column: freeze-snapshot
# gating only rewrites the sheet when a rebalance fires, so a sheet-persisted
# clock never started (GOOGL/META/AMZN, observed 2026-08-02).

def _seed_cfg(exit_pending=None):
    """Two-name steady state (tiers match live) so only the exit path moves."""
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓✓', 'TSM': '✓✓'}}]}
    if exit_pending is not None:
        cfg['exit_pending'] = exit_pending
    return cfg


def _below_exit_live():
    # TSM 71.0 < default exit score 73.0, but still ✓✓ (no tier crossing) and
    # still held while pending → membership unchanged → snapshot frozen.
    return [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 71.0, 'Tier': '✓✓'}]


def test_exit_pending_clock_persists_on_frozen_run(monkeypatch, tmp_path):
    """First leg: below-exit with no other change keeps the workbook frozen but
    MUST persist the clock to the config — the bug was discarding it."""
    import datetime as dt
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 71.0, '✓✓')])
    calls, saves = _mock_env(monkeypatch, _below_exit_live(), _seed_cfg())
    before = path.read_bytes()

    rep = rt.refresh(portfolio=str(path))

    today = dt.date.today().isoformat()
    assert calls == []                          # no rebalance event
    assert path.read_bytes() == before          # workbook frozen (byte-identical)
    assert saves and saves[-1] == {'TSM': today}   # clock persisted to config
    assert rep['pending'] == {'TSM': today}


def test_exit_confirms_after_prior_day_pending(monkeypatch, tmp_path):
    """Second leg: a clock from a PRIOR date + still below exit → EXIT confirms
    (membership change fires the rebalance) and the clock entry clears."""
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 71.0, '✓✓')])
    cfg = _seed_cfg(exit_pending={'TSM': '2026-07-30'})
    calls, saves = _mock_env(monkeypatch, _below_exit_live(), cfg)

    rep = rt.refresh(portfolio=str(path))

    assert len(calls) == 1
    assert '-TSM' in calls[0]['reason']
    assert cfg['exit_pending'] == {}            # cleared before log_rebalance saves
    assert rep['pending'] == {}
    tg = openpyxl.load_workbook(path)['Targets']
    row = next(r for r in tg.iter_rows(min_row=3, values_only=True)
               if r[0] == 'TSM')
    assert row[6] == 'N'                        # excluded from the book
    assert str(row[5]).startswith('EXIT (pending since 2026-07-30')


def test_same_day_pending_does_not_confirm_or_rewrite(monkeypatch, tmp_path):
    """Two runs on the same date are one data point: no confirm, and an
    unchanged clock map is not redundantly re-saved."""
    import datetime as dt
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 71.0, '✓✓')])
    today = dt.date.today().isoformat()
    calls, saves = _mock_env(monkeypatch, _below_exit_live(),
                             _seed_cfg(exit_pending={'TSM': today}))
    before = path.read_bytes()

    rep = rt.refresh(portfolio=str(path))

    assert calls == []                          # still pending, no exit
    assert saves == []                          # map unchanged → no config write
    assert path.read_bytes() == before
    assert rep['pending'] == {'TSM': today}


def test_exit_pending_clears_on_recovery(monkeypatch, tmp_path):
    """Score back above exit resets the clock (2 CONSECUTIVE runs required) —
    and the reset itself must be persisted on an otherwise-frozen run."""
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 78.0, '✓✓')])
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 78.0, 'Tier': '✓✓'}]
    calls, saves = _mock_env(monkeypatch, live,
                             _seed_cfg(exit_pending={'TSM': '2026-07-30'}))
    before = path.read_bytes()

    rep = rt.refresh(portfolio=str(path))

    assert calls == []
    assert path.read_bytes() == before
    assert saves and saves[-1] == {}            # cleared clock persisted
    assert rep['pending'] == {}


def test_dry_run_never_mutates_pending(monkeypatch, tmp_path):
    """--dry-run / the rule-25 gate must be able to probe repeatedly without
    starting or advancing clocks."""
    import datetime as dt
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 71.0, '✓✓')])
    cfg = _seed_cfg()
    calls, saves = _mock_env(monkeypatch, _below_exit_live(), cfg)

    rep = rt.refresh(dry_run=True, portfolio=str(path))

    assert saves == [] and calls == []
    assert 'exit_pending' not in cfg            # untouched
    today = dt.date.today().isoformat()
    assert rep['pending'] == {'TSM': today}     # ...but the report shows it


def test_pending_rebalance_true_when_confirm_due(monkeypatch, tmp_path):
    """Once a clock is a day old and the name is still below exit, the rule-25
    gate turns True — forcing the confirming run (the gate was blind to this)."""
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 71.0, '✓✓')])
    cfg = _seed_cfg(exit_pending={'TSM': '2026-07-30'})
    calls, saves = _mock_env(monkeypatch, _below_exit_live(), cfg)
    before = path.read_bytes()

    assert rt.pending_rebalance(portfolio=str(path)) is True
    assert calls == [] and saves == []          # read-only probe
    assert cfg.get('exit_pending') == {'TSM': '2026-07-30'}
    assert path.read_bytes() == before
