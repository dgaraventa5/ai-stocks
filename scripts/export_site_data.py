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


def export_performance(root: Path) -> dict:
    sp = root / 'tracking' / 'performance-series.json'
    if not sp.exists():
        fail('tracking/performance-series.json missing — run '
             'scripts/track_performance.py first')
    raw = json.loads(sp.read_text())
    cfg = json.loads(
        (root / 'tracking' / 'performance-config.json').read_text())
    for key in ('dates', 'model', 'bench', 'as_of'):
        if key not in raw:
            fail(f'performance-series.json missing key {key!r}')
    for b in ('SMH', 'QQQ', 'EW'):
        if b not in raw['bench']:
            fail(f'performance-series.json bench missing {b!r}')
    if not raw['model']:
        fail('performance-series.json has an empty series')
    if 'capital' not in cfg:
        fail('performance-config.json missing capital')
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
