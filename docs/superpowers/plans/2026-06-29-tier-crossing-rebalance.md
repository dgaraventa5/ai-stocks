# Tier-crossing Rebalance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a tier crossing on a held name re-weight the portfolio — both the displayed `Targets` sheet and the tracked model — so a rescored ✓✓✓ name (MU) stops showing a stale, inverted weight; then apply the one-time corrective.

**Architecture:** Extend `refresh_targets.py`'s rebalance gate from *membership change* to *membership OR tier change* (baseline = the last model event's stored `tiers`), make it the single writer of `Targets` (freeze the score/tier/weight snapshot between rebalances), and add a score-monotonicity regression gate. Pure sizing helpers move to a new yfinance-free `portfolio_sizing.py` so the gate runs in the minimal deploy CI.

**Tech Stack:** Python 3, openpyxl (xlsx), yfinance (prices, network), pytest (+ monkeypatch), event-sourced JSON model state.

## Global Constraints

- **Spec:** `docs/superpowers/specs/2026-06-29-tier-crossing-rebalance-design.md`.
- **Branch:** `tier-crossing-rebalance` (already checked out). Do NOT commit to `main`.
- **xlsx:** use `openpyxl`, never `pandas.to_excel`. Calculated cells stay Excel formulas (CLAUDE.md rule 4) — the corrective preserves the existing `Reconciliation` formulas.
- **Network:** yfinance only; throttle (`time.sleep(0.25)` as the file already does). `recalc()` is read-only and needs no network.
- **Tests:** `pytest`. A test file that imports a yfinance-importing module (`refresh_targets`, `portfolio_model`, `track_performance`) must start with `pytest.importorskip('yfinance')`. Pure tests on `portfolio_sizing` / openpyxl must NOT, so they run in the openpyxl-only deploy CI.
- **Privacy:** `export_site_data.py` is the only path to `site/data/` (gitignored); $10k notional. Don't weaken `tests/test_repo_privacy.py`.
- **Commits:** end every commit message with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **Rule 5:** the model auto-rebalances on material events (now incl. tier change), matching the existing convention; the WDC exit is Dom's already-made call (let it exit).

---

### Task 1: Pure sizing helpers (`portfolio_sizing.py`)

**Files:**
- Create: `scripts/portfolio_sizing.py`
- Create: `tests/test_portfolio_sizing.py`

**Interfaces:**
- Produces:
  - `tier_changes(include: list[str], info: dict[str, dict], last_tiers: dict[str, str]) -> list[tuple[str, str, str]]` — `(ticker, old, new)` for held names whose tier moved vs the last rebalance; ignores names absent from `last_tiers` (newly entered) and `None` tiers.
  - `build_reason(entered: list[str], exited: list[str], tier_chg: list[tuple[str, str, str]], resize: bool) -> str`
  - `weights_score_monotonic(rows: list[tuple[float, float]], tol: float = 1e-4) -> list[tuple]` — `(score, weight)` rows; returns `[]` if weight is non-increasing as score decreases, else the violating adjacent pairs.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_portfolio_sizing.py
