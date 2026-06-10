# Portfolio Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A read-only, password-gated static site sharing the AI supply chain model portfolio with friends, all dollars indexed to a $10k notional base.

**Architecture:** One-way data flow: repo workbooks/tracking files → `scripts/export_site_data.py` (the single privacy boundary, $10k scaling) → `site/data/*.json` → plain static frontend (terminal-dark, Chart.js, no npm build). The daily performance series is persisted to `tracking/performance-series.json` by the existing weekly pipeline (`track_performance.py`, which already runs yfinance), so CI deploys are offline and deterministic. Cloudflare Pages hosts the site; a `site/_worker.js` enforces a shared password; a GitHub Action deploys on push to `main`.

**Tech Stack:** Python 3 + openpyxl (exporter), pytest (tests), vanilla HTML/CSS/JS + vendored Chart.js (frontend), Cloudflare Pages + Workers (hosting/auth), GitHub Actions (CI).

**Spec:** `docs/superpowers/specs/2026-06-10-portfolio-site-design.md` — read it first.

**Verified data-shape facts (do not re-derive):**
- `00-master/portfolio.xlsx` → `Targets` sheet: title in row 1, headers in **row 2**: `Ticker, Layer, TOTAL, Tier, Rank, Status, Include?, Override, Target %, Notes`. Data from row 3. Current portfolio = rows with `Include? == 'Y'` (16 rows). `Layer` is a string like `'06 AI Compute Silicon / GPUs / merchant accelerators'` — first 2 chars are the layer number.
- `00-master/ai_supply_chain_scoring.xlsx` → `Watchlist` sheet: headers in row 1; col 1 `Ticker`, col 2 `Company`. → `Rating Audit` sheet: headers row 1: `Date, Ticker, Dimension, Rating, Rationale, Source, Confidence, Type`. ~1830 rows; `Type == 'Initial'` rows are batch baselines (exclude from change log).
- `tracking/performance-config.json`: keys `inception` (`'2026-05-26'`), `capital` (`13800.0`), `benchmarks`, `ew_universe` (35 tickers), `events` (list of `{date, reason, allocations: {ticker: dollars}, cash}`).
- `per-stock/{TICKER}/thesis.md` § `## 1. One-line thesis`: body is a `> ...` blockquote. Unpopulated files still contain template placeholders in `{braces}` — **currently true for most/all holdings**, so expect many "template thesis" warnings; that is correct behavior, not a bug.
- `scripts/` modules import each other flat (`from common import ROOT`); scripts are run from repo root as `python3 scripts/x.py` with `scripts/` reachable because each script lives there. Tests must add `scripts/` to `sys.path` (done in `tests/conftest.py`).

**File map:**

| Path | Responsibility |
|---|---|
| `scripts/portfolio_model.py` (modify) | add `build_daily_series(cfg)` → writes `tracking/performance-series.json` |
| `scripts/track_performance.py` (modify) | call `build_daily_series` on each non-dry run |
| `scripts/export_site_data.py` (create) | privacy boundary: read workbooks/tracking → `site/data/*.json`, $10k scaling |
| `scripts/check_site.py` (create) | post-export smoke check (data sanity + dead-reference scan) |
| `tests/conftest.py`, `tests/test_export_site_data.py` (create) | fixture workbooks + exporter tests incl. privacy regression |
| `tracking/notion-scan-links.json` (create) | `[{date, title, url}]` — backfilled, then appended weekly by the Cowork routine |
| `site/css/terminal.css`, `site/js/common.js`, `site/js/vendor/chart.umd.js` | shared frontend assets |
| `site/index.html` + `site/js/dashboard.js` | dashboard |
| `site/performance.html` + `site/js/performance.js` | full chart + monthly table |
| `site/positions.html` + `site/js/positions.js` | holdings table + thesis expanders |
| `site/changes.html` + `site/js/changes.js` | change log |
| `site/scans.html` + `site/js/scans.js` | weekly scan links |
| `site/_worker.js` | Cloudflare Pages advanced-mode worker: password gate |
| `.github/workflows/deploy-site.yml` | test → export → check → deploy |

`site/data/` is CI-generated output — add it to `.gitignore` (Task 2).

---

### Task 1: Daily performance series (`build_daily_series`)

The exporter must not need network access, so the dated series is built by the weekly pipeline and committed. yfinance code is impractical to unit-test; verification is running it for real.

**Files:**
- Modify: `scripts/portfolio_model.py` (append to end of file)
- Modify: `scripts/track_performance.py:110-125` (the `if not args.dry_run:` block)

- [ ] **Step 1: Add `build_daily_series` to `scripts/portfolio_model.py`**

Append at end of file:

```python
SERIES = ROOT / 'tracking' / 'performance-series.json'


def build_daily_series(cfg: dict) -> dict | None:
    """Daily valuation series since inception, written to SERIES.

    Model values are DOLLARS (event-sourced walk: within each event period,
    value = cash + sum(alloc * price/price_at_event_start), missing-price
    names carried flat). Benchmarks are growth-of-1 from inception. The site
    exporter rescales both to the $10k notional base.
    """
    import pandas as pd

    inception = cfg['inception']
    inc_date = dt.date.fromisoformat(inception)

    def growth(t):
        s = _series(t, inception)
        if s is None:
            return None
        s = s[s.index.date >= inc_date]
        return None if s.empty else s / s.iloc[0]

    smh, qqq = growth('SMH'), growth('QQQ')
    if smh is None or qqq is None:
        flag('series: benchmark price data unavailable — series not built')
        return None
    idx = smh.index

    ew_parts = [g.reindex(idx).ffill()
                for t in cfg['ew_universe'] if (g := growth(t)) is not None]
    ew = sum(ew_parts) / len(ew_parts)

    model = pd.Series(0.0, index=idx)
    events = cfg['events']
    for i, ev in enumerate(events):
        start = dt.date.fromisoformat(ev['date'])
        end = (dt.date.fromisoformat(events[i + 1]['date'])
               if i + 1 < len(events) else None)
        mask = (idx.date >= start)
        if end is not None:
            mask &= (idx.date < end)
        if not mask.any():
            continue
        seg = pd.Series(float(ev.get('cash', 0)), index=idx[mask])
        for t, alloc in ev['allocations'].items():
            s = _series(t, inception)
            sub = None if s is None else s[s.index.date >= start]
            if sub is None or sub.empty:
                seg += alloc            # carried flat (no price data)
                continue
            seg += alloc * (sub.reindex(idx[mask]).ffill()
                            / sub.iloc[0]).fillna(1.0)
        model[idx[mask]] = seg

    out = {
        'start': inception,
        'as_of': str(idx[-1].date()),
        'dates': [str(d.date()) for d in idx],
        'model': [round(float(v), 2) for v in model],
        'bench': {
            'SMH': [round(float(v), 6) for v in smh.reindex(idx).ffill()],
            'QQQ': [round(float(v), 6) for v in qqq.reindex(idx).ffill()],
            'EW': [round(float(v), 6) for v in ew],
        },
    }
    SERIES.write_text(json.dumps(out) + '\n')
    return out
```

- [ ] **Step 2: Call it from `scripts/track_performance.py`**

Change the import line (line 31) from:

```python
from portfolio_model import load_cfg, mark, ret_since
```

to:

```python
from portfolio_model import build_daily_series, load_cfg, mark, ret_since
```

In `main()`, inside the existing `if not args.dry_run:` block, add as its **first** line:

```python
        build_daily_series(cfg)
```

- [ ] **Step 3: Run for real and inspect**

Run: `python3 scripts/track_performance.py --dry-run` — confirm it still prints a mark and does NOT write the series (dry-run unchanged).
Run: `python3 scripts/track_performance.py`
Expected: appends to performance-log.md AND creates `tracking/performance-series.json`.

