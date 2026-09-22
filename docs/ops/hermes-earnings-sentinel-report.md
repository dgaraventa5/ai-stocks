# Hermes earnings-sentinel report — v1

Status: proposed, not registered. The legacy Claude task remains disabled.

Owner: proposed Hermes script-only job `ai-stocks-earnings-sentinel-report`.

Schedule: weekdays 18:30 local time (`30 18 * * 1-5`).

Source command:

    .venv/bin/python scripts/scheduled_ops.py earnings-sentinel --limit 2

Contract:

- Reuse the existing detection-only `earnings_sentinel` functions.
- Read the current scope, earnings calendar, latest close dates, and existing sentinel state.
- Emit at most two ticker/report events with `briefing` and/or `rescore` phases, bounded flags, overflow counts, and a stable SHA-256 dedup key.
- Do not call `--mark`; report-only runs never claim a briefing or rescore completed.
- Write only the local Hermes heartbeat/dedup state under `$HERMES_HOME/data/ai-stocks-scheduled-ops/`.
- Never create context briefings, change ratings or scores, edit workbooks, create branches or PRs, generate tickets, access brokerage tools, or invoke order execution.
- Empty or duplicate output is silent in Hermes no-agent mode.
- A non-zero script exit is an alert.

The report tells Dom which attended workflow is due. It does not perform financial analysis or trade execution.
