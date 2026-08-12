# Tradability Filter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Exclude foreign-listed (Robinhood/Fidelity-untradable) tickers from portfolio selection and band shadows while leaving the Watchlist, scoring, and score-history panel untouched.

**Architecture:** A pure predicate `is_tradable()` in `portfolio_sizing.py` (dot-suffix rule), a `selection.tradable_only` flag defaulting to `False` in `portfolio_model.DEFAULT_PCFG`, and a filtered selection universe inside `refresh_targets.refresh()` — held untradable names exit via the existing dead/override immediate-exit branch, and `_update_band_shadows` receives the filtered list. Spec: `docs/superpowers/specs/2026-08-11-tradability-filter-design.md`.

**Tech Stack:** Python 3, openpyxl, pytest. No new dependencies, no network in any new code path.

## Global Constraints

- `tradable_only: false` (or absent) must reproduce pre-change behavior exactly — the existing test suite pins this because `_mock_env` pcfgs omit the key.
- `info`, `layers`, and the score-history `append_snapshot` call keep the FULL universe; only `ranked`/`order`/`in_play` and the shadow updater use the filtered list.
- The held-untradable exit is immediate (dead/override branch), never the 2-run exit-pending clock.
- Commit with explicit paths only — never `git add -A` (tracking/live/ is not ignored on origin/main).
- All new logic that the openpyxl-only deploy CI tests must stay import-light (no yfinance/pandas at module level).

---

### Task 1: `is_tradable` predicate + config default

**Files:**
- Modify: `scripts/portfolio_sizing.py` (append function)
- Modify: `scripts/portfolio_model.py:62` (`DEFAULT_PCFG['selection']`)
- Test: `tests/test_portfolio_sizing.py`

**Interfaces:**
- Produces: `is_tradable(ticker: str) -> bool` (importable from `portfolio_sizing`); `load_pcfg()['selection']['tradable_only']` defaulting to `False`.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_portfolio_sizing.py`)

```python
def test_is_tradable_us_listings():
    from portfolio_sizing import is_tradable
    assert all(is_tradable(t) for t in ('NVDA', 'BRK-B', 'TSM', 'MELI'))


def test_is_tradable_rejects_exchange_suffixes():
    from portfolio_sizing import is_tradable
    foreign = ('6861.T', '6268.T', 'KGX.DE', '0981.HK', '5347.TWO',
               'AUTO.OL', 'MELE.BR', 'DRO.AX', '2049.TW')
    assert not any(is_tradable(t) for t in foreign)


def test_pcfg_defaults_tradable_only_false(monkeypatch, tmp_path):
    import portfolio_model as pm
    monkeypatch.setattr(pm, 'PCONFIG', tmp_path / 'missing.json')
    assert pm.load_pcfg()['selection']['tradable_only'] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_portfolio_sizing.py -k tradable -v`
Expected: FAIL (ImportError / KeyError).

- [ ] **Step 3: Implement** — append to `scripts/portfolio_sizing.py`:

```python
def is_tradable(ticker: str) -> bool:
    """US-brokerage tradability (spec 2026-08-11): foreign local lines carry
    an exchange-suffix dot (6861.T, KGX.DE, 0981.HK); US listings never do.
    Deterministic and offline by design — no per-name list, no API."""
    return '.' not in ticker
```

In `scripts/portfolio_model.py`, change the `DEFAULT_PCFG` selection line to:

```python
    'selection': {'mode': 'score', 'tradable_only': False},
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_portfolio_sizing.py tests/test_refresh_targets.py -v`
Expected: all PASS (including untouched suite — default False changes nothing).

- [ ] **Step 5: Commit**

```bash
git add scripts/portfolio_sizing.py scripts/portfolio_model.py tests/test_portfolio_sizing.py
git commit -m "feat: is_tradable predicate + selection.tradable_only config default (off)"
```

### Task 2: filtered selection + immediate exit in refresh_targets

**Files:**
- Modify: `scripts/refresh_targets.py` (imports; selection block ~line 300; membership loop ~line 342)
- Test: `tests/test_refresh_targets.py`

**Interfaces:**
- Consumes: `portfolio_sizing.is_tradable` (Task 1).
- Produces: `refresh()` honoring `pcfg['selection'].get('tradable_only')`; held untradable names get status `EXIT (untradable)`.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_refresh_targets.py`, reusing `_build_portfolio`, `_mock_env`, `_rank_cfg`, `_rank_pcfg`)

