# Scheduled runs — shared protocol (CLAUDE.md rule 37)

Four unattended jobs keep research and scores current. Each is a project
skill; the desktop scheduler only holds a thin prompt that invokes it.

| Job (`--job`) | Skill | Schedule (Pacific) | What it does |
|---|---|---|---|
| `daily-watch` | `/daily-watch` | Mon–Fri 15:45 | Earnings sentinel (briefing, then mechanical re-score) + news and filing watch on holdings ∪ top 25 |
| `weekly-scan` | `/weekly-scan` | Sat 08:00 | Full-watchlist filing scan, objective refresh, portfolio pipeline, weekly mark |
| `rating-research` | `/rating-research` | Sun 08:00 | Fresh briefings for the stalest rated names, with rating proposals |
| `quarterly-rescore` | `/rescore-quarterly` | 22nd of Feb, May, Aug, Nov at 12:00 | Refreshes rows over 90 days old, re-baselines the EW benchmark, writes the rescore and calibration reports |

**Where they run: this Mac, in the main checkout — never a cloud session.**
Cloud sandboxes block Yahoo and SEC at the network proxy (every cloud scan from
2026-06-12 to 2026-09-18 fell back to web search and re-scored nothing). The
Claude desktop app must be open and the Mac awake; a missed run fires at the
next launch. Machine-local state (`tracking/earnings-sentinel-state.json`,
`tracking/live/`, `.cache/`) is why a worktree is not used.

## Autonomy (Dom, 2026-10-12; trading amended 2026-11-01)

A scheduled run MAY, without asking:
- write briefings (`per-stock/{T}/context-{date}.md`), news-log lines, cached filings;
- refresh objective inputs and run the scoring chain, including a model event
  (`refresh_targets.py`) when membership changes or an exit clock confirms;
- ADD a rule-35 entry hold for a not-held name (a hold only delays a buy);
- write the three-sentence thesis for a name that joined the Targets without
  one (rule 39);
- commit, open a PR, merge it once CI passes, and confirm the site deployed.

A scheduled run MUST NOT:
- change any subjective rating (D1–D5, M1–M3, R1–R5) or append to the Rating
  Audit — it writes a proposal to `tracking/rating-proposals.md` instead;
- write a rule-15 EPS ruling (withheld cells stay withheld; list them);
- remove, shorten or extend an entry hold; edit CLAUDE.md, the rubric,
  methodology bands, cohort membership or `capacity-mw.json`;
- place a trade. Never call a Robinhood order/write tool, never run
  `execute_ticket.py --confirm` (rule 29). A model event's ticket trades at the
  next 06:35 executor run, not from the session.
- touch `~/.hermes`, other sessions' branches, worktrees or untracked files.

Every model event writes a live ticket, in any session (2026-11-01). The next
06:35 executor run trades it. `scripts/ticket_data_check.py` leaves flagged buys
off that ticket and the executor notifies Dom; sells and other buys still go.
The monthly rebalance (rule 29, 2026-10-05) is a separate path and does not run
this check.

## Run sequence (every job)

1. **Preflight.** (The two reconciliation status files the morning executor rewrites — `tracking/live-status.json`, `tracking/live-vs-model.json` — are expected to be modified; preflight ignores them and `land` commits them with the run.)
   `python3 scripts/scheduled_run.py preflight --job <job>`.
   Exit 1 → do nothing else: send the notification with the printed
   problems and stop. Do not "work around" a failed check (no web-search
   substitute for a blocked SEC/Yahoo, no stash of someone's changes).
2. **Branch.** `python3 scripts/scheduled_run.py branch` (creates
   `auto/<job>-<date>` from origin/main). Every run branches, quiet or not.
3. **Do the job** per its skill. Use the real date (`date +%F`). Then log the
   outcome: `python3 scripts/scheduled_run.py log --text "<one line>"` appends
   to `tracking/scheduled-run-log.md`. Every run logs and lands (Dom,
   2026-10-12): nothing a run finds is left only in a chat or on this Mac,
   and a missed run shows up as a missing date. Put not-material and
   could-not-verify items in the line, briefly.
4. **Test.** `python3 -m pytest tests -q`. A quiet run whose only change is its log
   line skips this step (CI still gates the merge). On a test failure still run step 5's `land`
   (so the work is visible on a PR) but NOT `merge`; notify, release the lock,
   stop. The next run's preflight refuses until that PR is dealt with — loud
   by design.
5. **Land.** `python3 scripts/scheduled_run.py land --message "<title>"
   [--body-file <path>]` then `python3 scripts/scheduled_run.py merge`.
   Do not run `git add`, `git commit`, `git push` or `gh pr merge` yourself —
   they are deliberately not pre-approved. `land` stages only `per-stock/`,
   `00-master/` and `tracking/`, refuses if anything else or anything under
   `tracking/live/` is staged, and pushes only this run's branch; `merge`
   waits for CI, squash-merges only this run's PR and syncs local main.
   Then confirm the site deploy: `gh run list --workflow deploy-site.yml --limit 1`.
6. **Report.** Notion page (below), then one notification, then
   `python3 scripts/scheduled_run.py release`. Always release the lock, on
   every exit path.

## Reporting

- **Notion:** child page under `368b69da11c081968dfdf4e44f6000e0`
  ("AI Supply Chain — 10-Layer Lifecycle Overview") via the Notion connector
  (`notion-search`, `notion-fetch`, `notion-create-pages`; load with
  ToolSearch). Search for the exact title first and update rather than
  duplicate. Titles: `Daily Watch — {date}`, `Weekly News Scan — {date}`,
  `Rating Research — {date}`, `Quarterly Rescore — {date}`. No real dollars, share counts or account
  numbers (rule 29). Only the weekly scan appends to
  `tracking/notion-scan-links.json`.
- **Notification:** `python3 scripts/scheduled_run.py notify --message "<line>"`
  — a plain macOS notification, one line under 200 characters, leading with
  what needs Dom ("PLTR re-scored 74→77, enters at rank 14; ticket trades at the next 06:35 run"). Do
  not use the in-app PushNotification tool: it skips delivery when the run's
  own window counts as active (2026-10-13).
- **Quiet daily runs** make no Notion page and no notification, but they
  still land and merge their one log line in `tracking/scheduled-run-log.md`.
  The weekly
  scan reads that file and reports how many daily runs happened.
- If Notion is not connected, still land the work, say so in the
  notification, and put the report in the PR body.

## Written for Dom

Plain English, decision first. Every number cites its source (rule 1). A gap
is stated as a gap (rule 3). Each report ends with **"Needs you"**: rating
proposals awaiting a yes/no, EPS rulings, buys the data check left off a
ticket, expiring entry holds.

## Buys the data check left off

A buy that `ticket_data_check.py` flags waits for the next ticket; the rest of
the ticket still trades. To place it sooner, fix or rule on the flagged data in
an attended session, then regenerate from a fresh reconciliation with
`python3 scripts/generate_trade_ticket.py`. A manual run does not repeat the
data check (only a model event's ticket does), so look at the flag before
regenerating. The ticket sends at the next 06:35 run, or
sooner if Dom runs `python3 scripts/execute_ticket.py --ticket <path> --confirm`
himself.
