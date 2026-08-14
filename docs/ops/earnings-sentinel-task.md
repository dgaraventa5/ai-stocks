# earnings-sentinel scheduled task — canonical prompt

Registered on the local scheduler: weekdays 18:30 ET (`30 18 * * 1-5`),
taskId `earnings-sentinel`. This file is the versioned source of the prompt;
if it changes, re-register the task.

---

You are running the earnings sentinel for the AI Supply Chain research
project (spec docs/superpowers/specs/2026-08-13-earnings-sentinel-design.md).
Working directory: /Users/dom/Desktop/ai-stocks. Use the REAL current date
(`date +%F`); never hardcode dates. Read CLAUDE.md rules 9, 12, 25, 29, 31
before starting.

STEPS:
1. Detect: `python3 scripts/earnings_sentinel.py` (JSON on stdout). If both
   `briefing_due` and `rescore_due` are empty: append one line
   "<today>: quiet (scope N, flagged: …)" to tracking/earnings-sentinel-log.md
   ONLY if `flagged` is non-empty, then STOP. Most evenings end here.
2. Git setup (only if events exist): `git fetch origin main` then
   `git checkout -b earnings/<today> origin/main` (branching discipline —
   never branch from local main).
3. BRIEFING PHASE — for each name in `briefing_due`, independently:
   - Fetch the press release / 8-K from SEC EDGAR and the transcript if
     published (fall back to WebSearch with the current year in the query).
   - Write per-stock/<TICKER>/context-<today>.md: Headline numbers vs
     consensus / Guidance / DIFF vs prior mental model / Implications for
     ratings (which D/M/R dimensions look affected — do NOT change ratings).
   - Append one line to per-stock/<TICKER>/news-log.md (date + source + summary).
   - If revenue or EPS surprise exceeds ±15% or gross margin moved >500bps
     sequentially, prefix the run-log entry with "⚠️ RULE-9 IMMEDIATE".
   - `python3 scripts/earnings_sentinel.py --mark briefed <TICKER> <report_date>`
4. RESCORE PHASE — if `rescore_due` is non-empty (run once for the whole set):
   - `python3 scripts/refresh_objective_inputs.py <TICKERS> --dry-run`, review
     output for obviously-corrupt values (rule 27 market-cap check), then run
     without --dry-run.
   - `python3 scripts/momentum_50dma.py <TICKERS>`
   - `python3 scripts/refresh_reverse_dcf.py <TICKERS>`
   - `python3 scripts/recalc_watchlist.py --sync`  (auto-chains refresh_targets,
     rule 25; a membership/tier change fires a model event + ticket, rule 29)
   - For each ticker: `python3 scripts/earnings_sentinel.py --mark rescored
     <TICKER> <report_date>`
   - Flag in the run log, do not fix: Layer-9 capacity-cohort names (EV/MW
     denominator needs human MW research, rule 13) and TTM-vs-MRQ divergence
     >10pts on any quality metric (rule 9).
5. Report: append a dated section to tracking/earnings-sentinel-log.md —
   names briefed, names re-scored with before/after Total Score and rank,
   whether a model event fired, whether a ticket was generated OR refused
   (stale/missing recon snapshot), and all flags. If a model event fired or a
   ticket was refused, also notify:
   `osascript -e 'display notification "<one-line summary>" with title
   "Earnings sentinel" sound name "Submarine"'`
6. Commit (stage explicit paths — per-stock/, tracking/earnings-sentinel-*,
   00-master/*.xlsx, tracking/score-history.csv; NEVER `git add -A`), push,
   open a PR titled "Earnings sentinel <today>". If push/PR is blocked
   (headless egress), leave the branch and note it in the run log.
7. You are read-only toward Robinhood (rule 29): never call any order/write
   tool; execution belongs exclusively to Dom's launchd executor.

SUCCESS CRITERIA: quiet exit on no-event days; on event days — sourced
briefings + news-log lines for every reporting name, the mechanical re-score
chain run exactly once, state marked, run log + notification accurate about
whether a ticket exists, no rating changes, no order tools.
