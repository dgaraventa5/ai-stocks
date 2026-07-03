# Weekly News Scan — 2026-07-03

**Scope:** 172 watchlist tickers. Scan window: June 26 – July 3, 2026.

**Method / network note:** SEC EDGAR (data.sec.gov, www.sec.gov, efts.sec.gov) and yfinance remain 403-blocked from this cloud environment's egress proxy — confirmed again this session (same restriction as the June 12/19/26 scans; `curl`, `WebFetch`, and `yfinance` all hit `403`/`curl: (56) CONNECT tunnel failed`). The scan was conducted via WebSearch/WebFetch against SEC full-text search mirrors, StockTitan, company IR pages, and financial news sources, with parallel research agents covering: portfolio holdings, Layer 10 SaaS (per this week's specific ask), semis/equipment, power/nuclear, optical/storage/networking, enterprise software/security, neocloud/bitcoin miners, mega-cap adjacent (TSLA/AAPL), and tracked-fund 13F activity. Every claim below is sourced; items that could not be corroborated against a primary source are flagged explicitly rather than stated as fact (rule 3).

**Local-only checks (no network required) confirmed clean:**
- `audit_rating_integrity.py --summary` → **169 rated names, 0 gate violations, 0 stale (>90d)**. Clean for a third consecutive week.
- `resolve_forecasts.py --dry-run` → **0 forecasts due**. All 14 open forecasts resolve 2026-09-30 (Phase 1 rollout, `REL_STRENGTH_1Q`); nothing to grade this cycle.
- `refresh_targets.py --check` → **"Targets reflect current scores ✓"** — no pending rebalance. The portfolio was already re-weighted on 2026-07-02 (see mental-model note below); no membership or tier change occurred in this scan window.
- 50DMA momentum refresh (`momentum_50dma.py`) — attempted, confirmed blocked (`curl: (56) CONNECT tunnel failed, response 403`). No values written (0/1). Consistent with the last three scans; flagging the gap rather than guessing.
- Performance series (`tracking/performance-series.json`) is already current through **2026-07-02** via the separate daily-refresh GitHub Actions CI (which has real network access) — no local refresh needed; see Portfolio Pipeline section for the mark.

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

**Context:** Portfolio composition changed materially since last week's scan (2026-06-26) due to a scoring-methodology overhaul (cohort-relative Value/Quality percentiles, a reverse-DCF mispricing metric, removal of the subjective-rating floor) that landed 2026-07-01/02, two same-day rebalances (`351d74e` then a corrective `4605043` after a reverse-DCF clamp fix). Book went 15→13→12 names. Current 12 holdings, live scores as of the July 2 refresh:

| Ticker | Score | Tier | Mental model (pre-scan) |
|--------|-------|------|--------------------------|
| NVDA | 85.1 | ✓✓✓ | Dominant AI GPU, ~80-90% merchant accelerator share. Now the sole ✓✓✓ name (was ✓✓ pre-overhaul) — cohort-relative scoring lifted it materially, not a fundamentals change. CUDA moat, Blackwell ramp, China ~$0 DC revenue. Largest weight (12%). |
| MU | 84.8 | ✓✓ | HBM3E/HBM4 for Blackwell/next-gen AI. Q3 FY26 (June 24, prior window) was a step-change: $41.5B rev, 84.9% GM, 16 take-or-pay SCAs (~$100B contracted). The reverse-DCF clamp fix knocked it from ✓✓✓ back to ✓✓ — a methodology correction (uncapped growth was saturating the score), not a thesis reversal. |
| TSM | 82.4 | ✓✓ | World's leading contract fab. N3/N2 ramp, CoWoS capacity build. Dropped from ✓✓✓ (87.9 two weeks ago) to 82.4 on cohort-relative rescoring, not a thesis change. Taiwan geopolitics remains the standing risk. |
| ANET | 79.3 | ✓✓ | Arista DC networking. AI fabric $3.5B→$3.25B target raised, MSFT+META ~42% of revenue (confirmed sharper in June 29 10-Q read: largest account rising 20%→26% YoY). Spectrum-X competitive watch ongoing. |
| META | 79.1 | ✓✓ | Social/ads + AI infra (Llama, Superintelligence Labs). AI monetizing via ad ranking, $6.6GW nuclear PPA portfolio. **This week's mental model was too narrow** — see Material Events: Meta is now disclosing plans to become an AI-compute *seller* (Meta Compute), not just a buyer. |
| CRDO | 78.2 | ✓✓ | Credo Technology. SerDes/AEC/silicon photonics for 400G-3.2T. FY26 revenue 3x YoY. Vertical integration (post-DustPhotonics) advancing. |
| AVGO | 77.9 | ✓✓ | Largest custom ASIC designer (Google TPUs, Meta training ASICs) + Ethernet networking. Q2 FY26 AI semi $10.8B (+143%); Q3 guide AI semi $16B. |
| AMZN | 77.7 | ✓✓ | **New to book this week** (entered via the post-overhaul rebalance, replacing PLTR/APP/RDDT, which fell below the exit line once the software business-model bias was removed). AWS hyperscaler, Trainium2/3 reducing NVDA dependency, Anthropic partnership (major investor + primary cloud provider). First week holding it — flagged for closer tracking going forward. |
| MSFT | 77.1 | ✓✓ | Azure AI, Copilot across Office, OpenAI relationship. ~$75B+ annual capex. Wiz acquisition closed March 2026. |
| GOOGL | 75.6 | ✓✓ | Hyperscaler. Gemini, TPU/Blackstone JV, 2026 capex guided $180-190B. Completed $84.75B equity/debt package mid-June. |
| SNDK | 75.1 | ✓✓ | Sandisk (spun from WD 2025). NAND flash, memory-cycle recovery + AI storage demand. Not an AI-moat play — pricing recovery + datacenter mix shift. |
| FIX | 75.1 | ✓✓ | Comfort Systems USA. HVAC/mechanical DC construction pure-play. Record $12.45B backlog, Q1 rev +56.5% YoY. |

