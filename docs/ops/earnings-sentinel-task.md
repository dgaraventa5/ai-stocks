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
1. Detect: `python3 scripts/earnings_sentinel.py` (JSON on stdout). Quiet runs
   append one line "<today>: quiet (scope N, flagged: …)" to
   tracking/earnings-sentinel-log.md only when `flagged` is non-empty. Either
   way, when both `briefing_due` and `rescore_due` are empty, the run STOPS
   here — most evenings end here.
2. Git setup (only if events exist): first run the unmerged-branch guard —
   `git branch --list 'earnings/*' --no-merged origin/main`. If this lists any
   prior earnings/* branch, do NOT proceed with any phase (briefing or
   rescore): append a line to tracking/earnings-sentinel-log.md noting the
   unmerged branch, send
   `osascript -e 'display notification "prior earnings-sentinel branch
   unmerged — merge it, then the sentinel resumes" with title "Earnings
   sentinel" sound name "Submarine"'`, and STOP. (This guard exists to prevent
   nightly binary-xlsx merge collisions.) Otherwise: `git fetch origin main`
   then `git checkout -b earnings/<today> origin/main` (branching discipline —
   never branch from local main).
3. BRIEFING PHASE — if `briefing_due` has more than 8 names, brief only the 8
   highest-ranked (by the scope's score order) this run; leave the rest
   unmarked (they remain due tomorrow) and note the deferral in the run log
   (step 6). For each briefed name, independently:
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
5. Test gate (only if steps 3/4 ran): run `python3 -m pytest tests/ -q`.
   Record the result in the run log (step 6) AND the PR body (step 7). If the
   ONLY failure is `test_targets_reweight_gate` and it is because a rule-26
   exit-pending clock started this run, that is expected-by-design — say so
   explicitly in the PR body rather than blocking. Any OTHER failure: do NOT
   open the PR — report it in the run log and the notification (step 6)
   instead, and leave the branch for Dom.
6. Report: append a dated section to tracking/earnings-sentinel-log.md —
   names briefed, names re-scored with before/after Total Score and rank,
   whether a model event fired, whether a ticket was generated OR refused
   (stale/missing recon snapshot), the step-5 test-gate result, and all flags
   (including any briefing-phase deferral from step 3). If a model event
   fired, a ticket was refused, the unmerged-branch guard fired, or the test
   gate blocked the PR, also notify:
   `osascript -e 'display notification "<one-line summary>" with title
   "Earnings sentinel" sound name "Submarine"'`
7. Commit (stage explicit paths — per-stock/, tracking/earnings-sentinel-*,
   tracking/performance-config.json, 00-master/*.xlsx, 00-master/reverse-dcf.json,
   tracking/score-history.csv; NEVER `git add -A`), push, open a PR titled
   "Earnings sentinel <today>" whose body includes the step-5 test-gate result
   (and the rule-26-exit-clock caveat when applicable). If push/PR is blocked
   (headless egress), leave the branch and note it in the run log.
8. You are read-only toward Robinhood (rule 29): never call any order/write
   tool; execution belongs exclusively to Dom's launchd executor.

SUCCESS CRITERIA: quiet exit on no-event days; on event days — sourced
briefings + news-log lines for every reporting name, the mechanical re-score
chain run exactly once, state marked, run log + notification accurate about
whether a ticket exists, no rating changes, no order tools.
