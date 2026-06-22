---
description: Force-refresh the portfolio site dashboard (performance series) and deploy to live
---

Manually run the daily dashboard refresh and deploy it. Use this when the
`daily-refresh.yml` cron has fallen behind (it's best-effort and drops runs —
see CLAUDE.md §Portfolio site), so the dashboard / performance pages are stale.

This does the full path the cron does: rebuild the performance series → verify →
commit → push to `main` → confirm the Cloudflare deploy succeeded. Run all of it
autonomously; **stop only if a safety gate (Step 3 or 5) fails** — those gates
exist to catch the one dangerous failure mode (see Step 3).

## Why this is risky enough to need a runbook

The series is rebuilt from `tracking/performance-config.json`, the **notional
$10k** portfolio config. If you rebuild from a stale or wrong-branch copy of that
config (e.g. a feature branch that predates a notional-rescale or rebalance), the
*entire historical series* shifts — silently leaking real-dollar-derived values
and regressing the privacy boundary. This is invisible unless you diff the
rebuilt history against what's already committed. Step 1 (sync to origin/main)
prevents it; Step 3 (history diff) catches it if prevention failed.

`site/data/*.json` is **gitignored** — it is regenerated at deploy time by
`export_site_data.py`. The only file you commit is `tracking/performance-series.json`.

## Steps

1. **Sync to origin/main first.** The dashboard deploys from `main`, and the
   config must be the current one. Run:

   ```bash
   git fetch origin
   git switch main && git reset --hard origin/main   # or: git checkout main && git rebase
   ```

   If you have uncommitted work elsewhere, stash it — do NOT build the series
   from a feature branch. (A feature branch's `performance-config.json` may be
   stale even when `git diff main` looks clean, because that compares to *local*
   main, which can itself be behind origin.)

2. **Rebuild the series:**

   ```bash
   python3 scripts/track_performance.py --series-only
   ```

   On a market holiday or weekend there's no new trading bar, so the file won't
   change — that's a no-op, report it and stop (nothing to deploy).

3. **VERIFY (hard gate — do not skip).** Compare the rebuilt series against the
   committed one:

   ```bash
   python3 - <<'PY'
   import json, subprocess
   old = json.loads(subprocess.check_output(['git','show','origin/main:tracking/performance-series.json']))
   new = json.load(open('tracking/performance-series.json'))
   od = {d: old['model'][i] for i, d in enumerate(old['dates'])}
   nd = {d: new['model'][i] for i, d in enumerate(new['dates'])}
   shared = [d for d in old['dates'] if d in nd]
   maxdiff = max((abs(od[d]-nd[d]) for d in shared), default=0)
   print('start value :', new['model'][0])
   print('as_of       :', new['as_of'], '| dates:', len(new['dates']))
   print('shared dates:', len(shared), '| max abs model diff:', round(maxdiff, 4))
   print('new dates   :', [d for d in nd if d not in od])
   PY
   ```

   Require ALL of:
   - **start value** equals the notional base (`capital` in `performance-config.json`, currently 10000.0)
   - **max abs model diff** on shared dates ≲ 0.1 (rounding only — history must NOT change)
   - **new dates** contains only the new trading day(s), nothing rewritten

   If the diff is large (e.g. hundreds of points) or the start value isn't the
   notional base → **STOP.** You built from a stale/wrong config. Re-do Step 1
   and rebuild. Do not commit or push.

4. **Regenerate site data** (so you can eyeball the dashboard the deploy will produce):

   ```bash
   python3 scripts/export_site_data.py
   python3 -c "import json; p=json.load(open('site/data/performance.json')); m=json.load(open('site/data/meta.json')); print('perf as_of', p['as_of'], '| summary', p['summary']); print('meta', {k:m[k] for k in ('as_of','last_rebalance','holdings','notional')})"
   ```

5. **Privacy gate (hard gate):**

   ```bash
   python3 -m pytest tests/test_export_site_data.py -q
   ```

   Must be all green (includes `test_privacy_no_real_dollars_anywhere`). If it
   fails → STOP, do not push.

6. **Commit & push to main.** Only `tracking/performance-series.json` should be
   staged (`site/data` is gitignored). End the commit message with the
   `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer.

   ```bash
   git add tracking/performance-series.json
   git commit -m "chore(site): refresh performance series to <as_of>"
   git push origin main
   ```

   If the push is rejected (remote moved — a cron or PR merge landed): `git fetch`,
   inspect `origin/main`'s series as_of, `git rebase origin/main` (resolve the
   single-line JSON conflict by taking your fully-rebuilt file), re-run Step 3,
   then push.

7. **Confirm the deploy.** Push to `main` triggers the "Deploy portfolio site"
   workflow (regenerates `site/data`, runs `check_site.py`, deploys to Cloudflare):

   ```bash
   gh run list --branch main --limit 1
   gh run watch <run-id> --exit-status
   ```

   Report the final dashboard figures (as_of, total return, vs SMH/QQQ/SPY/EW)
   and confirm the deploy concluded `success`.

## Notes

- This does NOT touch the narrative `performance-log.md` (that's the weekly
  routine's job) — series + dashboard only.
- Holidays/weekends self-skip at Step 2 (no new bar = no change).
- This is the manual equivalent of `daily-refresh.yml`; reach for it whenever the
  dashboard `as_of` is older than the last trading day.
