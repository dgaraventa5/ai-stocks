"""Parse Form 4 (insider transactions) for a ticker and summarize.

Used to inform M3 (Insider Activity) per templates/rating-rubric-and-workflow.md.

Critical distinctions the rubric cares about:
  P = Open-market PURCHASE     ← the signal per Lakonishok & Lee (2001)
  S = Open-market SALE          ← much noisier; routine after rallies
  M = Option exercise + sale   ← often tax management, not view
  F = Tax withhold (RSU vest)  ← routine, not discretionary
  A = Grant/Award              ← compensation, not signal
  G = Gift                      ← not signal
  D = Disposition (non-open)
  V = Transaction reported voluntarily

10b5-1 flag: plan transactions are pre-scheduled; treat as routine.

Usage:
  python3 scripts/parse_form4.py CEG
  python3 scripts/parse_form4.py CEG --since 2025-05-17
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from collections import defaultdict
from pathlib import Path

from lxml import etree

from common import ROOT, per_stock_dir

CODE_DESC = {
    "P": "Open-mkt buy",       # the signal
    "S": "Open-mkt sale",
    "M": "Option exercise",
    "F": "Tax withhold (RSU)",
    "A": "Grant/Award",
    "G": "Gift",
    "D": "Disposition",
    "V": "Voluntary",
    "X": "Option exercise",
    "C": "Conversion",
    "I": "Discretionary",
    "J": "Other (J)",
    "K": "Equity swap",
}


def _txt(node, xpath: str) -> str:
    els = node.xpath(xpath)
    if not els:
        return ""
    t = els[0].text if hasattr(els[0], "text") else str(els[0])
    return (t or "").strip()


def _float(node, xpath: str, default: float = 0.0) -> float:
    s = _txt(node, xpath)
    try:
        return float(s)
    except ValueError:
        return default


def _is_10b5_1(doc_root) -> bool:
    # Multiple ways filings flag a 10b5-1 plan
    flag_nodes = doc_root.xpath("//rule10b5_1Flag/value")
    for n in flag_nodes:
        if (n.text or "").strip() in ("1", "true", "TRUE"):
            return True
    # Or it shows up in a footnote
    for fn in doc_root.xpath("//footnote"):
        if fn.text and re.search(r"10b5[-\s–]?1", fn.text):
            return True
    return False


def parse_file(path: Path) -> list[dict]:
    doc = etree.parse(str(path)).getroot()
    reporter = _txt(doc, "//rptOwnerName")
    title = _txt(doc, "//officerTitle")
    relation = []
    if doc.xpath("//isOfficer[normalize-space()='1' or normalize-space()='true']"):
        relation.append("Officer")
    if doc.xpath("//isDirector[normalize-space()='1' or normalize-space()='true']"):
        relation.append("Director")
    if doc.xpath("//isTenPercentOwner[normalize-space()='1' or normalize-space()='true']"):
        relation.append("10%Owner")
    is_10b5 = _is_10b5_1(doc)

    rows = []
    for tx in doc.xpath("//nonDerivativeTransaction"):
        date = _txt(tx, ".//transactionDate/value")
        code = _txt(tx, ".//transactionCode")
        ad_code = _txt(tx, ".//transactionAcquiredDisposedCode/value")  # A or D
        shares = _float(tx, ".//transactionShares/value")
        price = _float(tx, ".//transactionPricePerShare/value")
        post = _float(tx, ".//sharesOwnedFollowingTransaction/value")
        rows.append(dict(
            file=path.name, date=date, reporter=reporter, title=title,
            relation="/".join(relation), code=code, ad=ad_code,
            shares=shares, price=price, value=shares * price,
            post_shares=post, is_10b5=is_10b5,
        ))
    return rows


def summarize(ticker: str, since: str | None = None) -> None:
    d = per_stock_dir(ticker) / "filings"
    files = sorted(d.glob("4_*.xml"))
    if since:
        files = [f for f in files if f.name.split("_")[1] >= since]
    if not files:
        print(f"No Form 4 files in {d.relative_to(ROOT)} (since={since}).")
        return

    all_rows = []
    parse_errors = 0
    for fp in files:
        try:
            all_rows.extend(parse_file(fp))
        except Exception as e:
            parse_errors += 1
            print(f"  parse error {fp.name}: {e}")

    print(f"\nParsed {len(files) - parse_errors}/{len(files)} Form 4 files for {ticker}.")
    print(f"Total non-derivative transactions: {len(all_rows)}")
    print()

    # --- Headline detail table ---
    print(f"{'Date':<11} {'Reporter':<26} {'Role':<16} {'Code':<5} {'A/D':<4} "
          f"{'Shares':>10} {'$/sh':>9} {'Value $':>14} {'10b5-1'}")
    print("-" * 115)
    for r in sorted(all_rows, key=lambda x: x["date"]):
        print(f"{r['date']:<11} {r['reporter'][:26]:<26} {r['relation'][:16]:<16} "
              f"{r['code']:<5} {r['ad']:<4} {r['shares']:>10,.0f} {r['price']:>9,.2f} "
              f"${r['value']:>13,.0f} {'Y' if r['is_10b5'] else ''}")

    # --- Aggregation ---
    by_code = defaultdict(lambda: {"n": 0, "shares": 0, "value": 0})
    by_code_10b5 = defaultdict(lambda: {"n": 0, "shares": 0, "value": 0})
    for r in all_rows:
        b = by_code_10b5[r["code"]] if r["is_10b5"] else by_code[r["code"]]
        b["n"] += 1
        b["shares"] += r["shares"]
        b["value"] += r["value"]

    print("\nBy transaction code (discretionary):")
    for code in sorted(by_code):
        b = by_code[code]
        print(f"  {code} {CODE_DESC.get(code,'?'):<22} {b['n']:>3} tx  {b['shares']:>14,.0f} sh  "
              f"${b['value']:>15,.0f}")
    print("\nBy transaction code (10b5-1 plan):")
    for code in sorted(by_code_10b5):
        b = by_code_10b5[code]
        print(f"  {code} {CODE_DESC.get(code,'?'):<22} {b['n']:>3} tx  {b['shares']:>14,.0f} sh  "
              f"${b['value']:>15,.0f}")

    # --- The rubric-relevant headline ---
    open_market_buys = [r for r in all_rows if r["code"] == "P"]
    open_market_sales = [r for r in all_rows if r["code"] == "S" and not r["is_10b5"]]

    print(f"\n{'=' * 60}")
    print("M3 SIGNAL (per rubric):")
    print(f"  Open-market PURCHASES (code P): {len(open_market_buys)}")
    if open_market_buys:
        for r in open_market_buys:
            print(f"    {r['date']} {r['reporter']}: {r['shares']:,.0f} sh @ ${r['price']:.2f}")
    else:
        print("    (none — absence of buying is itself the signal)")
    print(f"  Discretionary open-market SALES (S, not 10b5-1): {len(open_market_sales)}")
    print(f"  10b5-1 programmed transactions: {sum(1 for r in all_rows if r['is_10b5'])}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("--since", default=None, help="Floor date YYYY-MM-DD")
    args = ap.parse_args()
    summarize(args.ticker, since=args.since)


if __name__ == "__main__":
    main()
