# P1 before/after — cohort-relative (peer-ranked) scoring

**Date:** 2026-07-02  
**Status:** REVIEW ONLY — nothing changed in the live workbook, scores, tiers, or portfolio. This shows what peer-relative scoring *would* do, so we can recalibrate the tier cutoffs before turning it on (critique §5-4).

**What changed:** six style-biased metrics (EV/EBITDA, FCF-yield, P/S, ROIC, gross margin, FCF margin) now rank each name against its layer peers instead of against fixed cutoffs — but only where the peer group has ≥8 names (else it falls back to the old cutoffs). Everything else (Net-Debt/EBITDA, Fwd P/E, PEG, Growth, and all judgment ratings) is unchanged.

## 1. The point: the business-model bias collapses

Mean subscore, capital-light (silicon L06 + software L10) **minus** capital-heavy (power/grid/DC/fabs/servers):

| Category | Old gap (fixed cutoffs) | New gap (peer-ranked) |
|---|---|---|
| Quality | **+28.4** (light 83 vs heavy 55) | **+5.9** (light 59 vs heavy 53) |
| Value | -2.1 | -1.4 |

Quality was mostly measuring 'has software margins' — every SaaS name maxed the band at ~100, so it never discriminated *within* software. Now it does. The 28→6 collapse is the fix.

## 2. Tier changes

28 names change tier: **10 up, 18 down**. More down than up because the peer-ranked scores compress toward the middle (a name can no longer sit at 100 just for its business model) — which is exactly why the tier cutoffs need re-cutting before this goes live.

### Biggest drops (all software — were auto-maxed before)

| Ticker | Layer | TOTAL old→new | Quality old→new | Tier |
|---|---|---|---|---|
| ZS | 10 | 75.5 → 61.8 | 100 → 41 | ✓✓ → ✓ |
| SNOW | 10 | 63.6 → 52.6 | 68 → 19 | ✓ → ? |
| MDB | 10 | 61.3 → 50.9 | 68 → 24 | ✓ → ? |
| WDAY | 10 | 74.7 → 66.5 | 100 → 63 | ✓✓ → ✓ |
| PANW | 10 | 72.7 → 64.8 | 100 → 66 | ✓✓ → ✓ |
| CRWD | 10 | 61.6 → 53.9 | 79 → 44 | ✓ → ? |
| AAPL | 10 | 62.2 → 54.6 | 91 → 59 | ✓ → ? |
| DDOG | 10 | 71.0 → 65.3 | 79 → 55 | ✓✓ → ✓ |
| TEM | 10 | 58.0 → 52.6 | 58 → 10 | ✓ → ? |
| CRM | 10 | 72.8 → 67.6 | 80 → 56 | ✓✓ → ✓ |

### Biggest rises (capital-heavy — were unfairly buried)

| Ticker | Layer | TOTAL old→new | Quality old→new | Tier |
|---|---|---|---|---|
| CORZ | 09 | 50.9 → 57.2 | 30 → 45 | ? → ✓ |
| INTC | 05 | 50.1 → 55.6 | 45 → 58 | ? → ✓ |
| KEEL | 09 | 38.9 → 42.8 | 15 → 19 | ✗ → ? |
| RMBS | 06 | 66.9 → 70.1 | 100 → 97 | ✓ → ✓✓ |
| BTDR | 09 | 53.4 → 56.2 | 22 → 34 | ? → ✓ |
| PUMP | 01 | 52.7 → 55.2 | 50 → 54 | ? → ✓ |
| CSCO | 07 | 68.0 → 70.4 | 85 → 81 | ✓ → ✓✓ |
| AAOI | 07 | 53.3 → 55.6 | 25 → 13 | ? → ✓ |
| APLD | 09 | 54.7 → 56.4 | 30 → 31 | ? → ✓ |
| NVDA | 06 | 84.1 → 85.6 | 100 → 94 | ✓✓ → ✓✓✓ |

## 3. Portfolio-eligible roster (≥74.5) — WITH THE OLD CUTOFFS

Old cutoffs applied to the new scores: **21 → 16 names**. This is NOT the final roster — it's what happens if we keep the old 74.5 line against a compressed distribution. Re-cutting the line (§5-4) is the next step; only then does the real roster emerge.

- Would ENTER: AMZN
- Would EXIT: ALAB, AMD, EQT, PLTR, WDAY, ZS

The exits are the crowded silicon/software winners (AMD, Palantir, Workday, Zscaler, Astera) that were riding the business-model inflation — the same names the 13F put-target test and the equal-weight-beats-the-model result pointed at.

## 4. Next step (needs your sign-off)

Re-cut the tier cutoffs (85/70/55/40) and the portfolio entry/exit lines (74.5/73.0) to fit the new, more-compressed spread — so 'top tier' still means top tier. We do that together, then regenerate the roster, then (only with your OK) wire it into the live workbook and decide on any rebalance.