"""Pure sizing helpers — no yfinance, runs in the openpyxl-only deploy CI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from portfolio_sizing import tier_changes, build_reason, weights_score_monotonic


def _info(d):
    return {t: {'Tier': tier} for t, tier in d.items()}


def test_tier_changes_detects_crossing():
    info = _info({'MU': '✓✓✓', 'NVDA': '✓✓'})
    last = {'MU': '✓✓', 'NVDA': '✓✓'}
    assert tier_changes(['MU', 'NVDA'], info, last) == [('MU', '✓✓', '✓✓✓')]


def test_tier_changes_ignores_within_tier_and_new_names():
    info = _info({'MU': '✓✓✓', 'APP': '✓✓'})   # APP newly entered (not in last)
    last = {'MU': '✓✓✓'}                          # MU unchanged
    assert tier_changes(['MU', 'APP'], info, last) == []


def test_build_reason_concatenates_membership_and_tier():
    r = build_reason(['APP'], ['WDC'], [('MU', '✓✓', '✓✓✓')], False)
    assert 'membership: +APP, -WDC' in r and 'tier: MU ✓✓→✓✓✓' in r


def test_build_reason_resize_only():
    assert build_reason([], [], [], True) == 'manual resize'


def test_weights_monotonic_flags_inversion():
    # MU (86.4) at 7.44 below NVDA (84.08) at 9.32 — the bug.
    rows = [(87.9, 9.6), (86.4, 7.44), (84.08, 9.32)]
    assert weights_score_monotonic(rows)   # non-empty → violation


def test_weights_monotonic_accepts_sorted():
    rows = [(87.9, 11.7), (86.4, 11.7), (84.08, 9.3), (80.1, 7.5)]
    assert weights_score_monotonic(rows) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_portfolio_sizing.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'portfolio_sizing'`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/portfolio_sizing.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_portfolio_sizing.py -q`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/portfolio_sizing.py tests/test_portfolio_sizing.py
git commit -m "feat(sizing): pure tier-change / reason / monotonicity helpers

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: `log_rebalance` stores tiers (`portfolio_model.py`)

**Files:**
- Modify: `scripts/portfolio_model.py:96-112` (`log_rebalance`)
- Create: `tests/test_log_rebalance_tiers.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `log_rebalance(cfg, weights, reason, tiers=None) -> dict` — the appended/replaced event now includes `'tiers': dict(tiers or {})`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_log_rebalance_tiers.py
import sys
from pathlib import Path

import pytest

pytest.importorskip('yfinance')   # portfolio_model imports yfinance at module load
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import portfolio_model as pm


def test_log_rebalance_stores_tiers(monkeypatch):
    cfg = {'inception': '2026-05-26',
           'events': [{'date': '2026-06-18', 'reason': 'seed',
                       'allocations': {'MU': 700.0}, 'cash': 0.0}]}
    # mark() hits the network; stub it to a fixed value with no missing names.
    monkeypatch.setattr(pm, 'mark', lambda c: (10000.0, {}, []))
    monkeypatch.setattr(pm, 'save_cfg', lambda c: None)   # don't touch disk
    monkeypatch.setattr(pm.dt, 'date', type('D', (), {
        'today': staticmethod(lambda: pm.dt.date(2026, 6, 29))}))

    ev = pm.log_rebalance(cfg, {'MU': 0.5, 'TSM': 0.5}, 'tier: MU ✓✓→✓✓✓',
                          {'MU': '✓✓✓', 'TSM': '✓✓'})

    assert ev['tiers'] == {'MU': '✓✓✓', 'TSM': '✓✓'}
    assert cfg['events'][-1]['tiers'] == {'MU': '✓✓✓', 'TSM': '✓✓'}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_log_rebalance_tiers.py -q`
Expected: FAIL — `TypeError: log_rebalance() takes 3 positional arguments but 4 were given`.

- [ ] **Step 3: Modify `log_rebalance`**

Replace the signature and event-construction in `scripts/portfolio_model.py` (currently lines 96-112):

```python
def log_rebalance(cfg: dict, weights: dict[str, float], reason: str,
                  tiers: dict[str, str] | None = None) -> dict:
    """Mark the model, re-allocate at today's value, append (or same-day
    replace) the event, and persist. `weights` are fractions of total value
    (summing to 1 - cash buffer, as refresh_targets produces them). `tiers` is
    the per-name tier at rebalance time — the baseline the tier-crossing detector
    compares future runs against."""
    today = dt.date.today().isoformat()
    value, _, missing = mark(cfg)
    if missing:
        flag(f'rebalance marked with carried values for: {", ".join(missing)}')
    alloc = {t: round(w * value, 2) for t, w in weights.items()}
    event = {'date': today, 'reason': reason, 'allocations': alloc,
             'tiers': dict(tiers or {}),
             'cash': round(value - sum(alloc.values()), 2)}
    if cfg['events'] and cfg['events'][-1]['date'] == today:
        cfg['events'][-1] = event       # idempotent same-day re-runs
    else:
        cfg['events'].append(event)
    save_cfg(cfg)
    return event
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_log_rebalance_tiers.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/portfolio_model.py tests/test_log_rebalance_tiers.py
git commit -m "feat(model): log_rebalance stores per-name tiers for the crossing baseline

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Wire the gate + freeze-snapshot into `refresh()` (`refresh_targets.py`)

**Files:**
- Modify: `scripts/refresh_targets.py:44` (import) and `:289-407` (sizing → model rollforward block)
- Create: `tests/test_refresh_targets.py`

**Interfaces:**
- Consumes: `tier_changes`, `build_reason`, `weights_score_monotonic` (Task 1); `log_rebalance(..., tiers)` (Task 2).
- Produces: `refresh(dry_run=False, resize=False, portfolio=None)` now (a) fires the rebalance on membership OR tier change OR `resize`; (b) writes `Targets`/`Reconciliation`/README and logs the event ONLY when firing (frozen snapshot otherwise); (c) passes `tiers` to `log_rebalance`.

- [ ] **Step 1: Write the failing integration test**

```python
# tests/test_refresh_targets.py
"""refresh() gate + freeze-snapshot behaviour, over a temp workbook with
recalc / network / log_rebalance mocked."""
import sys
from pathlib import Path

import openpyxl
import pytest

pytest.importorskip('yfinance')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import refresh_targets as rt


def _build_portfolio(path, holdings):
    """holdings: [(ticker, layer, score, tier)] written as Include?=Y rows."""
    wb = openpyxl.Workbook()
    sz = wb.active
    sz.title = 'Sizing Rules'
    sz.append(['Portfolio Sizing Rules'])
    sz.append(['Parameter', 'Value', 'Notes'])
    sz.append(['Cash buffer %', 0, ''])
    sz.append(['Max single position %', 0.12, ''])
    sz.append(['Tier-based base weight', None, None, None, None])
    sz.append(['Tier', 'Score Floor', 'Weight @ Floor', 'Weight @ Ceiling',
               'Score Ceiling'])
    sz.append(['✓✓✓', 85, 0.12, 0.12, 100])
    sz.append(['✓✓', 70, 0.03, 0.10, 85])
    sz.append(['✓', 55, 0.01, 0.03, 70])
    sz.append(['?', 40, 0, 0, 55])
    sz.append(['✗', 0, 0, 0, 40])
    sz.append(['Portfolio Value ($)', 10000, ''])
    tg = wb.create_sheet('Targets')
    tg.append(['Target Portfolio (test)'])
    tg.append(['Ticker', 'Layer', 'TOTAL', 'Tier', 'Rank', 'Status',
               'Include?', 'Override', 'Target %', 'Notes'])
    for i, (t, lay, sc, tier) in enumerate(holdings, 1):
        tg.append([t, lay, sc, tier, i, 'HOLD', 'Y', None,
                   round(100 / len(holdings), 2), None])
    wb.create_sheet('Reconciliation')
    wb.create_sheet('Positions').append(['Ticker', 'Company', 'Shares'])
    wb.create_sheet('README').append(['Last built', 'old'])
    wb.save(path)


def _mock_env(monkeypatch, live, cfg):
    monkeypatch.setattr(rt, 'recalc', lambda: live)
    monkeypatch.setattr(rt, 'last_trade_age_days', lambda t: 1)
    monkeypatch.setattr(rt, 'current_price', lambda t: 100.0)
    monkeypatch.setattr(rt.time, 'sleep', lambda *_a, **_k: None)
    monkeypatch.setattr(rt, 'load_cfg', lambda: cfg)
    calls = []

    def fake_log(cfg_, w, reason, tiers=None):
        calls.append({'reason': reason, 'tiers': tiers, 'weights': dict(w)})
        return {'allocations': {k: v * 10000 for k, v in w.items()}, 'cash': 0.0}

    monkeypatch.setattr(rt, 'log_rebalance', fake_log)
    return calls


def test_refresh_fires_on_tier_change(monkeypatch, tmp_path):
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 78.0, '✓✓')])
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 78.0, 'Tier': '✓✓'}]
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓', 'TSM': '✓✓'}}]}   # NVDA was ✓✓, now ✓✓✓
    calls = _mock_env(monkeypatch, live, cfg)

    rt.refresh(portfolio=str(path))

    assert len(calls) == 1
    assert calls[0]['tiers'] == {'NVDA': '✓✓✓', 'TSM': '✓✓'}
    assert 'tier: NVDA ✓✓→✓✓✓' in calls[0]['reason']
    # Targets rewritten: NVDA (✓✓✓) now outweighs TSM (✓✓).
    tg = openpyxl.load_workbook(path)['Targets']
    w = {r[0]: r[8] for r in tg.iter_rows(min_row=3, values_only=True) if r[0]}
    assert w['NVDA'] > w['TSM']


def test_refresh_frozen_when_unchanged(monkeypatch, tmp_path):
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓'),
                            ('TSM', '05 Fabs', 78.0, '✓✓')])
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0, 'Tier': '✓✓✓'},
            {'ticker': 'TSM', 'layer': '05 Fabs', 'TOTAL': 78.0, 'Tier': '✓✓'}]
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓✓', 'TSM': '✓✓'}}]}   # tiers already match → no change
    calls = _mock_env(monkeypatch, live, cfg)
    before = path.read_bytes()

    rt.refresh(portfolio=str(path))

    assert calls == []                     # no rebalance event logged
    assert path.read_bytes() == before     # workbook untouched (frozen snapshot)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_refresh_targets.py -q`
Expected: FAIL — `test_refresh_frozen_when_unchanged` fails (current `refresh()` always rewrites `Targets` and never reads `tiers`), and the tier-reason assertion fails.

- [ ] **Step 3: Add the import**

In `scripts/refresh_targets.py`, after line 44 (`from portfolio_model import load_cfg, log_rebalance`) add:

```python
from portfolio_sizing import tier_changes, build_reason, weights_score_monotonic
```

- [ ] **Step 4: Replace the sizing→rollforward block**

Replace everything from `# ---- sizing ----` (line 289) through the end of the model-rollforward block (line 407, the `else: print('model membership unchanged ...')`) with:

```python
    # ---- sizing ----
    base = {t: base_weight(info[t]['TOTAL'], p['tiers']) for t in include}
    weights = cap_and_normalize(base, layers, 1.0 - cash, max_single, layer_cap)

    # ---- rebalance gate: membership change OR a held name crossed a tier band ----
    # (--resize forces it). Crossing baseline is the LAST MODEL EVENT's stored
    # tiers, NOT the Targets sheet: the sheet can carry a fresh tier from an
    # out-of-band score edit (the bug this fixes), so it is not a trustworthy
    # baseline. Within-tier drift changes nothing — hysteresis preserved.
    cfg = load_cfg()
    last_ev = cfg['events'][-1]
    prior_model = set(last_ev['allocations'])
    last_tiers = last_ev.get('tiers', {})
    tier_chg = tier_changes(include, info, last_tiers)
    entered = sorted(set(include) - prior_model)
    exited = sorted(prior_model - set(include))
    fire = bool(entered or exited) or bool(tier_chg) or resize

    # ---- tier-change reporting (allocation delta vs prior model weight) ----
    denom = sum(last_ev['allocations'].values()) + last_ev.get('cash', 0)
    prior_w = {t: a / denom for t, a in last_ev['allocations'].items()} if denom else {}
    for t, old, new in tier_chg:
        flag(f'{t}: tier {old} → {new} | allocation '
             f'{prior_w.get(t, 0) * 100:.1f}% → {weights.get(t, 0) * 100:.1f}%')

    by_layer: dict[str, float] = {}
    for t, v in weights.items():
        by_layer[layers[t]] = by_layer.get(layers[t], 0) + v
    for lay, v in sorted(by_layer.items(), key=lambda kv: -kv[1]):
        if v > 0.25:
            flag(f'layer {lay}: {v:.0%} of portfolio (no layer cap active)')

    # ---- sanity: freshly computed weights must be monotonic in score ----
    viol = weights_score_monotonic([(info[t]['TOTAL'], weights.get(t, 0))
                                    for t in include])
    if viol:
        flag(f'non-monotonic weights {viol} — investigate base_weight/caps')

    if dry_run:
        print(f'\n{"Tkr":<7}{"Rank":>5}{"Score":>7}{"Status":<34}{"Wt %":>6}')
        for t in sorted(include, key=lambda t: -weights.get(t, 0)):
            print(f'{t:<7}{rank.get(t, 0):>5}{info[t]["TOTAL"]:>7.1f}'
                  f'{statuses.get(t, ""):<34}{weights.get(t, 0) * 100:>6.1f}')
        verdict = ('REBALANCE: ' + build_reason(entered, exited, tier_chg, resize)
                   if fire else 'FREEZE (no membership/tier change)')
        print(f'(dry run — would {verdict}; nothing written)')
        return

    if not fire:
        print('membership & tiers unchanged since last rebalance — '
              'snapshot frozen, nothing written')
        return

    # ---- prices for the trade plan (only when firing) ----
    prices: dict[str, float] = {}
    for t in include:
        prices[t] = current_price(t)
        time.sleep(0.25)
        if prices[t] is None:
            flag(f'{t}: no current price — Reconciliation row left without shares')

    # ---- rewrite Targets ----
    targets.delete_rows(1, targets.max_row)
    targets.append([f'Target Portfolio (refreshed {today}, live Watchlist scores)'])
    targets.append(['Ticker', 'Layer', 'TOTAL', 'Tier', 'Rank', 'Status',
                    'Include?', 'Override', 'Target %', 'Notes'])
    for c in targets[2]:
        c.fill, c.font = copy(HEADER_FILL), copy(HEADER_FONT)
    for x in live:
        t = x['ticker']
        if x['TOTAL'] < 55 and t not in include and t not in overrides:
            continue   # keep the sheet to ✓-and-better plus anything tracked
        targets.append([
            t, x['layer'], round(x['TOTAL'], 2), x['Tier'], rank[t],
            statuses.get(t, ''), 'Y' if t in include else 'N',
            overrides.get(t, ''), round(weights.get(t, 0) * 100, 2) or None,
            notes.get(t, ''),
        ])

    # ---- rewrite Reconciliation ----
    has_positions = any(positions.cell(row=r, column=1).value not in (None, 'TOTAL')
                        for r in range(2, positions.max_row + 1))
    recon.delete_rows(1, recon.max_row)
    mode = ('target vs current positions'
            if has_positions else 'fresh deployment — Positions sheet is empty')
    recon.append([f'Mechanical target diff ({mode}) — not a trade '
                  f'recommendation; decisions are Dom\'s (CLAUDE.md rule 5)'])
    recon.append([f'Portfolio: ${capital:,.0f} | Prices as of {today}'])
    recon.append(['Ticker', 'Score', 'Target %', '$ Amount', 'Price', 'Shares',
                  'Round $', 'Delta'])
    for c in recon[3]:
        c.fill, c.font = copy(HEADER_FILL), copy(HEADER_FONT)
    held = {}
    if has_positions:
        for r in range(2, positions.max_row + 1):
            t = positions.cell(row=r, column=1).value
            if t and t != 'TOTAL':
                held[t] = positions.cell(row=r, column=3).value or 0
    cap_row = next(r for r in range(1, sizing.max_row + 1)
                   if sizing.cell(row=r, column=1).value == 'Portfolio Value ($)')
    cap_cell = f"'Sizing Rules'!$B${cap_row}"
    for t in sorted(include, key=lambda t: -weights.get(t, 0)):
        r = recon.max_row + 1
        # Formulas, not pasted values (CLAUDE.md rule 4).
        recon.append([
            t, round(info[t]['TOTAL'], 1), round(weights[t] * 100, 2),
            f'=C{r}/100*{cap_cell}', prices.get(t),
            f'=IF(E{r}="","",ROUND(D{r}/E{r},4))',
            f'=IF(E{r}="","",F{r}*E{r})',
            (f'={held.get(t, 0)}-F{r}' if has_positions else 'NEW'),
        ])
    r = recon.max_row + 1
    recon.append(['TOTAL', None, f'=SUM(C4:C{r - 1})', f'=SUM(D4:D{r - 1})',
                  None, None, f'=SUM(G4:G{r - 1})', None])

    # ---- README breadcrumbs ----
    rm = wb['README']
    for row in rm.iter_rows():
        if row[0].value == 'Last built':
            row[1].value = f'{today} (refresh_targets.py — hysteresis pipeline)'

    wb.save(path)
    print(f'wrote {len(include)} target positions to {path}')

    # ---- log the rebalance event (membership and/or tier change, or resize) ----
    reason = build_reason(entered, exited, tier_chg, resize)
    tiers_now = {t: info[t]['Tier'] for t in include}
    ev = log_rebalance(cfg, weights, reason, tiers_now)
    print(f'model rebalanced: {reason} — value at rebalance '
          f'${sum(ev["allocations"].values()) + ev["cash"]:,.0f}')
```

Note: the earlier `prior_tiers` / `prior_weights` locals (read from the Targets sheet around lines 184-202) are now unused by this block; leave them in place — they are harmless and removing them touches the fragile column-index extraction.

- [ ] **Step 5: Run the integration + full suite**

Run: `python3 -m pytest tests/test_refresh_targets.py tests/test_portfolio_sizing.py tests/test_log_rebalance_tiers.py -q`
Expected: PASS (all).

- [ ] **Step 6: Commit**

```bash
git add scripts/refresh_targets.py tests/test_refresh_targets.py
git commit -m "feat(targets): rebalance on tier crossing; freeze snapshot between rebalances

refresh_targets now fires on membership OR tier change (baseline = last model
event tiers) or --resize, writes the Targets/Reconciliation snapshot only when
firing, and stores tiers on the event. Closes the stale-weight gap that left MU
(✓✓✓) below NVDA (✓✓).

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Apply the corrective rebalance + monotonicity data gate

**Files:**
- Modify (data): `00-master/portfolio.xlsx`, `tracking/performance-config.json`, `tracking/performance-series.json`
- Modify: `tests/test_portfolio_sizing.py` (append the data gate)

**Interfaces:** consumes the firing path from Task 3 and `weights_score_monotonic` from Task 1.

- [ ] **Step 1: Dry-run the corrective and inspect**

Run: `python3 scripts/refresh_targets.py --resize --dry-run`
Expected: WDC shows EXIT (resize, score 71.6 < 74.5); the 13 remaining names re-weighted with MU and TSM at the top (~11.7%); verdict line says `would REBALANCE`. **If anything other than WDC exits, or any unexpected name enters, STOP and report to Dom before the live run** (a new entrant is a real membership signal, not part of this corrective).

- [ ] **Step 2: Run the corrective for real**

Run: `python3 scripts/refresh_targets.py --resize`
Expected: prints `wrote 13 target positions ...` and `model rebalanced: membership: -WDC; tier: MU ✓✓→✓✓✓ ...` (tier delta present iff MU's old tier differs from the model baseline; with the pre-`tiers` 2026-06-18 event the baseline is empty, so the reason is `membership: -WDC` — still correct). This writes `portfolio.xlsx` and appends a 2026-06-29 event (with `tiers`) to `performance-config.json`.

- [ ] **Step 3: Verify the corrected workbook**

Run:
```bash
python3 -c "
from openpyxl import load_workbook
ws = load_workbook('00-master/portfolio.xlsx')['Targets']
rows = [(r[0], r[2], r[3], r[8]) for r in ws.iter_rows(min_row=3, values_only=True) if r[0] and r[6]=='Y']
for t, sc, tier, w in sorted(rows, key=lambda x: -x[3]):
    print(f'{t:<6} {sc:<6} {tier:<4} {w}')
assert all(rows[i][3] is not None for i in range(len(rows)))
assert 'WDC' not in [r[0] for r in rows], 'WDC should have exited'
print('included:', len(rows))
"
```
Expected: 13 included rows; MU and TSM at the top near 11.7%; WDC absent.

- [ ] **Step 4: Rebuild the performance series**

Run: `python3 scripts/track_performance.py --series-only`
Expected: rebuilds `tracking/performance-series.json` through today; no error. (If yfinance is network-blocked, STOP and flag — do not fabricate; CLAUDE.md data rule.)

- [ ] **Step 5: Add the monotonicity data gate**

Append to `tests/test_portfolio_sizing.py`:

```python
import openpyxl

_REPO = Path(__file__).resolve().parent.parent


def test_targets_weights_monotonic():
    """Regression gate: the committed Targets sheet's included weights must be
    monotonic in score — a ✓✓✓ name can never be weighted below a ✓✓ name
    (the MU bug). openpyxl only; runs in the deploy CI."""
    ws = openpyxl.load_workbook(_REPO / '00-master' / 'portfolio.xlsx')['Targets']
    rows = [(float(r[2]), float(r[8]))
            for r in ws.iter_rows(min_row=3, values_only=True)
            if r[0] and str(r[6]).strip().upper() == 'Y' and r[2] is not None
            and r[8] is not None]
    assert rows, 'no included Targets rows found'
    assert weights_score_monotonic(rows) == []
```

- [ ] **Step 6: Run the gate + full suite**

Run: `python3 -m pytest tests/ -q`
Expected: PASS, including `test_targets_weights_monotonic` (green now that the corrective is applied).

- [ ] **Step 7: Verify the site export shows MU at the top (no commit — site/data is gitignored)**

Run:
```bash
python3 scripts/export_site_data.py
python3 -c "
import json
p = json.load(open('site/data/positions.json'))
top = sorted(p, key=lambda d: -d['weight'])[:3]
print([(d['ticker'], d['weight'], d['tier']) for d in top])
mu = next(d for d in p if d['ticker']=='MU')
print('MU:', mu['weight'], mu['tier'])
assert mu['tier']=='✓✓✓' and mu['weight'] >= 11.0, 'MU should be a top-weight ✓✓✓'
"
```
Expected: MU among the top with weight ≈11.7% and tier ✓✓✓; the inversion is gone.

- [ ] **Step 8: Commit the corrected data + the gate**

```bash
git add 00-master/portfolio.xlsx tracking/performance-config.json tracking/performance-series.json tests/test_portfolio_sizing.py
git commit -m "data: corrective rebalance — MU/TSM to ✓✓✓ top weights, WDC exits

Forced --resize re-weight: MU and TSM (✓✓✓) to ~11.7%, WDC (71.6 < 74.5)
exits, 13-name book. New 2026-06-29 model event stores tiers as the crossing
baseline. Adds the score-monotonicity data gate.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Close the bypass in docs (CLAUDE.md + weekly-scan)

**Files:**
- Modify: `CLAUDE.md` (operating rules, near rule 9/12)
- Modify: the weekly-scan skill markdown (the Step that touches the portfolio/Targets)

**Interfaces:** none (documentation).

- [ ] **Step 1: Locate the weekly-scan portfolio step**

Run: `grep -rln "refresh_targets\|Targets sheet\|portfolio.xlsx" ~/.claude/plugins ~/.claude/skills 2>/dev/null; grep -rn "Targets\|refresh_targets" .claude/ 2>/dev/null | head`
Expected: the weekly-scan skill file path. (If the skill is not editable in-repo, record the convention in CLAUDE.md only and note that in the commit.)

- [ ] **Step 2: Add the single-writer rule to CLAUDE.md**

Add a short operating rule (next number in sequence) to `CLAUDE.md`:

```markdown
### N. Targets sheet has one writer: refresh_targets.py (added 2026-06-29)

`00-master/portfolio.xlsx` `Targets` is written ONLY by `scripts/refresh_targets.py`.
Never hand-edit scores/tiers into it — that bypass left MU showing ✓✓✓ at a stale
✓✓-band weight (a ✓✓✓ name below a ✓✓ name) because weights and the model never
moved. After any rescore that could change a held name's tier, run
`python3 scripts/refresh_targets.py` (it re-weights + logs a model event iff
membership OR a held tier changed; within-tier drift freezes the snapshot, no churn).
`--resize` forces a re-weight. The score-monotonicity gate
(`tests/test_portfolio_sizing.py::test_targets_weights_monotonic`) fails the build on
any inversion. See spec 2026-06-29-tier-crossing-rebalance-design.md.
```

- [ ] **Step 3: Update the weekly-scan skill step (if editable)**

In the weekly-scan skill's portfolio/Targets step, replace any "update Targets scores from the Watchlist" instruction with: "run `python3 scripts/refresh_targets.py` — do not hand-edit the Targets sheet; it re-weights and logs a rebalance only on a membership/tier change."

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(rules): refresh_targets.py is the single Targets writer; no hand-edits

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage:**
- Trigger = tier crossing → Task 3 gate (`fire = ... or bool(tier_chg)`). ✓
- Freeze whole snapshot → Task 3 write-gating + `test_refresh_frozen_when_unchanged`. ✓
- Store tier-at-rebalance → Task 2. ✓
- Single Targets writer / close bypass → Task 5. ✓
- Score-monotonicity invariant → Task 1 helper + Task 4 data gate. ✓
- Corrective dated today, WDC exits → Task 4 (dry-run guard + `--resize`). ✓
- `--resize` forces rebalance → Task 3 (`or resize`). ✓
- Legacy events without `tiers` → `last_ev.get('tiers', {})` (Task 3); corrective is forced (Task 4). ✓
- No paid data, no scoring/band/weight changes → nothing in any task touches those. ✓

**2. Placeholder scan:** No TBD/TODO; every code step shows full code; commands show expected output. ✓

**3. Type consistency:** `tier_changes`/`build_reason`/`weights_score_monotonic` signatures match between Task 1 definition, Task 3 calls, and the Task 4 data gate. `log_rebalance(cfg, weights, reason, tiers)` matches between Task 2 and the Task 3 call. `info[t]['Tier']`, `x['TOTAL']`, `x['ticker']`, `x['layer']` match `recalc()`'s actual return shape. ✓
