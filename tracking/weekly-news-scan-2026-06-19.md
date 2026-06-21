# Weekly News Scan — 2026-06-19

**Scope:** 163 watchlist tickers. Scan date: 2026-06-19 (covering June 12–19).

**Note on execution:** SEC EDGAR (data.sec.gov + www.sec.gov) and Yahoo Finance (yfinance) are 403-blocked from this cloud environment — same egress-restriction issue as the 2026-06-12 morning scan. 8-K scan was completed via WebSearch against SEC full-text search and StockTitan; scores via `recalc_watchlist.py` (local, no network needed); performance series from `tracking/performance-series.json` (written by the daily-refresh CI). **Rule 9 refreshes for CRDO, HPE, and PANW are blocked — flagged below for follow-up.** 50DMA refresh and `refresh_targets.py`/`track_performance.py` also blocked (require yfinance).

**Post-scan note:** A major mid-week portfolio and methodology change occurred (June 16–17) that this scan is the first to document: R5 Disruption Risk dimension added (Rule 16), 12 QQQ-coverage names scored, and the portfolio tightened to a 14-name 76-bar book. The portfolio pipeline section covers this.

**Unresolved tickers (no SEC CIK):** SBGSY, TOELY, BESIY — foreign ADRs (known limitation). SPCX (SpaceX) — private, no EDGAR filings.

---

## Step 0 — Mental Models: ✓✓ Portfolio Holdings (pre-scan articulation)

No ✓✓✓ names (highest score: TSM 84.7, NVDA 84.1 — both below 85 threshold). Portfolio tightened June 17 to 14 names at 76-bar. Mental models below are for those 14 holdings as of scan start.

| Ticker | Score | Mental model |
|--------|-------|--------------|
| TSM | 84.7 | World's leading contract fab. N3/N2/CoWoS in high demand. Secular beneficiary of every AI chip NVDA/AMD/AVGO/ALAB ships. May revenue +30.1% YoY (June 10 6-K). Key existential risk: Taiwan geopolitics. |
| NVDA | 84.1 | Dominant AI GPU, ~80-90% merchant accelerator share. Q1 FY27 $81.6B (+85%), Q2 guided $91B. Networking $14.8B (+199%). CUDA moat. China = $0 DC revenue. Nearly debt-free as of the scan. |
| SNDK | 80.1 | Sandisk (spun from WD 2024). NAND flash, recovering memory cycle + AI storage demand. Not a specific AI moat play — demand-driven pricing recovery. |
| MU | 80.0 | HBM3E for Blackwell. HBM sold out through 2026. Massive margin recovery. Q3 FY26 earnings scheduled June 24 — guided $33.5B revenue (+140% from prior year trend), 81% gross margin. TTM scores significantly understated relative to current run rate. |
| META | 79.4 | Social/ads platform + massive AI infra (Llama, Superintelligence Labs). AI already monetizing through ad ranking. High capex but clear ROI. Less supply-chain pure-play, more AI beneficiary. |
| AVGO | 79.2 | Largest custom ASIC designer (Google TPUs, Meta training ASICs). Ethernet networking. CEO projected custom AI chips >$100B annual by end 2027. Q2 FY26 re-rated margins: TTM GM 76.3% (was 67.8%). |
| CRDO | 78.9 | Credo Technology, SerDes + AEC connectivity for AI clusters. FY26 $1.3B revenue (3× YoY). Q4 FY26 revenue $437M (+157% YoY). DustPhotonics acquired May 28 (Silicon Photonics PICs for 400G/800G/1.6T). Customer concentration remains the key risk. |
| APP | 78.9 | AppLovin, AI-driven mobile ad platform. AXS engine is generating substantial margin expansion. AI-native ad targeting model with growing network effects. Newer to the watchlist. |
| ANET | 78.5 | Arista, dominant DC networking. AI fabric revenue target $3.5B. MSFT + META are 42% of revenue (26% + 16%). Spectrum-X competitive watch ongoing. |
| WDC | 78.0 | Western Digital (HDD + flash). AI datacenters need massive storage. Recovering cycle + AI demand. Separate from SNDK (different product/market focus). |
| MSFT | 77.2 | Azure AI, Copilot+ across Office, OpenAI lock-in. $75B+ capex annually. Wiz acquisition completed March 2026 ($32B). |
| ALAB | 77.1 | Astera Labs connectivity ASICs. Scorpio PCIe 5.0 fabric in volume. NVLink Fusion + UALink (2027 design wins). Customer A (likely Amazon) = 29% Q1 2026 revenue. |
| GOOGL | 76.8 | Hyperscaler. Gemini 3.5, TPU/Blackstone JV, capex $180–190B 2026. Completed $84.75B June equity/debt package (in prior scan). $19.25B mandatory convertible preferred + $16.75B base. |
| FIX | 76.7 | Comfort Systems USA, HVAC/mechanical. Q1 revenue +56.5% to $2.87B, record backlog $12.45B. DC construction pure-play. |

