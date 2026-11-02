"""tests/test_input_currency.py — quarter comparison, offline, stubbed lookups."""
import datetime as dt

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
    assert ic.classify(D(2026, 6, 30), D(2026, 9, 12)) == "current"


def test_a_print_on_a_later_quarter_is_behind():
    # CIEN 2026-09-08: Yahoo still at April after the August quarter was reported
    assert ic.classify(D(2026, 4, 30), D(2026, 9, 3)) == "behind"
    assert ic.classify(D(2026, 6, 30), D(2026, 6, 30) + dt.timedelta(days=85)) == "behind"
    assert ic.classify(D(2026, 6, 30), D(2026, 6, 30) + dt.timedelta(days=84)) == "current"


def test_failed_lookups_are_never_current():
    assert ic.classify(ic.FAILED, D(2026, 10, 21)) == "failed"
    assert ic.classify(D(2026, 9, 30), ic.FAILED) == "failed"
    assert ic.classify(ic.FAILED, ic.NOT_CHECKABLE) == "failed"


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
