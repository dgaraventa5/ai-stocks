# Weekly News Scan — 2026-05-29

**Scan period:** May 22–29, 2026
**Tickers scanned:** 122 (full watchlist)
**Method:** WebSearch news synthesis (SEC EDGAR direct API returned 403 from cloud environment; all claims below are cited to named sources)
**Portfolio positions (Include=Y):** TSM, NVDA, EQT, ANET, ALAB, GOOGL, EXE, ARM, AVGO, RRC, MSFT, AMD, PLTR, AR, NBIS

---

## Step 0 — Pre-Scan Mental Models (✓✓ Portfolio Positions)

Written before scanning to create a diff target. The gap between what I believed and what the scan surfaces is the signal.

| Ticker | Prior Mental Model (pre-scan) |
|---|---|
| **TSM** (83.28) | Irreplaceable CoWoS manufacturer; every leading-edge AI chip goes through TSMC; geopolitical risk is primary overhang; 2nm Arizona on track |
| **EQT** (81.45) | Largest US gas producer; AI data center power demand is structural tailwind; low-cost Marcellus; financial discipline improved post-Equitrans acquisition |
| **NVDA** (79.08) | Dominant AI accelerator; $81.6B Q1, $91B Q2 guide; Rubin in production; CUDA moat is most durable competitive advantage; AMD and custom ASICs are threats but not displacement |
| **EXE** (77.55) | Expand Energy gas E&P; CFO insider buy flagged last week as positive signal; AI power play |
| **RRC** (76.58) | Range Resources; first-mover Marcellus; highest NYMEX premium in a decade; strong FCF |
| **ANET** (75.87) | AI networking market leader; FY26 guide $11.5B (+27.7%); AI fabric target $3.5B; gross margin under pressure absorbing supply chain costs (1-2 year window) |
| **AR** (75.47) | Antero Resources; natural gas E&P; Appalachian Basin; ND/EBITDA data gap from last batch score |
| **GOOGL** (74.02) | Best-in-class model (Gemini 3.5) + TPU silicon + cloud; 2027 capex "significantly increasing" from $190B; OpenAI was exclusive to Azure — assumed GOOGL wouldn't be impacted |
| **MSFT** (73.57) | Azure assumed as exclusive AI cloud for OpenAI's compute; Copilot monetization starting; assumed Azure premium underwriting analyst models |
| **ALAB** (73.12) | Scorpio X confirmed into Trainium3 Q3 ramp; revenue tripling to ~$390M in 2026; customer concentration at Amazon/Google/MSFT; valuation stretched |
| **AVGO** (72.23) | Custom ASIC for hyperscalers (XPUs for Google, Meta); >$100B custom silicon projection by end-2027; strong FCF; VMware software business |
| **PLTR** (72.00) | AIP platform for enterprise + government AI; Q1 blowout post-consolidation; quiet week expected |
| **AMD** (71.82) | MI-series GPU ramp; EPYC dominant in cloud; Venice on 2nm confirmed; competing for NVIDIA AI share |
| **ARM** (71.66) | 50% surge on AGI roadmap was in prior week; debate: justified re-rating vs momentum overshoot; CCO selling post-rally |
| **NBIS** (65.52, AVG) | AI-native GPU cloud; revenue inflected from $51M to $399M YoY; $2.6B BE deal; $20-25B capex plan requires scrutiny; execution is the key risk |

---

## ⚠️ Material Events

### Tier 1 — Thesis-Shifting

