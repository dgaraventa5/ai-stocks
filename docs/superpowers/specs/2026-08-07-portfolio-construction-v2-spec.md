# Spec: Portfolio construction v2 — inverse-vol sizing, top-N selection, band shadows

**Date:** 2026-08-07
**Status:** Proposal — the live portfolio is NOT to be changed until Dom approves the migration table in §A3
**Supersedes:** the standalone inverse-vol sizing spec (folded in here as Part A)

This is one change-set with three parts, in build order:
- **Part A — Sizing:** replace tier-proportional position sizes with inverse-volatility sizes. (Evidence-driven; approved direction.)
- **Part B — Selection form:** convert the absolute score cutoff (≥76 / <74.5) to a **top-N with hysteresis** rule. (Logic-driven structural fix; does NOT retune selectivity.)
- **Part C — Instrumentation:** score-band shadow portfolios + point-in-time score logging, so the *actual* cutoff level gets decided by forward data in ~2 quarters, not by a backtest now.

Sequencing: A and B land together (they touch the same rebalance path); C can land same day — it is additive tracking only. Nothing in this spec changes the scoring engine.

---

## Part A — Inverse-volatility position sizing

### A0. Why (evidence)

Measured on the real window 2026-05-26 → 2026-08-06 (n≈50 trading days, includes the July
semis crash), chain-linked on the actual roster events, real prices:

| Construction | Total | Vol | Sharpe | maxDD |
|---|---|---|---|---|
| Inverse-vol on model roster | **+7.67%** | 37.4% | **1.10** | −13.0% |
| Equal-weight on model roster | +6.08% | 48.0% | 0.64 | −16.7% |
| EW ≥70 universe (~40) | +3.79% | 40.1% | 0.41 | −14.1% |
| **Model (tier-weighted, actual)** | **+0.93%** | 47.4% | 0.02 | **−18.4%** |

Decomposition: the score's *selection* (≥76 subset) beat the broad universe (+2.3 pts, EW vs
EW) — first positive selection evidence in the project, through a crash. The *tier-proportional
sizing* cost ~5.1 pts vs equal-weighting the identical names (it concentrated the book in
TSM/MU into the July memory crash). Keep the score as selector; stop using it as sizer.

