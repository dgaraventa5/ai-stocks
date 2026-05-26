"""Fetch SEC filings (10-K, 10-Q, 8-K, DEF 14A, etc.) for a ticker.

Usage:
  python3 scripts/sec_edgar.py NVDA --forms 10-K 10-Q --limit 4
  python3 scripts/sec_edgar.py VRT --forms 8-K --since 2026-01-01

Saves the primary document of each matching filing to
  per-stock/{TICKER}/filings/{form}_{filing-date}_{accession}.{ext}

Where possible the primary doc is HTML or PDF straight from EDGAR; we
do not convert HTML → PDF (leave that to the reader's browser).
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from common import cik_for, flag, per_stock_dir, sec_get


def submissions(cik: str) -> dict:
    """Pull the EDGAR submissions index for a CIK."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    return sec_get(url, host_data_sec=True).json()


def _raw_doc_path(primary_doc: str) -> str:
    # EDGAR puts ownership/foreign filings under an xsl{Stylesheet}/ subdir that
    # serves the XSLT-rendered HTML view. The underlying XML sits at the
    # accession root with the same filename. Strip the prefix to get raw data.
    if "/" in primary_doc and primary_doc.startswith("xsl"):
        return primary_doc.split("/", 1)[1]
    return primary_doc


def primary_doc_url(cik: str, accession_no: str, primary_doc: str) -> str:
    acc_clean = accession_no.replace("-", "")
    cik_int = int(cik)
    return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_clean}/{_raw_doc_path(primary_doc)}"


def fetch_filings(
    ticker: str,
    forms: list[str],
    *,
    limit: int = 4,
    since: str | None = None,
) -> list[Path]:
    cik = cik_for(ticker)
    if cik is None:
        flag(f"Could not resolve ticker {ticker} to a CIK — skipping.")
        return []

    out_dir = per_stock_dir(ticker, create=True) / "filings"
    data = submissions(cik)

    recent = data.get("filings", {}).get("recent", {})
    form_list = recent.get("form", [])
    accession_list = recent.get("accessionNumber", [])
    date_list = recent.get("filingDate", [])
    primary_list = recent.get("primaryDocument", [])

    saved: list[Path] = []
    counts: dict[str, int] = {f: 0 for f in forms}

    for form, accession, fdate, primary in zip(
        form_list, accession_list, date_list, primary_list
    ):
        if form not in forms:
            continue
        if since and fdate < since:
            continue
        if counts[form] >= limit:
            continue

        url = primary_doc_url(cik, accession, primary)
        ext = Path(primary).suffix or ".htm"
        safe_form = form.replace("/", "-")
        out = out_dir / f"{safe_form}_{fdate}_{accession}{ext}"
        if out.exists():
            counts[form] += 1
            continue

        resp = sec_get(url)
        out.write_bytes(resp.content)
        saved.append(out)
        counts[form] += 1
        print(f"saved {out.relative_to(out_dir.parent.parent.parent)}")

    for form, n in counts.items():
        if n == 0:
            flag(f"No {form} filings found for {ticker} (since={since}).")

    return saved


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch SEC filings for a ticker.")
    ap.add_argument("ticker")
    ap.add_argument("--forms", nargs="+", default=["10-K", "10-Q"],
                    help="Forms to fetch (default: 10-K 10-Q)")
    ap.add_argument("--limit", type=int, default=4,
                    help="Max filings per form (default: 4 = last year of 10-Qs)")
    ap.add_argument("--since", default=None,
                    help="Filing date floor YYYY-MM-DD (default: no floor)")
    args = ap.parse_args()

    fetch_filings(args.ticker, args.forms, limit=args.limit, since=args.since)


if __name__ == "__main__":
    main()
