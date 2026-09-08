# Weekly News Scan — 2026-09-04

**Scope:** 214 watchlist tickers. Scan window: **2026-08-21 – 2026-09-04** (14 days — covers a
2-week gap since the last scan ran 2026-08-21; there was no scan filed for the week of
2026-08-28).

## Execution note (network constraints — unchanged from every scan since 2026-06-12)

SEC EDGAR (`data.sec.gov`, `www.sec.gov`, `efts.sec.gov`) and Yahoo Finance
(`query1/2.finance.yahoo.com`) are confirmed 403-blocked from this session's egress proxy
(verified via `curl` and the proxy's own status endpoint before starting — `recentRelayFailures`
shows `connect_rejected` on `data.sec.gov:443`; direct WebFetch to sec.gov/company IR domains
was also blocked mid-scan for at least one subagent). Substituted the `web_scan.py` fallback
methodology (date-verified, source-preferenced) executed through **10 parallel research
agents**: 3 covering the 15 portfolio holdings in depth (NVDA/MU/TSM/SNDK/ALAB;
CRDO/ANET/VRT/FIX/EME; MSFT/AVGO/META/GMED/RDDT), 1 covering 11 other high-tier watchlist names
not currently held (EQT/TER/APH/GOOGL/AMZN/PLTR/WDC/APP/ISRG/CGNX/6861.T), 1 on the Layer-10
SaaS focus (PLTR/DDOG/CRM), 4 sweeping the remaining 186 tail tickers (~47 each), and 1 checking
the six tracked funds' 13F-HR status. **All 214 tickers received at least one query this week.**

**Important correction to last scan's framing:** this is not a fully "dark" week for objective
data. Other sessions with live network access ran *inside* this window per their normal
schedules — the **earnings sentinel** (rule 31) briefed and mechanically rescored **CRDO**
(9/1 print, rescored 9/3, commit `1b84a57`) and briefed **AVGO** (9/2 print, no rule-9 trigger,
same commit); a **Layer-6 analog-cohort rating refresh** ran 8/31 (commit `f95365c`/`bcf172f`);
and `daily-refresh.yml` kept `tracking/performance-series.json` current through 9/3. This scan's
job was to (a) read and report that already-committed state rather than duplicate it, and
(b) WebSearch for anything genuinely new in-window — M&A, litigation, executive moves,
competitive/labor developments — that those automated passes wouldn't catch. Local, non-network
scripts confirmed clean: `audit_rating_integrity.py --summary` (0 gate violations, 0 stale),
`resolve_forecasts.py --dry-run` (0 due), `refresh_targets.py --check` (Targets reflect current
scores, no pending rebalance). `momentum_50dma.py` and an independent live `refresh_targets.py`/
`track_performance.py` run (need yfinance) remain blocked this session — the committed
performance series through 9/3 is read below, not independently re-verified.

One data-quality item corrected this scan: the tracked-fund CIK for **Whale Rock Capital** in
`weekly_scan_runner.py` was wrong (`0001485922` matched no fund in any source checked) —
corrected to `0001387322` based on secondary-aggregator corroboration (whalewisdom/13f.info/
opengovus all agree); flagged for primary-EDGAR reverification once access is restored.

**Post-scan update (same day, after PRs #44/#52/#53/#54 merged to main):** Dom's local
sessions closed most of this scan's open pipeline items before it was even filed — AVGO and
CRDO post-Q3 fundamentals were ingested and hand-recomputed (`a1739a7`), AVGO got a rule-12
rating pass (`be9b638`, M1 5→4), CRDO's PR-#51 M2 5→4 was re-applied, and a **`resize_monthly`
model event fired 2026-09-04** (CRDO outside the ±25% drift band) — Targets rewritten, one
trade ticket generated. The 📊 / 💼 sections and action items below were **rewritten against
merged main** rather than the pre-merge state the scan originally captured; the ⚠️ material
events are unchanged. #44 also landed a 2026-08-24 rating refresh that includes **TE** (T1
Energy) — confirming the P/TE correction above.

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

15 current holdings (all ✓✓ tier; unchanged membership since 2026-08-07's v2 migration —
rank-based selection + inverse-vol sizing): **NVDA, FIX, TSM, MU, CRDO, SNDK, ANET, MSFT, AVGO,
GMED, EME, VRT, RDDT, ALAB, META.**

Going in (carried from the 2026-08-21 scan): **NVDA** the dominant AI-accelerator vendor
mid-Blackwell/Rubin ramp, Burry short/CXMT-competition as open threads, plus the $500B
financing platform and $105B SB Energy guaranty already flagged. **MU** an HBM-bottleneck
beneficiary post tier-jump. **TSM** the sole advanced-node foundry, no red flags. **CRDO** an
optical/AEC interconnect name with the Marvell/Celestial-AI thread open. **SNDK** watching for
guidance widening. **ANET** clean, tracking hyperscaler capex. **VRT** watching guidance
follow-through with a fresh legal-risk thread (securities-fraud investigation announcements).
**FIX/EME** unchanged DC-construction plays. **MSFT** an Azure/AI growth story with an open
Guardian-dispute thread. **AVGO** the custom-ASIC (Google TPU) name with the Marvell-warrant
competitive-diversification narrative and an unsigned $60-100B AI-debt financing deal in
negotiation. **GMED** a distinct Layer-11 surgical-robotics thesis. **RDDT** the thinnest-
research position, Google-licensing-renewal and DAU-decline threads open. **ALAB** watching for
MRVL share-loss evidence. **META** watching the AI-hiring-discrimination injunction hearing
(8/24) and the child-safety trial (opened 8/17).

**Diff against this week's scan — four genuine, distinct developments, no thesis breaks:**
1. **CRDO reported Q1 FY27 in-window (9/1): a real beat, but the stock fell ~20% on
   margin/opex and customer-concentration concerns** — the earnings-sentinel's T+1 rescore
   (81.20→82.40, #3) captured only the price crash; the fundamentals landed 9/4 (PR #53) along
   with a re-applied M2 Rel-Strength 5→4, netting **81.87 / #4**, tier unchanged. The -20% week
   pushed CRDO outside the rule-28 ±25% drift band and fired the month's `resize_monthly`
   event (weight 4.07%→3.57%).
2. **AVGO reported Q3 FY26 in-window (9/2): beat on revenue/EPS/AI-revenue (AI semis crossed
   the >50%-of-revenue threshold pre-registered in its own context file), but stock fell
   ~5-6% on a Q4 guide that missed consensus by ~0.7%** — no rule-9 trigger (surprises inside
   15%). Fundamentals ingested 9/4 (Rev YoY 47.9→85.5%, ROIC hand-recomputed 21.3→28.7,
   ND/EBITDA 1.08→0.68): 77.74→**79.23 / #6**; the same-day rule-12 pass then took M1 EPS
   Revisions 5→4 (consensus level flat post-beat) → **78.7 / #7** (enters the score panel with
   the 9/5 rows). R3 Balance-Sheet is **deferred** to the unfiled Q3 10-Q guarantee footnote.
   The $60-100B AI-debt financing remained **unsigned** through window-end.
