"""Point-in-time score panel (spec 2026-08-07 Part C2).

Every scoring pass appends the full ranked watchlist to
tracking/score-history.csv — the panel that the future IC test, band analysis
and any cutoff/backtest work require (backfill is impossible, which is why
logging starts now and never skips a pass). Append-only: one snapshot per
date; re-running a pass the same day is a no-op (first pass of the day wins),
and committed rows are never rewritten.
"""
from __future__ import annotations

import datetime as dt

from common import ROOT

CSV = ROOT / 'tracking' / 'score-history.csv'
HEADER = 'date,ticker,total_score,rank,tier\n'


def append_snapshot(results, when: str | None = None) -> int:
    """Append one `date,ticker,total_score,rank,tier` row per scored name.

    results: recalc_watchlist.recalc() output. Returns rows appended (0 when
    `when` is already logged — idempotent re-runs, no duplicates, no rewrite).
    """
    when = when or dt.date.today().isoformat()
    live = sorted((x for x in results if x.get('TOTAL') is not None),
                  key=lambda x: -x['TOTAL'])
    if not live:
        return 0
    if CSV.exists():
        with CSV.open() as f:
            if any(line.startswith(when + ',') for line in f):
                return 0
    else:
        CSV.write_text(HEADER)
    with CSV.open('a') as f:
        for i, x in enumerate(live):
            f.write(f"{when},{x['ticker']},{x['TOTAL']:.2f},{i + 1},"
                    f"{x['Tier'] or ''}\n")
    return len(live)
