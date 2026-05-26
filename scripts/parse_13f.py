"""Parse a 13F-HR information table for a fund's CIK or specific accession.

A 13F filing lists every U.S. equity position above $200K held by an
institutional manager at quarter-end, filed 45 days after period close.
The XML schema is stable: ns3:infoTable with nameOfIssuer, cusip, value
(in $thousands), sshPrnamt (shares), etc.

Usage:
  python3 scripts/parse_13f.py --cik 0001067983                # latest filing
  python3 scripts/parse_13f.py --cik 0001067983 --period 2025-Q4
  python3 scripts/parse_13f.py --accession 0001067983-25-000123
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from common import flag, sec_get


@dataclass
class Holding:
    issuer: str
    cusip: str
    value_thousands: float
    shares: int
    title_class: str

    def as_row(self) -> list:
        return [self.issuer, self.cusip, self.title_class,
                self.shares, self.value_thousands]


def _latest_13f_accession(cik: str, period: str | None = None) -> tuple[str, str] | None:
    """Return (accession_no, filing_date) for the matching 13F-HR filing."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    data = sec_get(url, host_data_sec=True).json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])

    for form, acc, fdate, rdate in zip(forms, accessions, dates, report_dates):
        if form != "13F-HR":
            continue
        if period:
            # period is like "2025-Q4" → match reportDate quarter-end
            y, q = period.split("-Q")
            q_ends = {"1": "-03-31", "2": "-06-30", "3": "-09-30", "4": "-12-31"}
            expected = y + q_ends[q]
            if rdate != expected:
                continue
        return acc, fdate
    return None


def _information_table_url(cik: str, accession: str) -> str | None:
    """Find the information table XML inside a 13F filing's directory."""
    acc_clean = accession.replace("-", "")
    cik_int = int(cik)
    idx_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F"  # noqa: E501 — unused, kept for reference
    # The filing directory index lists all files in this accession.
    index_json = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_clean}/index.json"
    resp = sec_get(index_json)
    items = resp.json().get("directory", {}).get("item", [])
    for it in items:
        name = it.get("name", "")
        # Information tables are named like "informationtable.xml" or "form13fInfoTable.xml"
        if re.search(r"(infotable|information.?table)\.xml$", name, re.IGNORECASE):
            return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_clean}/{name}"
    return None


def parse_holdings(xml_bytes: bytes) -> list[Holding]:
    """Parse the 13F informationtable.xml. Namespace varies (ns1/ns3/...);
    use a namespace-agnostic XPath via local-name()."""
    root = etree.fromstring(xml_bytes)
    holdings: list[Holding] = []
    for it in root.xpath("//*[local-name()='infoTable']"):
        def text(tag: str) -> str:
            els = it.xpath(f".//*[local-name()='{tag}']")
            return els[0].text if els else ""

        try:
            value = float(text("value") or 0)
        except ValueError:
            value = 0.0
        try:
            shares = int(float(text("sshPrnamt") or 0))
        except ValueError:
            shares = 0

        holdings.append(Holding(
            issuer=text("nameOfIssuer"),
            cusip=text("cusip"),
            value_thousands=value,
            shares=shares,
            title_class=text("titleOfClass"),
        ))
    return holdings


def fetch_and_parse(*, cik: str | None = None, accession: str | None = None,
                    period: str | None = None) -> list[Holding]:
    if accession is None:
        if cik is None:
            raise ValueError("Provide either --cik or --accession")
        found = _latest_13f_accession(cik, period)
        if found is None:
            flag(f"No 13F-HR found for CIK {cik} (period={period}).")
            return []
        accession, fdate = found
        print(f"Using accession {accession} (filed {fdate}).")
    else:
        # Derive CIK from accession (format CIK-YY-NNNNNN)
        cik = accession.split("-")[0].zfill(10)

    xml_url = _information_table_url(cik, accession)
    if xml_url is None:
        flag(f"Could not locate informationtable.xml in {accession}.")
        return []

    xml_bytes = sec_get(xml_url).content
    return parse_holdings(xml_bytes)


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse a 13F-HR information table.")
    ap.add_argument("--cik", default=None, help="Filer CIK (zero-padded or not)")
    ap.add_argument("--accession", default=None,
                    help="Specific accession number, e.g. 0001067983-25-000123")
    ap.add_argument("--period", default=None,
                    help="Report period like 2025-Q4 (filters by reportDate)")
    ap.add_argument("--top", type=int, default=20, help="Print top N holdings by value")
    args = ap.parse_args()

    cik = args.cik.zfill(10) if args.cik else None
    holdings = fetch_and_parse(cik=cik, accession=args.accession, period=args.period)
    if not holdings:
        return

    holdings.sort(key=lambda h: h.value_thousands, reverse=True)
    print(f"\nTop {args.top} holdings ({len(holdings)} total):")
    print(f"{'Issuer':<40} {'CUSIP':<10} {'Shares':>14} {'Value ($000s)':>16}")
    print("-" * 84)
    for h in holdings[:args.top]:
        print(f"{h.issuer[:40]:<40} {h.cusip:<10} {h.shares:>14,} {h.value_thousands:>16,.0f}")


if __name__ == "__main__":
    main()
