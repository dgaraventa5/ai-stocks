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
