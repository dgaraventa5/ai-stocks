# Weekly News Scan — 2026-06-12

**Scope:** 135 watchlist tickers. Scan date: 2026-06-12 (covering June 5–12).

**Note on execution:** The morning remote run was blocked on network egress (SEC EDGAR +
yfinance unreachable) — see git history for the partial version. This file is the **completed
scan**, re-run locally the same day with full network access. All steps completed.

**Unresolved tickers (no SEC CIK):** SBGSY, TOELY, BESIY — foreign ADRs that do not file with
EDGAR (Schneider, Tokyo Electron, BESI report via home-market disclosures; not covered by the
8-K scan, known limitation). PSTG resolved — see ⚠️ Everpure rename below.

---

## Step 0 — Mental Models: ✓✓ Positions (pre-scan articulation)

No ✓✓✓ names exist in the current watchlist (highest score: NVDA 83.3).
Mental models below are for the 16 portfolio holdings (all ✓✓).

| Ticker | Score | Mental model |
|--------|-------|--------------|
| NVDA | 83.3 | Dominant AI GPU supplier, ~80-90% merchant accelerator market share. Q1 FY2027: $81.6B revenue (+85% YoY), Q2 guided $91B. Networking revenue $14.8B (+199% YoY) is the key upstream signal. Risk: CUDA moat erosion, China = $0 DC revenue. No ✓✓✓ because P/S and EV/EBITDA remain high at this revenue level. |
| TSM | 79.8 | World's leading contract fab. N3/N2 in high demand, CoWoS packaging still a bottleneck. Secular beneficiary of every node that NVDA, AMD, AVGO, ALAB ship. Key existential risk: Taiwan geopolitics — can't price it out, just acknowledge it. |
| SNDK | 79.7 | Spun from WD (2024), focused on NAND flash. AI infrastructure storage demand + recovering memory cycle. Thesis is demand-driven pricing recovery, not a specific AI moat. |
| MU | 79.5 | HBM3E supplier for NVDA Blackwell. HBM sold out through 2025-2026. Massive margin recovery underway after the 2023-24 memory trough — MRQ margins likely far above TTM averages (TTM limitation flag). Risk: HBM market eventually expands (Samsung/SK Hynix), cyclicality always returns. |
| META | 79.0 | Social media / ad platform deploying massive AI infra (Llama models, AI-ranked feed/ads). Just restructured into Superintelligence Labs (2026-05-20). High capex but AI is already monetizing through ad-ranking improvement. Less supply-chain pure-play, more AI-beneficiary. |
| CRDO | 78.3 | Credo Technology, connectivity ASICs (SerDes IP, AEC cables) linking GPUs within AI clusters. Revenue ramp directly tied to hyperscaler GPU deployments. Customer concentration is the main risk — ~90% of revenue from a handful of hyperscalers. |
| GOOGL | 77.7 | Hyperscaler with TPU custom silicon, Gemini 3.5 models, dominant AI-enhanced search+ads. At Google I/O, launched Gemini 3.5, $5B TPU JV with Blackstone, capex guided to "significantly increase" vs 2026's $190B. Key risk: OpenAI/Anthropic disrupting search, though moat is wider than consensus thinks. |
| ANET | 77.5 | Arista, dominant DC networking. AI clusters demand 400G/800G Ethernet switches. AI fabric target raised to $3.5B (full-year 2026). Risk vector: NVIDIA Spectrum-X gaining share at both META and MSFT; supply chain shortages (wafers, CPUs, optics) flagged to persist 1-2 more years. |
| EME | 76.7 | EMCOR, electrical/mechanical contractor riding the data center construction wave. High-visibility backlog, limited AI-specific moat but reliable execution and backlog growth. **Gate violation** — no thesis.md populated. |
| ALAB | 76.5 | Astera Labs, Layer 7 connectivity ASICs. Scorpio switch (PCIe 5.0 fabric) in volume shipments. NVLink Fusion (NVIDIA + hyperscaler custom switch) and UALink switch (Amazon/AMD) design wins in 2027. Customer A (likely Amazon) = 29% of revenue Q1 2026. Key new-money entry since June 2026 rebalance. |
| FIX | 76.4 | Comfort Systems USA, HVAC/mechanical contractor. Q1: revenue +56.5% to $2.87B, record backlog $12.45B, dividend raised 14%. DC construction pure-play with no AI-specific moat. **Gate violation** — no thesis.md. |
| MSFT | 76.2 | Azure AI growing strongly, Copilot+ across Office suite. Massive capex ($75B+ annually). OpenAI partnership creates both lock-in advantage and dependency risk. **Gate violation** — no thesis.md. Scores lower on value (high multiples) but strong quality + AI thesis. |
| PLTR | 74.8 | AI-native software for government + commercial. Q1 2026: revenue $1.633B (+85% YoY, beat by 5.8%), NRR 150%, US commercial +133% YoY, adj FCF margin 57%. AIP is their production-grade AI platform. Key Layer 10 risk: NRR compression is the canary — watch for any sign NRR drops from 150%. Expensive (~97x fwd P/E). |
| AVGO | 74.6 | Broadcom, largest custom ASIC designer (Google TPUs, Meta training chips), plus Ethernet networking (Tomahawk, Jericho). CEO projected custom AI chips > $100B annual revenue by end of 2027. VMware integration ongoing but AI revenue is the re-rating driver. |
| EQT | 73.8 | Largest US nat gas producer. Thesis: AI data centers → electricity demand → gas demand. Score barely above exit threshold (73.0). No AI moat — pure macro beneficiary of demand growth. Held on hysteresis; next adverse score move would trigger EXIT PENDING. |
| TER | 73.0 | Teradyne, semiconductor test equipment. AI chips (HBM, complex logic) require significantly more test time per die. Structurally higher ATE demand. **Score exactly at exit threshold (73.0) — hairline above EXIT PENDING.** Any score deterioration on next refresh triggers the 2-run exit process. **Gate violation** — no thesis.md. |

