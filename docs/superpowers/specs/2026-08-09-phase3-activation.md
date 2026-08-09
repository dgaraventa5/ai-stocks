# Phase-3 activation decision — scheduled executor (§C5)

**Date:** 2026-08-09
**Decision owner:** Dom
**Status:** BUILT, NOT ACTIVE — activation is a single Dom-run `launchctl load`

## Decision (Rating-Audit spirit: dated, reasoned, reversible)

Dom requested Phase 3 (zero-touch scheduled execution) be built ahead of the
spec's recommended gate (≥3 months / ≥6 tickets / zero validation failures /
zero recon anomalies in Phase 2). Claude's stated position, logged per the
collaboration model: **build yes, activate not yet** — the manual command is
the cheapest circuit breaker available and the codebase is one day old.
Building now, activating later, keeps the decision reversible in both
directions.

## What activation changes

- `launchd/com.dom.aistocks.executor.plist` runs `scripts/executor_cron.py`
  weekdays 06:35 PT. It picks the newest unexecuted, unexpired ticket and runs
  the executor with `--confirm` — no human eyeball between model event and
  order transmission.
- **C5 safety posture switches on:** macOS notification on every execution
  attempt; ANY validation failure auto-raises `trading-halt.flag` (not just
  investigate-later flags); full-turnover tickets are never auto-executed
  (the wrapper deliberately omits `--allow-full-turnover`, so a full redeploy
  still requires Dom's terminal).
- Post-send reconciliation runs immediately via the transport's READ methods
  (fill verification, anomaly halt, sanitized status). Known O1 caveat: the
  Keychain token may be stale in headless context — a token failure notifies
  and sends nothing (fails safe, never halts, never guesses).

## Activation (Dom only)

```bash
cp launchd/com.dom.aistocks.executor.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.dom.aistocks.executor.plist
```

## Rollback

```bash
launchctl unload ~/Library/LaunchAgents/com.dom.aistocks.executor.plist
```

…or create `tracking/live/trading-halt.flag` (halts all execution while the
schedule keeps ticking — useful for a pause rather than a teardown).

## Boundary unchanged

Claude never calls order tools and never loads/unloads this agent (CLAUDE.md
rule 29). The scheduled path is Dom's own script on Dom's own machine; the
executor remains the only order writer.
