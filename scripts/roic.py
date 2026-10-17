"""TTM return on invested capital, computed from the financial statements.

Why this module exists (2026-09-08): ROIC (Watchlist col 11) was a *curated*
input -- refresh_objective_inputs printed "curated input, not fetched" on every
single refresh and kept whatever number was last typed in. The result was a
column that was 39% blank (84 of 214, including all 39 robotics names), carried
hand-rounded values next to computed ones, and went stale exactly when it
mattered: CIEN read 11 while its true TTM figure had moved to ~20 after
operating profit nearly tripled.

Definition (approved by Dom 2026-09-08):

    ROIC = TTM NOPAT / capital employed
         = TTM operating income x (1 - effective tax rate)
           -------------------------------------------------
              total assets - current liabilities

* **TTM, not last fiscal year.** This is the whole point. On CIEN's last
  completed fiscal year the answer is 7.5%; on a trailing-twelve-month basis
  including the quarter just reported it is ~20.6%. Same company, same formula.
  Annual statements describe a different company for fast-growing names, and TTM
  is already the project convention for margins and growth (rule 9).
* **Denominator is capital employed (TA - CL), NOT debt+equity-cash.** The
  financing form was tried first and REJECTED on the data: subtracting all cash
  collapses the denominator for cash-rich names and manufactures enormous
  returns. Measured 2026-09-08 -- NTAP: equity 1.4B + debt 2.7B - cash 3.6B =
  0.5B of "invested capital" against 6.9B of revenue, giving ROIC 262%; PLTR
  0.58B -> 451%; GEV 1.63B on 41B revenue -> 110%. Those rank a storage vendor
  above NVDA on capital efficiency, which is an artifact, not a finding. TA - CL
  is the classic ROCE denominator: bounded, never near-zero for a going concern,
  and proportionate to the business (NTAP 6.7B, PLTR 10.1B, GEV 25.0B). The cost
  is that idle cash sits in the base, so cash hoarders score lower -- defensible,
  since uninvested cash genuinely isn't earning an operating return.
* **Goodwill is INCLUDED (it falls inside total assets).** Stripping it would measure how
  well the operating business runs; including it measures the return on every
  dollar actually deployed, acquisitions included. Deliberate: it marks down
  serial acquirers (AVGO ~29% -> ~20%) rather than letting them look efficient
  for capital they really did spend. This is a capital-allocation framework, so
  the denominator is all the capital.
* **Currency-neutral (rule 19 does NOT apply).** Numerator and denominator both
  come from the same statements in the same reporting currency, so the units
  cancel -- unlike P/S or EV/EBITDA, which divide a USD price by local-currency
  financials. Foreign filers are computable here; they are excluded for now by
  caller choice (Dom, 2026-09-08), not by any FX limitation.

Percentile scoring (rule 20) ranks ROIC within a layer cohort, so extreme
negatives rank last harmlessly and are NOT blanked. The one hard blank is a
non-positive invested capital, where the ratio is meaningless rather than
merely bad (a near-zero denominator is what produced CRWD's -1263%).
"""
from __future__ import annotations

# Effective-tax-rate clamp. A loss-making quarter, a valuation-allowance release
# or a one-off repatriation charge can make the raw rate negative or >100%,
# which would flip or explode NOPAT. The floor is 0, NOT 10%: genuinely low
# effective rates are real (AVGO runs ~3.8% on its IP structure, CIEN ~8.8%) and
# clamping them up understated those names. The floor only stops a net tax
# BENEFIT from lifting NOPAT above operating income.
TAX_MIN, TAX_MAX, TAX_DEFAULT = 0.0, 0.35, 0.21

_OP_KEYS = ("Operating Income", "EBIT")
_GAAP_OP_KEY = "Total Operating Income As Reported"
_SPECIAL_KEY = "Special Income Charges"

