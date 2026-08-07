# Portfolio Construction v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Inverse-volatility position sizing (Part A), top-N-with-hysteresis selection (Part B), and band-shadow + point-in-time-score instrumentation (Part C) per the 2026-08-07 spec — all built and tested, with the live portfolio left untouched until Dom approves the migration table.

**Architecture:** New pure module `scripts/position_sizing.py` (inverse-vol weights, cap/floor, drift band); rank-selection pure functions added to `scripts/portfolio_sizing.py`; both wired into `refresh_targets.refresh()` behind mode switches in a new `tracking/portfolio-config.json` (modes stay `tier`/`score` until migration). The existing EW chain-link engine in `portfolio_model.ew_growth` is generalized to power the EW_ROSTER and band shadow series. A new `scripts/score_history.py` appends the point-in-time score panel from `sync_scores()` (the rule-25 universal finalize step). A migration script prints the §A3 before/after table; `--apply` is Dom-only.

**Tech Stack:** Python 3, openpyxl, pandas (lazy), yfinance (lazy), pytest. Site: vanilla JS + Chart.js.

## Global Constraints

- **Live portfolio must NOT change** until Dom approves the §A3 migration table. All new behavior lands behind `sizing.mode: "tier"` / `selection.mode: "score"` defaults that reproduce today's behavior exactly.
- **No scoring-engine changes** (spec Non-goals): recalc_watchlist, weights, metrics untouched.
- **No tuning** LOOKBACK/caps/N/M against the 10-week history. Params verbatim from spec: `LOOKBACK=60`, `SIGMA_FLOOR=0.005`, `MAX_WEIGHT=0.12`, `MIN_WEIGHT=0.03`, `DRIFT_BAND=0.25`, `N=15`, `M=18`, bands `1–15 / 16–25 / 26–40`.
- **No backfilled shadows** — band series are forward-only from deploy date.
- **CI is openpyxl-only** (deploy-site workflow): every new module importable without pandas/yfinance at module level; tests needing pandas use `pytest.importorskip` (see `tests/test_ew_chainlink.py`).
- **Rule 26:** the Sizing Rules sheet stays authoritative for entry/exit params; `Entry rank`/`Exit rank` rows (currently inert) become the Part-B params. Cross-run state lives in `tracking/performance-config.json`, never in display artifacts.
- **Rule 18/25:** `refresh_targets.py` remains the single Targets writer; the reweight gate must stay green throughout (modes default to current behavior, so it will).
- **Branching discipline:** branch `feature/portfolio-construction-v2` from origin/main (already fetched, in sync).
- Weights sum to 1.0 within 1e-9 after all adjustments (spec A1).
- Every rebalance event carries a machine-readable `kind`: `membership` | `tier` | `resize_monthly` | `sizing_migration_invvol` | `manual_resize` (spec A2 asks for a typed reason; we add `kind` alongside the existing human-readable `reason` so old events stay valid).

