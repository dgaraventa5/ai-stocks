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

The workflow never pushes `main`. It uses only the job-scoped, same-repository `GITHUB_TOKEN`; no personal OAuth token, PAT, GitHub App secret, or external repository is involved.

### Built-in token recursion design

GitHub normally suppresses workflow recursion for events created by `GITHUB_TOKEN`, and a token-authored pull request's ordinary `pull_request` run requires manual approval. GitHub documents two exceptions that always create runs: `workflow_dispatch` and `repository_dispatch`. V1 uses `workflow_dispatch` because it accepts an exact branch ref and GitHub defines its `GITHUB_SHA` as the last commit on that ref.

After creating or updating the PR, the daily workflow:

1. reads the PR's exact `headRefOid`;
2. dispatches `ci.yml` on `automation/performance-series` through the REST API;
3. verifies the returned run is `workflow_dispatch`, has that exact head SHA, and contains a successful job named `test`;
4. re-verifies the PR head did not move;
5. enables squash auto-merge;
6. verifies the merge commit is current `main`;
7. explicitly dispatches and waits for `deploy-site.yml` on that merge SHA, because a `GITHUB_TOKEN` merge does not recursively trigger the normal `push` deployment.

`ci.yml` ignores the sole generated path for ordinary `pull_request` triggering, avoiding an approval-required duplicate run, but retains normal PR CI for every other change. The explicit dispatch supplies the same required `test` context from the GitHub Actions app on the PR head commit.

Official behavior:

- https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event

Workflow permissions are explicit and job-scoped: `actions: write` for the two dispatches, `contents: write` for the automation branch and merge, and `pull-requests: write` for PR creation/auto-merge. Repository defaults stay read-only. The complete refresh is capped at 30 minutes.

## Exact proposed GitHub settings

Apply only after separate approval, in one cutover window:

1. Keep default workflow permissions read-only and allow GitHub Actions to create pull requests. GitHub's combined setting also says “approve,” but this workflow never calls review approval and branch protection grants no bypass.
2. Set `allow_auto_merge=true` and `delete_branch_on_merge=true`.
3. Protect `main` with:
   - require pull requests before merging;
   - required status check context: `test`;
   - require branches to be up to date (`strict=true`);
   - zero required human approvals for this deterministic path;
   - enforce protections for administrators;
   - disallow force pushes and deletions;
   - do not grant any bypass actor.
4. Arm the workflow only after verifying those settings by setting the non-secret repository variable `AUTOMATION_CUTOVER_ENABLED=true`. The job-scoped `GITHUB_TOKEN` cannot request Administration permission to introspect repository settings, so this explicit gate prevents pre-cutover runs; PR creation, dispatch SHA checks, auto-merge, and deployment checks then fail closed at runtime.

Exact setting commands (do not run before approval):

    gh api --method PUT \
      repos/dgaraventa5/ai-stocks/actions/permissions/workflow \
      -f default_workflow_permissions=read \
      -F can_approve_pull_request_reviews=true

    gh api --method PATCH repos/dgaraventa5/ai-stocks \
      -F allow_auto_merge=true \
      -F delete_branch_on_merge=true

    gh api --method PUT \
      repos/dgaraventa5/ai-stocks/branches/main/protection \
      --input - <<'JSON'
    {
      "required_status_checks": {"strict": true, "contexts": ["test"]},
      "enforce_admins": true,
      "required_pull_request_reviews": {
        "dismiss_stale_reviews": false,
        "require_code_owner_reviews": false,
        "required_approving_review_count": 0,
        "require_last_push_approval": false
      },
      "restrictions": null,
      "required_linear_history": true,
      "allow_force_pushes": false,
      "allow_deletions": false,
      "block_creations": false,
      "required_conversation_resolution": false,
      "lock_branch": false,
      "allow_fork_syncing": false
    }
    JSON

    gh api repos/dgaraventa5/ai-stocks/actions/permissions/workflow
    gh api repos/dgaraventa5/ai-stocks \
      --jq '{allow_auto_merge,delete_branch_on_merge}'
    gh api repos/dgaraventa5/ai-stocks/branches/main/protection \
      --jq '{required_status_checks,enforce_admins,required_pull_request_reviews,allow_force_pushes,allow_deletions}'

    gh variable set AUTOMATION_CUTOVER_ENABLED \
      --repo dgaraventa5/ai-stocks --body true

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

1. Obtain separate approval for the GitHub settings and cron activation.
2. Merge the implementation PR. The new daily workflow fails closed until all settings below are applied.
3. In the same cutover window, apply the exact Actions, auto-merge, branch deletion, and branch-protection commands above. No secret is created.
4. Manually dispatch `Daily site refresh` once:

       gh workflow run daily-refresh.yml --ref main
       run_id=$(gh run list --workflow daily-refresh.yml --event workflow_dispatch \
         --limit 1 --json databaseId --jq '.[0].databaseId')
       gh run watch "$run_id" --exit-status

5. Verify the workflow-created PR head received a successful `test` check from the explicit dispatch, auto-merged, and explicitly dispatched a successful deployment:

       gh pr list --state all --head automation/performance-series \
         --limit 1 --json number,state,headRefOid,mergeCommit,url
       gh run list --workflow ci.yml --event workflow_dispatch --limit 5 \
         --json databaseId,headSha,status,conclusion,url
       gh run list --workflow deploy-site.yml --event workflow_dispatch --limit 5 \
         --json databaseId,headSha,status,conclusion,url

6. Copy wrappers into the active profile's `$HERMES_HOME/scripts/`.
7. Register all three Hermes jobs paused from `cron-definitions.json`.
8. Run each paused job once with fixture inputs or an equivalent copied dry-run wrapper; inspect delivery and heartbeat state.
9. Confirm Claude tasks are still disabled, launchd is still unloaded, and `cronjob list` contains no duplicate owner.
10. Resume weekly and earnings report jobs first; resume health after both have established heartbeats. Never resume Claude counterparts.

## Rollback

1. Pause all three Hermes jobs; do not enable Claude automatically.
2. Set `AUTOMATION_CUTOVER_ENABLED=false`, then disable `Daily site refresh`; there is no personal credential or secret to revoke.
3. Close (do not merge) any open `automation/performance-series` PR after preserving its URL and diff.
4. Revert the implementation PR on a new branch and run the full suite.
5. Remove branch-protection/settings changes only with separate approval; never bypass the `test` gate to restore direct pushes.
6. Restore legacy task text only from Git history or the migration backup, keep it disabled, and seek a new equivalence review before any activation.