**Thesis diff vs. articulated model (post-scan):** Two updates this week:
(1) **NVDA** — model said "nearly debt-free"; the $25B bond deal (June 15–18) changes that. At $50B+/quarter OCF it's easily serviceable (ND/EBITDA ~0.25x even post-raise) but it signals NVDA sees a decade of capital-intensive AI ahead, or is positioning for a strategic move. No acquisition announced. Watch use of proceeds disclosures.
(2) **CRDO** — DustPhotonics close (May 28) was not in the mental model and is a material strategic shift toward vertical integration of the optical stack. Thesis implication: CRDO is no longer just a SerDes/AEC play — it's building a full optical+electrical connectivity stack for AI DC. Updates the competitive moat and capex profile.

---

## ⚠️ Material Events

### New This Week (June 12–19)

| Ticker | Event |
|--------|-------|
| **NVDA** 💼 | 8-K 6/18 (8.01): Completed **$25.0B seven-tranche senior notes** (4.250% '28 through 5.625% '56, tranches from $3B to $4B), priced June 15, closed June 18. First NVDA bond deal since 2021 and its **largest-ever debt transaction**, upsized from initial ~$20B target on $85B+ in orders. Use of proceeds: general corporate purposes including debt repay/refinancing. NVDA held $50.3B cash and generated $50.3B operating cash flow in the most recent quarter — this is not a distress raise. Continuity of the AI-financing-wave theme (adds NVDA to the borrowing cohort alongside GOOGL, AMZN, CRWV, HUT, KEEL from the June 12 scan). ND/EBITDA impact: minimal at current EBITDA run rate; BS Risk score unchanged. Strategic signal: NVDA locking in decade-scale debt at fixed rates implies management sees sustained capex need. |
| **OKLO** ⚛️ | 8-K 6/18 (1.01): Signed **LOI with Centrus Energy (LEU)** for HALEU fuel supply to power up to 5 Aurora powerhouses at Oklo's planned 1.2 GW clean energy campus in southern Ohio; Centrus deliveries from Piketon, OH starting 2029. Also signed **MOU with Kiewit Nuclear Solutions** for EPC planning for the initial Ohio Aurora deployments. First concrete fuel supply LOI for Oklo — advances the Aurora deployment thesis from regulatory-approval story to operational planning stage. |
| **LEU** ⚛️ | 8-K 6/18 (1.01): Centrus counterpart to the OKLO LOI above — HALEU supply + prepayment terms to be negotiated in definitive agreement. Backed by $900M DOE HALEU task order to Centrus. Centrus stock rose on announcement. Both OKLO and LEU are on the watchlist. |
| **SMCI** | Depositary shares offering (**75M shares × 7.00% Series A Mandatory Convertible Preferred**, representing 1/20 of a preferred share) **closed June 15** — this confirms the $7B multi-instrument raise from the June 12 scan. Per follow-up item #2 from that scan: $3.75B preferred + $1.33B common + $1.25B ATM = $6.3B+; the June 15 close confirms the preferred tranche settlement. SMCI stock +10.4% on June 18 (per search results). |

### Scan Gaps (June 1–12, not in prior scan)

