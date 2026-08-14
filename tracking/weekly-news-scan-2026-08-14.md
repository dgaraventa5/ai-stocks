# Weekly News Scan — 2026-08-14

**Scope:** 214 watchlist tickers. Scan window: **2026-08-07 – 2026-08-14.**

## Execution note (network constraints — unchanged from every scan since 2026-06-12)

SEC EDGAR (`data.sec.gov`, `www.sec.gov`) and Yahoo Finance (`query1/2.finance.yahoo.com`) are confirmed
403-blocked from this session's egress proxy (verified directly via `curl` and the proxy's own status
endpoint before starting — `recentRelayFailures` shows `connect_rejected` on `data.sec.gov:443`).
Substituted the `web_scan.py` fallback methodology (date-verified, source-preferenced) executed through
**9 parallel research agents**: 3 covering the 15 current portfolio holdings in depth (NVDA/MU/TSM/SNDK/ALAB;
CRDO/ANET/VRT/FIX/EME; MSFT/AVGO/META/GMED/RDDT), 1 covering the Layer-10 SaaS watch (PLTR/DDOG/CRM) on the
requested NRR/AI-adoption/pricing dimensions, 4 sweeping the remaining 196 tail tickers (~49 each), and 1
checking the six tracked funds' 13F-HR status (today, 2026-08-14, is the Q2 2026 13F filing deadline).
**All 214 tickers received at least one query this week.**

Local, non-network scripts ran cleanly: `audit_rating_integrity.py --summary`, `resolve_forecasts.py
--dry-run`, `refresh_targets.py --check`. `momentum_50dma.py` and a live `refresh_targets.py` run (needs
yfinance for the inverse-vol lookback) remain blocked (confirmed via live test calls this session).

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

15 current holdings (Targets sheet refreshed 2026-08-11; the portfolio migrated to v2 construction —
rank-based selection + inverse-vol sizing — on 2026-08-07, approved by Dom): **NVDA, FIX, TSM, MU, CRDO,
SNDK, ANET, MSFT, AVGO, GMED, EME, VRT, RDDT, ALAB, META.**

Going in: **NVDA** (84.02 ✓✓) believed the dominant AI-accelerator vendor mid-Blackwell/Rubin ramp, Burry
puts and CXMT competition open risk threads. **FIX** (82.29 ✓✓) and **TSM** (82.25 ✓✓) believed unchanged
on-thesis. **MU** (80.76 ✓✓) on-thesis with the Burry short and CXMT threads open. **CRDO** (79.72 ✓✓)
believed quiet. **SNDK** (79.05 ✓✓) and **ANET** (78.81 ✓✓) both already refreshed 2026-08-07 (rule 9,
closing out last week's flagged action item) after their Q2 beats — believed captured. **MSFT** (77.78 ✓✓)
and **META** (73.27 ✓✓) believed stable, refreshed 2026-08-02. **AVGO** (77.16 ✓✓) on-thesis, Samsung MOU
and HBM ITC case open, next earnings 8/29. **GMED** (76.61 ✓✓) and **EME** (75.54 ✓✓) both refreshed
2026-08-07 post-earnings — believed captured, thin research base as recent entrants (GMED 8/2, EME 8/2).
**VRT** (74.08 ✓✓), **RDDT** (73.37 ✓✓), and **ALAB** (73.32 ✓✓) all newly entered 2026-08-07 via the v2
rank-selection migration — thinnest research base of the 15, flagged for the deepest scrutiny this week.

**What the scan changed:** VRT's entry narrative gets a real correction (its pre-entry 7/29 print was
actually a **revenue miss**, not the clean beat implied by "raised guidance" framing — see below). RDDT, as
a brand-new position, surfaced a CLO departure, an S&P 500 addition, and — more importantly — pre-window
context (Google content-licensing tension, a sequential US-DAU decline, and a coming reduction in
DAU-disclosure granularity) that a thin research base would otherwise miss. ALAB picked up a real
competitive-threat data point (MRVL's Celestial AI/XConn acquisitions putting it directly into ALAB's
optical-interconnect market) from this week's separate rule-12 rotation research, not from this scan itself
but newly relevant now that ALAB is held. NVDA and MU both had their short-seller thread escalate materially
(Burry named the $500B NVDA financing deal "shades of Enron" and added to the MU short). None of this moves
a score mechanically (no tier changes fired), but it is real incremental information layered onto positions
initiated or refreshed within the last two weeks.

---

## ⚠️ Material Events

### Portfolio holdings

