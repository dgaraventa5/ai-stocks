"""Chain-linked EW benchmark: a roster re-baseline must splice continuously
and inject no look-ahead.

The EW universe was frozen at the 2026-05-25 roster. When it is re-baselined
to the current >=70 universe, the series must keep the OLD roster before the
splice date and the NEW roster after — so the since-inception alpha stays a
valid skill test (names that ran INTO the >=70 set don't get retroactive
credit). See portfolio_model.ew_growth / ew_roster_events.
"""
import pytest

pytest.importorskip('yfinance')          # pm imports yfinance at module level
pd = pytest.importorskip('pandas')

import portfolio_model as pm

DATES = pd.to_datetime(
    ['2026-05-26', '2026-05-27', '2026-05-28', '2026-05-29', '2026-06-01'])
# AAA rises 10%/day throughout. BBB is flat through the splice, then +20%/day.
PRICES = {
    'SMH': [10, 10, 10, 10, 10],         # only used to source the calendar
    'AAA': [100, 110, 121, 133, 146],
    'BBB': [50, 50, 60, 72, 72],
}


@pytest.fixture
def fake_prices(monkeypatch):
    def fake_series(ticker, earliest):
        if ticker not in PRICES:
            return None
        return pd.Series(PRICES[ticker], index=DATES, dtype=float)
    pm._series_cache.clear()
    monkeypatch.setattr(pm, '_series', fake_series)


def test_chainlink_splices_continuously_without_lookahead(fake_prices):
    cfg = {
        'inception': '2026-05-26',
        'ew_events': [
            {'date': '2026-05-26', 'roster': ['AAA']},
            {'date': '2026-05-28', 'roster': ['BBB']},   # re-baseline splice
        ],
    }
    ew = pm.ew_growth(cfg)
    vals = [round(float(v), 4) for v in ew.reindex(DATES)]

    # Before splice: follows AAA only (BBB's flat pre-splice prices irrelevant).
    assert vals[0] == 1.0
    assert vals[1] == pytest.approx(1.1)           # AAA 100->110

    # Splice day reflects BBB's REAL move off the prior close (60/50 = +20%),
    # carried from the level the old roster reached — not a neutral 0% day,
    # and NOT influenced by AAA's continued climb to 133/146.
    assert vals[2] == pytest.approx(1.1 * 1.2)     # 1.32
    assert vals[3] == pytest.approx(1.1 * (72 / 50))   # 1.584
    assert vals[4] == pytest.approx(1.1 * (72 / 50))   # 1.584

    # Look-ahead guard: AAA's post-splice return must not leak in. A naive
    # full-rewrite holding BBB from inception would instead give BBB growth-of-1
    # = 72/50 = 1.44 on the last day; chain-link gives 1.584. They must differ.
    assert vals[4] != pytest.approx(72 / 50)


def test_legacy_flat_roster_still_works(fake_prices):
    """No ew_events -> single inception-dated roster from ew_universe."""
    cfg = {'inception': '2026-05-26', 'ew_universe': ['AAA']}
    ew = pm.ew_growth(cfg)
    vals = [round(float(v), 4) for v in ew.reindex(DATES)]
    assert vals == [1.0, 1.1, 1.21, 1.33, 1.46]     # pure AAA growth-of-1


def test_roster_events_normalizes_and_sorts():
    cfg = {'inception': '2026-05-26',
           'ew_events': [{'date': '2026-05-28', 'roster': ['B']},
                         {'date': '2026-05-26', 'roster': ['A']}]}
    evs = pm.ew_roster_events(cfg)
    assert [e['date'] for e in evs] == ['2026-05-26', '2026-05-28']

    legacy = {'inception': '2026-05-26', 'ew_universe': ['A', 'B']}
    evs = pm.ew_roster_events(legacy)
    assert evs == [{'date': '2026-05-26', 'roster': ['A', 'B']}]
