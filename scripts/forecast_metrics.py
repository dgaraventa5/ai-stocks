"""Calibration metrics: Brier, Murphy REL/RES/UNC, Brier Skill Score, log loss,
reliability table. Pure Python (no numpy) — CI-safe. See design spec §8.

p_i = forecast probability, o_i in {0,1} = outcome, N = count, o_bar = base rate.
"""
from __future__ import annotations

import math

DEFAULT_BINS = [(i / 10, (i + 1) / 10) for i in range(10)]  # [0,.1)...[.9,1.0]


def brier(ps, outs) -> float:
    n = len(ps)
    return sum((p - o) ** 2 for p, o in zip(ps, outs)) / n


def base_rate(outs) -> float:
    return sum(outs) / len(outs)


def uncertainty(outs) -> float:
    o = base_rate(outs)
    return o * (1 - o)


def _bin_index(p, bins) -> int:
    for i, (lo, hi) in enumerate(bins):
        if lo <= p < hi:
            return i
        if i == len(bins) - 1 and p == hi:   # last bin closed on the right (p==1.0)
            return i
    return len(bins) - 1


def reliability_table(ps, outs, bins=DEFAULT_BINS) -> list[dict]:
    rows = []
    for i, (lo, hi) in enumerate(bins):
        idx = [j for j in range(len(ps)) if _bin_index(ps[j], bins) == i]
        if not idx:
            rows.append({"bin": (lo, hi), "n": 0, "p_bar": None, "o_bar": None})
            continue
        n = len(idx)
        rows.append({"bin": (lo, hi), "n": n,
                     "p_bar": sum(ps[j] for j in idx) / n,
                     "o_bar": sum(outs[j] for j in idx) / n})
    return rows


def murphy_decomposition(ps, outs, bins=DEFAULT_BINS) -> dict:
    n = len(ps)
    o = base_rate(outs)
    table = reliability_table(ps, outs, bins)
    rel = sum(r["n"] * (r["p_bar"] - r["o_bar"]) ** 2 for r in table if r["n"]) / n
    res = sum(r["n"] * (r["o_bar"] - o) ** 2 for r in table if r["n"]) / n
    unc = o * (1 - o)
    return {"REL": rel, "RES": res, "UNC": unc,
            "BS_reconstructed": rel - res + unc, "table": table}


def brier_skill_score(ps, outs):
    unc = uncertainty(outs)
    if unc == 0:
        return None   # all-same-outcome -> BSS undefined
    return 1 - brier(ps, outs) / unc


def log_loss(ps, outs, eps=1e-6) -> float:
    n = len(ps)
    total = 0.0
    for p, o in zip(ps, outs):
        p = min(max(p, eps), 1 - eps)
        total += o * math.log(p) + (1 - o) * math.log(1 - p)
    return -total / n