Confidence framing (don't overstate in docs/UI): "drop score-proportional sizing" is
high-confidence. "Inverse-vol specifically beats equal-weight" is a lean (+1.6 pts over EW is
inside 10-week noise) — hence the permanent EW shadow + tripwire (§A4). Inverse-vol's failure
mode is gentle: noisy vol estimates degrade it *toward* equal-weight.

### A1. The sizing rule

For the current roster R (all names passing the Part-B selection rule):

```
sigma_i = stdev(daily returns of i over trailing LOOKBACK trading days)
raw_i   = 1 / max(sigma_i, SIGMA_FLOOR)
w_i     = raw_i / sum(raw_j for j in R)
then apply caps/floor and renormalize
```

Parameters (single config block, `portfolio-config.json` → `sizing`):
- `LOOKBACK = 60` trading days
- `SIGMA_FLOOR = 0.005` daily (≈8% annualized)
- `MAX_WEIGHT = 0.12` — iterative cap-and-redistribute (cap breachers, redistribute pro-rata
  among uncapped, repeat to convergence; unit-test convergence)
- `MIN_WEIGHT = 0.03` — post-cap floor; lift and renormalize
- Insufficient history (< LOOKBACK days, e.g. recent IPOs): use the median sigma of the
  name's layer cohort; log when the fallback fires
- Weights sum to 1.0 within 1e-9 after all adjustments

Implement as a pure function `inverse_vol_weights(prices, roster, cfg) -> Series` in
`scripts/position_sizing.py`. No I/O inside; unit-testable.

### A2. When re-sizing happens (turnover guardrails)

Weights are recomputed and traded only on:
1. **Membership events** — any Part-B add/remove (existing trigger). Whole book re-sizes.
2. **Scheduled re-size** — monthly, first trading day; trade **only** names drifted more than
   `DRIFT_BAND = 0.25` relative from target (target 8% → trade only if <6% or >10%).
3. Never intra-month on vol changes alone — a vol spike changes next month's targets, not
   today's positions.

Log every re-size as an event in `performance-config.json` `events` (same schema as
tier-crossing events) with `"reason": "resize_monthly" | "membership" | "sizing_migration_invvol"`
so the series stays fully reconstructible.

### A3. Migration (one-time, gated on Dom)

Compute inverse-vol targets for the current roster; present the before/after table (ticker,
current weight, new target, delta) for **explicit approval**; on approval log one
`sizing_migration_invvol` event. History is not restated — the migration event is the seam.

### A4. Permanent sizing audit + tripwire

Add a chain-linked `EW_ROSTER` shadow series (equal-weight of the model's actual roster on the
same event dates) to `performance-series.json`, surfaced on the site's Performance tab.
`MODEL − EW_ROSTER` is the standing measurement of what the sizing rule adds.
**Tripwire (proposal, confirm in §D):** if MODEL trails EW_ROSTER over two consecutive
quarters, revert sizing to equal-weight.

---

## Part B — Selection form: top-N with hysteresis (replaces absolute ≥76 / <74.5)

### B0. Why

The 76/74.5 lines are absolute numbers inherited from the pre-overhaul scale. The 2026-07-02
scoring overhaul reshaped the score distribution (42/169 names changed tier) — any future
methodology change silently changes what an absolute cutoff *means*, and portfolio size becomes
a side effect of scale drift rather than a chosen property. Converting to rank form fixes the
mechanism. **This is a form change, not a selectivity retune:** N is chosen to match the
current book (~15), and moving N later is a data decision that Part C exists to inform.

### B1. The rule

- **Entry:** a name enters when it ranks in the **top N = 15** of the watchlist by TOTAL score.
- **Exit:** a name exits only when it falls **below rank M = 18**.
- Ranks N+1..M (16–18) are the hysteresis dead-band: incumbents there stay, outsiders there
  don't enter — same anti-churn philosophy as today's 76/74.5, expressed in ranks.
- Ties at the boundary: break by higher score, then by incumbency (incumbent stays).
- Trigger cadence unchanged: evaluated on the existing weekly/quarterly refresh and on-demand
  scans, exactly where the ≥76 check runs today.
- Membership changes flow into Part A (a membership event re-sizes the whole book).

### B2. Guardrails

- Expected steady-state churn should be similar to today's; add a log line whenever a
  rank-crossing would trade so the first month of the new rule is auditable.
- If a scoring-methodology change ever reshuffles ranks en masse, membership changes still go
  through the normal event path (visible diff), never a silent resort — same principle as the
  overhaul's "portfolio NOT yet changed" gate.
- Do NOT tune N against the 10-week return history. N=15 is continuity; changing N is a
  Part-C-informed decision later.

---

## Part C — Instrumentation: band shadows + point-in-time scores

### C0. Why

The cutoff *level* question ("should the bar be lower?") flipped answers between the two
windows we've measured (breadth won through Jul 1; selectivity won through Aug 6). Ten weeks
cannot settle it, and intermediate-cutoff backtests are blocked anyway by the absence of a
point-in-time score panel (using today's scores on past prices is look-ahead, doubly so across
the Jul-2 overhaul). So the cutoff gets decided by **forward** evidence: run the bands live and
watch where the score's discrimination fades.

### C1. Band shadow portfolios (forward-only, equal-weight, chain-linked)

Add three shadow series to the tracker, starting at deploy date (no backfill):
- `BAND_TOP` — EW of ranks 1–15 (mirrors the Part-B book, unsized)
- `BAND_NEXT` — EW of ranks 16–25
- `BAND_TAIL` — EW of ranks 26–40
Rosters refresh on the same cadence as Part B, membership changes logged as shadow events.
Surface all three on the Performance tab next to EW_ROSTER.

**Decision rule (pre-registered now so it can't be gamed later):** after **two full quarters**,
compare the bands. If `BAND_NEXT` has kept pace with `BAND_TOP` (within noise) → the score's
discrimination extends past rank 15 → raising N (e.g., to 20–25) is justified, and the
diversification is free. If `BAND_NEXT` lags materially → the bar is earning its keep → N holds.
`BAND_TAIL` is the control that shows where discrimination clearly dies.

### C2. Point-in-time score panel (prerequisite for everything later)

On **every** scoring pass (weekly scan, quarterly rescore, ad-hoc), append the full watchlist
to `tracking/score-history.csv`: `date, ticker, total_score, rank, tier` (one row per name per
pass; append-only; never rewritten). This is the panel the IC test, the band analysis, and any
future cutoff/backtest work all require. Backfill is impossible — which is exactly why logging
starts now and never skips a pass.

---

## Tests (blocking)

Part A: `test_invvol_weights_basic` (synthetic vols → exact weights) · `test_caps_and_floor`
(cap binds → redistribution correct, converges, sums to 1; floor lifts) · `test_sigma_floor` ·
`test_short_history_fallback` (cohort-median path, logged) · `test_monotonic` (lower vol ⇒
weakly higher weight post-cap) · `test_drift_band` (inside → no trades; outside → to target) ·
`test_event_log_roundtrip` (resize event reproduces identical daily series on tracker re-run).

Part B: `test_topn_entry_exit_hysteresis` (rank 15 enters; incumbent at 17 stays; incumbent at
19 exits; outsider at 16 doesn't enter) · `test_tie_break` (score then incumbency) ·
`test_rank_stability` (a methodology reshuffle produces membership diffs through the event
path, never a silent resort).

Part C: `test_band_rosters_disjoint_and_complete` (bands partition ranks 1–40, refresh with
Part-B cadence) · `test_score_history_append_only` (a pass appends exactly one row per name;
re-running a pass does not duplicate or rewrite).

Integration: full pipeline on a frozen price fixture is byte-identical on repeat runs.

## Non-goals / do NOT do

- No changes to the scoring engine, category weights, or metrics (separate workstreams; P3
  remains IC-gated).
- No minimum-variance / risk-parity optimizers in this change (later candidates, evaluated
  against the §A4 shadow).
- No score, tier, or return forecast as a sizing input.
- No tuning LOOKBACK, caps, N, or M against the 10-week history — that is curve-fitting the
  window that motivated the change.
- No backfilled band shadows — forward-only.

## Open decisions for Dom

1. `MAX_WEIGHT` 12% / `MIN_WEIGHT` 3% — confirm or adjust (12% binds mainly on MSFT/GOOGL in
   calm regimes with ~15 names).
2. Scheduled re-size cadence: monthly (tested) vs quarterly (less turnover, staler targets).
3. Tripwire to revert sizing to equal-weight: MODEL < EW_ROSTER two consecutive quarters — confirm.
4. Part B N/M: 15/18 proposed for continuity — confirm.
5. Band boundaries for C1 (1–15 / 16–25 / 26–40) — confirm.
6. Optional: forward tier-weight paper shadow for nostalgia/comparison, or rely on
   pre-migration history only? (Default: rely on history.)

---

*Commit one-liner: the score chooses the names by rank, trailing volatility chooses the sizes,
equal-weight rides shotgun as the permanent null, and three score-bands run ahead as scouts so
the cutoff decision gets made by data in two quarters instead of by a backtest today.*
