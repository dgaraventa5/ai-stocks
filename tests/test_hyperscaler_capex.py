"""tests/test_hyperscaler_capex.py — capex filler, offline, fictional numbers."""
import datetime as dt
from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

import hyperscaler_capex as hc

D = dt.date
LABELS = ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4", "2025-Q1", "2025-Q2",
          "2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2", "2026-Q3", "2026-Q4"]


def _book(path: Path) -> Path:
    """The tracker's layout: five company rows, TOTAL and YoY % rows."""
    wb = Workbook()
    ws = wb.active
    ws.title = hc.SHEET
    ws.append(["Ticker", *LABELS])
    for t in ("MSFT", "GOOGL", "META", "AMZN", "ORCL"):
        ws.append([t])
    ws.append(["TOTAL"])
    ws.append(["YoY %"])
    wb.create_sheet("Guidance & commentary").append(["Date", "Ticker"])
    wb.save(path)
    return path


def _fact(start, end, val_m, accn="0000000000-26-000001", form="10-Q",
          filed="2026-10-30"):
    return {"start": start, "end": end, "val": val_m * 1e6, "accn": accn,
            "form": form, "filed": filed}


def _year(y, q1, h1, m9, fy, filed=None):
    """One fiscal year's year-to-date ladder, the way cash flows are filed."""
    s = f"{y}-01-01"
    return [_fact(s, f"{y}-03-31", q1, filed=filed or f"{y}-04-30"),
            _fact(s, f"{y}-06-30", h1, filed=filed or f"{y}-07-30"),
            _fact(s, f"{y}-09-30", m9, filed=filed or f"{y}-10-30"),
            _fact(s, f"{y}-12-31", fy, form="10-K", filed=filed or f"{y + 1}-02-01")]


def _quarters(*pairs):
    return {label: {"value": v, "basis": "reported", "start": "2026-07-01",
                    "end": "2026-09-30", "accn": "a", "form": "10-Q",
                    "filed": "2026-10-30", "less_start": "", "less_end": "",
                    "less_accn": "", "less_filed": ""} for label, v in pairs}


# ---- quarters --------------------------------------------------------------

@pytest.mark.parametrize("end,label", [(D(2026, 8, 31), "2026-Q3"),
                                       (D(2026, 2, 28), "2026-Q1"),
                                       (D(2026, 9, 30), "2026-Q3"),
                                       (D(2025, 12, 31), "2025-Q4")])
def test_a_quarter_goes_under_the_calendar_quarter_it_ends_in(end, label):
    assert hc.quarter_label(end) == label


def test_next_label_rolls_the_year():
    assert hc.next_label("2026-Q4") == "2027-Q1"
    assert hc.next_label("2026-Q2") == "2026-Q3"


def test_year_to_date_figures_become_single_quarters():
    out = hc.quarterly_capex(_year(2025, 10, 25, 45, 70))
    assert {k: v["value"] for k, v in out.items()} == {
        "2025-Q1": 10.0, "2025-Q2": 15.0, "2025-Q3": 20.0, "2025-Q4": 25.0}


def test_quarters_before_2024_are_left_out():
    out = hc.quarterly_capex(_year(2023, 1, 2, 3, 4) + _year(2024, 1, 2, 3, 4))
    assert sorted(out) == ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"]


def test_a_reported_quarter_cites_the_newest_filing_of_that_figure():
    facts = _year(2025, 10, 25, 45, 70)
    facts.append(_fact("2025-01-01", "2025-03-31", 10, accn="later",
                       filed="2026-04-30"))
    q1 = hc.quarterly_capex(facts)["2025-Q1"]
    assert q1["basis"] == "reported" and q1["accn"] == "later"
    assert q1["less_accn"] == ""


def test_a_computed_quarter_cites_both_filings_and_periods():
    facts = [_fact("2025-01-01", "2025-09-30", 45, accn="nine-month"),
             _fact("2025-01-01", "2025-12-31", 70, accn="full-year", form="10-K")]
    q4 = hc.quarterly_capex(facts)["2025-Q4"]
    assert q4["value"] == 25.0 and q4["basis"] == "difference"
    assert (q4["accn"], q4["start"], q4["end"]) == ("full-year", "2025-01-01", "2025-12-31")
    assert (q4["less_accn"], q4["less_start"], q4["less_end"]) == (
        "nine-month", "2025-01-01", "2025-09-30")


def test_the_trace_matches_the_shared_definition():
    from xbrl_periods import quarterly_from_facts
    facts = _year(2024, 3, 7, 12, 20) + _year(2025, 10, 25, 45, 70)
    facts.append(_fact("2024-10-01", "2025-09-30", 99))       # a TTM fact
    expected = {e: round(v / 1e6, 1) for e, v in quarterly_from_facts(facts).items()}
    got = {q["end"]: q["value"] for q in hc.quarterly_capex(facts).values()}
    assert got == expected


