# Legacy Claude earnings-sentinel task — retired ownership

Status: disabled and superseded after fixture equivalence proof. Do not register or enable a task from this file.

The former Claude task combined detection, research, rescoring, workbook writes, branch creation, pushes, PR creation, and ticket-producing model events. That scope is intentionally not transferred to unattended Hermes automation.

Replacement report contract:

- `docs/ops/hermes-earnings-sentinel-report.md`
- `scripts/scheduled_ops.py earnings-sentinel --limit 2`
- proposed paused definition: `automation/hermes/cron-definitions.json`

The replacement is report-only. It does not mark events complete, modify financial/scoring artifacts, create branches or PRs, generate tickets, or access live-order execution. Attended workflows remain separately approved.

Historical task text is preserved in Git history and the migration backup.
