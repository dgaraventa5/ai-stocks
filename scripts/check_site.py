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
    for key in ('dates', 'model', 'bench', 'summary', 'monthly', 'as_of'):
        if key not in perf:
            errors.append(f'performance.json missing key {key}')
    if not all(k in perf for k in ('dates', 'model', 'bench')):
        perf = None
    if perf is not None:
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
