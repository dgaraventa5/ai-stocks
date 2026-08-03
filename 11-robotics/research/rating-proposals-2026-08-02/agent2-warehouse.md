All five briefings are written. Summary of the work and the ratings.

## What was done

- Read the rubric, the Layer-11 decision record, and the warehouse sections of the segment research.
- Per-name fresh verification for all five (no sector shortcuts), including direct EDGAR work on SYM: parsed the full Q2 FY2026 10-Q and **all 86 Form 4/4A filings from 2025-08-02 to 2026-08-02**, and text-extracted Daifuku's Q1 FY2026 presentation PDF.
- Wrote `per-stock/{TICKER}/context-2026-08-02.md` for SYM, AUTO.OL, 6383.T, KGX.DE, 2590.HK with the five required sections and cited numerics.
- No .xlsx touched, no yfinance/Python market data run.

## Three findings that change the decision record

1. **SYM's "+255% YTD, crowded momentum" framing is wrong for 2026.** That Barchart figure is dated 2025-12-01. SYM closed **$42.94 on 2026-07-30, −31% over three months and ~−49% from the December-2025 high** (corroborated by Form 4 sale prices: ~$81–84 in Dec 2025 → $40–45 in Jul 2026). It is a broken-momentum name, not an extended one. Goldman cut its PT to $45 from $54.
2. **SYM's material weakness is still open.** The Q2 FY2026 10-Q states DCPs were **"not effective" as of 2026-03-28** due to the unremediated weakness in controls over *timing of cost-of-revenue recognition* — ~20 months after the restatement. Plus a second retrospective accounting-principle change (SBC attribution, −$44.1M APIC). The securities MTD was argued 2025-12-16 and is undecided. "Subpoena" returns zero hits in the 10-Q — flagged, not assumed resolved.
3. **Daifuku's "intralogistics orders +49.5%" is mislabelled.** That is the *"Other"* reportable segment, and Daifuku says its growth was "mainly in **cleanroom** systems." The actual warehouse end-market proxy — **Commerce/retail — saw orders fall 22% YoY**. Electronics is **46.1% of Q1 orders (+89%)**. Daifuku is a semiconductor-capex name first, a warehouse name second.

**Cross-cutting:** four of five score M2 = 1. The entire warehouse-automation cohort de-rated hard in 2026 while XLI ran **+17.4% YTD (to 2026-06-26) / +20% in H1**. That is a cohort-level observation, not five independent reads.

**Provisional per rule 9 — four of five report within 11 days:** SYM **Aug 5**, Daifuku **Aug 6**, AutoStore **Aug 13**, Geek+ H1 late August. Only KION has just reported (Jul 30).

---

## SYM — Symbotic

