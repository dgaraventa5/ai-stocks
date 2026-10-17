# Weekly News Scan — 2026-10-17

Scheduled run (rule 37), local Mac. Filing window 2026-10-09 → 2026-10-17 (8 days),
`scheduled_run.py scan-filings --scope all`: **39 filings from 194 EDGAR names, 0 lookups
failed**, 23 names not on EDGAR (foreign local lines). Every filing was read from its primary
SEC document (exhibits included); GFS's exhibit was pulled separately.

## Step 0: what I believed going in (holdings, all ✓✓)

There are no ✓✓✓ names, so no full `/refresh-context` was triggered.

- **NVDA, AVGO, ALAB, CRDO, ANET, MU, SNDK, WDC:** the AI-silicon and connectivity core, where demand is set by hyperscaler capex. Expected news: supply and allocation, not demand.
- **TSM:** leading-edge monopoly; 2nm ramping, gross margin mid-60s.
  - *Diff:* Q3 confirmed it (GM 66.4%, Q4 guide US$52.3–54.3B, 6-K 2026-10-15). No model change.
- **MSFT, META, AMZN, PLTR, RDDT:** AI buyers and adopters whose scores ride on the capex and adoption narrative. AMZN was already sliding on rank.
- **FIX, EME, VRT:** the data-center build-out trade, where backlog is the signal.
- **GMED:** a robotics name that is mostly a med-tech compounder.

**Diff vs this week's filings:** only TSM filed among holdings, and the Q3 print matched the model. No holding had a thesis-shifting filing. The week's damage was price, not news (see the weekly mark).

## ⚠️ Material events

| Ticker | Filing | What happened |
|---|---|---|
| ⚠️ **ASML** | 6-K 2026-10-14 (Ex. 99.2) | Q3 net sales €11.66B (+55% YoY vs €7.52B), GM 57.5%, op margin 44.4%, net income €4.96B, EPS €12.95. Q4 guide €14.2–15.2B at ~57% GM; FY26 €44–45B at ~56%. Bookings are not in the presentation (the 99.1 press release was not read). |
| ⚠️ **CIFR** | 8-Ks 2026-10-13/14/16 | Barber Lake AI-lab lease amended to 20 yrs / $9.1B (+$5.2B). Contracted HPC revenue $16.6B (+46% QoQ); 700 MW gross contracted HPC; new "Apollo" site up to 900 MW (2028). Issued $850M of 0.00% converts due 2032 (conversion ~$15.31, capped call to $28.35), plus ~40.7M shares in a 2030-note exchange. |
| ⚠️ **FLEX** | 8-Ks 2026-10-13/14 | Closed the EPC Power acquisition for $4.4B cash, funded by $3.3B + $1.1B 364-day loans due 2027-10-13. It goes into the Axiom Solutions spin-off (1Q 2027). Amazon's warrant was amended to carry into the spin-off. |
| ⚠️ **FORM** | 8-K 2026-10-13 | Teradyne will buy 2,234,887 shares for ~$300M (private placement, closing Q4 2026), plus a test collaboration across HPC, advanced packaging, HBM and silicon photonics. |
| ⚠️ **CAMT** | 6-Ks 2026-10-14 | Q3 pre-announced at $160–161M (+27% YoY, above guide). Q4 guide ~$180M; first 2027 view >$800M; >$800M of orders in 2026. New ~3-yr model: ~$1.2B revenue at a 34–36% operating margin. |
| ⚠️ **SMCI** | 8-K 2026-10-15 | CFO David Weigand "ceased serving"; Mark Long (WDC CFO 2016–19) is CFO effective 2026-10-14. No reason given, at a company with a control-problem history. |
| ⚠️ **TTMI** | 8-K 2026-10-13 | $400M brownfield AI-PCB capacity plan at four China sites and Penang, on top of the $1.2B 2025–29 plan. Raises the China share of capacity. |
| ⚠️ **TSEM** | 6-K 2026-10-13 | Expanded multi-year SiGe deal: Semtech pays to secure dedicated capacity in US, Israel and Japan fabs for AI optical and copper interconnects. No $ value disclosed. |
| ⚠️ **GFS** | 6-K 2026-10-14 (Ex. 99.1) | Chosen to operate two new Malta, NY fabs under a US-Japan initiative with up to $21B of Japanese funding. The first ~$10B fab comes online in 2029 at ~900k 300mm wafers/yr. |
| ⚠️ **WDAY** | 8-K 2026-10-13 | Agreed to acquire ConductorOne, an agentic identity platform for people and AI agents. Close expected in fiscal Q4 FY27; price not disclosed. |
| ⚠️ **MDB** | 8-K 2026-10-15 | Interim CEO Ittycheria's terms ($15M RSUs, committed through ≥2028-04-01) and a $10M retention grant for CFO Berry. The permanent CEO search is still open. |
| ⚠️ **DLR** | 8-K 2026-10-09 | €1.0B of 5.125% green notes due 2036 at 99.289% (net ~€985.8M). |
| ⚠️ **SSII** | 8-Ks 2026-10-13 | FDA 510(k) answer filed for SSi Mantra; review expected to end Q1 2027. Sold a $21.0M secured convertible for $20M (8.75%, converts at 95% of market): dilutive and expensive. |
| **ONDS** | 8-K 2026-10-13 | Formed Regna AI with Palantir (sovereign defense AI on Palantir AIP). No financial terms; narrative until customers appear. |
| **PLUG** | 8-K 2026-10-15 (prelim) | Q3 revenue growth >10% YoY; FY26 guide ~15–16% reaffirmed; Q3 cash use ~$28M, cash ~$134M. Full results 2026-11-09. |
| **STM** | 6-K 2026-10-13 | CEO Chéry to be proposed for a one-year reappointment at the 2027 AGM. A short renewal, which hints at succession planning. |

