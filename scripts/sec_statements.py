"""SEC XBRL (companyfacts) fallback for the statement-based scoring inputs.

Why (2026-11-20): Yahoo's quarterly statements trail the company's own filings
by a quarter, per name and silently (TER, KLIC, PANW, INTU, SHAZ, RCAT on the
day this was written: each had filed its 10-Q or 10-K at SEC, Yahoo still
served the quarter before). A lagging statement leaves ROIC, FCF yield, FCF
margin and EV/FCF a quarter old, and an EPS gap or missing cash figure blank.
SEC is the primary source of truth (CLAUDE.md, data sources), so when Yahoo is
behind or missing a row, the same calculation is run on the company's own
XBRL facts.

Rules:
- Yahoo stays the default. SEC is used for an input only when its period ends
  more than NEWER_DAYS after Yahoo's (Yahoo is a quarter behind), or Yahoo has
  no value and SEC's is not older (`prefer_sec`). Every SEC value is flagged.
- One companyfacts request per name, and only for names whose Yahoo
  statements lag `mostRecentQuarter` or miss an input (batch_score decides).
- Fiscal Q4 is never tagged on its own; quarters come from
  xbrl_periods.quarterly_from_facts, which derives Q4 = FY - 9M (the 70-100
  day filter alone drops a quarter a year; CLAUDE.md rule 34).
- us-gaap only, in the company's financial currency. IFRS filers (POET) and
  6-K filers have no quarterly us-gaap facts and stay on Yahoo. 20-F filers
  (CAMT, HSAI) have annual facts, used for FCF only when Yahoo has none newer.
- The formulas are the existing ones: roic.effective_tax_rate and the rule-34
  definition, fcf_source.fcf_detail, eps_growth.eps_yoy_fallback,
  revenue_cagr.rev_3y_cagr. One known basis difference, flagged on every SEC
  ROIC: SEC's OperatingIncomeLoss is GAAP, while Yahoo's "Operating Income"
  adds back special charges (rule 34 amendment 2026-10-16).

Everything except `fetch_companyfacts` / `SecContext.get` is pure and
stdlib-only, so it is tested offline (CI runs pytest with openpyxl only).
"""
from __future__ import annotations

import datetime as dt

import eps_growth
import fcf_source
import revenue_cagr
import roic
import xbrl_periods

NEWER_DAYS = 45            # a quarter is ~91 days; month-end normalization ~5
ANNUAL_DAYS = (340, 380)   # 52/53-week fiscal years run 364-371 days

# Concept candidates, in priority order. A company may switch concepts over
# time; the concept with the newest data wins and older periods are filled
# from the others (_pick).
DURATION_TAGS = {
    "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
                "RevenueFromContractWithCustomerIncludingAssessedTax",
                "SalesRevenueNet", "SalesRevenueGoodsNet"),
    "operating_income": ("OperatingIncomeLoss",),
    "pretax": ("IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
               "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"),
    "tax": ("IncomeTaxExpenseBenefit",),
    "net_income": ("NetIncomeLossAvailableToCommonStockholdersBasic", "NetIncomeLoss",
                   "ProfitLoss"),
    "ocf": ("NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
    "capex": ("PaymentsToAcquirePropertyPlantAndEquipment",
              "PaymentsToAcquireProductiveAssets",
              "PaymentsToAcquireOtherProductiveAssets",
              "PaymentsForCapitalImprovements",
              "PaymentsToAcquireOilAndGasPropertyAndEquipment",
              "PaymentsToAcquireOilAndGasProperty"),
}
INSTANT_TAGS = {
    "assets": ("Assets",),
    "current_liabilities": ("LiabilitiesCurrent",),
    "cash": ("CashAndCashEquivalentsAtCarryingValue",
             "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Cash"),
    "short_term_investments": ("ShortTermInvestments", "MarketableSecuritiesCurrent",
                               "AvailableForSaleSecuritiesDebtSecuritiesCurrent"),
    "debt_total": ("DebtLongtermAndShorttermCombinedAmount", "LongTermDebt"),
    "debt_noncurrent": ("LongTermDebtNoncurrent",),
    "debt_current": ("LongTermDebtCurrent",),
    "short_term_borrowings": ("ShortTermBorrowings", "CommercialPaper"),
}


# --------------------------------------------------------------------------
# companyfacts -> {series name: {date: value}}
# --------------------------------------------------------------------------