| Dim | Rating | Rationale | Source | Conf |
|---|---|---|---|---|
| D1 AI/Robotics Rev % | **5** | ~100% — "robotic based automation systems… move, store and sort cases and eaches in warehouses"; all three revenue lines are robotics systems/software/service | 10-Q Q2 FY2026 (2026-05-06), MD&A | High |
| D2 Supply Chain Position | **3** | Mid-chain systems integrator with real differentiation (case-handling density) but 22.2% gross margin and an 85%-of-revenue counterparty = the buyer holds pricing power; AutoStore/Dematic/Exotec/Vanderlande all viable | 10-Q Q2 FY2026 income statement + Significant Customers | Med |
| D3 Moat Strength | **3** | Genuine switching costs once a site is deployed and $22.7B contracted, but 22.2% GM proves price competition, and Amazon's captive robotics is a structural threat | 10-Q Q2 FY2026; FY2025 10-K backlog | Med |
| D4 Capacity Expansion | **4** | Systems in Deployment 70 vs 46 YoY (+52%), funded by $2.0B cash + $1.86B customer deferred revenue — but the binding constraint is deployment execution, and only ~14% of RPO converts in 12 months | 10-Q Q2 FY2026, RPO + MD&A | Med |
| D5 AI-Buildout Tie *(L11 lens, proposed)* | **3** | 100% robotics at scale, but the anchor is a **retailer**; demand is funded by retail labour economics, not AI-infrastructure capex. No hyperscaler or fab revenue | 10-Q Q2 FY2026, Significant Customers | Med |
| M1 EPS Revisions | **3** | Zacks consensus EPS unchanged over 30 **and** 60 days; Zacks Rank #3 (Hold) | Zacks/TradingView Q3 preview | High |
| M2 Rel. Strength vs XLI | **1** | −31% over 3 months (to $42.94, 2026-07-30) and −15.5% since the Q2 print, vs XLI +17.4% YTD → gap far beyond 20% | stockanalysis; Zacks via Yahoo; etfdb XLI | High |
| M3 Insider Activity | **3** | **Zero `P` codes across all 86 Form 4s in 12 months.** Sells are 10b5-1 programs or option-exercise sell-to-cover (routine per rubric); largest discretionary director sale ~14% of holdings (Ford), below the band-2 line → step-4 default | EDGAR CIK 1837240, 86 Form 4/4A parsed 2025-08-02→2026-08-02 | High |
| R1 Customer Concentration | **1** | Customer A (Walmart) = **84.5% of Q2, 85.0% of H1** revenue, >10% of AR; 85.9% a year ago. Rubric band 1 is >60% — mechanical | 10-Q Q2 FY2026, Significant Customers | High |
| R2 Geographic / Export | **5** | No legs. Revenue is essentially US/North America (Walmex and Exol are nascent). Worst plausible shock = Section 232 tariffs on imported components raising cost on fixed-price contracts — a *margin* risk, <10% of revenue geographically exposed | 10-Q Q2 FY2026; Manufacturing Dive on Section 232 | Med |
| R3 Balance Sheet | **5** | Cash **$2,009.4M**, no debt line on the balance sheet (zero hits on "convertible"); total liabilities $2,467.8M are operating, incl. $1,860.4M deferred revenue. Net cash ≈ full $2.0B | 10-Q Q2 FY2026 balance sheet | High |
| R4 Regulatory / Litigation | **2** | **Material weakness unremediated as of 2026-03-28, DCPs "not effective"**; *Decker/Traina* MTD argued 2025-12-16 and undecided; derivative suits consolidated | 10-Q Q2 FY2026 Items 1 & 4 | High |
| R5 Disruption Risk | **5** | Non-Layer-10 default; physical infrastructure | Rule 16 | High |

**DEBATABLE**
- **D4 = 4 vs 5.** A $22.7B contracted backlog with +52% deployment growth reads as "major buildout with customer commitments backing it." I held 4 because the constraint is execution pace — and slow deployment is literally what the securities suits allege.
- **R4 = 2 vs 1.** The unremediated weakness plus live class action is squarely 2. A 1 would require a disclosed enforcement action; the FY2025-Q3 subpoena disclosure has simply *disappeared* from later filings without a stated resolution. Flagged, not assumed closed.
- **M3 = 3 vs 2.** Rubric step 4 gives 3, and I applied it. But zero open-market buys across 86 filings during a 49% drawdown is the rubric's own "key question" answered in the negative — and SoftBank sold 9.09M shares (Dec 2025 + May 2026) down to 2.0M. A 2 is not supportable under the written procedure, but Dom may want the asymmetry noted.
- **D5 = 3 vs 4.** Deploying coordinated robot fleets for the world's largest retailer is arguably *the* physical-AI buildout. I judged the buildout-tie honestly per instruction: the funding source is retail capex.

---

## AUTO.OL — AutoStore

