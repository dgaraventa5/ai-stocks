"""Scaffold a new per-stock/{TICKER}/ directory from the project templates.

Creates:
  per-stock/{TICKER}/
    thesis.md              (copied from templates/per-stock-template.md)
    news-log.md            (header only — append entries per CLAUDE.md §6)
    catalysts-watchlist.md (header only)
    filings/               (empty)
    transcripts/           (empty)

Usage:
  python3 scripts/new_ticker.py NVDA
  python3 scripts/new_ticker.py NVDA --fetch-financials --fetch-filings
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from common import ROOT, per_stock_dir

TEMPLATE = ROOT / "templates" / "per-stock-template.md"


def scaffold(ticker: str, *, overwrite: bool = False) -> Path:
    ticker = ticker.upper()
    d = per_stock_dir(ticker, create=True)

    thesis = d / "thesis.md"
    if not thesis.exists() or overwrite:
        body = TEMPLATE.read_text().replace("{TICKER}", ticker)
        body = body.replace("{YYYY-MM-DD}", dt.date.today().isoformat())
        thesis.write_text(body)
        print(f"wrote {thesis.relative_to(ROOT)}")
    else:
        print(f"skipped (exists): {thesis.relative_to(ROOT)}")

    news = d / "news-log.md"
    if not news.exists() or overwrite:
        news.write_text(
            f"# {ticker} — news log\n\n"
            "Per CLAUDE.md §6: append every material development with date, "
            "source, and a one-line summary. The thesis itself only changes "
            "when a development materially affects an existing section.\n\n"
            "| Date | Source | Summary |\n"
            "|---|---|---|\n"
        )
        print(f"wrote {news.relative_to(ROOT)}")

    cat = d / "catalysts-watchlist.md"
    if not cat.exists() or overwrite:
        cat.write_text(
            f"# {ticker} — catalysts watchlist\n\n"
            "Forward-looking events that could move the thesis. Use the "
            "thesis.md §8 table as the canonical list; this file is for "
            "lower-priority items and ad-hoc capture.\n\n"
            "| Date | Event | Why it matters |\n"
            "|---|---|---|\n"
        )
        print(f"wrote {cat.relative_to(ROOT)}")

    return d


def main() -> None:
    ap = argparse.ArgumentParser(description="Scaffold a new per-stock directory.")
    ap.add_argument("ticker")
    ap.add_argument("--overwrite", action="store_true",
                    help="Overwrite existing files (default: skip)")
    ap.add_argument("--fetch-financials", action="store_true",
                    help="Also run yfinance puller to build financials.xlsx")
    ap.add_argument("--fetch-filings", action="store_true",
                    help="Also fetch latest 4 10-K + 10-Q filings from EDGAR")
    args = ap.parse_args()

    scaffold(args.ticker, overwrite=args.overwrite)

    if args.fetch_financials:
        from yfinance_fundamentals import build_financials
        build_financials(args.ticker)

    if args.fetch_filings:
        from sec_edgar import fetch_filings
        fetch_filings(args.ticker, ["10-K", "10-Q"], limit=4)


if __name__ == "__main__":
    main()
