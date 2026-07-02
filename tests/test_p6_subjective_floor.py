"""P6 (rule 22): AI Thesis and Risk map ratings via (mean-1)*25, so a genuine
all-1 rating floors at 0 instead of the old 20. 1->0, 3->50, 5->100."""
import recalc_watchlist as rc

_MS = dict(ev=60.0, fcf_yield=60.0, ps=60.0, roic=60.0, gm=60.0, fcf_mgn=60.0)
_W = {'Value': 0.2, 'Quality': 0.2, 'Growth': 0.15, 'AI': 0.2,
      'Momentum': 0.1, 'Risk': 0.15}


def _row(ai, risk):
    return dict(ticker='X', layer='06 AI Compute Silicon / GPUs', row=2,
                ev_fcf=None, fwd_pe=20.0, peg=1.0, nd_eb=1.0, rev_cagr=8.0,
                rev_yoy=20.0, eps_yoy=20.0, ai_inputs=[ai] * 5,
                mom_inputs=[3, 3, 3], dma_pct=60.0, risk_inputs=[risk] * 5)


def test_ai_thesis_all_ones_now_floors_at_zero():
    assert rc._assemble(_row(1, 3), _MS, _W)['AI'] == 0.0


def test_ai_thesis_all_threes_is_fifty():
    assert rc._assemble(_row(3, 3), _MS, _W)['AI'] == 50.0


def test_ai_thesis_all_fives_is_one_hundred():
    assert rc._assemble(_row(5, 3), _MS, _W)['AI'] == 100.0


def test_risk_all_ones_floors_at_zero():
    assert rc._assemble(_row(3, 1), _MS, _W)['Risk'] == 0.0


def test_risk_all_fives_is_one_hundred():
    assert rc._assemble(_row(3, 5), _MS, _W)['Risk'] == 100.0