def test_two_period_ends_in_one_calendar_quarter_keep_the_later():
    facts = [_fact("2025-04-01", "2025-06-28", 5, accn="early"),
             _fact("2025-04-03", "2025-06-30", 6, accn="late")]
    q = hc.quarterly_capex(facts)["2025-Q2"]
    assert (q["end"], q["value"]) == ("2025-06-30", 6.0)
    facts.reverse()
    assert hc.quarterly_capex(facts)["2025-Q2"]["end"] == "2025-06-30"


# ---- workbook --------------------------------------------------------------

def test_apply_writes_values_formulas_and_sources(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    changes, dirty = hc.apply(wb, {"MSFT": _quarters(("2026-Q3", 39.4))})
    ws = wb[hc.SHEET]
    assert dirty and changes == ["  MSFT 2026-Q3: 39.4 (new; 10-Q a)"]
    assert ws.cell(2, 12).value == 39.4
    assert ws.cell(7, 12).value == '=IF(COUNT(L2:L6)<5,"",SUM(L2:L6))'
    assert ws.cell(8, 12).value == '=IF(OR(L7="",H7=""),"",L7/H7-1)'
    assert ws.cell(8, 2).value is None          # no prior year for 2024
    src = list(wb[hc.SOURCES].iter_rows(values_only=True))
    assert src[0] == hc.SOURCE_HEADER
    assert src[1][:6] == ("MSFT", "2026-Q3", 39.4, "reported", "2026-07-01",
                          "2026-09-30")
    assert ws.cell(8, 5).value is None          # 2024-Q4 has no prior year
    assert ws.cell(8, 6).value == '=IF(OR(F7="",B7=""),"",F7/B7-1)'


def test_an_older_sources_layout_is_rebuilt(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    wb.create_sheet(hc.SOURCES).append(("Ticker", "Quarter", "Period end"))
    wb[hc.SOURCES].append(("ORCL", "2026-Q3", "2026-08-31"))
    _, dirty = hc.apply(wb, {"MSFT": _quarters(("2026-Q3", 39.4))})
    rows = list(wb[hc.SOURCES].iter_rows(values_only=True))
    assert dirty and rows[0] == hc.SOURCE_HEADER and [r[0] for r in rows[1:]] == ["MSFT"]


def test_a_restated_value_is_reported_as_changed(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    hc.apply(wb, {"MSFT": _quarters(("2026-Q3", 39.4))})
    changes, _ = hc.apply(wb, {"MSFT": _quarters(("2026-Q3", 40.0))})
    assert changes == ["  MSFT 2026-Q3: 40.0 (CHANGED from 39.4; 10-Q a)"]


def test_a_rerun_with_the_same_data_changes_nothing(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    data = {"MSFT": _quarters(("2026-Q3", 39.4))}
    hc.apply(wb, data)
    assert hc.apply(wb, data) == ([], False)


def test_a_new_quarter_adds_a_column_with_formulas(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    hc.apply(wb, {"GOOGL": _quarters(("2027-Q2", 60.0))})
    ws = wb[hc.SHEET]
    assert [ws.cell(1, c).value for c in (14, 15)] == ["2027-Q1", "2027-Q2"]
    assert ws.cell(3, 15).value == 60.0
    assert ws.cell(8, 15).value == '=IF(OR(O7="",K7=""),"",O7/K7-1)'


def test_an_unread_company_keeps_its_citations(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    hc.apply(wb, {"MSFT": _quarters(("2026-Q3", 39.4)),
                  "ORCL": _quarters(("2026-Q3", 28.5))})
    hc.apply(wb, {"MSFT": _quarters(("2026-Q3", 39.4))})       # ORCL failed
    tickers = [r[0] for r in wb[hc.SOURCES].iter_rows(min_row=2, values_only=True)]
    assert tickers == ["MSFT", "ORCL"]


# ---- report ----------------------------------------------------------------

def test_a_failed_company_exits_nonzero_and_is_named(tmp_path, capsys):
    path = _book(tmp_path / "c.xlsx")
    fetch = lambda t: hc.FAILED if t == "ORCL" else _quarters(("2026-Q3", 1.0))
    assert hc.report(fetch, path, write=True) == 1
    assert "COULD NOT READ: ORCL" in capsys.readouterr().err
    assert load_workbook(path)[hc.SHEET].cell(2, 12).value == 1.0


def _fetch_ok(t):
    return _quarters(("2026-Q2", 1.0), ("2026-Q3", 2.0))


def test_a_write_with_nothing_new_leaves_the_file_alone(tmp_path):
    path = _book(tmp_path / "c.xlsx")
    assert hc.report(_fetch_ok, path, write=True) == 0
    before = path.read_bytes()
    assert hc.report(_fetch_ok, path, write=True) == 0
    assert path.read_bytes() == before


def test_combined_totals_print_only_for_complete_quarters(tmp_path, capsys):
    path = _book(tmp_path / "c.xlsx")
    hc.report(_fetch_ok, path)
    out = capsys.readouterr().out
    assert "Combined 2026-Q3: 10.0 $M" in out and "Combined 2026-Q2: 5.0 $M" in out
    fetch = lambda t: _quarters(("2026-Q3", 2.0)) if t != "ORCL" else _quarters(("2026-Q2", 1.0), ("2026-Q3", 2.0), ("2026-Q4", 3.0))
    hc.report(fetch, path)
    assert "Combined 2026-Q4" not in capsys.readouterr().out


def test_a_company_two_quarters_behind_is_flagged(tmp_path, capsys):
    path = _book(tmp_path / "c.xlsx")
    fetch = lambda t: _quarters(("2026-Q1", 1.0)) if t == "AMZN" else _quarters(("2026-Q3", 2.0))
    assert hc.report(fetch, path) == 1
    assert "NO RECENT QUARTER: AMZN (latest 2026-Q1)" in capsys.readouterr().err
    one_behind = lambda t: _quarters(("2026-Q2", 1.0)) if t == "AMZN" else _quarters(("2026-Q3", 2.0))
    assert hc.report(one_behind, path) == 0


def _sec(monkeypatch, payload):
    import common
    import types
    monkeypatch.setattr(common, "cik_for", lambda t: "1")
    monkeypatch.setattr(common, "sec_get",
                        lambda *a, **k: types.SimpleNamespace(json=lambda: payload))
    monkeypatch.setattr(hc.time, "sleep", lambda s: None)


def test_fetch_reads_the_company_tag(monkeypatch):
    facts = _year(2025, 10, 25, 45, 70)
    _sec(monkeypatch, {"facts": {"us-gaap": {hc.TAGS["MSFT"]: {"units": {"USD": facts}}}}})
    assert hc.fetch("MSFT")["2025-Q4"]["value"] == 25.0


@pytest.mark.parametrize("payload", [
    {"facts": {"us-gaap": {}}},                                    # tag missing
    {"facts": {"us-gaap": {hc.TAGS["MSFT"]: {"units": {"USD": []}}}}},   # no quarters
    {"nothing": True}])
def test_fetch_that_finds_nothing_is_a_failure(monkeypatch, payload):
    _sec(monkeypatch, payload)
    assert hc.fetch("MSFT") == hc.FAILED


def test_a_dry_run_never_saves(tmp_path):
    path = _book(tmp_path / "c.xlsx")
    before = path.read_bytes()
    assert hc.report(lambda t: _quarters(("2026-Q3", 1.0)), path) == 0
    assert path.read_bytes() == before


def test_the_weekly_scan_and_capex_update_run_it():
    root = Path(hc.__file__).resolve().parent.parent
    scan = (root / ".claude" / "commands" / "weekly-scan.md").read_text()
    update = (root / ".claude" / "commands" / "capex-update.md").read_text()
    assert "python3 scripts/hyperscaler_capex.py --write" in scan
    assert "python3 scripts/hyperscaler_capex.py --write" in update


def test_a_reported_quarter_beats_a_computed_one():
    facts = [_fact("2025-01-01", "2025-06-30", 25),
             _fact("2025-01-01", "2025-09-30", 45),
             _fact("2025-07-01", "2025-09-30", 21, accn="standalone",
                   filed="2026-10-30")]
    q3 = hc.quarterly_capex(facts)["2025-Q3"]
    assert (q3["value"], q3["basis"], q3["accn"]) == (21.0, "reported", "standalone")


def test_no_combined_total_when_a_company_could_not_be_read(tmp_path, capsys):
    path = _book(tmp_path / "c.xlsx")
    fetch = lambda t: hc.FAILED if t == "ORCL" else _fetch_ok(t)
    hc.report(fetch, path)
    assert "Combined" not in capsys.readouterr().out


def test_a_write_with_nothing_new_does_not_save(tmp_path, monkeypatch):
    from openpyxl.workbook.workbook import Workbook as WB
    path = _book(tmp_path / "c.xlsx")
    hc.report(_fetch_ok, path, write=True)
    saves = []
    monkeypatch.setattr(WB, "save", lambda self, p: saves.append(p))
    hc.report(_fetch_ok, path, write=True)
    assert saves == []


# ---- second review: cross-check, totals, repair -----------------------------

@pytest.mark.parametrize("tamper", ["drop", "add", "value"])
def test_the_trace_must_agree_with_the_shared_definition(monkeypatch, tamper):
    import xbrl_periods
    real = xbrl_periods.quarterly_from_facts

    def fake(facts):
        out = dict(real(facts))
        if tamper == "drop":
            out.pop("2025-06-30")
        elif tamper == "add":
            out["2025-05-31"] = 1.0
        else:
            out["2025-06-30"] += 5e6
        return out
    monkeypatch.setattr(xbrl_periods, "quarterly_from_facts", fake)
    with pytest.raises(ValueError):
        hc.quarterly_capex(_year(2025, 10, 25, 45, 70))


def test_the_order_facts_arrive_in_does_not_change_the_citation():
    facts = _year(2025, 10, 25, 45, 70)
    facts.append(_fact("2025-01-01", "2025-03-31", 10, accn="later",
                       filed="2026-04-30"))
    facts.append(_fact("2025-07-01", "2025-09-30", 20, accn="standalone",
                       filed="2025-10-30"))
    for order in (facts, list(reversed(facts))):
        out = hc.quarterly_capex(order)
        assert out["2025-Q1"]["accn"] == "later"
        assert (out["2025-Q3"]["basis"], out["2025-Q3"]["accn"]) == ("reported", "standalone")
        assert out["2025-Q4"]["less_filed"] == "2025-10-30"


def test_combined_change_on_a_year_earlier(tmp_path, capsys):
    path = _book(tmp_path / "c.xlsx")
    hc.report(lambda t: _quarters(("2025-Q3", 2.0), ("2026-Q3", 3.0)), path)
    out = capsys.readouterr().out
    assert "Combined 2026-Q3: 15.0 $M, +50% on 2025-Q3" in out
    assert "Combined 2025-Q3: 10.0 $M\n" in out


def test_a_broken_formula_is_restored_and_saved(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    data = {"MSFT": _quarters(("2026-Q3", 39.4))}
    hc.apply(wb, data)
    wb[hc.SHEET].cell(7, 12).value = "=SUM(L2:L5)"
    changes, dirty = hc.apply(wb, data)
    assert changes == [] and dirty
    assert wb[hc.SHEET].cell(7, 12).value == '=IF(COUNT(L2:L6)<5,"",SUM(L2:L6))'


def test_a_hand_edited_value_is_put_back_and_saved(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    data = {"MSFT": _quarters(("2026-Q3", 39.4))}
    hc.apply(wb, data)
    wb[hc.SHEET].cell(2, 12).value = 1.0
    changes, dirty = hc.apply(wb, data)
    assert changes == ["  MSFT 2026-Q3: 39.4 (CHANGED from 1.0; 10-Q a)"] and dirty


def test_sources_name_the_tag_used(tmp_path):
    wb = load_workbook(_book(tmp_path / "c.xlsx"))
    hc.apply(wb, {"AMZN": _quarters(("2026-Q3", 77.3))})
    row = list(wb[hc.SOURCES].iter_rows(min_row=2, values_only=True))[0]
    assert row[0] == "AMZN" and row[-1] == "PaymentsToAcquireProductiveAssets"


def test_fetch_uses_each_company_s_own_tag(monkeypatch):
    facts = _year(2025, 10, 25, 45, 70)
    _sec(monkeypatch, {"facts": {"us-gaap": {
        "PaymentsToAcquireProductiveAssets": {"units": {"USD": facts}},
        "PaymentsToAcquirePropertyPlantAndEquipment": {"units": {"USD": []}}}}})
    assert hc.fetch("AMZN")["2025-Q4"]["value"] == 25.0
    assert hc.fetch("MSFT") == hc.FAILED


def test_a_reported_quarter_wins_whatever_order_it_was_filed_in():
    standalone = _fact("2025-07-01", "2025-09-30", 21, accn="standalone",
                       filed="2025-01-15")        # filed before the year-to-date ladder
    facts = [standalone, _fact("2025-01-01", "2025-06-30", 25, filed="2025-07-30"),
             _fact("2025-01-01", "2025-09-30", 45, filed="2025-10-30")]
    q3 = hc.quarterly_capex(facts)["2025-Q3"]
    assert (q3["value"], q3["accn"]) == (21.0, "standalone")


def test_zero_length_facts_are_ignored():
    facts = _year(2025, 10, 25, 45, 70)
    facts.append(_fact("2025-01-01", "2025-01-01", 5))
    assert hc.quarterly_capex(facts)["2025-Q1"]["value"] == 10.0


def test_values_keep_one_decimal_in_millions():
    facts = [_fact("2025-01-01", "2025-03-31", 10.4)]
    assert hc.quarterly_capex(facts)["2025-Q1"]["value"] == 10.4