# Names whose GAAP operating income must replace Yahoo's "Operating Income"
# (added 2026-10-16). Yahoo's line adds back whatever it files as a "special
# charge". That is right for genuine one-offs (impairments, a restructuring) and
# stays the rule for everyone else. It is wrong when Yahoo files a line that the
# company itself reports as an ordinary operating cost, so a name goes on this
# list only on documented evidence from its own income statement -- the rule-15
# standard, not a mechanical threshold. Rejected alternatives, measured on the
# Watchlist 2026-10-16: (a) GAAP for every name, which would put one-off
# impairments into 40+ names' ROIC for a year (MBLY -3.8B goodwill, INTC, ENTG);
# (b) GAAP whenever charges recur at a steady size, whose cutoff would decide
# names by itself (steadiness SHOP 0.77, AVGO 0.49, CRM 0.41 -- the last two are
# company-labeled restructuring). The REVIEW flag below surfaces candidates.
GAAP_OPERATING_INCOME = {
    "SHOP": ("transaction and loan losses ($141M in Q2 2026) are an operating "
             "line on Shopify's own income statement (10-Q Q2 2026 p.7); Yahoo "
             "files them as a restructuring charge and adds them back, printing "
             "operating income of $629M against the 10-Q's $488M"),
}

# REVIEW flag: charges stripped in all four quarters, worth more than this share
# of TTM operating income. A prompt to read the 10-Q, never a value change.
REVIEW_SHARE = 0.10
_EQ_KEYS = ("Stockholders Equity", "Total Equity Gross Minority Interest")
_CASH_KEYS = ("Cash Cash Equivalents And Short Term Investments",
              "Cash And Cash Equivalents")


def _ttm(df, keys, n=4):
    """Sum of the last n quarters for the first key present. None if short."""
    for k in keys if isinstance(keys, tuple) else (keys,):
        if df is not None and k in df.index:
            s = df.loc[k].dropna()
            if len(s) >= n:
                return float(s.iloc[:n].sum())
    return None


def _latest(df, keys):
    """Most recent non-null value for the first key present."""
    for k in keys if isinstance(keys, tuple) else (keys,):
        if df is not None and k in df.index:
            s = df.loc[k].dropna()
            if len(s):
                return float(s.iloc[0])
    return None


def effective_tax_rate(pretax, tax):
    """Clamped effective rate; TAX_DEFAULT when the inputs can't yield one."""
    if pretax is None or tax is None or pretax <= 0:
        return TAX_DEFAULT, True
    r = tax / pretax
    if r < TAX_MIN or r > TAX_MAX:
        return min(max(r, TAX_MIN), TAX_MAX), True
    return r, False


def _last4(df, key):
    """Last four quarterly values (most recent first), or None if short."""
    if df is None or key not in df.index:
        return None
    s = df.loc[key].dropna()
    return [float(v) for v in s.iloc[:4]] if len(s) >= 4 else None


def _operating_income(inc, ticker):
    """(TTM operating income, flags), honoring GAAP_OPERATING_INCOME."""
    flags: list[str] = []
    op = _ttm(inc, _OP_KEYS)
    special = _last4(inc, _SPECIAL_KEY)
    if ticker in GAAP_OPERATING_INCOME:
        gaap = _ttm(inc, (_GAAP_OP_KEY,))
        if gaap is None and op is not None and special is not None:
            gaap = op + sum(special)
        if gaap is None:
            flags.append("GAAP operating income unavailable — Yahoo's line "
                         "kept (overstates; see GAAP_OPERATING_INCOME)")
        else:
            flags.append(f"GAAP operating income used ({ticker}: Yahoo adds "
                         f"back an operating cost)")
            return gaap, flags
    elif (op is not None and special is not None and op != 0
          and all(v < 0 for v in special)
          and abs(sum(special)) > REVIEW_SHARE * abs(op)):
        flags.append(f"REVIEW: Yahoo strips charges every quarter "
                     f"({abs(sum(special)) / abs(op):.0%} of operating income) "
                     f"— check the 10-Q; if they are an operating line, add "
                     f"the name to roic.GAAP_OPERATING_INCOME")
    return op, flags


