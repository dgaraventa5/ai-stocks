# Daily Site Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A weekday GitHub Actions cron refreshes `tracking/performance-series.json` and redeploys the portfolio site, so the dashboard and performance pages show daily-fresh model-vs-SMH/QQQ/SPY numbers.

**Architecture:** `track_performance.py` gains a `--series-only` mode (rebuild series JSON, no log append). A new workflow `daily-refresh.yml` runs it after market close with yfinance retries, commits the series only if it changed (byte-identical on holidays, so no calendar logic), and runs the existing test → export → check → wrangler deploy steps inline (a `GITHUB_TOKEN` push cannot trigger `deploy-site.yml`).

**Tech Stack:** Python 3.12, yfinance, pytest, GitHub Actions, Cloudflare Pages (wrangler-action).

**Spec:** `docs/superpowers/specs/2026-06-11-daily-site-refresh-design.md`

**Context an engineer needs:**
- `scripts/track_performance.py` `main()` currently: parses `--dry-run`, loads cfg, marks the portfolio, prints a markdown block; if not dry-run it calls `build_daily_series(cfg)` and appends the block to `tracking/performance-log.md`. The log append must stay WEEKLY (Cowork routine runs the script with no flags) — `--series-only` must not touch the log.
- `scripts/portfolio_model.py` imports `yfinance` at module level, so any test importing `track_performance` must `pytest.importorskip('yfinance')`: the existing `deploy-site.yml` CI installs only `openpyxl pytest` and must keep passing.
- Tests live in `tests/`; `tests/conftest.py` already does `sys.path.insert(0, …/scripts)`, so test files import scripts as plain modules (e.g. `import export_site_data as ex`).
- `as_of` in the series file is stamped from the last trading date in the price index (`portfolio_model.py:174`), not wall-clock — a holiday rebuild is byte-identical, which is what makes "commit only if changed" the holiday guard.

---

### Task 1: `--series-only` flag on track_performance.py

**Files:**
- Test: `tests/test_track_performance.py` (create)
- Modify: `scripts/track_performance.py` (argparse + early return in `main()`)

- [ ] **Step 1: Write the failing test**

Create `tests/test_track_performance.py`:

```python
"""--series-only: the daily site-refresh path must not touch the weekly log."""
import sys

import pytest

# portfolio_model imports yfinance at module level; deploy-site CI installs
# only openpyxl+pytest and must keep passing without it.
pytest.importorskip('yfinance')

import track_performance as tp


def test_series_only_builds_series_and_skips_log(monkeypatch, tmp_path):
    built = []
    monkeypatch.setattr(tp, 'load_cfg', lambda: {'sentinel': True})
    monkeypatch.setattr(tp, 'build_daily_series', lambda cfg: built.append(cfg))
    monkeypatch.setattr(tp, 'mark',
                        lambda cfg: pytest.fail('mark() must not run'))
    log = tmp_path / 'performance-log.md'
    monkeypatch.setattr(tp, 'LOG', log)
    monkeypatch.setattr(sys, 'argv', ['track_performance.py', '--series-only'])

    tp.main()

    assert built == [{'sentinel': True}]
    assert not log.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_track_performance.py -v`
Expected: FAIL — argparse exits with `error: unrecognized arguments: --series-only` (SystemExit), because the flag doesn't exist yet.

- [ ] **Step 3: Implement the flag**

In `scripts/track_performance.py`, `main()` — add the argument and an early branch right after `load_cfg()`:

```python
    ap = argparse.ArgumentParser(description='Mark model portfolio vs benchmarks')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--series-only', action='store_true',
                    help='rebuild tracking/performance-series.json and exit; '
                         'no log append (daily site-refresh path)')
    args = ap.parse_args()

    cfg = load_cfg()
    if args.series_only:
        build_daily_series(cfg)
        return
    inception, capital = cfg['inception'], cfg['capital']
```

