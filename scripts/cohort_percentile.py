"""Cohort-relative percentile scoring — the pure transform behind P1 of the
2026-07-01 scoring critique.

WHY: the live Methodology tab maps each metric to 0-100 via *absolute* threshold
bands (Gross Margin >=60 -> 100, ROIC >=25 -> 100, absolute EV/EBITDA & FCF-yield
bands). Software/silicon auto-max those bands; power, fabs, servers, cooling and
industrials score 30-60 *regardless of within-peer attractiveness*. So Quality and
Value partly measure "high-margin asset-light business model" — a style bet, not an
opportunity (finding F3). P1 replaces the absolute band with a within-cohort
percentile rank for the style-biased metrics, so a name is scored against its peers
rather than against a silicon-calibrated absolute yardstick.

SCOPE OF THIS MODULE (deliberately narrow): the percentile MATH only.
  - It does NOT decide which names form a cohort, nor how thin layers merge into
    super-cohorts — that is §5-decision-1 and awaits Dom's sign-off.
  - It is NOT wired into recalc_watchlist.py or the Excel formulas yet.
The caller supplies the cohort's list of values; this module turns a value's rank
within that list into a 0-100 score.

CONVENTION: mid-rank percentile.
    score(value) = ( #{peers worse than value} + 0.5 * #{peers equal to value} ) / n * 100
Chosen because it is the standard statistical percentile-rank, handles ties
symmetrically, is robust to cohort size, and maps the cohort median to ~50. It
deliberately does NOT force the best name to exactly 100 / worst to exactly 0 —
where the tier bands land on this new distribution is §5-decision-4 (band
recalibration), a separate call, and hard-pinning the endpoints here would
pre-empt it.
"""
from __future__ import annotations

from typing import Iterable, List, Optional

Number = Optional[float]


def percentile_score(value: Number,
                     cohort_values: Iterable[Number],
                     higher_is_better: bool = True) -> Number:
    """Return ``value``'s mid-rank percentile within ``cohort_values``, in [0, 100].

    ``value`` may be a member of ``cohort_values`` (the normal case, when scoring
    every name in a cohort against the whole cohort) or an external probe.

    Returns ``None`` when ``value`` is ``None`` or the cohort has no non-null
    members — mirroring the workbook's "blank stays blank; AVERAGE skips it"
    convention so a missing metric never fabricates a score.
    """
    if value is None:
        return None
    peers = [c for c in cohort_values if c is not None]
    n = len(peers)
    if n == 0:
        return None
    if higher_is_better:
        worse = sum(1 for c in peers if c < value)
    else:
        worse = sum(1 for c in peers if c > value)
    ties = sum(1 for c in peers if c == value)
    return (worse + 0.5 * ties) / n * 100.0


def rank_cohort(values: Iterable[Number],
                higher_is_better: bool = True) -> List[Number]:
    """Score every element of ``values`` against the cohort formed by the
    non-null elements of ``values`` itself.

    Preserves length and position; ``None`` inputs stay ``None`` (and are
    excluded from the ranking of the others). This is the shape P1 will consume:
    one metric column for one cohort in, the 0-100 scores out.
    """
    values = list(values)
    non_null = [v for v in values if v is not None]
    return [percentile_score(v, non_null, higher_is_better) if v is not None else None
            for v in values]


import re as _re

MIN_COHORT_SIZE = 8


def top_level_layer(layer_str):
    """'06 AI Compute Silicon / GPUs' -> '06'. None/blank/no-code -> None.
    The cohort key for P1 (§5-1: pure top-level layer, no cross-model merge)."""
    if not layer_str:
        return None
    m = _re.match(r"\s*(\d{2})", str(layer_str))
    return m.group(1) if m else None


def cohort_metric_scores(values, higher_is_better, absolute_fn,
                         min_size=MIN_COHORT_SIZE):
    """Percentile-rank `values` within their cohort when >= min_size are
    non-null; otherwise score each via `absolute_fn` (the live absolute band).
    Blanks stay blank in both cases. This is the min-cohort-size guard that keeps
    a thin cohort from shipping a noisy 5-name percentile."""
    non_null = [v for v in values if v is not None]
    if len(non_null) >= min_size:
        return rank_cohort(values, higher_is_better)
    return [absolute_fn(v) if v is not None else None for v in values]
