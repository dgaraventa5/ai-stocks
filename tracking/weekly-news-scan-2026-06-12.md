# Weekly News Scan — 2026-06-12

**Scope:** 135 watchlist tickers. Scan date: 2026-06-12 (covering June 5–12).

**⛔ NETWORK BLOCKER — PARTIAL SCAN:** The remote execution environment blocks outbound
access to `www.sec.gov`, `data.sec.gov`, and `query2.finance.yahoo.com`. As a result:
- SEC EDGAR 8-K scan (Steps 1–4) **could not run** — no 8-K data for June 5–12
- Objective input refresh via yfinance **could not run** (Rule 9)
- `scripts/momentum_50dma.py`, `scripts/refresh_targets.py`, `scripts/track_performance.py` **all blocked**

**What completed:** Local score recalculation (all 135 names), portfolio pipeline status from
existing spreadsheet data, and the Rule-12 integrity audit.

**Resolution needed:** Add `data.sec.gov`, `www.sec.gov`, and `query2.finance.yahoo.com` to
the environment's network egress allowlist (Settings → Egress), then re-run this scan.

---

## Step 0 — Mental Models: ✓✓ Positions (pre-scan articulation)

No ✓✓✓ names exist in the current watchlist (highest score: NVDA 83.3).
Mental models below are for the 16 portfolio holdings (all ✓✓).

| Ticker | Score | Mental model |
|--------|-------|--------------|
| NVDA | 83.3 | Dominant AI GPU supplier, ~80-90% merchant accelerator market share. Q1 FY2027: $81.6B revenue (+85% YoY), Q2 guided $91B. Networking revenue $14.8B (+199% YoY) is the key upstream signal. Risk: CUDA moat erosion, China = $0 DC revenue. No ✓✓✓ because P/S and EV/EBITDA remain high at this revenue level. |
| TSM | 79.8 | World's leading contract fab. N3/N2 in high demand, CoWoS packaging still a bottleneck. Secular beneficiary of every node that NVDA, AMD, AVGO, ALAB ship. Key existential risk: Taiwan geopolitics — can't price it out, just acknowledge it. |
| SNDK | 79.7 | Spun from WD (2024), focused on NAND flash. AI infrastructure storage demand + recovering memory cycle. Thesis is demand-driven pricing recovery, not a specific AI moat. |
| MU | 79.5 | HBM3E supplier for NVDA Blackwell. HBM sold out through 2025-2026. Massive margin recovery underway after the 2023-24 memory trough — MRQ margins likely far above TTM averages (TTM limitation flag). Risk: HBM market eventually expands (Samsung/SK Hynix), cyclicality always returns. |
| META | 79.0 | Social media / ad platform deploying massive AI infra (Llama models, AI-ranked feed/ads). Just restructured into Superintelligence Labs (2026-05-20). High capex but AI is already monetizing through ad-ranking improvement. Less supply-chain pure-play, more AI-beneficiary. |
| CRDO | 78.3 | Credo Technology, connectivity ASICs (SerDes IP, AEC cables) linking GPUs within AI clusters. Revenue ramp directly tied to hyperscaler GPU deployments. Customer concentration is the main risk — ~90% of revenue from a handful of hyperscalers. |
| GOOGL | 77.7 | Hyperscaler with TPU custom silicon, Gemini 3.5 models, dominant AI-enhanced search+ads. At Google I/O, launched Gemini 3.5, $5B TPU JV with Blackstone, capex guided to "significantly increase" vs 2026's $190B. Key risk: OpenAI/Anthropic disrupting search, though moat is wider than consensus thinks. |
| ANET | 77.5 | Arista, dominant DC networking. AI clusters demand 400G/800G Ethernet switches. AI fabric target raised to $3.5B (full-year 2026). Risk vector: NVIDIA Spectrum-X gaining share at both META and MSFT; supply chain shortages (wafers, CPUs, optics) flagged to persist 1-2 more years. |
| EME | 76.7 | EMCOR, electrical/mechanical contractor riding the data center construction wave. High-visibility backlog, limited AI-specific moat but reliable execution and backlog growth. **Gate violation** — no thesis.md populated. |
| ALAB | 76.5 | Astera Labs, Layer 7 connectivity ASICs. Scorpio switch (PCIe 5.0 fabric) in volume shipments. NVLink Fusion (NVIDIA + hyperscaler custom switch) and UALink switch (Amazon/AMD) design wins in 2027. Customer A (likely Amazon) = 29% of revenue Q1 2026. Key new-money entry since June 2026 rebalance. |
| FIX | 76.4 | Comfort Systems USA, HVAC/mechanical contractor. Q1: revenue +56.5% to $2.87B, record backlog $12.45B, dividend raised 14%. DC construction pure-play with no AI-specific moat. **Gate violation** — no thesis.md. |
| MSFT | 76.2 | Azure AI growing strongly, Copilot+ across Office suite. Massive capex ($75B+ annually). OpenAI partnership creates both lock-in advantage and dependency risk. **Gate violation** — no thesis.md. Scores lower on value (high multiples) but strong quality + AI thesis. |
| PLTR | 74.8 | AI-native software for government + commercial. Q1 2026: revenue $1.633B (+85% YoY, beat by 5.8%), NRR 150%, US commercial +133% YoY, adj FCF margin 57%. AIP is their production-grade AI platform. Key Layer 10 risk: NRR compression is the canary — watch for any sign NRR drops from 150%. Expensive (~97x fwd P/E). |
| AVGO | 74.6 | Broadcom, largest custom ASIC designer (Google TPUs, Meta training chips), plus Ethernet networking (Tomahawk, Jericho). CEO projected custom AI chips > $100B annual revenue by end of 2027. VMware integration ongoing but AI revenue is the re-rating driver. |
| EQT | 73.8 | Largest US nat gas producer. Thesis: AI data centers → electricity demand → gas demand. Score barely above exit threshold (73.0). No AI moat — pure macro beneficiary of demand growth. Held on hysteresis; next adverse score move would trigger EXIT PENDING. |
| TER | 73.0 | Teradyne, semiconductor test equipment. AI chips (HBM, complex logic) require significantly more test time per die. Structurally higher ATE demand. **Score exactly at exit threshold (73.0) — hairline above EXIT PENDING.** Any score deterioration on next refresh triggers the 2-run exit process. **Gate violation** — no thesis.md. |

