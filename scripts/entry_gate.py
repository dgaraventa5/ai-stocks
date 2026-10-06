"""Entry gate (rule 35, 2026-10-06): research-before-entry.

A score built from quarterly filings and 1-5 ratings cannot react to an event
that landed yesterday. Twice in two days the model would have bought a name the
day after such an event (SBGSY's $22.6B acquisition, APP's county enforcement
action). The gate touches ENTRIES only — never scores, ranks, or held names:

  * a name may not enter without a context briefing newer than `max_age` days;
  * a name may not enter while it has an unexpired hold in
    00-master/entry-holds.json (human-written, like eps-yoy-overrides.json).

Deferred, not cancelled: when the hold expires or a fresh briefing lands, the
name enters on the next run if it still ranks. Pure, offline, stdlib only.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

HOLDS_FILE = Path('00-master') / 'entry-holds.json'
_BRIEFING = re.compile(r'^context-(\d{4}-\d{2}-\d{2})\.md$')


def latest_briefing_date(root: Path, ticker: str) -> dt.date | None:
    """Newest per-stock/{ticker}/context-YYYY-MM-DD.md date, or None."""
    d = Path(root) / 'per-stock' / ticker
    if not d.is_dir():
        return None
    dates = []
    for f in d.iterdir():
        m = _BRIEFING.match(f.name)
        if m:
            try:
                dates.append(dt.date.fromisoformat(m.group(1)))
            except ValueError:
                continue
    return max(dates) if dates else None


def load_holds(root: Path) -> dict[str, dict]:
    """ticker -> hold entry. A missing or unreadable file means no holds."""
    try:
        raw = json.loads((Path(root) / HOLDS_FILE).read_text())
    except (OSError, ValueError):
        return {}
    return {k: v for k, v in raw.items()
            if not k.startswith('_') and isinstance(v, dict)}


def entry_block(ticker: str, today: str, root: Path,
                max_age: int = 30) -> str | None:
    """Reason this name may not enter today, or None when entry is allowed."""
    now = dt.date.fromisoformat(today)
    hold = load_holds(root).get(ticker)
    if hold:
        exp = hold.get('expires')
        try:
            live = exp is None or dt.date.fromisoformat(exp) >= now
        except ValueError:
            live = True          # unreadable expiry fails closed
        if live:
            return (f'entry hold until {exp or "cleared"}: '
                    f'{hold.get("reason", "no reason recorded")}')
    last = latest_briefing_date(root, ticker)
    if last is None:
        return 'no context briefing on file'
    age = (now - last).days
    if age > max_age:
        return f'latest briefing {last} is {age}d old (> {max_age}d)'
    return None
