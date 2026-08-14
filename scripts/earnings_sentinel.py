"""Earnings sentinel — detection only (spec 2026-08-13-earnings-sentinel-design).

Pure decision functions + a JSON state file. NO side effects on any workbook;
the scheduled task drives all refreshes and calls back --mark on completion.
Never imports yfinance/pandas at module level (CI minimal-env rule).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import time
import zoneinfo
from pathlib import Path

from portfolio_sizing import is_tradable

ET = zoneinfo.ZoneInfo("America/New_York")
DEFAULT_TOP_N = 25
MAX_REPORT_AGE_DAYS = 5     # older unprocessed reports fall to the weekly cadence
_OPEN = dt.time(9, 30)

_REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = _REPO_ROOT / "tracking" / "earnings-sentinel-state.json"
SCORE_HISTORY = _REPO_ROOT / "tracking" / "score-history.csv"


def build_scope(holdings, ranked_rows, top_n=DEFAULT_TOP_N):
    """Holdings ∪ top-N tradable ranks (spec §3). Sorted, deduped."""
    tradable = [t for t, _ in sorted(ranked_rows, key=lambda r: r[1])
                if is_tradable(t)]
    return sorted(set(tradable[:top_n]) | set(holdings))


def classify_session(report_ts: dt.datetime) -> str:
    """BMO iff a real pre-open time; midnight = date-only placeholder → AMC
    (conservative: waits one extra close rather than re-scoring pre-reaction)."""
    t = report_ts.astimezone(ET).time()
    return "BMO" if dt.time(0, 0) < t < _OPEN else "AMC"


def _next_weekday(d: dt.date) -> dt.date:
    d += dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def reaction_day(report_ts: dt.datetime) -> dt.date:
    """First regular session whose close reflects the print (spec §4.3)."""
    d = report_ts.astimezone(ET).date()
    return d if classify_session(report_ts) == "BMO" else _next_weekday(d)


def due_events(scope, calendar, latest_close, state, now):
    """Spec §4.4. calendar: {t: [ET-aware datetimes]}; latest_close: {t: date}."""
    out = {"briefing_due": [], "rescore_due": [], "flagged": {}}
    tickers_state = state.get("tickers", {})
    for t in scope:
        dates = calendar.get(t)
        if not dates:
            out["flagged"][t] = "no earnings date available (rule 3: flagged, not guessed)"
            continue
        past = [ts for ts in dates if ts <= now]
        if not past:
            continue                      # next report is in the future
        report = max(past)
        rdate = report.astimezone(ET).date()
        if (now.astimezone(ET).date() - rdate).days > MAX_REPORT_AGE_DAYS:
            continue                      # pre-sentinel history / weekly cadence
        session = classify_session(report)
        ev = {"ticker": t, "report_date": rdate.isoformat(), "session": session}
        st = tickers_state.get(t, {})
        if st.get("briefed") != ev["report_date"]:
            out["briefing_due"].append(ev)
        if st.get("rescored") != ev["report_date"]:
            lc = latest_close.get(t)
            if lc is not None and lc >= reaction_day(report):
                out["rescore_due"].append(ev)
            # else: reaction close not printed yet (incl. holidays) — quiet defer
    return out


def load_state(path: Path = STATE_PATH) -> dict:
    path = Path(path)
    if not path.exists():
        return {"tickers": {}}
    return json.loads(path.read_text())


def mark(path: Path, phase: str, ticker: str, report_date: str) -> None:
    if phase not in ("briefed", "rescored"):
        raise ValueError(f"unknown phase {phase!r}")
    path = Path(path)
    state = load_state(path)
    state.setdefault("tickers", {}).setdefault(ticker, {})[phase] = report_date
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


# ---- I/O layer --------------------------------------------------------------

def latest_ranked_rows(csv_path: Path = SCORE_HISTORY):
    rows = list(csv.DictReader(open(csv_path)))
    if not rows:
        return []
    newest = max(r["date"] for r in rows)
    return [(r["ticker"], int(r["rank"])) for r in rows if r["date"] == newest]


def _holdings() -> list[str]:
    from generate_trade_ticket import _targets_weights   # openpyxl-only, offline
    weights, _meta = _targets_weights()
    return sorted(weights)


def _now() -> dt.datetime:
    return dt.datetime.now(tz=ET)


def _fetch_calendar(tickers):
    import yfinance as yf                                # lazy (CI minimal-env)
    out = {}
    for t in tickers:
        try:
            df = yf.Ticker(t).get_earnings_dates(limit=8)
            out[t] = ([ts.to_pydatetime().astimezone(ET) for ts in df.index]
                      if df is not None and len(df) else [])
        except Exception:
            out[t] = []                                  # → flagged downstream
        time.sleep(0.1)
    return out


def _fetch_latest_close(tickers):
    import yfinance as yf                                # lazy (CI minimal-env)
    out = {}
    for t in tickers:
        try:
            h = yf.Ticker(t).history(period="5d")
            out[t] = h.index[-1].date() if len(h) else None
        except Exception:
            out[t] = None
        time.sleep(0.1)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Earnings sentinel (detection only).")
    ap.add_argument("--mark", nargs=3, metavar=("PHASE", "TICKER", "REPORT_DATE"),
                    help="record a completed phase: briefed|rescored TICKER YYYY-MM-DD")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    args = ap.parse_args(argv)

    if args.mark:
        phase, ticker, report_date = args.mark
        mark(STATE_PATH, phase, ticker, report_date)
        print(f"marked {ticker} {phase} for report {report_date}")
        return 0

    scope = build_scope(_holdings(), latest_ranked_rows(SCORE_HISTORY), args.top_n)
    now = _now()
    calendar = _fetch_calendar(scope)
    # closes are only needed for names with a recent past report
    recent = [t for t in scope
              if any(ts <= now and
                     (now.astimezone(ET).date() - ts.astimezone(ET).date()).days
                     <= MAX_REPORT_AGE_DAYS
                     for ts in calendar.get(t, []))]
    latest_close = _fetch_latest_close(recent)
    out = due_events(scope, calendar, latest_close, load_state(STATE_PATH), now)
    out["scope_size"] = len(scope)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
