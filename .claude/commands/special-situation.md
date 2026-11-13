---
description: Temporary close watch on one name while a live situation unfolds — fresh briefing every ~2 weeks plus post-event reviews, with rating proposals
---

A **special situation** is a name whose story is moving faster than the rule-12
90-day rotation can follow: a CEO exit, an investigation, a transformative deal.
This job gives it its own cadence until the situation settles, then hands it
back to `/rating-research`. Normally an unattended scheduled run: **read
`docs/ops/scheduled-runs.md` and follow its run sequence and limits exactly.**
This job never changes a rating and never runs the scoring chain.

Arguments: `$ARGUMENTS` = `{TICKER} [post-print]`.

- `{TICKER}` alone: the **biweekly** check. It researches only when the
  newest `per-stock/{T}/context-*.md` is **10 or more days old**. A briefing
  written in the meantime (by `/daily-watch`, an earnings briefing or an
  attended session) resets the clock.
- `{TICKER} post-print`: always researches. Used for a one-off review after an
  earnings report or a scheduled event.

Active watches, their exit conditions and their tasks are listed in
`per-stock/{T}/catalysts-watchlist.md` under "Special-situation watch".

## 1. Preflight

`python3 scripts/scheduled_run.py preflight --job special-{t}` (ticker in
lower case). Exit 1 → notify with the printed problems and stop.

Then `python3 scripts/scheduled_run.py branch`.

## 2. Decide whether to research

Find the newest `per-stock/{T}/context-YYYY-MM-DD.md`. In biweekly mode, if it
is under 10 days old, log
`skipped — newest briefing {date} ({n} days old)`, land and merge the log line,
release the lock and stop. No Notion page and no notification on a skip.

## 3. Research

Run `/refresh-context {T}` in full: mental model first, filings, transcript,
news, and the 2b/2c/2d/2e checks. It writes `per-stock/{T}/context-{date}.md`.
For the news, start from `python3 scripts/news_watch.py --tickers {T} --from
{date of the previous briefing} --to {today}`: a dated headline list for the
whole gap. Confirm each material item from its publisher before using it.
Exit 1 means the news side is UNCHECKED; say so in the briefing.
Search specifically for every open item in the name's "Special-situation
watch" list (e.g. for NVDA: permanent CEO named, the board investigation's
findings, congressional testimony, any agency action naming the company,
China import approvals). Use the current year in every query. Append news-log
lines for anything material, and update the catalysts table: move resolved
items to resolved, add new dated ones.

**Skip refresh-context's objective-input step.** This job does not write the
workbook; `/daily-watch` and `/weekly-scan` own re-scoring.

## 4. Propose, don't apply

Compare every dimension (D1–D5, M1–M3, R1–R5) against
`templates/rating-rubric-and-workflow.md` using the new briefing.

- For each **open** proposal on this name in `tracking/rating-proposals.md`,
  re-compute it on current data. Append a replacement entry and change the old
  entry's `Status:` line to `SUPERSEDED {date} (re-computed below)`. If the
  evidence no longer supports it, append an entry saying so with
  `Status: WITHDRAWN-SUGGESTED` and leave the old one for Dom to close.
- For any other dimension whose evidence now fits a different band, append a
  new proposal in the `/daily-watch` step 5 format, with "effect if approved"
  computed on a scratch copy of the workbook.
- Say "no change" explicitly for dimensions that hold.

Never edit an `APPROVED` or `DECLINED` entry. Never propose a move in order to
cross a tier or rank threshold.

## 5. Exit check

Read the watch's exit conditions. If **all** are met, say so at the top of the
report: "the {T} special-situation watch can be retired". Retiring it is Dom's
decision; it means disabling the scheduled task and marking the watch closed in
the catalysts file. Never disable or delete a scheduled task from a run.

## 6. Land and report

Per the protocol: test, `land`, `merge`, confirm the deploy. Then publish a
Notion page `{T} Special Situation — {date}` under the protocol's parent page.
Open with what changed since the last briefing, in plain English with sources.
Then the proposals (ticker, dimension, current → proposed, one-line reason,
score/rank effect, membership change yes/no), the open items still unresolved,
and the exit-check result. Then send one notification, for example
"NVDA watch: CEO search still open; R4 proposal re-confirmed, M1 now 4→4; 2 items need you".
Always finish with `python3 scripts/scheduled_run.py release`.
