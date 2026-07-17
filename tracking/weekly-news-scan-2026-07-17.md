# Weekly News Scan — 2026-07-17

**Scope:** 173 watchlist tickers. Scan window: 2026-07-10 – 2026-07-17.

## Execution note (network + search-budget constraints)

SEC EDGAR (`data.sec.gov`, `www.sec.gov`) and Yahoo Finance are still 403-blocked from this cloud session's egress proxy (`curl` CONNECT tunnel failures confirmed directly, and again via a live `momentum_50dma.py NVDA` test — reverted, no data corrupted). Substituted `WebSearch`, per the `web_scan.py` fallback (date-verified, source-filtered, full-watchlist query plan) established in the 2026-07-10 scan retro.

**Coverage gap — WebSearch session budget exhausted.** Unlike the last two scans, this week attempted full 173-ticker coverage (12 holdings + PLTR/DDOG/CRM at 3 queries each, remaining ~158 tail names at 1 query each) via 11 parallel research agents. The session's shared WebSearch call budget (200 calls) was exhausted partway through the tail sweep. **54 of 173 tickers were never queried** — flagging per rule 3 rather than presenting this as full coverage:

- Not searched at all: **STM, STX, SWKS, TE, TEL, TEM, TLN, TOELY, TSEM, TSLA, TT, TTMI, TXN, UCTT, UEC, UMC, WDAY, WULF, WYFI, XEL, ZS** (21), **PPL, PSIX, PUMP, PWR, QCOM, RIOT, RMBS, RRC, SBGSY, SEI, SHAZ, SMCI, SMR, SNOW, SNPS** (15), **HUBB, HUT, INTC, INTU, IREN, IRM, JCI, KEEL, KEYS** (9), **NNE, NOW, NRG, NTAP, NVT, NVTS, NXPI, NXT, OKLO** (9)
- All 12 portfolio holdings, PLTR/DDOG/CRM, and 119 other tail names were fully searched (some tail names got 16-25 of 25 planned queries before their agent's slice of the budget ran out — those are reported as genuinely "nothing found," not gaps).

**Recommendation for Dom:** the 200-call session budget is a hard constraint for full-watchlist coverage at this query density; either the weekly scan needs a higher `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, a lower query-per-ticker density for the tail, or acceptance that full sweeps happen periodically rather than every week (as in the prior two scans, which scoped to holdings + SaaS-watch only). The 54 un-searched tickers should be prioritized in next week's scan.

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

Same 12 holdings as the last three scans (book unchanged since the 7/2 rebalance, membership-wise): NVDA, TSM, MU, CRDO, META, ANET, AVGO, AMZN, SNDK, MSFT, GOOGL, FIX.

Going into this scan: NVDA (dominant AI-accelerator vendor, Blackwell ramp) was believed comfortably ✓✓✓; TSM (sole leading-edge foundry) and MU (HBM/DRAM beneficiary, ~$100B SCA backlog) were believed stable ✓✓; the four hyperscalers (META/AMZN/MSFT/GOOGL) were believed to be in a quiet pre-earnings period; AVGO/CRDO/ANET (custom silicon/networking/optical) were believed unchanged since their respective CFO-transition/insider-sale news; SNDK was flagged as a name whose ~800% YTD run warrants an expectations check; FIX was believed unchanged post its 7/1 leadership transition.

**What was wrong, and why it matters:** a full objective-input refresh ran **2026-07-16** (commit `78a8b3d`, "after AI selloff" — outside this scan, run directly by Dom/a prior session) across all 173 names. It **crossed NVDA's tier**: 85.1 (✓✓✓) → 84.39 (✓✓), triggering a freeze-safe rebalance (membership unchanged, NVDA target 12.0% → 11.76%). MU also drifted materially within-tier (84.8 → 80.64). Both moves are **price-driven** (post-selloff Value/cohort-percentile inputs), not fundamentals — MU's FQ3 numbers were separately re-verified as OPERATIONAL (not one-off-driven) on 2026-07-16 per the rule-15 pass. This is exactly the kind of silent drift Step 0 is meant to catch: last week's scan reported NVDA as a ✓✓✓ holding; it no longer is, and that happened without an intervening scan.

---

## ⚠️ Material Events (7/10 – 7/17)

### Portfolio holdings

1. **TSM — Q2 2026 earnings (2026-07-16, 6-K) — MATERIAL, triggers rule-9** 📊
   Record quarter: $40.20B revenue, net income +77.4% YoY / +23.4% QoQ (5th consecutive record quarter), HPC platform = 66% of revenue. Raised FY2026 capex guidance to $60–64B. Announced an **additional $100B Arizona investment** (total Arizona commitment now $265B) for 2nm logic fabs + advanced packaging. Delayed June monthly-revenue 6-K also landed (7/13): NT$442.68B, +67.9% YoY.
   Sources: [CNBC](https://www.cnbc.com/2026/07/16/tsmc-second-quarter-profit-.html), [SEC 6-K](https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000451/a2q26e_withguidancexfinal.htm)

2. **AVGO — ITC institutes second Section 337 investigation (2026-07-16)**
   US ITC voted to open a second investigation into Samsung's HBM/DDR5 memory products (Netlist patent complaint, USPN 12,646,537 / 12,650,937), naming **Google, Nvidia, Broadcom, and Super Micro** as co-respondents. Supply-chain/IP legal exposure to watch — no ruling yet, not a finding against AVGO specifically.
   Source: [PRNewswire](https://www.prnewswire.com/news-releases/us-international-trade-commission-votes-to-institute-second-investigation-into-samsung-302827022.html)

3. **AMZN — AWS SVP departure + Trainium external sales (2026-07-15)**
   AWS SVP Dave Brown (~19 years at Amazon) to depart. Separately, Amazon began selling its custom Trainium AI chips **directly to external companies beyond AWS** — first direct competition with Nvidia's merchant-silicon business. Relevant to AMZN's AI-Thesis moat/position dimensions.
   Sources: [GuruFocus](https://www.gurufocus.com/news/8961494/amazon-amzn-aws-executive-dave-brown-to-depart-after-nearly-19-years), [SahmCapital](https://www.sahmcapital.com/news/content/amazon-amzn-starts-selling-trainium-ai-chips-beyond-aws-and-into-rival-turf-2026-07-15)

4. **GOOGL — EU DMA binding specification orders (2026-07-16)**
   EU Commission ordered Google to give rival AI assistants system-level Android access (by July 2027) and share Search ranking/click/query data with competitors (by Jan 2027) — a new regulatory remedy beyond the already-final €4.1B Android fine, touching the AI-assistant/Search moat directly.
   Source: [SiliconANGLE](https://siliconangle.com/2026/07/16/eu-orders-google-share-search-data-rivals-broaden-android-feature-access/)

5. **WDC — Kioxia merger talks reportedly reopened (2026-07-15, unconfirmed)**
   Media reports (not company-confirmed, no 8-K) that Western Digital reopened NAND merger talks with Kioxia; WDC shares fell ~9% intraday on the report. WDC is not a current portfolio holding (exited 2026-06-26) but remains watchlist-tracked.
   Sources: [GuruFocus](https://www.gurufocus.com/news/8960543/western-digital-wdc-reopens-merger-talks-with-kioxia), [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/western-digital-wdc-reopens-kioxia-151411891.html)

6. **MU — automotive SCA agreements completed (2026-07-16)**
   Completed Strategic Customer Agreements with Tier-1 automotive suppliers/ecosystem partners, continuing the auto-diversification thread (GM 7/1, Ford 7/6). Separately, stock fell 6.96% on 7/15 amid a reported Michael Burry short-position headline + SK Hynix's Nasdaq debut — the Burry report is unverified against a primary filing.
   Source: [GlobeNewswire](https://www.globenewswire.com/news-release/2026/07/16/3328495/14450/en/Micron-Strengthens-Automotive-Ecosystem-Supply-Through-Strategic-Customer-Agreements.html)

7. **NVDA — Japan ecosystem expansion (2026-07-15/16)**
   Japan government (METI)/Noetra Corp. launched a Vera Rubin "AI factory" (13,750 Vera CPUs / 27,500 Rubin GPUs, 140MW) as national AI infrastructure ("FRONTia Project"); Japan robotics/manufacturing leaders (FANUC, Fujitsu, Honda R&D, Kawasaki, Hitachi, Sony) joined the Cosmos Coalition; Japanese enterprises building on NVIDIA Nemotron open models. Demand-diversification/ecosystem signal, not a customer-concentration change. Note: the previously-flagged $500B US-investment report remains **unconfirmed/stale** — no new July development found beyond the pre-existing 2025-origin 4-year plan.
   Source: [GlobeNewswire](https://www.globenewswire.com/news-release/2026/07/16/3328258/0/en/japan-government-industrial-leaders-and-nvidia-launch-the-world-s-first-national-ai-infrastructure.html)

8. **SNDK — Meta NAND deal still unconfirmed; large stock move flagged unverified**
   The 7/9 Reuters/Meta-memo report of a SanDisk NAND supply deal remains **unconfirmed by either company** as of 2026-07-17 — no 8-K located, SanDisk declined comment. Separately, headlines report the stock fell ~15% intraday 7/15; the underlying cause could not be confirmed this pass — flagged for direct follow-up next scan given the size of the move.
   Source: [Blocks & Files](https://www.blocksandfiles.com/flash/2026/07/13/sandisk-sets-up-flash-chip-supply-agreement-with-meta/5270489)

9. **MSFT — securities-fraud class-action deadline notices (7/13–7/17)**
   Multiple plaintiff-firm deadline alerts (Aug 11, 2026 lead-plaintiff deadline) tied to the already-disclosed Jan 2026 Azure capacity-guidance miss + Copilot-functionality allegations — no new underlying misconduct, just solicitation/deadline notices. Separately confirms the 7/6 layoffs (4,800 jobs, 2.1% of workforce, concentrated in Xbox) came in below the previously-reported 5,000–9,000 rumor range.

### Layer 1 (Power) — AI-power-demand names, non-holdings

10. **VST — cleared ~10,924 MW in PJM's 2028/2029 capacity auction (2026-07-14)**, weighted-average clearing price $325/MW-day across 7 zones.
11. **CEG — all Constellation PJM plants cleared the same auction (2026-07-14)**: 18,875 MW total (COMED 10,200, EMAAC 6,550, MAAC 1,725).
    Both are the AI-power-demand thesis playing out in real capacity-market pricing — a genuinely bullish, quantifiable data point for the Layer-1/Layer-9 power-constraint thesis.

### Layer 9 (Bitcoin-miner-to-AI pivot)

12. **CLSK — first SIGNED AI/HPC lease (2026-07-14)** ⚠️
    20-year infrastructure lease with an unnamed high-investment-grade tech company at the Sandersville, GA campus (175MW critical IT load, ~$6.6B contracted revenue over the initial term, up to $11.6B with extensions); entire Texas portfolio (718 acres, up to 885MW) now under exclusivity with the same tenant. This is the first SIGNED AI/HPC lease since the 6/22 `/refresh-context` pass flagged CLSK as zero signed leases / zero AI revenue (100% BTC mining) — likely narrows or closes the rule-13 EV/MW-high-vs-AI-Thesis-low divergence. **Recommend a `/refresh-context CLSK` pass** to re-rate AI Thesis D1/D2 once tenant identity is confirmed.
    Source: [StockTitan 8-K](https://www.stocktitan.net/sec-filings/CLSK/8-k-cleanspark-inc-reports-material-event-c565e0b9aba9.html)

### Other watchlist names (non-holdings)

- **APP** — 12.65% stock drop (7/13) on a BofA note flagging softer e-commerce ad-pixel growth for AppLovin's AI merchant platform; Pomerantz LLP opened a securities-fraud investigation (7/16, plaintiff-firm solicitation, not a filed suit).
- **ABBNY** — Q2 2026: revenue $9.48B (+12% YoY), record orders ~$12B (+28% YoY), op. EBITDA margin 20.2%, net income $1.23B; announced acquisitions incl. Rotork/Rotorque (2026-07-16).
- **ASML** — Q2 2026 (6-K, 7/15): €9.3B net sales, raised FY2026 outlook to €43–45B net sales / 54–56% gross margin.
- **EQT** — preliminary Q2 derivatives 8-K (7/14, ~$45M gain, subject to change ahead of the 7/21 full results); $0.165/share dividend declared.
- **BW** — $50M buyback authorized + full redemption of $61.4M 6.50% senior notes due 2026 (7/13).
- **CEVA** — COO transition disclosed (last day 8/1, transition through year-end).
- **ADSK** — 8-K discloses agreement to acquire MaintainX for ~$3.575B; exact filing date unverified in-window, flagged for follow-up.
- **ORCL** — 8-K/A amends co-CEO/CFO compensation terms (administrative, not a new leadership change).

---

## 📊 Earnings Refreshed (Rule #9)

**TSM** was the only watchlist name to report quarterly earnings inside this window (Q2 2026, 6-K filed 2026-07-16). A **full 173-name objective-input refresh already ran the same day** (commit `78a8b3d`, 2026-07-16 20:50 PDT / 2026-07-17 11:50 Taipei — after TSM's Taipei-morning earnings release). TSM's sheet row shows "Last Updated 2026-07-16" with Rev YoY 35.1%, closely matching the 6-K's H1 2026 +35.6% YoY figure — **the refresh appears to have already captured post-earnings data**; no separate rule-9 refresh action was taken this pass. No other watchlist name reported earnings in-window (all other holdings' Q2 dates fall late July/August: AMZN 7/30, MSFT 7/29, ANET 8/4, META TBD, EME 7/30).

**TTM vs MRQ check:** not applicable this pass — TSM's own quality metrics (GM 61.87%, ROIC 48.6%) were not compared against an MRQ figure separately; the "Last Updated" match above is the strongest available signal that the refresh is current.

**Score movement:** TSM held at 82.25 / ✓✓ (no tier change from the 7/16 refresh — see Portfolio Pipeline below for the one tier change that did occur, NVDA).

---

## 💼 Portfolio Pipeline

```
$ python3 scripts/refresh_targets.py --check
Targets reflect current scores ✓
```

**Tier crossing already occurred outside this scan, on 2026-07-16 — flagging prominently per Step 3 of the routine spec:**

| Ticker | Old Score/Tier | New Score/Tier | Old Target % | New Target % |
|---|---|---|---|---|
| **NVDA** | 85.1 / ✓✓✓ | 84.39 / ✓✓ | 12.0% | 11.76% |

Membership unchanged (still 12 holds, no entry/exit band crossings — 70/74.5/73.0 thresholds). The freeze-safe rebalance fired because a **held name's tier** changed (NVDA ✓✓✓→✓✓), which is the trigger condition; MU's within-tier drift (84.8→80.64, still ✓✓) did not fire a separate event. This is a price-driven scoring artifact from the post-selloff objective refresh, not a change to NVDA's underlying AI-compute franchise — but it is exactly the kind of move Dom should be aware of since last week's scan reported NVDA as the portfolio's sole ✓✓✓ name.

### Weekly performance mark (from `tracking/performance-series.json`, maintained by network-capable `daily-refresh.yml` CI; latest close 2026-07-16)

| Period | Model | SMH | QQQ | SPY | EW Universe |
|---|---|---|---|---|---|
| This week (7/9 → 7/16) | **−6.14%** | −6.39% | −2.40% | −0.13% | −5.95% |
| Since inception (5/26) | **−1.06%** ($9,893.99) | −5.52% | −3.23% | +0.28% | −0.41% |

⚠️ **Rough week — the "AI selloff" cited in the 7/16 objective-refresh commit is visible directly in the mark.** The model gave back its entire since-inception gain this week (was +5.42% as of the 7/10 scan, now −1.06%), roughly matching SMH's drawdown and worse than QQQ/SPY, though the model still holds a since-inception edge of +4.46pp over SMH and +2.17pp over the EW universe — the higher-conviction concentration cuts both ways in a broad AI-name drawdown. Not a thesis break in itself (no fundamental deterioration surfaced this scan for any holding), but the magnitude is large enough that it's worth a conscious gut-check on the Layer-06-silicon concentration flag below. Per project rules, this is not a trade recommendation.

**Concentration flag (carried forward, updated):** Layer-06 silicon (NVDA 11.76% + MU 9.64% + AVGO 7.61% + SNDK 7.09% ≈ **36.1%**) is down from the ~42% flagged at the 7/2 rebalance (largely from NVDA's tier-driven trim), but remains the largest single-layer concentration in the book with no cap active.

**50DMA refresh:** blocked by yfinance egress (same as every session this cycle) — a live test (`momentum_50dma.py NVDA`) confirmed the block and its stray write was reverted before touching the committed sheet. Last-known 50DMA values stand.

---

## 🔬 Rating Integrity (Rule #12)

```
$ python3 scripts/audit_rating_integrity.py --summary
rating-integrity (all layers): 170 rated names | 0 UNGATED (no thesis) | 0 stale (>90d)
```

Clean — fifth consecutive week, no gate violations, no stale (>90d) ratings.

---

## 🎯 Calibration (Rule #17)

```
$ python3 scripts/resolve_forecasts.py --dry-run
0 resolved, 0 need review (dry run — nothing written)
```

14 open forecasts (`tracking/forecasts.jsonl`), all `REL_STRENGTH_1Q` seeded 2026-06-26 with `resolution_date: 2026-09-30`. Nothing due this week.

---

## 🎯 Layer 10 SaaS Watch: PLTR, DDOG, CRM

*Per scan instructions — tracking NRR, AI feature adoption, pricing-model shifts. None are current portfolio holdings.*

**PLTR (70.2 ✓✓):** Nothing material in-window beyond a routine Q2 2026 earnings-date announcement (Aug 3). Several genuinely newsworthy items (Nvidia sovereign-AI initiative, Surf Air Mobility expansion, US Army NGC2 progress, Rackspace partnership) all pre-date the window (6/29–7/9) and are not re-reported here.

**DDOG (63.5 ✓):** Nothing material. Named a Leader in the 2026 Gartner Magic Quadrant for Observability (6th consecutive year, 7/15, vendor recognition not scored). CEO Olivier Pomel sold 127,141 shares (~$32.9M) under a pre-arranged 10b5-1 plan (7/13) — routine. **No new analyst action** on top of last week's Bernstein downgrade (7/6) / Benchmark Street-high PT (7/2) — both stand unchanged.

**CRM (64.3 ✓):** No new 8-K/earnings in-window. Follow-up coverage (The Register, 7/15) added color on the KeyBanc Agentforce-adoption downgrade (already known) — quotes KeyBanc's CIO-survey checks as weak, cites "aggressive price increases," and Salesforce's on-record rebuttal ("fastest-growing product in Salesforce history"). This is commentary on an already-known downgrade, not a new rating action — still the most concrete evidence in-hand of the R5=2 disruption-risk thesis showing up in analyst channel checks. Track into the late-August fiscal Q2 report.

---

## Routine filings

*(Confirmed in-window, non-material — dividends, scheduled buybacks, routine insider 10b5-1 sales, earnings-date-only announcements)*

<details>
<summary>Expand for the full list</summary>

- **ENTG** — $0.10/share quarterly dividend declared (7/15)
- **EQIX** — two leadership departures (CBO Jon Lin, CAO Simon Miller) surfaced but filing dates unverified in-window (effective dates 7/18, 7/31) — flagged for direct follow-up next scan, not counted as confirmed in-window material
- **CRDO** — routine 10b5-1 Form 4 insider sales (CFO, CTO, COO) + a CEO intra-family share gift
- **ANET** — CEO Jayshree Ullal routine 10b5-1 Form 4 sale (7/10)
- **APH** — Q1 2026 dividend paid (7/15, already-declared)
- **TER** — CEO/director routine 10b5-1 sales, pre-existing plans
- **PLTR, RDDT, MKSI, VRT, DDOG** — Q2 2026 earnings-date scheduling announcements only (Aug 3–6)
- **EME** — Q2 2026 earnings-date scheduling announcement (7/30)
- **KLAC, ONTO, CDNS** and ~119 other tail names searched with zero in-window findings (see coverage note above for which 54 were not searched at all)

</details>

---

## New 13F Activity

Not directly re-checked this week (WebSearch budget was prioritized for the 8-K/news sweep). Per the 2026-07-03 scan's confirmation across all six tracked funds, Q2 2026 13F-HR filings are not due until **August 14, 2026** — no activity would be expected in this window regardless.

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🔴 | **WebSearch session budget (200 calls) is now a hard constraint on full-watchlist coverage** — 54 tickers went unsearched this week. Raise the budget, reduce query density for the tail, or accept holdings+SaaS-only scope most weeks with periodic full sweeps (as the last two scans did). |
| 🟡 | **NVDA tier crossing (✓✓✓→✓✓, 7/16)** is a price-driven scoring artifact from the post-selloff refresh, not a fundamentals change — flagged for awareness, no action implied. |
| 🟡 | **This week's model mark: −6.14%, erasing the since-inception gain to −1.06%.** Model still ahead of SMH/QQQ/EW since inception; not a thesis break, but the magnitude plus the Layer-06 concentration (36.1%) is worth a conscious look. |
| 🟢 | **CLSK's first signed AI/HPC lease (7/14)** — worth a `/refresh-context CLSK` pass to re-rate AI-Thesis D1/D2 once tenant identity is confirmed; this is the data point the 6/22 context briefing was waiting on. |
| 🟢 | **SNDK×Meta NAND deal** still unconfirmed after two scan cycles — worth `/refresh-context SNDK` once an 8-K or earnings disclosure lands (SNDK reports 8/5). |
| 🟢 | **WDC/Kioxia merger talk** (7/15) is media-report-only — track for an 8-K; WDC is not a current holding. |
| 🟢 | **AVGO ITC investigation** (7/16) and **GOOGL EU DMA orders** (7/16) are both new regulatory/legal exposure, early-stage (no rulings) — track, no action yet. |
