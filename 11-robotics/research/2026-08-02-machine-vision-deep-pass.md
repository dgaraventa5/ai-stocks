# Machine Vision / Robot Perception — 2026 Candidate Roster (2026-08-02)

*Research agent deliverable (follow-up deep pass on machine vision & robot perception). Preserved verbatim as scoring evidence.*

I have what I need. Writing up the deliverable.

## Machine Vision / Robot Perception — 2026 Candidate Roster

**As-of 2026-08-02.** Market caps from yfinance pulled today; FX applied: JPY 0.006338, EUR 1.1547, SEK 0.1052, HKD 0.12753, CNY 0.14814, MYR 0.24492, KRW 0.00069544.

**Read the "Robotics %" column carefully.** Almost no company in this bucket discloses robotics or machine-vision revenue as a reported segment. Where a number is an estimate, it is marked `est.` and the reasoning is shown in the detail section. `n/d` = not disclosed and I refuse to invent one.

### Roster

| Ticker | Company | Mkt Cap (USD) | Robotics/Vision % rev | Verdict |
|---|---|---|---|---|
| **CGNX** | Cognex | $10.9B | 100% vision; robotics n/d | **INCLUDE** |
| **HXGBY** → HEXA-B.ST | Hexagon AB | $26.2B | ~19% Autonomous Solutions; AEON pre-revenue | **INCLUDE** |
| **OUST** | Ouster | $2.6B | ~100% perception; industrial/robotics majority | **INCLUDE** |
| **6861.T** ← KYCCF | Keyence | $124.7B | ~30–40% vision `est.` | **INCLUDE** |
| **ZBRA** | Zebra Technologies | $14.0B | ~5–8% machine vision `est.` | **BORDERLINE** |
| **NOVT** | Novanta | $5.1B | ~15–20% robotics `est.` (AET seg. 50.9%) | **BORDERLINE** |
| **TDY** | Teledyne | $30.4B | ~10% industrial vision `est.` | **BORDERLINE** |
| **BSL.DE** | Basler AG | $0.89B | 100% machine vision | **BORDERLINE** |
| **HSAI** | Hesai Group | $21.2B | robotics units +138%; % of rev n/d | **BORDERLINE** |
| **AEVA** | Aeva Technologies | $1.2B | ~100% perception; industrial real but tiny | **BORDERLINE** |
| **SONY** → 6758.T | Sony Group | $136.6B | I&SS 17.7%, mobile-dominated | **EXCLUDE** |
| **OMRNY** → 6645.T | Omron | $6.8B | IAB ~53%; vision a minority sub-line | **EXCLUDE** |
| **EMR** | Emerson Electric | $83.9B | T&M ~9%; not vision | **EXCLUDE** |
| **IPGP** | IPG Photonics | $3.6B | ~0% vision (laser co.) | **EXCLUDE** |
| **MVIS** | MicroVision | ~$0.25B | ~100% lidar, but ~$1M/qtr revenue | **EXCLUDE** |
| **LAZR** | Luminar | **$0 — equity cancelled** | — | **EXCLUDE** |
| **098460.KQ** | Koh Young Technology | $1.25B | ~100% 3D inspection | **INCLUDE** (new find) |
| **0097.KL** | ViTrox | $4.0B | ~99% machine vision | **INCLUDE** (new find) |
| **2498.HK** | RoboSense | $1.4B | ~100% perception; robotics ~50% | **BORDERLINE** (new find) |
| **TWEKA.AS** | TKH Group | $2.0B | Vision seg. 29.7%; MV ~20% `est.` | **BORDERLINE** (new find) |

---

## Three things that invalidate the brief as written

