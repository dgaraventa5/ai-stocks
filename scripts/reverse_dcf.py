"""Reverse-DCF / implied-growth metric — the pure functions behind P2 of the
2026-07-01 scoring critique.

WHY: every existing input is backward-looking (TTM multiples, TTM margins, 3yr
CAGR) and measures business *quality*, not *mispricing* (finding F1). This metric
asks what the *price already assumes*: given the current EV, a fixed WACC and a
simple multi-stage DCF, solve for the FCF growth rate the market has baked in.
Then score the GAP between a grounded growth estimate and that implied growth —
a positive gap (grounded > implied) means the market underappreciates the name.
This is the Novy-Marx "quality conditioned on price" point the current additive,
quality-only form cannot express.

MODEL (deliberately simple and free-data implementable):
    FCF_t = fcf0 * (1 + g) ** t           for t = 1..years   (constant high growth)
    TV     = FCF_years * (1 + tg) / (wacc - tg)               (Gordon terminal)
    EV(g)  = sum_t FCF_t / (1+wacc)**t  +  TV / (1+wacc)**years
EV(g) is strictly increasing in g (for fcf0 > 0, wacc > tg), so `implied_growth`
inverts it by bisection.

SCOPE OF THIS MODULE: pure math only. It does NOT read the workbook, fetch a
WACC, choose the grounded growth estimate, or touch the live score. Placement
(a sub-metric inside Value vs a new category) is §5-decision-3; the 0-100
`gap_to_score` bands below are PROVISIONAL and any final calibration is IC-gated
under P3. Nothing here is wired into recalc_watchlist.py or the Excel formulas.
"""
from __future__ import annotations

from typing import Optional

Number = Optional[float]


def dcf_ev(g: float, fcf0: float, wacc: float,
           years: int = 10, terminal_growth: float = 0.03) -> float:
    """Enterprise value implied by a constant-growth-then-Gordon-terminal DCF.

    Raises ValueError if wacc <= terminal_growth (the Gordon denominator would be
    non-positive — a configuration error, not a per-name data gap).
    """
    if wacc <= terminal_growth:
        raise ValueError(
            f"wacc ({wacc}) must exceed terminal_growth ({terminal_growth})")
    pv_explicit = 0.0
    fcf_t = fcf0
    for t in range(1, years + 1):
        fcf_t = fcf0 * (1.0 + g) ** t
        pv_explicit += fcf_t / (1.0 + wacc) ** t
    tv = fcf_t * (1.0 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = tv / (1.0 + wacc) ** years
    return pv_explicit + pv_terminal


def implied_growth(ev: float, fcf0: float, wacc: float,
                   years: int = 10, terminal_growth: float = 0.03,
                   lo: float = -0.5, hi: float = 1.0,
                   tol: float = 1e-7, max_iter: int = 200) -> Number:
    """Solve EV(g) = ev for g by bisection over [lo, hi].

    Returns None when the metric cannot be defined for this name:
      - fcf0 <= 0  (no positive base to grow — honest skip, not a fabricated 0)
      - ev   <= 0
    Clamps to `lo` / `hi` when the target EV lies outside the achievable range at
    the growth bounds (returns the bound exactly, so callers can flag a pegged
    solve). Raises ValueError if wacc <= terminal_growth.
    """
    if wacc <= terminal_growth:
        raise ValueError(
            f"wacc ({wacc}) must exceed terminal_growth ({terminal_growth})")
    if fcf0 is None or fcf0 <= 0:
        return None
    if ev is None or ev <= 0:
        return None

    ev_lo = dcf_ev(lo, fcf0, wacc, years, terminal_growth)
    ev_hi = dcf_ev(hi, fcf0, wacc, years, terminal_growth)
    if ev <= ev_lo:
        return lo
    if ev >= ev_hi:
        return hi

    a, b = lo, hi
    for _ in range(max_iter):
        mid = (a + b) / 2.0
        ev_mid = dcf_ev(mid, fcf0, wacc, years, terminal_growth)
        if abs(ev_mid - ev) < tol or (b - a) / 2.0 < tol:
            return mid
        if ev_mid < ev:
            a = mid
        else:
            b = mid
    return (a + b) / 2.0


# PROVISIONAL 0-100 mapping (see module docstring — not the final calibration).
# gap = grounded_growth - implied_growth, in decimal (0.10 == 10pp). Monotone.
_GAP_BANDS = [
    (0.15, 100.0),
    (0.10, 90.0),
    (0.05, 75.0),
    (0.00, 60.0),
    (-0.05, 45.0),
    (-0.10, 30.0),
]


def gap_to_score(gap: float) -> float:
    """Map a growth gap to a provisional 0-100 score (monotone increasing)."""
    for thresh, score in _GAP_BANDS:
        if gap >= thresh:
            return score
    return 15.0


def mispricing_gap(ev: float, fcf0: float, wacc: float, grounded_g: float,
                   years: int = 10, terminal_growth: float = 0.03) -> Number:
    """grounded_g - implied_growth. Positive => underappreciated. None if the
    implied growth is undefined for this name."""
    ig = implied_growth(ev, fcf0, wacc, years=years,
                        terminal_growth=terminal_growth)
    if ig is None:
        return None
    return grounded_g - ig


def mispricing_score(ev: float, fcf0: float, wacc: float, grounded_g: float,
                     years: int = 10, terminal_growth: float = 0.03) -> Number:
    """Full chain: implied growth -> gap -> provisional 0-100 score."""
    gap = mispricing_gap(ev, fcf0, wacc, grounded_g, years=years,
                         terminal_growth=terminal_growth)
    if gap is None:
        return None
    return gap_to_score(gap)


# Plausible durable-growth band for the grounded estimate. Trailing 3yr revenue
# CAGR (the input recalc feeds) is a noisy FORWARD proxy: uncapped, hyper-growth
# AI names read 70-100% and all saturate at 100 (turning P2 into a growth factor
# that undoes P1), and a cyclical revenue dip reads negative and penalizes a cheap
# name. Clamping to [0, 25]% keeps it a mispricing signal. (review #1, 2026-07-02,
# approved by Dom.) Very few companies durably compound >25%/yr for a decade.
GROUNDED_FLOOR_PCT = 0.0
GROUNDED_CAP_PCT = 25.0


def reverse_dcf_score(ev_over_fcf, grounded_growth_pct, wacc: float = 0.10,
                      years: int = 10, terminal_growth: float = 0.03,
                      grounded_floor: float = GROUNDED_FLOOR_PCT,
                      grounded_cap: float = GROUNDED_CAP_PCT) -> Number:
    """The live P2 metric (§5-3): a 0-100 mispricing score computed straight from
    the EV/FCF multiple and a grounded growth estimate (in PERCENT, e.g. 8.0),
    clamped to a plausible durable range [grounded_floor, grounded_cap].

    Implied growth depends only on EV/FCF (fcf0 cancels out of the DCF), so we
    solve with fcf0=1 and ev = the multiple. A bigger positive gap (clamped
    grounded > implied) means the market underappreciates the name -> higher
    score. Returns None when EV/FCF is non-positive (negative FCF) or grounded
    growth is missing, so the Value average simply skips it."""
    if ev_over_fcf is None or ev_over_fcf <= 0 or grounded_growth_pct is None:
        return None
    g = max(grounded_floor, min(grounded_cap, grounded_growth_pct))
    implied = implied_growth(ev_over_fcf, 1.0, wacc, years=years,
                             terminal_growth=terminal_growth)
    if implied is None:
        return None
    return gap_to_score(g / 100.0 - implied)
