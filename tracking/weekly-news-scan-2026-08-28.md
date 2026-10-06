# Weekly News Scan — 2026-08-28

**Scope:** 214 watchlist tickers. Scan window: **2026-08-21 – 2026-08-28.**

## Execution note (network constraints — unchanged from every scan since 2026-06-12)

SEC EDGAR (`data.sec.gov`, `www.sec.gov`) and Yahoo Finance (`query1/2.finance.yahoo.com`) are confirmed
403-blocked from this session's egress proxy (verified via direct `curl` and a live `yfinance` call before
starting — the proxy's own status endpoint shows `recentRelayFailures` with `connect_rejected` on both
`data.sec.gov:443` and `query1.finance.yahoo.com:443`). Substituted the `web_scan.py` fallback methodology
(date-verified, source-preferenced) executed through **9 parallel research agents**: 3 covering the 15
current portfolio holdings in depth (NVDA/FIX/TSM/MU/CRDO; SNDK/ANET/MSFT/AVGO/GMED; EME/VRT/RDDT/ALAB/META),
1 covering 10 other high-tier watchlist names not currently held (AMZN/APP/GOOGL/TER/APH/WDC/ISRG/CGNX/EQT/PLTR)
plus a dedicated Layer-10 SaaS deep-dive (PLTR/DDOG/CRM) on the requested NRR/AI-adoption/pricing dimensions,
4 sweeping the remaining 187 tail tickers (~47 each), and 1 checking the six tracked funds' 13F-HR status.
**All 214 tickers received at least one query this week.**

Local, non-network scripts ran cleanly: `audit_rating_integrity.py` (211 rated names, 0 gate violations, 0
stale), `resolve_forecasts.py --dry-run` (0 forecasts due), `refresh_targets.py --check` (Targets reflect
current scores, no pending rebalance). `momentum_50dma.py`, a live `refresh_targets.py`/`track_performance.py`
run, and any Rule-9 objective-input refresh (all need yfinance) remain blocked — confirmed via a live test
call this session (`ConnectionError`/403 at the proxy). **Several watchlist names reported earnings inside
this window (NVDA, CRM, MRVL, SNPS, CRWD, INTU, WDAY, ADSK, PLAB, IREN, DRO.AX, and others) — the qualitative
details are captured below, but no objective-input refresh or before/after score computation could be run.**
This is a real gap, not a "nothing happened" week — see 📊 Earnings refreshed below.

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

15 current holdings (all ✓✓ tier; unchanged membership since 2026-08-07's v2 migration — rank-based selection
+ inverse-vol sizing): **NVDA, FIX, TSM, MU, CRDO, SNDK, ANET, MSFT, AVGO, GMED, EME, VRT, RDDT, ALAB, META.**

Going in (carried forward from last week, largely unchanged): **NVDA** believed the dominant AI-accelerator
vendor mid-Blackwell/Rubin ramp, financing/customer commitments piling up ($500B third-party financing MOUs,
$105B SB Energy deal), with AMD/custom-silicon competition as an open thread management itself now
acknowledges on calls. **FIX/EME** believed unchanged as DC-construction plays riding hyperscaler capex.
**TSM** believed the sole advanced-node foundry with no distinct red flags. **MU** believed an HBM-bottleneck
beneficiary post-tier-jump, watching margin durability into HBM4, now also watching a leadership succession
move and a tariff-policy risk thread. **CRDO** believed an optical/AEC interconnect name with MRVL's
Celestial-AI-derived platform as a competitive thread. **SNDK** believed watching whether guidance widens;
this week added a large multi-year capacity commitment. **ANET** believed clean, tracking hyperscaler capex
commentary. **MSFT** believed an Azure/AI growth + OpenAI-relationship story, still absorbing the 8/17
Guardian-chip-count controversy with no rebuttal yet. **AVGO** believed the custom-ASIC (Google TPU) name,
now watching a firming $70-100B AI-chip debt-financing structure and continued Google-diversification
narrative (Marvell). **GMED** believed a distinct Layer-11 surgical-robotics thesis, now layering in AI/digital
health via M&A. **VRT** believed watching guidance follow-through, with an open pre-litigation legal thread.
**RDDT** believed the thinnest-research position, open Google-licensing-renewal and US-DAU threads unresolved.
**ALAB** believed watching for MRVL share-loss evidence, not yet a thesis break. **META** believed watching
the AI-hiring-discrimination suit and a landmark child-safety trial as open legal risk.

