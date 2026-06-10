# DDOG Q1 2026 — Earnings Delta Summary
**Earnings date:** May 7, 2026
**Prepared:** 2026-05-26

---

## 1. AI Product Revenue Traction

**Signal: Strong positive**

- 6,500 customers on AI integrations (~20% of base, ~80% of ARR) — this cohort is the high-value core
- LLM Observability span volume nearly tripled QoQ; MCP server calls quadrupled QoQ
- Landed 7-8 figure deals with two global AI research labs specifically for GPU monitoring of training workloads
- GPU Monitoring launched April 2026, addressing the "black box" problem of GPU fleet costs (~14% of compute spend)
- 5 products at >$100M ARR, 3 more at $50-100M — pipeline of products approaching scale

**What's still missing:** Management refuses to break out AI revenue as a separate line item. We cannot directly score "AI revenue mix %" for the thesis. The 80% of ARR from AI integration users is a proxy, but it conflates AI-adjacent customers (who also use core observability) with pure AI workload monitoring revenue.

---

## 2. Cloud Consumption Growth Rate

**Signal: Accelerating (positive)**

- Non-AI customer revenue growth accelerated to mid-20% YoY, up from 23% prior quarter
- Total revenue growth: 32% YoY (up from ~28% in FY2025)
- First $1B revenue quarter; ARR exceeded $4B
- Full-year guide raised from $4.06-4.10B to $4.30-4.34B (from ~19% to ~26% midpoint growth)

This is not just an AI story. The core cloud observability business is reaccelerating, likely driven by resumed cloud migration spend and platform consolidation.

---

## 3. Net Dollar Retention Trend

**Signal: Stable to slightly improving**

- TTM NRR: low 120% range (up from ~120% prior quarter)
- Gross retention: mid-to-high 90% (stable)
- Multi-product adoption deepening: 56% on 4+ products (vs. 51% YoY), 35% on 6+ (vs. 28%)

NRR in the low 120s at this scale is strong. The multi-product adoption trajectory is the leading indicator here — customers are expanding wallet share steadily. No sign of the "optimization headwinds" that plagued cloud software in 2023-2024.

---

## 4. Large Customer Growth

**Signal: Strong positive**

- $100K+ ARR customers: ~4,550 (up 21% YoY from ~3,770)
- These customers generate ~90% of total ARR
- Record new logo bookings in the quarter
- Total customers: ~33,200

The 21% growth in $100K+ customers while revenue grew 32% implies existing large customers are expanding faster than new ones are being added — consistent with the NRR story.

---

## 5. Margin and FCF Trajectory

**Signal: Stable margins at healthy levels, strong cash generation**

| Metric | Q1 2026 |
|---|---|
| Non-GAAP operating margin | 22% |
| GAAP operating margin | 1% |
| FCF margin | ~29% |
| Gross margin | 80.2% (down slightly from 81.4%) |
| SBC as % of revenue | ~20% |

- FCF of $289M in Q1 ($335M operating cash flow less capex)
- FY2026 guided non-GAAP operating margin: 22-23%
- Cash + securities: $4.8B vs. $984.5M convertible debt = net cash of ~$3.8B

The GAAP/non-GAAP gap is the critical issue for scoring. SBC of $197M on $1B revenue means GAAP EBITDA is near-zero ($34.6M TTM per yfinance), producing the 2,184x EV/EBITDA that distorted the scoring. Non-GAAP EBITDA (adding back SBC) would be ~$250M/quarter or ~$1B annualized, yielding a more meaningful ~76x EV/non-GAAP EBITDA.

---

## 6. EV/EBITDA Investigation (2,184x)

**Verdict: yfinance data quality issue — technically accurate GAAP figure, but misleading for valuation purposes.**

- yfinance reports GAAP EBITDA of $34.6M TTM and EV of $75.7B, producing EV/EBITDA of 2,184x
- This is "correct" in the narrow sense that GAAP operating income is ~$7M/quarter ($28M annualized) plus minimal D&A
- The cause: $197M/quarter in stock-based compensation (~$780M annualized) sits between GAAP and non-GAAP
- SBC is a real economic cost (dilution), so GAAP EBITDA is not "wrong" — but it renders EV/EBITDA useless as a valuation metric for DDOG
- **Better valuation anchors for DDOG:** Forward P/E (~79x on $2.40 non-GAAP EPS), EV/Revenue (~18x on $4.3B guided), or EV/FCF (~65x on annualized FCF)

**Scoring implication:** The EV/EBITDA metric should either be replaced with EV/non-GAAP EBITDA (~76x) for high-SBC software names, or flagged as N/M (not meaningful) in the scoring spreadsheet when GAAP EBITDA is distorted by SBC >15% of revenue. This is a systematic issue that will affect all Layer 10 SaaS names (CRM, NOW, SNOW, PANW, etc.).

---

## Source Log

- [Datadog Q1 2026 Press Release](https://www.stocktitan.net/news/DDOG/datadog-announces-first-quarter-2026-financial-wceudctqtekl.html)
- [Q1 2026 Earnings Transcript — Motley Fool](https://www.fool.com/earnings/call-transcripts/2026/05/07/datadog-ddog-q1-2026-earnings-transcript/)
- [Q1 2026 Earnings Transcript — Investing.com](https://www.investing.com/news/transcripts/earnings-call-transcript-datadog-q1-2026-earnings-beat-expectations-stock-surges-93CH-4668436)
- [Datadog IR — Earnings Release](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results/)
- yfinance API data pull, 2026-05-26