**Thesis diff vs. prior model:** No material model-shifting signals surfaced from local data since the 2026-06-10 rebalance. The biggest open question remains the ANET/NVDA Spectrum-X competitive dynamic — no new data this week given the blocker.

---

## ⚠️ Material Events

**SEC EDGAR 8-K scan could not run — no material events to report this week.**

[FLAG] All material event identification for June 5–12 is missing. This is a process gap.
High-priority items to manually check when network access is restored:
- **ONTO**: $1.7B convertible proceeds — use-of-proceeds 8-K expected within 30 days of 2026-05-21 close
- **WULF**: Muskie Data Campus anchor tenant announcement (1 GW, ~285 acres KY — no tenant disclosed as of 2026-05-26)
- **D/NEE**: First FERC filing on Dominion/NextEra all-stock merger (18-24 month approval timeline)
- **PLTR/DDOG/CRM**: Layer 10 SaaS signals on NRR, AI feature adoption, pricing model shifts — no 8-K data available

---

## 📊 Earnings Refreshed

**yfinance blocked — no earnings refresh possible this week.**

[FLAG] Cannot determine whether any watchlist names reported Q2/Q3 results during June 5–12.
After network access is restored, check for Item 2.02 (Results of Operations) in 8-Ks for:
- Semiconductor names whose fiscal quarters end in late April/May (AMAT, LRCX, SNPS, KLAC, etc.)
- Any Layer 10 SaaS names with May quarter-ends

Previously flagged from 2026-05-26 scan and still pending:
- **KEYS** — April 2026 quarter likely now populated in yfinance; re-pull inputs
- **NVDA** — Full `/earnings-update` still recommended for Q1 FY2027 transcript analysis
- **MOD** — Full `/earnings-update` recommended for $4B hyperscaler chiller LTA details

---

## 💼 Portfolio Pipeline

**Pipeline scripts blocked by yfinance restriction. Status based on local spreadsheet data (last refreshed 2026-06-10).**

**Current portfolio (16 positions, all HOLD):**

| Ticker | Score | Target % | Notes |
|--------|-------|----------|-------|
| NVDA | 83.3 | 8.99% | HOLD — well above exit |
| TSM | 79.9 | 7.41% | HOLD |
| SNDK | 79.7 | 7.32% | HOLD |
| MU | 79.5 | 7.25% | HOLD |
| META | 79.0 | 7.00% | HOLD |
| CRDO | 78.3 | 6.70% | HOLD |
| GOOGL | 77.7 | 6.44% | HOLD |
| ANET | 77.5 | 6.34% | HOLD |
| EME | 76.7 | 5.95% | HOLD |
| ALAB | 76.5 | 5.87% | HOLD |
| FIX | 76.4 | 5.82% | HOLD |
| MSFT | 76.3 | 5.77% | HOLD |
| PLTR | 74.9 | 5.13% | HOLD |
| AVGO | 74.6 | 5.02% | HOLD |
| EQT | 73.9 | 4.68% | HOLD — 0.9 pts above exit threshold |
| TER | 73.0 | 4.29% | ⚠️ **HOLD — at exit threshold (73.0). Next refresh could trigger EXIT PENDING.** |

