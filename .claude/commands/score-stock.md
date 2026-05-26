---
description: Score a new stock and add it to the watchlist
---

Score ticker $ARGUMENTS for the AI Supply Chain Research project. Refer to CLAUDE.md at the project root for all conventions, data source priorities, and operating rules.

## Steps

0. **MANDATORY FIRST: Invoke /refresh-context $ARGUMENTS.** Claude's training data is stale; this command forces a fresh-research pass (WebSearch + WebFetch + EDGAR) so the scoring reflects current reality, not 12-month-old mental models. See `.claude/commands/refresh-context.md`. Output is `per-stock/$ARGUMENTS/context-{date}.md` — read it before proceeding. **Do not skip.** Stale data → wrong scores → missed buy opportunities. (Established 2026-05-18 after AMD layer session surfaced 3 D-dimension miscalibrations from stale models.)

1. **Pull financial inputs.** Use yfinance for: forward P/E, EV/EBITDA, FCF yield %, P/S ratio, ROIC %, gross margin %, FCF margin %, net debt/EBITDA, 3-year revenue CAGR %, latest-quarter revenue YoY %, latest-quarter EPS YoY %.

2. **Fall back to SEC EDGAR** for any field yfinance can't provide. Look up CIK, query the companyfacts API for raw line items, compute the ratio manually.

3. **Identify the supply chain layer.** Match the company's business to a layer in `00-master/ai_supply_chain_research_map.md`. If it doesn't fit, flag this — the map may need updating.

4. **Add row to scoring spreadsheet.** Open `00-master/ai_supply_chain_scoring.xlsx`. In the Watchlist tab, append a new row:
   - Ticker, Company (legal name from EDGAR), Layer, Last Updated = today
   - All blue input cells = the pulled values
   - **Leave 1-5 subjective columns BLANK** (AI Rev %, Position, Moat, Capacity, Hypersc., EPS Rev, Rel Str, Insider, Cust Conc, Geo Risk, BS Risk, Reg Risk)

5. **Save the workbook.** Use the xlsx recalc script if available to verify zero formula errors.

## Report back

- The new row, with all field values
- Computed objective subscores (Value, Quality, Growth) — these populate automatically once inputs are in
- Any data gaps and why (e.g., "FCF yield N/A — TTM FCF negative")
- Any anomaly worth knowing before I fill in the subjective ratings (e.g., "Just IPO'd 8 months ago, no 3-year history" or "Recent restatement of FY-1 financials")

## Do not

- Modify any existing rows
- Fill in subjective 1-5 ratings as part of this data-refresh workflow — those happen in a separate rating session (see `/templates/rating-rubric-and-workflow.md`). If you have a strong view on what a rating should be based on the data you pulled, propose it in your report-back, but don't write it to the spreadsheet.
- Skip the citation discipline — if a number came from yfinance vs EDGAR, note which