1. **NVDA — $500B AI-compute financing platform + escalating short-seller criticism (2026-08-10 to 08-13) — MATERIAL**
   NVIDIA announced partnerships with Apollo, BlackRock, Blackstone, Brookfield, Goldman Sachs, and KKR to
   establish independent AI-compute financing platforms targeting mobilization of "over $500 billion" in
   third-party capital over time for hyperscaler/enterprise data-center buildouts (NVIDIA clarifies this is
   aggregate third-party capital, not NVDA revenue or a single committed fund). Michael Burry called the deal
   a "Wall Street stunt"/"sign of desperation" with "shades of Enron" (Substack, 8/11–8/13) and disclosed he
   is holding/adding to NVDA put positions (Dec 2026/Jun 2027 expiries, low-$100s strikes). Separately,
   Bloomberg (8/7) reported the U.S. Bureau of Industry and Security is reviewing how Chinese AI firms access
   NVIDIA chips via offshore/rented compute in third countries — a potential export-control loophole close.
   NVDA reports FQ2 FY2027 earnings 8/26 (next window).
   Sources: [NVIDIA Newsroom](https://nvidianews.nvidia.com/news/nvidia-partners-with-apollo-blackrock-blackstone-brookfield-goldman-sachs-and-kkr-to-establish-ai-compute-infrastructure-financing-platforms-to-mobilize-over-500-billion-of-third-party-capital), [CNBC](https://www.cnbc.com/2026/08/10/nvidia-wall-street-asset-managers-500-billion-ai-push.html), [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/michael-burry-calls-nvidia-500b-070111672.html), [Bloomberg](https://www.bloomberg.com/news/articles/2026-08-07/us-reviews-china-s-offshore-access-to-nvidia-chips-after-ai-breakthroughs)

2. **MU — Burry expanded MU short as stock approached ~$1,000 (2026-08-13) — MATERIAL**
   Burry's Substack disclosed he added to his MU short (puts) as shares approached ~$1,000 (added near $924
   after initiating near $1,052 in July), citing capital-cost and potential 2028 excess-compute-capacity risk.
   No new CXMT-specific development found in-window. Stock extended its AI rally (+4.0% 8/13, +3.25% 8/14) on
   multiple analyst PT hikes (UBS reaffirmed Buy 8/10 citing $265.65 FY2028 EPS est.; Mizuho cited 60% upside
   on memory tightness through 2027).
   Sources: [24/7 Wall St.](https://247wallst.com/investing/2026/08/14/michael-burry-ramped-up-his-bets-against-micron-and-the-qqq-etf-is-the-big-short-investor-asking-for-trouble/), [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/michael-burry-shorts-micron-adding-141819112.html)

3. **SNDK — Investor Day: new multi-year targets, stock +14% (2026-08-13) — MATERIAL**
   Sandisk's 2026 Investor Day laid out long-term targets: mid-to-high-teens annual revenue growth
   FY2028–FY2030, non-GAAP gross margins ~80%, adjusted FCF margins ~50%. Shares surged >14% same day.
   **Correction to prior framing:** the 8/5 F4Q print (just outside last week's window, folded into the
   2026-08-07 rule-9 refresh) showed a headline beat, but its **forward FQ1 revenue guide ($10.3–10.8B) came
   in below the ~$11.16B consensus** — a guidance miss on the next quarter buried under the trailing-quarter
   beat. Worth flagging since this nuances the "clean beat" read baked into last week's refresh.
   Sources: [FXLeaders](https://www.fxleaders.com/news/2026/08/14/sandisk-stock-rips-14-sndk-targets-1579-as-ai-storage-boom-gets-a-2030-roadmap/), [Yahoo Finance](https://finance.yahoo.com/markets/stocks/article/sandisk-stock-sinks-as-revenue-forecast-falls-short-of-expectations-163703465.html)

4. **TSM — Sony JV for next-gen image sensors (2026-08-11) — MATERIAL**
   Sony Semiconductor Solutions and TSMC signed a definitive agreement to form "Advanced Vision Semiconductor
   Manufacturing Corporation," a Kumamoto, Japan JV (Sony ~¥465B incl. an existing fab, TSMC ~¥282B; volume
   production targeted 2029, pending regulatory approval) — new, non-AI-compute capacity commitment. Context,
   date-unconfirmed: reports that Taiwan is weighing stricter export controls on advanced AI chips to China,
   and that China's MOFCOM is considering restricting foreign fabs (incl. TSMC) from using Chinese-designed
   IP — flagged as material context but not clearly dated inside this window, not counted as new.
   Sources: [Sony Semiconductor](https://www.sony-semicon.com/en/news/2026/2026081101.html), [pr.tsmc.com](https://pr.tsmc.com/english/news/3333)

5. **ALAB — competitive-threat data point: MRVL now competes directly in optical interconnect — MATERIAL context**
   Not new this week (surfaced by the separate 2026-08-10 rule-12 rotation research pass, commit `1360176`)
   but newly relevant now that ALAB is a held position: MRVL closed the Celestial AI + XConn acquisitions
   (Feb 2026) and this week (8/10–8/12) launched a new AI memory/storage infrastructure platform (Bravera
   SC6, Structera X CXL, Photonic Fabric, stock +14%) targeting hyperscale/agentic-AI bandwidth bottlenecks —
   the same optical scale-up interconnect space ALAB operates in. No ALAB-specific M&A, financing, legal, or
   executive-departure item found in-window.
   Sources: [Timothy Sykes](https://www.timothysykes.com/news/marvell-technology-inc-mrvl-news-2026_08_12/), rule-12 rotation commit `1360176`

6. **VRT — entry-narrative correction: the pre-entry print was a revenue miss, not a beat — FLAG**
   VRT entered the portfolio 8/7 on a "raised guidance" framing. Digging into the underlying 7/29 Q2 print
   (just before entry): **revenue $3.27B (+24% YoY) missed consensus ~$3.38B**, with an initial negative
   stock reaction (~6% close-to-close, ~12% intraday at the open). The subsequent rally into this window was
   carried by raised FY guidance (net sales $13.8–14.2B, EPS $6.65–6.75), a Bitzero (non-hyperscaler)
   liquid-cooling partnership (8/4), and a cluster of sell-side reiterations (Bernstein 8/11, Argus 8/12,
   GLJ 8/4) — not the headline quarter. No 8-K, executive, M&A, financing, or legal/regulatory item found for
   VRT in-window. This doesn't change VRT's score, but the "beat-and-raise" framing at entry should be
   corrected to "miss-then-raise."
   Sources: [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/vertiv-q2-2026-earnings-revenue-121320056.html), [Investing.com](https://www.investing.com/news/analyst-ratings/bernstein-cuts-vertiv-stock-price-target-on-revenue-miss-supply-concerns-93CH-4828727)

7. **RDDT — S&P 500 addition, CLO departure, and pre-entry context worth surfacing — MATERIAL (new position, thin research)**
   **8/14:** Reddit will join the S&P 500 (replacing AvalonBay Communities), effective ahead of trading 8/18;
   shares surged as much as 11% after-hours. **8/12 (8-K):** Chief Legal Officer & Corporate Secretary
   Benjamin Lee is stepping down effective 9/14/2026 (through 9/25 for transition); Reddit intends to appoint
   Paul Cappuccio (former GC of AOL and Time Warner) as successor. Neither is a thesis break, but both are
   real Item-5.02/index-event disclosures on a position with almost no internal research yet. **Pre-entry
   context that a thin research base risks missing:** Reddit is in tense renewal talks with Google over its
   $60M/yr AI-training content-licensing deal (WSJ, 7/22, stock -8–9% intraday on the report — DA Davidson
   downplayed the exposure at <2% of 2026 revenue, Piper Sandler cut PT $215→$195); the 7/30 Q2 print showed
   a beat-and-raise but a **sequential US-DAU decline** (53.5M→53.2M) that drove a ~21% intraday drop despite
   the beat; and Reddit disclosed it will **stop reporting logged-in/logged-out user metrics starting Q3
   2026** — a disclosure-granularity reduction worth tracking.
   Sources: [GuruFocus](https://www.gurufocus.com/news/9034701/reddit-rddt-joins-sp-500-shares-rally-amid-mixed-valuation-signals), [Investing.com](https://www.investing.com/news/sec-filings/reddit-announces-chief-legal-officer-transition-appoints-paul-cappuccio-93CH-4856176), [CNBC](https://www.cnbc.com/2026/07/22/reddit-stock-google-ai-content-deal.html), [Motley Fool](https://www.fool.com/investing/2026/07/31/reddit-beat-on-revenue-profit-and-guidance-its-us/)

8. **META — AI-hiring-discrimination suit: response deadline landed in-window, hearing next window — FLAG**
   Meta's response in the Oakland federal AI-hiring-discrimination case was due 8/10 (inside this window);
   could not confirm what was filed or its content via web search. The preliminary-injunction hearing remains
   scheduled for 8/24 (next window). Recommend a targeted docket check (N.D. Cal., Judge Orrick) before next
   week's scan. AWS-exec-to-"Meta Compute" succession (Dave Brown/Dave Treadwell) is resolved, confirmed
   background, no new developments.
   Source: [GeekWire](https://www.geekwire.com/2026/departing-aws-exec-dave-brown-is-reportedly-joining-meta-as-facebook-parent-mulls-its-own-cloud/)

No material items found in-window for **FIX, EME, MSFT, AVGO, GMED, or CRDO** specifically beyond routine
insider 10b5-1 sales (FIX Chairman Franklin Myers ~$12.7M combined, 8/10–11) and analyst-rating churn. GMED
had no follow-on news at all since its 8/6 print (a legitimate "nothing to report," confirmed via multiple
query angles). AVGO's next earnings is 8/29; ANET had no in-window follow-on beyond its already-known
post-earnings analyst-target wave (JPM/WFC/Piper/BofA/Barclays, clustered 8/4–8/6, just before this window —
flag to confirm last week's scan captured it) and co-founder Bechtolsheim's ~$135M combined 10b5-1 sales
(8/5–8/6, just outside window, routine but large).

### Layer 10 SaaS Watch: PLTR, DDOG, CRM (net revenue retention, AI-feature adoption, pricing)

- **CRM correction:** Salesforce did **not** report earnings this window — its last print was Q1 FY2027
  (5/27), next is Q2 FY2027 on **8/26**. There is no new NRR/AI-adoption data to report. Most consequential
  item: **Srini Tallapragada, President & Chief Engineering/Customer Success Officer — Salesforce's most
  senior engineering executive — resigned** (8-K filed 8/5, effective 8/6, just outside window), transitioning
  to Special Advisor through 8/6/2027. Follows the Feb 2026 departure of AI EVP Adam Evans. Directly
  R5-disruption-relevant given rule 16's Layer-10 framing; flag ahead of the 8/26 print. Also in-window: a
  WARN-notice layoff (86 SF employees, effective 8/7) continuing a pattern of Agentforce-attributed
  support-headcount reduction (~9,000 → ~5,000 over the trailing year, per management commentary).
  Sources: [MarketScreener](https://www.marketscreener.com/news/salesforce-inc-announces-resignation-of-srini-tallapragada-from-president-and-chief-engineering-an-ce7f50ddd98af62c), [WARN Tracker](https://www.warntracker.com/layoff/salesforce-2026-08-07)

- **PLTR:** no new NRR/AI-adoption/pricing disclosure in-window (157% NDR was disclosed at the 8/3 print,
  just before window). Material: Pentagon Deputy Secretary of Defense Feinberg memo directs up to **$243.9M**
  in no-bid/sole-source Palantir services purchases through 3/31/2027 (reported 8/11) — government-revenue
  concentration/no-bid-optics item. Ongoing net insider selling (~$43.5M trailing 90 days, incl. a CTO
  charitable gift of 350,000 shares 8/10–11), no insider buying.
  Sources: [The Register](https://www.theregister.com/public-sector/2026/08/11/palantir-could-receive-244m-pentagon-no-bid-contract/5286438)

- **DDOG:** the "largest customer" usage-pullback story (widely believed OpenAI) continued via sell-side
  reaction only this week — confirmed, not denied, still not formally named by the company. Scotiabank
  raised its PT to $285 while explicitly noting "OpenAI's significant contribution to Datadog's revenue run
  rate" — the closest thing to a sell-side naming. BofA reiterated Buy, framing the sell-off as "the market
  treating one account's slowdown as a company-wide problem." No new NRR figure or Bits AI adoption metric
  disclosed in-window.
  Sources: [MarketScreener](https://www.marketscreener.com/news/scotiabank-adjusts-price-target-on-datadog-to-275-from-225-maintains-sector-outperform-rating-ce7f5cdddf8bfe24), [Yahoo Finance/TheStreet](https://finance.yahoo.com/markets/stocks/articles/datadog-coverage-bofa-stays-bullish-164700611.html)

### Other watchlist names — highest-materiality items

Given the volume this week, this section curates M&A, financing, leadership, legal/regulatory, and major
capacity/customer-deal items only; routine beats/raises with no distinct strategic angle are in the collapsed
routine section below.

**M&A / major corporate actions:**
- **WDAY** — Reuters reported PE firm Silver Lake is in talks to acquire Workday; shares spiked intraday
  from ~$177 to >$227 (8/13).
- **QCOM** — closed its acquisition of Modular Inc. (AI-native software), part of a push to $40B
  non-handset revenue by FY2029 (8/7).
- **SWKS** — issued $2.0B senior notes to fund its ~$3.0B Qorvo acquisition, **suspended its quarterly
  dividend**, and authorized a new $2.0B buyback, alongside a weaker Q3 (8/10).
- **INTC** — announced, upsized ($15B→$20B), and priced a common-stock offering at $95/share, closing 8/12
  (~$19.7B net proceeds for capex/working capital) — a large dilution event.
- **TSLA/SPCX** — "Terafab," a $16.8B AI-chip manufacturing complex in Texas (Tesla/SpaceX JV), continuing
  fallout from the 8/6 announcement; separately Musk is reportedly weighing separating Tesla's China business
  ahead of a possible Tesla–SpaceX combination (China ~18% of Tesla H1 2026 sales).
- **SPCX** — first quarterly report as a public company (8/4): revenue $7.81B (+92% YoY, beat), narrower
  net loss, but stock fell ~8% after-hours on rising capex.

**Major capacity / customer deals:**
- **CRWV** — Q2 revenue $2.58B (>2x YoY, beat), FY guidance raised to $13.2B, backlog $104B + $25B+ new
  Q3 commitments, new Anthropic/Meta business disclosed (8/11).
- **NEE** — finalized definitive agreements + funding milestone with the US Dept of Commerce and Government
  of Japan for up to 10 GW of gas-fired generation in TX/PA (8/12).
- **RIOT** — reschedule resolved (call held 8/10); disclosed a 20-year, 191MW AI data-center lease with an
  unnamed "leading frontier AI lab" at Rockdale (~$9.1B initial contract revenue, ~$16.1B with extensions).
- **BTDR** — new $4.7B, 16-year AI/HPC colocation lease in Tydal, Norway, but shares fell ~15% on a Q2
  earnings miss/widening loss despite the lease news.
- **AUTO.OL** — record Q2 (+43% YoY), raised FY26 guidance, first-ever $75M buyback, and a new strategic
  (non-binding) global supply agreement with Amazon.
- **AVAV** — $400M+ US Army production contract for the "Locust" directed-energy counter-drone system
  (Pentagon's first directed-energy counter-drone production deal), stock +25% (8/7).
- **ONDS** — Q2 revenue +13x YoY (beat), raised FY26 guidance to $525–550M, ~$280M in new Q2/early-Q3
  orders incl. an AFRL Grasshopper contract and a >$50M Army lethal-unmanned-systems order.
- **P (Everpure/fka Pure Storage)** — new design-win/supply agreement with a second top-5 hyperscaler for
  DirectFlash technology.
- **Sector-wide — drone tariffs:** Trump signed a proclamation (8/13) imposing tiered tariffs on imported
  drones/components (100% on >25kg or thermal-imaging drones; 25% on smaller units; lower rates for
  EU/Japan/Taiwan/Korea/Switzerland/UK) — a tailwind for US-manufacturer AVAV/RCAT/UMAC, a headwind/mixed
  signal for foreign-sourced DRO.AX (Australian).

**Legal / regulatory:**
- **PANW** — China's Cyberspace Administration opened a formal cybersecurity review of PANW products sold
  in China.
- **AAPL v. OpenAI** — new procedural filings: Apple asked the court to bar OpenAI from using the alleged
  trade secrets (8/4); OpenAI moved to dismiss, arguing Apple's own security/offboarding practices undercut
  its claims (8/6).
- **PRCT** — multiple new securities class-action filings (bulk end-of-quarter-discounting/inventory
  allegations) — but CEO Larry Wood bought ~$498K of shares 8/10, a notable insider-confidence buy amid the
  litigation.
- **SERV** — Uber **fully exited** its Serve Robotics stake (8/11) amid a deployment-strategy dispute, on
  top of an already-unwinding delivery partnership (guidance cut to $9–10M FY26, disclosed 8/6).
- **MBLY** — a director resigned following governance changes at parent Intel (8/12); CEO Amnon Shashua's
  planned step-down (announced 7/18) remains an open thread with no successor named.
- **GOOGL** (recent former holding, exited 8/3) — French publisher trade group (APIG, ~300 outlets) filed
  an antitrust complaint over AI Overviews, alleging 33–38% traffic loss (8/12); Gemini app surpassed 1
  billion monthly users (8/11). Background bearing directly on the exit thesis: Chief Scientist Jeff Dean's
  departure to found "Discovery Loop" and Demis Hassabis stepping back to Chairman (8/5, stock -5%/~$190B),
  plus a $25B bond sale (8/6, third major 2026 debt raise, ~$70B in <12 months) amid reported first-ever
  negative FCF — both just outside window but directly relevant to the 8/3 exit.
- **AMZN** (recent former holding, exited 8/3) — no new in-window items; background bearing on the exit
  thesis: Bezos's $4.1B share-sale filing and the NJ AG's antitrust "monopsony" suit (both 8/4, just outside
  window).

**Financing (data-center/power buildout):**
- **DUK** — priced and completed a $1.75B equity units offering to fund ~15GW of gas buildout for
  data-center demand.
- **ETR** — closed a $1.5B junior subordinated debentures offering.
- **ORCL** — new Quantinuum quantum-computing partnership on OCI; also planning a new round of layoffs
  ahead of its Sept 1 fiscal Q2 start, amid continued large-scale debt-funded AI-datacenter buildout — a
  balance-sheet-risk flag worth tracking.

**Leadership:**
- **PSIX** — Richard Hu (ex-BorgWarner/Delphi) becomes CEO effective 8/17, succeeding interim CEO Xun
  (Kenneth) Li, who stays as CFO.
- **D (Dominion)** — Virginia Gov. Spanberger said she is "deeply skeptical" of the $67B NextEra-Dominion
  merger; regulatory scrutiny intensifying.

**Notable earnings beats/misses (>15% or otherwise flagged):**
- **AMAT** — Q3 record revenue ($9.12B, +25%) and EPS ($3.50, +41%), but stock fell ~5% after-hours on
  China sales/outlook concerns.
- **SMCI** — FQ4 EPS beat, gross margin far above prior guide (15–17% vs. 8.2–8.4%), record backlog with
  >$60B in new quarterly orders, FQ1 guide >30% above consensus.
- **CSCO** — FQ4/FY26 results, AI orders >$9B, but stock fell ~7–8% on margin concerns; announced
  restructuring (up to $1B pretax charges) reallocating toward silicon/optics/security/AI.
- **NBIS** — shares +28–30% on a Q2 beat (revenue +454% YoY), reaffirmed FY26 guidance.
- **COHR / LITE** — both large FQ4 beats (COHR record $2.05B revenue +34% YoY; LITE revenue more than
  doubled YoY to $1.01B), both guided above Street.
- **AAON** — record Q2 revenue (>2x YoY) but margin compression drove a ~6% share drop and PT cuts.

---

## 📊 Earnings Refreshed (Rule #9)

No new rule-9-triggering objective refreshes were performed **this** scan. The four names flagged BLOCKED
last week (ANET, GMED, SNDK, EME) were already refreshed by a follow-up session on **2026-08-07**
(`7d39523`, before this scan window opened) — that closes out last week's top action item. No portfolio
holding reported qualifying (Item-2.02-equivalent) earnings *inside* this week's 8/7–8/14 window; NVDA and
AVGO's next reports (8/26, 8/29) both fall in the next window.

| Ticker | Reported | Beat/miss magnitude | Objective refresh status |
|---|---|---|---|
| ANET | 2026-08-04 | Rev +5.9%, EPS +13.3% | **Already refreshed 2026-08-07** (rule 9, prior session) |
| GMED | 2026-08-06 | GAAP EPS +17%, non-GAAP +22% | **Already refreshed 2026-08-07** |
| SNDK | 2026-08-05 | Rev beat, but **FQ1 guide below consensus** (see Material Events #3) | **Already refreshed 2026-08-07** — flag the forward-guide-miss nuance for the file |
| EME | 2026-07-30 | Rev +19.8%, EPS +25% | **Already refreshed 2026-08-07** |
| VST (not held) | 2026-08-07 (8-K) | GAAP EPS -53.4% miss (driven by a $472M unrealized hedge mark, not core ops) | **Handled by the new rule-31 earnings sentinel, 2026-08-13** — score 70.65→64.70, rank 23→69, tier ✓✓→✓. Driver: Rev YoY 43.4→-5.5 flagged as MTM-contaminated for hedge-heavy IPPs (not fixed, per rules 3/8). Not a portfolio holding; no ticket, no exit clock. |

**Tail-name rule-9 bucket-1 candidates this week (>15% beat/miss magnitude, not portfolio holdings):**
ACLS (+24.7%, just outside window), SNDK forward-guide (-4-7% vs. Street, in-window), NRG (-18.1% miss),
plus several already flagged last week and still pending a network-capable refresh session (AEIS, LSCC, SEI,
KLIC, ALAB [now a holding — see Material Events], CGNX, ALNT, CCJ, VPG, TNC, OUST). Recommend batching once
yfinance access is restored.

**TTM vs. MRQ check:** not computable this pass (yfinance blocked). No portfolio holding refresh occurred
this scan to check.

---

## 💼 Portfolio Pipeline

```
$ python3 scripts/refresh_targets.py --check
Targets reflect current scores ✓
```

No membership or tier change fired this scan. `exit_pending` map is empty — no holding is currently below
its exit threshold. A live re-weight run (`refresh_targets.py` without `--check`) was attempted and confirmed
**blocked** — inverse-vol sizing needs a 60-day yfinance price lookback per holding, which fails immediately
on this session's network state; this does not affect the `--check` gate result above, which only compares
against the last logged model event.

**50DMA refresh:** blocked by yfinance egress (unchanged every session this cycle) — last-known values
stand, not refreshed this pass.

**This week's pipeline events (already executed by prior sessions, reported for context — not new findings
from this scan):**
- 2026-08-07 — `sizing_migration_invvol`: one-time switch to inverse-vol sizing + rank selection (v2 spec,
  Dom-approved). Portfolio composition changed: **+VRT, +RDDT, +ALAB** (re-entered), **+6861.T**.
- 2026-08-11 — membership: **-6861.T** (tradability filter, rule 30 — untradable foreign listing, not a
  thesis change).

**Weekly performance mark** (from `tracking/performance-series.json`, maintained by network-capable
`daily-refresh.yml` CI; latest close 2026-08-13 — 2026-08-14 close not yet available):

| Period | Model | SMH | QQQ | SPY | EW Universe | EW_ROSTER |
|---|---|---|---|---|---|---|
| This window (8/7 → 8/13) | **+2.86%** | +1.10% | +1.25% | +0.60% | +4.17% | +3.77% |
| Since inception (5/26) | **+4.60%** ($10,459.88) | −2.16% | +0.36% | +3.90% | +9.45% | **+10.22%** |

The model outperformed all three market benchmarks (SMH/QQQ/SPY) both this window and since inception, but
**lags the equal-weight shadows notably** — EW_ROSTER (the rule-28 standing sizing audit: MODEL minus
EW_ROSTER) is +10.22% since inception vs. the model's +4.60%, a ~5.6pt gap. Inverse-vol sizing only started
2026-08-07, so this is one week of data under the new regime, not yet a two-quarter tripwire (rule 28) — but
worth watching. The new band shadows (BAND_TOP/NEXT/TAIL, live since 8/7) are too new for a read: BAND_TOP
+3.72% / BAND_NEXT +0.55% / BAND_TAIL +2.96% this window.

**Concentration flag** (current 15-name portfolio, allocations from the 2026-08-11 Targets snapshot,
$10,203 notional base): Layer-06 AI Compute Silicon (NVDA+MU+SNDK+AVGO+ALAB ≈ **28.19%**) remains the
largest single-layer concentration, no cap active. Layer-03 DC Construction (EME+FIX+VRT ≈ 19.79%) and
Layer-09 Hyperscalers (MSFT+META ≈ 17.77%) are the next-largest blocks.

---

## 🔬 Rating Integrity (Rule #12)

```
$ python3 scripts/audit_rating_integrity.py --summary
rating-integrity (all layers): 211 rated names | 0 UNGATED (no thesis) | 0 stale (>90d)
```

Clean — no gate violations, no stale (>90d) ratings. The 2026-08-10 rule-12 rotation (8 names: CMI, GNRC,
AMAT, MRVL, ALAB, SNDK, FN, NXT) already ran this cycle ahead of this scan.

---

## 🎯 Calibration (Rule #17)

```
$ python3 scripts/resolve_forecasts.py --dry-run
0 resolved, 0 need review (dry run — nothing written)
```

14 open forecasts (`tracking/forecasts.jsonl`), all `REL_STRENGTH_1Q` seeded 2026-06-26 with
`resolution_date: 2026-09-30`. Nothing due this week.

---

## Routine filings

<details>
<summary>Expand for the full list (confirmed in-window, non-material — dividends, routine buybacks, insider
10b5-1 sales, conference presentations, analyst PT changes without new information, and beat-quarters
without a distinct thesis-relevant angle beyond the sector-wide AI-capex theme already noted above).</summary>

**Power/Utilities:** EQIX (raised long-term guidance, 10-13% rev growth, flagged power/capacity as the
binding constraint — bordering material, noted above); XEL (MN PUC approved Integrated Distribution Plan
w/ flexible-interconnection mandates); OKLO (Q2 call, $3.0B cash, accelerated deployment); SMR (Paragon
contract for protection-system design); NNE (Q3 small-base miss offset by NRC KRONOS MMR application
acceptance + acquisition close); BWXT (CEO sold ~$1.7M shares, routine); PWR (KeyBanc upgrade to
Overweight); PLUG (Q2 rev ~$178M, break-even GM, raised guidance); DLR (routine dividend, PT raises); JCI
(Bernstein reiterated Buy post-Q3); BE (stock +10.68% partial rebound). PPL (Q2 in-line, guidance
reaffirmed, PA DC pipeline ~32GW 10th straight quarterly increase). Just-outside-window cluster (flagged
last week or the week before, not repeated): ATKR (Prysmian acquisition), AMD, CMI, NRG, TLN, IRM, CEG, SO,
MTZ, LEU, BWXT medical divestiture, OKLO criticality milestone, POWL record orders.

**Grid/DC construction/cooling:** LRCX ($3B+ 5-yr R&D lab expansion); CAMT (Q2 beat, H2 guide >30%
growth); TSEM (delayed +12.3% reaction to strong Q2/Q3 guide); ENTG, MKSI, KLIC, UCTT (all just-outside-window
Q2 beats, flagged for context only, no in-window follow-on).

**Semi-equipment/materials:** KLAC, ONTO (both +3-10% on sector AI-capex sympathy, no company news); TER
($1.0B undrawn revolving credit facility, routine); ARM (+5.5% sympathy move). No in-window items: PLAB,
TOELY, CDNS, SNPS, UMC.

**Fabs/foundry:** 0981.HK/SMIC (raised Q3 wafer prices on AI demand — bordering material, noted above);
ASX (July revenue +30.6% YoY — bordering material, noted above); HHUSF (routine board meeting). GFS
(just-outside-window CHIPS silicon-photonics award).

**EDA/IP/silicon:** MRVL (new AI memory/storage platform — noted above under ALAB); AMBA (just-outside-window
NXP acquisition-talk report, still open/unresolved — watch for confirmation); NXPI (Malaysia assembly-test
capacity expansion); ON (AI-datacenter power revenue disclosure, doubled YoY); CEVA (Q2 beat, record
licensing revenue). No in-window items: TXN, QCOM (beyond Modular close), ADI, STM, MCHP (just-outside-window
beat), SWKS (beyond Qorvo financing, noted above).

**Optical/networking:** COHR, LITE (both large beats, noted above); CIEN (+12.4% Lumentum sympathy, no
CIEN-specific news); APH (just-outside-window 2-for-1 split + raised guidance). No in-window items: FN, TEL,
GLW, CSCO (beyond restructuring, noted above).

**Servers/storage:** SMCI, DELL, HPE (SMCI noted above; DELL/HPE +3% sympathy moves). NTAP: no items.

**Cloud/neocloud/BTC-to-AI:** CRWV, NBIS, RIOT, BTDR (all noted above); CORZ (Q2 earnings due today 8/14
after market open, not yet available — follow up next scan); CIFR, CLSK (both routine JPMorgan
target-reset activity, part of a sector-wide bitcoin-miner reset); KEEL (deteriorating financials but
permitting progress, bordering material); APLD (~75MW Polaris Forge delivery milestone); HUT, WULF
(just-outside-window Q2 prints, flagged for context, no new in-window item). IREN: no items (FY26 results
8/27). SNOW, NOW: no items.

**Software/SaaS (Layer 10, non-focus names):** WDAY (Silver Lake talks, noted above); FTNT
(just-outside-window guidance raise); PATH (recovered from a sector-peer-driven ~11% drop, no new
PATH-specific disclosure); no in-window items: MDB, CRWD, ADBE, INTU, ADSK, ZS. TSLA, AAPL (both noted
above). TEM (+11% sector-wide AI-healthcare rally sympathy move). HOOD (routine Robinhood Ventures Fund
disclosure).

**Robotics/foreign/misc (Layer 11 and others):** SERV, AUTO.OL, AVAV, ONDS, PRCT, 6324.T/Harmonic Drive, MBLY
(all noted above); DRO.AX (new RfRecon product line, tariff-headwind context); SSII (record Q2, +39.4%
YoY); 9880.HK/Ubtech (routine board meeting); OUST (Econolite lidar partnership expansion, routine scale);
PDYN (Defense Advisory Board appointment). No in-window items: NTAP, 5347.TWO, ISRG, 2590.HK, HSAI, 2498.HK,
6861.T, 6506.T, KGX.DE.

</details>

---

## New 13F Activity

Today (2026-08-14) is the Q2 2026 13F-HR filing deadline for the six tracked funds. Status as of this scan
(the deadline itself, so several are plausibly filed-but-not-yet-indexed rather than genuinely late):

- **Baillie Gifford — FILED.** AUM grew ~$98B→~$110B. **SpaceX became the top/near-top holding** (~8%
  weight) following its June 2026 IPO. **NVIDIA remained a core position, increased to ~7.6–8.3% weight**,
  alongside adds in Alphabet and Axon Enterprise. Trims: Amazon, MercadoLibre, Spotify, Cloudflare, Shopify,
  Netflix (reported as gain-harvesting/rebalancing, not thesis exits).
- **Berkshire Hathaway** — expected to file today (~4:30pm ET per press previews), **not yet confirmed
  filed as of this scan**. Unconfirmed preview figures (net $19.8B in equity purchases under CEO Greg Abel,
  a large Alphabet position tied to the Q1 stake-tripling + a $10B private placement) should not be treated
  as verified until the filing itself is checked.
- **Tiger Global, Coatue, Whale Rock, Lone Pine** — **not yet filed/indexed as of this scan.** One
  unconfirmed MarketBeat alert (8/7) suggested a Tiger Global NVDA add, but the agent could not verify it
  corresponds to a genuine Q2 2026 (not recycled/stale) data point — not treated as confirmed.

Recommend re-running this check as part of next week's scan (or sooner if EDGAR access is restored) — funds
frequently file at/near 5pm ET on the deadline day itself, so aggregator lag rather than non-filing is the
likely explanation for the four "not yet filed" funds.

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🟡 | **VRT's entry narrative should be corrected**: the pre-entry 7/29 print was a revenue *miss* (not the clean beat implied by "raised guidance"); the rally was guidance/partnership/analyst-driven. Doesn't change the score, but worth noting in any VRT thesis file. |
| 🟡 | **RDDT, as a brand-new thin-research position, has real open threads**: Google content-licensing tension (renewal at stake, <2% of 2026 revenue per DA Davidson), a sequential US-DAU decline masked by a beat-and-raise headline, and a coming reduction in DAU-disclosure granularity (Q3 2026 onward). Worth a `/refresh-context RDDT` pass given the position is only a week old. |
| 🟡 | **ALAB now faces a named, concrete competitor** in optical scale-up interconnect: MRVL's Celestial AI/XConn-derived platform launched this week to a +14% stock reaction. Not a thesis break, but worth folding into ALAB's next research refresh (D2/D3 moat dimensions). |
| 🟡 | **META's AI-hiring-discrimination suit** had a response deadline land inside this window (8/10) with no confirmable public filing found — recommend a direct docket check before the 8/24 preliminary-injunction hearing. |
| 🟢 | **SNDK's forward guide (FQ1 $10.3–10.8B) came in below the ~$11.16B Street consensus**, buried under the trailing-quarter beat headline — worth a note in SNDK's file even though the 8/7 refresh already captured the trailing quarter. |
| 🟢 | **This week's model mark: +2.86% window, +4.60% since inception ($10,459.88).** Beat SMH/QQQ/SPY both this window and since inception, but the EW_ROSTER sizing-audit shadow (rule 28) is running +10.22% since inception vs. the model's +4.60% — a ~5.6pt gap in the first week of inverse-vol sizing. Not a two-quarter tripwire yet, but the gap is real and worth tracking closely as more weeks of data accumulate. |
| 🟢 | **Today (8/14) is the Q2 2026 13F deadline** for the six tracked funds. Only Baillie Gifford is confirmed filed (SpaceX now its top/near-top holding post-IPO; NVDA increased to ~7.6–8.3%). Berkshire/Tiger Global/Coatue/Whale Rock/Lone Pine are unconfirmed as of this scan — recommend a `/thirteenf-delta` pass once filings clear (likely early next week). |
| 🟢 | **A dense cluster of tail-name capacity/financing/M&A activity** this week (WDAY going-private talk, INTC's $20B stock offering, SWKS's dividend suspension + Qorvo debt raise, RIOT's $9.1B AI lease, CRWV's raised guide, drone-tariff proclamation) — none touch portfolio holdings directly but several (WDAY, INTC, ORCL's leverage) are worth a longer look if any cross into thesis-relevant territory next scan. |
