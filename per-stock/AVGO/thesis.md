# AVGO — Broadcom Inc.

**Layer:** 06 — AI Compute Silicon / Custom silicon (ASIC/XPU designers) + AI networking
**Last reviewed:** 2026-09-02 *(§3/§6/§9 updated from the post-Q3-FY26 briefing `context-2026-09-02.md` and the 2026-08-21 refresh; §4/§5/§7 still carry Q2-FY26 data and are owed a refresh. Objective inputs on the Watchlist are stale at 2026-07-16 — the mechanical rescore runs 2026-09-03.)*
**Current conviction:** ✓✓ *(tracks current Tier; Dom to confirm — see Decision log)*
**Current position size:** ~6.6% of tracked book (site weight, 2026-06-17)
**Thesis-break trigger:** Loss or in-housing of a core XPU customer (Google or Meta), OR clear evidence the third-party-financed (Apollo/Blackstone) compute platform is propping up demand that end-customer cash flows cannot sustain.

---

## 1. One-line thesis

> Broadcom is the leading designer of the custom AI chips (XPUs) hyperscalers build to reduce dependence on Nvidia — Google's TPU, Meta's MTIA, plus OpenAI, Anthropic and Apple — and it supplies the high-end Ethernet networking silicon that ties AI clusters together; AI silicon revenue is ~$10.8B/quarter and 49% of total (Q2 FY26, 8-K 2026-06-03), with management guiding >$100B of annual AI revenue as the FY27 *floor*.

---

## 2. Position in the AI supply chain

- **What they do:** Two businesses. (1) Semiconductor Solutions — custom AI accelerators (XPUs) co-designed with hyperscalers, plus merchant AI networking silicon (Tomahawk/Jericho Ethernet switches, optical/SerDes), plus a broad non-AI franchise (broadband, wireless, storage, industrial). (2) Infrastructure Software — VMware (VCF), mainframe and security software. Q2 FY26: semis $15,009M (68% of revenue), infra software $7,178M (32%) (8-K 2026-06-03).
- **Where they sit:** Upstream silicon designer (fabless; manufactured at TSMC). For custom AI compute, AVGO is the dominant merchant alternative to designing in-house — it is *how* a hyperscaler builds its own accelerator without an internal chip team at Nvidia's scale.
- **Unique vs. commoditized:** Defensible. Custom XPU design at leading-edge nodes is a multi-year, multi-billion-dollar co-engineering relationship (SerDes, packaging, multi-die, HBM integration) with few credible merchant suppliers (AVGO, Marvell, a tier of ODMs). AVGO holds a ~1-generation networking lead (Tomahawk 6 at 102.4T shipping >1 year; Nvidia Spectrum-X equivalent not expected until 2H 2026 per trade press, The Register 2026-06-04).
- **AI revenue mix:** AI semiconductor revenue was $10.8B in Q2 FY26, +143% YoY, ~49% of total revenue (8-K 2026-06-03; earnings call 2026-06-03). Networking is ~40% of AI revenue currently (management guides ~30% long-run); XPUs the balance.

---

## 3. Customers

Six core AI customers ("our six XPU customers", call 2026-09-02), four of them named, now structured around gigawatt-scale multi-year commitments rather than one-off design wins:

| Customer | Commitment (updated Q3 FY26) | Source / date |
|---|---|---|
| Google | Ironwood **TPU v7 shipping in high volume**; **TPU v8i in production**. "Multi-tens of billions of dollars of TPUs annually over the next several years." Multi-generation dev + supply + networking Supply Assurance through up to **2031** | call 2026-09-02; 8-K 2026-04-06 (Item 8.01) |
| Anthropic | **1 GW of Ironwood in 2026 → 5 GW of TPU v8i in 2027 → 10 GW in 2028** | call 2026-09-02 |
| OpenAI | **Jalapeño shipping**; **1.3 GW in 2027**; **>5 GW** of Jalapeño + successor generations in 2028 | call 2026-09-02 |
| Meta | Three **MTIA** generations through 2027; **3 GW visibility through 2028**; **production shipments begin Q4 FY26** | call 2026-09-02 |
| Two unnamed | Not broken out on the Q3 call (Q2: shipments begin late 2026, $6B in POs to date) | call 2026-06-03 |

