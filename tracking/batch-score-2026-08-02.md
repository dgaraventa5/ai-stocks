# Batch score run — 2026-08-02 (robotics Layer-11 build-out)

41/41 tickers added in 88s via scripts/batch_robotics_20260802.py (rows 175–215).
Decision record: 11-robotics/robotics-universe-2026-08-02.md

## Gaps (rule 3)

```
9880.HK: FCF fallback (levered est., flagged); HKD->CNY FX applied; ND/EBITDA blank (neg EBITDA)
SERV: ND/EBITDA blank (neg EBITDA)
6954.T: FCF Yield missing (yfinance gap)
6506.T: FCF fallback (levered est., flagged)
AUTO.OL: NOK->USD FX applied (ev_ebitda, ps, fcf_yield)
6383.T: FCF Yield missing
KGX.DE: FCF fallback (levered est., flagged)
2590.HK: FX HKD->CNY; ND/EBITDA blank; FCF fallback CORRECTED->blank (see corrections)
PRCT/SSII/OUST/AEVA/RCAT/ONDS/PDYN/MBLY: ND/EBITDA blank (neg EBITDA)
2252.HK: FX HKD->CNY; FCF fallback (flagged); ND/EBITDA blank
6324.T/6268.T/6481.T: FCF fallback (levered est., flagged)
6861.T: FCF Yield + ND/EBITDA missing (yfinance gaps on .T line)
HSAI: FX USD->CNY; FCF Yield missing; P/S CORRECTED (see corrections)
2498.HK: FX HKD->CNY; FCF Yield missing; ND/EBITDA blank
UMAC: FCF fallback (flagged); ND/EBITDA blank; Rev 3y CAGR blank (non-positive base)
DRO.AX: FCF fallback (flagged); TTM built from <4 quarters — treat all TTM fields low-confidence
```

## Manual data corrections applied post-pull (rule 3 — documented, not silent)

| Ticker | Field | Was | Now | Why |
|---|---|---|---|---|
| HSAI | P/S | 45.06 | 5.7 | yfinance ADR market cap corrupt ($21.2B); verified cap ~$2.64B (stockanalysis 2026-07-31) / TTM rev $461M |
| MBLY | P/S | 0.99 | 3.26 | yfinance counts Class A only (~$2.05B cap); true cap ~$6.75B incl. Intel Class B (850M sh x $7.94) |
| MBLY | FCF Yield % | 19.36 | 5.9 | same share-count corruption (19.25% FCFM x $2.07B rev / $6.75B cap) |
| 6481.T | Rev YoY / EPS YoY | -18.7 / +1307.8 | blank | fiscal-year-transition stub (THK moved FY-end; documented in components appendix) — not business reality |
| 2590.HK | FCF Yield / FCF Mgn | -66.1 / -227.6 | blank | levered-fallback implies -CNY~7B FCF on a company that raised HK$2.71B total and reported first profitability FY2025 — impossible |

Negative EV/EBITDA values on loss-makers were KEPT per existing sheet convention (SMR -8.4, OKLO -29.3 precedents; bands floor them).
