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

6. **Earnings-triggered objective refresh (Rule #9).** For any ticker where the 8-K scan surfaced quarterly earnings results (Item 2.02 "Results of Operations and Financial Condition"):

   a. Pull fresh yfinance data and update the Watchlist row's objective inputs (Fwd P/E, EV/EBITDA, FCF Yield, P/S, ROIC, Gross Margin, FCF Margin, ND/EBITDA, Rev 3yr CAGR, Rev YoY, EPS YoY). Update "Last Updated" to today.

   b. **Priority triage:** If the earnings beat/miss revenue or EPS estimates by >15%, or gross margin moved >500bps sequentially, flag with 📊 in the output — these are the names where stale inputs cost the most. Consider recommending a full `/earnings-update` for these names.

   c. **TTM check:** If yfinance TTM gross margin or FCF margin is >10 score points below the MRQ value (i.e., the most recent quarter is dramatically better than the trailing average), note the MRQ values in the output so the TTM limitation is visible.

   d. Compute the before/after Total Score for refreshed names. If any name's score moves by >5 points or crosses a tier boundary, flag with ⚠️ — this is a potential portfolio-level signal.

   **Why this exists:** During the 2026-05-26 MU review, 2-month-stale objective inputs after Q2 earnings caused a 14-point scoring error and a full tier miss (#23 → #4). The weekly scan already touches every name's 8-Ks; catching earnings and refreshing inputs in the same pass prevents this class of miss. If `/earnings-update` was already run on a name during the week, skip the refresh — don't duplicate work.

7. **Portfolio pipeline + weekly mark (added 2026-06-09).** After any score refreshes from Step 6:

   a. Refresh the 50DMA momentum inputs, then run the portfolio pipeline and the performance mark:
   ```bash
   python3 scripts/momentum_50dma.py
   python3 scripts/refresh_targets.py
   python3 scripts/track_performance.py
   ```

   `refresh_targets.py` is the **only writer** of the `Targets` sheet in `portfolio.xlsx` — do not hand-edit scores or tiers into it directly (Rule #18). Run it after any rescore that could change a held name's tier; use `--resize` to force a re-weight. It re-weights and logs a model event only on a membership or tier change; within-tier score drift freezes the snapshot (no churn). `refresh_targets.py` automatically recomputes Target % allocations for **all** portfolio members using the latest scores — not just ENTER/EXIT events. A tier upgrade (e.g., ✓✓ → ✓✓✓ from an earnings beat) immediately increases that name's target allocation; a tier downgrade decreases it. The script outputs a flag line for each holding that changed tier, with old and new allocations. This is the mechanism that keeps the portfolio composition maximally weighted toward the highest-scoring names each week.

   b. Report every pipeline FLAG in the output:
   - **ENTER/EXIT/EXIT PENDING/BLOCKED** — membership changes (ENTER/EXIT are rebalance events Dom mirrors in his account)
   - **Tier changes for existing holdings** — e.g., "MU ✓✓ → ✓✓✓: allocation 7.4% → 9.8%" — these are weight shifts without a membership change; Dom may want to rebalance toward the new target
   - **Dead tickers, layer-cap or concentration warnings, manual-override collisions**

   EXIT PENDING names confirm on the *next* weekly run — call out anything confirming next week so it isn't a surprise.

   c. Include the weekly mark (model value, returns vs SMH/QQQ/equal-weight universe) in the output. The model is the portfolio of record — membership changes logged by refresh_targets.py are rebalance events Dom mirrors in his account. Tier-driven weight shifts are reported for awareness but do not auto-log a rebalance event (only ENTER/EXIT does).

8. **Subjective-rating integrity (Rule #12, added 2026-06-10).** Run the gate + staleness audit:
   ```bash
   python3 scripts/audit_rating_integrity.py --summary
   python3 scripts/audit_rating_integrity.py   # full, if the summary shows any violations
   ```
   Report GATE violations (names carrying AI ratings with no thesis and no research briefing — their ratings are unbacked and should not be trusted) and STALE names (>90d since last research-backed review). These don't block the scan, but a GATE violation in a *portfolio holding* is a flag to surface prominently. The biweekly scheduled refresh routine handles the rotation; this step is the weekly check that it's keeping up.

9. **Resolve due forecasts (calibration loop, Rule #17, added 2026-06-26).** Grade any forecasts whose `resolution_date` has arrived:
   ```bash
   python3 scripts/resolve_forecasts.py --dry-run
   python3 scripts/resolve_forecasts.py
   ```
   Report newly **resolved** outcomes (id, outcome, the cited evidence string), anything routed to **needs_review** (needs a human-confirmed resolution), and the running **void/needs_review rate** (a high rate means the resolution rules are too vague — fix the rules, don't fudge the grades). Resolution only appends a new snapshot to `tracking/forecasts.jsonl`; it never edits a prior line.

## Output

Save to `/tracking/weekly-news-scan-{YYYY-MM-DD}.md` with these sections:
- **⚠️ Material events** (full one-sentence summary per item, plus ticker)
- **📊 Earnings refreshed** (tickers that reported this week: before/after score, TTM vs MRQ flags, any tier changes)
- **💼 Portfolio pipeline** (ENTER/EXIT/pending/blocked changes; tier-change reallocations for existing holdings with old→new Target %; weekly mark vs benchmarks; any concentration flags)
- **🔬 Rating integrity** (gate violations + stale names from Step 8; only if any exist)
- **🎯 Calibration** (newly resolved forecasts + needs_review items from Step 9; only if any)
- **Routine filings** (one-line each: ticker, filing type, generic descriptor)
- **New 13F activity** (only if any)

## If nothing material

Write "No material developments this week." and stop. Don't pad. The point of this scan is signal-to-noise, not coverage volume.
