# Weekly News Scan — 2026-06-26

**Scope:** 168 watchlist tickers. Scan date: 2026-06-26 (covering June 20–26).

**Note on execution:** SEC EDGAR (data.sec.gov + www.sec.gov) and yfinance remain 403-blocked from this cloud environment — same egress restriction as June 12 and June 19 scans. 8-K scan conducted via WebSearch against SEC full-text search and StockTitan. Objective inputs updated June 24 via the daily-refresh CI (all inputs are as of June 24 close, pre-MU earnings). 50DMA refresh and `refresh_targets.py`/`track_performance.py` blocked; portfolio membership confirmed from Targets sheet. **Rule 9 refresh for MU is blocked by network — flagged below as top priority.** This week's MU earnings are the single most significant event.

**Unresolved tickers (no SEC CIK):** SBGSY, TOELY, BESIY — foreign ADRs (known limitation). SPCX (SpaceX) — private.

---

## Step 0 — Mental Models: Portfolio Holdings (pre-scan articulation)

TSM crossed ✓✓✓ (87.9) in the June 24 refresh — first portfolio name at top tier. Portfolio is 14 holdings (13 with the current Targets state; WDC may exit this week — see pipeline section).

| Ticker | Score | Mental model (pre-scan) |
|--------|-------|--------------------------|
| TSM | 87.9 ✓✓✓ | World's leading contract fab. N3/N2 in full ramp; CoWoS capacity expanding to meet AI package demand. Every AI chip NVDA/AMD/AVGO/ALAB ships runs through TSMC. May 2026 revenue +30.1% YoY (6-K). Key risk: Taiwan geopolitics. Taiwan guarantee disclosures expanding. |
| NVDA | 84.1 | Dominant AI GPU, ~80-90% merchant accelerator share. Q1 FY27 $81.6B (+85%), Q2 guided $91B. Networking +199%. CUDA moat. China = $0 DC revenue. Completed $25B seven-tranche bond deal June 18. |
| SNDK | 80.1 | Sandisk (spun from WD 2025). NAND flash; memory cycle recovery + AI storage demand. Q3 FY26 revenue $5.95B (+251% YoY), GM 78.4%, Q4 guide $7.75-8.25B. Not an AI moat play — pricing recovery + datacenter mix shift. |
| CRDO | 80.0 | Credo Technology. SerDes + AEC + (post-DustPhotonics) Silicon Photonics PICs for 400G-3.2T. FY26 $1.3B revenue (3× YoY), Q4 $437M +157%. CEO PSU program with $7.5B revenue target. Vertical integration thesis advancing. |
| META | 79.5 | Social/ads + massive AI infra (Llama, Superintelligence Labs). AI monetizing through ad ranking. $6.6 GW nuclear PPA announced Jan 2026 (Oklo, Vistra, TerraPower). High capex with clear ROI. |
| MU | 79.4 | HBM3E/HBM4 for Blackwell and next-gen AI. **Q3 FY26 due June 24 (tonight relative to scan start).** Guided $33.5B / 81% GM. TTM score significantly understated — current run-rate is dramatically higher. |
| AVGO | 79.2 | Largest custom ASIC designer (Google TPUs, Meta training ASICs). Ethernet networking. Q2 FY26 $22.2B (+48% YoY); AI semiconductor $10.8B (+143%); Q3 guide $29.4B / AI semi $16B. GM 76.3% (refreshed). |
| ANET | 78.5 | Arista DC networking. AI fabric $3.5B target. MSFT + META = 42% of revenue. Spectrum-X competitive watch ongoing. Q1 2026 revenue $2.71B (+35.1% YoY). |
| MSFT | 78.4 | Azure AI, Copilot+ across Office, OpenAI lock-in. $75B+ capex annually. Wiz acquisition closed March 2026 ($32B). |
| GOOGL | 78.0 | Hyperscaler. Gemini 3.5, TPU/Blackstone JV, capex $180-190B 2026. Completed $84.75B June equity/debt package (June 12 scan). |
| ALAB | 77.1 | Astera Labs. Scorpio PCIe 5.0 fabric in volume. NVLink Fusion + UALink (2027). Customer A (Amazon?) = 29% Q1 2026 revenue. Taiwan Cloud Interop Lab expansion June 2026. |
| APP | 76.9 | AppLovin. AXS AI-driven mobile ad engine, strong margin expansion. AI-native ad targeting with growing network effects. Scored 78.9 in June 19 scan — expect decline in today's pass. |
| FIX | 76.7 | Comfort Systems USA. HVAC/mechanical DC construction pure-play. Record backlog $12.45B. Q1 revenue +56.5% to $2.87B. Only L03 DC construction name in the portfolio post-EME exit. |
| WDC | 71.6 | Western Digital. HDD + flash. Memory cycle recovery + AI storage demand. **Scored 78.0 in June 19 scan; dropped to 71.6 in June 24 refresh — well below the 76 bar. EXIT PENDING per framework.** |

