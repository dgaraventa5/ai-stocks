"""Backfill the alternative-build trackers (MODEL_TOP25, VQR70_TOP15,
VQR70_TOP25) from 2026-08-11 to the day before live tracking began
(Dom, 2026-11-21; CLAUDE.md rule 28 amendment).

Every backfilled roster event is marked ``"rebuilt": true``; the site draws
that stretch dashed. Two sources, of different quality:

- MODEL_TOP25 is point-in-time: the top 25 tradable names by total score as
  recorded in tracking/score-history.csv on each scoring date.
- VQR70_TOP15/25 are REBUILT: the score panel keeps totals only, so the
  category scores come from re-running TODAY's recalc code on the workbook
  and reverse-dcf.json as committed on origin/main on or before each date.
  Later methodology fixes therefore leak backwards (partly hindsight), and
  V/Q/R was chosen on this same window. Read the dashed part as context.

Each roster takes effect the day AFTER its scoring date (no same-day
look-ahead). Consecutive identical rosters are collapsed.

Default is a dry run; --write replaces any earlier rebuilt events in
tracking/performance-config.json and leaves live events untouched.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

START = '2026-08-11'
NAMES = ('MODEL_TOP25', 'VQR70_TOP15', 'VQR70_TOP25')
WB = '00-master/ai_supply_chain_scoring.xlsx'
RDCF = '00-master/reverse-dcf.json'


def _git(*args: str) -> bytes:
    return subprocess.run(['git', '-C', str(ROOT), *args], check=True,
                          capture_output=True).stdout


def _commit_on_or_before(path: str, day: str, ref: str) -> str | None:
    out = _git('rev-list', '-1', f'--before={day} 23:59:59', ref, '--',
               path).decode().strip()
    return out or None


def score_dates(first_live: str) -> list[str]:
    with open(ROOT / 'tracking' / 'score-history.csv') as f:
        days = {r['date'] for r in csv.DictReader(f)}
    return sorted(d for d in days if START <= d < first_live)


def model_top25(day: str) -> list[str]:
    from portfolio_sizing import is_tradable
    with open(ROOT / 'tracking' / 'score-history.csv') as f:
        rows = [r for r in csv.DictReader(f)
                if r['date'] == day and r['total_score']
                and is_tradable(r['ticker'])]
    rows.sort(key=lambda r: (-float(r['total_score']), r['ticker']))
    return [r['ticker'] for r in rows[:25]]


def vqr_rosters(day: str, ref: str, tmp: Path, cache: dict) -> dict:
    import recalc_watchlist as rw
    import refresh_targets as rt
    from portfolio_sizing import is_tradable
    key = (_commit_on_or_before(WB, day, ref),
           _commit_on_or_before(RDCF, day, ref))
    if key[0] is None:
        raise SystemExit(f'no workbook commit on or before {day}')
    if key not in cache:
        d = tmp / f'snap{len(cache)}'
        (d / '00-master').mkdir(parents=True)
        (d / WB).write_bytes(_git('show', f'{key[0]}:{WB}'))
        if key[1]:
            (d / RDCF).write_bytes(_git('show', f'{key[1]}:{RDCF}'))
        saved = rw._REPO_ROOT
        rw._REPO_ROOT = d             # reverse-dcf.json as of that date
        try:
            rows = rw.recalc(str(d / WB))
        finally:
            rw._REPO_ROOT = saved
        live = [x for x in rows
                if x['TOTAL'] is not None and is_tradable(x['ticker'])]
        cache[key] = rt.alt_build_rosters(live)
    return cache[key]


def build_events(first_live: str, ref: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {n: [] for n in NAMES}
    cache: dict = {}
    with tempfile.TemporaryDirectory() as t:
        for day in score_dates(first_live):
            eff = (dt.date.fromisoformat(day)
                   + dt.timedelta(days=1)).isoformat()
            if eff >= first_live:
                continue
            rosters = dict(vqr_rosters(day, ref, Path(t), cache))
            rosters['MODEL_TOP25'] = model_top25(day)
            for n in NAMES:
                evs = out[n]
                if rosters[n] and (not evs or
                                   sorted(evs[-1]['roster']) != sorted(rosters[n])):
                    evs.append({'date': eff, 'roster': rosters[n],
                                'rebuilt': True, 'scored': day})
    return out


def merge(cfg: dict, rebuilt: dict[str, list[dict]]) -> None:
    sh = cfg.setdefault('shadow_events', {})
    for n, evs in rebuilt.items():
        live = [e for e in sh.get(n, []) if not e.get('rebuilt')]
        if live and evs and evs[-1]['date'] >= live[0]['date']:
            raise SystemExit(f'{n}: rebuilt events overlap live tracking')
        sh[n] = evs + live


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--write', action='store_true',
                    help='save to tracking/performance-config.json')
    ap.add_argument('--ref', default='origin/main',
                    help='git ref whose history supplies past workbooks')
    a = ap.parse_args()
    from portfolio_model import load_cfg, save_cfg
    cfg = load_cfg()
    firsts = [next((e['date'] for e in cfg.get('shadow_events', {}).get(n, [])
                    if not e.get('rebuilt')), None) for n in NAMES]
    if None in firsts:
        raise SystemExit('live tracking has not started for every build')
    first_live = min(firsts)
    rebuilt = build_events(first_live, a.ref)
    for n, evs in rebuilt.items():
        print(f'{n}: {len(evs)} rebuilt rosters, '
              f'{evs[0]["date"] if evs else "-"} .. '
              f'{evs[-1]["date"] if evs else "-"} (live from {first_live})')
    if a.write:
        merge(cfg, rebuilt)
        save_cfg(cfg)
        print('written to tracking/performance-config.json')
    else:
        print('(dry run; --write to save)')


if __name__ == '__main__':
    main()
