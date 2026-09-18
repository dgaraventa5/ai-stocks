# Weekly News Scan — 2026-09-18

**Scope:** 214 watchlist tickers. Scan window: **2026-09-05 – 2026-09-18** (14 days —
covers a gap week; no scan was filed for the week of 2026-09-11). Last committed scan:
2026-09-04 (`tracking/weekly-news-scan-2026-09-04.md`, commit `db5bb34`).

## Execution note (network egress blocked this session — read before the rest)

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

---

## 📊 Earnings refreshed

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

---

## 💼 Portfolio pipeline

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

---

## 🩸 Capitulation flags

Attempted `python3 scripts/capitulation_flag.py NTAP --log-forecast` (NTAP is the only
EXIT/EXIT-PENDING/seam-damped name this window) — **blocked**: the script needs SEC XBRL
revenue data (`expectations_flag.quarterly_revenue_sec` → `data.sec.gov`), which is
network-blocked this session. No forecast was logged. Flag for a rerun once EDGAR is
reachable — worth doing given NTAP's exit is a valuation call, exactly the setup the
capitulation check screens for (though here it would need to show the *opposite* — an
expensive, not cheap, valuation — for the exit to look justified rather than premature).

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

Skipped per instructions — this is a headless/cloud run (rule 29, attended-sessions-only).

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

</details>

## New 13F activity

**Could not check.** The tracked-fund 13F-HR sweep (Berkshire, Baillie Gifford, Tiger Global,
Coatue, Whale Rock, Lone Pine) requires `data.sec.gov`, which is blocked this session (see
execution note). No data either way — flagged as a gap, not reported as "none found."
