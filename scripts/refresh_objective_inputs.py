"""Refresh objective Watchlist inputs (portfolio / all / subset) — rule-9 helper.

Subjective rating cells are NEVER touched. Deliberate-blank conventions
(foreign-ADR currency, EPS-YoY one-offs, negative-EBITDA, ROIC) are guarded so
a mechanical refresh cannot silently regress them. See
docs/superpowers/specs/2026-06-24-refresh-objective-inputs-design.md.
"""
from __future__ import annotations

import sys
import json
import datetime as dt
from pathlib import Path
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_score import _is_layer9_capacity, _CAPACITY_JSON

ROOT = Path(__file__).resolve().parent.parent
SCORING_PATH = ROOT / "00-master" / "ai_supply_chain_scoring.xlsx"
PORTFOLIO_PATH = ROOT / "00-master" / "portfolio.xlsx"


def _watchlist_tickers(scoring_path) -> list[str]:
    ws = load_workbook(scoring_path, read_only=True)["Watchlist"]
    out = []
    for r in range(2, ws.max_row + 1):
        v = ws.cell(row=r, column=1).value
        if v:
            out.append(str(v).strip().upper())
    return out


def _portfolio_hold_tickers(portfolio_path) -> list[str]:
    ws = load_workbook(portfolio_path, read_only=True)["Targets"]
    header_row = None
    for r in range(1, ws.max_row + 1):
        if ws.cell(row=r, column=1).value == "Ticker":
            header_row = r
            break
    status_col = None
    for c in range(1, ws.max_column + 1):
        if ws.cell(row=header_row, column=c).value == "Status":
            status_col = c
            break
    out = []
    for r in range(header_row + 1, ws.max_row + 1):
        t = ws.cell(row=r, column=1).value
        s = ws.cell(row=r, column=status_col).value
        if t and s and str(s).strip().upper() == "HOLD":
            out.append(str(t).strip().upper())
    return out


def resolve_targets(arg, scoring_path=SCORING_PATH, portfolio_path=PORTFOLIO_PATH) -> list[str]:
    watchlist = _watchlist_tickers(scoring_path)
    if arg == "all":
        return watchlist
    if arg == "portfolio":
        hold = _portfolio_hold_tickers(portfolio_path)
        wlset = set(watchlist)
        return [t for t in hold if t in wlset]
    # explicit subset
    wlset = set(watchlist)
    return [t.strip().upper() for t in arg if t.strip().upper() in wlset]


def mw_staleness_flag(ticker, layer, today, capacity_json=None):
    """Check Layer-9 capacity cohort MW data staleness (rule 13).

    Returns flag string if layer is Layer-9 capacity AND entry is missing OR as_of >90 days old;
    else None.

    Args:
        ticker: Stock ticker symbol.
        layer: Layer string from Watchlist.
        today: date object for age calculation.
        capacity_json: Override path to capacity-mw.json (for testing).

    Returns:
        str | None: Flag message or None.
    """
    if not _is_layer9_capacity(layer):
        return None
    path = capacity_json if capacity_json is not None else _CAPACITY_JSON
    try:
        data = json.loads(Path(path).read_text())
    except Exception:
        data = {}
    rec = data.get(ticker)
    if not rec or rec.get("secured_gross_mw") is None:
        return f"{ticker} EV/MW: missing from capacity-mw.json — add it (rule 13)."
    as_of = rec.get("as_of")
    try:
        age = (today - dt.date.fromisoformat(as_of)).days
    except Exception:
        return f"{ticker} EV/MW: capacity-mw.json as_of unparseable ({as_of!r}) — stale, refresh MW."
    if age > 90:
        return f"{ticker} EV/MW: capacity-mw.json as_of {as_of} → {age} days old (>90) → stale, refresh MW."
    return None
