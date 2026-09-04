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


class _Resp:
    def __init__(self, status, payload=None):
        self.status_code, self._p = status, payload or {}
    def json(self):
        return self._p


def test_rate_limit_is_retried_then_succeeds(monkeypatch):
    """429 must not silently shrink sweep coverage — a skipped name reads like
    a clean one when you are scanning 30 of them."""
    calls, slept = [], []
    seq = [_Resp(429), _Resp(429), _Resp(200, {"results": [BW_CHO]})]

    def fake_get(*a, **k):
        calls.append(1)
        return seq[len(calls) - 1]

    monkeypatch.setitem(__import__("sys").modules, "requests",
                        type("m", (), {"get": staticmethod(fake_get)}))
    res, skip = lc.courtlistener_search("q", filed_after="2023-01-01",
                                        backoff=0.01, sleep=slept.append)
    assert skip is None and res == [BW_CHO]
    assert len(calls) == 3 and len(slept) == 2
    assert slept[1] > slept[0]  # exponential


def test_rate_limit_gives_up_honestly(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "requests",
                        type("m", (), {"get": staticmethod(lambda *a, **k: _Resp(429))}))
    res, skip = lc.courtlistener_search("q", filed_after="2023-01-01",
                                        retries=2, backoff=0.01, sleep=lambda s: None)
    assert res == [] and "rate-limited" in skip and "rerun" in skip


def test_non_429_error_fails_fast(monkeypatch):
    calls = []

    def fake_get(*a, **k):
        calls.append(1)
        return _Resp(503)

    monkeypatch.setitem(__import__("sys").modules, "requests",
                        type("m", (), {"get": staticmethod(fake_get)}))
    res, skip = lc.courtlistener_search("q", filed_after="2023-01-01",
                                        backoff=0.01, sleep=lambda s: None)
    assert res == [] and "503" in skip and len(calls) == 1


def test_search_terms_drops_single_char_debris():
    # "Nebius Group N.V." -> "Nebius Group N V"; a bare "N" term made the
    # CourtListener query return zero dockets, i.e. a false clean (2026-08-24).
    assert lc.search_terms("Nebius Group N.V.") == ["Nebius"]
    assert lc.search_terms("T1 Energy Inc.") == ["T1", "Energy"]  # T1 survives


def test_search_variants_includes_former_names():
    # Dockets are captioned under the entity name AT FILING. KEEL read as clean
    # on its current name while "Bitfarms" returns a pending securities case.
    assert lc.search_variants("Keel Infrastructure Corp. (fka Bitfarms)") == \
        [["Keel", "Infrastructure"], ["Bitfarms"]]
    assert lc.search_variants("Foo Corp. formerly known as Bar Industries") == \
        [["Foo"], ["Bar", "Industries"]]
    assert lc.search_variants("T1 Energy Inc.") == [["T1", "Energy"]]
    assert lc.search_variants("") == []


def test_every_hit_lands_in_some_bucket():
    """A name whose only dockets are contract/employment must not print an
    empty report — that reads identically to 'clean' (KN, AEVA, 2026-08-24)."""
    contract = {"caseName": "Acme v. Knowles Corp", "docketNumber": "1:24-cv-1",
                "dateFiled": "2024-01-01", "dateTerminated": None,
                "suitNature": "190 Contract: Other", "cause": "28:1332 Diversity"}
    assert not lc.is_securities(contract) and not lc.is_ip(contract)
