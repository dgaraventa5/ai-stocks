---
description: Update hyperscaler capex tracker after a hyperscaler earnings release
---

Update `/tracking/hyperscaler-capex.xlsx` with the latest capex data from $ARGUMENTS.

$ARGUMENTS must be one of: MSFT, GOOGL, AMZN, META, ORCL.

## Steps

1. **Pull the latest 10-Q** for $ARGUMENTS from SEC EDGAR.

2. **Extract capex** from the cash flow statement. The line item is typically:
   - MSFT: "Additions to property and equipment"
   - GOOGL: "Purchases of property and equipment"
   - AMZN: "Purchases of property and equipment, including internal-use software and website development, net"
   - META: "Purchases of property and equipment"
   - ORCL: "Capital expenditures"

3. **Find the earnings call transcript** for the corresponding quarter. Search for "capital expenditure," "capex," or "capacity" — pull forward capex guide (next quarter, full year). If the company has shifted from FY guide to longer-term guide (e.g., AMZN sometimes), capture both.

4. **Update the spreadsheet** for $ARGUMENTS row:
   - Latest quarterly capex actual
   - TTM capex (sum trailing 4 quarters)
   - YoY growth %
   - Forward guide (next quarter and/or full year)
   - Delta vs. prior guide
   - Date of update

5. **Recalculate combined metrics** in the summary section:
   - Combined hyperscaler TTM capex (sum across all 5)
   - Combined YoY %
   - Trend direction (accelerating / steady / decelerating)

6. **Flag** any guide revision >5% in either direction. These are thesis-relevant for everyone in the supply chain.

## Report

- $ARGUMENTS-specific changes
- Combined hyperscaler trend after this update
- Anything thesis-relevant for my supply chain watchlist (e.g., "MSFT raised FY capex guide by 8% — bullish for VRT, GEV, BE")
