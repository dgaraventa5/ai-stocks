# Weekly News Scan — 2026-07-31

**Scope:** 173 watchlist tickers. Scan window: **2026-07-17 – 2026-07-31 (two weeks)** — no weekly scan ran on 2026-07-24 (gap in the schedule), so this pass extends the window to avoid a blind spot rather than silently skipping the missed week. A separate biweekly rating-refresh routine covered 8 Layer-1 Power names (PPL, XEL, VST, TLN, NRG, CCJ, UEC, LEU) through 2026-07-27 (`tracking/rating-refresh-2026-07-27.md`) — that research is referenced, not duplicated, below.

## Execution note (network constraints — unchanged from prior scans)

SEC EDGAR (`data.sec.gov`, `www.sec.gov`) and Yahoo Finance remain 403-blocked from this session's egress proxy (confirmed directly via `curl` and the proxy's own status endpoint before starting). Substituted `WebSearch` via the `web_scan.py` fallback methodology (date-verified, source-preferenced, full-watchlist query plan), executed through 8 parallel research agents: 4 covering the 12 portfolio holdings in depth (3 tickers each), 1 covering the Layer-10 SaaS watch (PLTR/DDOG/CRM) on the requested NRR/AI-adoption/pricing dimensions, and 4 sweeping the remaining 158 tail tickers. **All 173 tickers received at least one query this week** — a fuller sweep than the last two scans, which scoped to holdings+SaaS-only after hitting a WebSearch budget wall. Items with no confirmable publication date are marked UNVERIFIED per rule 3, not assumed in-window.

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

Same 12 holdings as the last several scans (unchanged since the 7/2 rebalance): NVDA, TSM, MU, CRDO, META, ANET, AVGO, AMZN, SNDK, MSFT, GOOGL, FIX.

Going in: **NVDA** (84.39 ✓✓) believed the dominant AI-accelerator vendor mid-Blackwell/Rubin ramp, tier-crossed down from ✓✓✓ on 7/16 (price-driven). **TSM** (82.25 ✓✓) believed strong post its 7/16 record Q2. **MU** (80.64 ✓✓) believed on-thesis (HBM/auto diversification) with an unconfirmed Burry short rumor as the open question. **CRDO** (79.72 ✓✓) believed quiet/unchanged. **META** (78.30 ✓✓) and **AMZN** (76.86 ✓✓) both had Q2 prints falling inside this window — a live open question going in, since neither had reported as of the 7/17 scan. **ANET** (78.24 ✓✓) believed unchanged, pre-earnings. **AVGO** (77.05 ✓✓) believed on-thesis with a fresh ITC legal overhang (Samsung HBM patent dispute) as the watch item. **SNDK** (76.11 ✓✓) believed expectations-stretched (800% YTD) with an unconfirmed Meta NAND deal as the open thread. **MSFT** (75.78 ✓✓) and **GOOGL** (72.39 ✓✓, GOOGL already reported 7/22 and refreshed 7/27) both had FY-end/Q2 catalysts in or near this window. **FIX** (75.08 pre-refresh ✓✓) believed unchanged post its 7/1 leadership transition, with a rule-9 refresh already applied 7/27.

**What was wrong, and why it matters:** three of the four hyperscaler holdings — **MSFT, META, and AMZN** — all reported Q2/FY2026 earnings *inside* this window, each with a major upward AI-capex guidance revision (MSFT FY27 capex guide **more than doubled** to $255–260B; AMZN raised FY26 capex to ~$220B; META narrowed to $130–145B with the low end up $10B). None of this was priced into last week's mental model, which treated META/AMZN as still-pending and didn't anticipate the scale of the capex acceleration. This is exactly the kind of thesis-relevant signal Step 0 exists to catch — and it arrives at a moment when this session **cannot refresh the objective inputs that would reflect it** (network-blocked), so the Watchlist's MSFT/AMZN/META rows are now meaningfully stale relative to what the market and the companies themselves just confirmed.

---

## ⚠️ Material Events

### Portfolio holdings

