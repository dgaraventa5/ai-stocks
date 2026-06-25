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
