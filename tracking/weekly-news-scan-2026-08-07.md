# Weekly News Scan — 2026-08-07

**Scope:** 214 watchlist tickers. Scan window: **2026-07-31 – 2026-08-07** (this was peak Q2/FY2026 earnings week for the sector — a large fraction of the watchlist reported either just before this window opened (7/28–7/30) or inside it; per scan discipline, only items dated inside 7/31–8/7 count as "material" below, and pre-window earnings are flagged separately for context, not counted).

## Execution note (network constraints — unchanged from prior scans)

SEC EDGAR (`data.sec.gov`, `www.sec.gov`) and Yahoo Finance (`query1/2.finance.yahoo.com`) are confirmed 403-blocked from this session's egress proxy (verified directly via `curl` and the proxy's own status endpoint before starting — `recentRelayFailures` shows `connect_rejected` on both hosts). This is the same network state as every scan since 2026-06-12. Substituted the `web_scan.py` fallback methodology (date-verified, source-preferenced) executed through **8 parallel research agents**: 3 covering the 13 current portfolio holdings in depth (NVDA/FIX/TSM/MU; CRDO/ANET/MSFT/AVGO; GMED/SNDK/EME/6861.T/META), 1 covering the Layer-10 SaaS watch (PLTR/DDOG/CRM) on the requested NRR/AI-adoption/pricing dimensions, and 4 sweeping the remaining 198 tail tickers (~50 each). **All 214 tickers received at least one query this week.** Because this was peak earnings week, the raw material-event count is unusually high (~128 items surfaced across agents) — this report curates to the thesis-relevant subset per CLAUDE.md's signal-over-volume rule; routine beat-and-raise prints with no distinct strategic angle are collapsed into the routine-filings toggle.

Local, non-network scripts ran cleanly: `audit_rating_integrity.py`, `resolve_forecasts.py --dry-run`, `refresh_targets.py --check`. `momentum_50dma.py` and any yfinance-based objective refresh remain blocked (confirmed via a live test call this session).

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

13 current holdings (all ✓✓ tier, none ✓✓✓; Targets sheet last refreshed 2026-08-03, when AMZN/GOOGL exited and GMED/6861.T entered): **NVDA, FIX, TSM, MU, CRDO, ANET, MSFT, AVGO, GMED, SNDK, EME, 6861.T, META.**

Going in: **NVDA** (84.33 ✓✓) believed the dominant AI-accelerator vendor mid-Blackwell/Rubin ramp. **FIX** (82.29 ✓✓) believed unchanged post its 7/27 refresh (Q2 beat, Hunt Electric deal already captured). **TSM** (82.25 ✓✓) believed on-thesis post record Q2, with an ongoing China-competition (CXMT) narrative as the watch item. **MU** (80.69 ✓✓) believed on-thesis (HBM/auto diversification) with an *unconfirmed* Burry short rumor and CXMT IPO as open threads. **CRDO** (79.72 ✓✓) believed quiet. **ANET** (78.24 ✓✓) was pre-earnings — open question going in. **MSFT** (77.78 ✓✓) and **META** (73.27 ✓✓) both already refreshed 8/2 post-Q2/Q4 prints, believed stable. **AVGO** (77.16 ✓✓) believed on-thesis with the Samsung MOU + ITC HBM patent case as watch items. **GMED** (76.61 ✓✓) and **6861.T** (74.62 ✓✓) both entered the portfolio 8/2 — thin research base, first real test of the position this week. **SNDK** (76.34 ✓✓) believed expectations-stretched, with an unconfirmed Meta-NAND deal rumor as an open thread. **EME** (74.79 ✓✓) entered 8/2, believed unchanged.

