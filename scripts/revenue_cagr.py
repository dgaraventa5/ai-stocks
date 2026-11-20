"""3-year revenue CAGR (Watchlist col 16) from Yahoo's annual income statement.

Pure and stdlib-only so it can be tested in CI's minimal environment;
batch_score.compute_inputs converts the pandas row to a {date: value} dict.

Why this exists (2026-11-19, AMAT): Yahoo adds the new fiscal-year column with
a blank (NaN) revenue weeks before the 10-K is filed. The old code took column
0 by position, got NaN, reported "non-positive base or current value", and the
refresh's keep-prior guard froze the cell on the previous three-year window
(3.23% for FY22->FY25 when FY23->FY26 was 9.11%).

Rules:
- Years are picked by date, never by position. The newest column is the end
  year; the base is the column dated about three years earlier.
- A blank newest year is filled from info['totalRevenue'] only when that TTM
  figure ends at the fiscal year end (info['mostRecentQuarter'] within
  FILL_TOLERANCE_DAYS of the column date), so TTM equals the fiscal year.
  The fill is reported as a gap note so it stays visible (rule 3).
- Otherwise a blank newest year returns None with a message naming the year.
  It never falls back to the previous window: a stale number is worse than a
  visible gap, and keep-prior already holds the last good value.
- Missing and non-positive values get different messages.
- When no column sits three years back (a fiscal-year-end change, or a year
  Yahoo dropped), the nearest column 2.5-4 years back is used and the growth
  is annualized over the real gap, with a flag. The old positional code
  treated TLN's 2021 column as three years before 2025 (13.95% vs a true
  2022->2025 2.87%) and HUT's June-2022 year as three years before Dec 2025.
"""
from __future__ import annotations

import datetime as dt
import math

FILL_TOLERANCE_DAYS = 20     # fiscal-year column dates are month-end normalized
BASE_TOLERANCE_DAYS = 45     # 52/53-week years drift a few days
SPAN_MIN, SPAN_MAX = 2.5, 4.0  # years, for the irregular-statement fallback
SHORT_MIN = 0.95             # years (52-week years run 364 days): a young company's whole history
# Stand-ins (Dom 2026-11-20, "i don't want blanked metrics"), same rule as the
# EPS loss stand-ins: growth from or to zero revenue has no meaningful %.
FROM_ZERO_VALUE = 100.0      # no revenue in the base year, revenue now: top band
TO_ZERO_VALUE = -100.0       # revenue in the base year, none now: bottom band
NO_REVENUE_VALUE = 0.0       # pre-revenue in both years: no growth


def _as_date(k) -> dt.date:
    if isinstance(k, dt.datetime):
        return k.date()
    if isinstance(k, dt.date):
        return k
    if hasattr(k, "date"):            # pandas Timestamp
        return k.date()
    return dt.date.fromisoformat(str(k)[:10])


def _blank(v) -> bool:
    if v is None:
        return True
    try:
        return math.isnan(float(v))
    except (TypeError, ValueError):
        return True


def _years_back(d: dt.date, n: int) -> dt.date:
    try:
        return d.replace(year=d.year - n)
    except ValueError:                # Feb 29
        return d.replace(year=d.year - n, day=28)


def _ttm_fill(newest: dt.date, info: dict) -> float | None:
    rev, mrq = info.get("totalRevenue"), info.get("mostRecentQuarter")
    if _blank(rev) or _blank(mrq) or float(rev) <= 0:
        return None
    q_end = dt.datetime.fromtimestamp(float(mrq), dt.timezone.utc).date()
    if abs((q_end - newest).days) > FILL_TOLERANCE_DAYS:
        return None
    return float(rev)


