# Weekly News Scan — 2026-10-24

Scheduled run (rule 37), local Mac. Filing window 2026-10-16 → 2026-10-24 (8 days),
`scheduled_run.py scan-filings --scope all`: **43 filings from 194 EDGAR names, 0 lookups
failed in the end**, 23 names not on EDGAR (foreign local lines). The first pass lost 12
lookups to a short DNS outage on this Mac (CCJ, UEC, LEU, BWXT, SMR, OKLO, NNE, EQT, RRC,
AR, EXE, PLUG); all 12 were retried once the network came back and succeeded, adding the
LEU and EXE 8-Ks. Every filing was read from its primary SEC document plus exhibits. The
META, FIX, WDC, TSM and CRDO filings had already been read and logged by the 2026-10-23
daily watch and are not repeated here.

## Step 0: what I believed going in (holdings)

FIX is the only ✓✓✓ holding (it crossed on 2026-10-23). It was fully briefed by the daily
watch on 2026-10-23 (`per-stock/FIX/context-2026-10-23.md`), so no second `/refresh-context`.

- **NVDA, AVGO, ALAB, CRDO, ANET, MU, SNDK, WDC:** the AI-silicon and connectivity core. Demand is set by hyperscaler capex; news should be about supply.
- **TSM:** leading-edge monopoly; Q3 (6-K 2026-10-15) confirmed it.
- **MSFT, META, PLTR, RDDT:** AI buyers and adopters. META's Q3 was a beat with a large one-off charge.
- **FIX, EME, VRT:** the data-center build-out trade, where backlog is the signal. FIX's backlog is $17.81B (8-K 2026-10-22).
- **GMED:** a robotics name that is mostly a med-tech compounder.

**Diff vs this week's filings:** no holding had a thesis-shifting filing beyond what the
daily watch already logged. The supply-chain read-through was positive: LRCX (+54% YoY, guide
up), TTMI (data-center sales +115%), SMCI (revenue ~26% above its own guide midpoint) and BE
(third guide raise) all point to demand still running ahead of plan. The model's damage this
week was price again (10-22: −5.6%), and it now pushes EME and VRT out of the top 18.

## ⚠️ Material events

