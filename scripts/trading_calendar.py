"""US equity trading calendar — stdlib only, rule-computed NYSE holidays.

Used by trade_ticket.build_ticket to expire tickets at the close of the Nth
US trading day after creation instead of N×24 wall-clock hours. The
scheduled executor (launchd/com.dom.aistocks.executor.plist) only attempts
execution at 06:35 PT on trading days, so a wall-clock TTL that spans a
weekend or a market holiday can lapse with zero execution attempts inside
it (2026-09-04-resize_monthly: created Friday evening, expired Sunday, first
live slot the Tuesday after Labor Day). Counting trading days makes the TTL
mean "this many execution opportunities" regardless of the calendar.

Holidays are computed from the NYSE rules (no data file to go stale):
New Year's Day, MLK Day, Presidents' Day, Good Friday, Memorial Day,
Juneteenth (observed since 2022), Independence Day, Labor Day, Thanksgiving,
Christmas. Weekend observance: Saturday → preceding Friday, Sunday →
following Monday — EXCEPT New Year's Day on a Saturday, which the NYSE does
not observe on Friday Dec 31 (the exchange was open 2021-12-31). Early
closes (13:00 ET the day after Thanksgiving and Christmas Eve) are NOT
modeled — expiry still uses 16:00 ET on those days, an over-allowance of
three hours that the executor's 09:35 ET slot never reaches into.

Ad-hoc closures (national days of mourning, e.g. 2025-01-09 for President
Carter) cannot be computed; add them to AD_HOC_CLOSURES when announced.
"""
from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York')
CLOSE_ET = dt.time(16, 0)

# Announced one-off full-day closures. YYYY-MM-DD. Keep sorted.
AD_HOC_CLOSURES: frozenset[str] = frozenset({
    '2025-01-09',   # national day of mourning, President Carter
})


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> dt.date:
    """n-th (1-based) `weekday` (Mon=0) of the month; n=-1 for the last."""
    if n > 0:
        first = dt.date(year, month, 1)
        offset = (weekday - first.weekday()) % 7
        return first + dt.timedelta(days=offset + 7 * (n - 1))
    last = (dt.date(year + (month == 12), (month % 12) + 1, 1)
            - dt.timedelta(days=1))
    offset = (last.weekday() - weekday) % 7
    return last - dt.timedelta(days=offset)


