"""Filing overrides: objective inputs taken from a filing where Yahoo is wrong.

Why: a fresh listing (ANT, IPO 2026-11-19) reaches Yahoo with gaps the
statement-based inputs cannot survive: no Q1-Q2 2026 statements (ROIC and FCF
fell back to FY2025), the pre-IPO convertible notes counted as $135B of debt
(ND/EBITDA scored as net debt), a scraped 22% gross margin, and an enterprise
value built on the old capital structure. The weekly refresh rewrites every
name, so filing-based values typed into the sheet would be overwritten.

How: `00-master/filing-overrides.json` holds, per ticker, the quarter the values
describe (`period_end`), the price-independent inputs (`fixed`: ROIC, gross
margin, FCF margin, ND/EBITDA), and the components of the price-dependent ones
(`ev`: TTM FCF, cash, debt, and shares still to be issued that are economically
debt-like). FCF yield and EV/FCF are recomputed from the current market cap on
every run, so they never freeze at a stale price.

Expiry: an override applies only while Yahoo's `mostRecentQuarter` is still
`period_end`. Once a newer quarter is reported, the override retires itself
and Yahoo's values flow through with an EXPIRED flag, so old-quarter numbers
never sit in live scores (the 2026-11-20 rule). Remove the entry, or replace it
with the new filing's values, when that flag appears.

Pure and stdlib-only: imported by refresh_objective_inputs (site-deploy pytest
env has no yfinance) and refresh_reverse_dcf.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERRIDES_PATH = ROOT / "00-master" / "filing-overrides.json"

# Sheet keys (refresh_objective_inputs.OBJ_COLS) an override may set.
FIXED_KEYS = frozenset({"roic", "gross_mgn", "fcf_mgn", "nd_ebitda"})
# Price-dependent keys recomputed from the `ev` block. ev_ebitda is col F, which
# holds EV/FCF for Layer 10 (rule 10) — the only layer an override covers today.
PRICE_KEYS = ("fcf_yield", "ev_ebitda")


def load(path=None) -> dict:
    """Ticker -> entry. Missing or unreadable file = no overrides."""
    p = Path(path) if path is not None else OVERRIDES_PATH
    try:
        data = json.loads(p.read_text())
    except (OSError, ValueError):
        return {}
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _mrq(info: dict) -> dt.date | None:
    v = (info or {}).get("mostRecentQuarter")
    try:
        return dt.datetime.fromtimestamp(int(v), tz=dt.timezone.utc).date()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def status(entry: dict, info: dict) -> str:
    """'active', 'expired' (newer quarter reported) or 'unknown' (no MRQ)."""
    mrq = _mrq(info)
    if mrq is None:
        return "unknown"
    return "expired" if mrq > dt.date.fromisoformat(entry["period_end"]) else "active"


def ev_fcf(entry: dict, info: dict) -> float | None:
    """EV/FCF at the current price, or None when expired / not computable.

    EV = market cap + debt + extra_shares x price - cash. extra_shares are
    shares owed but not yet issued (ANT's Amazon rollover notes), valued at
    market like the shares already in the market cap.
    """
    if status(entry, info) == "expired":
        return None
    ev = entry.get("ev") or {}
    mcap, price = info.get("marketCap"), info.get("currentPrice")
    fcf = ev.get("fcf_ttm")
    if not mcap or not fcf or fcf <= 0:
        return None
    extra = (ev.get("extra_shares") or 0) * (price or 0)
    if ev.get("extra_shares") and not price:
        return None
    value = mcap + (ev.get("debt") or 0) + extra - (ev.get("cash") or 0)
    return round(value / fcf, 1)


def apply(entry: dict, info: dict, writes: dict) -> tuple[dict, list[str]]:
    """Overlay an override onto the refresh's planned writes.

    Returns (writes, flags). Every replaced value is flagged with what Yahoo
    would have written, so the refresh report shows the override at work.
    """
    out = dict(writes)
    src = f"{entry.get('source', 'filing')}, quarter {entry['period_end']}"
    st = status(entry, info)
    if st == "expired":
        return out, [f"FILING OVERRIDE EXPIRED: a newer quarter than "
                     f"{entry['period_end']} is reported; Yahoo's values written. "
                     f"Check them against the new filing, then update or remove "
                     f"the entry in 00-master/filing-overrides.json."]

    flags = []
    if st == "unknown":
        flags.append("FILING OVERRIDE: could not confirm Yahoo's latest quarter; "
                     "override kept.")

    def put(key, value):
        if key in out and out[key] != value:
            flags.append(f"FILING OVERRIDE ({src}): {key} {value} "
                         f"(Yahoo would write {out[key]}).")
        out[key] = value

    for key, value in (entry.get("fixed") or {}).items():
        if key in FIXED_KEYS:
            put(key, value)

    if entry.get("ev"):
        mcap = info.get("marketCap")
        fcf = entry["ev"].get("fcf_ttm")
        if mcap and fcf:
            put("fcf_yield", round(fcf / mcap * 100, 2))
            multiple = ev_fcf(entry, info)
            if multiple is not None:
                put("ev_ebitda", multiple)
        else:
            flags.append("FILING OVERRIDE: no market cap from Yahoo; FCF yield "
                         "and EV/FCF left to Yahoo this run.")
    return out, flags
