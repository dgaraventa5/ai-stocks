# Weekly News Scan — 2026-09-18

**Scope:** 214 watchlist tickers. Scan window: **2026-09-05 – 2026-09-18** (14 days —
covers a gap week; no scan was filed for the week of 2026-09-11). Last committed scan:
2026-09-04 (`tracking/weekly-news-scan-2026-09-04.md`, commit `db5bb34`).

## Local completion pass (2026-09-18, attended local session — read this first)

The cloud session below could not reach SEC EDGAR or Yahoo Finance. A local session the
same day completed every blocked step. **Where this pass and the cloud pass disagree, this
pass wins** (it is primary-source); cloud-pass text is kept for the audit trail and marked
where superseded.

| Step | Status |
|---|---|
| Full 214-ticker EDGAR 8-K/6-K sweep, 2026-09-05 → 09-18 (`weekly_scan_runner.py`) | ✅ 191 names queried on primary EDGAR; 23 foreign lines have no EDGAR CIK (listed below). **69 filings** found and all 69 primary documents read (HTTP 200). |
| Rule-9 objective refresh | ✅ ALAB, RDDT, TER, VRT, PLTR (backlog) + ORCL, ADBE, AVAV (in-window Item 2.02 reporters). |
| `momentum_50dma.py` → `recalc --sync` → `refresh_targets.py` → `track_performance.py` | ✅ **NTAP exit confirmed**, one model event, one ticket written. |
| Capitulation check (rule 32-A) on NTAP | ✅ clean — no firing, no forecast logged. |
| 13F-HR tracked-fund check | ✅ none in window. **Two wrong fund CIKs found and fixed** (see 13F section). |

**News logs (rule 6):** 29 `per-stock/*/news-log.md` files appended. QCOM and ADI have no
news-log file — their items live only in this doc (gap flagged, not created).

**Not done this pass:** no Robinhood reconciliation (Step 10b) — not requested, and an
undeclared cash flow would falsely raise the halt flag. Heartbeat check only (see 🔴).

---

## Execution note — ORIGINAL CLOUD PASS (network egress blocked; superseded where the local pass re-ran the step)

**SEC EDGAR (`data.sec.gov`, `www.sec.gov`, `efts.sec.gov`) and Yahoo Finance
(`query1/2.finance.yahoo.com`, `fc.yahoo.com`) are 403-blocked from this session's egress
proxy** — confirmed via the proxy's own status endpoint (`recentRelayFailures`:
`connect_rejected`, "gateway answered 403 to CONNECT", on `www.sec.gov:443`) and by direct
`curl`/`requests`/`yfinance` calls, all of which failed identically. Per the proxy README
this is an organization policy denial, not a tool-config problem — it was not retried or
routed around. This is the same recurring failure CLAUDE.md documents as ongoing "since
2026-06-12."

**Consequence — what could and couldn't run:**
- `scripts/weekly_scan_runner.py` (primary EDGAR 8-K/6-K sweep): **could not run** — CIK
  lookup itself fails. Substituted the documented fallback, `WebSearch`, run directly
  (25 individual ticker queries + 6 sector-sweep queries — see below) rather than via
  `web_scan.py`'s full 214-ticker query plan, which would have required roughly 250+
  individual searches in a single session with no parallel-subagent capability available
  this run. **Coverage: full depth on the 25 priority names (17 holdings + 8 non-held
  ✓✓-tier names); sector-sweep only for the remaining ~189 tail tickers.** This is a
  real coverage gap versus the 2026-09-04 scan (which used 10 parallel subagents to touch
  all 214) — flagged, not silently narrowed.
- `scripts/audit_rating_integrity.py` and `scripts/resolve_forecasts.py`: **fully local,
  ran cleanly** (see below).
- `scripts/momentum_50dma.py`, `scripts/refresh_targets.py` (needs yfinance for the
  dead-ticker check), `scripts/capitulation_flag.py` (needs SEC XBRL via
  `expectations_flag.quarterly_revenue_sec`): **crashed on the network call, not run.**
  Their outputs below are read from the last committed state (2026-09-08) rather than
  freshly computed.
- `scripts/track_performance.py`: not re-run locally, but `daily-refresh.yml` (GitHub
  Actions, separate network) kept `tracking/performance-series.json` current through
  **2026-09-17** — read directly, not independently re-verified.
- 13F-HR tracked-fund check (Step 5): **blocked**, no data — cannot confirm or deny new
  filings this window.

**No data is fabricated to fill these gaps.** Where a mechanical script couldn't run, that
is stated explicitly rather than papered over.

---

## Step 0 — Mental models (pre-scan, portfolio holdings)

17 holdings, all ✓✓ tier (no ✓✓✓ currently exists on the sheet — max score is NVDA 84.62).
Priors going in, largely unchanged from 2026-09-04/08:

**NVDA** — dominant AI-accelerator vendor mid-Blackwell/Rubin ramp; Q2 FY27 beat (8/26)
already fully absorbed; Hugging Face acquisition ($12.93B) already confirmed pre-window.
**FIX** — DC-construction mechanical contractor, record backlog, Hunt Electric bolt-on
already absorbed; heavy insider selling is a standing watch item. **TSM** — sole
advanced-node foundry, capex trajectory keeps ratcheting up ($60-64B FY26 raised 7/16).
**CRDO** — optical/AEC interconnect, Q1 FY27 beat-but-fell (9/1) already absorbed; margin/opex
concerns and customer concentration are the open threads. **AVGO** — custom-ASIC (Google TPU)
name; Q3 FY26 beat-but-guide-miss (9/2) already absorbed by the earnings sentinel; the
$60-100B AI-debt SPV financing remains **unsigned**, R3 deferred to an unfiled 10-Q footnote.
**ANET** — clean AI-networking name, Meta/Microsoft concentration (42% combined) the standing
R1 risk; Spectrum-X competitive thread open. **SNDK** — HBM/NAND beneficiary, +574-800% YTD,
Meta flash-supply report still technically unconfirmed by either company. **MSFT** — Azure/AI
growth story; FY27 capex guide more than doubled to $255-260B (7/29, already refreshed 8/2).
**MU** — HBM-bottleneck beneficiary; Sadana C-suite exit (8/26) and the Taiwan union
profit-sharing dispute are the open operational threads; next earnings 9/30. **GMED** —
distinct Layer-11 surgical-robotics thesis, thin news-log/thesis history. **ALAB** — Amazon
Trainium3/Scorpio X ramp story; Q2 FY26 beat (8/4) **never objective-refreshed** (see below).
**EME** — DC-construction peer to FIX, clean. **VRT** — AI-DC power/cooling; Q2 miss (7/29,
-17%) triggered a widening securities-fraud-investigation roster (4 firms as of 9/1). **META**
— AI capex/Superintelligence Labs reorg; "Meta Compute" buyer→seller optionality still
unconfirmed at scale. **AMZN** — AWS re-acceleration (Q2 +37%), FY26 capex raised to ~$220B;
just entered the portfolio at rank 15 (2026-09-08). **RDDT** — thinnest-research position;
Google-licensing-renewal and DAU-decline threads open; Q2 beat (7/30) **never
objective-refreshed** (see below). **NTAP** — currently **EXIT PENDING** (rank 20, since
2026-09-08), despite a strong Q1 FY27 beat-and-raise already captured in that same refresh.

