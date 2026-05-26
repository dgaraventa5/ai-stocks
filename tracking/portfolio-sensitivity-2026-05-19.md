# Portfolio Sensitivity Analysis — 2026-05-19

Cross-portfolio sensitivity sweep on all 14 ✓✓ positions in the active portfolio (TSM ✓✓✓ was done on 2026-05-18). Each position was tested for ±20% on numerical inputs and ±1 on subjective ratings.

## Executive summary

**Verdict: Portfolio is robust.** 13 of 14 names have meaningful cushion above the ✓ tier line and NO single-input downgrade flips their tier. The exception is **NBIS** (+0.69pt cushion, 5 flip-risk scenarios).

## Per-name table

| Ticker | TOTAL | Tier | Cushion (+/-) | Top load-bearing | Flip risks | Confidence |
|---|---:|:-:|---:|---|---:|---|
| NVDA | 83.46 | ✓✓ | +13.46 | D1(1.2), D2(1.2) | 0 | HIGH |
| EQT | 82.24 | ✓✓ | +12.24 | D1(1.2), D2(1.2) | 0 | HIGH |
| ANET | 79.97 | ✓✓ | +9.97 | D1(1.2), D2(1.2) | 0 | HIGH |
| ALAB | 78.03 | ✓✓ | +8.03 | D1(1.2), D2(1.2) | 0 | HIGH |
| CTRA | 77.67 | ✓✓ | +7.67 | D1(1.2), D2(1.2) | 0 | MEDIUM-HIGH |
| GOOGL | 77.13 | ✓✓ | +7.13 | gm(1.2), D1(1.2) | 0 | HIGH |
| EXE | 76.95 | ✓✓ | +6.95 | D1(1.2), D2(1.2) | 0 | HIGH |
| ARM | 76.45 | ✓✓ | +6.45 | D4(1.2), D1(1.2) | 0 | HIGH |
| AVGO | 76.25 | ✓✓ | +6.25 | D2(1.2), D3(1.2) | 0 | HIGH |
| RRC | 75.96 | ✓✓ | +5.96 | D1(1.2), D2(1.2) | 0 | MEDIUM-HIGH |
| MSFT | 75.89 | ✓✓ | +5.89 | D1(1.2), D2(1.2) | 0 | HIGH |
| AMD | 75.83 | ✓✓ | +5.83 | D1(1.2), D2(1.2) | 0 | HIGH |
| PLTR | 75.69 | ✓✓ | +5.69 | D1(1.2), D2(1.2) | 0 | HIGH (already calibrated) |
| NBIS | 70.69 | ✓✓ | +0.69 | D2(1.2), D3(1.2) | 5 | MEDIUM — fragile |


## Key findings

### 1. NBIS is the portfolio's fragility point
- Cushion of only +0.69pts above the ✓ tier line
- 5 single-input downgrade scenarios drop NBIS to ✓ tier (any D1-D5 -1)
- **HOWEVER**, the fresh May 13 Q1 2026 data is *positive* for the locked ratings:
  - Meta $27B 5-year partnership confirmed → D1=5 / D5=5 firmly justified
  - 2026 capex raised to $20-25B → D4=5 firmly justified
  - The fragility is in the rubric design (low cushion), not in the actual thesis trajectory
- **Watch**: Q2 2026 customer-diversification metrics (mitigates Meta/MSFT concentration). If diversification stalls and a rating gets downgraded later, NBIS exits ✓✓ tier.

### 2. GOOGL has a numerical-input load-bearing risk (GM at threshold)
- Like TSM, GOOGL's GM (60.37%) sits just above the 60% canonical threshold (≥60 → 100 score)
- Q1 2026 trajectory is *favorable*: Services op margin +3pp YoY, Cloud op margin doubled to 32.9%, AI Overviews driving query ATH
- The 60% threshold is conservatively assessed as a floor, not ceiling. **Confidence: HIGH.**
- Worth flagging at next quarterly review: GM trajectory continues up = no concern

### 3. The Layer 1 (Power-Gen) names share a calibration flag
- EQT, CTRA, EXE, RRC all have D1=5 ratings on the *AI-driven gas demand thesis* rather than literal AI revenue %
- Per the standing D1 calibration item, these may be reviewed under strict-rubric reading at next quarterly rescore
- Combined Power-Gen exposure: 24.4% of portfolio — concentrated thesis bet
- **No fresh research changes the thesis** but worth being conscious of: a Layer 1 D1 recalibration would simultaneously affect 4 portfolio positions

### 4. AI subjective ratings dominate load-bearing across the portfolio
- 13 of 14 names have D1-D5 (AI dimensions) as their top 3 load-bearing inputs
- Only GOOGL has a numerical input (GM) leading
- The pattern: AI subscore weight = 30% of TOTAL, so ±1 on any D = ±1.20 TOTAL impact
- **Implication for monitoring**: focus quarterly review on whether the locked D1-D5 ratings still match the fresh-research evidence

## Cross-portfolio recommendations

| Action | Priority | Why |
|---|---|---|
| Watch NBIS Q2 2026 (~Aug 2026) customer-diversification | HIGH | Only fragile name; need to confirm Meta-concentration mitigates |
| Re-verify GOOGL GM trajectory at Q2 2026 | MEDIUM | If GM holds >60%, ✓✓ rating stable |
| Consider PLTR D1 upgrade to 5 at next rescore | MEDIUM | US Commercial +130% YoY justifies upgrade; lifts TOTAL ~1.2pts |
| Consider MSFT D1 upgrade to 5 at next rescore | LOW | Azure AI growth dominant; could justify |
| Layer 1 D1 calibration pass | MEDIUM | Affects 4 positions simultaneously; decide strict vs loose reading |

## Standing items (re-affirmed from prior sessions)

- TSM ✓✓✓ at 85.13 sits 0.13pts above tier line — D1 should arguably already be 5 (Q1 2026 HPC = 61% of revenue). Strong upgrade candidate.
- NOW (not in portfolio): ✓✓ at 73.5 but D1 was corrected 2026-05-18 from 4→2 (literal rubric); watch Q2 FY26 token-pool consumption.

## Files generated

Per-stock sensitivity reports for all 14 names at `per-stock/{TICKER}/sensitivity-2026-05-19.md`.

This consolidated report at `tracking/portfolio-sensitivity-2026-05-19.md`.
