"""The day's close reaches the series as soon as the session ends (2026-10-13).

Yahoo serves a fresh session's daily row with a blank adjusted close for
hours after the bell; auto_adjust + dropna dropped the day, so post-close
refreshes re-published the prior day.
"""
import datetime as dt

import pytest

pd = pytest.importorskip('pandas')

import portfolio_model as pm

IDX = pd.DatetimeIndex(['2026-10-09', '2026-10-12', '2026-10-13']).tz_localize('America/New_York')
CLOSE_1013 = int(dt.datetime(2026, 10, 13, 20, 0, tzinfo=dt.timezone.utc).timestamp())
NY = {'exchangeTimezoneName': 'America/New_York'}


@pytest.fixture(autouse=True)
def quiet(monkeypatch):
    monkeypatch.setattr(pm, 'flag', lambda *a, **k: None)


def hist(adj, close=(100.0, 101.0, 102.0), n=3):
    return pd.DataFrame({'Close': list(close)[:n], 'Adj Close': list(adj)[:n]},
                        index=IDX[:n])


def test_blank_adjusted_close_on_newest_row_uses_raw_close():
    s = pm._adjusted_closes('X', hist([99.0, 100.0, float('nan')]), {})
    assert list(s) == [99.0, 100.0, 102.0]


def test_blank_adjusted_close_on_older_row_is_still_dropped():
    s = pm._adjusted_closes('X', hist([float('nan'), 100.0, 101.0]), {})
    assert list(s.index.date) == [dt.date(2026, 10, 12), dt.date(2026, 10, 13)]


def test_missing_session_row_takes_the_official_close():
    meta = {**NY, 'regularMarketPrice': 103.5, 'regularMarketTime': CLOSE_1013}
    s = pm._adjusted_closes('X', hist([99.0, 100.0], n=2), meta)
    assert s.index[-1].date() == dt.date(2026, 10, 13) and s.iloc[-1] == 103.5
    assert str(s.index.tz) == 'America/New_York'


def test_no_append_before_the_close_or_for_foreign_listings():
    before = {**NY, 'regularMarketPrice': 103.5, 'regularMarketTime': CLOSE_1013 - 3600}
    assert len(pm._adjusted_closes('X', hist([99.0, 100.0], n=2), before)) == 2
    tokyo = {'exchangeTimezoneName': 'Asia/Tokyo', 'regularMarketPrice': 1.0,
             'regularMarketTime': CLOSE_1013}
    assert len(pm._adjusted_closes('X', hist([99.0, 100.0], n=2), tokyo)) == 2


def test_present_row_is_not_overwritten():
    meta = {**NY, 'regularMarketPrice': 999.0, 'regularMarketTime': CLOSE_1013}
    s = pm._adjusted_closes('X', hist([99.0, 100.0, 101.0]), meta)
    assert list(s) == [99.0, 100.0, 101.0]