| Ticker | Filing | What happened |
|---|---|---|
| ⚠️ **ATKR** | 8-K 2026-10-19 | Prysmian completed the buyout at **$95.00 cash per share (~$3.3B)**. NYSE delisting and a Form 15 follow; the 2031 notes were redeemed; all directors and officers were replaced. **The name no longer trades.** Removing it from the Watchlist is a rule-24 cohort change, which is Dom's call. |
| ⚠️ **SMCI** | 8-K 2026-10-20 (Ex.99.1, preliminary) | Q1 FY27 revenue estimated at **$18.5–19.5B vs a $14.5–15.5B guide** (~26% above the midpoint). Gross margin 12.0–12.5% vs a 10.4–10.8% guide. Full results 2026-11-03. This is the rule-9 "immediate" class once final numbers land. |
| ⚠️ **LRCX** | 8-K 2026-10-21 (Ex.99.1) | Record Sep-quarter revenue **$8.22B (+54% YoY, +22% QoQ)**. GAAP gross margin 52.3%, EPS $2.19 GAAP / $2.20 non-GAAP. China 35% of revenue. Next-quarter guide $8.60B ± $0.4B, EPS $2.33 ± $0.15. |
| ⚠️ **TTMI** | 8-Ks 2026-10-19/22 (Ex.99.1) | Q3 sales **$1.2B (+60% YoY)**; data center and networking +115%, now 41% of sales. Non-GAAP EPS $1.46 vs $0.67; book-to-bill 2.13. Q4 guide $1.42–1.44B; first 2027 outlook $6.5–6.75B. Buying MKS's Ophir Optics for **~$650M cash** (~10.3x FY27 adj. EBITDA, part revolver-funded). Pro forma net leverage 2.8x. |
| ⚠️ **MKSI** | 8-K 2026-10-19 (Ex.99.1) | Selling Ophir Optics to TTM for **$650M cash** (>18x projected FY26 adj. EBITDA). Proceeds go to the balance sheet. Close expected Q2 2027. |
| ⚠️ **BE** | 8-K 2026-10-22 (Ex.99.1/99.2) | Q3 revenue **$1,235.8M (+138% YoY)**. Non-GAAP gross margin 34.5%; non-GAAP EPS $0.94 vs $0.15. **FY26 guide raised for the third time** to $4.4–4.6B revenue and $3.10–3.40 non-GAAP EPS. Added to the S&P 500. |
| ⚠️ **SPCX** | 8-K 2026-10-20 (Ex.99.1) | Q3 revenue **$14.575B (+161% YoY)**. GAAP EPS $0.35 vs −$0.36; adj. EBITDA $8.8B. Capex $19.6B, of which $16.4B in the SI segment; 1.7 GW of nameplate compute. Agreed to buy 800 MHz spectrum (price not disclosed). No numeric guidance. SPCX has an entry hold to 2026-11-10. |
| ⚠️ **ISRG** | 8-K 2026-10-20 (Ex.99.1) | Q3 revenue **$3.05B (+22% YoY)**, procedures ~+15%. GAAP EPS $1.49 vs $1.95 after a **$450M ($0.99/share) antitrust class-action settlement** charge, which still needs court approval. Non-GAAP EPS $3.00 vs $2.40. |
| ⚠️ **NBIS** | 6-K 2026-10-22 (Ex.99.1) | **$3.5B senior secured bridge loan from Citi** (SOFR + 2.75%, stepping up to 3.50%, matures 2027-10-16) for data centers and GPUs. Cites >$40B of investment-grade customer contracts available for later asset-backed financing. |
| ⚠️ **BTDR** | 6-K 2026-10-19 (Ex.99.1) | New Malaysia data-services agreements: 67 MW (A901, Q2 2027) and 60 MW (A103, Q1 2028). >70% of A201 is contracted (>$1.7B over 5 years). AI Cloud backlog ~$2.9B. Bought 200 acres next to Rockdale. |
| ⚠️ **CRM** | 8-K 2026-10-20 (Ex.99.1/99.2) | Definitive agreement to buy **Braze for ~$5.66B EV** ($47.50/share cash). Close in FY28. FY27 guide unchanged; funding described as balance sheet, non-dilutive. |
| ⚠️ **WDAY** | 8-K 2026-10-23 (Ex.1.1/4.2) | **$2.5B of senior notes** (5.70% 2029 through 6.50% 2036). ~$1.0B retires the 3.50% April-2027 notes; the rest is general purposes. |
| ⚠️ **TEM** | 8-K 2026-10-23 (Item 8.01) | Data-licensing deals with **Bristol-Myers Squibb ($137.5M fixed through 2031) and Pathos AI (up to $55M)**, $192.5M in all over ~5 years. BMS can exit on 12 months' notice plus a fee. |
| ⚠️ **RCAT** | 8-K 2026-10-23 (Ex.99.1) | All-cash tender for **Steyr Motors AG at €39.00/share** (~€205M by my calculation; 28.9% premium). The anchor holder has committed. Acceptance period runs to 2026-12-18. |
| ⚠️ **LEU** | 8-K 2026-10-16 (Ex.99.1) | Bought supplier Westerman Holdings for **~$116.0M** ($95.0M cash plus $21.0M in unregistered shares). |
| ⚠️ **EXE** | 8-K 2026-10-19 (Ex.99.1) | **New CEO:** Daniel E. Brown (ex-Chord Energy) from 2026-10-26. The interim CEO returns to non-executive chair. |
| ⚠️ **UMAC** | 8-Ks 2026-10-22/23 (Ex.99.1) | $16.9M drone-component order from Powerus, a customer UMAC holds equity in. Closed the Upgrade Energy acquisition (~1.79M shares + $1.0M cash + up to $26M earn-out). |
| ⚠️ **UPST** | 8-K 2026-10-20 (Item 1.01) | Up to **$200M secured revolver** (MUFG) to capitalize Upstart Bank, N.A., which still needs regulatory approval. |
| ⚠️ **WULF** | 8-K 2026-10-23 (Item 1.01) | Morgan Stanley secured revolver upsized **$250M → ~$400M**. |
| ⚠️ **CIFR** | 8-K 2026-10-16 (Item 1.01) | The definitive $850M 0.00% 2032 convert and 2030-note exchange (already in the 2026-10-17 scan). |

