# Weekly News Scan — 2026-10-31

Scheduled run (rule 37), local Mac. Filing window 2026-10-23 → 2026-10-31 (8 days),
`scheduled_run.py scan-filings --scope all`: **91 filings from 194 EDGAR names, 0 lookups
failed**, 23 names not on EDGAR (foreign local lines). Every filing was read from its primary
SEC document. Items the daily watch had already logged this week (holdings' prints, AVGO, ORCL,
META's equity raise) are not repeated. Two batches were read for headlines, tables and guidance
rather than cover to cover: the long releases, and the merger agreement exhibits.

## Step 0: what I believed going in (holdings)

Not written cold before the scan: this comes from the week's daily-watch log, read at the start.

- **MU, FIX (✓✓✓):** memory pricing and data-center backlog were the two strongest lines in the model. MU has no print this week; FIX's backlog is $17.81B (8-K 2026-10-22).
- **NVDA, AVGO, ALAB, CRDO, ANET, SNDK, WDC, TSM, ASML:** demand set by hyperscaler capex; news should be about supply.
- **MSFT, META, PLTR:** AI buyers and adopters. META's cash burn and its ~$37.5B equity raise are the open question.
- **EME, VRT:** the build-out trade; both beat.
- **RDDT, LRCX, GMED:** the weak end of the roster.

**Diff vs the filings:** the demand signal strengthened again, and from outside the holdings. GE Vernova orders (+96% organic), AEP's 84 GW of contracted load, and Carrier's data-center orders (~+300%) all say the build-out is still accelerating. The −7.6% on 10-30 was not caused by any filing I read; I could not establish the cause.

## ⚠️ Material events

| Ticker | Filing | What happened |
|---|---|---|
| ⚠️ **EQT / RRC** | 8-K 2026-10-26 (Ex.99.1) | **EQT buying Range Resources, all stock:** 0.987 EQT per RRC share, ~73%/27% ownership, pro forma EV >$50B, close expected Q1 2027. Termination fees RRC $423M / EQT $1,148M. Two watchlist names become one, which is a rule-24 cohort change at close. |
| ⚠️ **GEV** | 8-K 2026-10-28 (Ex.99) | Q3 revenue $12.64B (+27%), **orders $29.3B (+96% organic)**, backlog $197B. FY guide raised: revenue $46.5–47.5B, FCF $16–17B (from $11.5–12.5B). Gas backlog + slots 122 GW. Buyback doubled to $20B. Agreed **$9.0B Trench Group** acquisition, close late 2027. |
| ⚠️ **AEP** | 8-K 2026-10-28 (Ex.99.1) | **15 GW of new load commitments signed in Q3; 84 GW contracted by 2031.** $100B five-year capex. New EPS guides: 2027 $6.75–7.05, 2028 $7.40–7.70. |
| ⚠️ **INTC** | 8-K 2026-10-29 (Ex.99.1) | Q3 revenue $16.5B (+21%), DCAI +78%. **Q4 guide $15–16B with GAAP GM 37.1% vs 43.0%**, about −590bps by my subtraction. PC slowdown through 1H27. **Completed a $23B public equity offering.** |
| ⚠️ **SEI** | 8-K 2026-10-29 (Ex.99.1) | **~900 MW power deal** with an unnamed investment-grade existing customer: 15 years plus a 15-year option, deployments 1H27 through 2028. |
| ⚠️ **SYM** | 8-K 2026-10-29 (Ex.99.1) | **Walmart ~$6B initial commitment** across 25 US distribution centers, including $125M R&D. Backlog up to +$6.92B. |
| ⚠️ **SPCX** | 8-K 2026-10-26 (Item 8.01) | **Binding Apollo commitment for a ~$40B GPU master finance lease**, ~5–5.25 years, close by year-end; fixed rate not yet set. Entry hold runs to 2026-11-10. |
| ⚠️ **CARR** | 8-K 2026-10-29 (Ex.99) | Q3 sales $6.26B (+12%), adj EPS $0.87. GAAP EPS $(3.16) after a **$3.1B goodwill impairment** (Climate Solutions Europe). Data-center orders ~+300%. |
| ⚠️ **XEL** | 8-Ks 2026-10-29/30 | FY26 $4.10–4.16; first 2027 guide $4.48–4.62. **New $6.0B at-the-market equity program.** |
| ⚠️ **PWR** | 8-K 2026-10-29 (Ex.99.1) | Revenue $12.01B vs $7.63B, adj EPS $6.06 vs $3.33, backlog $63.7B. Guide raised, but the figures are not in the exhibit. |
| ⚠️ **TT** | 8-K 2026-10-29 (Ex.99.1) | Revenue +18%, backlog $12.5B (+73%). FY growth raised to ~13.5%; EPS only reaffirmed on supply and inflation headwinds. |
| ⚠️ **JCI** | 8-K 2026-10-27 (Ex.99.1) | FQ4 orders +44% organic, backlog $23.0B. Initiated FY27 adj EPS $6.15–6.30. |
| ⚠️ **HUBB / NXT / EQIX / DLR / CDNS / FLEX / FTNT / NOW** | 8-Ks 2026-10-26 → 10-29 | Guides raised. DLR record bookings $855M; EQIX record $533M, third raise; NOW's AI ACV target to $1.7B. NXT's gross margin fell to 31.1% from 35.9%. |
| ⚠️ **MTZ** | 8-K 2026-10-29 (Ex.99.1) | Revenue +30%, but pipeline permitting delays hit margins and comms customers deferred H2 spend. GAAP EPS $1.89 vs adj $2.96. |
| ⚠️ **MPWR** | 8-K 2026-10-29 (Ex.99.1, 99.2) | Enterprise Data $506.7M (+164.6%). **New CFO Tony Balow.** |
| ⚠️ **ACLS** | 8-K 2026-10-27 (Ex.99.1) | **New CFO Jeroen Delsman** from Nov 12. |
| ⚠️ **CCJ** | 6-K 2026-10-30 (Ex.99.1, 99.2) | Adj EPS C$0.00 vs C$0.07; Key Lake extended outage. Non-binding US$120B Korea framework, six AP1000s. |
| ⚠️ **AMAT** | 8-K 2026-10-26 (Ex.99.1) | Stake in Besi up to ~20%; HSR pending. |
| ⚠️ **PUMP / GNRC / UMC / STM / ASX / GLW / LEU / HIVE** | Various | PUMP ~510 MW contracted. GNRC's Amazon deal is $2.4B across 2027–28 (previously disclosed). UMC extra ~US$3.2B capex and a US$1.8B convert. STM says demand is above supply. GLW has four multibillion customer deals. LEU shipped its first new centrifuge. HIVE's BUZZ took a ~$129M GPU facility at 9.0%. |

## 📊 Earnings refreshed

The Last Updated test could not be used: PR #230 stamped every row 2026-10-30. Instead I dry-ran
all 49 reporters and wrote **48**. **D was left out on purpose:** right after its print Yahoo
returned no debt or enterprise value, which would have blanked two good cells. Its row is
unchanged. Then ran `momentum_50dma.py` (214/217), `refresh_reverse_dcf.py` (136 with EV/FCF) and
`recalc_watchlist.py --sync`.

Scores against `main` before this run (moves of 0.5 or more, or a tier change):

| Ticker | Before | After | Tier | Why |
|---|---|---|---|---|
| ⚠️ **MTZ** | 61.94 | **55.86** | ✓ | **Largest move.** EPS YoY 51.7 → −6.3% on GAAP; adj EPS $2.96 vs GAAP $1.89, so a ruling is worth considering. Rev YoY 23.4 → 29.9%. |
| XEL | 57.77 | 55.29 | ✓ | Two blank ratios refilled by Yahoo. |
| ENTG | 65.29 | 64.48 | ✓ | Inputs. |
| IRM | 58.37 | 57.65 | ✓ | Not a reporter; percentile peers moved. |
| HOOD | 67.24 | 66.74 | ✓ | Rev YoY now 11.8%. EPS override is STALE. |
| MSFT | 80.79 | 80.29 | ✓✓ | ND/EBITDA −0.04 → 0.34. |
| ⚠️ **TT** | 69.94 | **70.25** | ✓ → **✓✓** | Crossed 70 by 0.25. |
| KLAC | 70.55 | 71.09 | ✓✓ | Inputs. |
| JCI | 57.83 | 58.56 | ✓ | Ratios only; EPS not yet on the new quarter. |
| NVT | 73.16 | 74.21 | ✓✓ | Sep quarter now in Yahoo. Rank 21 → 16. |
| ⚠️ **INTC** | 54.65 | **55.80** | ? → **✓** | Crossed 55 by 0.80, on the print before the guide cut reaches estimates. |
| SNDK | 82.35 | 83.79 | ✓✓ | Sep quarter in Yahoo. Rank 5 → 3. |

- **📊 Rule-9 flags:** SNDK and STX (both already flagged by the daily watch). The >15%-vs-consensus test cannot be run across this list: no filing states consensus. No reported gross-margin move this week exceeded 500bps in the batch reads; NXT was closest at −480bps. FORM was +400bps.
- **TTM vs MRQ:** SNDK MRQ GM 85.0% vs TTM 79.95% (8-K 2026-10-29).
- **Yahoo still behind on EPS:** JCI's cell (−42.9%) and DLR's (−56.1%) do not match this week's releases (JCI $1.60 vs $0.42; DLR $0.48 vs $0.15). Those cells will move on a later refresh.

## 💼 Portfolio pipeline

- **Model event, 2026-10-31: RDDT and LRCX exited.** Both clocks ran from 2026-10-30; RDDT is tradable rank 21, LRCX 24. The book goes to **17 names at equal weight, 5.9% each** (was 5.26%). No entries.
- **New exit clock: GMED**, tradable rank 19, since 2026-10-31. It can confirm on the next real run, normally **Monday 2026-11-02 at the daily watch**.
- **One slip from a clock: META**, tradable rank 18 at 73.54, 0.12 above GMED. Friday's rule-15 ruling took it down from 79.62.
- **Next in line:** NVT rank 16, STX 17. An entry needs rank 15; VRT holds it at 74.50, with NVT 0.29 behind.
- **Entries deferred:** none. No name at rank 15 or better is outside the book.
- **Held ticket:** `held-ticket-2026-10-31-membership.json`, 10 orders: 3 sells (AMZN, RDDT, GMED) and 7 buys (ALAB, ANET, ASML, CRDO, FIX, META, SNDK), 9 dust-suppressed, buys scaled to 95.3% to fit cash. Expires 2026-11-03.
- **Concentration:** Layer 06 is 29% of the portfolio (no layer cap active).
- **Site refresh:** `daily-refresh.yml` failed its last four scheduled runs. I read the latest log (2026-10-31 13:44Z): the rule-25 gate saw the pending RDDT/LRCX exits, which this run's model event clears. The series itself is current to 2026-10-30.
- **Weekly mark** (`tracking/performance-series.json`, closes 2026-10-23 → 2026-10-30):

| | Week | Since inception (2026-05-26) |
|---|---|---|
| **Model** | **−2.6%** | −8.0% |
| SMH | −0.9% | −13.2% |
| QQQ | −2.0% | −5.2% |
| SPY | −0.6% | +1.2% |
| EW universe | −2.2% | −2.5% |

  Friday did it: the model fell −7.6% on 10-30, SMH −7.0%, QQQ −3.5%. Monday to Wednesday had been +1.8%, +3.0% and +2.2%.

## 🩸 Capitulation flags

None fired, so no forecasts were logged.
- RDDT: P/S 4.36 is at the **0.2th percentile** of its own 3-year range, but revenue YoY of 53.0% is below its 3-year median of 67.9%. That is one leg of the setup, and the second failed.
- LRCX: 72.9th percentile; revenue YoY 54.4% vs 22.9%.
- GMED: 22.7th percentile; revenue YoY 5.9% vs 26.4%.

## 🔬 Rating integrity

`audit_rating_integrity.py --summary`: 214 rated names, **0 ungated**, **72 stale (>90 days)**, up from 68 last week.

## 🎯 Calibration

`resolve_forecasts.py`: 0 resolved, 0 needs_review.

## 🔴 Live pipeline (heartbeat only; reconciliation skipped per rule 37)

- `executor_cron.py --heartbeat-check` exits 1: **"execute" is stale** (last 2026-10-16) and "series" is the retired local job. recon, ticket_gen and rebalance are 2026-10-30.
- No `trading-halt.flag` is present. The last one was cleared and archived 2026-10-30.
- **Nothing has traded in the live account since 2026-10-16.** That makes Monday's first-of-month rebalance the first trade in over two weeks.

## Routine filings

- TER: Q3 revenue $1,306M (+70% YoY, below Q2); Q4 $1,250–1,350M.
- KLAC: FQ1 revenue $4.136B; Dec guide $4.7B ±$0.2B.
- ENTG: Q3 sales $1,006M; Q4 $1,025–1,055M.
- FORM: Q3 revenue $280.5M (+38.4%); Q4 $285M ±$10M.
- UCTT: Q3 revenue $759M (+49%); Q4 $800–860M.
- NXPI: Q3 revenue $3,786M (+19%); $5B new buyback.
- ALGM: Q3 sales $277M (+29%).
- TEL: FQ4 sales $5.3B (+12%), orders $6.1B (+29%).
- AR: Q3 EPS $1.19 vs $0.24; 4.2 Bcfe/d.
- D: Q3 operating EPS $1.28 vs $1.06, top half of the $3.45–3.69 guide; the NextEra merger (logged 2026-05-18) still pending.
- MBLY: 8-K/A, EVP Nehushtan moves to a 20% scope.
- HOOD, NOW: 8-K/As (non-GAAP tax presentation; XBRL only).
- LSCC: committee appointments. MOD: severance terms, no departures.
- TTMI: $100M buyback completed at $86.31; new $100M authorization.
- DLR: legal opinion for Teraco resale shares. TE: resale registration, 13.44M shares.
- SSII: telesurgery demos. STM: weekly buyback report; CTO and CSO appointments from 2027-01-01. ASX: release version of results.
- MRVL, RCAT, TEM, UMAC, WDAY, WULF, UMC (10-23 items): in last week's scan.

## New 13F activity

None in the window. Situational Awareness LP's latest filings on EDGAR are a Schedule 13D/A and Form 4 from 2026-09-17, outside the window. Q3 13F-HRs are due around 2026-11-16.

## Daily watch this week

**5 of 5** weekdays ran: 2026-10-26, 10-27, 10-28, 10-29 and 10-30.

## Needs Dom

- **Monday 2026-11-02 rebalance:** the first-trading-day executor run trades to the Targets on its own, regardless of held tickets (rule 37). It will carry out the RDDT and AMZN exits, plus LRCX if the account holds it. GMED cannot be bought while its clock runs: ticket generation excludes exit-clock names from buys (`generate_trade_ticket.py:83`, read, not run).
- **Held ticket:** `held-ticket-2026-10-31-membership.json`. Release is in an attended session only.
- **Rating proposals:** 14 still PROPOSED, none changing membership on the numbers when written:
  - 2026-10-18: ANET D2/R2/M2, FIX M2, SNDK D1/R1/R2, MSFT M2/M3
  - 2026-10-27: CRDO M2, GOOGL M2, NVDA M2/M1, ALAB R2

  No new proposals this run. Worth a look on Sunday: SEI and SYM D-dims, INTC after the guide, AVGO R3 (the ~$43B backstop).
- **EPS-YoY (rule 15) rulings:**
  - Overrides now STALE, cells withheld at the old ruling: **AMZN** (fresh −2.4%), **GOOGL** (−24.3%), **HOOD** (−15.8%), **NOW** (−44.8%), **TER** (+186.4%).
  - Withheld at ≥300%: **SNDK** +7133%, **AR** +382%, **FORM** +372%.
  - One-off candidates: **MTZ** (written −6.3%), **CARR** ($3.1B impairment; fetch empty, −15.2% kept), **XEL** (prior-year wildfire charge), **JCI**, **DLR**.
- **ATKR** is still on the Watchlist after its buyout; removing it is your rule-24 call. EQT/RRC becomes the same question at close.
- **Entry holds expiring within 10 days:** **GOOGL 2026-11-05**, **SPCX 2026-11-10**. Neither name is near entry. APP (11-15) and INTU (11-21) are outside the window.

## Could not verify

- The cause of the 10-30 selloff.
- Consensus figures for the rule-9 >15% surprise test.
- Which reporters' EPS cells Yahoo still has on the June quarter, beyond JCI and DLR.
- PWR's new guide figures (on its IR site, not in the exhibit).
- Why LRCX has no leg in the held ticket. It is not among the sells; I did not reconcile the account.
- Fresh values for D (held back, see above).
