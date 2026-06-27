"""High-water-mark guard: a rebuild must never drop a trading day already
recorded in the committed series.

Root cause (2026-06-27): yfinance intermittently serves the latest trading bar
with a NaN close (unsettled adjusted close). portfolio_model._series does
`['Close'].dropna()`, so the rebuilt series comes back one day SHORTER. The
daily-refresh.yml commit guard (`git diff --quiet`) committed that regression,
bouncing the dashboard `as_of` BACKWARD (Jun 26 -> Jun 25). build_daily_series
must refuse to overwrite a committed series with one that drops recorded bars.
"""
import json

import pytest

pytest.importorskip('yfinance')          # pm imports yfinance at module level
pd = pytest.importorskip('pandas')

import portfolio_model as pm

# Five-day calendar; SMH sources the trading calendar, AAA is the only holding.
ALL_DATES = ['2026-05-26', '2026-05-27', '2026-05-28', '2026-05-29', '2026-06-01']
PRICES = {
    'SMH': [10, 11, 12, 13, 14],
    'QQQ': [10, 11, 12, 13, 14],
    'SPY': [10, 11, 12, 13, 14],
    'AAA': [100, 110, 121, 133, 146],
}

CFG = {
    'inception': '2026-05-26',
    'capital': 10000,
    'ew_universe': ['AAA'],
    'events': [{'date': '2026-05-26', 'reason': 'init',
                'allocations': {'AAA': 10000}, 'cash': 0}],
}


def _install_prices(monkeypatch, upto):
    """Mock _series so every ticker only has bars through index `upto` (the
    flicker: yfinance drops the latest NaN-close bar)."""
    dates = pd.to_datetime(ALL_DATES[:upto])

    def fake_series(ticker, earliest):
        if ticker not in PRICES:
            return None
        return pd.Series(PRICES[ticker][:upto], index=dates, dtype=float)
    pm._series_cache.clear()
    monkeypatch.setattr(pm, '_series', fake_series)


@pytest.fixture(autouse=True)
def _isolate_series(monkeypatch, tmp_path):
    monkeypatch.setattr(pm, 'SERIES', tmp_path / 'performance-series.json')
    monkeypatch.delenv('FORCE_SERIES', raising=False)


def test_refuses_to_drop_a_recorded_trading_day(monkeypatch):
    # Committed series spans all 5 days (high-water-mark = 2026-06-01).
    _install_prices(monkeypatch, upto=5)
    full = pm.build_daily_series(CFG)
    assert full['as_of'] == '2026-06-01'

    # Next rebuild flickers short (yfinance dropped the latest bar): only 4 days.
    _install_prices(monkeypatch, upto=4)
    out = pm.build_daily_series(CFG)

    # Guard must refuse: return None AND leave the committed file untouched.
    assert out is None
    on_disk = json.loads(pm.SERIES.read_text())
    assert on_disk['as_of'] == '2026-06-01'          # NOT regressed to 05-29
    assert on_disk['dates'] == ALL_DATES


def test_allows_genuine_advance(monkeypatch):
    _install_prices(monkeypatch, upto=4)
    pm.build_daily_series(CFG)                        # committed through 05-29

    _install_prices(monkeypatch, upto=5)             # new valid bar arrives
    out = pm.build_daily_series(CFG)
    assert out['as_of'] == '2026-06-01'
    assert json.loads(pm.SERIES.read_text())['as_of'] == '2026-06-01'


def test_first_build_writes_when_no_committed_file(monkeypatch):
    _install_prices(monkeypatch, upto=4)
    out = pm.build_daily_series(CFG)
    assert out is not None
    assert pm.SERIES.exists()


def test_same_day_revaluation_still_writes(monkeypatch):
    """A rebuild with the SAME dates but corrected values must still write."""
    _install_prices(monkeypatch, upto=5)
    pm.build_daily_series(CFG)

    # Same calendar, AAA revalued (e.g. dividend backfill) — no dropped dates.
    bumped = dict(PRICES, AAA=[100, 110, 121, 133, 160])
    dates = pd.to_datetime(ALL_DATES)
    monkeypatch.setattr(pm, '_series',
                        lambda t, e: (pd.Series(bumped[t], index=dates, dtype=float)
                                      if t in bumped else None))
    pm._series_cache.clear()
    out = pm.build_daily_series(CFG)
    assert out is not None
    assert out['as_of'] == '2026-06-01'
    assert out['model'][-1] != pytest.approx(146.0 / 100 * 10000)  # revalued


def test_force_env_bypasses_guard(monkeypatch):
    _install_prices(monkeypatch, upto=5)
    pm.build_daily_series(CFG)                        # committed through 06-01

    monkeypatch.setenv('FORCE_SERIES', '1')
    _install_prices(monkeypatch, upto=4)             # deliberate shorter rebuild
    out = pm.build_daily_series(CFG)
    assert out is not None
    assert out['as_of'] == '2026-05-29'              # override wrote the shorter
    assert json.loads(pm.SERIES.read_text())['as_of'] == '2026-05-29'