## 📊 Earnings refreshed

Refreshed with `refresh_objective_inputs.py`: BE, NEE, LRCX, SMCI, TTMI, KN, TXN, TSLA, SPCX,
ISRG, plus FIX and WDC. The daily watch had left FIX and WDC marked for a retry because Yahoo
statements were still a quarter behind. META was already re-scored on 2026-10-23. KN and NEE
timed out on the first pass and succeeded on retry.

| Ticker | Before | After | Tier | Note |
|---|---|---|---|---|
| ⚠️📊 **LRCX** | 67.90 | **72.42** | ✓ → **✓✓** | Rev YoY 30.0 → 54.4%, EPS YoY 32.4 → 75.5%. Rank 48 → 23, not near entry (15). |
| ⚠️ **ISRG** | 69.96 | **66.21** | ✓✓ → **✓** | EPS YoY 24.3 → −25.8%. That drop is the **$450M settlement** (rule 15: a ruling is needed; see Needs Dom). Excluding it, GAAP EPS would be ~$2.48 vs $1.95. |
| ⚠️ **TSLA** | 39.47 | 36.09 | ✗ | Rev YoY 25.5 → −0.2%, EPS YoY −4.9 → −42.7%. |
| FIX | 85.27 | 86.18 | ✓✓✓ | The Sep quarter is now in Yahoo: rev YoY 53.7%, EPS YoY 67.7%. Rank 1. |
| WDC | 74.41 | 75.29 | ✓✓ | The new quarter landed, so the EPS YoY override is now **STALE and withheld** (fresh GAAP +50.5%). Rank 14. |
| TXN | 65.29 | 66.73 | ✓ | Rev YoY 22.8 → 27.7%, GM 58.3 → 60.2%. |
| TTMI | 61.05 | 62.87 | ✓ | Rev YoY 37.4 → 59.9%. |
| NEE | 63.63 | 62.13 | ✓ | GAAP EPS YoY 55 → **95.9%**, against adjusted +9.7% (Ex.99). Probably one-off-driven, so a rule-15 ruling is worth considering. |
| SPCX | 59.85 | 60.55 | ✓ | Rev YoY 91.9 → 161.4%. EPS YoY override **STALE, withheld**. Rev 3y CAGR fetch empty, prior kept. |
| KN | 56.71 | 57.81 | ✓ | Ratios only; the Sep quarter is not yet in Yahoo. |
| BE | 70.23 | 70.68 | ✓✓ | EPS YoY fetch empty (prior 60 kept). |
| SMCI | 65.04 | 65.04 | ✓ | Ratios only. The Sep quarter is preliminary and not in Yahoo; the rule-15 override (503.7, June quarter) still applies. |

- **📊 flags:** LRCX (revenue +54% with a guide above Q3) and SMCI (~26% above its own guide midpoint, once final). The >15%-vs-consensus test cannot be run: no filing states consensus. `/earnings-update LRCX` is worth doing; SMCI after 2026-11-03.
- **TTM vs MRQ (rule 9):** LRCX's MRQ gross margin is 52.3% vs a TTM of 51.1%, which is within tolerance. BE's MRQ non-GAAP gross margin is 34.5% vs a TTM of 31.8%.
- Then ran `momentum_50dma.py` (213/217 written) and `recalc_watchlist.py --sync`. **`refresh_reverse_dcf.py` was stopped after ~60 minutes** stuck on slow Yahoo connections. `00-master/reverse-dcf.json` is the one written 2026-10-23 19:17 by the daily watch, one day old. The reverse-DCF term is about 3% of TOTAL, so the effect is small. It will refresh on the next run.
- **Other moves ≥0.5 pt (50DMA and price):** STX 72.65 → 73.27 (rank 22 → 19), VRT 73.25 → 72.75, NVDA 84.39 → 83.87, ONTO 70.19 → 69.57 (✓✓ → ✓), CCJ 55.29 → 54.67 (✓ → ?).