Run: `python3 -c "
import json; d = json.load(open('tracking/performance-series.json'))
assert d['dates'][0] == '2026-05-26', d['dates'][0]
assert len(d['dates']) == len(d['model']) == len(d['bench']['SMH'])
assert abs(d['model'][0] - 13800) < 50, d['model'][0]
assert 0.5 < d['bench']['QQQ'][-1] < 2.0
print('OK', len(d['dates']), 'days, model now', d['model'][-1])
"`
Expected: `OK <n> days, model now <value close to the printed mark>`.

- [ ] **Step 4: Commit**

```bash
git add scripts/portfolio_model.py scripts/track_performance.py tracking/performance-series.json tracking/performance-log.md
git commit -m "feat(site): persist daily performance series for site exporter"
```

---

### Task 2: Test scaffolding + fixtures

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/__init__.py` (empty)
- Modify: `.gitignore` (append `site/data/`)

- [ ] **Step 1: Create `tests/__init__.py`** (empty file) **and `tests/conftest.py`:**

```python
"""Fixture data for export_site_data tests.

Builds miniature versions of the real workbooks with DISTINCTIVE real-dollar
values (13800, 824.7, 13386.55) that the privacy regression test asserts
never appear in exported output.
"""
import json
import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

REAL_DOLLARS = ['13800', '824.7', '13386.55']   # planted; must never leak


@pytest.fixture
def repo(tmp_path):
    """A miniature repo tree with every input the exporter reads."""
    (tmp_path / '00-master').mkdir()
    (tmp_path / 'tracking').mkdir()
    (tmp_path / 'site' / 'data').mkdir(parents=True)

    # --- portfolio.xlsx: Targets sheet, headers in row 2, data from row 3
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Targets'
    ws.append(['Target Portfolio (test)'])
    ws.append(['Ticker', 'Layer', 'TOTAL', 'Tier', 'Rank', 'Status',
               'Include?', 'Override', 'Target %', 'Notes'])
    ws.append(['NVDA', '06 AI Compute Silicon / GPUs', 83.3, '✓✓', 1,
               'HOLD', 'Y', None, 60.0, None])
    ws.append(['TSM', '05 Fabs & Foundries', 78.1, '✓✓', 2,
               'HOLD', 'Y', None, 40.0, None])
    ws.append(['ARM', '06 Silicon - IP', 66.0, '✓', 3,
               'EXIT', 'N', None, 0.0, None])
    wb.save(tmp_path / '00-master' / 'portfolio.xlsx')

    # --- scoring.xlsx: Watchlist + Rating Audit
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Watchlist'
    ws.append(['Ticker', 'Company', 'Layer'])
    ws.append(['NVDA', 'NVIDIA Corp', '06'])
    ws.append(['TSM', 'TSMC', '05'])
    wa = wb.create_sheet('Rating Audit')
    wa.append(['Date', 'Ticker', 'Dimension', 'Rating', 'Rationale',
               'Source', 'Confidence', 'Type'])
    wa.append(['2026-05-17', 'NVDA', 'D1', 5, 'Initial baseline rating.',
               'src', 'High', 'Initial'])
    wa.append(['2026-06-10', 'NVDA', 'D2', 4, 'Re-rated on directness lens.',
               'src', 'High', 'Re-rate'])
    wa.append(['2026-06-10', 'NVDA', 'D3', 3, 'Second dimension same day.',
               'src', 'Medium', 'Re-rate'])
    wb.save(tmp_path / '00-master' / 'ai_supply_chain_scoring.xlsx')

    # --- performance-config.json (events: inception, then TSM enters / ARM exits)
    cfg = {
        'inception': '2026-05-26', 'capital': 13800.0, 'cash': 71.72,
        'benchmarks': ['SMH', 'QQQ'], 'ew_universe': ['NVDA', 'TSM'],
        'events': [
            {'date': '2026-05-26', 'reason': 'initial deployment',
             'allocations': {'NVDA': 824.7, 'ARM': 500.0}, 'cash': 71.72},
            {'date': '2026-06-10', 'reason': 'rebalance (score refresh)',
             'allocations': {'NVDA': 900.0, 'TSM': 700.0}, 'cash': 50.0},
        ],
    }
    (tmp_path / 'tracking' / 'performance-config.json').write_text(
        json.dumps(cfg))

    # --- performance-series.json (3 days, real dollars incl. planted 13386.55)
    series = {
        'start': '2026-05-26', 'as_of': '2026-05-28',
        'dates': ['2026-05-26', '2026-05-27', '2026-05-28'],
        'model': [13800.0, 13903.5, 13386.55],
        'bench': {'SMH': [1.0, 1.01, 0.98], 'QQQ': [1.0, 1.005, 0.99],
                  'EW': [1.0, 1.02, 0.97]},
    }
    (tmp_path / 'tracking' / 'performance-series.json').write_text(
        json.dumps(series))

    # --- thesis files: NVDA populated, TSM still the template
    nv = tmp_path / 'per-stock' / 'NVDA'
    nv.mkdir(parents=True)
    (nv / 'thesis.md').write_text(
        '# NVDA — NVIDIA\n\n## 1. One-line thesis\n\n'
        '> The compute layer toll booth: every training run pays NVDA.\n\n'
        '---\n\n## 2. Position in the AI supply chain\n\ntext\n')
    ts = tmp_path / 'per-stock' / 'TSM'
    ts.mkdir(parents=True)
    (ts / 'thesis.md').write_text(
        '# {TICKER} — {Company Name}\n\n## 1. One-line thesis\n\n'
        '> {Single sentence: why does this stock exist in the portfolio?}\n\n'
        '---\n\n## 2. Position in the AI supply chain\n')

    # --- notion scan links
    (tmp_path / 'tracking' / 'notion-scan-links.json').write_text(json.dumps([
        {'date': '2026-06-05', 'title': 'Weekly News Scan — 2026-06-05',
         'url': 'https://www.notion.so/abc123'},
    ]))
    (tmp_path / 'tracking' / 'weekly-news-scan-2026-06-05.md').write_text('x')
    (tmp_path / 'tracking' / 'weekly-news-scan-2026-05-29.md').write_text('x')

    return tmp_path
```

- [ ] **Step 2: Append `site/data/` to `.gitignore`**

```bash
echo "site/data/" >> .gitignore
```

- [ ] **Step 3: Verify fixtures build**

Run: `python3 -m pytest tests -q --collect-only`
Expected: `no tests ran` (collects without import errors).

- [ ] **Step 4: Commit**

```bash
git add tests/__init__.py tests/conftest.py .gitignore
git commit -m "test(site): fixture repo for exporter tests"
```

---

### Task 3: Exporter — positions

**Files:**
- Create: `scripts/export_site_data.py`
- Create: `tests/test_export_site_data.py`

- [ ] **Step 1: Write failing tests** — create `tests/test_export_site_data.py`:

```python
import json

import pytest

import export_site_data as ex


def test_positions_only_included_rows(repo):
    pos = ex.export_positions(repo)
    assert [p['ticker'] for p in pos] == ['NVDA', 'TSM']   # ARM excluded


def test_positions_fields_and_scaling(repo):
    pos = ex.export_positions(repo)
    nvda = pos[0]
    assert nvda == {
        'ticker': 'NVDA', 'company': 'NVIDIA Corp',
        'layer_num': '06', 'layer': 'Silicon',
        'weight': 60.0, 'notional': 6000,
        'score': 83.3, 'tier': '✓✓',
    }
    assert sum(p['notional'] for p in pos) == 10000


