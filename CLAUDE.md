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
  CLAUDE.md                           # This file
```

## Data sources (in priority order)

1. **SEC EDGAR** (https://data.sec.gov, https://www.sec.gov/edgar) — primary source of truth for filings. Use User-Agent header `Dom Researcher dom@example.com` (replace with real email). Rate limit: 10 req/sec max, throttle with `time.sleep(0.1)`.
2. **yfinance Python library** — fundamentals, market data. Install if missing: `pip install yfinance`. Has occasional rate limits and incomplete data on small-caps.
3. **Company IR pages** — earnings calls, investor presentations. Fall back to motleyfool.com if IR doesn't publish transcripts.
4. **FRED** (https://fred.stlouisfed.org) — macro/rates/electricity data.
5. **EIA** (https://www.eia.gov) — energy and electricity data.
6. **13f.info** — pre-parsed 13F holdings.

**Do not use** paid sources (Bloomberg, FactSet, LSEG, FMP paid tier) — this project is free-tools-only.

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

**How to refresh:** Pull yfinance data and update the Watchlist row. For fast-ramp names where TTM averages understate the current business (e.g., 4 quarters spanning a margin ramp), note the MRQ values in the context briefing so the TTM limitation is visible.

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

**Current Layer 10 names affected:** PLTR, SNOW, NOW, CRM, DDOG, CRWD, MDB, PATH. When adding new Layer 10 names, use EV/FCF with these bands. The column header in the spreadsheet still says "EV/EBITDA" — for Layer 10 names, read it as EV/FCF.

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

## Common tools and libraries (pre-approved for installation)

```bash
pip install yfinance pandas openpyxl requests beautifulsoup4 lxml
```

For 13F XML parsing, use `lxml`. For HTML scraping (IR pages), use `beautifulsoup4`. For Excel, use `openpyxl` (NOT pandas to_excel — it strips formulas).

## Subagent patterns

When running batch tasks (e.g., score 10 new tickers), prefer parallel subagents over sequential. Each subagent handles one ticker end-to-end, writes its row to the spreadsheet, returns. The orchestrator merges results.

Exception: when scraping rate-limited sources (SEC EDGAR, yfinance backend), serialize to avoid throttling.

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
