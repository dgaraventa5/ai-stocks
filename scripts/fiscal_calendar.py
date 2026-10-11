"""Rule 36 (2026-10-10): forward P/E on a common calendar year.

yfinance `forwardPE` is price over NEXT-FISCAL-YEAR consensus EPS, which is a
different twelve months for the third of the watchlist without a December
year-end. On a fast grower the later window flatters the multiple (WDC 13.1 on
fiscal 2028 vs 16.1 on calendar 2027). Off-cycle names blend their current-year
(`0y`) and next-year (`+1y`) consensus by the share of the target calendar year
each covers. Pure, offline, stdlib only — the caller supplies the estimates.

Spec: docs/superpowers/specs/2026-10-10-forward-pe-calendar-year-design.md
"""
from __future__ import annotations

import datetime as dt


def target_year(today: dt.date) -> int:
    """The calendar year December-year companies' forward estimate refers to.

    They report the prior year by the end of February, after which yfinance's
    "next fiscal year" is the following calendar year. In January-February some
    have rolled and some have not; the convention stays on the earlier year for
    those weeks (documented approximation, cautious for growers).
    """
    current_fy = today.year if today.month >= 3 else today.year - 1
    return current_fy + 1


def _shift_year(d: dt.date, years: int) -> dt.date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:               # Feb 29
        return d.replace(year=d.year + years, day=28)


def _overlap_days(start_excl: dt.date, end_incl: dt.date, year: int) -> int:
    lo = max(start_excl + dt.timedelta(days=1), dt.date(year, 1, 1))
    hi = min(end_incl, dt.date(year, 12, 31))
    return max((hi - lo).days + 1, 0)


def calendar_year_eps(eps_0y: float, eps_1y: float, fy_end: dt.date,
                      year: int) -> float:
    """Consensus EPS for calendar `year`, from the two fiscal-year estimates.

    `fy_end` is the end of the CURRENT fiscal year (the `0y` estimate); `+1y`
    ends one year later. Any part of `year` after the `+1y` window has no
    estimate and takes `+1y` — the cautious direction when earnings grow.
    """
    days = (dt.date(year, 12, 31) - dt.date(year, 1, 1)).days + 1
    w0 = _overlap_days(_shift_year(fy_end, -1), fy_end, year) / days
    return w0 * eps_0y + (1.0 - w0) * eps_1y


def calendar_year_forward_pe(raw_pe: float | None, eps_0y: float | None,
                             eps_1y: float | None, fy_end: dt.date | None,
                             today: dt.date | None = None
                             ) -> tuple[float | None, list[str]]:
    """Forward P/E restated to the common calendar year, plus log flags.

    Scales the raw multiple by (+1y EPS / calendar-year EPS) so price and the
    data vendor's EPS basis are untouched. Never lowers a multiple; keeps the
    raw value (flagged) on missing or non-positive inputs.
    """
    if raw_pe is None or raw_pe <= 0:
        return raw_pe, []
    if (fy_end is None or eps_0y is None or eps_1y is None
            or eps_0y != eps_0y or eps_1y != eps_1y):      # None or NaN
        return raw_pe, ['calendar-year P/E: estimates or fiscal year end '
                        'missing — kept raw']
    if eps_0y <= 0 or eps_1y <= 0:
        return raw_pe, ['calendar-year P/E: non-positive consensus EPS — '
                        'kept raw']
    year = target_year(today or dt.date.today())
    cal = calendar_year_eps(eps_0y, eps_1y, fy_end, year)
    if cal <= 0:
        return raw_pe, ['calendar-year P/E: non-positive blended EPS — kept raw']
    adj = raw_pe * eps_1y / cal
    if adj < raw_pe * (1 - 1e-9):
        return raw_pe, [f'calendar-year P/E: blend would LOWER the multiple '
                        f'({raw_pe:.1f} -> {adj:.1f}; 0y estimate above +1y) — '
                        f'kept raw']
    return adj, []
