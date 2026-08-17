# Weekly rating refresh — 2026-08-17

> **PR fallback (step 6).** `gh pr create` failed three times with `HTTP 503` from
> `api.github.com/graphql` (attempts at ~09:5x, +20s, +45s backoff). The branch
> `refresh/ratings-2026-08-17` pushed successfully to origin, so this is a GitHub API
> outage, not auth or egress. Open the PR when the API recovers:
> `gh pr create --title "Weekly rating refresh 2026-08-17" --body-file <this file> --base main`

---

Weekly subjective-rating research refresh (CLAUDE.md rule 12). **Research only — no ratings changed, no edits to `00-master/ai_supply_chain_scoring.xlsx`.**

Rotation from `audit_rating_integrity.py --stalest 8`: **STX, GEV, NVDA, EME, MOD, TSM, AVGO, MSFT** — briefings 66–73 days old. Backlog was already clean (0 gate violations, 0 stale), so this is preventive burn-down rather than catch-up. Seven of the eight reported earnings inside the staleness window.

Network preflight passed (`NET_OK`) before any research — no DarkWake silence in this run.

---

## ⚠️ Thesis-break signals

**None** across the eight names. Three items are not breaks but should not be absorbed quietly:

1. **NVDA — a $105B contingent credit exposure to OpenAI, filed today.** The 8-K of 2026-08-17 (Item 1.01) commits NVIDIA to residual value guaranties on ~4.25 GW of IT load at the SB Energy PORTS campus with OpenAI as tenant, "cumulatively capped at $105 billion," plus discretionary credit support for another 3.8 GW. If OpenAI defaults or becomes insolvent, NVIDIA covers the shortfall. It won't appear in ND/EBITDA. This is a genuinely new kind of risk on the name and deserves an argument, not an absorption.
2. **MSFT — the "$15B capex cut" is not a cut.** Guidance moved ~$190B → ~$175B for CY2026 purely from reclassifying future data-center leases and extending assumed useful life from 15 to 25 years. Real outlay is unchanged and FY27 capex is guided to *rise*. **Any rating pass that marks supplier D5 down on the headline will mis-mark the entire supply chain.** Second-order: the depreciation-life extension also flatters forward margins — an earnings-quality item worth naming.
3. **MOD — margin compression is real.** Gross margin −340bps to 20.8% on supplier constraints, Q1 FCF a $5.0M use of cash. Guidance reaffirmed, so management treats it as transitory, but a cooling supplier that cannot get components is not the bottleneck it's rated as.

---

## Per-ticker findings