def rev_3y_cagr(revenue: dict, info: dict | None = None
                ) -> tuple[float | None, list[str]]:
    """(CAGR % rounded to 2dp or None, gap notes) from {fiscal-year date: revenue}."""
    info = info or {}
    rows = sorted(((_as_date(k), v) for k, v in revenue.items()),
                  key=lambda kv: kv[0], reverse=True)
    if len(rows) < 2:
        return None, [f"Rev 3y CAGR: only {len(rows)} year of data"]

    gaps: list[str] = []
    newest, r_now = rows[0]
    if _blank(r_now):
        r_now = _ttm_fill(newest, info)
        if r_now is None:
            return None, [f"Rev 3y CAGR: newest fiscal year {newest} revenue is "
                          "blank in Yahoo (10-K not yet loaded); left to keep-prior"]
        gaps.append(f"Rev 3y CAGR: fiscal year {newest} revenue blank in Yahoo; "
                    f"used info.totalRevenue ({r_now / 1e6:,.0f}M, TTM to the "
                    "fiscal year end)")

    target = _years_back(newest, 3)
    base = [(d, v) for d, v in rows[1:]
            if abs((d - target).days) <= BASE_TOLERANCE_DAYS]
    span = 3.0
    if not base:
        # No column three years back: a fiscal-year-end change (HUT, RCAT,
        # 6383.T) or a year Yahoo dropped. Use the nearest earlier column in the
        # SPAN_MIN..SPAN_MAX window and annualize over the real gap, flagged.
        # The old code treated whatever sat in position 3 as three years back.
        near = [(d, v) for d, v in rows[1:] if not _blank(v)
                and SPAN_MIN <= (newest - d).days / 365.25 <= SPAN_MAX]
        if not near:
            # A young company (SPCX, WYFI, TE on 2026-11-20): annualize its
            # whole history when it covers at least SHORT_MIN years, flagged.
            dated = [(d, v) for d, v in rows[1:] if not _blank(v)]
            young = [(d, v) for d, v in dated
                     if (newest - d).days / 365.25 >= SHORT_MIN]
            # Only when the whole history is short: an older year means the
            # three-year base is a gap, not a young company.
            if not young or max((newest - d).days for d, _ in dated) / 365.25 >= SPAN_MIN:
                return None, gaps + [f"Rev 3y CAGR: base year {target} revenue missing"]
            base = [min(young, key=lambda dv: dv[0])]
            span = (newest - base[0][0]).days / 365.25
            gaps.append(f"Rev 3y CAGR: SHORT HISTORY — annualized over "
                        f"{base[0][0]} -> {newest} ({span:.2f} years)")
            near = None
        if near:
            # prefer a base at least three years back (the nearest one); fall
            # back to a shorter span only when none exists
            older = [dv for dv in near if dv[0] <= target]
            base = [max(older, key=lambda dv: dv[0]) if older
                    else min(near, key=lambda dv: dv[0])]
            span = (newest - base[0][0]).days / 365.25
            gaps.append(f"Rev 3y CAGR: no fiscal year near {target}; annualized over "
                        f"{base[0][0]} -> {newest} ({span:.2f} years). Check for a "
                        "fiscal-year-end change or a short transition period")
    if _blank(base[0][1]):
        return None, gaps + [f"Rev 3y CAGR: base year {base[0][0]} revenue missing"]
    base_d, r_3y = base[0]
    r_3y = float(r_3y)
    r_now = float(r_now)
    if r_3y <= 0 or r_now <= 0:
        v = (NO_REVENUE_VALUE if r_3y <= 0 and r_now <= 0
             else FROM_ZERO_VALUE if r_3y <= 0 else TO_ZERO_VALUE)
        return v, gaps + [f"Rev 3y CAGR: revenue {r_3y / 1e6:,.1f}M ({base_d}) -> "
                          f"{r_now / 1e6:,.1f}M ({newest}); growth from or to zero "
                          f"has no %, scored as {v:+.0f}"]
    return round(((r_now / r_3y) ** (1 / span) - 1) * 100, 2), gaps


YOY_TOLERANCE_DAYS = 20      # quarterly columns are month-end normalized


def rev_yoy_fallback(quarterly: dict, latest_quarter: dt.date | None = None
                     ) -> tuple[float | None, str]:
    """Revenue YoY (col 17) from quarterly revenue when Yahoo's revenueGrowth
    is missing, which it is whenever the year-ago quarter had no revenue
    (UEC, OKLO, NNE on 2026-11-20). Same stand-ins as the CAGR: from zero
    FROM_ZERO_VALUE, to zero TO_ZERO_VALUE, zero both NO_REVENUE_VALUE.
    Returns (None, reason) only when the quarters are not in the statement."""
    cols = {_as_date(k): float(v) for k, v in quarterly.items() if not _blank(v)}
    if not cols:
        return None, "no quarterly revenue in the statement"

    def near(target):
        best = min(cols, key=lambda d: abs((d - target).days))
        return best if abs((best - target).days) <= YOY_TOLERANCE_DAYS else None

    cur = near(latest_quarter) if latest_quarter else max(cols)
    if cur is None:
        return None, (f"statement ends {max(cols)}, behind the latest reported "
                      f"quarter {latest_quarter}")
    base = near(_years_back(cur, 1))
    if base is None:
        return None, f"no year-ago quarter (near {_years_back(cur, 1)})"
    now, then = cols[cur], cols[base]
    if then <= 0 or now <= 0:
        v = (NO_REVENUE_VALUE if then <= 0 and now <= 0
             else FROM_ZERO_VALUE if then <= 0 else TO_ZERO_VALUE)
        return v, (f"quarter {cur} revenue {now / 1e6:,.1f}M vs {then / 1e6:,.1f}M "
                   f"a year earlier; growth from or to zero has no %, scored as {v:+.0f}")
    return round((now / then - 1) * 100, 2), (
        f"computed from statement revenue {cur} vs {base}")
