# CLAUDE.md

This file is read by Claude Code on every session. It encodes the conventions, data sources, and rules for the AI Supply Chain Research project.

## Project purpose

A systematic, repeatable equity research process for AI infrastructure stocks. The Aschenbrenner "Situational Awareness" thesis is the macro view; this project executes the bottoms-up work to identify and track investable names across the supply chain.

The goal is **not** to chase ideas from 13F filings or social media. The goal is to do enough first-principles work to develop independent conviction.

## Folder structure (memorize this)

```
AI-Supply-Chain/
  00-master/
    ai_supply_chain_research_map.md   # Supply chain layer map, 100+ tickers
    ai_supply_chain_scoring.xlsx      # Scoring spreadsheet (Watchlist tab)
    portfolio.xlsx                    # Current positions + sizing
  01-power-generation/                # Per-layer thematic notes
  02-grid-equipment/
  03-data-centers/
  04-semi-equipment/
  05-fabs/
  06-silicon/
  07-optical-networking/
  08-servers/
  09-cloud/
  10-applications/
  per-stock/
    {TICKER}/
      thesis.md
      financials.xlsx
      filings/                        # 10-K, 10-Q, 8-K PDFs
      transcripts/                    # Earnings call transcripts
      catalysts-watchlist.md
      news-log.md
  tracking/
    weekly-news-scan-{YYYY-MM-DD}.md
    quarterly-rescore-{YYYY}-Q{N}.md
    13f-tracking.xlsx
    hyperscaler-capex.xlsx
  templates/
    per-stock-template.md
    quarterly-update-checklist.md
  site/                               # Friend-facing static site (see §Portfolio site)
  tests/                              # pytest suite (site exporter)
  CLAUDE.md                           # This file
```

## Data sources (in priority order)

