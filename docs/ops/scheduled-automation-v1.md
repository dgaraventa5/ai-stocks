# Scheduled automation and generated-data ownership — v1

Status: implementation proposed in PR; no Hermes jobs or GitHub settings are activated by this document.

## Safety boundary

V1 automation detects, validates, reports, and moves one deterministic generated file through a protected pull request. It does not perform company research, make discretionary rating or trade decisions, generate order tickets, load launchd, or access live-order execution.

## Single-writer ownership

| Artifact or state | Sole owner | Write path |
|---|---|---|
| `tracking/performance-series.json` | GitHub `Daily site refresh` | stable `automation/performance-series-v2` PR only |
| deployed `site/data/` output | `Deploy portfolio site` | Pages artifact only; not committed |
| Hermes heartbeat/dedup state | proposed Hermes script-only jobs | `$HERMES_HOME/data/ai-stocks-scheduled-ops/state.json` only |
| `tracking/earnings-sentinel-state.json` | attended legacy-compatible marking command | report-only jobs read it and never call `--mark` |
| workbook, score history, ratings, targets, tickets | attended engineering/research workflows | no unattended V1 owner |
| per-stock research/context/news files | attended research workflows | no unattended V1 owner |

The paused launchd 06:35 executor remains a separate live-order path and is not loaded or called. The obsolete 13:35 local performance writer was removed in PR 72.

## Daily deterministic generated-data PR

`Daily site refresh` checks out a fresh hosted runner at `main`, generates only `tracking/performance-series.json`, runs the full `tests` suite, and asks `scripts/generated_data_pr.py` for a mutation-free plan.

Stable branch: `automation/performance-series-v2`. Preserve the original `automation/performance-series` branch and PR 74 as evidence until the recovery PR is merged, then close PR 74 without merging it.

Allowed PR scope: exactly `tracking/performance-series.json`.

Planner behavior:

- no branch and no PR: create one;
- one owned PR with different deterministic content: update it with `--force-with-lease` pinned to the fetched commit;
- one owned PR with identical content: wait without another push;
- orphan branch, multiple PRs, wrong base/head, unexpected files, `DIRTY`/`BLOCKED` merge state, or failed required check: stop loudly;
- a successful update enables squash auto-merge, which waits for branch protection's required `test` check.

The workflow never pushes `main` directly and does not use a PAT or branch-protection bypass.

### Failed built-in-token proof and root cause

The first live proof created PR 74 at `11c311cfb1c6b8fe88bf6c31e79dd756bd2f19d2`. Workflow-dispatch run 35793381910 completed job `test` successfully on that exact SHA through GitHub Actions app 15368, and REST associated the check run with PR 74. GitHub nevertheless returned an empty PR `statusCheckRollup`, GraphQL returned `statusCheckRollup: null`, and branch protection kept the PR `BLOCKED`.

This is expected GitHub behavior, not a race. GitHub documents that checks created by workflow jobs are evaluated for a pull request only when triggered by `push`, `pull_request`, `pull_request_review`, `pull_request_target`, `deployment`, or `deployment_status`. A `workflow_dispatch` job check does not satisfy a required pull-request check even when it passes on the head SHA. The former `paths-ignore` also prevented the eligible `pull_request` run and left the required check pending.

Source: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks#checks-from-some-workflow-jobs-are-not-evaluated

PR 74 and `automation/performance-series` are not reused or merged. Preserve their identifiers and diff as evidence, then close PR 74 after the recovery PR merges.

### Repository-scoped GitHub App recovery

The least-privilege recovery uses a dedicated GitHub App installed only on `dgaraventa5/ai-stocks`. Its installation token pushes `automation/performance-series-v2` and creates the PR. GitHub's own token documentation identifies a GitHub App installation token as the unattended alternative when a `GITHUB_TOKEN`-authored PR would otherwise require workflow approval.

Source: https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs

The App receives only:

- Metadata: read (implicit);
- Actions: read, to observe required CI and deployment;
- Checks: read, to verify the exact required check run and source app;
- Contents: read/write, to push the automation branch and merge;
- Pull requests: read/write, to create the PR and enable auto-merge.

It receives no Administration, Checks write, Secrets, or bypass permission. Repository branch protection remains strict and unchanged. The workflow's built-in `GITHUB_TOKEN` is reduced to `contents: read`.

After creating or updating the PR, the daily workflow:

1. waits for the ordinary `pull_request` run instead of dispatching CI;
2. requires `gh pr checks --required` to show `test` passing with event `pull_request`;
3. verifies the successful check run came from GitHub Actions app 15368 and is associated with that PR;
4. re-verifies the PR head SHA;
5. enables squash auto-merge with `--match-head-commit`;
6. verifies the App-token merge is current `main`;
7. waits for the normal `push`-triggered deployment and requires it to succeed.

