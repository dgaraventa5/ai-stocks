---
description: Weekly research rotation — fresh briefings for the stalest rated names, with rating proposals for approval
---

Refresh the research behind the oldest subjective ratings (CLAUDE.md rule 12).
Normally an unattended scheduled run: **read `docs/ops/scheduled-runs.md` and
follow its run sequence and limits exactly.** This job never changes a rating.

## 1. Preflight

`python3 scripts/scheduled_run.py preflight --job rating-research`

## 2. Pick the names (4 per run; `$ARGUMENTS` overrides with explicit tickers)

```bash
python3 scripts/audit_rating_integrity.py --summary
python3 scripts/audit_rating_integrity.py --stalest 12
```

Order of priority:
1. any GATE violation (rated with no thesis and no briefing) — holdings first;
2. current holdings and top-25 names whose newest briefing is over 30 days old
   (these are the names the rule-35 entry gate would defer);
3. the stalest remaining names, rotating layers so one layer does not take
   every slot.

Also list entry holds in `00-master/entry-holds.json` expiring within 10 days;
a name on that list takes a slot, because its hold lapsing makes it buyable.

## 3. Research each name — one at a time, per ticker, no sector shortcuts

Run `/refresh-context {T}` in full for each (mental model first, then filings,
transcript, news, the FCF-conversion check, the expectations flag and the
capitulation flag). It writes `per-stock/{T}/context-{date}.md`. Append the
news-log lines for anything material it surfaced. Use parallel subagents for
the reading, but serialize SEC and Yahoo calls.

## 4. Propose, don't apply

Compare every dimension (D1–D5, M1–M3, R1–R5) against the rubric at
`templates/rating-rubric-and-workflow.md` using the fresh briefing. For each
dimension where the evidence fits a different band, append to
`tracking/rating-proposals.md` in the format given in `/daily-watch` step 5,
with "effect if approved" computed on a scratch copy of the workbook. Say
"no change" explicitly for a name whose ratings all hold — that is a result.

Apply the absolute rubric, not relative ranking. Never propose a move in order
to cross a tier or rank threshold. For a hold about to expire, state whether
the event behind it has resolved (Dom decides whether to renew).

## 5. Land and report

Per the protocol (briefings and proposals are committed; no scores move, so no
model event is expected — run `python3 scripts/refresh_targets.py --check` and
report if it is red). Notion page `Rating Research — {date}`:

- **What I looked at** — the names and why each was picked.
- Per name: what changed since the last briefing, in three or four sentences,
  with sources.
- **Needs you** — a table of proposals: ticker, dimension, current → proposed,
  one-line reason, effect on score and rank, membership change yes/no.
- **Holds expiring** — and whether each still looks warranted.
- **Queue** — how many names remain over 90 days stale.
