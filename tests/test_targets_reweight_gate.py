"""Re-weight gate (rule 25): the committed Targets must reflect the live scores.

If a score change (objective refresh, re-rating, methodology change, cohort edit)
moved a held name's tier or the roster and refresh_targets wasn't re-run, the
portfolio weights are stale. This gate fails in that case — so stale weights can't
be committed. Offline (no yfinance); the fix is `python3 scripts/refresh_targets.py`.
"""
import refresh_targets as rt


def test_targets_reflect_current_scores():
    assert not rt.pending_rebalance(), (
        "Portfolio weights are STALE vs the live scores — a rebalance is pending. "
        "Run `python3 scripts/refresh_targets.py` (--resize to force immediate "
        "exits) and commit the updated Targets (rule 25).")