def _d(value):
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _facts(gaap: dict, tag: str, unit: str) -> list:
    return ((gaap.get(tag) or {}).get("units") or {}).get(unit) or []


def _quarterly(facts) -> dict:
    return {dt.date.fromisoformat(k): v
            for k, v in xbrl_periods.quarterly_from_facts(facts).items()}


def _annual(facts) -> dict:
    out = {}
    for f in sorted(facts, key=lambda f: str(f.get("filed") or "")):
        s, e = _d(f.get("start")), _d(f.get("end"))
        if s and e and ANNUAL_DAYS[0] <= (e - s).days <= ANNUAL_DAYS[1]:
            try:
                out[e] = float(f["val"])
            except (KeyError, TypeError, ValueError):
                pass
    return out


def _instant(facts) -> dict:
    out = {}
    for f in sorted(facts, key=lambda f: str(f.get("filed") or "")):
        e = _d(f.get("end"))
        if e and not f.get("start"):
            try:
                out[e] = float(f["val"])
            except (KeyError, TypeError, ValueError):
                pass
    return out


def _pick(gaap, tags, unit, build) -> tuple[dict, str | None]:
    """Series for the concept with the newest data; gaps filled from the rest."""
    per = [(t, build(_facts(gaap, t, unit))) for t in tags]
    per = [(t, s) for t, s in per if s]
    if not per:
        return {}, None
    newest = max(max(s) for _, s in per)
    tag, primary = next((t, s) for t, s in per if max(s) == newest)
    merged = dict(primary)
    for _t, s in per:
        for d, v in s.items():
            merged.setdefault(d, v)
    return merged, tag


def statements(companyfacts: dict, currency: str | None
               ) -> tuple[dict | None, str]:
    """Parse companyfacts into quarterly / annual / instant series.

    Returns (None, reason) for a filer with no us-gaap facts in that currency.
    """
    gaap = (companyfacts or {}).get("facts", {}).get("us-gaap")
    if not gaap:
        return None, "no us-gaap XBRL facts (IFRS or 6-K filer)"
    unit = currency or "USD"
    st = {"unit": unit, "q": {}, "a": {}, "i": {}, "tag": {}}
    for name, tags in DURATION_TAGS.items():
        st["q"][name], st["tag"][name] = _pick(gaap, tags, unit, _quarterly)
        st["a"][name], atag = _pick(gaap, tags, unit, _annual)
        st["tag"][name] = st["tag"][name] or atag
    for name, tags in INSTANT_TAGS.items():
        st["i"][name], st["tag"][name] = _pick(gaap, tags, unit, _instant)
    if not any(st["q"].values()) and not any(st["a"].values()):
        return None, f"no us-gaap duration facts in {unit}"
    return st, "ok"


# --------------------------------------------------------------------------
# Source choice
# --------------------------------------------------------------------------

def is_newer(a: dt.date | None, b: dt.date | None, days: int = NEWER_DAYS) -> bool:
    """True when period end `a` is more than `days` after `b` (or b unknown)."""
    if a is None:
        return False
    return b is None or (a - b).days > days


def prefer_sec(y_val, y_end, s_val, s_end) -> bool:
    """Use SEC's value? Yes when it describes a newer period than Yahoo's, or
    Yahoo has nothing and SEC's period is not older than Yahoo's."""
    if s_val is None or s_end is None:
        return False
    if y_val is None:
        return not is_newer(y_end, s_end)
    return is_newer(s_end, y_end)


def lagging(yahoo_end: dt.date | None, most_recent_quarter: dt.date | None) -> bool:
    """Yahoo's statement ends a quarter before the company's latest reported
    quarter (info['mostRecentQuarter'])."""
    return most_recent_quarter is not None and is_newer(most_recent_quarter, yahoo_end)


# --------------------------------------------------------------------------
# The inputs, computed on SEC series
# --------------------------------------------------------------------------

def last_four(series: dict, end: dt.date | None = None):
    """(sum, end) of four consecutive quarters ending at `end` (default the
    newest), else (None, None)."""
    dates = sorted((d for d in series if end is None or d <= end), reverse=True)[:4]
    if len(dates) < 4 or (end is not None and dates[0] != end):
        return None, None
    if not xbrl_periods.quarters_are_consecutive(sorted(dates)):
        return None, None
    return float(sum(series[d] for d in dates)), dates[0]


