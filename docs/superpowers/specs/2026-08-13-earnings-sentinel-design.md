# Earnings Sentinel — event-driven refresh + same-cycle execution seam

**Date:** 2026-08-13
**Status:** Approved design, pending implementation plan
**Approved by:** Dom (conversation 2026-08-13)

## 1. Problem

Rule 9 mandates an earnings-triggered objective refresh — within one session for
big beats/misses, within a week otherwise — but its only enforcement is Step 6
of the weekly scan. A name reporting Tuesday can carry a stale score until the
following Monday: up to 6 days of latency on exactly the names where staleness
costs the most (the MU incident that created rule 9 was a 14-point, full-tier
miss). Since portfolio construction v2, a stale score is not just a research
problem — it directly delays rank-selection membership changes and therefore
trades.

## 2. Goal / non-goals

**Goal:** when a name that can move the portfolio reports earnings, re-score it
on the first post-reaction close and let the existing execution pipeline trade
the resulting model event the next morning — cutting print-to-trade latency
from up to 6 days to ~26–41 hours — while teeing up the rule-12 subjective
review the same evening the print drops.

**Non-goals (deliberate):**
- No intraday re-scoring. Momentum 50DMA and the market-cap-based Value ratios
  are defined on daily closes; scoring a partial-day price degrades input
  quality to buy ~1 day that captures nothing (the gap move is untradable by
  any end-of-day system). Real-time speed is an explicit non-goal of the
  project charter.
- No second execution window. The Phase-3 executor's single predictable
  06:35 PT run (spec §C5) is a safety feature; this design does not touch it.
- No new execution code and no order tools in any Claude session (rule 29
  invariant — restated in §7).
- No methodology changes: no new Watchlist columns, no band/param changes, no
  change to the weekly scan (it remains the rule-9 catch-all).
- No automatic subjective rating changes (rule 12 — ratings stay in the human
  loop; the sentinel only drafts the briefing).

## 3. Scope: which names are watched

**Current holdings ∪ top 25 tradable ranks**, rebuilt at every run:

- Holdings from the portfolio model (Targets roster).
- Top 25 by rank from the most recent `tracking/score-history.csv` snapshot,
  filtered through `portfolio_sizing.is_tradable` (rule 30). Rank 25 covers
  held names (1–15), the hysteresis dead-band (16–18), and the BAND_NEXT
  scouts (19–25) — every name where a fresh score can change a position or
  the pre-registered band experiment. Names ranked 26+ cannot enter the
  portfolio until they climb, so their earnings stay on the weekly cadence.

Holdings are always tradable (rule 30 exits untradables immediately), so the
scope is all-US-listed — which is also where yfinance earnings-date coverage
is reliable.

The top-25 is taken **over the tradable-filtered ranking**, matching
selection's own tradable-universe ranking (rule 30) — foreign lines vacate
slots rather than occupying them, so in full-universe terms (Watchlist rank,
foreign names included) the effective scope can reach roughly rank 35.

## 4. Detection: `scripts/earnings_sentinel.py`

Pure detector — **no side effects on any workbook or tracking artifact except
its own state file**. Responsibilities:

1. Build the scope set (§3).
2. Pull each name's next/most-recent earnings date via yfinance
   (`Ticker.get_earnings_dates()`; import lazy — CI minimal-env rule). A name
   with no date available is listed in the output under `flagged`, never
   guessed (rule 3); the weekly cadence covers it.
3. Compute each report's **reaction day** — the first regular session whose
   close reflects the print:
   - Report timestamped before 09:30 ET (BMO) → reaction day = report day.
   - Report timestamped after 09:30 ET (AMC) → reaction day = next trading
     day.
   - Timestamp missing/unparseable → treat as AMC (conservative: waits one
     extra day rather than re-scoring on a pre-reaction close).

`MAX_REPORT_AGE_DAYS = 5`: a report that is already more than 5 days old the
first time the sentinel sees it (first deployment, or a name newly entering
scope) is left to the weekly cadence rather than briefed/rescored — a
self-healing guard against dumping a backlog of stale reports into a single
run.

4. Emit two event lists against per-ticker state:
   - **`briefing_due`** — report has dropped (report timestamp ≤ now) and no
     briefing has been recorded for it. Fires the evening of the print (T+0).
   - **`rescore_due`** — a regular-session close ≥ reaction day exists (the
     run is at 18:30 ET, after the close) and no re-score has been recorded
     for this report. Fires the evening of the reaction day.

**State:** `tracking/earnings-sentinel-state.json` — per ticker, the report
date last briefed and last re-scored. **Machine-local and gitignored** (not
committed): the sentinel always runs on Dom's own machine, and this file is
process state, not project state — committing it would create nightly
diff/merge churn on a file with no research content. Both phases are
idempotent: re-running the sentinel after a completed phase emits nothing.
State updates only after the corresponding phase actually completes — the
task calls back
`earnings_sentinel.py --mark {briefed|rescored} {TICKER} {report-date}` when a
phase finishes, never at detection time — so a failed run retries next
evening.

Output is JSON on stdout: `{briefing_due, rescore_due, flagged}` with the
report date and BMO/AMC classification per name.

## 5. The scheduled task: `earnings-sentinel`

Local scheduled task (same scheduler as `weekly-rating-refresh`), **weekdays
18:30 ET**. Market holidays need no special casing — no new close exists, so
nothing becomes due. Most evenings both lists are empty and the run exits in
seconds.