| Ticker | Event |
|--------|-------|
| **CRDO** ⚠️💼 | (1) 8-K 5/28 (2.01): **DustPhotonics acquisition closed** at $750M cash + ~0.92M ordinary shares (~3.21M contingent shares on milestones); Silicon Photonics PIC technology for 400G/800G/1.6T (roadmap 3.2T) — vertically integrates optical design into CRDO's connectivity stack. Non-GAAP EPS accretive FY27. (2) 8-K 6/01 (2.02): **Q4 FY26 earnings**: revenue $437M +157% YoY; FY26 full year $1.3B (3×); non-GAAP NI $662M (5×). CEO William Brennan granted 100% performance-based PSU (6 tranches, revenue targets $2.5B→$7.5B, stock hurdles $244.70→$489.40 through June 30). Portfolio holding — **Rule 9 refresh needed** (Q4 rev beat likely >15%). Blocked by network. |
| **HPE** 📊 | 8-K 6/01 (2.02): **Q2 FY26 earnings** — revenue $10.7B +40% YoY, non-GAAP EPS $0.79 vs $0.54 est (**+46% beat → ⚠️ Rule 9 priority**). AI Systems Orders $1.8B. Raised full-year guidance: 29–33% revenue growth, ≥$3.5B FCF. **Rule 9 refresh needed (📊 priority — EPS beat >15%).** Not a portfolio holding. Blocked by network. |
| **PANW** | 8-K 6/02 (2.02): **Q3 FY26 earnings** — revenue $3.00B +31% YoY, Next-Gen Security ARR $8.1B +60%. Non-GAAP EPS $0.85; GAAP net loss -$177M (charges from CyberArk/Chronosphere integration, $388M revenue contribution). Raised FY26 NGS ARR to $8.90–$8.95B (59–60% growth). **Rule 9 refresh needed.** Not a portfolio holding. Blocked by network. |
| **CRDO** (thesis note) | DustPhotonics close means CRDO is now a vertically integrated optical+electrical connectivity company — SerDes IP (the core), AEC active cables, and now Silicon Photonics PICs (for 400G/800G/1.6T transceiver cores). Competitive implication: reduces dependence on third-party optical IC suppliers and widens the addressable market. Key question for the next `/refresh-context CRDO` or `/earnings-update CRDO`: does the DustPhotonics margin profile drag or expand CRDO's blended FCF margin? |

---

## 📊 Earnings Refreshed (Rule #9)

**All Rule 9 refreshes this week are blocked by network egress restrictions** (yfinance + SEC 403). The refreshes are flagged; inputs remain at their last-updated values.

| Ticker | Reported | Priority | Notes |
|--------|----------|----------|-------|
| **CRDO** 📊 | Q4 FY26 (6/01, scan gap) | **HIGH — portfolio holding** | Rev $437M +157% YoY. Almost certainly a >15% beat. Old objective inputs are ~6 weeks stale post-DustPhotonics close. Refresh as soon as network access is restored. |
| **HPE** 📊 | Q2 FY26 (6/01, scan gap) | **HIGH — EPS +46%** | EPS $0.79 vs $0.54 est = 46% beat. Gross margin and FCF margin shift likely material. Not held, but the inputs understate AI server demand. |
| **PANW** | Q3 FY26 (6/02, scan gap) | Normal | Revenue beat moderate. Non-GAAP strong, GAAP distorted by integration charges. Refresh next rescore. |
| **MU** | Q3 FY26 — **June 24** (next week) | **Prepare** | Guided $33.5B revenue (81% GM, $1.4B opex). If in-line, will be the highest-impact Rule 9 refresh of the month. Current score 80.0 is TTM-based and significantly understates the current run rate. Have `/earnings-update MU` ready for June 24 post-close. |

**TTM limitation note (MU, CRDO):** Both names are on rapid fundamental ramps where TTM averaging understates the current business. MU's TTM GM is likely 15–20 points below the most recent quarter; CRDO's revenue trajectory means TTM likely includes two sub-scale quarters. When refreshes run, flag MRQ vs TTM divergence per Rule 9c.

---

## 💼 Portfolio Pipeline

### Mid-Week Portfolio & Methodology Changes (June 16–17)

**Two major structural changes occurred this week — this scan is first to document them.**

**June 16 — R5 Disruption Risk dimension added (Rule 16):**
- New fifth Risk dimension for Layer 10 (Models, Software & Applications) names: R5 rates business-model durability against agentic AI disruption (5 = no credible disruption, 1 = active erosion visible). All non-Layer-10 names default to 5.
- Rescored all 12 new QQQ-coverage names (WDAY, ADSK, CRM, PANW, ZS, FTNT, NOW, DDOG, CRWD, MDB, TEM, INTU) with both objective inputs and R5.
- Full-watchlist R5 pass completed.

**June 17 — Portfolio tightened to 14-name "76-bar" book:**
"Concentrate top names" — entry threshold raised from 74.5 to 76.0. This is a framework-level decision (per feedback: framework changes require Dom sign-off — surfacing here as documentation of a change that already occurred per the commit log).