3. **META resolved two of its three open legal threads**: the child-safety trial settled for
   ~$18B over 10 years (8/26, court-approved), and the AI-layoff-discrimination
   preliminary-injunction signal went against plaintiffs (8/24, a signal not yet a final
   order). VRT's legal thread went the other way — **widened**, not resolved (a second
   plaintiffs' firm, Hagens Berman, joined 9/1) but still pre-litigation.
4. **MU picked up two new, non-thesis-breaking threads**: a C-suite reshuffle (Sadana to
   Senior Advisor) and a genuinely new operational-risk item — a Taiwan union strike vote
   (~10,000 workers, ~80% support) over profit-sharing, developing through the window with
   no strike yet. Taiwan hosts ~60% of Micron's production and most of its HBM output.

Everything else (NVDA's confirmed $12.93B Hugging Face acquisition, TSM's confirmatory
capex-tool-order Bloomberg report, GMED's small terms-undisclosed AI acquisition, GOOGL's DOJ
ad-tech win, AMZN's new FTC ad-pricing suit) is detailed below but does not change the standing
model. SNDK, ANET, FIX, EME, and RDDT had no new material company-specific developments beyond
routine analyst/insider/macro noise in-window.

---

## ⚠️ Material events

### Portfolio holdings

**NVDA**
- **[2026-09-03, confirmed; first reported 8/27]** Definitive agreement to acquire **Hugging
  Face for $12.93B** — NVIDIA's second-largest deal on record after the ~$20B Groq asset
  purchase, expected to close H1 2027 pending regulatory approval. Hugging Face hosts ~3M
  models/1M apps for 18M+ developers (~$150M ARR); NVIDIA committed the platform stays open to
  AMD and other hardware/cloud providers. Stock reaction modest (+1.8–2.6%) — ecosystem/
  developer-mindshare consolidation, not a customer or margin event. —
  [TechCrunch](https://techcrunch.com/2026/09/03/nvidia-confirms-it-will-buy-hugging-face-for-12-9-billion/),
  [CNBC](https://www.cnbc.com/2026/09/03/nvidia-agrees-to-buy-hugging-face-for-almost-13-billion-ai-expansion.html)
- Q2 FY27 earnings (8/26) were already fully briefed and rescored by the earnings-sentinel
  pipeline before this scan ran (commits `245241a`/`cb911f2`) — not reproduced here; net effect
  over the full window was +0.58 score points, tier/rank unchanged (✓✓/#1).

**MU**
- **[2026-08-26]** ⚠️ Leadership restructuring (8-K Item 5.02): Manish Bhatia promoted to
  **President and COO**; Dr. Scott DeBoer promoted to **President and Chief Technology and
  Products Officer**; **Sumit Sadana (EVP/Chief Business Officer for 9+ years) stepped down to
  Senior Advisor to the CEO** — an exit from an operating C-suite role, not from the company.
  CEO Sanjay Mehrotra unchanged. —
  [GlobeNewswire](https://www.globenewswire.com/news-release/2026/08/26/3351270/14450/en/micron-announces-leadership-appointments-to-accelerate-innovation-and-growth.html)
- **[2026-08-28 – 09-02, developing]** ⚠️ Micron's two Taiwan unions (~10,000 workers, ~80%
  support in an informal poll) are heading toward a **strike vote in September** over a
  profit-sharing dispute — demanding the Incentive Pay Plan be replaced with a scheme setting
  aside 15% of FY2027 operating profit for bonuses (vs. Samsung's 10.5%/SK Hynix's 10%).
  Taiwan hosts ~60% of Micron's global production and most of its HBM output — new
  operational-risk thread with no precedent in the current cycle; mediation ongoing, no strike
  yet. —
  [TrendForce](https://www.trendforce.com/news/2026/08/28/news-micron-taiwan-strike-vote-possible-in-sept-as-80-union-back-action-over-bonus-gap-with-samsung-sk-hynix/),
  [Taipei Times](https://www.taipeitimes.com/News/biz/archives/2026/09/02/2003863518)
- No other in-window items — routine only: 9/1 fractional dividend-adjustment 6-K, Stifel
  initiated Buy coverage, continued Bernstein/BofA price-target raises into the NAND-shortage
  narrative.

**TSM**
- **[2026-09-02]** Bloomberg reported TSMC's quarterly chipmaking-tool-order needs have nearly
  doubled since year-end 2025 (~1.9x the December estimate, up from ~1.5x in Q1); the company
  is simultaneously building/outfitting ~20 wafer fabs globally (vs. a historical ~5 at a
  time), and advanced-node + CoWoS packaging capacity remains fully sold out. Press-report
  based, not a company filing — confirmatory of the capex-acceleration thread already visible
  in TSM's own 7/16 guidance raise, not new company-disclosed information. —
  [Bloomberg](https://www.bloomberg.com/news/articles/2026-09-02/tsmc-s-quarterly-chipmaking-tool-needs-almost-doubled-this-year)
- No other in-window items — routine only: 9/1 fractional-share dividend-adjustment 6-K,
  Stifel initiated Buy coverage.

**SNDK** — no in-window material items; routine conference-participation announcements (Citi
TMT 9/1, Goldman Communacopia 9/9) and continued analyst PT increases into the NAND-shortage
narrative.

**CRDO**
- **[2026-09-01, AMC]** ⚠️ Q1 FY27: revenue $479.0M (+114.7% YoY, beat ~$471.8M est.);
  non-GAAP EPS $1.20 vs $1.12 est. (+7.1%, smallest beat in 6 quarters); non-GAAP GM 68.0%
  flat, but opex $95.2M overshot the $86-90M guide; Q2 guided $525-535M, FY27 outlook raised to
  >85% growth with optical >$600M. —
  [company 8-K Ex-99.1](https://www.stocktitan.net/sec-filings)
- **[2026-09-02]** ⚠️ **Stock fell ~20%** (opened ~$188, closed ~$164.50) despite the beat —
  cited drivers: margin/opex concerns buried in the print, a Q2 outlook seen as light relative
  to AI-demand expectations, renewed customer-concentration worries (top 3 customers = 34%/27%/
  16% of revenue), and at least one analyst price-target cut (BofA to $275 from $340, kept
  Buy — UNVERIFIED DATE on the note itself). —
  [Motley Fool](https://www.fool.com/investing/2026/09/02/why-credo-technology-stock-plunged-20-today/),
  [AskTraders](https://www.asktraders.com/analysis/credo-technology-shares-plunge-20-despite-earnings-beat)
- **Earnings-sentinel rescore already committed** (9/3, `1b84a57`): 81.20→82.40 (#5→#3), tier
  unchanged (✓✓); explicitly flagged that yfinance had not yet ingested Q1 FY27 statements, so
  the score move reflects the price crash via momentum/inverse-vol mechanics, not updated
  fundamentals — **not a post-earnings fundamental verdict.** No Marvell/Celestial-AI
  competitive-thread update found in-window.

**ANET** — no in-window material items; Deutsche Bank initiated Buy 8/31 (secondary-sourced,
primary note not located). No new Nvidia Spectrum-X competitive escalation found.

**MSFT** — no in-window material items of the magnitude of the prior week's Guardian-dispute
move; no confirmed resolution/rebuttal of the Guardian AI-chip-count dispute found in-window
(flagged as an open gap, not confirmed either way). Routine product news only (Copilot
consolidation, MAI-Transcribe-2 release).

**AVGO** — busiest holding again, five items:
- **[2026-09-02]** ⚠️ Q3 FY26 (already briefed by the earnings sentinel, `context-2026-09-02.md`
  / commit `1b84a57`): revenue $29,591M +86% YoY (+0.6% vs. ~$29.4B guide); non-GAAP EPS $3.32
  +96% (+2.5-5.1% vs. $3.16-3.24 consensus) — **no rule-9 trigger** (surprises inside 15%, GM
  sequential move inside 500bps). The news is the guide: Q4 revenue ~$34.8B (+93%), AI semi
  revenue $21.7B guided (+236%), FY26 AI raised to ~$58B, "secured supply" claimed for ~$115B
  FY27. **AI semis reached 56% of revenue — the >50% threshold pre-registered as a watch
  item has fired.** Four of five pre-registered watch items remain unresolved (10-Q RVG/VIE
  footnote not yet filed; no Q3 AI-bookings figure disclosed; no Marvell/Google-warrant
  commentary on the call; receivables did not normalize, $13.7B vs $7.1B FYE25 against +55%
  revenue growth). Infra software recovered (+29% YoY, ARR +15%, op margin +650bps).
- **[2026-09-03]** ⚠️ Stock fell ~5-6% despite the beat, on the Q4 revenue guide missing
  consensus by ~0.7%. —
  [Motley Fool](https://www.fool.com/investing/2026/09/03/why-broadcom-stock-dropped-today/)
- **[2026-08-21]** Marvell/Google-warrant fallout partially **reversed**: Marvell gave back 6%
  the session after its spike while AVGO ticked up ~1%, as the challenger's rally faded on
  warrant-dilution concerns. —
  [24/7 Wall St.](https://247wallst.com/investing/2026/08/21/marvell-sinks-6-as-google-warrant-dilution-overtakes-the-deal-rally-broadcom-ticks-up/)
- **[through 9/4]** The **$60-100B AI-chip debt financing remained unsigned/in-negotiation**
  through window-end (Bloomberg reporting described a junior ~$30B / senior $60-70B structure,
  Blackstone/Apollo participating, via an off-balance-sheet SPV) — a gap to keep tracking, not
  resolved this window.
- VMware vCenter CVE-2026-59310 (CVSS 9.8): federal CISA KEV remediation deadline was 8/21
  (in-window); active n-day mass exploitation continued to be reported through the window
  (Babuk-derived ransomware, suspected China-nexus actor). No new AVGO-specific liability
  disclosure found.

**GMED**
- **[2026-08-26]** Acquired **Higgs Boson Health**, a Duke-incubated digital-health/AI startup,
  to build out a "surgical intelligence" (patient-journey outcomes/analytics) pillar. **Deal
  terms not disclosed.** —
  [GlobeNewswire](https://www.globenewswire.com/news-release/2026/08/26/3351730/0/en/globus-medical-announces-acquisition-of-higgs-boson-health-to-transform-healthcare-experience-through-ai-driven-digital-solutions.html)
- No other in-window items — routine only. No confirmed date on the prior scan's unconfirmed
  Stifel Hold/$64 PT item (still unresolved).

**EME** — no in-window material items; the ~$700M pending electrical-contractor acquisitions
remain slated for Q3 2026 close, no in-window closing announcement found.

**FIX**
- **[2026-08-26]** CEO Brian Lane sold 16,024 shares (~$25.8M), reducing his direct stake to
  145,065 shares — a single large sale, no evidence of coordinated multi-insider selling. —
  [GuruFocus](https://www.gurufocus.com/news/9057505/comfort-systems-usa-fix-ceo-brian-lane-sells-16024-shares)
- No other in-window material items. The 6-day/17% stock slide (ending ~8/26) traces to a weak
  July industrial-production print released 8/18 — **outside the window** and macro, not
  company-specific.

**VRT**
- **[2026-08-25]** ⚠️ Pomerantz LLP announced an investor investigation into potential
  securities-fraud claims tied to the Q2 miss/7/29 drop. —
  [GlobeNewswire](https://www.globenewswire.com/news-release/2026/08/25/3351013/1087/en/investor-alert-pomerantz-law-firm-investigates-claims-on-behalf-of-investors-of-vertiv-holdings-co-vrt.html)
- **[2026-09-01]** ⚠️ **A new firm, Hagens Berman**, issued a similar investor alert — the
  roster of soliciting plaintiffs' firms is widening (now 4: Bronstein Gewirtz, Schall/SBS,
  Pomerantz, Hagens Berman). —
  [GlobeNewswire](https://www.globenewswire.com/news-release/2026/09/01/3354299/32716/en/vrt-alert-hagens-berman-national-trial-attorneys-encourages-vertiv-holdings-co-nyse-vrt-investors-with-significant-losses-to-contact-firm.html)
- **Progression check:** no evidence found of an actual filed class-action complaint or SEC
  enforcement action — all activity remains at the pre-litigation solicitation stage. Widening
  roster, not escalation.

**RDDT** — no in-window material items. Google content-licensing-renewal and US-DAU-decline
threads remain open with no fresh update; Meta's "Hatch" consumer AI agent (surfacing
Reddit/DoorDash/Etsy/Yelp content) is reported "targeted for early September" but its launch
date could not be confirmed in-window — forward-looking positive for RDDT's data-licensing
optionality, flagged not confirmed.

**META**
- **[2026-08-26]** ⚠️ **Settled the multistate child-safety/social-media-addiction lawsuit for
  ~$18B paid over 10 years** (court-approved by Judge Gonzalez Rogers); includes platform
  changes (nighttime app blocking for minors, stronger age-verification investment). Resolves
  the trial flagged as "opened 8/17" last scan. TechCrunch flags the underlying
  age-verification tech "doesn't work well." —
  [CNN](https://www.cnn.com/2026/08/26/tech/meta-states-settle-trial-children),
  [Washington Post](https://www.washingtonpost.com/technology/2026/08/26/meta-pay-up-18b-settle-lawsuit-alleging-social-media-harm-children/)
- **[2026-08-24]** ⚠️ AI-layoff-discrimination case: Judge Orrick signaled plaintiffs are
  unlikely to win a preliminary injunction (record doesn't support success on the merits;
  claims likely belong in arbitration) — a signal, not yet a final written order. —
  [Courthouse News](https://www.courthousenews.com/meta-workers-claiming-ai-fired-them-unlikely-to-see-relief/)
- "Hatch" AI-agent launch (see RDDT above) reported "targeted for early September" —
  UNVERIFIED DATE, not confirmed launched in-window.

### Other high-tier watchlist (not held)

- **GOOGL** — **[2026-09-02]** ⚠️ A federal judge rejected the DOJ's bid to force divestiture
  of Google's ad exchange (AdX)/open-sourcing DFP auction logic in the ad-tech antitrust case,
  ordering behavioral remedies instead — the third straight rejection of a Big Tech breakup
  bid; both sides submit a proposed final judgment within 30 days. —
  [CNBC](https://www.cnbc.com/2026/09/02/google-defeats-us-bid-to-force-ad-tech-sale.html)
- **AMZN** — **[2026-08-31]** ⚠️ FTC + 22 states sued Amazon alleging a "secret ad surcharge
  scheme" — claims Amazon manipulated sponsored-listing auctions since 2018 to overcharge
  ~1.2M advertisers by an alleged $20B+ since 2019; Amazon calls it "misguided." —
  [FTC](https://www.ftc.gov/news-events/news/press-releases/2026/08/ftc-states-sue-amazon-over-secret-ad-surcharge-scheme),
  [CNBC](https://www.cnbc.com/2026/08/31/amazon-ftc-lawsuit-advertisers.html)
- **PLTR** — **[2026-09-01]** ⚠️ Army/Anduril awarded $192M in TITAN production orders,
  Palantir's share $127M for 8 systems — moves TITAN into production. **[~9/2]** Peter Zaffino
  (outgoing AIG CEO) announced to join Palantir as Global Head of Financial Services
  (eff. 1/15/2027). **[9/2]** Stock fell 6.6% on profit-taking two sessions after a 2026 closing
  high (~144x earnings); ARK sold ~$26M PLTR 8/31. —
  [DefenseScoop](https://defensescoop.com/2026/09/01/army-titan-platform-production-awards-palantir-anduril/),
  [The Insurer](https://www.theinsurer.com/ti/news/aigs-zaffino-steps-down-as-executive-chair-to-join-palantir-2026-09-02/)
- **WDC** — **[2026-08-26]** ⚠️ Entered exchange agreements for ~$191.0M of 3.00% Convertible
  Notes due 2028, exchanging for ~$192.7M cash + common stock (closed on/after 9/2) —
  debt-restructuring/financing event. —
  [8-K](https://www.sec.gov/Archives/edgar/data/0000106040/000119312526365796/d376254d8k.htm)
- **TER** — **[2026-09-01]** Launched three new UltraFLEXplus test instruments targeting
  AI/data-center semiconductor and PCIe 6 testing, showcased at SEMICON Taiwan. Baird
  downgraded to Neutral 8/21 (UNVERIFIED DATE on primary source). —
  [StockTitan](https://www.stocktitan.net/news/TER/teradyne-launches-advanced-ultra-fle-xplus-instruments-engineered-dq7nh56ftl1q.html)
- **APH** — 2-for-1 split completion (9/2, mechanical follow-through of the 8/5-6 announcement,
  not new information).
- No other in-window material items: **EQT** (RBC Hold reiterated, routine), **ISRG** (Penang
  facility announcement was 8/17, pre-window, no in-window follow-on), **CGNX** (JPM Buy
  reiterated, routine dividend), **APP** (Cantor Buy reiterated, no new item), **6861.T**
  (Keyence — reportedly down ~8% trailing week as of early Sept, but no driver could be
  identified/confirmed — UNVERIFIED, not presented as material).

### Layer-10 SaaS focus (PLTR / DDOG / CRM) — this week's thematic mandate

**CRM (Salesforce) — the big one.** Reported Q2 FY27 **[2026-08-26]**: revenue $11.35B (+11%
YoY, above high end of guide); non-GAAP EPS $5.90 vs. ~$3.27 consensus — **but $2.53 of the
$5.90 came from a mark-to-market gain on Salesforce's Anthropic equity stake, not operations**
(GAAP diluted EPS $4.29). **Flag: the headline EPS beat is materially inflated by a
non-operating gain; the core operating beat is smaller than the headline suggests.** cRPO $33.5B
+14% YoY (cited as the "real" underlying-demand signal); FY27 revenue guide raised to
$46.1-46.4B. Stock rose ~22-23% — best single day since 2020. —
[CNBC](https://www.cnbc.com/2026/08/26/salesforce-crm-q2-earnings-report-2027.html),
[Motley Fool](https://www.fool.com/investing/2026/08/27/salesforce-stock-just-soared-but-investment-gains-delivered-usd2-53-of-its-usd5-90-in-per-share-profit/)

- **NRR:** could not locate a headline net-revenue-retention % for Q2 FY27 despite multiple
  targeted searches — management substituted qualitative language ("attrition near its lowest
  level on record," "strongest net-new ACV growth in four years"). **Flag per rule 3: this is
  not a substitute for a hard NRR figure, and it's conspicuous in a quarter where the
  disruption narrative makes retention the single most-watched number.** Priority follow-up
  once EDGAR access is restored (check the 10-Q MD&A).
- **Agentforce/AI monetization (the core deliverable):** Agentforce ARR exceeded **$1.5B,
  +240% YoY** (note: the metric definition now includes Slackbot and Headless 360 — a scope
  change that inflates the growth rate somewhat, not purely organic). Combined "AI and Data"
  (Agentforce + Data 360) ARR ~$3.9B, +210% YoY. Agentforce for IT Service >450 customers
  **including migrations off ServiceNow** — a notable competitive-displacement data point.
  3.2B Agentic Work Units delivered in Q2 (+97% QoQ), 19T+ tokens processed.
- **Pricing model:** confirmed running **three concurrent pricing architectures** — per-AWU
  metered, flex-credit pools, and traditional per-user seat editions ($125/user/month) — i.e.
  hedging between predictable per-seat ACV and consumption upside, not a clean pivot to
  consumption billing.
- **Disruption narrative — direct management response:** CEO Benioff explicitly rebutted the
  "SaaSpocalypse" thesis on the call ("Frontier models depend on CRM. They don't replace it"),
  citing seat growth, record-low attrition, and 9-of-top-10 AI companies as Salesforce/Slack
  customers (spend +435% YoY). Also relevant: **$27B spent on buybacks in a single quarter**
  (8/13, pre-window but directly on-thesis), explicitly framed as a bet against the
  SaaSpocalypse narrative.
- **[2026-08-27]** ⚠️ **Claudeforce** — expanded Salesforce/Anthropic partnership: Claude
  becomes an available reasoning model inside Agentforce; Salesforce becomes a plugin *inside*
  Claude (37 prebuilt sales skills, open beta targeted Sept 2026) letting users query/act on
  CRM data without opening Salesforce. **Double-edged for the R5 disruption read:** validates
  Salesforce's data/workflow moat, but also normalizes accessing CRM data/actions from outside
  the Salesforce UI. —
  [Anthropic](https://www.anthropic.com/news/salesforce-anthropic-expanded-partnership)
- **[2026-09-01]** Contentful acquisition closed (~$1.5B, agreed May, cleared Australian
  antitrust 8/4) — adds headless CMS to the "Headless 360" content layer.

**PLTR** — see Army TITAN contract + Zaffino hire above. No new NRR disclosure in-window (last
disclosed: 150% US commercial as of Q1 FY26; a separately-cited "134%, +600bps" figure could
not be reconciled — **flag: conflicting NRR figures across sources, needs primary-10-Q
verification**). No new Foundry/AIP adoption metrics found in-window.

**DDOG** — no earnings in-window (Q2 was 8/6). The prior scan's open item — a possible
"Bits AI per-investigation → AI-Credits" consumption pricing shift — is now **date-confirmed
at 2026-06-10 (DASH conference)**, resolving the gap but landing well before this window (~74-
82% effective per-investigation price cut via a shared credit pool spanning Bits Chat/
Security/Dev). NRR stable "in the low-120s%" as of 6/30 quarter-end, no new disclosure
in-window. **Material in-window development:** continued fallout from the large-customer
usage-cut overhang disclosed at the 8/6 print — Zacks downgraded (Strong Buy→Hold) and
reports of sizable institutional selling; DDOG down ~22% over the trailing month as of 9/2. A
customer-concentration event, not itself a pricing/NRR/AI-adoption signal, but the single most
consequential DDOG item touching AI-workload-monetization durability this window.

### Long-tail (186 names) — selected material items by sub-sector

**Power/grid/DC-construction:**
- **D/NEE** — [9/3] ⚠️ Dominion Energy shareholders approved the $66.8-67B all-stock NextEra
  merger (98% approval); still needs state/federal regulatory sign-off.
- **NVT** — [8/24] Agreed to acquire Maverick Power for up to $2.3B ($1.75B base + $550M
  earnout); expected close Q4 2026.
- **BWXT** — [8/26] Selected by the U.S. Army to deploy a 20-MW Advanced Nuclear Reactor at
  Fort Campbell, KY (Janus program).
- **GEV** — [8/26/27] Claire McDonough named incoming CFO (joins Nov 2026); also won a 400kV
  GIS substation contract and signed an HVDC JV with LS Electric for Korea's grid.
- **AMD** — [9/2] AMD/Cisco/HUMAIN announced MI355X-based AI infrastructure live in Saudi
  Arabia.
- **SBGSY (Schneider Electric)** — [8/23] Q2: revenue $13.4B, +16.5% organic; raised FY guide
  on electrification/AI-DC demand.
- **HTHIY (Hitachi)** — [8/23] Anand Birje named CEO of the combined Hitachi Digital
  Services + GlobalLogic org, effective 9/1.
- Data-quality flag: one source claimed an "NRG mid-September EPS guidance raise" —
  **UNVERIFIED / date-impossible** (today is only 9/4); likely a search-index artifact, do not
  treat as confirmed.

**Semi-equipment / fabs / silicon:**
- **KLIC** — [effective 9/1] Dr. Raj Talluri (ex-Enovix/Micron/Qualcomm/TI) became President &
  CEO.
- **GFS** — [9/2] Announced UX platform tech for Physical-AI edge applications + a GCRAM
  memory JV with RAAAM.
- **UMC** — [9/2] Completed NT$4.79B domestic convertible-bond funding; approved up to
  US$1.8B in 7th overseas convertibles.
- **MRVL** — [8/28] Shares fell 6-10% despite the $12.2B Google deal, on underwhelming forward
  guidance relative to the deal size.
- **NVTS** — [8/24/25] Signed a definitive agreement to acquire Claros Inc. for up to ~$232.8M
  (AI-DC power-delivery tech).

**Optical / networking / servers — a big earnings week:**
- **CIEN** — [9/3] ⚠️ Q3 FY26: revenue $1.67B (+37% YoY), GAAP EPS $1.83 vs. $0.35 y/y — but
  shares fell ~10% on cautious Q4 guidance and margin concerns.
- **SMCI** — [8/24] ⚠️ Taiwan prosecutors indicted 9 people (incl. 2 ex-SMCI Taiwan-subsidiary
  employees, 1 Nvidia Taiwan employee) for illegally routing 74 of 130 B300 AI servers to China
  via Indonesia/Japan/HK transshipment; SMCI says it self-reported/cooperated and isn't a
  target. Stock fell ~7%.
- **DELL** — [9/1] ⚠️ Q2 FY27: record revenue $47.0B (+58% YoY); raised FY27 outlook by $25B
  to ~$192B, incl. $74B from AI servers.
- **HPE** — [9/2] ⚠️ Q3 FY26 beat: revenue $12.21B (+33.7% YoY); raised FY guidance;
  networks-for-AI orders hit $2.2B cumulative (target raised to $2.5-3.0B).
- **SNOW** — [9/2] ⚠️ Q2 FY27: revenue $1.55B (+35% YoY); raised full-year product-revenue
  forecast; shares surged ~20.6%.

**Neocloud / bitcoin-miner-pivot cohort — continued capacity-deal cadence:**
IREN (raised FY26 ARR target to >$4B, $2.8B new contracts; $2.4B Blue Owl compute financing),
HUT (WSJ tied its Texas site to a reported ~$35B Nvidia/Anthropic arrangement), WULF (482MW
Kentucky PSC power approval), BTDR (~$100M, ~200-acre AI/HPC land purchase), CORZ ($600M
secured credit facilities) — no single-item smoking gun, but the cohort's capacity/financing
narrative remained active and consistently in-window this week.

**Software/analog — another dense earnings week:**
MDB (Q2 beat, but shares fell ~12.6% on Atlas/AI-growth concerns), CRWD (Q2 beat, raised
guidance, shares +11%+), ZS (Q4 beat, ARR +25% to $3.77B), PANW (Q4 beat, but shares fell
~5-7% on gross-margin compression), INTU (EPS beat by 22.5%, but FY27 guide fell short, shares
-11%+), WDAY (Q2 beat, operating margin 11.8% vs. prior-year 9.4%; **exec departure**: Amy
Bunszel (23-yr veteran) announced retirement same day as ADSK's print — different company,
same day, do not conflate), ADSK (Q2 beat, raised guidance). **FLEX** — [9/3] agreed to acquire
EPC Power (800V AI-DC power conversion) for $4.4B ahead of a planned CPI-segment spinoff. **SEI
(Solaris Energy Infrastructure — not SEI Investments)** — [8/27] acquired Omega Foundation
Services, expanding a ~660MW power platform. **TEM** — [8/24] FDA 510(k) clearance for an
AI pulmonary-hypertension product.

**Storage / Layer-11 robotics / defense-adjacent:**
- **NTAP** — [9/2] FQ1 2027: revenue $2.03B, EPS +66.5% YoY; raised full-year guidance.
- **HOOD** — [8/28] ⚠️ Ninth Circuit ruled 3-0 that Robinhood/Kalshi sports event contracts
  aren't "swaps" under the CEA, letting Nevada enforce gambling law (Robinhood appealing,
  SCOTUS-track circuit split); **[9/1]** Morgan Stanley upgraded to Overweight ($124→$150 PT).
- **AVAV** — [9/2] Awarded $464.8M Army OTA for LOCUST X3 laser weapons — first-ever U.S.
  production contract for directed-energy weapons.
- **KTOS** — [9/1] Won >$20M mobile-SATCOM-gateway contract.
- **PRCT** — [8/31, ongoing] Multiple law firms filed/publicized securities-fraud
  class-action deadline notices (Sept 22 lead-plaintiff deadline) tied to an 18% stock drop.
- **DRO.AX** — [8/26] Record H1 revenue (+74% YoY) but swung to a statutory net loss on margin
  deterioration; ~A$250M sell-off followed; FY26 guidance reaffirmed.
- **2498.HK (RoboSense)** — [8/26] Interim results: revenue +30.2% YoY, LiDAR units +169.6% YoY.

**Coverage gap (scan-process error, corrected same day):** two real tickers received no
actual news coverage this scan because the tail-sweep agent was seeded with the wrong company
names and "confirmed" them as unresolvable — **P is Everpure (fka Pure Storage), Layer 8
storage**, not a retired Pandora ticker; **TE is T1 Energy Inc., Layer 1 solar/renewables**, not
a mistyped TE Connectivity. Both rows are valid in the Watchlist (added 2026-07-16). An earlier
version of this document (and the 2026-09-04 commit message / Notion page) wrongly flagged them
as dead/mistyped — that was the agent's assumption, unverified against the local spreadsheet,
not a finding. **Neither name was searched under its real company name this scan — carry both
into next week's sweep.** `SPCX` (SpaceX, IPO'd 2026-06-12) is already correctly on the
Watchlist in Layer 10 — no action needed.

- **AMBA** — NXP Semiconductors reportedly in talks to acquire Ambarella (~$3B+), first
  reported 7/31; still open/unresolved, no in-window confirmatory update found — worth a
  dedicated follow-up regardless of window boundaries given the deal size.

**No other in-window material items (grouped, brief):** the large majority of the tail —
power/utilities (AEP, DUK, SO, ETR, PPL, XEL, VST, TLN, NRG, CCJ, UEC, LEU, SMR, OKLO, NNE),
grid/construction (HUBB, PWR, MTZ, POWL, ATKR, DLR, EQIX, IRM, MOD, CARR, TT, JCI, ASML),
semi-equipment (AMAT, LRCX ex-dividend-raise, KLAC, TOELY, ONTO, CAMT, ENTG, MKSI, PLAB
litigation-deadline-only, UCTT, CDNS, SNPS, ARM), fabs (INTC, TSEM, GFS ex-item above), optical/
connectivity (COHR, LITE, FN, AAOI, POET, CSCO, TEL, GLW), analog/power silicon (TXN, QCOM, ADI,
STM, NXPI, MCHP, ON, SWKS, MPWR, AMBA ex-item above, CEVA, KN, AEIS, LSCC, RMBS, STX, FORM,
ACLS), large-cap software (ADBE, FTNT), and most Layer-11 foreign names (Fanuc, Yaskawa,
Daifuku, Kion, Harmonic Drive, Nabtesco, THK, HIWIN, AutoStore, and most JP/HK/DE/AU small
caps) — only routine dividends, analyst price-target moves, conference appearances, or
pre-window earnings found in this window. Full ticker-level detail is in the `<details>`
toggle below.

---

## 📊 Earnings refreshed

Both held names that reported in-window were fully refreshed by Dom's local sessions on 9/3-9/4
(merged main, PRs #52/#53/#54) — nothing left for this scan to do on rule 9:

| Ticker | Print | Score path | Now | Tier |
|---|---|---|---|---|
| **CRDO** | Q1 FY27, 9/1 | 79.72 (8/17) → 82.40 (9/3 T+1, price-only) → fundamentals + M2 5→4 (9/4) | **81.87 / #4** | ✓✓ (unch.) |
| **AVGO** | Q3 FY26, 9/2 | 77.16 (8/17) → 77.74 (9/3, 50DMA band) → fundamentals + ROIC 28.7 (9/4) → 79.23 / #6 → M1 5→4 (9/4) | **78.7 / #7** (panel 9/5) | ✓✓ (unch.) |

**TTM/MRQ flags:** AVGO Rev YoY 85.5% and EPS YoY +216% are operational (rule 15 reviewed, not
blanked); ROIC is a hand-recomputed curated input because yfinance never supplies it — the
"fetch returned no data" guard now says so instead of logging a failure. **No rule-9 immediate
trigger** on either name (surprises inside 15%, GM moves inside 500bps). **No tier crossings;
no >5-pt single-cause move.** Layer-06 cohort knock-on from AVGO (rule 20): NVDA/ALAB +0.23,
MPWR -0.45, QCOM -0.30, rest <0.2.

**Not refreshed (non-held, network-blocked here):** CRM, DELL, HPE, SNOW, CIEN, MDB, CRWD, ZS,
PANW, INTU, WDAY, ADSK, NTAP and several neoclouds reported in-window — rule-9's "within 1
week" priority applies, none executable this session. Recommend `/refresh-objective` on this
set from an on-network session, prioritizing CRM (thematic mandate) and PANW/MDB (post-beat
margin-compression sell-offs).

**Not refreshed this scan (non-held names, network-blocked):** CRM, DELL, HPE, SNOW, CIEN, MDB,
CRWD, ZS, PANW, INTU, WDAY, ADSK, NTAP, and several neocloud names all reported strong or
mixed quarters in-window (see above) — none are current portfolio holdings, so rule-9's
"within 1 week" (not "immediate") priority applies, and none is executable this session given
the yfinance block. Flagging rather than fabricating updated objective inputs for any of them;
recommend a follow-up `/refresh-objective` pass once egress is restored, prioritizing CRM given
this week's thematic mandate and DDOG/PANW given their post-earnings margin-compression flags.

---

## 💼 Portfolio pipeline

- **Model event: `resize_monthly` fired 2026-09-04** (kind `resize_monthly`, reason "CRDO outside
  drift band") — the rule-28 monthly ±25% drift-band pass, triggered by CRDO's -20% week (data,
  not a methodology deploy, so rule 32-C damping doesn't apply). **Membership unchanged (15/15
  HOLD), no tier changes, no ENTER/EXIT/EXIT PENDING.** Targets rewritten (header now
  "refreshed 2026-09-04"); `refresh_targets.py --check` green on merged main. The dry-run had
  said FREEZE — it doesn't simulate the monthly pass — so the real run fired.
- **Inverse-vol re-size, old → new target %** (biggest moves bold):

  | Ticker | 8/17 | 9/04 | | Ticker | 8/17 | 9/04 |
  |---|---|---|---|---|---|---|
  | NVDA | 10.38 | **11.04** | | GMED | 10.05 | 9.60 |
  | FIX | 6.73 | **5.98** | | EME | 7.62 | **6.92** |
  | TSM | 8.51 | 8.79 | | ALAB | 3.73 | 3.76 |
  | CRDO | 4.07 | **3.57** | | VRT | 5.67 | 5.64 |
  | MU | 3.73 | 3.89 | | RDDT | 4.62 | 4.50 |
  | AVGO | 7.64 | 7.24 | | META | 8.60 | **9.68** |
  | ANET | 6.90 | 6.88 | | MSFT | 8.75 | **9.47** |
  | SNDK | 3.00 | 3.03 | | | | |

- **Trade ticket `2026-09-04-resize_monthly`:** 1 order (**VRT buy** — share delta vs. the 9/3
  recon actuals, where VRT was a drift-flagged under-hold), 14 names dust-suppressed; **expires
  2026-09-06 22:11Z**. Deliberately left for the executor (rules 5/29 — deleting it would be a
  discretionary trade call by Claude). ⚠️ **Timing:** 9/4 is a Friday and the ticket expires
  Sunday night — if the launchd executor only runs weekday mornings, it dies unexecuted and
  regenerates on the next model event; if that's not the intent, Dom runs it by hand.
- **Rank watch (tradable universe, rule 30):** META is tradable-rank **15** (full-universe 16 —
  6861.T at 13 is untradable), i.e. on the N=15 entry line, first name into the 16-18 dead-band
  on any further slip; AMZN (16) / APP (17) / GOOGL (18) queue behind it. Exit needs rank >18
  plus the 2-run clock — nothing pending, `exit_pending` empty.
- **Live account (sanitized `live-status.json`, as of 9/3):** not halted, 0 open orders, 0
  anomalies; **9 drift flags** (ALAB, CRDO, EME, FIX, META, MSFT, NVDA, SNDK, VRT); live-vs-model
  shortfall running **~-3.9pp** (live -7.75% vs model -3.63% at 9/2, baseline 8/9) — the live
  book is not fully mirroring the model weights; the VRT ticket closes one of the nine.
- **Methodology seam** (rule 32-C, stamped 2026-08-31 for the P2 acceleration deploy) expires
  **2026-09-07**; not exercised (no exit clock started inside it).
- **Weekly mark** (`tracking/performance-series.json`, now current through **2026-09-04** on
  merged main — the 9/4 session added +1.8% and lifted the whole window):

  | | Window (8/21→9/4) | Since inception (5/26) |
  |---|---|---|
  | **Model** | **+1.14%** ($9,972.86 → $10,086.38) | **+0.86%** |
  | SMH | +1.18% | — |
  | QQQ | +0.77% | — |
  | SPY | +0.58% | — |
  | Equal-weight universe (EW) | -0.45% | — |
  | EW twin of model roster (EW_ROSTER) | +1.01% | — |
  | BAND_TOP (ranks 1-15) | +1.13% | — |
  | BAND_NEXT (ranks 16-25) | **-4.51%** | — |
  | BAND_TAIL (ranks 26-40) | +0.72% | — |

  Model ≈ SMH, ahead of QQQ/SPY/EW and its own EW_ROSTER shadow (the sizing audit, rule 28:
  +0.13pp this window). **BAND_NEXT -4.5% vs BAND_TOP +1.1%** is the widest band spread yet —
  ranks 16-25 absorbed PLTR -6.6%, the AMZN FTC suit, DDOG's -22% month. One fortnight, not the
  two-full-quarter test rule 28 pre-registers, but it currently reads "hold N=15".
- `momentum_50dma.py` and an independent live `track_performance.py` run remain blocked this
  session (yfinance) — the committed state above was produced by Dom's on-network sessions on
  9/3-9/4, read here, not re-verified.
- No concentration, layer-cap, dead-ticker, or manual-override-collision flags.

---

## 🩸 Capitulation flags

Not applicable this week — no holding is EXIT, EXIT PENDING, or seam-damped (`refresh_targets.py
--check` confirms no pending rebalance), so Step 7d's exit-side capitulation check has no
names to run against.

---

## 🔬 Rating integrity

`audit_rating_integrity.py --summary`: **211 rated names | 0 gate violations (no thesis) | 0
stale (>90d).** Clean. Note for awareness (not a violation): MU's most recent context briefing
is 2026-05-26 — still inside the 90-day window as of this scan, but the stalest of the 15
holdings, and now carries two new threads (leadership reshuffle, Taiwan strike risk) — a good
candidate for the next `/refresh-context MU` rotation.

---

## 🎯 Calibration

`resolve_forecasts.py --dry-run`: **0 forecasts due, 0 needing review.** 25 forecasts remain
open; the earliest-maturing batch (`momentum.rel_strength`, logged 2026-06-26) resolves
2026-09-30.

---

## 🔴 Live pipeline

Skipped — cloud/headless session (rule 29: MCP OAuth does not survive headless runs). No
heartbeat/reconcile check performed.

---

## New 13F activity

Q2 2026 13F-HR deadline was 2026-08-14 (prior scan window). This scan checked for
**amendments or late filers** in the 8/21-9/4 window:

| Fund | Status | Notes |
|---|---|---|
| Berkshire Hathaway | Confirmed filed 2026-08-14, no amendment in-window | $299B/29 holdings (cross-confirmed) |
| Baillie Gifford | No new activity found in-window | Search coverage limitation, not a positive "no amendment" confirmation |
| Tiger Global | No new activity confirmed in-window | One ambiguous "filed Sept 4" search snippet could not be corroborated — likely a date-confusion artifact, not treated as confirmed |
| Coatue Management | Confirmed filed 2026-08-14, no amendment in-window | 66 holdings, $48.6B; MU position +~1,800% (165,931→3.14M sh) |
| Lone Pine Capital | No new activity found in-window | — |
| **Whale Rock Capital** | **Now resolved** — confirmed filed 2026-08-14 (predates this window; closes last scan's open "not yet confirmed" gap) | $12.46-12.5B, 35 positions. Top: SNDK, AMD, GOOGL, TTMI, ALAB. **CIK correction**: the repo's tracked CIK (0001485922) matched no fund — corrected to 0001387322 in `weekly_scan_runner.py`, based on secondary-aggregator corroboration (whalewisdom/13f.info/opengovus); recommend primary-EDGAR reverification once access is restored |

**No 13F-HR/A amendments found for any of the six tracked funds this window.** All
position-level detail above is secondary-aggregator sourced (EDGAR direct access blocked) —
treat as directional, not primary-verified, per rule 1.

---

## Routine filings

<details>
<summary>Expand for the full grouped list (confirmed in-window, non-material — dividends,
routine buybacks, insider 10b5-1/144 sales absent a specific flag above, analyst PT changes
without new information, conference appearances, and beat-quarters without a distinct
thesis-relevant angle beyond what's captured above). Several dates below are UNVERIFIED
(search-snippet-only, no confirmed primary date) — flagged inline by the source agents, kept
here for completeness rather than promoted to "material."</summary>

**Power/Utilities:** AEP, DUK, SO, ETR, PPL, XEL, VST, TLN, NRG (see UNVERIFIED guidance-raise
flag above), CCJ, UEC, LEU, SMR, OKLO, NNE, RRC, AR, EXE, PLUG, CMI, GNRC, ETN, ABBNY — routine
dividends/analyst notes only; a broad AI/semiconductor sell-off (8/28-9/1, 10-yr Treasury
yield to ~4.8%) compressed sentiment sector-wide without distinct per-name catalysts.

**Grid/DC construction/cooling:** HUBB, PWR, MTZ, POWL, ATKR, DLR, EQIX, IRM, MOD, CARR, TT,
JCI — no new in-window items beyond routine dividends/conference participation.

**Semi-equipment/materials:** AMAT (board appointment, UBS PT raise — governance/sentiment
only), LRCX (27% dividend raise 8/27 + board-governance transition), KLAC (routine dividend),
TOELY (5:1 split, record date Sept 30 — announcement date unclear), ONTO, CAMT (routine
insider sale), ENTG, MKSI, UCTT, CDNS (down 7.6% 9/1, sector selloff not company news), SNPS
(Investor Day 9/30, future), ARM (AGM in September, PT raise date unclear).

**Fabs/foundry:** INTC (caught in sector selloff, Nova Lake leak unconfirmed), TSEM, GFS (see
item above), UMC (see item above), 0981.HK/SMIC (unverifiable "Sept 17" story excluded),
5347.TWO, HHUSF, CAMT.

**EDA/IP/silicon:** MRVL (see item above), AMD (see Saudi item above), ALGM (broad selloff,
no specific catalyst identified), NXPI (routine Q3 dividend, Malaysia facility groundbreaking
date unclear), QCOM, TXN, ADI, STM, CEVA, LSCC, AMBA (see AMBA data-quality flag above), RMBS,
MPWR, FORM, NVTS (see item above), PLAB (see litigation-deadline item above).

**Optical/networking:** COHR (Deutsche Bank Buy 8/31; price-action driver unclear), LITE
(analyst initiations only), FN, AAOI (UNVERIFIED co-packaged-optics-delay story), POET, CSCO
(Deutsche Bank Buy 8/31), TEL (routine dividend), GLW.

**Servers/storage:** ACLS, COHU (routine Form 4), AMKR, ASX — no new in-window items beyond
routine.

**Cloud/neocloud/BTC-to-AI:** NBIS (Goldman Street-high PT, routine insider sale), APLD (no
in-window operational news; analyst PTs reaffirmed), CIFR, CLSK, RIOT (all: analyst-sentiment
notes only, no new operational catalyst), CRWV (Rescale partnership 8/24, minor), KEEL
(UNVERIFIED low-quality-source items — flag before acting), ORCL (EU antitrust scrutiny
ongoing, no specific in-window filing found; Jefferies PT cut).

**Software/SaaS (non-focus names):** NOW (BofA PT raise, Tech Mahindra partnership — dates
unclear), CSCO/GLW (see above).

**Robotics/foreign/misc (Layer 11 and others):** 6954.T, 6506.T, 6383.T, KGX.DE, 6324.T,
6268.T, 6481.T, 2049.TW, AUTO.OL — no new in-window disclosures; 9880.HK (CICC Buy reiterated,
routine), 2590.HK (IFA Berlin promotional PR, not financial), SSII, TNC (recurring plaintiff
solicitation dating to April, no new disclosure), RRX, ALNT, NOVT, VPG, ALGM, MELE.BR
(buyback updates only), HSAI, AEVA (CFO transition pre-window), MBLY, RCAT (partnership
pre-window), UMAC (routine proxy), PDYN, SYM (small CTO Form 4 sale), OUST (two lidar
partnerships, 8/26 and 9/2 — minor, not elevated to material), 2252.HK (MicroPort MedBot —
could not confirm reported interim results in-window, needs direct HKEX check).

</details>

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🔴 | **VRT-buy ticket `2026-09-04-resize_monthly` expires Sunday 2026-09-06 22:11Z.** If the launchd executor doesn't run on Saturday morning, the month's only resize order dies unexecuted (the next model event regenerates it, but the nine live-vs-model drift flags keep compounding the ~-3.9pp shortfall). Decide: let it lapse, or run `execute_ticket.py` by hand before Sunday night. |
| 🟡 | **AVGO officer selling — rubric question for you (rule 8, not a per-name nudge):** Tan ~40% of pre-holdings ($185M), Brazeal ~49% ($110M, 109 fills), Spears ~26%, none 10b5-1-flagged; one director buy keeps M3 at 4 because rubric step 1 makes buying dispositive. Also **R3 is deferred** to the unfiled Q3 10-Q — the RVG guarantee footnote decides between 4 and 5; check EDGAR for the 10-Q (~mid-Sept). |
| 🟡 | **CRDO is now fully refreshed (81.87 / #4) and re-sized down to 3.57%** — the remaining question is whether the -20% (beat + light guide + concentration) is a one-quarter wobble or the start of a pattern; nothing mechanical pending. |
| 🟡 | **MU's Taiwan union strike-vote risk** — ~10,000 workers, ~80% informal-poll support, heading toward a September vote over profit-sharing terms vs. Samsung/SK Hynix. No strike yet, mediation ongoing. Taiwan hosts ~60% of Micron's production and most HBM output — worth a direct follow-up next scan. Combined with the leadership reshuffle and the fact that MU's context briefing (5/26) is the stalest of the 15 holdings, this is a strong candidate for the next `/refresh-context MU`. |
| 🟡 | **VRT's legal-risk thread widened, not resolved** — a fourth plaintiffs' firm (Hagens Berman) joined 9/1, still pre-litigation solicitation stage with no filed complaint found. Worth tracking for the next R3/R4 subjective-rating refresh rather than treating each week's item in isolation. |
| 🟡 | **AVGO's $60-100B AI-debt financing remains unsigned** through window-end and the Q3 call added nothing on it. PR #53 landed the #51 AVGO `thesis.md` rewrite — verify §9 (thesis-killer #2) now frames the RVG/VIE exposure as contingent debt rather than "exogenous, not AVGO-balance-sheet"; if not, that's the follow-up. |
| 🟡 | **CRM's Q2 FY27 print is the clearest thesis-relevant data point of the week** (+22-23% stock move) but the headline EPS beat is inflated by a non-operating Anthropic-stake gain, and a hard NRR% could not be located despite the disruption-risk mandate making it the most-watched number this quarter — recommend a direct 10-Q pull once EDGAR access is restored, and consider this for the next Layer-10 R5 absolute-lens review given the Claudeforce announcement's double-edged read (validates the data moat but normalizes off-platform CRM access). |
| 🟢 | **Coverage gap, not a data-quality issue:** `P` (Everpure, fka Pure Storage) and `TE` (T1 Energy) got no real news coverage this scan because the sweep agent searched the wrong company names — both are valid Watchlist rows. Carry both into next week's sweep under their correct names. (An earlier version of this scan wrongly flagged them as dead/mistyped tickers — corrected.) |
| 🟢 | **AMBA/NXP acquisition talks** (first reported 7/31, ~$3B+) remain open with no in-window confirmatory update — worth a dedicated follow-up regardless of window boundaries given the deal size. |
| 🟢 | **META resolved two of three open legal threads** ($18B child-safety settlement 8/26; AI-discrimination injunction signal went against plaintiffs 8/24) — both worth folding into the next R3/R4 refresh as reduced (not eliminated) legal-risk exposure. |
| 🟢 | **Whale Rock Capital's tracked CIK was wrong** in `weekly_scan_runner.py` (0001485922 matched no fund) — corrected to 0001387322 based on secondary-aggregator corroboration; flag for primary-EDGAR reverification once access is restored. |
| 🟢 | **A dense earnings week for non-held Layer-10/software names** (CRM, DELL, HPE, SNOW, CIEN, MDB, CRWD, ZS, PANW, INTU, WDAY, ADSK, NTAP) — none triggered a Rule-9 refresh since none are current holdings, but several (PANW, MDB, DDOG-continuation) showed post-beat stock drops on margin/growth-durability concerns, a pattern worth watching across the SaaS cohort broadly, not just the three focus names. |

**Score changes this window (all via Dom's 9/3-9/4 local sessions, merged main):** CRDO
79.72→81.87 (#4), AVGO 77.16→78.7 (#7, panel 9/5); Layer-06 cohort ripple <0.5 elsewhere.
**No tier changes; no membership changes.** One `resize_monthly` model event (9/4) with one
open trade ticket (VRT buy, expires 9/6). This scan itself made no score edits.
