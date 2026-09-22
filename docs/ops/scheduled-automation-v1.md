# Scheduled automation and generated-data ownership — v1

Status: implementation proposed in PR; no Hermes jobs or GitHub settings are activated by this document.

## Safety boundary

V1 automation detects, validates, reports, and moves one deterministic generated file through a protected pull request. It does not perform company research, make discretionary rating or trade decisions, generate order tickets, load launchd, or access live-order execution.

## Single-writer ownership

| Artifact or state | Sole owner | Write path |
|---|---|---|
| `tracking/performance-series.json` | GitHub `Daily site refresh` | stable `automation/performance-series` PR only |
| deployed `site/data/` output | `Deploy portfolio site` | Pages artifact only; not committed |
| Hermes heartbeat/dedup state | proposed Hermes script-only jobs | `$HERMES_HOME/data/ai-stocks-scheduled-ops/state.json` only |
| `tracking/earnings-sentinel-state.json` | attended legacy-compatible marking command | report-only jobs read it and never call `--mark` |
| workbook, score history, ratings, targets, tickets | attended engineering/research workflows | no unattended V1 owner |
| per-stock research/context/news files | attended research workflows | no unattended V1 owner |

The paused launchd 06:35 executor remains a separate live-order path and is not loaded or called. The obsolete 13:35 local performance writer was removed in PR 72.

## Daily deterministic generated-data PR

`Daily site refresh` checks out a fresh hosted runner at `main`, generates only `tracking/performance-series.json`, runs the full `tests` suite, and asks `scripts/generated_data_pr.py` for a mutation-free plan.

Stable branch: `automation/performance-series`.

Allowed PR scope: exactly `tracking/performance-series.json`.

Planner behavior:

- no branch and no PR: create one;
- one owned PR with different deterministic content: update it with `--force-with-lease` pinned to the fetched commit;
- one owned PR with identical content: wait without another push;
- orphan branch, multiple PRs, wrong base/head, unexpected files, `DIRTY`/`BLOCKED` merge state, or failed required check: stop loudly;
- a successful update enables squash auto-merge, which waits for branch protection's required `test` check.

The workflow no longer pushes `main` or deploys Pages inline. The PAT-authored merge to `main` triggers the existing `Deploy portfolio site` push workflow.

### Why a dedicated token is required

Events produced by the default `GITHUB_TOKEN` normally do not recursively trigger other workflows. A PR created or updated only by that token can therefore remain without the required `test` run. Use a repository-only fine-grained PAT so the generated PR triggers ordinary `pull_request` CI. Never grant brokerage, organization, or unrelated repository access.

Proposed secret:

- name: `AI_STOCKS_AUTOMATION_TOKEN`
- resource owner: Dom's GitHub account
- repository access: only `dgaraventa5/ai-stocks`
- repository permissions: Metadata read, Administration read, Contents read/write, Pull requests read/write
- expiration: 90 days or the shortest operationally acceptable interval

The workflow's own `GITHUB_TOKEN` remains `contents: read`.

## Exact proposed GitHub settings

Apply only after separate approval and before merging/activating this workflow:

1. Repository setting `allow_auto_merge=true`.
2. Repository setting `delete_branch_on_merge=true`.
3. Add secret `AI_STOCKS_AUTOMATION_TOKEN` with the scope above.
4. Protect `main` with:
   - require pull requests before merging;
   - required status check context: `test`;
   - require branches to be up to date before merging (`strict=true`);
   - no required human approval for the generated-data bot path;
   - enforce protections for administrators;
   - disallow force pushes;
   - disallow deletions;
   - do not grant bypass to the token owner or GitHub Actions.
5. Keep default workflow permissions read-only. Do not enable GitHub Actions approval of PRs; this design does not depend on bot approval.

If policy later requires a human approval, remove automatic merge from the daily workflow and accept that daily publication waits for attended approval.

## Hermes report-only replacements

Canonical paused definitions: `automation/hermes/cron-definitions.json`.

| Job | Schedule (host local time) | Mode | Bound | Delivery |
|---|---:|---|---:|---|
| `ai-stocks-weekly-rating-report` | `0 10 * * 1` | script-only, no agent | 60 s; 2 items | Telegram |
| `ai-stocks-earnings-sentinel-report` | `30 18 * * 1-5` | script-only, no agent | 150 s; 2 items | Telegram |
| `ai-stocks-ops-health` | `0 8 * * *` | script-only, no agent | 60 s; 10 alerts | Telegram |

