# Weekly News Scan — 2026-07-24

**Scope:** 173 watchlist tickers. Scan window: 2026-07-17 – 2026-07-24. **Full coverage achieved** (172/173 tickers searched directly; the 173rd, APH, was closed with a direct follow-up query after its shard agent dropped it — see Execution note). This is the first full-watchlist sweep since the WebSearch budget was raised 200→500 after last week's coverage gap.

## Execution note (network + methodology)

SEC EDGAR (`data.sec.gov`) and Yahoo Finance (`query2.finance.yahoo.com`) are still 403-blocked from this cloud session's egress proxy — confirmed directly via `curl`, the agent-proxy status endpoint (`connect_rejected`, "policy denial"), and a live `yfinance`/`momentum_50dma.py` test (reverted, no data corrupted; see Portfolio Pipeline). Same persistent block as every session since 2026-06-12 per CLAUDE.md's known-issue note. Substituted the `web_scan.py` WebSearch fallback (date-verified, source-filtered, full-watchlist query plan), executed via **10 parallel research agents**, each covering ~18 tickers with the tiered query plan (3 queries for holdings/✓✓+, 1 for the tail). 219 planned queries, ~410 WebSearch calls actually run (agents cross-checked ambiguous dates with follow-ups) — well inside the 500-call budget.

**Coverage:** 172 of 173 tickers got direct search coverage; APH was missed by its shard agent and closed with two direct follow-up searches (no material event, earnings not until 7/29 — see Routine filings). No ticker went fully unsearched this week, unlike the 54-ticker gap on 2026-07-17.

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