## 💼 Portfolio pipeline

- **Model:** frozen. Membership and tiers are unchanged since the 2026-10-18 event, so **no ticket was generated** this run. `refresh_targets.py --check` is green.
- **⚠️ Two new exit clocks, started 2026-10-24:**
  - **EME:** tradable rank 19, below the exit line of 18.
  - **VRT:** tradable rank 20.
  - They are outside the 2026-10-17 seam window, so they are not damped. Both confirm on the first real `refresh_targets` run after today, normally the **Monday 2026-10-26 daily watch**, if they are still below rank 18.
  - That would be a model event: both sold, the book goes to 15 names at equal weight, and a ticket is generated, which the daily watch holds.
  - There would be no entry: every tradable rank ≤ 15 is already held (APP is 16th, STX 17th).
- **FIX** crossed to ✓✓✓. In equal-weight mode this does not change its allocation (5.9%).
- **APP** is now tradable rank 16, so it no longer qualifies to enter. Its entry hold (to 2026-11-15) is moot for now.
- **Concentration:** Layer 06 is 29% of the portfolio (no layer cap active).
- **Weekly mark** (`tracking/performance-series.json`, closes 2026-10-16 → 2026-10-23):

| | Week | Since inception (2026-05-26) |
|---|---|---|
| **Model** | **−4.2%** | −5.6% |
| SMH | −2.3% | −12.4% |
| QQQ | −0.8% | −3.3% |
| SPY | −0.4% | +1.8% |
| EW universe | −0.8% | −0.3% |

  10-22 did most of the damage: the model fell −5.6% and SMH −6.0%. On 10-23 the model fell −1.5% while SMH rose +0.7%. EW_ROSTER matches the model exactly, as expected in equal-weight mode.

## 🩸 Capitulation flags

Neither exit-side name fired.
- EME: P/S 1.54 is at the 52.7th percentile of its own 3-year range; revenue YoY is 19.8% vs a 3-year median of 17.0%.
- VRT: P/S 6.52 is at the 65.6th percentile; revenue YoY is 24.1% vs 23.4%.

No forecasts were logged.

## 🔬 Rating integrity

`audit_rating_integrity.py --summary`: 214 rated names, **0 ungated**, **68 stale (>90 days)**, unchanged from last week. No holding has a gate violation.

## 🎯 Calibration

`resolve_forecasts.py`: 0 forecasts due, 0 needs_review.

## 🔴 Live pipeline (heartbeat only; reconciliation skipped per rule 37)

- **⚠️ Trading is halted.** `tracking/live/trading-halt.flag` (last rewritten 2026-10-23 13:39Z) records the scheduled executor refusing the **2026-10-18 AMZN-exit ticket**, every weekday 10-19 → 10-23.
  - The main refusal: AMZN "not in current Targets roster", so the executor's roster allowlist blocks the sale of the name being exited.
  - Also refused: stale-quote drift on eight buy legs.
  - The flag was already present before the 10-19 run ("pre-existing halt").
  - Result: **AMZN's model exit has not been carried out in the live account, and nothing has traded since 2026-10-16.**
  - Clearing the halt and fixing or regenerating the ticket are Dom's actions. This run touched neither.
- `executor_cron.py --heartbeat-check` exits 1:
  - **"execute" is stale** (last 2026-10-16), a direct result of the halt.
  - "series" is stale too, but that is the retired local job; the GitHub series is current as of 2026-10-23.
  - recon, ticket_gen and rebalance are 2026-10-23.

## Routine filings