def statement_roic(t, ticker=None) -> tuple[float | None, list[str]]:
    """(ROIC %, flags) for a yfinance Ticker. None when not computable.

    Returns the reason in flags so callers can report a gap rather than paper
    over it (rule 3). Never raises on a missing statement.

    STATEMENT LAG (the trap this guards): yfinance's quarterly statements can
    trail the company's own reporting by a full quarter, per-name and silently.
    On 2026-09-08 CIEN's latest quarterly column was 2026-04-30 even though it
    had reported the quarter ended 2026-08-01 five days earlier -- so a naive
    4-quarter sum returned the year ending in APRIL and looked perfectly normal.
    info['mostRecentQuarter'] knew the true quarter, so we compare the two and
    flag STALE. A stale ROIC is still far better than a frozen hand-typed one,
    but it must be visible, never assumed current (rule 3). Upgrade path if this
    proves annoying: SEC XBRL companyfacts with Q4 derived as FY - 9M (Q4 is
    never tagged as a standalone period).
    """
    flags: list[str] = []
    try:
        inc = t.quarterly_income_stmt
        bs = t.quarterly_balance_sheet
    except Exception as exc:                                  # pragma: no cover
        return None, [f"statement fetch failed: {exc}"]

    asof = None
    try:
        if inc is not None and len(inc.columns):
            asof = inc.columns[0].date()
            mrq = (t.info or {}).get("mostRecentQuarter")
            if mrq:
                import datetime as _dt
                true_q = _dt.datetime.fromtimestamp(mrq, _dt.UTC).date()
                if (true_q - asof).days > 45:
                    flags.append(
                        f"STALE: statements end {asof}, company has reported "
                        f"{true_q} — TTM is a quarter behind")
    except Exception:
        pass
    if asof:
        flags.append(f"as-of {asof}")

    pretax = _ttm(inc, ("Pretax Income",))
    tax = _ttm(inc, ("Tax Provision",))
    rate, defaulted = effective_tax_rate(pretax, tax)
    if defaulted:
        flags.append(f"effective tax rate unusable/clamped -> {rate:.0%}")

    op, opflags = _operating_income(inc, ticker or getattr(t, "ticker", None))
    flags.extend(opflags)
    if op is None:
        if inc is not None and not any(
                k in inc.index for k in _OP_KEYS + (_GAAP_OP_KEY,)):
            return _financial_template_roic(inc, bs, rate, flags)
        return None, flags + ["no 4 quarters of operating income"]

    ta = _latest(bs, ("Total Assets",))
    cl = _latest(bs, ("Current Liabilities",))
    if ta is None or cl is None:
        return None, flags + ["no total assets / current liabilities"]
    ic = ta - cl
    if ic <= 0:
        return None, flags + [
            f"capital employed non-positive ({ic/1e6:,.0f}M) — ratio meaningless"]

    return round(op * (1 - rate) / ic * 100, 2), flags


def _financial_template_roic(inc, bs, rate, flags):
    """Return on equity for names Yahoo files on a financial-company template.

    Added 2026-10-16 for LMND (insurer) and UPST (lender), which were blank:
    Yahoo gives them no operating-income line and an unclassified balance sheet
    (no Current Liabilities), so neither half of the standard formula exists.

    Numerator -- Total Revenue - Total Expenses when both are filed (LMND; it
    leaves out non-operating items), else Pretax Income (UPST). Both are AFTER
    interest, and for these businesses that is right: borrowed money is the raw
    material. UPST's own 10-Q books its funding interest inside operating
    expenses (us-gaap InterestExpenseOperating, $12.5M in Q2 2026) and its GAAP
    operating income ($14.6M) sits within ~$2.6M of pretax ($17.2M).

    Denominator -- stockholders' equity. Because the numerator has already paid
    the interest, adding debt to the base would charge the debt twice. (Equity +
    debt was measured as the alternative: UPST 7.6% -> 2.1%, LMND -21% -> -15%.)
    The cost: this is a return on EQUITY, so leverage amplifies it relative to
    the TA - CL names it is ranked against. Flagged, never silent (rule 3).

    Gated on the operating line being absent altogether, so a normal company
    with a missing quarter never lands here.
    """
    rev = _ttm(inc, ("Total Revenue",))
    exp = _ttm(inc, ("Total Expenses",))
    if rev is not None and exp is not None:
        op, basis = rev - exp, "revenue - total expenses"
    else:
        op, basis = _ttm(inc, ("Pretax Income",)), "pretax income"
    if op is None:
        return None, flags + ["no 4 quarters of operating income or pretax income"]
    eq = _latest(bs, _EQ_KEYS)
    if eq is None:
        return None, flags + ["no stockholders equity"]
    if eq <= 0:
        return None, flags + [
            f"equity non-positive ({eq/1e6:,.0f}M) — ratio meaningless"]
    flags.append(f"FINANCIAL TEMPLATE: {basis} / stockholders equity "
                 "(return-on-equity proxy, after interest)")
    return round(op * (1 - rate) / eq * 100, 2), flags
