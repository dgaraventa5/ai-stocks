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
