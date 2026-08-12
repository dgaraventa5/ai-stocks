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


def rank_by_score(live, prior):
    """Watchlist tickers ranked by TOTAL desc for top-N selection (spec B1).

    Boundary ties break by higher score first (the sort key), then by
    incumbency (an incumbent outranks an equal-scored outsider), then by
    ticker for determinism. live: [{'ticker','TOTAL',...}] with TOTAL set."""
    return [x['ticker'] for x in sorted(
        live, key=lambda x: (-x['TOTAL'],
                             0 if x['ticker'] in prior else 1, x['ticker']))]


def topn_membership(prior, ranked, n, m):
    """Top-N selection with rank hysteresis (spec B1): outsiders ENTER at
    rank <= n; incumbents HOLD through rank <= m; ranks n+1..m are the
    dead-band. Returns (include, entered, exit_crossers) — exit_crossers are
    incumbents past rank m, which the caller runs through the rule-26 2-run
    exit-confirm clock (this function never exits a name itself)."""
    rank = {t: i + 1 for i, t in enumerate(ranked)}
    entered = [t for t in ranked[:n] if t not in prior]
    stay = [t for t in prior if rank.get(t, 10 ** 9) <= m]
    exit_crossers = sorted(t for t in prior if rank.get(t, 10 ** 9) > m)
    include = sorted(set(stay) | set(entered), key=lambda t: rank[t])
    return include, entered, exit_crossers


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


def is_tradable(ticker: str) -> bool:
    """US-brokerage tradability (spec 2026-08-11): foreign local lines carry
    an exchange-suffix dot (6861.T, KGX.DE, 0981.HK); US listings never do.
    Deterministic and offline by design — no per-name list, no API."""
    return '.' not in ticker
