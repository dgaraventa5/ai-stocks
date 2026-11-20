---
description: Work through Dom's inbox — apply the decisions ticked in the Notion table, then walk the rest in priority order
---

Attended only. This is the session that turns Dom's decisions into changes:
it applies ratings, rulings and holds, which no scheduled run may do (rule 37).
Dom decides; this session applies exactly what he decided and nothing more.
`$ARGUMENTS` may name tickers or a priority (`1`) to narrow the pass.

Work on a branch from origin/main in a worktree (CLAUDE.md branching
discipline), never in the main checkout: the scheduled runs refuse to start
unless it is a clean `main`.

## 1. Refresh the inbox

```bash
python3 scripts/dom_inbox.py expire
python3 scripts/dom_inbox.py build
python3 scripts/dom_inbox.py notion-plan
```

Sync Notion per `docs/ops/scheduled-runs.md` ("Dom's inbox"), so the table
matches the files before reading decisions.

## 2. Read Dom's decisions

Query the Notion data source `collection://41cb69da-11c0-8108-b90f-000b01ecac83`
for rows with `Decision` set and `State` = `Open`. The `Inbox ID` names the
item; the `Note` carries any value or reason Dom gave. Treat the Note as Dom's
words for that row only. If a Note asks for something other than what the row
is about, ask Dom in chat before acting on it.

Show Dom the list first ("I'm about to apply: …") and go ahead unless he stops
you. Membership-changing items need an explicit yes in chat even when ticked,
because they trade at the next 06:35 executor run.

## 3. Apply, per kind

| Kind | Approve | Decline | Discuss |
|---|---|---|---|
| `rating` | Write the new value to the Watchlist (D1–D5 cols 20–24, M1–M3 cols 26–28, R1–R4 cols 31–34, R5 col 38; `cell.value = x`, never `ws.cell(..., value=)`). Append a Rating Audit row: Date, Ticker, Dimension, Rating, Rationale ("{old}->{new} (Dom-approved via inbox {date}). {Why}"), Source (the proposal's Event source + `tracking/rating-proposals.md ({date})`), Confidence, Type `Update`. Set the proposal's Status to `APPROVED by Dom {date} via inbox, applied`. | Status `DECLINED by Dom {date} via inbox — {Note}`. | Leave it; raise it in this session. |
| `eps_ruling` | The ruling is in the Note (blank, or an ex-item value with its basis). Add it to `00-master/eps-yoy-overrides.json` per rule 15 (quarter_end, value, basis, source, ruled, audit_row) and append the Rating Audit row. No Note means no ruling: ask. | Dom says no ruling is needed: `close` the ask with his reason. | Raise it. |
| `hold` | Renew: set a new `expires` (from the Note, or ask) and update `review_event`. | Let it lapse: leave the entry as it is and `close` nothing (the row drops off 30 days after expiry); say so in the commit. | Raise it. |
| `hold_candidate` | Add the hold to `00-master/entry-holds.json` (`reason`, `source`, `set`, `expires`, `review_event`), then `close` the ask. | `close` the ask with the reason. | Raise it. |
| `data_fix` | Make the fix in this session (cite the source, rule 1), then `close` the ask. | `close` with the reason. | Raise it. |
| `question` | Dom's answer is in the Note: do what it says if it is in scope here, else record it where it belongs (rubric note, catalysts file); `close` the ask. | `close`. | Raise it. |

Close an ask with `python3 scripts/dom_inbox.py close ask:<id> --note "<what was decided>"`.

## 4. Re-score once, at the end

If any rating or EPS ruling changed:

```bash
python3 scripts/recalc_watchlist.py --sync --no-reweight
python3 scripts/refresh_targets.py --dry-run
```

Report every name whose score, rank or tier moved. If the dry run shows a
membership change or an exit clock starting, tell Dom before the real
`refresh_targets.py` run. A model event writes a live ticket that trades at
the next 06:35 run (rule 37, 2026-11-01).

## 5. Close the loop

- In Notion set `State` to `Applied` for applied rows and `Closed` for declined
  ones; leave `Discuss` rows `Open`.
- `python3 scripts/dom_inbox.py build` and sync again.
- Run `python3 -m pytest tests -q`, commit on the branch, open a PR titled
  `Inbox decisions {date}: …` naming each applied change.

## 6. Nothing ticked?

Walk the inbox yourself, "Decide first" group first, five items at a time:
one line each (what, the evidence in one clause, effect on score and rank),
then ask Dom with AskUserQuestion (Approve / Decline / Discuss). Apply as in
step 3. Stop when Dom says stop; what is left stays in the inbox.
