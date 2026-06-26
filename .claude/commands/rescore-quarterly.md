---
description: Quarterly rescore of all stale Watchlist rows (designed for /goal mode)
---

Run the quarterly rescore for the AI Supply Chain Research project. Refer to CLAUDE.md.

**This command is designed for `/goal` mode.**

## Completion criteria

- [ ] Every Watchlist row with Last Updated > 90 days has refreshed financial inputs
- [ ] Last Updated set to today for each refreshed row
- [ ] No subjective 1-5 columns modified
- [ ] `/tracking/quarterly-rescore-{YYYY}-Q{N}.md` exists with these sections:
  - Tier changes (e.g., ✓ → ✓✓, or ? → ✓) with score decomposition for each
  - Top 10 score increases (with which category drove it)
  - Top 10 score decreases (with which category drove it)
  - New names to consider (from recent 13F adds or news mentions)
  - Names to drop (✗ tier for 2 quarters running)
  - Top 15 by current Total Score
- [ ] No formula errors in the spreadsheet after save

## Execution

0. **For any row with Tier ✓✓ or ✓✓✓: MANDATORY invoke /refresh-context $TICKER.** The high-conviction names get a fresh-research pass at every quarterly rescore — these are the names where stale models cost real money. Lower-tier names can skip the research pass (objective input refresh is enough). See `.claude/commands/refresh-context.md`.
1. Identify stale rows (Last Updated > 90 days ago)
2. Re-pull financial inputs ticker by ticker. Respect SEC EDGAR rate limits (10 req/sec). yfinance can run more freely but throttle if errors appear.
3. Update Last Updated to today for each refreshed row
4. Compare current scores against the prior quarterly-rescore report
5. **Re-baseline the EW benchmark to the current universe.** After scores settle, append a new `ew_events` entry to `tracking/performance-config.json`: `{"date": "<next trading day>", "roster": [<all score>=70 tickers>]}`. Use the *next* trading day (not today) as the splice date so no already-observed bar is rewritten — the chain-link preserves prior history and drives EW returns from the new roster forward (see `portfolio_model.ew_roster_events`/`ew_growth`). Then rebuild the series: `python3 scripts/track_performance.py --series-only`. This keeps the EW skill-test tracking the live universe as it evolves instead of drifting against the frozen roster.
6. **Regenerate the calibration report (Rule #17 — the absolute-lens stress test).** Run `python3 scripts/calibration_report.py`. Review `tracking/calibration-report.md`: the headline Brier / BSS, the reliability table, and the per-dimension / per-layer breakdown. **BSS ≤ 0 on a dimension means those ratings add nothing over forecasting the cohort base rate** — surface it for a human decision (investigate or stop trusting the dimension); do NOT auto-reweight anything (rule 12). Calibration is the external standard that catches the uniform cohort bias the sort order hides.
7. Write the rescore report — note any rating changes that came out of /refresh-context briefings, with citations, and record the EW re-baseline (roster delta: added/dropped names)

## Report

When goal is met, print the top 15 tickers by Total Score so I see my priority queue for the next quarter.
