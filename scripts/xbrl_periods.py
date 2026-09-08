"""Decompose SEC companyfacts period frames into a true quarterly series.

**Why this module exists (2026-09-07).** `expectations_flag.quarterly_revenue_sec`
selected XBRL facts whose period length was 70-100 days and described the
result as "quarter-by-quarter". It isn't. A 10-K tags the **annual** frame and
nothing else covering the fourth fiscal quarter — there is no standalone
Oct-Dec fact for a calendar-year filer. So the series silently dropped one
quarter per year, with two downstream consequences:

  * `rev.shift(4)` reached back **five** calendar quarters, not four. DDOG's
    Q2 2026 printed +47.3% YoY (1,121.5 / 761.6, i.e. against Q1 2025)
    against a reported +36% (1,121.5 / 826.8).
  * `rev.rolling(4).sum()` summed four of the last **five** quarters, omitting
    a Q4, so the "TTM" denominator understated revenue and P/S ran rich.

The fix is the decomposition the old docstring claimed was already happening.
Every fact is filed under its period start, which makes each fiscal year's
year-to-date ladder explicit: Q1 (90d), H1 (181d), 9M (273d), FY (365d), all
sharing one start. Differencing consecutive rungs recovers the quarter each
rung added, so Q4 = FY - 9M. A directly-tagged quarter always wins over a
derived one — a reported number is evidence, a difference is arithmetic.

Deliberately **stdlib-only** (no pandas): this is the testable core, and the
deploy-site CI installs only openpyxl + pytest, so anything importing pandas
at module level would abort collection there.
"""
from __future__ import annotations

import datetime as dt

# A fiscal quarter is 13 weeks (91d), but 52/53-week calendars stretch one
# quarter a year to 14 weeks (98d) and period ends land on week boundaries.
# 70-100 keeps every real quarter and excludes half-years (~182d).
QUARTER_MIN_DAYS = 70
QUARTER_MAX_DAYS = 100


def _date(value):
    try:
        return dt.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _is_quarter_gap(days: int) -> bool:
    return QUARTER_MIN_DAYS <= days <= QUARTER_MAX_DAYS


def quarterly_from_facts(usd_facts) -> dict[str, float]:
    """XBRL USD fact list -> {ISO period-end: quarterly value}.

    Accepts the raw ``facts["us-gaap"][tag]["units"]["USD"]`` list. Facts
    missing a usable start/end are skipped rather than raising — companyfacts
    carries instant-in-time facts (balance-sheet items) with no ``start``.
    """
    direct: dict[str, float] = {}
    ladders: dict[dt.date, dict[dt.date, float]] = {}

    # Sort by filing date so a restatement filed later overwrites the original.
    for fact in sorted(usd_facts or [], key=lambda f: str(f.get("filed") or "")):
        start, end = _date(fact.get("start")), _date(fact.get("end"))
        if start is None or end is None:
            continue
        try:
            val = float(fact["val"])
        except (KeyError, TypeError, ValueError):
            continue
        days = (end - start).days
        if days <= 0:
            continue
        ladders.setdefault(start, {})[end] = val
        if _is_quarter_gap(days):
            direct[end.isoformat()] = val

    derived: dict[str, float] = {}
    for start, by_end in ladders.items():
        # Walk this fiscal year's year-to-date ladder. The implicit zeroth rung
        # is the period start itself, which is what makes a standalone Q1 fall
        # out of the same arithmetic as Q4 = FY - 9M.
        prev_end, prev_val = start, 0.0
        for end, val in sorted(by_end.items()):
            if _is_quarter_gap((end - prev_end).days):
                derived[end.isoformat()] = val - prev_val
            prev_end, prev_val = end, val

    out = dict(derived)
    out.update(direct)      # a reported quarter beats a derived one
    return out


def quarters_are_consecutive(dates) -> bool:
    """True when every step in ``dates`` is one quarter wide.

    Guards the invariant the 2026-09-07 bug violated silently: a missing
    quarter makes ``shift(4)`` reach back five quarters and ``rolling(4)``
    span five, which is how the old series printed DDOG at +47.3% YoY
    against a reported +36%. Callers should refuse to score on a gap rather
    than emit a misaligned number (rule 3).

    Accepts anything whose pairwise difference has ``.days`` — datetime.date
    or pandas Timestamps both work.
    """
    seq = list(dates)
    return all(_is_quarter_gap((b - a).days)
               for a, b in zip(seq[:-1], seq[1:]))