(Everything from `inception, capital = …` down is the existing code, unchanged.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_track_performance.py -v`
Expected: PASS (or SKIP if yfinance isn't installed locally — then `pip install yfinance` and re-run; the test must actually pass somewhere before commit).

Run the full suite to confirm nothing else broke: `python3 -m pytest tests -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_track_performance.py scripts/track_performance.py
git commit -m "feat(tracking): --series-only flag for daily site refresh"
```

---

### Task 2: daily-refresh.yml workflow

**Files:**
- Create: `.github/workflows/daily-refresh.yml`

- [ ] **Step 1: Write the workflow**

Create `.github/workflows/daily-refresh.yml`:

```yaml
name: Daily site refresh

on:
  schedule:
    # ~5:45pm ET during EDT, 4:45pm ET during EST — after close, adjusted
    # closes settled. Weekdays only; holidays self-skip via the
    # commit-if-changed guard (series is byte-identical when markets are shut).
    - cron: '45 21 * * 1-5'
  workflow_dispatch:

env:
  # Match deploy-site.yml: GitHub forces Node 24 for actions from 2026-06-16.
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

permissions:
  contents: write

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install yfinance pandas openpyxl pytest

      - name: Rebuild performance series (3 attempts — Yahoo throttles CI IPs)
        run: |
          for i in 1 2 3; do
            python scripts/track_performance.py --series-only && exit 0
            echo "attempt $i failed; retrying in 60s"
            sleep 60
          done
          echo "::error::yfinance failed after 3 attempts — site keeps yesterday's data"
          exit 1

      - name: Commit series if changed
        id: commit
        run: |
          if git diff --quiet tracking/performance-series.json; then
            echo "changed=false" >> "$GITHUB_OUTPUT"
            echo "series unchanged (holiday / no new data) — skipping deploy"
          else
            git config user.name 'github-actions[bot]'
            git config user.email 'github-actions[bot]@users.noreply.github.com'
            git add tracking/performance-series.json
            git commit -m "chore(data): daily performance series $(date -u +%F)"
            git pull --rebase origin main
            git push
            echo "changed=true" >> "$GITHUB_OUTPUT"
          fi

      # Inline deploy: a GITHUB_TOKEN push cannot trigger deploy-site.yml.
      - run: python -m pytest tests -q
        if: steps.commit.outputs.changed == 'true'
      - run: python scripts/export_site_data.py
        if: steps.commit.outputs.changed == 'true'
      - run: python scripts/check_site.py
        if: steps.commit.outputs.changed == 'true'
      - uses: cloudflare/wrangler-action@v3
        if: steps.commit.outputs.changed == 'true'
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy site --project-name=ai-supply-chain
```

- [ ] **Step 2: Syntax-check the YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/daily-refresh.yml')); print('ok')"`
(If PyYAML is missing locally: `pip install pyyaml`.)
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/daily-refresh.yml
git commit -m "ci(site): daily performance refresh + redeploy on weekday cron"
```

---

### Task 3: Update CLAUDE.md (the weekly-pipeline claim is now stale)

**Files:**
- Modify: `CLAUDE.md` — §Portfolio site, the "Performance series" bullet

- [ ] **Step 1: Edit the bullet**

Replace:

```markdown
- **Performance series:** `tracking/performance-series.json` is written by
  `track_performance.py` (weekly pipeline) so CI needs no network/yfinance.
```

with:

```markdown
- **Performance series:** `tracking/performance-series.json` is written by
  `track_performance.py`. `deploy-site.yml` needs no network/yfinance;
  `daily-refresh.yml` (weekday cron 21:45 UTC) rebuilds it with
  `--series-only`, commits if changed (holidays self-skip), and redeploys
  inline — dashboard/performance pages stay daily-fresh. The weekly Cowork
  routine still owns the narrative `performance-log.md`.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: CLAUDE.md reflects daily-refresh workflow"
```

---

### Task 4: Push and validate end-to-end

- [ ] **Step 1: Push to main**

```bash
git push origin main
```

(This also fires the normal `deploy-site.yml` run — it should stay green; the new test self-skips there because yfinance isn't installed.)

- [ ] **Step 2: Manually trigger the new workflow**

```bash
gh workflow run daily-refresh.yml
sleep 10
gh run list --workflow=daily-refresh.yml --limit 1
gh run watch $(gh run list --workflow=daily-refresh.yml --limit 1 --json databaseId --jq '.[0].databaseId')
```

Expected: run completes green. If today's data adds a date to the series, the deploy steps execute; if the series is unchanged (already refreshed today, or after-hours data not yet posted), the run logs "series unchanged … skipping deploy" — both are correct outcomes. A red run on the yfinance step after 3 retries means Yahoo throttling; re-trigger once before investigating.

- [ ] **Step 3: Verify the deploy-site run also stayed green**

```bash
gh run list --workflow=deploy-site.yml --limit 1
```

Expected: `completed success`.

- [ ] **Step 4: Confirm the site shows the fresh date**

If the manual run committed + deployed, check `site/data/meta.json` was regenerated in the run logs and (optionally, in browser) that the dashboard "as of" date matches the latest trading day.