The complete refresh remains capped at 30 minutes.

## Required GitHub App setup

Keep `AUTOMATION_CUTOVER_ENABLED=false` until the recovery PR is merged and every item below is verified.

1. Create a GitHub App named for ai-stocks automation.
2. Grant only Actions read, Checks read, Contents read/write, Pull requests read/write, and Metadata read.
3. Install it only on `dgaraventa5/ai-stocks`; grant no bypass actor in branch protection.
4. Store the App ID as a repository variable and its private key as a repository secret:

       gh variable set AI_STOCKS_AUTOMATION_APP_ID \
         --repo dgaraventa5/ai-stocks --body "$APP_ID"
       gh secret set AI_STOCKS_AUTOMATION_PRIVATE_KEY \
         --repo dgaraventa5/ai-stocks < app-private-key.pem

5. Return the default workflow setting to read-only with Actions PR creation disabled; the App creates PRs:

       gh api --method PUT \
         repos/dgaraventa5/ai-stocks/actions/permissions/workflow \
         -f default_workflow_permissions=read \
         -F can_approve_pull_request_reviews=false

6. Leave strict branch protection, required context `test` from app 15368, auto-merge, and branch deletion unchanged.
7. Set `AUTOMATION_CUTOVER_ENABLED=true` only for the approved proof run.

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

1. Merge the recovery PR with `AUTOMATION_CUTOVER_ENABLED=false`.
2. Close stale PR 74 without merging it; preserve its URL, head SHA, and failed-proof run ID in this document.
3. Create and install the repository-scoped App with exactly the permissions above; set `AI_STOCKS_AUTOMATION_APP_ID` and `AI_STOCKS_AUTOMATION_PRIVATE_KEY`.
4. Verify branch protection is still strict and still requires `test` from GitHub Actions app 15368. Do not add the automation App as a bypass actor.
5. Set `AUTOMATION_CUTOVER_ENABLED=true` only for the approved proof window, then manually dispatch `Daily site refresh` once:

       gh variable set AUTOMATION_CUTOVER_ENABLED \
         --repo dgaraventa5/ai-stocks --body true
       gh workflow run daily-refresh.yml --ref main
       run_id=$(gh run list --workflow daily-refresh.yml --event workflow_dispatch \
         --limit 1 --json databaseId --jq '.[0].databaseId')
       gh run watch "$run_id" --exit-status

6. Verify the new PR uses `automation/performance-series-v2`; PR 74 remains closed with its original head unchanged. Verify `test` is a `pull_request` check associated with the exact head, auto-merge completed, and deployment was a normal `push` run:

       gh pr list --state all --head automation/performance-series-v2 \
         --limit 1 --json number,state,headRefOid,mergeCommit,statusCheckRollup,url
       gh run list --workflow ci.yml --event pull_request --limit 5 \
         --json databaseId,headSha,status,conclusion,url
       gh run list --workflow deploy-site.yml --event push --limit 5 \
         --json databaseId,headSha,status,conclusion,url
       gh pr view 74 --json state,headRefOid,mergeStateStatus,statusCheckRollup,url

7. Immediately reset `AUTOMATION_CUTOVER_ENABLED=false` if any check association, merge, or deployment assertion fails.
8. Hermes cron activation remains a separate project and approval. Do not create or resume any Hermes job as part of this cutover.

## Rollback

1. Set `AUTOMATION_CUTOVER_ENABLED=false`; scheduled/manual runs then fail before App-token creation or checkout.
2. Revoke the repository App installation and delete `AI_STOCKS_AUTOMATION_PRIVATE_KEY` and `AI_STOCKS_AUTOMATION_APP_ID`.
3. Close, but do not merge, any open `automation/performance-series-v2` PR after preserving its URL and diff. Keep already-closed PR 74 closed.
4. Revert the recovery PR on a new branch and run the full suite.
5. Leave branch protection intact; never bypass required `test`, push `main` directly, or restore the ineligible `workflow_dispatch` check design.
6. Keep Claude tasks disabled, launchd unloaded, and Hermes jobs absent.

## 2026-10-06: PR-head lookup raced the push

Three runs (2026-10-03 05:36Z, 2026-10-06 01:43Z and 02:27Z) failed in "Create
or locate generated-data PR" with `PR head <old> does not match planned head
<new>`. The force-push to `automation/performance-series-v2` had succeeded; the
PR API simply had not registered the new head yet, so the single lookup saw the
previous commit. The auto-merge step never ran and PR 90 sat open with the site
series stuck at 2026-10-01.

Fix: the step now polls the PR head for up to about a minute and fails only if
it never equals the planned head. The exact-SHA guarantee is unchanged — a
genuinely unexpected head still stops the run. PR 90 was merged by hand.