def test_positions_schema_surprise_fails_loudly(repo):
    import openpyxl
    wb = openpyxl.load_workbook(repo / '00-master' / 'portfolio.xlsx')
    wb['Targets'].cell(row=2, column=9).value = 'Tgt %'   # renamed column
    wb.save(repo / '00-master' / 'portfolio.xlsx')
    with pytest.raises(SystemExit):
        ex.export_positions(repo)
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'export_site_data'`.

- [ ] **Step 3: Create `scripts/export_site_data.py`:**

```python
"""Export friend-safe site data — THE privacy boundary for the portfolio site.

Reads the workbooks and tracking files, scales every dollar figure to the
$10,000 notional base, and writes site/data/*.json. Nothing under site/
reads repo data except through this script, so what friends can see is
auditable here. EXCLUDED BY DESIGN: real share counts, real dollar values,
cost basis, real capital.

Usage: python3 scripts/export_site_data.py [--root DIR]
Fails loudly (exit 1) on schema surprises; warns (stderr) on soft gaps.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

import openpyxl

NOTIONAL = 10_000.0

LAYERS = {
    '01': 'Power Generation', '02': 'Grid Equipment', '03': 'Data Centers',
    '04': 'Semi Equipment', '05': 'Fabs & Foundries', '06': 'Silicon',
    '07': 'Optical Networking', '08': 'Servers', '09': 'Cloud',
    '10': 'Applications',
}

TARGETS_HEADERS = ['Ticker', 'Layer', 'TOTAL', 'Tier', 'Rank', 'Status',
                   'Include?', 'Override', 'Target %', 'Notes']


def fail(msg: str) -> None:
    print(f'EXPORT ERROR: {msg}', file=sys.stderr)
    raise SystemExit(1)


def warn(msg: str) -> None:
    print(f'WARN: {msg}', file=sys.stderr)


def _company_names(root: Path) -> dict[str, str]:
    wb = openpyxl.load_workbook(
        root / '00-master' / 'ai_supply_chain_scoring.xlsx', data_only=True)
    ws = wb['Watchlist']
    return {r[0]: r[1] for r in ws.iter_rows(min_row=2, values_only=True)
            if r[0]}


def export_positions(root: Path) -> list[dict]:
    wb = openpyxl.load_workbook(root / '00-master' / 'portfolio.xlsx',
                                data_only=True)
    ws = wb['Targets']
    headers = [c.value for c in ws[2]][:10]
    if headers != TARGETS_HEADERS:
        fail(f'Targets headers changed: {headers}')
    names = _company_names(root)
    out = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        if not row[0] or row[6] != 'Y':
            continue
        layer_num = str(row[1])[:2]
        if layer_num not in LAYERS:
            warn(f'{row[0]}: unrecognized layer {row[1]!r}')
        if row[8] is None:
            fail(f'{row[0]}: included row has no Target %')
        out.append({
            'ticker': row[0],
            'company': names.get(row[0], row[0]),
            'layer_num': layer_num,
            'layer': LAYERS.get(layer_num, str(row[1])),
            'weight': round(float(row[8]), 2),
            'notional': round(float(row[8]) / 100 * NOTIONAL),
            'score': round(float(row[2]), 1),
            'tier': row[3],
        })
    if not out:
        fail('no included positions found in Targets')
    return out
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests -q`
Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/export_site_data.py tests/test_export_site_data.py
git commit -m "feat(site): exporter — positions.json"
```

---

### Task 4: Exporter — performance

**Files:**
- Modify: `scripts/export_site_data.py` (append functions)
- Modify: `tests/test_export_site_data.py` (append tests)

- [ ] **Step 1: Append failing tests:**

```python
def test_performance_scaled_to_notional(repo):
    perf = ex.export_performance(repo)
    assert perf['dates'][0] == '2026-05-26'
    assert perf['model'][0] == 10000.0
    # 13386.55 / 13800 * 10000
    assert abs(perf['model'][-1] - 9700.4) < 0.1
    assert perf['bench']['SMH'][0] == 10000.0
    assert abs(perf['bench']['SMH'][-1] - 9800.0) < 0.1


def test_performance_summary_and_monthly(repo):
    perf = ex.export_performance(repo)
    s = perf['summary']
    assert abs(s['total_return'] - (13386.55 / 13800 - 1)) < 1e-6
    assert abs(s['vs_smh'] - (s['total_return'] - (-0.02))) < 1e-6
    assert perf['monthly'][0]['month'] == '2026-05'
    assert perf['as_of'] == '2026-05-28'
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests -q`
Expected: 2 FAIL (`AttributeError: ... no attribute 'export_performance'`), 3 PASS.

- [ ] **Step 3: Append implementation:**

```python
def export_performance(root: Path) -> dict:
    sp = root / 'tracking' / 'performance-series.json'
    if not sp.exists():
        fail('tracking/performance-series.json missing — run '
             'scripts/track_performance.py first')
    raw = json.loads(sp.read_text())
    cfg = json.loads(
        (root / 'tracking' / 'performance-config.json').read_text())
    capital = float(cfg['capital'])
    k = NOTIONAL / capital
    model = [round(v * k, 2) for v in raw['model']]
    bench = {name: [round(g * NOTIONAL, 2) for g in series]
             for name, series in raw['bench'].items()}

    def total(series):
        return series[-1] / series[0] - 1

    summary = {
        'total_return': total(model),
        'vs_smh': total(model) - total(bench['SMH']),
        'vs_qqq': total(model) - total(bench['QQQ']),
        'vs_ew': total(model) - total(bench['EW']),
    }

    monthly: list[dict] = []
    by_month: dict[str, list[int]] = {}
    for i, d in enumerate(raw['dates']):
        by_month.setdefault(d[:7], []).append(i)
    prev_close = {'model': model[0], 'SMH': bench['SMH'][0],
                  'QQQ': bench['QQQ'][0]}
    for month in sorted(by_month):
        last = by_month[month][-1]
        row = {'month': month}
        for key, series in (('model', model), ('SMH', bench['SMH']),
                            ('QQQ', bench['QQQ'])):
            row[key] = round(series[last] / prev_close[key] - 1, 6)
            prev_close[key] = series[last]
        monthly.append(row)

    return {'dates': raw['dates'], 'model': model, 'bench': bench,
            'summary': summary, 'monthly': monthly, 'as_of': raw['as_of']}
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests -q`
Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/export_site_data.py tests/test_export_site_data.py
git commit -m "feat(site): exporter — performance.json ($10k-indexed)"
```

---

### Task 5: Exporter — changes

**Files:**
- Modify: `scripts/export_site_data.py` (append)
- Modify: `tests/test_export_site_data.py` (append)

- [ ] **Step 1: Append failing tests:**

```python
def test_changes_from_events_and_audit(repo):
    ch = ex.export_changes(repo)
    kinds = {(c['date'], c['type'], c.get('ticker')) for c in ch}
    assert ('2026-05-26', 'inception', None) in kinds
    assert ('2026-06-10', 'add', 'TSM') in kinds
    assert ('2026-06-10', 'drop', 'ARM') in kinds
    rerates = [c for c in ch if c['type'] == 'rerate']
    assert len(rerates) == 1                       # grouped by (date, ticker)
    assert rerates[0]['ticker'] == 'NVDA'
    assert rerates[0]['detail'] == 'D2, D3'
    assert 'Initial baseline' not in json.dumps(ch)   # Type==Initial excluded


def test_changes_no_dollar_amounts(repo):
    text = json.dumps(ex.export_changes(repo))
    for planted in ('824.7', '13800', '900.0', '700.0'):
        assert planted not in text


def test_changes_sorted_newest_first(repo):
    ch = ex.export_changes(repo)
    assert [c['date'] for c in ch] == sorted(
        (c['date'] for c in ch), reverse=True)
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests -q`
Expected: 3 FAIL (no attribute `export_changes`), 5 PASS.

- [ ] **Step 3: Append implementation:**

```python
def export_changes(root: Path) -> list[dict]:
    cfg = json.loads(
        (root / 'tracking' / 'performance-config.json').read_text())
    out: list[dict] = []
    events = cfg['events']
    for i, ev in enumerate(events):
        if i == 0:
            out.append({'date': ev['date'], 'type': 'inception',
                        'ticker': None, 'note': ev['reason']})
            continue
        prev, curr = set(events[i - 1]['allocations']), set(ev['allocations'])
        for t in sorted(curr - prev):
            out.append({'date': ev['date'], 'type': 'add', 'ticker': t,
                        'note': ev['reason']})
        for t in sorted(prev - curr):
            out.append({'date': ev['date'], 'type': 'drop', 'ticker': t,
                        'note': ev['reason']})
        if curr == prev:
            out.append({'date': ev['date'], 'type': 'resize', 'ticker': None,
                        'note': ev['reason']})

    wb = openpyxl.load_workbook(
        root / '00-master' / 'ai_supply_chain_scoring.xlsx', data_only=True)
    ws = wb['Rating Audit']
    grouped: dict[tuple[str, str], dict] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        date, ticker, dim, _rating, rationale, _src, _conf, typ = row[:8]
        if not date or not typ or str(typ).strip().lower() == 'initial':
            continue
        key = (str(date)[:10], ticker)
        g = grouped.setdefault(key, {'dims': [], 'rationale': rationale})
        g['dims'].append(str(dim))
    for (date, ticker), g in grouped.items():
        note = (g['rationale'] or '').strip()
        out.append({'date': date, 'type': 'rerate', 'ticker': ticker,
                    'detail': ', '.join(sorted(g['dims'])),
                    'note': note[:200] + ('…' if len(note) > 200 else '')})

    return sorted(out, key=lambda c: (c['date'], c['type']), reverse=True)
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests -q`
Expected: 8 PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/export_site_data.py tests/test_export_site_data.py
git commit -m "feat(site): exporter — changes.json (events + rating audit)"
```

---

### Task 6: Exporter — theses + scans

**Files:**
- Modify: `scripts/export_site_data.py` (append)
- Modify: `tests/test_export_site_data.py` (append)

- [ ] **Step 1: Append failing tests:**

```python
def test_theses_extracts_populated_and_nulls_template(repo, capsys):
    th = ex.export_theses(repo, ['NVDA', 'TSM'])
    assert th['NVDA'] == ('The compute layer toll booth: every training run '
                          'pays NVDA.')
    assert th['TSM'] is None
    assert 'TSM' in capsys.readouterr().err     # warned


def test_theses_missing_file_is_null(repo, capsys):
    th = ex.export_theses(repo, ['NVDA', 'XYZ'])
    assert th['XYZ'] is None
    assert 'XYZ' in capsys.readouterr().err


def test_scans_passthrough_and_orphan_warning(repo, capsys):
    scans = ex.export_scans(repo)
    assert scans == [{'date': '2026-06-05',
                      'title': 'Weekly News Scan — 2026-06-05',
                      'url': 'https://www.notion.so/abc123'}]
    assert '2026-05-29' in capsys.readouterr().err   # scan md with no link
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests -q`
Expected: 3 FAIL, 8 PASS.

- [ ] **Step 3: Append implementation:**

```python
THESIS_SECTION = re.compile(
    r'^## 1\. One-line thesis\s*$(.*?)(?=^## |\Z)', re.M | re.S)


def export_theses(root: Path, tickers: list[str]) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for t in tickers:
        path = root / 'per-stock' / t / 'thesis.md'
        if not path.exists():
            warn(f'{t}: no thesis.md — snippet omitted')
            out[t] = None
            continue
        m = THESIS_SECTION.search(path.read_text())
        body = '' if not m else m.group(1)
        lines = [ln.lstrip('> ').strip() for ln in body.splitlines()]
        text = ' '.join(ln for ln in lines if ln and ln != '---').strip()
        if not text or re.search(r'\{.+?\}', text):
            warn(f'{t}: thesis.md is still the template — snippet omitted')
            out[t] = None
        else:
            out[t] = text
    return out


def export_scans(root: Path) -> list[dict]:
    lp = root / 'tracking' / 'notion-scan-links.json'
    if not lp.exists():
        warn('tracking/notion-scan-links.json missing — scans page empty')
        return []
    scans = json.loads(lp.read_text())
    for s in scans:
        if not all(s.get(k) for k in ('date', 'title', 'url')):
            fail(f'malformed scan link entry: {s}')
    linked = {s['date'] for s in scans}
    for md in sorted(root.glob('tracking/weekly-news-scan-*.md')):
        date = md.stem.replace('weekly-news-scan-', '')
        if date not in linked:
            warn(f'scan {date} has no Notion link entry — omitted from site')
    return sorted(scans, key=lambda s: s['date'], reverse=True)
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests -q`
Expected: 11 PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/export_site_data.py tests/test_export_site_data.py
git commit -m "feat(site): exporter — theses.json + scans.json"
```

---

### Task 7: Exporter — main() + privacy regression test

**Files:**
- Modify: `scripts/export_site_data.py` (append)
- Modify: `tests/test_export_site_data.py` (append)

- [ ] **Step 1: Append failing tests:**

```python
def test_main_writes_all_files(repo):
    ex.main(repo)
    names = {p.name for p in (repo / 'site' / 'data').glob('*.json')}
    assert names == {'positions.json', 'performance.json', 'changes.json',
                     'theses.json', 'scans.json', 'meta.json'}
    meta = json.loads((repo / 'site' / 'data' / 'meta.json').read_text())
    assert meta['as_of'] == '2026-05-28'
    assert meta['last_rebalance'] == '2026-06-10'
    assert meta['holdings'] == 2


def test_privacy_no_real_dollars_anywhere(repo):
    """THE regression test: planted real-dollar values must never leak."""
    from conftest import REAL_DOLLARS
    ex.main(repo)
    for p in (repo / 'site' / 'data').glob('*.json'):
        text = p.read_text()
        for planted in REAL_DOLLARS:
            assert planted not in text, f'{planted} leaked into {p.name}'
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests -q`
Expected: 2 FAIL (no attribute `main`), 11 PASS.

- [ ] **Step 3: Append implementation:**

```python
def main(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parent.parent
    out_dir = root / 'site' / 'data'
    out_dir.mkdir(parents=True, exist_ok=True)

    positions = export_positions(root)
    performance = export_performance(root)
    changes = export_changes(root)
    theses = export_theses(root, [p['ticker'] for p in positions])
    scans = export_scans(root)
    cfg = json.loads(
        (root / 'tracking' / 'performance-config.json').read_text())
    meta = {
        'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(
            timespec='seconds'),
        'as_of': performance['as_of'],
        'last_rebalance': cfg['events'][-1]['date'],
        'holdings': len(positions),
        'notional': NOTIONAL,
    }
    for name, data in (('positions', positions), ('performance', performance),
                       ('changes', changes), ('theses', theses),
                       ('scans', scans), ('meta', meta)):
        (out_dir / f'{name}.json').write_text(json.dumps(data) + '\n')
        print(f'wrote site/data/{name}.json')


if __name__ == '__main__':
    main(Path(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == '--root'
         else None)
```

- [ ] **Step 4: Run tests, then run the exporter against the REAL repo**

Run: `python3 -m pytest tests -q`
Expected: 13 PASS.

Run: `python3 scripts/export_site_data.py`
Expected: six `wrote site/data/*.json` lines; many `WARN: <T>: thesis.md is still the template` lines (expected at launch — see data-shape facts above); `WARN: scan ... has no Notion link entry` until Task 8 backfills.

Run: `python3 -c "
import json
pos = json.load(open('site/data/positions.json'))
assert len(pos) == 16, len(pos)
assert abs(sum(p['notional'] for p in pos) - 10000) < 100
print('OK — 16 positions, notional sums to ~10k')
"`
Expected: `OK — 16 positions, notional sums to ~10k`

- [ ] **Step 5: Commit**

```bash
git add scripts/export_site_data.py tests/test_export_site_data.py
git commit -m "feat(site): exporter main() + privacy regression test"
```

---

### Task 8: Notion scan-link backfill + routine instruction

**Files:**
- Create: `tracking/notion-scan-links.json`

- [ ] **Step 1: Backfill via the Notion connector (MCP)**

Use the Notion MCP tools (`ToolSearch` for `notion-fetch` / `notion-search` if schemas not loaded). Fetch the parent page `https://www.notion.so/368b69da11c081968dfdf4e44f6000e0` and list its child pages. For each child titled `Weekly News Scan — YYYY-MM-DD`, record `{date, title, url}`.

Write `tracking/notion-scan-links.json` as a JSON array sorted by date ascending, e.g.:

```json
[
  {"date": "2026-05-29", "title": "Weekly News Scan — 2026-05-29", "url": "https://www.notion.so/<page-id>"},
  {"date": "2026-06-05", "title": "Weekly News Scan — 2026-06-05", "url": "https://www.notion.so/<page-id>"}
]
```

**Fallback if Notion MCP is unavailable in the executing session:** create the file as an empty array `[]`, and add to the final report: "Dom: paste the existing scan page URLs into tracking/notion-scan-links.json (date + title + url per entry)."

- [ ] **Step 2: Verify exporter picks them up**

Run: `python3 scripts/export_site_data.py && python3 -c "import json; print(json.load(open('site/data/scans.json')))"`
Expected: the backfilled entries, newest first; no orphan warnings for backfilled dates.

- [ ] **Step 3: Commit**

```bash
git add tracking/notion-scan-links.json
git commit -m "feat(site): backfill Notion scan links"
```

- [ ] **Step 4: Record the routine change for Dom (manual — cannot be done from this repo)**

Add to the final hand-back report, verbatim, for Dom to paste into the Cowork "Weekly scanner" routine's Step 4 instructions:

> After creating the Notion page, append an entry `{"date": "{YYYY-MM-DD}", "title": "Weekly News Scan — {YYYY-MM-DD}", "url": "<the created page URL>"}` to the JSON array in `tracking/notion-scan-links.json` (keep the array sorted by date), so it is included in the Step 5 commit.

---

### Task 9: Frontend shared assets (CSS, common.js, Chart.js vendor)

**Files:**
- Create: `site/css/terminal.css`
- Create: `site/js/common.js`
- Create: `site/js/vendor/chart.umd.js` (downloaded)

- [ ] **Step 1: Vendor Chart.js**

```bash
mkdir -p site/js/vendor
curl -fsSL https://cdn.jsdelivr.net/npm/chart.js@4.4.9/dist/chart.umd.js -o site/js/vendor/chart.umd.js
ls -la site/js/vendor/chart.umd.js
```

Expected: file ~200KB. If the pinned version 404s, use `https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.js`.

- [ ] **Step 2: Create `site/css/terminal.css`:**

```css
/* Terminal-dark theme — GitHub-dark palette, monospace, dense. */
:root {
  --bg: #0d1117; --panel: #161b22; --border: #30363d;
  --text: #e6edf3; --dim: #8b949e; --green: #3fb950; --red: #f85149;
  --accent: #58a6ff;
  --mono: "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: var(--mono); font-size: 14px; line-height: 1.5;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 16px 48px; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

nav {
  display: flex; gap: 18px; align-items: baseline;
  padding: 14px 0; border-bottom: 1px solid var(--border); margin-bottom: 20px;
}
nav .brand { font-weight: 700; letter-spacing: 1px; margin-right: auto; }
nav a { color: var(--dim); font-size: 13px; }
nav a.active { color: var(--text); border-bottom: 2px solid var(--green); }

.stat-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
.stat {
  flex: 1; min-width: 130px; background: var(--panel);
  border: 1px solid var(--border); border-radius: 6px; padding: 10px 12px;
}
.stat .v { font-size: 19px; font-weight: 700; }
.stat .k {
  font-size: 10px; color: var(--dim); text-transform: uppercase;
  letter-spacing: 1px; margin-top: 2px;
}

.panel {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 6px; padding: 14px; margin-bottom: 20px;
}
.panel h2 {
  margin: 0 0 10px; font-size: 12px; color: var(--dim);
  text-transform: uppercase; letter-spacing: 1px;
}

table { width: 100%; border-collapse: collapse; font-size: 13px; }
th {
  text-align: left; color: var(--dim); font-size: 10px;
  text-transform: uppercase; letter-spacing: 1px;
  border-bottom: 1px solid var(--border); padding: 4px 8px;
}
td { padding: 5px 8px; border-bottom: 1px solid #21262d; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
tr.clickable { cursor: pointer; }
tr.clickable:hover td { background: #1c2128; }

.pos { color: var(--green); }
.neg { color: var(--red); }
.dim { color: var(--dim); }

.badge {
  display: inline-block; font-size: 10px; padding: 1px 7px;
  border-radius: 10px; border: 1px solid var(--border); color: var(--dim);
}
.badge[data-layer="01"] { color: #f0b72f; border-color: #f0b72f44; }
.badge[data-layer="02"] { color: #e3b341; border-color: #e3b34144; }
.badge[data-layer="03"] { color: #58a6ff; border-color: #58a6ff44; }
.badge[data-layer="04"] { color: #bc8cff; border-color: #bc8cff44; }
.badge[data-layer="05"] { color: #d2a8ff; border-color: #d2a8ff44; }
.badge[data-layer="06"] { color: #3fb950; border-color: #3fb95044; }
.badge[data-layer="07"] { color: #56d4dd; border-color: #56d4dd44; }
.badge[data-layer="08"] { color: #ff9bce; border-color: #ff9bce44; }
.badge[data-layer="09"] { color: #79c0ff; border-color: #79c0ff44; }
.badge[data-layer="10"] { color: #ffa657; border-color: #ffa65744; }

.thesis-row td {
  background: #11151c; color: var(--dim); font-size: 12.5px;
  padding: 8px 12px 10px; border-left: 2px solid var(--green);
}
.chart-box { position: relative; height: 320px; }
.chart-box.compact { height: 200px; }
.toggles { display: flex; gap: 14px; margin-bottom: 10px; font-size: 12px; }
.toggles label { color: var(--dim); cursor: pointer; }
.error-note {
  color: var(--red); border: 1px dashed var(--red); border-radius: 6px;
  padding: 10px; font-size: 13px;
}
.footer { color: var(--dim); font-size: 11px; margin-top: 28px; }
select, .filter {
  background: var(--panel); color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; font-family: var(--mono); font-size: 13px; padding: 4px 8px;
}
```

- [ ] **Step 3: Create `site/js/common.js`:**

```javascript
/* Shared helpers: data loading, formatting, nav, chart defaults. */

async function loadJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}

function fmtMoney(v) {
  return '$' + Math.round(v).toLocaleString('en-US');
}

function fmtPct(v, digits = 2) {
  const s = (v * 100).toFixed(digits);
  return (v >= 0 ? '+' : '') + s + '%';
}

function pctClass(v) { return v >= 0 ? 'pos' : 'neg'; }

function el(tag, attrs = {}, html = '') {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  e.innerHTML = html;
  return e;
}

function esc(s) {
  return String(s).replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function showError(containerId, msg) {
  const c = document.getElementById(containerId);
  if (c) c.innerHTML = `<div class="error-note">data unavailable: ${esc(msg)}</div>`;
}

function renderNav(active) {
  const pages = [['index.html', 'Dashboard'], ['performance.html', 'Performance'],
    ['positions.html', 'Positions'], ['changes.html', 'Changes'],
    ['scans.html', 'Scans']];
  const nav = document.querySelector('nav');
  nav.innerHTML = '<span class="brand">AI SUPPLY CHAIN</span>' + pages.map(
    ([href, label]) =>
      `<a href="${href}" class="${href === active ? 'active' : ''}">${label}</a>`
  ).join('');
}

const CHART_COLORS = { model: '#3fb950', SMH: '#58a6ff', QQQ: '#bc8cff', EW: '#8b949e' };

function lineDataset(label, data, color, emphasized = false) {
  return { label, data, borderColor: color, backgroundColor: color,
    borderWidth: emphasized ? 2.2 : 1.2, pointRadius: 0, tension: 0.1 };
}

function baseChartOptions() {
  return {
    responsive: true, maintainAspectRatio: false, animation: false,
    interaction: { mode: 'index', intersect: false },
    plugins: { legend: { labels: { color: '#8b949e', boxWidth: 12,
      font: { family: 'Menlo, monospace', size: 11 } } } },
    scales: {
      x: { ticks: { color: '#8b949e', maxTicksLimit: 8,
             font: { family: 'Menlo, monospace', size: 10 } },
           grid: { color: '#21262d' } },
      y: { ticks: { color: '#8b949e',
             font: { family: 'Menlo, monospace', size: 10 },
             callback: v => '$' + v.toLocaleString() },
           grid: { color: '#21262d' } },
    },
  };
}
```

- [ ] **Step 4: Verify files parse (no tooling, so a syntax sanity check via node if present, else skip)**

Run: `node --check site/js/common.js 2>/dev/null && echo JS-OK || echo "node unavailable — skipped"`
Expected: `JS-OK` (or skip note).

- [ ] **Step 5: Commit**

```bash
git add site/css/terminal.css site/js/common.js site/js/vendor/chart.umd.js
git commit -m "feat(site): terminal-dark theme, shared JS, vendored Chart.js"
```

---

### Task 10: Dashboard page

**Files:**
- Create: `site/index.html`
- Create: `site/js/dashboard.js`

- [ ] **Step 1: Create `site/index.html`:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>AI Supply Chain — Dashboard</title>
<link rel="stylesheet" href="css/terminal.css">
</head>
<body>
<div class="wrap">
  <nav></nav>
  <div id="main">
    <div class="stat-row" id="stats"></div>
    <div class="panel">
      <h2>Performance — $10k model vs SMH (since inception)</h2>
      <div class="chart-box compact"><canvas id="chart"></canvas></div>
    </div>
    <div class="panel">
      <h2>Top positions</h2>
      <table id="top-positions"></table>
      <p style="margin:8px 0 0"><a href="positions.html">all positions →</a></p>
    </div>
    <div class="panel">
      <h2>Recent changes</h2>
      <table id="recent-changes"></table>
      <p style="margin:8px 0 0"><a href="changes.html">full change log →</a></p>
    </div>
  </div>
  <div class="footer" id="footer"></div>
</div>
<script src="js/vendor/chart.umd.js"></script>
<script src="js/common.js"></script>
<script src="js/dashboard.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `site/js/dashboard.js`:**

```javascript
renderNav('index.html');

(async () => {
  try {
    const [meta, perf, positions, changes] = await Promise.all([
      loadJSON('data/meta.json'), loadJSON('data/performance.json'),
      loadJSON('data/positions.json'), loadJSON('data/changes.json'),
    ]);

    const value = perf.model[perf.model.length - 1];
    const s = perf.summary;
    document.getElementById('stats').innerHTML = [
      [fmtMoney(value), 'Model value ($10k base)', pctClass(s.total_return)],
      [fmtPct(s.total_return), 'Since inception', pctClass(s.total_return)],
      [fmtPct(s.vs_smh), 'vs SMH', pctClass(s.vs_smh)],
      [String(meta.holdings), 'Holdings', ''],
      [meta.as_of, 'Data as of', 'dim'],
    ].map(([v, k, cls]) =>
      `<div class="stat"><div class="v ${cls}">${v}</div><div class="k">${k}</div></div>`
    ).join('');

    new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: perf.dates, datasets: [
        lineDataset('Model', perf.model, CHART_COLORS.model, true),
        lineDataset('SMH', perf.bench.SMH, CHART_COLORS.SMH),
      ]},
      options: baseChartOptions(),
    });

    const top = [...positions].sort((a, b) => b.weight - a.weight).slice(0, 5);
    document.getElementById('top-positions').innerHTML =
      '<tr><th>Ticker</th><th>Layer</th><th class="num">Weight</th>' +
      '<th class="num">Score</th><th>Tier</th></tr>' +
      top.map(p => `<tr>
        <td><b>${esc(p.ticker)}</b> <span class="dim">${esc(p.company)}</span></td>
        <td><span class="badge" data-layer="${p.layer_num}">${esc(p.layer)}</span></td>
        <td class="num">${p.weight.toFixed(1)}%</td>
        <td class="num">${p.score.toFixed(1)}</td><td>${esc(p.tier)}</td></tr>`).join('');

    document.getElementById('recent-changes').innerHTML =
      changes.slice(0, 3).map(c => `<tr>
        <td class="dim">${c.date}</td><td><b>${esc(c.ticker || '—')}</b></td>
        <td>${esc(c.type)}${c.detail ? ' <span class="dim">' + esc(c.detail) + '</span>' : ''}</td>
        <td class="dim">${esc(c.note || '')}</td></tr>`).join('');

    document.getElementById('footer').textContent =
      `$10,000 notional base · not investment advice · generated ${meta.generated_at}`;
  } catch (e) {
    showError('main', e.message);
  }
})();
```

- [ ] **Step 3: Verify in a local server**

Run: `python3 scripts/export_site_data.py && python3 -m http.server 8765 --directory site & SRV=$!; sleep 1; curl -s http://localhost:8765/index.html | grep -c "dashboard.js"; curl -s http://localhost:8765/data/meta.json | head -c 120; kill $SRV`
Expected: `1` and the meta JSON snippet. Then open `http://localhost:8765` in a browser manually if available: stat row, chart, tables render; no console errors.

- [ ] **Step 4: Commit**

```bash
git add site/index.html site/js/dashboard.js
git commit -m "feat(site): dashboard page"
```

---

### Task 11: Sub-pages (performance, positions, changes, scans)

**Files:**
- Create: `site/performance.html`, `site/js/performance.js`
- Create: `site/positions.html`, `site/js/positions.js`
- Create: `site/changes.html`, `site/js/changes.js`
- Create: `site/scans.html`, `site/js/scans.js`

All four HTML files share the dashboard's skeleton. Only `<title>`, the `#main` contents, and the page JS file differ — copy `site/index.html` and replace those parts exactly as shown.

- [ ] **Step 1: Create `site/performance.html`** — `#main` becomes:

```html
  <div id="main">
    <div class="panel">
      <h2>$10k model vs benchmarks (since inception 2026-05-26)</h2>
      <div class="toggles" id="toggles"></div>
      <div class="chart-box"><canvas id="chart"></canvas></div>
    </div>
    <div class="panel">
      <h2>Monthly returns</h2>
      <table id="monthly"></table>
    </div>
  </div>
```

with `<title>AI Supply Chain — Performance</title>` and `<script src="js/performance.js"></script>` as the last script.

- [ ] **Step 2: Create `site/js/performance.js`:**

```javascript
renderNav('performance.html');

(async () => {
  try {
    const perf = await loadJSON('data/performance.json');
    const series = [
      ['Model', perf.model, CHART_COLORS.model, true],
      ['SMH', perf.bench.SMH, CHART_COLORS.SMH, false],
      ['QQQ', perf.bench.QQQ, CHART_COLORS.QQQ, false],
      ['EW universe', perf.bench.EW, CHART_COLORS.EW, false],
    ];
    const chart = new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: perf.dates,
        datasets: series.map(([l, d, c, em]) => lineDataset(l, d, c, em)) },
      options: { ...baseChartOptions(),
        plugins: { legend: { display: false } } },
    });

    document.getElementById('toggles').innerHTML = series.map(([l], i) =>
      `<label><input type="checkbox" data-i="${i}" checked> ${l}</label>`).join('');
    document.getElementById('toggles').addEventListener('change', e => {
      const i = Number(e.target.dataset.i);
      chart.setDatasetVisibility(i, e.target.checked);
      chart.update();
    });

    document.getElementById('monthly').innerHTML =
      '<tr><th>Month</th><th class="num">Model</th><th class="num">SMH</th>' +
      '<th class="num">QQQ</th></tr>' +
      perf.monthly.map(m => `<tr><td>${m.month}</td>
        <td class="num ${pctClass(m.model)}">${fmtPct(m.model)}</td>
        <td class="num ${pctClass(m.SMH)}">${fmtPct(m.SMH)}</td>
        <td class="num ${pctClass(m.QQQ)}">${fmtPct(m.QQQ)}</td></tr>`).join('');
  } catch (e) { showError('main', e.message); }
})();
```

- [ ] **Step 3: Create `site/positions.html`** — `#main` becomes:

```html
  <div id="main">
    <div class="panel">
      <h2>All holdings — click a row for the thesis</h2>
      <table id="positions"></table>
    </div>
  </div>
```

with `<title>AI Supply Chain — Positions</title>` and `<script src="js/positions.js"></script>`. The Chart.js script tag may be dropped on this page and the next two.

- [ ] **Step 4: Create `site/js/positions.js`:**

```javascript
renderNav('positions.html');

(async () => {
  try {
    const [positions, theses] = await Promise.all([
      loadJSON('data/positions.json'), loadJSON('data/theses.json')]);
    const rows = [...positions].sort((a, b) => b.weight - a.weight);
    const table = document.getElementById('positions');
    table.innerHTML =
      '<tr><th>Ticker</th><th>Company</th><th>Layer</th>' +
      '<th class="num">Weight</th><th class="num">Notional</th>' +
      '<th class="num">Score</th><th>Tier</th></tr>';
    for (const p of rows) {
      const thesis = theses[p.ticker];
      const tr = el('tr', thesis ? { class: 'clickable' } : {}, `
        <td><b>${esc(p.ticker)}</b>${thesis ? ' <span class="dim">▸</span>' : ''}</td>
        <td class="dim">${esc(p.company)}</td>
        <td><span class="badge" data-layer="${p.layer_num}">${esc(p.layer)}</span></td>
        <td class="num">${p.weight.toFixed(1)}%</td>
        <td class="num">${fmtMoney(p.notional)}</td>
        <td class="num">${p.score.toFixed(1)}</td><td>${esc(p.tier)}</td>`);
      table.appendChild(tr);
      if (thesis) {
        const detail = el('tr', { class: 'thesis-row', hidden: '' },
          `<td colspan="7">${esc(thesis)}</td>`);
        table.appendChild(detail);
        tr.addEventListener('click', () => detail.toggleAttribute('hidden'));
      }
    }
  } catch (e) { showError('main', e.message); }
})();
```

- [ ] **Step 5: Create `site/changes.html`** — `#main` becomes:

```html
  <div id="main">
    <div class="panel">
      <h2>Change log
        <select id="filter" class="filter" style="float:right">
          <option value="">all types</option>
          <option value="add">add</option><option value="drop">drop</option>
          <option value="resize">resize</option><option value="rerate">rerate</option>
          <option value="inception">inception</option>
        </select>
      </h2>
      <table id="changes"></table>
    </div>
  </div>
```

with `<title>AI Supply Chain — Changes</title>` and `<script src="js/changes.js"></script>`.

- [ ] **Step 6: Create `site/js/changes.js`:**

```javascript
renderNav('changes.html');

(async () => {
  try {
    const changes = await loadJSON('data/changes.json');
    const render = (type) => {
      document.getElementById('changes').innerHTML =
        '<tr><th>Date</th><th>Ticker</th><th>Type</th><th>Detail</th></tr>' +
        changes.filter(c => !type || c.type === type).map(c => `<tr>
          <td class="dim">${c.date}</td><td><b>${esc(c.ticker || '—')}</b></td>
          <td>${esc(c.type)}</td>
          <td class="dim">${c.detail ? esc(c.detail) + ' — ' : ''}${esc(c.note || '')}</td>
        </tr>`).join('');
    };
    render('');
    document.getElementById('filter').addEventListener('change',
      e => render(e.target.value));
  } catch (e) { showError('main', e.message); }
})();
```

- [ ] **Step 7: Create `site/scans.html`** — `#main` becomes:

```html
  <div id="main">
    <div class="panel">
      <h2>Weekly news scans (opens in Notion)</h2>
      <table id="scans"></table>
    </div>
  </div>
```

with `<title>AI Supply Chain — Weekly Scans</title>` and `<script src="js/scans.js"></script>`.

- [ ] **Step 8: Create `site/js/scans.js`:**

```javascript
renderNav('scans.html');

(async () => {
  try {
    const scans = await loadJSON('data/scans.json');
    document.getElementById('scans').innerHTML = scans.length
      ? scans.map(s => `<tr><td class="dim">${s.date}</td>
          <td><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)} ↗</a></td></tr>`).join('')
      : '<tr><td class="dim">no scans linked yet</td></tr>';
  } catch (e) { showError('main', e.message); }
})();
```

- [ ] **Step 9: Verify all pages serve**

Run: `python3 -m http.server 8765 --directory site & SRV=$!; sleep 1; for p in index performance positions changes scans; do echo "$p: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8765/$p.html)"; done; kill $SRV`
Expected: five `200`s. Open in a browser if available and click through all pages — no console errors, thesis rows expand, filter works, toggles work.

- [ ] **Step 10: Commit**

```bash
git add site/*.html site/js/*.js
git commit -m "feat(site): performance, positions, changes, scans pages"
```

---

### Task 12: Smoke checker (`scripts/check_site.py`)

**Files:**
- Create: `scripts/check_site.py`

- [ ] **Step 1: Create `scripts/check_site.py`:**

```python
"""Post-export smoke check: data sanity + dead-reference scan.

