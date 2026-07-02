"""Unit tests for the P1 cohort-relative scoring wiring (pure parts).

The live score grades each metric against fixed cutoffs (absolute bands). P1
instead ranks each name against its layer peers (percentile) for the six
style-biased metrics — BUT only when the peer group is big enough to rank
meaningfully (min-cohort-size guard); otherwise it falls back to the absolute
band. These tests cover the two pure pieces: layer grouping and the
percentile-or-fallback decision.
"""
import p1_cohort_scoring as p1


def test_top_level_layer_extracts_prefix():
    assert p1.top_level_layer("06 AI Compute Silicon / GPUs") == "06"
    assert p1.top_level_layer("01 Power Generation / Nuclear-specific") == "01"
    assert p1.top_level_layer("10 Models, Software & Applications / AI cybersecurity") == "10"


def test_top_level_layer_handles_missing():
    assert p1.top_level_layer(None) is None
    assert p1.top_level_layer("") is None
    assert p1.top_level_layer("no-layer-code") is None


def _double(v):
    """Stand-in absolute band function for tests."""
    return v * 2 if v is not None else None


def test_cohort_scores_percentile_when_big_enough():
    # 8 non-null values, higher-is-better, min_size 8 -> percentile ranks.
    vals = [10, 20, 30, 40, 50, 60, 70, 80]
    out = p1.cohort_metric_scores(vals, higher_is_better=True,
                                  absolute_fn=_double, min_size=8)
    # matches the pure percentile transform, and is monotonic increasing
    assert out == __import__("cohort_percentile").rank_cohort(vals, True)
    assert out[0] < out[-1]
    # NOT the absolute fallback (which would be v*2 = 20 for the first)
    assert out[0] != 20


def test_cohort_falls_back_to_absolute_when_too_small():
    # only 5 non-null -> below min_size 8 -> absolute band per value.
    vals = [10, 20, 30, 40, 50]
    out = p1.cohort_metric_scores(vals, higher_is_better=True,
                                  absolute_fn=_double, min_size=8)
    assert out == [20, 40, 60, 80, 100]      # _double applied to each


def test_cohort_min_size_counts_non_null_only():
    # 8 slots but only 6 non-null -> still falls back to absolute.
    vals = [10, 20, None, 30, 40, None, 50, 60]
    out = p1.cohort_metric_scores(vals, higher_is_better=True,
                                  absolute_fn=_double, min_size=8)
    assert out[2] is None and out[5] is None     # blanks preserved
    assert out[0] == 20                           # absolute fallback (6 < 8)


def test_cohort_lower_is_better_direction():
    vals = [10, 20, 30, 40, 50, 60, 70, 80]
    out = p1.cohort_metric_scores(vals, higher_is_better=False,
                                  absolute_fn=_double, min_size=8)
    assert out[0] > out[-1]                        # smallest value scores best


def test_tier_bands_match_live_scale():
    # P1 must reuse the same tier scale so before/after is apples-to-apples.
    assert p1.tier(90) == "✓✓✓"
    assert p1.tier(75) == "✓✓"
    assert p1.tier(60) == "✓"
    assert p1.tier(45) == "?"
    assert p1.tier(20) == "✗"
    assert p1.tier(None) is None
