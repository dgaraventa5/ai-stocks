# Improvements

Format: - [ ] Title — why it matters (evidence). Done when: <checkable condition>. [impact×confidence÷effort score, S/M/L]

## Open


## Needs Dom
<!-- Findings the loop must not act on: they touch Off-limits paths, need a deletion, or need something only Dom can do. The loop never works these. Approved items are done in an attended session; declined items move to Rejected. -->

- [ ] Upgrade local packages — certifi, urllib3 and soupsieve on this Mac carry published advisories, reachability unchecked. The executor runs on Homebrew Python, so pinning `requirements.txt` does not reach it. Action: Dom upgrades Homebrew Python packages.
- [ ] Get a CourtListener token — the litigation check returns 401 for every name without one. Action: Dom creates a free account; the code side is done.
- [ ] Review the 11 drafted thesis-break triggers — each is in its `thesis.md` marked as a draft, with sources and caveats in `tracking/thesis-trigger-drafts.md`. MSFT, SNDK and TSM have weak support, and ALAB, ANET and PLTR report this week. Action: Dom approves or edits each.
- [ ] Decide whether to track hyperscaler capex — `tracking/hyperscaler-capex.xlsx` has no inputs filled and `/capex-update` has no caller. Decision: schedule it, or retire the tracker?
- [ ] Decide whether expired research should block — `audit_rating_integrity.py` now reports names whose only research is past the 90-day window (123 on 2026-11-02, none held or top 25), but they still pass the rule-12 gate. Decision: make EXPIRED a hard gate, keep it as a report, or limit it to held and top 25?
- [ ] Remove the retired trade-hold step from the scheduled prompts — the daily watch, weekly scan and rating research prompts still say "Trades are held" and call `scheduled_run.py hold-tickets`, which was removed 2026-11-01, so that step errors and the wording contradicts rule 37. An attended edit of the prompts was refused on 2026-11-02. `/daily-watch`, `/weekly-scan` and `docs/ops/scheduled-runs.md` also still mention held tickets. Action: Dom OKs the wording, or edits the three tasks in the app.
- [ ] Pre-approve the new read-only scripts — `run_health.py`, `input_currency.py` and `thesis_watch.py` are not in `.claude/settings.json`, nor is `portfolio_theses.py`, which already runs. Scheduled runs may still allow them, and the 2026-11-07 weekly scan will be the first real test. Action: Dom adds them if that run is blocked.

## Done

- [x] Add the thesis-break watch — `scripts/thesis_watch.py` prints every portfolio trigger, and `/weekly-scan` compares the week's news to them. Approved by Dom 2026-11-02. Drafts stay marked until Dom reviews them (Needs Dom).
- [x] Schedule quarterly work — `/rescore-quarterly` now has unattended rules and runs on the 22nd of Feb, May, Aug and Nov (task `ai-stocks-quarterly-rescore`), approved by Dom 2026-11-02. The first calibration report graded the 14 resolved forecasts: Brier 0.41, worse than the base rate, on a sample the report itself calls noise.
- [x] Show which quarter each score rests on — `scripts/input_currency.py` runs in `/weekly-scan` Step 6e, and the site now shows a scores date beside the performance date. It uses the newest quarter with revenue, because Yahoo can post a column with only EPS. Its run on 2026-11-02 over holdings and the top 25 found AMZN, APH, NVT, PLTR, RDDT and SNDK behind. BEHIND is a prompt to look: an Item 2.02 8-K can be a preliminary release or a presentation. Approved by Dom 2026-11-02.
- [x] Put run health in the weekly scan — `/weekly-scan` Step 11 reports it, and only misses from the last 14 days fail the exit code, so an old miss ages out. Approved by Dom 2026-11-02.
- [x] Hold thinned peer baskets through the grace window — a forecast with any peer short of prices now stays open until grace ends, then grades on the same 25% rule, approved by Dom 2026-11-02. A delisted or thinly traded peer such as TOELY therefore makes a forecast wait the full 30 days, and `resolve_forecasts.py` exits 1 for it until then, so weekly scans can report it as ungraded for about five weeks.
- [x] Merge the rule-13 cohort check — `scripts/layer_cohorts.py` is now the one definition and all four scoring files import it. All 217 scores came out identical before and after on 2026-11-02. The live cohort is 15 names, while rule 13 still lists 12.
- [x] Retire the ten finished scripts — the nine one-offs and `weekly_scan_runner.py` are deleted, approved by Dom 2026-11-02, and stay in git history. The six watch-only 13F funds now live in `.claude/commands/thirteenf-delta.md`, and `/weekly-scan` reads them there.
- [x] Pin the CI test tools — every workflow now installs from pinned files (`requirements-test.txt` holds pytest and openpyxl), and a test fails any unpinned `pip install` line. Attended fix, approved by Dom 2026-11-02.
- [x] Stop failed lookups counting as a quiet day — `/daily-watch` now runs its three detect commands separately, and a quiet day needs an empty `flagged` plus a clean exit from the sentinel and `scan-filings`. A blocked run skips the re-score, and a flagged 8-K gets briefed and re-scored so the flag clears. Attended fix, approved by Dom 2026-11-02. A normal day's `flagged` was not measured because a live sentinel run was refused, so a name that stays flagged would send a report every day until it clears.
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