**Thesis diff vs. articulated model (post-scan):** Two genuine model updates this week.
(1) **AVGO** — the mental model said "VMware integration ongoing but AI revenue is the re-rating
driver"; the Q2 FY26 refresh shows the re-rating is *already in the numbers* (TTM GM +846bps,
EPS +87.5% YoY) and the model had not priced how fast margins are ramping. (2) **GOOGL** — the
model framed Alphabet as a self-funding hyperscaler; the $16.75B mandatory convertible preferred
raise breaks that frame — even Alphabet now taps external capital for AI capex. ANET/Spectrum-X
remains open — no new data this week.

---

## ⚠️ Material Events

| Ticker | Event |
|--------|-------|
| **GOOGL** 💼 | 8-K 6/05 (1.01): Sold **$19.25B of 6.25% mandatory convertible preferred** ($16.75B base + overallotments) — part of an **$84.75B June equity package**: $18B common, $19.25B preferred, $40B ATM, **$10B private placement to Berkshire Hathaway** (8-Ks 6/04-05; corrected from initial ~$16.75B read during 6/12 /refresh-context). Alphabet's first large external AI-capex financing; buybacks halted (zero in Q1 vs $15.1B yr-ago). |
| **ETN** | 8-K 6/11 (7.01/8.01): **Separating vehicle Mobility segment** to Dana Inc. via Reverse Morris Trust — Eaton gets ~$1.1B cash, shareholders ≥50.1% of SpinCo+Dana. Post-close Eaton is a cleaner electrical/data-center pure-play. Positive for Layer 2 thesis directness. |
| **MRVL** | 8-K 6/11 (5.02): **CFO Willem Meintjes resigned** eff. 6/15; replaced by board member Daniel Durn (ex-Adobe, ex-AMAT CFO). High-caliber replacement, orderly handoff — watch for any restatement/timing signals anyway. |
| **P** (fka PSTG) | **Pure Storage renamed Everpure, Inc., ticker PSTG → P.** Watchlist, research map, and per-stock dir updated. Q1 FY27 reported 5/27 (scan gap); Rule-9 refresh done — FCF margin 16.8%→6.8%, score now 59.5 (✓). Also DEFA14A 6/02: founder Scott Dietzen off Nom/Gov committee under shareholder pressure. |
| **HUT** | 8-K 6/10 (1.01): Closed **$4.25B 6.129% senior secured notes due 2042** funding a 352MW six-hall turnkey DC (Nueces County, TX) leased to a tenant rated **AA- or higher** — strongest confirmation yet of the miner→IG-tenant-DC conversion thesis. |
| **APLD** | 8-Ks 6/09: **Delta Forge 2 long-term lease signed** (second AI Factory campus, new southern state); priced $1.59B 7.00% notes for 150MW ELN-04 at Polaris Forge 1; $350M revolver; MOU to assign ELN-04 lease to a **CoreWeave** subsidiary if it reaches IG rating. |
| **CIEN** | 8-K 6/08+6/11 (1.01/2.03/3.02): Priced **$2.0B convertible notes due 2031** + hedge/warrants (~7.7M shares max). Big raise for Ciena's size — check use of proceeds in next 10-Q. |
| **KEEL** | 8-K 6/10 (1.01): **$458M 1.25% converts due 2032** (upsized from $350M) to accelerate DC development (Panther Creek, Sharon, Moses Lake). |
| **CRWV** | 8-K 6/11 (7.01): Launching **$3.5B USD+EUR senior notes due 2032** — partly refinancing; leverage stack keeps compounding. |
| **NVTS** | 8-K 6/09 (5.02): Director **Ranbir Singh resigned**; company pointedly references his April/May Schedule 13Ds — activist/governance fight in progress. |
| **VRT** | 8-K 6/12 (7.01): **Closed ThermoKey S.p.A. acquisition** (Italian heat exchangers) — thermal bolt-on, consistent with cooling-attach thesis. VRT at 73.7, still below entry (74.5). |
| **MSFT** | 8-K 6/05 (5.02): **Reid Hoffman not standing for re-election** (director since 2017). No disagreement cited; board-composition note, not thesis-moving. |
| **TSM** | 6-K 6/10: **May revenue NT$416.98B, +30.1% YoY** (+1.5% MoM); Jan–May +30.0% YoY — momentum intact, thesis-confirming. |
| **CIFR** | 8-K 6/08-09: Stingray Compute priced **$810M 6.00% senior secured notes due 2031** — HPC project financing. |
| **HUBB** | 8-K 6/08-09: $1.9B 3-tranche senior notes; **closed NSI Industries acquisition** (electrical fittings). |
| **AMZN** | FWP/424B5 6/08: **C$14.0B five-tranche maple bond** (3.40% '29 → 5.00% '56) + new term loan — hyperscaler debt-funding theme continues. |
| **SMCI** | 8-K 6/09 (8.01) + S-3ASR + 424B5 ×5 (6/09–6/12): risk-factor refresh ahead of a **large multi-instrument capital raise** — sizes TBD; pull prospectus supplements next scan. |