def easter(year: int) -> dt.date:
    """Gregorian Easter Sunday (anonymous / Meeus-Jones-Butcher algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return dt.date(year, month, day + 1)


def _observed(d: dt.date, *, saturday_to_friday: bool = True) -> dt.date | None:
    if d.weekday() == 5:      # Saturday
        return d - dt.timedelta(days=1) if saturday_to_friday else None
    if d.weekday() == 6:      # Sunday
        return d + dt.timedelta(days=1)
    return d


def nyse_holidays(year: int) -> set[dt.date]:
    """Full-day NYSE closures in `year` (rule-computed + AD_HOC_CLOSURES)."""
    fixed = [
        (dt.date(year, 1, 1), False),      # New Year's: no Fri observance
        (dt.date(year, 6, 19), True),      # Juneteenth
        (dt.date(year, 7, 4), True),       # Independence Day
        (dt.date(year, 12, 25), True),     # Christmas
    ]
    out: set[dt.date] = set()
    for d, sat_to_fri in fixed:
        obs = _observed(d, saturday_to_friday=sat_to_fri)
        if obs is not None:
            out.add(obs)
    if year < 2022:
        out.discard(_observed(dt.date(year, 6, 19)))   # not observed pre-2022
    # New Year's Day of NEXT year on a Sunday is observed Monday Jan 2 of
    # next year, not this year — nothing to add here. But next year's Jan 1
    # on a Saturday is simply unobserved (see module docstring).
    out.add(_nth_weekday(year, 1, 0, 3))       # MLK: 3rd Monday of Jan
    out.add(_nth_weekday(year, 2, 0, 3))       # Presidents': 3rd Mon of Feb
    out.add(easter(year) - dt.timedelta(days=2))   # Good Friday
    out.add(_nth_weekday(year, 5, 0, -1))      # Memorial: last Mon of May
    out.add(_nth_weekday(year, 9, 0, 1))       # Labor: 1st Mon of Sep
    out.add(_nth_weekday(year, 11, 3, 4))      # Thanksgiving: 4th Thu of Nov
    for s in AD_HOC_CLOSURES:
        d = dt.date.fromisoformat(s)
        if d.year == year:
            out.add(d)
    return out


def is_trading_day(d: dt.date) -> bool:
    return d.weekday() < 5 and d not in nyse_holidays(d.year)


def holiday_name(d: dt.date) -> str | None:
    """Best-effort label for a closure date (for audit strings), else None."""
    if d.weekday() >= 5 or is_trading_day(d):
        return None
    y = d.year
    names = {
        _nth_weekday(y, 1, 0, 3): 'MLK Day',
        _nth_weekday(y, 2, 0, 3): "Presidents' Day",
        easter(y) - dt.timedelta(days=2): 'Good Friday',
        _nth_weekday(y, 5, 0, -1): 'Memorial Day',
        _nth_weekday(y, 9, 0, 1): 'Labor Day',
        _nth_weekday(y, 11, 3, 4): 'Thanksgiving',
    }
    for date_, name, sat in ((dt.date(y, 1, 1), "New Year's Day", False),
                             (dt.date(y, 6, 19), 'Juneteenth', True),
                             (dt.date(y, 7, 4), 'Independence Day', True),
                             (dt.date(y, 12, 25), 'Christmas', True)):
        obs = _observed(date_, saturday_to_friday=sat)
        if obs is not None:
            names[obs] = name + (' (observed)' if obs != date_ else '')
    if d.isoformat() in AD_HOC_CLOSURES:
        return 'ad-hoc closure'
    return names.get(d, 'closure')


def next_trading_days(after: dt.date, n: int) -> list[dt.date]:
    """The first `n` trading days strictly after `after`, in order."""
    out: list[dt.date] = []
    d = after
    while len(out) < n:
        d += dt.timedelta(days=1)
        if is_trading_day(d):
            out.append(d)
    return out


def skipped_closures(start: dt.date, end: dt.date) -> list[dt.date]:
    """Weekday holidays in (start, end] — the calendar days that would have
    counted under a naive weekday rule but did not trade."""
    out = []
    d = start
    while d < end:
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and not is_trading_day(d):
            out.append(d)
    return out


def close_utc(d: dt.date) -> dt.datetime:
    """16:00 ET on `d`, as an aware UTC datetime (DST handled by zoneinfo)."""
    return dt.datetime.combine(d, CLOSE_ET, tzinfo=ET).astimezone(dt.timezone.utc)


def expiry_after_trading_days(created: dt.datetime, n: int) -> tuple[dt.datetime, str]:
    """Close of the n-th US trading day strictly after `created`'s ET date.

    Returns (aware UTC datetime, human-readable basis string for the ticket
    audit trail). The creation day itself never counts, whatever the hour:
    a ticket generated at 09:35 ET Monday and one generated at 18:00 ET
    Monday both get Tuesday and Wednesday as their n=2 sessions — the
    executor's same-day 09:35 ET attempt is a bonus, not a counted one.
    """
    if n < 1:
        raise ValueError(f'TTL must be >= 1 trading day, got {n}')
    if created.tzinfo is None:
        created = created.replace(tzinfo=dt.timezone.utc)
    anchor = created.astimezone(ET).date()
    days = next_trading_days(anchor, n)
    last = days[-1]
    skipped = skipped_closures(anchor, last)
    basis = (f'close (16:00 ET) of trading day {n} after {anchor.isoformat()} '
             f'(ET date of creation): {last.isoformat()}')
    if skipped:
        basis += ' — skipped ' + ', '.join(
            f'{s.isoformat()} ({holiday_name(s)})' for s in skipped)
    return close_utc(last), basis
