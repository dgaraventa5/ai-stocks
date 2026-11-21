# Prompt for Grok — ANT (Anthropic) subjective rating pass

Paste everything below the line into Grok. Attach or paste `per-stock/ANT/context-2026-11-21.md` where it says [BRIEFING].

---

You're helping me rate one stock in a personal equity-research system I run. I need your independent judgment on 13 ratings, each on a 1–5 scale, with evidence. Please read all of this before you start.

## The project in one paragraph

I track ~218 companies across the AI supply chain, from power generation and chips through data centers, cloud and AI software. Each company gets a 0–100 Total Score from six categories: Value 20%, Quality 20%, Growth 15%, AI Thesis 20%, Momentum 10%, Risk 15%. Value, Quality and Growth come from objective data (P/S, margins, growth rates and so on), and those are already filled in for this company. The other three categories come from 13 judgment ratings, 1–5 each. That's your job. The top-ranked names feed a small real-money portfolio, so these ratings matter. The point of the system is independent conviction, not echoing consensus or company marketing.

## The company

**ANT — Anthropic, PBC**, maker of the Claude AI models. It listed on Nasdaq on 2026-11-19 at $83 (largest IPO on record, $81.3B raised) and closed at $88.91 on 2026-11-20. Its only financial disclosure so far is the IPO prospectus (424B4, SEC accession 0001628280-26-074944, CIK 0002130357). It has filed no 10-Q, no 10-K and held no earnings call. I put it in **Layer 10: Models, Software & Applications**.

A research briefing with the key prospectus facts and citations is attached: [BRIEFING]

## Why you, and a warning that applies to you too

The briefing was written by Claude, which Anthropic makes, so I'm getting the ratings from a different model. But you have a stake too: xAI, which makes you, is now part of SpaceX (ticker SPCX, also on my watchlist), and Grok competes with Claude. So:

- **Treat the briefing as a lead, not a source.** Check any fact that a rating depends on against the prospectus (sec.gov) or a named, dated news source. Tell me if anything in the briefing is wrong or missing.
- **Ask yourself on every rating:** would I give the same number to OpenAI, Google DeepMind or xAI on the same evidence? If not, say why.
- No "this is the most important company in the world" reasoning, and no "it's overhyped" reasoning either. Rate the evidence against the band definitions.

## Rules that matter for this pass

1. **Cite every factual claim**: the filing and page/section, or the URL and date. Unsourced = unusable.
2. **Flag, don't assume.** If the evidence for a dimension doesn't exist yet (likely for the Momentum ratings on a two-day-old stock), say so and give the default the rubric implies, marked as a default. Never invent a number.
3. **Rate on the band definitions below, literally.** If the rubric's wording doesn't fit a foundation-model company, say so explicitly rather than quietly bending it. Those framework questions are the most useful thing you can give me.
4. **Give a confidence for each rating:** Low / Medium / High.
5. **Use the current year (2026) in searches.** Your training data may be stale; check for developments after 2026-11-19.
6. Don't recommend buying or selling. I make that call.

## The 13 ratings and their bands

**Scoring direction:** for AI Thesis and Momentum, 5 = best. For **Risk, 5 = LOWEST risk** (inverted).

### AI Thesis (20% of total score)

**D1. AI revenue % of total.** How much revenue is genuinely AI-driven, not legacy revenue with AI branding.
5 = >50% clearly AI-tied; 4 = 25–50%; 3 = 10–25%; 2 = 5–10%; 1 = <5% or unclear.

**D2. Supply-chain position.** Where it sits in the value chain and whether that gives pricing power.
5 = bottleneck with few substitutes, pricing power demonstrable; 4 = 2–4 viable competitors, pricing stable to firming, tight capacity; 3 = mid-chain with some differentiation, substitutes exist but switching has a cost; 2 = commoditized, competes on price; 1 = customer can swap cheaply and quickly.
Anchors: ASML/TSMC leading-edge = 5; AMAT/LRCX = 4; CoreWeave = 3. Don't confuse high market share with a bottleneck.

**D3. Moat strength.** Durability of advantage: IP, switching costs, scale, network effects. The rating most prone to halo effect, so be ruthless.
5 = durable across several dimensions, customers stay when price rises, 10+ years plausible; 4 = strong in one or two dimensions, holds share vs credible rivals; 3 = modest, pricing competitive; 2 = weak, could lose share, price-taker; 1 = commodity.
Anchors: NVIDIA (CUDA), ASML, TSMC = 5; CoreWeave = 3. Bias check: would you give the same rating if the stock were down 40%?

**D4. Capacity expansion.** Where it is in its build-out.
5 = major build-out funded and under way, multi-year, backed by commitments; 4 = active expansion, capacity growing meaningfully; 3 = steady-state; 2 = constrained or deferred; 1 = shrinking. Announced ≠ committed ≠ funded; check which.

