# Weekly News Scan — 2026-08-21

**Scope:** 214 watchlist tickers. Scan window: **2026-08-14 – 2026-08-21.**

## Execution note (network constraints — unchanged from every scan since 2026-06-12)

SEC EDGAR (`data.sec.gov`, `www.sec.gov`) and Yahoo Finance (`query1/2.finance.yahoo.com`) are confirmed
403-blocked from this session's egress proxy (verified directly via `curl` and the proxy's own status
endpoint before starting — `recentRelayFailures` shows `connect_rejected` on `data.sec.gov:443`, and
direct `curl` calls to `query1.finance.yahoo.com` and `www.sec.gov` both failed the same way).
Substituted the `web_scan.py` fallback methodology (date-verified, source-preferenced) executed through
**10 parallel research agents**: 3 covering the 15 current portfolio holdings in depth (NVDA/MU/TSM/SNDK/ALAB;
CRDO/ANET/VRT/FIX/EME; MSFT/AVGO/META/GMED/RDDT), 1 covering 11 other high-tier watchlist names not currently
held (EQT/TER/APH/GOOGL/AMZN/PLTR/WDC/APP/ISRG/CGNX/6861.T), 1 covering the Layer-10 SaaS watch (PLTR/DDOG/CRM)
on the requested NRR/AI-adoption/pricing dimensions, 4 sweeping the remaining 188 tail tickers (~47 each), and
1 checking the six tracked funds' 13F-HR status. **All 214 tickers received at least one query this week.**

Local, non-network scripts ran cleanly: `audit_rating_integrity.py --summary` (0 gate violations, 0 stale),
`resolve_forecasts.py --dry-run` (0 forecasts due), `refresh_targets.py --check` (Targets reflect current
scores, no pending rebalance). `momentum_50dma.py` and a live `refresh_targets.py`/`track_performance.py` run
(need yfinance) remain blocked (confirmed via live test calls this session). No watchlist name reported
earnings inside this window (all 15 holdings' Q2 prints clustered late July–Aug 13, before the window opens),
so **no Rule-9 earnings-triggered objective refresh applies this week.**

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

15 current holdings (all ✓✓ tier; unchanged membership since 2026-08-07's v2 migration — rank-based selection
+ inverse-vol sizing): **NVDA, FIX, TSM, MU, CRDO, SNDK, ANET, MSFT, AVGO, GMED, EME, VRT, RDDT, ALAB, META.**

Going in: **NVDA** believed the dominant AI-accelerator vendor mid-Blackwell/Rubin ramp, with the Burry
short-thesis narrative and CXMT/China competition as the open risk threads, plus the ~$500B financing deal
already flagged last scan. **FIX/EME** believed unchanged as DC-construction plays riding hyperscaler capex.
**TSM** believed the sole advanced-node foundry with no distinct red flags carried in. **MU** believed an
HBM-bottleneck beneficiary post-tier-jump, watching margin durability into HBM4. **CRDO** believed an
optical/AEC interconnect name with MRVL's Celestial-AI-derived platform as a new competitive thread (flagged
against ALAB, not CRDO, last scan). **SNDK** believed watching whether last scan's below-consensus forward
guide widens. **ANET** believed clean, tracking hyperscaler capex commentary. **MSFT** believed an Azure/AI
growth + OpenAI-relationship story. **AVGO** believed the custom-ASIC (Google TPU) name with a recent
CFO transition (non-thesis). **GMED** believed a distinct Layer-11 surgical-robotics thesis. **VRT** believed
watching guidance follow-through after last scan's entry-narrative correction (pre-entry print was a miss,
not a clean beat). **RDDT** believed the thinnest-research position, with open Google-licensing-renewal and
sequential-US-DAU-decline threads. **ALAB** believed watching for MRVL share-loss evidence following last
week's named-competitor flag, not yet a thesis break. **META** believed watching the AI-hiring-discrimination
suit ahead of the Aug 24 preliminary-injunction hearing.

