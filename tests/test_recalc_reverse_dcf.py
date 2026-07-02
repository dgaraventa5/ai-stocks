"""P2 integration: the reverse-DCF mispricing score is a 6th Value sub-metric.

Tests recalc_watchlist._assemble directly (no network/workbook) — a cheap EV/FCF
name gets a reverse-DCF lift to Value; when EV/FCF is absent the term drops out
and Value is the original five-metric average.
"""
import recalc_watchlist as rc

_MS = dict(ev=60.0, fcf_yield=60.0, ps=60.0, roic=60.0, gm=60.0, fcf_mgn=60.0)
_W = {'Value': 0.2, 'Quality': 0.2, 'Growth': 0.15, 'AI': 0.2,
      'Momentum': 0.1, 'Risk': 0.15}


def _row(ev_fcf, rev_cagr=8.0):
    return dict(ticker='X', layer='06 AI Compute Silicon / GPUs', row=2,
                ev_fcf=ev_fcf, fwd_pe=20.0, peg=1.0, nd_eb=1.0,
                rev_cagr=rev_cagr, rev_yoy=20.0, eps_yoy=20.0,
                ai_inputs=[4, 4, 4, 4, 4], mom_inputs=[3, 3, 3], dma_pct=60.0,
                risk_inputs=[4, 4, 4, 4, 4])


def test_reverse_dcf_lifts_value_for_cheap_name():
    cheap = rc._assemble(_row(ev_fcf=5.0), _MS, _W)     # cheap -> high revDCF score
    blank = rc._assemble(_row(ev_fcf=None), _MS, _W)     # no revDCF term
    assert cheap['Value'] > blank['Value']


def test_reverse_dcf_penalizes_rich_name():
    rich = rc._assemble(_row(ev_fcf=60.0), _MS, _W)      # rich -> low revDCF score
    blank = rc._assemble(_row(ev_fcf=None), _MS, _W)
    assert rich['Value'] < blank['Value']


def test_value_is_five_metrics_when_reverse_dcf_absent():
    blank = rc._assemble(_row(ev_fcf=None), _MS, _W)
    expected = rc.avg_nonnull([rc.score_fwd_pe(20.0), 60.0, 60.0, 60.0,
                               rc.score_peg(1.0)])
    assert abs(blank['Value'] - expected) < 1e-9
