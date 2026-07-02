"""Foreign-ADR currency-trap fix.

A foreign company that trades as a US ADR (price in USD) but reports its
financials in a local currency (TWD for TSM/UMC) gets GARBAGE market-cap-based
ratios from yfinance: P/S, EV/EBITDA and FCF-Yield divide a USD numerator by a
local-currency denominator (off by the ~32x TWD/USD factor). yfinance's ADR
enterpriseValue is itself corrupt, so FX-converting the ADR fields is
unreliable. The robust fix: source those three ratios from the company's LOCAL
listing (e.g. 2330.TW), where trading currency == financial currency, so the
ratios are clean, dimensionless, and directly comparable to USD-listed names.

Detection is a trading-vs-financial-currency mismatch — NOT "financial != USD",
which also (wrongly) flags a clean local-listed foreign name like Vanguard
(5347.TWO, TWD/TWD).

This module is pure + free of yfinance at import time (so refresh_objective_inputs
can import it without pulling yfinance). The one network wrapper, fetch_local_ratios,
imports yfinance lazily.
"""
from __future__ import annotations

from typing import Optional

# ADR ticker -> local listing whose trading currency matches its financial
# reporting currency (so yfinance's ratios for the local ticker are clean).
# Extend as other foreign ADRs are added to the watchlist (e.g. ASX).
ADR_LOCAL = {
    "TSM": "2330.TW",   # TSMC — reports TWD, ADR trades USD; local 2330.TW is TWD/TWD
    "UMC": "2303.TW",   # United Microelectronics — same
}


def has_currency_mismatch(trading: Optional[str], financial: Optional[str]) -> bool:
    """True when a name trades in one currency but reports financials in another
    (the ADR currency trap). False if either is missing or they match."""
    if not trading or not financial:
        return False
    return str(trading).upper() != str(financial).upper()


def _sane(v, lo, hi):
    """Return v as float if within [lo, hi], else None (defense against a bad
    local-ticker fetch; the local listing should already be clean)."""
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if lo <= v <= hi else None


def local_value_ratios(local_info: dict, local_fcf) -> dict:
    """Pure: given a LOCAL listing's yfinance info dict (same-currency, clean)
    and its statement FCF, return the three fixed ratios {ev_ebitda, ps,
    fcf_yield}. EV/EBITDA may be negative (loss-maker) and passes through; P/S
    is bounded to non-negative; FCF-Yield is FCF/marketCap (both local currency,
    so the ratio is currency-neutral)."""
    ev_ebitda = _sane(local_info.get("enterpriseToEbitda"), -1000.0, 1000.0)
    ps = _sane(local_info.get("priceToSalesTrailing12Months"), 0.0, 1000.0)
    mcap = local_info.get("marketCap")
    if local_fcf is not None and mcap:
        fcf_yield = round(local_fcf / mcap * 100, 2)
    else:
        fcf_yield = None
    return {"ev_ebitda": ev_ebitda, "ps": ps, "fcf_yield": fcf_yield}


def fetch_local_ratios(ticker: str, *, ticker_cls=None, fcf_fn=None) -> Optional[dict]:
    """Network wrapper: for a mapped ADR, fetch its local listing and return the
    clean {ev_ebitda, ps, fcf_yield}. Returns None if the ticker is unmapped or
    the fetch fails. yfinance/statement_fcf imported lazily to avoid a circular
    import with batch_score (which calls this)."""
    local = ADR_LOCAL.get(ticker)
    if not local:
        return None
    if ticker_cls is None:
        import yfinance as yf
        ticker_cls = yf.Ticker
    if fcf_fn is None:
        from batch_score import statement_fcf
        fcf_fn = statement_fcf
    try:
        lt = ticker_cls(local)
        li = lt.info
        local_fcf = fcf_fn(lt)
    except Exception:
        return None
    return local_value_ratios(li, local_fcf)
