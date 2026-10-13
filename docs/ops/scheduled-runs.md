# Scheduled runs — shared protocol (CLAUDE.md rule 37)

Three unattended jobs keep research and scores current. Each is a project
skill; the desktop scheduler only holds a thin prompt that invokes it.

| Job (`--job`) | Skill | Schedule (Pacific) | What it does |
|---|---|---|---|
| `daily-watch` | `/daily-watch` | Mon–Fri 15:45 | Earnings sentinel (briefing, then mechanical re-score) + news and filing watch on holdings ∪ top 25 |
| `weekly-scan` | `/weekly-scan` | Sat 08:00 | Full-watchlist filing scan, objective refresh, portfolio pipeline, weekly mark |
| `rating-research` | `/rating-research` | Sun 08:00 | Fresh briefings for the stalest rated names, with rating proposals |

**Where they run: this Mac, in the main checkout — never a cloud session.**
Cloud sandboxes block Yahoo and SEC at the network proxy (every cloud scan from
2026-06-12 to 2026-09-18 fell back to web search and re-scored nothing). The
Claude desktop app must be open and the Mac awake; a missed run fires at the
next launch. Machine-local state (`tracking/earnings-sentinel-state.json`,
`tracking/live/`, `.cache/`) is why a worktree is not used.

## Autonomy (Dom, 2026-10-12): "rescore, hold trades"

A scheduled run MAY, without asking:
- write briefings (`per-stock/{T}/context-{date}.md`), news-log lines, cached filings;
- refresh objective inputs and run the scoring chain, including a model event
  (`refresh_targets.py`) when membership changes or an exit clock confirms;
- ADD a rule-35 entry hold for a not-held name (a hold only delays a buy);
- commit, open a PR, merge it once CI passes, and confirm the site deployed.

A scheduled run MUST NOT:
- change any subjective rating (D1–D5, M1–M3, R1–R5) or append to the Rating
  Audit — it writes a proposal to `tracking/rating-proposals.md` instead;
- write a rule-15 EPS ruling (withheld cells stay withheld; list them);
- remove, shorten or extend an entry hold; edit CLAUDE.md, the rubric,
  methodology bands, cohort membership or `capacity-mw.json`;
- release a trade: every ticket the run generates is parked by
  `scheduled_run.py hold-tickets`. Never call a Robinhood order/write tool,
  never run `execute_ticket.py --confirm` (rule 29).
- touch `~/.hermes`, other sessions' branches, worktrees or untracked files.

Known limit, stated plainly: a held ticket only stops *that* ticket. The
launchd executor's monthly rebalance (rule 29, 2026-10-05) trades to the
Targets on the first trading day of each month regardless.

## Run sequence (every job)

1. **Preflight.** `python3 scripts/scheduled_run.py preflight --job <job>`.
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
4. **Hold + test.** `python3 scripts/scheduled_run.py hold-tickets`, then
   `python3 -m pytest tests -q`. A quiet run whose only change is its log
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
  `Rating Research — {date}`. No real dollars, share counts or account
  numbers (rule 29). Only the weekly scan appends to
  `tracking/notion-scan-links.json`.
- **Notification:** the PushNotification tool, one line under 200
  characters, leading with what needs Dom ("PLTR re-scored 74→77, enters at
  rank 14; ticket HELD"). If the tool is unavailable (this fallback is not pre-approved and will prompt):
  `osascript -e 'display notification "<line>" with title "AI stocks"'`.
- **Quiet daily runs** make no Notion page and no notification, but they
  still land and merge their one log line in `tracking/scheduled-run-log.md`.
  The weekly
  scan reads that file and reports how many daily runs happened.
- If Notion is not connected, still land the work, say so in the
  notification, and put the report in the PR body.

## Written for Dom

Plain English, decision first. Every number cites its source (rule 1). A gap
is stated as a gap (rule 3). Each report ends with **"Needs you"**: rating
proposals awaiting a yes/no, EPS rulings, held tickets, expiring entry holds.

## Releasing a held trade

In an attended session: say "release the held ticket". Held tickets go stale
(2-trading-day expiry, 3% quote drift), so release means regenerating from a
fresh reconciliation, then Dom runs `python3 scripts/execute_ticket.py
--ticket <path> --confirm` himself.