Same 12 holdings as the last five scans (membership unchanged since 7/2 rebalance): NVDA, TSM, MU, CRDO, META, ANET, AVGO, AMZN, SNDK, MSFT, GOOGL, FIX — all currently ✓✓ tier (no ✓✓✓ holdings since NVDA's 7/16 tier crossing, so no `/refresh-context`-level treatment triggered by the tier rule).

Full per-name pre-scan model recorded in this session; condensed: NVDA (dominant accelerator vendor, just crossed ✓✓✓→✓✓ on price not fundamentals) and TSM (record Q2, raised capex) were believed stable post-earnings; MU was believed to be watching for confirmation of the unverified Burry-short rumor; the four hyperscalers (META/AMZN/MSFT/GOOGL) were believed to be in pre-earnings quiet periods; AVGO/CRDO/ANET were believed unchanged since their respective legal/insider-sale news; SNDK carried two open threads (unconfirmed Meta NAND deal, unexplained 7/15 drop); FIX was believed unchanged post its 7/1 leadership transition.

**What the scan surfaced that the model missed:** **FIX reported Q2 earnings this week (7/23) with a ~20% EPS beat and backlog nearly doubling YoY ($8.12B→$13.70B)** — not on my radar going in (I was tracking it as "quiet post-leadership-transition"). **GOOGL reported Q2 (7/22)** with strong headline growth but a **negative free-cash-flow quarter** (-$5.9B) and a capex guidance raise to $195-205B, plus a **new €890M EU DMA fine** (7/23, distinct from the 7/16 binding-specification orders) — the fine and the FCF dynamic weren't anticipated. **SNDK's two open threads (Meta NAND deal, 7/15 drop cause) remain unresolved for a third consecutive scan** — nothing new found this week despite direct searches. This is exactly the kind of gap Step 0 is meant to catch: two portfolio holdings had real, scoring-relevant news this week that a pure "nothing changed" prior would have missed.

---

## ⚠️ Material Events

### Portfolio holdings

1. **FIX — Q2 2026 earnings (2026-07-23) — MATERIAL, triggers rule-9, 📊 immediate-priority (beat ≈20%, exceeds 15% threshold)**
   GAAP EPS $12.53 (beat by $2.11, ≈20% above consensus), revenue +50.3% YoY to $3.27B, same-store backlog nearly doubled YoY ($8.12B→$13.70B), dividend raised $0.10 (to $0.90/sh). This is the standout print of the week for a holding.
   Source: [StockTitan 8-K](https://www.stocktitan.net/news/FIX/comfort-systems-usa-reports-second-quarter-2026-6pc4g0cg8jje.html)

2. **GOOGL — Q2 2026 earnings (2026-07-22) + EU DMA fine (2026-07-23) — MATERIAL, triggers rule-9** 📊
   Consolidated revenue +24% YoY to $119.8B, Google Cloud +82% to $24.8B, op margin 34% (+2pt) — but FY26 capex guidance raised to $195-205B and the quarter posted **negative FCF of -$5.9B**, with management flagging a Q3 shift toward third-party/leased compute as a margin-pressure bridge. Separately, the EU Commission fined Alphabet **€890M (~$1B)** under the DMA (Search self-preferencing, Play Store anti-steering), ordering a Search redesign within 60 days — distinct from and in addition to the 7/16 binding-specification orders reported last week. Google is evaluating an appeal.
   Sources: [SEC 8-K/exhibit](https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000066/googexhibit991q22026.htm), [CNBC](https://www.cnbc.com/2026/07/23/google-1-billion-eu-fine-dma.html)

3. **AMZN — AGI-unit layoffs confirmed (2026-07-22)**
   Amazon confirmed layoffs within its Artificial General Intelligence unit (teams under VPs Adeeb Shanaa and Vishal Sharma), framed as strategic realignment even as AI-infra spend increases — follows the January 2026 companywide 16,000-role cut. Reports Q2 earnings 7/30.
   Source: [CNBC](https://www.cnbc.com/2026/07/22/amazon-lays-off-some-employees-in-its-agi-unit.html)

4. **NVDA — Korea research lab (2026-07-23), minor**
   NVIDIA and KAIST launched a joint AI research lab in Seoul ($300M collaboration, ~$50M/yr compute over 5 years) — ecosystem-expansion signal, not a customer-concentration or fundamentals change.
   Source: [GlobeNewswire](https://www.globenewswire.com/news-release/2026/07/23/3332666/0/en/NVIDIA-and-KAIST-Launch-Joint-AI-Research-Lab-to-Accelerate-AI-Innovation-in-Korea.html)

5. **MSFT — Databricks partnership expansion (2026-07-23), minor**
   Decade-long partnership extension deepening Azure Databricks / Azure Cobalt (Arm) usage. No new Azure-capacity event or pre-earnings signal found; the Copilot/Azure securities-fraud class action saw only recurring plaintiff-firm solicitation notices, no new substantive allegation. Reports 7/29.
   Source: [PRNewswire](https://www.prnewswire.com/news-releases/databricks-and-microsoft-expand-partnership-to-help-enterprises-bring-business-context-to-enterprise-ai-302832954.html)

6. **AVGO — no new in-window development; ITC matter unchanged**
   Extra scrutiny applied per this scan's instructions: the Samsung HBM/DDR5 ITC investigation (instituted 7/16, AVGO named co-respondent) has no ruling or procedural update dated in-window; evidentiary hearing still slated Nov 2026. No new custom-silicon customer news since the OpenAI "Jalapeño" item (~6/24).

7. **MU, TSM, CRDO, ANET, META, SNDK — no material in-window events found.** MU: no confirmation/denial of the Burry short-rumor; auto-SCA and $100B US-investment threads are pre-window. TSM: Q2 earnings landed 7/16, one day before this window (already covered last scan). CRDO/ANET: only routine insider 10b5-1 sales and analyst PT moves. META: pre-earnings quiet period (reports 7/29), board departures pre-window. **SNDK: the Meta NAND-deal rumor and the unexplained 7/15 ~15% drop remain unconfirmed for a third consecutive scan** — direct searches this week found nothing beyond analyst PT raises (Bernstein $1,700→$3,000).

### Layer 4/5 (Semi-equipment / Fabs) — earnings-heavy week

8. **INTC — Q2 2026 earnings (2026-07-23) — large beat, 📊 immediate-priority**
   Revenue $16.1B (+25% YoY, $1.8B above guidance midpoint), non-GAAP gross margin 41.8% (+280bps vs. guide), non-GAAP EPS $0.42 vs. $0.20 guided (~110% beat vs. guide), DCAI server revenue +59% YoY.
   Source: [CNBC](https://www.cnbc.com/2026/07/23/intel-intc-earnings-report-q2-2026.html)

9. **SMCI — preliminary Q4 FY2026 update (2026-07-21) — 📊 immediate-priority (gross margin +~700-880bps sequential vs. prior guide)**
   Revenue tracking near the low end of $11.0-12.5B guidance, but GAAP/non-GAAP gross margin now estimated 15-17% vs. 8.2-8.4% prior guidance on favorable mix — comfortably clears the rule-9 "gross margin moved >500bps sequentially" threshold. Full results/call Aug 11.
   Source: [SEC 8-K](https://www.sec.gov/Archives/edgar/data/0001375365/000137536526000019/fq42026businessupdate.htm)

10. **TEL — record fiscal Q3 2026 (2026-07-22)**
    Net sales $5.16B (+14% YoY), GAAP EPS $2.55 (+19%), adj. EPS $2.94 (+22%), record orders $5.7B (+27%), raised Q4 guide.
    Source: SEC 8-K

11. **TXN — Q2 2026 earnings (2026-07-22)**
    Revenue $5.46B (+23% YoY), EPS $2.14 (+52% YoY), broad growth incl. data center.
    Source: SEC 8-K

12. **STM — Q2 2026 earnings (2026-07-23)**
    Revenue $3.49B (+26% YoY, above outlook midpoint), raised data-center revenue ambition to >$1B (2026) / >$2B (2027).
    Source: [GlobeNewswire](https://www.globenewswire.com/news-release/2026/07/23/3331866/0/en/stmicroelectronics-reports-q2-2026-financial-results.html)

13. **BESIY — Q2/H1 2026 results (2026-07-23)**
    Revenue €249.9M (+68.7% YoY), net income +177.3% YoY, orders +128.8% YoY — hybrid bonding/photonics/datacenter driven. Foreign filer, disclosed via press release not EDGAR.
    Source: [GlobeNewswire](https://www.globenewswire.com/news-release/2026/07/23/3331898/0/en/BE-Semiconductor-Industries-N-V-Announces-Q2-26-and-H1-26-Results.html)

14. **AMKR — NVIDIA $1.5B prepayment partnership (2026-07-23)**
    Multi-year strategic partnership; NVIDIA prepays $1.5B to fund advanced-packaging/test capacity expansion (incl. Arizona) for next-gen AI/accelerated-computing platforms.
    Source: [Amkor IR](https://ir.amkor.com/news-releases/news-release-details/amkor-technology-announces-strategic-partnership-nvidia-expand)

15. **WDC — Kioxia merger talks revived, stock +12.5% (2026-07-22)**
    Renewed NAND-merger discussions (share deal or spin-off, no terms confirmed) plus a sector rebound and continued China-chip restrictions; Citi/Wells Fargo/Cantor raised PTs sharply. WDC is not a current holding (exited 6/26) but is watchlist-tracked.
    Source: [TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262047263-western-digital-wdc-stock-surges-july-22-2026-kioxia-merger-hdd-sold-out-tradingkey)

### Layer 1 (Power) — earnings + AI-power-demand contracts

16. **EQT — Q2 2026 earnings (2026-07-21)**: sales 634 Bcfe above guidance-high, net income $211M, raised FY26 volume guidance, trimmed capex $25M. Same-day: completed Blackline Midstream acquisition.
17. **RRC — Q2 2026 earnings (2026-07-21) — 📊 immediate-priority (EPS beat ≈28%)**: net income $195M ($0.83/sh) vs. ~$0.65 consensus, revenue $759.6M vs. ~$747.2M est.
18. **GEV — Q2 2026 earnings (2026-07-22)**: revenue $11.1B (+22% YoY), adj. EBITDA margin 11.3%, FCF $5.1B, raised outlook, $2.3B buybacks in-quarter.
19. **NEE — Q2 2026 earnings (2026-07-24)**: GAAP net income $3.144B ($1.50/sh) vs. $2.028B ($0.98/sh) Q2-25; 3.6GW backlog add; reiterated Dominion Energy combination progress. *(GAAP-vs-adjusted EPS figures diverged slightly across sources — not reconciled this pass.)*
20. **SO** — Georgia Power signed a 25-year power supply deal for OpenAI's ~3,200MW Effingham County, GA data center (7/22).
21. **DUK** — NC rate-hike settlement roughly halved the proposed increase (~18%→~9.5% cumulative) and cut requested ROE 10.1%→9.8% (7/20).
22. **OKLO** — joined a ~$200M Trump-administration nuclear-acceleration program (with X-Energy, Microsoft, Nvidia) for AI-datacenter reactor deployment (7/21).
23. **AEP** — added ex-Equinix CEO Charles Meyers to its board (7/20), directly AI-datacenter-relevant.
24. **PPL** — signed the White House Ratepayer Protection Pledge on large-load (datacenter) cost allocation (7/23) — borderline-material policy commitment, not an order.

### Data-center construction / REITs / cooling

25. **DLR — Q2 2026 earnings (2026-07-23)**: revenue $1.9B (+29% YoY), raised FFO/Core FFO outlook.
26. **MTZ** — closed $1.65B acquisition of The Superior Group (DC-focused electrical contractor), 7/20.
27. **VRT** — acquired Strategic Thermal Labs (liquid cooling), 7/20; announced Tognana, Italy chiller-capacity expansion, 7/21.
28. **CARR** — acquired 75F (AI-enabled building automation), 7/23.
29. **EQIX** — CBO Jon Lin's departure took effect 7/18 (previously flagged pending; now confirmed effective).
30. **TT** — Chief Global Integrated Supply Chain Officer departing 8/1 (determined 7/20).

### Layer 9 (Bitcoin-miner/neocloud pivot) — capacity/financing wave

31. **IREN** — raised AI Cloud ARR target $3.7B→>$4B on $2.8B new multi-year contracts (7/20).
32. **HUT** — second 352MW/15-yr lease at Beacon Point, TX campus (7/20).
33. **NBIS** — first senior secured debt facility, ~$775M, GPU-backed (7/17).
34. **CRWV** — $2.6B GPU-backed term loan (7/17); separately pressured by reports of SpaceX competing for Pentagon AI-compute business (7/18).

### Layer 10 SaaS (per this scan's specific NRR/pricing/adoption watch instruction)

35. **NOW (not a holding)** — Q2 2026: subscription revenue +24.5% YoY (beat guide by 150bps), ServiceNow AI crossed **$1B ACV**, FY guide raised to $15.77B subscription revenue (7/22).
36. **CRM (SaaS watch name)** — Morgan Stanley downgraded to Equal-Weight, cut PT 35% ($287→$185) on cRPO/Agentforce-adoption concerns (7/21), a direct follow-up to the 7/9 KeyBanc/Bernstein downgrades. Separately, Agentforce Help Agent reached GA with a new **pay-per-resolution pricing model** ($2/resolution) — a genuine pricing-model shift, exact GA date unconfirmed. Continues to build the R5=2 disruption-risk case.
37. **DDOG (SaaS watch name)** — no fresh in-window NRR/AI-adoption/pricing signal found; last data point remains the 7/15 Gartner MQ leadership mention (pre-window).
38. **PLTR (not a holding)** — no fresh NRR/pricing signal; last figure remains Q1's 150% NRR (5/4); Q2 reports 8/3.

### Other notable (non-holdings)

39. **RDDT** — shares fell ~9% (7/22) on WSJ reports Reddit is weighing ending Google's ~$60M/yr AI content-licensing deal, seeking usage-based fees instead.
40. **TSLA — Q2 2026 earnings (2026-07-22) — 📊 immediate-priority (EPS miss ≈35%)**: revenue beat ($28.24B vs. $25.71B est.) but adj. EPS $0.33 missed $0.51 est.; op margin fell to 1.4%; capex +142% YoY; FCF deficit $1.09B.
41. **AAPL** — entered early DOJ settlement talks on the iPhone antitrust case (7/17); wearables reportedly still a sticking point.
42. **TEM** — definitive ~$1.5B all-stock merger agreement to acquire Personalis (7/20).
43. **SPCX** — set first-ever earnings date (Aug 4), triggering an ~$116B/911.5M-share lock-up release Aug 6; short interest reportedly ~32% of float ahead of it (7/21).

---

## 📊 Earnings Refreshed (Rule #9)

**Objective-input refresh could NOT be executed this session** — both `data.sec.gov` and `query2.finance.yahoo.com` returned 403 policy denials from this cloud session's egress proxy (confirmed via `curl`, the proxy status endpoint, and a direct `yfinance` call). This is the same persistent block noted in every scan since 2026-06-12. A stray `momentum_50dma.py NVDA` connectivity test was reverted (binary xlsx diff from the openpyxl load/save cycle, zero value changes) before it could touch the committed sheet — confirmed via `git status`/`git diff` before and after.

**14 watchlist names reported quarterly results or a material guidance update in-window and need an objective-input refresh once network access is available** (Fwd P/E, EV/EBITDA or EV/FCF, FCF Yield, P/S, ROIC, margins, Rev/EPS YoY, "Last Updated"):

| Ticker | Holding? | Result | 📊 Immediate priority (rule 9b) |
|---|---|---|---|
| **FIX** | **Y** | EPS beat ≈20%, backlog nearly 2x YoY | ✅ |
| **GOOGL** | **Y** | Rev +24% YoY, Cloud +82%, capex↑, FCF −$5.9B | Beat magnitude vs. consensus not confirmed — flag for refresh regardless (holding + capex/FCF shift is thesis-relevant) |
| INTC | N | Rev $1.8B above guide, EPS ~110% above guide | ✅ |
| RRC | N | EPS beat ≈28% | ✅ |
| TSLA | N | EPS miss ≈35% | ✅ |
| SMCI | N | Gross margin +~700-880bps sequential vs. guide | ✅ |
| TEL | N | Record orders +27%, raised guide | — |
| STM | N | Rev +26% YoY, above outlook midpoint | — |
| TXN | N | Rev +23% YoY, EPS +52% YoY | — |
| BESIY | N | Net income +177% YoY | — |
| NOW | N | Beat guide 150bps | — |
| KN | N | Beat ≈6% | — |
| GEV | N | Raised outlook | — |
| NEE | N | EPS +53% YoY (GAAP/adj. discrepancy flagged) | — |
| DLR | N | Raised FFO outlook | — |
| EQT | N | Raised volume guidance | — |

**TTM vs. MRQ check:** not applicable — no refresh ran, so no TTM/MRQ comparison could be computed this pass.

**Recommendation:** the two portfolio-holding refreshes (FIX, GOOGL) are the priority once a network-capable session is available — FIX's ~20% beat is exactly the kind of print rule 9 exists to catch quickly (cf. the MU 14-point/tier miss that motivated the rule), and it's currently sitting un-refreshed in a live portfolio position. Recommend `/earnings-update FIX` and `/earnings-update GOOGL`, or `/refresh-objective portfolio` at minimum, run locally or in a network-allowlisted session at the next opportunity.

---

## 💼 Portfolio Pipeline

```
$ python3 scripts/refresh_targets.py --check
Targets reflect current scores ✓
```

No score changes were made this session (objective refresh blocked — see above), so there is nothing for `refresh_targets.py` to react to; Targets remain in sync with the currently-committed scores. **This is a soft gap, not a clean bill of health**: FIX's beat is real and, once scored, could plausibly move it within- or across-tier given the backlog nearly doubling — that update simply hasn't happened yet.

`momentum_50dma.py` and `track_performance.py` were not run against the full watchlist (both require the same blocked yfinance path); the committed 50DMA values and the performance series stand as last refreshed by the network-capable `daily-refresh.yml` CI.

### Weekly performance mark (from `tracking/performance-series.json`, maintained by `daily-refresh.yml`; latest close 2026-07-23)

| Period | Model | SMH | QQQ | SPY | EW Universe |
|---|---|---|---|---|---|
| This week (7/16 → 7/23) | **+3.13%** | +1.98% | −1.98% | −1.67% | +2.02% |
| Since inception (5/26) | **+2.04%** ($10,203.52) | −3.65% | −5.14% | −1.40% | +1.61% |

The model **recovered the entire since-inception drawdown flagged last week** (was −1.06% as of 7/16, now +2.04%) and is back to leading every tracked benchmark (SMH, QQQ, SPY, EW) since inception. Not a signal to act on (rule 5 — no trade recommendations), just the mark for the record.

**Concentration flag (carried forward):** Layer-06 silicon (NVDA + MU + AVGO + SNDK, last known ≈36%) remains the book's largest single-layer concentration; no cap active. Weights are unchanged from last week since no refresh ran.

---

## 🔬 Rating Integrity (Rule #12)

```
$ python3 scripts/audit_rating_integrity.py --summary
rating-integrity (all layers): 170 rated names | 0 UNGATED (no thesis) | 0 stale (>90d)
```

Clean — sixth consecutive week, no gate violations, no stale (>90d) ratings.

---

## 🎯 Calibration (Rule #17)

```
$ python3 scripts/resolve_forecasts.py --dry-run
0 resolved, 0 need review (dry run — nothing written)
$ python3 scripts/resolve_forecasts.py
0 resolved, 0 need review
```

14 open forecasts (`tracking/forecasts.jsonl`), all `REL_STRENGTH_1Q` seeded 2026-06-26 with `resolution_date: 2026-09-30`. Nothing due this week.

---

## Routine filings

<details>
<summary>Expand for the full list</summary>

- **APH** — no material event; Q2 2026 earnings not until 7/29 (analyst PT raises to $175-200 range, stock +4.75% on 7/21) — closed via direct follow-up after its shard agent missed it.
- **NVDA** — routine EVP Worldwide Field Ops transition 8-K (filed 7/2, pre-window, noted for completeness).
- **MU** — quarterly dividend $0.15/sh paid 7/21 (declared earlier).
- **ANET** — CTO/President Kenneth Duda routine 10b5-1 sale (~$7.39M, 7/20); minor VeloCloud SD-WAN security feature launch (7/21).
- **CRDO** — cluster of sell-side PT raises (Evercore, Stifel, BofA) after management meetings (7/20, stock +7.84%); routine 10b5-1 sales (CFO, COO, CTO).
- **AMZN** — Amazon Business hit $60B annualized GMV milestone (7/21, not core-material); Q2 call scheduled 7/30.
- **MSFT, META** — earnings-date-only scheduling (7/29 both), no pre-announcements.
- **AVGO** — routine Form 4 exec sales pre-window; Standard Chartered/CNCF partnership news pre-window.
- **SNDK** — Bernstein PT raise to $3,000 (7/21, stock +10.5%); FQ4/FY26 earnings (8/5) and Investor Day (8/13) scheduling, announced pre-window.
- **TSM** — routine month-end 6-K (7/24, no disclosed material content beyond standard capital-appropriation disclosure).
- **HPE** — new board member David Goulden appointed (7/24, sub-C-suite, routine governance).
- **ADBE** — CLO retention/severance letter filed as 8-K (7/17) tied to the ongoing CEO transition — a retention agreement, not a departure.
- **SWKS** — unconfirmed-date reports of an accelerated Qorvo acquisition close (end-2026 vs. early-2027).
- **MOD** — new Commercial HVAC segment President appointed (7/21, sub-C-suite).
- **PSIX, TE** — plaintiff-firm securities investigation announcements / ongoing short-seller overhang; no new primary-source filing pinned in-window.
- **SHAZ** — new CFO appointed, effective 8/24 (7/22).
- **~110 other tail names** searched with zero in-window findings (only pre- or post-window items, or nothing at all): CCJ, UEC, LEU, BWXT, SMR, NNE, AR, EXE, CMI, GNRC, ETN, ABBNY, HTHIY, HUBB, PWR, POWL, NVT, ATKR, IRM, EME, JCI, ASML, AMAT (no in-window hits), LRCX, KLAC, TOELY, TER, ONTO, CAMT, KLIC, ENTG, MKSI, PLAB, UCTT, CDNS, SNPS, ARM, GFS, TSEM, UMC, MRVL, ALAB, COHR, LITE, FN, AAOI, POET, CSCO, CIEN, GLW, DELL, SNOW, KEYS, TTMI, MPWR, FLEX, MDB, PATH, AMBA, CEVA, AIP, NXT, AAON, FORM, AEIS, NVTS, LSCC, RMBS, STX, SEI, PUMP, BW, WYFI, HIVE, QCOM, ADI, NXPI, MCHP, ON, PANW, APP, FTNT, ZS, INTU, WDAY, ADSK, ACLS, COHU, ASX, NTAP, 5347.TWO, HHUSF, 0981.HK, HOOD, BE, CEG, D, ETR, VST, TLN, ORCL, CORZ, CIFR, CLSK, BTDR, KEEL, RIOT, WULF, P (no data at all — zero hits).

</details>

---

## New 13F Activity

Not re-checked this week — per the 2026-07-03 confirmation across all six tracked funds, Q2 2026 13F-HR filings are not due until **August 14, 2026**. No activity expected in this window regardless.

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🔴 | **FIX (portfolio holding, 6.5% weight) posted a ~20% EPS beat with backlog nearly doubling YoY (7/23) and cannot be scored this session** — SEC/yfinance egress is blocked in this cloud session (persistent since 6/12). Recommend running `/earnings-update FIX` (and `/earnings-update GOOGL`, also un-refreshed) locally or in a network-allowlisted session at the next opportunity — this is the exact staleness pattern that caused the MU 14-point/tier miss in May. |
| 🟡 | **GOOGL (portfolio holding) posted a negative-FCF quarter (-$5.9B) with capex guidance raised to $195-205B, plus a new €890M EU DMA fine (7/23)** — both thesis-relevant (margin trajectory, regulatory overhang) and un-scored pending the same network block. |
| 🟡 | **INTC, RRC, TSLA, SMCI all had >15%-threshold beats/misses or >500bps margin swings this week** — none are holdings, but all are watchlist names due an objective refresh per rule 9 whenever network access returns; SMCI's margin swing in particular is a large single-quarter signal. |
| 🟢 | **SNDK's Meta NAND-deal rumor and 7/15 drop cause remain unresolved for a third scan cycle** — worth a `/refresh-context SNDK` pass once SNDK's own 8/5 earnings or an 8-K clarifies either thread. |
| 🟢 | **Model recovered fully this week: +3.13%, since-inception now +2.04% and ahead of SMH/QQQ/SPY/EW again** (was -1.06% since-inception as of last scan). No action implied, included for the record per rule 5. |
| 🟢 | **AI-power-demand thesis had a strong week of confirming data points**: Georgia Power's 25-yr/3,200MW OpenAI deal (SO), the AMD Helios/Anthropic 2GW MI450/Cerebras cluster of announcements, Amkor's $1.5B NVIDIA prepayment, and continuing Layer-9 capacity/financing activity (IREN, HUT, NBIS, CRWV) — none are holdings but reinforce the broader thesis. |
| 🟢 | **CRM's Agentforce pay-per-resolution pricing shift + the Morgan Stanley downgrade** continue building the R5=2 disruption-risk case for the next Layer-10 subjective-rating review. |
