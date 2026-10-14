"""Is the performance series caught up to the last closed trading session?

Root cause (2026-10-13): Yahoo publishes a session's daily bar roughly 5-6
hours after the 16:00 ET close (observed: absent at 21:20 ET, present by
21:55 ET). The daily-refresh workflow's early runs rebuilt the series before
the bar existed, re-published the prior day, and reported success — so the
dashboard sat a day behind while every run was green. This check makes that
state visible: it warns on any run that ends behind, and `--strict` (the last
scheduled run of the night) fails so a missed day turns the workflow red.

Stdlib only (uses trading_calendar) so it runs in any CI environment.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trading_calendar import close_utc, is_trading_day  # noqa: E402

SERIES = Path(__file__).resolve().parent.parent / 'tracking' / 'performance-series.json'


def last_closed_session(now: dt.datetime) -> dt.date:
    """Most recent trading day whose 16:00 ET close is at or before `now`."""
    d = now.astimezone(dt.timezone.utc).date() + dt.timedelta(days=1)
    while not (is_trading_day(d) and close_utc(d) <= now):
        d -= dt.timedelta(days=1)
    return d


def check(as_of: str, now: dt.datetime) -> tuple[bool, str]:
    """(fresh?, message) for a series whose last bar is `as_of`."""
    expected = last_closed_session(now)
    have = dt.date.fromisoformat(as_of)
    if have >= expected:
        return True, f'series is current: as_of {as_of} (last closed session {expected})'
    return False, (f'series as_of {as_of} is behind the last closed session '
                   f'{expected} — Yahoo has not published that bar yet')


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--series', type=Path, default=SERIES)
    ap.add_argument('--strict', action='store_true',
                    help='exit 1 when behind (use on the final run of the night)')
    args = ap.parse_args(argv)
    as_of = json.loads(args.series.read_text())['as_of']
    fresh, msg = check(as_of, dt.datetime.now(dt.timezone.utc))
    if fresh:
        print(msg)
        return 0
    level = 'error' if args.strict else 'warning'
    print(f'::{level}::{msg}')
    return 1 if args.strict else 0


if __name__ == '__main__':
    sys.exit(main())