Run after export_site_data.py, before deploy. Exit 1 on any failure.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'

REQUIRED = {
    'positions.json': list, 'performance.json': dict, 'changes.json': list,
    'theses.json': dict, 'scans.json': list, 'meta.json': dict,
}

errors: list[str] = []

for name, typ in REQUIRED.items():
    p = SITE / 'data' / name
    if not p.exists():
        errors.append(f'missing {p}')
        continue
    data = json.loads(p.read_text())
    if not isinstance(data, typ):
        errors.append(f'{name}: expected {typ.__name__}')

pos_file = SITE / 'data' / 'positions.json'
if pos_file.exists():
    pos = json.loads(pos_file.read_text())
    total = sum(p['notional'] for p in pos)
    if abs(total - 10000) > 150:
        errors.append(f'notional sum {total} not ~10000')

perf_file = SITE / 'data' / 'performance.json'
if perf_file.exists():
    perf = json.loads(perf_file.read_text())
    n = len(perf['dates'])
    for key in ('model',):
        if len(perf[key]) != n:
            errors.append(f'performance.{key} length mismatch')
    for bname, series in perf['bench'].items():
        if len(series) != n:
            errors.append(f'performance.bench.{bname} length mismatch')

# Dead-reference scan: every local src/href in the HTML must exist.
for html in SITE.glob('*.html'):
    for ref in re.findall(r'(?:src|href)="([^"#]+)"', html.read_text()):
        if ref.startswith(('http', 'mailto')):
            continue
        if not (SITE / ref).exists():
            errors.append(f'{html.name}: dead reference {ref}')

