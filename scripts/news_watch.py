"""Dated news headlines for the daily-watch scope, from Google News RSS.

Why this exists (2026-11-12 diagnosis, IMPROVEMENTS.md): the daily watch's news
step was one WebSearch per name in "standard" mode with a query like
"Nvidia NVDA news October 28 2026". For six weeks that search returned
evergreen SEO pages and the same calendar date one year earlier (e.g.
"stockstory 2025 10 28 why nvidia nvda stock is up today"), so runs logged
"no dated in-window web news for any scope name" and called the day quiet.
Only 108 of 851 standard-mode results across all daily-watch runs (13%)
carried a single Oct/Nov-2026 URL. That is how the NYT's 10-29 report on NVIDIA's CEO,
the Reuters 10-28 DOJ inquiry into the Hugging Face deal, and two weeks of
follow-ups never reached a news-log.

This helper replaces the guesswork with a dated feed: one Google News RSS
query per name, `after:`/`before:` bounded, every item carrying a publisher
and a publication timestamp. It filters to the window on the US/Eastern date,
tags headlines that match material-event words (a sort hint for the reader,
never a judgment), and fails closed:

  blocked  more than 20% of lookups failed (network, non-RSS reply)
  thin     more than half of the names that were looked up came back with
           zero in-window items — for holdings and the top 25 that means the
           feed or the query broke, not that the world went quiet

Either exits 1 with "do not report as quiet". Free source, no key, stdlib
only (CI minimal-env rule). Read-only: writes nothing but `--out`.

Replay a past window:
    python3 scripts/news_watch.py --tickers NVDA --from 2026-10-29 --to 2026-10-29
"""
from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
WORKBOOK = ROOT / "00-master" / "ai_supply_chain_scoring.xlsx"
HOLDS = ROOT / "00-master" / "entry-holds.json"
EASTERN = ZoneInfo("America/New_York")
FEED = "https://news.google.com/rss/search"
USER_AGENT = "Mozilla/5.0 (compatible; research-news-watch/1.0)"
MAX_FAILURE_RATE = 0.20
MAX_EMPTY_RATE = 0.50
ITEMS_PER_NAME = 15            # newest first; the count reports the full total
PAUSE_SECONDS = 1.0

# Legal-form words dropped from the Watchlist company name before quoting it.
# "Vertiv Holdings" → "Vertiv"; "NVIDIA Corporation" → "NVIDIA".
_SUFFIXES = {"inc", "inc.", "corp", "corp.", "corporation", "co", "co.",
             "company", "ltd", "ltd.", "limited", "plc", "holdings", "holding",
             "group", "n.v.", "nv", "s.a.", "sa", "ag", "se", "the"}

# Words that mark a headline worth opening first. A sort hint, not a verdict:
# the daily-watch reader still decides materiality against the skill's list.
MATERIAL_HINTS = re.compile(
    r"\b(ceo|cfo|cto|chief executive|resign\w*|steps? down|step down|ousted|"
    r"fired|succession|interim|board|probe\w*|investigat\w*|subpoena\w*|doj|"
    r"justice department|sec charges|ftc|antitrust|regulator\w*|lawsuit|sues|"
    r"sued|class action|indict\w*|fraud|spy|espionage|export control\w*|"
    r"sanction\w*|ban\w*|tariff\w*|acquir\w*|acquisition|merger|takeover|"
    r"buyout|divest\w*|spin-?off|guidance|outlook cut|cuts? forecast|"
    r"warns?|recall\w*|short seller|restat\w*|auditor|going concern|"
    r"bankrupt\w*|downgrade[sd]? by moody|default|congress\w*|house committee|"
    r"senate)\b", re.I)


def query_name(company: str | None, ticker: str) -> str:
    """The quoted search phrase for one name: company name minus legal forms."""
    words = [w for w in str(company or "").replace(",", " ").split()
             if w.lower() not in _SUFFIXES]
    return " ".join(words) if words else ticker


