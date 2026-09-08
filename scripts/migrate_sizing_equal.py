"""One-time sizing flip: inverse-vol -> equal weight (2026-09-08, Dom-gated).

Default run: print the before/after table (ticker, current weight, equal
target, delta) and the one-way turnover. WRITES NOTHING.

--apply (run ONLY on Dom's approval): stamp a rule-32 methodology seam,
seed the INVVOL_ROSTER shadow with the live book's final inverse-vol
allocations (so the shadow starts exactly where the model leaves off),
flip tracking/portfolio-config.json sizing.mode to "equal", then run
refresh_targets.refresh(resize=True, migration='sizing_migration_equal')
so the book re-sizes in ONE event — the seam in the history; nothing is
restated. Selection (rank N/M), the sizing params (still feeding the
shadow) and the band shadows are untouched.

Why (CLAUDE.md rule 33): a prior-driven decision, not a data verdict —
the 20-bar post-migration gap vs the equal-weight twin was noise (t≈-0.25),
but inverse-vol structurally underweights the high-beta names this universe
is selected for, and the v2 spec itself only ever rated inverse-vol a "lean".
"""
from __future__ import annotations

import argparse
import datetime as dt
import json

from portfolio_model import PCONFIG, current_weights, load_cfg, save_cfg
from position_sizing import equal_weights
import refresh_targets as rt

KIND = 'sizing_migration_equal'
SEAM_REASON = ('sizing flip: inverse-vol -> equal weight (rule 33, '
               'prior-driven; inverse-vol retired to INVVOL_ROSTER shadow)')


def seed_invvol_shadow(cfg: dict, today: str) -> dict:
    """First INVVOL_ROSTER event = the last live event's allocations as
    weights (cash excluded), dated today. Same-day re-runs replace; an
    existing shadow from another date is refused, never clobbered."""
    last = cfg['events'][-1]
    alloc = last['allocations']
    tot = sum(alloc.values())
    ev = {'date': today, 'roster': sorted(alloc),
          'weights': {t: round(v / tot, 6) for t, v in sorted(alloc.items())}}
    evs = cfg.setdefault('shadow_events', {}).setdefault('INVVOL_ROSTER', [])
    if evs and evs[-1]['date'] != today:
        raise ValueError(f'INVVOL_ROSTER already seeded ({evs[-1]["date"]}); '
                         f'refusing to clobber')
    if evs:
        evs[-1] = ev
    else:
        evs.append(ev)
    return ev


def build_table() -> None:
    cfg = load_cfg()
    last = cfg['events'][-1]
    held = sorted(last['allocations'])
    cur = current_weights(cfg)
    if cur is None:
        # No bar on/after the last event yet (holiday / same-day event):
        # the book has not drifted from its logged allocations.
        tot = sum(last['allocations'].values()) + float(last.get('cash', 0))
        cur = {t: a / tot for t, a in last['allocations'].items()}
        print('(no post-event bar — current weights = last event allocations)')
    eq = equal_weights(held)
    print(f'Equal-weight migration table — {len(held)} names @ '
          f'{100 / len(held):.2f}% each. NOTHING APPLIED.\n')
    print(f'{"Tkr":<7}{"Now %":>7}{"EW %":>7}{"Δ":>7}')
    turnover = 0.0
    for t in sorted(held, key=lambda t: -cur.get(t, 0.0)):
        now, new = cur.get(t, 0.0) * 100, eq[t] * 100
        turnover += abs(new - now)
        print(f'{t:<7}{now:>7.2f}{new:>7.2f}{new - now:>+7.2f}')
    print(f'\none-way turnover ≈ {turnover / 2:.1f}% of book')
    print(f'last event: {last["date"]} {last.get("kind")} — {last["reason"]}')
    print('\nApprove with: python3 scripts/migrate_sizing_equal.py --apply')


def apply() -> None:
    today = dt.date.today().isoformat()
    seam = rt.stamp_seam(SEAM_REASON)
    print(f'methodology seam stamped: {seam["date"]} — {seam["reason"]}')
    cfg = load_cfg()
    ev = seed_invvol_shadow(cfg, today)
    save_cfg(cfg)
    print(f'INVVOL_ROSTER seeded: {ev["date"]}, {len(ev["roster"])} names')
    pcfg = json.loads(PCONFIG.read_text())
    prev = pcfg.setdefault('sizing', {}).get('mode')
    pcfg['sizing']['mode'] = 'equal'
    PCONFIG.write_text(json.dumps(pcfg, indent=2) + '\n')
    print(f'sizing mode flipped: {prev} -> equal')
    rt.refresh(resize=True, migration=KIND)   # logs the one migration event


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='sizing flip to equal weight: print the table (default) '
                    'or apply it')
    ap.add_argument('--apply', action='store_true',
                    help='DOM-GATED: stamp seam, seed INVVOL_ROSTER, flip '
                         'sizing.mode=equal, re-size the live book in one '
                         f'{KIND} event')
    args = ap.parse_args()
    apply() if args.apply else build_table()