# Page JS must only fetch data files that the exporter writes.
for js in SITE.glob('js/*.js'):
    for ref in re.findall(r"loadJSON\('([^']+)'\)", js.read_text()):
        if not (SITE / ref).exists():
            errors.append(f'{js.name}: fetches missing {ref}')

if errors:
    print('SMOKE CHECK FAILED:', file=sys.stderr)
    for e in errors:
        print(f'  - {e}', file=sys.stderr)
    sys.exit(1)
print(f'smoke check OK ({len(list(SITE.glob("*.html")))} pages, '
      f'{len(REQUIRED)} data files)')
```

- [ ] **Step 2: Run it**

Run: `python3 scripts/export_site_data.py && python3 scripts/check_site.py`
Expected: `smoke check OK (5 pages, 6 data files)`.

- [ ] **Step 3: Prove it catches a dead reference**

Run: `sed -i '' 's|js/dashboard.js|js/dashboardX.js|' site/index.html && python3 scripts/check_site.py; sed -i '' 's|js/dashboardX.js|js/dashboard.js|' site/index.html`
Expected: `SMOKE CHECK FAILED` with the dead reference listed (then restored).

- [ ] **Step 4: Commit**

```bash
git add scripts/check_site.py
git commit -m "feat(site): smoke checker for exported site"
```

---

### Task 13: Password gate (`site/_worker.js`)

Advanced-mode Pages worker (definitely bundled by `wrangler pages deploy site`): gates every route including `/data/*.json`. Cookie = SHA-256 of the password + constant salt; password lives in the `SITE_PASSWORD` env var on Cloudflare, never in the repo.

**Files:**
- Create: `site/_worker.js`

- [ ] **Step 1: Create `site/_worker.js`:**

```javascript
/* Shared-password gate for the whole site (Cloudflare Pages advanced mode).
   SITE_PASSWORD is a Cloudflare Pages environment variable / secret. */