**Thesis diff (articulated vs. scan-discovered):**
- **MU:** Pre-scan model was conservative ($33.5B guided). Actual Q3 results came in at $41.5B — a $8B beat and a fundamental step-change in the business model (16 take-or-pay SCAs with ~$100B contracted revenue). The thesis has strengthened dramatically; the mental model was understating this quarter.
- **WDC:** Score drop to 71.6 was a post-refresh surprise. The SNDK share exchange (June 22 close) may have affected yfinance market cap / dilution calculations. Needs investigation before the exit is confirmed.

---

## ⚠️ Material Events (June 20–26)

### 1. MU — Q3 FY26 Earnings (June 24) 📊📊📊 — HIGHEST PRIORITY

**8-K filed June 24 (Item 2.02).** Micron reported its largest quarter in history:

| Metric | Q3 FY26 Actual | vs. Prior Guidance | vs. Prior Year (Q3 FY25) |
|--------|-----------------|---------------------|---------------------------|
| Revenue | **$41.46B** | +24% above $33.5B guided | +346% YoY |
| Gross Margin | **84.9%** | +390bps vs. 81% guided | +4,420bps YoY |
| EPS (non-GAAP) | **$25.11** | +$4.62 vs. $20.49 consensus | +998% YoY |

**Q4 FY26 guidance:** Revenue ~$50B (+343% YoY vs. $11.3B prior year), GM ~86%.

**Strategic Customer Agreements (SCAs):** 16 take-or-pay, non-cancellable customer contracts covering ~$100B in minimum contracted revenue and $22B in upfront customer cash deposits (back-end-loaded return schedule). HBM3E and HBM4 fully booked through 2027; demand extending into 2028. These contracts fundamentally de-risk MU's revenue visibility — the business model is meaningfully different from the prior memory cycle (no inventory glut scenario with take-or-pay commitments).

**HBM4:** >$1B in HBM4 revenue already shipped. Volume ramp tracking 2× faster than HBM3E 12-high. Data center revenue exceeded $25B in Q3; enterprise SSD $5B.

**Score impact (estimated, Rule 9):** Current score 79.4 uses pre-Q3 TTM data (GM 58.44%, FCF mgn 17.69%, Rev 3yr CAGR 6.71%). Estimated post-refresh score **~86-87 → would cross ✓✓✓ (85)** based on TTM improvements: GM → ~72%+ (from 84.9% Q3), FCF margin → ~24%+, Rev 3yr CAGR → ~60-80%+, EV/EBITDA → ~15-16× (dramatically lower). **Network-blocked; full `/earnings-update MU` needed as top priority.**

**TTM limitation note:** MU's TTM inputs significantly understate the current run rate. MRQ GM (84.9%) is 26pp above TTM GM (58.44%). The actual forward earnings power is closer to the MRQ-implied trajectory. This is the most extreme TTM/MRQ divergence on the watchlist.

**Stock:** +14.6% after hours to $1,192.52 on June 24.

