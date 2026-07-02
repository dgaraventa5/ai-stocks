"""Cohort-governance gate (rule 24): the committed cohort-membership map must
match the live Watchlist-derived cohorts. If this fails, cohort membership or
per-metric eligibility changed without regenerating the map — run
`python3 scripts/cohort_membership.py --update` and review the diff.
"""
import cohort_membership as cm


def test_committed_cohort_map_matches_live_watchlist():
    assert cm.check(), (
        "cohort-membership.md is stale vs the live Watchlist — a cohort change "
        "wasn't recorded. Run `scripts/cohort_membership.py --update`, review the "
        "diff (that's the logged before/after), and commit it.")


def test_impact_reports_unknown_ticker_cleanly():
    assert "not on the Watchlist" in cm.impact("NOTATICKER")


def test_generate_is_deterministic():
    assert cm.generate() == cm.generate()