const COOKIE = 'gate';

async function token(env) {
  const data = new TextEncoder().encode(`${env.SITE_PASSWORD}|gate-v1`);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, '0')).join('');
}

function loginPage(msg) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>AI Supply Chain</title>
<style>
body{margin:0;background:#0d1117;color:#e6edf3;font-family:Menlo,monospace;
display:flex;align-items:center;justify-content:center;min-height:100vh}
form{background:#161b22;border:1px solid #30363d;border-radius:6px;
padding:28px;width:300px}
h1{font-size:14px;letter-spacing:1px;margin:0 0 16px}
input{width:100%;box-sizing:border-box;background:#0d1117;color:#e6edf3;
border:1px solid #30363d;border-radius:6px;padding:8px;font-family:inherit}
button{margin-top:10px;width:100%;background:#238636;color:#fff;border:0;
border-radius:6px;padding:8px;font-family:inherit;cursor:pointer}
.err{color:#f85149;font-size:12px;margin-top:8px}
</style></head><body>
<form method="POST" action="/login">
<h1>AI SUPPLY CHAIN</h1>
<input type="password" name="password" placeholder="password" autofocus>
<button>enter</button>${msg ? `<div class="err">${msg}</div>` : ''}
</form></body></html>`;
}

export default {
  async fetch(request, env) {
    if (!env.SITE_PASSWORD) {
      return new Response('SITE_PASSWORD not configured', { status: 500 });
    }
    const url = new URL(request.url);
    const expected = await token(env);
    const cookies = request.headers.get('Cookie') || '';

    if (cookies.includes(`${COOKIE}=${expected}`)) {
      return env.ASSETS.fetch(request);
    }
    if (request.method === 'POST' && url.pathname === '/login') {
      const form = await request.formData();
      if (form.get('password') === env.SITE_PASSWORD) {
        return new Response(null, {
          status: 302,
          headers: {
            'Location': '/',
            'Set-Cookie': `${COOKIE}=${expected}; HttpOnly; Secure; ` +
                          'SameSite=Lax; Max-Age=31536000; Path=/',
          },
        });
      }
      return new Response(loginPage('wrong password'), {
        status: 401, headers: { 'Content-Type': 'text/html' } });
    }
    return new Response(loginPage(''), {
      status: 401, headers: { 'Content-Type': 'text/html' } });
  },
};
```

- [ ] **Step 2: Test locally with wrangler**

Run: `cd /Users/dom/Desktop/ai-stocks && npx wrangler pages dev site --binding SITE_PASSWORD=testpw --port 8788` (background it), then:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8788/            # expect 401
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8788/data/meta.json   # expect 401 (data gated too)
curl -s -D - -o /dev/null -X POST -d 'password=testpw' http://localhost:8788/login | grep -i 'set-cookie\|HTTP/'   # expect 302 + Set-Cookie gate=...
COOKIE=$(curl -s -D - -o /dev/null -X POST -d 'password=testpw' http://localhost:8788/login | grep -io 'gate=[a-f0-9]*')
curl -s -o /dev/null -w '%{http_code}\n' -H "Cookie: $COOKIE" http://localhost:8788/   # expect 200
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'password=wrong' http://localhost:8788/login  # expect 401
```

Then kill the dev server. (`npx wrangler` will prompt to install wrangler on first use — accept; no package.json needed.)

- [ ] **Step 3: Commit**

```bash
git add site/_worker.js
git commit -m "feat(site): shared-password gate (Pages advanced-mode worker)"
```

---

### Task 14: CI workflow + Cloudflare setup

**Files:**
- Create: `.github/workflows/deploy-site.yml`

- [ ] **Step 1: Create `.github/workflows/deploy-site.yml`:**

```yaml
name: Deploy portfolio site

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install openpyxl pytest
      - run: python -m pytest tests -q
      - run: python scripts/export_site_data.py
      - run: python scripts/check_site.py
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy site --project-name=ai-supply-chain
```

Note: CI installs only `openpyxl pytest` — the exporter and tests must not import yfinance/pandas (they don't; the series builder runs only in the weekly pipeline, which is the design).

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/deploy-site.yml
git commit -m "ci(site): test, export, check, deploy to Cloudflare Pages"
```

- [ ] **Step 3: One-time Cloudflare setup (document in final report — needs Dom's accounts)**

Include these exact steps in the hand-back report:

1. Create/log into a Cloudflare account → `npx wrangler login`.
2. `npx wrangler pages project create ai-supply-chain` (production branch: `main`).
3. Set the password: `npx wrangler pages secret put SITE_PASSWORD --project-name ai-supply-chain` (or Dashboard → Workers & Pages → ai-supply-chain → Settings → Variables and Secrets).
4. Create an API token (Dashboard → My Profile → API Tokens → "Edit Cloudflare Workers" template, scoped to the account) and add GitHub repo secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` (account ID is on the dashboard right sidebar).
5. Merge this branch to `main` (the deploy workflow only triggers there); first deploy can also be run manually: `python3 scripts/export_site_data.py && npx wrangler pages deploy site --project-name=ai-supply-chain`.
6. Paste the routine instruction line from Task 8 Step 4 into the Cowork "Weekly scanner" routine.
7. Share `https://ai-supply-chain.pages.dev` + the password with friends.

---

### Task 15: Documentation

**Files:**
- Modify: `CLAUDE.md` (folder structure section + a new short section)

- [ ] **Step 1: Update CLAUDE.md folder structure** — add to the tree after `templates/`:

```
  site/                               # Friend-facing static site (see §Portfolio site)
  tests/                              # pytest suite (site exporter)
```

- [ ] **Step 2: Add a section after "## Subagent patterns":**

```markdown
## Portfolio site (added 2026-06-10)

A password-gated static site for close friends: `site/` on Cloudflare Pages,
deployed by `.github/workflows/deploy-site.yml` on push to `main`.

- **Privacy boundary:** `scripts/export_site_data.py` is the ONLY path from
  repo data to `site/data/`. All dollars are scaled to a $10,000 notional
  base; real capital, share counts, and cost basis are excluded by design.
  `tests/test_export_site_data.py::test_privacy_no_real_dollars_anywhere` is
  the regression gate — never weaken it.
- **Performance series:** `tracking/performance-series.json` is written by
  `track_performance.py` (weekly pipeline) so CI needs no network/yfinance.
- **Scan links:** `tracking/notion-scan-links.json` maps scan dates to Notion
  URLs; the Cowork weekly routine appends to it.
- The spec lives at `docs/superpowers/specs/2026-06-10-portfolio-site-design.md`.
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: portfolio site conventions in CLAUDE.md"
```

---

## Final verification (after all tasks)

```bash
python3 -m pytest tests -q                 # 13 PASS
python3 scripts/export_site_data.py        # 6 files + expected WARNs
python3 scripts/check_site.py              # smoke check OK
git log --oneline -15                      # one commit per task step-group
```

Then hand back to Dom with: the Cloudflare setup steps (Task 14 Step 3), the routine instruction line (Task 8 Step 4), and the list of holdings whose thesis is still the template (so populating them makes snippets appear).