Sources: SEC EDGAR 8-K June 24; [Investing.com Q3 slides](https://www.investing.com/news/company-news/micron-q3-fy2026-slides-record-415b-revenue-85-margins-93CH-4759286); [CNBC Q3 2026](https://www.cnbc.com/2026/06/24/micron-mu-earnings-report-q3-2026.html); [TechTimes SCAs](https://www.techtimes.com/articles/319032/20260625/micron-q3-2026-earnings-100b-contracts-signals-ai-memory-cycle-break.htm).

---

### 2. CEG — Constellation + Walmart Nuclear PPA (June 23) ⚛️

**8-K filed ~June 23 (Item 1.01).** Constellation and Walmart announced a long-term nuclear power purchase agreement for emissions-free electricity from Constellation's Dresden Clean Energy Center in Illinois. ~176 MW of wholesale supply including 30 MW of expanded generating capacity. Two 15-year terms beginning 2029 and 2030. Backstopped by Constellation's strong nuclear operations (44,666 GWh, 92.3% capacity factor in Q1 2026).

This is CEG's third major AI/data-center–adjacent nuclear PPA in 2026 (after Microsoft Three Mile Island in prior cycles). Walmart is not a hyperscaler but the breadth of clean-energy corporate buyers validates the long-term PPA model. Thesis intact.

Sources: [Walmart press release](https://corporate.walmart.com/news/2026/06/23/constellation-and-walmart-announce-longterm-agreement-to-support-reliable-emissionsfree-nuclear-energy-in-illinois); [SEC 8-K filing](https://www.sec.gov/Archives/edgar/data/0001868275/000110465926069482/tm2616531d1_8k.htm).

---

### 3. CRWV — Nasdaq-100 Inclusion (June 22) 💼

CoreWeave joined the Nasdaq-100 Index effective June 22 (announced June 12 via 8-K). Passive mandate forces: $800B+ in QQQ-mirroring assets required to allocate to CRWV in proportion to its index weighting regardless of price or valuation. Stock +18.87% pre-inclusion as traders front-ran the mandate. Fell modestly on inclusion date (classic sell-the-news). CRWV also reportedly added $32B to its AI backlog ahead of inclusion.

Portfolio note: CRWV is a Watchlist name (Layer 9 Neocloud), not in the current portfolio model. Score was not in the top Targets. The Nasdaq-100 inclusion increases CRWV's float-adjusted market cap and liquidity, potentially improving its scoring inputs on next refresh.

Sources: [CoreWeave press release](https://investors.coreweave.com/news/news-details/2026/CoreWeave-to-Join-Nasdaq-100-Index/default.aspx); [TechTimes Nasdaq-100 rebalance](https://www.techtimes.com/articles/318402/20260615/nasdaq-100-rebalance-adds-five-ai-stocks-june-22-qqq-holders-get-coreweave-debt.htm).

---

### 4. FIX — COO Appointment (June 22) 🔧

**8-K filed June 22 (Item 5.02).** Craig Sasser, currently Regional Vice President (Atlantic Region), will be appointed Chief Operating Officer effective July 1, 2026. Compensation: $600K base salary, 90% target bonus. No mention of prior COO departure — this may be a newly created role as FIX scales its DC construction business. With a record $12.45B backlog and Q1 revenue +56.5% YoY, the COO appointment signals organizational scaling to match growth. Positive thesis signal — management investing in execution infrastructure.

Sources: [SEC 8-K filing](https://www.sec.gov/Archives/edgar/data/0001035983/000110465926076386/tm2618408d1_8k.htm).

---

### 5. CRWD — Stock Split Record Date (June 25) 📋

CrowdStrike's 4-for-1 stock split record date falls in this scan window (June 25). Distribution: July 1, 2026. Trading on split-adjusted basis: July 2. Announced June 3 via 8-K. The split makes CRWD shares more accessible to retail investors but does not change fundamentals. CRWD is a Watchlist name (Layer 10 cybersecurity), not currently in the portfolio (score 72.7).

Sources: [SEC 8-K June 3](https://www.sec.gov/Archives/edgar/data/0001535527/000153552726000022/crwd-20260603.htm); [Yahoo Finance split article](https://finance.yahoo.com/markets/stocks/articles/crowdstrikes-4-1-stock-split-113100110.html).

---

### 6. ANET — Co-Founder Insider Sale (Form 4, June 22) 📋

Andreas Bechtolsheim (co-founder, ~10% owner via family trust) sold 260,900 ANET shares on June 15, 2026 for ~$43M ($163.51–169.17/share range). Filed as Form 4 June 22. **Pre-planned: 10b5-1 plan entered February 20, 2026.** This is the third large Bechtolsheim sale in 2026 ($34.7M, $39.1M, and now $43M via similar pre-arranged sales). Stock fell 6.41% on June 23.

Per framework Rule 7: insider selling is ambiguous; pre-planned sales especially so (entered well before the trade). The pattern of recurring large sales by the founding shareholder is worth tracking but does not constitute a bearish signal per established research. **Does not change thesis or rating.**

Sources: [StockTitan Form 4](https://www.stocktitan.net/sec-filings/ANET/form-4-arista-networks-inc-insider-trading-activity-ff8e3f0bd660.html); [Investing.com](https://www.investing.com/news/insider-trading-news/arista-networks-andreas-bechtolsheim-sells-43-million-in-anet-stock-93CH-4753414).

---

### 7. WDC — SNDK Share Exchange Closed (June 22) 💼

Western Digital closed its exchange of 1,038,681 SanDisk (SNDK) shares held as treasury for WDC common shares on June 22, with pricing based on VWAP of both stocks June 16–18. WDC surged 6% on the June 11 announcement; fell 4% on June 25. The exchange reduces WDC's SNDK holding and introduces modest WDC share dilution. Not a fundamental business change but contributed to price volatility and may be affecting yfinance market cap calculations (explaining part of the score drop from 78.0 to 71.6). See pipeline section.

Sources: [MoneyCheck](https://moneycheck.com/western-digital-wdc-surges-6-on-sandisk-share-exchange-agreement/); [StockTitan 8-K](https://www.stocktitan.net/sec-filings/WDC/8-k-western-digital-corp-reports-material-event-a0b2489c799c.html).

---

## 📊 Earnings Refreshed (Rule #9)

### MU — Q3 FY26 (June 24 — PRIORITY, BLOCKED)

| | Before Q3 refresh | After Q3 refresh (estimated) |
|--|--|--|
| Score | 79.4 | ~86–87 (est.) |
| Tier | ✓✓ | **✓✓✓ (est.)** |
| GM (TTM) | 58.44% | ~72%+ |
| FCF Mgn (TTM) | 17.69% | ~24%+ |
| Rev 3yr CAGR | 6.71% | ~60-80%+ |
| EV/EBITDA (TTM) | 32.0× | ~15-16× |

📊 **Priority: revenue beat +24% vs guidance (+$8B), GM +390bps vs guidance.** This exceeds the Rule 9 "priority" threshold (>15% beat + >500bps GM sequential move) on both counts. Full `/earnings-update MU` should be run as soon as network access is available. The SCA structure (~$100B take-or-pay) also warrants thesis.md update.

**TTM limitation:** MRQ GM 84.9% is 26.5pp above TTM GM 58.44%. TTM averages will understate the current run rate for at least 3 quarters. Flag MRQ vs TTM divergence prominently when refresh runs.

No other earnings 8-Ks found in the June 20–26 window for watchlist tickers. SNDK Q3 was April 30 (already reflected in scores).

---

## 💼 Portfolio Pipeline

### Score Changes Since June 19 Scan

| Ticker | June 19 Score | Current Score | Change | Note |
|--------|--------------|---------------|--------|------|
| TSM | 84.7 | **87.9** | +3.2 | ⚠️ **TIER CHANGE: ✓✓ → ✓✓✓** (first portfolio name >85) |
| CRDO | 78.9 | 80.0 | +1.1 | Up (earnings refresh carried from June 19 scan) |
| MSFT | 77.2 | 78.4 | +1.2 | Up |
| GOOGL | 76.8 | 78.0 | +1.2 | Up |
| ANET | 78.5 | 78.5 | 0.0 | Unchanged |
| MU | 80.0 | 79.4 | −0.6 | ↓ slightly; stale (pre-Q3 earnings) |
| META | 79.4 | 79.5 | +0.1 | Stable |
| AVGO | 79.2 | 79.2 | 0.0 | Unchanged |
| SNDK | 80.1 | 80.1 | 0.0 | Unchanged |
| ALAB | 77.1 | 77.1 | 0.0 | Unchanged |
| APP | 78.9 | **76.9** | −2.0 | ↓ Hairline above 76 bar |
| FIX | 76.7 | 76.7 | 0.0 | Unchanged |
| **WDC** | **78.0** | **71.6** | **−6.4** | ⚠️ **BELOW 76 BAR — EXIT PENDING** |
| RDDT | new | 79.4 | — | New Watchlist entry; not yet in Targets |

Score changes are from the June 24 full-watchlist objective refresh. MU's change is pre-Q3 earnings (staleness, not fundamental deterioration).

---

### ⚠️ Portfolio Flag: WDC — EXIT PENDING

WDC scored **71.62** in the June 24 refresh — **4.4 points below the 76-bar**. In the Targets sheet, WDC is listed as Include=Y / Status=HOLD at row 34 with score 71.62. Per framework, this is an EXIT signal; the position confirms for exit on **next week's scan** (July 3 week) unless the score recovers.

**What drove the drop (78.0 → 71.6):**
- Fwd P/E: 35.66 → scores 30 (was probably 25-30 range before)
- EV/EBITDA: 56.11 → scores 5 (catch-all; very expensive vs. EBITDA)
- Rev 3yr CAGR: −20.28% → scores 15 (memory downcycle base effect)
- P/S: 18.84 → scores 15

Value subscore is very weak. WDC's 3-year CAGR is negative because the memory downcycle is in the denominator; EV/EBITDA at 56× is inflated because EBITDA is recovering from trough. The SNDK share exchange may also have temporarily distorted yfinance market cap (WDC issued new shares June 22).

**Do NOT change Include flag automatically** — this is an alert for Dom to review. Potential mitigating factors: (1) WDC Q4 FY26 earnings will be the next major data point; (2) SNDK share exchange dilution effect may be transient in yfinance inputs; (3) WDC's fundamental business (HDD + flash in AI storage ramp) is intact. However, the framework is clear: below 76 for the current week, EXIT PENDING.

**Replacement candidate if WDC exits:** RDDT (79.4, above 76 bar, new Layer 10 AI advertising) is the highest-scoring non-portfolio name. However, RDDT was just added to the Watchlist June 24 — no thesis.md yet, no Rating Audit entries. **RDDT is GATED** until research-backed.

---

### 🌟 TSM: First ✓✓✓ Portfolio Name

TSM crossed 85 → **87.9 (✓✓✓)** in the June 24 refresh. This is the first top-tier name in the portfolio since inception. Subscore breakdown: Value 80, Quality 100, Growth 83, AI 100, Momentum 80, Risk 76. The May revenue 6-K (+30.1% YoY), CoWoS capacity expansion, and continued N2 ramp are driving the fundamentals. The ✓✓✓ tier does not trigger any framework action, but it's a milestone: TSMC is now in a class by itself within the portfolio.

---

### Weekly Performance Mark (through June 25, 2026)

| Period | Model | SMH | QQQ | SPY | EW Universe | Model α vs SMH | Model α vs QQQ |
|--------|-------|-----|-----|-----|-------------|----------------|----------------|
| Since inception (2026-05-26) | **+4.2%** ($10,417) | +5.8% | −1.8% | −1.9% | +5.1% | **−1.6%** | **+6.0%** |
| This week (June 18→25) | **−3.4%** | −3.5% | −3.2% | −1.7% | −3.0% | **+0.1%** | **−0.2%** |

Model value June 25: **$10,417** (down from $10,780 on June 18).

**Context:** Weak week across the board — AI names pulled back from highs. The model tracked nearly identically with SMH (model −3.4%, SMH −3.5%), suggesting the AI semiconductor tilt continues to be the primary driver. MU's +14.6% AH move on June 24 after market close will not fully appear in June 25 prices; the June 26 series entry should capture it. QQQ alpha inception-to-date remains strong at +6.0% — the portfolio's quality tilt continues to outperform the broader tech index meaningfully.

**50DMA refresh:** Blocked by yfinance egress. Last-known 50DMA % values from June 24 refresh are current.

---

## 🔬 Rating Integrity (Rule #12)

```
python3 scripts/audit_rating_integrity.py --summary
→ 168 rated names | 0 UNGATED (no thesis) | 0 stale (>90d)
```

**Clean for the second consecutive week.** The gate violations count reached zero in the June 19 scan (63 violations in June 12, 0 in June 19). The full-watchlist expansion to 168 names (from 163 last week) absorbed RDDT — but RDDT is a new name without AI ratings set yet, so it does not count as a gate violation.

**Flag:** RDDT was added June 24 with score 79.4. Before any subjective AI/Momentum/Risk ratings are set, RDDT will appear as ungated. Run `audit_rating_integrity.py` before assigning ratings to confirm gate status.

---

## 🎯 Layer 10 SaaS Watch: PLTR, DDOG, CRM

*Per scan instructions: specifically track net revenue retention, AI feature adoption, and pricing model shifts as key thesis risks.*

**PLTR (76.4):**
- Q1 2026: $1.633B revenue (+85% YoY). US commercial +133%. NRR 139–150%.
- Raised 2026 guidance to $7.65–7.66B (+71% YoY).
- AIPCon 10 (June 4): Customer demos across Kirkland & Ellis, McCarthy Building, USDA, Hertz — strong enterprise breadth.
- Google Cloud Marketplace + GNP Seguros + McCarthy Building partnerships.
- **Thesis read:** No NRR deterioration signal. AIP adoption metrics are strengthening, not weakening. PLTR is the clearest AI-native enterprise software beneficiary in the watchlist and does not show the pricing compression / workflow displacement that R5=2/3 names do. Disruption risk low. At 76.4, PLTR is just above the 76 bar — the question is whether it enters the portfolio if WDC exits.

**DDOG (71.0):**
- Q1 2026: $1.006B revenue (+32% YoY). NRR ~120% (recovering from 110s).
- Multi-product adoption: 56% customers using 4+ products (up from 51%), 35% using 6+.
- New AI features: MCP Server, Bits AI Security Agent, GPU Monitoring.
- **Thesis read:** NRR recovery and GPU observability are incremental positives. Agentic AI risk (R5=4 — security software; AI expands attack surface, net-neutral/tailwind) is not materializing as pricing compression. DDOG is executing on the AI tailwind thesis. No pricing shift signals this week.

**CRM (72.8):**
- No new 8-K this week specifically. Smart-money sources report fund trimming across CRM/NOW/ADBE — cited as agentic AI disruption fears.
- **Thesis read:** This week's scan did not surface a specific CRM material event. Consistent with R5=2 rating (core workflow is an agentic AI target; active erosion not yet confirmed). The fund trimming is a Momentum/Risk signal, not a Growth signal. Monitor for Dreamforce announcements (typically September) and any pricing pressure in Q2 results (Aug).

---

## Routine Filings

| Ticker | Form | Date | Summary |
|--------|------|------|---------|
| NVDA | None (meeting) | June 24 | Annual Meeting of Stockholders (online); ISC 2026: Vera Rubin platform, 35 European AI supercomputers, 81% of TOP500 runs NVIDIA. |
| ALAB | — | — | Taiwan Cloud Interop Lab expansion (June 3 press release, outside window); Annual Meeting results (June 8, outside window). |
| SNDK | — | — | Q3 FY26 earnings (April 30, outside window): Rev $5.95B +251% YoY, GM 78.4%, Q4 guide $7.75-8.25B. |

---

## New 13F Activity

None expected. Q2 2026 13F filings are not due until August 14, 2026. Most recent 13F data is Q1 2026 (filed ~May 15). Note from Q1 data: Berkshire tripled Alphabet stake; smart money trimming CRM/NOW/ADBE on agentic disruption thesis.

---

## Action Items for Dom

| Priority | Action |
|----------|--------|
| 🔴 | **Run `/earnings-update MU`** — Q3 FY26 is a massive beat ($41.5B vs $33.5B guided, 84.9% GM). Score likely crosses ✓✓✓ (~87). SCAs change business model narrative for thesis.md. |
| 🟡 | **WDC EXIT decision** — Score 71.62 (4.4pts below 76 bar). Review whether the SNDK share exchange transiently distorted yfinance inputs before confirming exit next scan. |
| 🟡 | **RDDT research** — Score 79.4, above 76 bar. Needs thesis.md before it can enter the portfolio model. Layer 10 AI advertising. |
| 🟢 | **PLTR enter decision** — Score 76.4, above bar. If WDC exits, PLTR is next-in-line with established thesis. Confirm no gate violation. |
| 🟢 | **MU SCA thesis update** — The 16 take-or-pay SCAs (~$100B) represent a qualitative business model change worth documenting in thesis.md separately from the score update. |
