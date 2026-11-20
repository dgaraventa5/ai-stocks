"""Tests for scripts/revenue_cagr.py — 3-year revenue CAGR from Yahoo's annual
income statement. Offline, stdlib only (no pandas/yfinance in this chain).

The bug these cover (AMAT, 2026-11-19): Yahoo adds the new fiscal-year column
with a blank (NaN) revenue weeks before the 10-K is filed. The old code took
column 0 by position, got NaN, reported "non-positive base or current value",
and the refresh's keep-prior guard froze the cell on the previous window.
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import revenue_cagr as rc  # noqa: E402

NAN = float("nan")
D = dt.date


def _amat(newest=NAN):
    return {D(2026, 10, 31): newest, D(2025, 10, 31): 28_368e6,
            D(2024, 10, 31): 27_176e6, D(2023, 10, 31): 26_517e6,
            D(2022, 10, 31): 25_785e6}


AMAT_INFO = {"totalRevenue": 34_446e6,
             "mostRecentQuarter": 1792886400}  # 2026-10-25, fiscal Q4 end


def test_complete_statement_uses_newest_year_and_three_back():
    v, gaps = rc.rev_3y_cagr(_amat(34_446e6), {})
    assert v == 9.11 and gaps == []


def test_blank_newest_year_filled_from_ttm_when_it_ends_at_fiscal_year_end():
    v, gaps = rc.rev_3y_cagr(_amat(), AMAT_INFO)
    assert v == 9.11
    assert len(gaps) == 1 and "2026-10-31" in gaps[0] and "totalRevenue" in gaps[0]


def test_blank_newest_year_without_matching_ttm_returns_none_and_says_why():
    # latest quarter ended mid-year: TTM is not the fiscal year, so no fill
    info = {"totalRevenue": 33e9, "mostRecentQuarter": 1785196800}  # 2026-07-28
    v, gaps = rc.rev_3y_cagr(_amat(), info)
    assert v is None
    assert "2026-10-31" in gaps[0] and "blank" in gaps[0]
    assert "non-positive" not in gaps[0]


def test_blank_newest_year_with_no_info_returns_none():
    v, gaps = rc.rev_3y_cagr(_amat(), {})
    assert v is None and "blank" in gaps[0]


def test_never_falls_back_to_the_previous_window():
    # the stale FY22->FY25 answer (3.23) must not come back silently
    v, _ = rc.rev_3y_cagr(_amat(), {})
    assert v != 3.23


def test_base_is_chosen_by_date_not_position():
    # an old placeholder column in the middle must not shift the base year
    rev = _amat(34_446e6)
    rev[D(2021, 10, 31)] = 23_063e6
    v, _ = rc.rev_3y_cagr(rev, {})
    assert v == 9.11


def test_missing_base_year_is_reported_as_missing():
    rev = _amat(34_446e6)
    rev[D(2023, 10, 31)] = NAN
    v, gaps = rc.rev_3y_cagr(rev, {})
    assert v is None and "2023-10-31" in gaps[0] and "missing" in gaps[0]


def test_growth_from_zero_revenue_is_a_top_band_stand_in():
    # Stand-ins, not blanks (Dom 2026-11-20): from or to zero has no %
    rev = _amat(34_446e6)
    rev[D(2023, 10, 31)] = -5e6
    v, gaps = rc.rev_3y_cagr(rev, {})
    assert v == rc.FROM_ZERO_VALUE and "growth from or to zero" in gaps[0]


def test_revenue_falling_to_zero_and_pre_revenue_stand_ins():
    base = {D(2026, 12, 31): 0.0, D(2025, 12, 31): 1e6, D(2024, 12, 31): 1e6,
            D(2023, 12, 31): 2e6}
    assert rc.rev_3y_cagr(base, {})[0] == rc.TO_ZERO_VALUE
    base[D(2023, 12, 31)] = 0.0
    assert rc.rev_3y_cagr(base, {})[0] == rc.NO_REVENUE_VALUE


def test_short_history_is_annualized_and_flagged():
    # young company: two fiscal years only
    v, gaps = rc.rev_3y_cagr({D(2026, 10, 31): 1e9, D(2025, 10, 31): 8e8}, {})
    assert v == 25.02 and "SHORT HISTORY" in gaps[0]   # 365-day year
    v, gaps = rc.rev_3y_cagr({D(2026, 10, 31): 1e9}, {})
    assert v is None and "1 year" in gaps[0]


def test_accepts_datetime_keys_and_unsorted_input():
    rev = {dt.datetime(2022, 10, 31): 25_785e6, dt.datetime(2026, 10, 31): 34_446e6,
           dt.datetime(2024, 10, 31): 27_176e6, dt.datetime(2023, 10, 31): 26_517e6}
    v, _ = rc.rev_3y_cagr(rev, {})
    assert v == 9.11


def test_missing_year_uses_the_true_three_year_base_not_position_three():
    # TLN: Yahoo has no 2023 column; position 3 is 2021, four years back
    tln = {D(2025, 12, 31): 2_626e6, D(2024, 12, 31): 2_073e6,
           D(2022, 12, 31): 2_412e6, D(2021, 12, 31): 1_775e6}
    v, gaps = rc.rev_3y_cagr(tln, {})
    assert v == 2.87 and gaps == []


def test_fiscal_year_change_annualizes_over_the_real_gap_and_flags_it():
    # HUT: June fiscal years, then December; nothing sits at 2022-12-31
    hut = {D(2025, 12, 31): 235_118e3, D(2024, 12, 31): 162_385e3,
           D(2023, 6, 30): 86_737e3, D(2022, 6, 30): 79_185e3}
    v, gaps = rc.rev_3y_cagr(hut, {})
    span = (D(2025, 12, 31) - D(2022, 6, 30)).days / 365.25
    assert v == round(((235_118 / 79_185) ** (1 / span) - 1) * 100, 2)
    assert len(gaps) == 1 and "annualized" in gaps[0] and "2022-06-30" in gaps[0]


def test_no_base_in_the_fallback_window_returns_none():
    rev = {D(2026, 12, 31): 5e9, D(2025, 12, 31): 4e9, D(2024, 12, 31): 3e9,
           D(2021, 12, 31): 2e9}           # 5 years back: outside 2.5-4
    v, gaps = rc.rev_3y_cagr(rev, {})
    assert v is None and "missing" in gaps[0]
