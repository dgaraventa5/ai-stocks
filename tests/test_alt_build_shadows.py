"""Alternative-build trackers on the Performance tab (Dom, 2026-11-21):
Model top 25, V/Q/R floor 70 top 15, V/Q/R floor 70 top 25."""
import sys
from pathlib import Path

import pytest

pytest.importorskip('yfinance')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import refresh_targets as rt


def _row(t, total, ai, v, q, r):
    return {'ticker': t, 'TOTAL': total, 'AI': ai,
            'Value': v, 'Quality': q, 'Risk': r}


def test_vqr_weights_are_live_20_20_15_rescaled():
    assert rt.VQR_WEIGHTS['Value'] == pytest.approx(0.3636, abs=1e-4)
    assert rt.VQR_WEIGHTS['Quality'] == pytest.approx(0.3636, abs=1e-4)
    assert rt.VQR_WEIGHTS['Risk'] == pytest.approx(0.2727, abs=1e-4)
    assert sum(rt.VQR_WEIGHTS.values()) == pytest.approx(1.0)


def test_vqr_score_renormalises_over_available_categories():
    assert rt.vqr_score(_row('A', 80, 90, 60, 60, 60)) == pytest.approx(60)
    # Risk blank: the average of Value and Quality, not dragged toward zero
    assert rt.vqr_score(_row('A', 80, 90, 50, 70, None)) == pytest.approx(60)
    assert rt.vqr_score(_row('A', 80, 90, None, None, None)) is None


def test_ai_floor_is_inclusive_and_blank_ai_is_out():
    live = [_row('AT70', 50, 70, 90, 90, 90),
            _row('BELOW', 99, 69.9, 99, 99, 99),
            _row('NOAI', 99, None, 99, 99, 99)]
    r = rt.alt_build_rosters(live)
    assert r['VQR70_TOP15'] == ['AT70']
    assert r['MODEL_TOP25'] == ['BELOW', 'NOAI', 'AT70']   # TOTAL order, no floor


def test_rosters_rank_and_cut():
    # 30 names, all AI >= 70. TOTAL falls with i; V/Q/R rises with i, so the
    # two rankings run in opposite directions.
    live = [_row(f'T{i:02d}', 100 - i, 80, i, i, i) for i in range(1, 31)]
    r = rt.alt_build_rosters(live)
    assert r['MODEL_TOP25'] == [f'T{i:02d}' for i in range(1, 26)]
    assert r['VQR70_TOP15'] == [f'T{i:02d}' for i in range(30, 15, -1)]
    assert r['VQR70_TOP25'] == [f'T{i:02d}' for i in range(30, 5, -1)]


def test_excluded_names_never_enter():
    live = [_row('A', 90, 90, 90, 90, 90), _row('B', 80, 90, 80, 80, 80)]
    r = rt.alt_build_rosters(live, excluded={'A'})
    assert all('A' not in roster for roster in r.values())


def test_real_run_logs_alt_builds_forward_only(monkeypatch, tmp_path):
    import datetime as dt
    from test_refresh_targets import (_build_portfolio, _mock_env, _rank_cfg,
                                      _rank_pcfg, _rank_prior)
    path = tmp_path / 'portfolio.xlsx'
    prior = _rank_prior()
    _build_portfolio(path, [(t, '06 Silicon', 90.0, '✓✓') for t in prior])
    live = [{'ticker': f'T{i:02d}', 'layer': '06 Silicon',
             'TOTAL': 90.0 - (i - 1), 'Tier': '✓✓', 'AI': 75.0 if i % 2 else 60.0,
             'Value': 50.0 + i, 'Quality': 50.0, 'Risk': 50.0}
            for i in range(1, 21)]
    cfg = _rank_cfg(prior)
    _mock_env(monkeypatch, live, cfg)
    monkeypatch.setattr(rt, 'load_pcfg', _rank_pcfg)
    today = dt.date.today().isoformat()

    rt.refresh(portfolio=str(path))

    ev = cfg['shadow_events']
    assert ev['MODEL_TOP25'] == [{'date': today,
                                  'roster': [f'T{i:02d}' for i in range(1, 21)]}]
    # odd tickers clear the floor; higher Value ranks first
    assert ev['VQR70_TOP15'][0]['roster'] == [f'T{i:02d}' for i in range(19, 0, -2)]
    assert ev['VQR70_TOP25'][0]['roster'] == ev['VQR70_TOP15'][0]['roster']
    before = {k: [dict(e) for e in v] for k, v in ev.items()}
    rt.refresh(portfolio=str(path))                  # same-day re-run
    assert cfg['shadow_events'] == before


def test_dry_run_logs_nothing(monkeypatch, tmp_path):
    from test_refresh_targets import (_build_portfolio, _mock_env, _rank_cfg,
                                      _rank_live, _rank_pcfg, _rank_prior)
    path = tmp_path / 'portfolio.xlsx'
    prior = _rank_prior()
    _build_portfolio(path, [(t, '06 Silicon', 90.0, '✓✓') for t in prior])
    cfg = _rank_cfg(prior)
    _mock_env(monkeypatch, _rank_live(), cfg)
    monkeypatch.setattr(rt, 'load_pcfg', _rank_pcfg)
    rt.refresh(dry_run=True, portfolio=str(path))
    assert 'shadow_events' not in cfg


# ---- backfill (scripts/backfill_alt_builds.py, 2026-11-21) ------------------

import backfill_alt_builds as bf  # noqa: E402


def test_merge_keeps_live_events_and_replaces_old_rebuilt_ones():
    live = {'date': '2026-11-21', 'roster': ['A']}
    cfg = {'shadow_events': {'VQR70_TOP15': [
        {'date': '2026-08-01', 'roster': ['OLD'], 'rebuilt': True}, live]}}
    new = {'VQR70_TOP15': [{'date': '2026-08-12', 'roster': ['B'],
                            'rebuilt': True}]}
    bf.merge(cfg, new)
    assert cfg['shadow_events']['VQR70_TOP15'] == new['VQR70_TOP15'] + [live]


def test_merge_refuses_overlap_with_live_tracking():
    cfg = {'shadow_events': {'VQR70_TOP15': [
        {'date': '2026-11-21', 'roster': ['A']}]}}
    with pytest.raises(SystemExit):
        bf.merge(cfg, {'VQR70_TOP15': [{'date': '2026-11-21', 'roster': ['B'],
                                        'rebuilt': True}]})


def test_build_events_next_day_effective_and_collapsed(monkeypatch):
    monkeypatch.setattr(bf, 'score_dates',
                        lambda first: ['2026-08-11', '2026-08-13', '2026-11-20'])
    lists = {'2026-08-11': ['A', 'B'], '2026-08-13': ['B', 'A'],
             '2026-11-20': ['C']}
    monkeypatch.setattr(bf, 'model_top25', lambda day: lists[day])
    monkeypatch.setattr(bf, 'vqr_rosters', lambda day, ref, tmp, cache: {
        'VQR70_TOP15': lists[day], 'VQR70_TOP25': lists[day]})
    ev = bf.build_events('2026-11-21', 'origin/main')
    got = [(e['scored'], e['date'], e['roster']) for e in ev['MODEL_TOP25']]
    # same names in another order is not a new roster; each takes effect the
    # day after its scoring date; a roster effective on the live start date
    # would overlap live tracking and is dropped
    assert got == [('2026-08-11', '2026-08-12', ['A', 'B'])]
    assert all(e['rebuilt'] for evs in ev.values() for e in evs)