*The Q2 "unreconciled" Anthropic flag (~3.5 GW per 8-K vs "another 5 GW" per call) is **resolved** by the Q3 call's explicit 1 / 5 / 10 GW ladder for 2026 / 2027 / 2028.*

- **Scale of the ramp:** AI semiconductor revenue **$16.7B in Q3 FY26, +221% YoY, +54% QoQ = 56% of total revenue**, guided to **$21.7B (+236%) in Q4**. FY26 AI revenue raised to **~$58B** (from ~$56B); management claims "secured the supply" to reach **~$115B in FY27** and indicates ~$230B in FY28 (call 2026-09-02).
- **⚠️ Bookings visibility — metric discontinued this quarter.** Q2 disclosed **AI bookings >$30B vs $10.8B shipped (~2.8×)**. **No AI bookings or backlog dollar figure was disclosed for Q3**; the qualitative substitute was "demand simply exceeds supply." The named per-customer gigawatt ladder above is arguably a stronger form of visibility, but it is **not the same metric** — treat the bookings/shipments ratio as unobserved from Q3 onward, not as deteriorating (rule 3).
- **Concentration risk:** High and structurally unchanged. Six customers are essentially the entire AI franchise, and two of them (Anthropic, OpenAI) are pre-profit frontier labs whose consumption is "dependent on … continued commercial success" (8-K 2026-04-06 language). **New second-order channel:** those counterparties now fund capacity through levered off-balance-sheet vehicles (Anthropic stacked ~$71B of off-book chip-lease SPV debt in ~60 days, 2026-08), so concentration runs through the *financing chain* as well as the revenue line. Scored **Cust Conc 3** (watchlist 2026-07-16).
- **Substitution risk — the dual-sourcing vector, now quantified.** Tan first acknowledged Google would have "some diversity of sources" on the Q2 call (2026-06-03). Since then:
  - **MediaTek** holds the compute-die second source at Google (TPU v8 split reported as AVGO "Sunfish" training / MediaTek "Zebrafish" inference) — this predates the Marvell news by a quarter.
  - **Marvell** received a Google warrant for ~59.0M MRVL shares @ $206.58 (~$12.18B), signed 2026-07-29, disclosed via MRVL 8-K 2026-08-19. Scope is TPU-**attach** silicon (inference accelerators, storage controllers, NICs, memory-interface controllers, near-memory compute); 97.7% vests across 240 tranches of $500M of *discretionary* Google Custom Products revenue → **$120B cumulative for full vest, with no minimum purchase, no floor and no exclusivity**. Assessed in `context-2026-08-21.md` as **predominantly incremental, not displacement**.
  - **Sell-side estimates of AVGO's retained share at Google diverge widely:** BofA 55–60%, Morgan Stanley ~80%, Macquarie 65%-by-2028. The spread itself is the honest state of knowledge.
  - **⚠️ Unresolved:** whether Marvell's "AI inference accelerators" means the near-memory MPU or a true inference TPU die. **Management was asked nothing and said nothing about Marvell, the warrant, or share loss on the 2026-09-02 call.** Countervailing datapoint: Google's **TPU v8i — the inference line — is in production at Broadcom**, which cuts against the displacement reading.
- **Structural note:** the whole point of the XPU business *is* customer in-housing of compute — AVGO captures the design rather than losing it. The residual risk is dual-sourcing within that captured design, not the in-housing itself.

---

## 4. Pricing & demand