```python
def _tradability_pcfg():
    p = _rank_pcfg()
    p['selection']['tradable_only'] = True
    return p


def _mixed_live():
    """Ranks 1-17 with a foreign name at raw rank 3 and one at 16."""
    tickers = ['T01', 'T02', '6861.T', 'T04', 'T05', 'T06', 'T07', 'T08',
               'T09', 'T10', 'T11', 'T12', 'T13', 'T14', 'T15', '6268.T', 'T17']
    return [{'ticker': t, 'layer': '11 Robotics', 'TOTAL': 90.0 - i,
             'Tier': '✓✓'} for i, t in enumerate(tickers)]


def test_tradable_only_blocks_foreign_entry_and_exits_held(monkeypatch, tmp_path):
    """Held 6861.T exits IMMEDIATELY (no pending clock); foreign outsiders
    never enter; tradable names below them shift up into the entry band."""
    path = tmp_path / 'portfolio.xlsx'
    prior = ['T01', 'T02', '6861.T', 'T04', 'T05', 'T06', 'T07', 'T08',
             'T09', 'T10', 'T11', 'T12', 'T13', 'T14']
    _build_portfolio(path, [(t, '11 Robotics', 90.0, '✓✓') for t in prior])
    calls, _saves = _mock_env(monkeypatch, _mixed_live(), _rank_cfg(prior))
    monkeypatch.setattr(rt, 'load_pcfg', _tradability_pcfg)

    rep = rt.refresh(portfolio=str(path))

    assert '6861.T' in rep['exited']                 # immediate, this run
    assert rep['pending'] == {}                      # never on the clock
    assert 'T15' in rep['entered']                   # shifted into rank<=15
    assert '6268.T' not in rep['entered']
    assert len(calls) == 1 and calls[0]['kind'] == 'membership'
    assert '6861.T' not in calls[0]['weights']
    tg = openpyxl.load_workbook(path)['Targets']
    rows = {r[0]: r for r in tg.iter_rows(min_row=3, values_only=True) if r[0]}
    assert rows['6861.T'][6] == 'N'
    assert 'untradable' in str(rows['6861.T'][5])    # Status column


def test_tradable_only_off_keeps_foreign(monkeypatch, tmp_path):
    """Flag off (default): foreign names rank and hold exactly as before."""
    path = tmp_path / 'portfolio.xlsx'
    prior = ['T01', 'T02', '6861.T', 'T04', 'T05', 'T06', 'T07', 'T08',
             'T09', 'T10', 'T11', 'T12', 'T13', 'T14']
    _build_portfolio(path, [(t, '11 Robotics', 90.0, '✓✓') for t in prior])
    calls, _saves = _mock_env(monkeypatch, _mixed_live(), _rank_cfg(prior))
    monkeypatch.setattr(rt, 'load_pcfg', _rank_pcfg)   # no tradable_only key

    rep = rt.refresh(portfolio=str(path))

    assert rep['exited'] == []
    assert '6861.T' not in rep.get('pending', {})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_refresh_targets.py -k tradable -v`
Expected: first test FAILs (6861.T lands on the pending clock instead of exiting; T15 doesn't enter); second may already pass (that's the regression pin — fine).

- [ ] **Step 3: Implement** in `scripts/refresh_targets.py`:

Add to the `portfolio_sizing` import: `is_tradable`.

After `live` is built and sorted (just after the `append_snapshot` block, before `# ---- selection form`), insert:

```python
    # ---- tradability filter (spec 2026-08-11): selection ranks over the
    # buyable universe only; info/layers/score-panel stay full-universe.
    tradable_only = bool(pcfg['selection'].get('tradable_only'))
    sel_live = ([x for x in live if is_tradable(x['ticker'])]
                if tradable_only else live)
    untradable = ({t for t in info if not is_tradable(t)}
                  if tradable_only else set())
    for t, v in overrides.items():
        if v == 'INCLUDE' and t in untradable:
            flag(f'{t}: Override=INCLUDE but untradable — filter wins, stays out')
```

(Note: `pcfg = load_pcfg()` currently sits below this point at the selection-form block — move that single line up above the insert.)

Then switch the selection block to the filtered list — in rank mode `ranked = rank_by_score(sel_live, prior_include)` and in score mode `rank`/`order`/`in_play` built from `sel_live` instead of `live` (`in_play = {x['ticker'] for x in sel_live if x['TOTAL'] >= exit_score}`).

In the membership loop, extend the dead/override branch:

```python
        if t in dead or overrides.get(t) == 'EXCLUDE' or t in untradable:
            statuses[t] = ('EXIT (untradable)' if t in untradable
                           else 'EXIT (dead/override)')
            if t in untradable:
                flag(f'{t}: held but untradable on US brokerages — EXIT')
            continue
```

And in the entry loop, skip untradable before the override checks (defensive — they are already absent from `order`):

```python
        if t in untradable:
            continue
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_refresh_targets.py -v`
Expected: all PASS, both modes.

- [ ] **Step 5: Commit**

```bash
git add scripts/refresh_targets.py tests/test_refresh_targets.py
git commit -m "feat: tradable_only selection filter — foreign names can't enter, held ones exit immediately"
```