**Exited since last scan:** WDC (dropped below the 76 bar on the June 24 refresh, EXIT confirmed). ALAB, APP, RDDT, PLTR all exited/never entered in the post-overhaul rebalance — "crowded software/apps that fell below the exit line once the business-model bias was removed" (commit `351d74e`).

**Thesis diff (articulated vs. scan-discovered):** The single biggest gap between the pre-scan mental model and what the scan surfaced is **META**. The pre-scan model treated Meta purely as an AI-infrastructure *buyer* (capex, PPAs, ad-ranking monetization). The scan found Meta is now reported to be building a business to *sell* excess AI compute — "Meta Compute" — competing directly with AWS/Azure/GCP (and, notably, with two of its own current neocloud suppliers, CoreWeave and Nebius). This is a business-model expansion worth a closer look at the next `/refresh-context META`, not just a news-log entry.

---

## ⚠️ Material Events

### 🔺 Top story: "Meta Compute" — Meta moves from AI-compute buyer to seller (July 1)

Bloomberg/CNBC reported Meta is developing plans to sell excess AI compute capacity and bare-metal GPU access to outside developers, competing directly with AWS, Azure, and Google Cloud. Two possible models under discussion: a Bedrock-style hosted-model-access layer, or a raw-capacity neocloud model. Meta disclosed it already resells capacity today — Anthropic pays Meta ~$1.25B/month, Google pays ~$920M/month — establishing this isn't hypothetical. Effort reportedly led by Santosh Janardhan, Daniel Gross, and Dina Powell McCormick. No pricing, timeline, or customer list announced yet. **META** rose +8.8–9.7% on the news (closed $612.91, 3× average volume).

This is a **direct competitive threat to Meta's own current neocloud suppliers**: **CRWV** fell ~13.9% (Meta has a $21B CoreWeave deal through 2032), **NBIS** fell ~17% (Meta has a $27B Nebius deal), **IREN** fell ~6.5%. It also appears to be the dominant driver of a broader July 1–2 AI-hardware selloff that hit **WDC** (-7% then -9.92%), **STX** (-4.8% to -10.4%), **COHR** (-6.5%), and **LITE** (-6.63%) — none of which showed company-specific negative fundamentals in the same window; all four moves are attributed by secondary sources to the same Meta-compute-leasing anxiety plus a broader memory/AI-hardware profit-taking wave (Micron, SanDisk also down sharply). Flagging this as a theme to revisit, not a confirmed thesis break for any of the four.

Related: **Google reportedly capped Meta's Gemini API access** (FT via Bloomberg, June 28) — Google told Meta as early as March it couldn't fill Meta's full requested Gemini capacity, forcing Meta to ration internal AI-token usage (content moderation, scam detection affected). Read-through: AI compute demand is outstripping supply even among the largest players — a constraint signal for **GOOGL** (2026 capex guided $180–190B) and added context for why Meta may want its own resale business.