| Dim | Rating | Rationale | Source | Conf |
|---|---|---|---|---|
| D1 AI/Robotics Rev % | **5** | ~100% — cube-storage ASRS with robots on a grid; 1,900+ installations in 65+ countries | AutoStore company page; Q1 2026 results | High |
| D2 Supply Chain Position | **4** | IP/product owner selling modules through an integrator network; **72.7% GM sustained through a downturn** is a pricing-power signature; 2–4 credible substitutes (Exotec, Ocado, Dematic multishuttle) | Q1 2026 results (2026-04-23) | Med-High |
| D3 Moat Strength | **4** | Patent estate, the integrator ecosystem as a switching cost, 1,900 installed grids that expand incrementally, 44.0% adj. EBITDA margin. Capped at 4: Chinese tote-to-person entrants, and its largest integrator (Kardex) is a listed competitor | Q1 2026 results; segment research 2026-08-02 | Med |
| D4 Capacity Expansion | **3** | No disclosed multi-year capex program; +92.9% revenue is absorbing capacity built in the 2021–22 boom, and 2025–26 capital was spent **cutting debt and refinancing**, not expanding plant | Q1 2026 report; S&P upgrade note | Med |
| D5 AI-Buildout Tie *(L11 lens, proposed)* | **3** | Pure warehouse-automation beneficiary; CubeVerse/AutoStore Intelligence add an AI software layer on the installed base, but there is no AI-infrastructure or fab revenue tie | Robotics 24/7 on CubeVerse launch | Med |
| M1 EPS Revisions | **3** | No direct revision data located. Q1 was a large beat (+92.9% revenue) but order intake fell ~8% sequentially from Q4 2025's $194.2M, capping forward estimates — net neutral. **Flagged** | Q1 2026 + Q4 2025 releases | Low-Med |
| M2 Rel. Strength vs XLI | **2** | NOK 11.19 (2026-07-28); **underperformed FTSE Global All Cap by −6.28% over 6 months** → roughly +2–4% absolute vs XLI's ~+14% over the same window ≈ −10 to −12% gap | Investing.com AUTO; Simply Wall St; etfdb XLI | Med |
| M3 Insider Activity | **3** | **Default, flagged** — Norwegian issuer, outside the SEC Form 4 workflow; no primary-source insider data available | Rubric M3 sourcing rule | Low (flagged) |
| R1 Customer Concentration | **4** | 1,900+ installations across 65+ countries diversifies *end* customers, but revenue flows through a concentrated **partner channel** whose largest member (Kardex) is a competitor. **No disclosed >10% partner figure located — estimate** | Segment research 2026-08-02; company page | Low-Med (flagged) |
| R2 Geographic / Export | **4** | One leg, policy: worst plausible shock = a **US Section 232 tariff on imported robotics/industrial machinery** hitting European-built (Norway/Poland) ASRS shipped into its largest market. **% of revenue exposed NOT verified this session — rule-3 flag; the rubric's mandatory % is missing** | Manufacturing Dive; Mordor Intelligence on 15% steel-content tariffs | Low-Med (flagged) |
| R3 Balance Sheet | **4** | Net debt **$136M, 0.5x** net debt/adj. EBITDA (policy ceiling 2.0x); July-2026 maturities refinanced with a 5-yr $150M TLB + $350M RCF; liquidity $411M; **S&P upgraded to 'BB' stable** | Q1 2026 report; Investing.com/S&P | High |
| R4 Regulatory / Litigation | **4** | Routine; Ocado patent dispute understood resolved and nothing material surfaced. **Flag: I did not read the 2025 annual report legal section** | Web verification only | Med (flagged) |
| R5 Disruption Risk | **5** | Non-Layer-10 default | Rule 16 | High |

**DEBATABLE**
- **D4 = 3 vs 4.** Revenue +93%, product expansion into cold chain/SMB/case handling and a RaaS framework are a form of TAM expansion. I rated the capex reality, not the TAM.
- **R2 = 4 vs 5.** Without the Americas revenue %, this rating does not meet the rubric's mandatory "% of revenue exposed" requirement. It should be confirmed from the annual report before being trusted.
- **The +92.9% is off a depressed comp** (2024 revenue *fell* 4%). Growth inputs should not be extrapolated.

---

## 6383.T — Daifuku

