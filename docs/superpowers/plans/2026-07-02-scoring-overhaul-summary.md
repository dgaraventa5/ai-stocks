# Scoring overhaul — what changed & how the scores moved

**Date:** 2026-07-02  ·  **For review**  ·  Portfolio NOT yet changed.

This summarizes the scoring-system overhaul (the external critique, items P0–P6). Everything here changed how names are **scored**, not what is **owned**. All changes are committed, tested (157 checks), and reversible.

## The changes, in plain English

| # | Change | What it does | Status |
|---|---|---|---|
| P0 | Fixed stale docs | The rating rubric quoted the wrong category weights; corrected + locked with a test | Done |
| P1 | **Peer-ranking** | The six "style" metrics (margins, ROIC, EV/EBITDA, FCF-yield, P/S) now rank each name against its layer peers instead of fixed cutoffs | **Live** |
| P2 | **Cheap-vs-expectations** | A reverse-DCF: rewards names whose price is justified by growth, dings names priced for more growth than they show | **Live** |
| P6 | Removed the score floor | AI-Thesis & Risk no longer floor at 20 — a genuine "zero" can now score 0 | **Live** |
| P4 | Double-counting | Measured it (correlations 0.6–0.8); documented as deliberate rather than removing inputs (each adds an angle) | Measured/disclosed |
| P5 | Dual-meaning rating | "Hyperscaler exposure" means two things; peer-grouping already separates them | Documented |
| P3 | Re-weighting categories | Deliberately parked — needs months of real return data (~fall) | Waiting on data |

Plus enabling work: a **currency fix** (foreign stocks like TSMC now get real valuation numbers instead of blanks), **peer-group expansion** (added foundries so the group is big enough to rank), rated **NetApp**, and swapped out **SkyWater** (being acquired) for **SMIC**.

## How the scores moved (old methodology vs new, same data)

Across the **169 fully-rated names**, **42 changed tier**. The scale barely shifted overall — the point was to change *who ranks where*, not to inflate/deflate everyone.

### Biggest drops — mostly crowded software/chip names that were getting a free ride

| Name | Layer | Old → New | Tier |
|---|---|---|---|
| ZS | 10 | 75.5 → 61.4 (-14.1) | ✓✓ → ✓ |
| SWKS | 06 | 53.6 → 41.3 (-12.4) | ? → ? |
| AAPL | 10 | 62.2 → 49.8 (-12.4) | ✓ → ? |
| MDB | 10 | 61.3 → 49.2 (-12.1) | ✓ → ? |
| WDAY | 10 | 74.7 → 63.5 (-11.2) | ✓✓ → ✓ |
| SNOW | 10 | 63.6 → 52.6 (-11.0) | ✓ → ? |
| PATH | 10 | 69.9 → 60.0 (-9.9) | ✓ → ✓ |
| FTNT | 10 | 68.2 → 58.6 (-9.6) | ✓ → ✓ |
| PANW | 10 | 72.7 → 63.2 (-9.4) | ✓✓ → ✓ |
| CRWD | 10 | 61.6 → 52.7 (-9.0) | ✓ → ? |
| SPCX | 10 | 51.8 → 43.2 (-8.6) | ? → ? |
| QCOM | 06 | 59.0 → 50.5 (-8.5) | ✓ → ? |

### Biggest rises — capital-heavy names the old bands unfairly buried

| Name | Layer | Old → New | Tier |
|---|---|---|---|
| AMZN | 09 | 73.3 → 77.7 (+4.4) | ✓✓ → ✓✓ |
| TE | 01 | 46.1 → 50.2 (+4.1) | ? → ? |
| CORZ | 09 | 50.9 → 54.5 (+3.6) | ? → ? |
| ORCL | 09 | 65.3 → 68.2 (+2.9) | ✓ → ✓ |
| INTC | 05 | 50.1 → 52.9 (+2.8) | ? → ? |
| OKLO | 01 | 34.7 → 37.0 (+2.4) | ✗ → ✗ |
| CRWV | 09 | 62.7 → 64.9 (+2.2) | ✓ → ✓ |
| NBIS | 09 | 61.8 → 63.9 (+2.1) | ✓ → ✓ |
| NVDA | 06 | 84.1 → 85.9 (+1.8) | ✓✓ → ✓✓✓ |
| IREN | 09 | 57.1 → 58.8 (+1.7) | ✓ → ✓ |
| RMBS | 06 | 66.9 → 68.5 (+1.6) | ✓ → ✓ |
| HUT | 09 | 61.2 → 62.6 (+1.4) | ✓ → ✓ |

## The roster now — top 20 by the new score

| Rank | Name | Layer | Score | Tier |
|---|---|---|---|---|
| 1 | NVDA | 06 | 85.9 | ✓✓✓ |
| 2 | MU | 06 | 85.6 | ✓✓✓ |
| 3 | TSM | 05 | 82.4 | ✓✓ |
| 4 | CRDO | 07 | 80.6 | ✓✓ |
| 5 | ANET | 07 | 79.8 | ✓✓ |
| 6 | META | 09 | 79.1 | ✓✓ |
| 7 | AVGO | 06 | 77.9 | ✓✓ |
| 8 | AMZN | 09 | 77.7 | ✓✓ |
| 9 | MSFT | 09 | 77.1 | ✓✓ |
| 10 | GOOGL | 09 | 75.6 | ✓✓ |
| 11 | FIX | 03 | 75.6 | ✓✓ |
| 12 | ALAB | 06 | 75.6 | ✓✓ |
| 13 | SNDK | 06 | 75.1 | ✓✓ |
| 14 | EME | 03 | 74.7 | ✓✓ |
| 15 | RDDT | 10 | 74.4 | ✓✓ |
| 16 | VRT | 03 | 73.8 | ✓✓ |
| 17 | APP | 10 | 72.6 | ✓✓ |
| 18 | PLTR | 10 | 72.0 | ✓✓ |
| 19 | APH | 07 | 70.6 | ✓✓ |
| 20 | VST | 01 | 70.3 | ✓✓ |

## Notable single-name moves worth knowing

- **TSMC**: the currency fix revealed how expensive it is (22× EV/EBITDA was hidden as a blank) → dropped ✓✓✓ → ✓✓.
- **Zscaler**: peer-ranking cut its Quality 100 → 41 (below-average *among software*), but the reverse-DCF gave some back (growth justifies its multiple) — the multi-lens effect working.
- **Amazon**: +4.4, crossing *into* the portfolio-eligible roster (it was just below the line before) — the old bands were unfairly holding it back.
- **Nvidia**: ticked up into the very top tier (✓✓ → ✓✓✓) — it now sits at the top of its silicon cohort.
- **Intel**: rose in score (ranks better among foundries than the fixed bands allowed), but the removed floor (P6) partly offset it, so it stayed just under the ✓ line.
- Low-AI names (bitcoin miners, hydrogen, some chip names) dropped on the removed 20-floor — they no longer bank free AI-thesis credit.

## What this means
- The score now measures **merit within an industry** and **price vs. expectations**, not "has software-style margins."
- It moved *against* the crowded, already-run-up favorites and *toward* fairly-priced leaders and capital-heavy names — the direction the "equal-weight beats the model" evidence pointed.
- **Next step:** the portfolio rebalance — bringing holdings in line with these scores. Your call; not done yet.

