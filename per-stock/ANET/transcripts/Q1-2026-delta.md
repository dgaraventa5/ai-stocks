# ANET Q1 2026 — Delta Summary

**Earnings date:** May 5, 2026
**Sources:** [Arista IR press release](https://investors.arista.com/Communications/Press-Releases-and-Events/Press-Release-Detail/2026/Arista-Networks-Inc--Reports-First-Quarter-2026-Financial-Results/), [Motley Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/05/05/arista-anet-q1-2026-earnings-transcript/), [TIKR CFO follow-up](https://www.tikr.com/blog/arista-networks-fell-14-after-earnings-heres-what-the-cfo-said-9-days-later)

---

## 1. AI networking demand trajectory

**Verdict: Accelerating, but supply-constrained.**

- AI networking revenue target raised to $3.5B for FY2026 (from $3.25B prior), more than doubling 2025 levels.
- 100+ cumulative AI customers across hyperscalers, neo-clouds, and enterprise.
- Fourth major customer officially transitioned from InfiniBand to Ethernet at production scale — this took ~2 years and validates the Ethernet thesis.
- Scale-Across (connecting geographically distributed DC clusters) emerging as a meaningful revenue stream — management expects it to contribute "at least a third" of AI revenue in 2026.
- Enterprise inference described as "the calm before the storm" — hundreds/thousands of units today vs. hundreds of thousands for training. Multi-year ramp ahead.

**Key number:** Combined recognized + deferred revenue growth = 54% YoY. The headline 35% growth understates actual demand.

---

## 2. 800G adoption and speed transition timeline

- 800G actively deployed with 100+ customers. This is the current production speed for AI scale-out.
- 1.6T expected at production scale in 2027.
- XPO (Extended Pluggable Optics): 12.8 Tbps per module with liquid cooling, production in 2027. Ullal: "XPO has a ten-year run, especially at 1.6T and 3.2T."
- Scale-Up opportunity (ESUN-based) deferred to 2027-2028. 5-7 rack design opportunities identified but all target 1.6T speeds.

**What this means:** Arista is well-positioned for the current 800G cycle and has a clear path to 1.6T. The 800G-to-1.6T transition is a product refresh cycle that should sustain demand. XPO is a longer-term architectural bet that could meaningfully differentiate vs. competitors at higher speeds.

---

## 3. Customer concentration

- Microsoft and Meta confirmed as 10%+ customers — "have been 10% and greater customers for over a decade."
- Management expects "at least one, maybe two" additional 10%+ customers in 2026, contingent on shipment volumes.
- Customer concentration remains a risk, but diversification is happening: 100+ AI customers, strong enterprise/campus motion, MSP channel via Big Switch/VeloCloud.

**Meta-NVIDIA concern:** Meta announced a multi-year deal with NVIDIA including Spectrum-X Ethernet switches. Arista stock fell ~2.4% on the news. However, Arista reportedly remains Meta's sole supplier for disaggregated scheduled fabric switching in spine applications. The relationship appears additive (NVIDIA for leaf/GPU-adjacent, Arista for spine/fabric) rather than purely substitutive. Still, this bears close monitoring.

---

## 4. Competitive dynamics — NVIDIA Spectrum-X

**This is the most important strategic question for ANET holders.**

NVIDIA networking context (Q1 FY2027, reported May 20, 2026):
- NVIDIA data center networking revenue: $14.8B (+199% YoY)
- Spectrum-X annualized run rate: >$10B
- CFO Kress claimed Spectrum-X is "larger than all Ethernet network peers combined"
- Meta and Microsoft (Arista's two largest customers) both use Spectrum-X
- InfiniBand also grew >4x YoY

**Is NVIDIA taking share from Arista?** The evidence is nuanced:

1. **TAM expansion argument (bullish for ANET):** The AI networking market is growing from ~$10B toward $20B+ (650 Group estimate). NVIDIA's entry into Ethernet via Spectrum-X validates Ethernet as the AI networking standard, expanding the pie. Citi analysts concur. Arista's 35% revenue growth in Q1 occurred during the same period NVIDIA was scaling Spectrum-X aggressively.

2. **Share displacement argument (bearish for ANET):** NVIDIA captured 25.9% of DC Ethernet switching market share per IDC Q2 2025 data, surpassing Arista's 18.9%. NVIDIA bundles Spectrum-X with GPU sales, creating a bundling advantage Arista cannot match. Meta and Microsoft using both vendors may eventually consolidate toward the vendor offering the tighter GPU-network integration.

3. **Market segmentation argument (nuanced):** NVIDIA Spectrum-X is strongest in GPU-adjacent leaf switching within AI training clusters. Arista is strongest in spine/fabric, campus, and enterprise. Scale-Across (WAN interconnect between DCs) is a segment where NVIDIA has minimal presence and Arista has a clear advantage. The two companies may be serving different layers of the same network.

**My assessment:** The TAM is growing fast enough that both companies are growing revenue simultaneously. But the mix is shifting — NVIDIA owns the GPU-adjacent leaf tier, and that tier is the fastest-growing segment. Arista's best defense is: (a) spine/fabric dominance, (b) Scale-Across as a differentiated wedge, (c) campus/enterprise diversification, and (d) EOS software stickiness. The risk scenario is not that NVIDIA kills Arista's revenue, but that NVIDIA captures the highest-growth segment and Arista's growth rate decelerates from 35% toward 15-20% in 2027-2028.

---

## 5. Margin and guidance trends

**Gross margin:**
- Q1 GAAP: 61.9% (down 180bps YoY from 63.7%)
- Q1 Non-GAAP: 62.4% (down 170bps YoY from 64.1%)
- Drivers: (a) customer mix — hyperscaler concentration means volume discounts, (b) supply chain cost absorption — management intentionally absorbing elevated costs for wafers, silicon, memory, optics rather than passing through to customers.
- Ullal: "We are gonna do everything, including hurt our gross margins to supply to that demand this year and next year."
- FY2026 guidance: 62-64% (implies floor near current levels)

**Operating margin:** Non-GAAP 47.8%, flat YoY. Revenue growth offsetting GM compression through operating leverage.

**Q2 2026 guidance:**
- Revenue: ~$2.8B (+3.4% QoQ, implies ~30% YoY)
- Non-GAAP GM: 62-63%
- Non-GAAP OM: 46-47%
- Non-GAAP EPS: ~$0.88

**Deferred revenue ($6.2B, +15% QoQ):**
- CFO clarified this is "contracted AI demand" — real orders not yet recognized because hyperscale deployments take 6-8 quarters to reach acceptance (up from historical 2-4 quarters).
- This is a massive future revenue tailwind if it converts. But it also introduces volatility and makes the P&L harder to model.
- Key monitoring metric: Q2 deferred revenue (reported August). Growth toward $6.5B+ confirms accelerating demand; decline below $5.8B is a warning signal.

**Supply chain:**
- Purchase commitments: $8.9B (up from $6.8B), multiyear, primarily TSMC
- Inventory: $2.38B (deliberate build, not channel stuffing)
- Lead times: 52 weeks reliably, with reservations needed beyond
- Shortages expected 1-2 years across wafers, silicon, CPUs, optics, memory
- This is simultaneously a headwind (constraining near-term revenue, pressuring margins) and a moat indicator (Arista's $8.9B in commitments locks in supply that competitors may not have)

---

## 6. Stock price reaction and market narrative

Stock fell ~14% on May 5, despite beat-and-raise:
- Revenue beat by $44M, EPS beat by $0.05
- Full-year guidance raised to $11.5B (+27.7%)
- AI target raised to $3.5B

**Why the selloff:**
1. Q2 guidance ($2.8B) was below some buy-side models that extrapolated Q1's beat
2. Supply chain warning of 1-2 year shortages spooked investors
3. Gross margin compression narrative (cost absorption language was blunt)
4. Deferred revenue volatility language created uncertainty about revenue recognition timing

**Post-earnings context (CFO at Needham, May 14):**
- Reframed deferred as demand strength, not revenue delay
- Combined growth metric (54% including deferred) provides better demand picture
- Reiterated comfort with full-year margin and revenue guide

---

## Summary Assessment

| Dimension | Q4 2025 Signal | Q1 2026 Signal | Direction |
|---|---|---|---|
| AI demand | Strong | Stronger (raised target) | Improving |
| Revenue growth | ~30% | 35.1% | Accelerating |
| Gross margin | 63.4% | 62.4% | Compressing |
| Operating margin | ~47% | 47.8% | Stable |
| Deferred revenue | $5.37B | $6.20B | Building |
| Supply chain | Constrained | More constrained | Worsening |
| Customer breadth | Expanding | Expanding (100+ AI) | Improving |
| NVIDIA competition | Acknowledged | Intensifying | Watch closely |

**Net thesis impact:** Q1 2026 supports the bull thesis on AI demand and Arista's positioning in Ethernet networking. The bear case is not demand destruction but rather margin compression (from supply costs + NVIDIA competitive pressure in high-growth leaf segment) and a potential growth deceleration in 2027 as the 800G cycle matures. The $6.2B deferred revenue balance is either a massive coiled spring or a source of future volatility — the next 2-3 quarters will tell.
