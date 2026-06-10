# ALAB — Q1 2026 Delta Summary

**Reported:** May 5, 2026
**Prior quarter:** Q4 2025 (revenue ~$270M)
**This quarter:** Q1 2026 (revenue $308.4M)

---

## 1. Revenue Growth Trajectory

| Period | Revenue | Growth |
|---|---|---|
| Q1 2025 | $159.4M | — |
| Q4 2025 | ~$270M | — |
| Q1 2026 | $308.4M | +93% YoY, +14% QoQ |
| Q2 2026 guide | $355-365M | +15-18% QoQ implied |

**Assessment:** Hyper-growth continues. 93% YoY is decelerating from the 144% YoY seen in prior quarters, but the sequential acceleration (14% QoQ, guiding 15-18% QoQ) shows the ramp is sustained, not plateauing. If midpoint Q2 guide ($360M) holds, the annualized run-rate exits H1 at ~$1.44B. For context, full-year 2025 revenue was roughly $770M. The company is on track to approximately double revenue year-over-year in FY2026.

**What changed:** The growth driver is shifting from signal conditioning (Aries retimers, Taurus cables) toward Scorpio fabric switches. PCIe Gen 6 is now >1/3 of revenue, up from a minority in prior quarters.

---

## 2. Product Mix Shift — The Scorpio Pivot

This is the most important development in the quarter.

| Product Line | Role | Q1 2026 Status |
|---|---|---|
| **Scorpio X-Series** (scale-up) | 320-lane AI fabric switch | Initial volume shipments began; production ramp H2 2026 |
| **Scorpio P-Series** (scale-out) | 32-320 lane fabric switch | Shipping; two new hyperscaler customers for late 2026 |
| **Aries** (retimers) | PCIe/CXL signal conditioning | Mature, strong PCIe 6 adoption |
| **Taurus** (cables) | Ethernet AEC modules | Steady across GPU/XPU platforms |
| **Leo** (memory) | CXL memory controller | Azure M-series ramp + new KV cache design win (2027) |

**Key quote:** "Scorpio will become our largest product line by the end of the year" — CEO. Scorpio was ~15% of revenue in 2025. To become the largest line by year-end, it needs to reach 25%+ of a much larger revenue base. This is a bold claim and the single most important metric to track in Q2-Q3.

**Why it matters:** Scorpio transforms ALAB from a "retimer/cable company" into a "fabric switch platform company." Fabric switches are higher-ASP, more defensible (hardware-accelerated Hypercast, in-network compute), and address the $20B projected scale-up switching market by 2030. But they also carry higher hardware content, which compresses gross margins (see section 5 below).

---

## 3. Customer Concentration — Improving but Still Extreme

| Customer | Q1 2025 | Q1 2026 | Direction |
|---|---|---|---|
| A | 12% | 29% | Way up — likely Amazon (warrant agreement) |
| B | 26% | 21% | Down |
| C | — | 16% | New to top-5 |
| D | 23% | 12% | Down |
| E | — | 12% | New to top-5 |
| **Top 5 total** | — | **~90%** | — |

**Assessment:** The top-5 concentration at ~90% is extreme but structurally expected for a semiconductor company selling into hyperscalers. The positive signal is diversification: Customer A surged (Amazon partnership via warrant), but two new customers entered the top-5, suggesting Scorpio is broadening the customer base. Customer B and D declining as a share (while revenue nearly doubled) means their absolute spend likely held flat or grew modestly while new customers ramped.

**Geographic note:** Taiwan 30%, Singapore 30%, China 29% — these are manufacturing partner locations, not end-customer geographies. The actual end-customer exposure is US hyperscalers; the geographic data is misleading.

**China exposure (29%):** This is contract manufacturing, not end-demand. But it creates real risk if export controls tighten on Chinese manufacturing partners or if there are tariff escalations.

---

## 4. Competitive Dynamics: ALAB vs. CRDO

| Metric | ALAB (Q1 FY2026) | CRDO (Q3 FY2026, ended Jan 2026) |
|---|---|---|
| Revenue | $308.4M | $407.0M |
| YoY Growth | +93% | +201.5% |
| Non-GAAP Gross Margin | 76.4% | 68.6% |
| Non-GAAP EPS | $0.61 | $1.07 |
| Forward GM Guide | ~73% (Q2) | 64-66% (Q4 FY2026) |

**Key differences:**
- **CRDO is growing faster** (201% vs 93% YoY) but off a smaller base and with much lower gross margins
- **ALAB has structurally higher margins** (~76% vs ~69%) because retimers and fabric switches are semiconductor-heavy, while CRDO's AEC business carries more hardware/cable content
- **Both face margin compression ahead:** ALAB guiding 73% (Scorpio ramp + Amazon warrant), CRDO guiding 64-66% (AEC mix shift). CRDO's margin trajectory is worse.
- **Different TAMs:** ALAB is moving into PCIe/CXL fabric switching (scale-up networking); CRDO is dominant in Ethernet optical DSPs and AECs (scale-out networking). They overlap on AECs but are increasingly divergent on the highest-growth segments.
- **Both have extreme customer concentration**: ALAB top-5 = 90%; CRDO similarly concentrated
- **CRDO stock dropped 10-14% on its earnings** despite the massive beat — margin guidance compression spooked investors. ALAB stock dipped 0.83% on its earnings for similar margin-guide reasons.

