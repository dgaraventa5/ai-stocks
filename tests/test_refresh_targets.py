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
    calls = []

    def fake_log(cfg_, w, reason, tiers=None):
        calls.append({'reason': reason, 'tiers': tiers, 'weights': dict(w)})
        return {'allocations': {k: v * 10000 for k, v in w.items()}, 'cash': 0.0}

    monkeypatch.setattr(rt, 'log_rebalance', fake_log)
    return calls


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
    calls = _mock_env(monkeypatch, live, cfg)

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
    calls = _mock_env(monkeypatch, live, cfg)
    before = path.read_bytes()

    rt.refresh(portfolio=str(path))

    assert calls == []                     # no rebalance event logged
    assert path.read_bytes() == before     # workbook untouched (frozen snapshot)


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
    calls = _mock_env(monkeypatch, live, cfg)

    rt.refresh(portfolio=str(path))            # must not raise

    assert len(calls) == 1                     # rebalance still logged
    wb = openpyxl.load_workbook(path)
    assert 'Reconciliation' not in wb.sheetnames   # not recreated (kept slim)
    w = {r[0]: r[8] for r in wb['Targets'].iter_rows(min_row=3, values_only=True)
         if r[0]}
    assert w['NVDA'] > w['TSM']                # Targets snapshot still written
