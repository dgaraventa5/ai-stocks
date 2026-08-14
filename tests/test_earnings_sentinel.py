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