### Task 3: band shadows rank the tradable universe

**Files:**
- Modify: `scripts/refresh_targets.py:482` (the `_update_band_shadows` call site)
- Test: `tests/test_refresh_targets.py`

**Interfaces:**
- Consumes: `sel_live` from Task 2.

- [ ] **Step 1: Write the failing test**

```python
def test_band_shadows_exclude_untradable(monkeypatch, tmp_path):
    path = tmp_path / 'portfolio.xlsx'
    prior = ['T01', 'T02', 'T04', 'T05']
    _build_portfolio(path, [(t, '11 Robotics', 90.0, '✓✓') for t in prior])
    cfg = _rank_cfg(prior)
    _mock_env(monkeypatch, _mixed_live(), cfg)
    monkeypatch.setattr(rt, 'load_pcfg', _tradability_pcfg)

    rt.refresh(portfolio=str(path))

    rosters = [e['roster'] for evs in cfg['shadow_events'].values() for e in evs]
    assert all('.' not in t for r in rosters for t in r)
    assert 'T15' in cfg['shadow_events']['BAND_TOP'][-1]['roster']
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_refresh_targets.py -k band_shadows_exclude -v`
Expected: FAIL — `6861.T` appears in BAND_TOP.

- [ ] **Step 3: Implement** — at the call site change `live` to `sel_live`:

```python
    shadows_changed = False if dry_run else _update_band_shadows(
        cfg, sel_live, pcfg, today)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_refresh_targets.py -v`
Expected: all PASS (existing shadow tests run flag-off and keep passing).

- [ ] **Step 5: Commit**

```bash
git add scripts/refresh_targets.py tests/test_refresh_targets.py
git commit -m "feat: band shadows rank tradable universe only (forward-only seam)"
```

### Task 4: flip the live config + full-suite verification

**Files:**
- Modify: `tracking/portfolio-config.json`

- [ ] **Step 1: Edit config** — `"selection"` becomes:

```json
  "selection": {
    "mode": "rank",
    "tradable_only": true
  },
```

- [ ] **Step 2: Full suite + offline gate**

Run: `python3 -m pytest tests/ -q` — expected: all pass.
Run: `python3 scripts/refresh_targets.py --check` — expected: reports pending rebalance (membership change: −6861.T). That's the rule-25 gate correctly demanding the refresh run in Task 5, not a failure of this change.

- [ ] **Step 3: Commit**

```bash
git add tracking/portfolio-config.json
git commit -m "config: enable tradable_only selection (Dom-approved 2026-08-11)"
```

### Task 5: run the real refresh (exits 6861.T)

- [ ] **Step 1: Dry run** — `python3 scripts/refresh_targets.py --dry-run`
Verify: 6861.T `EXIT (untradable)`; 15 names remain; META HOLDs at rank 15; AMZN stays out; no other entries/exits.

- [ ] **Step 2: Real run** — `python3 scripts/refresh_targets.py`
Expected: one `membership` event (−6861.T), inverse-vol weights renormalized, Targets rewritten, band-shadow rosters refreshed with today's date. If ticket generation refuses for lack of a recon snapshot, report it — no sell exists anyway (0 real shares).

- [ ] **Step 3: Gate green** — `python3 scripts/refresh_targets.py --check` and `python3 -m pytest tests/ -q`
Expected: no pending rebalance; suite green.

- [ ] **Step 4: Commit** (explicit paths; score panel + performance config move with the run)

```bash
git add 00-master/portfolio.xlsx tracking/performance-config.json tracking/score-history.csv
git status --short   # verify nothing from tracking/live/ is staged
git commit -m "rebalance: exit 6861.T (untradable), 16→15 names, weights renormalized"
```

### Task 6: document (CLAUDE.md rule 30) + PR

- [ ] **Step 1: Add rule 30 to CLAUDE.md** after rule 29, ~10 lines: tradability filter exists, dot-suffix definition, what it does NOT touch (watchlist/cohorts/score panel), pointer to the spec, and the reversibility flag.

- [ ] **Step 2: Commit + PR**

```bash
git add CLAUDE.md
git commit -m "docs: rule 30 — tradability filter for portfolio selection"
git push -u origin feat/tradability-filter
gh pr create --title "Tradability filter: exclude foreign listings from portfolio selection + band shadows" --body "..."
```

## Self-review notes

- Spec coverage: config/predicate (T1), selection + immediate exit (T2), shadows (T3), flag flip (T4), the 6861.T exit event (T5), docs (T6). Watchlist/site/score-history untouched by construction — no task edits them.
- `pcfg` load-order move in Task 2 is the only refactor; it is mechanical (pure dict load, no side effects).
- Type consistency: `is_tradable` name used identically in Tasks 1–3; `sel_live` defined in Task 2, consumed in Task 3.