---

## ⚠️ Material events

### Portfolio holdings

**TSM** — **[2026-09-17]** ⚠️ Announced a new Longtan expansion: three additional wafer fabs
targeting 1.4nm-and-below processes, first fab targeted for completion ~2030, total investment
>NT$1 trillion (**~$31.4B**). Adds to the already-elevated capex trajectory (FY26 guide raised
to $60-64B on 7/16, $265B total Arizona commitment). — [GuruFocus](https://www.gurufocus.com/news/9087313/taiwan-semiconductor-tsm-plans-expansion-with-314-billion-investment)
- August monthly revenue +53% YoY / +10% MoM to NT$514.81B, 4th straight monthly increase —
  demand/capacity remains the story, no new margin or customer disclosure this window.

**VRT** — **[September 2026, exact date unconfirmed]** ⚠️ Acquired **UtilityInnovation Group
(UIG)**, a microgrid-controls/behind-the-meter-power specialist — extends the
"build-your-own-power" bolt-on strategy (ThermoKey 6/12, Strategic Thermal Labs 4/27). Deal
terms not found. — flagged UNVERIFIED EXACT DATE, found via a sector sweep not a primary
filing; confirm via a future EDGAR pass.
- Securities-fraud investigation roster (Pomerantz, Schall, Bronstein Gewirtz, Hagens Berman)
  remains at the **pre-litigation solicitation stage** — no new firm, no filed complaint found
  this window (last addition was Hagens Berman, 9/1, already reported 2026-09-04).
- Routine: $0.0625/share quarterly dividend declared 9/2, payable 9/24.

**MU** — **[ongoing, developing]** ⚠️ Taiwan union mediation continues: the Taoyuan union says
it may move toward a strike vote if talks scheduled for **9/18 (today) and 9/21** don't
produce a concrete profit-sharing proposal. Micron announced FY26 cash rewards (incl. a
T$1M Taiwan bonus) that unions say doesn't meet their core 15%-of-operating-profit ask. Still
no strike, no vote date set — an update to the standing thread, not an escalation.
Next earnings 9/30 (outside window).

**ANET** — No new in-window company disclosure found. (Context: the Q2 FY26 print, 8/4 — 3rd
outlook raise this year to ~$12.6B, tripled multi-year supplier commitments to $9.7B — predates
this window and was not previously logged; noted here for completeness, not as a new event.)
Routine: joining the S&P 100 on 9/21 (replacing Nike); director Mark Templeton filed an
intent-to-sell for 20k shares (9/8).

**META** — **[September 2026]** Acquired Swedish AI startup **Stilla.ai**, folded into the
Meta Business Agent product (automated business messaging across WhatsApp/Messenger/Instagram
for 1M+ businesses). Iris in-house AI chip (Broadcom design / TSMC fab) targeted to begin
production this month. Launched **Meta One** (AI-usage subscription) and **Muse** (personal AI
agent). None of these change the thesis materially — incremental AI-monetization/build-out
news consistent with the standing model. Routine: $0.525/share dividend declared, payable 9/28.

**AMZN** — **[2026-09-08]** Cybersecurity executive Kevin Mandia (Mandiant founder) elected to
the Board — a notable but non-thesis-moving governance addition. Continued incremental
layoffs (121 more WA corporate/fulfillment roles) alongside the AI-capex ramp — consistent
with the pattern already logged. No new material items on the AWS/Trainium/capex thread this
window.

**RDDT** — No new in-window company disclosure. Stock jumped on S&P 500 inclusion (9/2,
pre-window) and "fastest monthly user growth in 2026" reporting (9/10); EU Kids Act
child-safety regulation flagged 9/17 as a forward risk to monitor, no concrete rule yet.

**NTAP** — See 💼 Portfolio pipeline below — no *new* in-window disclosure (Q1 FY27 beat was
9/2, pre-window, and was already captured in the 2026-09-07/08 refresh).

**NVDA, FIX, AVGO, SNDK, MSFT, GMED, ALAB, EME, CRDO** — no new in-window material items found
beyond what's already logged/priced. MSFT published a provisional AI-model "code of conduct"
(9/14, restricting weapon-assistance/autonomous-goal-setting/concealment) — an industry
self-governance signal (coincides with Anthropic/OpenAI leaders discussing a development
slowdown) rather than a company-specific fundamental event; noted for context only. CRDO
continued to be volatile (down cumulatively ~32% over 30 days post its 9/1 print, then +8% on
9/16) — sentiment/valuation churn on already-known fundamentals, not new information.

### Non-held ✓✓-tier names

**GOOGL** — Gemini 3.8 Flash launch + new cybersecurity-focused model; Cloud backlog +82% YoY
to $155B (context from Q2/Q3 commentary, not a fresh disclosure this window); Waymo announced
its first EU robotaxi target (Munich, commercial by late 2027) — expansion-optionality news,
not thesis-moving this window.
**PLTR** — UBS raised PT to $250 (9/15); reported "tightening access" to third-party
OpenAI/Anthropic models over data-security concerns for government/enterprise customers — a
governance move, not a customer loss. No new contract disclosures found this window (Army
TITAN $127M and the Zaffino hire were both pre-window, 9/1-2, already logged 2026-09-04).
**ISRG** — EU approval of da Vinci SP for gynecologic procedures; a favorable meta-analysis
(9/8) on outcomes vs. laparoscopic/open surgery across 13 conditions — supportive but not
new-contract/guidance news.
**TER, ALAB (again), APH, CGNX, EQT, 6861.T (Keyence)** — no material in-window items found;
routine analyst-target moves and conference appearances only (EQT: UBS PT $73→$77 9/14, Stifel
initiated Buy 9/4; CGNX: TipRanks reaffirmed Buy/$80 9/15).

### Tail sweep (sector-level, not exhaustive — see coverage-gap note above)

- **Power/grid/DC-construction:** Bloom Energy's 2.8GW Oracle fuel-cell MSA and various
  behind-the-meter/microgrid M&A (a sector theme VRT's UIG deal, above, is part of) continue;
  no new items surfaced for AR, BE, GEV, D/NEE beyond what prior scans logged.
- **Neoclouds/bitcoin-miner pivot (Layer 9, not portfolio holdings):** **IREN** reported a
  $1.6B Dell AI-infra deal and a $9.7B Microsoft partnership with "Nvidia preferred partner"
  status (dates not independently pinned down this pass) — a large move for that cohort,
  flagged for a dedicated look next scan given it's outside this session's priority-ticker
  budget.
- **Layer-10 SaaS disruption theme:** Reported broad September software-sector volatility
  after "OpenAI's GPT-6 Astra" reportedly revived AI-disruption fears (CRM, INTU, NOW named as
  falling sharply on this) — thematically relevant to the rule-16 R5 disruption dimension for
  Layer 10 names generally; none of our three Layer-10 focus names from the 2026-09-04 scan
  (PLTR/DDOG/CRM) are portfolio holdings, and this pass didn't have budget for a fresh
  deep-dive — flagged as a theme to watch, not confirmed against any of our own names'
  numbers.
- **Robotics (Layer 11, not holdings):** Ongoing consolidation (Zebra Technologies roll-up
  buyback, Ouster/SteroLabs, Grid Dynamics/Acumen) and Figure AI's BMW Spartanburg ramp —
  sector color, no GMED/ISRG/CGNX-specific read-through found beyond what's logged above.
- Nothing found suggesting a going-concern, auditor change, delisting, or bankruptcy event
  anywhere in the watchlist this window.

### EDGAR primary-source sweep (local completion pass — full watchlist)

Source for every item: the 8-K/6-K on SEC EDGAR, filing date in brackets. 69 filings across
45 names; the items below are the ones that could plausibly move a thesis. Everything else is
under Routine filings.

**Corrections to the cloud pass (WebSearch-sourced) now that primary filings are in hand:**
- **VRT / UtilityInnovation Group — confirmed, and much bigger than "bolt-on".** 8-K filed
  **2026-09-02** (acc. 0001193125-26-379306, Items 1.01/7.01 — two trading days *before* this
  window, which is why the in-window sweep shows no VRT 8-K): merger agreement dated 9/1 to
  acquire Utility Innovation Holdings for **~$1.45B cash upfront + up to $1.15B earn-out** (two
  EBITDA tranches), HSR-conditioned, Q4 2026 close expected, funded from existing resources.
  The cloud pass had "terms not found / date unconfirmed" — both now resolved. ⚠️ Largest VRT
  deal to date; bears on R3 (cash use) and the behind-the-meter-power thesis leg. The filing
  is already sitting untracked in `per-stock/VRT/filings/`.
- **TSM Longtan ~$31.4B expansion** — **not in any TSM 6-K this window** (the only TSM filing
  is the 9/10 August-revenue 6-K). Remains a single-secondary-source item (GuruFocus) —
  downgrade to UNVERIFIED until a 6-K or TSMC release confirms.
- **IREN "$1.6B Dell / $9.7B Microsoft"** — IREN filed **no 8-K/6-K in the window**; those
  items are not new-this-window. Drop the "dedicated look" flag as a *new event*.
- **CLSK Meta lease** — the 9/17 deck restates the 175 MW Sandersville / Meta-subsidiary lease;
  that lease was **already logged** (signed 2026-07-10, in `capacity-mw.json` and the CLSK
  news-log). Only the financing below is new. (CLAUDE.md rule 13's "CLSK… zero AI/HPC
  contracts" parenthetical is now stale wording — doc fix suggested, not made here.)

**Portfolio holdings**
- **AMZN** [9/14, 8-K 8.01] — closed a **£4.25B** four-tranche sterling notes offering
  (5.200% 2029 → 6.650% 2045). Capex-funding-consistent, immaterial to the balance sheet.
  [9/9, 5.02] Mandia board election confirmed on primary. AMZN is also the counterparty in two
  watchlist customer wins this window (GNRC, QCOM — below), both equity-warrant-linked: a
  data point on how AMZN is locking up DC supply.
- **SNDK** [9/11, 1.01] — revolver refinanced into a **$1.5B facility due 2031** (SOFR+1.375%,
  collateral falls away at investment grade). Liquidity housekeeping, no new drawn debt.
  [9/16, 5.02] exec pay adjustments — routine.
- **NTAP** [9/11, 5.07] — annual meeting results, charter officer-exculpation amendment. Routine.
- **TSM** [9/10, 6-K] — August revenue NT$514.81B, +53.3% YoY / +10.1% MoM; Jan–Aug +39.3% YoY
  (confirms the cloud pass on primary).
- No 8-K/6-K in window from: NVDA, FIX, CRDO, AVGO, ANET, MSFT, MU, GMED, ALAB, EME, VRT, META,
  RDDT. (The MU union, META Stilla.ai and MSFT items in the cloud pass remain
  secondary-sourced — none was filed as an 8-K.)

**Layer-10 SaaS focus (PLTR / DDOG / CRM — NRR, AI adoption, pricing)**
- **CRM** [9/17, 7.01 — Dreamforce Investor Day deck] ⚠️ (R5-relevant, no guidance change):
  reaffirmed FY27 revenue $46.1–46.4B and FY30 $63B+; announced a **$25B accelerated share
  repurchase** (≥14% share-count reduction at an expected ~$182 average). AI disclosure is the
  useful part: top-100 agentic-usage customers show **>2x ARR uplift** in the 18 months since
  Agentforce launch; agentic adopters 1.5–2x ARR uplift **"with some seat optimization"** —
  i.e., management itself concedes seats shrink as agents land, with consumption/ARR uplift
  more than offsetting *in the adopter cohort*. That is the first primary-source quantification
  of the seat-compression-vs-agent-uplift trade we track under R5 / the SaaS renewal thread.
  No NRR figure disclosed. Data 360 ~$1B AOV. Caveat: cohort is self-selected top adopters.
- **PLTR** — no 8-K in window (Form 4 only, 9/17). One primary-source read-through: **NBIS
  6-K [9/8]** names Nebius as Palantir's *preferred sovereign AI infrastructure partner*
  (Nebius compute inside the Palantir enterprise perimeter for commercial customers; no $ or
  MW). No NRR/pricing disclosure this window.
- **DDOG** — no 8-K in window. Heavy insider-form cadence continues (9 Form 4s, 7 Form 144s
  in 14 days); 10b5-1 status **not verified** (forms not opened) — flag for the M3 review, not
  scored here.
- **ADBE** [9/8, 5.02] ⚠️ **CEO succession:** Anil Chakravarthy becomes President & CEO
  12/1/2026; Shantanu Narayen → Executive Chair; **David Wadhwani (head of the core Creativity
  & Productivity business) steps down 9/27**. Interim CFO (Steve Day) still in seat. For a
  name rated R5-exposed, losing the creative-business head during the AI transition is a real
  D3/R5 input. [9/10, 2.02] Q3 FY26: revenue $6.76B +13%, non-GAAP EPS $6.13 (+0.7% vs
  consensus per Benzinga — secondary), ARR $27.5B, "AI-first ARR" +150% YoY, FY26 guide raised.
- **ORCL** [9/10, 2.02] ⚠️ Q1 FY27: revenue $19.35B +30%; cloud infrastructure $7.39B
  **+121%**; **RPO $664B** (+$209B YoY, >$30B new AI contracts in-quarter); **capex $28.5B in
  one quarter** (vs $8.5B), FCF ≈ −$5B, completed a **$20B ATM equity sale**, interest expense
  +55%. FY27 guide ≥$90B revenue / $8.10 non-GAAP EPS. EPS surprise +10.3%, revenue +1.1%
  (CNBC citing LSEG — secondary; under the 15% rule-9 trigger). [9/14] Ellison cancelled his
  10b5-1 sale plan, no shares sold — M3-relevant.

**Customer wins / capacity (non-held)**
- **GNRC** [9/16, 1.01/3.02] ⚠️ Long-term **Amazon** backup-generator supply agreement —
  initial deliveries **$2.4B over 2027–28**; Amazon gets a warrant for up to 1.69M GNRC shares
  at $200.93 vesting against up to **$8B** of payments. First hyperscaler-scale contract for
  GNRC — directly relevant to D1/D5.
- **QCOM** [9/8, 3.02] ⚠️ Warrant to **Amazon** for up to 25M shares ($161.26 strike, to 2036)
  vesting against up to **$60B** of Amazon purchases of Qualcomm **server-chip** products;
  3.75M shares vested at signing on initial commitments. A data-center silicon customer win
  for a name we rate low on AI Thesis (30) — D1/D5 review warranted.
- **BTDR** [9/16, 6-K] ⚠️ Malaysia A102 (9.5 MW, GB300) 100% contracted, >$800M expected
  revenue, prepayments cover ~50% of capex; new 10-yr 65.1 MW agreement (Johor AI capacity →
  86.8 MW); AI Cloud ARR ~$86M (from ~$76M); 200 acres added at Rockdale TX.
  **`capacity-mw.json` BTDR entry is as-of 2026-04-30 — stale, refresh due (rule 13).**
- **CORZ** [9/10, 7.01] — ERCOT large-load status: Denton 297 MW + 74 MW, Pecos 300 MW base
  + 300 MW studied, Hunt 431 MW — all *conditionally* approved. De-risks ~1.4 GW of Texas
  power; `capacity-mw.json` CORZ entry is as-of 2026-05-06 — review.
- **LEU** [9/9, 9/17] — two definitive multi-year HALEU supply contracts with prepayments
  (Radiant Industries; Antares Nuclear). No values disclosed.
- **WYFI** [9/14, deck] — NC-1 10-yr / 40 MW IT contract with Nscale (~$865M TCV), >$550M
  cloud TCV won since May; ~70 MW online by YE26E.
- **TSEM** [9/17, 6-K] — high-volume shipments of NewPhotonics laser-integrated optical
  engines (800G–1.6T) on Tower's SiPho platform; unquantified.
- **ASX** [9/9, 6-K] — August revenue +45.7% YoY; ATM (packaging/test) segment **+53.1% YoY**.

**Financing events**
- **CRWV** [9/17] ⚠️ launched **$3.0B convertible notes due 2033** (+$500M greenshoe) **and a
  new ATM for up to 35M Class A shares**; deck shows total debt $35.6B ($38.6B pro forma),
  8.3% weighted cost, backlog $104.2B **excluding >$25B of commitments added early Q3**. R3.
- **CLSK** [9/17–18] ⚠️ priced **$2.276B 7.875% senior secured notes due 2031** at 98.5 to
  finish the Meta-leased Sandersville campus (~$11.9M per IT MW); project-level debt but with
  a **parent completion guarantee** — R3.
- **LEU** [9/11] ⚠️ ~$500M equity raise (shares + pre-funded warrants) plus four series of
  common warrants (~$500M exercise value each, strikes $227–$363); in advanced talks to buy a
  domestic manufacturing supplier for ~$115–125M.
- **OKLO** [9/11] ⚠️ prior **$1.0B ATM fully used in ~4 months** (18.0M shares, ~$55.6 avg);
  new $1.0B ATM opened.
- **GLW** [9/11] ⚠️ new **$2.0B ATM** equity program — unusual for GLW; watch for use.
- **GFS** [9/8, 6-K] ⚠️ issuing **9.9M shares to the U.S. Department of Commerce** at $37.85
  (~$375M by arithmetic; total not stated) with voting/transfer restrictions — USG becomes a
  shareholder.
- **NVT** [9/15–17] — financing the $1.75B (+ up to $550M earn-out) Maverick Power
  acquisition (announced 8/21): $800M 6.150% notes due 2036 + $600M delayed-draw term loan +
  $250M revolver capacity.
- **TTMI** [9/10] — $500M 6.750% notes due 2034 + expected $1.1B incremental term loans to
  fund the Epiq Solutions acquisition (~$1.6B new debt). R3.
- **ADI** [9/17] $3.0B four-tranche notes; **DELL** [9/10, 9/15] $5.0B notes (refinancing 2026
  first-lien); **ADSK** [9/10] $1.0B notes repaying its term loan; **EXE** [9/16–17] $500M
  notes — all investment-grade, low thesis impact.

**M&A / corporate structure**
- **ADI** [9/9] ⚠️ acquiring **Alif Semiconductor** (edge-AI MCUs) for $1.35B cash + up to
  $200M contingent; close by end-2026.
- **FLEX** [9/15] ⚠️ spin-off of Cloud & Power Infrastructure named **Axiom Solutions
  International**, targeted Q1 CY2027; Revathi Advaithi to run Axiom, Michael Hartung to become
  Flex CEO, Amy Schwetz joins 10/5 as expected post-spin Flex CFO. The AI-DC exposure we rate
  FLEX for leaves with Axiom — the FLEX row will need a re-think at separation.
- **MOD** [9/10, 9/17] — Performance Technologies spin/Gentherm merger closes **10/1**
  (record 9/28); SpinCo cash to Modine cut **$210M → $159M** on a tax-preservation adjustment;
  RemainCo to be renamed Modexus Solutions (ticker stays MOD).
- **ONDS** [9/14] — closed Gate Technologies + Bron Technologies: $105M cash + 10.7M shares
  + up to $185M earn-out. **SEI** [9/8] — closed Omega Foundation Services (~$77M cash + 3.6M
  shares). **EXE** [9/16] — closed Twin Eagle. **ATKR** [9/15] — HSR waiting period expired on
  the Prysmian take-out (watchlist relevance ends at close).
- **NEE / D** [9/14] — enhanced Virginia concessions for the pending merger; notably both
  companies back SCC/legislative efforts to shield residential customers from
  **data-center service costs** — a regulatory thread for the Layer-1 thesis.

**Nothing found** on going-concern, auditor change, restatement (4.02), delisting (3.01) or
bankruptcy (1.03) — now confirmed across all 191 EDGAR-filing names, not just the sweep.

**No EDGAR coverage (foreign local lines, no CIK — 23):** SBGSY, TOELY, BESIY, 5347.TWO,
HHUSF, 0981.HK, 9880.HK, 6954.T, 6506.T, AUTO.OL, 6383.T, KGX.DE, 2590.HK, 2252.HK, 6324.T,
6268.T, 6481.T, 2049.TW, 6861.T, 2498.HK, BSL.DE, DRO.AX, MELE.BR — home-market disclosure
not swept this pass (standing gap, same as every prior EDGAR scan).

---

## 📊 Earnings refreshed

**Local completion pass — 8 names refreshed** (`refresh_objective_inputs.py`, dry-run first;
then `refresh_reverse_dcf.py` for the same names, `momentum_50dma.py` for all 214, and
`recalc_watchlist.py --sync`). "Before" = the 2026-09-08 score panel
(`tracking/score-history.csv`); "after" = live recalc. Because 50DMA % was refreshed for every
name in the same pass, "after" includes each name's momentum move, not just fundamentals.

| Ticker | Trigger | Before | After | Δ | Tier | Biggest input moves (yfinance TTM, 2026-09-18) |
|---|---|---|---|---|---|---|
| **ALAB** 📊 | Q2 print 8/4, EPS +15.9% vs est. | 75.28 (#12) | 75.26 (#12) | −0.02 | ✓✓ → ✓✓ | Fwd P/E 73→47, P/S 55→44, Rev YoY 93→105%, EPS YoY 152→199%; **FCF margin 34.2→23.0%** offsets |
| **RDDT** 📊 | Q2 print 7/30, EPS +31.6% | 73.78 (#15) | 75.39 (#11) | **+1.61** | ✓✓ → ✓✓ | Fwd P/E 20→16, EV/FCF 38→26, FCF yield 2.4→3.5%, P/S 14→10 |
| **VRT** | Q2 print 7/29 (miss) | 74.08 (#14) | 74.58 (#15) | +0.50 | ✓✓ → ✓✓ | Fwd P/E 33→27, EV/EBITDA 48→35, FCF margin 21→25%; Rev YoY 30→24%, **50DMA % 80→43** |
| **TER** | Q2 print 7/28 | 71.70 (#21) | 72.47 (#19) | +0.77 | ✓✓ → ✓✓ | EV/EBITDA 43→37, Rev YoY 87→104%; 50DMA % 88→61 |
| **PLTR** | Q2 print ~8/4 | 71.85 (#20) | 72.97 (#18) | +1.12 | ✓✓ → ✓✓ | Fwd P/E 64→76, P/S 62→69 (more expensive); Rev YoY 85→93%, 50DMA % 20→44 |
| **ORCL** ⚠️ | Q1 FY27 8-K 9/10 | 69.09 | 71.17 | **+2.08** | **✓ → ✓✓** | Rev YoY 20.6→29.6%, EPS YoY 26→63%; FCF margin −35→−40%, gross margin 65.8→64.0% |
| **ADBE** | Q3 FY26 8-K 9/10 | 61.41 | 62.89 | +1.48 | ✓ → ✓ | small moves; Fwd P/E 8.5→9.0 |
| **AVAV** 📊 | Q1 FY27 8-K 9/9, non-GAAP EPS +96.7% vs est. (Investing.com — secondary) | 59.25 | 55.73 | **−3.52** | ✓ → ✓ | **Rev YoY 133→5.7%** (BlueHalo acquisition lapped) |

Ranks are full-universe (incl. untradable 6861.T at #14).

**Flags (rule 3):**
- **ORCL crossed ✓ → ✓✓** (tier boundary — ⚠️ per Step 6d). Not held; tradable rank is outside
  the top 15, no pipeline event. Note the refresh is what *reveals* the tension in the row:
  Growth inputs jumped while FCF margin sank to −40% on $28.5B/quarter capex.
- **No name moved >5 points.** The two >15%-beat backlog names barely moved the needle: the
  ALAB result is a wash (cheaper multiple vs a 11-pt FCF-margin drop); RDDT +1.6.
  The feared MU-style tier miss did not materialise — but the inputs were 9 weeks stale and
  are now dated 2026-09-18.
- **TER EPS YoY withheld:** fresh value +378% trips the rule-15 ≥300% safety net — cell left
  as-is pending a ruling (needs the 10-Q to decide operational vs one-off; per
  `feedback_eps_yoy_verify_filings`, not inferred from yfinance). **Open judgment item for Dom.**
- **AVAV EPS YoY:** cell already blank under an earlier ruling; preserved. The agent read of
  the 8-K notes the GAAP swing (−$1.44 → −$0.10) is dominated by lower BlueHalo
  purchase-accounting amortization — consistent with keeping it blank; the
  `eps-yoy-overrides.json` entry should be re-ruled for the new quarter (STALE semantics).
- **ALAB FCF margin 34→23%:** large enough to deserve a look at the 10-Q cash-flow statement
  (working capital vs capex) at the next `/refresh-context ALAB`. Flagged, not explained.
- **ROIC (rule 34):** unchanged for 6 of the 8 — expected, since the whole column was
  recomputed on 2026-09-08. Rule-34 statement-lag STALE status was not re-checked per name.
- **TTM vs MRQ:** not computed per-name this pass. ALAB (+105% YoY) and PLTR (+93%) are the
  two where TTM most understates run-rate — note for their next context briefing.
- **Score-panel note:** `score-history.csv` is date-deduped, so the 2026-09-18 panel captured
  the first sync (after the 5 backlog names + 50DMA) and does **not** include the later
  ORCL/ADBE/AVAV refresh. The workbook is current; the panel picks those up at the next pass.

**Other tier crossings this pass — all from the 50DMA % refresh, no fundamentals change:**
CGNX 70.42 → 69.53 (✓✓ → ✓), CIEN 70.31 → 69.32 (✓✓ → ✓), PSIX 53.90 → 56.61 (? → ✓),
CARR 57.10 → 54.79 (✓ → ?), SSII 55.45 → 53.87 (✓ → ?), P 55.12 → 53.44 (✓ → ?),
PLUG 42.36 → 35.76 (? → ✗, −6.6 ⚠️ >5 pts). SHAZ +11.7 (23.75 → 35.42, stays ✗ — first
50DMA value now that it has ≥60 days of history). None is a holding.

<details>
<summary>Original cloud-pass text (superseded — backlog table as first surfaced)</summary>


**None refreshed this session** — `refresh_objective_inputs.py`/yfinance are blocked (see
execution note). What the scan did surface, though, is a **rule-9 backlog** that predates this
session and needs urgent attention once network access is restored:

| Ticker | Earnings date | Result | EPS surprise | Watchlist "Last Updated" | Gap |
|---|---|---|---|---|---|
| **ALAB** | 2026-08-04 | Rev $392.4M +104% YoY | **+15.9%** (adj. EPS $0.80 vs $0.69 est.) | 2026-07-16 | **>15% beat, never refreshed — 📊 immediate priority, ~6 weeks overdue** |
| **RDDT** | 2026-07-30 | Rev $805M vs $744.9M est. | **+31.6%** (EPS $1.25 vs $0.95 est.) | 2026-07-16 | **>15% beat, never refreshed — 📊 immediate priority, ~7 weeks overdue** |
| **TER** | 2026-07-28 | Rev $1,329M, EPS +300%+ YoY | not independently sized this pass | 2026-07-16 | Refresh overdue (not held; lower priority) |
| **VRT** | 2026-07-29 | Rev $3.27B, **miss** vs $3.38B est. | ~-3.3% (inside the 15% threshold) | 2026-07-16 | Refresh overdue — a portfolio holding; **not urgent-priority by magnitude, but 7+ weeks stale is a real gap** |
| **PLTR** | ~2026-08-04/05 | Rev $1.935B +93% YoY, US Comm +149% | not independently sized this pass | 2026-07-16 | Refresh overdue (not held; lower priority) |

**NTAP and CIEN and MDB were already refreshed** (2026-09-07/08, see git history) — not
duplicated here.

This table is a genuine backlog finding, not new-this-week — it accumulated across the
several consecutive network-blocked sessions since mid-2026-07 and simply hadn't been
surfaced in one place before. **Recommend a priority `/refresh-objective ALAB RDDT TER VRT
PLTR` pass the next time yfinance is reachable**, with ALAB and RDDT first given the >15%
surprise trigger.

No TTM-vs-MRQ divergence could be checked this session (needs yfinance).

</details>

---

## 💼 Portfolio pipeline

**Local completion pass — ran for real** (`momentum_50dma.py` → `recalc --sync --no-reweight`
→ `refresh_targets.py` → `track_performance.py`). `refresh_targets.py` FLAG output, verbatim:

```
[FLAG] NTAP: exit confirmed (rank 20 > exit rank 18, pending since 2026-09-08)
[FLAG] layer 06: 31% of portfolio (no layer cap active)
[FLAG] shadow BAND_TOP: roster refreshed (15 names)
[FLAG] shadow BAND_NEXT: roster refreshed (10 names)
[FLAG] shadow BAND_TAIL: roster refreshed (15 names)
[FLAG] shadow INVVOL_ROSTER: re-targeted (16 names)
wrote 16 target positions to 00-master/portfolio.xlsx
model rebalanced: membership: -NTAP — value at rebalance $10,123
ticket written: tracking/live/tickets/ticket-2026-09-18-membership.json (1 orders, 15 dust-suppressed, 0 untradeable, 0 skipped; funding scale 1.000)
```

- **EXIT — NTAP (confirmed).** The rule-26 clock started 2026-09-08; the rule-32-C seam
  window closed 2026-09-15; NTAP is still at tradable rank 20 (score 72.96 → 70.98 — its
  50DMA % also slipped), below exit rank 18, so the exit confirmed mechanically.
  `exit_pending` is now empty. **Model event logged: `membership: -NTAP`**, roster 17 → 16,
  equal-weight re-targeted across 16.
- **No ENTER.** Entry needs tradable rank ≤ 15; the 16 incumbents still hold those slots
  (AMZN is tradable #15; META at tradable #16 sits inside the 16–18 dead-band and is held by hysteresis).
  Next in line: PLTR (tradable #17), TER (#18).
- **No EXIT PENDING names** → nothing queued to confirm next week.
- **Ticket:** one order (the NTAP leg); the 15 re-weight legs are dust-suppressed. It was
  built from the **2026-09-14 recon snapshot** (4 days old) — if NTAP share count changed
  since, the ticket is off; C2 gates + live-quote sanity still apply at execution. **Claude
  placed no orders (rule 29).** The launchd executor will pick this ticket up at its next
  06:35 PT trading-day slot (Mon 2026-09-21) unless Dom intervenes; TTL = 2 trading days.
- **Concentration:** Layer 06 (silicon) at 31% — informational, no cap active.
- **Rule-25 gate:** `refresh_targets.py --check` → "Targets reflect current scores ✓" (re-run
  after the later ORCL/ADBE/AVAV refresh — still green).
- **Tier changes among holdings:** none (all 16 remain ✓✓; in equal-weight mode tier
  crossings don't re-weight anyway, rule 33).

**Weekly mark (2026-09-18 close, `track_performance.py`, appended to `performance-log.md`):**

| | Since inception (2026-05-26) | This week (09-11 → 09-18) |
|---|---|---|
| **Model** ($10,000 notional) | **$10,123 / +1.23%** | +0.76% |
| SMH | −4.84% (model alpha +6.07) | +0.79% |
| QQQ | −1.10% (alpha +2.33) | +0.92% |
| SPY | +1.74% | −0.34% |
| Equal-weight universe | +4.27% (alpha −3.05) | +0.31% |
| EW_ROSTER shadow | +5.98% | +0.92% |

A volatile week inside the flat headline: the model fell to $9,624 on 9/15 (−4.2% from 9/11)
and recovered +5.2% over the last three sessions. Supersedes the cloud pass's 9/17 mark
($9,923 / −0.77%).

<details>
<summary>Original cloud-pass text (superseded) — pre-run state</summary>

**Could not run `momentum_50dma.py` / `refresh_targets.py` this session** (yfinance blocked —
see execution note). Reporting from the last committed state (2026-09-08,
`tracking/performance-config.json`, `00-master/portfolio.xlsx` Targets, `score-history.csv`)
plus the mechanical implication of the elapsed time, not a fresh run:

- **NTAP — EXIT PENDING, rank 20 (exit rank 18), clock running since 2026-09-08.** That same
  date carries a **methodology seam** (rule 34, ROIC-computation switch), which per rule 32-C
  freezes any exit clock *started inside* the 7-day seam window from confirming. **The seam
  window closed 2026-09-15** — it has now been open (post-seam) for 3 trading days. Mechanically,
  **if NTAP is still below rank 18 when `refresh_targets.py` next runs, the exit should
  confirm** (a prior-date clock still below exit confirms once the seam clears) — this
  session could not execute that run. Context for whoever runs it: NTAP posted a strong Q1
  FY27 beat-and-raise (9/2: revenue +30% to $2.03B, EPS $2.58 vs $2.04 est. +26.5%, FY27
  guidance raised) that was **already** captured in the 9/7-08 refresh that produced the
  rank-20/EXIT-PENDING state — i.e., the pending exit is a *valuation* call (price ran up
  faster than the score), not a stale-fundamentals artifact.
- No other ENTER/EXIT/tier-change flags to report — no scoring pass has run since 2026-09-08
  (confirmed via `tracking/score-history.csv`, last date 2026-09-08), and this session's local,
  network-free `recalc_watchlist.recalc()` reproduces that same state (no sheet edits since).
- **Weekly mark** (from `tracking/performance-series.json`, CI-updated through 2026-09-17,
  read not re-verified): Model (scaled $10,000 notional, rule-33 equal-weight) closed
  **$9,923.33**, **-0.77%** since the 2026-05-26 inception. This week (09-10→09-17): **+0.83%**.
  Since-inception benchmarks: SMH **-6.90%**, QQQ **-1.72%**, SPY **+1.86%**, equal-weight
  watchlist universe (EW) **+3.57%**. So the model continues to beat SMH and QQQ but trails
  SPY and the broad equal-weight universe since inception — unchanged framing from prior
  scans. Shadow rosters (informational, hidden on-site by default): EW_ROSTER +3.69%,
  INVVOL_ROSTER -1.19%, BAND_TOP -2.99%, BAND_NEXT -2.12%, BAND_TAIL -4.88% since inception.
- No concentration/layer-cap warnings surfaced (no fresh recalc to check them against; the
  09-08 state had none).

</details>

---

## 🩸 Capitulation flags

`python3 scripts/capitulation_flag.py NTAP --log-forecast` (NTAP = the only exit-side name):

```
NTAP   clean: P/S 5.26 = 98.9th pctile of own 3y range; rev YoY 29.9% vs 3y median 4.8%
```

**No firing, no forecast logged.** NTAP is being sold near the *top* of its own 3-year P/S
range, not the bottom — the opposite of the CRM-2026-06 capitulation setup. The exit is a
valuation/rank call on a name whose multiple ran ahead of its score, with fundamentals
accelerating (rev +30% vs a 4.8% median). Worth noting the mirror: that profile is *not* the
rule-14 expectations flag either (that needs growth *below* median).

<details>
<summary>Original cloud-pass text (superseded) — blocked</summary>

Attempted `python3 scripts/capitulation_flag.py NTAP --log-forecast` (NTAP is the only
EXIT/EXIT-PENDING/seam-damped name this window) — **blocked**: the script needs SEC XBRL
revenue data (`expectations_flag.quarterly_revenue_sec` → `data.sec.gov`), which is
network-blocked this session. No forecast was logged. Flag for a rerun once EDGAR is
reachable — worth doing given NTAP's exit is a valuation call, exactly the setup the
capitulation check screens for (though here it would need to show the *opposite* — an
expensive, not cheap, valuation — for the exit to look justified rather than premature).

</details>

---

## 🔬 Rating integrity

`python3 scripts/audit_rating_integrity.py --summary` (fully local, ran cleanly):

```
rating-integrity (all layers): 211 rated names | 0 UNGATED (no thesis) | 0 stale (>90d)
```

Clean — no GATE violations, no stale names. No full audit needed.

---

## 🎯 Calibration

```
$ python3 scripts/resolve_forecasts.py --dry-run
0 resolved, 0 need review (dry run — nothing written)
$ python3 scripts/resolve_forecasts.py
0 resolved, 0 need review
```

Fully local, ran cleanly. Nothing due for resolution this window; `tracking/forecasts.jsonl`
unchanged.

---

## 🔴 Live pipeline

Partial (local attended pass):
- **Halt flag:** none raised (`tracking/live/` holds only the cleared 2026-09-08 flag).
- **Heartbeat:** `executor_cron.py --heartbeat-check` → **`STALE pipeline jobs (no successful
  run in >3d): series`**. ⚠️ The *local* launchd series job has not succeeded since ~9/15
  (local `main` stops at the 9/15 series commit); the GitHub Actions cron kept the site series
  current, so nothing user-visible broke — but the local runner needs a look. recon / execute
  / ticket_gen heartbeats are fresh.
- **Reconciliation not run** this pass (see completion note). Latest snapshot 2026-09-14:
  16 positions, 0 open orders, not halted, VRT unrepaired leg cleared. Those 9/14
  `live-status.json` / `live-vs-model.json` edits were already sitting uncommitted in the
  working tree before this session and are **left out of this commit** (not this session's work).

<details>
<summary>Original cloud-pass text (superseded) — skipped</summary>

Skipped per instructions — this is a headless/cloud run (rule 29, attended-sessions-only).

</details>

---

## Routine filings

<details>
<summary>Click to expand — analyst/insider/conference noise, no thesis relevance</summary>

- **FIX** — closed 9/15 at $1,576.78; 12-mo analyst target $2,197 (Strong Buy consensus).
- **SNDK** — presented at Citi Global TMT (9/8) and Goldman Communacopia (9/9); stock range
  $1,630-1,647 as of 9/18.
- **ANET** — Templeton (director) intent-to-sell 20k shares filed 9/8; joining S&P 100 9/21.
- **GMED** — Ann Rhoads (insider) intent-to-sell 10k shares filed ~9/15 (~$584k); a UBS
  Neutral/$82 PT initiation carried a 9/28 date in the source — **date looks internally
  inconsistent (future-dated relative to scan date), flagged UNVERIFIED, not treated as
  confirmed.**
- **VRT** — $0.0625/share quarterly dividend, record 9/14, payable 9/24.
- **META** — $0.525/share quarterly dividend, record 9/21, payable 9/28.
- **GOOGL** — $0.22/share quarterly dividend, record 9/7, payable 9/14.
- **EQT** — $0.165/share quarterly dividend paid 9/1; UBS PT $73→$77 (9/14); Stifel initiated
  Buy (9/4).
- **CGNX** — TipRanks reaffirmed Buy/$80 PT (9/15).
- **PLTR** — UBS raised PT to $250 from $220 (9/15).
- **EME** — presented at Morgan Stanley's 14th Annual Laguna Conference (9/17).
- **CIEN** — already fully processed by the earnings-sentinel pipeline (9/8 briefing +
  mechanical re-score, prior to this window's start); not reproduced here.


**EDGAR sweep (local pass) — routine 8-K/6-K, one line each:**
- **AAOI** 9/10, 9/15 — bought its Houston Bldg 3 for $26.8M; 10-yr Ningbo factory lease (~38k m²) — small capacity adds.
- **ADSK** 9/10 — $1.0B notes repay term loan (net-debt neutral). **DELL** 9/10, 9/15 — $5.0B notes, refinancing. **EXE** 9/17 — $500M notes closed.
- **AMZN** 9/9 — Mandia director election. **PWR** 9/15 — board to 11, Ellen Rubin (ex-AWS) elected.
- **ARM** 9/10, 9/18 — AGM results; UK annual report furnished. **NTAP** 9/11, **NNE** 9/17 — annual-meeting votes.
- **BW** 9/8 — preferred dividend. **MPWR** 9/10 — $2.00 dividend (interim CFO still signing). **TXN** 9/17 — dividend +7% to $1.52.
- **HIVE** 9/16, 9/17 — BUZZ HPC revenue hire; ProCogia GPU partnership (unquantified; 8-K/press-release date mismatch noted).
- **HSAI** 9/8, 9/17 — HKEX monthly return; 2026 interim report (PDF, not parsed).
- **MBLY** 9/10 ×2 — COO designated Section-16 officer; EVP Strategy moves part-time.
- **MOD** 9/10 — rename to Modexus Solutions post-spin. **SHAZ** 9/11 — co-founder moves from COO to partnerships role (fixed term to 3/2027).
- **ORCL** 9/14 — Ellison cancels 10b5-1 plan. **SNDK** 9/11, 9/16 — revolver refi; exec pay.
- **STX** 9/9 — redeemed remaining $150.7M exchangeable notes. **WDC** 9/14 — calling $109.5M converts.
- **TSEM** 9/15 — ECOC exhibit. **TSM** 9/10 — monthly revenue. **ASX** 9/9 — monthly revenue.
- **VRT / PLTR / DDOG** — insider forms only (Form 4 / 144), no 8-K.

</details>

## New 13F activity

**None in window** (primary EDGAR submissions JSON, local pass). Expected — Q2 13Fs landed
mid-August; Q3 filings are due ~2026-11-16. Most recent 13F-HR per fund: Berkshire 8/14,
Baillie Gifford 8/6, Tiger Global 8/14, Coatue 8/14, Whale Rock 8/14, Lone Pine 8/14.

⚠️ **Two tracked-fund CIKs in `weekly_scan_runner.py` were wrong — fixed this pass:**

| Fund | CIK in script | What that CIK really is | Correct CIK (verified, EDGAR `name` field) |
|---|---|---|---|
| Baillie Gifford | 0001048268 | **IES Holdings, Inc.** | **0001088875** — BAILLIE GIFFORD & CO |
| Coatue | 0001336528 | **Pershing Square Capital Mgmt** | **0001135730** — COATUE MANAGEMENT LLC |
| Whale Rock | 0001387322 | — | confirmed correct on primary (closes the 2026-09-04 open item) |

IES Holdings itself files 13F-HRs, so the wrong CIK returned plausible-looking hits and would
never have errored. **Any past scan that reported "Baillie Gifford" or "Coatue" 13F activity
from this script's CIK list should be treated as suspect.** A repo-wide grep found the bad
CIKs only in this runner (plus a stale worktree copy) — `/thirteenf-delta` sourcing is not affected.

<details>
<summary>Original cloud-pass text (superseded)</summary>

**Could not check** — `data.sec.gov` blocked in the cloud session.

</details>
