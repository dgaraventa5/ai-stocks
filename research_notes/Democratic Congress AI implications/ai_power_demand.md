# AI Compute and Data-Center Power Demand: State and Outlook (as of 2026-11-14)

Scope: the demand side only (how strong, how durable, how sensitive to policy), as a baseline to set against political and regulatory risk from a new Democratic Congress.

Confidence key: **High** = primary filing (SEC 8-K/10-Q/6-K, ISO document) or several consistent reports. **Medium** = one reputable secondary source, or primary data with a definitional caveat. **Low** = a single blog or aggregator, unverified.

Sourcing note: many figures come from SEC filings already logged in this repository. These are cited by EDGAR URL or by accession number, with the repo file as the trail (`tracking/hyperscaler-capex.xlsx`, `tracking/weekly-news-scan-2026-10-31.md` and `-11-07.md`, `per-stock/{T}/news-log.md`). The other figures come from web searches run 2026-11-14. Some web pages could not be fetched directly: `siliconreport.com` is blocked in this sandbox, so its claims are relayed from search snippets and marked Medium or Low.

---

## 1. Hyperscaler and AI-lab capex: latest quarter, 2026/2027 guidance, financing strain

### Takeaway
Calendar Q3 2026 capex across MSFT, GOOGL, META, AMZN and ORCL was about **$230B, up about 118% YoY** (cash PP&E from the 10-Qs). Big-4 2026 guidance sits at roughly **$720–740B**, and the Street's 2027 estimate is about **$935B (+28%)**. Spend is not slowing; it is outrunning internal cash flow. In October and November 2026 the buyers turned to external financing at scale: Meta's roughly $37.5B equity raise plus about $26B of bonds, Microsoft's first bond deal in about nine years, Oracle's $10B equity plus $10B debt at 7–8.65%, and Broadcom's roughly $43B SPV backstop. That is the main fragility in the demand picture.

### Cited Findings

**Quarterly capex, calendar Q3 2026 (cash purchases of PP&E, XBRL from 10-Qs; $M)** — High confidence. Source: `tracking/hyperscaler-capex.xlsx`, built from EDGAR XBRL.

| Company | Q3 2025 | Q3 2026 | YoY | Filing |
|---|---|---|---|---|
| AMZN | 35,095 | **77,259** | +120% | 10-Q acc. 0001018724-26-000040, filed 2026-10-30 |
| GOOGL | 23,953 | **51,355** | +114% | 10-Q acc. 0001652044-26-000084, filed 2026-10-29 |
| MSFT (FQ1 FY27) | 19,394 | **39,367** | +103% | 10-Q acc. 0001193125-26-436133, filed 2026-10-28 |
| META | 18,829 | **33,942** | +80% | 10-Q acc. 0001628280-26-066773, filed 2026-10-22 |
| ORCL (Jun–Aug qtr) | 8,502 | **28,499** | +235% | 10-Q acc. 0001193125-26-389274, filed 2026-09-11 |
| **Total** | 105,773 | **230,422** | **+118%** | sum of the above |

- The five-company total of $230.4B, +118% vs Q3 2025, is from the repo's weekly scan of 2026-11-07, `hyperscaler_capex.py` reading 10-Q XBRL. ([AMZN 10-Q index on EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-Q)) **High.**
- **Definitional caveat:** figures that include finance leases run higher. Meta's Ex-99.1 gives Q3 capex "including finance-lease principal" of **$34.91B** ([META 8-K 2026-10-21, per news-log](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=8-K)). Secondary trackers give MSFT Q3 at **$45.2B**, likely including leases, against the 10-Q cash PP&E of $39.4B ([yieldtheory tracker](https://www.yieldtheory.app/research/hyperscaler-ai-capex-tracker-2026); [mmarw](https://www.mmarw.com/intelligence/ai/hyperscaler-capex-q3-2026)). **Medium.**