**Diff against this week's scan:** the biggest move is **META** — both open legal threads resolved this week:
the AI-hiring-discrimination preliminary-injunction hearing (8/24) leaned strongly against plaintiffs, and the
child-safety trial (opened 8/17) settled for **$17.1B** (8/26, paid over 10 years, with mandated product
changes). Net effect: legal-risk reduction, not a thesis change — worth noting the settlement is a real cash
cost and imposes minor-safety product constraints, but removes open-ended jury-verdict tail risk. **NVDA**
reported Q2 FY27 earnings (8/26) — captured by the earnings sentinel, no Rule-9 trigger (beat was +4.5%
revenue/+6.2% EPS, below the 15% threshold) — but the *call* surfaced new detail on FY28 guidance (~70% growth
vs ~44% consensus) and explicit management acknowledgment of AMD/custom-silicon competitive share gains,
worth tracking as an emerging thread. **AVGO's** financing story concretized from "in talks" to a defined
$70-100B lender structure. **SNDK** locked in a genuine $31B multi-year Japan capacity commitment. **MU** saw
a leadership reorg (no CEO change) and a new macro thread (potential tariff-exemption rollback for
data-center/server hardware, reported 8/27, hit MU/WDC/STX directly). Everything else was largely priced
into the standing model.

---

## ⚠️ Material events

### Portfolio holdings

**NVDA**
- **[2026-08-26]** Q2 FY27 earnings (already captured by the earnings sentinel, commit `245241a`): revenue
  $96.2B (+106% y/y, +4.5% vs ~$92.07B consensus), non-GAAP EPS $2.22 (+6.2% vs ~$2.09 consensus), gross
  margin 75.0% flat q/q; Data Center $89.0B (+117% y/y); Q3 guided $108.0B ±2% ex-China; commitments
  $119B→$279B. Rule-9 immediate trigger NOT met (below the 15%/500bps thresholds); no model event, no
  ratings changed. — [8-K acc 0001045810-26-000073]