**1. `LAZR` is dead and the ticker has been recycled.** Luminar filed Chapter 11 on 2025-12-15 after losing its Volvo contract, was delisted from Nasdaq, and under the confirmed liquidation plan **all equity interests have been or will be cancelled without consideration and have no value** ([Investing.com/SEC filing](https://www.investing.com/news/sec-filings/luminar-technologies-completes-liquidation-plan-and-cancels-all-equity-interests-93CH-4599993); [Luminar IR](https://investors.luminartech.com/news-events/press-releases/detail/110/luminar-technologies-inc-initiates-voluntary-chapter-11)). Querying `LAZR` in yfinance today returns **"Tema Photonics & Optical ETF"** — the ticker was reassigned. Anyone screening on `LAZR` is now silently screening an ETF.

**2. yfinance's MVIS market cap is broken by a factor of ~40.** It reports `marketCap` $6,211,106 from `sharesOutstanding` 23,350,024 × price $0.266 — but it simultaneously reports `floatShares` 326,455,351. The 1-for-15 reverse split was effective 2026-08-01 with split-adjusted trading from 2026-08-03 ([MicroVision IR](https://ir.microvision.com/news/press-releases/detail/461/microvision-announces-reverse-split-of-common-stock-to)), so yfinance is multiplying the **post-split share count by the pre-split price**. True cap is ~$251M ([companiesmarketcap](https://companiesmarketcap.com/microvision/marketcap/)). **Do not let this row enter any scoring pass until yfinance reconciles** — it would score as a nano-cap with a 4x P/S.

**3. Hexagon is a different company than it was 3 months ago.** The Octave spin-off completed 2026-05-28, distributing Asset Lifecycle Intelligence, Safety, Geospatial, ETQ and Bricsys to shareholders ([Hexagon IR](https://investors.hexagon.com/share-information/octave-separation)). Any pre-May revenue or margin history for HXGBY is not comparable to the current entity. yfinance still shows `totalRevenue` EUR 5.467B, which is the **pre-spin** group — RemainCo is annualizing ~EUR 4.2B off Q2's EUR 1,050.2M.

---

## INCLUDE

### CGNX — Cognex Corporation
**US, $10.9B.** Currency: clean (USD/USD). Avg vol 2.42M shares/day.

**Vision exposure: 100%** — this is the only US-listed pure-play machine vision company of scale. Logistics, packaging, consumer electronics and automotive together were **~85% of 2025 revenue** of **$994.4M, +9%** ([10-K coverage](https://www.stocktitan.net/sec-filings/CGNX/10-k-cognex-corp-files-annual-report-562c341a84f7.html)). Individual end-market percentages are **not broken out**, and Cognex does **not** disclose vision-guided-robotics revenue separately.

**2026 thesis:** Cognex is mid-inflection, not pre-inflection. Q1 2026 revenue **$268M, +24% YoY (+21% cc)**, gross margin **71.1% vs 66.8%**, adjusted EBITDA margin **26.9% (+1,010bps)**, adjusted EPS **$0.34, +113%** ([Cognex Q1 2026 release](https://www.prnewswire.com/news-releases/cognex-reports-first-quarter-2026-results-302764643.html)). That is the **ninth consecutive quarter of double-digit growth**, led by large e-commerce logistics customers. The product cycle is the real story: In-Sight 6900 (NVIDIA-powered) and In-Sight 3900 (Qualcomm embedded AI) push AI inference to the edge camera, with CEO Matt Moschner explicitly targeting "**the #1 provider of AI-powered machine vision**."

**Red flags — and they are substantive:**
- **Zero robotics/humanoid content.** I read the full Q1 2026 call transcript ([Motley Fool](https://www.fool.com/earnings/call-transcripts/2026/05/07/cognex-cgnx-q1-2026-earnings-transcript/)) — there is **not one mention** of robotics, humanoid, or physical AI. If your thesis is humanoid perception content, Cognex does not currently articulate it. It is a factory/warehouse inspection company benefiting from AI capex, not a robot-perception company.
- Management guided logistics to **"normalize to mid- to high single digits"** in 2026 against tougher comps — the 24% print is the easy comp, not the run-rate.
- CFO Dennis Fehr: **"short-cycle business with limited visibility, especially for the second half."** Q2 includes **$7M of electronics orders pulled forward from Q3**.
- Valuation is full: forward P/E 36.6, P/S 10.4 (yfinance).
- **Q2 2026 reports 2026-08-05** — three days out. Guidance is $280–300M revenue (+16.5% at midpoint) and adjusted EPS $0.40–0.44. Under your rule 9 this name needs an objective refresh within a week regardless.

**Verdict: INCLUDE.** It is the definitional name for the bucket, the margin expansion is real and large, and the AI product cycle is documented. Just don't sell it internally as a humanoid play — it isn't one yet.

### HXGBY (map → HEXA-B.ST) — Hexagon AB
**Sweden, $26.2B.** **DOUBLE CURRENCY TRAP — flag hard.** yfinance: HXGBY `currency`=USD / `financialCurrency`=EUR, **and** HEXA-B.ST `currency`=SEK / `financialCurrency`=EUR. Neither listing is currency-consistent. Your rule-19 `ADR_LOCAL` map does **not** solve this one — the local listing is *also* a trap. You need the **general FX branch** (`ratios_via_fx`), converting the SEK market cap into EUR. Proof the trap is live: yfinance prints HEXA-B.ST P/S at **45.6** (SEK cap ÷ EUR revenue) versus HXGBY's 4.78. The 45.6 is garbage.

**Vision/robotics exposure:** Q2 2026 net sales **EUR 1,050.2M, +12% organic**, EBITAC margin **24.3% (+330bps ex-divestitures)**. Post-spin divisions: **Manufacturing Intelligence EUR 452.1M (+13% organic, 24.3% margin)**, Infrastructure & Geospatial EUR 388.5M (+4%), **Autonomous Solutions EUR 201.7M (+20% organic, 31.0% margin)** ([Investing.com Q2 2026 slides](https://www.investing.com/news/company-news/hexagon-q2-2026-slides-12-growth-portfolio-reshape-amid-stock-drop-93CH-4818998)). Autonomous Solutions is **19.2% of revenue** (201.7/1,050.2, my calculation) and is both the fastest-growing and highest-margin division.

**2026 thesis — this is the strongest genuine humanoid-perception story on the list.** AEON is a bipedal-with-wheeled-feet industrial humanoid carrying **two full AI computers, NVIDIA GPUs, two head cameras and 22 spatial sensors** ([Digital Engineering](https://www.digitalengineering247.com/article/hexagon-live-2025-industrial-robot-aeons-debut-the-launch-of-octave-and-more)). Crucially it has a **named anchor customer with a unit number**: on 2026-04-22 Schaeffler committed to deploy **at least 1,000 AEON humanoids across its global factory network over 7 years**, following a completed 2025 pilot, and Schaeffler simultaneously becomes Hexagon's **Tier-1 rotary actuator supplier** ([Hexagon press release](https://hexagon.com/company/newsroom/press-releases/2026/hexagon-schaeffler-deploy-aeon-humanoids-across-global-factory-network); [The Robot Report](https://www.therobotreport.com/schaeffler-plans-to-deploy-1000-hexagon-humanoids-2032/)). Additional pilots with BMW Group and Pilatus Aircraft. The differentiator versus Tesla/Figure is that Hexagon already owns the metrology sensor stack — AEON's pitch is automated part **inspection**, targeted for rollout **starting end-2026**.

**Red flags:**
- **AEON is a pre-revenue cost center.** Robotics cost **~EUR 10M in Q2 2026, ~EUR 50M for full-year 2026**, with commercialization only *targeted* by end-2026. You are funding the R&D, not clipping the revenue.
- **The stock fell 18.9% on the Q2 print** (to ~$95.70 from $118) despite the best operational quarter in five years — the market read the new **2026–2030 targets of 4–6% organic growth** as a deceleration from the 12% just delivered, plus concern over robotics burn and Waygate integration.
- Post-spin history is ~one quarter long. Comparables are broken.
- Schaeffler's 1,000 units over 7 years is ~143/yr — meaningful validation, immaterial revenue near-term.

**Verdict: INCLUDE.** Best risk-adjusted humanoid-perception exposure available: a profitable, 24%-margin metrology business paying for the option, with a named customer and a unit commitment. Underwrite it as a measurement company with a free humanoid call option — not as a robotics pure-play.

### OUST — Ouster, Inc.
**US, $2.6B.** Currency: clean. Avg vol 5.13M shares/day.

**Exposure: ~100% perception**, and after February the mix is genuinely robotics-weighted rather than automotive. Q1 2026 revenue **$49M, +49% YoY**, product revenue **+55%**, **13th straight quarter of product revenue growth**, gross margin **43%**, **$175M cash and no debt**, >12,600 lidar and camera units shipped ([Ouster IR](https://investors.ouster.com/news-releases/news-release-details/ouster-announces-results-first-quarter-2026)).

**2026 thesis:** Ouster bought **StereoLabs** (closed 2026-02-04, **$35M cash + 1.8M shares**; StereoLabs did **$16M unaudited 2025 revenue**) to bolt market-leading stereo cameras and AI vision software onto digital lidar ([Ouster](https://investors.ouster.com/news-releases/news-release-details/ouster-acquires-stereolabs-creating-world-leading-physical-ai); [TechCrunch](https://techcrunch.com/2026/02/09/lidar-maker-ouster-buys-vision-company-stereolabs-as-sensor-consolidation-continues/)). The result is a unified lidar + camera + sensor-fusion + perception-software stack — the closest thing to a merchant "robot perception platform" in public markets. Management cited **several million-dollar industrial-automation deals with companies building foundational AI models and advanced robotics platforms**. REV8/L4 silicon adds native colour lidar.

**Red flags:**
- **Loss is widening, badly.** Q1 EPS **-$0.28 against a -$0.12 consensus** — a >2x miss.
- **Gross margin guided DOWN** to 35–40% for Q2 from 43% — the industrial/robotics mix is dilutive to margin. Q2 revenue guided $49.5–52.5M, i.e. roughly flat sequentially after a +49% quarter.
- P/S 14.2 (yfinance) with profitability only "targeted within the next year."
- Only ~7 weeks of StereoLabs was in Q1 — the +49% is partly inorganic and the clean organic rate is not disclosed. **FLAG.**

**Verdict: INCLUDE** as the highest-beta perception name. The platform logic is sound and the balance sheet ($175M, no debt) buys time, but this is a speculative sleeve, not a core position.

### 6861.T (map ← KYCCF) — Keyence Corporation
**Japan, $124.7B.** **CURRENCY TRAP:** KYCCF `currency`=USD / `financialCurrency`=JPY. Map **KYCCF → 6861.T** per rule 19 — the Tokyo line is clean (JPY/JPY) and yfinance's clean forward P/E of 43.5 only appears on 6861.T (KYCCF returns `null`). KYCCF's P/S of 0.0976 is trap garbage.

**Vision % of revenue: ~30–40%, my estimate — flagged.** Keyence does **not** disclose a product-line revenue split. My reasoning: Keyence and Cognex together hold close to half the global machine vision market ([Averroes comparison](https://averroes.ai/blog/cognex-vs-keyence-vision-systems)), and Keyence's vision pillar sits inside a catalogue also spanning measurement sensors, microscopes, laser markers, safety and 3D printers. Cognex's ~$1B of pure vision revenue against a roughly equal Keyence vision share implies Keyence vision revenue in the ballpark of **$3–5B** against group revenue of ~$8B, i.e. 30–40% is a plausible band with wide error bars. **Do not treat this as a cited figure.**

**2026 thesis:** FY2026 (year ended March 2026) net sales **+10.4%**, net income attributable **¥445.2B, +11.7%**, operating income **+8.4%**, ROE 13.5%, **operating margin 51.0%** ([Globe and Mail](https://www.theglobeandmail.com/investing/markets/stocks/KYCCF/pressreleases/1514350/keyence-delivers-double-digit-profit-growth-and-hikes-dividend-on-strong-fy2026-results/)). A 51% operating margin in industrial hardware is close to unique — it reflects a direct-sales, no-distributor, consultative model that competitors have never replicated.

**DATA CONFLICT — FLAG.** The FY2026 release reports net sales of **~¥1.17 trillion**, but yfinance shows `totalRevenue` of **¥1,254.8B**. These do not reconcile. Likely a fiscal-period boundary issue (Keyence's FY ends ~March 20, so yfinance's TTM may straddle into FY2027 Q1), but I could not confirm. **Resolve against the primary tanshin before scoring.**

**Red flags:**
- **Valuation is the entire debate.** Forward P/E 43.5 and P/S 15.7 (6861.T) for a ~10% grower. Under your rule-21 reverse-DCF, this multiple implies growth well above the recent revenue trend — expect it to score poorly on the mispricing metric.
- **Robotics content is indirect.** Keyence sells vision sensors into automation broadly; it has no disclosed humanoid or robot-perception programme.
- **KYCCF liquidity:** 3,072 shares/day at ~$505 ≈ **$1.55M/day** notional. Workable in dollar terms but on Pink Sheets with wide spreads. Prefer 6861.T if you have Tokyo access.
- Operating income (+8.4%) grew slower than sales (+10.4%) — margin has begun to compress off the peak.

**Verdict: INCLUDE** as the quality anchor of the bucket. Best business economics in industrial technology, at a price that leaves no room for error.

### 098460.KQ — Koh Young Technology *(not on your list — the best new find)*
**South Korea, $1.25B.** Currency: clean (KRW/KRW). Liquidity 2.30M shares/day ≈ **$44M/day** — excellent. Foreign ownership already **40.24% as of 2026-07-24** ([IndexerGO](https://www.indexergo.com/series/?frq=D&idxDetail=20210)), so foreign holders clearly can own it, but it requires KOSDAQ access.

**Vision exposure: ~100%.** Global #1 in 3D solder-paste inspection, plus 3D AOI and semiconductor packaging inspection — all optomechatronic machine vision.

**2026 thesis:** Q2 2026 revenue **₩88.8B (+70.4% YoY)** and operating profit **₩14.6B (+479.1%)**, both all-time records and well ahead of consensus (₩75.2B / ₩10.8B) ([FT Today](http://www.ftoday.co.kr/news/articleViewAmp.html?idxno=362715)). Q1 2026: 3D AOI +34%, 3D SPI +40%, **server-related revenue +193% to ~₩31.2B**, semiconductor packaging inspection **+79% to ₩12.2B (17% of sales)** ([The Elec](https://www.thelec.net/news/articleView.html?idxno=10969)). The driver is AI-server board inspection — ASICs, optical modules, high-speed switches — which puts it squarely in your AI supply chain rather than in generic factory automation. There is also a small "Physical AI" line closing the loop from 3D measurement back into production-equipment auto-correction, plus a brain-surgery robot.

**Red flags:** No US listing (KOHYF returns nothing in yfinance). Same AI-datacenter capex cyclicality as ViTrox — this is an order book, not an annuity. **DATA FLAG:** one English summary rendered Q2 revenue as "887.59 billion KRW"; the Korean primary source says **888억원 = ₩88.8B** — a 10x transcription error, and I used the correct figure.

**Verdict: INCLUDE.** ~5.2x forward sales (annualizing H1) for a #1-share pure-play machine vision company compounding at 70% — cheaper than ViTrox on comparable growth, and cheaper than Cognex on far better growth.

### 0097.KL — ViTrox Corporation *(not on your list)*
**Malaysia, $4.0B.** Currency: clean (MYR/MYR).

**Vision exposure: ~99%.** Both reportable segments are machine vision — Automated Board Inspection was **61% of 9M-2025 revenue and Machine Vision System 38%** ([The Star](https://www.thestar.com.my/business/business-news/2025/10/27/demand-for-tech-to-support-vitrox-earnings)).

**2026 thesis:** Q2 2026 revenue **RM374.9M vs RM183.0M** and net profit **RM85.04M vs RM39.94M**; H1 2026 net profit **RM136.24M on revenue RM641.97M**; shares at a record high ([NST](https://www.nst.com.my/amp/business/corporate/2026/07/1501119/vitrox-shares-hit-record-high-q2-profit-more-doubles)). Q1 was already +89% YoY ([The Star](https://www.thestar.com.my/business/business-news/2026/04/23/vitrox-posts-strong-1q-results-sees-continued-momentum-in-2026)). Driver: automated board inspection for cloud service providers, running near maximum output, expected to extend into H2.

**Red flags:** **No US listing found** (VTRXF/VTOXY both 404 in yfinance — I could not conclusively prove no OTC line exists, only that none surfaced). ~13.7x TTM sales / ~10x forward — rich. Entire beat is CSP/AI-datacenter concentration. **No robotics angle at all** — this is AI-capex exposure wearing a machine-vision label.

**Verdict: INCLUDE** on fundamentals; downgrade to BORDERLINE if you won't hold Bursa-listed equities.

---

## BORDERLINE

### ZBRA — Zebra Technologies
**US, $14.0B.** Currency clean. Forward P/E **14.2**, P/S 2.51 — by far the cheapest name in the bucket.

**Machine vision % of revenue: ~5–8%, my estimate — flagged, not disclosed.** Reasoning: Zebra assembled the position through Matrox Imaging (2022), Adaptive Vision, and **Photoneo (closed 2025-02-28 for $62M cash: $17M technology intangibles, $6M customer relationships, $34M goodwill** — [Zebra 10-Q](https://www.sec.gov/Archives/edgar/data/877212/000087721225000131/zbra-20250628.htm)). A $62M purchase price and ~$5.6B group revenue bound the contribution as small. **Critically, in Q4 2025 Zebra restructured its segments** into Connected Frontline and Asset Visibility & Automation, which folded machine vision in with barcode/card printing, RFID and data capture — so machine vision is now **less** visible in the filings, not more.

**2026 thesis:** **Machine vision grew double digits in Q1 2026, which management called a market inflection point**, driven by logistics wins in the US and Europe ([Investing.com Q1 call](https://www.investing.com/news/transcripts/earnings-call-transcript-zebra-q1-2026-earnings-beat-boosts-stock-93CH-4681302)). Full-year guidance was raised to **10–14% from 9–13%**, with Q2 net sales guided **+14–17%**. New CV70 CXP high-speed machine vision camera launched at Automate 2026. Photoneo's parallel structured light is certified to interface with most major robot manufacturers for bin picking and depalletizing — a real vision-guided-robotics asset.

**Red flags:** Machine vision is a rounding error inside a barcode-scanner and mobile-computer company — you cannot express a vision thesis through ZBRA without accepting ~92% unrelated revenue. The segment reorganization actively reduces disclosure. Enterprise mobile computing is cyclical and tariff-exposed. **Q2 2026 reports 2026-08-04** — two days out.

**Verdict: BORDERLINE.** Cheap and genuinely inflecting, but the vision exposure is too diluted to serve this bucket. Include only if you want it as a cheap automation name that happens to own good vision assets.

### NOVT — Novanta Inc.
**US, $5.1B.** Currency clean.

**Robotics % of revenue: ~15–20%, my estimate — flagged.** What *is* disclosed: Q1 2026 total revenue **$257.7M** (SEC XBRL `RevenueFromContractWithCustomer`, 10-Q for period ended 2026-04-03, CIK 0001076930) and **Automation Enabling Technologies segment revenue $131.2M, +6.6%** — i.e. **50.9% of group** (my calculation). But AET bundles photonics and precision motion alongside Robotics & Automation; ATI Industrial Automation is not separately reported. ATI was acquired in 2021 for **$172M upfront plus contingent payments** ([Novanta](https://investors.novanta.com/news/news-details/2021/Novanta-Announces-Agreement-to-Acquire-ATI/default.aspx)), which bounds it as a minority of AET.

**2026 thesis:** ATI is the single most *literally* humanoid-relevant asset on this entire list — robotic tool changers, **force/torque sensors** and collision sensors, i.e. the proprioceptive perception layer at the end of a robot arm, sold to industrial, collaborative and surgical robot OEMs ([ATI](https://www.ati-ia.com/)). Management cites **strong demand for products supporting physical AI applications — warehouse automation, precision robotics, and humanoids — driving double-digit revenue growth**, with bookings led by Robotics & Automation ([FinancialContent Q1 deep dive](https://markets.financialcontent.com/stocks/article/stockstory-2026-5-12-novt-q1-deep-dive-ai-driven-demand-and-new-products-propel-growth-amid-margin-pressures)). FY2026 outlook raised to **$1,040–1,055M**, Q2 guided $259–264M ([Seeking Alpha](https://seekingalpha.com/news/4591505-novanta-forecasts-259m-264m-q2-revenue-as-2026-outlook-rises-to-1040m-1055m)).

**Red flags:** Q2 organic growth guided to only **6–8%** — the "humanoid" narrative is running well ahead of the growth rate. Margin pressure was explicitly flagged in Q1. Forward P/E 34.4 for high-single-digit organic growth is demanding. Medical Solutions is roughly half the company and unrelated. **Q2 2026 reports 2026-08-05.**

**Verdict: BORDERLINE.** The clearest humanoid *content* story (force-torque sensing is non-optional on any manipulator), but sub-10% organic growth and a 34x multiple say the market already pays for the narrative. Worth a `/refresh-context` after 08-05.

### TDY — Teledyne Technologies
**US, $30.4B.** Currency clean. Forward P/E 24.6.

**Industrial machine vision % of revenue: ~10%, my estimate — flagged.** Digital Imaging is Teledyne's largest segment but is dominated by FLIR thermal (heavily defense) plus space and scientific sensors. The machine-vision-proper piece is DALSA/e2v industrial.

**2026 thesis:** Q2 2026 **Digital Imaging revenue +7.5%, FLIR +9%**, and **DALSA e2v industrial and scientific vision +high single digits, "a little over 8%"**, with particular strength in semiconductor inspection; margins in both FLIR and DALSA e2v "increased significantly." Full-year non-GAAP EPS raised to **$24.45–24.65**, full-year revenue growth ~7%, **200bps above the April projection** ([Motley Fool Q2 2026 transcript](https://www.fool.com/earnings/call-transcripts/2026/07/22/teledyne-tdy-q2-2026-earnings-call-transcript/); [Investing.com](https://www.investing.com/news/transcripts/earnings-call-transcript-teledyne-beats-q2-2026-estimates-and-lifts-outlook-93CH-4806599)).

**Red flags:** ~8% growth in the vision line is fine, not an inflection. Teledyne is a serial-acquirer conglomerate spanning marine, aerospace, defense electronics and test — vision is a minority of a minority. **No robotics or humanoid angle disclosed anywhere.**

**Verdict: BORDERLINE, leaning EXCLUDE for *this* bucket.** A good defense/imaging compounder, but it does not express a robot-perception thesis.

### BSL.DE — Basler AG
**Germany, $0.89B (EUR 768.8M).** Currency: clean at source (EUR/EUR). **The OTC ticker in your brief does not exist** — `BSLRF` returns a yfinance 404 ("Quote not found"). **FLAG: there is no verified US OTC line for Basler.** You must trade **BSL.DE** on Xetra.

**Vision exposure: 100%** — area-scan and line-scan cameras, 3D, SWIR/UV, embedded vision, lenses, frame grabbers and software.

**2026 thesis — the sharpest order inflection in the entire bucket.** Q1 2026 **incoming orders EUR 85.6M, +64% YoY**; revenue **EUR 77.3M, +30%**; **EBIT EUR 17.6M versus EUR 6.2M** — a near-tripling. FY2026 guidance raised to **EUR 247–270M** ([Basler via webdisclosure](https://www.webdisclosure.com/article/basler-ag-etr-bsl-basler-ag-reports-strong-start-in-2026-with-raised-forecast-s0BajFhzL0O)). Growth is attributed to China plus semiconductor, electronics and logistics. Basler has **doubled camera assembly capacity** with a new parts-placement machine ([Wiley Industry News](https://wileyindustrynews.com/en/news/basler-doubles-camera-production-capacity)) — capacity added *into* a 64% order surge is the classic pre-inflection signal. Robot relevance: Basler partnered with Orbbec on 3D vision systems for mobile robots ([The Robot Report](https://www.therobotreport.com/basler-orbbec-partner-3d-vision-systems-mobile-robots/)).

**Red flags:**
- **Liquidity is the binding constraint.** 42,930 shares/day (10-day: 27,166) at EUR 25 ≈ **EUR 1.07M/day**. That is a genuine size limit for anything but a small position.
- **China is the growth driver** — explicitly cited as the main contributor. That is concentration risk and geopolitical risk in one, and it cuts both ways versus a "China share loss" concern: Basler is currently *winning* in China, which makes it vulnerable to domestic substitution by Luster LightTech and Orbbec.
- Order growth of +64% against revenue +30% means a backlog build that could reverse violently — machine vision cameras are short-cycle and orders are cancellable.
- No US listing means no SEC filings, no Form 4 insider data (your M3 rating defaults to flagged), and `expectations_flag.py` will self-skip on no us-gaap XBRL.

**Verdict: BORDERLINE-INCLUDE.** Best pure-play order inflection available, at a real size limit. If you can live with ~EUR 1M/day, this is arguably the most interesting small-cap in the bucket.

### HSAI — Hesai Group
**China, $21.2B.** **CURRENCY TRAP:** `currency`=USD / `financialCurrency`=CNY. There is no clean same-currency listing, so this needs the rule-19 **general FX branch**, not `ADR_LOCAL`.

**Robotics % of revenue: NOT DISCLOSED — only units.** Q1 2026 **robotics lidar shipments 118,282 units, +137.8% YoY** against total revenue **RMB 681M (~$99M), +29.6%**, gross margin **>39%**, net income **RMB 18M** ([StockTitan](https://www.stocktitan.net/news/HSAI/hesai-group-reports-first-quarter-2026-unaudited-financial-wgvrptc5slt8.html); [Motley Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/05/19/hesai-hsai-q1-2026-earnings-call-transcript/)). **I will not convert units into a revenue percentage** — robotics lidar (lawnmower, delivery) carries a fraction of ADAS ASPs, and unit growth of +138% against revenue growth of +30% proves ASPs are falling hard. Anyone quoting "robotics is X% of Hesai revenue" from unit data is guessing.

**2026 thesis:** Ranked #1 by GGII, Yole and Frost & Sullivan across humanoid and quadruped robots, robotaxis, robovans and robotic lawnmowers. Signed orders with **Dreame and MOVA** representing a **backlog of over 10 million lidar units**; scaling capacity to **>4 million units in 2026**; full-year guidance reaffirmed at **3–3.5M lidar units**. The SGI segment (Kosmo + robotic actuation modules) is guided to **~RMB 100M in 2026 revenue, targeting ~RMB 500M by 2027**.

**Red flags:**
- **Valuation is extreme.** $21.2B against TTM revenue of RMB 3.18B (~$447M) ≈ **47x sales** for a company earning RMB 18M in the quarter. yfinance's forward P/E of 18.9 is not credible against that revenue base — **FLAG and verify before scoring.**
- **ASP collapse.** +138% units to +30% revenue is the single most important thing to underwrite here.
- Total China exposure: customers, manufacturing, PCAOB/geopolitical tail risk.
- The robot-lawnmower backlog is consumer appliance demand, not physical-AI demand. Be honest about what those 10M units are.

**Verdict: BORDERLINE.** Genuine #1 robotics-perception franchise with real unit volume, at a multiple that already prices the win. The undisclosed revenue mix is a rule-3 gap that should be closed before scoring.

### AEVA — Aeva Technologies
**US, $1.2B.** Currency clean.

**Exposure: ~100% perception**, with a genuinely non-automotive industrial line. Aeva's Eve technology powers **Nikon's APDIS MV5X laser radar, which entered commercial deployment in April 2026** under a multi-year production agreement for high-volume **automated robotic inspection and metrology** in automotive, aerospace and energy ([Aeva](https://www.aeva.com/press/nikon-begins-commercial-deployment-of-its-next-generation-apdis-mv5x-laser-radar-system-powered-by-aeva/)). Also partnered with SICK AG; production wins at Daimler Truck and a top European passenger OEM. Q1 2026 was a record revenue quarter ([Aeva IR](https://investors.aeva.com/news-releases/news-release-details/aeva-reports-first-quarter-2026-results)).

**Red flags:** **TTM revenue is $21.0M against a $1.18B market cap — 56x sales** (yfinance). "Record quarterly revenue" off that base is a low bar. FMCW lidar remains unproven at automotive volume. Cash burn requires monitoring. The Nikon programme is real but Aeva is a component supplier two layers from the end customer.

**Verdict: BORDERLINE, leaning EXCLUDE.** The industrial-robotics revenue driver is *genuine* — which is more than Innoviz or MicroVision can say — but 56x sales on $21M of revenue is a venture-stage risk profile.

### 2498.HK — RoboSense Technology *(not on your list)*
**China, $1.4B.** **CURRENCY TRAP on both lines** (HKD or USD traded, CNY reported) — needs the general FX branch.

**The most dramatic robotics pivot I found.** H1 2026 lidar sales **719,200 units, +169.6%**, of which **robotics 282,600 units, +510.4%** ([PR Newswire](https://www.prnewswire.com/news-releases/robosense-announces-h1-2026-lidar-sales-of-719-200-units-as-robotics-segment-grows-by-510-4-302821684.html)). In Q1 2026, **robotics lidar volume surpassed automotive ADAS for the first time** at 185,500 units, **+1,458.8% YoY** ([PR Newswire](https://www.prnewswire.com/news-releases/robosense-announced-q1-2026-lidar-sales-robotics-segment-grows-1-458-8-yoy-to-over-185-500-units-302737619.html)). Robotics was **~49% of Q4 2025 product sales revenue** ([Gasgoo](https://autonews.gasgoo.com/articles/news/robosense-achieves-first-quarterly-profit-in-2025-robotics-business-accounts-for-nearly-half-2037147819842895872)). At ~4.6x sales it is roughly **one tenth Hesai's multiple**.

**Red flags:** US OTC line RBSTF trades **~3,894 shares/day over 10 days (~$11k/day)** — unusable; you need HK access. Gross margin **fell to 21.7% from 23.5%** while volume exploded — same ASP-collapse problem as Hesai, worse. Still loss-making. Total China exposure.

**Verdict: BORDERLINE.** Materially cheaper than Hesai on the same thesis with better robotics mix — but worse margins, worse access, and equal geopolitical risk.

### TWEKA.AS — TKH Group *(not on your list)*
**Netherlands, $2.0B.** **CURRENCY TRAP** on the OTC line (TKHGF, USD/EUR); TWEKA.AS is clean EUR/EUR.

FY2025 **Vision Technologies turnover EUR 522.6M, +6.7% organic, 17.9% ROS** against group EUR 1,761.2M = **29.7% of group** (my calculation) at ~1.7x the group's 10.8% ROS ([TKH](https://www.tkhgroup.com/news/full-year-2025-and-q4-2025-results)). Q1 2026 Vision **+7.4% organic** with the machine vision orderbook "substantially higher" than year-end ([TKH Q1 2026](https://www.tkhgroup.com/news/q1-2026-market-update)). Owns **LMI Technologies** (Gocator 3D snapshot/laser-profile sensors used for robot guidance) — the best Western 3D robot-perception asset outside Cognex/Zebra.

**Red flags:** ~70% of the company is cables/electrification/parking. Net bank debt **EUR 461.4M, 1.9x leverage**. TKHGF returns no price or volume in yfinance. Machine Vision is not split from Security Vision, so my ~20%-of-group figure is derived. **H1 2026 results were not found and are due imminently — FLAG.**

**Verdict: BORDERLINE.** Sum-of-the-parts vision re-rating candidate; fails on purity.

---

## EXCLUDE

### SONY — Sony Group Corporation
**Japan, $136.6B.** **CURRENCY TRAP:** `currency`=USD / `financialCurrency`=JPY → map **SONY → 6758.T** (yfinance P/S 0.0108 on SONY is trap garbage; 6758.T shows 1.75).

**Answering your question directly: no, there is no genuine 2026 robot-vision thesis — it is consumer/mobile-dominated.** FY2026 Imaging & Sensing Solutions guidance is **¥2,250B revenue and ¥150B operating income** ([Investing.com Q1 FY2026 slides](https://www.investing.com/news/company-news/sony-q1-fy2026-slides-operating-income-surges-40-on-gaming-sensors-93CH-4827007)) against group TTM revenue of ~¥12,696B (yfinance) — **I&SS is ~17.7% of Sony** (my calculation), and within I&SS the growth driver is explicitly **high-end mobile smartphone sensors**. Sony itself warned that **smartphone sensor growth may fluctuate as the trend toward larger sensors plateaus**.

The robot-vision technology is real but unsized: event-based vision sensors co-developed with Prophesee, and an AITRIOS Robotics Package bundling multi-dToF, RGB, IMU and software for autonomous mobile robots. Sony AI's table-tennis robot "Ace" (published in *Nature*, April 2026) used nine IMX273 sensors plus three IMX636 event-based cameras ([Sony Semiconductor](https://www.sony-semicon.com/en/info/2026/2026042301.html)) — a superb technology demonstration and **zero disclosed revenue**.

**Verdict: EXCLUDE.** ~18% of revenue in image sensors, of which robot vision is an unsized sliver inside a games/music/pictures conglomerate. Buying SONY for robot perception is a ~1% exposure.

### OMRNY (→ 6645.T) — Omron Corporation
**Japan, $6.8B.** **CURRENCY TRAP:** USD/JPY → map to **6645.T**. Liquidity: OMRNY 10-day average **13,870 shares/day** — thin.

FY2026 (ended March 2026) net sales **¥767.4B, +7.3%**, operating income **¥59.9B, +12.1%**, net income **¥28.5B, +75.1%** ([BigGo/JPX TDnet](https://finance.biggo.com/news/jpx_tdnet_140120260513529706)). Industrial Automation is **~53% of revenue** — but note this uses the **FY2025 IAB figure of ¥409.5B**, so the percentage is approximate. **FLAG.** Machine vision is a minority sub-line within IAB and is not separately disclosed.

The story here is a **turnaround, not a robotics inflection**: Structural Reform Program NEXT2025 ran April 2024–September 2025 and cut **~¥35B of fixed costs** ([Omron business report](https://www.omron.com/global/en/assets/file/ir/shareholder/business_report_89th.pdf)). IAB sales were driven by "generative AI-related demand."

**Verdict: EXCLUDE.** A **7.8% operating margin** (59.9/767.4) versus Keyence's 51.0% on overlapping products tells you everything about relative franchise quality. If you want Japanese factory automation vision, own Keyence.

### EMR — Emerson Electric
**US, $83.9B.** Currency clean.

**Answering your question: yes, Emerson completed the NI acquisition on 2023-10-11 at an $8.2B equity value**, and NI became the **Test & Measurement segment** within the Software and Control group, still headquartered in Austin ([Emerson](https://www.emerson.com/en-us/news/2023/emerson-completes-ni-acquisition)). T&M grew **11% in Q1 2026** ([Emerson Q1 2026 transcript](https://www.aol.com/finance/emerson-emr-q1-2026-earnings-230814254.html)).

**But there is no vision/robotics angle.** NI is modular test hardware plus LabVIEW, selling into automotive and aerospace *test* — validation benches, not perception. NI's legacy Vision Builder/IMAQ products are peripheral and unsized. T&M is roughly 9% of Emerson's $18.3B revenue, inside an $84B diversified process-automation conglomerate.

**Verdict: EXCLUDE.** Mis-categorized. Test and measurement is not machine vision.

### IPGP — IPG Photonics
**US, $3.6B.** Currency clean.

Q1 2026 revenue **$265.5M, +17%**; Industrial Solutions **$227.6M, 86% of revenue, +21%**; emerging growth products 53% of revenue ([StockTitan](https://www.stocktitan.net/news/IPGP/ipg-photonics-announces-first-quarter-2026-financial-f9ytn869pbkp.html)). Q2 guided $260–290M; **Q2 2026 reported 2026-08-04**.

**The robotics angle is real but it is not perception.** IPG sells robot-mounted laser welding cells (LaserCell, single/dual 6-axis configurations) — the robot is the *delivery mechanism* for IPG's laser, not a customer for IPG vision. IPG has **no machine-vision product line of consequence**.

**Verdict: EXCLUDE from this bucket.** IPG is a fiber-laser company. Forward P/E 36.8 on 17% growth is also unattractive versus alternatives here.

### MVIS — MicroVision
**~$251M — NOT the $6.2M yfinance reports.** See the flag at the top.

MicroVision won Luminar's lidar assets at bankruptcy auction — Iris and Halo IP, inventory, engineering talent and certain contracts — for **$33M cash, closed 2026-02-03** ([MicroVision IR](https://ir.microvision.com/news/press-releases/detail/436/microvision-announces-agreement-to-acquire-luminar-assets); [Ropes & Gray](https://www.ropesgray.com/en/news-and-events/news/2026/02/microvision-acquires-luminar-lidar-assets)). Q1 2026 revenue **$935K** versus $589K prior year; FY2026 guidance **$10–15M**, most in H2; liquidity **$46.1M cash plus $42.0M remaining ATM capacity under a $150M programme** ([StockTitan 10-Q](https://www.stocktitan.net/sec-filings/MVIS/10-q-microvision-inc-quarterly-earnings-report-135eb5e449c1.html)). **1-for-15 reverse split effective 2026-08-01** to cure a January 2026 Nasdaq minimum-bid deficiency.

**Verdict: EXCLUDE.** Sub-$1M quarterly revenue, an ATM-funded balance sheet, and a reverse split to preserve listing. The Luminar assets may prove cheap, but this fails any reasonable quality gate.

### LAZR — Luminar Technologies
**Equity cancelled without consideration. Zero value.** Chapter 11 filed 2025-12-15 (S.D. Tex.) after losing the Volvo contract; Nasdaq delisting notice 2025-12-17, trading suspended 2025-12-24; traded as LAZRQ on OTC Pink thereafter. Luminar Semiconductor sold to Quantum Computing Inc.; the lidar business sold to MicroVision.

**Verdict: EXCLUDE — uninvestable.** Add `LAZR` to a ticker denylist so the recycled ETF ticker never enters a scoring pass.

---

## Existing watchlist names — unappreciated robotics angles

### TER — Teradyne (Universal Robots + MiR)
**The robotics segment just crossed a threshold worth flagging.** Teradyne Robotics posted **$100M in Q2 2026 revenue, +33% YoY from $75M, and +9% sequentially from $91M in Q1** — its **first-ever $100M quarter** ([TechTimes](https://www.techtimes.com/articles/322398/20260731/ai-factory-buildout-lifts-teradyne-robotics-first-ever-100m-quarter.htm); [The Robot Report](https://www.therobotreport.com/teradyne-robotics-revenue-rises-33-year-over-year-in-q2/)).

Two details that matter for your AI supply-chain thesis specifically:
- **AI-linked sales are >60% of revenue across all three business units** (Semiconductor Test, Product Test, Robotics).
- **Robotics' fastest-growing verticals were electronics manufacturing and semiconductors, both fueled by AI data center construction.** That reframes UR/MiR from a generic cobot business into a *second-order AI capex play* — robots building the AI buildout.
- US sales rose to **32% of Teradyne Robotics revenue**, with a Michigan manufacturing center launching later this year (reshoring tailwind).

If TER's AI-Thesis D-dimensions were rated when Robotics was a sub-scale drag, they are stale. **Recommend a `/refresh-context` pass on TER** — this looks like a rule-12 subjective-rating refresh trigger.

### Other exclusion-list names
No other watchlist name surfaced an unappreciated machine-vision angle in this research. **ONTO, CAMT, KLIC and MKSI** all sit in semiconductor process-control/metrology, which is adjacent but is not machine vision under any workable definition — I deliberately excluded Nova (NVMI) and Lasertec on the same reasoning to avoid double-counting your existing coverage.

---

## Open flags and data gaps (rule 3)

1. **Keyence revenue conflict, unresolved.** FY2026 release says net sales ~**¥1.17 trillion**; yfinance says **¥1,254.8B**. Probably a fiscal-boundary artifact (FY ends ~March 20) but unconfirmed. **Verify against the primary tanshin before scoring.**
2. **MVIS market cap is corrupt in yfinance** (post-split shares × pre-split price). Do not score until it reconciles.
3. **Hexagon's yfinance revenue (EUR 5.467B) is pre-Octave-spin** and not comparable to the ~EUR 4.2B RemainCo run-rate.
4. **Hesai's robotics revenue share is not disclosed** — only units. Unit growth (+138%) vastly exceeds revenue growth (+30%), so any unit-derived revenue percentage is wrong.
5. **Basler `BSLRF` does not exist** — yfinance 404. No verified US OTC line; Xetra only.
6. **Omron's IAB ~53%** uses an FY2025 segment figure against FY2026 group sales. Approximate.
7. **Zebra, Teledyne, Novanta and Keyence do not disclose machine-vision or robotics revenue.** All four percentages in the roster are my estimates with reasoning shown — none should be entered as cited data.
8. **Currency traps requiring rule-19 handling:** KYCCF (USD/JPY → 6861.T), SONY (USD/JPY → 6758.T), OMRNY (USD/JPY → 6645.T), HSAI (USD/CNY, **general FX branch, no clean listing**), **HXGBY AND HEXA-B.ST (both traps — USD/EUR and SEK/EUR; `ADR_LOCAL` will not fix this one)**, RBSTF and 2498.HK (USD or HKD vs CNY), TKHGF (USD/EUR). Clean: CGNX, ZBRA, NOVT, TDY, EMR, IPGP, OUST, AEVA, MVIS, BSL.DE, 0097.KL, 098460.KQ.
9. **Four names report within 72 hours** — CGNX and NOVT on 08-05, ZBRA and IPGP on 08-04. Under rule 9 any scoring done today is stale by Wednesday.
10. **No public pure-play exists** for event cameras (Prophesee, iniVation — private), vision software (MVTec private; Matrox and Photoneo both absorbed by Zebra), or 3D bin-picking (Mech-Mind private). SICK AG is family-held and unlisted. Hikvision's Hikrobot is a top-5 global machine vision vendor but is **uninvestable on US Entity List / NS-CMIC grounds**.

**Bottom line for the bucket:** the four names that actually express a *robot perception* thesis rather than a factory-inspection thesis are **Hexagon** (humanoid, named customer, funded), **Ouster** (merchant perception platform), **Novanta** (force-torque content) and **RoboSense/Hesai** (robot lidar volume). **Cognex and Keyence** are the quality anchors but are inspection businesses riding AI capex, not robot perception. **Koh Young and ViTrox** are the strongest fundamentals in the whole screen and are pure machine vision — but they are AI-datacenter cyclicals with no robotics content and no US listing.