- **Demand:** Management: "Demand for XPUs and networking is simply insatiable" (call 2026-06-03). 2H FY26 AI revenue expected to ~2× 1H; FY26 AI guide ~$56B reaffirmed (+~180%); FY27 AI >$100B reiterated, "on track, if not stronger"; FY28 directionally "substantial growth from 2027" (call 2026-06-03).
- **Pricing / content:** Content per GW stable near-term, rising generation-over-generation (more SRAM, embedded CPU cores, multi-die, HBM) (call 2026-06-03). Next-gen 200T switch tapes out in the current quarter.
- **Gross margin trend:** Consolidated non-GAAP GM 77.1% in Q2 (−230bps YoY), guided ~74% for Q3 — XPU mix dilution, framed as mix not structural (call 2026-06-03). Semi operating margin 62% (+460bps YoY); software GM 93%. TTM **GAAP** gross margin ~68% (financials.xlsx FY Summary, statement-based; FY25 67.8%) — the watchlist's 76.3% is the *non-GAAP* basis (yfinance `info.grossMargins`), the ~9pt gap being amortization of acquired VMware intangibles in GAAP COGS.
- **Backlog / lead times:** Supply for 2026–2027 secured ("working on 2028 and 2029 right now"). Inventory days rose 68 → 86 ($3.0B → $4.3B), a deliberate 2H build (10-Q filed 2026-06-09; call 2026-06-03).

---

## 5. Financials snapshot

> **Note:** `financials.xlsx` rebuilt 2026-06-20 — see the **FY Summary** tab (FY2023/24/25 + TTM-through-Q2-FY26, GAAP, formula-driven). TTM figures below are statement-based (Σ last 4 quarters) and reconcile to the watchlist.

| Metric | Q2 FY26 (quarter) | TTM / ratio | Source |
|---|---|---|---|
| Revenue | $22,187M (+48% YoY) | $75.5B TTM | 8-K 2026-06-03; FY Summary |
| AI semi revenue | $10,800M (+143% YoY) | 49% of total | 8-K / call 2026-06-03 |
| GAAP net income | $9,310M (+88% YoY) | $29.3B TTM | 8-K 2026-06-03; FY Summary |
| Adj. EBITDA | $15,244M (69% of rev) | $42.4B TTM | 8-K 2026-06-03; FY Summary |
| Gross margin | 77.1% non-GAAP (Q2) | 68.3% TTM GAAP | 8-K 2026-06-03; FY Summary |
| FCF (statement) | $10,262M (46% of rev) | $32.8B TTM; margin 43.4% | 8-K 2026-06-03; FY Summary |
| Capex | $231M | $0.86B TTM; ~1.1% of rev (fabless) | 8-K 2026-06-03; FY Summary |
| ROIC | — | 28.7% | watchlist 2026-09-04 — TTM NOPAT $38,033M (GAAP op income $42,960M = Q4 FY25 $7,654M + 9M FY26 $35,306M, × (1 − 11.47% 9M-FY26 GAAP effective rate $3,853M/$33,600M)) ÷ avg invested capital $132,692M (ST debt + LT debt + equity − cash: $135,134M at 2026-08-02, $130,250M at FYE 2025-11-02; 8-K 2026-09-02 Ex-99.1). Prior 21.3% (2026-06-12) was the same construction through Q2 FY26. |
| Net debt / EBITDA | — | 1.07× ($45.3B ND / $42.4B EBITDA) | FY Summary (MRQ net debt) |
| FCF conversion (FCF ÷ NI) | — | 112% TTM ($32.8B/$29.3B) — **clean**; FCF > NI on non-cash VMware amort. | FY Summary |
| Rev 3-yr CAGR | — | 24.4% | watchlist 2026-06-12 |
| EPS YoY | — | +87.5% (GAAP) | watchlist 2026-06-12 |

> **Correction (rule 3):** the 2026-06-12 briefing's "TTM FCF $27.2B / 93% conversion" used yfinance `info.freeCashflow` (levered estimate — the CLAUDE.md-documented trap). Statement-based TTM FCF is $32.8B (Σ quarterly OCF − capex), which reconciles to the watchlist's 43.41% margin and gives 112% conversion.

