"""Tests for scripts/fcf_source.py — one FCF calculation for FCF yield, FCF
margin and EV/FCF. Offline, stdlib only. Figures in $M from Yahoo statements
seen 2026-11-20."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import fcf_source as fs  # noqa: E402

D = dt.date
NAN = float("nan")
Q4 = [D(2026, 9, 30), D(2026, 6, 30), D(2026, 3, 31), D(2025, 12, 31)]


def test_four_consecutive_quarters_sum():
    q = {fs.OCF: dict(zip(Q4, [100, 90, 80, 70])),
         "Capital Expenditure": dict(zip(Q4, [-10, -10, -10, -10]))}
    v, note = fs.fcf_from_statements(q, {})
    assert v == 300 and note.startswith("quarterly TTM")


def test_a_gap_in_quarters_does_not_mix_years():
    # DLR: Q2 OCF blank; the old code summed four non-consecutive quarters
    q = {fs.OCF: {D(2026, 9, 30): 382, D(2026, 6, 30): NAN, D(2026, 3, 31): 532,
                  D(2025, 12, 31): 719, D(2025, 9, 30): 653},
         "Capital Expenditure": dict(zip(Q4, [-1, -1, -1, -1]))}
    a = {fs.OCF: {D(2025, 12, 31): 2412},
         "Purchase Of Investment Properties": {D(2025, 12, 31): -3181}}
    v, note = fs.fcf_from_statements(q, a)
    assert v == 2412 - 3181 and note.startswith("ANNUAL fiscal year 2025-12-31")
    assert "Purchase Of Investment Properties" in note


def test_missing_quarterly_capex_falls_to_annual():
    # APP: quarterly statement has OCF but no capex row
    q = {fs.OCF: dict(zip(Q4, [1429, 869, 1291, 1314]))}
    a = {fs.OCF: {D(2025, 12, 31): 3971}, "Capital Expenditure": {D(2025, 12, 31): -28}}
    v, note = fs.fcf_from_statements(q, a)
    assert v == 3943 and "ANNUAL" in note


def test_no_quarterly_statement_uses_latest_annual():
    # Japanese filers (6861.T) publish no quarterly cash flow on Yahoo
    a = {fs.OCF: {D(2026, 3, 31): 430680, D(2025, 3, 31): 409522},
         "Capital Expenditure": {D(2026, 3, 31): -28371, D(2025, 3, 31): -14342}}
    v, note = fs.fcf_from_statements({}, a)
    assert v == 430680 - 28371 and "2026-03-31" in note


def test_purchase_of_ppe_used_when_capital_expenditure_row_absent():
    q = {fs.OCF: dict(zip(Q4, [10, 10, 10, 10])),
         "Purchase Of PPE": dict(zip(Q4, [-2, -2, -2, -2]))}
    v, note = fs.fcf_from_statements(q, {})
    assert v == 32 and "Purchase Of PPE" in note


def test_nothing_usable_returns_none_with_reason():
    v, note = fs.fcf_from_statements({fs.OCF: {D(2025, 3, 31): -35}}, {})
    assert v is None and "no statement FCF" in note


def test_annual_year_without_capex_is_skipped_for_an_older_complete_year():
    a = {fs.OCF: {D(2025, 12, 31): 500, D(2024, 12, 31): 400},
         "Capital Expenditure": {D(2024, 12, 31): -100}}
    v, note = fs.fcf_from_statements({}, a)
    assert v == 300 and "2024-12-31" in note
