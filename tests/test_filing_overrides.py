"""Filing overrides: filing-sourced objective inputs that Yahoo gets wrong.

ANT (IPO 2026-11-19) is the first case: Yahoo had no Q1-Q2 2026 statements,
counted pre-IPO convertible notes as $135B of debt and scraped a 22% gross
margin, so every weekly refresh would overwrite the prospectus values. An
override holds while Yahoo's latest quarter is still the override's quarter,
then retires itself (flagged) when a newer quarter is reported.
"""
import datetime as dt
import json

from openpyxl import Workbook, load_workbook

import scripts.filing_overrides as fo
import scripts.refresh_objective_inputs as roi

SEP30 = int(dt.datetime(2026, 9, 30, tzinfo=dt.timezone.utc).timestamp())
DEC31 = int(dt.datetime(2026, 12, 31, tzinfo=dt.timezone.utc).timestamp())

ENTRY = {
    "period_end": "2026-09-30",
    "source": "424B4 acc. 0001628280-26-074944",
    "set": "2026-11-21",
    "fixed": {"roic": -2.27, "gross_mgn": 83.59, "fcf_mgn": 8.65, "nd_ebitda": 0},
    "ev": {"fcf_ttm": 3053e6, "cash": 244552e6, "debt": 0.0,
           "extra_shares": 1547676309},
}
YAHOO = {"roic": -23.72, "gross_mgn": 22.26, "fcf_mgn": -8.0, "nd_ebitda": 99.0,
         "fcf_yield": -0.24, "ev_ebitda": -126.2, "ps": 33.68}
INFO = {"mostRecentQuarter": SEP30, "marketCap": 1188428e6, "currentPrice": 88.91}


def test_applies_fixed_fields_while_yahoo_is_on_the_same_quarter():
    writes, flags = fo.apply(ENTRY, INFO, dict(YAHOO))
    assert writes["roic"] == -2.27
    assert writes["gross_mgn"] == 83.59
    assert writes["fcf_mgn"] == 8.65
    assert writes["nd_ebitda"] == 0
    assert writes["ps"] == 33.68                      # untouched key stays Yahoo's
    assert any("roic" in f and "-23.72" in f for f in flags)  # shows what it replaced


def test_price_dependent_ratios_use_the_current_market_cap():
    writes, _ = fo.apply(ENTRY, INFO, dict(YAHOO))
    assert writes["fcf_yield"] == round(3053e6 / 1188428e6 * 100, 2)   # 0.26
    ev = 1188428e6 + 1547676309 * 88.91 + 0.0 - 244552e6
    assert writes["ev_ebitda"] == round(ev / 3053e6, 1)                # ~354
    # a lower price moves both, rather than freezing them at the set date
    cheaper = dict(INFO, marketCap=1188428e6 / 2, currentPrice=88.91 / 2)
    w2, _ = fo.apply(ENTRY, cheaper, dict(YAHOO))
    assert w2["fcf_yield"] > writes["fcf_yield"]
    assert w2["ev_ebitda"] < writes["ev_ebitda"]


def test_retires_when_a_newer_quarter_is_reported():
    newer = dict(INFO, mostRecentQuarter=DEC31)
    writes, flags = fo.apply(ENTRY, newer, dict(YAHOO))
    assert writes == YAHOO                             # Yahoo's values flow through
    assert any("EXPIRED" in f for f in flags)          # and the retirement is loud


def test_unknown_quarter_keeps_the_override_and_says_so():
    writes, flags = fo.apply(ENTRY, dict(INFO, mostRecentQuarter=None), dict(YAHOO))
    assert writes["roic"] == -2.27
    assert any("could not confirm" in f for f in flags)


def test_missing_market_cap_leaves_price_ratios_to_yahoo_and_flags():
    writes, flags = fo.apply(ENTRY, dict(INFO, marketCap=None), dict(YAHOO))
    assert writes["fcf_yield"] == YAHOO["fcf_yield"]
    assert writes["roic"] == -2.27
    assert any("market cap" in f for f in flags)


def test_ev_fcf_helper_matches_the_sheet_value():
    assert fo.ev_fcf(ENTRY, INFO) == fo.apply(ENTRY, INFO, dict(YAHOO))[0]["ev_ebitda"]
    assert fo.ev_fcf(ENTRY, dict(INFO, mostRecentQuarter=DEC31)) is None


def test_load_skips_meta_and_tolerates_a_missing_file(tmp_path):
    assert fo.load(tmp_path / "nope.json") == {}
    p = tmp_path / "o.json"
    p.write_text(json.dumps({"_meta": {"x": 1}, "ANT": ENTRY}))
    assert list(fo.load(p)) == ["ANT"]


def test_refresh_uses_the_override_end_to_end(tmp_path):
    wb = Workbook(); ws = wb.active; ws.title = "Watchlist"
    ws.append(["Ticker", "Company", "Layer", "Last Updated"] + [None] * 34)
    ws.append(["ANT", "Anthropic, PBC", "10 Models", "2026-11-21"] + [None] * 34)
    ws.append(["NVDA", "Nvidia", "06 Silicon", "2026-11-21"] + [None] * 34)
    sp = tmp_path / "scoring.xlsx"; wb.save(sp)
    op = tmp_path / "filing-overrides.json"
    op.write_text(json.dumps({"ANT": ENTRY}))

    def fake_fetch(ticker, layer):
        fresh = {k: None for k in roi.OBJ_COLS}
        fresh.update(YAHOO)
        return dict(INFO, financialCurrency="USD", currency="USD"), fresh

    rep = roi.refresh(["ANT", "NVDA"], dry_run=False, scoring_path=sp,
                      fetcher=fake_fetch, dma_fetcher=lambda t: None,
                      today=dt.date(2026, 11, 28), overrides_path=op)
    ws2 = load_workbook(sp)["Watchlist"]
    assert ws2.cell(2, roi.OBJ_COLS["roic"]).value == -2.27       # ANT overridden
    assert ws2.cell(2, roi.OBJ_COLS["nd_ebitda"]).value == 0
    assert ws2.cell(3, roi.OBJ_COLS["roic"]).value == -23.72      # NVDA untouched
    assert any(f.startswith("ANT: FILING OVERRIDE") for f in rep["flags"])


def test_refresh_drops_yahoo_notes_the_override_replaced(tmp_path):
    wb = Workbook(); ws = wb.active; ws.title = "Watchlist"
    ws.append(["Ticker", "Company", "Layer", "Last Updated"] + [None] * 34)
    ws.append(["ANT", "Anthropic, PBC", "10 Models", "2026-11-21"] + [None] * 34)
    sp = tmp_path / "scoring.xlsx"; wb.save(sp)
    op = tmp_path / "filing-overrides.json"
    op.write_text(json.dumps({"ANT": ENTRY}))

    def fake_fetch(ticker, layer):
        fresh = {k: None for k in roi.OBJ_COLS}
        fresh.update(YAHOO)
        info = dict(INFO, financialCurrency="USD", currency="USD",
                    _fcf_note="ANNUAL fiscal year 2025-12-31",
                    _nd_flags=["ND/EBITDA: EBITDA non-positive — scored as net debt (99)"])
        return info, fresh

    rep = roi.refresh(["ANT"], dry_run=True, scoring_path=sp, fetcher=fake_fetch,
                      dma_fetcher=lambda t: None, today=dt.date(2026, 11, 28),
                      overrides_path=op)
    assert not any("ANNUAL" in f or "net debt (99)" in f for f in rep["flags"])
