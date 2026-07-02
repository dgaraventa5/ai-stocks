# Scoring Critique P1 (cohort-relative scoring) + P2 (reverse-DCF) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **This plan has BLOCKING prerequisites.** Do not begin the wiring tasks (P1-2 onward, P2-2 onward) until the five §5 decisions below are answered by Dom. The pure-function tasks (P1-0, P2-0) are already DONE. See "Blocking Decisions" before touching anything.

**Goal:** Aim the 0–100 Total Score at *mispricing* instead of *business quality* by (P1) replacing absolute metric bands with within-cohort percentile ranks for the style-biased metrics, and (P2) adding a reverse-DCF "implied growth vs grounded growth" gap metric — both landed behind before/after diffs and unit tests, neither trusted as "better" until the P3 validation gate (measured IC) is met.

**Architecture:** Two pure, unit-tested transforms (`scripts/cohort_percentile.py`, `scripts/reverse_dcf.py`) are computed per-cohort / per-name and then mirrored into both the Excel Methodology formulas and `scripts/recalc_watchlist.py` so Python TOTALs continue to match Excel. P1 is a *hybrid*: percentile only for the six style-biased metrics; Net Debt/EBITDA and the R-dimensions stay absolute. Every landing produces an explicit before/after Watchlist diff, re-derives tiers, and regenerates the membership roster — the rebalance itself stays a separate, Dom-approved `refresh_targets.py` run.

**Tech Stack:** Python 3.14, `openpyxl` (NOT pandas `to_excel` — it strips formulas), `pytest`. Free-data only (no Bloomberg/FactSet/paid FMP).

## Global Constraints

- **Sequence is fixed:** P0 (done) → P1/P2/P4–P6 → P3. P3 (category-weight changes) is **out of scope** for this plan and IC-gated (see "Explicit Non-Goals").
- **Verify against the workbook, never memory or the critique doc.** Re-read the live Weights/Methodology tabs before any edit; if the doc and workbook disagree, the workbook wins and you flag it. (Already flagged: doc said Risk header read "4 dimensions" — it already read 5; doc said "~76 inclusion threshold" — live script uses Entry 74.5 / Exit 73.0.)
- **Formulas over hardcoded values** in any `.xlsx` cell (CLAUDE.md rule 4). `recalc_watchlist.py` must mirror every new transform so Python TOTALs equal Excel.
- **After ANY structural row change to the Watchlist, run `python3 scripts/rebuild_watchlist_formulas.py`** (openpyxl `delete_rows`/`insert` does not rewrite formula references — CLAUDE.md rule 10/16). P1/P2 add columns, not rows, but any column insert has the same hazard — rebuild and re-verify.
- **No silent membership shift.** P1/P2 change scores → tiers → roster. Re-derive tiers explicitly, diff the roster, surface it to Dom. Do **not** let a scoring-methodology change auto-trigger `refresh_targets.py` (rule 18: it is the single Targets writer and logs a model event; a rebalance is a deliberate, separate, Dom-approved step).
- **`cohort_percentile.py` and `reverse_dcf.py` stay pure.** They do not read the workbook, fetch data, or choose a cohort/WACC/grounded-growth. Wiring lives in `recalc_watchlist.py` and a thin new config surface.
- **No new scope beyond this plan.** Critique §7 out-of-scope stands: no regime/conditional/interaction weighting, no ML weight matrix, no retroactive edits to frozen ratings, no changes to hysteresis rebalance logic.

---

## Blocking Decisions (critique §5) — must be answered by Dom before wiring