1. **SEC EDGAR** (https://data.sec.gov, https://www.sec.gov/edgar) — primary source of truth for filings. Use User-Agent header `Dom Researcher dom@example.com` (replace with real email). Rate limit: 10 req/sec max, throttle with `time.sleep(0.1)`.
2. **yfinance Python library** — fundamentals, market data. Install if missing: `pip install yfinance`. Has occasional rate limits and incomplete data on small-caps. **Known trap (fixed 2026-06-12):** `info.freeCashflow` is Yahoo's *levered* FCF estimate and does not reconcile to the cash-flow statements (printed NVDA's 47% TTM FCF margin as 18%). All FCF inputs must use statement-based TTM OCF − |capex| via `batch_score.statement_fcf()`; the info field is fallback-only and must be flagged.
3. **Company IR pages** — earnings calls, investor presentations. Fall back to motleyfool.com if IR doesn't publish transcripts.
4. **FRED** (https://fred.stlouisfed.org) — macro/rates/electricity data.
5. **EIA** (https://www.eia.gov) — energy and electricity data.
6. **13f.info** — pre-parsed 13F holdings.

**Do not use** paid sources (Bloomberg, FactSet, LSEG, FMP paid tier) — this project is free-tools-only.

**Remote/cloud sessions (egress allowlist):** sandboxed environments must allowlist
`data.sec.gov`, `www.sec.gov`, `efts.sec.gov`, `query1.finance.yahoo.com`,
`query2.finance.yahoo.com`, `fc.yahoo.com`, `guce.yahoo.com`, `consent.yahoo.com`
(or `*.sec.gov` + `*.yahoo.com`). Without these, the 8-K scan and all yfinance
refreshes fail — the 2026-06-12 scan had to be re-run locally for this reason.
If blocked, complete what runs locally, flag the gap, and do not fabricate data.

## Scoring system reference

The scoring spreadsheet at `00-master/ai_supply_chain_scoring.xlsx` has 5 sheets:
- README
- Weights (category weights, sum to 100%)
- Methodology (threshold bands for converting raw metrics to 0-100 scores)
- Watchlist (the working sheet — one row per stock)
- Rating Audit (append-only log of all subjective rating decisions)

Six categories, current weights (reweighted 2026-05-25):
- Value 20%, Quality 20%, Growth 15%, AI Thesis 20%, Momentum 10%, Risk 15%

Value category includes 5 metrics: Forward P/E, EV/EBITDA, FCF Yield %, P/S, and PEG Ratio (Fwd P/E ÷ EPS Growth %). PEG was added 2026-05-25 to penalize stocks that are expensive relative to their growth rate.

Momentum category includes 4 metrics: three subjective 1-5 ratings (EPS Revisions, Relative Strength, Insider Activity) plus one objective metric, "50DMA %" — the share of the last 120 trading days with close > 50-day SMA, added 2026-06-09 (see rule 11).

Previous weights (pre-2026-05-25): Value 15%, Quality 20%, Growth 15%, AI Thesis 30%, Momentum 10%, Risk 10%. Reweight rationale: within an AI-only watchlist, AI Thesis at 30% was circular (every name was selected for AI exposure). Higher Value and Risk weights better serve capital allocation decisions vs. pure triage.

Each stock gets a Total Score (0-100) and Tier:
- 85-100 → ✓✓✓ (top tier)
- 70-84 → ✓✓ (strong)
- 55-69 → ✓ (average)
- 40-54 → ? (below average)
- 0-39 → ✗ (avoid)

## Subjective rating workflow

For any subjective rating, follow the rubric at `/templates/rating-rubric-and-workflow.md`. The collaboration model:

1. Claude proposes ratings with rationale + source citation + confidence level (Low/Medium/High)
2. Dom accepts, overrides, or flags for discussion
3. Divergences get discussed — those are the high-value part
4. Final ratings + rationale get appended to the Rating Audit Log sheet of the scoring spreadsheet

**Key principles surfaced during BE rating session (2026-05-17):**
- Apply the same standards to insiders as we apply to our own portfolio decisions. Post-rally diversification is rational behavior, not bearish signal.
- Empirical research shows insider BUYING predicts returns reliably; insider SELLING is ambiguous. Weight these asymmetrically.
- The audit trail (rationale + source + date) is non-negotiable. Without it, future-Dom can't debug past-Dom's judgment.
- Disagreement between Claude and Dom is the productive part. If Claude is just rubber-stamping Dom's intuitions (or vice versa), the process isn't catching anything.

## Operating rules (must follow)

### 1. Cite every numeric claim
Every revenue, margin, capex, or growth number must reference a specific source: filing type + date + section, or URL. Example: "Gross margin 38% (10-Q Q1 2026, p.12)" — not "Gross margin 38%."

### 2. Follow the subjective rating process
When scoring or rescoring stocks, make sure to follow the outlined process above for us to collaborate on the subjective columns.

### 3. Flag, don't assume
If data is missing, ambiguous, or contradicts another source, flag it explicitly in your output. Don't paper over gaps. Acceptable: "Could not find FCF yield because TTM cash flow data is incomplete on yfinance for this ticker." Unacceptable: silently using a guess.

### 4. Prefer formulas over hardcoded values in Excel
When updating any .xlsx file, calculated cells must be Excel formulas, not Python-computed values pasted in. This keeps the workbook live when source data changes.

### 5. Don't recommend trades
This project produces research, not trade recommendations. You can identify high-scoring opportunities, flag thesis changes, and surface contradictions. The decision to buy, hold, or sell is mine.

### 6. Update the news log, not just the thesis
For every material development on a ticker, append to `/per-stock/{TICKER}/news-log.md` with date + source + 1-line summary. The thesis only changes when the development materially affects an existing section.

### 7. Keep transcripts as markdown, not PDF
Earnings call transcripts go in `/per-stock/{TICKER}/transcripts/Q{N}-{YYYY}.md` as markdown. Easier to grep, easier to diff against prior quarter.

### 8. Don't drift the methodology
The scoring band thresholds in `ai_supply_chain_scoring.xlsx` Methodology tab are calibrated. Don't modify them as part of a routine task — propose changes explicitly and require my approval.

### 9. Earnings-triggered objective refresh (added 2026-05-26)

**Context:** During the MU review, stale objective inputs (gross margin, FCF margin, ROIC) caused a 14-point scoring error and a full tier miss (#23 → #4). The data was 2 months stale after a quarter where fundamentals shifted dramatically. Quarterly rescores are too infrequent for high-momentum names.

**Rule:** When any watchlist name reports quarterly earnings, refresh its objective inputs within one week. Priority order:

1. **Immediate (within 1 session):** Any name that beats/misses revenue or EPS estimates by >15%, OR where gross margin moves >500bps sequentially. These are the names where staleness costs the most.
2. **Within 1 week:** All other watchlist names that reported earnings.
3. **Exception:** If `/earnings-update` is run on the name, the objective refresh is already included — don't duplicate.

**Primary enforcement:** The `/weekly-scan` skill (Step 6) now includes earnings-triggered refresh as a built-in step. Any 8-K with Item 2.02 (quarterly results) triggers an objective input refresh in the same pass. This is the expected catch-all — `/earnings-update` handles deep single-name processing, but the weekly scan ensures nothing slips through even if `/earnings-update` wasn't run.

**How to refresh:** Pull yfinance data and update the Watchlist row. For a scripted objective-only refresh of a set of names, use `/refresh-objective
<portfolio|all|TICKERS>` (dry-run first) — it refreshes every objective input,
guards the deliberate-blank conventions, and leaves subjective ratings untouched.
For fast-ramp names where TTM averages understate the current business (e.g., 4 quarters spanning a margin ramp), note the MRQ values in the context briefing so the TTM limitation is visible.

**TTM limitation (known issue):** yfinance provides TTM (trailing twelve months) data. For companies with rapidly improving fundamentals, TTM averages include lower quarters and systematically understate the current run-rate. This biases scores DOWN for high-momentum names — exactly the ones where staleness matters most. When TTM and MRQ diverge by >10 points on any quality metric, flag it in the per-stock context file. We may eventually want an MRQ-adjusted scoring option, but for now the TTM approach maintains cross-name comparability.

### 10. Layer 10 SaaS: EV/FCF replaces EV/EBITDA (added 2026-05-26)

**Context:** yfinance GAAP EBITDA for high-SBC SaaS names is near-zero or negative (SBC at 15-25% of revenue crushes GAAP operating income). This produced scores like EV/EBITDA = 2,184x for DDOG, dragging it down an entire tier on a garbage input. The metric provided zero differentiation across the entire Layer 10 cohort — all scored 5 (minimum).

**Rule:** For Layer 10 (Models, Software & Applications) names, the EV/EBITDA column in the Watchlist tab contains **EV/FCF** instead, scored on SaaS-calibrated bands:

| EV/FCF | Score |
|---|---|
| ≤20 | 100 |
| ≤30 | 90 |
| ≤40 | 75 |
| ≤55 | 60 |
| ≤75 | 45 |
| ≤100 | 30 |
| >100 | 15 |

**Why EV/FCF:** FCF is a real cash number (not adjusted by non-GAAP games), preserves the EV-based leverage signal that's the point of the metric, and yfinance provides the inputs. SBC dilution hits shareholders through share count, not through cash outflow, so FCF isn't distorted the way EBITDA is.

**Current Layer 10 names affected:** PLTR, SNOW, NOW, CRM, DDOG, CRWD, MDB, PATH, TEM. When adding new Layer 10 names, use EV/FCF with these bands. The column header in the spreadsheet still says "EV/EBITDA" — for Layer 10 names, read it as EV/FCF.

**Implementation note (2026-06-12):** the EV/FCF *values* were written on 2026-05-26 but the SaaS *bands* above were never implemented — Excel formulas and `recalc_watchlist.py` kept applying standard EV/EBITDA bands to EV/FCF values until the 2026-06-12 fix (`rebuild_watchlist_formulas.py`). Same fix also repaired formula row-reference drift on 106 rows caused by openpyxl row deletions (openpyxl `delete_rows` does NOT rewrite formula references — **always run `python3 scripts/rebuild_watchlist_formulas.py` after any structural row change to the Watchlist**).

### 11. Momentum: objective 50DMA % metric (added 2026-06-09)

**Context:** Momentum was the only category with zero objective inputs — three subjective 1-5 ratings with no defined measurement procedure. External feedback (reviewed 2026-06-09) suggested several momentum additions; this one was adopted because it objectifies trend consistency cheaply from free data. (Declined from the same review: P/B, operating margin, volume confirmation, institutional ownership delta, analyst PT upgrades — see Rating Audit 2026-06-09 entry.)

**Metric:** "50DMA %" (Watchlist col AC) = % of the last 120 trading days where close > 50-day SMA, from yfinance price history. Distinguishes consistent uptrends from one-gap bounces. Bands: ≥85→100, ≥70→90, ≥55→75, ≥40→60, ≥25→40, <25→20. Momentum Score averages the three subjective ratings (×20) with this banded score.

**How to refresh:** `python3 scripts/momentum_50dma.py` (all names) or with ticker args for a subset. Refresh alongside any objective input refresh (rule 9) and at quarterly rescores. Names with <60 days of price history are flagged and left blank (the Momentum average just skips them).

**Companion change (same review):** FCF conversion (TTM FCF ÷ TTM net income) was added to `/refresh-context` as a qualitative red-flag check — NOT a scored metric, because it misfires on high-SBC names (flatters them) and heavy-capex names (penalizes investment). See refresh-context.md Step 2b for the conditional flag definition.

### 12. Subjective-rating refresh discipline + thesis gate (added 2026-06-10)

**Context:** The 2026-06-10 Layer 1 directness re-rating found that names carried high AI-Thesis ratings with `thesis.md` files that were the untouched template — ratings assigned by sub-layer pattern-match, never backed by per-name research (123 of 136 rated names had no populated thesis). This is the same failure that hit Layer 2 in May (see [[feedback_per_name_research]]). Objective inputs have an earnings-triggered refresh (rule 9); subjective ratings had **no trigger and no gate**, so they were set once in a batch and frozen. Root cause: a ranking system is self-consistent but not self-correcting — uniform bias across a cohort cancels out of the sort order and is invisible to relative ranking. Only an absolute standard, applied from outside, exposes it.

**The gate (hard):** A watchlist name may not be trusted to carry subjective AI/Momentum/Risk ratings unless it is research-backed — defined as a populated `thesis.md` **or** a `context-{YYYY-MM-DD}.md` briefing within the staleness window. Enforced by `scripts/audit_rating_integrity.py`, which exits nonzero on any gate violation. Run it before trusting a scoring pass; `/score-stock` and batch scoring should treat a gate violation as "research first, then rate."

**Refresh triggers (subjective ratings):**
1. **On earnings** — when a rated name reports, re-examine its D-dimensions in the same pass as the rule-9 objective refresh. A beat/miss or a new customer/PPA/contract often moves D1/D2/D5.
2. **Rolling staleness** — no rated name should go >90 days without a research-backed review. `audit_rating_integrity.py` flags STALE names; the scheduled routine (below) feeds the stalest into `/refresh-context` on rotation.
3. **Absolute-lens stress test** — periodically test a *whole layer* against one external standard (e.g. the "directness" lens that drove the Layer 1 re-rate). This is the only thing that catches uniform bias, so it must be done deliberately, not left to relative ranking.

**Enforcement (so the refreshes actually happen — not just the logic):**
- **Weekly:** `/weekly-scan` Step 8 runs the integrity audit and surfaces gate + stale names.
- **Biweekly (scheduled):** a cloud routine runs `audit_rating_integrity.py --stalest` and then `/refresh-context` on the stalest rated names by layer rotation, writing fresh briefings for a collaborative rating session. The routine does the research legwork; rating changes stay in the human loop.
- **Quarterly:** `/rescore-quarterly` does a full pass and should fail loudly on any gate violation.

### 13. Layer 9 capacity cohort: EV/MW replaces EV/EBITDA (added 2026-06-12, approved by Dom)

**Context:** The SALP Q1 2026 13F stress test showed the entire bitcoin-miner-pivot/neocloud cohort scoring 7.5–21 on Value with zero differentiation — all five Value metrics are income-statement-derived, but this cohort's value object is secured power capacity (gigawatts of interconnection + powered land) against current GAAP losses. Same floor-pinning failure that drove rule 10. The cohort cells held garbage anyway (negative EV/EBITDA like −1,430 for NBIS).

**Rule:** For the Layer 9 capacity cohort — sub-layers containing "Bitcoin" or "Neocloud" (hyperscalers excluded) — the EV/EBITDA column contains **EV per secured gross MW** ($M/MW), scored: ≤2→100, ≤4→90, ≤6→75, ≤9→60, ≤12→45, ≤18→30, >18→15. Band anchor: ~$9–10M per gross MW AI-datacenter replacement cost (facility + power, excl. IT gear) sits at the 45/60 boundary — paying replacement scores mid, sub-half-replacement scores high.

**MW data:** `00-master/capacity-mw.json` — secured gross MW (energized + committed/under-construction; speculative pipeline excluded) with per-name basis, as-of date, source, and confidence. Critical-IT-load-only disclosures convert ×1.25 (flagged). Refresh alongside rule-9 earnings refreshes and quarterly rescores — a stale MW denominator is as bad as a stale margin. Disclosure bases vary by company (gross vs IT load, secured definitions); the json's `basis` field records each interpretation — read it before trusting cross-name comparisons.

**Division of labor (deliberate):** EV/MW measures *price per unit of capacity*; whether that capacity ever converts to AI revenue is the AI Thesis category's job (e.g., CLSK scores well on EV/MW but its 1.8 GW has zero AI/HPC contracts — its low AI Thesis score carries that information). Don't fold conversion probability into the Value metric.

**Current cohort:** CRWV, NBIS, APLD, IREN, CORZ, CIFR, CLSK, BTDR, HUT, KEEL, RIOT, WULF.

### 14. Expectations red-flag in /refresh-context (added 2026-06-12, approved by Dom)

The rubric has no "what's priced in" input — Value bands are absolute and Momentum rewards relative strength, so Total Score peaks where consensus is most crowded (5 of SALP's 6 biggest Q1 2026 put targets were our top-6 names). Counterweight: `/refresh-context` Step 2c runs `python3 scripts/expectations_flag.py {TICKER}` — flags P/S ≥90th percentile of own 3-year range combined with revenue growth below its 3-year median (peak multiple, decelerating growth). **Qualitative red flag for the context briefing, NOT a scored metric** — see refresh-context.md Step 2c for interpretation discipline. Script self-skips honestly on foreign filers and unmapped XBRL revenue tags.

### 15. EPS YoY: blank when one-time-dominated (added 2026-06-12, approved by Dom)

GAAP EPS YoY scores garbage when the change is dominated by disclosed non-operating items (divestiture gains, fair-value swings, large tax one-offs) — GEV's +1,768% from the ~$4.5B Prolec gain would have scored 100 on a divestiture. **Rule:** blank the EPS YoY input when a briefing/filing documents that the YoY change is non-operating-dominated; Growth then averages the revenue metrics. Applied on documented per-name evidence (cite the item in the Rating Audit), NOT mechanically on magnitude — a big operational number off a small base (e.g., SEI +303%) stays. Same garbage-input principle as the negative-EBITDA blanking convention and rules 10/13.

### 16. Risk: R5 Disruption Risk dimension (added 2026-06-17, approved by Dom)

**Context:** R1–R4 (customer concentration, geography, balance sheet, regulatory) measure whether earnings are *safe now*, not whether the *revenue model survives*. This let beaten-down application-SaaS names (down 40–67% on genuine agentic-AI disruption fears) still score ✓✓ — Value rises as price falls (20% weight) while the disruption thesis had nowhere to land (moat is only 1 of 5 AI-Thesis dims → ≤1.6pt swing). Surfaced in the 2026-06-17 QQQ-coverage batch (WDAY): a value-quality screen rewards a falling quality name *because* it is falling. R5 gives terminal-value/business-model durability a home.

**Rule:** The Risk category now averages **five** dimensions — R1–R4 plus **R5 Disruption Risk** (Watchlist col **AL / 38**, appended after Tier so Risk Score/TOTAL/Tier indices don't shift). Risk weight unchanged at 15%. Inverted like R1–R4: **5 = most durable / lowest disruption risk.** Bands:
- **5** — no credible AI/structural disruption to the core revenue model in ~5yr (physical infra, power, fabs, semis equip, HDD, networking, cloud compute). **Default for all non-Layer-10 names.**
- **4** — durable; AI net-neutral/tailwind or threatens only a peripheral line (security software — AI expands attack surface; consumption-priced data/observability; AI-native beneficiaries).
- **3** — contested but a structural moat (file format, regulatory, data, ecosystem) resists core disruption.
- **2** — core pricing model/workflow is a direct agentic-AI target; durability in question, no active erosion yet (or a durable sub-segment offsets).
- **1** — AI-native tools / the model layer can directly produce the core output or fully automate the workflow, **and** active erosion is visible (price concession, funnel/share loss).

**Scope:** Only Layer 10 (Models, Software & Applications) carries sub-5 R5; everything else defaults to 5. Refresh R5 alongside subjective-rating reviews (rule 12), applying the absolute-lens stress test across the *whole* Layer-10 cohort (not relative ranking). **Deliberate asymmetry:** because the default is the max (5), R5 mostly *rewards durability* (lifts the non-exposed field slightly) and penalizes only the genuinely-exposed cohort.

**Implementation:** R5 at col 38; `rebuild_watchlist_formulas.py` RISK template averages `AE:AH + AL`; `recalc_watchlist.py` `risk_inputs` includes col 38. **Run `rebuild_watchlist_formulas.py` after any structural row change still applies** (rule 10 note). The recalc-vs-Excel blank-handling divergence (recalc sums available category parts without renormalizing; Excel blanks TOTAL if any category is empty) is unchanged.

### 17. Forecast calibration loop (added 2026-06-26, approved by Dom)

**Context:** Subjective ratings (AI-Thesis, Momentum, Risk R1–R5) are implicit predictions, assigned and frozen but never graded against what happened. A ranking system can't see its own uniform bias (rule 12); calibration is the external absolute standard that can.

**Rule:** Selected ratings are logged as falsifiable, dated forecasts with a frozen, mechanical resolution rule in `tracking/forecasts.jsonl` — a **single append-only snapshot log** (creation appends an `open` snapshot; resolution appends a new snapshot of the same `id`; lines are never edited; the current state of an `id` is its last snapshot). Forecasts are resolved on schedule and graded with Brier score, the Murphy REL/RES/UNC decomposition, Brier Skill Score vs. the base rate, and a reliability diagram.

**Guarantees (do not weaken — treat like the site privacy gate):** `created_date`, `ticker`, `layer`, `dimension`, `rating_value`, `template`, `probability`, `resolution_date`, and `resolution_rule` are immutable (a changed mind is a *new* forecast); `created_date` is set to today at log time so backdating is impossible; the resolver consumes only post-`created_date` data (no look-ahead); ambiguous resolutions go to `needs_review`, never guessed (rule 3); every resolution carries a cited evidence string (rule 1).

**Boundary:** calibration is diagnostic — it does **not** feed back into the Total Score or category weights, adds **no** Watchlist columns, uses **no** paid data, and is **not** surfaced on the friend-facing site. A dimension proving to be noise is a human decision ("stop trusting it / investigate"), never an automatic reweight (the overfitting trap flagged in prior reviews).

**Cadence & scripts:** `/weekly-scan` runs `scripts/resolve_forecasts.py` (resolve due); `/rescore-quarterly` runs `scripts/calibration_report.py` (regenerate `tracking/calibration-report.md`). Seed/log forecasts with `scripts/log_forecast.py`. Core logic: `forecast_store.py` (the log), `forecast_cohorts.py` (frozen peer basket), `forecast_resolvers.py` (template registry), `forecast_metrics.py` (Brier/Murphy/BSS).

**Rollout:** Phase 1 = `REL_STRENGTH_1Q` on portfolio names (frozen layer-cohort EW basket; SMH fallback for thin layers). Phase 2 adds `EARNINGS_REACTION` + full watchlist + rating-time forecasts. Phase 3 adds the fundamental templates. Switch rating→probability defaults from the §4 priors to empirically-learned per-bucket hit rates once each dimension has ~30 resolved forecasts.

### 18. Targets sheet has one writer: refresh_targets.py (added 2026-06-29)

`00-master/portfolio.xlsx` `Targets` is written ONLY by `scripts/refresh_targets.py`.
Never hand-edit scores/tiers into it — that bypass left MU showing ✓✓✓ at a stale
✓✓-band weight (a ✓✓✓ name below a ✓✓ name) because weights and the model never
moved. After any rescore that could change a held name's tier, run
`python3 scripts/refresh_targets.py` (it re-weights + logs a model event iff
membership OR a held tier changed; within-tier drift freezes the snapshot, no churn).
`--resize` forces a re-weight. The score-monotonicity gate
(`tests/test_portfolio_sizing.py::test_targets_weights_monotonic`) fails the build on
any inversion. See spec 2026-06-29-tier-crossing-rebalance-design.md.

### 19. Foreign filers: convert to a common currency, never mix (added 2026-07-02, approved by Dom)

**Context:** A foreign company trading as a US ADR (price in USD) but reporting
financials in a local currency (TSM/UMC in TWD) produced garbage on every
market-cap-based ratio — P/S, EV/EBITDA, FCF-yield divide a USD numerator by a
local-currency denominator, off by the FX rate. The old convention just *blanked*
them, which hid how expensive names like TSM were (fixing it dropped TSM ✓✓✓→✓✓).
yfinance's ADR `enterpriseValue` is itself corrupt, so FX-converting the ADR fields
is unreliable.

**Rule:** Whenever a name's price currency differs from its financial-reporting
currency (`info['currency'] != info['financialCurrency']`), put numerator and
denominator in the **same** currency before computing P/S, EV/EBITDA, FCF-yield.
`scripts/adr_currency.py` does this inside `compute_inputs`:
- **Preferred (mapped US ADRs):** take the ratios from the company's LOCAL listing,
  where trading == reporting currency and yfinance's ratios are clean (US-ADR
  market caps are corrupt, so the local listing is more accurate). Map = `ADR_LOCAL`
  (TSM→2330.TW, UMC→2303.TW); extend it for new US ADRs.
- **General (any other foreign listing):** convert the market cap into the financial
  currency by exchange rate (`fx_rate`, via yfinance `{from}{to}=X`), compute
  EV = market cap + debt − cash (NOT the corrupt yfinance EV), and recompute the
  three ratios (`ratios_via_fx`). No per-name mapping — works for foreign primary
  listings (e.g. SMIC 0981.HK, HKD-trade / USD-report).
- Detection is **`trading != financial`**, NOT "financial != USD" (which wrongly
  blanks a clean same-currency foreign name like Vanguard 5347.TWO). Blank only when
  conversion is impossible (no FX rate). Skips Layer-10/9 (col F is EV/FCF or EV/MW).

Ratios are dimensionless once currency-consistent, so they compare apples-to-apples
across the whole watchlist regardless of reporting currency. Gross/FCF margins,
ND/EBITDA, growth %s and forward P/E are already currency-neutral and untouched.
Foreign filers still lack SEC Form-4 (M3 = flagged default) and `expectations_flag.py`
self-skips (no us-gaap XBRL). Refresh with `/refresh-objective` after adding to `ADR_LOCAL`.

### 20. P1 cohort-relative scoring is LIVE (added 2026-07-02, approved by Dom)

The six style-biased metrics — **EV/EBITDA, FCF-yield, P/S** (Value) and **ROIC,
gross margin, FCF margin** (Quality) — are scored as a **percentile rank within
the name's top-level-layer cohort** (§5-2 hybrid), NOT against absolute bands. A
cohort with <8 non-null values for a metric falls back to that metric's absolute
band (min-cohort-size guard, `cohort_percentile.cohort_metric_scores`). Col F
(EV/*) stays absolute for Layer 9 (mixed EV/EBITDA + EV/MW) and percentiles EV/FCF
for Layer 10. Everything else — ND/EBITDA, Fwd P/E, PEG, Growth, and all
subjective dims — is unchanged (absolute / subjective).

**Why:** absolute margin/ROIC bands measured "has an asset-light business model,"
not within-peer merit — software/silicon auto-maxed them (silicon+software vs
capital-heavy mean-Quality gap was **+28**; now **+6**). Before/after:
`docs/superpowers/plans/2026-07-02-p1-before-after-report.md`.

**Engine:** `recalc_watchlist.recalc(mode='percentile')` is the LIVE default and
the single source of truth for every consumer (`export_site_data`,
`refresh_targets`). `mode='absolute'` reproduces the pre-P1 scores. Tier bands
(85/70/55/40) and portfolio entry/exit (74.5/73.0) were reviewed and **held
unchanged** — the overall score scale barely compressed.

**Sheet:** the cohort-relative Value Score (col J) and Quality Score (col O) can't
be per-row Excel formulas, so they are **recalc-maintained VALUES** written by
`python3 scripts/recalc_watchlist.py --sync` (TOTAL/Tier stay formulas that
reference J/O). **After `rebuild_watchlist_formulas.py` (which restores absolute
formulas in J/O) OR any objective-input refresh, re-run `--sync`.** Deliberate
rule-4 exception for cohort-relative scoring (same garbage-input-family reasoning
as rules 10/13).

### 21. P2 reverse-DCF mispricing metric in Value (added 2026-07-02, approved by Dom)

Value now averages a **6th sub-metric** (§5-3): a reverse-DCF mispricing score
targeting finding F1 (reward *mispricing*, not just *quality*). For each name,
implied FCF growth is solved from its **EV/FCF** multiple (a fixed 10% WACC / 3%
terminal / 10-yr multi-stage DCF); the score is the gap between a grounded growth
estimate (**revenue 3-yr CAGR**) and that implied growth — a bigger positive gap
(grounded > implied) = cheaper-vs-expectations = higher score
(`reverse_dcf.reverse_dcf_score`). Folded into Value (no reweight), so it dodges
the P3 IC-gate.

**Data:** EV/FCF per name lives in `00-master/reverse-dcf.json`, refreshed by
`scripts/refresh_reverse_dcf.py` — currency-consistent per rule 19 (mapped ADRs
use the local listing, other foreign filers FX-convert; blank on
non-positive/unavailable FCF). `recalc` reads the json + the sheet's Rev-3y-CAGR;
a missing json makes the term drop out cleanly (Value = the five prior metrics).
**Refresh alongside objective refreshes (rule 9), then re-run `--sync`.**

**Effect:** 1 of 6 Value metrics ≈ 3.3% of TOTAL, so swings are small by design
(±3 pts). Rewards fast-growers whose multiple is justified by growth; penalizes
names whose multiple implies more growth than their recent revenue trend.
**Known limitation:** revenue-3yr-CAGR is a noisy grounded-growth proxy for
commodity/cyclical names (nat-gas E&P AR/RRC get dinged on a depressed revenue
trend) — a candidate refinement, documented not hidden.

### 22. Subjective floor removed: AI Thesis / Risk use (mean−1)×25 (added 2026-07-02, approved by Dom)

**P6 (finding F8).** AI Thesis and Risk map their 1–5 ratings to a subscore via
**(mean − 1) × 25** (1→0, 2→25, 3→50, 4→75, 5→100), NOT the old mean × 20 (which
floored at 20). A genuinely weak dimension can now drag the subscore to 0 rather
than banking 20/100 for free ("zero AI exposure still banked 20% credit on 20% of
the score"). Scoped to AI Thesis + Risk; **Momentum keeps rating × 20** (it blends
with the objective 50DMA band, so it isn't floored the same way). Lives in
`recalc_watchlist._assemble` and the Excel AI/Risk Score formulas
(`rebuild_watchlist_formulas.py`).

### 23. Collinear inputs (P4) + D5 dual-framework (P5): measured & disclosed (added 2026-07-02, approved by Dom)

**P4 — accepted double-counts (finding F4).** The flagged overlaps were measured
across the Watchlist (Pearson): **R3 Balance-Sheet-Risk ↔ Quality ND/EBITDA
+0.77**; **D2 Supply-Chain-Position ↔ D3 Moat +0.73**; **D5 Hyperscaler-Exposure
↔ D1 AI-Revenue-% +0.62** (vs ~+0.49 for a normal within-category pair).
Decision: **keep + disclose** (§5-5 option b) — each input adds a distinct angle
(R3 = holistic maturities/dilution vs the raw ratio; Position = pricing-power
bottleneck vs Moat = durability), so removing loses information; but the additive
sum DOES over-weight the shared signal, so treat a high-scoring "dominant crowded
AI winner" cluster with skepticism. **Future option if reducing the double-count
is wanted:** re-scope R3 to exclude leverage (already in ND/EBITDA), keeping only
maturities / dilution / going-concern — a rubric change + re-rate, not done here.

**P5 — D5 dual-framework (finding F9): RESOLVED as a reframe, normalization
rejected on evidence (2026-07-02).** D5 = supplier hyperscaler-revenue exposure
(Layers 1–8) OR buyer AI-capex commitment (Layer 9). F9 flagged two constructs in
one cross-layer-ranked column; and review #5 correctly killed an earlier false
claim that P1 cohorts "separate" them (they don't — D5 is subjective, not
peer-ranked, and enters the cross-layer TOTAL as an absolute value). **Examined:**
Layer-9 mean D5 = 3.7 vs supplier 3.3, half of L9 rates 5 — but those are the
mega-hyperscalers (META/MSFT/GOOGL/AMZN) genuinely at $30–80B/yr AI capex, so the
higher buyer mean is REAL, not a calibration error. **Tested the doc's proposed
fix** (percentile-within-framework normalization): it would dock those four ~1
TOTAL pt each for being correctly-common in their layer — under-crediting the real
AI leaders, the opposite of an improvement. **Decision: do NOT normalize.** Instead
D5 is reframed (rubric D5 section) as ONE dimension — *strength of AI-buildout tie*
— on a parallel 5-max-for-role scale, so a supplier's 5 and a hyperscaler's 5 are
deliberately-equivalent contributions (comparable by construction) even though the
raw evidence (">30% revenue" vs "$30B capex") must not be read literally against
each other. This closes the "two constructs, one column" concern at its root
without suppressing a real signal.

### 24. Cohort membership is governed (added 2026-07-02, review #3)

P1 percentile scores are ranks WITHIN a top-level-layer cohort, so cohort edits are
**score-determining** — adding a weak peer inflates the strong names' percentiles
with zero change to the companies. Governance:
- **Committed map:** `00-master/cohort-membership.md` (generated by
  `scripts/cohort_membership.py --update`) lists each cohort's members + per-metric
  eligibility (`pct` when the cohort has ≥8 non-null values, else `abs` fallback;
  Layer-09 col-F always `abs`). The Watchlist `Layer` column is the source of truth;
  this file is its **reviewable, diff-able projection**.
- **Drift gate:** `tests/test_cohort_membership.py` fails if the committed map ≠ the
  live Watchlist cohorts — you cannot change cohort membership/eligibility without
  the map (and its diff) moving with it.
- **On ANY cohort change** (add/remove a name, edit a Layer, or a metric crossing
  the n=8 line): run `python3 scripts/cohort_membership.py --impact <ticker>` to see
  how it shifts every incumbent's percentile scores (peer-inflation, quantified),
  then `--update`, and commit the new map in the SAME change — its git diff is the
  logged before/after.
- **Min-cohort-size guard** (rule 20): <8 non-null for a metric → that (cohort,
  metric) falls back to the absolute band (not merge-to-super-cohort). The map's
  `pct/abs` flags show this per cohort.

## Common tools and libraries (pre-approved for installation)

```bash
pip install yfinance pandas openpyxl requests beautifulsoup4 lxml
```

For 13F XML parsing, use `lxml`. For HTML scraping (IR pages), use `beautifulsoup4`. For Excel, use `openpyxl` (NOT pandas to_excel — it strips formulas).

## Subagent patterns

When running batch tasks (e.g., score 10 new tickers), prefer parallel subagents over sequential. Each subagent handles one ticker end-to-end, writes its row to the spreadsheet, returns. The orchestrator merges results.

Exception: when scraping rate-limited sources (SEC EDGAR, yfinance backend), serialize to avoid throttling.

## Portfolio site (added 2026-06-10)

A password-gated static site for close friends: `site/` on Cloudflare Pages,
deployed by `.github/workflows/deploy-site.yml` on push to `main`.

- **Privacy boundary:** `scripts/export_site_data.py` is the ONLY path from
  repo data to `site/data/`. All dollars are scaled to a $10,000 notional
  base; real capital, share counts, and cost basis are excluded by design.
  `tests/test_export_site_data.py::test_privacy_no_real_dollars_anywhere` is
  the regression gate — never weaken it.
- **Performance series:** `tracking/performance-series.json` is written by
  `track_performance.py`. `deploy-site.yml` needs no network/yfinance;
  `daily-refresh.yml` (weekday crons 21:05 + 22:35 + 00:35 UTC, targeting ~5pm
  ET right after the 4pm ET close) rebuilds it
  with `--series-only`, commits if changed (holidays self-skip), and redeploys
  inline — dashboard/performance pages stay daily-fresh. Three crons because
  GitHub's `schedule` trigger is best-effort and drops runs (it dropped
  2026-06-15 entirely); the commit-if-changed guard makes the backstops
  idempotent. The weekly Cowork routine still owns the narrative
  `performance-log.md`.
- **Scan links:** `tracking/notion-scan-links.json` maps scan dates to Notion
  URLs; the Cowork weekly routine appends to it.
- The spec lives at `docs/superpowers/specs/2026-06-10-portfolio-site-design.md`.

## What I'm NOT trying to optimize for

- Speed of single ticker analysis (10 minutes per name is fine)
- Comprehensive coverage of all stocks ever (~150 names max in watchlist)
- Real-time prices (15-min delay is fine)
- Beating the market on a daily/weekly basis

What I AM trying to optimize for:
- Independent conviction on every position
- Catching thesis breaks before consensus
- Identifying upstream/under-followed names
- A repeatable process I can run for years

## Output style

- Tables and bullet lists when summarizing data
- Prose when explaining reasoning
- One-line citations inline, not footnotes
- No filler ("As an AI..." etc.)
- Markdown headings for any output longer than 3 paragraphs

## When in doubt

- **Read the actual 10-K** rather than relying on yfinance summaries.
- **Ask before destructive operations.** Deleting files, overwriting whole sections of thesis.md, rebuilding spreadsheets — confirm first.
- **Default to skepticism** about consensus narratives. The thesis is that most investors are pricing this wrong; act accordingly.
