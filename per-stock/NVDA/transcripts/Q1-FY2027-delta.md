# NVDA Q1 FY2027 — Delta Summary vs. Q4 FY2026
**Prepared:** 2026-05-26
**Source:** Q1 FY2027 earnings call (2026-05-20); Q4 FY2026 baseline revenue $68.1B

> Prior quarter transcript not on file; deltas are Q1 FY2027 vs. Q4 FY2026 financial results and vs. the narrative framing on the prior call where available from public summaries.

---

## 1. Management tone on AI demand

**Shift: Materially more bullish. Language turned structurally positive.**

Q4 FY2026 framing (from public reporting): demand strong but supply-constrained; Blackwell ramp the key variable.

Q1 FY2027 framing: "Demand has gone parabolic." Jensen explicitly declared agentic AI as a commercial reality — "Tokens are now profitable" — framing demand as self-reinforcing rather than speculative capex. This is a tone upgrade. Prior quarters positioned AI capex as forward-looking investment; Q1 FY2027 positions it as current-revenue-generating activity.

**Thesis relevance:** High. The shift from "AI capex as investment" to "AI capex as ROI-generating" is the key thesis inflection. It makes demand more durable and less cyclical.

---

## 2. Customer concentration — the 50/50 split

**Shift: Significant structural change in reported mix. New disclosure framework.**

Q4 FY2026: NVIDIA reported Data Center as a single segment with Compute/Networking sub-lines. No explicit hyperscaler vs. enterprise split.

Q1 FY2027: NVIDIA **restructured its reporting** into Hyperscale ($37.9B) and ACIE — AI Cloud, Industrial, Enterprise ($37.4B). The 50/50 split is the headline. But the growth rates tell the story:
- Hyperscale: +12% QoQ
- ACIE: +31% QoQ

**This is the most important structural development in the quarter.** ACIE growing 2.6x faster than hyperscale means NVIDIA's demand is diversifying away from 5–6 hyperscalers toward a much broader base. Concentration risk is actively declining.

Sovereign AI sub-segment: +80% YoY, ~40 countries. This is a new demand vector that was only nascent a year ago.

**Risk implication:** The prior thesis concern about hyperscaler-capex-pause risk is materially reduced. A pause by one or two hyperscalers now only affects ~50% of revenue, and the ACIE segment has its own independent demand drivers.

---

## 3. AI revenue mix

**No change needed — NVDA is ~92% Data Center by revenue.**

Data Center: $75.2B of $81.6B total = 92.1% of revenue. Gaming/Edge Computing: ~$6.4B (7.9%). There is no ambiguity about AI revenue concentration — NVIDIA effectively is an AI infrastructure company with a legacy edge/gaming segment.

---

## 4. Networking revenue — the upside surprise

**Shift: Networking is now a major standalone business.**

Q4 FY2026 networking: ~$5.0B (estimated, based on prior disclosures; +34% YoY in that quarter).
Q1 FY2027 networking: $14.8B (+199% YoY, +196% QoQ approximation — this is the largest single-quarter jump).

The composition:
- InfiniBand: 4x+ YoY (next-gen XDR deployments for large cluster builds)
- Spectrum-X Ethernet: now larger than "all Ethernet AI networking peers combined"

**What this means:** NVDA networking is no longer just an adjacency — at $14.8B quarterly run rate that's a ~$59B annualized business in its own right, larger than most semiconductor companies' total revenue. This directly benefits Mellanox-heritage products and has upstream implications for optical transceiver suppliers (CIEN, COHR, IIVI, AAOI).

**NVLink Fusion (Marvell):** Announced at GTC (pre-earnings), not extensively discussed on the call. This allows third-party custom ASICs to connect into NVIDIA's NVLink fabric. Strategically significant: NVDA is positioning NVLink as an industry-standard interconnect fabric rather than a moat-protecting walled garden. The bet is that custom ASICs route through NVLink anyway, making NVDA the infrastructure layer even in a world of ASIC proliferation.

---

## 5. Capex / capacity / supply chain

**Shift: Supply commitment stepped up significantly.**

| Metric | Q4 FY2026 | Q1 FY2027 | Change |
|---|---|---|---|
| Inventory | $21.4B | $25.8B | +$4.4B |
| Supply commitments (total incl. prepaids) | $119.0B | $145.0B | +$26.0B |
| Quarterly revenue | $68.1B | $81.6B | +$13.5B |

The $26B increase in total supply commitments against a $13.5B sequential revenue increase means NVIDIA is committing supply well ahead of recognized revenue — building a demand buffer. This is either confidence or defensiveness (locking in TSMC capacity ahead of Vera Rubin ramp). Given the Q2 guide of $91B, the buffer looks intentional.

