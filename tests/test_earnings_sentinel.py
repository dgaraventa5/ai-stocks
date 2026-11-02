"""tests/test_earnings_sentinel.py — pure logic, no network, fictional data."""
import datetime as dt

from earnings_sentinel import (
    ET, build_scope, classify_session, reaction_day, due_events,
)


def _ts(y, m, d, hh, mm):
    return dt.datetime(y, m, d, hh, mm, tzinfo=ET)


# ---- build_scope -----------------------------------------------------------

RANKED = [("AAA", 1), ("BBB.T", 2), ("CCC", 3), ("DDD", 4)]


def test_scope_is_holdings_union_top_tradable_ranks():
    scope = build_scope(["ZZZ"], RANKED, top_n=2)
    # BBB.T is foreign → excluded from the rank leg; next tradable fills slot
    assert scope == ["AAA", "CCC", "ZZZ"]


def test_scope_dedupes_holdings_already_ranked():
    scope = build_scope(["AAA"], RANKED, top_n=2)
    assert scope == ["AAA", "CCC"]


def test_scope_top_n_counts_tradable_only():
    ranked = [("AAA", 1), ("B.T", 2), ("C.DE", 3), ("DDD", 4), ("EEE", 5)]
    assert build_scope([], ranked, top_n=2) == ["AAA", "DDD"]


# ---- session / reaction day ------------------------------------------------

def test_before_open_report_is_bmo():
    assert classify_session(_ts(2026, 8, 12, 7, 0)) == "BMO"


def test_after_close_report_is_amc():
    assert classify_session(_ts(2026, 8, 11, 16, 30)) == "AMC"


def test_midnight_timestamp_is_unknown_treated_amc():
    # date-only placeholder from the calendar source → conservative
    assert classify_session(_ts(2026, 8, 11, 0, 0)) == "AMC"


def test_reaction_day_bmo_same_day():
    assert reaction_day(_ts(2026, 8, 12, 7, 0)) == dt.date(2026, 8, 12)


def test_reaction_day_amc_next_weekday():
    assert reaction_day(_ts(2026, 8, 11, 16, 30)) == dt.date(2026, 8, 12)


def test_reaction_day_amc_friday_rolls_to_monday():
    assert reaction_day(_ts(2026, 8, 14, 16, 30)) == dt.date(2026, 8, 17)


# ---- due_events ------------------------------------------------------------

NOW_TUE_EVE = _ts(2026, 8, 11, 18, 30)   # Tue 18:30 ET
NOW_WED_EVE = _ts(2026, 8, 12, 18, 30)


def _state(**tickers):
    return {"tickers": tickers}


def test_amc_print_t0_briefing_only():
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 11)},
                     _state(), NOW_TUE_EVE)
    assert out["briefing_due"] == [
        {"ticker": "AAA", "report_date": "2026-08-11", "session": "AMC"}]
    assert out["rescore_due"] == []          # reaction close doesn't exist yet


def test_amc_print_next_evening_rescore_due():
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    st = _state(AAA={"briefed": "2026-08-11"})
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 12)}, st, NOW_WED_EVE)
    assert out["briefing_due"] == []
    assert out["rescore_due"] == [
        {"ticker": "AAA", "report_date": "2026-08-11", "session": "AMC"}]


def test_bmo_print_same_evening_both_due():
    cal = {"AAA": [_ts(2026, 8, 12, 7, 0)]}
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 12)},
                     _state(), NOW_WED_EVE)
    assert len(out["briefing_due"]) == 1 and len(out["rescore_due"]) == 1


def test_fully_processed_report_emits_nothing():
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    st = _state(AAA={"briefed": "2026-08-11", "rescored": "2026-08-11"})
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 12)}, st, NOW_WED_EVE)
    assert out["briefing_due"] == [] and out["rescore_due"] == []


def test_old_report_ignored_at_first_deployment():
    cal = {"AAA": [_ts(2026, 7, 20, 16, 30)]}    # >5 days ago
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 12)},
                     _state(), NOW_WED_EVE)
    assert out["briefing_due"] == [] and out["rescore_due"] == []


def test_future_report_emits_nothing():
    cal = {"AAA": [_ts(2026, 8, 20, 16, 30)]}
    out = due_events(["AAA"], cal, {}, _state(), NOW_WED_EVE)
    assert out["briefing_due"] == [] and out["rescore_due"] == []
    assert "AAA" not in out["flagged"]


