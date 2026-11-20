"""EPS YoY (Watchlist col 18) when Yahoo's earningsQuarterlyGrowth is missing.

Pure and stdlib-only so it can be tested in CI's minimal environment;
batch_score.compute_inputs converts the pandas row to a {date: value} dict.

Yahoo's earningsQuarterlyGrowth is net income, latest quarter vs the same
quarter a year earlier (HUT Q3-26 131M vs Q3-25 50M -> +162%). Yahoo returns
nothing when either quarter was a loss (QCOM after its -3.1B Q3-25; IREN's
-263M Q3-26), and sometimes returns nothing for no visible reason.

Before 2026-11-20 a missing figure left the cell blank and the refresh script
then kept that blank forever, with no recorded reason (57 names). This module
says WHY the figure is missing, and fills it from the statements when both
quarters are present and profitable:

- "loss_now": this quarter's net income is <= 0. Growth from or to a loss has
  no meaningful %, so the cell holds the stand-in LOSS_NOW_VALUE (-100,
  bottom band): a loss this quarter scores as the worst EPS growth (Dom,
  2026-11-20; a blank dropped the metric and flattered the name).
- "to_profit": year-ago quarter a loss, this quarter a profit: stand-in
  TO_PROFIT_VALUE (+100, top band); turning profitable is real growth.
- "computed": both quarters present and profitable; value computed from
  statement net income, the same measure Yahoo uses.
- "no_data": the statements cannot answer (statement lags the latest reported
  quarter, or a quarter is missing). The blank is a data gap and is flagged.
"""
from __future__ import annotations

import datetime as dt
import math

QUARTER_TOLERANCE_DAYS = 20   # statement columns are month-end normalized

LOSS_NOW, TO_PROFIT, COMPUTED, NO_DATA = "loss_now", "to_profit", "computed", "no_data"
LOSS_NOW_VALUE, TO_PROFIT_VALUE = -100.0, 100.0


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


def _near(cols: dict, target: dt.date):
    best = min(cols, key=lambda d: abs((d - target).days), default=None)
    if best is None or abs((best - target).days) > QUARTER_TOLERANCE_DAYS:
        return None
    return best


def eps_yoy_fallback(net_income: dict, latest_quarter: dt.date | None,
                     source: str = "Yahoo statements"
                     ) -> tuple[float | None, str, str]:
    """(value % or None, reason code, human note) from {quarter date: net income}.

    latest_quarter is info['mostRecentQuarter'] as a date; None means unknown,
    in which case the newest statement column is used. `source` names where
    the net income came from in the notes (sec_statements passes SEC facts).
    """
    cols = {_as_date(k): v for k, v in net_income.items()}
    if not cols:
        return None, NO_DATA, f"no quarterly net income in {source}"
    newest = max(cols)
    if latest_quarter is not None:
        cur_d = _near(cols, latest_quarter)
        if cur_d is None:
            return None, NO_DATA, (
                f"{source} end {newest}, behind the latest reported "
                f"quarter {latest_quarter} — cannot compute")
    else:
        cur_d = newest
    base_d = _near(cols, _years_back(cur_d, 1))
    if _blank(cols[cur_d]):
        return None, NO_DATA, f"quarter {cur_d} net income blank in {source}"
    cur = float(cols[cur_d])
    if cur <= 0:
        base_txt = ("" if base_d is None or _blank(cols[base_d])
                    else f" (vs {float(cols[base_d]) / 1e6:,.0f}M a year earlier)")
        return LOSS_NOW_VALUE, LOSS_NOW, (
            f"quarter {cur_d} net income {cur / 1e6:,.0f}M <= 0{base_txt} — "
            f"a loss quarter, scored as {LOSS_NOW_VALUE:+.0f} (bottom band)")
    if base_d is None or _blank(cols[base_d]):
        return None, NO_DATA, f"no year-ago quarter (near {_years_back(cur_d, 1)}) in {source}"
    base = float(cols[base_d])
    if base <= 0:
        return TO_PROFIT_VALUE, TO_PROFIT, (
            f"year-ago quarter {base_d} net income {base / 1e6:,.0f}M <= 0, now "
            f"{cur / 1e6:,.0f}M — loss to profit, scored as {TO_PROFIT_VALUE:+.0f} (top band)")
    value = round((cur / base - 1) * 100, 2)
    return value, COMPUTED, (
        f"Yahoo growth figure missing; computed from {source} net income "
        f"{cur_d} vs {base_d} ({cur / 1e6:,.0f}M vs {base / 1e6:,.0f}M)")