## 📊 Earnings refreshed

Refreshed with `refresh_objective_inputs.py`: EQT, RRC, PLUG, ASML. These four were last updated 2026-10-11 and filed after that. TSM was already refreshed by the 2026-10-15 daily watch (82.25 → 82.38).

| Ticker | Before | After | Tier | Note |
|---|---|---|---|---|
| ⚠️📊 **ASML** | 67.60 | **71.82** | ✓ → **✓✓** | Rev YoY 21.3 → 55.2%, EPS YoY 27.4 → 133.5% (operational: Q3 EPS €12.95 vs €5.49). GM 52.7 → 54.3%. Rank ~46 → ~26, not near entry (15). |
| EQT | 60.51 | 60.51 | ✓ | Item 2.02 was preliminary hedge figures only ($100M derivative gain); full Q3 results are not out. The change is price-driven. |
| RRC | 60.18 | 59.69 | ✓ | Same: preliminary derivatives only ($58.1M gain). |
| PLUG | 33.62 | 34.18 | ✗ | Preliminary only. The EPS YoY blank was preserved (prior ruling). |

- **📊 flag:** ASML. Revenue +55% YoY and an implied Q4 guide well above Q3. The >15% surprise test cannot be checked because consensus is not in the filing. A full `/earnings-update ASML` is worth doing.
- **TTM vs MRQ (rule 9):** ASML's MRQ gross margin is 57.5% vs a TTM of 54.3%, and the MRQ op margin is 44.4%. TTM understates the current run-rate.
- Then ran `momentum_50dma.py` (215/217 written), `refresh_reverse_dcf.py` (131 with EV/FCF) and `recalc_watchlist.py --sync`.
- **Other moves ≥0.5 pt (mostly the 50DMA refresh):** WDC 73.31 → 73.91, VRT 72.75 → 73.25, NVT +0.5, SNPS +0.5, ALAB +0.5, MU +0.5, EME 73.67 → 73.17, NEE −0.5, APLD 55.25 → 54.75 (✓ → ?).

## 💼 Portfolio pipeline

- **Model:** frozen. Membership and tiers are unchanged, so nothing was written and **no ticket was generated**. `refresh_targets.py --check` is green.
- **AMZN exit clock** (running since 2026-10-11; live rank 22 > exit rank 18): it is seam-damped until **2026-10-18**. It can confirm on the first real `refresh_targets` run after that, which is the Monday 2026-10-19 daily watch, if AMZN is still below rank 18. That would be a model event with a ticket, which the daily watch holds.
- **APP:** qualifies to enter (rank 15, 73.74) but is **deferred** by its entry hold (expires 2026-11-15).
- **EME** fell 73.67 → 73.17. That puts it at about tradable rank 18, right at the exit line: one more slip starts a clock.
- **Concentration:** Layer 06 is 28% of the portfolio (no layer cap active).
- **Weekly mark** (`tracking/performance-series.json`, closes 2026-10-09 → 2026-10-16):

| | Week | Since inception |
|---|---|---|
| **Model** | **−10.4%** | −1.5% |
| SMH | −10.5% | −10.4% |
| QQQ | −5.5% | −2.6% |
| SPY | −2.0% | +2.2% |
| EW universe | −8.9% | +0.5% |

  The losses were concentrated on 10-14 (−4.1%) and 10-16 (−3.8%), alongside SMH. That is an AI-semis drawdown, not a stock-specific event.

## 🩸 Capitulation flags