**Theme of the week: the AI buildout has moved decisively to debt + hybrid financing.**
GOOGL preferred ($16.75B) + AMZN maple bonds (C$14B) + HUT ($4.25B) + CRWV ($3.5B) + CIEN
($2.0B) + APLD ($1.59B+) + CIFR ($810M) + KEEL ($458M) ≈ **$40B+ of AI-infrastructure
financing in one week**, across every layer from hyperscaler to neocloud to miner-conversion.
Watch list implication: balance-sheet (BS Risk) ratings for Layer 3/9 names deserve scrutiny at
the next rescore — leverage is rising fastest exactly where scores are improving.

---

## 📊 Earnings Refreshed (Rule #9)

| Ticker | Reported | Score before → after | Notes |
|--------|----------|---------------------|-------|
| **AVGO** 📊 | Q2 FY26, 8-K 6/04 (scan gap — caught via 10-Q 6/09) | **74.6 → 78.2 (+3.6)** | **📊 GM +846bps TTM (67.8→76.3), Rev YoY 29.5→47.9, EPS YoY 31.6→87.5.** TTM still lags the current run-rate (MRQ above TTM on every growth metric) — classic rule-9 fast-ramp case. **Recommend full `/earnings-update AVGO`.** Tier unchanged ✓✓; rises #14 → #7 in portfolio rank. |
| **ORCL** | Q4 FY26, 8-K 6/10 (Item 2.02) | 62.8 → 63.4 | Rev $19.2B +21%, non-GAAP EPS $2.11 +24% (press release Ex 99.1); **RPO $638B, +$85B QoQ, +363% YoY**; IaaS +93%. FY26 FCF **−$23.7B** (capex) — FCF-driven Value metrics stay pinned at minimum; $75B of contracts are customer-prepaid/supplied hardware. Beat magnitude <15% → no immediate-priority flag. Tier ✓. |
| **UEC** | FQ3 2026 (Apr 30), 8-K 6/09 (Item 2.02) | 41.7 → 41.7 | Inputs refreshed; rev YoY + EPS YoY missing on yfinance (flagged, kept stale values). Pre-profitability uranium developer — bands unchanged. Tier ?. |
| **P** (fka PSTG) | Q1 FY27, 8-K 5/27 (scan gap) | n/a → 59.5 | Refresh overdue under Rule 9 (earnings 16 days ago). FCF margin 16.8→6.8, FCF yield 2.75→1.11 — meaningful FCF deterioration; rev/EPS YoY missing on yfinance (flagged). Tier ✓. |

