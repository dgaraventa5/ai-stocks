# MDB — MongoDB, Inc.

**Layer:** 10 Models, Software & Applications / AI data layer
**Last reviewed:** 2026-09-07
**Current conviction:** ? (TOTAL 49.9, rank #189 of 214)
**Current position size:** 0% — not a holding
**Thesis-break trigger:** Atlas YoY growth falling below ~25% — the cloud line is what the equity is underwritten on, and it has now printed ~29% for three consecutive quarters.

---

## 1. One-line thesis

> MongoDB is betting that agentic development multiplies the number of applications — and therefore operational database workloads — faster than it commoditises the choice of database, with the Voyage AI retrieval stack as the mechanism for capturing AI-era workloads on Atlas.

---

## 2. Position in the AI supply chain

- **What they do:** Document-model operational database, sold primarily as the Atlas managed cloud service, with a self-managed Enterprise Advanced line. The Voyage AI acquisition added embeddings and reranking, positioning Atlas as an "intelligent data platform" rather than a store.
- **Where they sit:** The data layer beneath AI applications — infrastructure for what gets built *on* AI, not for the buildout itself.
- **Unique vs. commoditized:** The document API and developer ergonomics are the durable asset; the storage underneath is not. That MongoDB is suing an open-source-compatible reimplementation is the clearest statement of where it believes the moat lives.
- **AI revenue mix:** **Not disclosed.** Four AI-retrieval capabilities went GA in Atlas and management attributes part of the strength to "early momentum with AI use cases," but there is no AI-specific revenue or consumption figure. Rated D1=2 — evidence of direction, not of magnitude.

---

## 3. Customers

| Customer | % revenue | Source / date |
|---|---|---|
| No customer disclosed >10% | — | 10-Q 2026-09-01 |

- **Hyperscaler exposure:** Atlas runs *on* AWS/Azure/GCP — they are simultaneously distribution channel and competitor (DocumentDB, Cosmos DB).
- **Concentration risk:** Low; broad developer-led base. Rated R1=5.
- **Substitution risk:** The central one. PostgreSQL with pgvector is now a credible default for both relational and vector workloads, and hyperscaler-managed alternatives are bundled into existing commitments.

---

## 4. Pricing & demand

- **Pricing trend:** Consumption-based on Atlas. **RPO $1,519.2M (+91% YoY) and cRPO $797.3M (+73%)** are growing roughly three times faster than revenue — either a large-contract mix shift or genuine forward demand. **Which of the two has not been established** and should be read out of the 10-Q before it is leaned on.
- **Lead times / backlog:** See RPO above.
- **Gross margin trend:** GAAP gross margin **74%**, up from 71% a year ago; non-GAAP 76% vs 74%.
- **Capacity utilization:** N/A.

---

## 5. Financials snapshot

(Q2 FY2027, quarter ended 2026-07-31.)

| Metric | Q2 FY27 | Prior year | Source |
|---|---|---|---|
| Total revenue | $771.8M (+30%) | — | 8-K Ex-99.1 2026-09-01 |
| Subscription / services | $747.1M (+31%) / $24.6M (+29%) | — | same |
| Atlas revenue growth | ~+29% YoY | — | same |
| Enterprise Advanced & other | ~+36% YoY | — | same |
| GAAP gross margin | 74% | 71% | same |
| GAAP operating income | $28.4M | $(65.3)M | same |
| Non-GAAP operating margin | 24% | 15% | same |
| GAAP net income | $40.9M / $0.50 diluted (3rd straight profitable quarter) | — | same |
| Free cash flow | $137.6M (nearly doubled) | — | same |
| Cash and investments | $2.4B | — | same |
| FY27 guidance | Revenue $2.99–3.03B (+21–23%); non-GAAP EPS $6.39–6.58; **Atlas growth outlook raised to ~27%** | — | same; Seeking Alpha 2026-09 |

**FCF conversion (rule 11 companion check):** above 1.0× — mechanically flattered by SBC, therefore uninformative. Accrual precondition **not tested** this pass.

---

## 6. Moat

- **IP / process know-how:** The document model and query API as a developer standard.
- **Scale advantage:** Modest. Atlas competes against hyperscalers with structurally lower infrastructure costs.
- **Switching costs:** Real but not absolute — data migration is painful, application rewrites more so; yet greenfield projects choose freely, and greenfield is where AI-era workloads originate.
- **Network effects:** Developer familiarity and ecosystem, which is the closest thing here to a network effect.
- **Regulatory / geographic:** None material.

**Moat rating:** Narrow, rated D3=3. Two-sided: MongoDB is the **plaintiff** in *MongoDB v. FerretDB* (1:25-cv-00641, D. Del., pending), defending the API surface offensively — while Atlas printing ~29% for three straight quarters is the market's verdict on whether that moat converts into compounding consumption.

---

## 7. Valuation

- **Current multiple:** P/S 10.67 — **35.0th percentile of its own 3-year range** (`expectations_flag.py`, 2026-09-07).
- **Rule 14 expectations flag:** **clean** — rev YoY 30.5% against a 3-year median of 23.0%. Growth well above its own median at a below-median multiple.
- **Rule 32-A capitulation flag:** does not fire (35.0th percentile is mid-range, not the ≤10th trough).
- **What's priced in:** A narrower, more falsifiable objection than in May. The bear case is no longer "Postgres and consumption softness" generally; it is specifically "Atlas has printed ~29% three quarters running." The stock fell ~14% premarket on 2026-09-03 despite beating on every line, because total-revenue acceleration came from Enterprise Advanced (+36%), not the cloud line. **Scenario multiples not modelled — flagged as a gap.**

---

## 8. Catalysts (next 4 quarters)

| Date | Event | Why it matters |
|---|---|---|
| Q3 FY27 print | Earnings | **Atlas YoY growth is the single number the market is watching.** Fourth consecutive ~29% would confirm the plateau. |
| Ongoing | Voyage AI monetisation | Whether GA retrieval features show up as measurable Atlas consumption. |
| Ongoing | RPO composition | Whether +91% RPO is broad bookings or a handful of large multi-year commitments. |
| Ongoing | *Baxter* (1:24-cv-05191) and derivative action | Two pending S.D.N.Y. securities matters. |

---

## 9. Risks

- **Thesis-killer #1:** Atlas growth breaks below ~25% while Enterprise Advanced carries the total — the equity is underwritten on the cloud line, and a self-managed-led mix is worth a materially lower multiple.
- **Thesis-killer #2:** pgvector-plus-Postgres becomes the default for AI application data, and MongoDB's document advantage stops mattering for new builds.
- **China / export controls:** No material direct exposure. Rated R2=4; **no geographic revenue breakout pulled this pass — flagged.**
- **Cyclical risk:** Consumption pricing transmits customer cost discipline directly into revenue.
- **Technology substitution:** The central risk (above). Two-directional on agents: coding agents could commoditise database choice, or multiply applications and therefore workloads. Management is explicitly betting on the second; no erosion is visible in retention or growth. Rated R5=4.
- **Regulatory / execution:** Two **PENDING** securities dockets — *Baxter v. MongoDB* (1:24-cv-05191, S.D.N.Y., filed 2024-07-09) and *In re MongoDB Shareholder Derivative Litigation* (1:24-cv-07594, filed 2024-10-07), both before Judge Gregory H. Woods III. Allegations, not findings; carried, not new. Rated R4=3.

---

## 10. The "inverse the thesis" test

1. **If agentic development is a tailwind, Atlas YoY growth breaks above 30% within two quarters as AI-era applications land.** If it prints ~29% or below a fourth consecutive time, the AI narrative is not reaching the revenue line and D1=2 is generous.
2. **If the document API is defensible, net expansion holds while pgvector adoption rises.** If new-workload wins visibly shift to Postgres, the FerretDB suit is defending a surface the market has already routed around.

---

## Source log

- 2026-09-01 — 8-K Item 2.02 + Ex-99.1 (accession 0001628280-26-059794) — cached in `filings/`
- 2026-09-01 — 10-Q (accession 0001628280-26-059830) — cached in `filings/`
- 2026-09-02 — Post-print reaction and Atlas-growth objection — Qz; InsiderFinance; HyperFRAME Research 2026-09-03
- 2026-09 — FY27 guidance and raised Atlas outlook — Seeking Alpha
- 2026-09-07 — `expectations_flag.py`, `capitulation_flag.py`, `litigation_check.py` (RECAP), `momentum_50dma.py`
- 2026-09-07 — Research briefing — `context-2026-09-07.md` (supersedes `context-2026-05-25.md`)

**Gap:** Q2 FY27 transcript not archived to `transcripts/` (rule 7).

---

## Decision log

| Date | Action | Conviction | Rationale | Position size after |
|---|---|---|---|---|
| 2026-09-07 | Thesis written; M2 3→4 | ? (49.9) | Rule-12 rotation. Measured +17.4pts vs IGV over six months; fundamentals inflected (24% non-GAAP operating margin, third GAAP-profitable quarter) but Atlas growth is the unresolved question | 0% |
