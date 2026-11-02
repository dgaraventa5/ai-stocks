"""Which quarter does each score rest on? Read-only check.

Last Updated stamps every refresh, even when Yahoo still serves the old quarter,
so a fresh date can sit on stale statements. This compares Yahoo's newest
quarterly statement to the company's newest earnings 8-K and writes nothing.

  python3 scripts/input_currency.py                # holdings and the top 25
  python3 scripts/input_currency.py --scope all    # every Watchlist name

A name is BEHIND when its newest earnings 8-K came at least NEWER_QUARTER_DAYS
after Yahoo's newest quarter-end: that gap is too long for a report on that
quarter, so the 8-K must cover a later one. Exits nonzero only when too many
lookups failed for the result to mean anything. Being behind is a report item,
not a failure, because only Yahoo can clear it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import time

import scheduled_run as sr

NEWER_QUARTER_DAYS = 85     # next quarter-end is ~91 days on; Q4 prints land within ~75
LOOKBACK_DAYS = 200
FAILED = "error"
NOT_CHECKABLE = "not checkable"     # no 8-Ks to compare against


def newest_earnings_filing(recent: dict, today: dt.date):
    """Newest Item 2.02 8-K date, or NOT_CHECKABLE for a filer with none."""
    start = today - dt.timedelta(days=LOOKBACK_DAYS)
    dates = [f["date"] for f in sr.filings_in_window(recent, start, today, {"8-K"})
             if f["earnings"]]
    return dt.date.fromisoformat(max(dates)) if dates else NOT_CHECKABLE


def classify(quarter, filed) -> str:
    if quarter == FAILED or filed == FAILED:
        return "failed"
    if filed == NOT_CHECKABLE:
        return "not_checkable"
    return "behind" if (filed - quarter).days >= NEWER_QUARTER_DAYS else "current"


def _statement_quarter(ticker):
    import yfinance as yf                                # lazy (CI minimal-env)
    try:
        df = yf.Ticker(ticker).quarterly_income_stmt
        cols = df.dropna(axis=1, how="all").columns if df is not None else []
        return max(cols).date() if len(cols) else FAILED
    except Exception:                                    # noqa: BLE001
        return FAILED
    finally:
        time.sleep(0.1)


def _filed_date(ticker, today):
    from common import cik_for, sec_get                  # lazy (CI minimal-env)
    if "." in ticker:                                    # foreign local line
        return NOT_CHECKABLE
    try:
        cik = cik_for(ticker)
        if not cik:
            return NOT_CHECKABLE
        data = sec_get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                       host_data_sec=True).json()
        return newest_earnings_filing(data.get("filings", {}).get("recent", {}), today)
    except Exception:                                    # noqa: BLE001
        return FAILED


def _today() -> dt.date:
    return dt.date.today()


def report(tickers, today, quarter_of=_statement_quarter, filed_of=_filed_date) -> int:
    rows = [(t, quarter_of(t), filed_of(t, today)) for t in tickers]
    by_status: dict[str, list] = {}
    for row in rows:
        by_status.setdefault(classify(row[1], row[2]), []).append(row)
    behind = by_status.get("behind", [])
    failed = by_status.get("failed", [])
    skipped = by_status.get("not_checkable", [])
    print(f"=== Score inputs vs newest reported quarter, {today} ===\n")
    print(f"  checked {len(rows)}: {len(by_status.get('current', []))} current, "
          f"{len(behind)} behind, {len(skipped)} not checkable, {len(failed)} failed")
    for t, quarter, filed in behind:
        print(f"  BEHIND: {t} Yahoo statements end {quarter}, earnings 8-K filed {filed}")
    for t, _, _ in failed:
        print(f"  COULD NOT CHECK: {t}")
    if sr.scan_blocked(len(rows), len(failed)):
        print("BLOCKED: too many lookups failed, so do not read this as all clear",
              file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scope", choices=["watch", "all"], default="watch")
    args = ap.parse_args(argv)
    return report(sr._scope(args.scope), _today())


if __name__ == "__main__":
    sys.exit(main())