1. **MSFT — Q4 FY2026 earnings (2026-07-29) — MATERIAL, triggers rule-9** 📊
   Revenue $90.0B (+18% YoY, beat consensus ~2.7%); adjusted EPS $4.74 vs. $4.24 consensus (beat ~11.8%); Azure grew 43% (accelerating), crossed $100B in FY revenue for the first time; Commercial RPO +84% YoY to $678B; M365 Copilot passed 30M paid seats. **FY2027 capex guidance $255–260B — more than double FY2026's $115.95B actual.** Stock closed +15% on 7/30, reported as the largest single-day market-cap gain in stock-market history (~+$500B).
   Sources: [SEC 8-K exhibit](https://www.sec.gov/Archives/edgar/data/0000789019/000119312526323632/msft-ex99_1.htm), [CNBC](https://www.cnbc.com/2026/07/29/microsoft-msft-q4-earnings-report-2026.html)

2. **AMZN — Q2 2026 earnings (2026-07-30) — MATERIAL, triggers rule-9** 📊
   Revenue $200.6B (+20% YoY, beat ~2.3%); GAAP EPS $5.75 vs. ~$1.82 consensus — **distorted by a $53.4B one-time pre-tax gain on Amazon's Anthropic investment** (flag for rule-15 treatment: EPS YoY looks non-operating-dominated, a blanking candidate once refreshed); AWS revenue $42.2B (+37% YoY, 5th straight accelerating quarter, margin 39% +650bps); FY2026 capex guidance raised from ~$200B to **~$220B** — management said even that won't meet 2026 demand and expects the same into 2027.
   Separately: departing AWS SVP Dave Brown confirmed (7/17) joining **Meta** to lead data-center build-out and a possible new "Meta Compute" cloud service — new information beyond the 7/15 departure disclosure, and a talent/competitive-overlap data point for both AMZN and META.
   Sources: [CNBC](https://www.cnbc.com/2026/07/30/amazon-amzn-q2-earnings-report-2026.html), [about Amazon](https://www.aboutamazon.com/news/company-news/amazon-earnings-q2-2026-report), [GeekWire](https://www.geekwire.com/2026/departing-aws-exec-dave-brown-is-reportedly-joining-meta-as-facebook-parent-mulls-its-own-cloud/)

3. **META — Q2 2026 earnings (2026-07-29) — MATERIAL, triggers rule-9** 📊
   Revenue $60.8B (+28% YoY, beat ~1%); EPS $6.18 **missed** consensus (~$7.14–7.22) by ~13–14% — total costs +55% YoY including a $2.4B legal-contingency charge and $1.18B severance (8,000-person headcount reduction); operating margin compressed to 31% from 43% a year ago; quarterly FCF fell to $784M from $8.55B a year earlier. **Capex guidance narrowed to $130–145B** (low end +$10B in one quarter); Q2 capex itself more than doubled YoY to $31.1B. Stock fell ~6.6–9% post-earnings.
   Separately: a federal judge denied an emergency injunction (date reported as 7/17, precise date not independently confirmed — flagged UNVERIFIED) sought by 26 employees trying to block AI-flagged (Metamate-scored) layoffs.
   Sources: [Investing.com transcript](https://www.investing.com/news/transcripts/earnings-call-transcript-meta-misses-eps-in-q2-2026-as-stock-sinks-after-hours-93CH-4821910), [KuCoin](https://www.kucoin.com/news/flash/meta-q2-2026-earnings-miss-estimates-capex-guidance-rises-to-145-billion)

4. **AVGO — Samsung MOU (2026-07-25)**
   Broadcom and Samsung signed a non-binding MOU worth **>$200B through 2030** covering HBM4 memory supply, 2nm foundry manufacturing, and advanced packaging for AVGO's AI accelerators — part of a ~$950B US-Korea semiconductor cooperation package. Non-binding statement of intent, not a firm order. The 7/16 ITC Section 337 investigation (Samsung HBM patent, AVGO/NVDA/GOOGL/SMCI named) has no in-window procedural update.
   Sources: [Bloomberg](https://www.bloomberg.com/news/articles/2026-07-25/samsung-inks-200-billion-chip-supply-with-broadcom), [CNBC](https://www.cnbc.com/2026/07/25/samsung-electronics-wins-200-billion-broadcom-ai-chip-partnership.html)

5. **MU — Burry short increase + CXMT IPO (2026-07-24, 2026-07-27)**
   Michael Burry disclosed adding to his MU short (new entry $933.86, after the original 7/2 $1,051.87 entry), citing the 209% YTD rally as extreme vs. the 200-day MA and low ROIC/ROE. Separately, **CXMT (China's #4 DRAM producer)** IPO'd on Shanghai's STAR Market, raising ~$8.6B (Asia's largest 2026 IPO), +470%, becoming China's most valuable listed company — still 2nd-gen HBM (none in the IPO prospectus), but a real China-DRAM-competition data point. Stock swung -9% (7/28) then +16% (7/30, Samsung/SK Hynix earnings read-through; BofA added MU to its "US 1 List").
   Sources: [GuruFocus](https://www.gurufocus.com/news/8979535/michael-burry-increases-short-positions-on-micron-mu-nvidia-nvda-and-caterpillar-cat), [TechNode](https://technode.com/2026/07/27/cxmt-becomes-chinas-most-valuable-a-share-company-after-8-6-billion-ipo/)

6. **NVDA — Vera Rubin ramp + US manufacturing (2026-07-20 to 07-22)**
   Vera Rubin NVL72 production ramping at CoreWeave/Google Cloud/Azure/OCI/Nebius (CoreWeave validated the first rack, 10x tokens/MW vs. Grace Blackwell NVL72 on a DeepSeek-R1 benchmark); Bristol Myers Squibb expanded its NVIDIA partnership for drug-discovery AI infrastructure; Wistron opened NVIDIA's first US-dedicated manufacturing plant (Fort Worth, TX, $700M) producing GB300 domestically. All positive customer/capacity signals; ITC investigation unresolved.
   Sources: [SiliconANGLE](https://siliconangle.com/2026/07/21/nvidia-doubles-ai-factories-showcases-massive-vera-rubin-performance-gains/), [NVIDIA Blog](https://blogs.nvidia.com/blog/wistron-manufacturing-texas/)

7. **GOOGL — DeepMind disbands AlphaFold team (2026-07-29/30)**
   Google DeepMind dissolved its dedicated AlphaFold team, reassigning most researchers; Nobel laureate John Jumper + 2 other core co-authors already departed for Anthropic in June (~25% of the original paper's authors have now left Google). Talent-attrition signal for AI-thesis/moat monitoring, not a financial-thesis break. Separately, GOOGL's **live watchlist score (72.39) now sits below the portfolio's 73.0 exit-score threshold** post the 7/27 rule-9 refresh — see Portfolio Pipeline below.
   Sources: [Engadget](https://www.engadget.com/2225849/google-shuts-down-alphafold/)

8. **FIX — Hunt Electric acquisition + dividend raise (2026-07-24)**
   Disclosed alongside the (already-refreshed) Q2 print: Hunt Electric acquisition (~$250M annualized revenue) and a dividend increase to $0.90/share. FIX's live score jumped to **82.29** (from the 75.08 pre-refresh snapshot) — still ✓✓, no tier crossing, genuinely fundamentals-driven (unlike NVDA's price-driven move two weeks ago).

*(ANET, CRDO: nothing beyond routine insider 10b5-1 sales and minor product announcements this window.)*

### Other watchlist names — highest-materiality items

**Executive transitions:**
- **AAPL** — 8-K (7/30, same filing as Q3 FY2026 results): **John Ternus becomes CEO effective 9/1/2026; Tim Cook moves to Executive Chairman.**
- **EQIX** — both previously-flagged departures now filing-confirmed: CBO Jon Lin effective 7/18; CAO Simon Miller's retirement effective 7/31.
- **ENTG** — Executive Chair Bertrand Loy retiring effective 7/31; James Gentilcore succeeds. Stock -9.4% (7/29).
- **PSIX** — New CEO Richard Hu appointed (effective 8/17); ongoing securities-fraud investigation announcements (Bronstein Gewirtz & Grossman, multiple dates through July).
- **MCHP** — COO Richard Simoncic resignation (effective 8/17), announced alongside the Hailo (edge-AI) acquisition, both 7/24.

**Legal/regulatory:**
- **ADI** — new, unrelated cybersecurity incident disclosed 7/26 (unauthorized access, data exfiltrated) — company still assessing.
- **INTU** — securities class-action shareholder alert (7/23) tied to a ~20% stock slide from weak fiscal Q3 tax-season results.
- **ZS** — Schall Law Firm fraud investigation announced 7/22.
- **PLAB** — active lead-plaintiff solicitation across multiple firms (deadline 9/4) re: alleged misleading IC-photomask-demand statements.

**Capacity / customer wins (AI-buildout thesis):**
- **CORZ** — signed a **15-year AMD colocation lease (~530MW, up to $14B potential revenue)** — a major capacity/customer win (7/27).
- **HUT** — fully commercialized the 1GW Beacon Point campus (2nd 352MW lease, $19.6B base-term contract value); separate unconfirmed reports of Nvidia lease commitments up to $50B tied to the same TX site.
- **NEE** — NextEra + Brookfield announced a ~$100B Kentucky data-center campus.
- **SO** — signed a 3.2GW/25-year data-center power contract with **OpenAI** near Savannah, GA.
- **IREN** — raised 2026 AI Cloud ARR target to >$4B (from $3.7B); signed $2.8B in new multi-year AI-developer contracts.
- **AMKR** — new 10-year TSMC Arizona advanced-packaging partnership.

**M&A:**
- **EXE** — definitive agreement to acquire Twin Eagle Holdings for $1.25B.
- **TEM** — definitive agreement to acquire the remaining 87.85% of Personalis for $1.6B.
- **LSCC** — completed the AMI acquisition, targeting >$1B ARR by YE2026.
- **ADSK** — $3.6B acquisition of MaintainX (confirmed, follow-up analyst coverage this window).
- **MTZ** — completed $1.65B Superior Group (Electrical Specialists) acquisition.
- **NXT** — acquisition of Zimmermann PV-Steel Group (Germany, up to €330M).

**Broad AI-capex-supercycle confirmations (beat + raised guidance, worth a rule-9 objective-input refresh once network access is restored):** BE (~2x EPS beat), UMC (EPS +255%, capex raised to $2.0B), MPWR (Enterprise Data +164% YoY), EME (record revenue, record $17.1B backlog), JCI (backlog +30% to $21B), PWR (guidance far above consensus), TER (revenue +104% YoY), APH (revenue +55% YoY, record), STX (record FCF, gross margin first time >50%), TT (record $12.1B backlog), DLR (big FFO beat, guidance raised), FLEX, GEV, TSLA (record revenue but EPS miss, deliveries first YoY growth in 2 years).

**"Beat but stock fell" divergences (candidates for `expectations_flag.py` at next context refresh, rule 14):** KLAC (-10.8%), GLW (-12% on weak Q3 guide), NXPI, RDDT (-10% AH), CRM's cRPO-vs-adoption gap (below).

**Foreign-filer / competitive-landscape watch:** CXMT's record Shanghai IPO (above, under MU) and continued TSM stock weakness (-17% off highs) on capex/margin-dilution and China-competition concerns are the same underlying theme — worth holding in mind together at the next Layer-05/06 cohort review.

### Layer 10 SaaS Watch: PLTR, DDOG, CRM

*Per scan instructions — tracking NRR, AI feature adoption, pricing-model shifts. None are current portfolio holdings.*

**CRM (64.29 ✓) — the most material development of the three.** Morgan Stanley downgraded CRM (Overweight→Equal Weight, PT cut 35% to $185) on **2026-07-21**, explicitly citing that Agentforce adoption improvements haven't moved cRPO (current remaining performance obligation) — a **second** major sell-side voice (after the 7/9 KeyBanc/Bernstein note) landing on the same complaint. This is the R5=2 disruption-risk thesis showing up directly in analyst channel checks, now from two independent shops. Separately, Agentforce Help Agent reached general availability with **pay-per-resolution pricing** ($2/resolution, $0 if unresolved) — the first concrete outcome-based-pricing SKU, direct evidence on the pricing-model-shift dimension (exact GA date within the window unverified; the pricing mechanics are confirmed). No standalone NRR figure could be confirmed as still disclosed this cycle — flagged for a direct 10-Q check rather than assumed. Next earnings 8/26 (outside window).

**PLTR (70.22 ✓✓)** — quiet on NRR/AI-adoption/pricing (no new data before the 8/3 print), but DIA withdrew its ASTRA solicitation (in-house-build alternative to Palantir's platform) after a Palantir GAO protest (7/20–24) — reinforces the "buy commercial, don't build custom" government moat.

**DDOG (63.51 ✓)** — nothing new on NRR/Bits AI adoption/pricing; routine continuing 10b5-1 insider sales (CEO, a director) and pre-earnings analyst PT raises (Morgan Stanley, Citi, BTIG all to ~$300). Next earnings 8/6 (outside window).

---

## 📊 Earnings Refreshed (Rule #9)

| Ticker | Reported | Beat/miss magnitude | Objective refresh status |
|---|---|---|---|
| **MSFT** | 2026-07-29 | Rev +2.7%, EPS +11.8%, FY27 capex guide >2x | **BLOCKED** — needs a network-capable session (SEC/yfinance egress denied here). 📊 top priority given the stock reaction and capex-guide magnitude. |
| **AMZN** | 2026-07-30 | Rev +2.3%, EPS beat distorted by $53.4B one-time Anthropic gain (rule-15 blank candidate) | **BLOCKED** — same. 📊 priority. |
| **META** | 2026-07-29 | Rev +1%, EPS miss ~13-14%, capex guide raised | **BLOCKED** — same. 📊 priority (close to the 15% miss threshold, and the capex/margin story is thesis-relevant regardless). |
| **GOOGL** | 2026-07-22 | Rev +24% YoY, Cloud +82% | **Already done** — 2026-07-27 refresh (EPS YoY blanked per rule 15, FCF margin/ND-EBITDA updated). No duplicate action taken. |
| **FIX** | 2026-07-23/24 | Rev +50.3%, EPS +91.9% | **Already done** — 2026-07-27 refresh. Confirm the Hunt Electric acquisition + dividend raise were captured alongside the Rev/EPS inputs (not just the growth %s). |
| **TSM** | 2026-07-16 (pre-window) | — | **Already captured** by the 7/16 full-watchlist objective refresh (confirmed in the 7/17 scan). |

**TTM vs. MRQ check:** not computable this pass for any of the three blocked names — no fresh yfinance pull was possible. Flagging per rule 9c that MSFT/AMZN/META's Q4/Q2 prints (all showing accelerating growth) make TTM-based Quality metrics *more* likely to understate the current run-rate than usual — worth a dedicated MRQ note when the refresh does run.

**Broader tail-name earnings:** a large number of non-holding names also reported strong beats + raised guidance this window (BE, UMC, MPWR, EME, JCI, PWR, TER, APH, STX, and more — see Material Events above). These fall under rule 9's "within 1 week" bucket rather than the priority bucket, and refreshing them is equally blocked by network egress this session. Recommend a batch `scripts/refresh_objective_inputs.py` (or `/refresh-objective`) run across **MSFT, AMZN, META** first, then the broader earners list, from a network-capable session.

---

## 💼 Portfolio Pipeline

```
$ python3 scripts/refresh_targets.py --check
Targets reflect current scores ✓
```

No membership or tier change fired — the Targets sheet (last written 2026-07-16, one name refreshed 2026-07-27) remains frozen per the hysteresis rule, and `--check` confirms nothing is currently gated on a stale rebalance.

**Two within-tier score moves worth Dom's attention despite the freeze:**

| Ticker | Pre-refresh (Targets snapshot) | Live (current) | Note |
|---|---|---|---|
| **FIX** | 75.08 / ✓✓ | **82.29** / ✓✓ | Fundamentals-driven improvement (Q2 beat). No action needed — still solidly ✓✓. |
| **GOOGL** | 75.26 / ✓✓ | **72.39** / ✓✓ | Now **below the portfolio's 73.0 exit-score threshold**. Doesn't fire an automatic rebalance because the scoring *Tier* itself (✓✓) hasn't crossed — the hysteresis mechanism only fires on tier crossings or membership changes, not on crossing the exit-score line while still within the same tier. Flagging explicitly since this is the kind of drift that could otherwise go unnoticed until a future tier cross. |

A small cohort-percentile ripple from the 7/27 GOOGL/FIX refresh nudged three other Layer-03 names (CARR, TT, AAON, each ≤0.8 pts) — immaterial, noted for completeness per rule 20's cohort-relative scoring mechanics, no tier effects.

**Weekly performance mark** (from `tracking/performance-series.json`, maintained by network-capable `daily-refresh.yml` CI; latest close 2026-07-30):

| Period | Model | SMH | QQQ | SPY | EW Universe |
|---|---|---|---|---|---|
| This window (7/17 → 7/30) | **−0.87%** | −3.17% | −1.69% | −0.22% | +0.17% |
| Since inception (5/26) | **−3.68%** ($9,632.31) | −10.50% | −6.30% | −0.93% | −0.80% |

The model recovered somewhat from last scan's -6.14% weekly drawdown and outperformed both SMH and QQQ this window and since inception, though it remains modestly behind SPY and the equal-weight universe on a since-inception basis. Not a thesis break — no fundamental deterioration surfaced this scan for any holding; the MSFT/AMZN capex-guide beats this week are a tailwind the mark doesn't yet fully reflect (as of the 7/30 close, one day after MSFT's +15% move). Per project rules, this is not a trade recommendation.

**Concentration flag (carried forward, unchanged):** Layer-06 silicon (NVDA 11.76% + MU 9.64% + AVGO 7.61% + SNDK 7.09% ≈ **36.1%**) remains the largest single-layer concentration, no cap active.

**50DMA refresh:** blocked by yfinance egress (unchanged every session this cycle) — last-known values stand, not refreshed this pass.

---

## 🔬 Rating Integrity (Rule #12)

```
$ python3 scripts/audit_rating_integrity.py --summary
rating-integrity (all layers): 170 rated names | 0 UNGATED (no thesis) | 0 stale (>90d)
```

Clean — sixth consecutive week, no gate violations, no stale (>90d) ratings. The 2026-07-27 biweekly rotation refreshed the 8 stalest Layer-1 names (PPL, XEL, VST, TLN, NRG, CCJ, UEC, LEU) via `/refresh-context` — research-only, no rating changes; see `tracking/rating-refresh-2026-07-27.md`.

---

## 🎯 Calibration (Rule #17)

```
$ python3 scripts/resolve_forecasts.py --dry-run
0 resolved, 0 need review (dry run — nothing written)
```

14 open forecasts (`tracking/forecasts.jsonl`), all `REL_STRENGTH_1Q` seeded 2026-06-26 with `resolution_date: 2026-09-30`. Nothing due this week.

---

## Routine filings

<details>
<summary>Expand for the full list (confirmed in-window, non-material — dividends, routine insider 10b5-1 sales, analyst PT changes without new information, earnings-date-only announcements, and beat-quarters without a thesis-relevant angle beyond the capex-supercycle theme noted above)</summary>

**Power/Utilities:** BE (Q2 2x beat, guidance raised; $1.7B Nebius-linked fuel cell project); CEG (PJM auction clear, Crane nuclear restart FERC waiver, NY DC-permit-moratorium overhang); DUK (dividend raise, analyst upgrades); NRG (dividend, unexplained stock pops); GEV (Q2 beat, Hawaiian Electric contract); AEP (Q2 mixed, board additions); ETR (Q2 miss, equity offering); D (Q2 call held, no results content surfaced yet); XEL (Q2 mixed — EPS beat/revenue miss, $70B+ capex plan through 2030); CCJ (Q2 miss, Cigar Lake stake raise, term-price strength); SO/CMI/GNRC/HTHIY (Q2 beats, guidance raises); PPL/OKLO/UEC — nothing new post-7/27 rotation beyond routine PT tweaks; SMR (litigation-firm investigation, analyst Hold init); RRC (Q2 beat, buyback completed); ABBNY (Q2 mixed, backlog record, M&A); NNE (AFWERX defense award).

**Grid/DC construction/cooling:** ETN, HUBB, TT, CARR, DLR, MOD, MTZ, PWR, TER, KEYS, POWL, AAON — broad Q2 beats/guidance raises on data-center demand, no distinct thesis-relevant angle beyond the sector-wide theme. IRM, NVT — stock drops with no distinct catalyst identified.

**Semi-equipment/materials:** ASML, KLAC (beat but -10.8% on cautious guide), CAMT, LRCX (+20% on beat), ONTO, MKSI, ENTG, LSCC, BESIY, FORM, ACLS, COHU, AEIS, UCTT, TOELY — broad beats/guidance raises; ONTO/COHU/MKSI/UCTT saw sector-wide selloff pressure with no distinct company catalyst.

**Fabs/foundry:** ASX, TSEM, GFS ($300M CHIPS silicon-photonics award), UMC (above), 5347.TWO, 0981.HK — nothing beyond noted items.

**EDA/IP/silicon:** SNPS (agentic-AI chip-design workflow push at DAC), CDNS (Q2 beat, Rapidus agentic-AI partnership), ARM (data-center royalty doubled), MRVL ($250M India AI investment), TXN, NXPI, QCOM (weak Q4 guide), MCHP (Hailo M&A + COO departure, above), ADI (cybersecurity incident, above), STM, SWKS (dividend eliminated, $2.0B buyback, Qorvo-merger leadership team named), ON, AMBA, NVTS ($203M non-cash earnout charge), LSCC.

**Optical/networking:** COHR, LITE (EVP retirement), FN, AAOI, CIEN, GLW (above), APH (above), TEL, POET (volatile), CRDO (routine only).

**Servers/storage:** SMCI ($60B+ new orders), DELL, HPE, WDC (above), STX (above), NTAP (DataPelago acquisition), FLEX, P.

**Cloud/neocloud/BTC-to-AI:** ORCL (above), CRWV (CEO sale, Galaxy Digital/Leidos/Backblaze deals), NBIS ($1B+ Reflection AI deal), APLD, CORZ (above), IREN (above), CIFR, HUT (above), RIOT, BTDR, WULF (NY moratorium risk), KEEL, HIVE, SHAZ, WYFI.

**Software/SaaS (Layer 10, non-focus names):** SNOW, NOW (Q2 beat, AI Control Tower >$1B ACV), MDB, PATH, FTNT, ADSK (MaintainX M&A), PANW (Embrace acquisition), ZS (above), INTU (above), WDAY (insider selling pattern), TSLA (above), AAPL (above), AMD (Anthropic 2GW MI450 deal), APP (sentiment-driven decline), RDDT (beat but AH drop), HOOD (record Q2, ABS financing filing).

**Foreign filers / other:** TE/T1 Energy (above), PUMP, PSIX (above), KN, AMKR (above), HHUSF.

</details>

---

## New 13F Activity

None. Per the 2026-07-03 scan's confirmation across all six tracked funds, Q2 2026 13F-HR filings are not due until **August 14, 2026** — no activity expected in this window regardless.

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🔴 | **MSFT, AMZN, META all reported Q2/FY2026 earnings this window with major AI-capex guidance increases (MSFT capex guide >2x, AMZN to ~$220B, META to $130-145B) and this session cannot refresh their objective inputs** (SEC/yfinance egress blocked). Recommend running `/refresh-objective MSFT,AMZN,META` (or `/earnings-update` per name) from a network-capable session as soon as possible — these are exactly the "staleness costs the most" names rule 9 exists to protect against. |
| 🟡 | **GOOGL's live score (72.39) is now below the portfolio's 73.0 exit-score threshold** but doesn't trigger EXIT PENDING because the scoring Tier itself hasn't crossed — worth a conscious look given this is a fundamentals-driven (not just price-driven) drift (FCF margin compression, negative-FCF quarter). |
| 🟡 | **CRM's disruption thesis (R5) picked up a second independent sell-side confirmation** (Morgan Stanley downgrade, 7/21) plus a concrete outcome-based-pricing data point (Agentforce Help Agent pay-per-resolution GA) — worth a `/refresh-context CRM` pass to re-examine R5/D-dimensions against the absolute-lens standard next rotation. |
| 🟢 | **AAPL CEO succession** (Ternus to become CEO 9/1, Cook to Executive Chairman) — not a portfolio holding but a major governance event on a Layer-10 watchlist name; worth a news-log note is already made, no further action implied. |
| 🟢 | **CORZ's 15-year, up to $14B AMD colocation lease** (7/27) is a major capacity/customer-win data point for the Layer-9 cohort — candidate for the next `/refresh-context` rotation given rule-13's EV/MW-vs-AI-Thesis divergence framework. |
| 🟢 | **This week's model mark: −0.87%, since-inception −3.68%.** Recovered from last week's -6.14% weekly drawdown; still ahead of SMH/QQQ since inception, modestly behind SPY/EW. Not a thesis break. |
| 🟢 | **MU (Burry short increase, CXMT IPO) and TSM (continued post-earnings stock weakness)** are both facing the same underlying China-competition narrative — worth holding in mind together at the next Layer-05/06 review, though neither shows a fundamentals-level thesis break yet. |
