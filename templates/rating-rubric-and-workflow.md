# Subjective Rating Rubric & Workflow

How to rate the 13 subjective columns in `00-master/ai_supply_chain_scoring.xlsx` reliably, including how Claude and Dom work together, what biases to guard against, and how to audit calibration over time.

---

## Why this exists

The scoring system has 13 subjective 1-5 ratings spread across AI Thesis (5), Momentum (3), and Risk (5). They carry **~42.5%** of the total score weight by direct contribution (AI Thesis 20% + Risk 15% + the 3 subjective Momentum ratings ≈ 7.5% of the 10% Momentum weight; the 4th Momentum input, 50DMA %, is objective), and they color how you read the objective inputs. If they're miscalibrated, the whole system is miscalibrated.

The goal of this rubric: replace vibes with checkable criteria so two informed people rating the same stock get the same answer.

---

## Category weights — the Weights tab is the single source of truth

These six category weights are **read from** `00-master/ai_supply_chain_scoring.xlsx` → **Weights** tab, which is authoritative. The table below is a mirror kept here for convenience; if it ever disagrees with the Weights tab, **the Weights tab wins and this doc is stale.** `tests/test_rubric_weights_match_workbook.py` fails the build on any drift — it is the gate that catches the AI-Thesis-quoted-at-30%-while-the-model-used-20% error that lived in this file until 2026-07-01.

| Category | Weight |
|---|---|
| Value | 20% |
| Quality | 20% |
| Growth | 15% |
| AI Thesis | 20% |
| Momentum | 10% |
| Risk | 15% |

Do not hand-tune these here. Category-weight changes are gated on measured Information Coefficient (not intuition) and are made in the Weights tab, never in this doc.

---

## The 13 dimensions

### AI Thesis (5 dimensions, 20% category weight)

#### D1. AI Revenue % of Total

**What it measures:** How much of the company's revenue is genuinely tied to AI infrastructure spend, not legacy business with AI marketing applied.

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | >50% of revenue clearly and reportedly AI-infrastructure-tied. Customers are AI buildouts. Loss of AI demand = existential. |
| **4** | 25-50%. Strong AI exposure that's a major growth driver, but not the whole business. |
| **3** | 10-25%. Meaningful AI exposure but legacy/non-AI is still majority. |
| **2** | 5-10%. Some AI exposure, maybe a growing segment, but not yet material. |
| **1** | <5% or unclear. Marketing claims AI exposure but the financials don't show it. |

**Anchor examples (illustrative — refine over time):**
- CoreWeave: 5
- Vertiv, Coherent, Lumentum: 4
- GE Vernova, EQT: 3
- Most utilities with some data-center load growth: 2-3
- Generic industrial conglomerates: 1

**Common failure modes:**
- Counting "data center" revenue as AI revenue (data centers existed before LLMs)
- Believing the IR deck's AI-revenue chart without checking segment disclosures
- Confusing "AI-adjacent" with "AI-driven"

**Sourcing rule:** Cite the specific filing (10-K segment data, 10-Q MD&A, or earnings call transcript) where AI revenue is disclosed or can be reasonably estimated. If estimating, show the math.

---

#### D2. Supply Chain Position

**What it measures:** Where the company sits in the value chain, and whether that position confers pricing power.

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Upstream bottleneck with limited substitutes. Customers must buy from a handful of suppliers. Lead times widening. Pricing power demonstrable. |
| **4** | Upstream with 2-4 viable competitors. Pricing stable to firming. Tight capacity. |
| **3** | Mid-chain with some differentiation. Multiple substitutes exist but switching has cost. |
| **2** | Mid-chain commoditized. Many suppliers; competition mostly on price. |
| **1** | Downstream / commodity. Customer can swap to alternative cheaply and quickly. |

**Anchor examples:**
- ASML (EUV), TSMC (leading-edge), large power transformers right now: 5
- AMAT, LRCX, Bloom Energy, Vertiv liquid cooling: 4
- CoreWeave (multiple competitors but spec advantages): 3
- Generic server OEMs, ODMs: 2
- Pure-play BTC mining capacity: 1-2

