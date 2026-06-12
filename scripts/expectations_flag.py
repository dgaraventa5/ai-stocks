"""Expectations red-flag check (rule 14, added 2026-06-12).

Answers one question /refresh-context Step 2c needs: is this name priced at
the top of its own recent history? The scoring rubric has no "what's priced
in" input anywhere — Value bands are absolute, and Momentum *rewards*
relative strength — so consensus-crowded names score highest exactly when
forward returns are most at risk. This check is the qualitative counterweight
(surfaced during the 2026-06-12 SALP 13F rubric stress test).

Method (free-data best effort):
  1. P/S percentile vs own 3-year history — daily close × current share count
     ÷ trailing-4Q revenue at each date (step function). Quarterly revenue
     comes from SEC companyfacts (yfinance only exposes ~5 quarters). Share
     count is held constant at today's value: an approximation that
     understates historical market cap for heavy diluters (i.e. flatters
     today's percentile downward) — flagged in output.
  2. Growth-support check — current P/S vs most recent YoY revenue growth.

FLAG fires when P/S percentile >= 90 AND YoY revenue growth is below the
3-year median growth (multiple at peak while growth is decelerating).
This is a QUALITATIVE red flag for the context briefing, NOT a scored metric:
a name can sit at its 3-year-high multiple for good reason (inflection); the
flag forces the briefing to argue why, not to auto-penalize.

Usage:
  python3 scripts/expectations_flag.py NVDA AVGO TSM
"""
from __future__ import annotations

import sys
import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import yfinance as yf

from common import cik_for, sec_get

REV_TAGS = ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "SalesRevenueNet")


def quarterly_revenue_sec(ticker: str) -> tuple[pd.Series | None, str | None]:
    """Quarterly revenue series from SEC companyfacts (10-Q/10-K, USD).

    yfinance only exposes ~5 quarters; companyfacts goes back years.
    Annual (FY) frames are decomposed implicitly by keeping only ~3-month
    periods (70-100 days), so the series is quarter-by-quarter.
    """
    cik = cik_for(ticker)
    if not cik:
        return None, "no CIK mapping for ticker"
    try:
        facts = sec_get(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
            host_data_sec=True).json()["facts"]["us-gaap"]
    except Exception as e:
        return None, f"companyfacts fetch failed ({type(e).__name__}: {e}) — transient? retry"
    # Companies switch revenue tags over time (e.g. NVDA: SalesRevenueNet ->
    # RevenueFromContractWithCustomer...), so a single tag can be years stale.
    # Build a series per tag, then merge with priority to the most recent tag.
    candidates = []
    for tag in REV_TAGS:
        if tag not in facts or "USD" not in facts[tag].get("units", {}):
            continue
        rows = {}
        for f in facts[tag]["units"]["USD"]:
            if not f.get("start") or not f.get("end"):
                continue
            days = (pd.Timestamp(f["end"]) - pd.Timestamp(f["start"])).days
            if 70 <= days <= 100:  # quarterly periods only
                rows[pd.Timestamp(f["end"])] = float(f["val"])
        if rows:
            candidates.append(pd.Series(rows).sort_index())
    if not candidates:
        return None, "no quarterly periods under any known revenue tag"
    candidates.sort(key=lambda srs: srs.index.max(), reverse=True)
    merged = candidates[0]
    for srs in candidates[1:]:
        merged = merged.combine_first(srs)
    merged = merged.sort_index()
    # Stale-series guard: if the latest quarter-end is >200 days old the
    # ffill would silently apply ancient revenue to today's price.
    if (pd.Timestamp.now() - merged.index.max()).days > 200:
        return None, f"latest XBRL quarter end {merged.index.max().date()} is >200 days stale"
    if len(merged) < 8:
        return None, f"only {len(merged)} quarterly periods in companyfacts"
    return merged, None


def expectations_check(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    out: dict = {"ticker": ticker, "flag": None, "notes": []}

    rev, err = quarterly_revenue_sec(ticker)
    if rev is None:
        out["notes"].append(f"SEC companyfacts: {err} — check skipped")
        return out
    rev = rev.iloc[-17:]  # ~4y of quarters: 3y TTM window + growth median

    ttm = rev.rolling(4).sum().dropna()

    px = t.history(period="3y", auto_adjust=True)["Close"]
    if px.empty:
        out["notes"].append("no price history — check skipped")
        return out
    px.index = px.index.tz_localize(None)

    shares = t.info.get("sharesOutstanding")
    if not shares:
        out["notes"].append("no sharesOutstanding — check skipped")
        return out

    # Daily TTM revenue as a step function (as-of latest reported quarter-end)
    ttm_daily = ttm.reindex(px.index, method="ffill").dropna()
    px = px.loc[ttm_daily.index]
    ps_series = px * shares / ttm_daily

    current_ps = ps_series.iloc[-1]
    pctile = float((ps_series <= current_ps).mean() * 100)

    yoy = (rev / rev.shift(4) - 1).dropna() * 100
    current_yoy = float(yoy.iloc[-1])
    median_yoy = float(yoy.iloc[-12:].median())

    out.update({
        "ps_current": round(float(current_ps), 2),
        "ps_3y_percentile": round(pctile, 1),
        "rev_yoy_current_pct": round(current_yoy, 1),
        "rev_yoy_3y_median_pct": round(median_yoy, 1),
        "flag": bool(pctile >= 90 and current_yoy < median_yoy),
    })
    out["notes"].append("share count held constant at today's value — "
                        "percentile is flattered DOWN for heavy diluters")
    return out


def main() -> None:
    tickers = sys.argv[1:]
    if not tickers:
        print(__doc__)
        sys.exit(1)
    for tk in tickers:
        r = expectations_check(tk)
        if r["flag"] is None:
            print(f"{tk:6} SKIPPED — {'; '.join(r['notes'])}")
            continue
        status = "⚠ EXPECTATIONS FLAG" if r["flag"] else "clean"
        print(f"{tk:6} {status}: P/S {r['ps_current']} = {r['ps_3y_percentile']}th "
              f"pctile of own 3y range; rev YoY {r['rev_yoy_current_pct']}% vs "
              f"3y median {r['rev_yoy_3y_median_pct']}%")


if __name__ == "__main__":
    main()
