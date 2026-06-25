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


OBJ_COLS = {"fwd_pe": 5, "ev_ebitda": 6, "fcf_yield": 7, "ps": 8,
            "roic": 11, "gross_mgn": 12, "fcf_mgn": 13, "nd_ebitda": 14,
            "rev_3y_cagr": 16, "rev_yoy": 17, "eps_yoy": 18}
DMA_COL = 29
LAST_UPDATED_COL = 4
EPS_YOY_EXTREME = 300.0
_ADR_BLANK_KEYS = ("ps", "ev_ebitda", "fcf_yield")


def _blank(v):
    return v is None or v == ""


def apply_guards(info, fresh, existing):
    """Apply smart blank-handling guards to produce safe write set.

    Args:
        info: yfinance info dict (needs 'financialCurrency').
        fresh: compute_inputs output dict (input-key → value).
        existing: current Watchlist cell values (input-key → value or None/"" if blank).

    Returns:
        (writes, flags): writes maps input-key → value for keys to write (absent = leave
        untouched; present-None = write blank). flags is a list of human-readable strings.
    """
    writes, flags = {}, []

    # Guard 1: currency — ADR/foreign filer blanks P/S, EV/EBITDA, FCF-Yield
    cur = info.get("financialCurrency")
    adr = bool(cur) and str(cur).upper() != "USD"
    if adr:
        for k in _ADR_BLANK_KEYS:
            writes[k] = None
        flags.append(
            f"ADR currency {cur}: blanked P/S, EV/EBITDA, FCF-Yield "
            f"(USD price vs local financials)."
        )

    # Per-key loop
    for key in OBJ_COLS:
        # ADR keys already forced-blank above; skip them in the per-key loop
        if adr and key in _ADR_BLANK_KEYS:
            continue

        if key == "eps_yoy":
            # (a) existing blank → preserve, do not write
            if _blank(existing.get(key)):
                flags.append(
                    "EPS YoY: cell currently blank (likely a documented one-off) "
                    "— preserved blank, not refilled."
                )
                continue
            # (b) fresh value extreme → withhold
            v = fresh.get(key)
            if v is not None and abs(v) >= EPS_YOY_EXTREME:
                flags.append(
                    f"EPS YoY: fresh {v:+.0f}% ≥ {EPS_YOY_EXTREME:.0f}% "
                    f"→ withheld as possible one-off (rule 15). Confirm blank or write."
                )
                continue
            # (c) fresh None over a non-blank existing → keep existing (don't clobber).
            # yfinance earningsQuarterlyGrowth is frequently None; same protection
            # the generic-key path applies (guard 4).
            if v is None and not _blank(existing.get(key)):
                flags.append(
                    f"eps_yoy: fetch returned no data — kept prior value {existing.get(key)}."
                )
                continue
            # (d) normal — write (may be None when existing is also blank)
            writes[key] = v
            continue

        # Guard 4: every other key — if fresh is None and existing is non-blank, keep existing
        v = fresh.get(key)
        if v is None and not _blank(existing.get(key)):
            flags.append(
                f"{key}: fetch returned no data — kept prior value {existing.get(key)}."
            )
            continue
        writes[key] = v

    return writes, flags


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


def read_existing(ws, row):
    """Read current cell values for all objective input keys.

    Args:
        ws: openpyxl worksheet.
        row: Row number to read from.

    Returns:
        dict: maps input-key to current cell value (or None/"" if blank).
    """
    return {k: ws.cell(row=row, column=c).value for k, c in OBJ_COLS.items()}


def write_row(ws, row, writes, dma_value, today_iso):
    """Write objective inputs and metadata to a row, never touching subjective columns.

    Args:
        ws: openpyxl worksheet.
        row: Row number to write to.
        writes: dict mapping input-key → value. Absent key = leave untouched;
                present key with None value = write blank.
        dma_value: Value for DMA_COL, or None to skip writing it.
        today_iso: ISO date string for LAST_UPDATED_COL.

    Returns:
        list[int]: Sorted list of column indices actually written.
    """
    touched = []
    for key, val in writes.items():
        c = OBJ_COLS[key]
        ws.cell(row=row, column=c).value = val
        touched.append(c)
    if dma_value is not None:
        ws.cell(row=row, column=DMA_COL).value = dma_value
        touched.append(DMA_COL)
    ws.cell(row=row, column=LAST_UPDATED_COL).value = today_iso
    touched.append(LAST_UPDATED_COL)
    return sorted(set(touched))