**Common failure modes:**
- Conflating "high market share" with "bottleneck" — they're different
- Forgetting that bottlenecks dissolve as capacity comes online (this is a moving rating)
- Rating Position based on past pricing power instead of forward-looking

---

#### D3. Moat Strength

**What it measures:** Durability of competitive advantage. THE most halo-effect-prone rating. Be ruthless.

**Components to consider:**
- IP / process know-how (patents, trade secrets, technical lead)
- Switching costs (customer integration depth)
- Scale advantage (unit cost vs. competitors)
- Network effects (rare in hardware, present in software)
- Regulatory / geographic

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Durable across multiple dimensions. Demonstrated pricing power. Customers stay even when price rises. 10+ year defensibility plausible. |
| **4** | Strong in one or two dimensions. Share held vs. credible competitors. Pricing roughly with inflation. |
| **3** | Modest moat. Share roughly stable but pricing is competitive. |
| **2** | Weak moat. Losing share possible. Price-taker behavior. |
| **1** | No moat. Pure commodity. Win on cost or operations, not on product. |

**Anchor examples:**
- ASML, TSMC at leading edge, NVIDIA (CUDA ecosystem): 5
- Coherent / Lumentum (optical IP), Vertiv (scale + customer entanglement): 4
- CoreWeave (capacity but commoditizing), Intel (legacy IP eroding): 3
- Generic server OEMs, most BTC miners: 1-2

**Common failure modes:**
- Rating Moat = 5 because the stock is up. (Stock price ≠ moat.)
- Rating Moat = 5 because the technology is "cool" rather than because customers can't switch.
- Forgetting that moats can erode (Intel was 5 a decade ago; arguably 2-3 today)

**Bias check:** Would you rate this Moat the same way if the stock were down 40%?

---

#### D4. Capacity Expansion

**What it measures:** Where the company is in its build-out cycle. Are they deploying capital to capture demand, or are they constrained / shrinking?

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Major buildout funded and underway. Multi-year capex program. Customer commitments backing it. |
| **4** | Active expansion in progress. Capacity growing meaningfully YoY. |
| **3** | Steady-state capex. Modest growth aligned with maintenance + organic demand. |
| **2** | Capex constrained or deferred. Underinvesting vs. opportunity. |
| **1** | Shrinking or divesting capacity. Capital flowing out. |

**Anchor examples:**
- Constellation/Talen restarting reactors, CoreWeave building data centers, Bloom Energy fab expansion: 5
- Most semi-equipment companies in current cycle: 4
- Mature utilities with normal capex: 3
- Companies in restructuring: 1-2

**Common failure modes:**
- Rating Capacity = 5 based on a press release rather than disclosed capex commitments
- Ignoring whether the expansion is funded (announced ≠ committed ≠ deployable)

---

#### D5. Hyperscaler Exposure / AI Infrastructure Commitment

**What it measures:** A SINGLE dimension — **strength of tie to the AI-infrastructure buildout** — read through two lenses depending on the company's role. Supply-chain companies (Layers 1-8): direct, material revenue from hyperscaler customers (supplier lens). Hyperscalers/cloud (Layer 9): intensity of AI-infrastructure investment commitment (buyer lens). The 1-5 scale is **parallel across both lenses: 5 = maximally AI-tied for this company's role, 1 = minimal.** A supplier's 5 and a hyperscaler's 5 are deliberately equivalent — both mean "as AI-tied as this kind of company gets" — so their contribution is directly comparable in the cross-layer score (even though the raw evidence, ">30% revenue" vs "$30B+ capex", should not be read literally against each other).

**Criteria — Layers 1-8 (supplier framework):**
| Rating | Definition |
|---|---|
| **5** | Multiple hyperscalers as anchor customers, combined >30% of revenue. Disclosed as "concentrated with major cloud providers." |
| **4** | One hyperscaler as anchor (15-30% of rev), or multiple at 5-15% each. |
| **3** | Selling to hyperscalers but not concentrated (5-15% total). |
| **2** | Indirect exposure — selling to mid-tier customers who sell to hyperscalers. |
| **1** | No meaningful hyperscaler revenue. |

