---
description: Weekly material news scan across the watchlist
---

Run the weekly news scan per CLAUDE.md.

## Steps

0. **For each ✓✓ or ✓✓✓ tier position: articulate your current mental model BEFORE scanning.** Write 1-2 sentences per name on what you currently believe about their AI thesis, customers, competitive position, and recent quarterly results. This is the lightweight version of `/refresh-context` — the diff between your articulated model and what the scan surfaces is the value of the exercise. Without this step you'll silently rationalize new news into your existing model and miss thesis-shifting signals.

   For full ✓✓✓ positions, consider invoking full `/refresh-context $TICKER` instead of just 8-K scanning, since highest-conviction names get the deepest refresh treatment.

1. **Read every ticker** from `00-master/ai_supply_chain_scoring.xlsx` Watchlist tab.

2. **For each ticker**, query SEC EDGAR for any 8-K filings in the past 7 days. Use:
   `https://data.sec.gov/submissions/CIK{cik}.json`
   Respect rate limit: 10 req/sec max. `time.sleep(0.1)` between requests.

3. **For each 8-K found**, read the filing and summarize what was disclosed in one sentence.

4. **Flag with ⚠️** anything that could plausibly change a thesis:
   - Customer wins or losses
   - Capacity announcements
   - Executive departures (especially CEO, CFO, CTO)
   - Guidance revisions
   - Material acquisitions or divestitures
   - Financing events (equity issuance, large debt raises)
   - Going concern or auditor changes
   - Legal/regulatory actions

5. **Also check** for new 13F-HR filings from tracked funds in the past 7 days. If found, note them — these can be followed up with `/thirteenf-delta`.

## Output

Save to `/tracking/weekly-news-scan-{YYYY-MM-DD}.md` with three sections:
- **⚠️ Material events** (full one-sentence summary per item, plus ticker)
- **Routine filings** (one-line each: ticker, filing type, generic descriptor)
- **New 13F activity** (only if any)

## If nothing material

Write "No material developments this week." and stop. Don't pad. The point of this scan is signal-to-noise, not coverage volume.
