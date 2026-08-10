"""Quote source: Robinhood MCP first (US names), yfinance fallback.

Why: Yahoo throttles datacenter IPs and rate-limits bursts — the recurring
pain in scheduled runs. The Robinhood transport is authenticated, JSON, and
already part of the pipeline; use it for the names it carries (US listings)
and keep yfinance for foreign local lines and anything Robinhood misses.
Both dead → the name is OMITTED and flagged, never guessed (rule 3).

Scope note: QUOTES only. The dividend-adjusted historical series
(performance tracking) stays on yfinance — Robinhood historicals have
different adjustment semantics and the series has a regression guard.
"""
from __future__ import annotations

import sys


def _flag(msg: str) -> None:
    print(f'FLAG: {msg}', file=sys.stderr)


def _yf_close(ticker: str) -> float | None:
    import yfinance as yf   # lazy (minimal-CI convention)
    hist = yf.Ticker(ticker).history(period='5d', auto_adjust=False)
    if hist is None or hist.empty:
        return None
    return round(float(hist['Close'].iloc[-1]), 2)


def _default_transport():
    """Best-effort Robinhood transport; None when credentials are absent
    (sandbox/CI) so callers fall straight through to yfinance."""
    try:
        from execute_ticket import RobinhoodTransport
        return RobinhoodTransport()
    except BaseException:            # SystemExit from token discovery included
        return None


def ref_prices(tickers: list[str], transport=None) -> dict[str, float]:
    """{ticker: last trade/close} — RH batch for US names, yfinance for the
    rest and for anything RH failed to answer."""
    us = [t for t in tickers if '.' not in t]
    foreign = [t for t in tickers if '.' in t]
    out: dict[str, float] = {}

    if us:
        transport = transport if transport is not None else _default_transport()
        if transport is not None:
            try:
                out.update(transport.quotes(us))
            except Exception as e:
                _flag(f'Robinhood quotes failed ({e}) — falling back to '
                      f'yfinance for {len(us)} names')

    for t in foreign + [t for t in us if t not in out]:
        px = _yf_close(t)
        if px:
            out[t] = px
        else:
            _flag(f'{t}: no price from Robinhood or yfinance — omitted '
                  f'(rule 3: flagged, not guessed)')
    return out


def ref_price(ticker: str, transport=None) -> float | None:
    return ref_prices([ticker], transport=transport).get(ticker)