- CRDO 8-K 5.07: annual-meeting votes (logged by the daily watch).
- ETN 8-K 8.01: FY2025 financials re-issued with the new Mobility segment (not a restatement).
- PUMP 8-K 5.02: new independent director.
- HSAI 6-K: Q3 results date 2026-11-10.
- POET 6-K: Q3 results date 2026-11-16; quarterly calls start with Q4.
- STM 6-K: weekly buyback report.
- TE 8-K 3.02: ~9.96M shares to pay the $30.0M Evervolt IP installment (minor dilution).
- KN 8-K 2.02: Q3 revenue $184.0M (+20% YoY, above guide); non-GAAP EPS $0.38; Q4 guide $180–190M.
- TXN 8-K 2.02: Q3 revenue $6.06B (+28% YoY); GAAP EPS $2.62 vs $1.48; Q4 guide $5.80–6.30B.
- NEE 8-K 2.02: Q3 adjusted EPS $1.24 (+9.7%); 8%+ EPS growth through 2032 reaffirmed; backlog 36.7 GW.
- TSLA 8-K 2.02: Q3 revenue $28.05B (−0.2%); non-GAAP EPS $0.48 vs $0.50; deliveries −2%; Optimus production started.
- DELL 8-K 5.02: General Counsel retiring 2027-02-01 (internal successor).
- LSCC 8-K 5.02: two new independent directors (board 8 → 10).
- SO 8-K 5.03: by-law amendments (special meetings, proxy access rules).
- MRVL 8-K 1.01: undrawn revolver raised $1.5B → $3B.
- UMC 6-K: Xiamen subsidiary GM changed. September insider sales include CFO Chitung Liu, 600,000 shares (insider selling is ambiguous under the rubric).
- TSM 6-K: month-end filing (cover only; logged by the daily watch).
- META / FIX / WDC: Q3 8-Ks, briefed and logged by the 2026-10-23 daily watch.

## New 13F activity

None in the window. Q3 13F-HRs are due around 2026-11-16.

## Daily watch this week

**3 of 5** weekdays ran: 2026-10-19, 10-20 and 10-23 (twice, am and pm).
**10-21 and 10-22 are missing** from `tracking/scheduled-run-log.md`, so those runs were missed. 10-22 was the −5.6% day and the WDC/FIX/BE/TTMI print day. The 10-23 run caught up on the holdings' earnings.

## Needs Dom

- **Trading halt and the AMZN exit:** investigate and clear `trading-halt.flag`, and decide how the AMZN sale gets placed. The roster allowlist refuses the sell leg of an exited name.
- **EME and VRT exits** can confirm Monday 2026-10-26. The ticket will be held.
- **Rating proposals:** nine from 2026-10-18 are still PROPOSED:
  - ANET D2/R2/M2
  - FIX M2
  - SNDK D1/R1/R2
  - MSFT M2/M3

  None changes membership. No new proposals were written this run. Candidates for Sunday's rating research: ISRG R4 (antitrust settlement), SMCI D-dims and M (the pre-announced beat), TEM D1 (data-licensing revenue).
- **EPS-YoY (rule 15) rulings:**
  - **META** +264% (from 2026-10-23, written because it is under 300%).
  - **ISRG** −25.8%, settlement-dominated, written.
  - **NEE** +95.9% GAAP vs +9.7% adjusted, written.
  - **WDC** and **SPCX** overrides are STALE, so their cells are withheld.
- **ATKR** has been delisted (acquired by Prysmian). Removing it from the Watchlist is a rule-24 cohort change (`cohort_membership.py --impact ATKR`).
- **Entry holds expiring within 10 days** (by 2026-11-03): none. The earliest is GOOGL on 2026-11-05.
- **Held ticket:** none from this run. The 2026-10-18 AMZN-exit ticket is not parked; it is the one the halted executor keeps refusing.

## Could not verify

- Consensus figures for the rule-9 >15% surprise test: no filing states consensus.
- SMCI's final Q1 numbers (preliminary only until 2026-11-03).
- The SPCX spectrum price and the CRM–Braze debt funding (both undisclosed).
- Fresh reverse-DCF inputs (run stopped; a 1-day-old file was used).
- The cause of the trading halt that existed before the 2026-10-19 run (only the 10-19 → 10-23 refusals are in the log I read).
