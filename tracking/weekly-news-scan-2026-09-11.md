# Weekly News Scan — 2026-09-11

**Scope:** 214 watchlist tickers. Scan window: **2026-09-04 – 2026-09-11**.

## Same-day follow-up (post-scan action items worked, still 2026-09-11)

Dom asked for all of the scan's action items to be worked same-day. Results:

- **AVGO R3 (partially resolved):** The Q3 FY26 10-Q (`avgo-20260802.htm`) has been filed and
  does contain formal contingent-liability language on the AI XPV platform's residual value
  guarantees ("contingent liabilities [Broadcom] believe[s] would have a low probability of
  occurring...") — the accounting-treatment question from thesis-killer #2 is answered: yes,
  it's now a filed disclosure, not only a verbal characterization. On size: asked about
  incremental exposure on the 9/2 call, management said there's "nothing new to add" beyond
  the existing ~$29B max on the initial $35B tranche — no escalation. The separate $60-100B
  second financing package remains unsigned. Written up in `per-stock/AVGO/thesis.md` §9 and
  `news-log.md`; **R3 rating itself left to Dom/the collaborative process (rule 2/8), not
  changed here.**
- **VRT UtilityInnovation deal — now primary-confirmed:** WebSearch surfaced the actual
  SEC-indexed 8-K content (accession 000119312526379306, signed by CFO Craig Chamberlin,
  merger agreement dated 9/1) — terms as previously reported ($1.45B cash + up to $1.15B
  earnout in two EBITDA-gated tranches, ~13x 2027E EBITDA, Q4 2026 close, JPM/Morgan Stanley
  advising). Upgraded from "secondary-sourced" to "primary-confirmed" in
  `per-stock/VRT/news-log.md`.
- **CRM NRR — settled as a finding, not a gap:** a fourth consecutive search (FY26 10-K, Q1/Q2
  FY27 releases, revenue-recognition disclosure aggregators) found no NRR percentage anywhere
  in Salesforce's disclosures. This now reads as a genuine disclosure-practice shift toward
  RPO/cRPO rather than a search-coverage problem. Logged in `per-stock/CRM/news-log.md` with a
  decision flagged for Dom: adopt cRPO growth as the go-forward proxy, keep flagging the
  absence, or treat it as settled.
- **13F CIK fixes — re-confirmed at a higher confidence level:** WebSearch surfacing
  EDGAR-indexed filing titles now directly names all three corrected/re-verified funds
  ("BAILLIE GIFFORD & CO", "COATUE MANAGEMENT LLC" signed by Philippe Laffont, "Whale Rock
  Capital Management LLC" signed by Alex Sacerdote) with matching addresses — about as strong
  as evidence gets without a direct sec.gov fetch (still blocked this session). Code comments
  in `scripts/weekly_scan_runner.py` updated accordingly.
- **AMZN `/refresh-context` run:** AMZN had no populated `thesis.md` and no prior context
  briefing despite being a live holding — first briefing written
  (`per-stock/AMZN/context-2026-09-11.md`). Headline findings: the Amazon-Anthropic
  relationship is a $100B/decade committed-spend contract (4/20/2026) with $13B cumulative
  equity investment and up to 5GW of dedicated Trainium capacity; AWS's AI and Chips
  businesses each independently crossed a $25B annualized run-rate in Q2 2026; Trainium
  external sales remain talks-only; and **the original 2023 FTC monopoly antitrust case
  (distinct from the 8/31 ad-surcharge suit) has a trial date of 2026-10-13** — a much sharper
  near-term catalyst than "an ongoing suit." Quantitative red-flag scripts (2b-2e) were all
  network-blocked; rating implications flagged, not decided.
- **ORCL `/refresh-objective --dry-run`:** ran clean but made zero changes — Yahoo Finance
  fetch failed with the same `403`/`ConnectionError` pattern as every other network call this
  session (`Cookie/crumb fetch failed`, `curl: (7) CONNECT tunnel failed, response 403`). The
  script's own guarantee ("a failed fetch never clobbers an existing value") held — ORCL's row
  is untouched, not silently corrupted. **Genuinely blocked, not attempted by hand** — ORCL's
  objective inputs need a network-enabled session.
- **NTAP capitulation check:** still genuinely blocked. `capitulation_flag.py` requires a live
  SEC XBRL quarterly-revenue pull plus 3 years of yfinance daily price history to compute a
  P/S percentile — this cannot be responsibly hand-approximated from WebSearch snippets
  without breaking the rule-17 calibration loop's precision guarantees. Confirmed via a direct
  test: `ProxyError... Tunnel connection failed: 403 Forbidden` on
  `www.sec.gov/files/company_tickers.json`. Recommend running
  `python3 scripts/capitulation_flag.py NTAP --log-forecast` from a network-enabled session
  before the exit confirms (no earlier than 2026-09-15).
- **MU Taiwan situation:** no action item beyond monitoring — next mediation session is
  9/21, outside this window; nothing to do until then.

## Execution note (network constraints — unchanged since 2026-06-12)

SEC EDGAR (`data.sec.gov`, `www.sec.gov`, `efts.sec.gov`) and Yahoo Finance
(`query1/2.finance.yahoo.com`) are confirmed 403-blocked from this session's egress proxy
(verified via direct `curl` and `WebFetch` before starting — both return `connect_rejected` /
`EGRESS_BLOCKED`). `WebFetch` to any `sec.gov` subdomain is also blocked. `WebSearch`,
however, works and surfaces SEC-filing content and news adequately. Substituted the same
`web_scan.py`-style fallback methodology used every scan since 2026-06-12, executed through
**10 parallel research agents**: 3 covering the 17 portfolio holdings in depth (NVDA/MU/TSM/
SNDK/ALAB/NTAP; CRDO/ANET/VRT/FIX/EME; MSFT/AVGO/META/GMED/RDDT/AMZN), 1 on the Layer-10 SaaS
thematic mandate (PLTR/DDOG/CRM — NRR/AI-adoption/pricing focus), 1 covering 22 non-held
high-tier watchlist names, 4 sweeping the remaining ~172 tail tickers (~43 each), and 1
checking the six tracked funds' 13F-HR status. **All 214 tickers received at least one query
this week.** Local, non-network scripts ran clean: `audit_rating_integrity.py --summary` (211
rated, 0 gate violations, 0 stale), `resolve_forecasts.py --dry-run` (0 due, 0 needing
review), `refresh_targets.py --check` (Targets reflect current scores, no pending rebalance).
`capitulation_flag.py`, `momentum_50dma.py`, and a live `refresh_targets.py`/
`track_performance.py` run all require yfinance/SEC and remain blocked this session — the
already-committed state from Dom's local sessions (through 2026-09-10) is read below, not
independently re-verified.

**Data-quality fix this scan:** the 13F-check agent found that two more tracked-fund CIKs in
`scripts/weekly_scan_runner.py` were wrong (same failure class as the Whale Rock CIK fixed
2026-09-04) — **Baillie Gifford**'s configured CIK (0001048268) resolves to IES Holdings, Inc.
(an unrelated electrical contractor), and **Coatue Management**'s (0001336528) resolves to
Pershing Square Capital Management, L.P. (Bill Ackman's fund). Corrected to 0001088875
(Baillie Gifford) and 0001135730 (Coatue), based on WebSearch of EDGAR-indexed filing titles
(secondary evidence, not a primary-EDGAR fetch — flagged for reverification once access is
restored, same standard as the Whale Rock fix). **Practical effect: every 13F check run since
this script existed has likely been silently polling the wrong two entities for Baillie
Gifford and Coatue.**

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

17 current holdings (up from 15 last week — **AMZN entered** rank 15/tradable on the 9/7
rule-9 refresh; **NTAP entered** the same day at rank 15/tradable, then a same-week
ROIC-methodology deploy (rule 34, 9/8) pushed it to tradable rank 20, starting an
EXIT-PENDING clock seam-damped to confirm no earlier than 2026-09-15): **NVDA, FIX, TSM,
CRDO, AVGO, ANET, SNDK, MSFT, MU, GMED, ALAB, EME, VRT, RDDT, NTAP, AMZN, META.**

Going in: **NVDA** dominant AI-accelerator vendor, confirmed $12.93B Hugging Face deal, open
Burry-short/CXMT-competition/$500B-financing/$105B-SB-Energy threads. **MU** HBM-bottleneck
beneficiary, 8/26 C-suite reshuffle (Sadana→Senior Advisor) and Taiwan strike-vote thread
still unresolved, stalest context briefing of the 15 — refreshed 9/7-9/8. **TSM** sole
leading-edge foundry, no red flags. **CRDO** optical/AEC interconnect, fully refreshed post
the -20% post-beat drop, Marvell/Celestial-AI thread open. **AVGO** custom-ASIC name,
$60-100B AI-debt financing unsigned, R3 deferred to the unfiled 10-Q. **ANET** clean,
tracking hyperscaler capex/Spectrum-X competition. **SNDK** watching NAND-shortage guidance.
**MSFT** Azure/AI growth, open Guardian AI-chip-count dispute. **GMED** distinct Layer-11
surgical-robotics thesis. **ALAB** watching MRVL share-loss evidence. **EME** ~$700M pending
acquisitions slated Q3 close. **VRT** widening (4-firm) pre-litigation securities-fraud
solicitation thread. **RDDT** thinnest-research position, Google-licensing/DAU-decline/Hatch
threads open. **NTAP** strong FQ1 print (9/2) then EXIT-PENDING purely on the ROIC
methodology recompute — a mechanism change, not fundamental deterioration. **AMZN** brand-new
entrant, FTC ad-surcharge suit the one known open item, otherwise under-researched relative to
the other 16. **META** two of three legal threads resolved, Hatch AI-agent launch pending.

**Diff against this week's scan — six genuine developments, no thesis breaks:**
1. **VRT signed a ~$1.45B cash (+$1.15B earnout) definitive acquisition of UtilityInnovation
   Group** (microgrid/behind-the-meter power), extending upstream into grid interconnect — a
   real strategic move buried one day before the strict window, not previously known.
2. **MU's Taiwan labor dispute escalated procedurally but not materially**: first mediation
   (9/4) failed, a second session is set for 9/21, and Micron announced (9/11) its largest-ever
   employee bonus program — read as a direct response to the profit-sharing demand. Separately,
   a Netlist Federal Circuit appeal had oral arguments 9/9 (legal-risk thread, not new
   exposure) and a DOJ antitrust inquiry into NVDA's Groq deal (9/9-10) touches the CXMT/memory
   competitive backdrop MU shares.
3. **MSFT picked up a second legal thread** (Seattle Times/Newsday copyright suits vs.
   OpenAI/Microsoft) alongside a positive trust signal (AFT/UFT AI-safety agreement) — the
   Guardian dispute itself remains unresolved.
4. **META's "Hatch"/"Muse" AI agent launched 9/8**, resolving last week's open thread and
   directly touching RDDT (Reddit is a named data source).
5. **AMZN, now a full holding, got its first standalone-governance item** (Kevin Mandia
   elected to the board, 9/8) with no update on the FTC ad-surcharge suit.
6. **NTAP's EXIT PENDING status is mechanical, not a company event** — no new company-specific
   news found this window; the clock is entirely a function of the rule-34 ROIC deploy and is
   seam-damped (rule 32-C) until 2026-09-15, so nothing confirms this week regardless.

Everything else (TSM, SNDK price action, ANET, FIX, EME, GMED, ALAB, RDDT, AVGO) is detailed
below but does not change the standing model.

---

## ⚠️ Material events

### Portfolio holdings

**NVDA**
- **[2026-09-09/10]** ⚠️ DOJ opened an antitrust investigation into whether Nvidia structured
  its ~$20B non-exclusive licensing deal with Groq to avoid merger review; a formal
  information demand has been sent. — [Bloomberg](https://www.bloomberg.com/news/articles/2026-09-10/doj-probes-nvidia-s-license-deal-with-groq-on-antitrust-concerns), [Axios](https://www.axios.com/2026/09/10/doj-nvidia-groq-antitrust)
- **[2026-09-09]** Michael Burry disclosed (Substack) he closed his December-2026-expiry NVDA
  and PLTR puts without rolling to later contracts — framed as portfolio-wide risk reduction,
  **not** a reversal of the bearish thesis (he retains other short exposure and 2027-dated
  PLTR/QQQ puts). — [Yahoo Finance](https://finance.yahoo.com/markets/options/articles/michael-burry-dumps-nvidia-palantir-194635018.html)
- **[2026-09-11, thread update]** Nikkei Asia: China's CXMT posted an 82% Q2 2026 operating
  margin — above SK Hynix (76%) and Samsung (70%) — as Korean makers reallocate capacity to
  HBM; CXMT separately reached HBM3E risk production in early September, shipping
  qualification batches to Alibaba T-Head and Cambricon (exact date UNVERIFIED). Relevant to
  the open CXMT-competition thread for both NVDA and MU. — [Seoul Economic Daily/Nikkei](https://en.sedaily.com/international/2026/09/11/chinas-cxmt-tops-sk-hynix-in-memory-profit-margin)

**MU**
- **[2026-09-11]** ⚠️ Announced company-wide "fiscal 2026 rewards" for 60,000+ employees —
  described as the largest bonus program in company history; Taiwan direct-labor employees get
  35-68 months' pay. Lands squarely inside the open strike-vote thread and reads as a direct
  response to the profit-sharing dispute. — [Focus Taiwan](https://focustaiwan.tw/business/202609110009)
- **[2026-09-04]** ⚠️ First formal mediation session with the two Taiwan unions ended without
  agreement; a second session is scheduled for 2026-09-21 (outside this window). No strike
  vote formally called as of 9/11. — [Gate.com](https://www.gate.com/en-us/news/detail/micron-taiwan-labor-union-reach-no-consensus-in-first-mediation-on-17862341)
- **[2026-09-09]** ⚠️ Federal Circuit heard oral arguments in Netlist v. Micron Technology
  Texas (No. 2025-1936), an appeal tied to an earlier willful-infringement jury verdict; MU
  shares fell ~3-5% around 9/10, partly attributed to renewed legal-risk concern (Netlist's
  8/12 ITC exclusion-order complaint on DDR5/MRDIMM also remains pending). A separate,
  favorable-to-Micron Federal Circuit ruling invalidating five Netlist patents landed 9/2 (just
  outside window) — background only. — [CAFC.uscourts.gov](https://www.cafc.uscourts.gov/09-09-2026-2025-1936-netlist-inc-v-micron-technology-texas-llc-audio-uploaded/)
- CXMT margin thread — see NVDA above; relevant to MU as well.

**TSM** — no new company-specific material items. Routine: August monthly revenue NT$514.81B
(+53.3% YoY, +10.1% MoM), $1.114/share dividend ex-date 9/16.

**SNDK**
- **[on/after 2026-09-05]** ⚠️ Raised prices ~10% across channel partners and consumer
  products, effective on new orders — a direct pricing action confirming the NAND-shortage
  thesis flagged as a watch item last scan. — [FX Leaders](https://www.fxleaders.com/news/2026/09/04/sndk-stock-breaks-resistance-as-nand-demand-strengthens-sandisk-but-memory-risks-remain/)

**CRDO** — no new material items. CTO Lawrence Cheng sold ~3,790 shares (~$644K, 10b5-1 plan)
on 9/4 — de minimis. No update on the Marvell/Celestial-AI competitive thread.

**ANET** — no new material items. S&P Dow Jones announced ANET joins the S&P 100 effective
9/21 (index mechanics, not fundamental — explains some recent strength).

**VRT**
- **[2026-09-02, one day pre-window — new information, not previously known]** ⚠️ Definitive
  agreement to acquire **Utility Innovation Holdings, Inc. ("UtilityInnovation Group")** — a
  microgrid/behind-the-meter power and advanced power-controls provider for data centers — for
  ~$1.45B cash at close plus up to $1.15B in earnout (max ~$2.6B, ~13x 2027E EBITDA); expected
  to close Q4 2026, expected EPS-accretive in year one. Extends Vertiv upstream into grid
  interconnect/power orchestration. — [Vertiv IR](https://investors.vertiv.com/news/news-details/2026/Vertiv-Announces-Agreement-to-Acquire-UtilityInnovation-Group-to-Accelerate-Time-to-Power-for-AI-Data-Centers/default.aspx), [HPCwire](https://www.hpcwire.com/off-the-wire/vertiv-to-acquire-utilityinnovation-group-for-1-45b/) — **dates/terms corroborated across secondary sources only; direct SEC/IR fetch blocked, so treat as reasonably confident, not primary-verified.**
- Legal thread: still pre-litigation — no filed complaint or SEC action confirmed. Two
  additional firms (Grabar Law, Robbins LLP) posted "investigating" ads, which is solicitation
  noise, not escalation.

**FIX** — no new material items. Continued positive analyst revisions (UBS PT to $2,225);
no update on the Brian Lane sale thread.

**EME** — no new items. The ~$700M pending electrical-contractor acquisitions have not been
confirmed closed via any 8-K/press release found this window.

**MSFT**
- **[2026-09-05 to 09-08]** ⚠️ Two more publishers — the Seattle Times and Newsday — sued
  OpenAI and Microsoft for copyright infringement, alleging systematic scraping of paywalled
  journalism to train AI models. A new legal-risk thread, adjacent to but distinct from the
  Guardian dispute. — [TechCrunch](https://techcrunch.com/2026/09/05/seattle-times-and-newsday-are-the-latest-publications-to-sue-openai-and-microsoft/)
- **[2026-09-09]** Signed a legally enforceable national AI-safety/privacy standard with
  AFT/UFT teachers' unions — contractually liable if student data is used to train AI or AI
  makes unsupervised decisions in schools; rolls out to US districts starting 11/1. A new
  compliance/liability surface, but also a trust signal for Education/Azure adoption. —
  [Engadget](https://www.engadget.com/2254167/microsoft-strikes-deal-with-national-teachers-union-to-not-use-school-data-to-train-ai/)
- Guardian AI-chip-count dispute: **still unresolved**, no new detail from Microsoft this
  window beyond Nadella reframing it as a power/construction constraint.

**AVGO**
- **[10-Q filed, officer certs signed 2026-09-09]** The expected mid-September 10-Q has been
  filed. **Could not verify via WebSearch/secondary sources whether the RVG/VIE guarantee
  footnote language resolves the open R3 question** — direct-read access to sec.gov is
  blocked this session. **Recommend Dom pull `avgo-20260802.htm` directly next session.**
- $60-100B AI-chip debt financing (Blackstone/Apollo SPV structure) remains **UNSIGNED**
  through window-end; terms still described as "in talks."
- No new AVGO-specific liability disclosure on the ongoing VMware vCenter CVE-2026-59310
  exploitation.

**META**
- **[2026-09-08]** ⚠️ Launched its consumer AI agent ("Muse"/"Hatch") in the US via standalone
  app and WhatsApp (free/$20/$100 tiers, autonomous multi-step tasks) — **resolves** last
  week's "targeted for early September" open thread. Explicitly integrates Reddit, DoorDash,
  Etsy, Yelp, and Outlook as connected data sources. — [Axios](https://www.axios.com/2026/09/08/meta-debuts-muse-personal-ai-agent), [TechCrunch](https://techcrunch.com/2026/09/08/meta-debuts-its-muse-ai-agent-will-consumers-trust-it/)
- AI-layoff-discrimination case: no final order this window (7/17 TRO denial with Judge Orrick
  flagging "serious questions" remains the most recent ruling).

**GMED** — no in-window material items beyond the already-known Higgs Boson Health
acquisition. The Excelsius3D CE Mark announcement (9/3) falls just pre-window.

**RDDT**
- **[cross-reference, 2026-09-08]** Meta's Hatch/Muse launch explicitly connects to Reddit
  content — moves the "Meta AI agent surfaces Reddit content" thread from speculative to
  confirmed/live (see META above).
- No movement on the Google content-licensing-renewal or US-DAU-decline threads this window.

**AMZN** (new holding — fuller sweep)
- **[8-K, filed 2026-09-08, certified 09-09]** Elected **Kevin Mandia** (former Mandiant/
  FireEye CEO, cybersecurity background) to Amazon's board, with a standard director RSU
  grant. Governance item, not a security-incident response — full filing text unverified
  (sec.gov blocked). — [SEC EDGAR](https://www.sec.gov/Archives/edgar/data/0001018724/000101872426000036/amzn-20260908.htm)
- No confirmed litigation response to the FTC/22-state "secret ad surcharge" suit (8/31) found
  this window. No new AWS/AI capex guidance, no exec departures.

### Layer-10 SaaS thematic focus (PLTR / DDOG / CRM) — NRR / AI adoption / pricing

**CRM (Salesforce)**
- **[2026-09-10]** ⚠️ Completed the **Fin (Intercom) acquisition** (~$3.6B cash) — months
  ahead of the original Q4 FY27 schedule; Fin's AI customer-service platform serves 30,000+
  companies, stated 76% end-to-end resolution rate. — [Salesforce](https://www.salesforce.com/news/press-releases/2026/09/10/salesforce-completes-acquisition-of-fin/)
- **[2026-09-10]** ⚠️ Reportedly in preliminary/non-binding talks to acquire **Listen Labs**
  for ~$2B (~67x its ~$30M ARR, a ~4x markup from an $500M valuation eight months prior) —
  would be Salesforce's 4th AI-related deal in 2026. — [Business Insider via Yahoo](https://finance.yahoo.com/technology/ai/articles/salesforce-2b-talks-acquire-listen-091244424.html)
- **NRR: still not found.** Repeated targeted searches of the Q2 FY27 10-Q MD&A and IR
  materials again failed to surface a hard NRR/net-dollar-expansion percentage. **Flag per
  rule 3: this looks like Salesforce may simply no longer be disclosing this metric, not a
  search-coverage gap** — worth a direct primary-10-Q read once EDGAR access is restored.
- **AI-adoption detail (webinar 9/1, three days pre-window but not previously in the
  baseline):** 7.0B cumulative Agentic Work Units delivered across Agentforce + Slack,
  3.2B in Q2 alone (+97% QoQ); Agentforce for IT Service now >450 customers including
  ServiceNow migrations.
- No new pricing-model change found (still three concurrent architectures: per-AWU, flex-
  credit, per-seat $125/user/month).

**PLTR**
- **[2026-09-10]** ⚠️ NVIDIA/Palantir launched a joint "Sovereign AI Operating System" stack
  (Nemotron models inside Foundry/AIP) at AIPCon 11, first deployed in NVIDIA's own supply
  chain, with Cisco/Dell as manufacturing partners; customer showcases include FAA, L3Harris,
  Novartis. — [Business Wire](https://www.businesswire.com/news/home/20260910834032/en/NVIDIA-and-Palantir-Bring-Sovereign-Intelligence-to-Critical-Supply-Chains)
- **[~2026-09-02/05]** Michael Burry renewed his bearish PLTR thesis, reframing it as
  structurally "a consultant, not a software company" (deferred-revenue-to-revenue ratio
  tracks Accenture, not SaaS peers), reiterating a scenario where market cap could fall below
  $100B from ~$432B. — [Motley Fool](https://www.fool.com/investing/2026/09/05/michael-burry-says-palantir-s-books-look-more-like-a-consultant-s-than-a-software-company-s/)
- **NRR clarified (not new — resolves last week's open item):** Q2 2026 NRR was **157%,
  +700bps sequentially** — reconciles the previously-flagged discrepancy (the ~150% figure was
  Q1's). Sourced from the Q2 release (8/3-8/10), predates this window.

**DDOG** — no new NRR, AI-feature-adoption, or pricing disclosure found this window.
Conference appearances at Citi (9/8) and Goldman Communacopia (9/10); **full transcripts were
inaccessible (Seeking Alpha/Gurufocus blocked), so a possible updated NRR figure from CFO
Obstler at Communacopia could not be confirmed either way — flagged as a gap, not a null
result.** Stock got a sentiment tailwind from Snowflake's 9/2 beat reinforcing an "AI expands
infra spend" narrative — not DDOG-specific news.

### Non-held high-tier watchlist

- **GOOGL** — **[2026-09-09]** ⚠️ Announced a record $15.1B AI-infrastructure investment in
  Finland. No new development on the AdX antitrust remedy since the 9/2 ruling. —
  [CNBC](https://www.cnbc.com/2026/09/09/google-finland-ai-infrastructure-investment.html)
- **ORCL** — **[2026-09-10]** ⚠️ Reported Q1 FY2027: revenue $19.3B (+30% YoY), cloud
  infrastructure +121% YoY, RPO swelled to $664B (+$30B in new AI contracts this quarter alone),
  raised FY27 revenue guide to $90B+; stock +7% premarket. **This is a rule-9-magnitude beat
  for a non-held name — recommend prioritizing ORCL for `/refresh-objective` given the size of
  the RPO jump and stock reaction; not actioned this scan (non-holding, "within 1 week"
  priority, and yfinance is blocked this session regardless).** — [CNBC](https://www.cnbc.com/2026/09/10/oracle-orcl-q1-earnings-report-2027.html)
- **DELL** — **[2026-09-09]** Priced an upsized $5B investment-grade bond offering (5x
  oversubscribed) to refinance 2026 first-lien notes.
- **WDC** — no new items; Kioxia merger-talk thread remains open with no in-window update.
- **6268.T (Nabtesco)** — disclosed a five-year (FY2021-25) restatement for unrecorded
  equity-method investment income (~¥2.8B); refiling due late September. **Announcement date
  is ~8/14, likely pre-window — flagging because the refiling deadline falls near this period
  and no in-window confirmation of an actual refiling was found.**
- TER, APH, ISRG, CGNX, EQT, CIEN, 6861.T, KEYS, AR, FN, APP, ARM, HSAI, BSL.DE, ADSK, HTHIY,
  RMBS — **no in-window material items** beyond what was already known.

### Long-tail (172 names) — selected material items by sub-sector

**Grid/DC infrastructure/fiber:**
- **GLW** — [9/8] ⚠️ Multi-year, multi-billion-dollar supply agreement with Verizon
  (2027-2032) for 80M+ miles of optical fiber for AI/broadband buildout; stock +7-9%.
- **VST** — [9/4-9/10] Priced $1.5B junior subordinated notes (financing to redeem existing
  preferred stock at reset dates).
- **NBIS** — [9/8] Palantir named Nebius its preferred sovereign-AI infrastructure partner
  (compute/inference inside Palantir's enterprise perimeter); no disclosed dollar figure.

**Semi-equipment/materials/foundries:**
- **AMKR** — [9/8] ⚠️ Phase 2 Arizona advanced-packaging campus, raising total commitment to
  ~$12B (nearly tripling cleanroom capacity, target completion end-2029).
- **ASML** — [9/7-9/8] Samsung High-NA EUV collaboration expanded; ASML/TSMC announced a joint
  initiative to transition to 12-inch photomasks for High-NA EUV.
- **GFS** — [9/8] $375M DoC R&D award for quantum tech; [9/9] long-term manufacturing
  partnership with Monolithic Power Systems (MPS process tech, Singapore 300mm fab).
- **TTMI** — [9/10] Priced $500M senior notes to fund the previously-announced Epiq
  Solutions/STG-ILFA acquisitions.
- **KLIC** — Dr. Raj Talluri became President/CEO effective 9/1 (announced 8/17, market
  digestion continued into this window).
- **INTC** — reported ~$15-20B secondary equity raise (dilution concerns, priced ~9/8) plus an
  Altera IPO reportedly targeting >$2B — **exact pricing date UNVERIFIED, recommend
  confirming before treating as final.**
- **SWKS** — [9/10-11] CEO said the $22B Skyworks-Qorvo merger is in "final stages," only two
  regulatory jurisdictions remaining; stock +9.8% then +7% follow-through.
- **AMBA** — NXP acquisition talks (open since 7/31) remain **unconfirmed** as of 9/11 — no
  definitive agreement; one low-quality aggregator claimed the deal was "finalized this week,"
  **not corroborated by any reliable source, not treated as fact.** AMBA's 9/3 Q2 earnings
  beat, not deal news, appears to be driving the stock this week.
- **AIP/AEVA** — Saurabh Sinha departed as AEVA CFO (9/5) to become Arteris (AIP) CFO (9/8) —
  same individual, two companies, same week.

**Software/AI agents:**
- **ADBE** — **[2026-09-03, one day pre-window, not previously known]** ⚠️ CEO succession:
  Anil Chakravarthy named President/CEO effective 12/1/2026; Shantanu Narayen becomes
  Executive Chair. — [Adobe Newsroom](https://news.adobe.com/news/2026/09/adobe-announces-anil-chakravarthy-to-become-president-and-ceo)
- **PANW** — **[9/1, boundary, not previously known]** ⚠️ Acquired AI-agent startup Console
  (~$500M reported).
- **SNOW, FLEX** — both already reported in last week's (2026-09-04) scan (SNOW's 9/2 Q2 beat;
  FLEX's 9/3 $4.4B EPC Power acquisition) — **not re-flagged as new this week.**

**Nuclear/uranium financing:**
- **LEU** — [9/10] ⚠️ Priced a $500M dilutive stock-and-warrant offering; shares -8.6%.
- **OKLO** — [9/11] New $1B ATM equity program replacing a terminated prior one; shares -3.5%.

**Robotics/defense:**
- **AVAV** — [9/9] ⚠️ FQ1'27: record revenue $480.5M (+6% YoY), EPS $0.59 (vs. $0.30 est.),
  record backlog $1.5B (+37% YoY), book-to-bill 1.4x.

**AI-capacity/neocloud cohort:**
- **IREN** — [9/8] Co-CEO publicly acknowledged the gap between $70.5M quarterly AI-cloud
  revenue and a claimed ~$1B annualized run-rate at a Goldman conference ("mega-deal
  announcements no longer move the stock"); shares -3.3%. Relevant to AI-revenue-delivery
  thesis risk across the cohort.
- **P (Everpure, fka Pure Storage)** — [9/4-9/8] Joining the S&P 500 effective 9/21,
  replacing Builders FirstSource.
- **SEI (Solaris Energy Infrastructure)** — [9/8] ⚠️ Sharply raised Q3/Q4 2026 adjusted EBITDA
  guidance (+23%/+48% at midpoint) and gave an initial Q1'27 guide; shares +16.5%.

**Other notable, dated at/just outside the strict window (flagged for completeness):**
- **AAPL** — [9/9] Product launch event (foldable iPhone Duo, iPhone 18 Pro/Max, Siri AI
  relaunch); coverage described this as John Ternus' first keynote as CEO succeeding Tim Cook —
  **this CEO-transition claim is UNVERIFIED and could not be corroborated against a primary
  announcement; flagging with real uncertainty rather than reporting as confirmed fact.**
- **TSLA** — [9/4] Cybercab launch drew a negative reaction (stock -6%) and triggered an NHTSA
  safety audit.

**Data-quality flags for the ticker map:** "2498.HK" in the watchlist could not be matched to
a real HKEX listing — search results only return HTC Corp (Taiwan-listed as 2498.TW/2498.TT);
**likely a ticker-mapping error, needs correction.** "2049.TW" was confirmed as HIWIN
Technologies (not Ares International, which trades as 2471.TW) — no action needed, just
confirming the existing mapping is correct. "KEEL" and "WYFI" remain thinly covered by
search — any items sourced from them this week are flagged inline as low-confidence.

---

## 📊 Earnings refreshed

**No portfolio holding reported new earnings inside the strict 9/4-9/11 window** (CRDO/AVGO
reported before 9/4 and were refreshed in last week's scan; NTAP reported 9/2 and was refreshed
via the 2026-09-07 rule-9 pass — before this scan's window, but worth summarizing since it
drove this week's only membership-adjacent event):

| Ticker | Print | Refresh | Result |
|---|---|---|---|
| NTAP | FQ1 2027, 9/2 | rule-9 objective refresh, 2026-09-07 | 69.2 ✓ → 73.0 ✓✓ (+3.7), tradable rank 26 → 15, **ENTER** |

That NTAP entry was itself immediately overtaken by the rule-34 ROIC methodology deploy the
next day (9/8) — see 💼 Portfolio pipeline below.

**Rule-9 candidate flagged, not actioned (non-holding):** **ORCL**'s 9/10 beat (RPO +$30B
in-quarter, raised FY27 guide) is large enough to warrant an objective refresh once network
access allows — recommend prioritizing it next session given the magnitude, even though it's
not a current holding (rule 9's "within 1 week" priority, not "immediate," applies since it
isn't held).

**Not refreshed this scan (non-held, network-blocked):** SNOW (9/2), AVAV (9/9), SEI (9/8) all
reported strong or mixed quarters in-window — none are current holdings, none actionable this
session given the yfinance block.

---

## 💼 Portfolio pipeline

- **No model event fired since 2026-09-08** (+AMZN membership). `refresh_targets.py --check`
  confirms Targets reflect current scores — no pending rebalance as of this scan.
- **NTAP is EXIT PENDING** (tradable rank 20 > exit rank 18, clock started 2026-09-08) — this
  is a pure side-effect of the rule-34 ROIC-methodology deploy, not a company-specific
  deterioration (no new NTAP news found this window — see above). The exit clock is
  **seam-damped to 2026-09-15** under rule 32-C (the ROIC deploy itself stamped the
  methodology seam) — it **cannot confirm before next week's scan (2026-09-18)** even if it
  stays below the exit rank. Flagging now so the eventual EXIT isn't a surprise.
- **Sizing:** equal-weight (rule 33, flipped 2026-09-07) — all 17 holdings carry equal target
  weight (~5.88% each of the invested book as of the last Targets refresh). Monthly drift-band
  resize check last ran 2026-09.
- **Live account (sanitized `live-status.json`, as of 2026-09-10):** **not halted**
  (recovers from a `halted=true` state briefly raised 2026-09-08 after a ticket refusal — since
  resolved locally), 15 positions, 0 open orders, 0 anomalies, **16 drift flags** (ALAB, AMZN,
  ANET, AVGO, CRDO, EME, GMED, META, MSFT, MU, NTAP, NVDA, RDDT, SNDK, TSM, VRT — i.e. nearly
  the whole book), and **1 unrepaired leg (VRT)**. This reflects Dom's local session state, not
  an independent reconciliation by this cloud session (rule 29 — Step 10 skipped, headless MCP
  OAuth unavailable).
- **Weekly mark** (`tracking/performance-series.json`, current through **2026-09-10**):

  | | Window (9/04→9/10) | Since inception (5/26) |
  |---|---|---|
  | **Model** | **-2.42%** ($10,086.38 → $9,842.02) | **-1.58%** |
  | SMH | -1.19% | — |
  | QQQ | -1.43% | — |
  | SPY | -1.60% | — |
  | Equal-weight universe (EW) | -2.04% | — |
  | EW twin of model roster (EW_ROSTER) | -2.79% | — |
  | INVVOL_ROSTER (rule-33 mirror shadow) | data begins 9/8, 3 points only — too short to read |
  | BAND_TOP (ranks 1-15) | -3.13% | — |
  | BAND_NEXT (ranks 16-25) | -1.13% | — |
  | BAND_TAIL (ranks 26-40) | -1.20% | — |

  A rough week across the board (broad AI/semiconductor sell-off, ~10yr yield pressure noted
  in prior scans) — the model (-2.42%) underperformed every named benchmark this window but
  **beat its own EW_ROSTER shadow by +0.37pp**, consistent with the 2026-09-10 recon commit
  message. BAND_TOP was the worst-performing band this week (-3.13%, opposite of last week's
  pattern where BAND_NEXT lagged) — one data point, not yet a pattern worth acting on (rule 28:
  don't tune against short windows).
- No concentration, layer-cap, dead-ticker, or manual-override-collision flags found.

---

## 🩸 Capitulation flags

**NTAP is EXIT PENDING this run**, which per Step 7d should trigger `capitulation_flag.py
NTAP --log-forecast`. **Could not run — the script requires a live SEC EDGAR CIK lookup
(`common.py: load_ticker_to_cik`), and SEC access is blocked this session** (confirmed via a
direct test: `ProxyError... Tunnel connection failed: 403 Forbidden` on
`www.sec.gov/files/company_tickers.json`). Flagging the gap rather than fabricating a result —
recommend running `python3 scripts/capitulation_flag.py NTAP --log-forecast` from a
network-enabled session before the exit confirms on/after 2026-09-15.

---

## 🔬 Rating integrity

`audit_rating_integrity.py --summary`: **211 rated names | 0 gate violations (no thesis) | 0
stale (>90d).** Clean. AMZN (new entrant) is not yet a rated name requiring the gate per se,
but has the thinnest research base of the 17 holdings — worth an early `/refresh-context AMZN`
given it just entered the portfolio without the deep-dive treatment the other 16 have
accumulated.

---

## 🎯 Calibration

`resolve_forecasts.py --dry-run`: **0 forecasts due, 0 needing review.** No change from last
scan — the earliest-maturing batch (`momentum.rel_strength`, logged 2026-06-26) still resolves
2026-09-30.

---

## 🔴 Live pipeline

Skipped per rule 29 — cloud/headless session (MCP OAuth does not survive headless runs). For
awareness only (read from the already-committed, sanitized `tracking/live-status.json`, not
independently reconciled this session): as of 2026-09-10, **not halted**, 0 open orders, 0
anomalies, 16 drift flags, 1 unrepaired leg (VRT) — see 💼 Portfolio pipeline above for detail.
A `halted=true` state was briefly raised 2026-09-08 after a ticket refusal and has since
cleared per Dom's local sessions.

---

## New 13F activity

Q2 2026 13F-HR deadline was 2026-08-14 (all six tracked funds confirmed filed on/around that
date across prior scans). This scan checked for **amendments** in the 9/4-9/11 window and
additionally **audited all six tracked CIKs** given the Whale Rock precedent:

| Fund | CIK (as of this scan) | Status |
|---|---|---|
| Berkshire Hathaway | 0001067983 | ✅ Confirmed correct; no amendment found in-window |
| Baillie Gifford | **0001088875 (corrected this scan)** | Prior CIK (0001048268) resolved to IES Holdings, Inc. — wrong entity. No amendment found under the corrected CIK in-window (search-coverage limited, see below). |
| Tiger Global | 0001167483 | ✅ Confirmed correct; no amendment found in-window |
| Coatue Management | **0001135730 (corrected this scan)** | Prior CIK (0001336528) resolved to Pershing Square Capital Management, L.P. — wrong entity. No amendment found under the corrected CIK in-window. |
| Whale Rock Capital | 0001387322 | Re-confirmed via a third independent WebSearch path (SEC-domain-indexed titles reading "Whale Rock Capital Management LLC," matching address) — **strong, still not primary-EDGAR-verified.** No amendment found in-window. |
| Lone Pine Capital | 0001061165 | ✅ Confirmed correct; no amendment found in-window |

**No new 13F-HR/A amendments found for any of the six tracked funds this window** — consistent
with expectations (Q3 2026 isn't due until mid-November). **Coverage caveat, stronger than
usual this week:** WebFetch to every secondary aggregator (whalewisdom.com, 13f.info,
opengovus.com) was also blocked this session, not just sec.gov — the "no amendment found"
conclusions rest on WebSearch's general index alone, which skews toward old, already-indexed
filings and is a weak-to-moderate negative for a real-time check, not a strong one.

**Fix applied this scan:** `scripts/weekly_scan_runner.py` `TRACKED_FUNDS` corrected for
Baillie Gifford and Coatue (see Execution note above and inline code comments). Recommend a
primary-EDGAR reverification of all three corrected CIKs (Whale Rock, Baillie Gifford, Coatue)
once network access is restored — and an audit of whether any other repo file references the
old, wrong CIKs.

---

## Routine filings

<details>
<summary>Expand for the full grouped list (confirmed in-window, non-material — dividends,
routine buybacks, insider 10b5-1/144 sales absent a specific flag above, analyst PT changes
without new information, conference appearances, and items resurfaced by the sweep agents that
were already reported in last week's 2026-09-04 scan and are not repeated here: SNOW's 9/2 Q2
beat, FLEX's 9/3 EPC Power acquisition).</summary>

**Power/Utilities:** SO, ETR, XEL, NRG, PUMP, WULF, CIFR, CLSK, RIOT — routine dividends/
analyst notes/conference appearances only; the bitcoin-miner-pivot cohort's capacity/financing
cadence continued (CLSK's August ops update, RIOT's prior-window Rockdale lease) without a
fresh in-window contract. **KEEL** — a PowerSecure backup-power item was reported by only a
low-reliability aggregator; **not corroborated, do not treat as confirmed.**

**Grid/DC construction/nuclear:** DUK, AEP, PPL, D, NEE, CEG, TLN, GNRC, KGX.DE — no new
in-window items beyond routine dividends/analyst notes. NNE signed a non-binding MOU with
Enveniam (nuclear fuel cycle collaboration, 9/4-9/6) — directional, not yet a contract. UEC —
Jefferies initiated Hold.

**Semi-equipment/materials:** ENTG, AMAT, FORM, UMC, 6383.T (Daifuku), TOELY (5-for-1 split,
announcement date unverified) — routine conference/analyst activity only.

**Fabs/foundry:** MRVL (no new item; the $12B FY guide raise and AI Infra Summit participation
are pre-window/routine), ASX (routine August sales print), CAMT, ACLS, ON, NXPI, COHU, AAOI
(the $600M ATM dilution event priced 8/21, pre-window).

**EDA/IP/silicon/optical:** LITE, COHR (routine insider sale, CFO), MPWR (see GFS/MPS item
above), TXN, BESIY, LSCC, ADI, TSEM, CCJ, NVT, AAON — routine only. MCHP guided Sept-quarter
+40% YoY at a Citi conference (directional color, not an 8-K event). STM raised data-center
revenue outlook color at the same conference. ALGM, UCTT, MELE.BR, NVTS (first US-manufactured
GaN device shipments, framed around onshoring — supply-chain data point, not a contract win),
CEVA (a 9/9 press release exists but content was not retrievable), POET, PDYN, 5347.TWO,
0981.HK, HHUSF — no material in-window items.

**Robotics/automation:** SYM (Barclays PT cut, valuation-driven), NXT, UMAC, 2590.HK, 2252.HK,
6506.T, 6324.T, 6481.T, 2049.TW (confirmed as HIWIN Technologies), 9880.HK, ONDS, DRO.AX
(routine firmware release), 6954.T, KTOS ($20M SATCOM contract, 9/1 boundary), RCAT, SERV
(reported cutting FY2026 guidance on weaker delivery volumes — date within window unverified,
directionally negative, flagged for confirmation) — all routine/below-materiality-bar this
week beyond what's individually noted.

**Servers/storage/data centers:** IRM, SMCI (no new item), HUT, TTMI (see financing item
above), EQIX (no new item; NVIDIA/Fabric One news predates window).

**Cloud/neocloud/software:** NOW, ADBE (see CEO-succession item above), FTNT (Gartner MQ
leader, recognition not disclosure), CRWD (no new item; Fal.Con announcements predate window),
TEM ($9.5M ARPA-H award, 9/9, minor), SSII, WDAY, PANW (see Console acquisition item above).

**Industrials/defense/connectors:** RRX, TKR, TNC (Chief Transformation Officer retirement
dated 9/3, one day pre-window), CARR, ATKR (no deal-status change on the Prysmian
acquisition), VPG, PSIX, MTZ, BWXT.

</details>

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🔴 | **NTAP is EXIT PENDING, seam-damped to 2026-09-15 — cannot confirm before next week's scan (9/18) even if it stays below the exit rank.** No company-specific news drives this; it's purely the rule-34 ROIC recompute. `capitulation_flag.py NTAP --log-forecast` could not be run this session (SEC access blocked) — please run it from a network-enabled session before the exit confirms, per Step 7d. |
| 🟡 | **VRT signed a real, material $1.45-2.6B acquisition (UtilityInnovation Group, 9/2) that wasn't in last week's scan** — worth folding into the next thesis/R-dimension review; extends Vertiv into grid interconnect. Dates/terms are secondary-sourced only (SEC/IR direct fetch blocked) — recommend a primary confirm when access allows. |
| 🟡 | **AVGO's 10-Q was filed (officer certs 9/9) but this session could not read whether the RVG/VIE guarantee footnote resolves the deferred R3 rating question** — recommend a direct read of `avgo-20260802.htm` next session. |
| 🟡 | **MU's Taiwan labor dispute escalated procedurally (failed mediation 9/4, second session 9/21) and Micron announced its largest-ever employee bonus program (9/11) in apparent direct response** — worth watching whether this resolves the dispute before the 9/21 mediation or whether a strike vote still gets called. Also note the Netlist Federal Circuit oral arguments (9/9) as a fresh legal-risk data point (not new exposure, but a docket to track). |
| 🟡 | **13F tracked-fund CIKs: two more were wrong (Baillie Gifford, Coatue) — same failure class as the Whale Rock fix.** Corrected in `scripts/weekly_scan_runner.py` this scan on WebSearch/secondary evidence only; please reverify all three corrected CIKs (Whale Rock, Baillie Gifford, Coatue) against primary EDGAR once access is restored, and consider auditing whether any other repo file (e.g., `00-master/` tracking sheets) references the old wrong CIKs. |
| 🟡 | **CRM's Q2 FY27 10-Q still doesn't appear to disclose a hard NRR% despite three consecutive scans of searching** — this is looking less like a search-coverage gap and more like Salesforce may no longer be disclosing this metric. Worth a direct primary-10-Q confirmation, and a decision on how to treat the absence going forward given the Layer-10 disruption-risk mandate makes retention the single most-watched number. |
| 🟡 | **ORCL's 9/10 beat (RPO +$30B in-quarter) is large enough to warrant a `/refresh-objective ORCL` once network access allows**, even though it's not a current holding — flagging per rule 9's "within 1 week" priority for non-held names. |
| 🟢 | **AMZN, now a full holding, is the thinnest-researched name in the book** — recommend an early `/refresh-context AMZN` rather than waiting for the normal rolling-staleness rotation, given it entered without the deep-dive treatment the other 16 holdings have accumulated. |
| 🟢 | **DDOG's Goldman Communacopia (9/10) and Citi TMT (9/8) transcripts were inaccessible this session** (Seeking Alpha/Gurufocus blocked) — a possible updated NRR figure from CFO Obstler could not be confirmed either way; worth a direct company IR-replay check next scan. |
| 🟢 | **Ticker-mapping flag: "2498.HK" does not resolve to a real HKEX listing** in any search this scan (only Taiwan-listed HTC Corp under a different code surfaces) — likely a data error in the watchlist, worth a direct correction rather than continued no-result scans. |
| 🟢 | **AAPL CEO-succession claim (Ternus replacing Cook, surfaced around the 9/9 product event) could not be corroborated** — flagging as unverified rather than reporting as fact; not a portfolio name, low priority, but worth a sanity check if it resurfaces. |
| 🟢 | **INTC's reported ~$15-20B secondary equity raise needs a pricing-date confirmation** before being treated as settled fact in any future note. |

**Score changes this window:** none from this scan (no local score-modifying work performed —
research/flagging only, per the rules). NTAP's ✓✓/EXIT-PENDING status stems entirely from
Dom's local 2026-09-07/08 sessions (rule-9 refresh + rule-34 ROIC deploy), already committed
before this scan began. **No tier changes; no new membership changes this scan.**
