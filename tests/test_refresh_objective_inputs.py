import json
import datetime as dt
import shutil
from pathlib import Path
from openpyxl import Workbook
import scripts.refresh_objective_inputs as roi


def _make_scoring(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Watchlist"
    headers = ["Ticker", "Company", "Layer", "Last Updated", "Fwd P/E"]
    ws.append(headers)
    for t in ["NVDA", "TSM", "MU", "GEV"]:
        ws.append([t, f"{t} Inc", "06 Silicon", None, None])
    p = tmp_path / "scoring.xlsx"
    wb.save(p)
    return p


def _make_portfolio(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Targets"
    ws.append(["Target Portfolio", None, None, None, None, None])
    ws.append(["Ticker", "Layer", "TOTAL", "Tier", "Rank", "Status"])
    ws.append(["NVDA", "06", 84.0, "✓✓", 1, "HOLD"])
    ws.append(["MU", "06", 79.9, "✓✓", 2, "HOLD"])
    ws.append(["XYZ", "06", 70.0, "✓✓", 3, None])  # not HOLD
    p = tmp_path / "portfolio.xlsx"
    wb.save(p)
    return p


def test_resolve_portfolio_returns_hold_tickers(tmp_path):
    sp = _make_scoring(tmp_path)
    pp = _make_portfolio(tmp_path)
    assert roi.resolve_targets("portfolio", scoring_path=sp, portfolio_path=pp) == ["NVDA", "MU"]


def test_resolve_all_returns_every_watchlist_ticker(tmp_path):
    sp = _make_scoring(tmp_path)
    pp = _make_portfolio(tmp_path)
    assert roi.resolve_targets("all", scoring_path=sp, portfolio_path=pp) == ["NVDA", "TSM", "MU", "GEV"]


def test_resolve_subset_drops_unknowns(tmp_path):
    sp = _make_scoring(tmp_path)
    pp = _make_portfolio(tmp_path)
    assert roi.resolve_targets(["nvda", "ZZZZ"], scoring_path=sp, portfolio_path=pp) == ["NVDA"]


L9 = "09 Compute-as-a-Service / Neocloud GPU clouds"
TODAY = dt.date(2026, 6, 24)


def _cap(tmp_path, payload):
    p = tmp_path / "capacity-mw.json"
    p.write_text(json.dumps(payload))
    return p


def test_mw_flag_missing_entry(tmp_path):
    cj = _cap(tmp_path, {})
    f = roi.mw_staleness_flag("CRWV", L9, TODAY, capacity_json=cj)
    assert f is not None and "CRWV" in f and "missing" in f.lower()


def test_mw_flag_stale_asof(tmp_path):
    cj = _cap(tmp_path, {"CRWV": {"secured_gross_mw": 300, "as_of": "2026-03-01"}})
    f = roi.mw_staleness_flag("CRWV", L9, TODAY, capacity_json=cj)
    assert f is not None and "stale" in f.lower()


def test_mw_flag_fresh_returns_none(tmp_path):
    cj = _cap(tmp_path, {"CRWV": {"secured_gross_mw": 300, "as_of": "2026-06-01"}})
    assert roi.mw_staleness_flag("CRWV", L9, TODAY, capacity_json=cj) is None


def test_mw_flag_non_l9_returns_none(tmp_path):
    cj = _cap(tmp_path, {})
    assert roi.mw_staleness_flag("NVDA", "06 Silicon", TODAY, capacity_json=cj) is None


# ---------------------------------------------------------------------------
# Task 3: apply_guards tests
# ---------------------------------------------------------------------------

def _blank_existing():
    return {k: None for k in roi.OBJ_COLS}


def test_guard_currency_blanks_adr_cols():
    info = {"financialCurrency": "TWD"}
    fresh = {"fwd_pe": 23.4, "ev_ebitda": 15.0, "fcf_yield": 3.2, "ps": 8.0,
             "roic": 20.0, "gross_mgn": 55.0, "fcf_mgn": 30.0, "nd_ebitda": 0.5,
             "rev_3y_cagr": 25.0, "rev_yoy": 30.0, "eps_yoy": 40.0}
    writes, flags = roi.apply_guards(info, fresh, _blank_existing())
    assert writes["ps"] is None and writes["ev_ebitda"] is None and writes["fcf_yield"] is None
    assert writes["fwd_pe"] == 23.4  # kept
    assert any("ADR" in f or "currency" in f.lower() for f in flags)


def test_guard_keeps_existing_on_fetched_none():
    info = {"financialCurrency": "USD"}
    fresh = {k: None for k in roi.OBJ_COLS}
    fresh["fwd_pe"] = 40.0
    existing = _blank_existing()
    existing["roic"] = 18.5  # human-curated
    writes, flags = roi.apply_guards(info, fresh, existing)
    assert "roic" not in writes  # untouched, not clobbered with None
    assert writes["fwd_pe"] == 40.0
    assert any("roic" in f.lower() for f in flags)


def test_guard_eps_yoy_preserves_blank():
    info = {"financialCurrency": "USD"}
    fresh = {k: 10.0 for k in roi.OBJ_COLS}
    fresh["eps_yoy"] = 50.0
    existing = {k: 9.0 for k in roi.OBJ_COLS}
    existing["eps_yoy"] = None  # deliberately blank (GEV-style)
    writes, flags = roi.apply_guards(info, fresh, existing)
    assert "eps_yoy" not in writes
    assert any("eps yoy" in f.lower() and "blank" in f.lower() for f in flags)


def test_guard_eps_yoy_withholds_extreme():
    info = {"financialCurrency": "USD"}
    fresh = {k: 10.0 for k in roi.OBJ_COLS}
    fresh["eps_yoy"] = 412.0
    existing = {k: 9.0 for k in roi.OBJ_COLS}
    writes, flags = roi.apply_guards(info, fresh, existing)
    assert "eps_yoy" not in writes
    assert any("412" in f or "extreme" in f.lower() for f in flags)


def test_guard_eps_yoy_normal_writes():
    info = {"financialCurrency": "USD"}
    fresh = {k: 10.0 for k in roi.OBJ_COLS}
    fresh["eps_yoy"] = 80.0
    existing = {k: 9.0 for k in roi.OBJ_COLS}
    writes, flags = roi.apply_guards(info, fresh, existing)
    assert writes["eps_yoy"] == 80.0