**D5. Tie to the AI build-out, Layer-10 reading.** For Layer 10, D5 asks **"is AI demonstrably working for this business?"**
5 = AI is a measured growth engine: disclosed AI usage/revenue/KPI metrics growing fast and visible in company-level results (one quarter of evidence is enough); 4 = quantified AI impact on at least one major line with company results moving the same way; 3 = AI products shipped with disclosed usage but no measured effect on revenue or margins yet; 2 = launches, pilots and narrative only; 1 = no meaningful AI use, or AI eroding the business.
Guards: rate measured evidence, not narrative; discount metrics whose definitions keep widening; demand *from* AI buyers belongs in D1, not D5.
**Framework question for you:** this lens was written for companies that *use* AI (software, ad platforms). Anthropic *makes* the models. Tell me whether this lens works for a model maker, how you applied it, and whether you'd propose a different reading. I decide that part.

### Momentum (10%)

**M1. EPS revisions, last 90 days.** 5 = multiple upward revisions; 4 = net positive; 3 = stable; 2 = net negative; 1 = multiple cuts. *There is no 90-day revision history for a stock that listed on 2026-11-19, and underwriter research initiates around mid-December. Say so; don't manufacture a trend.*

**M2. Relative strength vs sector, 3–6 months** (software benchmark: IGV). 5 = beat the sector by >20%; 4 = 5–20%; 3 = within ±5%; 2 = lagged by 5–20%; 1 = lagged by >20%. *Two trading days of history; same caveat.*

**M3. Insider activity, 12 months, from SEC Form 4s.** Procedure in order: (1) ≥2 insiders made open-market buys → 5; exactly one → 4. (2) Pre-scheduled 10b5-1 plan sales, estate-planning transfers and option-exercise-plus-sale are routine → 3, whatever their size. (3) Only discretionary open-market selling reaches 2 (15–30% of holdings across several executives) or 1 (>30%, or selling right before bad news). (4) No buying and no discretionary selling → 3. Private-placement purchases are not open-market buys. *Only Form 3s exist so far and the lockup is in force.*

### Risk (15%) — 5 = LOWEST risk

**R1. Customer concentration.** 5 = no customer >15% of revenue; 4 = top customer 15–25%; 3 = 25–40%; 2 = 40–60%; 1 = >60%. If contracted backlog is ≥1× trailing revenue, also grade the top customer's share of backlog and use whichever is worse. Consider separately whether sales channels (AWS Bedrock, Google Vertex, Microsoft) are a concentration the end-customer numbers hide, and tell me how you treated that.

**R2. Geographic / export risk.** Three legs: demand (revenue concentrated in a risk geography), policy (China or trade-policy exposure, or government action impairing revenue), asset (production assets in a risk geography). 5 = no legs, no single shock plausibly impairs >10% of revenue; 4 = demand leg only; 3 = two legs; 2 = asset leg, or policy currently impairing material revenue; 1 = active, existential-scale impairment. **Required:** name the single worst plausible shock and the % of revenue exposed, with a citation. Question for you: does the US Department of War supply-chain-risk designation belong here (policy leg), in R4, or both? Say which and why; don't count it twice.

**R3. Balance-sheet risk.** 5 = net cash, strong FCF, no debt concerns; 4 = modest leverage (<2× ND/EBITDA); 3 = 2–4×; 2 = 4–6×, marginal FCF, maturity wall; 1 = >6×, dilution risk, going-concern flags. This is the holistic view: weigh the ~$232–245B post-IPO cash against the ~$900.9B of mostly take-or-pay compute commitments ($70.7B due within 12 months), the Amazon rollover notes (~1.55B shares still to convert) and the share-price-linked public-benefit share contributions.

**R4. Regulatory / litigation risk.** 5 = clean; 4 = routine only; 3 = pending but immaterial; 2 = material litigation or active investigations; 1 = major regulatory threat. Check the current status of: the Department of War designation litigation (N.D. Cal. ruled for Anthropic 2026-08-27; the D.C. Circuit upheld the §4713 designation 2–1 on 2026-09-25; rehearing en banc petitioned), the October 2026 FTC civil investigative demand, and the copyright suits (Bartz settled for $1.5B; Concord Music and others pending). Also search federal dockets for any securities suit filed since the IPO. A plaintiff-firm "investigation" press release is not a filed case.

**R5. Disruption risk.** Does the revenue model survive ~5 years? 5 = no credible disruption to the core model; 4 = durable, AI net-neutral or a tailwind; 3 = contested, but a structural moat resists; 2 = core pricing/workflow is a direct target, durability in question, no erosion yet; 1 = the core output can be produced by others and erosion is visible (price cuts, share loss). For a model maker the threat is other frontier labs, open-weight models and price competition per token. Rate that, with evidence of pricing trends.

## What I need back

**1. A table, one row per rating:**

| Dim | Rating (1–5) | Confidence | Rationale (2–4 sentences) | Sources (filing + page, or URL + date) | Default? (Y if no evidence yet) |

**2. Framework questions**, answered separately: D5's lens for a model maker; where the government designation belongs (R2/R4); how you treated cloud-channel dependence in R1; any other band that didn't fit.

**3. Corrections:** anything in the briefing you found wrong, outdated or missing, with sources.

**4. The two ratings you're least sure of**, and what evidence would change them.

**5. The bias check:** where your number would differ for OpenAI or xAI given the same facts, and why.

Keep it factual and compact. I'll compare your ratings against the evidence myself, and disagreements are the useful part.
