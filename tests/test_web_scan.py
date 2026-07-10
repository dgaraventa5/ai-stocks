"""Regression tests for the web-scan fallback (scripts/web_scan.py).

Guards the two things that made the ad-hoc WebSearch fallback leak material events
for weeks, per the 2026-07-10 scan retro:
  1. date verification — undated hits must be surfaced as UNVERIFIED, never assumed
     in-window; out-of-window hits must be dropped.
  2. the materiality-keyword net — must flag the headline-light items that four scans
     missed (AVGO CFO transition, MU×Anthropic strategic agreement).
"""

from datetime import date

import web_scan as ws


# --- date parsing ---------------------------------------------------------

def test_parse_iso():
    assert ws.parse_date("filed 2026-07-09 by the company", 2026) == date(2026, 7, 9)


def test_parse_long_form():
    assert ws.parse_date("July 9, 2026", 2026) == date(2026, 7, 9)
    assert ws.parse_date("Jun 12, 2026 effective", 2026) == date(2026, 6, 12)


def test_parse_month_day_no_year_defaults_to_window_year():
    assert ws.parse_date("posted July 9", 2026) == date(2026, 7, 9)


def test_parse_slash_and_url():
    assert ws.parse_date("7/9/2026", 2026) == date(2026, 7, 9)
    assert ws.parse_date("https://x.com/2026/07/09/story", 2026) == date(2026, 7, 9)


def test_unparseable_returns_none():
    assert ws.parse_date("no date here at all", 2026) is None
    assert ws.parse_date("", 2026) is None


# --- materiality classification ------------------------------------------

def test_avgo_cfo_headline_is_material_leadership():
    """The exact item four consecutive scans missed — a CFO change with no big number."""
    cats = ws.classify("Broadcom names Amie Thuener as CFO as Kirsten Spears to retire")
    assert "leadership" in cats


def test_mu_anthropic_headline_is_material():
    cats = ws.classify(
        "Micron and Anthropic Announce Strategic Agreement to Scale AI Infrastructure")
    assert "m_and_a" in cats


def test_routine_headline_is_not_material():
    assert ws.classify("Company posts routine investor overview page") == []


# --- window verification --------------------------------------------------

def _res(ticker, title, d=None, url="", snippet=""):
    r = {"ticker": ticker, "title": title, "url": url, "snippet": snippet}
    if d is not None:
        r["date"] = d
    return r


def test_verify_partitions_correctly():
    results = [
        _res("SNDK", "SanDisk multi-year flash supply deal with Meta", "2026-07-09"),
        _res("AVGO", "Broadcom names new CFO", "2026-06-12"),          # out of window
        _res("NVDA", "undated product page"),                          # unverified
        _res("TSM", "TSMC routine overview", "2026-07-05"),            # in-window, routine
    ]
    out = ws.verify_results(results, date(2026, 7, 3), date(2026, 7, 10))

    assert [m["ticker"] for m in out["material"]] == ["SNDK"]
    assert out["material"][0]["categories"] == ["capacity_contract"]
    assert [u["ticker"] for u in out["unverified"]] == ["NVDA"]
    assert [o["ticker"] for o in out["out_of_window"]] == ["AVGO"]
    assert [r["ticker"] for r in out["routine"]] == ["TSM"]


def test_undated_never_silently_kept_in_window():
    """Rule 3: a hit with no parseable date is UNVERIFIED, not assumed in-window."""
    out = ws.verify_results([_res("X", "Big CFO departure, no date given")],
                            date(2026, 7, 3), date(2026, 7, 10))
    assert out["material"] == []
    assert len(out["unverified"]) == 1
