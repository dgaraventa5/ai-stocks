"""Pure portfolio-sizing helpers — no yfinance, no workbook I/O, no network.

Extracted from refresh_targets.py so the rebalance-gate logic and the
score-monotonicity regression gate are unit-testable and run in the
openpyxl-only deploy CI. See
docs/superpowers/specs/2026-06-29-tier-crossing-rebalance-design.md.
"""
from __future__ import annotations


def tier_changes(include, info, last_tiers):
    """[(ticker, old, new)] for held names whose tier moved vs the last rebalance.

    Baseline is the last MODEL EVENT's stored tiers, not the Targets sheet (which
    can carry a fresh tier from an out-of-band score edit — the bug this fixes).
    Names absent from last_tiers are newly entered (membership, not a crossing).
    """
    out = []
    for t in include:
        old = last_tiers.get(t)
        new = info[t].get('Tier')
        if old is not None and new is not None and old != new:
            out.append((t, old, new))
    return out


def build_reason(entered, exited, tier_chg, resize):
    """Human-readable rebalance reason from membership and/or tier deltas."""
    parts = []
    if entered or exited:
        parts.append('membership: '
                     + ', '.join([f'+{t}' for t in entered]
                                 + [f'-{t}' for t in exited]))
    if tier_chg:
        parts.append('tier: '
                     + ', '.join(f'{t} {old}→{new}' for t, old, new in tier_chg))
    if not parts and resize:
        parts.append('manual resize')
    return '; '.join(parts) or 'rebalance'


def weights_score_monotonic(rows, tol=1e-4):
    """rows: iterable of (score, weight). Returns [] if, sorted by score
    descending, weight is non-increasing (ties OK — cap-clipped names); else the
    violating (hi_score, hi_w, lo_score, lo_w) adjacent pairs. base_weight is
    monotonic in score and normalization/capping preserve order, so a violation
    means a stale/out-of-band weight (e.g. a ✓✓✓ name weighted below a ✓✓ name).
    """
    ordered = sorted(rows, key=lambda r: -r[0])
    viol = []
    for (s_hi, w_hi), (s_lo, w_lo) in zip(ordered, ordered[1:]):
        if w_lo > w_hi + tol:
            viol.append((s_hi, w_hi, s_lo, w_lo))
    return viol
