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


_FX_CACHE: dict = {}


def _fetch_fx(f: str, t: str, ticker_cls) -> Optional[float]:
    try:
        info = ticker_cls(f"{f}{t}=X").info
        return info.get("regularMarketPrice") or info.get("previousClose")
    except Exception:
        return None


def fx_rate(from_ccy, to_ccy, *, ticker_cls=None) -> Optional[float]:
    """Exchange rate: units of `to_ccy` per 1 `from_ccy`, via yfinance
    '{from}{to}=X'. 1.0 for the same currency; None if unavailable. The default
    (real) path is cached per pair; an injected ticker_cls (tests) is never
    cached, so it can't pollute the shared cache."""
    if not from_ccy or not to_ccy:
        return None
    f, t = str(from_ccy).upper(), str(to_ccy).upper()
    if f == t:
        return 1.0
    if ticker_cls is not None:
        return _fetch_fx(f, t, ticker_cls)
    key = (f, t)
    if key not in _FX_CACHE:
        import yfinance as yf
        _FX_CACHE[key] = _fetch_fx(f, t, yf.Ticker)
    return _FX_CACHE[key]


def ratios_via_fx(mcap_trading, rate, revenue, ebitda, debt, cash, fcf) -> dict:
    """Pure: the GENERAL currency fix. Convert market cap from the trading
    currency to the financial currency (× rate), then compute {ev_ebitda, ps,
    fcf_yield} against the financial-currency statement items (revenue/ebitda/
    debt/cash/fcf already in that currency, so ratios end up dimensionless and
    comparable to every other name). EV is computed here (market cap + debt −
    cash) rather than trusting yfinance's often-corrupt ADR enterpriseValue."""
    none = {"ev_ebitda": None, "ps": None, "fcf_yield": None}
    if not mcap_trading or not rate:
        return dict(none)
    mcap = mcap_trading * rate
    ps = _sane(round(mcap / revenue, 2), 0.0, 1000.0) if revenue else None
    ev = mcap + (debt or 0) - (cash or 0)
    ev_ebitda = (_sane(round(ev / ebitda, 2), -1000.0, 1000.0)
                 if (ebitda and ebitda > 0) else None)
    fcf_yield = round(fcf / mcap * 100, 2) if (fcf is not None and mcap) else None
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