**Scan-gap note:** No weekly scan ran 2026-05-31 → 2026-06-07 (between the 05-26 and 06-12
scans), so 8-Ks from that week (AVGO 6/04 earnings, P 5/27 earnings, MRVL late-May earnings)
were only caught this pass. MRVL is not refresh-priority (not held, score mid-table) but its
inputs are also post-earnings stale — fold into next quarterly rescore at latest.

Still pending from 2026-05-26 scan: **KEYS** re-pull (April quarter now likely populated),
**NVDA** + **MOD** full `/earnings-update`.

---

## 💼 Portfolio Pipeline

Full pipeline ran post-refresh: `momentum_50dma.py` (135/135 written) → `refresh_targets.py` →
`track_performance.py`.

- **Membership unchanged — 16 positions, all HOLD. No ENTER/EXIT/EXIT-PENDING events.**
- **TER survived at exactly 73.0** — the exit trigger requires score < 73.0; the refreshed
  50DMA inputs did not move it. Still the #1 watch item: any deterioration starts the 2-run
  exit confirm.
- **EQT 73.8** — held on hysteresis, 0.8 above exit.
- **AVGO 78.2** — biggest mover (+3.6), now 7th largest target weight.
- Next-in-line below entry (74.5): **VRT 73.7, AMD 73.5** — neither entered.
- [FLAG] **Layer 06 (silicon) = 35% of portfolio** (NVDA, SNDK, MU, AVGO, ALAB). No layer cap
  is configured for L06 — flagging per pipeline output; a cap decision is Dom's call
  (framework-level, per feedback memory).

**Performance mark (2026-06-12):** Model **$14,285, +3.52%** since 2026-05-26 inception.

| Benchmark | Since inception | Model alpha |
|---|---|---|
| SMH | +3.40% | **+0.11%** |
| QQQ | −0.96% | **+4.47%** |
| EW universe (35) | +3.22% | **+0.30%** |

Since the 2026-06-10 rebalance the model is +6.71% vs SMH +9.06% (−2.34% — SMH's NVDA/AVGO
mega-weights outran our caps this week) and QQQ +4.27% (+2.45%). Top contributors since
rebalance: SNDK +$203, ALAB +$120, MU +$117; bottom: MSFT −$16, EQT −$5.

---

## 🔬 Rating Integrity (Rule #12)

`audit_rating_integrity.py`: **135 rated names | 71 gate violations | 0 stale.** Unchanged
from the morning run (the P rename did not affect gate status).

**Portfolio holdings with gate violations (7/16 — highest priority):**
FIX, EME (since 05-18) · TER, TSM (since 06-10) · MSFT, GOOGL (since 05-18) · META (since 05-26).

Per Rule 12 these names' AI/Momentum/Risk subscores are unbacked until research-backed
briefings exist. Suggested `/refresh-context` order (score-weighted): TSM → META → MSFT →
GOOGL → EME → FIX → TER. The biweekly scheduled routine owns the rotation; surfacing here per
Step 8. **Note:** GOOGL and MSFT both had material 8-Ks this week (preferred raise; Hoffman
departure) — natural moment to do their briefings while the filings are fresh.

---

## Routine Filings

