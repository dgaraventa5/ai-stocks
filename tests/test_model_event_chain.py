"""Model valuation is chain-linked from prices (2026-10-13).

Root cause: the series walk and mark() re-based each event on the first close
ON OR AFTER its date and trusted the event's stored dollars. The 2026-10-11
(Sunday) event was valued at Friday's close, so Monday's return vanished —
the model printed 10609.29 on both 10-09 and 10-12 while every benchmark
moved. Same on 2026-08-03 and 2026-09-08.
"""
import pytest

pytest.importorskip('yfinance')
pd = pytest.importorskip('pandas')

import portfolio_model as pm

# Thu, Fri, Mon, Tue — the event lands on the Sunday in between.
DATES = pd.to_datetime(['2026-10-08', '2026-10-09', '2026-10-12', '2026-10-13'])
PRICES = {'SMH': [10, 10, 10, 10], 'QQQ': [10, 10, 10, 10],
          'SPY': [10, 10, 10, 10],
          'AAA': [100, 100, 110, 110],      # +10% on Monday
          'BBB': [50, 55, 55, 55]}          # +10% on Friday

CFG = {
    'inception': '2026-10-08', 'capital': 1000.0, 'ew_universe': ['AAA'],
    'events': [
        {'date': '2026-10-08', 'reason': 'init',
         'allocations': {'BBB': 1000.0}, 'cash': 0.0},
        # Sunday rotation into AAA, priced at Friday's close (1100)
        {'date': '2026-10-11', 'reason': 'rotate',
         'allocations': {'AAA': 1100.0}, 'cash': 0.0},
    ],
}


@pytest.fixture(autouse=True)
def fake_prices(monkeypatch, tmp_path):
    def fake_series(ticker, earliest):
        if ticker not in PRICES:
            return None
        return pd.Series(PRICES[ticker], index=DATES, dtype=float)
    pm._series_cache.clear()
    monkeypatch.setattr(pm, '_series', fake_series)
    monkeypatch.setattr(pm, 'SERIES', tmp_path / 'series.json')
    monkeypatch.setattr(pm, 'flag', lambda *a, **k: None)


def test_weekend_event_keeps_mondays_return():
    out = pm.build_daily_series(CFG)
    assert out['model'] == [1000.0, 1100.0, 1210.0, 1210.0]


def test_stale_event_dollars_are_weights_not_levels():
    # An event whose stored total is wrong (here: the old bug's flat value)
    # must not inject a jump — the level comes from the previous book.
    cfg = {**CFG, 'events': [CFG['events'][0],
                             {**CFG['events'][1],
                              'allocations': {'AAA': 900.0}}]}
    out = pm.build_daily_series(cfg)
    assert out['model'] == [1000.0, 1100.0, 1210.0, 1210.0]


def test_trading_day_event_switches_at_that_close():
    # Event dated Monday: Monday's return belongs to the OLD book (BBB, flat).
    cfg = {**CFG, 'events': [CFG['events'][0],
                             {**CFG['events'][1], 'date': '2026-10-12'}]}
    out = pm.build_daily_series(cfg)
    assert out['model'] == [1000.0, 1100.0, 1100.0, 1100.0]


def test_mark_agrees_with_series_and_ret_since_uses_fridays_close():
    out = pm.build_daily_series(CFG)
    value, pnl, missing = pm.mark(CFG)
    assert value == pytest.approx(out['model'][-1])
    assert pnl == {'AAA': pytest.approx(110.0)} and missing == []
    assert pm.ret_since('AAA', '2026-10-11', CFG['inception']) == pytest.approx(0.10)
    assert pm.event_levels(CFG) == pytest.approx([1000.0, 1100.0])


def test_held_since_dates_from_the_current_stretch():
    events = [{'date': '2026-01-01', 'allocations': {'AAA': 1}},
              {'date': '2026-02-01', 'allocations': {'BBB': 1}},
              {'date': '2026-03-01', 'allocations': {'AAA': 1, 'BBB': 1}},
              {'date': '2026-04-01', 'allocations': {'AAA': 1, 'BBB': 1}}]
    assert pm.held_since(events, 'AAA') == '2026-03-01'   # re-entry restarts
    assert pm.held_since(events, 'BBB') == '2026-02-01'
    assert pm.held_since(events, 'CCC') is None


def test_holdings_block_prices_from_the_entry_close():
    # AAA entered on the Sunday event: base = Friday's close (100), so
    # Monday's +10% counts; SPY flat, so vs_spy == ret.
    out = pm.build_daily_series(CFG)
    h = out['holdings']
    assert set(h) == {'AAA'}
    assert h['AAA']['since'] == '2026-10-11'
    assert h['AAA']['ret'] == pytest.approx(0.10)
    assert h['AAA']['vs_spy'] == pytest.approx(0.10)
    assert h['AAA']['spark'] == [1.0, 1.1, 1.1]          # Fri, Mon, Tue