| Change | Names | Notes |
|--------|-------|-------|
| **EXITED** (dropped below 76) | EME (75.5), PLTR (75.4), EQT (74.2), TER (73.5) | All below new 76 bar. TER at 73.5 — the June 12 scan flagged this as "hairline above exit." |
| **ENTERED** | APP (78.9), WDC (78.0) | Both scored well above 76; theses added June 18. |
| **Retained** (12 names) | TSM, NVDA, SNDK, MU, META, AVGO, CRDO, ANET, MSFT, ALAB, GOOGL, FIX | All ≥76.7 |

**Current 14-position portfolio (recalc scores, as of June 19):**

| Rank | Ticker | Score | Layer |
|------|--------|-------|-------|
| 1 | TSM | 84.7 | 05 Fabs |
| 2 | NVDA | 84.1 | 06 AI Compute |
| 3 | SNDK | 80.1 | 06 Memory |
| 4 | MU | 80.0 | 06 Memory |
| 5 | META | 79.4 | 09 Hyperscaler |
| 6 | AVGO | 79.2 | 06 Custom ASIC |
| 7 | CRDO | 78.9 | 07 Interconnect |
| 8 | APP | 78.9 | 10 Software |
| 9 | ANET | 78.5 | 07 Networking |
| 10 | WDC | 78.0 | 08 Servers/Storage |
| 11 | MSFT | 77.2 | 09 Hyperscaler |
| 12 | ALAB | 77.1 | 06 Custom ASIC |
| 13 | GOOGL | 76.8 | 09 Hyperscaler |
| 14 | FIX | 76.7 | 03 DC Construction |

**Pipeline status:**
- No ENTER signals (all names ≥76 are already in portfolio)
- No EXIT signals (lowest-scoring holding FIX at 76.7, comfortably above exit)
- **Next-in-line below 76:** ZS 75.5, PLTR 75.4, VRT 75.0, AMD 74.2
- **Watch:** FIX is the sole DC construction/mechanical contractor in the portfolio post-EME exit. Any score deterioration on FIX (e.g., backlog growth slows, margins compress) would put the portfolio without L03 coverage.

**50DMA refresh, `refresh_targets.py`, and `track_performance.py` all blocked** (yfinance egress). Pipeline membership confirmed from git commit log; performance mark computed from `tracking/performance-series.json`.

### Weekly Performance Mark (through June 18)

| Period | Model | SMH | QQQ | EW Universe | Model α vs SMH | Model α vs QQQ |
|--------|-------|-----|-----|-------------|----------------|----------------|
| Since inception (2026-05-26) | **+7.80%** ($10,780) | +9.59% | +1.42% | +8.32% | **−1.79%** | **+6.38%** |
| This week (June 12→18) | **+5.14%** | +6.44% | +2.67% | +5.60% | **−1.30%** | **+2.47%** |

Model value 2026-06-18: **$10,780** (up from $10,254 on June 12).

**Context:** The model underperformed SMH again this week as NVDA (+~14% week) and the broader semiconductor rally (NVDA bond deal as capex confidence signal) dominated. The model's per-position caps mean it captures less of mega-cap surges. QQQ alpha remains strongly positive (+6.38% inception). The June 17 rebalance (76-bar tighten) has been in place for 1 trading day — too early to assess its impact.

**Note:** June 19 series hasn't been written yet (CI runs ~5pm ET post-market). This mark reflects June 18 close.

---

## 🔬 Rating Integrity (Rule #12)

`audit_rating_integrity.py --summary`: **163 rated names | 63 gate violations (no thesis/briefing) | 0 stale (>90d)**

Watchlist grew from 135 tickers (June 12 scan) to 163 (+28) — the June 16 QQQ-coverage scoring batch added the new Layer 10 names (WDAY, ADSK, PANW, ZS, FTNT, CRWD, DDOG, MDB, NOW, TEM, INTU, plus others from the expanded Layer 6 analog/edge cohort).

Gate violations: 71 → 63 (down 8): the 7 cleared in the June 12 rating session + APP/WDC theses added June 18 account for 9 clearances; 1 new gate violation was introduced (from the batch add of new names without theses). 63 remaining gate violations are all non-portfolio names.

**Portfolio holdings with gate violations: 0.** All 14 portfolio holdings have theses or research briefings (cleared in the June 12 rating session, plus APP/WDC theses added June 18). This is the first scan with zero portfolio gate violations.