These are judgment calls about the *character* of the scoring system, not implementation details. They are being surfaced to Dom via a separate structured question set. Each task below names the decision it depends on. **Recommendations are stated (Dom's collaboration style: conviction + tradeoffs, not deference), but none is adopted until Dom signs off.**

| # | Decision | Options | Recommendation (pending sign-off) |
|---|---|---|---|
| **1** | **Cohort granularity for P1** | (a) top-level layer 01–10; (b) top-level layer with thin layers (<~8) merged into super-cohorts; (c) granular sub-layer (col C as-is) | **(b)** — col C is far too granular (many 1-name sub-layers → percentile is meaningless); pure top-level leaves Fabs (5) and Servers (7) too thin. Merge thin layers into documented super-cohorts. |
| **2** | **Relative vs absolute character** | (a) hybrid: percentile the 6 style-biased metrics, keep ND/EBITDA + R absolute (critique's proposal); (b) keep a larger absolute component | **(a)** — matches the critique's hybrid; targets exactly the style-bias metrics (F3) while keeping level-meaningful metrics absolute. |
| **3** | **Reverse-DCF placement (P2)** | (a) sub-metric inside Value (no reweight); (b) new standalone category (reweight → IC-gated, i.e. blocked by P3) | **(a)** — fold into Value first. Avoids a weight change (which is P3-gated), still gets the signal in. |
| **4** | **Recalibrate tier bands + entry/exit thresholds to the post-P1 distribution, or hold fixed?** | (a) recalibrate 85/70/55/40 + 74.5/73.0 to the new percentile-shaped distribution; (b) hold fixed and accept tier drift | **(a)** — percentile scores compress (cohort-max ≈ 92 not 100), so holding bands fixed silently reshuffles tiers. Recalibrate deliberately, as its own reviewed step, BEFORE finalizing P1. |
| **5** | **De-dup vs document collinear inputs (P4)** | (a) remove redundant inputs (R3↔Quality ND/EBITDA, D5↔D1, D2↔D3); (b) keep and disclose the double-count | Defer — P4 is a later task in this sequence tier; recommend deciding after seeing the P1 subscore-correlation matrix (Task P4-0). |

---

## File Structure

**Already created (Task P1-0, P2-0 — DONE, committed on branch `scoring-critique-p0-scaffolding`):**
- `scripts/cohort_percentile.py` — pure percentile transform. Public API:
  - `percentile_score(value, cohort_values, higher_is_better=True) -> float|None`
  - `rank_cohort(values, higher_is_better=True) -> list[float|None]`
- `scripts/reverse_dcf.py` — pure reverse-DCF. Public API:
  - `dcf_ev(g, fcf0, wacc, years=10, terminal_growth=0.03) -> float`
  - `implied_growth(ev, fcf0, wacc, years=10, terminal_growth=0.03, lo=-0.5, hi=1.0, tol=1e-7, max_iter=200) -> float|None`
  - `gap_to_score(gap) -> float`  (PROVISIONAL bands)
  - `mispricing_gap(ev, fcf0, wacc, grounded_g, ...) -> float|None`
  - `mispricing_score(ev, fcf0, wacc, grounded_g, ...) -> float|None`
- `tests/test_cohort_percentile.py` (12 tests), `tests/test_reverse_dcf.py` (12 tests).

**To create:**
- `scripts/cohorts.py` — cohort ASSIGNMENT (pure): maps a Watchlist layer string → cohort key, using a merge-map config. Decision-1/2 live entirely in the config it reads, not in code.
- `00-master/scoring-config.json` — the small Dom-owned config surface: cohort merge-map (§5-1), which metrics are percentile vs absolute (§5-2), WACC + grounded-growth source + reverse-DCF placement (§5-3), recalibrated tier bands (§5-4). Nothing here is chosen without Dom.
- `scripts/p1_before_after.py` — computes absolute-band vs percentile scores side by side, writes a diff report (per-name, per-cohort gap compression, per-tier movement, roster delta). Read-only.
- `tests/test_cohorts.py`, `tests/test_p1_scoring_integration.py`.

**To modify:**
- `scripts/recalc_watchlist.py` — add cohort-percentile scoring for the 6 metrics + the reverse-DCF Value sub-metric, gated by `scoring-config.json`.
- `00-master/ai_supply_chain_scoring.xlsx` — Methodology tab (document the percentile transform + reverse-DCF), Watchlist tab (new reverse-DCF input column; percentile is computed, not a stored band — see Task P1-2 note).
- `scripts/rebuild_watchlist_formulas.py` — mirror any new column/formula.
- `templates/rating-rubric-and-workflow.md` — document P1/P2 methodology (rubric is subjective-only, so this is a short cross-reference).
- `CLAUDE.md` — new rule documenting cohort-relative scoring + the IC-gate on weights (rule text drafted in Task P1-5).

---

## Task P1-0: Pure percentile transform — **DONE**

**Files:** `scripts/cohort_percentile.py`, `tests/test_cohort_percentile.py`

**Interfaces produced:** `percentile_score`, `rank_cohort` (signatures above).

- [x] Tests written first (12), verified RED (ModuleNotFoundError), implemented mid-rank percentile, verified GREEN, full suite green.
- Convention documented in-module: mid-rank percentile, ties symmetric, cohort median → ~50, endpoints deliberately NOT pinned to 0/100 (that interacts with §5-4).

---

## Task P1-1: Cohort assignment (pure, config-driven) — **BLOCKED on §5-1, §5-2**

**Files:**
- Create: `scripts/cohorts.py`
- Create: `tests/test_cohorts.py`
- Create (config authored WITH Dom): `00-master/scoring-config.json`

**Interfaces:**
- Consumes: nothing (pure).
- Produces: `cohort_key(layer_str, merge_map) -> str` and `top_level_layer(layer_str) -> str` for `recalc_watchlist.py`.

**Design note (why this isolates the decision):** `top_level_layer("06 AI Compute Silicon / GPUs") -> "06"` is a mechanical string op. `cohort_key` then applies a `merge_map` (e.g. `{"05": "semis", "04": "semis", "06": "semis"}`) so thin layers fold into super-cohorts. **The code is decision-independent; the `merge_map` values ARE §5-1.** Do not hardcode a merge-map — read it from `scoring-config.json`, whose values Dom sets.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cohorts.py
import cohorts

def test_top_level_layer_extracts_two_digit_prefix():
    assert cohorts.top_level_layer("06 AI Compute Silicon / GPUs") == "06"
    assert cohorts.top_level_layer("01 Power Generation / Nuclear-specific") == "01"

def test_cohort_key_passthrough_when_no_merge():
    assert cohorts.cohort_key("06 AI Compute Silicon / GPUs", merge_map={}) == "06"

def test_cohort_key_applies_merge_map():
    mm = {"04": "semis", "05": "semis", "06": "semis"}
    assert cohorts.cohort_key("05 Fabs & Foundries", mm) == "semis"
    assert cohorts.cohort_key("06 AI Compute Silicon / GPUs", mm) == "semis"

def test_cohort_key_none_layer_returns_none():
    assert cohorts.cohort_key(None, {}) is None
```

- [ ] **Step 2: Run, verify RED** — `pytest tests/test_cohorts.py -v` → FAIL (no module).
- [ ] **Step 3: Implement `scripts/cohorts.py`**

```python
"""Cohort assignment for P1 percentile scoring. Pure; policy lives in the
merge_map config (scoring-config.json), authored with Dom (§5-1)."""
import re

def top_level_layer(layer_str):
    if not layer_str:
        return None
    m = re.match(r'\s*(\d{2})', str(layer_str))
    return m.group(1) if m else None

def cohort_key(layer_str, merge_map):
    tl = top_level_layer(layer_str)
    if tl is None:
        return None
    return merge_map.get(tl, tl)
```

- [ ] **Step 4: Run, verify GREEN.**
- [ ] **Step 5 (WITH Dom): author `00-master/scoring-config.json`** — the merge-map + percentile-metric list, using Dom's §5-1/§5-2 answers. Skeleton:

```json
{
  "p1": {
    "cohort_merge_map": { "<see §5-1>": "..." },
    "percentile_metrics": ["gross_margin","fcf_margin","roic","ev_ebitda","fcf_yield","ps"],
    "absolute_metrics": ["nd_ebitda","peg","fwd_pe"]
  },
  "p2": { "wacc": 0.10, "terminal_growth": 0.03, "years": 10,
          "grounded_growth_source": "rev_3y_cagr", "placement": "value_submetric" },
  "tier_bands": { "note": "post-P1 recalibration lands here per §5-4" }
}
```
> `fwd_pe` / `peg` intentionally NOT percentiled: the critique's P1 metric list is Gross Margin, FCF Margin, ROIC, EV/EBITDA, FCF Yield, P/S only. Confirm with Dom whether P/E-family joins (default: no, per doc).

- [ ] **Step 6: Commit** — `git add scripts/cohorts.py tests/test_cohorts.py 00-master/scoring-config.json && git commit -m "feat(scoring): cohort assignment for P1 (config-driven, §5-1)"`

---

## Task P1-2: Percentile scoring in recalc_watchlist.py — **BLOCKED on P1-1 + §5-2**

**Files:**
- Modify: `scripts/recalc_watchlist.py`
- Create: `tests/test_p1_scoring_integration.py`

**Interfaces:**
- Consumes: `cohort_percentile.rank_cohort`, `cohorts.cohort_key`, `scoring-config.json`.
- Produces: a `recalc(..., mode="percentile"|"absolute")` switch so before/after (Task P1-4) can call both.

**Key design:** percentile scoring is inherently cross-sectional — you cannot score one row in isolation; you need the whole cohort's column at once. So `recalc()` gains a pre-pass: group rows by `cohort_key`, and for each (cohort, metric) call `rank_cohort` to get 0–100 scores, then substitute those for the absolute-band scores of the six percentile metrics. Absolute metrics (ND/EBITDA, PEG, Fwd P/E, all subjective) are unchanged. **Direction matters:** Gross Margin/FCF Margin/ROIC/FCF Yield are `higher_is_better=True`; EV/EBITDA and P/S are `higher_is_better=False`.

> **Layer-carve-out interaction (must handle):** col F already holds EV/FCF for Layer 10 (rule 10) and EV/MW for the Layer 9 capacity cohort (rule 13). Under percentile scoring these become "rank EV/FCF within the Layer-10 cohort" and "rank EV/MW within the Layer-9 capacity cohort" — which is *more* consistent, not less (the carve-outs were the ad-hoc precedent P1 generalizes). Preserve the value selection (which raw metric sits in col F), swap only the band→percentile step.

- [ ] **Step 1: Write failing integration test** — build a tiny 2-cohort workbook fixture (reuse conftest patterns), assert: (a) within a cohort the higher-Gross-Margin name gets the higher Quality-from-GM contribution; (b) a name maxing its cohort on a metric gets ~92 (n=6) not 100; (c) `mode="absolute"` reproduces today's numbers exactly (regression pin).
- [ ] **Step 2: Run, verify RED.**
- [ ] **Step 3: Implement the cohort pre-pass + `mode` switch in `recalc()`.** (Full code authored at execution time against the then-current `recalc_watchlist.py`; keep the absolute path byte-for-byte reproducible under `mode="absolute"`.)
- [ ] **Step 4: Run, verify GREEN; run full suite.**
- [ ] **Step 5: Commit.**

---

## Task P1-3: Mirror the percentile transform into Excel — **BLOCKED on P1-2 + §5-4**

**Files:** Modify `00-master/ai_supply_chain_scoring.xlsx` (Methodology + Watchlist), `scripts/rebuild_watchlist_formulas.py`.

**The hard part:** Excel has no clean native "percentile within a dynamic cohort" that stays live and legible across 168 rows with per-cohort grouping. Two options to put to Dom at execution time:
- **(A) Computed-column approach:** a helper block (hidden sheet or right-of-data columns) computes `PERCENTRANK.INC`/`COUNTIFS`-based cohort ranks per metric; the metric-score cells reference those. Stays "live" (rule 4) but adds ~6 helper columns and COUNTIFS complexity.
- **(B) Scripted-value approach:** `recalc_watchlist.py` writes the percentile scores as values, with a prominent Methodology note that the six metric columns are script-maintained (like the EV/FCF values were pre-2026-06-12). Violates the "formulas not values" preference for those cells — requires explicit Dom approval to relax rule 4 for cohort-relative metrics specifically.

- [ ] **Step 1:** Put A vs B to Dom (this is a real rule-4 tradeoff, not an implementer's call).
- [ ] **Step 2:** Implement chosen approach; document the transform in the Methodology tab (percentile convention, cohort definition, direction per metric).
- [ ] **Step 3: run `python3 scripts/rebuild_watchlist_formulas.py`**, then assert Python `recalc(mode="percentile")` TOTALs == Excel cached values for a sample of names.
- [ ] **Step 4: Commit.**

---

## Task P1-4: Before/after diff + tier re-derivation + roster regen (the P1 gate) — **BLOCKED on P1-2**

**Files:** Create `scripts/p1_before_after.py`; extend `tests/test_p1_scoring_integration.py`.

This is the acceptance artifact the critique mandates. It is read-only and does NOT write the Watchlist or Targets.

- [ ] **Step 1: Write failing tests** asserting the diff harness computes, for every name, both `absolute` and `percentile` TOTAL + tier; and that:
  - **(a) within-cohort monotonicity preserved** — within any cohort, ranking by percentile-TOTAL never inverts a strict ranking that all-metrics-better implies;
  - **(b) style-gap compression** — mean(percentile score) for the silicon+cloud group minus mean for the power+industrials group is materially smaller than under absolute bands (assert the gap shrinks by a threshold agreed with Dom);
  - **(c) tiers are re-derived** from the new TOTALs (not carried over).
- [ ] **Step 2: Run, verify RED.**
- [ ] **Step 3: Implement `p1_before_after.py`:** emits a markdown/CSV report — per-name (old→new TOTAL, old→new tier), per-cohort gap-compression table, and the **roster delta**: names crossing the live Entry 74.5 / Exit 73.0 thresholds (read from `refresh_targets.py` params, not hardcoded). Explicitly list ENTERs and EXITs.
- [ ] **Step 4: Run, verify GREEN.**
- [ ] **Step 5:** Produce the report and **hand it to Dom.** Membership changes are surfaced, never applied here.
- [ ] **Step 6: Commit the harness** (not any Watchlist change).

---

## Task P1-5: Tier-band recalibration + docs — **BLOCKED on §5-4, after P1-4 report**

- [ ] **Step 1:** With the P1-4 distribution in hand, Dom decides recalibrated tier bands + entry/exit thresholds (§5-4). Write them into `scoring-config.json` and the portfolio.xlsx "Sizing Rules" sheet.
- [ ] **Step 2:** Add a CLAUDE.md rule: cohort-relative scoring for the six style-biased metrics (cohort = per `scoring-config.json` merge-map), the hybrid boundary (ND/EBITDA + R stay absolute), and a restatement that category-weight changes remain IC-gated (P3).
- [ ] **Step 3:** Short cross-reference in `rating-rubric-and-workflow.md` (subjective ratings unaffected; objective metric scoring is now cohort-relative — see CLAUDE.md).
- [ ] **Step 4:** Re-run `tests/test_rubric_weights_match_workbook.py` (P0 gate) — still green (weights untouched).
- [ ] **Step 5: Commit.**
- [ ] **Step 6 (SEPARATE, Dom-approved):** only if Dom approves a rebalance on the new scores, run `python3 scripts/refresh_targets.py` as its own change with its own model-event log (rule 18). NOT part of the P1 methodology commit.

---

## Task P2-0: Pure reverse-DCF — **DONE**

**Files:** `scripts/reverse_dcf.py`, `tests/test_reverse_dcf.py`

- [x] Tests written first (12), RED, implemented (bisection solver + provisional gap bands), GREEN, full suite green. Sanity check confirmed: EV/FCF 50× megacap → implied ~19.5% → score 15; EV/FCF 5× cyclical → implied ~−12.5% → score 100 (anti-correlated with valuation, as required).

---

## Task P2-1: Grounded-growth + WACC wiring — **BLOCKED on §5-3**

**Files:** Modify `scripts/recalc_watchlist.py`; new Watchlist input column for `implied_growth` (or the resulting score); `tests/test_p2_scoring_integration.py`.

**Inputs the solver needs, and where they come from (free data only):**
- `ev` — already available (used for EV/EBITDA). Reuse the same EV source.
- `fcf0` — statement-based TTM FCF (`batch_score.statement_fcf()`, the CLAUDE.md-mandated source; NOT `info.freeCashflow`).
- `wacc`, `terminal_growth`, `years` — fixed assumptions from `scoring-config.json` (default 10% / 3% / 10yr; a single fixed WACC keeps it free-data and cross-comparable, per the critique).
- `grounded_g` — **§5-3-adjacent choice:** default `rev_3y_cagr` (already a Growth input) as the grounded estimate; confirm with Dom (alternative: a blend, or analyst LT growth if free).

- [ ] **Step 1: Write failing integration test** — a name with cheap EV/FCF and modest grounded growth scores high on the new sub-metric; a rich megacap scores low; a negative-FCF name yields None (blank, skipped in the Value average like other blanks).
- [ ] **Step 2: Run, verify RED.**
- [ ] **Step 3: Implement** — compute `mispricing_score` per row from config; per §5-3 **default placement = a 6th Value sub-metric** (Value average becomes 6 metrics when present, skipping blanks — no reweight, so no P3 entanglement). If Dom instead chooses a new category, STOP: that needs a weight and is P3-gated.
- [ ] **Step 4: Run, verify GREEN; full suite.**
- [ ] **Step 5: Mirror into Excel** (new input column + Methodology note), `rebuild_watchlist_formulas.py`, verify Python==Excel. Same rule-4 A/B tradeoff as P1-3 for the computed cells.
- [ ] **Step 6: Commit.**

---

## Task P2-2: P2 before/after diff — **BLOCKED on P2-1**

- [ ] Extend `p1_before_after.py` (or a sibling) to show Value-score and TOTAL movement from adding the reverse-DCF sub-metric, per-name and per-tier, plus roster delta vs live thresholds. Read-only; hand to Dom. Commit the harness only.

---

## The Validation Gate (critique §4) — acceptance, measured LATER

No P-item is "an improvement" until it beats the current version out-of-sample. Before/after diffs (P1-4, P2-2) show *what changed*; only these show *better*, and they need data that does not yet exist:
- **IC-by-category and IC-by-tier** from `tracking/forecasts.jsonl` / `tier_forward_returns.py` as forecasts resolve (calibration loop, rule 17; first resolutions ~2026-09-30).
- **EW-null:** does the changed score move the model toward beating equal-weight of the same universe (the EW that currently beats it, +6.76% vs +5.40%)? If not, the change isn't earning its complexity.

Wire each landed P-item's *retrospective* acceptance to these once data resolves. This is diagnostic only — it does not auto-reweight (that trap is why P3 is gated).

---

## Adjacent items in this sequence tier (P4/P5/P6) — planned after P1/P2 land

In-scope for the P1/P2/P4–P6 tier but sequenced after P1/P2 (kept out of this plan to avoid scope bloat; each gets its own short plan):
- **P4 (de-dup collinear inputs)** — start with Task P4-0: compute the category-subscore correlation matrix across the Watchlist so §5-5 (remove vs document) is data-informed.
- **P5 (D5 comparability)** — split D5 into supplier-exposure (L1–8) vs buyer-commitment (L9), each normalized within its framework before contributing.
- **P6 (×20 subjective floor)** — consider mapping rating 1→0 via `(rating−1)×25` so a genuine "zero" dimension can drag the score down. Minor; interacts with band recalibration (do after §5-4).

---

## Explicit Non-Goals (do NOT do in this plan)

- **P3 — category-weight changes: DEFERRED, IC-GATED.** No weight in the Weights tab moves on intuition, on the doc's Momentum↑/AI-Thesis↓ prior, or on any argument in this session. The deliverable that would justify a weight change is the **IC table** (per-category IC vs forward returns), not the change. Until ≥~2 quarters of resolved forecasts exist, weights stay. `tests/test_rubric_weights_match_workbook.py` (P0) keeps the doc honest to whatever the tab says.
- No regime-dependent / conditional / interaction-term weighting; no ML-learned weight matrix.
- No retroactive edits to frozen historical ratings (breaks the audit).
- No change to the hysteresis rebalance logic in `refresh_targets.py`.
- No optimizing anything on the current single-regime (AI-bull) return history.

---

## Self-review (spec coverage)

- P1 (§P1) → Tasks P1-0..P1-5 ✓ (percentile transform, cohort assignment, recalc wiring, Excel mirror, before/after+tiers+roster gate, band recalibration).
- P2 (§P2) → Tasks P2-0..P2-2 ✓ (solver+score done; grounded-growth/WACC wiring; before/after gate).
- §5 decisions 1–5 → surfaced as Blocking Decisions, each tied to the tasks it gates ✓.
- Critique test requirements → P1: monotonicity + style-gap compression + tier re-derivation + roster diff (P1-4) ✓; P2: solver unit tests + megacap-vs-cyclical sanity (P2-0, done) ✓.
- §4 validation gate → its own section, deferred to IC data ✓.
- §7 out-of-scope + P3 gate → Explicit Non-Goals ✓.