def sec_roic(st: dict, end: dt.date | None = None):
    """(ROIC %, flags, period end). Rule-34 definition on GAAP figures, TTM to
    `end` (default the newest quarter)."""
    op_q = st["q"].get("operating_income") or {}
    if not op_q:
        return None, ["no OperatingIncomeLoss in SEC facts"], None
    op, end = last_four(op_q, end or max(op_q))
    if op is None:
        return None, ["SEC: no four consecutive quarters of operating income"], None
    pretax, _ = last_four(st["q"].get("pretax") or {}, end)
    tax, _ = last_four(st["q"].get("tax") or {}, end)
    flags = [f"SEC 10-Q/10-K, TTM to {end}; GAAP operating income (Yahoo's line "
             "adds back special charges)"]
    if pretax is None and tax is not None:
        # Some filers tag pretax income in the 10-K only (INTU); net income +
        # income tax is the same figure for the tax-rate calculation.
        ni, _ = last_four(st["q"].get("net_income") or {}, end)
        if ni is not None:
            pretax = ni + tax
            flags.append("pretax income derived as net income + income tax")
    rate, defaulted = roic.effective_tax_rate(pretax, tax)
    if defaulted:
        flags.append(f"effective tax rate unusable/clamped -> {rate:.0%}")
    ta = st["i"].get("assets", {}).get(end)
    cl = st["i"].get("current_liabilities", {}).get(end)
    if ta is None or cl is None:
        return None, flags + [f"SEC: no total assets / current liabilities at {end}"], end
    ic = ta - cl
    if ic <= 0:
        return None, flags + [f"capital employed non-positive ({ic/1e6:,.0f}M)"], end
    return round(op * (1 - rate) / ic * 100, 2), flags, end


def sec_fcf(st: dict):
    """(FCF, note, period end, kind, revenue over the same period or None)."""
    def rows(part):
        return {fcf_source.OCF: st[part].get("ocf") or {},
                fcf_source.CAPEX_ROWS[0]: st[part].get("capex") or {}}
    fcf, note, end, kind = fcf_source.fcf_detail(rows("q"), rows("a"))
    rev = None
    if kind == fcf_source.QUARTERLY:
        rev, _ = last_four(st["q"].get("revenue") or {}, end)
    elif kind == fcf_source.ANNUAL:
        rev = (st["a"].get("revenue") or {}).get(end)
    tag = st["tag"].get("capex")
    return fcf, f"SEC {note} (capex concept {tag})", end, kind, rev


def sec_eps_yoy(st: dict, most_recent_quarter: dt.date | None):
    """eps_growth.eps_yoy_fallback on SEC quarterly net income."""
    return eps_growth.eps_yoy_fallback(st["q"].get("net_income") or {},
                                       most_recent_quarter,
                                       source=f"SEC 10-Q/10-K facts ({st['tag'].get('net_income')})")


def sec_rev_cagr(st: dict):
    """(CAGR %, notes, newest fiscal-year end) from SEC annual revenue."""
    rev = st["a"].get("revenue") or {}
    if not rev:
        return None, ["SEC: no annual revenue"], None
    v, notes = revenue_cagr.rev_3y_cagr(rev, {})
    return v, notes, max(rev)


def sec_debt_cash(st: dict):
    """(debt, cash, as-of, note) from the newest balance sheet. Basis differs
    from Yahoo's (leases excluded), so only used where Yahoo has nothing."""
    i = st["i"]
    dates = [max(s) for s in (i.get("assets"), i.get("cash")) if s]
    if not dates:
        return None, None, None, "SEC: no balance sheet"
    asof = max(dates)

    def at(name):
        return (i.get(name) or {}).get(asof)

    cash = at("cash")
    if cash is not None and at("short_term_investments") is not None:
        cash += at("short_term_investments")
    stb = at("short_term_borrowings") or 0.0
    if at("debt_total") is not None:
        debt = at("debt_total") + stb
    elif at("debt_noncurrent") is not None or at("debt_current") is not None:
        debt = (at("debt_noncurrent") or 0.0) + (at("debt_current") or 0.0) + stb
    elif at("short_term_borrowings") is not None:
        debt = stb
    else:
        debt = None
    return debt, cash, asof, (f"SEC balance sheet {asof} (debt excludes leases; "
                              f"cash includes short-term investments)")


