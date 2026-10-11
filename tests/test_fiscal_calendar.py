"""Rule 36: forward P/E on a common calendar year."""
import datetime as dt

import pytest

import fiscal_calendar as fc


def test_target_year_follows_december_reporters():
    # December-year companies have reported the prior year by March.
    assert fc.target_year(dt.date(2026, 10, 10)) == 2027
    assert fc.target_year(dt.date(2027, 3, 1)) == 2028
    assert fc.target_year(dt.date(2027, 2, 15)) == 2027


def test_wdc_worked_example_blends_two_fiscal_years():
    # FY ends 2027-07-03: fiscal 2027 covers Jan 1-Jul 3 (184 days) of 2027.
    eps = fc.calendar_year_eps(20.12, 31.83, dt.date(2027, 7, 3), 2027)
    assert eps == pytest.approx((184 * 20.12 + 181 * 31.83) / 365, abs=1e-6)
    assert 25.8 < eps < 26.0


def test_december_year_end_is_untouched():
    # 0y = FY2026 (ends 2026-12-31), +1y = FY2027 = the whole target year.
    assert fc.calendar_year_eps(5.0, 7.0, dt.date(2026, 12, 31), 2027) == pytest.approx(7.0)


def test_part_of_year_beyond_next_estimate_uses_next_estimate():
    # AVGO-shaped: FY ends 2026-11-01, +1y ends 2027-11-01; Nov-Dec 2027 has
    # no estimate, so +1y stands in -> blended figure equals +1y.
    assert fc.calendar_year_eps(11.66, 19.39, dt.date(2026, 11, 1), 2027) == pytest.approx(19.39)


def test_january_year_end_is_nearly_all_next_year():
    eps = fc.calendar_year_eps(9.31, 15.91, dt.date(2027, 1, 25), 2027)
    assert eps == pytest.approx((25 * 9.31 + 340 * 15.91) / 365, abs=1e-6)


def test_forward_pe_raised_for_off_cycle_grower():
    pe, flags = fc.calendar_year_forward_pe(13.09, 20.12, 31.83,
                                            dt.date(2027, 7, 3),
                                            today=dt.date(2026, 10, 10))
    assert pe == pytest.approx(13.09 * 31.83 / ((184 * 20.12 + 181 * 31.83) / 365))
    assert 16.0 < pe < 16.2 and flags == []


def test_never_lowers_the_pe():
    # PANW-shaped: current-year estimate above next-year -> blend would
    # LOWER the multiple. Keep raw and say so.
    pe, flags = fc.calendar_year_forward_pe(88.0, 4.0, 2.6, dt.date(2027, 7, 31),
                                            today=dt.date(2026, 10, 10))
    assert pe == 88.0
    assert any('kept raw' in f for f in flags)


@pytest.mark.parametrize('raw,e0,e1', [
    (None, 1.0, 2.0), (-5.0, 1.0, 2.0), (20.0, None, 2.0), (20.0, 1.0, None),
    (20.0, 1.0, -2.0), (20.0, -3.0, 2.0),
    (20.0, float('nan'), 2.0), (20.0, 1.0, float('nan')),
])
def test_missing_or_non_positive_inputs_keep_raw(raw, e0, e1):
    pe, flags = fc.calendar_year_forward_pe(raw, e0, e1, dt.date(2027, 7, 3),
                                            today=dt.date(2026, 10, 10))
    assert pe == raw
    if raw and raw > 0:
        assert flags and 'kept raw' in flags[0]


def test_december_name_returns_raw_without_flags():
    pe, flags = fc.calendar_year_forward_pe(22.0, 5.0, 7.0, dt.date(2026, 12, 31),
                                            today=dt.date(2026, 10, 10))
    assert pe == 22.0 and flags == []