**Pipeline flags:**
- No ENTER or EXIT events triggered based on current local scores
- No names above entry threshold (74.5) that aren't already in portfolio
- **TER watch**: Score 73.0 exactly equals the exit threshold. If any objective input worsens on next yfinance refresh (earnings miss, margin compression), TER triggers EXIT PENDING (2-run confirm required)
- **EQT watch**: Score 73.9, held on hysteresis; still 0.9 pts above exit but not re-entering territory (entry = 74.5)
- **VRT (73.7), AMD (73.5)**: Next tier below EQT — would need to reach 74.5 to enter

**Performance mark (last available: 2026-06-11):**
| Portfolio | Model Value | vs Inception |
|-----------|-------------|--------------|
| Model | $14,058.88 | **+1.9%** |
| SMH | — | +1.2% |
| QQQ | — | -1.8% |
| SPY | — | -1.7% |
| EW universe | — | +1.2% |

Model outperforming all benchmarks since 2026-05-26 inception. Cannot update to today (2026-06-12) without yfinance.

---

## 🔬 Rating Integrity (Rule #12)

`audit_rating_integrity.py` run: **71 gate violations, 0 stale names.**

Gate violations = names carrying subjective AI/Momentum/Risk ratings with **no thesis.md and no research briefing**. Their ratings are unbacked — do not trust their AI, Momentum, or Risk subscores.

**Portfolio holdings with gate violations (7/16 — highest priority):**

| Ticker | Score | Layer | Gate violation since |
|--------|-------|-------|---------------------|
| FIX | 76.4 | 03 | 2026-05-18 |
| EME | 76.7 | 03 | 2026-05-18 |
| TER | 73.0 | 04 | 2026-06-10 |
| TSM | 79.9 | 05 | 2026-06-10 |
| MSFT | 76.3 | 09 | 2026-05-18 |
| GOOGL | 77.7 | 09 | 2026-05-18 |
| META | 79.0 | 09 | 2026-05-26 |

7 of 16 portfolio holdings are carrying unresearched subjective ratings. Per Rule 12, these names' AI/Momentum/Risk subscores should not be trusted until research-backed briefings are produced. The scheduled biweekly refresh routine handles the queue by layer rotation; flag this for the next collaborative rating session.

**Full ungated list (71 names, non-portfolio):** GEV, ETN, SBGSY, ABBNY, HTHIY, HUBB, PWR, MTZ, POWL, NVT, ATKR, VRT, DLR, EQIX, IRM, CARR, TT, JCI, ASML, LRCX, KLAC, TOELY, ONTO, CAMT, KLIC, ENTG, MKSI, PLAB, UCTT, CDNS, SNPS, ARM, INTC, GFS, TSEM, UMC, COHR, LITE, AAOI, POET, CSCO, CIEN, APH, TEL, GLW, SMCI, DELL, HPE, CRWV, AMZN, ORCL, NBIS, APLD, CORZ, IREN, CIFR, CLSK, BTDR, HUT, RIOT, WULF, SNOW, NOW, CRM (non-portfolio names omitted above)

---

## Routine Filings

No filing data available — SEC EDGAR scan blocked.

---

## New 13F Activity

No 13F scan available — SEC EDGAR scan blocked.

---

## Follow-up Items

**Immediate (unblock network access first):**
1. Add `data.sec.gov`, `www.sec.gov`, `query2.finance.yahoo.com` to egress allowlist → re-run full scan
2. Run `scripts/momentum_50dma.py` + `scripts/refresh_targets.py` + `scripts/track_performance.py`

**From prior scan (2026-05-26), still open:**
3. **ONTO** — Monitor for use-of-proceeds disclosure (30-day window from 2026-05-21 close)
4. **WULF** — Anchor tenant at Muskie Data Campus (1 GW, no tenant announced)
5. **D/NEE** — First FERC merger filing (18-24 month approval timeline)
6. **KEYS** — Re-pull yfinance once April 2026 quarter is populated
7. **NVDA / MOD** — Full `/earnings-update` still recommended

**Rating integrity (backlog):**
8. Run `/refresh-context` on the 7 portfolio-name gate violations (priority order: TSM, META, MSFT, GOOGL, EME, FIX, TER)