**File map:**
- Create: `scripts/position_sizing.py`, `scripts/score_history.py`, `scripts/migrate_portfolio_v2.py`, `tracking/portfolio-config.json`, `docs/superpowers/specs/2026-08-07-portfolio-construction-v2-spec.md` (copy of Dom's spec)
- Modify: `scripts/portfolio_sizing.py`, `scripts/portfolio_model.py`, `scripts/refresh_targets.py`, `scripts/recalc_watchlist.py`, `scripts/export_site_data.py`, `site/js/performance.js`, `site/js/common.js`, `tests/test_portfolio_sizing.py`, `CLAUDE.md`
- Test (new): `tests/test_position_sizing.py`, `tests/test_topn_selection.py`, `tests/test_score_history.py`, `tests/test_band_shadows.py`

---

### Task 0: Branch + spec copy + config scaffold

**Files:**
- Create: `tracking/portfolio-config.json`
- Create: `docs/superpowers/specs/2026-08-07-portfolio-construction-v2-spec.md`
- Modify: `scripts/portfolio_model.py` (add `load_pcfg`)

**Interfaces:**
- Produces: `portfolio_model.load_pcfg() -> dict` with keys `sizing` (mode/lookback/sigma_floor/max_weight/min_weight/drift_band), `selection` (mode), `shadows` (top/next/tail). Defaults merged under any committed file so missing keys never KeyError.

- [x] **Step 1:** `git checkout -b feature/portfolio-construction-v2 origin/main`
- [x] **Step 2:** Copy `/Users/dom/Downloads/portfolio-construction-v2-spec.md` to `docs/superpowers/specs/2026-08-07-portfolio-construction-v2-spec.md` (repo convention: specs live in-repo).
- [x] **Step 3:** Write `tracking/portfolio-config.json`:

```json
{
  "_comment": "Portfolio-construction v2 switches + params (spec 2026-08-07). Modes stay tier/score until Dom approves the migration (scripts/migrate_portfolio_v2.py --apply). Selection N/M live on the Sizing Rules sheet (rule 26); this file owns sizing params and the mode switches.",
  "sizing": {
    "mode": "tier",
    "lookback": 60,
    "sigma_floor": 0.005,
    "max_weight": 0.12,
    "min_weight": 0.03,
    "drift_band": 0.25
  },
  "selection": { "mode": "score" },
  "shadows": { "top": 15, "next": 25, "tail": 40 }
}
```

- [x] **Step 4:** Add to `scripts/portfolio_model.py` (after `save_cfg`):

```python
PCONFIG = ROOT / 'tracking' / 'portfolio-config.json'

DEFAULT_PCFG = {
    # Spec 2026-08-07 §A1/§B1/§C1. Do NOT tune against the 10-week history.
    'sizing': {'mode': 'tier', 'lookback': 60, 'sigma_floor': 0.005,
               'max_weight': 0.12, 'min_weight': 0.03, 'drift_band': 0.25},
    'selection': {'mode': 'score'},
    'shadows': {'top': 15, 'next': 25, 'tail': 40},
}


def load_pcfg() -> dict:
    """Construction-v2 config: committed values merged over defaults, so a
    missing file or missing key falls back to current (tier/score) behavior."""
    try:
        raw = json.loads(PCONFIG.read_text())
    except (OSError, ValueError):
        raw = {}
    return {k: {**v, **(raw.get(k) or {})} for k, v in DEFAULT_PCFG.items()}
```

- [x] **Step 5:** Sanity: `python3 -c "import sys; sys.path.insert(0,'scripts'); from portfolio_model import load_pcfg; print(load_pcfg())"` → shows merged dict with `mode: tier`.
- [x] **Step 6:** Commit: `git add -A && git commit -m "feat(v2): config scaffold + spec copy for portfolio construction v2"`

---

### Task 1: Inverse-vol sizing pure functions (spec A1)

**Files:**
- Create: `scripts/position_sizing.py`
- Test: `tests/test_position_sizing.py`

**Interfaces:**
- Produces: `cap_floor_normalize(raw: dict[str,float], max_w: float, min_w: float) -> dict[str,float]` (sums to 1.0); `inverse_vol_weights(prices, roster: list[str], cfg: dict, layers: dict[str,str]|None) -> dict[str,float]` where `prices` is a wide pandas DataFrame of adjusted closes (columns=tickers). Consumed by Task 5 (refresh_targets) and Task 7 (migration).

- [x] **Step 1:** Write failing tests `tests/test_position_sizing.py` (names per spec Tests section):

```python
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


def test_drift_band():
    target = {'A': 0.08, 'B': 0.08, 'C': 0.08}
    inside = {'A': 0.081, 'B': 0.099, 'C': 0.061}            # all within ±25% rel
    w, traded = drift_band_filter(inside, target, band=0.25)
    assert traded == [] and w == inside                      # inside -> no trades
    outside = {'A': 0.081, 'B': 0.11, 'C': 0.05}             # B,C breach
    w, traded = drift_band_filter(outside, target, band=0.25)
    assert sorted(traded) == ['B', 'C']
    assert w['B'] / w['C'] == pytest.approx(1.0)             # both back to target ratio
    assert sum(w.values()) == pytest.approx(sum(target.values()), abs=1e-9)
```

- [x] **Step 2:** `python3 -m pytest tests/test_position_sizing.py -q` → FAIL (`ModuleNotFoundError: position_sizing`).
- [x] **Step 3:** Write `scripts/position_sizing.py`:

```python
"""Inverse-volatility position sizing + drift-band re-size filter (v2 Part A).

Pure functions: no yfinance, no workbook I/O, no network. pandas is imported
lazily inside functions so the openpyxl-only deploy CI can import this module
(see reference_ci_minimal_env_lazy_imports). Sizing params live in
tracking/portfolio-config.json -> `sizing` (portfolio_model.load_pcfg).
Spec: docs/superpowers/specs/2026-08-07-portfolio-construction-v2-spec.md
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
    rets = prices.pct_change()
    sigma: dict[str, float] = {}
    short: list[str] = []
    for t in roster:
        r = (rets[t].dropna().iloc[-lookback:] if t in rets.columns
             else pd.Series(dtype=float))
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
```

- [x] **Step 4:** `python3 -m pytest tests/test_position_sizing.py -q` → 6 passed.
- [x] **Step 5:** CI-safety check (no pandas at import): `python3 -c "import ast,sys; t=ast.parse(open('scripts/position_sizing.py').read()); assert not [n for n in t.body if isinstance(n,(ast.Import,ast.ImportFrom)) and 'pandas' in ast.dump(n)]; print('lazy OK')"`
- [x] **Step 6:** Commit: `git add scripts/position_sizing.py tests/test_position_sizing.py && git commit -m "feat(v2): inverse-vol sizing pure functions (spec Part A1/A2)"`

---

### Task 2: Top-N selection pure functions (spec B1)

**Files:**
- Modify: `scripts/portfolio_sizing.py` (append)
- Test: `tests/test_topn_selection.py`

**Interfaces:**
- Produces: `rank_by_score(live: list[dict], prior: set[str]) -> list[str]` (tickers sorted by TOTAL desc, ties → incumbent first, then ticker for determinism); `topn_membership(prior: set[str], ranked: list[str], n: int, m: int) -> tuple[list[str], list[str], list[str]]` returning `(include, entered, exit_crossers)`. `exit_crossers` feed the existing rule-26 2-run confirm clock in refresh() — the pure function does NOT exit them itself. Consumed by Task 5.

- [x] **Step 1:** Write failing tests `tests/test_topn_selection.py`:

```python
"""Top-N selection with rank hysteresis (spec 2026-08-07 Part B)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from portfolio_sizing import rank_by_score, topn_membership


def _ranked(n):
    return [f'T{i:02d}' for i in range(1, n + 1)]   # T01 = rank 1 ... 


def test_topn_entry_exit_hysteresis():
    ranked = _ranked(30)
    # outsider at rank 15 enters; incumbent at 17 stays; incumbent at 19
    # crosses the exit line; outsider at 16 does not enter.
    prior = {'T17', 'T19'} | set(_ranked(14)[:13])   # 13 top names + 2 stragglers
    include, entered, exit_crossers = topn_membership(prior, ranked, n=15, m=18)
    assert 'T14' in entered and 'T15' in entered      # outsiders in top-15 enter
    assert 'T16' not in include                       # dead-band outsider stays out
    assert 'T17' in include and 'T17' not in entered  # dead-band incumbent holds
    assert exit_crossers == ['T19']                   # below M -> exit crossing
    assert 'T19' not in include


def test_tie_break():
    live = [{'ticker': 'AAA', 'TOTAL': 80.0}, {'ticker': 'BBB', 'TOTAL': 80.0},
            {'ticker': 'CCC', 'TOTAL': 90.0}]
    # incumbency breaks the AAA/BBB tie in BBB's favor
    assert rank_by_score(live, prior={'BBB'}) == ['CCC', 'BBB', 'AAA']
    # no incumbents: deterministic (ticker) order, higher score still first
    assert rank_by_score(live, prior=set()) == ['CCC', 'AAA', 'BBB']


def test_rank_stability():
    """A methodology reshuffle produces a membership DIFF through the normal
    event path (entered/exit_crossers), never a silent resort: unchanged
    incumbents inside M are still included, every change is enumerated."""
    ranked_before = _ranked(30)
    prior = set(ranked_before[:15])
    inc0, ent0, ex0 = topn_membership(prior, ranked_before, 15, 18)
    assert (ent0, ex0) == ([], [])                    # steady state: no diff
    reshuffled = list(reversed(ranked_before))        # en-masse rank flip
    inc1, ent1, ex1 = topn_membership(prior, reshuffled, 15, 18)
    assert set(ent1) == set(ranked_before[16:30][-14:]) - prior  # new top names enumerated
    assert set(ex1) == {t for t in prior
                        if reshuffled.index(t) + 1 > 18}          # every exit enumerated
    assert set(inc1) == (prior - set(ex1)) | set(ent1)            # diff-complete, no resort
```

- [x] **Step 2:** `python3 -m pytest tests/test_topn_selection.py -q` → FAIL (ImportError).
- [x] **Step 3:** Append to `scripts/portfolio_sizing.py`:

```python
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
```

- [x] **Step 4:** `python3 -m pytest tests/test_topn_selection.py tests/test_portfolio_sizing.py -q` → all pass.
- [x] **Step 5:** Commit: `git add -A && git commit -m "feat(v2): top-N rank selection with hysteresis dead-band (spec Part B1)"`

---

### Task 3: Point-in-time score panel (spec C2)

**Files:**
- Create: `scripts/score_history.py`
- Modify: `scripts/recalc_watchlist.py` (hook in `sync_scores`)
- Test: `tests/test_score_history.py`

**Interfaces:**
- Produces: `score_history.append_snapshot(results: list[dict], when: str|None) -> int` (rows appended; 0 when `when` already logged). `results` is `recalc()` output. Writes `tracking/score-history.csv` with header `date,ticker,total_score,rank,tier`. Consumed by `sync_scores()` and Task 5 (`refresh()`).

- [x] **Step 1:** Write failing test `tests/test_score_history.py`:

```python
"""Append-only point-in-time score panel (spec 2026-08-07 Part C2)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import score_history as sh

LIVE = [
    {'ticker': 'AAA', 'TOTAL': 81.25, 'Tier': '✓✓'},
    {'ticker': 'BBB', 'TOTAL': 90.0, 'Tier': '✓✓✓'},
    {'ticker': 'NUL', 'TOTAL': None, 'Tier': None},   # unscored: skipped
]


def test_score_history_append_only(tmp_path, monkeypatch):
    csv = tmp_path / 'score-history.csv'
    monkeypatch.setattr(sh, 'CSV', csv)
    n = sh.append_snapshot(LIVE, when='2026-08-07')
    assert n == 2                                     # exactly one row per scored name
    lines = csv.read_text().splitlines()
    assert lines[0] == 'date,ticker,total_score,rank,tier'
    assert lines[1] == '2026-08-07,BBB,90.00,1,✓✓✓'   # rank 1 = highest score
    assert lines[2] == '2026-08-07,AAA,81.25,2,✓✓'
    before = csv.read_text()
    assert sh.append_snapshot(LIVE, when='2026-08-07') == 0   # re-run: no dupes
    assert csv.read_text() == before                          # ... and no rewrite
    assert sh.append_snapshot(LIVE, when='2026-08-08') == 2   # next pass appends
    assert csv.read_text().startswith(before)                 # strictly append-only
```

- [x] **Step 2:** Run → FAIL (ImportError).
- [x] **Step 3:** Write `scripts/score_history.py`:

```python
"""Point-in-time score panel (spec 2026-08-07 Part C2).

Every scoring pass appends the full ranked watchlist to
tracking/score-history.csv — the panel that the future IC test, band analysis
and any cutoff/backtest work require (backfill is impossible, which is why
logging starts now and never skips a pass). Append-only: one snapshot per
date; re-running a pass the same day is a no-op (first pass of the day wins),
and committed rows are never rewritten.
"""
from __future__ import annotations

import datetime as dt

from common import ROOT

CSV = ROOT / 'tracking' / 'score-history.csv'
HEADER = 'date,ticker,total_score,rank,tier\n'


def append_snapshot(results, when: str | None = None) -> int:
    """Append one `date,ticker,total_score,rank,tier` row per scored name.

    results: recalc_watchlist.recalc() output. Returns rows appended (0 when
    `when` is already logged — idempotent re-runs, no duplicates, no rewrite).
    """
    when = when or dt.date.today().isoformat()
    live = sorted((x for x in results if x.get('TOTAL') is not None),
                  key=lambda x: -x['TOTAL'])
    if not live:
        return 0
    if CSV.exists():
        with CSV.open() as f:
            if any(line.startswith(when + ',') for line in f):
                return 0
    else:
        CSV.write_text(HEADER)
    with CSV.open('a') as f:
        for i, x in enumerate(live):
            f.write(f"{when},{x['ticker']},{x['TOTAL']:.2f},{i + 1},"
                    f"{x['Tier'] or ''}\n")
    return len(live)
```

- [x] **Step 4:** Hook into `scripts/recalc_watchlist.py` `sync_scores()` — after `results = recalc(xlsx, mode='percentile')` add:

```python
    # Point-in-time score panel (v2 spec C2): --sync is the finalize step of
    # every scoring pass (rule 25), so logging here catches weekly scans,
    # quarterly rescores and ad-hoc passes without per-caller wiring.
    try:
        from score_history import append_snapshot
        append_snapshot(results)
    except OSError as e:
        print(f'score-history append failed (non-fatal): {e}')
```

- [x] **Step 5:** `python3 -m pytest tests/test_score_history.py -q` → pass. Run `python3 -m pytest tests/test_recalc_idempotent.py tests/test_recalc_modes.py -q` → still pass.
- [x] **Step 6:** Seed the panel (first snapshot, real data): `cd /Users/dom/Desktop/ai-stocks/scripts && python3 -c "from recalc_watchlist import recalc; from score_history import append_snapshot; print(append_snapshot(recalc()))"` → ~214.
- [x] **Step 7:** Commit: `git add -A && git commit -m "feat(v2): append-only point-in-time score panel (spec Part C2)"`

---

### Task 4: Chain-link generalization + shadow series in the tracker (spec A4, C1)

**Files:**
- Modify: `scripts/portfolio_model.py`
- Test: `tests/test_band_shadows.py`

**Interfaces:**
- Produces: `chain_linked_growth(events: list[dict], inception: str, idx) -> pd.Series|None` (extracted body of `ew_growth`; NaN before the first event date); `model_roster_events(cfg) -> list[dict]` (`[{date, roster}]` from `cfg['events']` allocations); `build_daily_series` output gains `bench` keys `EW_ROSTER` (always) and `BAND_TOP`/`BAND_NEXT`/`BAND_TAIL` (when `cfg['shadow_events']` holds them), with JSON `null` padding before each shadow's first event. Consumed by Task 6 (exporter/site).

- [x] **Step 1:** Refactor `ew_growth` — extract everything after the `idx` setup into:

```python
def chain_linked_growth(events, inception: str, idx):
    """Chain-linked equal-weight growth-of-1 over [{date, roster}] events.

    Extracted from ew_growth (2026-08-07) so the EW benchmark, the EW_ROSTER
    sizing-null shadow (spec A4) and the band shadows (spec C1) share one
    engine: within each roster period an equal-weight basket, re-based to the
    prior period's closing level at each splice — no splice return, no
    look-ahead, forward-only from the first event (NaN before it)."""
    import pandas as pd

    inc_date = dt.date.fromisoformat(inception)

    def gfull(t):
        s = _series(t, inception)
        if s is None:
            return None
        s = s[s.index.date >= inc_date]
        if s.empty or s.iloc[0] == 0:
            return None
        return (s / s.iloc[0]).reindex(idx).ffill()

    events = sorted(events, key=lambda e: e['date'])
    out = pd.Series(index=idx, dtype=float)
    level = 1.0
    anchor = None
    for i, ev in enumerate(events):
        start = dt.date.fromisoformat(ev['date'])
        end = (dt.date.fromisoformat(events[i + 1]['date'])
               if i + 1 < len(events) else None)
        mask = idx.date >= start
        if end is not None:
            mask &= idx.date < end
        if not mask.any():
            continue
        seg_idx = idx[mask]
        parts = []
        for t in ev['roster']:
            g = gfull(t)
            if g is None:
                continue
            base = g.loc[anchor] if anchor is not None else g.loc[seg_idx[0]]
            if base != base or base == 0:
                continue
            parts.append(g.reindex(seg_idx) / base)
        if not parts:
            continue
        seg = level * pd.concat(parts, axis=1).mean(axis=1)
        out[seg_idx] = seg
        level = float(seg.iloc[-1])
        anchor = seg_idx[-1]
    out = out.ffill()
    return None if out.isna().all() else out
```

`ew_growth(cfg, idx=None)` keeps only its idx-bootstrapping (SMH calendar) and ends with `return chain_linked_growth(ew_roster_events(cfg), cfg['inception'], idx)`. NOTE: `out = out.ffill()` intentionally does NOT backfill — a shadow starting mid-history stays NaN before its first event (forward-only guarantee).

- [x] **Step 2:** Add `model_roster_events` after `ew_roster_events`:

```python
def model_roster_events(cfg: dict) -> list[dict]:
    """[{date, roster}] mirroring the model's actual event history — the
    EW_ROSTER sizing-null (spec A4): same names, same event dates, equal
    weights. MODEL − EW_ROSTER is the standing measure of what the sizing
    rule adds; the permanent tripwire input."""
    return [{'date': ev['date'], 'roster': sorted(ev['allocations'])}
            for ev in cfg['events']]
```

- [x] **Step 3:** In `build_daily_series`, after the `ew` block, build the new series; change the output assembly to:

```python
    shadows: dict[str, list] = {}
    ew_roster = chain_linked_growth(model_roster_events(cfg), inception, idx)
    if ew_roster is not None:
        shadows['EW_ROSTER'] = ew_roster
    for name, evs in (cfg.get('shadow_events') or {}).items():
        s = chain_linked_growth(evs, inception, idx)
        if s is not None:
            shadows[name] = s          # NaN before first event = pre-deploy

    def pad(series):
        """Round; leading NaN (pre-first-event) becomes JSON null."""
        return [None if v != v else round(float(v), 6) for v in series]

    out = {
        'start': inception,
        'as_of': str(idx[-1].date()),
        'dates': [str(d.date()) for d in idx],
        'model': [round(float(v), 2) for v in model],
        'bench': {
            'SMH': [round(float(v), 6) for v in smh.reindex(idx).ffill()],
            'QQQ': [round(float(v), 6) for v in qqq.reindex(idx).ffill()],
            'SPY': [round(float(v), 6) for v in spy.reindex(idx).ffill()],
            'EW': [round(float(v), 6) for v in ew],
            **{name: pad(s) for name, s in shadows.items()},
        },
    }
```

and scope the NaN guard so shadow padding is allowed but core series stay strict:

```python
    strict = [out['model']] + [out['bench'][k] for k in ('SMH', 'QQQ', 'SPY', 'EW')]
    if any(v != v for series in strict for v in series):
        flag('series: NaN in output — series not written')
        return None
```

- [x] **Step 4:** Write `tests/test_band_shadows.py` — fake `_series` in the `test_ew_chainlink.py` style:

```python
"""Band shadows + EW_ROSTER series (spec 2026-08-07 A4/C1) and the event-log
roundtrip guarantee (spec A2: series fully reconstructible from events)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
pytest.importorskip('yfinance')
pd = pytest.importorskip('pandas')

import portfolio_model as pm

DATES = pd.to_datetime(['2026-05-26', '2026-05-27', '2026-05-28',
                        '2026-05-29', '2026-06-01'])
PRICES = {'SMH': [10, 10, 10, 10, 10], 'QQQ': [10, 10, 10, 10, 10],
          'SPY': [10, 10, 10, 10, 10],
          'AAA': [100, 110, 121, 133, 146], 'BBB': [50, 50, 60, 72, 72]}


@pytest.fixture
def fake_prices(monkeypatch):
    def fake_series(ticker, earliest):
        if ticker not in PRICES:
            return None
        return pd.Series(PRICES[ticker], index=DATES, dtype=float)
    pm._series_cache.clear()
    monkeypatch.setattr(pm, '_series', fake_series)


CFG = {
    'inception': '2026-05-26', 'capital': 10000.0,
    'ew_universe': ['AAA', 'BBB'],
    'events': [
        {'date': '2026-05-26', 'reason': 'initial', 'kind': 'membership',
         'allocations': {'AAA': 6000.0, 'BBB': 4000.0}, 'cash': 0.0},
        {'date': '2026-05-28', 'reason': 'resize_monthly', 'kind': 'resize_monthly',
         'allocations': {'AAA': 5000.0, 'BBB': 5900.0}, 'cash': 0.0},
    ],
    'shadow_events': {
        'BAND_TOP': [{'date': '2026-05-28', 'roster': ['AAA']}],   # starts mid-history
    },
}


def test_ew_roster_mirrors_model_events(fake_prices):
    evs = pm.model_roster_events(CFG)
    assert evs == [{'date': '2026-05-26', 'roster': ['AAA', 'BBB']},
                   {'date': '2026-05-28', 'roster': ['AAA', 'BBB']}]


def test_shadow_series_forward_only_null_padded(fake_prices, tmp_path, monkeypatch):
    monkeypatch.setattr(pm, 'SERIES', tmp_path / 'series.json')
    out = pm.build_daily_series(CFG)
    top = out['bench']['BAND_TOP']
    assert top[0] is None and top[1] is None          # pre-deploy: null, no backfill
    assert top[2] == 1.0                              # growth-of-1 from first event
    assert top[3] == pytest.approx(133 / 121, rel=1e-4)
    assert 'EW_ROSTER' in out['bench']                # sizing-null always present


def test_band_rosters_disjoint_and_complete():
    ranked = [f'T{i:02d}' for i in range(1, 50)]
    shadows = {'top': 15, 'next': 25, 'tail': 40}
    top = ranked[:shadows['top']]
    nxt = ranked[shadows['top']:shadows['next']]
    tail = ranked[shadows['next']:shadows['tail']]
    assert top + nxt + tail == ranked[:40]            # partition of ranks 1-40
    assert not (set(top) & set(nxt)) and not (set(nxt) & set(tail))


def test_event_log_roundtrip(fake_prices, tmp_path, monkeypatch):
    """A resize event reproduces an identical daily series on tracker re-run:
    the events log alone fully determines the series (spec A2)."""
    monkeypatch.setattr(pm, 'SERIES', tmp_path / 'series.json')
    out1 = pm.build_daily_series(CFG)
    bytes1 = (tmp_path / 'series.json').read_bytes()
    pm._series_cache.clear()
    out2 = pm.build_daily_series(json.loads(json.dumps(CFG)))   # fresh cfg copy
    bytes2 = (tmp_path / 'series.json').read_bytes()
    assert out1 == out2 and bytes1 == bytes2          # byte-identical repeat run
    # and the resize splice is continuous: model value on 05-28 equals the
    # marked value the event re-allocated (5000+5900), with no jump injected
    d = out1['dates'].index('2026-05-28')
    assert out1['model'][d] == pytest.approx(10900.0)
```

- [x] **Step 5:** `python3 -m pytest tests/test_band_shadows.py tests/test_ew_chainlink.py tests/test_track_performance.py tests/test_series_regression_guard.py -q` → all pass (refactor regression-guarded by the existing chain-link tests).
- [x] **Step 6:** Commit: `git add -A && git commit -m "feat(v2): EW_ROSTER + band shadow series via generalized chain-link engine (spec A4/C1)"`

---

### Task 5: refresh_targets — mode switches, rank membership, shadow roster upkeep (spec B1/B2, C1)

**Files:**
- Modify: `scripts/refresh_targets.py`
- Test: extend `tests/test_refresh_targets.py`

**Interfaces:**
- Consumes: `load_pcfg` (Task 0), `rank_by_score`/`topn_membership` (Task 2), `append_snapshot` (Task 3).
- Produces: `refresh()` honoring `selection.mode == 'rank'` (Entry rank/Exit rank from the Sizing Rules sheet; dead/override/pending-clock/max-positions machinery unchanged); band shadow roster upkeep in `cfg['shadow_events']` on every real run; `log_rebalance` events carrying `kind`.

- [x] **Step 1:** In `load_cfg`-adjacent imports add `load_pcfg` and the Task-2 functions; in `NEW_PARAMS` change the two rank rows (seed values only — the live sheet is updated by migration, rule 26):

```python
    ('Entry rank', 15, 'selection.mode=rank: non-holding ENTERs at rank <= N (spec B1)'),
    ('Exit rank', 18, 'selection.mode=rank: holding EXITs below rank M; N+1..M is the dead-band'),
```

- [x] **Step 2:** In `refresh()`, after `p = load_params(sizing)` add `pcfg = load_pcfg()`; after the `live`/`rank`/`info` block insert the mode-conditional membership predicates, replacing the inline score comparisons in the two membership loops (keeps/enters + status strings). Full replacement block for the membership section:

```python
    sel_mode = pcfg['selection']['mode']
    if sel_mode == 'rank':
        # Top-N selection (spec B1): ranks replace absolute score lines. The
        # dead-band N+1..M is the hysteresis; the rule-26 2-run confirm clock
        # still wraps every exit crossing (continuity decision, plan Task 5).
        entry_rank = int(p.get('Entry rank', 15))
        exit_rank = int(p.get('Exit rank', 18))
        ranked = rank_by_score(live, prior_include)
        rank = {t: i + 1 for i, t in enumerate(ranked)}   # incumbency tie-break
        keeps = lambda t: t in info and rank[t] <= exit_rank
        enters = lambda t: rank[t] <= entry_rank
        why = lambda t: f'rank {rank.get(t, "—")}, score {info[t]["TOTAL"]:.1f}'
        below = lambda t: f'rank {rank.get(t, "—")} > {exit_rank}'
    else:
        keeps = lambda t: t in info and info[t]['TOTAL'] >= exit_score
        enters = lambda t: info[t]['TOTAL'] >= entry_score
        why = lambda t: f'score {info[t]["TOTAL"]:.1f}'
        below = lambda t: f'score {info[t]["TOTAL"]:.1f} < {exit_score}'
```

Then rewrite the two loops to use `keeps(t)` / `enters(t)` / `why(t)` / `below(t)` in place of the literal `info[t]['TOTAL'] >= exit_score`-style expressions and their f-string status texts (statuses become e.g. `f'ENTER ({why(t)})'`, `f'EXIT PENDING ({below(t)}, since {…})'`). Freshness-gate candidates in rank mode: `{t for t in info if rank[t] <= exit_rank}` replaces the `>= exit_score` set. **Everything else in the loops — dead names, overrides, `--resize` immediate exits, the exit-pending clock, max_positions, BLOCKED — is untouched.** B2's audit line: whenever `sel_mode == 'rank'` and a rank crossing would trade, the existing `flag(...)` calls fire — they already print on every enter/exit; add rank to the text via `why(t)`.

- [x] **Step 3:** Band shadow roster upkeep (spec C1) — add helper + call it right before the `if dry_run:` block (shadows update on every real run, frozen or not, forward-only):

```python
def _update_band_shadows(cfg: dict, live: list, pcfg: dict, today: str) -> bool:
    """Refresh BAND_TOP/NEXT/TAIL rosters from today's ranks (spec C1).
    Pure-score ranking (no incumbency): the bands are unsized scouts, not the
    book. Appends a shadow event only when a roster actually changed;
    forward-only (first event = first real run after deploy). Returns True
    when anything changed (caller persists cfg)."""
    sh = pcfg['shadows']
    ranked = [x['ticker'] for x in
              sorted(live, key=lambda x: (-x['TOTAL'], x['ticker']))]
    rosters = {'BAND_TOP': ranked[:sh['top']],
               'BAND_NEXT': ranked[sh['top']:sh['next']],
               'BAND_TAIL': ranked[sh['next']:sh['tail']]}
    events = cfg.setdefault('shadow_events', {})
    changed = False
    for name, roster in rosters.items():
        evs = events.setdefault(name, [])
        if evs and sorted(evs[-1]['roster']) == sorted(roster):
            continue
        if evs and evs[-1]['date'] == today:
            evs[-1] = {'date': today, 'roster': roster}   # same-day idempotence
        else:
            evs.append({'date': today, 'roster': roster})
        changed = True
        flag(f'shadow {name}: roster refreshed ({len(roster)} names)')
    return changed
```

Call site (before `if dry_run:`): `shadows_changed = False if dry_run else _update_band_shadows(cfg, live, pcfg, today)`; extend the frozen-path persist condition to `if new_pending != dict(cfg.get('exit_pending', {})) or shadows_changed:` (and set `cfg['exit_pending'] = new_pending` before saving). On the fire path `log_rebalance` already saves cfg, carrying the shadow events with it.

- [x] **Step 4:** Score-history hook — in `refresh()` right after the `live` list is built: `if not dry_run: __import__('score_history').append_snapshot(live)` (idempotent with the sync_scores hook by date-dedupe; write it as a proper import at top of function, lazy for CI).

- [x] **Step 5:** `log_rebalance` gains `kind`: signature `log_rebalance(cfg, weights, reason, tiers=None, kind='membership')`, event dict gains `'kind': kind`. `refresh()` passes `kind='tier'` when only a tier change fired, `'manual_resize'` for `--resize`, else `'membership'`.

- [x] **Step 6:** New tests in `tests/test_refresh_targets.py` (reuse `_build_portfolio`/`_mock_env`; add `Entry rank`/`Exit rank` rows to the fixture sheet; monkeypatch `rt.load_pcfg` to `{'selection': {'mode': 'rank'}, 'sizing': {...tier...}, 'shadows': {...}}`):
  - `test_rank_mode_entry_and_deadband`: 20 live names, prior holds ranks 1–14 + rank 17 + rank 19; expect rank-15 outsider ENTERs, rank-16 outsider stays out, rank-17 incumbent HOLDs, rank-19 incumbent goes EXIT PENDING (clock, not immediate).
  - `test_rank_mode_exit_confirms_next_run`: same but with a prior-dated pending clock → rank-19 incumbent exits, `fire` True, reason contains the ticker.
  - `test_shadow_events_appended_on_real_run`: after a non-dry run, `cfg['shadow_events']['BAND_TOP']` exists with today's date and 15 names; a same-day second run appends nothing new.
  - `test_shadow_events_not_touched_on_dry_run`.
- [x] **Step 7:** `python3 -m pytest tests/test_refresh_targets.py tests/test_topn_selection.py -q` → all pass. Then the full-suite gate check: `python3 -m pytest tests/ -q` (score-mode defaults must leave every existing test green, including `test_targets_reweight_gate`).
- [x] **Step 8:** Commit: `git add -A && git commit -m "feat(v2): rank-mode selection + band shadow upkeep in refresh_targets (spec B/C1)"`

---

### Task 6: refresh_targets — inverse-vol sizing mode + monthly drift-band re-size (spec A1/A2)

**Files:**
- Modify: `scripts/refresh_targets.py`, `scripts/portfolio_model.py` (mark → current weights helper), `tests/test_portfolio_sizing.py` (scope the monotonic gate)
- Test: extend `tests/test_refresh_targets.py`

**Interfaces:**
- Consumes: `inverse_vol_weights`, `drift_band_filter` (Task 1).
- Produces: `refresh()` honoring `sizing.mode == 'inverse_vol'`; monthly re-size events (`kind='resize_monthly'`) gated by `cfg['sizing_state']['last_resize_check']` (YYYY-MM); `portfolio_model.current_weights(cfg) -> dict[str,float]|None`.

- [x] **Step 1:** Add to `portfolio_model.py`:

```python
def current_weights(cfg: dict) -> dict[str, float] | None:
    """Mark-to-market weight of each held name as a fraction of model value —
    the drifted 'current' side of the spec-A2 drift band. None if every price
    is missing (never guess; rule 3)."""
    ev = cfg['events'][-1]
    value, pnl, missing = mark(cfg)
    if not value or len(missing) == len(ev['allocations']):
        return None
    return {t: (alloc + pnl.get(t, 0.0)) / value
            for t, alloc in ev['allocations'].items()}
```

- [x] **Step 2:** In `refresh()` replace the sizing block (`base = ...; weights = cap_and_normalize(...)`) with:

```python
    siz = pcfg['sizing']
    if siz['mode'] == 'inverse_vol':
        # Spec A1: the score chooses the names, trailing vol chooses the sizes.
        prices = _price_frame(include, int(siz['lookback']))
        inv = inverse_vol_weights(prices, include, siz,
                                  layers={t: layers[t] for t in include})
        weights = {t: w * (1.0 - cash) for t, w in inv.items()}
    else:
        base = {t: base_weight(info[t]['TOTAL'], p['tiers']) for t in include}
        weights = cap_and_normalize(base, layers, 1.0 - cash, max_single,
                                    layer_cap)
```

with the price loader (module level, lazy imports):

```python
def _price_frame(tickers: list[str], lookback: int):
    """Wide adjusted-close frame for the sizing window, via the tracker's
    cached _series (dividend-adjusted, serialized fetches)."""
    import pandas as pd
    from portfolio_model import _series
    earliest = (dt.date.today()
                - dt.timedelta(days=int(lookback * 2.2) + 10)).isoformat()
    return pd.DataFrame({t: s for t in tickers
                         if (s := _series(t, earliest)) is not None})
```

- [x] **Step 3:** Rebalance-gate changes, replacing the current `fire = ...` line:

```python
    # Tier crossings re-size the book only under tier sizing; under inverse-vol
    # they carry no weight information (spec A0: stop using the score as sizer)
    # but still refresh the stored tier baseline via the monthly path.
    tier_fire = bool(tier_chg) and siz['mode'] != 'inverse_vol'
    fire = bool(entered or exited) or tier_fire or resize
    kind = ('manual_resize' if resize and not (entered or exited) else
            'membership' if (entered or exited) else 'tier')

    # Spec A2: monthly scheduled re-size, first real run of a new calendar
    # month, trading only names outside the drift band. Online real runs only
    # (mark() prices the book): dry runs and the offline rule-25 gate never
    # see or advance it, so pending_rebalance() stays offline-pure.
    if (siz['mode'] == 'inverse_vol' and not fire and not dry_run
            and check_freshness):
        state = cfg.setdefault('sizing_state', {})
        if today[:7] > state.get('last_resize_check', ''):
            cur = current_weights(cfg)
            if cur is None:
                flag('monthly re-size skipped: no prices to mark the book')
            else:
                new_w, traded = drift_band_filter(cur, weights,
                                                  float(siz['drift_band']))
                state['last_resize_check'] = today[:7]
                if traded:
                    weights = new_w
                    fire, kind = True, 'resize_monthly'
                    flag(f'monthly re-size: {", ".join(traded)} outside '
                         f'±{siz["drift_band"]:.0%} band — trading to target')
                else:
                    flag('monthly re-size: all names inside the drift band — '
                         'no trades')
```

`log_rebalance(..., kind=kind)` on the fire path; reason for monthly events: `f'resize_monthly: {", ".join(traded)} outside drift band'` (extend `build_reason` call accordingly: when `kind == 'resize_monthly'` bypass `build_reason`). A fired full re-size of any kind also stamps `cfg.setdefault('sizing_state', {})['last_resize_check'] = today[:7]` (a membership event IS that month's re-size). The frozen-path persist condition extends to include `sizing_state` changes.

- [x] **Step 4:** Scope the monotonic sanity check + gate to tier mode: wrap the in-refresh `weights_score_monotonic` check in `if siz['mode'] != 'inverse_vol':`, and in `tests/test_portfolio_sizing.py::test_targets_weights_monotonic` add at the top:

```python
    from portfolio_model import load_pcfg
    if load_pcfg()['sizing']['mode'] == 'inverse_vol':
        pytest.skip('rule-18 monotonicity gate applies to tier sizing only; '
                    'inverse-vol weights are deliberately not score-ordered '
                    '(v2 spec A0) — EW_ROSTER shadow is the sizing audit now')
```

- [x] **Step 5:** New tests in `tests/test_refresh_targets.py` (pcfg monkeypatched to `sizing.mode='inverse_vol'`, `rt._price_frame` monkeypatched to a synthetic frame, `pm`-level `mark`/`current_weights` mocked for the drift tests):
  - `test_invvol_mode_weights_from_vol_not_score`: two held names, higher-vol name gets the smaller weight even with the higher score; no monotonicity flag raised.
  - `test_monthly_resize_fires_outside_band`: last event a month ago, one name drifted outside band → `fire`, event `kind == 'resize_monthly'`, only after `last_resize_check` month rolls.
  - `test_monthly_resize_noop_inside_band`: drift inside band → no event, `last_resize_check` stamped, second run same month does not re-check.
  - `test_dry_run_never_touches_sizing_state`.
- [x] **Step 6:** Full suite: `python3 -m pytest tests/ -q` → green (live modes still tier/score).
- [x] **Step 7:** Commit: `git add -A && git commit -m "feat(v2): inverse-vol sizing mode + monthly drift-band re-size (spec A1/A2)"`

---

### Task 7: Surface EW_ROSTER + bands on the site (spec A4/C1)

**Files:**
- Modify: `scripts/export_site_data.py`, `site/js/performance.js`, `site/js/common.js`
- Test: extend `tests/test_export_site_data.py` (one test)

**Interfaces:**
- Consumes: `performance-series.json` bench keys from Task 4.
- Produces: `site/data/performance.json` `bench` carries any of `EW_ROSTER`/`BAND_TOP`/`BAND_NEXT`/`BAND_TAIL` present in the source (null-padded, notional-scaled); Performance tab plots them.

- [x] **Step 1:** In `export_site_data.py`, the bench scaling currently assumes floats. Replace with a null-tolerant scale and pass through all keys:

```python
    bench = {name: [None if g is None else round(g * NOTIONAL, 2)
                    for g in series]
             for name, series in raw['bench'].items()}
```

The required-keys check stays exactly as-is (`SMH/QQQ/SPY/EW` mandatory; shadows optional). The `total()` / `vs_*` headline calcs keep using the four required benches only — shadows are scouts, not headline comparisons; add `'vs_ew_roster': total(model) - total(bench['EW_ROSTER'])` **only when the key exists and its first value is not None** (it starts null-padded mid-series, so compute from its first non-null index):

```python
    if 'EW_ROSTER' in bench and any(v is not None for v in bench['EW_ROSTER']):
        s = bench['EW_ROSTER']
        i0 = next(i for i, v in enumerate(s) if v is not None)
        summary['vs_ew_roster'] = ((model[-1] / model[i0] - 1)
                                   - (s[-1] / s[i0] - 1))
```

- [x] **Step 2:** `site/js/common.js` CHART_COLORS gains: `EW_ROSTER: '#56d364', BAND_TOP: '#1f6feb', BAND_NEXT: '#d29922', BAND_TAIL: '#f85149'` (EW_ROSTER near the model green — it is the model's sizing-null twin).
- [x] **Step 3:** `site/js/performance.js` — append to the series tuple list, hidden-by-default so the default view stays clean (Chart.js `hidden: true`, toggled via legend):

```javascript
      ['EW roster (sizing null)', perf.bench.EW_ROSTER, CHART_COLORS.EW_ROSTER, true],
      ['Band 1–15', perf.bench.BAND_TOP, CHART_COLORS.BAND_TOP, true],
      ['Band 16–25', perf.bench.BAND_NEXT, CHART_COLORS.BAND_NEXT, true],
      ['Band 26–40', perf.bench.BAND_TAIL, CHART_COLORS.BAND_TAIL, true],
```

guarded with a filter on `undefined` series (pre-deploy data files), and `spanGaps: false` on these datasets so null padding renders as absent, not interpolated. Match the existing tuple→dataset construction in the file (read it first; the 4th element is the hidden flag — verify against `lineDataset`'s signature and adapt if it differs).
- [x] **Step 4:** Test in `tests/test_export_site_data.py`: build a minimal `performance-series.json` fixture whose bench includes `BAND_TOP` with leading nulls; assert exported `performance.json` preserves nulls and scales non-nulls; assert privacy gate still passes (`python3 -m pytest tests/test_export_site_data.py tests/test_repo_privacy.py -q`).
- [x] **Step 5:** Commit: `git add -A && git commit -m "feat(v2): surface EW_ROSTER + band shadows on the performance tab (spec A4/C1)"`

---

### Task 8: Migration script — §A3 table, Dom-gated apply

**Files:**
- Create: `scripts/migrate_portfolio_v2.py`

**Interfaces:**
- Consumes: everything above.
- Produces: default run prints the migration table + membership diff, writes nothing. `--apply` (DOM ONLY — do not run) flips `portfolio-config.json` modes to `inverse_vol`/`rank`, sets the live sheet's `Entry rank`/`Exit rank` cells to 15/18, and runs `refresh(resize=True)` with `kind='sizing_migration_invvol'`.

- [x] **Step 1:** Write `scripts/migrate_portfolio_v2.py`:

```python
"""One-time portfolio-construction-v2 migration (spec 2026-08-07 §A3).

Default: print the before/after table (ticker, current weight, new inverse-vol
target, delta) plus the score→rank membership diff, for Dom's explicit
approval. WRITES NOTHING.

--apply (run only on Dom's approval): flip tracking/portfolio-config.json to
sizing.mode=inverse_vol + selection.mode=rank, set the Sizing Rules sheet's
Entry rank/Exit rank to 15/18 (the sheet stays authoritative, rule 26), then
run refresh_targets.refresh(resize=True) so the book re-sizes in one
`sizing_migration_invvol` event — the seam in the history; nothing restated.
"""
from __future__ import annotations

import argparse
import json

from openpyxl import load_workbook

from portfolio_model import PCONFIG, current_weights, load_cfg, load_pcfg
from portfolio_sizing import rank_by_score, topn_membership
from position_sizing import inverse_vol_weights
from recalc_watchlist import recalc
import refresh_targets as rt


def build_table():
    cfg, pcfg = load_cfg(), load_pcfg()
    held = sorted(cfg['events'][-1]['allocations'])
    live = [x for x in recalc() if x['TOTAL'] is not None]
    live.sort(key=lambda x: -x['TOTAL'])
    info = {x['ticker']: x for x in live}
    layers = {x['ticker']: (x['layer'] or '')[:2] for x in live}

    ranked = rank_by_score(live, set(held))
    include, entered, exit_crossers = topn_membership(set(held), ranked, 15, 18)
    prices = rt._price_frame(include, int(pcfg['sizing']['lookback']))
    inv = inverse_vol_weights(prices, include, pcfg['sizing'],
                              layers={t: layers[t] for t in include})
    cur = current_weights(cfg) or {}
    rank = {t: i + 1 for i, t in enumerate(ranked)}

    print(f'{"Tkr":<7}{"Rank":>5}{"Score":>7}{"Now %":>7}{"New %":>7}{"Δ":>7}')
    for t in sorted(set(held) | set(include), key=lambda t: rank.get(t, 999)):
        now, new = cur.get(t, 0.0) * 100, inv.get(t, 0.0) * 100
        note = (' ENTER' if t in entered else
                ' EXIT-CROSS (2-run clock)' if t in exit_crossers else '')
        print(f'{t:<7}{rank.get(t, 0):>5}{info[t]["TOTAL"]:>7.1f}'
              f'{now:>7.1f}{new:>7.1f}{new - now:>+7.1f}{note}')
    print(f'\nmembership diff (score→rank form): '
          f'+{entered or "none"} / exit-crossers {exit_crossers or "none"}')
    print('NOT APPLIED — approve with: '
          'python3 scripts/migrate_portfolio_v2.py --apply')


def apply():
    pcfg = json.loads(PCONFIG.read_text())
    pcfg.setdefault('sizing', {})['mode'] = 'inverse_vol'
    pcfg.setdefault('selection', {})['mode'] = 'rank'
    PCONFIG.write_text(json.dumps(pcfg, indent=2) + '\n')
    wb = load_workbook(rt.PORTFOLIO)
    ws = wb['Sizing Rules']
    for row in ws.iter_rows():
        if row[0].value == 'Entry rank':
            row[1].value = 15
        if row[0].value == 'Exit rank':
            row[1].value = 18
    wb.save(rt.PORTFOLIO)
    print('modes flipped: sizing=inverse_vol, selection=rank (N=15, M=18)')
    rt.refresh(resize=True)          # logs the sizing_migration_invvol seam


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--apply', action='store_true',
                    help="DOM-GATED: flip modes and re-size the live book")
    args = ap.parse_args()
    apply() if args.apply else build_table()
```

Plus in `refresh()` (small addition): when the modes are freshly flipped and the migration's `resize=True` run fires with no membership/tier change, `kind` falls to `'manual_resize'` — special-case: `refresh(resize=True, migration=True)` param defaulting False; when True, `kind='sizing_migration_invvol'`. `migrate_portfolio_v2.apply()` calls `rt.refresh(resize=True, migration=True)`.

- [x] **Step 2:** Dry-run the table against real data: `cd scripts && python3 migrate_portfolio_v2.py` → table prints, `git status` clean (nothing written).
- [x] **Step 3:** Commit: `git add -A && git commit -m "feat(v2): Dom-gated migration script with before/after table (spec A3)"`

---

### Task 9: Docs + full verification + PR

**Files:**
- Modify: `CLAUDE.md` (new rule 28), `scripts/README.md` if it indexes scripts

- [x] **Step 1:** Append CLAUDE.md rule 28 (concise; content: v2 construction — modes in `tracking/portfolio-config.json` (defaults tier/score until migration), score chooses names by rank N=15/M=18 with the rule-26 clock intact, trailing 60d inverse-vol chooses sizes (12%/3% cap/floor), monthly drift-band re-size, EW_ROSTER as permanent sizing null + two-quarter tripwire, BAND shadows forward-only, `tracking/score-history.csv` appended on every scoring pass and never rewritten, monotonicity gate scoped to tier mode, migration is the history seam — pointer to the spec).
- [x] **Step 2:** Full suite: `python3 -m pytest tests/ -q` → all green. Minimal-env check (CI parity): `python3 -c "import sys; sys.path.insert(0,'scripts'); import position_sizing, score_history, portfolio_sizing; print('CI-import OK')"`.
- [x] **Step 3:** Real-data smoke (no writes): `python3 scripts/refresh_targets.py --dry-run` → identical membership/weights to pre-branch behavior (modes unchanged). `python3 scripts/refresh_targets.py --check` → green.
- [x] **Step 4:** Push branch, open PR titled "Portfolio construction v2: inverse-vol sizing, top-N selection, band shadows (Dom-gated migration)" with the migration table + open decisions (§D 1–6) in the body.

---

## Self-Review Notes

- **Spec coverage:** A0 evidence = docs only (no task needed); A1→Task 1; A2→Task 6; A3→Task 8; A4→Tasks 4+7 (tripwire is a documented decision rule, not code — flagged in PR body as open decision 3); B1→Tasks 2+5; B2 audit logging→Task 5 Step 2 (flag lines); C1→Tasks 4,5,7; C2→Task 3. All spec-named tests present: invvol basic/caps/sigma/short-history/monotonic/drift (Task 1), event-log-roundtrip (Task 4), topn/tie-break/rank-stability (Task 2 + refresh-level in Task 5), band-partition (Task 4), score-history-append-only (Task 3), frozen-fixture byte-identical integration (Task 4 roundtrip test).
- **Deliberate decisions beyond the spec letter (surface to Dom in the PR):**
  1. The rule-26 **2-run exit-confirm clock is kept** under rank selection (spec B1 is silent on it; removing it would be a bigger behavior change than the spec authorizes, and it composes cleanly: below-M starts the clock, next run confirms).
  2. **`kind` field** added to events rather than replacing the human-readable `reason` (old events stay valid; spec A2's typed reason satisfied).
  3. **Monthly re-size approximates "first trading day"** as "first real online run of the calendar month" (refresh runs at least weekly; exact-day scheduling would need a new cron for no measurable benefit).
  4. Tier crossings stop firing rebalances under inverse-vol sizing (they carry no weight information there); the monotonicity gate is scoped to tier mode.
  5. Sizing params in `tracking/portfolio-config.json` (spec's `portfolio-config.json`); selection N/M stay on the Sizing Rules sheet per rule 26.
