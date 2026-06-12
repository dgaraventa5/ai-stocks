# NVDA Q1 FY2027 — Delta Summary (final, 2026-06-12)

**Quarter ended 2026-04-26; call + 8-K + 10-Q all dated 2026-05-20.**
**Baseline:** Q4 FY2026 (revenue $68.1B). No prior-quarter transcript on file in `transcripts/` (checked 2026-06-12: only Q1 FY2027 files exist), so prior-quarter comparisons use Q4 FY2026 reported figures and public reporting of that call. Supersedes `Q1-FY2027-delta.md` (2026-05-26 reconstruction-based pass); adds the 10-Q deep-dive (FCF, concentration, commitments) and post-call competitive context (AVGO call, MSFT research).

---

## 1. Management tone on AI demand — upgraded again

Q4 FY26 framing: strong but supply-constrained. Q1 FY27: "Demand has gone parabolic... Agentic AI has arrived... Tokens are now profitable" (Huang). New hard anchor: "full confidence in **$1 trillion in Blackwell and Rubin revenue from 2025 through calendar 2027**" (Kress) — explicitly excluding standalone Vera CPU ($20B FY27 visibility, $200B claimed TAM) and LPX. Hyperscale capex framed at >$1T by 2027, AI infra $3–4T/yr by 2030. Tone shift from "capex as investment" to "capex as ROI-generating" — third consecutive quarter of YoY revenue acceleration backs it (transcript; MD&A: $81,615M, +85% YoY, +20% QoQ).

## 2. Customer concentration — diversifying AND concentrating (both true)

- New platform split: Hyperscale ~$38B (~50% of DC, +12% QoQ) vs ACIE ~$37B (+31% QoQ); sovereign +80% YoY across ~40 countries (transcript).
- **But the 10-Q shows billing concentration rising:** three direct customers = 21%/17%/16% of revenue (54%); three direct customers = 30%/18%/16% of **accounts receivable (64%)**, up from 25/18/13 (56%) at Jan-2026 (10-Q Note 7 + segment note). The 50/50 diversification story is about end-platform mix; the checks still come from a few giant intermediaries. The 2026-05-26 delta's "concentration risk is actively declining" was too generous — treat as mixed.

## 3. AI revenue mix

DC $75.2B = 92.1% of revenue (Hyperscale ~$38B / ACIE ~$37B); within DC, compute ~$60B (+77% YoY) and **networking ~$15B (+~3x YoY)**; Edge Computing $6.4B (+29% YoY); physical AI >$9B TTM (transcript). Networking is now ~18% of total revenue, a real second engine.

## 4. Capex / capacity / lead times / supply

- Total supply (inventory + purchase commitments + prepaids) **$145B**, up from $119B at Q4 (transcript; 10-Q: inventory $25,797M + commitments $119B). Raw materials nearly doubled QoQ ($3,807M→$6,647M, Note 7) — Rubin staging.
- **$95B of the $119B commitments is payable within the remainder of FY2027** (10-Q Note 10) — the supply bet is heavily front-loaded into the next 9 months.
- Lead times: risk factors still cite >12-month extended lead times; no specific numbers on call. Rubin ramp overlaps GB300 tail at TSMC — external reporting flags a strained Taiwan H2 (TechTimes, Computex 2026 coverage).

## 5. Forward guidance vs prior

| | Q1 FY27 guide (at Q4) | Q1 FY27 actual | Q2 FY27 guide |
|---|---|---|---|
| Revenue | ~$77B mid | $81.6B | $91B ±2% (consensus ~$86.8B) |
| GM (non-GAAP) | ~73% | 75.0% | 75.0% ±50bps; FY "mid-70s" |
| OpEx | — | $7.6B GAAP | **$8.5B GAAP / $8.3B non-GAAP**; FY +"upper 40s"% |

Correction vs 05-26 delta/transcript reconstruction: Q2 OpEx guide is $8.5B/$8.3B, not "$5.3B". Capital return: $80B new buyback + $39B remaining, dividend $0.01→$0.25, "~50% of FCF returned this year" (transcript).

## 6. The FCF margin "collapse" — explained (it's a data artifact)