# --------------------------------------------------------------------------
# Choosing a source: newer, and reconciled on the period both sources cover
# --------------------------------------------------------------------------
#
# companyfacts carries only standard us-gaap concepts. A company that files
# part of a line under its own extension concept is invisible to it: SHAZ's
# GPU purchases ($281M in Q2 2026 per Yahoo) are not in
# PaymentsToAcquirePropertyPlantAndEquipment ($12M). So before SEC replaces a
# Yahoo value with a newer one, the same calculation on SEC facts must
# reproduce Yahoo's value for Yahoo's own period. If it cannot, Yahoo is kept
# (a quarter old, flagged) rather than a wrong current figure written.

MATCH_DAYS = 20             # Yahoo dates are month-end normalized
FCF_TOL = 0.10              # of the larger |FCF|, floor 1% of TTM revenue
ROIC_TOL = (2.0, 0.20)      # points, or share of |Yahoo ROIC|: GAAP vs adjusted
REV_TOL = 0.02              # annual revenue, same fiscal year
NI_TOL, NI_FLOOR = 0.05, 1e6  # quarterly net income, same quarter (floor: units)


def _match(series: dict, target: dt.date | None, days: int = MATCH_DAYS):
    if not series or target is None:
        return None
    best = min(series, key=lambda d: abs((d - target).days))
    return best if abs((best - target).days) <= days else None


def _close(a: float, b: float, rel: float, floor: float = 0.0) -> bool:
    return abs(a - b) <= max(rel * max(abs(a), abs(b)), floor)


def _decision(value=None, note="", end=None, rev=None, use=False):
    return {"use": use, "value": value, "note": note, "end": end, "rev": rev}


def fcf_window(st: dict, end: dt.date, kind: str | None):
    """SEC FCF for the period Yahoo's figure covers, or None."""
    if kind == fcf_source.QUARTERLY:
        e = _match(st["q"].get("ocf") or {}, end)
        ocf, _ = last_four(st["q"].get("ocf") or {}, e) if e else (None, None)
        cap, _ = last_four(st["q"].get("capex") or {}, e) if e else (None, None)
    else:
        e = _match(st["a"].get("ocf") or {}, end, days=45)
        ocf = (st["a"].get("ocf") or {}).get(e)
        cap = (st["a"].get("capex") or {}).get(e)
    if ocf is None or cap is None:
        return None
    return ocf - abs(cap)


def choose_fcf(y_fcf, y_end, y_kind, st: dict) -> dict:
    s_fcf, s_note, s_end, _kind, s_rev = sec_fcf(st)
    if not prefer_sec(y_fcf, y_end, s_fcf, s_end):
        return _decision(note=f"SEC FCF not newer (SEC to {s_end})")
    if y_fcf is not None:
        check = fcf_window(st, y_end, y_kind)
        if check is None or not _close(check, y_fcf, FCF_TOL, 0.01 * abs(s_rev or 0)):
            got = "n/a" if check is None else f"{check / 1e6:,.0f}M"
            return _decision(note=(
                f"FCF to {s_end} NOT used: for Yahoo's period to {y_end} SEC "
                f"gives {got} vs Yahoo {y_fcf / 1e6:,.0f}M, so SEC's standard "
                "concepts miss part of the cash flow (likely a company-specific "
                "capex line) — kept Yahoo"))
        s_note += f"; reconciles with Yahoo to {y_end}"
    else:
        s_note += "; Yahoo had no FCF, so not reconciled"
    return _decision(s_fcf, s_note, s_end, s_rev, use=True)


def choose_roic(y_roic, y_end, st: dict) -> dict:
    s_val, s_flags, s_end = sec_roic(st)
    if not prefer_sec(y_roic, y_end, s_val, s_end):
        return _decision(note=f"SEC ROIC not newer or not computable ({'; '.join(s_flags)})")
    note = "; ".join(s_flags)
    if y_roic is not None:
        e = _match(st["q"].get("operating_income") or {}, y_end)
        check = sec_roic(st, e)[0] if e else None
        if check is None or not _close(check, y_roic, ROIC_TOL[1], ROIC_TOL[0]):
            return _decision(note=(
                f"ROIC to {s_end} NOT used: for Yahoo's period to {y_end} SEC "
                f"gives {check} vs Yahoo {y_roic} — kept Yahoo"))
        note += f"; reconciles with Yahoo to {y_end} ({check} vs {y_roic})"
    else:
        note += "; Yahoo had no ROIC, so not reconciled"
    return _decision(s_val, note, s_end, use=True)