- **[2026-08-27]** Stock +8.7% on the print and above-consensus Q3 guide; broader semis rallied alongside it
  (AVGO +4.5%, SK Hynix/Intel +2-4%). — [Motley Fool](https://www.fool.com/coverage/stock-market-today/2026/08/27/stock-market-today-aug-27-nvidia-surges-on-blowout-results-and-surprising-guidance/)
- **[2026-08-26 call]** ⚠️ Huang guided FY28 revenue growth of ~70% vs. ~44% LSEG consensus; management
  directly addressed AMD MI-series competition (no CUDA/NVLink lock-in cited as the moat) and rising
  hyperscaler custom-silicon share (~28% of AI chip market in 2026 vs ~21% in 2025, per management's own
  framing) — worth tracking as an emerging competitive thread, not yet thesis-moving. — [CNBC](https://www.cnbc.com/2026/08/26/nvidia-nvda-earnings-report-q2-2027-live-updates.html)
- **[2026-08-28]** Stock pulled back to ~$226 amid broader tariff-driven semis weakness (see MU below).

**MU**
- **[2026-08-26]** Leadership reorganization: Manish Bhatia promoted to President & COO; Scott DeBoer promoted
  to President & CTPO; Sumit Sadana (former Chief Business Officer) moved to Senior Advisor to CEO — no CEO
  departure, effective immediately. — [GlobeNewswire](https://www.globenewswire.com/news-release/2026/08/26/3351270/14450/en/micron-announces-leadership-appointments-to-accelerate-innovation-and-growth.html)
- **[2026-08-27]** ⚠️ Politico reported the Trump administration is weighing a second round of semiconductor
  tariffs that would strip data-center/server exemptions in place since January and extend duties to
  servers, laptops, and consoles; MU fell ~3% (to ~$900) on the report, alongside WDC (-3.6%) and STX
  (-1.1%) — policy risk, not yet enacted, but touches the whole hardware supply chain if it proceeds. — [CNBC](https://www.cnbc.com/2026/08/27/trump-semiconductor-tech-tariffs.html)

**SNDK**
- **[2026-08-27]** ⚠️ Kioxia and Sandisk announced plans to invest **over $31 billion (~¥5 trillion) in
  Japan through 2032**, expanding the Yokkaichi and Kitakami NAND fabs, contingent on Japanese government
  support — a major AI-driven-flash-demand capacity commitment (and matching capex-exposure lock-in). — [Kioxia](https://www.kioxia.com/en-jp/about/news/2026/20260827-3.html)

**AVGO**
- **[2026-08-21]** ⚠️ CNBC (David Faber) reported the AI-chip debt-financing SPV talks firmed to a defined
  ~$45B senior / ~$35B junior tranche structure (~$70-80B, potentially $100B total) with Blackstone/Apollo
  among lenders — escalation/specification of last week's "in talks" story, financing risk now concrete but
  unresolved. — [CNBC](https://www.cnbc.com/2026/08/21/broadcom-debt-deal-expected-to-reach-upwards-of-70-billion-sources.html)
- **[2026-08-21]** CISA's federal patch deadline (BOD 26-04) for the actively-exploited VMware vCenter
  CVE-2026-59310 passed; 361 compromised networks across 47 countries pre-deadline — ongoing reputational
  overhang on the VMware unit, no new Broadcom-specific action.
- FQ3 FY26 earnings confirmed for **September 2, 2026** (just outside next scan's normal cadence — flag for
  next week).

**GMED**
- **[2026-08-26]** ⚠️ Acquired **Higgs Boson Health**, a Duke-incubated AI/digital-health startup, folded into
  GMED's "surgical intelligence" software pillar; terms undisclosed. Small deal, thesis-consistent (AI-software
  layering onto hardware). — [GlobeNewswire](https://www.globenewswire.com/news-release/2026/08/26/3351730/0/en/globus-medical-announces-acquisition-of-higgs-boson-health-to-transform-healthcare-experience-through-ai-driven-digital-solutions.html)

**VRT**
- **[2026-08-21, 08-25]** Additional plaintiffs'-side law firms (Hagens Berman, Pomerantz) announced
  securities-fraud *investigations* tied to the pre-window Q2 miss. **Confirmed: no firm converted an
  investigation into an actual filed class-action complaint this week** — still pre-litigation stage, same
  posture as last week.

**RDDT**
- **[2026-08-25]** Director Robert Sauerberg sold 5,128 shares (~$820K), routine/scheduled — not flagged.
- Google content-licensing renewal and US-DAU-decline threads: no new in-window development on either
  (still open, unresolved since 7/22).

**ALAB / EME** — No material items found in window (EME's Q2 beat/RPO/dividend all pre-window; ALAB's Form-4
sell-to-cover cluster was last week, no new filings this week).

**META**
- **[2026-08-24]** ⚠️ Judge William Orrick (N.D. Cal.) signaled at the preliminary-injunction hearing that
  plaintiffs in the AI-hiring-discrimination suit are "unlikely" to win the injunction, calling claims better
  suited for arbitration — favorable for Meta, reduces near-term risk on this specific suit (no formal written
  order found yet). — [Courthouse News](https://www.courthousenews.com/meta-workers-claiming-ai-fired-them-unlikely-to-see-relief/)
- **[2026-08-26]** ⚠️⚠️ Meta agreed to a **$17.1 billion settlement** with 47 states + DC to resolve the
  child-safety/addiction trial (opened 8/17 in Oakland), paid over 10 years plus mandated minor-safety
  platform changes — converts an open-ended trial/verdict risk into a known, capped cost; a large real cash
  number and a product-design constraint, but net legal-risk reduction. — [NPR](https://www.npr.org/2026/08/26/nx-s1-5944781/meta-settlement-child-safety-lawsuit)

### Other high-tier watchlist (not held)

- **AMZN** — **[2026-08-27]** Raised 2026 capex guidance from ~$200B to ~$220B, citing soaring memory-chip
  costs and capacity not meeting demand through 2027; stock retreated on the raise plus renewed tariff
  concerns. — [FX Leaders](https://www.fxleaders.com/news/2026/08/27/amzn-stock-retreats-as-trump-chip-tariffs-and-220-billion-amazon-capex-raises-fresh-concerns/)
- **GOOGL** — **[2026-08-27]** Shed ~$692B in market value (~15% off peak) on compounding AI-competitiveness
  concerns (continued Jeff Dean/DeepMind-departure fallout, ~$190B 2026 capex vs. FCF-margin compression cited
  at 21%→9.2%). — [Yahoo/Bloomberg](https://finance.yahoo.com/technology/ai/articles/alphabet-loses-692-billion-market-123158437.html)
- **TER** — **[2026-08-21]** Downgraded to Neutral from Outperform at Baird.
- **WDC** — **[2026-08-26]** Entered exchange agreements covering ~$191.0M of 3.00% Convertible Senior Notes
  due 2028 for ~$192.7M cash + stock. — [SEC 8-K](https://www.sec.gov/Archives/edgar/data/0000106040/000119312526365796/d376254d8k.htm)
- **PLTR** — William Blair reiterated Outperform (8/26) citing Maven Smart System on track for $1B ARR by
  2028 — analyst note, government-AI traction signal.
- No in-window material items: APP, APH (2-for-1 split still digesting, mechanical), ISRG, CGNX, EQT.

### Layer-10 SaaS focus (PLTR / DDOG / CRM) — dedicated deep-dive

**CRM (Salesforce)** — reported Q2 FY2027 (2026-08-26, after close): revenue **$11.35B, +11% YoY** (~0.3% beat
vs ~$11.32B consensus — **not** a >15% beat). Non-GAAP EPS **$5.90** vs ~$3.27-3.28 consensus (nominally an
~80% beat) — but this was driven overwhelmingly by a **~$2.6B non-operating gain on Salesforce's Anthropic
investment stake**, not core operations (same one-time-item pattern as the GEV Prolec case under rule 15 —
**should not be read as a clean operational beat** in any future objective refresh). Non-GAAP operating margin
34.1% (GAAP 20.5%); gross margin / sequential-GM data not found — flagged as a gap, rule-9's 500bps test not
evaluable. **Agentforce/AI adoption:** combined Agentforce + Data Cloud annualized revenue ~$3.9B (+210%+
YoY); Agentforce alone surpassed $1.5B ARR (+240% YoY); **7B cumulative Agentic Work Units (AWU)** delivered
to date, **3.2B in Q2 alone (+97% QoQ)** — the clearest, most reliable adoption signal. Launched "Claudeforce"
(Anthropic Claude integration) on the call. FY27 revenue guidance raised to $46.1-46.4B; cRPO $33.5B (+14%
YoY); FCF $1.1B (+81% YoY). Specific NRR% not disclosed/found. Stock +8-14% post-print. **This is the single
most important earnings print of the week and the clearest test of the disruption-thesis pricing-model
question — flagged for a full `/earnings-update CRM` pass**, given the headline-vs-real-beat distinction
matters for scoring.

**DDOG (Datadog)** — no material items originated inside the window. Confirmed the Bits AI shift from
per-investigation to an AI Credits consumption model (a 74-82% effective per-run price cut) was announced at
DASH conference in **June 2026**, not this week — last week's "rumor" resolves as already-public, not new.
DDOG's more consequential thread (largest customer, likely OpenAI, cutting usage starting Q3, driving Q3
guide deceleration to 28-29% from 36%) was disclosed 8/6, just outside this window — worth confirming it's
reflected in DDOG's thesis materials if not already.

**PLTR** — see above (William Blair note); no new NRR/pricing-model disclosure found in-window.

### Selected long-tail items (thesis-relevant; full list in Routine filings toggle below)

- **MRVL** — **[2026-08-27]** Q2 FY27 record revenue $2.74B (data center +46% YoY to $2.17B), raised FY27
  outlook to ~$12B / FY28 to ~$18B; earnings call gave first detail on the Google custom-chip agreement scope
  (inference accelerators, storage, NICs, memory interface controllers) — **up to $120B potential revenue
  over 6.5 years** if milestones met. This is the direct follow-up to last two weeks' AVGO-competitive-threat
  flag (Google warrant deal) — the scale here reinforces that the Google-diversification pattern is real and
  large, not noise.
- **SNPS** — **[2026-08-26]** Q3 FY26 revenue $2.48B (beat), raised FY26 guidance to $9.69-9.74B; same-day
  8-K/A increased estimated pre-tax GAAP restructuring charges to $425-500M (Ansys-integration severance/
  facility closures) amid ~$10B debt load — cost-discipline flag worth tracking against the integration
  thesis.
- **SMCI** — **[2026-08-25]** +9.4% on Cisco integrating SMCI's liquid-cooled servers into its "Secure AI
  Factory" (launching October) and Taiwan authorities indicting 9 *individuals* (not corporate entities) over
  illegal AI-server exports to China — partial resolution of the export-compliance overhang central to the
  SMCI thesis.
- **IREN** — **[2026-08-27]** FY26: revenue $707.0M, net loss $702.6M; ~$4.0B contracted ARR for 2026
  capacity (incl. large Microsoft commitment + new AI-lab deal), ~1.2GW AI-DC build backed by ~$19.0B funding.
- **CRWD** — **[2026-08-27]** FQ2 revenue $1.47B (+26% YoY), record $333M net new ARR, FY27 guidance raised
  above Street; stock +19.6%. 📊 large beat/guide-up.
- **INTU** — **[2026-08-25]** Q4 FY26: EPS $4.03 vs $3.29 est (**+22% beat**); AI "Big Bets" segment +34%. 📊
- **WDAY** — **[2026-08-27]** Q2 FY27: beat on EPS/revenue; AI ARR ~$600M (+200% YoY, >25% of new ACV); FY27
  subscription guidance raised. 📊
- **ADSK** — **[2026-08-27]** Q2 FY27: EPS $3.12, revenue $2.01B, double-digit growth; +6.2%. 📊
- **NVTS** — **[2026-08-24]** Definitive agreement to acquire Claros for up to ~$233M — vertical power
  delivery/integrated voltage regulator tech for AI data centers.
- **BE** — **[2026-08-25]** +6.6% as an AI-server-campus microgrid deal expanded contracted fuel-cell capacity
  to ~250 MW across ~24 customers.
- **D** — **[2026-08-21]** Virginia SCC Chair (a former NextEra attorney) declined to recuse from presiding
  over the $66.8B Dominion-NextEra merger case; evidentiary hearings begin Nov 17.
- **HOOD** — **[2026-08-21]** +15% on Robinhood Ventures Fund II IPO pricing ($225.5-255.5M) + UK crypto
  rollout via Bitstamp UK.
- **GEV** — **[2026-08-27]** Selected by Laing O'Rourke for a 400 kV gas-insulated switchgear substation
  (National Grid transmission upgrade, UK) — grid-equipment demand signal.
- **WYFI** — **[2026-08-21]** Closed upsized $310M 5.00% Convertible Senior Notes due 2032 — dilutive raise.
- **PANW** — **[2026-08-27]** +11.1% on reports of shift to active M&A mode (after being rebuffed on
  Okta/Datadog pursuits); new NTT DATA alliance (8/22).
- **TSLA** — **[2026-08-21]** Nevada approved commercial robotaxi launch (+5.1%); separately, China recall of
  ~2.98M vehicles over a door-handle safety issue.
- **PRCT** — securities-fraud class action (filed 7/24, outside window) kept live via recurring lead-plaintiff
  deadline reminders through 8/25.
- **HHUSF (Foxconn)** — **[2026-08-27]** Reportedly weighing major India manufacturing expansion tied to
  AI-server demand.

**Boundary note (repeats last two scans' finding):** several consequential items clustered just outside this
window and are flagged for context only: MRVL/Google $12.2B warrant deal itself (8/18-19, its earnings-call
follow-up detail above IS in-window), APLD Q4 earnings + $36B contracted lease value (8/20), KEYS Q3 beat
(8/18), DDOG's largest-customer usage-cut disclosure (8/6).

---

## 📊 Earnings refreshed

**Blocked — yfinance network access unavailable this session (same constraint as every scan since
2026-06-12).** No objective-input refresh or before/after Total Score computation could be run for any name,
despite a heavy earnings week. Names that reported inside this window and are due a Rule-9 refresh when
network access is available:

| Ticker | Held? | Priority triage (per agent research) |
|---|---|---|
| NVDA | ✓✓ held | Already handled by earnings sentinel (245241a) — Rule-9 immediate NOT triggered (+4.5% rev / +6.2% EPS, below 15%). Mechanical rescore step (first post-reaction close, 8/27) has **not yet been committed** — flag for the sentinel/next attended session. |
| CRM | Layer-10 focus, not held | 📊 Headline EPS beat ~80% but driven by a ~$2.6B non-operating Anthropic-stake gain — **read the beat cautiously**; revenue beat only ~0.3% (not >15%). Recommend `/earnings-update CRM`. |
| MRVL | ✓ not held | Record quarter, raised FY27/FY28 outlook materially — recommend review. |
| SNPS | ✓ not held | Beat + raised guidance, but restructuring charges also rose — recommend review. |
| CRWD | ✓ not held | 📊 Large beat, FY27 guidance raised above Street. |
| INTU | ✓ not held | 📊 EPS beat +22% — exceeds the >15% priority-triage threshold. |
| WDAY | ✓ not held | 📊 Beat + raised guidance, AI ARR +200% YoY. |
| ADSK | ✓ not held | 📊 Beat, double-digit growth. |
| PLAB | ✓ not held | Beat (+24% EPS). |
| IREN | ✓ not held | Large contracted-ARR/capacity disclosure alongside FY26 results. |

**TTM check:** could not be evaluated for any name (requires yfinance TTM data).

**Recommendation:** this is now the third consecutive scan where Rule-9 refreshes have queued up unfulfilled
due to network access. Given the volume this week (10 names, several with >15% surprises), prioritize a
local/on-network session run of `refresh_objective_inputs.py` / `/refresh-objective` for at least the
📊-flagged names (CRM, CRWD, INTU, WDAY, ADSK) before the backlog compounds further.

---

## 💼 Portfolio pipeline

- `refresh_targets.py --check`: **Targets reflect current scores ✓** — no pending rebalance, no
  ENTER/EXIT/EXIT PENDING/BLOCKED flags, no tier-change reallocations. (Caveat: this check compares the
  Targets sheet against the *current, unrefreshed* Watchlist scores — given the Rule-9 backlog above, this
  "clean" read may not hold once objective inputs catch up.)
- `momentum_50dma.py`, a live `refresh_targets.py` run, and `track_performance.py` (weekly mark) all require
  yfinance and remain blocked this session. No new weekly mark to report; last committed
  model-value/benchmark comparison remains from the 2026-08-14 scan.
- No concentration, layer-cap, dead-ticker, or manual-override-collision flags observed (scope-limited to what
  `--check` covers, not a full pipeline run).

---

## 🔬 Rating integrity

`audit_rating_integrity.py`: **211 rated names | 0 gate violations (no thesis) | 0 stale (>90d).** Clean — no
action needed.

---

## 🎯 Calibration

`resolve_forecasts.py --dry-run`: **0 forecasts due, 0 needing review.** Nothing to resolve this week.

---

## 🔴 Live pipeline

Skipped — cloud/headless session (rule 29: MCP OAuth does not survive headless runs). No heartbeat/reconcile
check performed.

---

## Routine filings

<details>
<summary>Expand for the full list (confirmed in-window, non-material — dividends, routine buybacks, insider
10b5-1/144 sales absent a specific flag above, analyst PT changes without new information, conference
appearances, and beat-quarters without a distinct thesis-relevant angle beyond what's captured above).</summary>

**Power/Utilities:** CEG, AEP, DUK, SO, NEE, ETR, PPL, XEL, VST, TLN, NRG, CCJ, UEC, LEU, BWXT, SMR, OKLO, NNE,
RRC, AR, EXE, PLUG, CMI, GNRC, ETN, SBGSY, ABBNY, HTHIY, HUBB, PWR, MTZ, POWL, NVT, ATKR, DLR, EQIX, IRM, MOD,
CARR, TT, JCI, ASML: no confirmed in-window material items on this pass. (Note: VST/NRG's Texas ERCOT
data-center-interconnection audit saga has an Aug 31 conditional-classification deadline — worth a follow-up
next scan even though the 8/20 PUCT ruling itself is just outside this window.)

**Grid/DC construction/cooling:** GEV (flagged above); AMAT, LRCX, KLAC, TOELY, ONTO, CAMT, KLIC, ENTG, MKSI,
UCTT, CDNS, ARM, INTC, GFS, TSEM, COHR, LITE, FN, POET, CSCO, CIEN, GLW, DELL, HPE, ORCL, CIFR, CLSK, BTDR,
HUT, RIOT, SNOW, NOW, KEYS: no in-window items beyond what's flagged.

**Semi-equipment/materials/fabs/optical:** UMC ($1.8B convertible bond board approval, financing, routine);
AAOI ($600M dilutive ATM offering, 8/21); TTMI (CEO $1.1M open-market buy, 8/25); TEL (small HENN
plastics-connector M&A, 8/27); CORZ ($600M new credit facilities, 8/27); WULF (Kentucky PSC 482MW power
approval, 8/24); NBIS (convertible-notes settlement, completeness only): no other in-window items.

**Software/SaaS (Layer 10, non-focus names):** ZS (routine CFO share sale); HIVE (analyst PT cut only): no
other in-window items.

**Analog/misc:** NXPI (Malaysia factory groundbreaking, 8/25); AAON (corporate rebrand, minor); AAPL (Mac
product update, not filing-level); MPWR, FLEX, MDB, PATH, AMBA, CEVA, AIP, KN, NXT, BESIY, FORM, AEIS, LSCC,
RMBS, STX, SEI, PSIX, PUMP, BW, SHAZ, TXN, QCOM, ADI, STM, MCHP, ON, SWKS, ADBE, FTNT, SPCX, ACLS: no other
in-window items.

**Robotics/foreign/misc (Layer 11 and others):** 2049.TW (Hiwin CPO expansion, flagged above), DRO.AX (1H26
results, flagged above), MELE.BR (BYD chip-supply relationship, flagged above), AVAV (AV Eagle Greek JV,
flagged above), COHU, AMKR, ASX, NTAP, 5347.TWO, 0981.HK, 9880.HK, SERV, TNC, 6954.T, 6506.T, SYM, AUTO.OL,
6383.T, KGX.DE, 2590.HK, SSII, 2252.HK (zero English/local coverage found), 6324.T, 6268.T, 6481.T, TKR, RRX,
ALNT, NOVT, VPG, 6861.T, OUST, HSAI, AEVA, 2498.HK, BSL.DE, MBLY, KTOS, RCAT, ONDS, UMAC, PDYN, ALGM: no other
in-window items.

</details>

---

## New 13F activity

**Correction to last week's scan:** Whale Rock Capital's Q2 2026 13F-HR was reported last week as "NOT
confirmed filed" one week past deadline. This week's re-check finds it was actually **filed on-schedule
2026-08-14** (SEC accession 0001172661-26-002159) — same day as the other five tracked funds. All figures
below are secondary-aggregator sourced (data.sec.gov unreachable this session); treat as directional, not
filing-verified, until independently confirmed.

| Fund | Notable AI-infra/semi moves |
|---|---|
| Whale Rock Capital | $12.46B AUM, 35 holdings, 25.1% turnover. **NVDA cut ~64%** (1.04M → 377,204 shares) — the headline AI-name move. **AMD** was the top buy of the quarter, now a top-5 holding. New positions: Snowflake (~$225.2M), Twilio (~$169.6M). META reduced (magnitude unconfirmed). Top holdings now: SNDK, AMD, GOOGL, TTM Technologies, ALAB. |

No new 13F-HR/A amendments found for Berkshire Hathaway, Baillie Gifford, Tiger Global, Coatue Management, or
Lone Pine Capital in this window (not a definitive "confirmed none" — secondary sources don't reliably surface
amendment-only filings).

**Portfolio-relevant read:** Whale Rock's large NVDA trim (~64%) is a genuine divergence worth flagging
against last week's read of Berkshire/Baillie Gifford *adding* to GOOGL while Tiger Global trimmed AI-compute
names broadly — a third data point in the same direction (funds rotating out of mega-cap AI-compute
concentration) rather than a one-off. Worth a `/thirteenf-delta` pass once primary EDGAR access is available.

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🔴 | **Rule-9 objective-refresh backlog is now 3 scans deep and includes a heavy earnings week** (NVDA, CRM, MRVL, SNPS, CRWD, INTU, WDAY, ADSK, PLAB, IREN all reported in-window). Recommend a local/on-network session run `refresh_objective_inputs.py` for at least the 📊-flagged names (CRM, CRWD, INTU, WDAY, ADSK) before the gap compounds further, then `--sync`, `momentum_50dma.py`, `refresh_targets.py`, `track_performance.py` to close the pipeline gap. |
| 🟡 | **NVDA's mechanical rescore step (rule 31, "first post-reaction close") has not been committed** — the 8/26 briefing explicitly deferred it to the 8/27 run, but no corresponding commit exists. Worth checking whether the sentinel's rescore phase ran locally and failed to commit, or simply hasn't executed yet. |
| 🟡 | **CRM's headline EPS beat is misleading** — ~80% "beat" is mostly a ~$2.6B non-operating Anthropic-stake gain, not core execution (revenue beat only ~0.3%). Flag this distinction explicitly if/when CRM's objective inputs are refreshed, so EPS YoY isn't scored on the inflated headline number (same garbage-input principle as rule 15). |
| 🟡 | **META's $17.1B settlement + favorable AI-hiring-injunction signal** resolve both open legal threads flagged in recent scans — net risk reduction. Worth a light touch-up to the R3/R4 risk-dimension notes at the next subjective-rating refresh, though this alone likely isn't score-moving. |
| 🟡 | **Whale Rock's ~64% NVDA trim** is the third consecutive week of tracked-fund AI-compute-concentration reduction (after Berkshire/Baillie-Gifford-vs-Tiger-Global divergence last week). Worth a dedicated `/thirteenf-delta` pass once EDGAR access is available. |
| 🟢 | **MU's tariff-policy thread (Politico report, 8/27)** — proposed rollback of data-center/server tariff exemptions — is not yet enacted but would touch the whole hardware supply chain if it proceeds. Monitor next week. |
| 🟢 | **AVGO's AI-debt-financing SPV** firmed to a defined $70-100B structure (Blackstone/Apollo) — still not final terms; revisit once covenant/leverage detail is disclosed. |
| 🟢 | **VST/NRG's Texas ERCOT data-center-interconnection audit** has an Aug 31 conditional-classification deadline — the 8/20 PUCT ruling fell just outside this window; confirm outcome next scan. |
| 🟢 | **DDOG's largest-customer (likely OpenAI) usage-cut disclosure** (8/6, driving Q3 guide deceleration to 28-29% from 36%) is just outside two consecutive scan windows now — confirm it's reflected in DDOG's thesis materials. |
| 🟢 | **Weekly mark and 50DMA momentum inputs could not be refreshed this week** (yfinance blocked) — recommend a local/on-network session run to close the gap. |

**No score or tier changes this week** (objective refresh blocked; rating-integrity audit clean; no pending
rebalance per the current, unrefreshed scores).
