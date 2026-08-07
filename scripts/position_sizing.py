"""Inverse-volatility position sizing + drift-band re-size filter (v2 Part A).

Pure functions: no yfinance, no workbook I/O, no network. pandas is imported
lazily inside functions so the openpyxl-only deploy CI can import this module.
Sizing params live in tracking/portfolio-config.json -> `sizing`
(portfolio_model.load_pcfg). Spec:
docs/superpowers/specs/2026-08-07-portfolio-construction-v2-spec.md
"""
from __future__ import annotations

from common import flag


def cap_floor_normalize(raw: dict[str, float], max_w: float, min_w: float,
                        tol: float = 1e-9) -> dict[str, float]:
    """Normalize raw scores to weights summing to 1.0 under a per-name cap and
    floor. Iterative pin-and-redistribute: breachers are pinned at the bound,
    the rest re-share the remaining budget pro-rata; the pinned set only grows,
    so the loop terminates in <= len(raw) passes (unit-tested convergence)."""
    if not raw:
        return {}
    n = len(raw)
    if n * max_w < 1 - tol or n * min_w > 1 + tol:
        raise ValueError(f'infeasible cap/floor: n={n} max={max_w} min={min_w}')
    pinned: dict[str, float] = {}
    w: dict[str, float] = {}
    for _ in range(n + 1):
        budget = 1.0 - sum(pinned.values())
        free = {t: raw[t] for t in raw if t not in pinned}
        if not free:
            w = dict(pinned)
            break
        s = sum(free.values())
        w_free = {t: v / s * budget for t, v in free.items()}
        over = {t for t, v in w_free.items() if v > max_w + tol}
        under = {t for t, v in w_free.items() if v < min_w - tol}
        if not over and not under:
            w = pinned | w_free
            break
        pinned |= {t: max_w for t in over} | {t: min_w for t in under}
    assert abs(sum(w.values()) - 1.0) < 1e-9, 'weights must sum to 1'
    return w


def inverse_vol_weights(prices, roster: list[str], cfg: dict,
                        layers: dict[str, str] | None = None) -> dict[str, float]:
    """Inverse-trailing-volatility weights for `roster` (spec A1).

    prices: wide pandas DataFrame of dividend-adjusted closes (columns=tickers).
    Uses the trailing cfg['lookback'] daily returns; sigma is floored at
    cfg['sigma_floor']; caps/floor applied by cap_floor_normalize. Names with
    fewer than lookback returns (recent IPOs) take the median sigma of their
    layer cohort within the roster (flagged), falling back to the roster
    median. Returns {ticker: weight} summing to 1.0.
    """
    import pandas as pd

    lookback = int(cfg.get('lookback', 60))
    sigma_floor = float(cfg.get('sigma_floor', 0.005))
    sigma: dict[str, float] = {}
    short: list[str] = []
    for t in roster:
        # Per-ticker returns over the name's OWN trading days: a mixed-calendar
        # frame (e.g. 6861.T Tokyo sessions vs US names) interleaves indexes,
        # and a shared pct_change would see a NaN gap at every step.
        r = (prices[t].dropna().pct_change().dropna().iloc[-lookback:]
             if t in prices.columns else pd.Series(dtype=float))
        if len(r) >= lookback:
            sigma[t] = float(r.std())
        else:
            short.append(t)
    for t in short:
        lay = (layers or {}).get(t)
        cohort = [s for u, s in sigma.items()
                  if lay is not None and (layers or {}).get(u) == lay]
        pool = cohort or list(sigma.values())
        if not pool:
            raise ValueError('no roster name has sufficient price history')
        sigma[t] = float(pd.Series(pool).median())
        flag(f'{t}: <{lookback} return days — sigma from '
             f'{"layer-cohort" if cohort else "roster"} median ({sigma[t]:.4f})')
    raw = {t: 1.0 / max(sigma[t], sigma_floor) for t in roster}
    return cap_floor_normalize(raw, float(cfg.get('max_weight', 0.12)),
                               float(cfg.get('min_weight', 0.03)))


def drift_band_filter(current: dict[str, float], target: dict[str, float],
                      band: float) -> tuple[dict[str, float], list[str]]:
    """Monthly re-size filter (spec A2): trade ONLY names whose current weight
    sits outside the relative band around target (target 8%, band .25 -> trade
    only if <6% or >10%). Untraded names keep their drifted weight; the result
    is renormalized to the invested budget (sum of targets). Returns
    (weights, traded_tickers); traded == [] means no re-size event fires."""
    traded = sorted(t for t in target
                    if t not in current
                    or abs(current[t] - target[t]) > band * target[t] + 1e-12)
    if not traded:
        return dict(current), []
    w = {t: (target[t] if t in traded else current[t]) for t in target}
    s, budget = sum(w.values()), sum(target.values())
    w = {t: v / s * budget for t, v in w.items()}
    return w, traded
