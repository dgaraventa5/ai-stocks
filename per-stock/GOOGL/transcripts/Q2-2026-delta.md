# GOOGL — Q2 2026 vs Q1 2026 delta — written 2026-07-27

> **Baseline caveat:** there is no Q1 2026 transcript file in this repo. The comparison baseline is **Q1 2026 reported results and call guidance** as documented in `per-stock/GOOGL/context-2026-06-12.md` (Q1 10-Q acc. 0001652044-26-000048; Motley Fool Q1 call transcript, https://www.fool.com/earnings/call-transcripts/2026/04/29/alphabet-googl-q1-2026-earnings-call-transcript/) — not a prior-quarter transcript diff. Q2 figures from the Q2 2026 press release (8-K Ex-99.1, https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000066/googexhibit991q22026.htm) and Q2 10-Q (filed 2026-07-23, acc. 0001652044-26-000071).

## Headline deltas (Q1 2026 reported → Q2 2026 reported)

| Metric | Q1 2026 | Q2 2026 | Delta |
|---|---|---|---|
| Revenue | $109.9B (+22% YoY) | $119.8B (+24% YoY) | growth accelerated; +9% QoQ |
| Google Cloud | $20.0B (+63%) | $24.8B (+82%) | **major acceleration**, +24% QoQ |
| Cloud op margin | 32.9% | 35.6% ($8,814M/$24,768M) | +2.7pt QoQ |
| Consolidated op margin | 36.1% | 34.0% | −2.1pt QoQ (Alphabet-level AI R&D $5.8B vs $3.4B yr-ago; depreciation +42% YoY) |
| Search & other | $60.4B (+19%) | $63.3B (+17%) | still mid-teens+; Q3 faces tougher comp (CFO) |
| YouTube ads | $9.9B (+11%) | $11.1B (+13%) | World Cup tailwind |
| Cloud backlog (RPO) | $467.6B total / $462.3B Cloud | **$519.5B / $513.9B** | +$51.9B QoQ despite +82% revenue burn |
| Capex | $35.7B | $44.9B | +26% QoQ; H1 $80.6B |
| OCF | $45.8B | $39.1B | −15% QoQ |
| **FCF** | **+$10.1B** | **−$5.9B** | first negative FCF quarter of the AI cycle |
| Capex guide (FY26) | $180–190B (raised from $175–185B in April) | **$195–205B** | second raise in 3 months; 2027 still "increase significantly" |
| Headcount | 194,668 (3/31) | 198,933 (6/30) | +4,265 QoQ |
| EPS (diluted) | $5.11 (incl. $36.9B equity gains) | $9.11 (incl. $99.0B equity gains, +$6.26 EPS effect) | GAAP EPS garbage-in for run-rate purposes both quarters |

## Management tone and substance shifts

1. **AI demand / Gemini monetization — tone strengthened from "compute constrained" to "allocating scarcity."** Q1: "our cloud revenue would have been higher if we were able to meet the demand." Q2: still supply-constrained, but Pichai now articulates an explicit allocation hierarchy (frontier AGI development → Search/YouTube → Cloud) and is spending to bridge. Monetization proof points got harder: Gemini app 950M MAU (from 650M MAU cited ~Nov 2025 era), tokens 22B/min vs 16B/min in Q1 (+37% QoQ), Gemini Enterprise at ~90% of Fortune 100, AI Mode >1B MAU, AI Max 500k advertisers. Gemini-app advertising remains roadmap, not P&L.
2. **Cloud trajectory — inflected upward, not just sustained.** Growth went 63% → 82% YoY while backlog still GREW $52B QoQ; existing customers exceeding contracted commitments by >50% and new-customer velocity 2x YoY (call). TPU system sales now a named product revenue line ("Google Cloud generates product revenues primarily from the sale of TPU systems," press release segment description — first time in a PR) with inventory up $2.4B → $10.0B in six months (10-Q balance sheet; inventory note says TPU systems + Pixel), majority of TPU-deal revenue still 2027.
3. **Capex guidance — raised again ($180–190B → $195–205B), the second raise this year.** Reason given: pulling capacity delivery forward to meet demand, ~60/40 servers vs DC/network. 2027 "increase significantly" unchanged.
4. **The negative-FCF quarter and the third-party/leased compute bridge (new).** Q2 FCF −$5.9B (OCF $39.1B < capex $44.9B). CFO framed it as deliberate: expanding "third-party capacity in Q3 as a bridging strategy while we build out more internal capacity," with "modest margin pressure." The 10-Q shows the mechanics: leases-not-yet-commenced future payments now **$85.2B** (commencing 2026–2031), plus a June 2026 **~$5.8B non-cancelable short-term lease** commencing Q3 2026 (10-Q MD&A Leases) — renting compute while owned capacity catches up. Total fixed/guaranteed purchase commitments >1yr now **$707.0B**, "significant majority" long-term supply agreements (10-Q Note, Commitments). No comparable prior-period figure is given in the Q2 10-Q — flagged, do not assume the delta.
5. **Funding stack executed as designed:** equity package settled in Q2 — $30.5B common (incl. $10.0B Berkshire private placement) + $19.1B preferred net proceeds, plus $24.8B Q2 debt issuance; long-term debt $46.5B (12/31/25) → $98.2B (6/30/26); cash+securities $242.5B; buybacks zero for a second straight quarter ($69.5B authorization idle); ATM untouched. First preferred dividend declared July ($12.15/pref share, ~$0.60/depositary share, payable 8/15) (all: Q2 PR + 10-Q Financing notes).
6. **Forward guidance shifts:** Q3 laps the Search acceleration that began Q3 2025 (comp warning); slight FX headwind in Q3 vs +1pt in Q2; Cloud margin pressure near-term from third-party capacity costs + Wiz integration. No revenue guidance (as usual).

## New risks (not present at Q1)

- **EU DMA fine €890M + Search redesign order (2026-07-23):** first-ever DMA fine — €460M for Search self-preferencing (shopping/hotels/transport/sports verticals), €430M for Play Store anti-steering; 60 days (~Sept 21, 2026) to comply or face periodic penalties up to 5% of worldwide daily turnover; requires a Search results redesign in the EU (CNN, https://www.cnn.com/2026/07/23/business/europe-fines-google-1-billion-intl; TechTimes, https://www.techtimes.com/articles/321410/20260723/eu-fines-google-890-million-under-dma-orders-search-redesign-60-days.htm). Distinct from the 2026-07-16 DMA binding-specification orders. Qualitative sizing: the fine itself is noise (<1% of quarterly OCF), but the **redesign remedy** touches the EMEA revenue base — $32.5B in Q2, 27% of revenue (PR geo table) — and the demotion of Google's own verticals is the first structural, ongoing intervention in the Search SERP itself. Watch conversion/RPM commentary for EMEA from Q4 2026. Note: the Q2 10-Q (filed 7/23, same day) still says the DMA investigations' probable loss "cannot reasonably be estimated" and does not reflect the fine — timing artifact, flagged.
- **PriceRunner/Klarna Swedish judgment ~$2.1B** recognized in Q2 2026, under appeal (10-Q Legal Matters) — new private-action tail on EU shopping conduct.
- **Android €4.1B fine went final** (ECJ denial July 2026); $5.2B cash paid July 2026, previously accrued (10-Q) — cash out, no new P&L hit.
- Accrued fines/settlements liability now $17.4B (10-Q).

## What did NOT change

- Backlog conversion cadence (~50% within 24 months) — same language as Q1.
- 2027 capex direction ("increase significantly") — unchanged, still unquantified.
- Buyback halt, dividend policy ($0.22/qtr common), ATM undrawn — as set up in June.
- Earnings-quality distortion from non-marketable equity marks — bigger ($99.0B Q2, "primarily... SpaceX and a private company," 10-Q OI&E note; the private company is unnamed — flag, don't assume it is Anthropic) but the same phenomenon as Q1's $36.9B.

**Net read vs Q1:** demand-side evidence strengthened (Cloud accel + backlog build + enterprise adoption); cash-side strain arrived on schedule and slightly worse than modeled (negative FCF quarter, second capex raise); regulatory moved from tail-risk to active structural intervention in the EU.