- AAOI — S-8/S-8 POS ×10 (equity plan registration post-2026-plan approval) + annual-meeting 5.02/5.07
- AAON — 8-K 7.01: William Blair conference presentation
- AEIS — 8-K 8.01: redeeming remaining $136.7M 2.50% converts due 2028 (Sep 23); S-3ASR shelf
- ALAB — 8-K 5.07: annual meeting results
- AMBA — DEFA14A proxy supplement
- ASML, MRVL — SD (conflict minerals)
- AVGO — 8-K 8.01: debt tender offers; S-4 ×2 (exchange offers, not M&A); 10-Q Q2 FY26
- BTDR — 6-K; CIFR/CRWV/OKLO/PLTR/WULF/TT — 8-K 5.07 annual-meeting results
- D — $825M 5.35% senior notes '36; 425s (NEE merger comms, expected cadence); FWP/424B
- DELL — $6.0B revolver refi (replaces 2021 facility); 10-Q; 13D/A
- GOOGL — 8-A12B + CERT (NYSE listing of the new depositary shares); DEFA14A; PAO appointment
- INTC, PPL, RRC — 11-K (benefit plans)
- MU — 8-K 5.02: Alexis Black Björlin appointed independent director (Gov & Sustainability cmte)
- NVTS — S-3ASR shelf; DEFA14A
- PLAB, UEC — 10-Q
- PLUG — 8-K 7.01: annual-meeting presentation
- SO — ATM equity distribution agreement + S-3ASR; STX — 8-K: '28 exchangeable notes redemption
- TT — 8-K 5.02: Donald Simmons promoted to EVP & COO eff. 7/01 (internal promotion)
- TSEM, RMBS, BTDR — Schedule 13G; MRVL — 13G/A
- UMC — 6-K (routine monthly disclosure)
- XEL — 8-K 8.01: PSCo CO gas rate case — staff/UCA testimony proposes cutting the $190M ask
  to −$15M/+$86M; hearings July 23–31. Watch for Layer 1 read-through on utility capex recovery.
- UEC — DEF 14A/DEFA14A/ARS (proxy season)

## New 13F Activity

None. All 6 tracked funds (Berkshire, Baillie Gifford, Tiger, Coatue, Whale Rock, Lone Pine)
checked — no 13F-HR/A filings June 5–12 (between filing seasons; next cluster ~Aug 14).

---

## Follow-up Items

**New this week:**
1. ~~**AVGO** — full `/earnings-update`~~ ✅ DONE 2026-06-12 (transcript + delta + briefing; score 78.5 post rating session)
2. ~~**SMCI** — pull 424B5s for raise sizes~~ ✅ DONE 2026-06-12: **$6.3B+ multi-instrument raise** — $3.75B (up to $4.3B) 7.00% mandatory convertible preferred + $1.33B common + $1.25B ATM. Week's AI-financing total → ~$46B+.
3. ~~**GOOGL/MSFT** — `/refresh-context`~~ ✅ DONE 2026-06-12 (all 7 portfolio gate violations cleared; rating session completed, 20 changes + 3 overrides)
4. **Layer 3/9 BS Risk** — revisit at next rescore given the financing wave (portfolio L9 names re-rated 2026-06-12; non-portfolio HUT/APLD/CIFR/CRWV/KEEL still pending)
5. **ETN** — track Dana RMT regulatory/close timeline; post-separation Eaton is more thesis-direct
6. ~~**MRVL** — objective inputs stale~~ ✅ REFRESHED 2026-06-12: now 65.0 (✓). ⚠️ Tier unreliable — GAAP EPS YoY −80.6% is a one-time-charge artifact (Apr-26 qtr NI $34.5M on record revenue); without it MRVL ≈ ✓✓ boundary. Identify the charge in the 10-Q at next pass.

**Carried from 2026-05-26 scan:**
7. ~~**ONTO** — use-of-proceeds window~~ ✅ CLOSED 2026-06-12: disclosure was in the 5/21 8-K itself ($205M concurrent buyback @ $254.53 + capped calls; remainder GCP). Passive watch for deployment of remaining ~$1.2B.
8. **WULF** — Muskie anchor tenant: still none disclosed (verified 2026-06-12; KBW expects first 500MW lease as early as 1H 2027). Passive watch.
9. **D/NEE** — deal now signed: NextEra acquiring Dominion ~$67B (2026-05-15), close guided 12-18mo; FERC application not yet filed (verified 2026-06-12). Passive watch for the FERC docket.
10. ~~**KEYS** — re-pull yfinance~~ ✅ DONE 2026-06-12 (April quarter populated; 70.9 ✓✓)
11. **NVDA / MOD** — full `/earnings-update` still recommended (the two remaining actionable items)

**Rating integrity backlog:**
12. ~~Portfolio gate violations~~ ✅ CLEARED 2026-06-12 (71 → 64; all remaining are non-portfolio, biweekly rotation)
13. **R2 review flags** (new rubric, 2026-06-12): CAMT asset-leg, KLIC China mix, AVGO two-leg — research-first at next refresh/rescore (see rubric-calibration-notes.md)