**What the scan changed:** ANET reported its first-ever $3B quarter with raised guidance (a real fundamentals move, not yet reflected in its score). GMED and SNDK both reported first-since-portfolio-entry earnings beats — also not yet reflected. The Burry-short "rumor" on NVDA/MU converted to a **confirmed, sized position** this week. TSM and MU both picked up fresh CXMT competitive-threat data points (a second Beijing fab in early talks; independent analysis of CXMT's HBM technology gap). None of this is priced into the current Watchlist scores because **objective-input refresh remains network-blocked this session** — the diff below is real and the scoring lag is the main actionable item from this scan.

---

## ⚠️ Material Events

### Portfolio holdings

1. **ANET — Q2 2026 earnings (2026-08-04) — MATERIAL, triggers rule-9** 📊
   Revenue $3.036B (+37.7% YoY, beat consensus ~$2.87B by ~5.9%) — Arista's first-ever $3B quarter. EPS $1.02 vs. $0.90 consensus (+13.3% beat). Q3 guide ~$3.3B (+9% QoQ); FY2026 outlook raised to ~$12.6B (~40% growth), management held the ≥$3.5B AI-fabrics-revenue target. Etherlink AI platform customer count passed 100 cumulative customers. Concentration risk reiterated: heavy reliance on "Cloud Titan" customers (Microsoft, Meta specifically named) if they shift to proprietary in-house networking — not new information but worth noting given MSFT is also a portfolio holding.
   Sources: [Arista IR](https://investors.arista.com/Communications/Press-Releases-and-Events/Press-Release-Detail/2026/Arista-Networks-Inc--Reports-Second-Quarter-2026-Financial-Results/default.aspx), [SiliconANGLE](https://siliconangle.com/2026/08/04/arista-networks-stock-jumps-stellar-earnings-revenue-beat-strong-forecast/), [Motley Fool](https://www.fool.com/investing/2026/08/05/arista-networks-just-delivered-its-first-3-billion/)

2. **NVDA + MU — Michael Burry short position CONFIRMED and expanded (2026-08-02) — MATERIAL**
   Burry publicly added NVDA put options (expiring Dec 18 2026, strikes low $100s) and increased his MU short (sized near $880), citing concern that a "very significant proportion" of NVIDIA's current/future AI demand is financed via undisclosed, off-balance-sheet circular arrangements rather than end-customer-driven. This converts the item flagged as an "unconfirmed rumor" in recent scans to a confirmed, sized position — a genuine thesis-risk data point for both names, independent of one's view on the underlying claim.
   Sources: [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/michael-burry-sends-fresh-warning-162112665.html), [TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262055020-big-short-michael-burry-ai-bubble-ramping-short-positions-nvidia-micron-tradingkey)

3. **MU — CXMT competitive-threat escalation (2026-08-03/07-31) — MATERIAL**
   Reuters (8/3): CXMT is in early-stage talks, with local-government funding discussions, to build a **second** 12-inch DRAM fab in Yizhuang, Beijing — a capacity-expansion escalation beyond its existing Shanghai fab. Separately, a 7/31 CNBC competitive analysis (follow-on to CXMT's 7/27 IPO, itself pre-window) frames CXMT's initial HBM output as likely HBM3/HBM3E-class — one to two generations behind Micron/SK Hynix/Samsung (already on HBM4/4E) and running 20–30% higher cost-per-bit, i.e. the near-term competitive gap remains wide despite the capacity buildout.
   Sources: [Reuters via Yahoo Finance](https://finance.yahoo.com/technology/articles/exclusive-cxmt-plans-second-chip-082423366.html), [CNBC](https://www.cnbc.com/2026/07/31/cxmts-sk-hynix-samsung-micron-memory-chip.html)

4. **TSM — 3nm ramp acceleration (2026-08-03/08-05) — MATERIAL**
   TrendForce reports TSMC is accelerating its 3nm ramp, targeting 180K monthly wafer starts by early Q4 2026 (2–3 months ahead of prior expectations) on strong NVDA/AMD/Broadcom demand; combined 2nm+3nm starts seen exceeding 260K/month by year-end. Stock reaction positive, market cap back above $2T. (TSMC's capex raise to $60–64B was the 7/16 earnings-call item, already known — this is a new, separate demand-acceleration data point.)
   Sources: [TrendForce](https://www.trendforce.com/news/2026/08/03/news-tsmc-3nm-monthly-wafer-starts-to-hit-180k-by-early-4q26-on-strong-demand-2-3-months-ahead-of-expectations/), [Benzinga](https://www.benzinga.com/markets/tech/26/08/60958922/what-is-going-on-with-taiwan-semiconductor-stock-on-wednesday)

5. **GMED — Q2 2026 earnings + guidance raise (2026-08-06) — MATERIAL, triggers rule-9** 📊
   Revenue $789.6M (+5.9% YoY, +0.9% vs. consensus). GAAP diluted EPS $1.10 vs. $0.94 consensus (+17%) — down YoY only because of a comp against last year's $110.5M Nevro bargain-purchase gain, not operating deterioration; non-GAAP diluted EPS $1.34, +55.8% YoY and ~22% above consensus. Adj. EBITDA margin expanded 740bps to 35.4%. US Spine +7% (5th straight quarter of above-market growth); base business ex-Nevro +9%. FY2026 non-GAAP EPS guidance raised to $4.95–$5.05. This is GMED's first earnings print since it entered the portfolio (8/2) — a clean first read on the position.
   Sources: [Globus Medical press release](https://www.globenewswire.com/news-release/2026/08/06/3340797/0/en/globus-medical-reports-second-quarter-2026-results.html), [StockStory](https://stockstory.org/us/stocks/nyse/gmed/news/earnings/globus-medical-nysegmed-beats-q2-cy2026-sales-expectations)

6. **SNDK — F4Q FY2026 earnings (2026-08-05) — MATERIAL, triggers rule-9** 📊
   Revenue $8.97B, beat consensus (~$8.3–8.4B) by ~7–8%. Non-GAAP diluted EPS reported inconsistently across sources ($39.25 most common, one outlet reported $43.97 — **flag: verify against SanDisk's own release before entering into the Watchlist**); beat magnitude roughly 13–18% vs. consensus depending on which figure is used. Data-center revenue more than doubled sequentially to ~$3.0B (38% of bits); FY grew 437% to $5.15B. Eight strategic customers signed "New Business Model" agreements locking in **$93.9B** in minimum revenue at floor pricing (weighted avg 4+yr duration); >50% of FY27 supply already committed, ~2/3 by FY28. **Despite the beat, shares fell ~5–8% after hours** on investor concern about how long the memory-price cycle can run; CEO Goeckeler said PC/smartphone unit shipments should decline in 2026 but sees stabilization + rising avg. storage capacity supporting exabyte demand growth. On the Meta-NAND-deal thread specifically: no new confirmation found in-window (the original leaked-memo confirmation was ~7/13–7/18, pre-window).
   Sources: [SanDisk IR press release](https://investor.sandisk.com/news-releases/news-release-details/sandisk-reports-fiscal-fourth-quarter-2026-financial-results), [Benzinga](https://www.benzinga.com/markets/tech/26/08/60981164/sandisk-ceo-david-goeckeler-pc-smartphone-sales-nand-recovery)

7. **EME — Q2 2026 earnings (2026-07-30, just outside window) — FLAG, unrefreshed**
   Revenue $5.15B (record, +19.8% YoY, ~+9% vs. consensus); diluted EPS $9.06–9.09 vs. ~$7.23–7.25 consensus (~+25% beat). FY2026 revenue guidance raised to $20.0–20.5B (from $18.5–19.25B); diluted EPS guidance raised to $32.00–33.25 (from $28.25–29.75). Record RPOs of $17.14B; stock jumped ~18.6% premarket. **This print fell one day before the scan window and EME's Watchlist "Last Updated" is still 2026-07-16 — unlike FIX/MSFT/META, this earnings beat has not yet been captured in objective inputs**, and EME is a current portfolio holding. Recommend prioritizing in the next network-capable refresh.
   Sources: [BusinessWire](https://www.businesswire.com/news/home/20260730052970/en/EMCOR-Group-Inc.-Reports-Second-Quarter-2026-Results)

8. **6861.T (Keyence) — Q1 FY2027 results (2026-07-28, just outside window) — captured**
   Net sales +32.8% YoY to ¥346.6B (beat estimate ¥328.0B); operating profit +44.7% to ¥187.1B (beat ~13%); net income +51.0%. Gross margin 85% (+240bps), operating margin 54% (+450bps). Falls before the window, but Keyence's Watchlist "Last Updated" is 2026-08-02 (after this print) — already reflected, no action needed.
   Source: [Keyence FY2027 Q1 results](https://www.keyence.co.jp/pdf/FinancialResults_202607_en.pdf)

9. **META — AWS succession follow-through (2026-08-01) — MATERIAL**
   AWS named Dave Treadwell (27-yr Microsoft veteran) to run AWS's compute/ML unit, completing the succession after Dave Brown's departure to Meta to build "Meta Compute" — confirms the Brown-to-Meta move (first reported 7/18, pre-window) is proceeding as of this window. Separately, the AI-layoffs discrimination lawsuit against Meta has a preliminary-injunction hearing set for 8/24 (Meta's response due 8/10) — both dates fall after this window, flagged for next week's scan, nothing new to report yet.
   Source: [GeekWire](https://www.geekwire.com/2026/departing-aws-exec-dave-brown-is-reportedly-joining-meta-as-facebook-parent-mulls-its-own-cloud/)

No material items found in-window for **CRDO, MSFT, or AVGO** specifically (CRDO: no earnings this window, unexplained ~9% share move on 8/4 flagged rather than fabricating a cause; MSFT: only routine India-DC activation + analyst PT catch-up post-7/29 print, already refreshed 8/2; AVGO: the Samsung ITC case and the OpenAI "Jalapeño" financing overhang both remain open but had no confirmed in-window procedural update — AVGO's next earnings report is 8/29, outside this window).

### Layer 10 SaaS Watch: PLTR, DDOG, CRM (net revenue retention, AI-feature adoption, pricing)

- **PLTR — Q2 2026 (2026-08-03):** Revenue $1.935B (+93% YoY, beat by ~$123M); adj. EPS $0.41 vs. $0.35 est.; US commercial revenue $764M (+149% YoY); FY26 guidance raised to $8.16B (from ~$7.65–7.66B). Stock jumped ~30% (8/4) before a ~9% pullback (8/5–8/6) on valuation concerns (trailing P/E ~139x) and a UK press report that Palantir paid only £2M UK corporation tax on £247M UK revenue. **NRR: net dollar retention rose to 157% in Q2, up 700bps from 150% in Q1** — a genuine expansion signal, not a pricing-model shift. No AI-native competitive-loss or pricing-pushback signal found.
  Sources: [CNBC](https://www.cnbc.com/2026/08/03/palantir-pltr-earnings-q2-2026.html), [Intellectia.ai](https://intellectia.ai/blog/pltr-q2-2026-earnings-93-percent-revenue-growth)

- **DDOG — Q2 2026 (2026-08-06):** Revenue $1.12B (+36% YoY, beat $1.08B consensus); non-GAAP EPS $0.65 vs. $0.58 est.; operating margin 23% (up from 20%); $100K+ ARR customers ~4,720 (+23% YoY); FY26 guidance raised to $4.45–4.47B. **Stock fell ~16–19% despite the beat-and-raise**, driven by (a) Q3 guidance implying deceleration to 28–29% YoY vs. 36% in Q2, and (b) a disclosed usage reduction from Datadog's **largest customer** — a nine-figure, 17-product AI-company account widely believed by analysts to be OpenAI — starting Q3 despite a recent contract renewal; management called guidance "fully de-risked" around it but did not disclose the cause. **This is the sharpest disruption-thesis-relevant data point of the week for the R5 cohort**: an analyst directly asked on the call whether Bits AI automation reduces the telemetry volume driving consumption-based billing (the core disintermediation-risk question); CEO Pomel pushed back, arguing AI integrations (now 80% of ARR) drive *more* usage, not less. **Flag: could not verify whether the large-customer pullback is AI-substitution-driven or unrelated (cost optimization, workload shift) — reporting is speculative on cause, not confirmed.**
  Sources: [Datadog press release](https://www.globenewswire.com/news-release/2026/08/06/3340086/0/en/Datadog-Announces-Second-Quarter-2026-Financial-Results.html), [Seeking Alpha](https://seekingalpha.com/news/4628234-datadog-projects-fy-2026-revenue-of-4_45b-4_47b-while-derisking-guidance-for-its-largest), [GuruFocus call highlights](https://www.gurufocus.com/news/9014386/datadog-inc-ddog-q2-2026-earnings-call-highlights-revenue-surges-36-to-112b-aidriven-growth-accelerates)

- **CRM:** US Army Human Resources Command deployed Agentforce (via Missionforce National Security) in Salesforce's IL5 environment (8/5) — first DoW org on the newly authorized Agentforce Public Sector, targeting 24/7 AI support for 9.2M soldiers/veterans/families. Separately, an 86-person WARN layoff in San Francisco (8/7, third round since Sept 2025) — company continues to attribute efficiency gains to Agentforce absorbing inbound support volume. **Pricing:** Agentforce now runs three simultaneous pricing models ($2/conversation, Flex Credits at $500/100K, and $125/user/month seat licensing) — commentary frames this as reflecting genuine difficulty translating agentic usage into a predictable bill; some service-engineer deployments report ~10% seat-count reduction as AI increases per-agent efficiency (**sourcing on the pricing-model detail could not be confirmed as in-window — treat as contextual color on the already-known Agentforce shift, not a new dated item**). No new NRR disclosure this window (next fiscal-Q2 report is late Aug/early Sept).
  Sources: [Salesforce Newsroom](https://www.salesforce.com/news/press-releases/2026/08/05/us-army-hrc-agentforce-ai-powered-support/), [WARN Tracker](https://www.warntracker.com/layoff/salesforce-2026-08-07)

### Other watchlist names — highest-materiality items

Given the volume this week (peak earnings season), this section curates M&A, financing, leadership, legal/regulatory, and major capacity/customer-deal items only; routine beat-and-raise earnings prints with no distinct strategic angle are in the collapsed routine section below.

**M&A / divestitures:**
- **ATKR** — definitive agreement to be acquired by Prysmian S.p.A. for $95.00/share cash (~$3.8B EV), announced alongside a Q3 beat (8/2–8/3); shares +26.6% premarket.
- **BWXT** — definitive agreement to sell BWXT Medical + Kinectrics' medical-isotopes business to Nordic Capital for up to $800M, retaining a minority stake (8/3).
- **IREN** — completed acquisition of Mirantis Inc. (~12.6M IREN shares + ~$40M cash) to add a software layer to its AI Cloud platform (8/4).

**Major capacity / customer deals:**
- **NRG** — landmark 1.2 GW "bring-your-own-power" hyperscaler data-center deal, expandable to 2.4 GW (~$500M annual EBITDA at full operation), disclosed alongside Q2 results (8/4); shares fell 9.3% premarket on the mixed earnings print despite the deal.
- **LEU** — signed a definitive LEU/HALEU supply agreement with X-energy for Xe-100 SMRs and TRISO-X fuel (deliveries from 2030), expanding Centrus's enrichment backlog to $3B (8/5).
- **BTDR** — 16-year, ~$4.7B colocation agreement at its Tydal, Norway campus (121MW IT capacity, NVIDIA GPUs) with Volta (8/4).
- **CLSK** — first-ever HPC data-center lease: ~$6.6B contracted revenue over 20 years, 175MW facility, capacity starting late 2027 (8/6).
- **HUT** — closed $7.5B of fully-amortizing investment-grade project financing; contract portfolio scaled to ~$26.6B across 949MW (Q2 print, 8/4).
- **CIFR** — $810M project financing closed for its Stingray site; portfolio scaled to ~5.3GW across 11 sites (8/4).
- **CRWV** — new Leidos Holdings partnership bringing CoreWeave Federal's AI cloud into US defense/intelligence data centers; stock +20% (8/4).
- **SHAZ** — two large take-or-pay contracts disclosed with Q2 results: $1.32B/5-yr New Zealand expansion with a global AI lab, and $373M/5-yr for 2,048 NVIDIA B300 GPUs (8/6).
- **TE (T1 Energy)** — new contract to supply Clearway Energy Group with 641MW of domestic solar cells/modules (8/3).
- **ONDS** — subsidiary Mistral Inc. secured a >$50M add-on Army order under the existing $982M Lethal Unmanned Systems IDIQ (8/5).
- **KTOS** — awarded a US Army DEVCOM C5ISR contract for a next-gen "Enhanced Seeker" for the Javelin missile system (8/6), alongside a Q2 beat and raised FY guidance.
- **AEVA** — launched a new Optical Connectivity business (AI-datacenter optical source tech) with its first hyperscaler customer agreement signed (8/5).
- **DELL** — named technology provider on Volta's $10B, 133MW AI-factory deal in Norway (8/4).
- **SO (Southern Company)** — priced/upsized $2.73B in convertible senior notes to retire costlier debt (8/3–8/6).
- **PWR** — priced $2.0B senior notes offering across three tranches, closing 8/6.
- **ASX** — priced $1B zero-coupon convertible bond due 2031; shares fell ~6% on the pricing (8/3).

**Legal / regulatory:**
- **PANW** — China's Cyberspace Administration opened a formal cybersecurity review of PANW's China-sold products (8/6), echoing the prior Micron review.
- **AAPL** — escalated its trade-secrets suit against OpenAI, filing for a preliminary injunction and expedited discovery; disclosed an internal probe identified 11 additional ex-employees who may have leaked confidential data (8/4).
- **PLAB, PRCT** — multiple securities class-action filings this window (8/3–8/6) on both — PLAB tied to a May stock drop (IC photomask demand disclosure), PRCT tied to an ~18% decline on alleged undisclosed excess customer inventory / late-quarter bulk-discount "sales pull-in."
- **GOOGL** (recent former holding, exited 8/3) — sweeping AI leadership overhaul (8/5): Chief Scientist Jeff Dean departed after 27 years to co-found an Alphabet-backed startup; Demis Hassabis stepped back to Chair of DeepMind. Shares fell as much as 5% intraday, ~$190B in market value briefly erased.
- **AMZN** (recent former holding, exited 8/3) — Jeff Bezos filed to sell ~15M shares (~$4.07–4.8B) under a pre-existing 10b5-1 plan (8/4); same day, the NJ Attorney General filed an antitrust suit alleging Amazon controls pay/working conditions for Delivery Service Partner contractors.

**Leadership:**
- **CEG** — board chair Robert Lawless retired after 20+ years (Joe Dominguez became chairman); Roger Crandall (MassMutual chairman/CEO) appointed independent director (8/4–8/5) — alongside a Q2 beat, 920MW of new nuclear PPAs, and the $860M sale of the Brazos Valley Energy Center to LS Power.
- **TT (Trane Technologies)** — SVP & Chief Global Integrated Supply Chain Officer Mingxiao Guo departed under a separation agreement, company states no disagreement over operations/policy/controls (8/1).

**Notable misses / stock-reaction items (>15% or otherwise flagged):**
- **CCJ (Cameco)** — Q2 adj. EPS missed by ~55% (absence of prior-year Westinghouse Dukovany contribution); shares still rose 4.3% premarket on a revenue beat.
- **VPG** — Q2 EPS $0.04 missed $0.19 est. by ~79%; stock fell ~27% in a session despite a 7th straight quarter of book-to-bill ≥1.0.
- **TNC (Tennant)** — Q2 non-GAAP EPS 37.6% below consensus; stock fell sharply.
- **MTZ** — cut full-year Communications revenue guidance by ~$400M; stock -17.7% the session after its (pre-window) print.
- **OKLO** — Groves isotope facility reached first criticality (~11 months from groundbreaking, described as the fastest privately-funded greenfield-to-criticality transition), alongside Q2 results showing $3.0B cash on hand (8/5–8/7).
- **TSLA** — WSJ reported Tesla is weighing separation of its China business ahead of a possible Tesla–SpaceX merger (7/31); Tesla and SpaceX confirmed a $16.8B Phase 1 investment in the "Terafab" AI-chip complex in Texas (up to $119B total potential cost across phases) (8/6–8/7).

---

## 📊 Earnings Refreshed (Rule #9)

| Ticker | Reported | Beat/miss magnitude | Objective refresh status |
|---|---|---|---|
| **ANET** | 2026-08-04 | Rev +5.9%, EPS +13.3%, FY raised ~40% growth | **BLOCKED** — network-blocked this session. 📊 top priority: first $3B quarter, not yet reflected in score. |
| **GMED** | 2026-08-06 | GAAP EPS +17%, non-GAAP +22%, guidance raised | **BLOCKED** — same. 📊 priority: first print since 8/2 portfolio entry. |
| **SNDK** | 2026-08-05 | Rev +7-8%, EPS +13-18% (source inconsistency flagged), stock fell on outlook | **BLOCKED** — same. 📊 priority. |
| **EME** | 2026-07-30 (pre-window) | Rev +19.8%, EPS +25% | **BLOCKED, and still not captured** — Watchlist "Last Updated" is 2026-07-16, unlike FIX/MSFT/META. Now a portfolio holding — flag for immediate priority once network resumes. |
| **6861.T** | 2026-07-28 (pre-window) | Rev +32.8%, op. profit +44.7% | **Already captured** — Watchlist refreshed 2026-08-02, after this print. |
| **MSFT** | 2026-07-29 | — | **Already captured** — refreshed 2026-08-02. |
| **META** | 2026-07-29 | — | **Already captured** — refreshed 2026-08-02. |
| **FIX** | 2026-07-23/24 | — | **Already captured** — refreshed 2026-07-27. |

**TTM vs. MRQ check:** not computable this pass for ANET/GMED/SNDK/EME — no fresh yfinance pull was possible. Given all four show accelerating or beat-driven quarters, flag per rule 9c that TTM-based Quality metrics are more likely than usual to understate the current run-rate for these names once refreshed.

**Broader tail-name rule-9 bucket-1 triggers (>15% beat/miss magnitude, immediate-refresh threshold):** a large number of non-holding watchlist names also crossed this threshold this week — **AEIS** (+24%), **ACLS** (+24.7%), **LSCC** (+20%), **SEI** (+25.7%), **KLIC** (rev +123% YoY, EPS +19.2%), **ALAB** (Q3 guide ~44-49% above consensus), **CGNX** (+80% YoY), **ALNT** (+30.6%), and on the miss side **CCJ** (-55%), **VPG** (-79%), **TNC** (-37.6%), **OUST** (~-35%). All are equally network-blocked this session. Recommend a batch `scripts/refresh_objective_inputs.py` (or `/refresh-objective`) run across the portfolio-priority names first (ANET, GMED, SNDK, EME), then this bucket-1 tail list, from a network-capable session.

---

## 💼 Portfolio Pipeline

```
$ python3 scripts/refresh_targets.py --check
Targets reflect current scores ✓
```

No membership or tier change fired — expected, since this check runs against the **current (stale) Watchlist scores**, and ANET/GMED/SNDK's earnings beats above are not yet reflected in objective inputs (network-blocked). Once those refresh, ANET in particular (first $3B quarter, guidance raised ~40%) is a plausible candidate for a score move worth re-checking for a tier effect.

**50DMA refresh:** blocked by yfinance egress (unchanged every session this cycle) — last-known values stand, not refreshed this pass.

**Weekly performance mark** (from `tracking/performance-series.json`, maintained by network-capable `daily-refresh.yml` CI; latest close 2026-08-06 — 2026-08-07 close not yet available):

| Period | Model | SMH | QQQ | SPY | EW Universe |
|---|---|---|---|---|---|
| This window (7/31 → 8/6) | **+2.40%** | +5.73% | +3.88% | +2.88% | +3.54% |
| Since inception (5/26) | **+0.93%** ($10,093.43) | −5.09% | −2.03% | +2.66% | +3.73% |

The model gained ground this window but **underperformed all four benchmarks** on a window basis, and remains behind SPY and the equal-weight universe since inception (though ahead of SMH and QQQ). Not a thesis break — no fundamental deterioration surfaced this scan for any holding; the strong holdings-level earnings news this week (ANET, GMED, SNDK) is a tailwind the mark doesn't yet reflect since objective refresh is blocked. Per project rules, this is not a trade recommendation.

**Concentration flag (current 13-name portfolio, allocations from the 2026-08-03 Targets snapshot):** Layer-06 AI Compute Silicon (NVDA 10.83% + MU 8.93% + AVGO 7.09% + SNDK 6.66% ≈ **33.51%**) remains the largest single-layer concentration, no cap active. Layer-07 Optical/Networking (CRDO 8.42% + ANET 7.65% ≈ 16.07%) and the new Layer-11 Robotics exposure (GMED 6.8% + 6861.T 5.76% ≈ 12.56%) are the next-largest blocks.

---

## 🔬 Rating Integrity (Rule #12)

```
$ python3 scripts/audit_rating_integrity.py --summary
rating-integrity (all layers): 211 rated names | 0 UNGATED (no thesis) | 0 stale (>90d)
```

Clean — no gate violations, no stale (>90d) ratings.

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
<summary>Expand for the full list (confirmed in-window, non-material — dividends, routine buybacks, analyst PT changes without new information, earnings-date-only announcements, and beat-quarters without a thesis-relevant angle beyond the sector-wide AI-capex theme already noted above). A large fraction of the watchlist reported Q2 earnings just before this window (7/28-7/30) — those prints are omitted here entirely as out-of-window, not silently treated as "nothing happened."</summary>

**Power/Utilities:** BE (Q2 call, guidance raised to $3.4-3.8B, but also securities-class-action investigations after a China-supply-chain-disclosure stock drop); D (Q2 results, reaffirmed guidance); DUK (Q2 beat, $5-10B incremental capex upside flagged from data-center demand); SO (Q2/notes above); NEE (Virginia Gov. Spanberger to intervene in the Dominion-NextEra merger review); PPL (Q2 adj. EPS missed ~6%, guidance reaffirmed); VST (Q2 8-K, reaffirmed guidance, up to $1B "Helix Digital Infrastructure" initiative); TLN (Q2 beat, raised FY26 and 2027/28 outlooks); CCJ (above); LEU (Q2 beat alongside the X-energy deal above); BWXT (Q2 beat, record backlog, alongside the medical-business sale above); SMR (Q2 results, $1.9B cash, Paragon HIPS contract); OKLO (above); CMI (Q2 miss ~7%, stock -8.2%, but raised FY revenue guidance on data-center standby-power demand); ETN (Q2 beat, raised guidance, small AFRL quantum-computing grid-security contract); HUBB/ABBNY/SBGSY/HTHIY — no in-window items beyond analyst-rating catch-up. AEP, ETR, XEL, GNRC, RRC, AR, EXE, EQT, UEC, NNE, PLUG, BW, PSIX — Q2 prints or routine items, no distinct in-window thesis angle beyond the sector-wide theme.

**Grid/DC construction/cooling:** ETN (above), PWR (above), NVT (Q2 beat, new Blaine MN liquid-cooling facility lease, several exec appointments), POWL (Q3 record orders on data-center demand inflection), ATKR (above), EQIX (Q2 beat pre-window; new All Nippon Airways cloud-hub partnership), IRM (Q2 beat, raised guidance), TT (Q2 beat pre-window, exec departure above), CARR/JCI/ASML/AMAT/DLR/MOD — Q2 prints or routine items pre-window, no distinct in-window angle.

**Semi-equipment/materials:** ONTO (Q2 record revenue/backlog), KLIC (above), ENTG (Q2 beat + new board member), PLAB (securities class actions above), UCTT (Q2 swing to profit + new CFO), GFS (Q2 beat), TSEM (Q2 beat, silicon-photonics ramp), COHU (Q2 beat, raised FY guidance), 5347.TWO (Q2 beat, slowing Q3 shipment guide), AEIS/ACLS/LSCC (above) — all beats, no distinct angle beyond the theme. LRCX, KLAC, TOELY, TER, CAMT, MKSI, CDNS, ARM, INTC, UMC, ASML, AMAT — no in-window items (earnings pre-window or not yet reported).

**Fabs/foundry:** ASX (above, plus a Q2 beat pre-window), HHUSF, 0981.HK — no distinct in-window items.

**EDA/IP/silicon:** MRVL (unveiled next-gen AI memory/storage portfolio at FMS 2026, $250M India investment plan), ALAB (above), SNPS/CDNS/TXN/QCOM/ADI/STM/NXPI/MCHP/SWKS/NVTS — no distinct in-window items beyond routine analyst activity.

**Optical/networking:** COHR/LITE/FN (pre-earnings rallies on sector-wide 800G/1.6T sentiment, no discrete dated item), AAOI (Q2 beat, 5th consecutive record quarter, Pearland TX expansion), POET (board refresh), CIEN (WaveLogic 6/Toshiba QKD live-network trial, stock +17.3%), APH (2-for-1 stock split approved), TEL/GLW/CSCO — routine only.

**Servers/storage:** SMCI (no new items in-window), DELL (above), HPE (routine dividend), WDC (Q4 beat, EPS +8.87%), NTAP (all-time-high stock, no discrete driver), P (formerly PSTG, no items).

**Cloud/neocloud/BTC-to-AI:** ORCL (Q2 cloud partnership expansion, Gemini/Fusion integration, stock +9.2%), NBIS (no in-window items, stock down pre-earnings), APLD (Q4 results, stock +17.5%), CORZ (major shareholder 13D/A stake reduction from 8.1% to 4.4%), IREN (above), CIFR (above), CLSK (above), BTDR (above), HUT (above), RIOT (rescheduled its earnings call with no new date given — atypical, worth watching), WULF (Q2 revenue down 6% YoY, wide net loss), KEEL (no in-window items, earnings due 8/10), SNOW (product GA releases only), NOW (routine leadership/office announcements).

**Software/SaaS (Layer 10, non-focus names):** APP (Q2 beat, buybacks), FTNT/ADBE/INTU/WDAY/ADSK/ZS (no distinct in-window items; ZS named a Gartner MQ Leader), CRWD/MDB/PATH/AMBA/CEVA/AIP (no in-window material items), TSLA (above), AAPL (above), TEM (new multimodal cancer-diagnostic model), HOOD (Q2 beat, UK FCA crypto authorization), RDDT (whipsawed on analyst PT cuts post-earnings), SPCX (first major post-IPO share-lock-up expiration, 911.5M shares eligible).

**Robotics/foreign/misc (Layer 11 and others):** SERV (Q2 revenue +400%+), PRCT (Q2 beat but securities class actions + downgrade on demand softness above), SSII (new CFO), TNC (above), 6954.T/Fanuc (Q1 in-line revenue, shares -9.9% on the week), 6268.T/Nabtesco (net income +120% YoY), TKR (Q2 beat + 2 EVP appointments), RRX (Q2 beat, data-center-driven Automation & Motion Control segment), NOVT (Q2 beat but shares fell despite it), VPG (above), CGNX (above), OUST (above), AEVA (above, plus CFO departure), MBLY/KTOS/AVAV/RCAT/ONDS/UMAC/DRO.AX/PDYN (mix of Q2 beats/misses and contract awards, see above for the material ones), ALGM/MELE.BR/BSL.DE (BSL.DE raised FY guidance on H1 beat, flagged a Sony image-sensor supply disruption risk), 2252.HK/2498.HK/6324.T/6481.T/2049.TW/6506.T/6383.T/AUTO.OL/KGX.DE/2590.HK/HSAI/9880.HK — no confirmed in-window material items (several have earnings scheduled in-window or just after, not yet locatable — candidates for next week's follow-up).

</details>

---

## New 13F Activity

None. Per the 2026-07-03 scan's confirmation across all six tracked funds (Berkshire Hathaway, Baillie Gifford, Tiger Global, Coatue Management, Whale Rock Capital, Lone Pine Capital), Q2 2026 13F-HR filings are not due until **August 14, 2026** — no activity expected in this window. Not independently re-verified this week (SEC EDGAR network-blocked), but the due-date logic is unaffected by the network state.

---

## Action Items for Dom

| Priority | Action |
|---|---|
| 🔴 | **ANET, GMED, SNDK all reported Q2 earnings beats this window and this session cannot refresh their objective inputs** (SEC/yfinance egress blocked). ANET's first-ever $3B quarter + ~40%-growth guidance raise is the highest-value refresh — recommend `/refresh-objective ANET,GMED,SNDK` (or `/earnings-update` per name) from a network-capable session, then re-check `refresh_targets.py` for a tier/reweight effect. |
| 🔴 | **EME's 7/30 Q2 beat (record revenue, EPS +25%) has still not been captured in objective inputs** — its Watchlist "Last Updated" is 2026-07-16, unlike FIX/MSFT/META which all got the same-week treatment. Now a portfolio holding since 8/2; recommend folding into the same refresh batch above. |
| 🟡 | **DDOG's Q2 print is the sharpest Layer-10 disruption-risk data point in weeks**: beat-and-raise but stock fell ~16-19% on guidance deceleration plus an unexplained usage pullback from its largest customer (widely believed to be OpenAI) despite a recent renewal. Cause unconfirmed (AI-substitution vs. cost optimization) — worth a `/refresh-context DDOG` pass to examine R5 against this concrete data point rather than mechanically re-rating on speculation. |
| 🟡 | **Michael Burry's NVDA/MU short positions moved from unconfirmed rumor to confirmed, sized bets this week** (NVDA puts + expanded MU short, 8/2), alongside fresh CXMT competitive-threat data (a second Beijing DRAM fab in early talks, plus independent confirmation CXMT's HBM output remains 1-2 generations behind on quality/cost). No fundamentals-level thesis break in either name, but worth holding the NVDA/MU/TSM China-competition thread together at the next Layer-05/06 review. |
| 🟢 | **A large batch of non-holding watchlist names (AEIS, ACLS, LSCC, SEI, KLIC, ALAB, CGNX, ALNT on the beat side; CCJ, VPG, TNC, OUST on the miss side) crossed the rule-9 >15% immediate-refresh threshold this week** — all equally network-blocked. Recommend a batch `/refresh-objective` pass once a network-capable session is available, after the portfolio-priority names above. |
| 🟢 | **This week's model mark: +2.40% window, +0.93% since inception ($10,093.43).** Underperformed all four benchmarks (SMH/QQQ/SPY/EW) on a window basis; still behind SPY/EW and ahead of SMH/QQQ since inception. Not a thesis break — the ANET/GMED/SNDK earnings tailwind isn't yet reflected in scores pending the blocked refresh above. |
| 🟢 | **ATKR (Prysmian, $3.8B) and BWXT-medical (Nordic Capital, up to $800M) were both acquired/divested this window** — neither is a portfolio holding, noted for the watchlist's M&A tracking. |
| 🟢 | **GOOGL's Jeff Dean/AI-leadership exodus (8/5, ~$190B market-value hit) and AMZN's Bezos $4B share sale + new NJ antitrust suit (both 8/4)** landed within days of both names' 8/3 portfolio exit — not actionable for the model, but notable given the timing. |
