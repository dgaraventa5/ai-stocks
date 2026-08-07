"""Inverse-vol sizing pure functions (spec 2026-08-07 Part A)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
pd = pytest.importorskip('pandas')
np = pytest.importorskip('numpy')

from position_sizing import (cap_floor_normalize, drift_band_filter,
                             inverse_vol_weights)


def _prices(vols, days=90, seed=7):
    """Wide close-price frame with per-ticker daily vol ~= vols[t]."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range('2026-01-01', periods=days)
    return pd.DataFrame(
        {t: 100 * np.cumprod(1 + rng.normal(0, v, days))
         for t, v in vols.items()}, index=idx)


def test_invvol_weights_basic():
    # Deterministic sigmas via exactly alternating returns: sigma(A)=2*sigma(B)
    idx = pd.bdate_range('2026-01-01', periods=61)
    a = 100 * np.cumprod([1] + [1.02, 0.98] * 30)[:61]
    b = 100 * np.cumprod([1] + [1.01, 0.99] * 30)[:61]
    prices = pd.DataFrame({'A': a, 'B': b}, index=idx)
    cfg = {'lookback': 60, 'sigma_floor': 0.0, 'max_weight': 1.0,
           'min_weight': 0.0}
    w = inverse_vol_weights(prices, ['A', 'B'], cfg)
    assert w['B'] == pytest.approx(2 * w['A'], rel=1e-2)   # half the vol, double the weight
    assert sum(w.values()) == pytest.approx(1.0, abs=1e-9)


def test_caps_and_floor():
    raw = {'A': 10.0, 'B': 1.0, 'C': 1.0, 'D': 1.0, 'E': 1.0,
           'F': 1.0, 'G': 1.0, 'H': 1.0, 'I': 1.0, 'J': 0.05}
    w = cap_floor_normalize(raw, max_w=0.12, min_w=0.03)
    assert w['A'] == pytest.approx(0.12)                    # cap binds
    assert w['J'] == pytest.approx(0.03)                    # floor lifts
    assert all(0.03 - 1e-9 <= v <= 0.12 + 1e-9 for v in w.values())
    assert sum(w.values()) == pytest.approx(1.0, abs=1e-9)  # converges, sums to 1
    # redistribution correct: uncapped names keep pro-rata proportions
    assert w['B'] == pytest.approx(w['C'])


def test_caps_infeasible_raises():
    with pytest.raises(ValueError):
        cap_floor_normalize({'A': 1.0, 'B': 1.0}, max_w=0.12, min_w=0.03)


def test_sigma_floor():
    idx = pd.bdate_range('2026-01-01', periods=61)
    flat = pd.DataFrame({'A': [100.0] * 61,                  # zero vol
                         'B': 100 * np.cumprod([1] + [1.01, 0.99] * 30)[:61]},
                        index=idx)
    cfg = {'lookback': 60, 'sigma_floor': 0.005, 'max_weight': 1.0,
           'min_weight': 0.0}
    w = inverse_vol_weights(flat, ['A', 'B'], cfg)
    assert w['A'] < 1.0                                      # not infinite weight
    sigma_b = flat['B'].pct_change().dropna().std()
    assert w['A'] / w['B'] == pytest.approx(sigma_b / 0.005, rel=1e-6)


def test_short_history_fallback():
    prices = _prices({'A': 0.01, 'B': 0.02, 'C': 0.02})
    prices.loc[prices.index[:-10], 'C'] = np.nan             # only 10 days of C
    cfg = {'lookback': 60, 'sigma_floor': 0.0, 'max_weight': 1.0,
           'min_weight': 0.0}
    layers = {'A': '06', 'B': '08', 'C': '08'}
    w = inverse_vol_weights(prices, ['A', 'B', 'C'], cfg, layers=layers)
    # C takes its layer cohort's (B's) median sigma -> equal weight with B
    assert w['C'] == pytest.approx(w['B'], rel=1e-9)
    assert sum(w.values()) == pytest.approx(1.0, abs=1e-9)


def test_monotonic():
    prices = _prices({'A': 0.008, 'B': 0.012, 'C': 0.02, 'D': 0.03, 'E': 0.05,
                      'F': 0.01, 'G': 0.015, 'H': 0.025, 'I': 0.04, 'J': 0.02})
    cfg = {'lookback': 60, 'sigma_floor': 0.005, 'max_weight': 0.12,
           'min_weight': 0.03}
    roster = list('ABCDEFGHIJ')
    w = inverse_vol_weights(prices, roster, cfg)
    sig = {t: prices[t].pct_change().dropna().iloc[-60:].std() for t in roster}
    ordered = sorted(roster, key=lambda t: sig[t])
    for hi, lo in zip(ordered, ordered[1:]):                 # lower vol ⇒ weakly higher weight
        assert w[hi] >= w[lo] - 1e-9
    assert sum(w.values()) == pytest.approx(1.0, abs=1e-9)


def test_drift_band():
    target = {'A': 0.08, 'B': 0.08, 'C': 0.08}
    inside = {'A': 0.081, 'B': 0.099, 'C': 0.061}            # all within ±25% rel
    w, traded = drift_band_filter(inside, target, band=0.25)
    assert traded == [] and w == inside                      # inside -> no trades
    outside = {'A': 0.081, 'B': 0.11, 'C': 0.05}             # B,C breach
    w, traded = drift_band_filter(outside, target, band=0.25)
    assert traded == ['B', 'C']
    assert w['B'] / w['C'] == pytest.approx(1.0)             # both back to target ratio
    assert sum(w.values()) == pytest.approx(sum(target.values()), abs=1e-9)
