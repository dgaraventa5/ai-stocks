"""Unit tests for the P2 reverse-DCF / implied-growth metric (pure functions).

The metric targets finding F1 (the score measures business *quality*, not
*mispricing*). It solves for the FCF growth rate the current EV already assumes,
then scores the gap between a grounded growth estimate and that implied growth —
a positive gap (grounded > implied) meaning the market underappreciates the name.

Not yet wired into the live Watchlist score. The 0-100 band mapping here is
PROVISIONAL (placement inside Value vs a new category is §5-decision-3; any final
calibration is IC-gated under P3).
"""
import math

import pytest

import reverse_dcf as rd

WACC = 0.10
YEARS = 10
TG = 0.03


def test_dcf_ev_is_monotonic_in_growth():
    prev = None
    for g in [-0.30, -0.10, 0.0, 0.10, 0.25, 0.50]:
        ev = rd.dcf_ev(g, fcf0=20.0, wacc=WACC, years=YEARS, terminal_growth=TG)
        if prev is not None:
            assert ev > prev, f"EV not increasing at g={g}"
        prev = ev


def test_implied_growth_recovers_a_known_rate():
    # Forward: pick g*, price it. Inverse: recover g* from that EV.
    g_star = 0.15
    ev = rd.dcf_ev(g_star, fcf0=20.0, wacc=WACC, years=YEARS, terminal_growth=TG)
    g_hat = rd.implied_growth(ev, fcf0=20.0, wacc=WACC, years=YEARS,
                              terminal_growth=TG)
    assert g_hat == pytest.approx(g_star, abs=1e-4)


def test_implied_growth_recovers_several_rates():
    for g_star in [-0.20, -0.05, 0.0, 0.08, 0.22, 0.40]:
        ev = rd.dcf_ev(g_star, fcf0=15.0, wacc=WACC, years=YEARS,
                       terminal_growth=TG)
        g_hat = rd.implied_growth(ev, fcf0=15.0, wacc=WACC, years=YEARS,
                                  terminal_growth=TG)
        assert g_hat == pytest.approx(g_star, abs=1e-4)


def test_richer_ev_implies_more_growth():
    lo = rd.implied_growth(200.0, fcf0=20.0, wacc=WACC)
    hi = rd.implied_growth(600.0, fcf0=20.0, wacc=WACC)
    assert hi > lo


def test_negative_or_zero_fcf_returns_none():
    # Can't imply a multiplicative growth rate off non-positive base FCF —
    # honest skip (like the workbook's blank conventions), not a fabricated 0.
    assert rd.implied_growth(500.0, fcf0=0.0, wacc=WACC) is None
    assert rd.implied_growth(500.0, fcf0=-12.0, wacc=WACC) is None


def test_nonpositive_ev_returns_none():
    assert rd.implied_growth(0.0, fcf0=20.0, wacc=WACC) is None
    assert rd.implied_growth(-100.0, fcf0=20.0, wacc=WACC) is None


def test_wacc_must_exceed_terminal_growth():
    # Gordon terminal value diverges/negative otherwise — a config error, so raise.
    with pytest.raises(ValueError):
        rd.dcf_ev(0.10, fcf0=20.0, wacc=0.03, terminal_growth=0.03)
    with pytest.raises(ValueError):
        rd.implied_growth(500.0, fcf0=20.0, wacc=0.02, terminal_growth=0.03)


def test_implied_growth_clamps_out_of_range():
    # EV far above what even the max growth bound can justify -> clamp to hi.
    assert rd.implied_growth(1e12, fcf0=20.0, wacc=WACC, lo=-0.5, hi=1.0) == 1.0
    # EV far below the min bound -> clamp to lo.
    assert rd.implied_growth(0.001, fcf0=20.0, wacc=WACC, lo=-0.5, hi=1.0) == -0.5


def test_gap_to_score_is_monotonic_and_bounded():
    prev = None
    for gap in [-0.30, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15, 0.40]:
        s = rd.gap_to_score(gap)
        assert 0.0 <= s <= 100.0
        if prev is not None:
            assert s >= prev
        prev = s


def test_positive_gap_beats_negative_gap():
    assert rd.gap_to_score(0.12) > rd.gap_to_score(-0.12)


def test_mispricing_score_none_when_fcf_nonpositive():
    assert rd.mispricing_score(500.0, fcf0=-5.0, wacc=WACC, grounded_g=0.10) is None


def test_richly_valued_megacap_scores_worse_than_cheap_cyclical():
    """The doc's required sanity check: the metric must be anti-correlated with
    the current Value-multiple scores. A rich name (EV/FCF ~50) bakes in high
    implied growth -> small/negative gap -> low score. A cheap name (EV/FCF ~5)
    bakes in little/negative implied growth -> big gap -> high score. Same
    grounded growth for both, so only the price differs."""
    grounded = 0.08
    megacap = rd.mispricing_score(ev=1000.0, fcf0=20.0, wacc=WACC,
                                  grounded_g=grounded)   # EV/FCF = 50, rich
    cyclical = rd.mispricing_score(ev=100.0, fcf0=20.0, wacc=WACC,
                                   grounded_g=grounded)  # EV/FCF = 5, cheap
    assert cyclical > megacap