Balance sheet: cash $19.6B, receivables $10.8B, inventory $4.3B (10-Q filed 2026-06-09). Working-capital watch: receivables +66% and inventory +95% over four quarters vs. revenue +48% — explained by the disclosed 2H supply build; escalate only if FCF conversion degrades (context 2026-06-12).

---

## 6. Moat

- **IP / process know-how:** Leading-edge custom-silicon design (SerDes, advanced packaging, multi-die, HBM integration) and merchant AI-Ethernet silicon — a narrow field of credible suppliers. ~1-generation networking lead (Tomahawk 6 102.4T shipping >1 yr; Nvidia Spectrum-X equivalent ~2H 2026, The Register 2026-06-04).
- **Scale advantage:** Largest merchant XPU designer; co-development across six frontier customers compounds design IP and packaging learning. Q3 FY26 evidence: **four concurrent named programs** (Google TPU v7/v8i, Anthropic Ironwood, OpenAI Jalapeño, Meta MTIA) in volume or entering production in the same quarter — a cadence no other merchant designer is currently running.
- **Switching costs:** Very high. XPU programs are multi-generation co-engineering relationships; the Google agreement runs through up to 2031 (8-K 2026-04-06). Re-architecting a custom accelerator to a new vendor is a multi-year reset. The Q3 gigawatt ladder extends *committed* visibility into 2028 at three separate accounts.
- **Network effects:** Ethernet has overtaken InfiniBand in AI scale-out (Dell'Oro, via TrendForce) — AVGO benefits from the open-Ethernet ecosystem becoming the cluster fabric standard vs. Nvidia's proprietary stack.
- **Software annuity:** Infrastructure software is the non-AI half of the moat and it **re-accelerated in Q3** — $8,752M, +29% YoY, **ARR +15%**, 94% gross margin, operating margin **+650bps to ~84%** (8-K 2026-09-02) — recovering from the Q2 miss. VMware Private AI Cloud opens an enterprise vector. Offsetting: an open EU licensing matter and the CVE-2026-59310 vCenter mass-exploitation episode both feed a live VMware churn narrative.
- **Regulatory / geographic:** Manufacturing concentrated at TSMC (Taiwan) — shared industry geopolitical exposure.

**Moat rating:** Wide — but with a live, and now *quantified*, erosion vector at the anchor account. The dual-sourcing vector is real (MediaTek on compute die, Marvell on attach silicon) and sell-side estimates of AVGO's retained Google share span **55–80%** — a spread wide enough that the moat's *width* at that one account is genuinely uncertain, even though nothing observed to date constitutes displacement. Note rule 23: **D2 (Position) ↔ D3 (Moat) correlate at +0.73** — do not move both on a single piece of evidence.

---

## 7. Valuation

- **Current multiple:** At $392.90 (yfinance 2026-06-17), market cap ~$1.87T, EV ~$1.84T. Trades ~24× trailing sales (P/S, yfinance 2026-06-17) and ~65× trailing GAAP earnings (GAAP depressed by VMware acquisition amortization and SBC). FCF yield ~1.8% (watchlist 2026-06-12).
- **⚠️ Data flag (rule 1/3):** The watchlist "Fwd P/E" of 19.8 and yfinance forwardPE 20.3 both rest on a yfinance forward-EPS estimate of $19.35 that is **not credible** (vs. trailing GAAP EPS $6.03 — a ~3× one-year jump). Do not use the ~20× forward P/E. Annualizing Q2 non-GAAP EPS of $2.44 (8-K 2026-06-03) and layering the guided growth puts the forward non-GAAP P/E in roughly the mid-30s× — a premium but not extreme multiple for the growth rate.
- **Peer comparison:** Premium to large-cap semis on sales, in line-to-premium on growth-adjusted earnings given the AI ramp.
- **Bull case (3–5 yr):** FY27 AI >$100B as a *floor* with FY28 growth on top; software re-accelerating (+31% Q3 guide). If AI revenue compounds and GM mix stabilizes, a high-30s× forward earnings multiple on a much larger base.
- **Bear case (3–5 yr):** Hyperscaler capex digestion + anchor dual-sourcing + GM mix dilution compress both growth and multiple; the Apollo/Blackstone-funded demand proves financial-engineering-led rather than cash-flow-led.
- **What's priced in:** A lot of the AI ramp is in the multiple. Per rule 14, AVGO sits where consensus is most crowded (it was a top SALP Q1 2026 put target). High expectations are the risk, not the thesis.

---

## 8. Catalysts (next 4 quarters)

| Date | Event | Why it matters |
|---|---|---|
| 2026-09-02 | Q3 FY26 earnings | Tests the $16.0B AI guide (+200%+) and the +31% software guide; biggest single sequential step in the model |
| 2H 2026 | OpenAI silicon enters production; 200T switch tape-out | First revenue from a new XPU customer; confirms networking roadmap lead |
| 2026–2027 | Apollo/Blackstone XPU platform deployment ($35B first tranche, >20 GW total) | Validates (or undermines) the third-party-financed demand structure |
| 2H 2027 | Meta MTIA deliveries begin (3 GW through 2028) | Second mega-XPU program ramps; diversifies beyond Google |
| Ongoing | Google dual-sourcing developments | Direct read on moat-erosion vector at the anchor account |

---

## 9. Risks

- **Thesis-killer #1 — Core-customer loss / in-housing:** Google or Meta moving XPU volume to a rival merchant designer or fully internal team. Google dual-sourcing was acknowledged for the first time on the Q2 call (2026-06-03) and is now quantified in §3: MediaTek holds a compute-die second source, Marvell won TPU-*attach* silicon on a discretionary, no-minimum warrant structure, and sell-side estimates of AVGO's retained Google share span 55–80%. **Status: live vector, no displacement observed.** Management said nothing about it on the 2026-09-02 call.

- **Thesis-killer #2 — Financing-vehicle circularity *and* Broadcom's own contingent exposure to it.** *(Reframed 2026-09-02. The prior framing — "exogenous (system-level, not AVGO-balance-sheet) risk … AVGO's own ND/EBITDA is a comfortable 1.08×" — was wrong in a specific way: it treated the vehicle's leverage as the whole of the risk and Broadcom's balance sheet as uninvolved. Broadcom guarantees part of it.)*

  - **The vehicle.** The AI XPV platform, confirmed on the Q3 call as being "in partnership with **Apollo and Blackstone**," has **$35B secured for Anthropic's 1 GW** deployment. CFO Amie Thuener's framing: "we partner with sophisticated third-party financial partners to independently underwrite and capitalize the assets rather than providing the direct financing ourselves" (call 2026-09-02). BofA credit modelled the platform's senior debt reaching **~$370B by mid-2029** at 20 GW.
  - **⚠️ Broadcom's own exposure — the part the old framing missed.** Broadcom carries a **5-year residual value guarantee** backstopping lease payments, with **maximum exposure up to ~$29B on the initial $35B tranche**. **S&P reportedly treats the RVG as a contingent debt-like obligation and adds it to adjusted debt**, having tagged the first AI tranche credit-negative (AVGO A−). BofA cut its **credit** view to Marketweight (~2026-08-11) while its equity desk stayed constructive — keep the two separate. **Broadcom CDS spreads hit record levels the week of 2026-08-17.**
  - **A further $70–100B deal surfaced 2026-08-20/21** (Bloomberg: $60–70B senior + $30B junior; CNBC: $45B + $35B — **unsigned, size disputed, all parties declined comment; do not model a point estimate**). Broadcom would guarantee **"a portion"** of the senior tranche, **fraction undisclosed**.
  - **On the call, management characterised the RVGs as "contingent liabilities we view as low risk, supported by the strong profitability trajectory." That is a characterisation, not an accounting treatment.**
  - **⚠️ OPEN — the single highest-value document for this name: the VIE / residual-value-guarantee footnote in the Q3 FY26 10-Q, which as of 2026-09-02 is not yet filed** (the Q2 10-Q landed 6 days after the Q2 8-K, so expect ~2026-09-08). Two questions it must answer: **does the RVG get recognised, and what fraction of the newer deal does Broadcom guarantee?** Do not settle the R3 rating before reading it.
  - **Counter-evidence, stated fairly:** Broadcom's *reported* balance sheet improved materially in Q3 — cash $23,975M (vs $16,178M at FYE25), long-term debt $57,167M (vs $61,984M), short-term debt $2,252M, net debt ≈ $35.4B against annualising EBITDA well north of $80B. **The on-balance-sheet picture is stronger than the stale 1.08× ND/EBITDA implies. The entire risk is what sits off it.**
  - **Bull read unchanged:** third-party capital removes the binding constraint on demand. **Bear read sharpened:** if token-demand growth disappoints, the vehicle's committed capacity becomes an overhang *and* Broadcom's guarantee converts a customer's problem into Broadcom's.

- **Working capital / revenue-quality watch (new, 2026-09-02):** Trade receivables **$13,707M vs $7,145M at FYE25 (+92%)** against three-quarter revenue of $71,089M vs $45,872M (+55%); inventory doubled to **$4,523M** (from $2,270M). Consistent with a violent XPU ramp and rising memory content, and **FCF has not yet suffered** (46% of revenue in Q3) — but the gap between receivables growth and revenue growth widened rather than normalised, which is what the Q2 briefing asked to watch. Keep on the list.

- **Margin mix — now guided and explicitly explained, not hypothetical:** non-GAAP GM 77.1% (Q2) → **75.0% (Q3, beat the 74% guide)** → **~73% guided for Q4**, vs 78% a year ago, attributed on the call to "increasing mix of XPUs with their increasing memory content." Custom-ASIC revenue is structurally lower-margin than the legacy franchise; **this is the price of the ramp, and operating margin is holding at ~66%.**

- **Cyclical risk:** A hyperscaler capex pause would hit XPU and networking hard. **AI is now 56% of revenue (Q3), guided to ~62% in Q4** — up from ~49% at the Q2 review. The franchise is now majority-levered to one spend cycle; on the numbers AVGO is an AI-accelerator company with a software annuity attached.

- **China / export controls:** Indirect — AI silicon subject to evolving export rules; less direct exposure than Nvidia's China datacenter GPUs.

- **Technology substitution:** Nvidia closing the networking gap (Spectrum-X, 2H 2026); a step-change that made merchant XPUs uncompetitive vs. Nvidia's integrated rack economics.

- **Legal / regulatory (open):** ITC Section 337 investigation into Samsung HBM/DDR5 (Netlist complaint) names AVGO as a co-respondent, no ruling. EU General Court President dismissed Broadcom/VMware's bid to suspend a Commission information request (2026-08-03).

- **~~Execution / management~~ — RESOLVED:** the CFO transition is confirmed, not speculation. Kirsten Spears retired effective 2026-06-12; **Amie Thuener signed the 2026-09-02 8-K as Chief Financial Officer**.

---

## 10. The "inverse the thesis" test

1. **If, over the next 2–3 quarters, a core XPU customer (esp. Google) publicly shifts meaningful volume to a competing merchant designer or internal team, *and* AVGO's AI bookings stop outpacing shipments** — the "indispensable custom-silicon partner" premise is breaking, and the multiple is not defensible.
2. **If the Apollo/Blackstone-funded compute platform becomes the primary marginal source of XPU demand while frontier-lab (Anthropic/OpenAI) revenue and token usage underperform their committed capacity** — then reported demand is financial-engineering-led, FY27 ">$100B floor" is at risk, and the thesis is wrong about the durability of the ramp.

**Status as of 2026-09-02 (tests NOT rewritten — scored only):**
- **Test 1 — NOT MET.** Part 1 (a core XPU customer publicly shifting meaningful volume to a competing merchant designer) is *partially* fired and no worse than at 2026-08-21: the volume shifted is attach silicon on a discretionary, no-minimum structure, and the compute-die second source (MediaTek) predates it. Part 2 (AI bookings ceasing to outpace shipments) is **untested** — the bookings metric was not disclosed in Q3, so it is unobserved, not failed. **A test requires both halves of an AND. Do not re-rate on half of one.**
- **Test 2 — NOT MET, and now partly observable.** The Apollo/Blackstone platform is confirmed and scaling, but frontier-lab consumption has not visibly underperformed committed capacity; the FY27 AI figure was *raised* to ~$115B, not cut. The test's real trigger — committed capacity outrunning end-demand — remains the thing to watch, and the Q3 10-Q's guarantee footnote is the next hard evidence.

---

## Source log

- 2026-06-03 — 8-K (press release Ex 99.1, acc 0001730168-26-000051) — Q2 FY26 results — `filings/8-K_2026-06-03_0001730168-26-000051.htm`
- 2026-06-03 — Earnings call transcript (Motley Fool) — `transcripts/Q2-2026.md`; delta `transcripts/Q2-2026-delta.md`
- 2026-04-06 — 8-K (Item 8.01, acc 0001193125-26-144028) — Google LTA through 2031; Anthropic ~3.5 GW from 2027 — `filings/8-K_2026-04-06_0001193125-26-144028.htm`
- 2026-06-09 — 10-Q (avgo-20260503.htm) — balance sheet (cash $19.6B, AR $10.8B, inventory $4.3B)
- 2026-06-12 — Context briefing (post-/earnings-update) — `context-2026-06-12.md`
- 2026-06-12 — Watchlist objective refresh (`00-master/ai_supply_chain_scoring.xlsx`) — TTM ratios, ROIC, ND/EBITDA, CAGR
- 2026-06-17 — yfinance — price/market cap/EV/P-S valuation inputs
- 2026-06-04 — The Register — Tomahawk 6 vs. Spectrum-X timing
- TrendForce / Dell'Oro — Ethernet overtaking InfiniBand in AI scale-out
- 2026-06-20 — `financials.xlsx` FY Summary (rebuilt; yfinance statements, GAAP, formula-driven) — FY2023–25 + TTM-through-Q2-FY26

---

## Decision log

| Date | Action | Conviction | Rationale | Position size after |
|---|---|---|---|---|
| 2026-06-17 | Thesis populated from sourced briefing (was template-only) | ✓✓ *(tracks Tier; confirm)* | Per rule 12, name needed a research-backed thesis; data from post-Q2-FY26 briefing | ~6.6% (site weight) |
| 2026-06-20 | Rebuilt `financials.xlsx` (FY Summary tab); corrected GAAP gross margin (68% not 76%) and statement TTM FCF ($32.8B not $27.2B) | ✓✓ | Deep-dive financials gap; surfaced the info.freeCashflow trap in the briefing | ~6.6% |
| 2026-09-02 | §3/§6/§9 updated from post-Q3-FY26 briefing; **thesis-killer #2 reframed** — the "exogenous … not AVGO-balance-sheet" framing was wrong and is replaced with the RVG contingent-exposure framing (~$29B max on the initial $35B tranche; S&P treats it as debt-like). §10 tests preserved verbatim and scored, not rewritten. CFO-transition risk item closed as resolved. | ✓✓ *(unchanged — no re-rate)* | Owed since the 2026-08-21 refresh; the Q3 call's Apollo/Blackstone confirmation made the old framing indefensible. **No subjective rating changed (rule 12);** R3 explicitly deferred to the Q3 10-Q guarantee footnote, not yet filed. | unchanged |