**Criteria — Layer 9 (hyperscaler/cloud framework, added 2026-05-26):**
| Rating | Definition |
|---|---|
| **5** | $30B+/yr AI capex, multi-year committed buildout, clear strategic priority. Signed multi-year infrastructure deals (GPU supply, power PPAs). |
| **4** | $10-30B/yr AI capex, growing commitment, disclosed AI infrastructure roadmap. |
| **3** | $5-10B/yr AI infrastructure investment. |
| **2** | Some AI investment but not primary strategic focus. |
| **1** | Minimal AI infrastructure commitment. |

**Why two frameworks:** D5 was originally designed to score supply chain companies on hyperscaler demand exposure. But when applied to the hyperscalers themselves, it penalized companies like META (D5=1) for not selling cloud compute, even though META spends $40B+/yr on AI infrastructure and drives massive upstream demand. The Layer 9 framework measures the same underlying signal — how tied is this company to the AI buildout — from the buyer's side rather than the seller's side. (Methodology change approved 2026-05-26.)

**Cross-framework comparability (P5 / finding F9, examined 2026-07-02).** F9 flagged that a "5" encodes two different constructs yet is ranked across layers in one Total Score. Examined empirically: Layer-9 (buyer) mean D5 = 3.7 vs supplier mean 3.3, and half of Layer 9 rates 5 — but those are the mega-hyperscalers (META/MSFT/GOOGL/AMZN) genuinely spending $30–80B/yr, i.e. the actual AI-buildout leaders, so the higher buyer mean is *real*, not a calibration error. **Decision: keep both lenses on the common absolute 5-max-for-role scale; do NOT normalize D5 within-framework.** Percentile-within-framework normalization was tested and would dock those four ~1 Total pt each for being (correctly) common in their layer — under-crediting the real AI leaders, the opposite of an improvement. The parallel 1→5 structure already puts the lenses on one comparable strength scale by construction. (See CLAUDE.md rule 23.)

**Anchor examples:**
- *Supplier framework:* CoreWeave (Microsoft is anchor), Vertiv: 5. Coherent, Lumentum: 4. Most semi-equipment: 3-4. Utilities with DC load: 2-3.
- *Hyperscaler framework:* META ($40B+ capex, $100B AMD deal, multi-GW nuclear PPAs): 5. MSFT ($80B+ capex, OpenAI partnership): 5. ORCL (growing but smaller scale): 4-5.

**Common failure modes:**
- Counting "data center" exposure as hyperscaler exposure (data centers include enterprise, gov, second-tier clouds)
- Rating high based on a single recent customer announcement
- Ignoring that hyperscaler concentration is BOTH a positive (anchor demand) and a risk (single-customer dependency) — it's worth a 5 on Hyperscaler Exposure AND a 1 on Customer Concentration Risk
- *For Layer 9:* Rating based on announced capex alone without checking for committed deals (signed PPAs, binding GPU supply agreements) that demonstrate follow-through

---

### Momentum (3 dimensions, 10% category weight)

#### M1. EPS Revisions last 90 days

**What it measures:** Direction of sell-side estimate revisions over the last 90 days. The most objective of the "subjective" columns — Yahoo and Zacks have free revision tracking.

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Multiple upward revisions. Beat-and-raise pattern. Consensus moving higher. |
| **4** | Net positive revisions. Some up, few down. |
| **3** | Stable estimates. Neutral revision trend. |
| **2** | Net negative revisions. Some cuts. |
| **1** | Multiple cuts. Consensus moving sharply lower. |

**Sourcing rule:** Use Yahoo Finance "Analysis" tab → Earnings Estimate revisions, or Zacks Estimate Movement.

**Bias check:** This should be a near-mechanical rating, not a judgment call. If you find yourself agonizing, you're overthinking it.

---

#### M2. Relative Strength vs Sector

**What it measures:** Stock's price performance over the last 3-6 months relative to a sector benchmark.

