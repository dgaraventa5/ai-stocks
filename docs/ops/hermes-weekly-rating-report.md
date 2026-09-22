# Hermes weekly rating-integrity report — v1

Status: proposed, not registered. The legacy Claude task remains disabled.

Owner: proposed Hermes script-only job `ai-stocks-weekly-rating-report`.

Schedule: Monday 10:00 local time (`0 10 * * 1`).

Source command:

    .venv/bin/python scripts/scheduled_ops.py weekly-rating --limit 2

Contract:

- Read the scoring workbook, rating audit, thesis files, and context briefings through `audit_rating_integrity.audit()`.
- Emit at most two deterministic candidates, prioritizing gate violations and then the stalest review evidence.
- Include an overflow count and stable SHA-256 dedup key.
- Write only the local Hermes heartbeat/dedup state under `$HERMES_HOME/data/ai-stocks-scheduled-ops/`.
- Never research companies, change ratings, edit the workbook, create branches or PRs, use brokerage tools, or invoke order execution.
- Empty or duplicate output is silent in Hermes no-agent mode.
- A non-zero script exit is an alert.

The report is a queue/approval signal for a later attended research session. It is not a replacement for human-reviewed research or rating decisions.
