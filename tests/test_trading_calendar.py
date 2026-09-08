"""NYSE trading calendar (stdlib, rule-computed) — feeds ticket expiry.

Holiday dates below are the NYSE's published 2026 schedule; the weekend-
observance edge cases (Sat July 4 → Fri; Sat Jan 1 → NOT observed) are the
ones a naive rule gets wrong.
"""
import datetime as dt

import pytest

import trading_calendar as tc


def d(s):
    return dt.date.fromisoformat(s)


def test_nyse_2026_published_schedule():
    assert sorted(tc.nyse_holidays(2026)) == [
        d('2026-01-01'),   # New Year's Day (Thu)
        d('2026-01-19'),   # MLK Day
        d('2026-02-16'),   # Presidents' Day
        d('2026-04-03'),   # Good Friday
        d('2026-05-25'),   # Memorial Day
        d('2026-06-19'),   # Juneteenth (Fri)
        d('2026-07-03'),   # Independence Day observed (Jul 4 = Sat)
        d('2026-09-07'),   # Labor Day
        d('2026-11-26'),   # Thanksgiving
        d('2026-12-25'),   # Christmas (Fri)
    ]


def test_new_years_on_saturday_is_not_observed_on_friday():
    # 2022-01-01 was a Saturday; the NYSE traded on Fri 2021-12-31.
    assert tc.is_trading_day(d('2021-12-31'))
    assert d('2021-12-31') not in tc.nyse_holidays(2021)


def test_sunday_holiday_observed_monday():
    # 2023-01-01 Sunday → Mon 2023-01-02 closed
    assert not tc.is_trading_day(d('2023-01-02'))


def test_juneteenth_not_observed_before_2022():
    assert d('2021-06-18') not in tc.nyse_holidays(2021)   # Sat 19th → Fri
    assert d('2023-06-19') in tc.nyse_holidays(2023)


def test_ad_hoc_closure_carter_2025():
    assert not tc.is_trading_day(d('2025-01-09'))
    assert tc.holiday_name(d('2025-01-09')) == 'ad-hoc closure'


@pytest.mark.parametrize('year,expected', [
    (2024, '2024-03-31'), (2025, '2025-04-20'), (2026, '2026-04-05'),
    (2027, '2027-03-28'),
])
def test_easter(year, expected):
    assert tc.easter(year) == d(expected)


def test_weekends_never_trade():
    assert not tc.is_trading_day(d('2026-09-05'))   # Sat
    assert not tc.is_trading_day(d('2026-09-06'))   # Sun
    assert tc.is_trading_day(d('2026-09-08'))       # Tue after Labor Day


def test_next_trading_days_skips_weekend_and_holiday():
    assert tc.next_trading_days(d('2026-09-04'), 2) == [d('2026-09-08'),
                                                         d('2026-09-09')]
    assert tc.next_trading_days(d('2026-08-12'), 2) == [d('2026-08-13'),
                                                         d('2026-08-14')]


def test_close_utc_tracks_dst():
    assert tc.close_utc(d('2026-09-08')).isoformat() == '2026-09-08T20:00:00+00:00'
    assert tc.close_utc(d('2026-12-22')).isoformat() == '2026-12-22T21:00:00+00:00'


def test_expiry_anchors_on_et_date_not_utc_date():
    # 01:30Z Saturday is still 21:30 ET Friday → Friday is the anchor.
    created = dt.datetime(2026, 8, 15, 1, 30, tzinfo=dt.timezone.utc)
    exp, basis = tc.expiry_after_trading_days(created, 2)
    assert exp.isoformat() == '2026-08-18T20:00:00+00:00'     # Tue close
    assert 'after 2026-08-14' in basis


def test_expiry_rejects_zero_ttl():
    with pytest.raises(ValueError):
        tc.expiry_after_trading_days(
            dt.datetime(2026, 9, 4, tzinfo=dt.timezone.utc), 0)
