# Daily site refresh — design

**Date:** 2026-06-11
**Status:** Approved by Dom (2026-06-11)

## Problem

The portfolio site's dashboard and performance pages show data derived from
`tracking/performance-series.json`, which is only refreshed by the weekly
Cowork routine, and the site only redeploys on push to `main`. Friends see
up-to-week-old numbers. The data model already carries everything needed for
daily benchmark comparisons (model vs SMH / QQQ / SPY / EW); freshness is
purely a scheduling problem.

## Decision

A daily GitHub Actions cron workflow refreshes the performance series,
commits it if changed, and redeploys the site — no dependency on Dom's Mac,
no token-billed agent for a deterministic script.

Alternatives considered: launchd on the Mac (silently stale when the laptop
is closed), daily scheduled Claude routine (heavyweight for a script that
needs no judgment).

## Components

### 1. `scripts/track_performance.py` — `--series-only` flag

Calls `build_daily_series(cfg)` and exits. Does NOT append to
`tracking/performance-log.md` — the narrative log stays on its weekly
cadence via the unchanged Cowork routine.

### 2. `.github/workflows/daily-refresh.yml` (new)

Triggers: `schedule: '45 21 * * 1-5'` (≈5:45pm ET during EDT, 4:45pm ET
during EST — both after close with adjusted closes settled) plus
`workflow_dispatch` for manual end-to-end validation.

Steps:
1. Checkout, setup Python 3.12, `pip install yfinance pandas openpyxl pytest`.
2. `python scripts/track_performance.py --series-only` wrapped in a retry
   loop: 3 attempts, 60s apart (Yahoo throttles shared runner IPs).
3. If `tracking/performance-series.json` is unchanged per `git diff`, exit 0
   without committing. This naturally skips market holidays: `as_of` is
   stamped from the last trading date in the data, not wall-clock, so a
   holiday rebuild is byte-identical.
4. Bot commit `chore(data): daily performance series YYYY-MM-DD`, push to
   `main`.
5. Run the deploy pipeline inline: `pytest tests -q` →
   `scripts/export_site_data.py` → `scripts/check_site.py` → wrangler pages
   deploy. Inline because `GITHUB_TOKEN` pushes deliberately don't trigger
   other workflows; `deploy-site.yml` stays untouched for normal pushes.

Needs `permissions: contents: write` and reuses the existing
`CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` secrets.

## Error handling

Fail loudly, degrade gracefully: if all 3 yfinance attempts fail, the
workflow fails and GitHub notifies Dom; the site keeps serving yesterday's
data (correct-but-stale, never broken). No silent fallback data source, per
CLAUDE.md "flag, don't assume". The privacy boundary is unchanged — the
exporter remains the only path from repo data to `site/data/`, and the
existing privacy regression test still gates every deploy.

## Out of scope

- Position-level live prices on the positions page — weights/notionals there
  are rebalance targets by design, not daily marks.
- Any change to `deploy-site.yml`, the weekly log cadence, or the
  performance data model (SMH/QQQ/SPY/EW already present).

## Testing

- Unit test: `--series-only` leaves `performance-log.md` untouched (build
  function stubbed; no network in tests).
- Existing exporter/privacy suite continues to gate the deploy step.
- One manual `workflow_dispatch` run validates the workflow end-to-end
  before trusting the cron.