def test_new_quarter_fires_even_when_prior_quarter_processed():
    # state carries last quarter's report; a fresh print supersedes it
    cal = {"AAA": [_ts(2026, 5, 12, 16, 30), _ts(2026, 8, 11, 16, 30)]}
    st = _state(AAA={"briefed": "2026-05-12", "rescored": "2026-05-12"})
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 11)}, st, NOW_TUE_EVE)
    assert out["briefing_due"] == [
        {"ticker": "AAA", "report_date": "2026-08-11", "session": "AMC"}]


def test_missing_calendar_is_flagged_not_guessed():
    out = due_events(["AAA"], {"AAA": []}, {}, _state(), NOW_WED_EVE)
    assert "AAA" in out["flagged"]


def test_holiday_no_new_close_defers_rescore():
    # reaction day passed on the calendar but latest close is still older
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    st = _state(AAA={"briefed": "2026-08-11"})
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 11)}, st, NOW_WED_EVE)
    assert out["rescore_due"] == []
    assert "AAA" not in out["flagged"]       # quiet defer, not an error


def test_latest_close_fetch_error_is_flagged_not_deferred_forever():
    # I2: a persistent price-fetch failure must not look like a quiet holiday
    # defer forever — it gets flagged. Briefing still fires (unaffected).
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    out = due_events(["AAA"], cal, {"AAA": "error"}, _state(), NOW_WED_EVE)
    assert out["flagged"]["AAA"] == "latest-close lookup failed"
    assert out["rescore_due"] == []
    assert out["briefing_due"] == [
        {"ticker": "AAA", "report_date": "2026-08-11", "session": "AMC"}]


def test_calendar_fetch_error_is_flagged_without_iterating_string():
    # M5: an "error" sentinel must never reach the `past = [ts for ts in dates]`
    # comprehension (iterating a string char-by-char would crash on ts <= now).
    out = due_events(["AAA"], {"AAA": "error"}, {}, _state(), NOW_WED_EVE)
    assert out["flagged"]["AAA"] == "earnings-date lookup failed"
    assert out["briefing_due"] == [] and out["rescore_due"] == []


# ---- state / mark ----------------------------------------------------------
from earnings_sentinel import load_state, mark


def test_load_state_missing_file(tmp_path):
    assert load_state(tmp_path / "state.json") == {"tickers": {}}


def test_mark_roundtrip(tmp_path):
    p = tmp_path / "state.json"
    mark(p, "briefed", "AAA", "2026-08-11")
    mark(p, "rescored", "AAA", "2026-08-11")
    mark(p, "briefed", "BBB", "2026-08-12")
    st = load_state(p)
    assert st["tickers"]["AAA"] == {"briefed": "2026-08-11",
                                    "rescored": "2026-08-11"}
    assert st["tickers"]["BBB"] == {"briefed": "2026-08-12"}


