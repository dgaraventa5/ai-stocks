---
description: Update hyperscaler capex tracker after a hyperscaler earnings release
---

Update `/tracking/hyperscaler-capex.xlsx` with the latest capex data from $ARGUMENTS.

$ARGUMENTS must be one of: MSFT, GOOGL, AMZN, META, ORCL.

## Steps

1. **Actuals.** Run `python3 scripts/hyperscaler_capex.py --write`. It reads every company's cash-flow capex line from SEC filings, splits the year-to-date figures into single quarters, and writes them to the "Capex by quarter" sheet in USD millions, with each value cited in the "Sources" sheet (a computed quarter, such as Q4 = full year − 9 months, names both filings). Lines used:
   - MSFT: "Additions to property and equipment"
   - GOOGL, META: "Purchases of property and equipment"
   - AMZN: "Purchases of property and equipment, including internal-use software and website development"
   - ORCL: "Capital expenditures"

   A quarter sits under the calendar quarter it ends in (Oracle's August quarter is Q3). If the 10-Q is not filed yet, the press-release figure goes in the report, not the sheet; the next run picks up the filing. Exit 1 means a company could not be read, or is two or more quarters behind the others (most likely a changed XBRL tag): say so, never fill it by hand.

2. **Guidance.** Read the earnings call transcript for the quarter. Search for "capital expenditure", "capex" or "capacity" and pull the forward guide (next quarter, full year, and any longer-term guide).

3. **Record it** in the "Guidance & commentary" sheet: one row per data point with date, ticker, source (link or filing), the quote or figure, and its implication. Note the change against the prior guide.

4. **Combined trend.** The script prints the combined total for the two latest quarters all five have filed, with the change on a year earlier (the sheet's TOTAL and YoY % rows are formulas that compute the same once opened). Say whether combined spending is accelerating, steady or decelerating.

5. **Flag** any guide revision over 5% in either direction. These matter for everyone in the supply chain.

## Report

- $ARGUMENTS: latest quarter's capex, change on a year earlier, and the new guide
- Combined hyperscaler trend after this update
- Anything thesis-relevant for the supply chain watchlist (e.g., "MSFT raised FY capex guide by 8% — bullish for VRT, GEV, BE")
