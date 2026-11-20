"""Tests for scripts/eps_growth.py — EPS YoY when Yahoo's earningsQuarterlyGrowth
is missing. Offline, stdlib only (no pandas/yfinance in this chain).

Figures are the Yahoo quarterly net income seen 2026-11-20.
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import eps_growth as eg  # noqa: E402

NAN = float("nan")
D = dt.date


def test_loss_base_is_blank_with_reason():
    # QCOM: Q3-25 had a -3.1B tax charge; Yahoo returns no growth figure
    qcom = {D(2026, 9, 30): 1251e6, D(2026, 6, 30): 2002e6, D(2026, 3, 31): 7370e6,
            D(2025, 12, 31): 3004e6, D(2025, 9, 30): -3117e6}
    v, code, note = eg.eps_yoy_fallback(qcom, D(2026, 9, 27))
    assert v is None and code == eg.LOSS_BASE and "-3,117M" in note


def test_both_quarters_profitable_is_computed_like_yahoo():
    # HUT: Yahoo prints +161.6% = 131M / 50M - 1
    hut = {D(2026, 9, 30): 131e6, D(2026, 6, 30): -150e6, D(2026, 3, 31): -220e6,
           D(2025, 12, 31): -280e6, D(2025, 9, 30): 50e6}
    v, code, _ = eg.eps_yoy_fallback(hut, D(2026, 9, 30))
    assert v == 162.0 and code == eg.COMPUTED


def test_statement_behind_latest_quarter_is_a_data_gap():
    # statement lag (rule 34): newest column is a quarter behind
    rows = {D(2026, 6, 30): 100e6, D(2025, 6, 30): 80e6}
    v, code, note = eg.eps_yoy_fallback(rows, D(2026, 9, 30))
    assert v is None and code == eg.NO_DATA and "behind" in note


def test_missing_year_ago_quarter_is_a_data_gap():
    rows = {D(2026, 9, 30): 100e6, D(2026, 6, 30): 80e6, D(2025, 9, 30): NAN}
    v, code, _ = eg.eps_yoy_fallback(rows, D(2026, 9, 30))
    assert v is None and code == eg.NO_DATA


def test_blank_current_quarter_is_a_data_gap():
    # NVDA-style: newest net income NaN while the base exists
    rows = {D(2026, 10, 31): NAN, D(2025, 10, 31): 31_910e6}
    v, code, _ = eg.eps_yoy_fallback(rows, D(2026, 10, 25))
    assert v is None and code == eg.NO_DATA


def test_unknown_latest_quarter_uses_newest_column():
    rows = {D(2026, 9, 30): 120e6, D(2025, 9, 30): 100e6}
    v, code, _ = eg.eps_yoy_fallback(rows, None)
    assert v == 20.0 and code == eg.COMPUTED


def test_empty_statement():
    v, code, _ = eg.eps_yoy_fallback({}, D(2026, 9, 30))
    assert v is None and code == eg.NO_DATA


def test_accepts_datetime_and_string_keys():
    rows = {dt.datetime(2026, 9, 30): 120e6, "2025-09-30": 100e6}
    v, _, _ = eg.eps_yoy_fallback(rows, D(2026, 9, 30))
    assert v == 20.0