def test_mark_rejects_bad_phase(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        mark(tmp_path / "s.json", "executed", "AAA", "2026-08-11")


# ---- I/O layer -------------------------------------------------------------
import json as _json

from earnings_sentinel import latest_ranked_rows, main


def test_latest_ranked_rows_uses_newest_date_only(tmp_path):
    p = tmp_path / "score-history.csv"
    p.write_text(
        "date,ticker,total_score,rank,tier\n"
        "2026-08-07,OLD,80.0,1,X\n"
        "2026-08-11,AAA,84.0,1,X\n"
        "2026-08-11,BBB.T,82.0,2,X\n")
    assert latest_ranked_rows(p) == [("AAA", 1), ("BBB.T", 2)]


def test_main_detect_prints_json(tmp_path, monkeypatch, capsys):
    import earnings_sentinel as es
    import datetime as dt
    monkeypatch.setattr(es, "STATE_PATH", tmp_path / "state.json")
    hist = tmp_path / "score-history.csv"
    hist.write_text("date,ticker,total_score,rank,tier\n"
                    "2026-08-11,AAA,84.0,1,X\n")
    monkeypatch.setattr(es, "SCORE_HISTORY", hist)
    monkeypatch.setattr(es, "_holdings", lambda: ["AAA"])
    monkeypatch.setattr(es, "_fetch_calendar",
                        lambda ts: {"AAA": [dt.datetime(2026, 8, 11, 16, 30,
                                                        tzinfo=es.ET)]})
    monkeypatch.setattr(es, "_fetch_latest_close",
                        lambda ts: {"AAA": dt.date(2026, 8, 12)})
    monkeypatch.setattr(es, "_now",
                        lambda: dt.datetime(2026, 8, 12, 18, 30, tzinfo=es.ET))
    assert main([]) == 0
    out = _json.loads(capsys.readouterr().out)
    assert out["rescore_due"][0]["ticker"] == "AAA"


def test_main_mark_updates_state(tmp_path, monkeypatch):
    import earnings_sentinel as es
    monkeypatch.setattr(es, "STATE_PATH", tmp_path / "state.json")
    assert main(["--mark", "briefed", "AAA", "2026-08-11"]) == 0
    from earnings_sentinel import load_state
    assert load_state(tmp_path / "state.json")["tickers"]["AAA"]["briefed"] == "2026-08-11"


# ---- _fetch_latest_close ---------------------------------------------------
import sys as _sys
import types as _types


class _FakeHistory:
    def __init__(self, days):
        self.index = [dt.datetime(d.year, d.month, d.day) for d in days]

    def __len__(self):
        return len(self.index)


def _stub_yfinance(monkeypatch, days):
    import earnings_sentinel as es
    fake = _types.ModuleType("yfinance")
    fake.Ticker = lambda t: _types.SimpleNamespace(
        history=lambda period: _FakeHistory(days))
    monkeypatch.setitem(_sys.modules, "yfinance", fake)
    monkeypatch.setattr(es.time, "sleep", lambda s: None)


def test_empty_price_history_is_a_failed_lookup(monkeypatch):
    # yfinance returns an empty frame on a failed lookup rather than raising,
    # so empty must reach due_events as a failure, not as "no close yet".
    import earnings_sentinel as es
    _stub_yfinance(monkeypatch, [])
    closes = es._fetch_latest_close(["AAA"])
    assert closes == {"AAA": "error"}
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    out = due_events(["AAA"], cal, closes, _state(), NOW_WED_EVE)
    assert out["flagged"]["AAA"] == "latest-close lookup failed"
    assert out["rescore_due"] == []


def test_price_history_returns_newest_close_date(monkeypatch):
    import earnings_sentinel as es
    _stub_yfinance(monkeypatch, [dt.date(2026, 8, 11), dt.date(2026, 8, 12)])
    assert es._fetch_latest_close(["AAA"]) == {"AAA": dt.date(2026, 8, 12)}


# ---- SEC cross-check ---------------------------------------------------------
import pytest

from earnings_sentinel import (
    NOT_CROSS_CHECKABLE, _fetch_earnings_filings, cross_check, filing_signal,
    lookups_blocked,
)


@pytest.fixture(autouse=True)
def _no_sec_calls(monkeypatch):
    """main() must never reach SEC from a test; a test opts in by overriding."""
    import earnings_sentinel as es
    monkeypatch.setattr(es, "_fetch_earnings_filings", lambda tickers, today: {})


def _recent(*rows):
    forms, dates, items = zip(*rows) if rows else ((), (), ())
    return {"form": list(forms), "filingDate": list(dates), "items": list(items),
            "accessionNumber": ["a"] * len(rows), "primaryDocument": ["d"] * len(rows)}


TODAY = dt.date(2026, 8, 12)


def test_filing_signal_finds_a_fresh_item_202():
    recent = _recent(("8-K", "2026-08-11", "2.02,9.01"), ("8-K", "2026-08-10", "5.07"))
    assert filing_signal(recent, TODAY) == ["2026-08-11"]


def test_filing_signal_ignores_an_old_item_202():
    assert filing_signal(_recent(("8-K", "2026-07-01", "2.02")), TODAY) == []


def test_filing_signal_marks_a_6k_filer_foreign():
    recent = _recent(("6-K", "2026-08-11", ""), ("20-F", "2026-03-01", ""))
    assert filing_signal(recent, TODAY) == NOT_CROSS_CHECKABLE


def test_filing_signal_keeps_a_domestic_filer_with_a_stray_6k():
    recent = _recent(("6-K", "2026-08-11", ""), ("8-K", "2026-08-11", "2.02"))
    assert filing_signal(recent, TODAY) == ["2026-08-11"]


def _base():
    return {"briefing_due": [], "rescore_due": [], "flagged": {}}


def test_8k_the_calendar_missed_is_flagged():
    # the STX / MSFT case: Yahoo's next date is weeks out, the 8-K is already filed
    out = cross_check(_base(), ["AAA"], {"AAA": [_ts(2026, 9, 20, 16, 30)]},
                      {"AAA": ["2026-08-11"]}, _state(), NOW_WED_EVE)
    assert "2026-08-11" in out["flagged"]["AAA"]
    assert "not on the earnings calendar" in out["flagged"]["AAA"]


def test_calendar_that_lists_the_report_is_not_flagged():
    out = cross_check(_base(), ["AAA"], {"AAA": [_ts(2026, 8, 11, 16, 30)]},
                      {"AAA": ["2026-08-11"]}, _state(), NOW_WED_EVE)
    assert out["flagged"] == {}


def test_8k_filed_a_day_after_the_calendar_date_is_not_flagged():
    out = cross_check(_base(), ["AAA"], {"AAA": [_ts(2026, 8, 10, 16, 30)]},
                      {"AAA": ["2026-08-11"]}, _state(), NOW_WED_EVE)
    assert out["flagged"] == {}


def test_report_already_rescored_is_not_flagged_again():
    st = _state(AAA={"rescored": "2026-08-11"})
    out = cross_check(_base(), ["AAA"], {"AAA": []}, {"AAA": ["2026-08-11"]}, st, NOW_WED_EVE)
    assert out["flagged"] == {}


def test_an_existing_flag_keeps_its_reason():
    base = _base()
    base["flagged"]["AAA"] = "earnings-date lookup failed"
    out = cross_check(base, ["AAA"], {"AAA": "error"}, {"AAA": ["2026-08-11"]},
                      _state(), NOW_WED_EVE)
    assert out["flagged"]["AAA"].startswith("earnings-date lookup failed; ")
    assert "2026-08-11" in out["flagged"]["AAA"]


def test_foreign_filers_are_reported_not_cross_checkable():
    out = cross_check(_base(), ["BBB", "AAA"], {}, {"AAA": NOT_CROSS_CHECKABLE,
                                                    "BBB": NOT_CROSS_CHECKABLE},
                      _state(), NOW_WED_EVE)
    assert out["not_cross_checkable"] == ["AAA", "BBB"] and out["flagged"] == {}


def test_failed_filing_lookup_is_flagged():
    out = cross_check(_base(), ["AAA"], {}, {"AAA": "error"}, _state(), NOW_WED_EVE)
    assert out["flagged"]["AAA"] == "SEC filing lookup failed"


def test_same_day_report_stamped_later_than_the_run_is_not_flagged():
    now = _ts(2026, 8, 12, 10, 0)
    out = cross_check(_base(), ["AAA"], {"AAA": [_ts(2026, 8, 12, 16, 30)]},
                      {"AAA": ["2026-08-12"]}, _state(), now)
    assert out["flagged"] == {}


def test_calendar_date_after_today_does_not_cover_a_filed_8k():
    # Yahoo a day late is exactly the missed report this check exists to catch
    now = _ts(2026, 8, 12, 18, 30)
    out = cross_check(_base(), ["AAA"], {"AAA": [_ts(2026, 8, 13, 16, 30)]},
                      {"AAA": ["2026-08-12"]}, _state(), now)
    assert "2026-08-12" in out["flagged"]["AAA"]


def test_malformed_rescored_date_does_not_crash_the_run():
    st = _state(AAA={"rescored": "8/11"})
    out = cross_check(_base(), ["AAA"], {"AAA": []}, {"AAA": ["2026-08-11"]}, st, NOW_WED_EVE)
    assert "2026-08-11" in out["flagged"]["AAA"]


def test_failed_filing_lookup_keeps_an_existing_flag():
    base = _base()
    base["flagged"]["AAA"] = "latest-close lookup failed"
    out = cross_check(base, ["AAA"], {}, {"AAA": "error"}, _state(), NOW_WED_EVE)
    assert out["flagged"]["AAA"] == ("latest-close lookup failed; "
                                     "SEC filing lookup failed")


GOOD = [_ts(2026, 8, 11, 16, 30)]


def test_over_a_fifth_of_yahoo_lookups_failing_blocks():
    cal = {f"T{i}": ("error" if i < 3 else GOOD) for i in range(10)}
    assert lookups_blocked(cal, {}, {}) is True


def test_a_fifth_or_fewer_failing_does_not_block():
    cal = {f"T{i}": ("error" if i < 2 else GOOD) for i in range(10)}
    assert lookups_blocked(cal, {}, {}) is False


def test_empty_calendar_answers_count_as_failed_lookups():
    cal = {f"T{i}": ([] if i < 3 else GOOD) for i in range(10)}
    assert lookups_blocked(cal, {}, {}) is True


def test_failed_closes_count_with_yahoo():
    cal = {f"T{i}": GOOD for i in range(8)}
    closes = {"T0": "error", "T1": "error", "T2": "error"}
    assert lookups_blocked(cal, closes, {}) is True


def test_sec_failures_block_on_their_own_count():
    cal = {f"T{i}": GOOD for i in range(10)}
    filings = {f"T{i}": ("error" if i < 3 else []) for i in range(10)}
    assert lookups_blocked(cal, {}, filings) is True


def test_foreign_filers_do_not_count_as_sec_lookups():
    filings = {"AAA": "error", "BBB": []} | {
        f"F{i}": NOT_CROSS_CHECKABLE for i in range(20)}
    assert lookups_blocked({"AAA": GOOD}, {}, filings) is True


def test_all_foreign_scope_is_not_blocked_by_sec():
    assert lookups_blocked({"AAA": GOOD}, {}, {"AAA": NOT_CROSS_CHECKABLE}) is False


def test_an_empty_scope_blocks():
    assert lookups_blocked({}, {}, {}) is True


def _detect(tmp_path, monkeypatch, calendar, closes, filings):
    import earnings_sentinel as es
    monkeypatch.setattr(es, "STATE_PATH", tmp_path / "state.json")
    hist = tmp_path / "score-history.csv"
    hist.write_text("date,ticker,total_score,rank,tier\n2026-08-11,AAA,84.0,1,X\n")
    monkeypatch.setattr(es, "SCORE_HISTORY", hist)
    monkeypatch.setattr(es, "_holdings", lambda: ["AAA"])
    monkeypatch.setattr(es, "_fetch_calendar", lambda ts: calendar)
    monkeypatch.setattr(es, "_fetch_latest_close", lambda ts: closes)
    monkeypatch.setattr(es, "_fetch_earnings_filings", lambda ts, today: filings)
    monkeypatch.setattr(es, "_now", lambda: NOW_WED_EVE)
    return main([])


def test_main_flags_an_8k_the_calendar_lacks(tmp_path, monkeypatch, capsys):
    rc = _detect(tmp_path, monkeypatch, {"AAA": [_ts(2026, 9, 20, 16, 30)]}, {},
                 {"AAA": ["2026-08-11"]})
    out = _json.loads(capsys.readouterr().out)
    assert rc == 0 and out["blocked"] is False
    assert "2026-08-11" in out["flagged"]["AAA"]


def test_main_exits_nonzero_when_blocked(tmp_path, monkeypatch, capsys):
    rc = _detect(tmp_path, monkeypatch, {"AAA": "error"}, {}, {"AAA": []})
    captured = capsys.readouterr()
    assert rc == 1 and _json.loads(captured.out)["blocked"] is True
    assert "do not report" in captured.err


def _stub_sec(monkeypatch, cik, get):
    import common
    monkeypatch.setattr(common, "cik_for", lambda t: cik)
    monkeypatch.setattr(common, "sec_get", get)


def _unused_sec(*a, **k):
    raise AssertionError("no SEC call expected")


def test_fetch_marks_a_dotted_ticker_without_calling_sec(monkeypatch):
    _stub_sec(monkeypatch, "0000000001", _unused_sec)
    assert _fetch_earnings_filings(["6954.T"], TODAY) == {
        "6954.T": NOT_CROSS_CHECKABLE}


def test_fetch_marks_a_name_with_no_cik_not_cross_checkable(monkeypatch):
    _stub_sec(monkeypatch, None, _unused_sec)
    assert _fetch_earnings_filings(["AAA"], TODAY) == {"AAA": NOT_CROSS_CHECKABLE}


def test_fetch_reads_fresh_item_202_dates(monkeypatch):
    payload = {"filings": {"recent": _recent(("8-K", "2026-08-11", "2.02"))}}
    _stub_sec(monkeypatch, "0000000001",
              lambda url, **k: _types.SimpleNamespace(json=lambda: payload))
    assert _fetch_earnings_filings(["AAA"], TODAY) == {"AAA": ["2026-08-11"]}


def test_fetch_failure_becomes_a_blocked_run(monkeypatch):
    def down(url, **k):
        raise OSError("SEC down")

    _stub_sec(monkeypatch, "0000000001", down)
    filings = _fetch_earnings_filings(["AAA", "BBB"], TODAY)
    assert filings == {"AAA": "error", "BBB": "error"}
    assert lookups_blocked({"AAA": GOOD, "BBB": GOOD}, {}, filings) is True


def test_main_exits_nonzero_on_an_empty_calendar(tmp_path, monkeypatch, capsys):
    assert _detect(tmp_path, monkeypatch, {"AAA": []}, {}, {"AAA": []}) == 1
    assert _json.loads(capsys.readouterr().out)["blocked"] is True
