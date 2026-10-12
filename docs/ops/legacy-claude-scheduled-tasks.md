# Legacy Claude scheduled tasks

> **Superseded 2026-10-12 (CLAUDE.md rule 37).** The two legacy task IDs below stay disabled. Their work now runs as three new local tasks — `ai-stocks-daily-watch`, `ai-stocks-weekly-scan`, `ai-stocks-rating-research` — described in `docs/ops/scheduled-runs.md`. The Hermes report-only jobs were never activated and remain paused.

Both local Claude task records remain present but disabled. They must not be re-enabled after the Hermes report-only jobs are activated.

| Legacy task | Schedule | State | Replacement |
|---|---:|---|---|
| `weekly-rating-refresh` | `0 10 * * 1` | disabled | `ai-stocks-weekly-rating-report` |
| `earnings-sentinel` | `30 18 * * 1-5` | disabled | `ai-stocks-earnings-sentinel-report` |

The legacy tasks owned mutating research, workbook, branch, push, and PR behavior. V1 Hermes replacements deliberately do not: they are bounded report-only signals with zero LLM tokens and no live-order capability. Attended follow-up remains separate.

Equivalence boundary proven by fixture runs:

- stale/gate candidates are detected, prioritized, bounded, and deduplicated;
- earnings briefing/rescore events and lookup failures are detected, bounded, and deduplicated;
- stale heartbeats, failed checks, stale PRs, and conflicting PRs generate alerts;
- duplicate reports produce zero output;
- no repository or financial artifact is changed.

Original task text remains recoverable from Git history and the migration backup at `/Users/dom/Hermes/scratch/migration-backup/ai-stocks-20260922-133821-PDT`.