**Layer 10 R5 note (new):** The 12 QQQ names scored June 16 carry R5 ratings. Those ratings were assigned in the same scoring session and lack standalone Rating Audit entries for the R5 dimension. Consider flagging for a dedicated R5 audit pass on the Layer 10 cohort (the "absolute-lens stress test" called for in Rule 12) — uniform R5 bias across the cohort would only be visible from outside the relative ranking.

---

## Routine Filings

- **NVDA** — FWP + 424B5 (June 15): preliminary prospectus supplements for the senior notes offering; S-3 shelf (existing); EX-4/EX-5 trust indenture (June 18)
- **SMCI** — POSASR/424B5 (June 13–15): depositary share offering final prospectus
- **GOOGL** — S-3ASR (shelf registration for new depositary shares); 8-A12B (NYSE listing of preferred); annual proxy results (5.07) reported June 5 (in prior scan)
- **OKLO** — 8-K 5.07 (annual meeting results, June 3 — prior scan); S-3ASR $1B ATM (May 13 — prior scan); new: 1.01 LOI with LEU (June 18, noted above)
- **LEU** — 8-K 1.01 (Centrus/Oklo HALEU LOI, June 18, noted above)
- **NXP (NXPI)** — 8-K (June 11): interim dividend $1.014/share for Q2 2026
- **NVTS** — Two 8-Ks in June: prior scan covered June 9 (director Singh activist departure); a second 8-K was filed in the June 13–19 window (details blocked by EDGAR egress; check next scan)
- **ETN** — Dana RMT expected Q1 2027 close (confirmed by June 11 8-K — covered in prior scan; Eaton receives $1.1B cash + shareholders ≥50.1% of SpinCo+Dana)

---

## New 13F Activity

**Blocked — data.sec.gov not accessible.** Cannot confirm whether tracked funds (Berkshire, Baillie Gifford, Tiger, Coatue, Whale Rock, Lone Pine) filed 13F-HR/A since June 12. No 13F activity is expected in this period (between filing seasons; next 13F cluster ~Aug 14 for Q2 2026 holdings), but the check could not be run.

---

## Follow-up Items

**New this week:**
1. **CRDO** — Full `/earnings-update CRDO` recommended: Q4 FY26 beat + DustPhotonics optical strategy = large potential score delta. **Priority: run as soon as network access is available.** CRDO is portfolio holding #7.
2. **HPE** — Rule 9 refresh (EPS +46%, priority flag): `python3 scripts/batch_score.py --only HPE`. Not portfolio but inputs are stale.
3. **PANW** — Rule 9 refresh: `python3 scripts/batch_score.py --only PANW`. Standard priority.
4. **MU June 24 earnings** — Set up for `/earnings-update MU` post-June 24 close. Guidance: $33.5B revenue, 81% gross margin. If in-line, Rule 9 says immediate refresh (same session). TTM scores materially understate current run rate — will be highest-impact single refresh of the month.
5. **NVDA $25B debt** — No score change expected (ND/EBITDA stays low given EBITDA scale). Monitor use of proceeds disclosures for strategic signal — if next 10-Q mentions specific capex programs funded by the notes, that's thesis-relevant.
6. **Portfolio 76-bar rebalance** — Dom should review whether the tightened book reflects his intent. Key exits: PLTR (75.4 — near-miss), EME (75.5 — sole L03 mechanical contractor alongside FIX). Consider whether FIX alone provides adequate L03 exposure.
7. **R5 full-watchlist pass audit** — Layer 10 R5 ratings were assigned in a single batch session. Run absolute-lens stress test per Rule 12 to check for uniform bias (e.g., are all SaaS names rated 3 when some are closer to 2 or 4?).
8. **NVTS second June 8-K** — EDGAR-blocked; check on next scan with network access.

**Carried from 2026-06-12 scan:**
9. **Layer 3/9 BS Risk** — Financing wave (CRWV, HUT, APLD, CIFR, KEEL) — non-portfolio names, defer to next quarterly rescore.
10. **ETN** — Track Dana RMT regulatory/close timeline; target Q1 2027; post-separation Eaton is more thesis-direct. Passive watch.
11. **WULF** — Muskie anchor tenant: still none disclosed. "Advanced negotiations" on 480MW Kentucky site per a search result. Passive watch.
12. **D/NEE** — NextEra/Dominion deal progressing; FERC application not yet filed (as of June 12). Passive watch.
13. **MRVL** — GAAP EPS YoY artifact (April qtr NI $34.5M on record revenue). Identify the charge in the 10-Q at next pass.