def choose_rev_cagr(y_cagr, y_revenue: dict, st: dict) -> dict:
    """y_revenue: Yahoo's {fiscal-year date: revenue}, blanks allowed."""
    y_clean = {fcf_source._as_date(k): float(v) for k, v in (y_revenue or {}).items()
               if not _isblank(v)}
    y_fy = max(y_clean) if y_clean else None
    s_cagr, s_notes, s_fy = sec_rev_cagr(st)
    if not prefer_sec(y_cagr, y_fy, s_cagr, s_fy):
        return _decision(note="SEC revenue CAGR not newer")
    if y_fy is not None:
        e = _match(st["a"].get("revenue") or {}, y_fy, days=45)
        check = (st["a"].get("revenue") or {}).get(e)
        if check is None or not _close(check, y_clean[y_fy], REV_TOL):
            return _decision(note=(
                f"revenue CAGR NOT used: fiscal year {y_fy} revenue SEC "
                f"{check} vs Yahoo {y_clean[y_fy]} — kept Yahoo"))
    note = (f"SEC 10-K fiscal year {s_fy} (Yahoo's newest is {y_fy})"
            + (f"; {'; '.join(s_notes)}" if s_notes else ""))
    return _decision(s_cagr, note, s_fy, use=True)


def choose_eps_yoy(y_net_income: dict, latest: dt.date | None, st: dict) -> dict:
    """EPS YoY from SEC net income, used only where Yahoo's statements can't
    answer (eps_growth NO_DATA). Net income is checked on the newest quarter
    both sources hold."""
    v, code, note = sec_eps_yoy(st, latest)
    if code == eps_growth.NO_DATA:
        return _decision(note=note)
    ni = st["q"].get("net_income") or {}
    y = {fcf_source._as_date(k): float(x) for k, x in (y_net_income or {}).items()
         if not _isblank(x)}
    for d in sorted(y, reverse=True):
        e = _match(ni, d)
        if e is not None:
            if not _close(ni[e], y[d], NI_TOL, NI_FLOOR):
                return _decision(note=(
                    f"EPS YoY NOT used: quarter {d} SEC {ni[e] / 1e6:,.1f}M vs "
                    f"Yahoo {y[d] / 1e6:,.1f}M — kept the data gap"))
            break
    out = _decision(v, note, use=True)
    out["code"] = code
    return out


def _isblank(v) -> bool:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return True
    return f != f


# --------------------------------------------------------------------------
# Network (lazy) — one companyfacts request per name, memoized per process
# --------------------------------------------------------------------------

def fetch_companyfacts(ticker: str) -> tuple[dict | None, str]:
    if "." in ticker:
        return None, "foreign local listing — no SEC filings"
    from common import cik_for, sec_get       # lazy: requests is not in CI
    try:
        cik = cik_for(ticker)
    except Exception as e:                     # noqa: BLE001
        return None, f"CIK lookup failed ({e})"
    if not cik:
        return None, "no SEC CIK"
    try:
        return sec_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                       host_data_sec=True).json(), "ok"
    except Exception as e:                     # noqa: BLE001
        return None, f"companyfacts fetch failed ({e})"


class SecContext:
    """Fetch-once holder. `get()` returns parsed statements or None; `note`
    says why not. The fetcher is injectable for tests."""

    def __init__(self, ticker: str, currency: str | None, fetcher=fetch_companyfacts):
        self.ticker, self.currency, self._fetcher = ticker, currency, fetcher
        self._done, self._st, self.note = False, None, "not fetched"

    @property
    def fetched(self) -> bool:
        return self._done

    def get(self):
        if not self._done:
            self._done = True
            facts, self.note = self._fetcher(self.ticker)
            if facts is not None:
                self._st, self.note = statements(facts, self.currency)
        return self._st

    def newest_quarter(self) -> dt.date | None:
        st = self.get()
        if not st:
            return None
        ends = [max(s) for s in (st["q"].get("revenue"), st["q"].get("ocf"),
                                 st["q"].get("operating_income")) if s]
        return max(ends) if ends else None
