"""Unit tests for the P1 cohort-relative percentile transform (pure function).

Scope: ONLY the percentile math. Cohort *assignment* (which names share a
cohort, and how thin layers merge into super-cohorts) is §5-decision-1 of the
2026-07-01 critique and is deliberately NOT encoded here — it stays out of the
pure function until Dom signs off.

Not yet wired into the live Watchlist score.
"""
import cohort_percentile as cp


def test_none_value_returns_none():
    assert cp.percentile_score(None, [10, 20, 30]) is None


def test_empty_cohort_returns_none():
    assert cp.percentile_score(10, []) is None
    assert cp.percentile_score(10, [None, None]) is None


def test_higher_is_better_orders_ascending():
    # In a higher-is-better metric, the biggest raw value scores highest.
    lo = cp.percentile_score(10, [10, 20, 30], higher_is_better=True)
    mid = cp.percentile_score(20, [10, 20, 30], higher_is_better=True)
    hi = cp.percentile_score(30, [10, 20, 30], higher_is_better=True)
    assert lo < mid < hi


def test_lower_is_better_flips_order():
    # In a lower-is-better metric (e.g. EV/EBITDA), the smallest value scores highest.
    best = cp.percentile_score(10, [10, 20, 30], higher_is_better=False)
    worst = cp.percentile_score(30, [10, 20, 30], higher_is_better=False)
    assert best > worst


def test_median_maps_near_50():
    # Middle of a symmetric odd cohort sits at the 50th percentile (mid-rank).
    assert cp.percentile_score(20, [10, 20, 30], higher_is_better=True) == 50.0


def test_all_equal_returns_50():
    # No dispersion -> everyone is average -> neutral 50 (mid-rank of a full tie).
    for v in cp.rank_cohort([25, 25, 25, 25]):
        assert v == 50.0


def test_single_element_cohort_returns_50():
    # A name with no peers can't be ranked; neutral 50, not a spurious 0 or 100.
    assert cp.percentile_score(42, [42], higher_is_better=True) == 50.0


def test_endpoints_use_midrank_convention():
    # n=4, higher-is-better: worst -> (0+0.5)/4, best -> (3+0.5)/4.
    scores = cp.rank_cohort([10, 20, 30, 40], higher_is_better=True)
    assert scores == [12.5, 37.5, 62.5, 87.5]


def test_ties_share_the_same_midrank_score():
    scores = cp.rank_cohort([10, 10, 20], higher_is_better=True)
    assert scores[0] == scores[1]           # the two 10s tie
    assert scores[2] > scores[0]            # 20 beats them


def test_rank_cohort_preserves_blanks_and_length():
    scores = cp.rank_cohort([10, None, 30], higher_is_better=True)
    assert len(scores) == 3
    assert scores[1] is None
    assert scores[0] < scores[2]            # None ignored in the ranking


def test_rank_cohort_is_monotonic_in_raw_value():
    # Strictly-better raw value never scores lower within the same cohort.
    raw = [3.1, 9.9, 5.5, 5.5, 1.0, 12.4, 8.0]
    scores = cp.rank_cohort(raw, higher_is_better=True)
    paired = sorted(zip(raw, scores), key=lambda p: p[0])
    for (v0, s0), (v1, s1) in zip(paired, paired[1:]):
        assert s1 >= s0                      # non-decreasing in raw value


def test_scores_are_bounded_0_100():
    scores = cp.rank_cohort([1, 2, 3, 100, -50, 7], higher_is_better=True)
    for s in scores:
        assert 0.0 <= s <= 100.0