Hermes has a three-minute per-run hard interrupt. Each wrapper sets an equal or tighter subprocess timeout. `no_agent=true` means zero model calls, zero model tokens, and no agent tool access. Expected model cost is $0 per run; only local CPU and the existing earnings calendar/price network reads are used.

Versioned wrappers live in `automation/hermes/`. At activation, copy—not symlink—them into the active profile's `$HERMES_HOME/scripts/`, because cron scripts must resolve inside that directory:

- `ai-stocks-weekly-rating-report.py`
- `ai-stocks-earnings-sentinel-report.py`
- `ai-stocks-ops-health.py`

No cron jobs have been created. Definitions remain `paused: true` until a separately approved activation.

## Deterministic state and deduplication

Every report has `schema_version: 1`, a stable report kind, bounded sorted items/alerts, overflow counts, `report_only: true`, and a SHA-256 `dedup_key` over canonical semantic content. Wall-clock generation time is excluded from the key.

After a successful script run, an atomic local state write records `last_success_at`, status, and dedup key. Identical actionable output is silent. Quiet output is silent but still refreshes the heartbeat. The repo, workbooks, scoring data, and sentinel completion state are not touched.

Health thresholds:

- weekly rating heartbeat: stale after 192 hours;
- earnings sentinel heartbeat: stale after 48 hours;
- generated-data PR: stale after 6 hours;
- failed/cancelled/timed-out checks and `DIRTY`/`BLOCKED` PRs alert immediately.

## Isolation and existing PR handling

- GitHub generation uses an ephemeral hosted checkout and the dedicated stable automation branch.
- Report-only Hermes jobs make no branch and need no worktree because they have no repository write path.
- Any future mutating agent workflow is outside V1 and must use a new branch/worktree from current `origin/main`, enumerate open/conflicting PRs first, and stop rather than overlap an unmerged writer.
- Existing `earnings/*`, `refresh/ratings*`, or `automation/*` PRs are surfaced by the health report; V1 report jobs never modify them.

## Fixture proof

All proofs use synthetic fixtures and temporary local state; no market/order path runs and no financial methodology changes.

- Weekly first run: two items plus overflow, 0.07 s; identical second run: 0 output bytes.
- Earnings first run: two combined events, bounded flag plus overflow, 0.04 s; identical second run: 0 output bytes.
- Health run: emitted `stale_run`, `stale_pr`, `failed_check`, and `blocked_pr`, 0.04 s.

Fixtures: `tests/fixtures/scheduled_ops/`.

## Legacy Claude ownership

`weekly-rating-refresh` and `earnings-sentinel` remain disabled. Their mutating ownership is retired only after the fixture proof above and the regression suite pass. The local task records are retained as disabled tombstones for rollback/history; they must not be re-enabled alongside Hermes.

## Activation checklist

1. Review and merge the implementation PR.
2. Obtain separate approval for GitHub settings and cron activation.
3. Create the scoped PAT and repository secret; verify its expiration reminder.
4. Apply the exact branch protection and auto-merge settings above.
5. Manually dispatch `Daily site refresh` once. Verify one scoped PR, `test` success, auto-merge, and subsequent `Deploy portfolio site` success.
6. Copy wrappers into the active profile's `$HERMES_HOME/scripts/`.
7. Register all three Hermes jobs paused from `cron-definitions.json`.
8. Run each paused job once with fixture inputs or an equivalent copied dry-run wrapper; inspect delivery and heartbeat state.
9. Confirm Claude tasks are still disabled, launchd is still unloaded, and `cronjob list` contains no duplicate owner.
10. Resume weekly and earnings report jobs first; resume health after both have established heartbeats. Never resume Claude counterparts.

## Rollback

1. Pause all three Hermes jobs; do not enable Claude automatically.
2. Disable the `Daily site refresh` schedule or remove `AI_STOCKS_AUTOMATION_TOKEN` to fail closed.
3. Close (do not merge) any open `automation/performance-series` PR after preserving its URL and diff.
4. Revert the implementation PR on a new branch and run the full suite.
5. Remove branch-protection/settings changes only with separate approval; never bypass the `test` gate to restore direct pushes.
6. Restore legacy task text only from Git history or the migration backup, keep it disabled, and seek a new equivalence review before any activation.