Partner data centers >10MW: nearly doubled YoY, now >80 sites. This signals that the physical infrastructure build-out to absorb NVDA product is accelerating.

**Vera Rubin timeline (key update):** Production shipments begin Q3 2026; ramp continues Q4 2026; Q1 FY2028 "certainly going to be very big." Prior GTC disclosure had H2 2026 broadly — the call confirmed Q3 specifically.

---

## 6. Forward guidance vs. prior

| | Q4 FY2026 Actual | Q1 FY2027 Actual | Q1 FY2027 Guide (given at Q4) | Q2 FY2027 Guide |
|---|---|---|---|---|
| Revenue | $68.1B | $81.6B | ~$77.2B (midpoint) | $91.0B ±2% |
| Non-GAAP GM | 73.5% | 75.0% | ~73.0% | 75.0% ±50bps |

Q1 beat its own guidance on revenue by ~$4.4B. Q2 guide of $91B was above consensus of ~$86.8B — a ~$4.2B beat-and-raise at the guidance line.

The sequential pattern: Q4→Q1: +$13.5B, Q1→Q2 guided: +$9.4B. Growth rate is decelerating in absolute dollars but still massive in absolute terms.

---

## 7. China — zero revenue, no path

**Shift: Status quo maintained. No change from Q4. Now two consecutive quarters of zero.**

China data center compute revenue: zero in Q1; zero in Q2 guidance.

Management declined to speculate on re-engagement timeline. The situation: H200 export licenses required; none granted; no anticipated timeline. The prior H20 product (designed specifically to comply with prior export controls) is now also restricted.

**Quantification:** At peak China represented ~20–25% of data center revenue (FY2024). At current $75B quarterly DC run rate, China exclusion represents a structural revenue ceiling of uncertain size. Management's position is this is already fully priced in — "consistent with last quarter." The upside risk (any China normalization) is not in guidance.

---

## 8. New risks raised

1. **OpEx acceleration:** Full-year OpEx growth "upper 40s%" YoY. This is fast — faster than revenue growth on a percentage basis if revenue growth eventually normalizes. The driver is R&D (Rubin, next-gen) and internal AI compute spend. Operating leverage thesis is temporarily pressured.

2. **Export licensing uncertainty:** Specific language around "uncertain whether any imports will be allowed" for China signals the situation could worsen (further restrictions) or improve (licenses granted) — binary and unpredictable.

3. **Supply chain complexity at scale:** Management flagged the "unprecedented" complexity of managing $145B in supply commitments. At this scale, execution risk is non-trivial — a TSMC yield issue or CoWoS packaging constraint could affect revenue cadence.

4. **Vera Rubin ramp execution:** The product is on track for Q3 production, but the transition from Blackwell to Rubin will involve a customer migration cycle. Any delay or yield issue would impact H2 FY2027 growth expectations.

---

## 9. Thesis-relevant items for NVDA

### Supports thesis:
- Revenue growth re-accelerating at scale ($81.6B vs. $68.1B). Not a deceleration story.
- ACIE growing 31% QoQ — enterprise/sovereign demand is real, not just hyperscaler.
- Networking $14.8B is a new profit driver that compounds the data center moat.
- $91B Q2 guide — consensus was $86.8B. Not priced in.
- Vera Rubin confirmed Q3 — no product slip.
- NVLink Fusion = NVDA as infrastructure standard even in ASIC world.
- FCF $48.6B — $192B+ annualized FCF run rate. Capital return ($80B buyback) is real.

### Potential thesis pressure:
- OpEx +upper 40s% YoY means operating leverage narrative needs refinement.
- China zero revenue is a permanent headwind (for now) to TAM realization.
- Supply commitments at $145B — if demand normalizes, this becomes inventory overhang risk.
- No verbatim competitive commentary on AMD/ASICs — signals either non-concern or deliberate avoidance. Worth monitoring.

### Neutral / watch:
- Hyperscale growing "only" 12% QoQ — still enormous in absolute terms but the slowdown vs. ACIE deserves watching.
- Networking tripling YoY creates optical/networking names as must-watch for confirmation (CIEN, COHR, AAOI).

---

## 10. Financial inputs already updated (per weekly scan Step 6)

| Metric | Value | Source |
|---|---|---|
| Fwd P/E | 16.99 | Weekly scan 2026-05-26 |
| EV/EBITDA | 31.24 | Weekly scan 2026-05-26 |
| FCF Yield % | 2.29% | Weekly scan 2026-05-26 |
| Last Updated | 2026-05-26 | — |

**Subjective ratings not modified per task instructions. Those require the Dom + Claude collaboration workflow per CLAUDE.md §2.**