AMZN (exit pending) is **clean**: P/S 3.48 is at the 57.6th percentile of its own 3-year range, and revenue YoY is 19.6% vs a 3-year median of 13.0%. No forecast was logged.

## 🔬 Rating integrity

`audit_rating_integrity.py --summary`: 214 rated names, **0 ungated**, **68 stale (>90 days)**. The Sunday rating-research rotation works through these. No gate violation in any holding.

## 🎯 Calibration

**14 Phase-1 `REL_STRENGTH_1Q` forecasts resolved** (created 2026-06-26, due 2026-09-25). They had been sitting unresolved for three weeks because no weekly scan ran between 2026-09-18 and today. The result is **7 of 14** outperformed their layer cohort over 63 trading days.

- **Hits (7):** TSM +4.5% vs −13.4%; NVDA +17.0% vs −3.2%; META +36.7% vs −18.2%; ANET +31.1% vs −11.7%; MSFT +38.7% vs −18.3%; GOOGL +2.0% vs −16.3%; FIX −10.5% vs −12.2%.
- **Misses (7):** SNDK −15.0% vs −1.6%; CRDO −11.4% vs −7.8%; MU −4.4% vs −2.1%; AVGO −3.2% vs −2.2%; ALAB −6.9% vs −2.0%; APP −34.9% vs +25.6%; WDC −22.1% vs +31.5%.

0 needs_review and 0 void. The cited evidence string for each is in `tracking/forecasts.jsonl`. A Brier and reliability read waits for `/rescore-quarterly` (`calibration_report.py`).

## 🔴 Live pipeline (heartbeat only; reconciliation skipped per rule 37)

- `executor_cron.py --heartbeat-check` exits 1 with **"series" stale** (last 2026-09-22). That is the retired local series job. The performance series itself is current: as of 2026-10-16, refreshed on GitHub (`series_freshness.py`, PR #168). **This is not an outage.** The heartbeat check still expects a job that moved to GitHub, so it will keep reporting stale until it is updated.
- Today's heartbeat entries for `recon`, `execute`, `ticket_gen` and `rebalance` are all 2026-10-16.

## Routine filings

- CSCO 8-K 5.02: new independent director (Girish Rishi).
- XEL 8-K 8.01: NSP-Minnesota proposes a 2027–28 base-rate freeze instead of a rate case.
- ASX 6-K: September revenue NT$88.1B (+45.5% YoY); Q3 +44.8% YoY.
- EXE 8-K 5.02: new Chief Accounting Officer.
- LSCC 8-K/A: AMI acquisition financials and pro formas (~$918M term debt; deal closed in July).
- STM 6-K: weekly buyback report.
- TSEM 6-Ks: EGM proxy on exec pay; Q3 results date 2026-11-02.
- UMC 6-K: declined to comment on a press revenue rumor; Q3 call 2026-10-28.
- KLIC 8-K 5.02: FY27 incentive plan metrics changed.
- ENTG 8-K: $0.10 dividend.
- RIOT 8-K 1.01: custody moved to BitGo.
- LMND 8-K/A: incoming CFO pay terms (handover disclosed in July).
- CRDO 8-K 5.07: annual meeting votes.
- ETN 8-K 8.01: segment re-presentation (new Mobility segment; not a restatement).
- TSM 6-K: Q3 results, already logged by the daily watch.

## New 13F activity

None in the window. The latest 13F-HR from each tracked fund (Berkshire, Baillie Gifford, Tiger, Coatue, Whale Rock, Lone Pine) is from 2026-08-06/14. Q3 filings are due around 2026-11-16.

## Daily watch this week

**5 of 5** weekday runs happened (2026-10-12 through 10-16, `tracking/scheduled-run-log.md`).

## Needs Dom

- **Rating proposals:** none open, and none written this run. Candidates for the Sunday rating-research pass:
  - TTMI R2 (China capacity).
  - SMCI (unexplained CFO exit).
  - CIFR D-dims (contracted revenue +46%).
  - WDAY D5/R5 (agentic-identity acquisition).
- **CIFR `capacity-mw.json`:** the deck shows 700 MW gross contracted HPC and 907 MW operating + contracted. The rule-13 MW denominator needs a human refresh (a scheduled run may not edit it).
- **EPS rulings:** none needed. ASML's +133.5% is operational.
- **Entry holds expiring within 10 days:** none. The earliest is GOOGL on 2026-11-05.
- **Held ticket:** none this run.
- **Heartbeat check:** retire or repoint the stale "series" entry.

## Could not verify

- ASML Q3 bookings (the 99.1 press release text was not captured).
- WDAY's deal price and the TSEM–Semtech dollar terms (both undisclosed).
- CIFR's use of proceeds.
- Consensus figures for the rule-9 >15% surprise test (no consensus source in the filings).