def feed_url(phrase: str, start: dt.date, end: dt.date) -> str:
    """Google News RSS search URL bounded one day either side of the window
    (the operators are coarse; the exact window is applied to pubDate)."""
    q = (f'"{phrase}" after:{(start - dt.timedelta(days=1)).isoformat()} '
         f'before:{(end + dt.timedelta(days=1)).isoformat()}')
    return FEED + "?" + urllib.parse.urlencode(
        {"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})


def parse_feed(xml_text: str) -> list[dict]:
    """RSS → items. Raises ValueError on anything that is not an RSS channel
    (a consent page or an HTML error must count as a failed lookup)."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise ValueError(f"not RSS: {e}") from e
    if root.find("channel") is None:
        raise ValueError("not RSS: no <channel>")
    items = []
    for it in root.iter("item"):
        raw = it.findtext("pubDate") or ""
        try:
            published = email.utils.parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            published = None
        if published is not None and published.tzinfo is None:
            published = published.replace(tzinfo=dt.timezone.utc)
        items.append({"title": (it.findtext("title") or "").strip(),
                      "source": (it.findtext("source") or "").strip(),
                      "link": (it.findtext("link") or "").strip(),
                      "published": published})
    return items


def in_window(items: list[dict], start: dt.date, end: dt.date) -> list[dict]:
    """Keep items whose US/Eastern publication date is in [start, end],
    newest first. An undated item is dropped: undated is unverified."""
    kept = []
    for i in items:
        p = i["published"]
        if p is None:
            continue
        d = p.astimezone(EASTERN).date()
        if start <= d <= end:
            kept.append({"date": d.isoformat(),
                         "published": p.astimezone(EASTERN).isoformat(),
                         "source": i["source"],
                         "title": i["title"],
                         "link": i["link"],
                         "hint": bool(MATERIAL_HINTS.search(i["title"]))})
    kept.sort(key=lambda x: x["published"], reverse=True)
    return kept


def verdict(n_attempted: int, n_failed: int, n_empty: int) -> dict:
    """blocked = too many failed lookups; thin = too many names with nothing.
    Either one means the window cannot be reported as quiet."""
    looked = n_attempted - n_failed
    blocked = n_attempted == 0 or n_failed / n_attempted > MAX_FAILURE_RATE
    thin = looked > 0 and n_empty / looked > MAX_EMPTY_RATE
    return {"blocked": blocked, "thin": thin}


def _fetch(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def _companies() -> dict[str, str]:
    from openpyxl import load_workbook                  # lazy (CI minimal-env)
    ws = load_workbook(WORKBOOK, read_only=True, data_only=True)["Watchlist"]
    out = {}
    for t, name in ws.iter_rows(min_row=2, max_col=2, values_only=True):
        if not t:
            break
        out[str(t).strip().upper()] = str(name or "").strip()
    return out


def _hold_names() -> list[str]:
    try:
        holds = json.loads(HOLDS.read_text())
    except (OSError, ValueError):
        return []
    return sorted(k.upper() for k in holds if not k.startswith("_"))


def _scope() -> list[str]:
    import scheduled_run                                 # read-only reuse
    return scheduled_run._scope("watch")


def run(tickers: list[str], start: dt.date, end: dt.date,
        companies: dict[str, str], fetch=_fetch, sleep=time.sleep) -> dict:
    names, failed, empty = [], [], []
    for n, t in enumerate(tickers):
        phrase = query_name(companies.get(t), t)
        url = feed_url(phrase, start, end)
        try:
            items = in_window(parse_feed(fetch(url)), start, end)
        except Exception as e:                          # noqa: BLE001
            failed.append({"ticker": t, "query": phrase,
                           "error": f"{type(e).__name__}: {str(e)[:80]}"})
            continue
        finally:
            if n < len(tickers) - 1:
                sleep(PAUSE_SECONDS)
        if not items:
            empty.append(t)
        names.append({"ticker": t, "query": phrase, "count": len(items),
                      "hinted": sum(i["hint"] for i in items),
                      "items": sorted(items, key=lambda i: not i["hint"])
                               [:ITEMS_PER_NAME]})
    report = {"from": start.isoformat(), "to": end.isoformat(),
              "attempted": len(tickers), "failed": failed, "empty": empty,
              "names": names}
    report.update(verdict(len(tickers), len(failed), len(empty)))
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tickers", nargs="+",
                   help="names to check (default: holdings ∪ top 25, plus "
                        "every name with an entry hold)")
    p.add_argument("--days", type=int, default=2,
                   help="window length ending today (default 2)")
    p.add_argument("--from", dest="start", type=dt.date.fromisoformat)
    p.add_argument("--to", dest="end", type=dt.date.fromisoformat)
    p.add_argument("--out", help="write the JSON report here")
    a = p.parse_args(argv)

    end = a.end or dt.datetime.now(EASTERN).date()
    start = a.start or end - dt.timedelta(days=a.days)
    tickers = ([t.upper() for t in a.tickers] if a.tickers
               else sorted(set(_scope()) | set(_hold_names())))
    report = run(tickers, start, end, _companies(),
                 fetch=_fetch, sleep=time.sleep)

    text = json.dumps(report, indent=2)
    if a.out:
        Path(a.out).write_text(text + "\n")
    else:
        print(text)
    hinted = [f"{n['ticker']}({n['hinted']})" for n in report["names"] if n["hinted"]]
    print(f"news {start}..{end}: {len(report['names'])} names looked up, "
          f"{len(report['failed'])} failed, {len(report['empty'])} empty; "
          f"hinted: {', '.join(hinted) or 'none'}"
          + (f" → {a.out}" if a.out else ""), file=sys.stderr)
    if report["blocked"] or report["thin"]:
        why = "too many lookups failed" if report["blocked"] else \
              "too many names returned nothing"
        print(f"NEWS WATCH {'BLOCKED' if report['blocked'] else 'THIN'}: {why} "
              "— do not report this window as quiet", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
