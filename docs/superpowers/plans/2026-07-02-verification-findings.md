# Post-overhaul verification — findings against the 8-point code review

**Date:** 2026-07-02 · Verified against the actual code (branch `scoring-verification-followup`), each with a test or printed artifact, not prose. The review was right to demand gates: it caught **two real issues that change scores** (#1, #7), **two corrections to my summary** (#4, #5), and **two effects I under-described** (#2, #6).

## Scorecard

| # | Item | Verdict | Gate |
|---|---|---|---|
| 1 | Reverse-DCF sign/shape | Sign ✅ correct, constants ✅ fixed — **but mis-calibrated** ⚠️ | `test_reverse_dcf_monotonic_*` + printed NVDA/ZS/EQT ordering |
| 2 | Within-category reweight | ✅ real, was under-acknowledged | code trace: `value = avg_nonnull([… 6 metrics])` |
| 3 | Cohort governance | ⚠️ guard exists, artifact + rule missing | code trace |
| 4 | Tier bands re-derived? | ✅ consciously held — **but I mis-cited the threshold** | Sizing Rules = 76.0/74.5 |
| 5 | P5 actually comparable? | ❌ **no — my summary was wrong, P5 is open** | code trace: AI-Thesis not peer-ranked |
| 6 | P6 remap clean? | ✅ correct — **but a full rescale, not just a floor** | printed remap table |
| 7 | Currency-fix sweep | ⚠️ **incomplete — 7 more foreign names still blank** | printed sweep incl. ASML |
| 8 | Idempotency | ✅ deterministic | `test_recalc_idempotent.py` |

---

## The two that change scores (need your call before we push)

### #1 — Reverse-DCF (P2) is mis-calibrated: it rewards trailing growth, not mispricing
Sign and shape are correct (monotonic in the grounded-minus-implied gap; WACC 10% / 3% terminal / 10yr are fixed constants, no per-name knobs). **But the "grounded growth estimate" is trailing 3-yr revenue CAGR, and that breaks it in practice:**

| Name | EV/FCF | grounded (3yr CAGR) | implied | gap | score |
|---|---|---|---|---|---|
| NVDA | 39.8 | **100%** | 16% | +84 | 100 |
| MU | 43.8 | 71% | 18% | +53 | 100 |
| ZS | 24.7 | 35% | 10% | +25 | 100 |
| EQT | 10.4 | **−12%** | −2% | −10 | 30 |
| RRC | 11.9 | −18% | 0% | −18 | 15 |

The AI names' trailing growth is enormous and backward-looking, so they **all max at 100** (no discrimination), while cheap cyclicals with a *declining* revenue trend get **penalized**. Net effect: P2 behaves like a growth/momentum factor and **partially undoes P1's de-biasing** — the opposite of a mispricing signal. (My summary's "Zscaler — growth justifies its multiple" hid this: ZS scored the *maximum*, same as NVDA.)

**Options:** (a) cap grounded growth (e.g. ≤20–25%) so hyper-growth doesn't saturate; (b) dampen/decay trailing CAGR toward a mean; (c) use a different grounded estimate; (d) accept it (it's ~3.3% of TOTAL). **My rec: (a) cap it** — cheapest fix that restores the intended behavior. This is a calibration choice, so it's yours.

### #7 — The currency fix is incomplete: 7 more foreign names still blank
Only TSM/UMC were refreshed. Still carrying the old blanked valuation (would move like TSMC did on refresh): **ASML** (EUR), Cameco (CAD), Schneider (EUR), Hitachi (JPY), Tokyo Electron (JPY), BE Semi (EUR), ASE (TWD). ASML especially is a big name that could enter the roster. **Rec: refresh all 7 (via the FX path) to finish the rollout.**

**Both #1 and #7 change the scores the rebalance was built on** — so if we fix either, we should re-rebalance before pushing. That's the honest state: the rebalance I ran is on scores with these two open issues. Good news is nothing's pushed yet.

---

## Corrections to the record
- **#4:** the live portfolio thresholds are **Entry 76.0 / Exit 74.5** (Sizing Rules sheet), not the 74.5/73.0 I cited during our recalibration chat. The bands *were* consciously held and the rebalance used the correct numbers; my framing used the wrong ones. Of the 42 tier changes, **8 crossed the 76 entry line**, but hysteresis (74.5 exit) meant only **4 changed the roster** (+AMZN, −APP/−PLTR/−RDDT); SNDK/GOOGL/ALAB/FIX now sit *held* in the 74.5–76 grandfather zone.
- **#5:** corrected in CLAUDE.md rule 23 — **P5 is deferred, not resolved.** D5 is not peer-ranked, so cohorts don't make the two frameworks comparable; my "cohorts separate them" claim was false.

## Acknowledgments (effects I under-described)
- **#2:** adding the reverse-DCF made Value a 6-metric average, so EV/EBITDA, P/S etc. each dropped from 20% → 16.7% *within Value* — and only for the 111 names that have a reverse-DCF value (the 61 blanks stay at 5 metrics). That's a real, if small, within-category reweight, applied inconsistently across names. It was a mechanical consequence, now on the record.
- **#6:** P6 isn't just "removed the floor." `(rating−1)×25` drops every sub-5 rating (3→50 not 60) and widens the spacing 20→25 — a full rescale of the AI-Thesis and Risk axes (rankings preserved, levels and spread changed).

## Governance to add (#3)
- Cohorts are derived from the Watchlist Layer column at runtime; there's no standalone reviewable cohort-membership artifact and no *enforced* "re-score + log before/after on any cohort edit" rule. The min-cohort-size guard (fall back to absolute at <8) does exist and is tested. Recommend: commit a generated `cohort-membership.md` and add the re-score rule.

## Gates added this pass
- `test_reverse_dcf_monotonic_cheap_fair_expensive`, `test_reverse_dcf_scores_the_gap_not_the_level` (#1)
- `test_recalc_idempotent.py` — pipeline is deterministic across two runs, both modes (#8)