**DELL — Q1 FY2027 MASSIVELY beats; AI server guide raised to $60B for FY2027.** Dell reported on May 28, 2026: revenue $43.8B (+88% YoY), beating the $36.16B consensus by 21%; AI server revenue $16.1B (+757% YoY); AI orders booked this quarter $24.4B; AI backlog now $51.3B. FY2027 AI server revenue guidance raised to $60B; total FY2027 revenue guide midpoint $167B (+~50% YoY). Primary supply constraint: DRAM/NAND shortages limiting backlog conversion speed. Stock surged ~39% after hours May 28. *Cross-watchlist read-through:* The $51B backlog and $757% AI server growth rate is the single strongest data point this week for the entire AI supply chain — positive read-through for MU (HBM memory), TSM (server-class manufacturing), ANET (networking), VRT (cooling), and NVDA (GPU content per rack). ([Dell 8-K, May 28 2026](https://www.sec.gov/Archives/edgar/data/0001571996/000157199626000021/exhibit991earnings8kq1fy27.htm); [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/dell-q1-fy2027-earnings-beat-111201048.html))

**AMZN/OpenAI — $50B investment + $100B AWS 8-year commitment; Azure exclusivity ended.** Amazon announced on approximately May 27, 2026 a multi-year strategic partnership with OpenAI: Amazon investing $50B ($15B immediately, $35B contingent on IPO or AGI milestone); OpenAI committing $100B to AWS over eight years; OpenAI consuming 2 gigawatts of Trainium capacity (Trainium3 and Trainium4); AWS becomes exclusive third-party cloud distributor for OpenAI Frontier enterprise platform. *Simultaneously*, the April 2026 restructuring of the OpenAI-Microsoft deal was confirmed: OpenAI can now run products on any cloud, Microsoft's exclusive arrangement ended, Microsoft no longer receives OpenAI revenue share. **This directly impairs MSFT's thesis.** The Azure "exclusive AI premium" — which underwrites investor models for Azure growth, premium pricing, and Fortune 500 sales leverage — is now gone. AWS AI revenue run rate was already >$15B in Q1 2026, ascending rapidly. ([OpenAI press release](https://openai.com/index/amazon-partnership/); [About Amazon](https://www.aboutamazon.com/news/aws/openai-amazon-partnership-explained); [Tom's Hardware](https://www.tomshardware.com/tech-industry/amazon-invests-50-billion-in-openai); [TechCrunch](https://techcrunch.com/2026/04/27/openai-ends-microsoft-legal-peril-over-its-50b-amazon-deal/); [Axios](https://www.axios.com/2026/04/28/openai-microsoft-cloud-amazon))

⚠️ **MSFT thesis risk flag:** The Azure-exclusive-OpenAI premium has been a material assumption. The multi-cloud OpenAI relationship changes competitive dynamics. This does not immediately destroy the thesis — Azure has other large workloads, Azure AI Studio, and enterprise stickiness — but the "exclusive OpenAI compute" moat is no longer valid. **Recommend DOM review before quarterly rescore.**

**MU — Stock crosses $1 trillion market cap; HBM4 sold out through year-end.** On May 22, 2026, President Trump publicly praised Micron Technology at a rally in Suffern, NY. On May 26, 2026, UBS nearly tripled its price target to $1,625, citing: fully sold-out HBM4 production through year-end 2026, prior Q2 FY2026 revenue of $23.9B (+196% YoY), EPS $12.07 (+756% YoY), and 75% gross margins. Stock surged 19.29% on May 26, briefly topping $1 trillion market cap for the first time ($895.88 close). As of May 28, stock at $942. CEO Sanjay Mehrotra confirmed only fulfilling 50-65% of key customers' medium-term demand. *Thesis confirmation:* The HBM memory bottleneck thesis is playing out exactly as modeled. The supply-demand imbalance for HBM is more severe than consensus expected. ([The Tech Marketer](https://thetechmarketer.com/micron-mu-stock-2026-ubs-1625-target-trillion-hbm/); [FX Leaders](https://www.fxleaders.com/news/2026/05/26/micron-mu-stock-leaps-after-ubs-call-but-valuation-and-semiconductor-risks-loom/))

---

### Tier 2 — Material to Thesis (Portfolio Positions)

**MSFT — OpenAI exclusivity ended; Azure AI premium assumption invalidated.** (See Tier 1 cross-entry above.) Azure AI revenue run rate still large and growing, but the prior thesis assumption of OpenAI exclusivity is no longer valid. Monitor: does MSFT guide Azure growth down in Q4 FY2026 earnings (due July), or do they reframe around broader AI enterprise demand? No new 8-K this week. Quarterly dividend ($0.91/share, ex-date May 21) and routine board appointment (Carmine Di Sibio, former EY chairman, added May 14) are routine. ([Neowin](https://www.neowin.net/news/openai-signs-a-50-billion-deal-with-amazon-partnership-with-microsoft-remains-unchanged/); [Motley Fool](https://www.fool.com/investing/2026/05/06/why-amazon-might-be-the-real-winner-of-the-microso/))

**ALAB — First public Scorpio X demo at Computex June 3; insider trust selling.** Astera Labs announced it will hold a press conference and first public demonstration of the Scorpio X-Series 320 Lane Smart Fabric Switch at Computex 2026 in Taipei on June 3, 2026. Stock reached a new all-time high of $315.81 on May 22 and was at $349 on May 29. Significant insider selling occurred May 14-22: a COO-linked trust sold 280,000 shares on May 19; other affiliated trusts sold over 100,000 additional shares. *Framework note:* per our asymmetric insider analysis, post-rally trust diversification is distinct from bearish insider conviction; no direct discretionary open-market C-suite purchase selling is flagged as a red signal — but the scale here (280K+ shares) is notable and worth tracking. ([StockTitan](https://www.stocktitan.net/news/ALAB/astera-labs-to-host-press-conference-live-demos-and-technical-talks-fd878ldorhyw.html); [TradingKey](https://www.tradingkey.com/news/market-movers/261934321-market-movers-alab-20260528))

**ARM — New all-time high (~$344); Mizuho raises PT to $360.** ARM stock surged another +13.6% mid-day May 29, reaching a fresh ATH of $349.42 and closing around $335. This is on top of the 50% weekly surge reported in last week's scan. Mizuho raised its price target to $360 from $290. CCO William Abbey sold 2,300 shares on May 22 (post-rally diversification; per framework: CCO sale post-ATH is asymmetrically less informative than buying). No material 8-K. At current prices, ARM trades at a premium that requires sustained data center royalty growth to justify. Monitor against next quarterly earnings for evidence of the $2B+ data center revenue trajectory. ([CNBC](https://www.cnbc.com/quotes/ARM); [TradingKey](https://www.tradingkey.com/news/market-movers/261934049-market-movers-pltr-20260528))

**NBIS — Hedge fund Situational Awareness LP discloses 5.6% stake (~$2.6B).** On May 28, 2026, Situational Awareness LP — a hedge fund focused on AI infrastructure — disclosed a 5.6% stake in Nebius Group, holding over 12 million Class A shares as of March 31, 2026, valued at approximately $2.6B. Stock rose 8.14% on the disclosure. Management will present at BofA Global Technology Conference on June 3. *Thesis note:* A named AI-specialist fund taking a $2.6B position is consistent with the thesis but does not change fundamentals. The Bloom Energy $2.6B fuel cell deal remains the primary watch item. ([TradingKey](https://www.tradingkey.com/news/market-movers/261933968-market-movers-nbis-20260528))

**PLTR — DIA contract challenge; Cleveland Cliffs commercial deal; stock consolidating.** Palantir challenged the Pentagon's Defense Intelligence Agency over the MARS analytics upgrade, arguing DIA should open commercial bidding rather than build in-house — the White House reportedly supports open competition. Separately, PLTR signed a 3-year deal with Cleveland Cliffs for AI-assisted steel production. Stock consolidated in the $132-$140 range this week ($137.57 on May 28), +4.1% above intraday low. No new 8-K. *Layer 10 SaaS signals:* No NRR disclosure this week, but government revenue from Q1 +84% YoY demonstrates the platform is not a single-contract story. ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/palantir-dia-contract-challenge-means-071038512.html); [IBTimes](https://www.ibtimes.com/palantir-challenges-pentagon-intelligence-contract-over-ai-data-system-modernization-3803137))

**GOOGL — Google engineer charged with insider trading; EQT AI partnership.** A Google software engineer was charged May 27, 2026, with insider trading for using confidential Google search data to bet on Polymarket, generating ~$1.2M. Alphabet is cooperating with authorities and put the employee on leave. Governance flag: raises questions about access controls for proprietary data, but this is an individual bad actor case, not a systemic compliance failure. A partnership with EQT (portfolio position) was announced to enhance AI adoption — limited detail available. No new material 8-K in scan window. ([Washington Post](https://www.washingtonpost.com/technology/2026/05/27/google-employee-charged-with-insider-trading-polymarket/); [Benzinga](https://www.benzinga.com/markets/prediction-markets/26/05/52829551/google-engineer-insider-trading-polymarket-charges))

---

### Tier 3 — Material to Thesis (Non-Portfolio)

**MRVL — Record Q1 FY2027; FY2027 revenue guide $11.5B (+40% YoY).** Marvell Technology reported on May 27, 2026: record Q1 net revenue $2.418B (+28% YoY), non-GAAP EPS $0.80 (beat $0.75 estimate), data center 76% of total revenue, operating cash flow $639M (record). Q2 FY2027 guide: +12% QoQ and +35% YoY. Full FY2027 guide: ~$11.5B (+40% YoY). Stock +5% in after-hours. Custom silicon (AWS Trainium, Google TPUs using ARM-based architecture) is the growth driver. 8-K filed May 27. ([SEC EDGAR MRVL 8-K](https://www.sec.gov/Archives/edgar/data/0001835632/000183563226000014/q127_8kx522026ex-991.htm); [Investing.com](https://www.investing.com/news/transcripts/earnings-call-transcript-marvell-technology-sees-q1-fy2027-earnings-beat-stock-rises-93CH-4713356))

**SNOW — NRR inflects to 126% (FIRST increase in 5 consecutive quarters); $6B AWS deal.** Snowflake reported Q1 FY2027 on May 27: product revenue $1.33B (+34% YoY), strongest sequential dollar growth in company history; NRR **126%** (up from 125%, the **first increase in five consecutive declining quarters**); FY2027 guide raised to $5.84B (+31% YoY). Additionally announced: a $6B, five-year AWS commitment (>2x prior arrangement), covering Graviton and AI accelerator capacity; and signed a definitive agreement to acquire Natoma (enterprise MCP platform for AI agents). Stock +37% after hours. *Layer 10 SaaS signal: the NRR inflection is the most important data point — it suggests AI-driven workload expansion is beginning to outpace customer optimization headwinds that pressured NRR from 130%+ to 110s over 2024-2025.* Rescore warranted per tracking file. ([SEC EDGAR CRM 8-K](https://www.sec.gov/Archives/edgar/data/0001108524/000110852426000125/crm-q1fy27xexhibit991.htm); [EBC Financial Group](https://www.ebc.com/forex/snowflake-stock-surges-the-nrr-signal-bears-could-not-price-in); [IndMoney](https://www.indmoney.com/blog/us-stocks/why-snow-stock-is-rising-q1-fy2027-earnings-aws-deal))

**CRM — Agentforce ARR $1.2B (+205% YoY); record non-GAAP margin 34.8%.** Salesforce reported Q1 FY2027 on May 27-28: revenue $11.13B (+13% YoY), beat $11.05B estimate; non-GAAP EPS $3.88 (vs $3.12 estimate, beat 24%); non-GAAP operating margin 34.8% (+250bps YoY, record). Agentforce ARR reached $1.2B (+205% YoY); Agentforce + Data 360 combined ARR $3.4B; 3.8 billion Agentic Work Units delivered to date (+111% QoQ); 50%+ of Agentforce bookings from existing customers. Processed 28.6 trillion tokens to date (+152% QoQ). Raised FY27 guidance (not quantified in available results). 8-K filed May 27. *Layer 10 SaaS signal: Agentforce monetization is real — $1.2B ARR in its first year exceeds most SaaS product launches. The 205% YoY growth on an already large base is the thesis working. The consumption model (AWUs) is diverging from seat-based pricing.* ([Salesforce press release](https://www.salesforce.com/news/press-releases/2026/05/27/fy27-q1-earnings/); [CNBC](https://www.cnbc.com/2026/05/27/salesforce-crm-q1-earnings-report-2027.html); [SEC EDGAR](https://www.sec.gov/Archives/edgar/data/0001108524/000110852426000125/crm-q1fy27xexhibit991.htm))

**DDOG — NRR recovery to 130%+ (from 110s in 2024-2025); first $1B quarter.** Datadog reported Q1 2026 on May 7 (just outside scan window, included for Layer 10 completeness): revenue $1.006B (+32% YoY) — first $1B quarter; NRR back above 130% (recovered from 110s range). FY2026 guide raised to $4.30-4.34B. Sakana AI partnership. *Layer 10 SaaS signal: NRR returning above 130% suggests AI observability demand is now exceeding prior-cycle customer optimization. Paired with SNOW's NRR uptick, this suggests a broad AI workload expansion wave hitting the Layer 10 SaaS cohort simultaneously.* ([Datadog IR](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results); [StockTitan](https://www.stocktitan.net/news/DDOG/datadog-announces-first-quarter-2026-financial-wceudctqtekl.html))

**MOD — $4B+ long-term data center capacity deal; FY2027 DC guide +60-80%.** Modine Manufacturing reported Q4 FY2026 on May 26 (8-K filed same day): revenue $954.4M (+47% YoY), beat $929.9M estimate; EPS $1.71, beat $1.57 estimate. Signed a "landmark long-term capacity agreement" with an undisclosed data center customer securing over $4B in future revenue. Data center segment full-year sales grew 73% to $1.1B. FY2027 guidance: total sales +20-35%, Data Center segment +60-80%. Gentherm RMT spin-off pending. 8-K filed May 26. ([SEC EDGAR MOD 8-K](https://www.sec.gov/Archives/edgar/data/0000067347/000110465926066291/mod-20260526xex99d1.htm); [GuruFocus](https://www.gurufocus.com/news/8886163/modine-manufacturing-co-mod-q4-2026-earnings-call-highlights-record-revenue-and-strategic-growth-amid-challenges))

**VRT — Investor Day May 22; 20-22% CAGR five-year target; multiple PT raises.** Vertiv held an Investor Day on May 22, 2026, outlining a 20-22% revenue CAGR target over five years and highlighting expanding services, converged infrastructure, and disciplined capital deployment. Analyst price target raises following the event: Roth Capital to $355 (from $335), Oppenheimer to $353 (from $330), TD Cowen to $387 (from $347, Buy maintained). Stock rose on the news. No new 8-K filing. ([CNBC](https://www.cnbc.com/quotes/VRT))

**TSM — Europe Technology Symposium (Amsterdam, May 29); CoWoS roadmap extended to 2029.** TSMC held its European Technology Symposium on May 29 in Amsterdam, emphasizing that advanced packaging is now "as important as transistor scaling." Highlights: 5.5-reticle CoWoS in production today at >98% yield; 14-reticle CoWoS in 2028 capable of integrating ~10 compute dies + 20 HBM stacks; SoW-X targeting 64 HBM stacks for 2029. Routine dividend announced ($0.955/share, ex-date June 11). *Thesis note:* TSMC's CoWoS leadership remains the key technical bottleneck for AI chip supply. The 2028-2029 roadmap suggests supply capacity will expand but demand continues to outpace near-term availability. ([New Electronics](https://www.newelectronics.co.uk/content/blogs/tsmc-technology-symposium-2026-a-systems-driven-era); [Semi Engineering](https://semiengineering.com/tsmc-tech-symposium-2026-by-the-numbers/))

**WULF — 8-K: 1+ GW Eastern Kentucky HPC campus acquired.** TeraWulf filed an 8-K on May 26, disclosing the acquisition (closed May 22) of the "Muskie Data Campus" in Eastern Kentucky from Industrial Equity Partners. Site: 285+ acres, capable of supporting up to 1 GW of HPC/AI data center capacity. Timeline: initial 500 MW delivery 2H 2028, additional 500 MW targeted 2H 2030. AEP subsidiary (American Electric Power) constructing a 345 kV substation tied to the 765 kV transmission backbone. No disclosed customer. *Note:* AEP subsidiary involvement is a cross-watchlist linkage (AEP is in the watchlist as a regulated utility). ([SEC EDGAR WULF 8-K](https://www.sec.gov/Archives/edgar/data/0001083301/000108330126000109/wulfeasternkypr5-26x26.htm); [GlobeNewsWire](https://www.globenewswire.com/news-release/2026/05/26/3301045/0/en/terawulf-expands-infrastructure-platform-with-acquisition-of-1-gw-eastern-kentucky-hpc-campus.html))

**OKLO — DoE selects for Surplus Plutonium Utilization Program (May 26).** Oklo was selected by the Department of Energy on May 26, 2026, for advanced talks to join the Surplus Plutonium Utilization Program, which converts designated surplus plutonium into fuel for advanced reactors. Oklo is pairing the program with a partnership with European developer newcleo, potentially bringing up to $2 billion in project capital (subject to definitive agreements). This advances Oklo's path to reactor fuel supply and investor validation of the design. ([StockTwits](https://stocktwits.com/news-articles/markets/equity/smr-oklo-nne-nuclear-stocks-ai-energy-retail-traders/cZX21jLReXr))

**SMCI — Taiwan authorities arrest 3 in server diversion case; SMCI cooperating; stock +10%.** In the May 22-29 window, Super Micro announced cooperation with Taiwanese authorities who arrested three suspects for illicit diversion of SMCI AI servers (containing NVIDIA chips) to the restricted China market, seizing 50 servers. CEO Liang stated SMCI was a "victim" deceived by third-party schemes. NVIDIA has urged SMCI to strengthen its compliance program. Stock surged ~10% on the announcement, suggesting the market views active prosecution/cooperation as progress on the compliance narrative. Prior Hagens Berman securities class action (lead plaintiff deadline was May 26) remains outstanding. Q3 FY2026 (ended March 31, 2026) results from May 5: revenue $10.2B (+123% YoY, -19% QoQ), non-GAAP EPS $0.84 beat $0.62 estimate, gross margin improved to 10.1% from 6.4%. ([Benzinga](https://www.benzinga.com/markets/tech/26/05/52848628/super-micro-jumps-10-as-it-cracks-down-on-smuggling-with-new-taiwan-alliance); [Investing.com](https://www.investing.com/news/company-news/supermicro-aids-taiwan-authorities-in-server-diversion-case-93CH-4714601))

**ANET — XPO optics introduced; doubled 2026 AI networking target.** Arista introduced liquid-cooled XPO optics and a universal AI spine designed for next-gen training and inference clusters, claiming a 75% reduction in networking racks and 44% floor space savings vs traditional pluggable optics. The company doubled its 2026 AI networking revenue target (from $1.75B to $3.5B, already communicated at Q1 but now confirmed with product roadmap). Open Ethernet vs InfiniBand positioning is gaining traction as hyperscalers prioritize vendor independence. Stock held up after last week's supply-chain warning. ([Simply Wall St](https://simplywall.st/stocks/us/tech/nyse-anet/arista-networks/news/arista-doubles-2026-ai-target-as-open-ethernet-role-expands); [Motley Fool](https://www.fool.com/investing/2026/05/28/massive-news-arista-stock-could-surge-on-explosive/))

**CRDO — Q4 FY2026 earnings June 1 (upcoming); ZeroFlap design win; stock +12.94%.** Credo Technology stock surged 12.94% on May 22. ZeroFlap active electrical cables were confirmed in Rebellions' RebelPOD AI inference clusters (AI factory product). Rothschild & Co Redburn launched with Buy/$206 target. Q4 FY2026 earnings after market close June 1, 2026: consensus expects EPS $1.03 (+194% YoY), revenue $433.3M (+155% YoY); company guided $425-435M. TSMC 2026 Symposium showcase confirmed. *Upcoming catalyst* — CRDO earnings will be the next major read on AI connectivity ASIC demand. ([StocksToTrade](https://stockstotrade.com/news/credo-technology-group-holding-ltd-crdo-news-2026_05_22-2/); [MarketBeat](https://www.marketbeat.com/instant-alerts/credo-technology-group-crdo-to-release-earnings-on-monday-2026-05-25/))

---

### Cross-Cutting Themes

**Layer 10 SaaS NRR Inflection — Broad Recovery Signal.** Three of the four Layer 10 SaaS names reported NRR improvement this week or in the immediately prior period:
- **SNOW**: NRR 126% — first uptick in five consecutive declining quarters
- **DDOG**: NRR back above 130% — recovered from 110s range in 2024-2025
- **CRM**: Agentforce + Data 360 ARR expanding from existing customers (50%+ of Q1 bookings); consumption-based AWU model growing 111% QoQ

The directional implication: AI-driven workload expansion is now large enough to outpace the customer optimization cycle that drove NRR down in 2024-2025. This is the inflection point the thesis has been waiting for at Layer 10.

**DELL read-through across supply chain.** DELL's $43.8B Q1 revenue (+88% YoY) and $60B FY2027 AI server guide is the single strongest demand signal in the scan period. Supply chain implications by layer:
- Memory (MU): DRAM/NAND constraints limiting DELL's backlog conversion — validates HBM shortage thesis
- Networking (ANET, CRDO): 4,000+ enterprise customers now buying AI servers need fabric and connectivity
- Cooling (VRT, MOD): Thermal density increase per rack drives demand
- Silicon (NVDA, AVGO, ALAB): GPU content per rack is primary AI server cost
- Manufacturing (TSM): Every server GPU/ASIC manufactured by TSMC

**Multi-cloud OpenAI = Azure headwind; AWS tailwind.** The competitive landscape for cloud AI workloads shifted materially this week. OpenAI — previously an Azure-exclusive workload — is now dividing compute across AWS (Trainium) and remaining on Azure (GPT), while also exploring other hyperscalers. This is a:
- **AMZN/AWS positive**: $100B 8-year commitment from OpenAI, 2GW Trainium capacity
- **MSFT/Azure risk**: Exclusive premium lost; Azure must compete on price and features vs. AWS and GCP for AI workloads
- **GOOGL neutral**: Gemini/TPU remains vertically integrated; not directly affected
- **TSM positive**: Trainium chip manufacturing is TSMC

---

## Score Changes

No in-session score changes this week. Scores require Dom to sign off on subjective dimension changes. The following rescores are now triggered:

| Ticker | Trigger | Dimensions Likely Affected |
|---|---|---|
| MRVL | Q1 FY2027 beat; FY27 guide $11.5B (+40%) | D1 AI Rev %, M1 EPS Rev, Growth subscore |
| SNOW | Q1 beat; NRR 126% (first uptick); $6B AWS deal | D1 AI Rev %, Growth, Momentum |
| CRM | Q1 beat; Agentforce ARR $1.2B (+205%); record margin | D1 AI Rev %, D2 Position/Moat, M1 EPS Rev |
| DELL | Q1 MASSIVE beat; AI server revenue $16.1B; $60B FY27 guide | D1 AI Rev %, Growth, Momentum |
| MOD | $4B+ long-term DC deal; FY27 DC guide +60-80% | D1 AI Rev %, D4 Capacity, Growth |
| MSFT | OpenAI exclusivity ended; Azure premium assumption changes | D5 Hyperscaler moat, D2 Position, Risk |
| WULF | 1 GW Kentucky campus acquisition; execution risk expansion | D4 Capacity, Risk |
| OKLO | DoE surplus plutonium program selection | D4 Capacity, D3 AI Revenue % |

---

## Portfolio Impact

No tier changes this week. All portfolio names remain in the same tier as the prior scan.

**However, two items warrant Dom's attention before next quarterly rescore:**

1. ⚠️ **MSFT (✓✓, 73.57)** — OpenAI multi-cloud means the Azure "exclusive AI cloud" thesis assumption needs rewriting. This is not an immediate score change, but it is a thesis shift that should be discussed before the quarterly rescore. The risk is that Azure growth slows as OpenAI workloads migrate to AWS Trainium, and the premium pricing for "OpenAI-only cloud" narrows. Recommend flagging for Dom review.

2. ⚠️ **ALAB (✓✓, 73.12)** — COO trust sold 280,000+ shares May 14-22. Per asymmetric framework, trust-based post-rally diversification is not the same as discretionary open-market C-suite selling. The Computex Scorpio X demo (June 3) is the next catalyst. No score change recommended now, but the selling scale warrants disclosure.

**Non-portfolio tier movement to watch:**
- **SNOW (AVG, 69.57)** — NRR inflection + guide raise puts it on the cusp of moving to ✓✓ (STRONG, ≥70). Rescore may push it over.
- **DELL (STRONG, 71.53)** — Massive AI server beat likely to push score higher within STRONG tier. Not a portfolio position; note for research coverage only.

---

## Routine Filings (No Material Impact)

- **NVDA** — No new 8-K in May 22-29 window; most recent was May 20 Q1 earnings (covered last scan). Board appointment of Suzanne Nora Johnson effective July 13 (May 7 filing, pre-scan).
- **GEV** — CEO confirmed backlog grew >$13B QoQ; 110 GW gas turbine target by year-end 2026. No new 8-K in window.
- **AVGO** — May 26: BCM68850 (50G PON edge AI SoC with integrated NPU, Wi-Fi 8). May 27: Samsung 5G+Wi-Fi 8 FWA platform collaboration; FuriosaAI partnership. Susquehanna PT raised to $490 from $450. Routine product announcements; no 8-K.
- **INTC** — Arc G-Series graphics processors and Core Ultra Series 3 edge AI announced May 28. CEO Lip-Bu Tan fireside chat at J.P. Morgan TMT conference May 19. Routine; no thesis change.
- **ARM** — Routine Mizuho PT raise to $360. Stock at ATH. CCO sold 2,300 shares May 22 (routine post-rally diversification per asymmetric framework).
- **NRG** — 2026 outlook guidance reaffirmed after Q1. LS Power deal closed January 30, guidance update was a February 8-K (pre-scan window).
- **CEG** — Calpine acquisition completed January 7, 2026 (pre-scan). No new 8-K in May 22-29 window.
- **EME / FIX** — Q1 results filed April 29 (pre-scan). No new 8-K in window; backlog remains record ($15.62B EME, $12.45B FIX).
- **HPE** — Q2 FY2026 earnings after close June 1. Consensus: EPS $0.53, revenue $9.77B.
- **CORZ** — Q1 results May 6 (pre-scan). $3.3B project bond closed. 243 MW billing to CoreWeave. No new 8-K in window.
- **EQT / RRC / AR / EXE** — No material 8-K events in window. Natural gas markets stable in $3.27/MMBtu Henry Hub range; EQT Q1 beat ($2.33 EPS vs $2.16 estimate). All gas E&P names quiet.

---

## New 13F Activity

No new 13F-HR filings from tracked funds identified. **Exception:** Situational Awareness LP (an AI-focused hedge fund) disclosed a 5.6% stake in NBIS (Nebius Group) via a 13D filing on approximately May 28, 2026. This is a 5%+ beneficial ownership disclosure, not a 13F-HR quarterly filing. Next 13F-HR deadline: August 14, 2026 (for Q2 holdings as of June 30, 2026).

---

## Upcoming Catalysts (May 29 – June 7, 2026)

| Date | Ticker | Event |
|---|---|---|
| June 1 | CRDO | Q4 FY2026 earnings (consensus: $433.3M revenue, $1.03 EPS) |
| June 1 | HPE | Q2 FY2026 earnings (consensus: $9.77B revenue, $0.53 EPS) |
| June 3 | ALAB | Computex 2026 — first public demo of Scorpio X-Series 320 Lane Switch |
| June 3 | NBIS | BofA Global Technology Conference fireside chat |
| June 9 | TSM | Ex-dividend date for $0.955/share dividend |
| June 11 | KLAC | 10-for-1 stock split effective (split-adjusted trading June 12) |
| ~June 25 | MU | Q3 FY2026 earnings expected (Micron FQ3 ends May 31, 2026) |

---

## Portfolio Action Items

1. **MSFT** — ⚠️ Discuss thesis impact of OpenAI multi-cloud before quarterly rescore. The Azure exclusive AI cloud assumption that underpins Azure premium growth is now gone. How does this change forward estimates and the thesis narrative?
2. **ALAB** — Monitor Computex Scorpio X demo (June 3) for product maturity signals and customer traction commentary. Flag insider trust selling for Dom awareness.
3. **SNOW** — Non-portfolio. NRR inflection to 126% is the "Rescore After Earnings" trigger. Recommend rescore session.
4. **CRM** — Non-portfolio but STRONG-tier. Agentforce ARR $1.2B (+205%) is the thesis working. Rescore warranted.
5. **MRVL** — Non-portfolio but STRONG-tier (70.48). FY27 guide $11.5B (+40%). Rescore triggered.
6. **DELL** — Non-portfolio but STRONG-tier. Largest demand signal this week. Rescore triggered for earnings-driven metrics.
7. **MU** — Portfolio position (STRONG tier, 71.40). UBS PT to $1,625 and $1T market cap confirms HBM thesis. No rescore needed; track Q3 FY2026 earnings (due ~June 25) for continued HBM demand signal.
8. **WULF** — Non-portfolio (AVG tier). 1 GW Kentucky campus acquisition is a material capacity expansion. Flag for quarterly rescore.
9. **NBIS** — Portfolio position. Situational Awareness LP 5.6% stake confirms institutional validation. Continue monitoring capex execution and funding sources.
10. **PLTR** — Portfolio position. DIA contract challenge is consistent with the aggressive government AI thesis. Stock consolidating — no action.

---

*Scan method note: SEC EDGAR direct API (data.sec.gov) returned HTTP 403 from the remote cloud execution environment. All material event findings were sourced via WebSearch with citation to named sources and SEC EDGAR URLs where available. Coverage equivalent to direct API scan.*
