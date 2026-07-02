"""Unit tests for the foreign-ADR currency-trap fix (pure functions).

The trap (project memory: foreign-ADR-currency-trap): a name that trades in one
currency (USD ADR) but reports financials in another (TWD) has garbage
market-cap-based ratios from yfinance — P/S, EV/EBITDA, FCF-Yield mix USD price
with local financials. Detection is a trading-vs-financial mismatch; the fix
sources those three ratios from the company's LOCAL listing (same-currency, so
its ratios are clean and dimensionless — directly comparable to USD names).
"""
import adr_currency as ac


def test_mismatch_true_when_currencies_differ():
    assert ac.has_currency_mismatch("USD", "TWD") is True


def test_mismatch_false_when_same_currency():
    # Vanguard (5347.TWO) trades AND reports in TWD -> clean, NOT a trap.
    assert ac.has_currency_mismatch("TWD", "TWD") is False
    # Hua Hong (HHUSF) trades AND reports in USD -> clean.
    assert ac.has_currency_mismatch("USD", "USD") is False


def test_mismatch_case_insensitive():
    assert ac.has_currency_mismatch("twd", "TWD") is False


def test_mismatch_false_when_either_missing():
    assert ac.has_currency_mismatch("USD", None) is False
    assert ac.has_currency_mismatch(None, "TWD") is False
    assert ac.has_currency_mismatch("", "TWD") is False


def test_local_value_ratios_normal_case():
    # 2330.TW (TSM local): clean same-currency ratios + local statement FCF.
    out = ac.local_value_ratios(
        {"enterpriseToEbitda": 22.0, "priceToSalesTrailing12Months": 15.6,
         "marketCap": 6.4e13}, local_fcf=1.05e12)
    assert out["ev_ebitda"] == 22.0
    assert out["ps"] == 15.6
    assert out["fcf_yield"] == round(1.05e12 / 6.4e13 * 100, 2)  # 1.64


def test_local_value_ratios_negative_ev_ebitda_passes_through():
    # A loss-making foundry can have negative EV/EBITDA — meaningful, keep it
    # (the scoring bands handle negatives); do not blank.
    out = ac.local_value_ratios(
        {"enterpriseToEbitda": -30.0, "priceToSalesTrailing12Months": 8.0,
         "marketCap": 1e12}, local_fcf=-2e10)
    assert out["ev_ebitda"] == -30.0
    assert out["fcf_yield"] == -2.0


def test_local_value_ratios_rejects_absurd_values():
    out = ac.local_value_ratios(
        {"enterpriseToEbitda": None, "priceToSalesTrailing12Months": 5000.0,
         "marketCap": 1e9}, local_fcf=1e8)
    assert out["ev_ebitda"] is None           # None in -> None out
    assert out["ps"] is None                  # 5000 is absurd -> rejected


def test_local_value_ratios_blank_fcf_yield_when_inputs_missing():
    assert ac.local_value_ratios(
        {"enterpriseToEbitda": 20.0, "priceToSalesTrailing12Months": 8.0},
        local_fcf=1e8)["fcf_yield"] is None   # no marketCap
    assert ac.local_value_ratios(
        {"enterpriseToEbitda": 20.0, "priceToSalesTrailing12Months": 8.0,
         "marketCap": 1e9}, local_fcf=None)["fcf_yield"] is None


def test_adr_local_map_has_tsm_and_umc():
    assert ac.ADR_LOCAL["TSM"] == "2330.TW"
    assert ac.ADR_LOCAL["UMC"] == "2303.TW"


# --- general FX conversion (the "convert whenever we need it" mechanism) ---

def test_fx_rate_same_currency_is_one_no_network():
    assert ac.fx_rate("USD", "USD") == 1.0


def test_fx_rate_uses_from_to_ticker():
    # Injected fake yfinance: fx_rate('HKD','USD') must query 'HKDUSD=X'.
    seen = {}

    class _FakeTicker:
        def __init__(self, sym):
            seen["sym"] = sym
        @property
        def info(self):
            return {"regularMarketPrice": 0.1275}

    assert ac.fx_rate("HKD", "USD", ticker_cls=_FakeTicker) == 0.1275
    assert seen["sym"] == "HKDUSD=X"


def test_ratios_via_fx_converts_market_cap_then_computes():
    # mcap 100 (trading) x rate 0.1 = 10 (financial currency). revenue 5, ebitda 2,
    # debt 3, cash 1, fcf 1  ->  P/S 2, EV/EBITDA (10+3-1)/2 = 6, FCF-yield 1/10 = 10%.
    out = ac.ratios_via_fx(mcap_trading=100.0, rate=0.1, revenue=5.0,
                           ebitda=2.0, debt=3.0, cash=1.0, fcf=1.0)
    assert out["ps"] == 2.0
    assert out["ev_ebitda"] == 6.0
    assert out["fcf_yield"] == 10.0


def test_ratios_via_fx_negative_ebitda_blanks_ev_ebitda():
    out = ac.ratios_via_fx(mcap_trading=100.0, rate=0.1, revenue=5.0,
                           ebitda=-2.0, debt=0.0, cash=0.0, fcf=1.0)
    assert out["ev_ebitda"] is None          # non-positive EBITDA -> blank
    assert out["ps"] == 2.0


def test_ratios_via_fx_blank_when_market_cap_or_rate_missing():
    assert ac.ratios_via_fx(None, 0.1, 5.0, 2.0, 0.0, 0.0, 1.0)["ps"] is None
    assert ac.ratios_via_fx(100.0, None, 5.0, 2.0, 0.0, 0.0, 1.0)["ps"] is None


def test_ratios_via_fx_treats_missing_debt_cash_fcf_gracefully():
    out = ac.ratios_via_fx(mcap_trading=100.0, rate=0.1, revenue=5.0,
                           ebitda=2.0, debt=None, cash=None, fcf=None)
    assert out["ev_ebitda"] == 5.0           # ev = mcap 10 + 0 - 0 = 10; /2 = 5
    assert out["fcf_yield"] is None          # no FCF