**Phase 1 — briefing (evening of the print), per `briefing_due` name:**
- Draft a context briefing `per-stock/{TICKER}/context-{YYYY-MM-DD}.md` from
  the release/8-K (EDGAR) and transcript if published — the rule-12 D-dimension
  review is teed up the night the print drops, not days later.
- Rule-9 immediate tier: if revenue or EPS surprise exceeds ±15%, or gross
  margin moved >500bps sequentially, say so loudly in the run report.
- Append the print to `per-stock/{TICKER}/news-log.md` (rule 6).

**Phase 2 — re-score (evening of the reaction day), per `rescore_due` name:**
- Objective-input refresh for those tickers
  (`refresh_objective_inputs.py`, the same chain `/refresh-objective` drives),
  plus `momentum_50dma.py {tickers}` and `refresh_reverse_dcf.py`.
- `recalc_watchlist.py --sync` — which per rule 25 auto-chains
  `refresh_targets`; a membership or held-tier change fires a model event and
  mechanical ticket generation (rule 29).
- Flags, not auto-fixes: Layer-9 capacity-cohort names (EV/MW denominator
  needs human-researched MW data, rule 13) and TTM-vs-MRQ divergence >10pts
  on any quality metric (rule 9).

**Git:** before branching, an **unmerged-branch guard**
(`git branch --list 'earnings/*' --no-merged origin/main`) checks for a prior
`earnings/*` branch that never merged; if one exists, the run does not
proceed with any phase — it logs, notifies, and stops. This prevents the
nightly-run/binary-xlsx merge collision that motivated the guard. Otherwise:
branch from origin/main (fetch first — branching discipline), commit, push,
PR; on the known headless PR/push blocks, leave the branch + write the run
report and flag it (weekly-refresh fallback behavior).

**Run report:** append a dated section to
`tracking/earnings-sentinel-log.md` — names briefed, names re-scored, score
deltas, whether a model event fired, all flags. On a fired model event or any
refusal (see §7), also send a macOS notification (best-effort osascript, same
pattern as `executor_cron.macos_notify`).

## 6. End-to-end timeline

| Report slot | Print | Briefing | Re-score (post-reaction close) | Trade (executor 06:35 PT) | Print→trade |
|---|---|---|---|---|---|
| Before open (≈⅓ of names) | Wed 07:00 | Wed 18:30 | Wed 18:30 (same run) | Thu 09:35 ET | ~26h |
| After close (≈⅔) | Tue 16:30 | Tue 18:30 | Wed 18:30 | Thu 09:35 ET | ~41h |

Versus up to ~6 days on the weekly cycle. Tickets are generated ~15h before
the executor window — comfortably inside the 48h default TTL
(`trade_ticket.py DEFAULTS`).

## 7. Execution seam (no new execution code)

The sentinel session — like every Claude session — **never calls an order or
write tool** (rule 29; platform rule). The chain it plugs into already exists
and is live-proven:

sentinel re-score → `recalc --sync` → `refresh_targets` model event →
mechanical ticket (`generate_trade_ticket.py`) → **Dom-activated**
`executor_cron.py` (launchd `com.dom.aistocks.executor`, weekdays 06:35 PT)
validates the full C2 gate set and transmits — with notification on every
attempt, auto-halt on any validation failure, and no auto-execution of
full-turnover tickets.

**Stale-recon refusal is surfaced, not worked around:** ticket generation
computes share deltas from the latest recon snapshot, and reconciliation only
runs in attended sessions (MCP OAuth does not survive headless runs). If a
model event fires but ticket generation refuses on a missing/stale snapshot,
the sentinel reports it and notifies — the correct outcome is Dom opens a
session, runs recon, and regenerates; never a ticket built on assumed
holdings.

## 8. Known limitations (stated, not hidden)

- **Statement lag:** Yahoo ingests new quarterly statements 1–3 days after the
  release. The reaction-day re-score is fully fresh on price-driven inputs;
  statement-driven inputs (margins, ROIC, growth) may still reflect the prior
  quarter until Yahoo catches up. The weekly scan remains the catch-all that
  sweeps this (rule 9 unchanged). A per-name "statements still stale" re-check
  loop was considered and rejected as gold-plating.
- **yfinance earnings dates** are occasionally missing or wrong even for
  liquid names (dates also shift when companies reschedule). The sentinel
  re-reads the calendar every run, flags gaps, and the weekly cadence
  backstops misses.
- **Turnover pressure:** more scoring passes → more chances to cross the
  15/18 rank boundary during earnings season. The hysteresis band, 2-run exit
  clock, and within-tier freeze already dampen this; more tickets in earnings
  season is the design working, and each still passes the executor's caps.

## 9. Testing

Unit tests on the pure logic, no network in the test path (CI minimal-env:
yfinance imported lazily, fixtures fictional per the no-real-identifiers
rule):
- Scope construction: holdings ∪ top-25-tradable from fixture score-history
  rows; foreign suffix exclusion.
- Reaction-day computation: BMO / AMC / missing-timestamp cases; weekend and
  holiday rollover to next trading day.
- Due-event selection: idempotency against state (briefed but not re-scored;
  both done; failed-run retry); a rescheduled earnings date superseding a
  stale one.

## 10. CLAUDE.md

Implementation adds a rule ("Earnings sentinel") recording: scope rule
(holdings ∪ top-25 tradable), the two-phase trigger, the state file, that the
weekly scan remains the rule-9 catch-all, and the §7 seam restatement. The
build-the-invocation principle: the trigger ships with the logic in the same
change.