| Dim | Rating | Rationale | Source | Conf |
|---|---|---|---|---|
| D1 AI/Robotics Rev % | **5** | ~100% of revenue is automated material handling / cleanroom transport systems across every reportable segment | Q1 FY2026 presentation (2026-05-14) p.7 | High |
| D2 Supply Chain Position | **4** | Global #1 in material handling **and** a dominant cleanroom OHT/AMHS supplier into fabs — an oligopoly with multi-year qualification cycles; capacity is the binding constraint (just added 30%). Blended down by competitive intralogistics | Q1 FY2026 presentation p.7, p.19 | Med-High |
| D3 Moat Strength | **4** | Fab AMHS is validated into customer wafer-transport flows (very high switching cost); 15.2% OPM and rising in hardware; service = 28% of sales. Airport/automotive (~24%) are lower-moat | Q1 FY2026 presentation p.3, p.13 | Med |
| D4 Capacity Expansion | **5** | New Shiga cleanroom factory completed **April 2026, +30% domestic cleanroom capacity** with a fab-replica test line; Tokyo Lab physical-AI R&D hub opened Mar 2026; record **¥700.2B backlog**; orders guided **+16–22%**. Funded from net cash | Q1 FY2026 presentation p.15, p.19, p.20 | Med-High |
| D5 AI-Buildout Tie *(L11 lens, proposed)* | **5** | **Electronics = 46.1% of Q1 orders (¥101.9B, +89%)**; Clean Factomation orders **+215%**, segment income ¥0.6B→¥3.3B. Daifuku's own words: "expansion in advanced semiconductor investments with increased demand for **AI applications**." This is a direct AI-capex tie, not an adjacency | Q1 FY2026 presentation p.7, p.10 | High |
| M1 EPS Revisions | **4** | **H1 forecast revised UP** at Q1 — sales +¥10.0B to ¥330.0B, OP +¥5.5B to ¥48.0B; FY held unchanged on external uncertainty. Consensus Buy (11 buy / 1 sell), target ¥7,487 vs ¥5,983 | Q1 FY2026 presentation p.15–16; stockanalysis | Med |
| M2 Rel. Strength vs XLI | **1** | ¥5,983 (2026-07-31) vs the **¥7,857 all-time high of 2026-05-11 = −23.9% in <3 months**; ~−7.6% over 6 months from ~¥6,472 — vs XLI +17.4% YTD. Both windows exceed a 20% gap | stockanalysis TYO:6383; Investing.com; etfdb XLI | Med |
| M3 Insider Activity | **3** | **Default, flagged** — Japanese issuer, no SEC Form 4 data | Rubric M3 sourcing rule | Low (flagged) |
| R1 Customer Concentration | **4** | Electronics is 41.4% of Q1 sales and necessarily concentrates into a handful of fab operators (TSMC/Samsung/SK Hynix/Micron), even if none exceeds 15%. **No disclosure located — estimate** | Q1 FY2026 presentation p.10 | Med (flagged) |
| R2 Geographic / Export | **3** | Two legs. Demand: **Taiwan 13.1% + South Korea 12.4% of Q1 sales (19.7% + 15.5% of orders) = ~25% shipped into strait-adjacent geographies.** Policy: **China 11.8% of sales**, orders −14% YoY, with a Suzhou production subsidiary. Worst plausible shock = a Taiwan contingency, directly ~13% of sales, with second-order exposure to the whole 41% electronics book | Q1 FY2026 presentation p.9–10 | Med-High |
| R3 Balance Sheet | **5** | Cash ¥251.8B; total liabilities ¥284.8B are mostly payables/contract liabilities; net assets ¥458.3B. Net cash confirmed by EV ¥2.01T < market cap ¥2.20T | Q1 FY2026 presentation p.8; stockanalysis | High |
| R4 Regulatory / Litigation | **4** | Routine; nothing material surfaced. **Flag: I did not read the yūka shōken hōkokusho legal section** | Web + IR materials only | Med (flagged) |
| R5 Disruption Risk | **5** | Non-Layer-10 default | Rule 16 | High |

**DEBATABLE**
- **M2 = 1 vs 2.** The 12-month picture is +53–57%, i.e. strong outperformance; the rubric's 3–6-month window is unambiguously negative. I rated the window as written rather than the story. My 6-month starting price (~¥6,472, late Feb) comes from a search snippet, so the 6-month gap has ±few-points uncertainty; the 3-month gap (−24% vs a rising XLI) does not.
- **R2 = 3 vs 2.** Daifuku has production assets in China (Suzhou) and Korea (Clean Factomation). Under a strict reading, an asset leg in a risk geography is band 2 (the TSM anchor). I held 3 because the Chinese subsidiary is ~5% of orders and serves China domestically.
- **D1 = 5** treats conveyance/storage/OHT automation as "robotics." That is the broad reading; a narrow "articulated/mobile robot" definition would score lower. Consistent with how the bucket was constructed.
- **Fiscal-year trap:** the year-end moved from March to **December**, with FY2024 an irregular transition period. Any yfinance TTM crossing that boundary is not comparable — verify Growth inputs against the tanshin.

---

## KGX.DE — KION Group

