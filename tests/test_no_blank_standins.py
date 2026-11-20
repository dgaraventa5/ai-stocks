"""Stand-ins instead of blanked metrics (Dom 2026-11-20: "i don't want blanked
metrics"). A metric that is undefined because the business fails its test
scores a band; only a true data gap stays blank. Offline, stdlib + openpyxl."""
import datetime as dt
import sys
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import rebuild_watchlist_formulas as rwf  # noqa: E402
import recalc_watchlist as rw  # noqa: E402
import revenue_cagr as rc  # noqa: E402
import reverse_dcf as rd  # noqa: E402

D = dt.date


# ---- reverse-DCF Value term ----------------------------------------------------

def test_negative_fcf_scores_the_bottom_band_not_blank():
    # AMZN 2026-11-20: TTM FCF negative, EV/FCF absent; Value had risen 58 -> 69
    assert rd.value_term(None, -1.7, 12.0) == rd.NEG_FCF_SCORE == 15.0


def test_negative_ev_on_positive_fcf_scores_the_top_band():
    assert rd.value_term(-3.0, 4.0, 12.0) == rd.NEG_EV_SCORE


def test_no_multiple_and_no_fcf_yield_is_a_data_gap():
    assert rd.value_term(None, None, 12.0) is None


def test_missing_cagr_uses_revenue_yoy():
    assert rd.value_term(20.0, 5.0, None, rev_yoy_pct=30.0) == \
        rd.reverse_dcf_score(20.0, 30.0, rev_yoy_pct=30.0)


def test_normal_multiple_unchanged():
    assert rd.value_term(20.0, 5.0, 8.0) == rd.reverse_dcf_score(20.0, 8.0)


# ---- PEG -----------------------------------------------------------------------

def _row(fwd_pe, eps_yoy):
    wb = Workbook()
    ws = wb.active
    ws.cell(2, 1).value = "XYZ"
    ws.cell(2, 5).value = fwd_pe
    ws.cell(2, 18).value = eps_yoy
    return rw._read_raw(ws, 2)["peg"]


def test_peg_stand_in_for_shrinking_eps_or_forecast_loss():
    assert _row(20.0, -100.0) == rw.PEG_STANDIN          # loss quarter stand-in
    assert _row(20.0, 0.0) == rw.PEG_STANDIN
    assert _row(-15.0, 30.0) == rw.PEG_STANDIN           # forecast loss
    assert rw.score_peg(rw.PEG_STANDIN) == 15            # bottom band


def test_peg_normal_and_data_gap():
    assert _row(20.0, 40.0) == 0.5
    assert _row(None, 40.0) is None
    assert _row(20.0, None) is None


def test_peg_formula_and_recalc_agree_on_the_stand_in():
    assert rwf.PEG_STANDIN == rw.PEG_STANDIN
    f = rwf.PEG.format(r=7)
    assert f == '=IF(OR(E7="",R7=""),"",IF(OR(R7<=0,E7<0),99,E7/R7))'


# ---- revenue YoY fallback ------------------------------------------------------

Q = {D(2026, 9, 30): 1.86e6, D(2026, 6, 30): 1.21e6, D(2026, 3, 31): 0.0,
     D(2025, 12, 31): 0.0, D(2025, 9, 30): 0.0}


def test_rev_yoy_from_zero_is_top_band():
    # OKLO 2026-11-20: first revenue this year, none a year ago
    v, why = rc.rev_yoy_fallback(Q, D(2026, 9, 30))
    assert v == rc.FROM_ZERO_VALUE and "from or to zero" in why


def test_rev_yoy_pre_revenue_and_computed():
    v, _ = rc.rev_yoy_fallback({**Q, D(2025, 3, 31): 0.0}, D(2026, 3, 31))
    assert v == rc.NO_REVENUE_VALUE
    v, why = rc.rev_yoy_fallback({D(2026, 9, 30): 120.0, D(2025, 9, 30): 100.0},
                                 D(2026, 9, 30))
    assert v == 20.0 and "computed" in why


def test_rev_yoy_lagging_statement_is_a_data_gap():
    v, why = rc.rev_yoy_fallback(Q, D(2026, 12, 31))
    assert v is None and "behind" in why
