"""Rule 37 data check. Cases are the failures found on 2026-10-30."""
import datetime as dt

import ticket_data_check as dc

OK = {'rev_yoy': 40.0}


def flagged(t, row, jumps=None, drop=-2.0):
    return dc.flagged_buys([t], {t: row}, jumps or {}, {t: drop}).get(t, [])


def test_clean_buy_passes():
    assert flagged('AAA', OK) == []


def test_eps_is_no_longer_checked():
    # 2026-11-20: rule 15 now writes the reported EPS figure, so the data
    # check no longer asks for EPS rulings (it used to hold META's +265% buy)
    assert flagged('META', {'rev_yoy': 25.0, 'eps_yoy': 265.0}) == []
    assert flagged('WDC', {'rev_yoy': 25.0, 'eps_yoy': None}) == []


def test_blank_revenue_growth_is_flagged():
    assert 'revenue growth is blank' in flagged('AAA', {'rev_yoy': None})


def test_fall_and_failed_price_lookup_are_flagged():
    assert flagged('RDDT', OK, drop=-29.0) == ['fell 29% in 5 sessions']
    assert flagged('AAA', OK, drop=-14.9) == []
    assert flagged('AAA', OK, drop=None) == ['could not look up recent prices']


def test_unknown_ticker_is_flagged():
    assert dc.flagged_buys(['ZZZ'], {}, {}, {}) == {'ZZZ': ['not on the Watchlist']}


def test_score_jump_uses_the_window_only():
    rows = [{'ticker': 'META', 'date': '2026-10-10', 'total_score': '60.0'},
            {'ticker': 'META', 'date': '2026-10-24', 'total_score': '74.1'},
            {'ticker': 'META', 'date': '2026-10-29', 'total_score': '79.8'},
            {'ticker': 'AAA', 'date': '2026-10-24', 'total_score': '70.0'},
            {'ticker': 'AAA', 'date': '2026-10-29', 'total_score': '74.9'}]
    assert dc.score_jumps(rows, {'META', 'AAA'}, dt.date(2026, 10, 29)) == {'META': 5.7}
