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
    def __init__(self, inc, bs, info=None):
        self.quarterly_income_stmt = inc
        self.quarterly_balance_sheet = bs
        self.info = info or {}


def _tk(op=(100, 100, 100, 100), pretax=(400,), tax=(84,), assets=1500.0,
        cur_liab=500.0, asof=dt.date(2026, 6, 30), mrq=None):
    """Capital employed = assets - cur_liab (default 1000)."""
    inc = _Frame({"Operating Income": list(op), "Pretax Income": list(pretax),
                  "Tax Provision": list(tax)}, columns=[_Col(asof)])
    bs = _Frame({"Total Assets": [assets], "Current Liabilities": [cur_liab]})
    info = {}
    if mrq:
        info["mostRecentQuarter"] = int(dt.datetime(
            mrq.year, mrq.month, mrq.day, tzinfo=dt.UTC).timestamp())
    return _Ticker(inc, bs, info)


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


# --- Financial-company statement templates (insurers, lenders) -------------
# Yahoo files LMND (insurer) and UPST (lender) on templates with no operating-
# income line and an unclassified balance sheet (no Current Liabilities). Their
# income is reported AFTER the cost of the money they borrow, so the matching
# capital base is shareholders' equity, not TA - CL or equity + debt.

def _fin_tk(rev=None, total_exp=None, pretax=(25, 25, 25, 25), tax=(0, 0, 0, 0),
            assets=3000.0, equity=500.0, cur_liab=None):
    rows = {"Pretax Income": list(pretax), "Tax Provision": list(tax)}
    if rev is not None:
        rows["Total Revenue"] = list(rev)
    if total_exp is not None:
        rows["Total Expenses"] = list(total_exp)
    bs = {"Total Assets": [assets], "Stockholders Equity": [equity]}
    if cur_liab is not None:
        bs["Current Liabilities"] = [cur_liab]
    return _Ticker(_Frame(rows, columns=[_Col(dt.date(2026, 6, 30))]),
                   _Frame(bs))


def test_insurer_uses_revenue_less_expenses_over_equity():
    """LMND shape: Total Revenue / Total Expenses / Pretax, no operating line.
    Revenue - expenses = -40/qtr -> -160 TTM; loss -> statutory 21%;
    -160 x 0.79 / 500 = -25.28%."""
    v, flags = roic.statement_roic(_fin_tk(
        rev=(250,) * 4, total_exp=(290,) * 4, pretax=(-40,) * 4, tax=(1,) * 4))
    assert v == -25.28
    assert any(f.startswith("FINANCIAL TEMPLATE") for f in flags)


def test_lender_falls_back_to_pretax_over_equity():
    """UPST shape: no operating line and no Total Expenses -> pretax income,
    whose interest cost is already an operating expense for a lender.
    100 TTM x (1 - 0.02) / 500 = 19.6%."""
    v, flags = roic.statement_roic(_fin_tk(pretax=(25,) * 4, tax=(0.5,) * 4))
    assert v == 19.6
    assert any("pretax income" in f for f in flags)


def test_financial_template_ignores_debt_in_denominator():
    """Income after interest over equity + debt would charge debt twice (its
    interest in the numerator AND its principal in the base). Assets and
    any debt must not move the answer -- only equity does."""
    a, _ = roic.statement_roic(_fin_tk(assets=3000.0))
    b, _ = roic.statement_roic(_fin_tk(assets=9000.0))
    assert a == b


def test_financial_template_non_positive_equity_blanks():
    v, flags = roic.statement_roic(_fin_tk(equity=0.0))
    assert v is None and any("equity non-positive" in f for f in flags)


def test_financial_template_needs_four_quarters():
    v, flags = roic.statement_roic(_fin_tk(pretax=(25, 25)))
    assert v is None and any("4 quarters" in f for f in flags)


def test_operating_income_without_current_liabilities_stays_blank():
    """The equity base is only for after-interest income. A normal operating-
    income line (before interest) over equity would flatter leveraged names, so
    a classified-income / unclassified-balance-sheet name stays blank."""
    inc = _Frame({"Operating Income": [100] * 4, "Pretax Income": [400],
                  "Tax Provision": [84]}, columns=[_Col(dt.date(2026, 6, 30))])
    bs = _Frame({"Total Assets": [1500.0], "Stockholders Equity": [800.0]})
    v, flags = roic.statement_roic(_Ticker(inc, bs))
    assert v is None and any("current liabilities" in f for f in flags)


def test_standard_names_never_take_the_financial_path():
    v, flags = roic.statement_roic(_tk())
    assert v == 31.6
    assert not any(f.startswith("FINANCIAL TEMPLATE") for f in flags)