| Dim | Rating | Rationale | Source | Conf |
|---|---|---|---|---|
| D1 AI/Robotics Rev % | **4** | IAS (Dematic) = **EUR 861M of EUR 2,916M = 29.5%** of Q2 2026 revenue; FY2026 guidance implies ~29%. Band 4 is 25–50%, and this sits at the low end. **Flag: not all of IAS is robotics** (conveyors, sorters, software) | Q2 2026 slides (2026-07-30) | High on the number, Med on the definition |
| D2 Supply Chain Position | **3** | Top-3 warehouse integrator + top-2 forklift OEM, with real software/service differentiation and 47% service revenue — but 7.0% IAS and 8.8% ITS EBIT margins are a price-competitive project business | Q2 2026 slides | Med |
| D3 Moat Strength | **3** | Installed-base annuity is genuine (service = 47% of group revenue; EUR 2.95B IAS backlog), but a −40% order swing in one quarter shows the moat does not hold volume | Q2 2026 slides | Med |
| D4 Capacity Expansion | **2** | **Contracting, not expanding.** Explicit "order selectivity" declining low-margin deals; group orders −20%, IAS −40%, backlog flat, ITS revenue guidance upper end *lowered*, FCF −EUR 25M in Q2. Only a 70% bolt-on of Smart Innovation NV | Q2 2026 slides | Med-High |
| D5 AI-Buildout Tie *(L11 lens, proposed)* | **3** | Deepest *technology* tie in the segment — live Jetson-based autonomous trucks for GXO, Omniverse/Mega digital twins, AI Control Tower, with NVIDIA + Accenture — but it is capability, not AI-infrastructure revenue, and 71% of the company is forklifts | KION GTC 2026 press release; CXTMS; MHW Mag | Med |
| M1 EPS Revisions | **2** | FY2026 guidance **narrowed with the ITS revenue upper end lowered**; group orders −20% / IAS −40% set up cuts. Consensus target EUR 57.47 vs EUR 38.93 shows the Street has not yet marked to tape | Q2 2026 slides; stockanalysis ETR:KGX | Med |
| M2 Rel. Strength vs XLI | **1** | EUR 38.93 (2026-07-31), **−26.27% over 1 year**, near the 52-week low of EUR 35.80 against a EUR 70.45 high (−45%), vs XLI +17.4% YTD | stockanalysis ETR:KGX; etfdb XLI | High |
| M3 Insider Activity | **3** | **Default, flagged** — German issuer, no SEC Form 4 data | Rubric M3 sourcing rule | Low (flagged) |
| R1 Customer Concentration | **5** | Highly diversified — 69,100 truck orders in the quarter across a mass customer base, plus Dematic project customers; no customer near 15% | Q2 2026 slides | High |
| R2 Geographic / Export | **4** | One policy leg: **US Section 232 robotics/industrial-machinery tariffs** on European-built trucks and automation shipped into the Americas. Secondary: **Weichai Power's 46.5% Chinese control with Supervisory Board seats**, a live procurement question for US customers. **% of revenue by region NOT verified this session — rule-3 flag; the mandatory % is missing** | KION 2025 AR general information; Manufacturing Dive | Low-Med (flagged) |
| R3 Balance Sheet | **4** | Net financial debt EUR 1.244B, **0.6x LTM adj. EBITDA**; FY FCF guided EUR 420–540M. **Flag: this excludes the leasing/financial-services book and pension obligations; all-in leverage is likely higher, and net debt doubled from Q1's EUR 587M / 0.3x** | Q2 2026 slides | Med (flagged) |
| R4 Regulatory / Litigation | **4** | Routine; nothing material surfaced. Weichai control is a governance/related-party consideration, not litigation. **Flag: legal section not read** | Web verification only | Low-Med (flagged) |
| R5 Disruption Risk | **5** | Non-Layer-10 default | Rule 16 | High |

**DEBATABLE**
- **D4 = 2 vs 3.** "Steady-state capex with discipline" is a fair alternative framing; I rated 2 because order selectivity plus a European efficiency program is capacity *rationalisation*, and the forward book is shrinking. This is the rating most at odds with the "cheap optionality" narrative.
- **D1 = 4 vs 3.** If robotics is defined narrowly (AMRs/autonomous trucks/piece-picking rather than all of Dematic), the numerator falls below 25% and D1 drops to 3.
- **R2 = 4 vs 3.** Two legs (US import policy + Chinese controlling shareholder) would justify 3. I could not obtain the regional revenue split to size either — this rating should be re-derived from the FY2025 annual report.
- **My web-search budget was exhausted before I could retrieve KION's regional revenue table** (the Q1 press-release page returned no content and the H1 trade article returned HTTP 403). Flagged rather than papered over.

---

## 2590.HK — Geekplus (Geek+)