**Sector benchmarks:**
- Semis: SOXX / SMH
- Software: IGV
- Utilities: XLU
- Industrials: XLI
- Energy: XLE

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Outperforming sector by >20% over 6 months. Clear leader. |
| **4** | Outperforming sector by 5-20%. |
| **3** | In line with sector ±5%. |
| **2** | Underperforming sector by 5-20%. |
| **1** | Lagging sector by >20%. |

**Bias check:** This is a momentum input, not a quality input. A great company with poor near-term price action might warrant a 2 here — and that's correct, that's what the rating means. Don't fight the read.

---

#### M3. Insider Activity

**What it measures:** Officers and directors' open-market trades over the past 12 months. Sourced from Form 4 filings on SEC EDGAR.

**Important framing:** Insider selling is ambiguous; insider buying is signal. Academic research (Lakonishok & Lee 2001, Jeng-Metrick-Zeckhauser 2003) finds insider buying predicts returns reliably while selling is much noisier. After a multi-year run, executives have legitimate diversification reasons to trim — the same logic we'd apply to our own concentrated portfolio positions. Apply the same standard to them that we apply to ourselves.

**Use % of holdings, not absolute share counts.** A CEO selling 500K shares means different things if they hold 5M vs. 500M.

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Multiple insiders buying in open market, OR any single open-market buy >$1M discretionary |
| **4** | One insider buying meaningfully. Selling <5% of holdings annually. |
| **3** | Routine selling, <15% of holdings over 12 months. No discretionary buying. (This is the "diversification" default for post-rally situations.) |
| **2** | Discretionary selling 15-30% of holdings over 12 months across multiple executives. |
| **1** | Heavy selling >30% of senior holdings, OR executive resignations following sales, OR insider selling concentrated immediately before negative news. |

**Decision procedure (apply in this order — do not skip steps):**

1. **Find open-market BUYS first.** If ≥2 insiders made open-market discretionary buys in the last 12 months → **5**, full stop. If exactly 1 did → **4**. Dollar size does NOT downgrade this: the only dollar threshold in the rubric is the *single-buyer* path to 5 (a lone buy >$1M). Multiple buyers = 5 regardless of dollar amounts. (Established 2026-05-28 after CEVA was wrongly rated 4 — CEO+CFO+Director all bought but the rating was discounted on "modest" dollar size, which is a flagged failure mode.)
2. **If no buys, classify the SELLS by type before scoring.** Sales that are 10b5-1 pre-scheduled, GRAT transfers, or option-exercise-plus-same-day-sale are **routine** → default **3**, even if they total >15% or >30% of holdings. The 15-30% (band 2) and >30% (band 1) thresholds apply ONLY to *discretionary open-market* selling. Do not push a name to 2 or 1 on the size of 10b5-1 sales. (Established 2026-05-28 after AIP was wrongly rated 2 — two directors sold 28% and 48% via 10b5-1 plans, which the rubric says to treat as routine.)
3. **Only discretionary open-market sells reach bands 2 and 1.** Size them by % of holdings (never absolute share counts): 15-30% across multiple execs → 2; >30%, or resignations-after-sales, or selling right before bad news → 1.
4. **Default when there's neither buying nor discretionary selling = 3** (the post-rally diversification baseline).

**Sourcing rule:** SEC EDGAR Form 4 filings. Critical distinctions:
- **10b5-1 pre-scheduled trades** = much less informative. Treat as routine.
- **Open-market discretionary trades** = more informative.
- **GRAT transfers** = estate planning, not signal. Don't count as selling.
- **Option exercise + same-day sale** = often tax management around expiry, not view.

**Common failure modes:**
- Treating large 10b5-1 sales as bearish — they're often automated quarterly programs
- Counting absolute share counts instead of % of holdings (this is the big one)
- Ignoring small but consistent open-market BUYING by board members — that often IS material
- Applying a different standard to executives than you'd apply to yourself in the same position

**The key question:** Is anyone BUYING? Absence of buying matters more than presence of selling. If a CEO believes the stock is undervalued after a pullback, they can demonstrate that with a meaningful open-market purchase. If no insider does that across multiple opportunities, the absence is the signal.

---

### Risk (5 dimensions, 15% category weight) — 5 = LOWEST risk

