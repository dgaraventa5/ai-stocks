# Improvements

Format: - [ ] Title — why it matters (evidence). Done when: <checkable condition>. [impact×confidence÷effort score, S/M/L]

## Open


## Needs Dom
<!-- Findings the loop must not act on: they touch Off-limits paths, need a deletion, or need something only Dom can do. The loop never works these. Approved items are done in an attended session; declined items move to Rejected. -->

- [ ] Retire nine finished one-off scripts — they have no remaining job and most can overwrite live workbooks; six hardcode the main checkout's path, so running one from a worktree still writes to main (`add_50dma_metric`, `apply_compzone_rerate`, `apply_ep_moat_fix`, `apply_layer1_rerate`, `apply_layer1_rerate_batch2`, `batch_robotics_20260802`, `build_workbooks`, `remove_ctra`, `reweight_and_add_peg`). Decision: delete them? They stay in git history.
- [ ] Retire `scripts/weekly_scan_runner.py` — frozen on a September window, turns SEC errors into "no filings", and the README still calls it primary (`:37-38`, `:108-109`). Move its six 13F fund CIKs somewhere tracked first. Decision: delete it?
- [ ] Upgrade local packages — certifi, urllib3 and soupsieve on this Mac carry published advisories, reachability unchecked. The executor runs on Homebrew Python, so pinning `requirements.txt` does not reach it. Action: Dom upgrades Homebrew Python packages.
- [ ] Get a CourtListener token — the litigation check returns 401 for every name without one. Action: Dom creates a free account; the code side is in Open.
- [ ] Track hyperscaler capex and thesis-break triggers — `tracking/hyperscaler-capex.xlsx` has no inputs filled, `/capex-update` has no caller, and 11 of 17 portfolio names have a placeholder break trigger. Decision: who writes the triggers, and should a read-only `scripts/thesis_watch.py` be wired into `/weekly-scan`?
- [ ] Show which quarter each score rests on — Last Updated stamps every refresh even when Yahoo still serves the old quarter (`scripts/refresh_objective_inputs.py:424`), and the site's "Data as of" is the performance date, not the scores date. Decision: wire a read-only `scripts/input_currency.py` into `/weekly-scan`, and add a scores date to the exporter?
- [ ] Schedule quarterly work — no quarterly rescore or calibration report has ever been written, so the forecasts resolved 2026-10-17 are ungraded. Decision: schedule `/rescore-quarterly`?
- [ ] Fix the rule-13 cohort check duplication — `is_layer9_capacity` lives in four scoring files, so a cohort change has to hit all four. Decision: consolidate, with a before/after score check?
- [ ] Stop sentinel flags counting as a quiet day — `/daily-watch` defines quiet as "nothing due, nothing material, `--check` green" and never mentions `flagged`, so a day whose only news is a failed lookup sends no page or notification (`.claude/commands/daily-watch.md:39`; `2ba3c89a` makes these flags more common). The file is Off-limits to the loop. The sentinel can now also exit 1 with `blocked: true`, and `/daily-watch` does not handle that either: run as one command block, only the last exit code is seen. Decision: treat a non-empty `flagged` or `blocked` as not quiet, or require them in the run-log line?
- [ ] Decide whether expired research should block — `audit_rating_integrity.py` now reports names whose only research is past the 90-day window (123 on 2026-11-02, none held or top 25), but they still pass the rule-12 gate. Decision: make EXPIRED a hard gate, keep it as a report, or limit it to held and top 25?
- [ ] Decide how a thinned peer basket should grade — a forecast still gets a permanent grade when up to 25% of its peers have no prices, even inside the grace window (`scripts/forecast_resolvers.py:73`, `MISSING_CONSTITUENT_TOLERANCE`), so a partial throttle can grade on a smaller basket. Rule 17 treats resolution rules as frozen. Decision: hold these inside grace, or keep the tolerance?
- [ ] Pin the CI test tools — `requirements.txt` is now pinned, but `pytest` is still installed unpinned (`.github/workflows/ci.yml:22`, `daily-refresh.yml:63`), and `deploy-site.yml:16` installs `openpyxl pytest` unpinned. Workflows are Off-limits to the loop. Action: pin them in an attended session.
- [ ] Decide how to use the run health check — nothing runs `scripts/run_health.py` yet, and wiring it into `/weekly-scan` touches an Off-limits file. Its exit stays 1 for good once any slot is missed, because the log is append-only, and until a calibration report exists. Decision: wire it in as a report, and if the exit code should mean anything, add a recent-days window first?

## Done

- [x] Run health check: detect missed runs and sort failed workflows — `scripts/run_health.py` lists 10-21 and 10-22 as missed and 10-25 as late, labels failed runs by-design or real, and writes nothing (`5b12ac93`). Dom chose to commit after a fourth evaluation failed on test gaps only; those gaps were closed afterwards and no evaluator has reviewed the closing tests.
- [x] Sentinel: cross-check earnings against SEC filings — flags a fresh Item 2.02 8-K the calendar lacks, reports 6-K filers as `not cross-checkable`, and sets `blocked` with a nonzero exit over 20% failed lookups (`25cee55b`). A live pass on 2026-11-02 showed 0 of 25 empty calendars, so a normal day does not block.
- [x] Pin exact package versions — all 25 packages pinned to what CI runs, suite passes on a fresh Python 3.12 venv, pip-audit clean (`ba73369e`).
- [x] Forecast resolver: hold transient price failures in the grace window — degraded results inside grace write nothing, a raised throttle is counted not a crash, and any ungraded due forecast exits nonzero (`1981c16d`).
- [x] Form 4 parser: read the real 10b5-1 checkbox — 268 sales across 1,766 cached filings moved from discretionary to plan, 0 ticked sales left mislabelled, and parse errors print UNCHECKED (`ee588859`).
- [x] Rating audit: report expired research and add tests — `--summary` prints `123 EXPIRED (held 0, top 25 0, rest 123)` as of 2026-11-02, up from the 116 first measured as briefings aged past 90 days; the gate has offline tests (`e6968cf1`). Making EXPIRED a hard gate stays Dom's call (Needs Dom).
- [x] Site: show the data date and stale warning on every page — one shared footer, red note after 5 days, disclaimer stays if meta.json fails or as_of is unreadable (`26c3e608`).
- [x] Litigation check: stop reporting green when it could not look — named skip reason, `checked N, skipped M` line, nonzero exit, optional `COURTLISTENER_TOKEN` kept out of output (`b6ff95b6`). A real token is still Dom's step (Needs Dom).
- [x] SEC requests: retry transient failures — network errors, cut-off bodies, 429 and 5xx now get up to three attempts through the rate limiter (`f1f02a91`).
- [x] Sentinel: treat an empty price lookup as a failure — an empty `history()` frame now reaches `due_events` as a failed lookup and is flagged, not deferred (`2ba3c89a`).

## Rejected
<!-- Items Dom doesn't want, each with a one-line reason. /audit must never re-propose these. -->
