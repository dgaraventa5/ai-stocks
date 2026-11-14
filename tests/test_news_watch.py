"""Offline tests for scripts/news_watch.py (the daily-watch news feed).

Regression for the 2026-10-29 → 11-11 miss: a holding's front-page story
never reached the news-log because the search returned last year's
same-date pages and the run read "nothing dated" as quiet. Headlines here
are fictional stand-ins of the same shape.
"""
import datetime as dt
import sys
import urllib.parse
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import news_watch as nw  # noqa: E402

D = dt.date


def rss(*items):
    body = "".join(
        f"<item><title>{t}</title><link>https://news.example/{n}</link>"
        + (f"<pubDate>{p}</pubDate>" if p else "")
        + f"<source url='https://pub.example'>{s}</source></item>"
        for n, (t, p, s) in enumerate(items))
    return f"<?xml version='1.0'?><rss><channel><title>x</title>{body}</channel></rss>"


# The real failure in miniature: one in-window story, and the year-earlier
# same-date SEO page that the old search returned instead.
MISS_DAY = rss(
    ("Chipmaker's chief seen as target of foreign spy plot - Wire",
     "Thu, 29 Oct 2026 14:05:00 GMT", "Wire"),
    ("Why ChipCo stock is up today", "Tue, 28 Oct 2025 18:00:00 GMT", "SEO Farm"),
    ("ChipCo stock news today", None, "Evergreen"),
)


def test_regression_in_window_story_is_kept_and_hinted_stale_pages_dropped():
    items = nw.in_window(nw.parse_feed(MISS_DAY), D(2026, 10, 29), D(2026, 10, 29))
    assert [i["title"][:20] for i in items] == ["Chipmaker's chief se"]
    assert items[0]["hint"] is True
    assert items[0]["date"] == "2026-10-29"


def test_window_uses_eastern_date():
    # 02:30 GMT on 10-30 is still 10-29 in New York.
    feed = rss(("Late story", "Fri, 30 Oct 2026 02:30:00 GMT", "Wire"))
    assert nw.in_window(nw.parse_feed(feed), D(2026, 10, 29), D(2026, 10, 29))
    assert not nw.in_window(nw.parse_feed(feed), D(2026, 10, 30), D(2026, 10, 30))


def test_undated_and_unparseable_dates_are_dropped():
    feed = rss(("No date", None, "A"), ("Bad date", "not a date", "B"))
    assert nw.in_window(nw.parse_feed(feed), D(2026, 1, 1), D(2030, 1, 1)) == []


def test_newest_first():
    feed = rss(("older", "Thu, 29 Oct 2026 10:00:00 GMT", "A"),
               ("newer", "Thu, 29 Oct 2026 20:00:00 GMT", "B"))
    items = nw.in_window(nw.parse_feed(feed), D(2026, 10, 29), D(2026, 10, 29))
    assert [i["title"] for i in items] == ["newer", "older"]


@pytest.mark.parametrize("text", ["<html><body>Before you continue</body></html>",
                                  "not xml at all", "<rss></rss>"])
def test_non_rss_reply_is_a_failure_not_an_empty_feed(text):
    with pytest.raises(ValueError):
        nw.parse_feed(text)


@pytest.mark.parametrize("company,ticker,want", [
    ("NVIDIA Corporation", "NVDA", "NVIDIA"),
    ("Vertiv Holdings", "VRT", "Vertiv"),
    ("Comfort Systems USA", "FIX", "Comfort Systems USA"),
    ("Taiwan Semiconductor Manufacturing Co., Ltd.", "TSM",
     "Taiwan Semiconductor Manufacturing"),
    ("", "XYZ", "XYZ"),
    (None, "XYZ", "XYZ"),
])
def test_query_name_drops_legal_forms(company, ticker, want):
    assert nw.query_name(company, ticker) == want


def test_feed_url_quotes_the_name_and_pads_the_window():
    url = nw.feed_url("Vertiv", D(2026, 10, 29), D(2026, 10, 30))
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["q"][0]
    assert q == '"Vertiv" after:2026-10-28 before:2026-10-31'
    # no calendar-date words: those matched last year's same-date pages
    assert "October" not in q


@pytest.mark.parametrize("title,hint", [
    ("ChipCo CEO resigns after board probe", True),
    ("Regulators open antitrust investigation into ChipCo deal", True),
    ("ChipCo to acquire SoftCo for $12B", True),
    ("ChipCo cuts guidance for fourth quarter", True),
    ("ChipCo shares rise 3% in morning trade", False),
    ("Analyst raises ChipCo price target", False),
])
def test_material_hints(title, hint):
    assert bool(nw.MATERIAL_HINTS.search(title)) is hint


def test_verdict_blocked_and_thin():
    assert nw.verdict(25, 0, 3) == {"blocked": False, "thin": False}
    assert nw.verdict(25, 6, 0)["blocked"]            # 24% failed
    assert not nw.verdict(25, 5, 0)["blocked"]        # exactly 20% is allowed
    assert nw.verdict(25, 0, 13)["thin"]              # 13 of 25 empty
    assert not nw.verdict(25, 0, 12)["thin"]
    assert nw.verdict(0, 0, 0)["blocked"]             # nothing looked up
    assert not nw.verdict(4, 4, 0)["thin"]            # all failed: blocked, not thin


def test_run_counts_failures_and_empties_and_never_sleeps_after_last():
    feeds = {"Alpha": MISS_DAY,
             "Beta": rss(("old", "Mon, 01 Jan 2024 00:00:00 GMT", "A"))}
    sleeps = []

    def fetch(url):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["q"][0]
        name = q.split('"')[1]
        if name == "Gamma":
            raise OSError("timed out")
        return feeds[name]

    r = nw.run(["AAA", "BBB", "CCC"], D(2026, 10, 29), D(2026, 10, 29),
               {"AAA": "Alpha Inc.", "BBB": "Beta Corp", "CCC": "Gamma Ltd"},
               fetch=fetch, sleep=sleeps.append)
    assert [n["ticker"] for n in r["names"]] == ["AAA", "BBB"]
    assert r["names"][0]["count"] == 1 and r["names"][0]["hinted"] == 1
    assert r["empty"] == ["BBB"]
    assert [f["ticker"] for f in r["failed"]] == ["CCC"]
    assert r["blocked"]                                # 1 of 3 failed > 20%
    assert len(sleeps) == 2


def test_main_exits_nonzero_when_thin(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(nw, "_companies", lambda: {"AAA": "Alpha"})
    monkeypatch.setattr(nw, "_fetch", lambda url: rss())
    monkeypatch.setattr(nw.time, "sleep", lambda s: None)
    out = tmp_path / "news.json"
    code = nw.main(["--tickers", "AAA", "--from", "2026-10-29", "--to",
                    "2026-10-29", "--out", str(out)])
    assert code == 1
    assert "do not report this window as quiet" in capsys.readouterr().err
    assert out.exists()


def test_main_exits_zero_on_a_normal_window(monkeypatch, tmp_path):
    monkeypatch.setattr(nw, "_companies", lambda: {"AAA": "Alpha"})
    monkeypatch.setattr(nw, "_fetch", lambda url: MISS_DAY)
    monkeypatch.setattr(nw.time, "sleep", lambda s: None)
    assert nw.main(["--tickers", "AAA", "--from", "2026-10-29", "--to",
                    "2026-10-29", "--out", str(tmp_path / "n.json")]) == 0
