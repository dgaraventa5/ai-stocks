"""Capitulation flag (rule 32-A, added 2026-08-31) — the mirror of rule 14.

The rule-14 expectations flag catches one failure mode: a name priced at the
TOP of its own history while growth decelerates (peak multiple, crowded
consensus). The 2026-08 post-mortem on the CRM/ZS/PLTR exit misses (+53%/+50%/
+44% after exit vs QQQ ~flat) exposed the mirror-image blind spot: a name
priced at the BOTTOM of its own 3-year range while fundamentals hold. CRM sat
at ~Fwd P/E 11 / 10% FCF yield with revenue growth INTACT — the fear that
crushed the price was counted three times (dead momentum, low AI-directness,
R5 disruption risk) while the cheapness counted once, and the model exited at
maximum pessimism. Nothing in the framework could even *name* that setup.

FLAG fires when P/S percentile <= 10 of its own 3-year range AND current YoY
revenue growth >= its 3-year median (multiple at trough while growth holds).

This is a QUALITATIVE red flag for context briefings and the weekly pipeline
review, NOT a scored metric — a name can sit at its 3-year-low multiple for
good reason (secular decline the revenue line hasn't caught yet); the flag
forces the briefing to argue why, not to auto-reward. Before it ever touches
a score, it must EARN it: every firing can log a rule-17 forecast
(--log-forecast) claiming the name beats its frozen layer cohort over the
next quarter, at the uninformed 0.55 base-rate prior. Once ~30 such forecasts
resolve, the calibration report says whether capitulation predicts anything —
the empirical gate any scored version has to pass first.

Usage:
  python3 scripts/capitulation_flag.py CRM ZS PLTR
  python3 scripts/capitulation_flag.py CRM --log-forecast   # flag fires -> log
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import forecast_cohorts as cohorts
import forecast_store as store
from forecast_resolvers import resolution_date_for

PS_TROUGH_PCTILE_MAX = 10.0   # mirror of the rule-14 >= 90 peak threshold
DIMENSION = "signal.capitulation"
TEMPLATE = "REL_STRENGTH_1Q"   # same resolver as rule-17 Phase 1 — no new code
HORIZON_TD = 63
BASE_RATE_PROB = 0.55          # deliberately uninformed: the point is to LEARN
                               # the hit rate, not to assert one


def capitulation_decision(ps_pctile: float, yoy_current: float,
                          yoy_median: float,
                          pctile_max: float = PS_TROUGH_PCTILE_MAX) -> bool:
    """Pure decision: trough multiple AND growth holding at/above its median."""
    return bool(ps_pctile <= pctile_max and yoy_current >= yoy_median)


def capitulation_check(ticker: str) -> dict:
    """P/S-percentile + growth check against the name's own 3-year history.

    Reuses the rule-14 machinery (SEC companyfacts quarterly revenue, price
    history, constant share count) — same skips, same caveats. Heavy imports
    are lazy so this module stays importable in the deploy-site CI env."""
    from expectations_flag import quarterly_revenue_sec   # pulls pandas/requests
    import yfinance as yf

    t = yf.Ticker(ticker)
    out: dict = {"ticker": ticker, "flag": None, "notes": []}

    rev, err = quarterly_revenue_sec(ticker)
    if rev is None:
        out["notes"].append(f"SEC companyfacts: {err} — check skipped")
        return out
    rev = rev.iloc[-17:]
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
        "flag": capitulation_decision(pctile, current_yoy, median_yoy),
    })
    out["notes"].append("share count held constant at today's value — "
                        "percentile is flattered DOWN for heavy diluters")
    return out


def _has_open_capitulation(ticker: str, path) -> bool:
    return any(s["ticker"] == ticker and s["dimension"] == DIMENSION
               for s in store.open_forecasts(path))


def log_capitulation_forecast(ticker: str, *, rows=None,
                              path=store.FORECASTS_PATH,
                              today: dt.date | None = None) -> dict | None:
    """Append one open rule-17 forecast for a flagged name; None if an open
    capitulation forecast for the ticker already exists (no stacking — one
    live prediction per name per episode)."""
    ticker = ticker.upper()
    today = today or dt.date.today()
    if _has_open_capitulation(ticker, path):
        store.flag(f"{ticker}: open capitulation forecast already logged — skip")
        return None
    layer, rule = cohorts.build_frozen_cohort(ticker, rows=rows)
    claim = (f"{ticker} total return outperforms its frozen Layer-{layer} "
             f"equal-weight peer basket over the next {rule['horizon_td']} "
             f"trading days (capitulation-flag firing)"
             if rule["benchmark"] != "SMH" else
             f"{ticker} total return outperforms SMH over the next "
             f"{rule['horizon_td']} trading days (capitulation-flag firing)")
    return store.append_creation(dict(
        ticker=ticker, layer=layer, dimension=DIMENSION, rating_value=None,
        template=TEMPLATE, claim=claim, probability=BASE_RATE_PROB,
        resolution_date=resolution_date_for(today, HORIZON_TD).isoformat(),
        resolution_rule=rule, status="open"), path=path, today=today)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("tickers", nargs="+")
    ap.add_argument("--log-forecast", action="store_true",
                    help="log a rule-17 forecast for each name whose flag fires")
    args = ap.parse_args()
    for tk in args.tickers:
        r = capitulation_check(tk.upper())
        if r["flag"] is None:
            print(f'{tk:6} SKIPPED — {"; ".join(r["notes"])}')
            continue
        status = "⚠ CAPITULATION FLAG" if r["flag"] else "clean"
        print(f'{tk:6} {status}: P/S {r["ps_current"]} = '
              f'{r["ps_3y_percentile"]}th pctile of own 3y range; rev YoY '
              f'{r["rev_yoy_current_pct"]}% vs 3y median '
              f'{r["rev_yoy_3y_median_pct"]}%')
        if r["flag"] and args.log_forecast:
            snap = log_capitulation_forecast(tk)
            if snap:
                print(f'       logged {snap["id"]}  p={snap["probability"]:.2f} '
                      f'resolves {snap["resolution_date"]}')


if __name__ == "__main__":
    main()