| Dim | Rating | Rationale | Source | Conf |
|---|---|---|---|---|
| D1 AI/Robotics Rev % | **5** | ~100% — AMR systems and related services; 72,000+ robots delivered across 40+ countries | FY2025 results (2026-03-30) | High |
| D2 Supply Chain Position | **3** | #1 global AMR share for 7 consecutive years, and a **46.6% non-domestic gross margin** says it is not competing purely on price abroad — but AMRs are the most contested corner of warehouse robotics, with dozens of Chinese and Western substitutes | FY2025 results; Interact Analysis via Robotics & Automation News | Med |
| D3 Moat Strength | **3** | Real service moat abroad (64+ service stations, 12 parts centres, 90+ new channel partners) plus 78% large-customer repurchase and 80+ F500 clients. Capped at 3: no IP barrier, brutal domestic ASP competition, and a geopolitical event could void it | FY2025 results | Med |
| D4 Capacity Expansion | **4** | Orders **CNY 4.137B, +31.7%** (book-to-bill ~1.30); international orders +40%, Americas +50%; subscription orders +90%; overseas service infrastructure scaling; funded by the HK$2.71B IPO | FY2025 results; Geekplus IPO release | Med |
| D5 AI-Buildout Tie *(L11 lens, proposed)* | **3** | 100% robot revenue with a Geek+ Brain embodied-intelligence platform, but demand is driven by e-commerce/labour economics, not AI-infrastructure capex. The humanoid/unmanned-warehouse plan has **no disclosed revenue** and earns no credit | FY2025 results; MODEX 2026 release | Med |
| M1 EPS Revisions | **3** | No revision data located. FY2025 beat into first positive adjusted profit and 13 buy / 0 sell with a HK$32.01 target vs a HK$9.62 price — targets have simply not been cut yet, which is not evidence of upward revisions. **Flagged** | Investing.com 2590; BigGo/Deutsche Bank | Low (flagged) |
| M2 Rel. Strength vs XLI | **1** | HK$9.62 (2026-08-02) against a 52-week range of HK$8.85–33.90 — **at the low, −72% from the high, −29% in 1 month, −35% in 3 months** vs XLI +17.4% YTD | Investing.com 2590; Simply Wall St; etfdb XLI | High |
| M3 Insider Activity | **3** | **Default, flagged** — HK issuer, no SEC Form 4 data. Context only: the **IPO lock-up expired 2026-07-09**; Zhongwan Hezhi and Vertex Ventures publicly committed to hold, which is management-friendly framing, not a supply guarantee | Rubric M3 sourcing rule; BigGo Finance | Low (flagged) |
| R1 Customer Concentration | **4** | ~950 end customers, 80+ Fortune Global 500, 78% repurchase rate — implies diversification. **The HKEX prospectus top-customer table was NOT verified this session; this is an estimate, not a disclosure** | FY2025 results | Low-Med (flagged) |
| R2 Geographic / Export | **2** | Both an asset leg and a live policy leg. **75.3% of revenue and ~80% of new orders are non-domestic**, produced entirely in China, into markets where the **US Commerce Department has an open Section 232 investigation into robotics imports** — while the Americas book (+50%) is the growth engine. Worst plausible shock = a US tariff or procurement ban on Chinese AMRs, exposing the majority of revenue | FY2025 results; Manufacturing Dive; The Robot Report | Med-High |
| R3 Balance Sheet | **4** | Post-IPO cash from the HK$2.71B raise; FY2025 operating cash flow **+CNY 85.7M** and adjusted net profit **+CNY 43.8M**, both first-ever positive. **Flag: FY2025 balance sheet not read; "adjusted" ≠ GAAP profitable** | FY2025 results; IPO release | Low-Med (flagged) |
| R4 Regulatory / Litigation | **3** | No material litigation surfaced, but only ~13 months of listed history under a thinner HKEX disclosure regime, and a newly-expired lock-up. Trade policy is scored in R2, not here | Web verification only | Low (flagged) |
| R5 Disruption Risk | **5** | Non-Layer-10 default | Rule 16 | High |

**DEBATABLE**
- **R2 = 2 vs 1.** If the Section 232 investigation produces tariffs or a procurement ban, the impairment becomes material and unmitigated across 75% of revenue — band 1. Today it is a threat, not an active impairment, so 2 is the correct present-tense read. This is the single rating most likely to move on news.
- **R1 = 4** is an estimate. The HKEX prospectus concentration table should be pulled before this is trusted; a project-based robotics vendor can be lumpier than a 950-customer count suggests.
- **D2/D3 = 3 vs 2.** A pure-commodity reading of AMRs would put both at 2. The 46.6% overseas gross margin and seven years of share leadership argued me up to 3.
- **The valuation gap is the story.** 13 buy / 0 sell with a HK$32 consensus target against a HK$9.62 tape is not a mispricing signal — it is analysts who have not marked to a geopolitical binary.

---

**Rule-3 gaps carried forward (nothing papered over):** KION's regional revenue split (search budget exhausted; blocks a rubric-compliant R2), AutoStore's Americas revenue % and partner concentration, Daifuku's and Geek+'s customer-concentration disclosures, and legal-proceedings sections for all four foreign filers.