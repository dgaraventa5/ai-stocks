"""tests/test_input_currency.py — quarter comparison, offline, stubbed lookups."""
import datetime as dt
import sys
import types

import pytest

import common
import input_currency as ic

D = dt.date
TODAY = D(2026, 11, 2)


def _recent(*filings):
    """filings.recent block: (form, date, items)."""
    return {"form": [f[0] for f in filings], "filingDate": [f[1] for f in filings],
            "items": [f[2] for f in filings], "accessionNumber": ["x"] * len(filings),
            "primaryDocument": ["x"] * len(filings)}


def test_newest_earnings_filing_ignores_other_8ks():
    recent = _recent(("8-K", "2026-10-30", "5.02"), ("8-K", "2026-10-21", "2.02,9.01"),
                     ("8-K", "2026-07-22", "2.02"))
    assert ic.newest_earnings_filing(recent, TODAY) == D(2026, 10, 21)


def test_a_filer_with_no_earnings_8k_is_not_checkable():
    assert ic.newest_earnings_filing(_recent(("6-K", "2026-10-14", "")), TODAY) == ic.NOT_CHECKABLE


def test_a_print_on_the_latest_quarter_is_current():
    assert ic.classify(D(2026, 9, 30), D(2026, 10, 21)) == "current"


def test_a_slow_fourth_quarter_print_is_current():
    # TE's Q4 print came 90 days after year-end
    assert ic.classify(D(2025, 12, 31), D(2026, 3, 31)) == "current"


def test_a_print_on_a_later_quarter_is_behind():
    # CIEN 2026-09-08: Yahoo still at April after the August quarter was reported
    assert ic.classify(D(2026, 4, 30), D(2026, 9, 3)) == "behind"
    assert ic.classify(D(2026, 6, 30), D(2026, 6, 30) + dt.timedelta(days=100)) == "behind"
    assert ic.classify(D(2026, 6, 30), D(2026, 6, 30) + dt.timedelta(days=99)) == "current"


def test_failed_lookups_are_never_current():
    assert ic.classify(ic.FAILED, D(2026, 10, 21)) == "failed"
    assert ic.classify(D(2026, 9, 30), ic.FAILED) == "failed"
    assert ic.classify(ic.FAILED, ic.NOT_CHECKABLE) == "not_checkable"


def test_report_names_what_is_behind_and_exits_clean(capsys):
    quarters = {"AAA": D(2026, 9, 30), "BBB": D(2026, 4, 30), "CCC": D(2026, 9, 30)}
    filed = {"AAA": D(2026, 10, 21), "BBB": D(2026, 9, 3), "CCC": ic.NOT_CHECKABLE}
    code = ic.report(list(quarters), TODAY, quarters.get, lambda t, _: filed[t])
    out = capsys.readouterr().out
    assert code == 0
    assert "checked 3: 1 current, 1 behind, 1 not checkable, 0 failed" in out
    assert "BEHIND: BBB Yahoo statements end 2026-04-30, earnings 8-K filed 2026-09-03" in out


def test_too_many_failures_is_blocked_not_all_clear(capsys):
    tickers = ["A", "B", "C", "D", "E"]
    code = ic.report(tickers, TODAY, lambda t: ic.FAILED if t in "AB" else D(2026, 9, 30),
                     lambda t, _: D(2026, 10, 21))
    captured = capsys.readouterr()
    assert code == 1
    assert "BLOCKED" in captured.err and "COULD NOT CHECK: A" in captured.out


def test_quiet_result_stays_silent_about_problems(capsys):
    code = ic.report(["A"], TODAY, lambda t: D(2026, 9, 30), lambda t, _: D(2026, 10, 21))
    out = capsys.readouterr().out
    assert code == 0 and "BEHIND" not in out and "COULD NOT CHECK" not in out


def test_failure_rate_counts_only_names_it_tried(capsys):
    tickers = [f"T{i}" for i in range(10)]
    filed = {t: ic.NOT_CHECKABLE for t in tickers[:6]}
    quarter = lambda t: ic.FAILED if t == "T6" else D(2026, 9, 30)    # 1 of 4 tried
    assert ic.report(tickers, TODAY, quarter,
                     lambda t, _: filed.get(t, D(2026, 10, 21))) == 1
    assert "NOT CHECKABLE (no earnings 8-K): T0, T1, T2, T3, T4, T5" in capsys.readouterr().out


def test_nothing_checkable_is_blocked_not_all_clear(capsys):
    assert ic.report(["A", "B"], TODAY, lambda t: pytest.fail("no Yahoo call needed"),
                     lambda t, _: ic.NOT_CHECKABLE) == 1


@pytest.mark.parametrize("recent", [{}, {"form": ["8-K"], "filingDate": ["2026-10-21"]}])
def test_an_unusable_filings_block_is_a_failure(recent):
    with pytest.raises(ValueError):
        ic.newest_earnings_filing(recent, TODAY)


def _yahoo(monkeypatch, frame):
    fake = types.SimpleNamespace(Ticker=lambda t: types.SimpleNamespace(quarterly_income_stmt=frame))
    monkeypatch.setitem(sys.modules, "yfinance", fake)
    monkeypatch.setattr(ic.time, "sleep", lambda s: None)


def test_a_quarter_with_only_eps_does_not_count(monkeypatch):
    pd = pytest.importorskip("pandas")
    columns = [pd.Timestamp("2026-09-30"), pd.Timestamp("2026-06-30")]
    frame = pd.DataFrame({columns[0]: [None, 0.4], columns[1]: [100.0, 0.3]},
                         index=["Total Revenue", "Diluted EPS"])
    _yahoo(monkeypatch, frame)
    assert ic._statement_quarter("INTC") == D(2026, 6, 30)


def test_no_revenue_row_or_empty_frame_is_a_failure(monkeypatch):
    pd = pytest.importorskip("pandas")
    _yahoo(monkeypatch, pd.DataFrame())
    assert ic._statement_quarter("AAA") == ic.FAILED
    _yahoo(monkeypatch, None)
    assert ic._statement_quarter("AAA") == ic.FAILED


def _sec(monkeypatch, cik, payload):
    response = types.SimpleNamespace(json=lambda: payload)
    monkeypatch.setattr(common, "cik_for", lambda t: cik)
    monkeypatch.setattr(common, "sec_get", lambda *a, **k: response)


def test_filed_date_reads_the_newest_print(monkeypatch):
    _sec(monkeypatch, "1", {"filings": {"recent": _recent(("8-K", "2026-10-21", "2.02"))}})
    assert ic._filed_date("AAA", TODAY) == D(2026, 10, 21)


def test_filed_date_failures_are_failures_not_skips(monkeypatch):
    _sec(monkeypatch, "1", {"name": "no filings key"})
    assert ic._filed_date("AAA", TODAY) == ic.FAILED

    def down(*a, **k):
        raise OSError("network")
    monkeypatch.setattr(common, "sec_get", down)
    assert ic._filed_date("AAA", TODAY) == ic.FAILED


def test_foreign_lines_and_unmapped_names_are_not_checkable(monkeypatch):
    assert ic._filed_date("9880.HK", TODAY) == ic.NOT_CHECKABLE
    _sec(monkeypatch, None, {})
    assert ic._filed_date("AAA", TODAY) == ic.NOT_CHECKABLE


def test_the_lookback_window_limits_old_prints():
    old = TODAY - dt.timedelta(days=ic.LOOKBACK_DAYS + 1)
    recent = _recent(("8-K", old.isoformat(), "2.02"))
    assert ic.newest_earnings_filing(recent, TODAY) == ic.NOT_CHECKABLE