**2026 full-year guidance (from Q3 calls, late October 2026)**
- **Alphabet:** 2026 capex held at **$195–205B**. For 2027, management said capex will "increase significantly"; the widely quoted ">$300B" is press framing, not guidance ([Q3 call transcript, singjupost](https://singjupost.com/alphabet-googl-q3-2026-earnings-call-transcript/); repo GOOGL news-log 2026-10-28). **High** for the 2026 range, **Medium** for the 2027 wording.
- **Amazon:** 2026 cash capex of about **$220B**, unchanged. Q4 revenue guide $240–247B. The CEO projects AWS growth "over 40% both in 2027 and in 2028." TTM FCF is **−$42.4B** ([AMZN 8-K 2026-10-29, acc. 0001018724-26-000038](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=8-K); repo AMZN context-2026-10-29). **High.**
- **Microsoft:** calendar-2026 capex reported **trimmed to about $170B from about $175B** ([search summary of Silicon Report, 2026-10-29](https://www.siliconreport.com/alphabet-amazon-meta-and-microsoft-plan-over-740b-in-capex); page not directly fetchable). **Medium/Low.** On the July call the CFO said FY27 capex "will grow year-over-year" and gave FQ1 capex as >$50B. The circulated "$255–260B FY27" figure was an analyst preview, **not guidance**, and should not be cited (repo MSFT news-log correction, 2026-10-18; [CFO Dive](https://www.cfodive.com/)). FQ1 cash PP&E of $39.4B (10-Q), or $45.2B including leases (secondary), looks **below** the ">$50B" FQ1 indication. Treat that as possible but unconfirmed: the basis of the >$50B figure is unclear.
- **Meta:** 2026 capex of **$135–145B** including finance-lease principal, narrowed from $130–145B with the low end raised. Q3 FCF was **−$2.12B**. 2027: "strong overall revenue growth" and continued aggressive investment, with no number ([META 8-K 2026-10-21](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=8-K); repo META context-2026-10-23). **High.**
- **Oracle (Investor Day, 2026-10-28):** FY30 revenue target of $225B+. Capex peaks in **FY27–28**, then steps down. FCF turns positive in 2H FY28, reaching $30B+ in FY29. Further capital raises are capped at $20B through FY30, on top of a $20B ATM already done. FY27 guide of ≥$90B revenue reaffirmed ([ORCL 8-K Item 7.01, acc. 0001193125-26-435853](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001341439&type=8-K)). **High.**
- **Aggregate:** Big-4 2026 capex of about **$720–740B**. The 2027 analyst consensus is about **$934.5B, +28%**, with Alphabet the largest implied jump at about +42%. These are third-party estimates, not guidance ([yieldtheory 2027 forecast](https://www.yieldtheory.app/research/hyperscaler-capex-2027-forecast)). **Medium** for the 2026 sum (it is arithmetic on guidance), **Low/Medium** for 2027.

**Contracted forward demand (backlog/RPO) — the durability evidence**
- **Microsoft:** commercial RPO **$677B (+73%)** at FQ1 FY27. Azure **+48%**; Microsoft Cloud $63.9B (+30%) ([MSFT 8-K Ex-99.1, 2026-10-28](https://www.sec.gov/Archives/edgar/data/789019/000119312526436122/msft-ex99_1.htm)). **High.** In July management said RPO growth was +25% excluding OpenAI, which means a large concentration in OpenAI (repo MSFT news-log). **Medium.**
- **Alphabet:** Cloud backlog **$560.8B** (+$46.9B QoQ). Purchase commitments rose to **$924.4B** from $811.0B in one quarter. Leases not yet commenced: $130.5B, from $85.2B. Backstops $75.7B; guarantees $22.8B, including $6.6B of TPU repurchase obligations ([GOOGL 10-Q Q3 2026](https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000084/goog-20260930.htm)). **High.**
- **Amazon:** contracted backlog about **$496B**, 6.4-year weighted life (Q2 10-Q). Amazon invested **$50B in OpenAI preferred**, alongside a $100B / 8-year OpenAI AWS commitment. The Anthropic relationship is a $100B / decade committed-spend contract with up to 5 GW of Trainium capacity (repo AMZN news-log 2026-09-11 and 2026-10-05, from the [10-Q filed 2026-07-31](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-Q)). **High/Medium.**
- **CoreWeave (Q3, reported 2026-11-10):** revenue about **$3.66B (+168%)**, backlog **$132.5B (+138%)**. FY26 capex guide raised to **$37–39B**. 2027 capex is "in line with 2026" if the company builds only for its committed backlog. Q3 net loss $709M. About $9B of customer prepayments is expected in the next three months, with the build financed through delayed-draw term loans ([Motley Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/11/10/coreweave-crwv-q3-2026-earnings-call-transcript/); [TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262299527-coreweave-earnings-report-q3-revenue-growth-backlog-capital-expenditures-net-loss-tradingkey)). **Medium/High.** Sources disagree on the share of backlog recognized within 24 months (26% vs 36%).

**AI labs: OpenAI/Stargate, xAI, Anthropic**
- **Stargate:** OpenAI said on 2026-04-29 that Stargate had passed its goal of **10 GW secured by 2029**. "Secured" means under contract, not online. Separately, about **8 IT-GW** was announced at PORTS-Pike, Ohio, on 2026-08-17, with no reconciled total published. Abilene (1.2 GW) had **2 of 8 buildings** operating as of June 2026 ([stargate.how](https://stargate.how/news/has-stargate-reached-10-gw); [9to5ai](https://9to5ai.tech/the-gigawatt-datacenter-race); [Wikipedia: Stargate LLC](https://en.wikipedia.org/wiki/Stargate_LLC)). **Medium/Low.** Trackers warn that the same gigawatts are double-counted across chip, cloud and site deals.
- **Oracle–OpenAI:** a $300B contract, described as 4.5 GW over five years from 2027 ([IntuitionLabs](https://intuitionlabs.ai/articles/oracle-openai-300b-deal-analysis)). **Medium.**
- **xAI:** acquired by SpaceX in February 2026 at a $250B valuation ([Wikipedia: xAI](https://en.wikipedia.org/wiki/XAI_(company))). A reported Anthropic compute lease on Colossus 1 and 2 runs about $1.25B a month from June 2026 to May 2029, about $45B in total (single trade-blog source citing a SpaceX S-1; **Low**). Reuters reported in July 2026 that 59 gas turbines were installed for Colossus 2 without federal air permits (relayed via search; **Medium**).
- **Anthropic capacity:** Google signed credit-support agreements backstopping Anthropic's 20-year, ~401 MW Hawesville lease with WULF (WULF 8-K Item 1.01, 2026-11-04, per repo weekly scan 2026-11-07). TSMC's board approved up to US$500M each in Anthropic (at IPO price) and OpenAI preferred ([TSM 6-K 2026-11-10](https://www.sec.gov/Archives/edgar/data/1046179/000104617926000797/)). **High.**

**Financing strain (Oct–Nov 2026)** — all from SEC 8-Ks; **High** unless noted.
- **Meta:** closed a **~$37.5B equity raise** ($25.0B of Class A via forward sales at $625, plus a $12.5B 6.50% mandatory convertible), then **$15.0B of USD notes** (5.85–7.50%, 2031–2056) on 2026-11-05 and **€9.0B of EUR notes** on 2026-11-12. That is three large financings in three weeks. It also created a non-voting Class C share "for capital raising" ([8-K acc. 0001193125-26-438017](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=8-K); [8-K 2026-11-12](https://www.sec.gov/Archives/edgar/data/1326801/000119312526458525/d177728d8k.htm)).
- **Microsoft:** a multi-tranche senior notes offering (2028–2066), its first US bond sale in about nine years. Reuters reported about **$25B** ([8-K acc. 0001193125-26-447173](https://www.sec.gov/Archives/edgar/data/789019/000119312526447173/d178557d8k.htm)). The total is **Medium**: it was not confirmed from the filing text.
- **Alphabet:** **€6.0B** of notes (2026-11-05). Q3 ATM use was **$12.4B**, with $27.6B remaining. Q3 FCF was **−$9.1B**. Shares fell **−12.6%** on 2026-10-29 after Q3 ([10-Q](https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000084/goog-20260930.htm); repo GOOGL news-log).
- **Oracle:** closed a **$10B common stock offering plus $10B of notes at 7.000–8.650%** (2029–2046) ([8-K 2026-11-04](https://www.sec.gov/Archives/edgar/data/1341439/000119312526447507/d131790d8k.htm)). Coupons this high on investment-grade AI debt mean the cost of credit is rising.
- **Amazon:** long-term debt face value went from **$68.8B to $133.0B in six months** (Q2 10-Q); TTM FCF −$42.4B.
- **Broadcom:** a new AI-rack residual-value backstop, with **~$43B** maximum contingent liability, to an **SPV** that finances rack purchases and leases for one unnamed customer. If it is additive to the first tranche of about $29B, the combined maximum is about $72B ([AVGO 8-K Item 2.03, acc. 0001193125-26-434271](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001730168&type=8-K)). This is vendor financing via an SPV, the private-credit-style structure the question asks about.
- **Second-tier:** IREN says **$6B of its $15B FY27 capex is unfunded** and its >$4B run-rate target slipped to January–February 2027 (EX-99.1 2026-11-05). Intel completed a **$23B equity offering** (8-K 2026-10-29). HIVE took a GPU facility at 9.0% (repo weekly scans).
- **Capex cuts:** found **only one**, Microsoft's reported ~$5B trim to CY26 (Medium/Low). No company cut 2027 plans. Meta raised the low end of its range; Alphabet guided 2027 up "significantly"; CoreWeave raised its low end.

### Inferences
- Demand intent is intact and accelerating: Q3 capex roughly doubled YoY, backlogs grew, and every 2027 statement points up. The weak point has moved from willingness to spend to **ability to self-fund**. Meta, Alphabet and Amazon all printed negative FCF, and every major buyer tapped equity or debt markets within about four weeks. This makes 2027 capex more sensitive to **credit conditions and equity-market tolerance** than to policy.
- Concentration risk: a large share of RPO and backlog traces to two counterparties, OpenAI and Anthropic, whose own spending depends on continued fundraising and IPO markets. Anthropic has an S-1 on file.
- Market stress signals: GOOGL −12.6% on its capex print; MU −5.9% on 10-29 attributed in media to capex worries; NVDA −9.3% on 11-05 in a sector selloff and about −25% after the CEO resigned on 11-11. Investors are starting to price financing risk even though the reported numbers have not decelerated.

### Gaps
- No formal 2027 capex number from any of the four hyperscalers. Microsoft's FY27 guidance from the 2026-10-28 call was not found in a primary or reliable recap. The "$170B, trimmed from $175B" figure could not be fetched (sandbox blocks siliconreport.com).
- No primary figure for Stargate's operational GW or for xAI's 2026 capital raises. The Anthropic–xAI lease terms are unverified.
- Basis mismatch (cash PP&E vs including finance leases vs calendar/fiscal) means the aggregate is roughly ±5% depending on definition.

---

## 2. AI chip and infrastructure demand signals (Nvidia, TSMC, HBM, networking, power equipment)

### Takeaway
Supply-chain signals are **stronger than the buyer-side mood**. TSMC grew 41% in Q3 and its October revenue was up about 60% YoY. SK hynix says DRAM/HBM is effectively sold out through 2029, with long-term agreements covering more than half of 2027–28. Networking (ANET +58%, ALAB +154%) and power equipment (GEV orders +96% organic) are accelerating. Nvidia reports on **2026-11-17**, against a $108B guide, under the cloud of its CEO's departure and China/export-control friction.

### Cited Findings
- **Nvidia:** Q3 FY27 guide was **$108.0B ±2%** with gross margin of 74.0%, assuming **no China data-center compute revenue**. Q2 FY27 data-center revenue was **$89.0B (+117% YoY)** and total revenue **$96.2B (+106%)** ([NVDA Q2 FY27 8-K](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000073/q2fy27pr.htm)). **High.** Results are due 2026-11-17 ([FourWeekMBA](https://fourweekmba.com/ai-nvidia-earnings-nov-17-108b-guide-89-above-a-year-ago/)). No current backlog figure found. The last explicit visibility statement was "$0.5 trillion Blackwell+Rubin through CY2026," from November 2025 and now stale ([Q3 FY26 call PDF](https://s201.q4cdn.com/141608511/files/doc_financials/2026/q3/NVDA-Q3-2026-Earnings-Call-19-November-2025-5_00-PM-ET.pdf)).
- **Nvidia policy and governance shocks:** Jensen Huang resigned as CEO and director effective 2026-11-11, with CFO Kress as interim CEO ([8-K Item 5.02, acc. 0001045810-26-000082](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=8-K)). **High.** Treasury Secretary Bessent said agencies back adding customer Megaspeed to the Commerce entity list ([The Standard / Reuters, 2026-11-13](https://www.thestandard.com.hk/news/article/348472/Bessent-blames-Commerce-Dept-over-lack-of-export-controls-for-Nvidia-partner-Megaspeed)). Reuters reported about 600,000 H200s stuck in Hong Kong awaiting Beijing approval ([The Next Web](https://thenextweb.com/news/nvidia-h200-chips-hong-kong-china-import-approval)). **Medium.**
- **TSMC:** Q3 revenue **US$46.72B (+41.2%)**, above guide. Q4 guide **US$52.3–54.3B**, gross margin 65–67% ([TSM 6-K 2026-10-15](https://www.sec.gov/Archives/edgar/data/1046179/000104617926000726/a3q26e_withguidancexfinal.htm)). October revenue was NT$586.89B, **+59.7% YoY**. The board approved about **US$40.93B** of capital appropriations for advanced-node and packaging capacity ([TSM 6-K 2026-11-10](https://www.sec.gov/Archives/edgar/data/1046179/000104617926000797/)). **High.**
- **HBM/memory:** SK hynix says its DRAM and HBM supply through **2029 is virtually sold out**, with more than half of 2027–28 capacity under long-term agreements. It sees demand outrunning supply through 2030 and HBM demand at about 2x what it can supply. Q3 revenue was **KRW 104.6T (+328%)** with operating profit of KRW 83.3T ([Financial News Korea, 2026-10-28](https://en.fnnews.com/news/202610282128013224); [Seeking Alpha](https://seekingalpha.com/news/4625688-samsung-sk-hynix-micron-sell-out-2027-memory-chip-supply-report)). **Medium/High.** Micron's FY26 10-K reports RPO of about **$134B** at minimum pricing and **$12.75B of customer deposits** (repo MU news-log, [10-K FY26](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000723125&type=10-K)). **High.**
- **Networking/optics:** **Arista** Q3 revenue was **$3.658B (+58.5%)**, beating its own guide by about 11%, with a Q4 guide of $3.9–4.0B. **Astera Labs** Q3 was **$584.9M (+154%)**, Q4 guide $730–750M (EX-99.1s 2026-11-03, repo weekly scan 2026-11-07). Corning disclosed four multibillion customer deals (repo weekly scan 2026-10-31). **High.**
- **Data-center construction and power/cooling** (Q3 8-Ks, repo weekly scan 2026-10-31; **High**):
  - **GE Vernova:** orders **$29.3B (+96% organic)**, backlog **$197B**, gas backlog plus slot reservations **122 GW**, FCF guide raised to $16–17B.
  - **Quanta:** backlog **$63.7B**.
  - **Comfort Systems:** backlog **$17.81B**.
  - **Trane:** backlog **$12.5B (+73%)**.
  - **Johnson Controls:** orders **+44%** organic.
  - **Digital Realty:** record bookings of **$855M**. **Equinix:** record bookings of **$533M**.

### Inferences
- Upstream suppliers (TSMC, memory) are capacity-allocating into **2027–2029 under prepaid or contracted terms**. That locks in a large share of the 2027 build regardless of US policy changes in 2027. Their demand is global: sovereign AI, Asian clouds, and non-US labs.
- The main near-term risk to the chip demand signal is the Nvidia governance and export-control overhang. That is a federal-policy channel (Commerce entity list, China licensing), not an end-demand problem.

### Gaps
- Nvidia's actual Q3 FY27 print and Q4 guide (2026-11-17) were not available on 2026-11-14.
- No TSMC "AI accelerator revenue share" update for 2026 was found. No optical-module (Coherent, Lumentum, InnoLight) Q3 demand data was gathered.

---

## 3. AI revenue and usage: is end-demand real?

### Takeaway
The two leading labs are at roughly **$50B (OpenAI) and $81B (Anthropic) annualized run-rates** under different methods. Cloud AI growth is accelerating: Azure +48%, AWS +39%, its fastest in about five years. This is real, fast-growing revenue, though still well short of the roughly $900B a year of capex it supports.

### Cited Findings
- **Anthropic:** run-rate revenue of about **$81B as of 2026-10-31**, up about $10B in a month. Its amended S-1 (2026-11-10) defines run-rate as trailing-28-day consumption fees × 13. Q3 2026 GAAP revenue was **$17.0B** ([24/7 Wall St., 2026-11-11](https://247wallst.com/investing/2026/11/11/anthropic-says-its-revenue-run-rate-jumped-to-an-81-billion-run-rate/); [CryptoBriefing](https://cryptobriefing.com/anthropic-revenue-run-rate-80-billion-ipo/)). **Medium/High**: it is S-1 based, but I read it through secondary reports.
- **OpenAI:** quarterly revenue crossed **$10B** for the first time, an annual run-rate of about **$50B** (Bloomberg, reported 2026-11-11). Earlier "~$70B" figures included partner revenue. OpenAI told investors it expects at least a **$70B** run-rate by year-end ([TechCrunch, 2026-11-11](https://techcrunch.com/2026/11/11/openais-quarterly-revenue-reportedly-crosses-10b-for-the-first-time/)). **Medium.** The two companies' methods differ (Anthropic grosses up cloud-partner sales), so a direct comparison is imprecise.
- **Cloud platforms:**
  - **Azure** +48%; Microsoft Cloud $63.9B (+30%, accelerating) ([MSFT Ex-99.1](https://www.sec.gov/Archives/edgar/data/789019/000119312526436122/msft-ex99_1.htm)). **High.**
  - **AWS** $46.0B (+39%, fastest in about five years) (AMZN 8-K 2026-10-29). **High.** AWS's AI business and its chips business each passed a **$25B annualized run-rate** in Q2 2026 (repo AMZN news-log 2026-09-11). **Medium.**
  - **CoreWeave** exit-2026 run-rate target of **$20–21B** ([Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/11/10/coreweave-crwv-q3-2026-earnings-call-transcript/)). **Medium.**
- **Enterprise:** ServiceNow raised its AI ACV target to **$1.7B** (repo weekly scan 2026-10-31). **Medium.**
- **Search-monetization drag:** Alphabet named lower AI Mode monetization as one Search headwind. Search growth slowed to **+12.0% from +16.8%** in Q2 (repo GOOGL news-log, Q3 call). **Medium.** AI substitution can cannibalize existing revenue as well as create new revenue.

### Inferences
- Combined lab revenue of about $130B (run-rate) plus cloud AI services makes this real demand, not speculation alone. Even so, the ratio of capex (about $730B Big-4 in 2026, plus Oracle, CoreWeave and the labs) to direct AI revenue is still several times over. The investment is a bet on continued 2–3x annual revenue growth at the labs.
- Anthropic's IPO and OpenAI's fundraising mean the demand chain now depends partly on **public-market appetite in 2027**.

### Gaps
- No credible industry-wide **token-volume** figure for Q3/Q4 2026 was found. Google, Microsoft and OpenAI token counts were not located in a dated primary source.
- No enterprise-adoption survey (Census BTOS, Ramp AI Index) for late 2026 was gathered.

---

## 4. Power demand: forecasts, interconnection queues, capacity prices, retail prices, equipment, nuclear

### Takeaway
Grid demand from data centers is the **binding physical constraint**, and it has become a **retail-price political issue**. The latest PJM base auction cleared at the **$325/MW-day cap and 6.8 GW short** of its reliability requirement. The market monitor attributes **$29.4B** of capacity costs to data centers. ERCOT's large-load queue is **~410–470 GW**, against a peak load of about 85–90 GW. Utilities are signing contracted load at record pace, with AEP at 84 GW by 2031. Equipment is sold out into 2029–30: gas turbines carry 3- to 6-year lead times, and transformers about 2.5–3 years.

### Cited Findings

**National load forecasts**
- **LBNL:** US data centers used about **183 TWh in 2024** (>4% of US electricity), projected to reach **426 TWh by 2030** (+133%) ([Utility Dive citing KHI/LBNL](https://www.utilitydive.com/news/us-data-centers-could-4x-water-use-by-2028-double-electricity-by-2030-khi/825774/)). **Medium**: a secondhand LBNL figure.
- **EPRI "Powering Intelligence 2026"** (February 2026): data centers could consume **9–17% of US generation by 2030**, about 60% above EPRI's 2024 estimate ([EPRI press release](https://www.epri.com/about/media-resources/press-release/trb5wwt7oemdbkaamxrccqkq2ktteae8); [EPRI exec summary](https://powering-intelligence.epri.com/executive-summary.html)). **High.**
- **451 Research / S&P (April 2026):** US data-center grid demand roughly triples from 2025 to **~183.2 GW by 2030**, up from 117.1 GW in its June 2025 forecast ([S&P Global](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2026/5/surging-us-data-center-power-demand-tests-sustainability-targets-101100707)). **Medium/High.**

**PJM**
- 2026 load forecast: summer peak growth of about **3.6% a year** over the next decade, vs 0.3% in the 2021 forecast. Peak rises from 160 GW (2025) to **253 GW by 2046**, driven by data centers ([PJM 2026 Load Forecast Report](https://www.pjm.com/-/media/DotCom/library/reports-notices/load-forecast/2026-load-report.pdf); [Modo Energy](https://modoenergy.com/research/en/pjm-load-forecast-data-centers-2046)). **High.**
- **2028/29 Base Residual Auction** cleared at the FERC-approved **$325/MW-day cap**, **6,831 MW short** of the reliability requirement ([Data Center Frontier](https://www.datacenterfrontier.com/energy/article/55397507/pjms-new-data-center-power-equation); [Avanza Energy](https://avanzaenergy.substack.com/p/the-164-billion-reliability-tax-how)). **Medium/High.**
- The Independent Market Monitor (report dated 2026-11-12) estimates data-center load added **$29.4B** to capacity costs across four auctions. It projects a further **$5–10B** in the December 2026 auction (2029/30) and recommends **postponing** that auction ([Energy News Beat](https://energynewsbeat.co/electrical-generation/pjms-monitor-put-29-4-billion-on-data-center-load-the-policy-fight-is-who-pays-next/); [Monitoring Analytics reports](https://www.monitoringanalytics.com/reports/Reports/2025/IMM_Analysis_of_the_20262027_RPM_Base_Residual_Auction_Part_A_20251001.pdf)). **Medium**: the 2026-11-12 report was seen only via secondary coverage.
- PJM filed a backstop capacity-procurement plan at FERC in August 2026 (search summary). **Low/Medium.**

**ERCOT**
- The large-load queue grew from **63 GW (December 2024) to ~410 GW (March 2026)**, about 87% data centers, with 198 new requests in Q1 2026 ([ERCOT board item, 2026-04-13](https://www.ercot.com/files/docs/2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf); [RTO Insider](https://www.rtoinsider.com/129421-ercot-large-load-requests-soar-again/)). **High.**
- By mid-2026 trackers cite **~466–474 GW**, with **~8.9–9.5 GW approved to energize** ([ercotqueue.com](https://www.ercotqueue.com/charts/large-load); [Corley Energy](https://www.corleyenergy.com/ercot-large-load-queue.html)). **Medium.** One tracker's 238.6 GW figure conflicts with these.
- The PUCT must finish its **SB6** large-load rulemaking (standard interconnection, transparency, curtailment) by **2026-12-31**. One source says ERCOT paused energization approvals for AI data centers of 75 MW or more; **Low**, unverified.

**Utility contracted load (Q3 2026 8-Ks; High)**
- **AEP:** 15 GW of new load commitments signed in Q3, **84 GW contracted by 2031**, $100B five-year capex (8-K 2026-10-28).
- **PPL:** about 2 GW of generation terms for a QTS data center, long-term EPS growth raised to 7–9% (2026-11-06).
- **Entergy:** expanded Google service agreement (2026-11-02).
- **Solaris Energy:** a 900 MW, 15-year contract; 3.2 GW contracted.
- **Vistra:** closed the Cogentrix acquisition (~5.5 GW of gas). Initiated 2027 EBITDA guidance of $7.7–8.5B.
- **Xcel:** a new **$6.0B ATM** to fund its build.

**Dominion and Southern:** no current contracted-GW figure gathered (see Gaps).

**Retail prices**
- EIA average residential price: **17.30¢/kWh (2025) → 18.29¢ (2026 forecast, July 2026 STEO)**, up from an 18.02¢ forecast in December 2025 ([ConsumerAffairs citing EIA](https://www.consumeraffairs.com/news/your-electric-bill-will-probably-go-up-in-2026-heres-why-122325.html); [NextMSC](https://www.nextmsc.com/industry-deep-dive/why-electricity-bills-rising-2026)). **Medium.**
- Residential prices rose **+4.9% YoY in July 2026**; Ohio bills are up >20% over two years ([NextMSC](https://www.nextmsc.com/industry-deep-dive/why-electricity-bills-rising-2026)). **Low/Medium.**
- **Attribution is contested.** FactCheck.org cites about $18/month added in western Maryland from capacity prices, with 63% attributed to data centers ([FactCheck.org, Oct 2026](https://www.factcheck.org/2026/10/data-centers-and-electricity-prices-its-not-as-simple-as-voters-may-think/)). A CEPR study finds data centers raise prices, especially for households ([CEPR/VoxEU](https://cepr.org/voxeu/columns/how-data-centres-affect-electricity-prices-and-whom)). Power bills and data centers were a key midterm issue in battleground states such as OH, MI and PA ([Forbes, 2026-11-02](https://www.forbes.com/sites/maryroeloffs/2026/11/02/data-centers-are-key-issue-in-midterm-battleground-states-as-household-electric-rates-soar/); [Star-Advertiser/Reuters, 2026-10-31](https://www.staradvertiser.com/2026/10/31/breaking-news/power-bills-and-data-centers-cast-rare-spotlight-on-utilities-in-u-s-midterms/)). **Medium/High.**

**Equipment backlogs and lead times**
- **GE Vernova:** gas backlog plus slot reservations **122 GW**; orders +96% organic (Q3 8-K 2026-10-28). **High.**
- **Siemens Energy:** gas turbine backlog **69 GW** at 2026-06-30 (15 GW booked in the quarter), with lead times of **≥3 years**. Grid Technologies (transformers) backlog **€51B**. Transformer and switchgear capacity to grow about 50% by 2030 ([Utility Dive](https://www.utilitydive.com/news/siemens-gas-turbine-backlog-nears-70-gw-as-company-expands-manufacturing/827390/)). **High/Medium.**
- **Mitsubishi Heavy:** large-frame backlog **~35 GW** (August 2026, vs 23 GW a year earlier). New orders deliver in **2028–2030** ([EUCI](https://www.euci.com/natural-gas-turbine-manufacturers-see-order-backlog-grow-as-worldwide-demand-soars/)). **Medium.** One source says 32 GW.
- Wood Mackenzie: a large US turbine ordered today takes about **6 years** to arrive. Developers are turning to used turbines, aeroderivatives and reciprocating engines ([Yahoo Finance](https://finance.yahoo.com/energy/articles/gas-turbine-shortage-just-became-210000180.html); [International Finance](https://internationalfinance.com/utilities/data-centres-turn-to-used-turbines-and-jet-engines-as-waits-stretch-into-2030s/)). **Medium.**
- **Transformers:** WoodMac Q2 2025 survey put power transformers at about **128 weeks** and GSUs at about **144 weeks**. Later reports cite >160 weeks for some substation units ([stackpath.ie](https://stackpath.ie/global/power-equipment)). **Medium.** The survey data is 2025.

**Nuclear**
- **Restarts:**
  - **Crane / TMI-1:** Microsoft, 20-year PPA, about 835 MW. Constellation targets **2027**, though one tracker says mid-2028.
  - **Palisades:** PPAs require service by **March 2027**; fuel loading began in August 2026.
  - **Duane Arnold:** Google, 25-year PPA, restart by **Q1 2029**. DOE loan up to $1.9B closed 2026-09-08.
  - DOE loans across the three total up to **$4.4B** ([AP via Courthouse News, 2026-10-16](https://www.courthousenews.com/us-is-reviving-shuttered-nuclear-plants-to-meet-growing-electricity-demand-and-to-power-data-centers/); [Michigan Public](https://www.michiganpublic.org/transportation-infrastructure/2026-10-16/united-states-nuclear-plants-palisades-michigan)). **Medium/High.**
- **New deals:**
  - **Meta:** **6.6 GW** of nuclear (Vistra uprates, TerraPower, Oklo), announced 2026-01-09 ([Introl](https://introl.com/blog/meta-nuclear-power-deal-oklo-terrapower-vistra-6gw-2026)). **Medium.**
  - **Amazon–Talen:** up to 1,920 MW through 2042.
  - **Amazon–Dominion:** a 300 MW SMR near North Anna.
  - **Google–Kairos:** 50 MW to TVA ([smrintel](https://smrintel.com/nuclear-data-center-deals/)). **Medium.**

### Inferences
- **Binding constraint, 2027–2030:** power delivery (interconnection, transmission, firm capacity) and long-lead equipment (gas turbines through 2029–30, transformers ~3 years), not chips or demand. New gas capacity ordered now mostly arrives in 2029–31. Nuclear restarts add about 2.5 GW in 2027–29, and SMRs come after 2030. Behind-the-meter and bridge generation (recips, aeroderivatives, used turbines, fuel cells) and **flexible/curtailable load** are the near-term workarounds.
- Queues are vastly speculative. ERCOT's ~470 GW requested against ~9 GW approved shows that queue numbers overstate real demand by an order of magnitude. Contracted load (AEP's 84 GW) and turbine reservations are the better demand gauges.
- The PJM capacity-cost spillover onto households is now a measurable, politically salient cost. It is the most direct link between AI demand and voter-facing pricing, and so the most likely target for regulators (state PUCs, FERC, PJM rule changes) and for Congress.

### Gaps
- **Not found:** Grid Strategies' latest five-year load forecast, EIA STEO data-center-specific numbers, BloombergNEF's US data-center outlook, and the **full LBNL report** (only secondhand).
- **Dominion** and **Southern** contracted data-center GW for Q3 2026 were not gathered. The search did not surface them, and they are not in the repo's recent scans.
- **Not verified from primary sources:** ERCOT's energization-pause claim, and the exact December 2026 PJM auction schedule (postponement recommended, not confirmed).

---

## 5. Supply constraints and timelines (2027–2030)

### Takeaway
On every supplier's own telling, demand exceeds deliverable supply through at least 2028–2030: memory to 2029–30, gas turbines into 2029–31, transformers about 3 years, nuclear restarts in 2027–29. A policy-induced demand drop would first show up as **easing of these queues**, which acts as a long buffer before supplier revenue is hit.

### Cited Findings
- Memory: sold out through 2029; shortage expected through 2030 (SK hynix, [FN News](https://en.fnnews.com/news/202610282128013224)). **Medium/High.**
- Turbines: Siemens Energy ≥3-year lead times; MHI deliveries 2028–2030; WoodMac about 6 years for a large US unit ordered now (sources in section 4). **Medium/High.**
- Construction lag: Abilene had 2 of 8 buildings live by June 2026 ([9to5ai](https://9to5ai.tech/the-gigawatt-datacenter-race)). IREN's revenue ramp slipped on "customer design change and supplier delays" (EX-99.1, 2026-11-05). **Medium.**
- CoreWeave: over 50% of its $132.5B backlog is tied to contracts with delivery starting by end-2026, but only about 26–36% is recognized within 24 months ([TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262299527-coreweave-earnings-report-q3-revenue-growth-backlog-capital-expenditures-net-loss-tradingkey); [Fool](https://www.fool.com/earnings/call-transcripts/2026/11/10/coreweave-crwv-q3-2026-earnings-call-transcript/)). **Medium.**

### Inferences
- Through about 2028 the pace of the build-out is set by **power and equipment availability**, not by demand. Even a meaningful demand cut (say −20% versus plan) would likely shorten queues rather than reduce shipments from sold-out suppliers in 2027. Names exposed to "next-dollar" demand are more exposed than sold-out bottleneck suppliers: smaller neoclouds, speculative miner-to-AI conversions, and second-tier equipment.
- Delays compound financing risk. Every quarter of slip means capital is deployed without revenue, which feeds back into the FCF and credit strain from section 1.

### Gaps
- No consolidated public estimate of how many GW of US AI data-center capacity actually **energized** in 2026, or are due in 2027, was found. SemiAnalysis public posts were not reached.

---

## 6. How policy-sensitive is the demand? (federal vs private, state and global)

### Takeaway
The **core demand drivers are mostly outside direct federal control**. Funding comes from private balance sheets and capital markets (about $900B of 2027 capex, roughly 70% from four companies). Cloud and AI revenue growth is global. TSMC and memory are allocated through 2029 to global buyers. The federal levers that do matter act mainly on **supply, cost and permitting** (power, equipment, chips to China), not on whether hyperscalers want compute. The **most binding policy risk is at the state level**: PUC large-load tariffs, siting moratoria, ERCOT/PUCT rules, and Texas's governor-elect.

### Cited Findings
- **Federal grid policy:** DOE's 2025-10-23 Section 403 directive asked FERC for a large-load interconnection rule (>20 MW) by 2026-04-30. FERC instead issued **show-cause orders to six RTOs on 2026-06-18** (50 MW+ at >69 kV), and docket RM26-4 remains open ([Duane Morris](https://www.duanemorris.com/alerts/ferc_acts_advance_data_center_large_load_integration_six_rto_regions_0626.html); [ABA](https://www.americanbar.org/groups/infrastructure-regulated-industries/resources/magazine/spring-2026/jurisdictional-collision-large-loads-data-center-interconnection/)). NERC is to file large-load registry criteria and standards by **2026-12-31**. MISO filed large-load tariff revisions on 2026-08-28 (ER26-3650). **Medium/High.** These are federal, mostly independent-commission levers. FERC is independent of Congress, but Congress can legislate and use oversight.
- **Federal financing support:** DOE loans of up to $4.4B for the three nuclear restarts ([AP / Courthouse News](https://www.courthousenews.com/us-is-reviving-shuttered-nuclear-plants-to-meet-growing-electricity-demand-and-to-power-data-centers/)). **Medium/High.**
- **Federal environmental permitting:** the reported xAI Colossus 2 turbines installed without federal air permits (Reuters, July 2026, via search summary). **Medium.** This is a Clean Air Act enforcement vector for behind-the-meter gas.
- **Export controls:** about 600,000 H200s stuck pending Beijing approval. Bessent says agencies back an entity-list designation for NVDA customer Megaspeed. Nvidia's guide already assumes zero China DC compute ([NVDA 8-K](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000073/q2fy27pr.htm); [The Standard/Reuters](https://www.thestandard.com.hk/news/article/348472/Bessent-blames-Commerce-Dept-over-lack-of-export-controls-for-Nvidia-partner-Megaspeed)). **Medium/High.** House committee chairs asked Huang to appear (2026-11-04, per repo NVDA news-log from CNBC/Bloomberg). **Medium.**
- **State policy:** Texas governor-elect **Gina Hinojosa** (Democrat, takes office January 2027) reportedly campaigned on halting new data centers. Vistra fell about 14% on 2026-11-04 and KeyBanc cut it to Sector Weight ([TIKR](https://www.tikr.com/blog/vistra-fell-14-on-the-texas-election-vote-heres-what-the-november-6-report-has-to-settle); repo VST news-log). **Low/Medium**: secondary sources only, not wire-verified. Texas SB6 rulemaking is due by 2026-12-31. A Heatmap poll found rising electricity prices to be the top reason cited for opposing a local data center (via the [FactCheck.org / search summary](https://www.factcheck.org/2026/10/data-centers-and-electricity-prices-its-not-as-simple-as-voters-may-think/)). **Medium.**
- **Midterm politics:** coverage frames power bills and data centers as midterm issues in OH, MI and PA ([Forbes](https://www.forbes.com/sites/maryroeloffs/2026/11/02/data-centers-are-key-issue-in-midterm-battleground-states-as-household-electric-rates-soar/)). One item reports Heritage and Rep. Roy tying the GOP midterm loss to AI, with Musk giving $288M ([FourWeekMBA](https://fourweekmba.com/ai-heritage-roy-tie-gop-midterm-loss-to-ai-musk-gave-288m/)). **Low**: aggregator, causation not established.
- **Global demand:** TSMC October revenue +59.7%; SK hynix has long-term deals with 14 large customers, including global CSPs; TSMC is investing in both Anthropic and OpenAI (6-Ks above). **High.**

### Inferences
- **Rough sensitivity map (judgment, not sourced):**
  - **(a) Low direct federal sensitivity:** hyperscaler willingness to spend, lab revenue growth, global semiconductor demand.
  - **(b) Moderate federal sensitivity:**
    - Export controls (China and SE-Asia diversion), which hit Nvidia volumes, not US build-out.
    - FERC/NERC large-load rules and cost allocation (who pays for transmission and capacity).
    - Federal air permitting for on-site gas.
    - DOE loans and tax credits for nuclear and clean firm power.
    - Tariffs on imported transformers, turbines and components.
  - **(c) High state and local sensitivity:**
    - PUC large-load tariffs (minimum takes, collateral).
    - Siting moratoria.
    - The Texas executive and PUCT under SB6.
    - PJM-state pressure to cap or reallocate capacity costs.
- A Democratic Congress cannot directly cut private capex. Its most plausible demand-relevant levers are indirect:
  - Ratepayer-protection mandates that push grid costs onto data centers, raising their power cost but leaving demand intact.
  - Environmental permitting scrutiny of behind-the-meter gas.
  - Oversight of export-control enforcement, which could tighten.
  - Hearings that raise the political cost of the build.
  - Possibly AI-specific legislation.

  Most of these slow the **pace** or raise the **cost** of the build-out more than they reduce its **size**. With a sitting President's veto (as of 2026-11-14), major statutory changes face long odds before 2029. Investigations and oversight are the realistic near-term tools.
- The **larger demand risk is financial, not political**. Buyers' negative FCF, rising credit spreads (Oracle at 7–8.65%), SPV backstops (Broadcom's ~$43B), and lab dependence on IPO and fundraising markets could cut 2027–28 capex faster than any likely federal action. Political noise could, however, be the catalyst that tightens those financing conditions.

### Gaps
- No quantitative estimate was found of what share of announced US data-center capacity depends on federal permits, federal land, DOE loans or tax credits.
- No found analysis specifically models a Democratic-Congress scenario for AI infrastructure. The state-level Texas policy detail (scope of Hinojosa's "halt," and the governor's authority over ERCOT and PUCT) remains unverified.
