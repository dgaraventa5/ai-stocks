---
description: Weekday watch — earnings sentinel (brief, then re-score) plus news and filing watch on holdings and the top 25
---

Run the daily watch. This is normally an unattended scheduled run: do not stop
to ask questions. **Read `docs/ops/scheduled-runs.md` first and follow its run
sequence and limits exactly** (preflight → branch → job → hold + test → land →
report → release). Read CLAUDE.md rules 9, 12, 25, 26, 29, 31, 35.

Scope: current holdings ∪ top 25 tradable ranks (the earnings-sentinel scope).

## 1. Preflight

`python3 scripts/scheduled_run.py preflight --job daily-watch` — exit 1 means
notify with the problems and stop.

## 2. Detect

```bash
python3 scripts/earnings_sentinel.py                       # briefing_due / rescore_due / flagged
python3 scripts/scheduled_run.py scan-filings --scope watch --days 4 --out "$TMPDIR/filings.json"
python3 scripts/refresh_targets.py --check                 # exit 1 = a model event is pending
```

`scan-filings` exit 1 means SEC lookups failed — report the window as
UNCHECKED, never as quiet. Drop filings already recorded in the name's
`news-log.md` (the 4-day window overlaps on purpose so weekends are covered).

Then the news watch: one WebSearch per scope name for the last 2 days
("{company} {ticker} news {month year}"), plus one for each name with a live
entry hold in `00-master/entry-holds.json`. Keep only items dated inside the
window from a primary or wire source; an undated hit is unverified, not news.

**Material** means it could change a thesis or a rating: customer win or loss,
guidance change, capacity or capex announcement, CEO/CFO/CTO change,
acquisition or divestiture, large financing, a regulator or court action, an
auditor or going-concern change, a credible competitive or product shock.
Price moves, analyst targets, dividends and conference appearances are not.

**Quiet day** = nothing due, nothing material, `--check` green. Branch, then
`python3 scripts/scheduled_run.py log --text "quiet (scope N, filings F); <any
not-material or could-not-verify items, one clause each>"`, then `land` and
`merge` per the protocol, release the lock, and stop. No Notion page, no
notification. Most days end here.

On every other day, log one line the same way before landing (what reported,
what moved, what needs Dom).

## 3. Earnings — briefing phase (`briefing_due`, at most 8 names, highest rank first)

For each: read the earnings 8-K exhibit from EDGAR (and the call transcript if
published), then write `per-stock/{T}/context-{date}.md` — headline numbers
vs consensus, guidance, what changed vs the prior briefing, and which rating
dimensions look affected. Append one line to `news-log.md`. Mark with
`python3 scripts/earnings_sentinel.py --mark briefed {T} {report_date}`.
A revenue or EPS surprise beyond ±15%, or gross margin moving more than
500bps sequentially, is a rule-9 immediate flag — lead the report with it.

## 4. Earnings — re-score phase (`rescore_due`, once for the whole set)

```bash
python3 scripts/refresh_objective_inputs.py {TICKERS} --dry-run   # look for corrupt values first
python3 scripts/refresh_objective_inputs.py {TICKERS}
python3 scripts/momentum_50dma.py {TICKERS}
python3 scripts/refresh_reverse_dcf.py {TICKERS}
python3 scripts/recalc_watchlist.py --sync
python3 scripts/earnings_sentinel.py --mark rescored {T} {report_date}   # each ticker
```

Record before/after Total Score and rank for each. Flag, do not fix: withheld
or STALE EPS YoY cells (rule 15 — needs Dom's ruling), Layer-9 MW denominators
(rule 13), TTM-vs-MRQ gaps over 10 points (rule 9).

## 5. Material news (at most 3 names per run; holdings first)

For each: append the `news-log.md` line (date + source + one sentence). If the
event bears on a rating, run `/refresh-context {T}` to write a dated briefing,
then append a proposal to `tracking/rating-proposals.md`:

```
## {date} — {T} — {dimension} {current} → {proposed}  (confidence Low/Med/High)
Event: … (source + date)
Why: … which rubric band the new evidence fits
Effect if approved: Total {x} → {y}, rank {a} → {b}; membership change yes/no
Status: PROPOSED
```

Compute "effect if approved" on a scratch copy of the workbook, never the live
one. **Do not change the rating.** Do not move a rating to cross a threshold.

If the name is NOT held and the event is one of the rule-35 kinds (new
government enforcement action, securities case filed in the last 90 days,
guidance cut, transformative transaction), add an entry hold to
`00-master/entry-holds.json` with `reason`, `source`, `set`, an `expires` just
after its next earnings date, and `review_event`. Never edit or remove an
existing hold.

## 6. Model

If step 4 ran, `recalc --sync` already ran the portfolio step. Otherwise, if
`--check` was red in step 2, run `python3 scripts/refresh_targets.py` (this is
the confirming run for an exit clock, or a newly enterable name). Then
`python3 scripts/capitulation_flag.py {exit-side tickers} --log-forecast` for
any name exiting or on an exit clock (rule 32-A).

Report exactly what the model did: entered, exited, clock started (and the
date it can confirm), deferred by the entry gate, or nothing.

## 7. Hold, test, land, report

Per the protocol. Notion page `Daily Watch — {date}`:

- **What happened** — two or three sentences.
- **Earnings** — table: ticker, result vs consensus, score and rank before → after.
- **News** — one line per material item with its source link.
- **Model** — events, exit clocks, entry holds added; "ticket HELD" if one was generated.
- **Needs you** — rating proposals (yes/no each), EPS rulings, held ticket.
- **Could not verify** — anything unchecked or undated.