- 10-Q Statements of Cash Flows: **OCF $50,344M, capex $1,757M → Q1 FCF $48,587M = 59.5% of revenue.** Working capital was net **positive** (+$3,544M): inventory −$4,420M, AR −$2,243M, prepaid −$983M, MORE than offset by accrued liabilities +$7,763M (taxes payable $2,669M→$10,638M) and AP +$2,210M.
- TTM statement FCF = $119.08B on $253.49B revenue = **47.0% — unchanged**.
- The 18.3% margin / 0.93% yield came from `yfinance info["freeCashflow"]` = $46.34B (Yahoo "levered FCF" estimate), which is internally inconsistent with yfinance's own statement rows ($119.08B). Exact Yahoo formula unverifiable — flagged. Likely confounders in this quarter's statements: $15,936M non-cash equity-securities gains inside net income, and $18,582M investing-section purchases of non-marketable securities.
- **Genuine forward cash watch (don't over-correct the other way):** $95B supply commitments + $27B investment commitments payable in FY27, and $10.6B accrued-but-unpaid taxes mean H2 FY27 FCF will absorb real outflows.
- **Pipeline fix needed:** `scripts/yfinance_fundamentals.py:101` uses `info.freeCashflow` — propose statement-based TTM OCF−capex (DDOG/EV-EBITDA-class garbage-input failure, cf. CLAUDE.md rule 10). Watchlist FCF Yield (0.93) and FCF margin (18.3) are currently wrong inputs; central refresh should not score off them.

## 7. New risks raised this quarter

1. **Circular ecosystem investing, now disclosed:** $18.6B into private companies/infra funds in one quarter; "some of these investments include AI model makers that may indirectly purchase or use our products in the cloud" (10-Q MD&A). Non-marketable securities $22.3B→$43.4B; $27B more committed (Note 6). $15.9B of Q1 net income is non-cash investment gains — GAAP EPS quality degraded (~27% of NI).
2. **Front-loaded supply bet:** $95B payable in 9 months against demand that management itself calls "parabolic" — classic over-ordering risk if tokens-profitability narrative falters.
3. **OpEx ramp:** FY27 OpEx +"upper 40s"% (R&D compute +112% YoY) — operating leverage pause.
4. **AR concentration at 64% top-3** — counterparty/financing-shape risk as neocloud intermediaries grow.
5. **H200-China execution risk now two-sided:** licenses granted (Feb 2026, ~10 buyers incl. Alibaba/Tencent/ByteDance per SCMP/knightli), POs received (Tom's Hardware), but China-side import approval unknown; 25% US tariff condition. Upside optionality, not yet revenue.

## 8. Thesis-relevant items

- **Spectrum-X share:** "now larger than all peers combined" (Kress); corroborated externally — NVDA passed Cisco/Arista in DC Ethernet (~$2.3B/qtr, +647% YoY; NextPlatform/IDC-derived; consistent with this week's MSFT research note). **Tension:** this week's AVGO call claims a 1-generation networking silicon lead — revenue-share dominance and silicon-generation lead can coexist; watch Tomahawk 6 vs Spectrum-X next-gen sockets.
- **Custom-ASIC competition:** Huang dismissed SRAM/LPX-class inference ASICs as "niche... for some time"; meanwhile 10-Q reveals a **Groq non-exclusive license agreement with $3,957M accrued purchase consideration** (Note 7) — NVDA is buying optionality in the inference-ASIC direction it publicly downplays. AVGO XPU customers now 6 (incl. OpenAI, Anthropic). NVDA counter: "every single frontier model company will jump on VeraRubin from the get-go."
- **Rubin timeline:** production shipments Q3 2026, ramp into Q4, "Q1 [FY28] very big"; AWS >1M Blackwell+Rubin GPUs starting this year; Google XGS up to 960K Rubin GPUs (transcript).
- **Vera standalone CPU:** new $200B TAM claim, $20B FY27 revenue visibility — entirely new vector (agent-orchestration CPUs), not in prior thesis.
- **China:** zero DC compute revenue 2nd consecutive quarter ($0 vs $4.6B YoY Hopper-to-China, MD&A); guidance still assumes $0; licenses exist but unexercised.

## Net read

Beat-and-raise with the strongest demand language to date, networking now empirically #1 in DC Ethernet, and a clean cash engine (59.5% quarterly FCF margin). The real new negatives are quality-of-earnings (investment gains, circularity), front-loaded supply commitments, and rising billing concentration — none thesis-breaking, all worth explicit Risk-dimension treatment at next rescore. The scary FCF print was a data artifact.
