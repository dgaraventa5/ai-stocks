# Exit-pending clock persistence: make the 2-run exit hysteresis actually run

**Date:** 2026-08-02
**Status:** Approved by Dom (Option A + param revert), 2026-08-02
**Author:** Dom + Claude

## Problem

The EXIT PENDING two-run confirmation clock is persisted only in the Targets
sheet's Status column, but the freeze-snapshot gating (2026-06-29 design) rewrites
that sheet only when a rebalance fires (membership or held-tier change). A holding
that drifts below the exit score **without** a tier crossing stays in `include`
(that is the hysteresis working), so membership doesn't change, `fire` stays
False, and the freshly computed `EXIT PENDING (since …)` status is printed to
stdout and discarded at the `if not fire:` early return
(`refresh_targets.py:337`). Every run restarts the clock; the exit can never
confirm while snapshots stay frozen.

Observed live 2026-08-02: GOOGL (72.4), META (73.3), AMZN (72.8) all flagged
EXIT PENDING against the then-live exit score 74.5 while the committed Targets
sheet showed Status=HOLD from 2026-07-16 for all three.

Two aggravating gaps:

- **The rule-25 gate is blind to it.** `pending_rebalance()` keys off `fire`, so
  the CI/test gate stays green while holdings sit below the exit bar with a
  stalled clock.
- **Zero test coverage** of the exit-hysteresis path (`EXIT PENDING` appeared
  only in `refresh_targets.py` itself).

Root cause is the same class as the MU tier/weight inversion the 2026-06-29
design fixed: cross-run state stored in a display artifact (the sheet) that the
model of record (`tracking/performance-config.json`) doesn't know about. That
spec already ruled the sheet "not a trustworthy baseline" and moved the tier
baseline to the config — the pending clock never got the same treatment. Its
edge-case analysis covered "below-exit holding **+ tier crossing** in one
window" but missed below-exit with nothing else changing, which is the common
case.

## Decisions (Dom, 2026-08-02)

1. **Option A:** the pending clock moves into `tracking/performance-config.json`
   as a top-level `exit_pending: {ticker: since-date}` map. The Targets sheet
   Status column becomes display-only, written at rebalances.
2. **Params revert:** Sizing Rules entry/exit revert from 76/74.5 (the
   2026-06-18 concentration experiment, commit `923d87f`) to **74.5/73.0** "for
   now". This makes CLAUDE.md rule 20's "(74.5/73.0)" parenthetical and the
   `NEW_PARAMS` code defaults correct again; the sheet remains the authoritative
   source for live params.
3. **Sequencing:** no `--resize`. The revert makes EME (74.8 ≥ 74.5) enter on
   the next real run (entry has no hysteresis → membership change → snapshot
   rewrite); AMZN (72.8) and GOOGL (72.4) start persisted exit clocks and
   confirm on the next real run on a later day; META (73.3 ≥ 73.0) holds.

## Design

### State

`tracking/performance-config.json` gains a top-level map:

```json
"exit_pending": {"AMZN": "2026-08-02", "GOOGL": "2026-08-02"}
```

Transient hysteresis state, not an event — it does not belong in `events[]`.
`refresh()` reads it via `load_cfg()` (moved above the membership pass) and no
longer parses `EXIT PENDING` out of the sheet's Status column (that parse is
deleted; the current sheet carries no pending statuses, so there is nothing to
migrate).

### Transitions (real runs only)

- **Below exit, no clock** → add `{ticker: today}`; status
  `EXIT PENDING (score …, since <today>)`; name stays in `include`.
- **Below exit, clock from a prior date** → EXIT confirmed (membership change →
  `fire`); entry removed. Same-day re-runs still don't confirm — the confirm
  requires two independent data points, not two invocations.
- **Recovered above exit** → entry removed (clock resets; existing semantics).
- **Exited via resize / dead / override** → entry removed.

### Persistence rules

- **Firing run:** `cfg['exit_pending'] = new_pending` is set before
  `log_rebalance(cfg, …)`, which already saves the whole config — one write.
- **Frozen run:** if the map changed, save only the config
  (`save_cfg(cfg)`); the workbook is not touched — frozen runs stay
  byte-identical on the xlsx, preserving the freeze-snapshot invariant.
- **Dry runs** (`--dry-run`, `pending_rebalance()`, the rule-25 gate, tests)
  **never mutate the map** — the gate must be able to probe repeatedly without
  advancing clocks.

### Enforcement falls out naturally

Once a clock is a day old and the name is still below exit, a dry run computes
the confirmed exit → `exited` non-empty → `fire=True` →
`refresh_targets.py --check` and `test_targets_reflect_current_scores` fail
until the real run executes the exit. The gate that was blind to a stalled exit
now forces the confirming leg. Consequence to know: after a clock starts, the
suite goes red the **next day** until the confirm run is committed — rule 25
working as designed.

### Non-goals

- No change to the confirm semantics (2 runs on distinct dates; `--resize`
  bypasses; recovery resets the clock).
- No change to tier bands, sizing, or the freeze-snapshot write gating for the
  workbook.
- `Exit confirm runs` param stays cosmetic (the 2-run semantic is structural);
  not wired up here.
- Not surfaced on the friend-facing site (exporter validates the Status header
  but never reads its values — verified).

## Testing

Extending `tests/test_refresh_targets.py` fixtures (`_build_portfolio` /
`_mock_env`; `_mock_env` additionally stubs `save_cfg` so tests can't write the
real config):

- Clock starts and persists to config on a frozen run; workbook byte-identical;
  no rebalance event.
- Prior-date clock + still below → exit confirms, one event logged, map entry
  cleared, Targets rewritten with the name excluded.
- Same-day clock → no confirm, no redundant config write.
- Recovery above exit clears the clock (config saved, workbook frozen).
- Dry run / `pending_rebalance()` never mutate the map.
- `pending_rebalance()` is True when a confirm is due.

## Files touched

- `scripts/refresh_targets.py` — read/maintain/persist `exit_pending`; delete
  the Status-column parse; docstring.
- `tests/test_refresh_targets.py` — six new tests + `save_cfg` stub in
  `_mock_env`.
- `00-master/portfolio.xlsx` Sizing Rules — entry/exit 76/74.5 → 74.5/73.0
  (note records both changes).
- `CLAUDE.md` — new rule 26 (this design + param history); correction note on
  rule 20's parenthetical.
- `tracking/performance-config.json` + `00-master/portfolio.xlsx` Targets —
  output of the post-revert real run (+EME; AMZN/GOOGL clocks started).
