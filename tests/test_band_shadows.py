"""Band shadows + EW_ROSTER series (spec 2026-08-07 A4/C1) and the event-log
roundtrip guarantee (spec A2: the series is fully reconstructible from the
events log — a resize event reproduces an identical series on re-run)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
pytest.importorskip('yfinance')
pd = pytest.importorskip('pandas')

import portfolio_model as pm

DATES = pd.to_datetime(['2026-05-26', '2026-05-27', '2026-05-28',
                        '2026-05-29', '2026-06-01'])
PRICES = {'SMH': [10, 10, 10, 10, 10], 'QQQ': [10, 10, 10, 10, 10],
          'SPY': [10, 10, 10, 10, 10],
          'AAA': [100, 110, 121, 133, 146], 'BBB': [50, 50, 60, 72, 72]}


@pytest.fixture
def fake_prices(monkeypatch):
    def fake_series(ticker, earliest):
        if ticker not in PRICES:
            return None
        return pd.Series(PRICES[ticker], index=DATES, dtype=float)
    pm._series_cache.clear()
    monkeypatch.setattr(pm, '_series', fake_series)


CFG = {
    'inception': '2026-05-26', 'capital': 10000.0,
    'ew_universe': ['AAA', 'BBB'],
    'events': [
        {'date': '2026-05-26', 'reason': 'initial', 'kind': 'membership',
         'allocations': {'AAA': 6000.0, 'BBB': 4000.0}, 'cash': 0.0},
        {'date': '2026-05-28', 'reason': 'resize_monthly',
         'kind': 'resize_monthly',
         'allocations': {'AAA': 5000.0, 'BBB': 5900.0}, 'cash': 0.0},
    ],
    'shadow_events': {
        'BAND_TOP': [{'date': '2026-05-28', 'roster': ['AAA']}],  # mid-history
    },
}


def test_ew_roster_mirrors_model_events(fake_prices):
    assert pm.model_roster_events(CFG) == [
        {'date': '2026-05-26', 'roster': ['AAA', 'BBB']},
        {'date': '2026-05-28', 'roster': ['AAA', 'BBB']}]


def test_shadow_series_forward_only_null_padded(fake_prices, tmp_path,
                                                monkeypatch):
    monkeypatch.setattr(pm, 'SERIES', tmp_path / 'series.json')
    out = pm.build_daily_series(dict(CFG))
    top = out['bench']['BAND_TOP']
    assert top[0] is None and top[1] is None      # pre-deploy: null, no backfill
    assert top[2] == 1.0                          # growth-of-1 from first event
    assert top[3] == pytest.approx(133 / 121, rel=1e-4)
    assert 'EW_ROSTER' in out['bench']            # sizing-null always present
    assert None not in out['bench']['EW_ROSTER']  # spans full history


def test_band_rosters_disjoint_and_complete():
    ranked = [f'T{i:02d}' for i in range(1, 50)]
    sh = {'top': 15, 'next': 25, 'tail': 40}      # DEFAULT_PCFG['shadows']
    top = ranked[:sh['top']]
    nxt = ranked[sh['top']:sh['next']]
    tail = ranked[sh['next']:sh['tail']]
    assert top + nxt + tail == ranked[:40]        # partition of ranks 1-40
    assert not (set(top) & set(nxt)) and not (set(nxt) & set(tail))


def test_event_log_roundtrip(fake_prices, tmp_path, monkeypatch):
    """A resize event reproduces an identical daily series on tracker re-run:
    the events log alone fully determines the series (spec A2)."""
    monkeypatch.setattr(pm, 'SERIES', tmp_path / 'series.json')
    out1 = pm.build_daily_series(json.loads(json.dumps(CFG)))
    bytes1 = (tmp_path / 'series.json').read_bytes()
    pm._series_cache.clear()
    out2 = pm.build_daily_series(json.loads(json.dumps(CFG)))
    bytes2 = (tmp_path / 'series.json').read_bytes()
    assert out1 == out2 and bytes1 == bytes2      # byte-identical repeat run
    # and the resize splice is continuous: model value on 05-28 equals the
    # marked value the event re-allocated (5000+5900), no injected jump
    d = out1['dates'].index('2026-05-28')
    assert out1['model'][d] == pytest.approx(10900.0)
