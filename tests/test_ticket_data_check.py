"""Rule 37 data check. Cases are the failures found on 2026-10-30."""
import datetime as dt

import ticket_data_check as dc

Q = dt.date(2026, 9, 30)
OK = {'rev_yoy': 40.0, 'eps_yoy': 60.0}


def flagged(t, row, overrides=None, jumps=None, quarters=None, drop=-2.0):
    return dc.flagged_buys([t], {t: row}, overrides or {}, jumps or {},
                           quarters if quarters is not None else {t: Q},
                           {t: drop}).get(t, [])


def test_clean_buy_passes():
    assert flagged('AAA', OK) == []


def test_one_off_eps_needs_a_ruling():
    row = {'rev_yoy': 25.0, 'eps_yoy': 265.0}
    assert 'EPS YoY is +265% with no ruling for this quarter' in flagged('META', row)
    ruling = {'META': {'quarter_end': '2026-09-30'}}
    assert flagged('META', row, overrides=ruling) == []


def test_big_eps_backed_by_revenue_passes():
    assert flagged('NVDA', {'rev_yoy': 60.0, 'eps_yoy': 126.0}) == []


def test_blank_eps_with_stale_ruling_is_flagged():
    row = {'rev_yoy': 25.0, 'eps_yoy': None}
    ruling = {'WDC': {'quarter_end': '2026-07-03'}}
    assert flagged('WDC', row, overrides=ruling) == [
        'EPS YoY is blank with no ruling for this quarter']


def test_failed_quarter_lookup_is_flagged():
    row = {'rev_yoy': 25.0, 'eps_yoy': None}
    assert flagged('AAA', row, quarters={'AAA': None}) == [
        'could not look up the latest reported quarter']


def test_blank_revenue_growth_is_flagged():
    assert 'revenue growth is blank' in flagged('AAA', {'rev_yoy': None, 'eps_yoy': 10.0})


def test_fall_and_failed_price_lookup_are_flagged():
    assert flagged('RDDT', OK, drop=-29.0) == ['fell 29% in 5 sessions']
    assert flagged('AAA', OK, drop=-14.9) == []
    assert flagged('AAA', OK, drop=None) == ['could not look up recent prices']


def test_unknown_ticker_is_flagged():
    assert dc.flagged_buys(['ZZZ'], {}, {}, {}, {}, {}) == {'ZZZ': ['not on the Watchlist']}


def test_score_jump_uses_the_window_only():
    rows = [{'ticker': 'META', 'date': '2026-10-10', 'total_score': '60.0'},
            {'ticker': 'META', 'date': '2026-10-24', 'total_score': '74.1'},
            {'ticker': 'META', 'date': '2026-10-29', 'total_score': '79.8'},
            {'ticker': 'AAA', 'date': '2026-10-24', 'total_score': '70.0'},
            {'ticker': 'AAA', 'date': '2026-10-29', 'total_score': '74.9'}]
    assert dc.score_jumps(rows, {'META', 'AAA'}, dt.date(2026, 10, 29)) == {'META': 5.7}