This is inverted from the others. **5 means the stock has LOW risk on this dimension, 1 means HIGH risk.**

#### R1. Customer Concentration

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Diversified. No customer >15% of revenue. |
| **4** | Top customer 15-25%. Manageable concentration. |
| **3** | Top customer 25-40%. Real dependence but not existential. |
| **2** | Top customer 40-60%. Major dependency. |
| **1** | Single customer >60%, or near-single-buyer market structure. |

**Sourcing rule:** 10-K usually discloses any customer >10% of revenue. Industry knowledge fills gaps.

---

#### R2. Geographic / Export Risk

**Revised 2026-06-12 (approved by Dom).** The original bands were written in China/export-control
language only, which left shipment-geography concentration (e.g., TER at 41% Taiwan + 19% Korea)
and asset-location risk unscored by the text — forcing case-law judgment calls. These bands codify
the risk-leg tiering that the 2026-06-12 calibration review found already implicit in the sheet.
(Pre-revision bands: see git history for this file.)

**The three risk legs (assess each from filings):**
- **Demand leg** — revenue shipped to a risk geography (Taiwan/Korea strait exposure, etc.).
  Substitutable in principle if the customer survives the shock.
- **Policy leg** — China/trade-policy exposure: meaningful China revenue under current or
  plausible restrictions.
- **Asset leg** — production assets physically located in a risk geography (fabs in Taiwan,
  plants in a conflict zone). Not substitutable.

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | No legs. Domestic/diversified — no single geographic or trade-policy shock plausibly impairs >10% of revenue. |
| **4** | One leg, demand only. Shipment concentration to a risk geography (>25% of revenue), no material China/policy overhang. |
| **3** | Two legs. Shipment concentration PLUS China/trade-policy overhang (current or plausible restrictions; past impacts absorbed/stabilized). |
| **2** | Asset leg, OR policy currently impairing material revenue (e.g., China DC revenue = $0, procurement bans) but not existential. |
| **1** | Active, material, unmitigated impairment underway — geographic/policy shock with existential-scale revenue impact. |

**Rationale requirement (mandatory, added with this revision):** every R2 rating must name
(a) the single worst plausible shock for this name and (b) the % of revenue exposed to it,
with the filing citation. "Diversified" without a named shock is not a rationale.

