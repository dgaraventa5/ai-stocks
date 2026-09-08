# DDOG — Datadog, Inc.

**Layer:** 10 Models, Software & Applications / AI observability & infrastructure software
**Last reviewed:** 2026-09-07
**Current conviction:** ✓ (TOTAL 63.4, rank #82 of 214)
**Current position size:** 0% — not a holding
**Thesis-break trigger:** The AI-native customer cohort declining in aggregate ARR for two consecutive quarters — i.e. the largest-account usage step-down disclosed in Q2 2026 generalising from one customer to the cohort.

---

## 1. One-line thesis

> Datadog is the default observability platform for cloud-native infrastructure, monetised on consumption rather than seats, so it is a levered claim on how much compute its customers actually run — which makes AI workloads a direct revenue tailwind and AI customers' spending discipline a direct revenue risk.

---

## 2. Position in the AI supply chain

- **What they do:** Unified monitoring and security across infrastructure, applications, logs and now LLM/agent workloads. Sold on consumption (hosts, ingested events, spans), landing narrow and expanding by product attach.
- **Where they sit:** Downstream of the buildout — Datadog does not sell into AI infrastructure, it observes the applications running on it. Its demand is a second derivative of compute deployed.
- **Unique vs. commoditized:** The ingest layer is genuinely commoditising (OpenTelemetry, Grafana). What is not commoditised is the correlated data estate across 100+ integrations and the workflows built on it — the moat is data gravity, not the dashboard.
- **AI revenue mix:** **Not separately disclosed.** Datadog does not break out an AI revenue line. Rated D1=3 (10–25%) on the basis that AI-native customers are a material but minority cohort; a disclosed figure would be needed to move it (rubric D1 sourcing rule).

---

## 3. Customers

| Customer | % revenue | Source / date |
|---|---|---|
| Largest customer (leading AI company, nine-figure contract, 17 products; widely reported as OpenAI) | not disclosed; ~2–4% implied vs $4.45–4.47B FY26 guided revenue | Q2 2026 call coverage, 2026-08; 8-K Ex-99.1 2026-08-06 |
| ~4,720 customers at ≥$100k ARR (+23% YoY) | — | 8-K Ex-99.1 2026-08-06 |

- **Hyperscaler exposure:** Indirect. Datadog rides on AWS/Azure/GCP rather than selling to them; it is a marketplace partner, not a supplier.
- **Concentration risk:** No customer disclosed above 10%. Rated R1=5 on that basis. **Recorded limitation:** the live exposure is *cohort* concentration in AI-native customers, which R1 (single-customer share) does not measure. Do not read R1=5 as "no concentration risk."
- **Substitution risk:** Real and rising from two directions — hyperscalers bundling native observability, and AI-native entrants (Resolve AI, $125M raised February 2026, founded by OpenTelemetry co-creators) sitting *on top of* Datadog rather than replacing it.

---

## 4. Pricing & demand

- **Pricing trend:** Consumption-priced; effective pricing is a function of customer usage, not list rates. The Q2 2026 disclosure that the largest account **renewed but reduced usage sequentially** is the first hard evidence of a spending ceiling at the top of the customer base.
- **Lead times / backlog:** N/A (SaaS). Forward visibility comes from guidance: Q3 2026 revenue $1.135–1.145B, implying ~29% YoY against 36% delivered in Q2.
- **Gross margin trend:** Not analysed this pass — **flagged as a gap**, not as clean.
- **Capacity utilization:** N/A.

---

## 5. Financials snapshot

(See `financials.xlsx` for detail. Figures below are Q2 2026 unless noted.)

| Metric | Q2 2026 | YoY change | Source |
|---|---|---|---|
| Revenue | $1.12B | +36% (fastest since 2022) | 8-K Ex-99.1 2026-08-06 |
| GAAP operating income | $5M (0% margin) | — | same |
| Non-GAAP operating income | $257M (23% margin) | — | same |
| Operating cash flow | $316M | — | same |
| Free cash flow | $279M | — | same |
| Cash + marketable securities | $5.0B | — | same |
| FY2026 guidance | $4.45–4.47B revenue; non-GAAP EPS $2.50–2.54 | — | same |

**FCF conversion (rule 11 companion check):** far above 1.0× — the mechanical high-SBC software pattern that *flatters* names like this, so it carries no information. The accrual precondition (receivables + inventory vs revenue) was **not tested** this pass.

---

## 6. Moat

- **IP / process know-how:** Breadth rather than depth — 100+ integrations, 100+ capabilities launched at DASH 2026, and the Adaptive ML acquisition (reinforcement-learning-operations, agentic LLM post-training) moving Datadog into the model layer rather than only consuming it.
- **Scale advantage:** The correlated telemetry estate. Competitors can match a feature; matching the data already resident is harder.
- **Switching costs:** High in practice — instrumentation is embedded in customer code and workflows. Evidenced by ~4,720 customers at ≥$100k ARR, +23% YoY.
- **Network effects:** Weak. Value does not rise with other customers' participation.
- **Regulatory / geographic:** None material.

**Moat rating:** Narrow-to-wide, rated D3=4. Sixth consecutive year a Gartner Magic Quadrant Leader for Observability Platforms. The bear counterweight is architectural: if the valuable layer becomes the agentic SRE sitting above the data, Datadog owns the substrate but not the interface.

---

## 7. Valuation

- **Current multiple:** P/S 17.98 — **65.5th percentile of its own 3-year range** (`expectations_flag.py`, 2026-09-07).
- **Rule 14 expectations flag:** **clean.** Rev YoY 35.6% against a 3-year median of 26.8% — growth above its own median at a mid-range multiple.
- **Rule 32-A capitulation flag:** does not fire (65.5th percentile is nowhere near the ≤10th trough).
- **What's priced in:** The market marked the stock down 15–19% on a beat-and-raise because of one disclosed customer step-down — i.e. it is pricing the *durability* of AI-native consumption, not the current growth rate. **Full scenario multiples not modelled this pass — flagged as a gap.**

---

## 8. Catalysts (next 4 quarters)

| Date | Event | Why it matters |
|---|---|---|
| Q3 2026 print | Earnings | The first quarter that *contains* the largest-customer step-down. Tests whether ~29% guided is conservative or the new run-rate. |
| Q3–Q4 2026 | AI-native cohort disclosure | Any quantification of AI-customer ARR would let D1 and R1 be rated on evidence instead of inference. |
| Ongoing | Bits AI / Agent Builder adoption | Whether agentic remediation monetises or is absorbed as table stakes. |
| Ongoing | Resolve AI and peers | Whether the over-the-top agentic SRE layer takes the customer relationship. |

---

## 9. Risks

- **Thesis-killer #1:** AI-native consumption proves structurally elastic — customers optimise spend as aggressively as the 2023–24 cloud-optimisation cycle, but permanently, because agents make usage tuning cheap.
- **Thesis-killer #2:** The agentic interface layer (Resolve AI and successors) becomes where the work happens, reducing Datadog to a commodity data store priced accordingly.
- **China / export controls:** No material direct exposure.
- **Cyclical risk:** High beta to customer cloud spend in both directions — consumption pricing has no floor.
- **Technology substitution:** OpenTelemetry commoditising ingest; hyperscaler-native observability bundled at zero marginal price.
- **Regulatory / execution:** No pending federal securities docket found in RECAP (`litigation_check.py`, 2026-09-07); one IP matter terminated 2025-05-21; remaining dockets are employment/ADA. Rated R4=5.

---

## 10. The "inverse the thesis" test

1. **If the AI-native cohort is a durable growth engine, aggregate ARR from AI-native customers grows sequentially in Q3 and Q4 2026 even as the single largest account steps down.** If instead the cohort declines two quarters running, the concentration was the growth, and D1/D5/R1 are all wrong.
2. **If the moat is data gravity, net revenue retention holds and ≥$100k-ARR customer count keeps compounding above 20% while agentic competitors raise capital.** If customer count decelerates below ~15% while Resolve AI-type entrants scale, the interface layer is winning and D3=4 is too high.

---

## Source log

- 2026-08-06 — 8-K Item 2.02 + Ex-99.1 (accession 0001628280-26-053829) — cached in `filings/`
- 2026-08-06 — 10-Q (accession 0001628280-26-054458) — cached in `filings/`
- 2026-08 — Q2 2026 call coverage (largest-customer step-down) — TradingView/Benzinga; TradingKey
- 2026 — DASH 2026 feature roundup — datadoghq.com/blog/dash-2026-new-feature-roundup-keynote/
- 2026 — Competitive read on agentic observability — StackScout; Fluidify
- 2026-09-07 — `expectations_flag.py`, `capitulation_flag.py`, `litigation_check.py`, `momentum_50dma.py`
- 2026-09-07 — Research briefing — `context-2026-09-07.md` (supersedes `context-2026-05-25.md`)

**Gap:** Q2 2026 earnings transcript not archived to `transcripts/` (rule 7). The customer-concentration specifics are sourced from press coverage of the call, not a primary transcript.

---

## Decision log

| Date | Action | Conviction | Rationale | Position size after |
|---|---|---|---|---|
| 2026-05-25 | Added to watchlist | ✓✓ | Score 75.4, Quality 100, PEG 0.7 — beat four existing portfolio names at the time | 0% |
| 2026-09-07 | Thesis written; M1 5→4 | ✓ (63.4) | Rule-12 rotation. FY guide raised but Q3 framed to ~29% on the disclosed largest-customer usage step-down | 0% |
