"""Thesis-break triggers for the model portfolio. Read-only check.

Prints each Targets name's trigger from its thesis.md, so the weekly scan can
compare the week's filings and news to them. A trigger still awaiting Dom's
review is marked DRAFT. Exit 1 if a name has no real trigger.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from portfolio_theses import portfolio_tickers

ROOT = Path(__file__).resolve().parent.parent
DRAFT_MARK = "(draft, awaiting Dom's review)"
_TRIGGER = re.compile(r"^\*\*Thesis-break trigger:\*\*[ \t]*(.*)$", re.M)


def trigger_of(text: str) -> str | None:
    """The trigger line's text, or None for a missing line or the template."""
    m = _TRIGGER.search(text)
    value = m.group(1).strip() if m else ""
    return None if not value or value.startswith("{") else value


def load_triggers(tickers, root: Path = ROOT) -> dict[str, str | None]:
    out = {}
    for t in tickers:
        path = root / "per-stock" / t / "thesis.md"
        out[t] = trigger_of(path.read_text()) if path.exists() else None
    return out


def report(triggers: dict[str, str | None]) -> int:
    missing = sorted(t for t, v in triggers.items() if v is None)
    drafts = sorted(t for t, v in triggers.items() if v and DRAFT_MARK in v)
    print(f"{len(triggers)} portfolio names: {len(missing)} missing, "
          f"{len(drafts)} draft\n")
    for t, value in sorted(triggers.items()):
        if value is None:
            print(f"{t}: MISSING")
        elif DRAFT_MARK in value:
            print(f"{t}: DRAFT {value.replace(DRAFT_MARK, '').strip()}")
        else:
            print(f"{t}: {value}")
    return 1 if missing else 0


def main() -> int:
    return report(load_triggers(portfolio_tickers(ROOT)))


if __name__ == "__main__":
    sys.exit(main())
