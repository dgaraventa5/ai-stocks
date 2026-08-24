"""Litigation red-flag check for /refresh-context Step 2d (added 2026-08-24).

WHY THIS EXISTS
---------------
The 2026-08-24 rating refresh found that BW's subjective ratings rested on a
briefing that knew nothing about a pending securities-fraud class action
naming the company, its Chairman/CEO and its CFO — *Caleb Cho v. Babcock &
Wilcox Enterprises, Inc.*, 5:26-cv-00886 (N.D. Ohio), filed 2026-04-14 —
which alleges the flagship $2.4B AI-datacenter contract was a related-party
deal with the counterparty tied to BW's own ~19% shareholder.

The reason the pipeline missed it is the important part: **the case appears in
none of BW's periodic filings.** The FY2025 10-K predates the complaint; both
10-Qs filed afterwards say "no new litigation to disclose." So the rule-9
earnings-triggered refresh and the Step-2 filings pull both came back clean,
twice, on a name where the central thesis premise was being contested in
federal court. A filings-only view was complete and still wrong.

This check goes outside the filing chain to the court's own docket index, and
— more usefully — cross-checks the two against each other. The signal worth
having is not "a case exists" (plaintiff-firm press releases already spam
that); it is **"a case exists AND the company's own filings don't mention
it,"** which is precisely the blind spot that produced the BW miss.

METHOD (free data, no auth)
---------------------------
1. Query the CourtListener/RECAP index of federal dockets by case name.
   PACER itself requires credentials; Stanford's Securities Class Action
   Clearinghouse is offline until Winter 2026; RECAP is the usable free route.
2. Split results into SECURITIES dockets (nature of suit 850, or a Securities
   Exchange Act cause) and OTHER material dockets (patent/IP, contract) — the
   latter kept at lower prominence because they can bear on D3 moat (e.g.
   MPWR carries active Vicor power-module patent suits).
3. Cross-check against the newest local 10-K/10-Q in per-stock/{T}/filings/:
   if a PENDING securities docket was filed before that filing went out and
   the filing contains no litigation language, report **DISCLOSURE MISMATCH**.

INTERPRETATION DISCIPLINE (read before acting on output)
--------------------------------------------------------
This is a **qualitative red flag for the briefing, NOT a scored metric** —
same standing as the rule-14 expectations flag and the 2b FCF-conversion
check. Specifically:

* A filed complaint is an *allegation*. Plaintiff firms file reflexively after
  any sharp drawdown; most securities class actions settle small or are
  dismissed. Do not treat a hit as established wrongdoing.
* A MISMATCH is **not** an accusation of improper disclosure. Reg S-K Item 103
  requires disclosure of *material* pending proceedings and ASC 450 requires
  it where a material loss is reasonably possible — management may legitimately
  judge a matter immaterial. The script reports dates and lets the analyst
  reason; it does not adjudicate.
* Note the as-of nuance the BW case turns on: a 10-Q's "no new litigation"
  sentence is scoped to its **period end**, not its filing date. A complaint
  filed between period end and filing date creates an apparent mismatch that
  is literally accurate. Both dates are printed for exactly this reason.
* RECAP is a *mirror* of PACER, not PACER. Coverage is good for securities
  dockets but not guaranteed complete — **absence of a hit is weak evidence,
  presence is strong evidence.** Never record "no litigation" as a verified
  fact on the strength of a clean run; record "no federal docket found in
  RECAP."

Usage:
  python3 scripts/litigation_check.py BW
  python3 scripts/litigation_check.py BW MPWR WYFI --years 3
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import time
from pathlib import Path

from common import per_stock_dir

CL_SEARCH = "https://www.courtlistener.com/api/rest/v4/search/"
USER_AGENT = "Dom Researcher dgaraventa5@gmail.com"

# Dropped when deriving search terms from a company's legal name. CourtListener
# case captions abbreviate inconsistently ("Babcock & Wilcox Enterprises, Inc."
# appears as "Babcock & Wilcox Enterprises, Inc." but sibling entities appear as
# "Babcock & Wilcox Solar Energy, Inc."), so matching on the distinctive head of
# the name beats matching the full legal string.
_SUFFIXES = {
    "inc", "inc.", "incorporated", "corp", "corp.", "corporation", "co", "co.",
    "company", "ltd", "ltd.", "limited", "llc", "lp", "plc", "holdings",
    "holding", "group", "enterprises", "international", "technologies",
    "technology", "the", "and", "of", "n.v.", "nv", "sa", "ag", "se",
}
# Litigation language in a periodic filing. Deliberately excludes bare
# "Securities Exchange Act" — every 10-Q cover page cites it.
_LITIGATION_MARKERS = (
    "class action", "putative", "securities litigation", "lead plaintiff",
    "shareholder derivative", "stockholder derivative", "amended complaint",
    "securities class", "10b-5", "10b(5)",
)


def search_terms(company: str, *, max_terms: int = 2) -> list[str]:
    """Distinctive head tokens of a company name, for a caseName query.

    '&' is stripped: CourtListener's query parser silently returns zero results
    for a quoted phrase containing it (this cost a false 'no cases' reading
    during development).
    """
    cleaned = re.sub(r"[^\w\s]", " ", (company or "").replace("&", " "))
    tokens = [t for t in cleaned.split() if t and t.lower() not in _SUFFIXES]
    return tokens[:max_terms]


def build_query(terms: list[str], *, securities_only: bool = False) -> str:
    if not terms:
        return ""
    q = "caseName:(%s)" % " ".join(terms)
    if securities_only:
        q += " AND suitNature:850"
    return q


def is_securities(docket: dict) -> bool:
    nature = (docket.get("suitNature") or "").lower()
    cause = (docket.get("cause") or "").lower()
    return ("850" in nature or "securities" in nature
            or "securities exchange act" in cause or "15:78" in cause)


def is_ip(docket: dict) -> bool:
    nature = (docket.get("suitNature") or "").lower()
    return "830" in nature or "patent" in nature or "trademark" in nature


def is_pending(docket: dict) -> bool:
    return not docket.get("dateTerminated")


def matches_company(docket: dict, terms: list[str]) -> bool:
    """Guard against caption noise — a court-scoped keyword search can return
    unrelated cases (a q=Babcock N.D. Ohio search returns 'Saki v. Norman')."""
    name = (docket.get("caseName") or "").lower()
    return all(t.lower() in name for t in terms) if terms else False


def courtlistener_search(query: str, *, filed_after: str,
                         timeout: int = 30) -> tuple[list[dict], str | None]:
    """Federal dockets from the RECAP index. Returns (results, skip_reason)."""
    import requests  # lazy: deploy-site CI installs only openpyxl+pytest

    try:
        resp = requests.get(
            CL_SEARCH,
            params={"q": query, "type": "r", "filed_after": filed_after,
                    "order_by": "dateFiled desc"},
            headers={"User-Agent": USER_AGENT}, timeout=timeout)
    except Exception as e:  # network down, DNS, TLS
        return [], f"CourtListener unreachable ({type(e).__name__}: {e})"
    if resp.status_code == 429:
        return [], "CourtListener rate-limited (HTTP 429) — retry later"
    if resp.status_code != 200:
        return [], f"CourtListener returned HTTP {resp.status_code}"
    try:
        return resp.json().get("results") or [], None
    except Exception as e:
        return [], f"CourtListener response unparseable ({type(e).__name__}: {e})"


def latest_periodic_filing(ticker: str) -> tuple[Path, str] | None:
    """Newest local 10-K/10-Q as (path, filing_date). Filing date comes from the
    sec_edgar.py filename convention FORM_YYYY-MM-DD_accession.htm."""
    d = per_stock_dir(ticker) / "filings"
    if not d.is_dir():
        return None
    best: tuple[Path, str] | None = None
    for p in d.iterdir():
        m = re.match(r"(10-K|10-Q)_(\d{4}-\d{2}-\d{2})_", p.name)
        if m and (best is None or m.group(2) > best[1]):
            best = (p, m.group(2))
    return best


def filing_mentions_litigation(path: Path) -> bool:
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).lower()
    return any(marker in text for marker in _LITIGATION_MARKERS)


def disclosure_mismatch(securities: list[dict],
                        filing: tuple[Path, str] | None,
                        mentions: bool) -> list[dict]:
    """Pending securities dockets predating the newest filing that the filing
    never mentions. Empty when the filing does discuss litigation."""
    if not filing or mentions:
        return []
    _, filing_date = filing
    return [d for d in securities
            if is_pending(d) and (d.get("dateFiled") or "9999") < filing_date]


def _fmt(d: dict) -> str:
    status = "PENDING" if is_pending(d) else f"terminated {d['dateTerminated']}"
    return (f"      {d.get('caseName')}\n"
            f"        {d.get('docketNumber')} · {d.get('court')} · "
            f"filed {d.get('dateFiled')} · {status}\n"
            f"        {d.get('suitNature') or 'nature n/a'} · "
            f"{d.get('cause') or 'cause n/a'} · judge {d.get('assignedTo') or 'n/a'}")


def check(ticker: str, company: str | None = None, years: int = 3) -> str:
    from datetime import date, timedelta

    company = company or _company_from_watchlist(ticker) or ticker
    terms = search_terms(company)
    if not terms:
        return f"{ticker} SKIPPED — no usable search terms from company name {company!r}"

    filed_after = (date.today() - timedelta(days=365 * years)).isoformat()
    results, skip = courtlistener_search(build_query(terms), filed_after=filed_after)
    if skip:
        return (f"{ticker} SKIPPED — {skip}. Absence of a result here is NOT "
                f"evidence of no litigation; note the skip in the briefing.")

    hits = [d for d in results if matches_company(d, terms)]
    securities = [d for d in hits if is_securities(d)]
    ip = [d for d in hits if is_ip(d) and d not in securities]

    filing = latest_periodic_filing(ticker)
    mentions = filing_mentions_litigation(filing[0]) if filing else False
    mismatches = disclosure_mismatch(securities, filing, mentions)

    out = [f"=== {ticker} ({company}) — federal dockets since {filed_after} "
           f"[caseName:({' '.join(terms)})] ==="]
    if not hits:
        out.append("  No federal docket found in RECAP. NOTE: RECAP mirrors "
                   "PACER and is not guaranteed complete — record this as "
                   "'no docket found', not as 'no litigation'.")
    if securities:
        out.append(f"  SECURITIES dockets ({len(securities)}):")
        out += [_fmt(d) for d in securities]
    if ip:
        out.append(f"  IP/patent dockets ({len(ip)}) — may bear on D3 moat:")
        out += [_fmt(d) for d in ip]

    if filing:
        path, fdate = filing
        out.append(f"  Newest local filing: {path.name} (filed {fdate}); "
                   f"litigation language present: {'YES' if mentions else 'NO'}")
    else:
        out.append("  Newest local filing: NONE cached — run sec_edgar.py first "
                   "for the disclosure cross-check.")

    if mismatches:
        out.append(f"  ⚠️  DISCLOSURE MISMATCH ({len(mismatches)}): pending "
                   f"securities docket(s) filed before {filing[1]}, and that "
                   f"filing contains no litigation language.")
        for d in mismatches:
            out.append(f"      {d.get('docketNumber')} filed {d.get('dateFiled')} "
                       f"vs filing dated {filing[1]}")
        out.append("      Check the as-of date: a 10-Q's 'no new litigation' "
                   "sentence is scoped to PERIOD END, not filing date. A "
                   "complaint filed after period end is disclosed literally "
                   "accurately. Read the filing's Item 1 before concluding "
                   "anything, and do NOT allege improper disclosure — "
                   "materiality under Reg S-K Item 103 / ASC 450 is "
                   "management's judgment.")
    elif securities:
        out.append("  No disclosure mismatch: the newest filing discusses "
                   "litigation, or the docket postdates it.")
    return "\n".join(out)


def _company_from_watchlist(ticker: str) -> str | None:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(
            Path(__file__).resolve().parents[1] / "00-master" /
            "ai_supply_chain_scoring.xlsx", data_only=True, read_only=True)
        ws = wb["Watchlist"]
        rows = ws.iter_rows(values_only=True)
        header = list(next(rows))
        t_i, c_i = header.index("Ticker"), header.index("Company")
        for row in rows:
            if row[t_i] == ticker:
                return row[c_i]
    except Exception:
        return None
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tickers", nargs="+")
    ap.add_argument("--years", type=int, default=3,
                    help="lookback window for dateFiled (default 3)")
    ap.add_argument("--company", help="override company name (single ticker)")
    args = ap.parse_args(argv)

    for i, t in enumerate(args.tickers):
        if i:
            time.sleep(1.0)  # be polite to a free service
        print(check(t.upper(), args.company if len(args.tickers) == 1 else None,
                    args.years))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