**Bottom line:** These are complementary, not directly competitive, in their highest-growth segments. ALAB's moat is in PCIe/CXL fabric switching where CRDO doesn't play. CRDO's moat is in Ethernet optical DSPs where ALAB is a minor player. The overlap is in AECs/smart cable modules (Taurus vs. CRDO's AECs), where CRDO has scale advantage. On our watchlist, CRDO ranks #7; ALAB should be evaluated on the strength of the Scorpio fabric pivot, not head-to-head with CRDO.

---

## 5. Margin Trends — The Watch Item

| Quarter | Non-GAAP GM | Commentary |
|---|---|---|
| Q1 2025 | ~75% (GAAP 74.9%) | Pre-Scorpio ramp |
| Q4 2025 | 75.7% | Favorable signal conditioning mix |
| Q1 2026 | 76.4% | Peak; lower hardware within signal conditioning |
| Q2 2026 guide | ~73% | -340bps: 200bps Amazon warrant + 140bps Scorpio mix |

**Assessment:** Q1 2026 at 76.4% is likely the near-term peak. The Q2 guide of ~73% is a meaningful step-down. The Amazon warrant (200bps) is noncash and arguably should be excluded from operational analysis, but it flows through reported non-GAAP gross margin.

The more important structural question: as Scorpio becomes the largest product line (higher hardware content), will gross margins stabilize in the 72-74% range or continue declining toward 70%? Management's framing of "systematic, thoughtful evaluation of custom business opportunities" suggests they're aware of the margin dilution risk and trying to manage it.

For comparison, CRDO's non-GAAP gross margin is heading toward 64-66%. Even at 73%, ALAB maintains a significant margin premium, reflecting the higher semiconductor content in its product mix.

---

## 6. New Growth Vectors (2027+)

Several new revenue streams were disclosed or confirmed that don't contribute meaningfully in 2026 but set up the 2027-2028 growth runway:

| Initiative | Expected Revenue | TAM Signal |
|---|---|---|
| NVLink Fusion custom switches | 2027 | NVIDIA partnership; hybrid rack architecture |
| UALink fabric switches | 2027 | Amazon + AMD ASIC launches; higher ASPs than PCIe |
| Optical fiber-attach (XScale) | 2027 volume | Major AI platform qualification underway |
| NPO chipsets | 2027 | Multi-rack cluster enablement |
| CPO-enabled Scorpio X | 2028+ | Larger domain networking |
| Custom KV cache (Leo CXL) | 2027 | Inference/agentic computing demand |

**Assessment:** The 2027 pipeline is loaded. If even half of these ramp on schedule, ALAB has multiple growth vectors beyond Scorpio PCIe switches. The NVLink Fusion and UALink initiatives are particularly important because they lock ALAB into the NVIDIA and AMD/Amazon ecosystems at the switching layer, creating structural switching costs.

**Risk:** This is a lot of simultaneous new-product execution. R&D at $96.2M/quarter (31% of revenue) reflects the investment intensity. If any of these miss timelines, the revenue bridge from Scorpio alone may not sustain the growth rate the market is pricing in.

---

## 7. Valuation Context

| Metric | ALAB |
|---|---|
| NTM EV/EBITDA | ~49x |
| NVIDIA NTM EV/EBITDA | ~21x |
| Marvell NTM EV/EBITDA | ~39x |
| Semi peer mean | ~31x |

ALAB trades at a significant premium to semiconductor peers. The premium is justified only if: (1) Scorpio ramps to become the largest product line, (2) revenue continues 50%+ growth into 2027, and (3) gross margins stabilize above 70%. Any miss on these three conditions triggers multiple compression. The TIKR mid-case projects ~26% revenue CAGR through 2030, with net income margins around 35%.

---

## Summary: What Changed vs. Prior Quarter

| Dimension | Before Q1 2026 | After Q1 2026 | Thesis Impact |
|---|---|---|---|
| Revenue trajectory | Hyper-growth, accelerating | Hyper-growth sustained, 93% YoY, sequential acceleration | Confirms |
| Product mix | Retimer-led, Scorpio emerging | Scorpio in production, CEO says "largest line by year-end" | **Strengthens** |
| Gross margin | 76% range, expanding | 76.4% peak, guiding 73% on Scorpio mix + Amazon warrant | **Watch item** |
| Customer diversification | Concentrated | Still 90% top-5 but two new names entered; Amazon deepened | Neutral-to-positive |
| Competitive position | Strong in retimers | Extending into fabric switches; differentiated Hypercast IP | **Strengthens** |
| 2027 pipeline | Known but vague | NVLink Fusion, UALink, optical, KV cache all with timelines | **Strengthens** |
| Valuation | Premium | 49x NTM EV/EBITDA; premium depends on execution | **Risk factor** |

**Overall assessment:** Q1 2026 supports and modestly strengthens the bull thesis. The Scorpio pivot is real and accelerating. The 2027 pipeline is deeper than previously understood. The main caution is margin compression as product mix shifts toward higher-hardware-content switches, and the premium valuation leaves no room for execution misses.
