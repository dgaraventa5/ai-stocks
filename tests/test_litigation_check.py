"""Litigation red-flag check (/refresh-context Step 2d, added 2026-08-24).

Pure-logic tests only — no network. `litigation_check` imports `requests`
lazily inside courtlistener_search precisely so this module stays importable
in the deploy-site CI env, which installs only openpyxl + pytest.
"""
from pathlib import Path

import litigation_check as lc

# The real BW docket that motivated this check.
BW_CHO = {
    "caseName": "Cho v. Babcock & Wilcox Enterprises, Inc.",
    "docketNumber": "5:26-cv-00886",
    "court": "District Court, N.D. Ohio",
    "dateFiled": "2026-04-14",
    "dateTerminated": None,
    "suitNature": "850 Securities/Commodities",
    "cause": "15:78m(a) Securities Exchange Act",
    "assignedTo": "Sara Elizabeth Lioi",
}
# Real noise from a court-scoped q=Babcock search — must not match.
NOISE = {
    "caseName": "Saki v. Norman", "docketNumber": "1:26-cv-01148",
    "dateFiled": "2026-05-17", "dateTerminated": None,
    "suitNature": "440 Civil Rights: Other", "cause": "42:1983 Civil Rights Act",
}
MPWR_VICOR = {
    "caseName": "Vicor Corporation v. Monolithic Power Systems, Inc.",
    "docketNumber": "7:26-cv-00005", "dateFiled": "2026-01-09",
    "dateTerminated": None, "suitNature": "830 Patent",
    "cause": "35:271 Patent Infringement",
}
TERMINATED = dict(BW_CHO, docketNumber="1:20-cv-00001",
                  dateFiled="2020-01-01", dateTerminated="2021-08-09")


def test_search_terms_strips_suffixes_and_ampersand():
    # '&' must go: CourtListener returns zero results for a quoted phrase
    # containing it, which reads as "no litigation" and is a false clean.
    assert lc.search_terms("Babcock & Wilcox Enterprises, Inc.") == ["Babcock", "Wilcox"]
    assert lc.search_terms("WhiteFiber, Inc.") == ["WhiteFiber"]
    assert lc.search_terms("HIVE Digital Technologies Ltd.") == ["HIVE", "Digital"]
    assert lc.search_terms("Power Solutions International, Inc.") == ["Power", "Solutions"]


def test_search_terms_handles_empty_company():
    assert lc.search_terms("") == []
    assert lc.search_terms(None) == []


def test_build_query_shapes():
    assert lc.build_query(["Babcock", "Wilcox"]) == "caseName:(Babcock Wilcox)"
    assert lc.build_query(["Babcock"], securities_only=True) == \
        "caseName:(Babcock) AND suitNature:850"
    assert lc.build_query([]) == ""


def test_classification():
    assert lc.is_securities(BW_CHO)
    assert not lc.is_securities(NOISE)
    assert not lc.is_securities(MPWR_VICOR)
    assert lc.is_ip(MPWR_VICOR)
    assert not lc.is_ip(BW_CHO)


def test_pending_vs_terminated():
    assert lc.is_pending(BW_CHO)
    assert not lc.is_pending(TERMINATED)


def test_matches_company_rejects_caption_noise():
    terms = ["Babcock", "Wilcox"]
    assert lc.matches_company(BW_CHO, terms)
    assert not lc.matches_company(NOISE, terms)
    assert not lc.matches_company(BW_CHO, [])


def test_disclosure_mismatch_fires_on_the_bw_pattern():
    # Q2 10-Q filed 2026-08-10, complaint 2026-04-14, no litigation language.
    filing = (Path("10-Q_2026-08-10_x.htm"), "2026-08-10")
    assert lc.disclosure_mismatch([BW_CHO], filing, mentions=False) == [BW_CHO]


def test_no_mismatch_when_filing_discusses_litigation():
    filing = (Path("10-Q_2026-08-10_x.htm"), "2026-08-10")
    assert lc.disclosure_mismatch([BW_CHO], filing, mentions=True) == []


def test_no_mismatch_when_docket_postdates_the_filing():
    # BW's Q1 10-Q went out 2026-05-11 but a complaint filed later can't be a
    # mismatch — and a terminated case never is.
    early = (Path("10-Q_2026-03-01_x.htm"), "2026-03-01")
    assert lc.disclosure_mismatch([BW_CHO], early, mentions=False) == []
    late = (Path("10-Q_2026-08-10_x.htm"), "2026-08-10")
    assert lc.disclosure_mismatch([TERMINATED], late, mentions=False) == []


def test_no_mismatch_without_a_cached_filing():
    assert lc.disclosure_mismatch([BW_CHO], None, mentions=False) == []


def test_litigation_markers_exclude_boilerplate(tmp_path):
    # Every 10-Q cover page cites the Securities Exchange Act — that alone must
    # not read as "this filing discusses litigation".
    boiler = tmp_path / "f.htm"
    boiler.write_text("<p>pursuant to the Securities Exchange Act of 1934</p>")
    assert not lc.filing_mentions_litigation(boiler)

    real = tmp_path / "g.htm"
    real.write_text("<p>a putative <b>class action</b> was filed</p>")
    assert lc.filing_mentions_litigation(real)


def test_filing_mentions_litigation_missing_file():
    assert not lc.filing_mentions_litigation(Path("/nonexistent/x.htm"))


def test_latest_periodic_filing_picks_newest_and_ignores_8k(tmp_path, monkeypatch):
    d = tmp_path / "BW" / "filings"
    d.mkdir(parents=True)
    for n in ("10-Q_2026-05-11_a.htm", "10-Q_2026-08-10_b.htm",
              "10-K_2026-03-16_c.htm", "8-K_2026-08-21_d.htm"):
        (d / n).write_text("x")
    monkeypatch.setattr(lc, "per_stock_dir", lambda t, **k: tmp_path / t)
    got = lc.latest_periodic_filing("BW")
    assert got is not None and got[1] == "2026-08-10"
    assert got[0].name == "10-Q_2026-08-10_b.htm"


def test_latest_periodic_filing_none_when_no_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(lc, "per_stock_dir", lambda t, **k: tmp_path / t)
    assert lc.latest_periodic_filing("NOPE") is None
