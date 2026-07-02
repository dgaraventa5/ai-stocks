"""P1 before/after report tool — a thin wrapper over recalc_watchlist's two
scoring modes.

The scoring itself now lives in ONE place: recalc_watchlist.recalc(mode=...).
mode='percentile' is the live model (peer-ranked for the six style-biased
metrics); mode='absolute' is the pre-P1 fixed-band scoring. This module just
pairs them per name for the before/after review. The pure cohort helpers are
re-exported from cohort_percentile so their tests keep a stable import path.
"""
from __future__ import annotations

import recalc_watchlist as rc
from cohort_percentile import (  # noqa: F401 - re-exported for tests / callers
    top_level_layer, cohort_metric_scores, MIN_COHORT_SIZE)

tier = rc.tier
XLSX = rc.XLSX
# Live portfolio membership thresholds (refresh_targets.py) — for roster diffs.
ENTRY_SCORE = 74.5
EXIT_SCORE = 73.0


def score_watchlist(xlsx=XLSX):
    """Live-absolute vs cohort-relative scores for every name (both computed by
    recalc_watchlist, so there is no second scoring implementation to drift)."""
    ab = {x['row']: x for x in rc.recalc(xlsx, mode='absolute')}
    pc = {x['row']: x for x in rc.recalc(xlsx, mode='percentile')}
    out = []
    for row, a in ab.items():
        p = pc[row]
        out.append(dict(
            ticker=a['ticker'], layer=a['layer'], tl=top_level_layer(a['layer']),
            rated=a['AI'] is not None,
            abs_total=a['TOTAL'], abs_tier=a['Tier'],
            pct_total=p['TOTAL'], pct_tier=p['Tier'],
            abs_value=a['Value'], pct_value=p['Value'],
            abs_quality=a['Quality'], pct_quality=p['Quality']))
    return out