### NVDA — [context-2026-08-17.md](per-stock/NVDA/context-2026-08-17.md)
- **$105B RVG cap on 4.25 GW, OpenAI tenant, obligations begin ~2028** (8-K 2026-08-17, Item 1.01); +$1.5B equity into SB Energy ([Axios, 2026-08-17](https://www.axios.com/2026/08/17/openai-nvidia-ohio-data-center-sb-energy))
- Q1 FY27 (2026-05-20): revenue ~$81.6B **+85%**, Data Center $75B **+92%**, ~87% of total ([CNBC](https://www.cnbc.com/2026/05/20/nvidia-nvda-earnings-report-q1-2027.html))
- Custom ASIC share 15–20% and growing **+44.6% YoY vs +16.1% for merchant GPUs** ([Introl](https://introl.com/blog/custom-silicon-inflection-2026-hyperscaler-asics-nvidia-gpu))
- China loosening: H200 case-by-case licensing, but a 25% Section 232 tariff attached; Rubin still barred ([BIS](https://www.bis.gov/press-release/department-commerce-revises-license-review-policy-semiconductors-exported-china))
- P/S at the **18.8th percentile** of its own 3-year range while growing 132% — cheapest on sales in 3 years
- **Ratings to revisit: R1, R3, D3, D5, R4.** Hold momentum until the 2026-08-26 print.

### MSFT — [context-2026-08-17.md](per-stock/MSFT/context-2026-08-17.md)
- Q4 FY26 (2026-07-29): revenue **$90.0B +18%**, adj. EPS $4.74 vs $4.24 expected ([Yahoo](https://finance.yahoo.com/technology/articles/microsoft-q4-2026-earnings-azure-111058880.html))
- **Azure re-accelerated 40% → 43%** and crossed $100B annual — direction reverses the deceleration I had assumed ([Fortune](https://fortune.com/2026/07/29/microsoft-azure-100-billion-annual-revenue-earnings-revenue-cloud-ai/))
- **Commercial RPO +84% to $678B**; M365 Copilot 20M → 30M paid seats in one quarter
- Capex "cut" is accounting only ([CFO Dive](https://www.cfodive.com/news/microsoft-holds-line-ai-spending-plans/826648/), [Benzinga](https://www.benzinga.com/markets/tech/26/07/60808802/microsofts-15-billion-capex-cut-isnt-a-cut-at-all))
- OpenAI terms: rev-share capped $38B through 2030, Azure exclusivity ended, IP rights to 2032
- **Ratings to revisit: D1, R1. Explicitly do NOT move D5 on the capex headline.**

### TSM — [context-2026-08-17.md](per-stock/TSM/context-2026-08-17.md)
- Q2 2026: revenue ~$39.6B **+36%**, net profit **+77.4%**, 9th straight double-digit profit-growth quarter; 7nm-and-below = 77% of wafer revenue
- **July monthly revenue $14.49B, +44.7% YoY — a record; FY26 growth guidance raised to ">40%" from ">30%"** ([DigiTimes](https://www.digitimes.com/news/a20260810VL209/tsmc-revenue-growth-2026-forecast.html))
- **Q3 gross margin guided 65–67%** — well above the high-50s/low-60s I carried
- **Capex raised to $60–64B from $52–56B**; Arizona to $265B / four fabs — a direct Layer-4 read-through
- CoWoS sold out through 2026, lead times into 2027; capacity 75k → 125–130k wpm by end-2026
- **Ratings to revisit: D2, D1, D5, R2.** Quality inputs: TTM will understate a 65–67% margin (rule-9 TTM trap).

### AVGO — [context-2026-08-17.md](per-stock/AVGO/context-2026-08-17.md)
- Q2 FY26 (2026-06-03): revenue **$22.2B +48%**, **AI semi $10.8B +143%**, adj. EBITDA 69% of revenue, FCF 46% ([Broadcom IR](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-second-quarter-fiscal-year-2026-financial))
- **Q3 AI guided $16.0B (>200% YoY) — more than half of total revenue; FY26 ~$56B, FY27 reiterated >$100B**
- **Six core custom-silicon customers incl. Anthropic, Google, Meta, OpenAI** — broader than the Google+Meta duopoly I modeled
- **Apple locked through 2031** (8-K 2026-07-06, Item 8.01); Apple frames it as >$30B / 15B+ US-made chips — reframes the "legacy drag" leg as an annuity
- The stock fell on the Q2 print on **software**, not AI ([CNBC](https://www.cnbc.com/2026/06/03/broadcom-avgo-earnings-report-q2-2026.html)) — inverts which segment carries the risk
- **Ratings to revisit: D1, D2/D3 (careful — rule 23 flags +0.73 correlation), D5, R1, R3.**

### STX — [context-2026-08-17.md](per-stock/STX/context-2026-08-17.md)
- Q4 FY26 (2026-07-28): revenue **$3.63B +48%**, **record 52.7% non-GAAP gross margin** (13th straight quarter of gains), EPS $5.71, FCF $1.1B — best in a decade
- Sept-quarter guide **$4.1B / $7.30 EPS**, ~56% YoY growth
- **HAMR/Mozaic now 40% of nearline exabytes**; Mozaic 4 (44TB) ramping at the two largest CSPs
- **Supply allocated into calendar 2028**, 2029 discussions underway; datacenter ~90% of exabyte shipments ([The Register](https://www.theregister.com/storage/2026/07/29/ai_storage_boom_is_keeping_seagates_hard_drives_spinning/5280437))
- 3.50% 2028 converts called, redemption 2026-09-08 — mostly converts to equity
- **P/S at the 99.1st percentile of its own 3-year range** — highest in the rotation. Flag correctly doesn't fire (growth 33.8% vs 2.1% median), but the market is paying a record multiple on the premise that a 2%-median-growth business permanently re-rated. Argue it explicitly.
- **Ratings to revisit: D1, D3, D5 — and R1 in the opposite direction** (~90% datacenter is *more* concentrated). Quality: classic TTM-vs-MRQ trap.

### EME — [context-2026-08-17.md](per-stock/EME/context-2026-08-17.md)
- Q2 2026 (2026-07-30): **EPS $9.06 vs $7.23 consensus — a 25% beat**; revenue $5.15B vs $4.73B. **>15% surprise ⇒ rule-9 priority-1 objective refresh.**
- 10-Q Note 3, the cleanest AI-demand evidence in the rotation: **network-and-communications = 58% of US electrical revenue (from 50%) and 35% of mechanical (from 22%)** — mechanical roughly doubled YoY
- **RPO $17.14B** across US segments; FY guidance raised to **$20.0–20.5B revenue / $32.00–33.25 EPS**
- M&A is disciplined bolt-ons (four in 1H26 for $99.8M) — growth is organic, better quality than assumed
- Minor: MSHA imminent-danger order at a subsidiary mine, 2026-07-28, no injuries (8-K Item 1.04) — log it, don't re-rate on it
- **Ratings to revisit: D1, D5, R1 (end-market vs single-customer concentration), R4 (minor).**

### GEV — [context-2026-08-17.md](per-stock/GEV/context-2026-08-17.md)
- Q2 2026 (2026-07-22): **orders $24.2B +88%** (Power +134% organic) on revenue $11.1B +12%
- 10-Q: **RPO $176.28B**; **contract liabilities +$14,088M in six months** — customers prepaying ~$14.1B net to hold equipment slots. Scarcity converting to *cash*, not just price.
- Gas turbine backlog **116 GW, up from 100 GW in Q1**; capacity 20 → 24 GW (2028) → 30 GW (2030); pricing +300% over 3 years, 2026 orders +10–20 pts on $/kW
- **Electrification booked $2.4B of data-center orders in Q1 alone — more than all of 2025** ([CNBC](https://www.cnbc.com/2026/07/02/ge-vernovas-gas-turbines-arent-the-only-way-its-winning-from-the-ai-boom.html))
- Discipline against over-attribution: **~20% of GW under contract explicitly serves data centers**, ~80% traditional
- **Ratings to revisit: D5 and D1 (rate the tie honestly — most revenue is still traditional power), D3, R3.** Rule 15: re-verify the Prolec EPS-YoY blank against the filing.
- **Gap flagged, not papered over:** Wind segment performance did not surface this pass. Also: GEV still has **no populated `thesis.md`** — gate-compliant only while briefings stay fresh.

### MOD — [context-2026-08-17.md](per-stock/MOD/context-2026-08-17.md)
- **Data Centers is now a standalone reported segment** (8-K 2026-07-24, effective 2026-04-01), FY26 recast for comparability
- Q1 FY27: net sales $874.1M **+28%**; **Data Centers $348.6M, +90%**, ~40% of consolidated sales, segment adj. EBITDA $51.7M
- **Gross margin −340bps to 20.8%** on supplier capacity constraints; SG&A includes $7.1M of RMT costs; FCF a $5.0M use
- **FY27 guidance reaffirmed** (+20–35% sales, $650–680M adj. EBITDA)
- Gentherm RMT: MOD holders get **~40% of the combined company**, close by end CY2026, leaving a **pure-play climate company**; PT becomes a discontinued operation — segment history breaks at that point
- Product disclosure now names **CDUs, rear-door heat exchangers and immersion** — broader liquid-cooling content than I credited
- **Ratings to revisit: D1, D5, D2 (cuts *against* — MOD was on the receiving end of scarcity), R1 (>10% customer plus a single-customer $4B LTA — sharper, not softer), R3.**

---

## Checks run

- **Expectations red flag (rule 14):** clean on 7 of 8. TSM self-skipped (foreign filer, no us-gaap XBRL) — documented behavior, noted in its briefing with a manual substitute check.
- **FCF-conversion red flag (rule 2b):** clean on all 8 — no name has two consecutive years below 60%. MSFT (50%) and TSM (58%) are single-year, heavy-capex cases the rule explicitly says it misfires on.
- **Watch items rather than flags:** AVGO receivables +62% vs revenue +24%; STX AR +60% vs +34%; MOD AR +53% / inventory +48% vs +23%; NVDA inventory +112% vs +65%.

## Backlog burn-down

| | Before | After |
|---|---|---|
| Rated names | 211 | 211 |
| Gate violations (rated, no research) | **0** | **0** |
| Stale (>90d) | **0** | **0** |
| Stalest briefing age | ~73d (STX) | ~66d → reset to 0 for all 8 |

Next rotation surfaces: MPWR, TE, PSIX, PUMP, BW, WYFI, SHAZ, HIVE.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