*Sources: [CNBC](https://www.cnbc.com/2026/07/01/meta-stock-cloud-ai-compute.html), [Bloomberg](https://www.bloomberg.com/news/articles/2026-07-01/meta-is-building-a-cloud-business-to-sell-excess-ai-compute), [Yahoo Finance](https://finance.yahoo.com/technology/ai/articles/nebius-coreweave-iren-tumble-meta-162444225.html), [Bloomberg (Gemini cap)](https://www.bloomberg.com/news/articles/2026-06-28/google-caps-meta-s-use-of-gemini-ai-financial-times-reports).*

**Action flag:** Worth a `/refresh-context META` to formally examine whether this changes AI-Thesis dimensions (D1 revenue mix, D3 moat) — not done here per rule 5 (no scoring change without the subjective-rating process).

---

### Portfolio holdings (12)

| Ticker | Event | Date | Source |
|---|---|---|---|
| **NVDA** | 8-K (Item 5.02): EVP Worldwide Field Operations Ajay Puri (21-yr exec) stepping down to a senior advisory role; Nicholas Parker (ex-Microsoft EVP/Chief Business Officer) named successor, effective ~Aug 24. | Filed 6/28 | [SEC](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000060/nvda-20260628.htm) |
| **NVDA** | NVIDIA + partners (TSMC, Foxconn, Wistron, Amkor, SPIL) reportedly plan up to $500B in US AI-infrastructure investment over 4 years, including first domestic Blackwell production (Arizona chip build/test, Texas supercomputer assembly). ⚠️ Could not confirm against a primary NVIDIA source (blog fetch 403'd) — secondary-sourced only. | ~7/1 | [CIO Dive](https://www.ciodive.com/news/nvidia-domestic-ai-infrastructure-chip-manufacturing-tariffs/745441/) |
| **MU** | Strategic Customer Agreement with General Motors — long-term US supply of LPDRAM/NOR/UFS NAND for ADAS and in-cabin AI, tied to the $2.0B Manassas, VA fab modernization. One of the 16 SCAs referenced on the Q3 call. Terms undisclosed. | 7/1 | [GlobeNewswire](https://www.globenewswire.com/news-release/2026/07/01/3320600/14450/en/Micron-and-General-Motors-Sign-Strategic-Agreement-to-Secure-Supply-and-Accelerate-Innovation.html) |
| **AVGO / AMZN** | US lifted its export ban on Anthropic's Fable 5/Mythos 5 models (ban had run ~3 weeks after Amazon researchers found a jailbreak/safety issue). Positive read-through for AVGO's disclosed 3.5GW custom-silicon compute deal supporting Anthropic and Amazon's $100B+ AWS/Anthropic commitment. | 7/1–7/2 | [TipRanks](https://www.tipranks.com/news/amazon-broadcom-stocks-do-the-happy-dance-as-u-s-ends-ban-on-anthropics-top-fable-ai-model), [CoinDesk](https://www.coindesk.com/tech/2026/07/01/anthropic-restores-ai-models-fable-mythos-after-the-u-s-lifts-export-controls) |
| **AMZN** | AWS reportedly launched a $1B "IC Accelerated Modernization Framework" (credits through Oct 2030) to migrate US Intelligence Community workloads to AWS, plus a $1B "Forward Deployed Engineering" customer-embed program. ⚠️ Exact publication date within vs. just after the window not fully pinned down. | Early July (date uncertain) | [About Amazon](https://www.aboutamazon.com/news/company-news/amazon-news-today-top-stories-company) |
| **MSFT** | ⚠️ Reported layoffs of ~5,000–9,000 employees (~2.5–4% of workforce; sales, consulting, Xbox gaming), timed to the FY2027 start (July 1) — a recurring annual pattern, framed as funding continued AI capex. **Not confirmed via a primary filing/company statement** — press-report sourced only. | ~7/1 | [Fox Business](https://www.foxbusiness.com/economy/microsoft-eyes-another-wave-layoffs-hit-5000-workers-next-week), [Business Today](https://www.businesstoday.in/technology/news/story/microsoft-to-layoff-over-5000-employees-across-teams-540239-2026-07-01) |
| **GOOGL** | Joined the Dow Jones Industrial Average effective 6/29, replacing Verizon (in the index since 2004; announced 6/23 by S&P DJI). Shares +3.7–4% on inclusion. Liquidity/visibility event, not fundamentally thesis-altering. | 6/29 | [CNBC](https://www.cnbc.com/2026/06/23/alphabet-verizon-dow-djia.html) |
| **GOOGL** | EU Court of Justice upheld the €4.1B ($4.67B) Android antitrust fine, ending Alphabet's challenge to the European Commission's 2018 decision. Shares ~1% lower on the news. Final, binding — worth confirming whether already reserved for on the balance sheet. | 7/2 | [Yahoo Finance](https://finance.yahoo.com/technology/articles/alphabet-shares-edge-lower-eu-185900492.html) |
| **SNDK** | Stock fell ~10% on 7/1 (first trading day of Q3), part of a broader Korean-memory-led selloff (Samsung, SK Hynix) after a +720–857% H1 2026 run and a 6/25 all-time-high close ($2,335). No new SNDK-specific filing found — sentiment/valuation-reset move layered on the Meta Compute-adjacent memory selloff. Bernstein ($3,000 PT, 6/30) and BofA ($2,500 from $2,100, late June) both held/raised targets through the move. | 7/1 | [FXLeaders](https://www.fxleaders.com/news/2026/07/02/sandisk-sndk-stock-dives-toward-1600-as-korean-semiconductor-stocks-lead-global-decline/) |
| **FIX** | Leadership transitions effective 7/1 (announced 6/22, effective in-window): Craig Sasser (prev. RVP Atlantic Region) → COO; Briston Blair (prev. SVP Innovation & Strategy) → Chief Strategy & Innovation Officer. Trent McKenna continues as President. | Effective 7/1 | [Comfort Systems IR](https://investors.comfortsystemsusa.com/news-releases/news-release-details/comfort-systems-announces-leadership-transitions-and-0) |
| **FIX** | Form 4: Director Franklin Myers sold 6,700 shares (~$13.1M, $1,954.47/share). Continues a pattern of heavy insider selling in 2026 (~$152M sold trailing 12mo, zero buys) — consistent with prior activity, not a new signal per the framework's asymmetric insider-selling weighting. Stock fell 8.1% same day (profit-taking + insider overhang + leadership-change news), still up ~95% YTD. | 6/26 | [StockTitan](https://www.stocktitan.net/sec-filings/FIX/form-4-comfort-systems-usa-inc-insider-trading-activity-f253bb95251b.html) |

No material in-window items found for **TSM**, **ANET**, or **CRDO** beyond routine price action / a routine Form 4 (CRDO director sale, $0.9M, 7/1) — all three were individually searched.

---

### 🎯 Layer 10 SaaS Watch: PLTR, DDOG, CRM (per this week's specific ask)

*Tracking NRR, AI feature adoption, and pricing-model shifts as the key thesis risk. None of the three are currently portfolio holdings (all exited in the July rebalance), but they remain on the watchlist.*

**PLTR (Palantir)** — No new NRR disclosure in-window (last reported: 150% NDR, Q1 2026, outside window).
- ⚠️ Expanded Nvidia partnership: Nemotron open models deployed inside AIP/Foundry/Ontology/Apollo for US government + critical infrastructure ("sovereign AI" positioning). 6/29. Stock +4.6–9.3%. [BusinessWire](https://www.businesswire.com/news/home/20260629390275/en/Palantir-Launches-Engine-for-Deploying-NVIDIA-Nemotron-Open-Models-in-Sovereign-Environments)
- US Army selected Palantir Foundry as the cloud data-layer baseline for NGC2 (Next Generation Command and Control), alongside Anduril's Lattice for the tactical layer. Announced 6/22 (just before window); continued reaction in-window. [DefenseScoop](https://defensescoop.com/2026/06/22/army-taps-anduril-lead-ngc2-common-data-layer-baseline/)
- **Pricing-model signal:** CEO Karp publicly criticized OpenAI/Anthropic's token-based pricing on CNBC ("something has gone completely wrong" — argues it leaves enterprises overpaying/exposing competitive IP), implicitly positioning Palantir's outcome-based pricing as differentiated. 7/1–7/2. [CNBC](https://www.cnbc.com/2026/07/01/palantir-karp-open-ai-anthropic-tokens.html)
- Trump's federal disclosure revealed a Palantir stake ≥$1M; D.A. Davidson upgraded to Buy ($115→$175 PT) — both contributed to a July 1 rally.
- No SEC 8-K located within the window (last identifiable 8-Ks: 6/9, 5/4) — could not confirm via EDGAR (blocked).

**DDOG (Datadog)** — No new NRR disclosure in-window (last reported: low-120% TTM NDR, Q1 2026).
- ⚠️ **M&A:** Acquired Adaptive ML, a Reinforcement Learning Operations (RLOps) startup, to help enterprises build/deploy specialized AI agents — price undisclosed. 6/30. [Datadog press release](https://www.datadoghq.com/about/latest-news/press-releases/datadog-acquires-adaptive-ml-to-accelerate-its-investment-in-ai-research-and-development/)
- No pricing-model shift found in-window (explicit non-finding, not an omission).
- Truist's 6/15 upgrade (Buy, $190→$300 PT) is outside-window, but stock momentum continued into it (+8.17% 6/26).

**CRM (Salesforce)** — No new NRR disclosure in-window (Agentforce ARR $1.2B, +205% YoY, was the last figure, May 27 report).
- ⚠️ **Pricing-model shift, directly on-thesis:** Outcome-based pricing for the Agentforce Help Agent is scheduled for general availability in **July 2026** — a shift toward usage/outcome-based pricing layered on top of existing Flex Credits ($0.10/action) and per-user ($125+/mo) tiers. Exact GA date within the month not pinned down further. [Salesforce](https://www.salesforce.com/news/stories/agentforce-help-agent-announcement/)
- Guggenheim upgraded CRM to Buy ($228 PT, ~40–46% implied upside), arguing "AI will pressure CRM, but not kill it" and that the ~35–41% YTD decline over-priced the bear case. 7/1. [GuruFocus](https://www.gurufocus.com/news/8940473/salesforce-crm-upgraded-to-buy-with-228-target-amid-ai-concerns)
- Background context (outside window but relevant to the disruption-thesis read): CRM hit a record ~14-day losing streak into a 52-week low around 6/22 on AI-disruption fears + the $3.6B Fin/Intercom acquisition.

---

### Broader watchlist — material events

**Governance / legal / regulatory:**
- **SNOW** — Say-on-pay vote **FAILED** at the 2026 Annual Meeting (124.5M against vs. 96.3M for); stockholders separately backed majority-voting for director elections. 6/29. [TipRanks](https://www.tipranks.com/news/company-announcements/snowflake-shareholders-reject-executive-pay-support-governance-changes)
- **PANW** — MeetingTV sued Palo Alto Networks and its acquired Koi Security unit, alleging Koi's AI platform ("Wings") hallucinated a threat report falsely linking MeetingTV to a Chinese state actor, causing infrastructure blocks by other security vendors. Reputational/legal exposure directly tied to AI-generated threat intelligence. 6/29, follow-up 7/2. [Axios](https://www.axios.com/2026/06/29/palo-alto-networks-meeting-tv-ai-cyber-lawsuit), [The Register](https://www.theregister.com/legal/2026/07/02/startup-sues-palo-alto-networks-koi-security-saying-an-ai-hallucinated-report-falsely-linked-it-to-chinese-espionage/5266201)
- **SMCI** — Taiwanese authorities raided Supermicro's local office and two supply-chain partners (9 sites, ~50 servers seized) as part of a widening probe into alleged NVIDIA AI-chip smuggling to China via Japan. 6/29–30. **Follow-up 7/1:** Supermicro published an open letter disputing the "raid" framing, stating Taiwan authorities confirmed Supermicro is **not the target** — four Taiwan employees were questioned (two pending hearing, two released on bail); the alleged target is third-party smuggling by operators using Supermicro servers. [Bloomberg](https://www.bloomberg.com/news/articles/2026-06-29/super-micro-office-raided-as-taiwan-expands-chip-smuggling-probe), [DataCenterDynamics](https://www.datacenterdynamics.com/en/news/supermicro-publishes-open-letter-clarifying-details-of-reported-taiwanese-raids/)
- **AAPL** — Vision Pro/smart-glasses chief Paul Meade (7-year lead) is departing for OpenAI to start its hardware unit. Second senior Apple hardware exec lost to OpenAI amid the Ternus CEO transition. 6/26. [Bloomberg](https://www.bloomberg.com/news/articles/2026-06-26/apple-s-vision-pro-and-smart-glasses-chief-paul-meade-is-leaving-for-openai)
- **TSLA** — First known fatal crash involving the Tesla Semi program: a Semi rear-ended two stopped vehicles at a red light in Dayton, NV (driver reportedly asleep), killing a married couple and critically injuring a third person. 6/28. [Electrek](https://electrek.co/2026/07/01/tesla-semi-first-fatal-crash-nevada/), [Forbes](https://www.forbes.com/sites/alanohnsman/2026/07/01/teslas-electric-semi-has-its-first-fatal-crash/)

**Earnings-adjacent / operating updates (no new 8-K Item 2.02 this window, but notable):**
- **TSLA** — Q2 2026 deliveries: 480,126 (production 451,758), +25% YoY, ~74,000 above Street consensus (406,024) — best-ever Q2, first YoY growth quarter since 2023. Energy storage deployments 13.5 GWh, +40%+ YoY. Filed via 8-K 7/2. Full financial earnings call is July 22 (outside window). [Electrek](https://electrek.co/2026/07/02/tesla-q2-2026-deliveries-480126/), [SEC 8-K](https://www.sec.gov/Archives/edgar/data/0001318605/000162828026046717/tsla-20260702.htm)
- **ORCL** — Continued fallout from a 6/23 10-K risk-factor addition (AI datacenter delays, GPU/power shortages, buildout execution) and the FY26 capex/cash-flow picture (capex $55.7B vs. $50B target, FCF −$23.7B, guiding $90–95B FY27 capex, planning $45–50B in new debt/equity). Bloomberg published a recap 7/1 reiterating the risk, not new information, but a signal that the market is still digesting it. [Bloomberg](https://www.bloomberg.com/news/newsletters/2026-07-01/oracle-warns-ai-data-center-splurge-may-not-pay-off)

**Power / nuclear:**
- **CEG / VST / TLN / NRG (sector-wide, PJM-exposed)** — PJM urged the US Energy Secretary to declare a reliability emergency amid record forecast peak demand (~159,563 MW 7/1, ~162,860 MW 7/2), citing environmental-permit constraints on certain plants. 7/1. [Motley Fool](https://www.fool.com/investing/2026/07/01/why-constellation-energy-stock-is-tumbling-today/) — **CEG**: Citi cut its price target to $297 from $348 explicitly citing the updated PJM outlook; stock hit a 52-week low (~$240) 7/2.
- **CCJ** — Cigar Lake mine temporarily suspended due to a sulfuric-acid-plant shutdown at Orano's McClean Lake mill (which processes Cigar Lake ore). Cameco says no expected 2026 production impact currently, flags risk if repairs extend. 7/1. [Investing.com](https://www.investing.com/news/company-news/cameco-suspends-cigar-lake-mine-operations-due-to-mill-issue-93CH-4769929)
- **BE** — Brookfield expanded its AI-infrastructure financing partnership **fivefold, $5B → $25B**, to fund/finance Bloom fuel-cell power for AI data centers. Stock +10.07%. 6/30. [BusinessWire](https://www.businesswire.com/news/home/20260630023022/en/Brookfield-and-Bloom-Energy-Expand-AI-Infrastructure-Partnership-to-%2425-Billion-Fivefold-Increase-to-Build-and-Finance-Rapid-Power-for-AI-Infrastructure)
- **OKLO** — DOE approved the final Documented Safety Analysis for Oklo Isotopes' Groves Isotope Test Reactor (Texas), advancing toward operational authorization (targeting first criticality July 2026). Moderate signal — a test-reactor/isotope unit, not the core Aurora powerhouse business. Also a small tuck-in acquisition (Creative Engineers, sodium/alkali-metal engineering) 6/30. 7/1. [BusinessWire](https://www.businesswire.com/news/home/20260701843499/en/U.S.-Department-of-Energy-Approves-Final-Safety-Analysis-for-Oklos-Groves-Isotope-Test-Reactor-Advancing-the-Project-Toward-Operational-Authorization)

**Semis / equipment:**
- **QCOM** — Fell ~5% 7/1–7/2 after Elon Musk publicly denied reports SpaceX was developing a Snapdragon-powered AI handset ("utterly false"), reversing a speculative rally; also removed from several Russell indices. [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/why-qualcomm-qcom-shares-trading-011624811.html)
- **ARM** — Oracle Cloud Infrastructure announced adoption of Arm's AGI CPU architecture for agentic AI workloads — cited as the catalyst for a 5.3% rebound 7/2 (after a 3.6% pullback 7/1 on sector profit-taking). [TradingKey](https://www.tradingkey.com/news/market-movers/262007416-market-workers-arm-20260702)
- **LRCX** — CEO Timothy Archer filed Form 144 to sell 30,000 shares, closely following a $19.1M Director sale; stock also fell ~9.7%/-7.4% (7/1–7/2) in the sector-wide equipment selloff.

**Networking / storage (sector selloff, ties to the Meta Compute story above):**
- **CIEN** — Fell 8.9% (6/29), continued "sell the news" fallout after the June 4 earnings beat (guidance only modestly cleared consensus) plus a persistent zero-buy insider-selling pattern (49 sales, 0 buys trailing 6mo); a further ~6% tumble around 6/30 tied to the June 8–11 upsized convertible-note offering and a broader optical-sector reversal (Lumentum, Coherent, Marvell, Corning also down sharply that day).
- **APH** — +6.2% (6/30) after Evercore ISI reiterated it as top pick in connectors/sensors (Outperform, $180 PT) on AI datacenter connectivity demand.

**Neocloud / bitcoin-miner-pivot cohort:**
- **CRWV / NBIS / IREN** — Meta Compute selloff, see top story (−13.9% / −17% / −6.5%, 7/1).
- **HUT** — Fell ~10% (7/1) same day its majority-owned subsidiary American Bitcoin Corp announced a 1-for-15 reverse stock split (effective 7/2) to maintain Nasdaq minimum-bid compliance. Could not confirm whether the HUT drop was driven by the split, the sector-wide Meta Compute selloff, or both. [PR Newswire](https://www.prnewswire.com/news-releases/american-bitcoin-announces-effective-date-of-reverse-stock-split-302815796.html)
- **BTDR** — Colocation lease for a Tydal, Norway AI data-center site (targeting Nvidia's Vera Rubin platform); shares +5.1% premarket. **Company itself flags the lease as conditional, not guaranteed to take effect.** 6/29. [Yahoo Finance](https://finance.yahoo.com/technology/ai/articles/bitdeer-shares-advance-norway-ai-141226442.html)
- **KEEL** — Added to the Russell 3000 (6/29). Sharp selloff 7/1–7/2, down ~13.7% in a session (~$447M in equity value, roughly wiping out the ~$445.4M raised in its June 9 convert offering). Aggregator sources cite "delays/cost overruns on a transport project" and cash-burn concerns — **could not corroborate against a primary source; flagging as unverified sourcing, real price move.**
- **CIFR** — Stock fell from ~$29 (mid-June) to ~$19.97 (7/2). Aggregators attribute this to a "critical cybersecurity breach," but **no primary source (SEC filing or major outlet) corroborates this claim** — flagging explicitly as unverified per rule 3, not treating as a confirmed event. Only confirmed in-period filing activity is the previously-disclosed $810M notes offering (closed 6/15).

---

## 📊 Earnings Refreshed (Rule #9)

**No new earnings 8-Ks (Item 2.02) were identified for any watchlist name within the June 26 – July 3 window** — all research agents were specifically asked to flag these and found none. MU's Q3 FY26 beat (June 24) was already captured and refreshed in the prior scan cycle; its current score (84.8, ✓✓) reflects that refresh plus the subsequent methodology overhaul (reverse-DCF clamp), not stale data. Nothing to refresh this cycle.

---

## 💼 Portfolio Pipeline

**No membership or tier changes this week.** `refresh_targets.py --check` confirms **"Targets reflect current scores ✓"** — no pending rebalance. The last rebalance (12-name book: NVDA, MU, TSM, ANET, META, CRDO, AVGO, AMZN, MSFT, GOOGL, SNDK, FIX) was logged 2026-07-02, one day before this scan window opened; nothing in this week's news changes membership or a held name's tier.

**50DMA refresh:** Blocked by yfinance egress (confirmed this session). Last-known values are from the July 2 refresh.

### Weekly performance mark (through 2026-07-02, via daily-refresh CI)

| Period | Model | SMH | QQQ | SPY | EW Universe |
|--------|-------|-----|-----|-----|-------------|
| This week (Jun 26 → Jul 2) | **+0.04%** | −3.16% | +0.86% | +2.17% | +0.15% |
| Since inception (2026-05-26) | **+0.44%** ($10,043.83) | −1.64% | −2.31% | −0.52% | +3.17% |

Model α vs. SMH this week: **+3.2pp**. Inception-to-date α vs. SMH: **+2.1pp**, vs. QQQ: **+2.75pp**. Note the inception-to-date figures compressed sharply from two weeks ago (model was +4.2% at 6/25) — reflects both a rough two weeks for AI-semi-heavy names broadly (SMH −3.16% this week alone) and the portfolio-composition churn from the methodology overhaul. EW universe (+3.17% inception) is now modestly ahead of the model — worth watching, though the model's tilt is by construction toward higher-conviction names, not simple diversification.

**Concentration flag (carried from the 7/2 rebalance, not new):** Layer-06 (silicon: NVDA, MU, AVGO) is ~42% of the book with no cap currently active — flagged to Dom at the time of the rebalance, accepted.

---

## 🔬 Rating Integrity & Calibration

Both checks clean this cycle — no violations, nothing due:
- **Rule #12 gate/staleness audit:** 169 rated names, 0 gate violations, 0 stale (>90 days). Third consecutive clean week.
- **Rule #17 forecast resolution:** 0 of 14 open forecasts due (all resolve 2026-09-30, Phase 1 `REL_STRENGTH_1Q` rollout). Nothing to grade.

---

## Routine Filings

| Ticker | Item | Date | Note |
|--------|------|------|------|
| AMAT | Index | 6/26 | Russell reconstitution: removed from value benchmarks, added to Russell Top 50; also launched new epi/CMP/deposition/eBeam AI-packaging tools. |
| ADI | Index | 6/27 | Russell reclassification value → growth (AI/data-center exposure). |
| INTC | Facility | 7/1 | Groundbreaking on a 107,000 sq ft EUV-photomask expansion at Santa Clara (supports future 18A-P/14A nodes). |
| ALAB | Price action | 6/30 | New all-time high, continued momentum from June 22 Nasdaq-100 inclusion — not a new catalyst. |
| APP | Product/exec | 6/30–7/1 | Public self-serve AXON ad platform launch + e-commerce ads rollout; Raymond James initiated Strong Buy; CTO/CLO transitions (Giovanni Ge, Corina Cacovean effective 7/1 and 8/1). |
| RDDT | Price action | 7/1 | +14% on optimism that 2027 AI-data-licensing renewals move to usage-based pricing (CEO commentary). |
| KLAC | Rating | in-window (exact date unconfirmed) | Moody's affirmed A2, revised outlook to positive, citing AI-driven process-control demand. |
| CRDO | Form 4 | 7/1 | Director Clyde Hosein sold 3,451 shares (~$0.9M) — routine. |
| AVGO | Form 4 | 6/29 (filed) | CLCAO Mark Brazeal sold 25,000 shares (~$9.675M) — part of an ongoing pattern, not flagged material. |
| DELL | Governance | Effective 7/1 | Completed Delaware → Texas redomestication (shareholder-approved 6/25). Administrative only. |
| SNOW | Governance | 6/29 | Directors Briggs, McLaughlin, Ramaswamy re-elected; PwC ratified (alongside the say-on-pay failure noted above). |
| CRWD | Corporate action | Record 6/25, distributed 7/1, split-adjusted trading 7/2 | 4-for-1 stock split. No fundamental change. |
| STX | Form 4 | 7/1 | CEO William Mosley sold ~30,000 shares / exercised 14,000 options under a pre-existing 10b5-1 plan (adopted Feb 2026) — routine. |
| WDC | Rating | 7/1 | BofA raised price target to $732 from $610 the same day the stock fell ~10% — notable divergence, not itself material. |
| CORZ | Form 4 | 7/1 | Insider (Todd DuChene) sold ~10,000 shares — routine. |

---

## New 13F Activity

**None.** Confirmed via targeted search across all six tracked funds (Berkshire Hathaway, Baillie Gifford, Tiger Global, Coatue Management, Whale Rock Capital, Lone Pine Capital) — no new 13F-HR or 13F-HR/A filings this week, consistent with the Q2 2026 deadline not arriving until August 14, 2026. Berkshire's most recent 13F-HR remains the Feb 17, 2026 filing (Q4 2025 period). One non-filing data point of note: Bloomberg (7/2) reported Whale Rock's flagship fund is +72.5% YTD on AI-infra bets, but this references its already-known Q1 2026 rotation (AEIS, VIAV, MKSI), not new activity.

---

## Action Items for Dom

| Priority | Action |
|----------|--------|
| 🔴 | **META thesis review** — "Meta Compute" is a business-model expansion (buyer → seller of AI compute) not captured in the current thesis.md. Worth a `/refresh-context META` or thesis update before the next rating cycle touches D1/D3. |
| 🟡 | **SMCI watchlist flag** — Taiwan smuggling-probe raid, even with Supermicro's "not the target" clarification, is a legal/regulatory overhang worth monitoring for follow-on developments. Not a portfolio holding currently. |
| 🟡 | **CRWV/NBIS/IREN** (non-portfolio, Layer 9) — the Meta Compute story is a real competitive threat to their core supplier relationships with Meta; worth a look if either name approaches the 76 entry bar again. |
| 🟢 | **AMZN** — first week as a portfolio holding; no dedicated thesis.md news-log history yet in this report cadence. Worth confirming research-backed status ahead of any subjective rating touch (already gate-clean per the audit, but flagging for awareness). |
| 🟢 | **CIFR "breach" claim** — unverified rumor, do not treat as fact; revisit if a primary source surfaces. |
