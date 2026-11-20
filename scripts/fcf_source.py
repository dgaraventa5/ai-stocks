"""Free cash flow from the statements: one calculation for every FCF input.

Pure and stdlib-only so it can be tested in CI's minimal environment;
batch_score.statement_fcf converts the pandas frames to {row: {date: value}}.

Why (2026-11-20): FCF yield fell back to Yahoo's info.freeCashflow (a levered
estimate that does not reconcile to the statements) whenever the quarterly
cash-flow statement had fewer than four quarters, while EV/FCF (reverse-DCF,
Layer-10 col F) gave up. Eight names showed a positive FCF yield next to a
blank EV/FCF. DLR's "positive" yield was the Yahoo estimate; from its own
statement, development spend (filed as "Purchase Of Investment Properties")
exceeds operating cash flow.

Order:
1. Trailing four quarters, only when the four newest operating-cash-flow
   quarters are consecutive and each has a capex figure. (The old code summed
   the four newest non-blank values of each row separately, so a gap could
   mix quarters from different years.)
2. Otherwise the latest fiscal year from the annual statement, flagged with
   its date (Japanese and other foreign filers publish no quarterly cash
   flow on Yahoo).
3. Otherwise None, flagged. Never Yahoo's estimate.

Capex is "Capital Expenditure", else "Purchase Of PPE", else "Purchase Of
Investment Properties" (REITs file development spend there).
"""
from __future__ import annotations

import datetime as dt
import math

OCF = "Operating Cash Flow"
CAPEX_ROWS = ("Capital Expenditure", "Purchase Of PPE",
              "Purchase Of Investment Properties")
FOUR_QUARTER_SPAN_DAYS = (250, 300)   # newest to 4th-newest quarter end


def _as_date(k) -> dt.date:
    if isinstance(k, dt.datetime):
        return k.date()
    if isinstance(k, dt.date):
        return k
    if hasattr(k, "date"):            # pandas Timestamp
        return k.date()
    return dt.date.fromisoformat(str(k)[:10])


def _clean(row: dict | None) -> dict:
    out = {}
    for k, v in (row or {}).items():
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if not math.isnan(f):
            out[_as_date(k)] = f
    return out


def _capex(stmt: dict, dates) -> tuple[dict, str] | tuple[None, None]:
    """The first capex row that covers every date in `dates`."""
    for name in CAPEX_ROWS:
        row = _clean(stmt.get(name))
        if row and all(d in row for d in dates):
            return row, name
    return None, None


def fcf_from_statements(quarterly: dict, annual: dict
                        ) -> tuple[float | None, str]:
    """(FCF or None, note). quarterly/annual: {row name: {date: value}}."""
    q_ocf = _clean(quarterly.get(OCF))
    newest = sorted(q_ocf, reverse=True)[:4]
    if len(newest) == 4:
        span = (newest[0] - newest[3]).days
        cap, name = _capex(quarterly, newest)
        if FOUR_QUARTER_SPAN_DAYS[0] <= span <= FOUR_QUARTER_SPAN_DAYS[1] and cap:
            fcf = sum(q_ocf[d] for d in newest) - abs(sum(cap[d] for d in newest))
            note = (f"quarterly TTM to {newest[0]}" if name == CAPEX_ROWS[0]
                    else f"quarterly TTM to {newest[0]} (capex from '{name}')")
            return fcf, note

    a_ocf = _clean(annual.get(OCF))
    for d in sorted(a_ocf, reverse=True):
        cap, name = _capex(annual, [d])
        if cap:
            fcf = a_ocf[d] - abs(cap[d])
            extra = "" if name == CAPEX_ROWS[0] else f", capex from '{name}'"
            return fcf, (f"ANNUAL fiscal year {d} (no four consecutive quarters "
                         f"with capex in Yahoo's quarterly statement{extra})")
    return None, ("no statement FCF: neither four consecutive quarters nor a "
                  "fiscal year with both operating cash flow and capex")
