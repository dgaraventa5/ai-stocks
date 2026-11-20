"""SEC companyfacts fallback (scripts/sec_statements.py). Offline, stdlib only:
companyfacts JSON is synthesized in the shape data.sec.gov returns it."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import eps_growth  # noqa: E402
import fcf_source  # noqa: E402
import sec_statements as ss  # noqa: E402

D = dt.date
Q_ENDS = {y: [f"{y}-03-31", f"{y}-06-30", f"{y}-09-30", f"{y}-12-31"]
          for y in range(2021, 2027)}


def _ladder(quarters_by_year, ytd_only=False, filed="2026-10-30"):
    """Facts for a calendar fiscal year: 10-Q YTD rungs + the 10-K FY.
    ytd_only mimics the cash-flow statement (no standalone Q2/Q3). Q4 is
    never tagged on its own, as at SEC."""
    facts = []
    for year, vals in quarters_by_year.items():
        start = f"{year}-01-01"
        run = 0.0
        prev_end = start
        for i, v in enumerate(vals):
            end = Q_ENDS[year][i]
            run += v
            form = "10-K" if i == 3 else "10-Q"
            facts.append({"start": start, "end": end, "val": run, "form": form,
                          "filed": filed})
            if not ytd_only and i in (1, 2):
                q_start = (dt.date.fromisoformat(prev_end) + dt.timedelta(days=1)).isoformat()
                facts.append({"start": q_start, "end": end, "val": v, "form": form,
                              "filed": filed})
            prev_end = end
    return facts


def _inst(values):
    return [{"end": e, "val": v, "form": "10-Q", "filed": "2026-10-30"}
            for e, v in values.items()]


def _cf(gaap, unit="USD"):
    return {"facts": {"us-gaap": {k: {"units": {unit: v}} for k, v in gaap.items()}}}


def _company(capex_tag="PaymentsToAcquirePropertyPlantAndEquipment", capex=10.0):
    """Seven quarters to 2026-09-30, the newest a quarter ahead of Yahoo."""
    rev = {2025: [100, 110, 120, 130], 2026: [140, 150, 160]}
    op = {2025: [20, 22, 24, 26], 2026: [28, 30, 32]}
    pretax = {2025: [20, 22, 24, 26], 2026: [28, 30, 32]}
    tax = {2025: [4, 4.4, 4.8, 5.2], 2026: [5.6, 6, 6.4]}
    ni = {2025: [16, 17.6, 19.2, 20.8], 2026: [22.4, 24, 25.6]}
    ocf = {2025: [30, 33, 36, 39], 2026: [42, 45, 48]}
    cap = {2025: [capex] * 4, 2026: [capex] * 3}
    bs = {"2026-06-30": 1000.0, "2026-09-30": 1100.0}
    cl = {"2026-06-30": 200.0, "2026-09-30": 220.0}
    return _cf({
        "RevenueFromContractWithCustomerExcludingAssessedTax": _ladder(rev),
        "OperatingIncomeLoss": _ladder(op),
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": _ladder(pretax),
        "IncomeTaxExpenseBenefit": _ladder(tax),
        "NetIncomeLoss": _ladder(ni),
        "NetCashProvidedByUsedInOperatingActivities": _ladder(ocf, ytd_only=True),
        capex_tag: _ladder(cap, ytd_only=True),
        "Assets": _inst(bs),
        "LiabilitiesCurrent": _inst(cl),
        "CashAndCashEquivalentsAtCarryingValue": _inst({"2026-09-30": 50.0}),
        "ShortTermInvestments": _inst({"2026-09-30": 25.0}),
        "LongTermDebtNoncurrent": _inst({"2026-09-30": 300.0}),
        "LongTermDebtCurrent": _inst({"2026-09-30": 20.0}),
    })


def _st(**kw):
    st, note = ss.statements(_company(**kw), "USD")
    assert st is not None, note
    return st


# ---- parsing -----------------------------------------------------------------

def test_q4_derived_from_fy_minus_9m_in_cash_flow():
    st = _st()
    # cash flow is YTD only; Q4 2025 = FY - 9M = 138 - 99 = 39
    assert st["q"]["ocf"][D(2025, 12, 31)] == 39
    assert st["q"]["ocf"][D(2026, 6, 30)] == 45
    assert st["a"]["ocf"] == {D(2025, 12, 31): 138}


def test_newest_concept_wins_and_older_periods_are_filled():
    old = _ladder({2025: [5, 5, 5, 5]})
    new = _ladder({2026: [7, 7, 7]})
    st, _ = ss.statements(_cf({"Revenues": old,
                               "RevenueFromContractWithCustomerExcludingAssessedTax": new}),
                          "USD")
    assert st["tag"]["revenue"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert st["q"]["revenue"][D(2025, 12, 31)] == 5     # filled from Revenues
    assert st["q"]["revenue"][D(2026, 9, 30)] == 7


def test_restatement_filed_later_wins():
    facts = _ladder({2026: [10, 10, 10]}, filed="2026-08-01")
    facts.append({"start": "2026-04-01", "end": "2026-06-30", "val": 12,
                  "form": "10-Q", "filed": "2026-11-01"})
    st, _ = ss.statements(_cf({"Revenues": facts}), "USD")
    assert st["q"]["revenue"][D(2026, 6, 30)] == 12


def test_ifrs_or_6k_filer_has_no_statements():
    st, note = ss.statements({"facts": {"ifrs-full": {"Revenue": {}}}}, "USD")
    assert st is None and "us-gaap" in note


def test_financial_currency_unit_is_used():
    st, _ = ss.statements(_cf({"Revenues": _ladder({2025: [1, 1, 1, 1]})}, unit="CNY"), "CNY")
    assert st["a"]["revenue"] == {D(2025, 12, 31): 4}
    st, note = ss.statements(_cf({"Revenues": _ladder({2025: [1, 1, 1, 1]})}, unit="CNY"), "USD")
    assert st is None and "USD" in note


# ---- source choice -------------------------------------------------------------

def test_is_newer_and_prefer_sec():
    assert ss.is_newer(D(2026, 9, 30), D(2026, 6, 30))
    assert not ss.is_newer(D(2026, 8, 2), D(2026, 7, 31))      # same quarter, normalized
    assert ss.prefer_sec(1.0, D(2026, 6, 30), 2.0, D(2026, 9, 30))
    assert not ss.prefer_sec(1.0, D(2026, 6, 30), 2.0, D(2026, 6, 28))
    assert ss.prefer_sec(None, D(2026, 6, 30), 2.0, D(2026, 6, 28))  # Yahoo blank
    assert not ss.prefer_sec(None, D(2026, 9, 30), 2.0, D(2026, 3, 31))  # SEC older
    assert not ss.prefer_sec(1.0, D(2026, 6, 30), None, D(2026, 9, 30))


def test_lagging_uses_most_recent_quarter():
    assert ss.lagging(D(2026, 7, 31), D(2026, 10, 25))          # NVDA on 2026-11-20
    assert not ss.lagging(D(2026, 10, 31), D(2026, 10, 25))
    assert not ss.lagging(D(2026, 7, 31), None)


def test_last_four_needs_consecutive_quarters():
    s = {D(2026, 9, 30): 1, D(2026, 6, 30): 1, D(2026, 3, 31): 1, D(2025, 9, 30): 1}
    assert ss.last_four(s) == (None, None)                      # 2025-Q4 missing
    s[D(2025, 12, 31)] = 1
    assert ss.last_four(s) == (4.0, D(2026, 9, 30))


# ---- the inputs ----------------------------------------------------------------

def test_sec_roic_ttm_matches_rule_34():
    v, flags, end = ss.sec_roic(_st())
    # TTM op 26+28+30+32 = 116, tax 23.2 / pretax 116 = 20%, capital 1100-220
    assert end == D(2026, 9, 30)
    assert v == round(116 * 0.8 / 880 * 100, 2)
    assert any("GAAP operating income" in f for f in flags)


def test_pretax_derived_when_only_10k_tags_it():
    cf = _company()
    gaap = cf["facts"]["us-gaap"]
    key = "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"
    gaap[key]["units"]["USD"] = [f for f in gaap[key]["units"]["USD"] if f["form"] == "10-K"]
    st, _ = ss.statements(cf, "USD")
    v, flags, _ = ss.sec_roic(st)
    assert v == round(116 * 0.8 / 880 * 100, 2)                 # NI + tax = pretax
    assert any("derived as net income + income tax" in f for f in flags)


def test_choose_fcf_newer_and_reconciled():
    st = _st()
    # Yahoo TTM to June (month-end): OCF 36+39+42+45 = 162, capex 40 -> 122
    d = ss.choose_fcf(122.0, D(2026, 6, 30), fcf_source.QUARTERLY, st)
    assert d["use"] and d["end"] == D(2026, 9, 30)
    assert d["value"] == (39 + 42 + 45 + 48) - 40
    assert d["rev"] == 130 + 140 + 150 + 160                     # same four quarters
    assert "reconciles with Yahoo" in d["note"]


def test_choose_fcf_refuses_when_sec_misses_a_capex_line():
    # SHAZ 2026-11-20: Yahoo's capex includes a line SEC's standard concept lacks
    d = ss.choose_fcf(-200.0, D(2026, 6, 30), fcf_source.QUARTERLY, _st())
    assert not d["use"] and "NOT used" in d["note"]


def test_choose_fcf_not_newer_keeps_yahoo():
    d = ss.choose_fcf(134.0, D(2026, 9, 30), fcf_source.QUARTERLY, _st())
    assert not d["use"] and "NOT used" not in d["note"]


def test_choose_fcf_when_yahoo_has_none():
    d = ss.choose_fcf(None, None, None, _st(capex_tag="PaymentsToAcquireProductiveAssets"))
    assert d["use"] and "not reconciled" in d["note"]
    assert "PaymentsToAcquireProductiveAssets" in d["note"]


def test_choose_roic_reconciles_on_yahoos_period():
    st = _st()
    yahoo_june, *_ = ss.sec_roic(st, D(2026, 6, 30))
    d = ss.choose_roic(yahoo_june + 0.5, D(2026, 6, 30), st)
    assert d["use"] and d["end"] == D(2026, 9, 30)
    d = ss.choose_roic(yahoo_june + 9.0, D(2026, 6, 30), st)
    assert not d["use"] and "NOT used" in d["note"]


def test_choose_rev_cagr_uses_a_10k_yahoo_has_not_loaded():
    rev = {y: [100 * 1.1 ** (y - 2021)] * 4 for y in range(2021, 2026)}
    st, _ = ss.statements(_cf({"Revenues": _ladder(rev)}), "USD")
    # Yahoo's newest fiscal year is 2024 (blank 2025 placeholder)
    y_rev = {D(2024, 12, 31): 4 * 100 * 1.1 ** 3, D(2023, 12, 31): 4 * 100 * 1.1 ** 2,
             D(2022, 12, 31): 440.0, D(2021, 12, 31): 400.0, D(2025, 12, 31): float("nan")}
    d = ss.choose_rev_cagr(None, y_rev, st)
    assert d["use"] and d["end"] == D(2025, 12, 31) and d["value"] == 10.0
    y_rev[D(2024, 12, 31)] *= 1.05                                # concepts disagree
    d = ss.choose_rev_cagr(9.0, y_rev, st)
    assert not d["use"] and "NOT used" in d["note"]


def test_choose_eps_yoy_fills_a_lagging_statement(monkeypatch):
    monkeypatch.setattr(ss, "NI_FLOOR", 0.0)        # synthetic figures are tiny
    st = _st()
    y_ni = {D(2026, 6, 30): 24.0, D(2025, 6, 30): 17.6}            # Yahoo ends June
    d = ss.choose_eps_yoy(y_ni, D(2026, 9, 30), st)
    assert d["use"] and d["code"] == eps_growth.COMPUTED
    assert d["value"] == round((25.6 / 19.2 - 1) * 100, 2)
    d = ss.choose_eps_yoy({D(2026, 6, 30): 40.0}, D(2026, 9, 30), st)
    assert not d["use"] and "NOT used" in d["note"]


def test_choose_eps_yoy_stays_a_gap_when_sec_is_behind_too():
    d = ss.choose_eps_yoy({}, D(2026, 12, 31), _st())
    assert not d["use"] and "behind" in d["note"]


def test_debt_and_cash_from_latest_balance_sheet():
    debt, cash, asof, note = ss.sec_debt_cash(_st())
    assert (debt, cash, asof) == (320.0, 75.0, D(2026, 9, 30))
    assert "leases" in note


# ---- fetch-once context ----------------------------------------------------------

def test_context_fetches_once_and_reports_why():
    calls = []

    def fetcher(t):
        calls.append(t)
        return _company(), "ok"

    ctx = ss.SecContext("TER", "USD", fetcher=fetcher)
    assert not ctx.fetched
    assert ctx.get() is ctx.get() and calls == ["TER"]
    assert ctx.newest_quarter() == D(2026, 9, 30)

    bad = ss.SecContext("POET", "USD", fetcher=lambda t: ({"facts": {}}, "ok"))
    assert bad.get() is None and "us-gaap" in bad.note


def test_foreign_local_listing_never_hits_the_network():
    assert ss.fetch_companyfacts("6861.T") == (None, "foreign local listing — no SEC filings")


def test_fcf_detail_reports_period_and_kind():
    q = {fcf_source.OCF: {D(2026, 9, 30): 4, D(2026, 6, 30): 3, D(2026, 3, 31): 2,
                          D(2025, 12, 31): 1},
         "Capital Expenditure": {D(2026, 9, 30): -1, D(2026, 6, 30): -1,
                                 D(2026, 3, 31): -1, D(2025, 12, 31): -1}}
    assert fcf_source.fcf_detail(q, {})[1:] == ("quarterly TTM to 2026-09-30",
                                                D(2026, 9, 30), fcf_source.QUARTERLY)
    a = {fcf_source.OCF: {D(2025, 12, 31): 9}, "Capital Expenditure": {D(2025, 12, 31): -2}}
    v, _note, end, kind = fcf_source.fcf_detail({}, a)
    assert (v, end, kind) == (7, D(2025, 12, 31), fcf_source.ANNUAL)