**Scope note:** supply-side foundry dependence (a fabless company's chips made at TSMC) is NOT
an R2 leg — it is industry-systemic and belongs in the thesis narrative, not this rating.
R2 scores the company's own revenue geography and asset footprint.

**Anchor examples (as of 2026-06-12):** EME, FIX (US-only): 5. TER, ONTO, FORM, CAMT
(Asia-shipment concentration, limited China overhang): 4. AMAT, LRCX, KLAC, ASML, AMD
(shipment concentration + absorbed export-control impact): 3. TSM (fabs in Taiwan), NVDA
(China DC = $0), MU (China procurement ban): 2.

**Sourcing rule:** Geographic revenue breakout in 10-K/10-Q. Property/asset locations from
10-K Item 2. Current BIS Entity List status (entity-list.com or BIS website).

---

#### R3. Balance Sheet Risk

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Net cash position. Strong FCF generation. No debt concerns. |
| **4** | Modest leverage. ND/EBITDA <2x. Maturities well-spread. |
| **3** | Average leverage for sector. ND/EBITDA 2-4x. |
| **2** | Elevated leverage. ND/EBITDA 4-6x. FCF marginal. Maturity wall in next 2 years. |
| **1** | Stressed. ND/EBITDA >6x. Dilution risk. Going concern flags. |

**Note:** This overlaps with the Quality category's ND/EBITDA input. The difference: ND/EBITDA is the input metric; Balance Sheet Risk is the holistic view including maturities, FCF resilience, and dilution risk.

---

#### R4. Regulatory / Litigation Risk

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | Clean. No material overhangs. |
| **4** | Routine matters only. No material disclosed risks. |
| **3** | Some pending matters disclosed but immaterial. |
| **2** | Material litigation or active regulatory investigations. |
| **1** | Major regulatory threat (e.g., DOJ antitrust, FDA action, class action that could be material). |

**Sourcing rule:** 10-K "Legal Proceedings" section + recent 8-Ks announcing investigations or lawsuits.

#### R5. Disruption Risk (added 2026-06-17, see CLAUDE.md rule 16)

Business-model durability — does the *revenue stream survive*, vs. R1–R4 which ask if earnings are *safe now*. 5 = most durable / lowest disruption risk.

**Criteria:**
| Rating | Definition |
|---|---|
| **5** | No credible AI/structural disruption to the core revenue model in ~5yr. **Default for all non-Layer-10 names** (physical infra, power, fabs, semis equip, HDD, networking, cloud compute). |
| **4** | Durable; AI net-neutral/tailwind or threatens only a peripheral line (security software, consumption-priced data/observability, AI-native beneficiaries). |
| **3** | Contested but a structural moat (file format, regulatory, data, ecosystem) resists core disruption. |
| **2** | Core pricing model/workflow is a direct agentic-AI target; durability in question, no active erosion yet (or a durable sub-segment offsets). |
| **1** | AI-native tools / the model layer can directly produce the core output or fully automate the workflow, AND active erosion is visible (price concession, funnel/share loss). |

**Scope:** only Layer 10 carries sub-5; everything else defaults to 5. Apply the absolute-lens stress test across the whole Layer-10 cohort, not relative ranking. Watchlist col AL/38.

---

## How we work together: the rating session

For each new stock that crosses the "deserves a rating" threshold (typically after a `/deep-dive` has been completed):

### Step 0 — Pre-rating research (MANDATORY)

Before any rating proposal, Claude MUST invoke `/refresh-context $TICKER` to pull fresh research. Claude's training data is stale; without an explicit fresh-research pass, ratings will be silently biased by 12-month-old mental models.

The `/refresh-context` command does:
1. Articulates Claude's pre-research mental model (what Claude thinks it knows about the ticker)
2. Pulls latest filings (10-Q, 8-K) via `scripts/sec_edgar.py`
3. WebSearch with current year for: quarterly results, AI revenue, customer wins, layer-specific dynamics
4. WebFetch latest earnings call transcript (best-effort)
5. Writes briefing to `per-stock/$TICKER/context-{YYYY-MM-DD}.md`
6. Surfaces the **diff between pre-research mental model and fresh reality** — this is the most important section of the briefing

**Established 2026-05-18 after Layer 6 rating session.** Fresh research on AMD surfaced META 6 GW deal, MI450 customer wins, and ROCm-7 PyTorch first-class support — none of which were in the original rating proposal. Three D-dimensions shifted from 4 → 5; AMD TOTAL moved from ~73 to ~76.5. Same staleness pattern almost certainly exists on other names. **Skipping this step means missing buy opportunities through systematic underweighting.**

The rating session below references the briefing file. If the briefing surfaces something the rater didn't know, that's a rating update, not "anchoring on fresh info" — that's the calibration the system depends on.

### Step 1 — Claude proposes initial ratings

Claude reads the deep-dive output (`thesis.md`, `financials.xlsx`, filings, transcripts) and writes a draft rating sheet:

```
TICKER: BE (Bloom Energy)
Date: 2026-05-17

D1. AI Revenue %: 4
   Rationale: ~40% of revenue tied to data center / AI buildouts based on Q4 2025 10-K segment disclosure. Trending up sharply.
   Source: 10-K FY2025, Item 7 MD&A
   Confidence: Medium (estimate; company doesn't disclose explicit "AI revenue")

D2. Supply Chain Position: 4
   Rationale: Fuel cells are an upstream power-bottleneck solution with 2 viable competitors (Plug, Ballard) but Bloom has scale lead and proven hyperscaler deployments.
   Source: Industry context + 10-K customer disclosures
   Confidence: High

... (continues for all 13 dimensions)
```

**Critical:** Every rating must include:
- One-sentence rationale
- Source citation
- Confidence level (Low / Medium / High)

### Step 2 — Dom reviews

You read Claude's draft. For each rating, do one of:

- **Accept** — write "OK" or nothing; the rating stands
- **Disagree with new value** — write the new rating and your reasoning in one sentence
- **Disagree with rationale** — same rating but a different reason; write both
- **Flag for discussion** — "Let's talk about D3 Moat"

### Step 3 — Discuss divergences

For any flag-for-discussion item, you and Claude back-and-forth. Claude must defend the rating with evidence, you must articulate the counter. The disagreement is the most valuable part of this whole process — it's where blind spots get caught.

### Step 4 — Finalize and log

Final ratings get entered in the spreadsheet. Ratings + rationales + date get appended to a "Rating Audit Log" sheet (see Audit section below).

---

## Bias checks to run before finalizing

Before committing a rating, ask:

1. **Endowment check.** "Would I rate this the same if I didn't already own it?"
2. **Halo check.** "Did I rate this dimension high because the company is doing well overall?"
3. **Recency check.** "Am I anchoring on the last earnings call or the durable picture?"
4. **Anchor comparison.** "How does this compare to my anchor examples at this rating level?"
5. **Narrative check.** "Am I rating this because the Aschenbrenner story fits, or because the evidence demands it?"
6. **Inverse test.** "What would I need to see to rate this one level lower? Do I see any of it?"

If any of these checks raises a concern, drop the rating by one level and require explicit evidence to raise it back.

---

## Audit mechanism — quarterly and annual

### Quarterly review (run alongside `/rescore-quarterly`)

For every stock in the Watchlist whose Tier is ✓✓ or higher:
- Re-read the rating rationales from last quarter
- For each rating: has anything material changed?
- Track ratings that have moved by 2+ levels since initial — these are either real changes (good) or calibration drift (bad)

### Annual calibration check

Once a year, do a full audit:
- Take all ✓✓✓ ratings from a year ago. Did those stocks outperform the sector?
- Take all ✗ ratings from a year ago. Did those underperform?
- For mid-tier stocks, was performance roughly random or did the rating predict anything?

**If calibration is off:**
- Identify which dimension was most miscalibrated
- Adjust the criteria for that dimension (be specific — change the rubric definition, not just the score)
- Document why the change was made

**Critical rule:** Do NOT retroactively change past ratings. Hindsight bias rewriting history makes the audit useless. Past ratings are frozen — the rubric evolves.

### Rating Audit Log

Add a sheet to `00-master/ai_supply_chain_scoring.xlsx` named "Rating Audit" with columns:
- Date
- Ticker
- Dimension (D1-D5, M1-M3, R1-R5)
- Rating
- Rationale (one line)
- Source
- Confidence
- Initial / Update / Override

Every rating change goes here. Append-only. This is the diary that lets you debug your own judgment over time.

---

## Claude's limitations to remember

This rubric works because we're collaborating, not because Claude is always right. Specifically:

- **Claude can be sycophantic.** If you push back on a rating, Claude may cave when it shouldn't. Watch for unprincipled retreats.
- **Claude can hallucinate specifics** about smaller companies. Always verify a Claude claim against the source filing for any rating you're uncertain about.
- **Claude doesn't have real-time data.** Insider activity, recent press, very recent earnings — Claude's view may be stale.
- **Claude may default to "balanced" ratings.** When uncertain, Claude tends toward 3 rather than committing to 2 or 4. If a 3 feels like a cop-out, push for a decision.
- **Claude reflects training-data biases.** Including over-indexing on well-known names and under-rating unfamiliar ones.

Your job in the partnership is to push back where Claude is weak. Claude's job is to provide structure, citations, and a second pair of eyes that doesn't get emotionally attached to positions.

---

## A note on getting started

Don't try to perfectly rate everything immediately. The rubric works because it's applied consistently, not because the first ratings are perfect. Better to:

1. Rate 10 stocks together using this process
2. After 3 months, audit those ratings — what did you see vs. what actually happened?
3. Refine the rubric based on what you learned
4. Then expand to the next 20

Aim for "directionally right and improving" over "perfectly right immediately." The audit log is what makes improvement possible — without it, you're just guessing each quarter.