**Diff against this week's scan:** the mental model mostly held — no thesis breaks. The one genuine shift is
**AVGO's competitive-exclusivity narrative concretizing**: Marvell's $12.2B Google warrant (below) is the
second consecutive week of evidence (after CRDO/ALAB's MRVL flag) that Google is diversifying its custom-silicon
supply base beyond a single-vendor relationship — worth tracking as a pattern, not yet a score-moving event
since Broadcom's own TPU/AI-networking agreement runs through 2031 per CEO Hock Tan's own acknowledgment.
**VRT** now carries an open legal-risk thread (securities-investigation announcements) that wasn't in the
pre-scan model. Everything else was already priced into the standing model.

---

## ⚠️ Material events

### Portfolio holdings

**NVDA**
- **[2026-08-14]** NVIDIA announced strategic financing partnerships with Apollo, BlackRock, Blackstone,
  Brookfield, Goldman Sachs, and KKR to mobilize **over $500 billion** of third-party capital for AI-infrastructure
  buildout — structured as MOUs, keeps financing off NVIDIA's own balance sheet. — [NVIDIA Newsroom](https://nvidianews.nvidia.com/news/nvidia-partners-with-apollo-blackrock-blackstone-brookfield-goldman-sachs-and-kkr-to-establish-ai-compute-infrastructure-financing-platforms-to-mobilize-over-500-billion-of-third-party-capital)
- **[2026-08-17]** 8-K: NVIDIA entered residual-value guaranties with SB Energy for ~4.25 GW of IT load (option
  for ~3.8 GW more) at the PORTS-Pike Technology Campus, Ohio; NVIDIA's aggregate payment obligation capped at
  **$105 billion**; also investing $1.5B directly in SB Energy; site to be leased to an OpenAI affiliate under a
  20-year lease. — [SEC 8-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000069/nvda-20260817.htm)
- [2026-08-19/20] routine-adjacent — reports NVIDIA received a path to export up to 100,000 H200 chips to China
  and plans a new export-compliant chip (licensed Groq LPU tech) for China by year-end; regulatory development,
  not yet a signed contract or filing. — [CNBC](https://www.cnbc.com/2026/08/19/china-ai-nvidia-chips-us-export-controls.html)
- Q2 FY2027 earnings scheduled **2026-08-26** — outside this window, flag for next scan.

**MU**
- **[2026-08-20]** Announced **Micron Research Labs**, a new Boise research hub backed by a planned **$10 billion
  investment over the next decade** (groundbreaking targeted 2027); public support from NVIDIA's Jensen Huang,
  Apple's Tim Cook, Applied Materials' Gary Dickerson, Lam Research's Tim Archer, plus Commerce Secretary Lutnick
  and White House OSTP. — [Tom's Hardware](https://www.tomshardware.com/tech-industry/micron-commits-usd10-billion-to-new-us-based-research-labs-boise-hub-to-target-post-dram-and-nand-technologies-and-packaging)
- Netlist filed an ITC complaint + parallel CDCA federal suit against Micron (also Supermicro/HPE/Lenovo) alleging
  DDR5 RDIMM/MRDIMM patent infringement — **complaint itself filed 2026-08-12, before the window**; only continued
  market coverage (MU down ~5-7% intra-week amid this + broader chip selloff) falls in-window. Recommend the
  news-log entry cite 8/12 as the actual event date. — [PRNewswire](https://finance.yahoo.com/technology/articles/netlist-files-patent-infringement-action-142207121.html)

**AVGO** — busiest name of the week, four distinct items:
- **[2026-08-14]** Stock -6% after Bank of America questioned a ~$370B AI-debt financing vehicle tied to leasing
  custom AI accelerators (sector-financing-durability concern, not AVGO balance-sheet debt directly); compounded
  by broad AI-trade profit-taking. — [24/7 Wall St](https://247wallst.com/investing/2026/08/14/broadcom-sinks-6-as-bofa-flags-370b-in-ai-debt-amd-climbs-4-on-bairds-1250-call/)
- **[2026-08-14, ongoing]** VMware vCenter zero-day (CVE-2026-59310, patch already released July 29) confirmed
  actively exploited — ~361 IPs across 47 countries compromised.
- **[2026-08-18/19]** **Marvell announced a custom AI-chip deal with Google**: a warrant for Google to buy up to
  ~$12.2B of Marvell stock (58.97M shares @ $206.58), tied to expanding TPU-ecosystem chip work (inference
  accelerators, storage/NIC). AVGO fell ~4-5% on fears this erodes its Google-TPU relationship; CEO Hock Tan
  acknowledged Google will use multiple suppliers, but Broadcom's own long-term TPU/AI-networking agreement runs
  through 2031. — [CNBC](https://www.cnbc.com/2026/08/19/marvell-google-ai-chips.html)
- **[2026-08-20]** Bloomberg reported Broadcom is in talks with lenders (incl. Blackstone, Apollo) to raise
  **$60-100B** in debt financing for AI chip production benefiting Anthropic and others (builds on the June "AI
  XPV Platform," which already provided Anthropic $35B); still being negotiated. — [Bloomberg via Yahoo](https://finance.yahoo.com/technology/ai/articles/broadcom-repoirtedly-seeking-raise-over-204953745.html)

**VRT**
- **[2026-08-18]** Multiple plaintiffs'-side firms (Bronstein Gewirtz & Grossman, Pomerantz, Schall/SBS Law)
  announced securities-fraud investigations into Vertiv and its officers/directors, examining whether the
  company issued misleading statements ahead of the Q2 2026 miss and 17.26% single-day drop (Jul 29, before this
  window). These are law-firm client-solicitation announcements, not confirmed SEC enforcement or filed class
  actions — flagging as material for legal-risk awareness at the pre-litigation stage.
  — [GlobeNewswire/Pomerantz](https://www.globenewswire.com/news-release/2026/08/18/3347340/1087/en/investor-alert-pomerantz-law-firm-investigates-claims-on-behalf-of-investors-of-vertiv-holdings-co-vrt.html)

**MSFT**
- **[2026-08-17]** Stock -3.2-3.3% — largest driver: profit-taking + AI-capex/margin concern (Morgan Stanley
  flagged "gap between capital deployment and revenue generation"). Same day, a Guardian investigation reported
  Microsoft has ~2.2M AI chips installed globally vs. its stated 5GW of added DC capacity; Microsoft disputes the
  Guardian's methodology/figures but hasn't specified which numbers are wrong.
  — [Motley Fool](https://www.fool.com/investing/2026/08/17/why-microsoft-stock-dropped-today/)

**META**
- **[2026-08-17]** Landmark trial opened in federal court (Oakland) with California AG Rob Bonta co-leading a
  29-state-AG coalition alleging Meta designed platform features to addict/harm underage users and misled the
  public about known harms. States' initial calculation cited a theoretical maximum penalty around **$1.4
  trillion** (not a specific ask). Case originally filed 2023; trial opened this week.
  — [NPR](https://www.npr.org/2026/08/18/nx-s1-5935458/meta-child-safety-social-media-addiction-trial-opening)
- AI-hiring-discrimination suit: no new in-window docket filing found; response to the preliminary-injunction
  motion was due Aug 10 (outside window, unconfirmed whether filed); the **hearing itself is Aug 24 — just after
  this window closes.** Flag for direct follow-up next scan.

**RDDT**
- **[2026-08-18]** Reddit officially joined the **S&P 500**, replacing AvalonBay Communities (announced Aug 13,
  just before window; the effective inclusion date, Aug 18, is in-window). Shares had jumped ~11-12% on the
  announcement. Enabled by Reddit's first full year of GAAP profitability in 2025.
- Google content-licensing renewal and US-DAU-decline threads: no new in-window development on either.

**ALAB**
- **[2026-08-17]** Form 4s: CEO Jitendra Mohan and President/COO Sanjay Gajendra each sold ~86,180 shares
  (~$30.8M each); GC Philip Mazzara sold 6,801 shares (~$2.3M). Company characterization: mandated "sell-to-cover"
  transactions for RSU-vesting tax withholding, not discretionary open-market sales — flagging given dollar size
  and coordinated timing, with the mitigating context noted.
- **[2026-08-17]** 13F disclosure: Amazon bought 277,777 ALAB shares in Q2 (~$134.2M), now Amazon's 4th-largest
  disclosed equity position — informational, reflects the existing Feb-2026 warrant/strategic relationship, not a
  new one.

**No in-window material items:** TSM (routine 6-K only), SNDK (sector-selloff price action only), CRDO (sector
selloff only), ANET (conference appearances only), FIX (routine CFO Form 4, rates-driven selloff), EME
(institutional-ownership filing + Zacks commentary only), GMED (stock -3%, unconfirmed-date Stifel Hold/$64 PT).

### Other high-tier watchlist (not held)

- **GOOGL** — see Marvell $12.2B warrant above (Google is the counterparty, filed as a Marvell 8-K). Jeff Dean
  (Chief Scientist, 27-yr veteran) departed to co-found "Discovery Loop" — **dated Aug 5-6, before this window**,
  flagged for context only.
- **ISRG** — [2026-08-17] Announced new ~316,000 sq ft manufacturing facility in Penang, Malaysia (RM2B
  investment, ~1,200 jobs, targeted operational 2028) — first Southeast Asia manufacturing site.
- **WDC** — [2026-08-17] Shares +7% on Commerce Secretary Lutnick's semiconductor/storage-reshoring comments —
  macro/policy-driven, not a WDC-initiated disclosure.
- **AMZN** — crossed $3T market cap this window (commentary, not a new disclosure).
- No in-window material items: EQT (note: search noise conflates EQT Corp with the unrelated Swedish PE firm EQT
  AB — do not conflate), TER, APH (mechanical 2-for-1 split record date only), PLTR (routine Form 4 only; the
  $243.9M Pentagon no-bid memo is dated Aug 4-13, ambiguously at/before the window edge), APP (analyst PT changes
  only), CGNX (routine dividend record date), 6861.T (no coverage found, English or Japanese).

### Layer-10 SaaS focus (PLTR / DDOG / CRM)

Quiet week by design — all three reported Q2 earnings before this window (PLTR 8/3, DDOG 8/6) or haven't yet
(CRM's Q2 FY2027 print is **2026-08-26**, just after this window closes). No new NRR, AI-feature-adoption, or
pricing-model disclosures dated in-window for any of the three. Most recent disclosed NRR: PLTR 150%
(pre-window), DDOG low-$120s% TTM (pre-window). DDOG's Bits AI per-investigation→AI-Credits consumption pricing
shift could not be date-confirmed — flagged for a follow-up via Datadog's pricing-page changelog. **CRM is the
one to prioritize for next week's Rule-9 refresh** — multiple analyst notes are explicitly flagging
Agentforce/AWU consumption-billing monetization as the swing factor for the 8/26 print, directly on the
disruption-thesis pricing-model mandate.

### Selected long-tail items (thesis-relevant; full list in Routine filings toggle below is not exhaustive —
### see gaps note)

- **ORCL** — Project Jupiter ($165B AI data center, New Mexico, ~2.5GW gas fuel cells for OpenAI compute) hit a
  gas-pipeline routing delay after the state Land Office repeatedly rejected the route; in-service date pushed
  from Aug 2026 to Feb 2027 (6-month slip); shares fell as much as 5%. Oracle says the broader project timeline
  remains on track. — [TipRanks](https://www.tipranks.com/news/oracle-stock-falls-as-its-165-billion-ai-data-center-hits-another-pipeline-roadblock)
- **CRWV** — [08-20] Hudson River Trading signed a multibillion-dollar multiyear deal for AI cloud/trading-research
  compute.
- **HUT** — [08-18/20] Reports of a long-term NVIDIA lease covering Hut 8's entire 1-GW Texas data center, options
  up to $50B over 30 years; Freedom Capital initiated Buy.
- **NBIS** — [08-18] Vantage Data Centers deal to deploy NVIDIA-powered AI infrastructure at the CWL1 site, Wales
  (+8.8%); [08-19] priced an upsized **$5.0B** convertible senior notes offering (~$4.94B net proceeds for
  data centers/GPU procurement).
- **APLD** — [08-20] Q4/FY2026: revenue +400%+ YoY, beat; ~$36B contracted lease revenue (potential $86B with
  renewals).
- **MRVL** — see Google $12.2B warrant above; also launched new AI-memory products (Bravera SC6, Structera X,
  Photonic Fabric).
- **FTNT** — [08-17] Acquired Virtue AI (AI-runtime-protection for autonomous AI systems).
- **HPE** — [08-16] Secured court/regulatory approval for the Juniper Networks acquisition settlement.
- **TEM** — [08-19] Announced $1.5B acquisition of Personalis (tumor-informed MRD assays, ~$20B TAM).
- **TTMI** — [08-17] Definitive agreement to acquire Epiq Solutions (~$1.1B all-cash).
- **MOD** — [08-21] Third-party investigative report (Hunterbrook Media, unconfirmed by Modine) identified Google
  as the previously-unnamed customer behind Modine's ~$4B Airedale-chillers supply agreement.
- **HSAI** — [08-18] Q2 beat; CEO framed the quarter as a pivot to "full-stack infrastructure platform for
  Robotics and Physical AI."
- **PRCT / PLAB** — securities class-action deadline-alert notices (law-firm solicitation stage, same pattern as
  VRT above) — PRCT [08-17/19] tied to an 18% drop on alleged channel-stuffing; PLAB [08-15/17/18] tied to
  IC-photomask-demand disclosures.
- **AMD** — [08-19] Appointed Tim Ryan (Citi) to the board, succeeding retiring director Joseph Householder.
- **CRWD** — [08-20] CTO Elia Zaitsev departing after 13 years, no successor named (source: aggregated coverage,
  primary URL not independently confirmed — flag for verification).
- **WYFI** — [08-19/21] Priced an upsized $270.0M convertible senior notes offering; stock fell as much as 25% on
  the announcement.
- **PSIX** — [08-17] New CEO Richard Hu, succeeding interim CEO/continuing CFO Xun (Kenneth) Li.
- **BTDR** — [08-20] Malaysia AI-cloud contracts adding ~$400M in five-year revenue (part of a >$2B AI pipeline).
- **UMC** — [08-14] Capital-structure change (RSA cancellation, new convertible-bond terms).

**Boundary note (repeats last scan's finding):** a large share of the tail cohort's real fundamental news
(earnings, guidance, M&A) clustered **Aug 3–13**, just before this window opens — RIOT's $9.1B/20-yr Anthropic
compute lease (Aug 10) is the most consequential near-miss (bitcoin-miner→AI-infrastructure-landlord thesis
shift); confirm it's reflected in RIOT's thesis.md. Also just-outside-window: SWKS's $2B notes/dividend
suspension (Aug 10), LRCX's $3B+ R&D lab expansion (Aug 13), IREN's Microsoft Horizon-1 delivery (Aug 13), NEE's
DOE/Japan 10GW gas-generation funding (Aug 12), CLSK's $6.6B AI-DC lease (Jul 14-15), CEG's $860M divestiture
(Aug 6), CORZ's $444M Polaris DS close (Aug 13).

---

## 📊 Earnings refreshed

**None.** No watchlist name reported quarterly earnings inside this scan window (2026-08-14 to 2026-08-21) —
all 15 holdings' Q2 prints clustered late July through Aug 13, before the window opens. Rule-9 does not trigger
this week. (For awareness: several non-held watchlist names *did* report in-window with large beats — ADI
(+40% YoY revenue), APLD (+400%+ YoY), KEYS (~24% EPS beat), ADSK, FN, HSAI, ONDS, PWR — but a Rule-9 objective
refresh requires yfinance, which remains network-blocked. Flagging rather than fabricating updated inputs.)

---

## 💼 Portfolio pipeline

- `refresh_targets.py --check`: **Targets reflect current scores ✓** — no pending rebalance, no ENTER/EXIT/EXIT
  PENDING/BLOCKED flags, no tier-change reallocations.
- `momentum_50dma.py`, a live `refresh_targets.py` run, and `track_performance.py` (weekly mark) all require
  yfinance and remain blocked this session — same constraint as every scan since 2026-06-12. No weekly mark to
  report this week; last committed model-value/benchmark comparison is from the 2026-08-14 scan (+2.86% window,
  +4.60% since inception at that time). Recommend a local/on-network session run these three scripts to close the
  gap once egress is restored.
- No concentration, layer-cap, dead-ticker, or manual-override-collision flags (none of these scripts ran, so
  this is "not observed" rather than "confirmed clean" for anything beyond what `--check` covers).

---

## 🔬 Rating integrity

`audit_rating_integrity.py --summary`: **211 rated names | 0 gate violations (no thesis) | 0 stale (>90d).**
Clean — no action needed.

---

## 🎯 Calibration

`resolve_forecasts.py --dry-run`: **0 forecasts due, 0 needing review.** Nothing to resolve this week.

---

## 🔴 Live pipeline

Skipped — cloud/headless session (rule 29: MCP OAuth does not survive headless runs). No heartbeat/reconcile
check performed.

---

## New 13F activity

Q2 2026 13F-HR deadline was 2026-08-14 (last week). Status as of this scan:

| Fund | Status | Filed | Notes (UNCONFIRMED — secondary aggregator figures, not primary-XML-verified) |
|---|---|---|---|
| Berkshire Hathaway | **Confirmed filed** | 2026-08-14 | 89 reportable positions, $299.25B aggregate value. GOOGL added ~24.5M shares (~45% value increase, ~$28.2B stake); BAC trimmed ~30.2M shares; COF reduced ~58%. |
| Baillie Gifford | **Confirmed filed**, no amendment | 2026-08-14 | Portfolio ~$98B→~$110B. SpaceX ~$8.78B (top/near-top holding). NVDA ~8.26% weight. Adds: NVDA, GOOGL, Axon. Trims: AMZN, MELI, Spotify, Cloudflare, Shopify, Netflix. |
| Tiger Global | **Confirmed filed** | 2026-08-14 | 46 positions (down from 54), $23.98B total, net seller ~$2.8B. New: Cerebras (~$660M), AMD (~$392M), Seagate, Visa. GOOGL trimmed ~45%; NVDA trimmed ~7%; AVGO trimmed ~$690M. 17 full exits incl. AppLovin, Netflix, WDAY. |
| Coatue Management | **Confirmed filed** | 2026-08-14 (medium-high confidence — EDGAR index page found but not directly fetched) | $48.63B value (up from $29.01B). Top holdings: TSM, LRCX, MU, SpaceX, AMAT. New: SpaceX, Intel, Cerebras, Hut 8. |
| Lone Pine Capital | **Confirmed filed** | 2026-08-14 | $16.4B value, top-10 concentration 53.87%. Top holdings: NBIS, ASML, STX, Home Depot, AMAT. Adds: Nu Holdings, Medline, Carvana, TeraWulf, GOOGL (+42.8%). |
| Whale Rock Capital | **NOT confirmed filed** | — | Latest verifiable data is still Q1 2026 (period 2026-03-31, filed 2026-05-15). **Re-check next scan.** |

Portfolio-relevant reads: Berkshire and Baillie Gifford both adding to GOOGL; Tiger Global going the other way
(trimming GOOGL ~45%, AVGO, and NVDA modestly) while adding Cerebras/AMD — a genuine divergence in AI-compute
positioning across the tracked funds worth a `/thirteenf-delta` pass once primary filings can be read directly
(all figures above are secondary-aggregator sourced, not independently verified against primary XML tables per
rule 1 — treat as directional only).

---

## Routine filings

<details>
<summary>Expand for the full list (confirmed in-window, non-material — dividends, routine buybacks, insider
10b5-1/144 sales absent a specific flag above, analyst PT changes without new information, conference
appearances, and beat-quarters without a distinct thesis-relevant angle beyond what's captured above).</summary>

**Power/Utilities:** DUK ($1.75B equity units offering, closed 8/13, mostly out-of-window); SO (Truist downgrade
+ routine dividend); PPL (routine dividend); CMI (BESS data-center supply win 8/16 + routine dividend); GEV
(CIGRE Paris conference announcement); no in-window items: AEP, ETR, XEL, D (one unconfirmed 8-K, content not
verified), NEE (DOE/Japan funding is 8/12, just outside window), NRG, VST, CEG, TLN, OKLO, SMR (routine Paragon
HIPS design contract, no dollar figure), BWXT (routine SVP appointment + GF-Value commentary), PLUG, BE
(Power Connect product launch), UEC.

**Grid/DC construction/cooling:** LRCX ($3B+ R&D lab expansion, 8/13, just outside window); GLW (Zayo fiber
supply-agreement expansion, 15,000 route miles by 2030); ETN (multi-million BSD Builders contracts + insider
selling, both 8/18); JCI, PWR (Q2 backlog +50% is 8/13, just outside window), MTZ (closed $650M senior notes
offering), CARR, TT, AAON, HUBB, NVT, KEYS (Q3 beat 8/18), IRM: no new in-window items beyond what's flagged.

**Semi-equipment/materials:** ADI (Q3 record beat 8/19); AMAT (Q3 beat, 8/13, just outside window); KLAC
(Qnity Electronics SP7 XP install, product-adoption item); ACLS, ENTG, MKSI, UCTT (Needham conference
appearances only); ONTO, TER: no in-window items.

**Fabs/foundry:** 0981.HK/SMIC (Q2 beat, borderline 8/13-14); ASX, HHUSF, GFS, TSEM, CAMT, 5347.TWO: no confirmed
in-window items.

**EDA/IP/silicon:** MRVL (Google $12.2B warrant, flagged above); AMD (Tim Ryan board appointment); ALGM
(sector-wide selloff -11%, Form 144); NXPI, QCOM, TXN, ADI (flagged above), STM (routine IFRS semi-annual
re-filing), CEVA, LSCC, AMBA, ARM, RMBS, MPWR, POET, NVTS, FORM, PLAB (securities class-action deadline
notices, flagged above): no other in-window items beyond what's flagged.

**Optical/networking:** FN (Q4 beat, record quarter, 8/17); COHR, CIEN, LITE, AAOI, GLW (flagged above): no
other in-window items.

**Servers/storage:** SMCI, DELL, HPE (Juniper settlement flagged above), NTAP (routine Form 4): no other
in-window items.

**Cloud/neocloud/BTC-to-AI:** CRWV, HUT, NBIS, APLD, BTDR (all flagged above); CIFR, WULF (bullish analyst
commentary on the prior-window Anthropic lease, no new item); HIVE (Q1 earnings 8/14 + $350M GPU deal 8/17);
CORZ, IREN, RIOT, CLSK: no new in-window items beyond the just-outside-window items noted above.

**Software/SaaS (Layer 10, non-focus names):** WDAY (no in-window item; Aug 27 earnings pending), FTNT
(flagged above), PANW (Frontier AI Critical Defense Program launch w/ Anthropic/OpenAI as partners), SNOW,
ADBE (BlackRock disclosed >10% stake, +4.5%), INTU, ADSK (Q2 beat 8/18), MDB, CRWD (CTO departure, flagged
above), ZS, PATH (routine CEO 10b5-1 sale): no other in-window items.

**Robotics/foreign/misc (Layer 11 and others):** AVAV, PDYN, RCAT (Blue Ops/Havoc maritime-defense partnership,
no disclosed value), OUST, SERV, DRO.AX, AUTO.OL (routine buyback/PSU settlement), 6954.T, 6324.T, 6268.T,
6481.T, 6383.T, 9880.HK, 2590.HK, 2049.TW, 2252.HK, 6506.T, ALNT (product-line expansion), NOVT, VPG, TKR
(routine dividend), RRX, SSII (Q2 8/13, just outside window), KLIC (President appointment, unconfirmed source),
CGNX (flagged above), ISRG (flagged above): no other in-window items.

</details>

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🟡 | **AVGO's competitive narrative is developing a pattern, not yet a thesis break.** Marvell's $12.2B Google warrant is the second consecutive week (after CRDO/ALAB's MRVL flag on optical interconnect) that a portfolio holding faces evidence of Google diversifying its custom-silicon supplier base. AVGO's own TPU/AI-networking agreement runs through 2031 per CEO Hock Tan, but worth a `/refresh-context AVGO` pass to update the AI-Thesis moat dimension with the accumulating evidence rather than treating each week's item in isolation. |
| 🟡 | **VRT now carries an open legal-risk thread** — multiple law firms announced securities-fraud investigations (8/18) tied to the pre-window Q2 miss. Pre-litigation stage (client solicitation, not a filed complaint or SEC action), but worth tracking for R3/R4 risk-dimension purposes at the next subjective-rating refresh. |
| 🟡 | **Whale Rock Capital's Q2 2026 13F is still not confirmed filed**, one week past the deadline (other five tracked funds all filed 8/14). Re-check next scan. |
| 🟡 | **CRM reports Q2 FY2027 on 2026-08-26** — multiple analysts are flagging Agentforce/AWU consumption-billing monetization as the key swing factor, directly on the Layer-10 disruption-thesis tracking mandate. Prioritize for next week's Rule-9 refresh. |
| 🟢 | **Weekly mark and 50DMA momentum inputs could not be refreshed this week** (yfinance blocked) — the last committed model-value/benchmark comparison is from 2026-08-14. Recommend running `momentum_50dma.py`, `refresh_targets.py`, and `track_performance.py` from a local/on-network session to close the gap. |
| 🟢 | **META's AI-hiring-discrimination preliminary-injunction hearing is 2026-08-24** — just after this window closes. Direct follow-up recommended next scan rather than relying on secondary coverage. |
| 🟢 | **RIOT's $9.1B/20-year Anthropic compute-lease deal (Aug 10) landed one day before this window** — a consequential bitcoin-miner→AI-infrastructure-landlord thesis shift. Confirm it's already reflected in RIOT's thesis.md; if not, worth a dedicated research pass regardless of the scan-window boundary. |
| 🟢 | **13F divergence across tracked funds**: Berkshire and Baillie Gifford both added to GOOGL this quarter; Tiger Global went the other way (trimmed GOOGL ~45%, AVGO, NVDA modestly) while rotating into Cerebras/AMD. Worth a `/thirteenf-delta` pass once primary EDGAR access is available — all figures above are secondary-aggregator sourced. |

**No score or tier changes this week** (no watchlist name reported earnings in-window; rating-integrity audit
clean; no pending rebalance).
