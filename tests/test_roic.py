"""TTM ROIC calculation (scripts/roic.py).

Uses a hand-rolled stub rather than pandas DataFrames: the minimal deploy CI has
only openpyxl + pytest, and roic.py itself imports nothing beyond the stdlib
(it takes the ticker as a parameter), so these must stay dependency-free.
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import roic  # noqa: E402


class _Series:
    def __init__(self, vals):
        self._v = [v for v in vals if v is not None]

    def dropna(self):
        return self

    def __len__(self):
        return len(self._v)

    @property
    def iloc(self):
        return self

    def __getitem__(self, k):
        return _Series(self._v[k]) if isinstance(k, slice) else self._v[k]

    def sum(self):
        return float(sum(self._v))


class _Frame:
    """Minimal df stand-in: .index, .columns, .loc[key] -> _Series."""
    def __init__(self, rows, columns=None):
        self._rows = rows
        self.columns = columns or []

    @property
    def index(self):
        return list(self._rows)

    @property
    def loc(self):
        return self

    def __getitem__(self, k):
        return _Series(self._rows[k])


class _Col:
    def __init__(self, d): self._d = d
    def date(self): return self._d


class _Ticker:
    def __init__(self, inc, bs, info=None, ticker=None):
        self.quarterly_income_stmt = inc
        self.quarterly_balance_sheet = bs
        self.info = info or {}
        if ticker:
            self.ticker = ticker


def _tk(op=(100, 100, 100, 100), pretax=(400,), tax=(84,), assets=1500.0,
        cur_liab=500.0, asof=dt.date(2026, 6, 30), mrq=None, extra=None,
        ticker=None):
    """Capital employed = assets - cur_liab (default 1000)."""
    rows = {"Operating Income": list(op), "Pretax Income": list(pretax),
            "Tax Provision": list(tax)}
    rows.update(extra or {})
    inc = _Frame(rows, columns=[_Col(asof)])
    bs = _Frame({"Total Assets": [assets], "Current Liabilities": [cur_liab]})
    info = {}
    if mrq:
        info["mostRecentQuarter"] = int(dt.datetime(
            mrq.year, mrq.month, mrq.day, tzinfo=dt.UTC).timestamp())
    return _Ticker(inc, bs, info, ticker)


def test_basic_roic():
    """400 op x (1-0.21) / (1500-500) = 31.6%."""
    v, _ = roic.statement_roic(_tk())
    assert v == 31.6


def test_low_effective_rate_is_used_not_floored():
    """A genuinely low rate (AVGO ~3.8%, CIEN ~8.8%) must NOT be clamped up:
    the 10% floor this replaced understated exactly those names."""
    r, defaulted = roic.effective_tax_rate(1000.0, 38.0)
    assert not defaulted and abs(r - 0.038) < 1e-9


def test_tax_benefit_floored_at_zero():
    """A net tax benefit would lift NOPAT above operating income — floor at 0."""
    r, defaulted = roic.effective_tax_rate(1000.0, -250.0)
    assert defaulted and r == 0.0


def test_absurd_rate_clamped_high():
    r, defaulted = roic.effective_tax_rate(100.0, 90.0)
    assert defaulted and r == roic.TAX_MAX


def test_loss_making_falls_back_to_statutory():
    r, defaulted = roic.effective_tax_rate(-500.0, 10.0)
    assert defaulted and r == roic.TAX_DEFAULT


def test_non_positive_capital_employed_blanks():
    """Current liabilities exceeding total assets: ratio meaningless, not merely
    bad. (The old debt+equity-cash form produced CRWD's -1263% this way.)"""
    v, flags = roic.statement_roic(_tk(assets=400.0, cur_liab=500.0))
    assert v is None
    assert any("non-positive" in f for f in flags)


def test_cash_rich_name_does_not_explode():
    """Regression for the rejected financing denominator: a name whose cash ~
    equals its equity (NTAP/PLTR/GEV shape) collapsed debt+equity-cash toward
    zero and produced ROIC of 262-451%. Capital employed stays proportionate."""
    v, _ = roic.statement_roic(_tk(op=(250, 250, 250, 250), assets=10_000.0,
                                   cur_liab=3_000.0))
    assert v is not None and 0 < v < 25, f"denominator collapsed: {v}"


def test_negative_roic_is_kept_not_blanked():
    """Percentile scoring (rule 20) ranks a loss-maker last harmlessly, so a
    negative ROIC is real information and must survive."""
    v, _ = roic.statement_roic(_tk(op=(-50, -50, -50, -50)))
    assert v is not None and v < 0


def test_fewer_than_four_quarters_is_none():
    v, flags = roic.statement_roic(_tk(op=(100, 100)))
    assert v is None and any("4 quarters" in f for f in flags)


def test_stale_statements_are_flagged():
    """The CIEN 2026-09-08 case: statements end 2026-04-30 while the company has
    reported 2026-08-01, so a naive 4-quarter sum is a year ending in APRIL."""
    v, flags = roic.statement_roic(
        _tk(asof=dt.date(2026, 4, 30), mrq=dt.date(2026, 8, 1)))
    assert v is not None, "stale data should still compute, just be flagged"
    assert any(f.startswith("STALE") for f in flags)


def test_current_statements_not_flagged_stale():
    v, flags = roic.statement_roic(
        _tk(asof=dt.date(2026, 6, 30), mrq=dt.date(2026, 6, 30)))
    assert v is not None and not any(f.startswith("STALE") for f in flags)


# --- Yahoo's "special charge" add-back (2026-10-16, SHOP) --------------------
# Yahoo's quarterly "Operating Income" adds back whatever it files as a special
# charge. For SHOP that includes "transaction and loan losses", a line on the
# company's own income statement, so Yahoo printed 629 for Q2 2026 against the
# 10-Q's 488. Shape below: Yahoo 100/qtr, GAAP 80/qtr, 20/qtr filed as special.
_SHOP_SHAPE = {"Total Operating Income As Reported": [80, 80, 80, 80],
               "Special Income Charges": [-20, -20, -20, -20]}


def test_listed_name_uses_gaap_operating_income(monkeypatch):
    """320 GAAP op x (1-0.21) / 1000 = 25.28%, not the 31.6% on Yahoo's line."""
    monkeypatch.setitem(roic.GAAP_OPERATING_INCOME, "TEST", "fixture")
    v, flags = roic.statement_roic(_tk(extra=_SHOP_SHAPE, ticker="TEST"))
    assert v == 25.28
    assert any("GAAP operating income" in f for f in flags)


def test_listed_name_without_as_reported_line_subtracts_special_charges(monkeypatch):
    monkeypatch.setitem(roic.GAAP_OPERATING_INCOME, "TEST", "fixture")
    shape = {"Special Income Charges": [-20, -20, -20, -20]}
    v, _ = roic.statement_roic(_tk(extra=shape, ticker="TEST"))
    assert v == 25.28


def test_listed_name_with_no_gaap_figure_keeps_yahoo_line_and_flags(monkeypatch):
    """Rule 3: a missing GAAP figure is flagged, not silently swapped."""
    monkeypatch.setitem(roic.GAAP_OPERATING_INCOME, "TEST", "fixture")
    v, flags = roic.statement_roic(_tk(ticker="TEST"))
    assert v == 31.6
    assert any("GAAP operating income unavailable" in f for f in flags)


def test_unlisted_name_keeps_yahoo_operating_income():
    """One-off impairments and restructuring stay excluded for everyone else
    (MBLY's -3.8B goodwill charge must not sink its ROIC for a year)."""
    v, _ = roic.statement_roic(_tk(extra=_SHOP_SHAPE, ticker="OTHER"))
    assert v == 31.6


def test_shop_is_listed_with_a_citation():
    assert "10-Q" in roic.GAAP_OPERATING_INCOME["SHOP"]


def test_charges_stripped_every_quarter_raise_review_flag():
    """Unlisted name, charges every quarter worth >10% of op income: flag it
    for a 10-Q check. The value is unchanged -- a flag, never a swap."""
    v, flags = roic.statement_roic(_tk(extra=_SHOP_SHAPE, ticker="OTHER"))
    assert v == 31.6
    assert any(f.startswith("REVIEW") for f in flags)


def test_one_off_charge_does_not_raise_review_flag():
    shape = {"Special Income Charges": [-300, 0, 0, 0]}
    _, flags = roic.statement_roic(_tk(extra=shape, ticker="OTHER"))
    assert not any(f.startswith("REVIEW") for f in flags)


def test_small_recurring_charge_does_not_raise_review_flag():
    shape = {"Special Income Charges": [-5, -5, -5, -5]}
    _, flags = roic.statement_roic(_tk(extra=shape, ticker="OTHER"))
    assert not any(f.startswith("REVIEW") for f in flags)
