---
description: Process new 13F filings from tracked funds (designed for /goal mode)
---

Check for new 13F-HR filings from tracked funds. Refer to CLAUDE.md.

## Tracked funds

- **Situational Awareness LP** — CIK 0002045724

(Add more funds here over time as instructed.)

**This command is designed for `/goal` mode.**

## Completion criteria

- [ ] For every tracked fund: latest 13F filing date checked against `/tracking/13f-tracking.xlsx`
- [ ] For every NEW filing found: holdings parsed from EDGAR XML, delta computed vs prior quarter
- [ ] A new sheet added to `/tracking/13f-tracking.xlsx` per new filing, named `{Fund}-{YYYY}-Q{N}`
- [ ] Each sheet contains: full current holdings, new positions, exited positions, top 10 adds by $ value, top 10 trims by $ value
- [ ] For every NEW position appearing in a tracked fund that isn't already in `00-master/ai_supply_chain_scoring.xlsx` Watchlist: `/score-stock` has been run

## Steps

1. Query EDGAR submissions API for each tracked fund's CIK
2. Compare latest filing date to what's in 13f-tracking.xlsx
3. For each new filing, parse the XML (use `lxml`, the filing format is INFORMATION TABLE)
4. Compute the deltas
5. Add the sheet to 13f-tracking.xlsx
6. Run `/score-stock` for each new position not yet in watchlist

## Report

Per fund: total $ value, # of holdings, top 3 changes, any thesis-relevant moves (especially adds to my watchlist names or exits from them).
