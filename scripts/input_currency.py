"""Which quarter does each score rest on? Read-only check.

Last Updated stamps every refresh, even when Yahoo still serves the old quarter,
so a fresh date can sit on stale statements. This compares the newest quarter
with revenue in Yahoo's statements to the company's newest earnings 8-K, and
changes no project data.

  python3 scripts/input_currency.py                # holdings and the top 25
  python3 scripts/input_currency.py --scope all    # every Watchlist name

A name is BEHIND when its newest earnings 8-K came at least NEWER_QUARTER_DAYS
after that quarter-end: too long for a report on that quarter, so the 8-K almost
certainly covers a later one. An Item 2.02 8-K can also be a preliminary release
or a presentation, so read BEHIND as a prompt to look, not as a fact. Exits
nonzero only when too many lookups failed, or none worked, for the result to
mean anything.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import time

import scheduled_run as sr

NEWER_QUARTER_DAYS = 100    # a next-quarter print needs 91 days plus closing the books
                            # (10+); slow Q4 prints land up to ~90 days out
LOOKBACK_DAYS = 200
FAILED = "error"
NOT_CHECKABLE = "not checkable"     # no 8-Ks to compare against
_FILING_COLUMNS = ("form", "filingDate", "items", "accessionNumber", "primaryDocument")


def newest_earnings_filing(recent: dict, today: dt.date):
    """Newest Item 2.02 8-K date, or NOT_CHECKABLE for a filer with none.
    Raises on a block that can't answer, so it counts as a failed lookup."""
    columns = [recent.get(k) for k in _FILING_COLUMNS]
    if (not all(columns) or len({len(c) for c in columns}) != 1
            or not all(recent["filingDate"])):
        raise ValueError("unusable filings block")
    start = today - dt.timedelta(days=LOOKBACK_DAYS)
    dates = [f["date"] for f in sr.filings_in_window(recent, start, today, {"8-K"})
             if f["earnings"]]
    return dt.date.fromisoformat(max(dates)) if dates else NOT_CHECKABLE


def classify(quarter, filed) -> str:
    if filed == NOT_CHECKABLE:
        return "not_checkable"
    if quarter == FAILED or filed == FAILED:
        return "failed"
    return "behind" if (filed - quarter).days >= NEWER_QUARTER_DAYS else "current"


def _statement_quarter(ticker):
    """Newest quarter with revenue. Yahoo can post a column with only EPS days
    before the statements fill in, so a column alone proves nothing."""
    import yfinance as yf                                # lazy (CI minimal-env)
    try:
        revenue = yf.Ticker(ticker).quarterly_income_stmt.loc["Total Revenue"].dropna()
        return max(revenue.index).date() if len(revenue) else FAILED
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
        return newest_earnings_filing(data["filings"]["recent"], today)
    except Exception:                                    # noqa: BLE001
        return FAILED


def _today() -> dt.date:
    return dt.date.today()


def report(tickers, today, quarter_of=_statement_quarter, filed_of=_filed_date) -> int:
    rows = []
    for t in tickers:
        filed = filed_of(t, today)
        rows.append((t, None if filed == NOT_CHECKABLE else quarter_of(t), filed))
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
    if skipped:
        print(f"  NOT CHECKABLE (no CIK or earnings 8-K): {', '.join(r[0] for r in skipped)}")
    if sr.scan_blocked(len(rows) - len(skipped), len(failed)):
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
