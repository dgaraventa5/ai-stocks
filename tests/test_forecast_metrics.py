import forecast_metrics as m


def test_brier_known_value():
    # all p=0.5, half outcomes 1 -> every term 0.25
    assert abs(m.brier([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0]) - 0.25) < 1e-12


def test_murphy_identity_holds_for_discrete_forecasts():
    # forecasts placed at distinct bin centers -> zero within-bin spread -> exact identity
    ps = [0.2, 0.2, 0.8, 0.8]
    outs = [0, 0, 1, 1]
    d = m.murphy_decomposition(ps, outs)
    assert abs((d["REL"] - d["RES"] + d["UNC"]) - m.brier(ps, outs)) < 1e-12
    assert abs(d["BS_reconstructed"] - m.brier(ps, outs)) < 1e-12


def test_bss_sign_and_undefined():
    # a discriminating forecaster beats the base-rate null
    assert m.brier_skill_score([0.2, 0.2, 0.8, 0.8], [0, 0, 1, 1]) > 0
    # all-same outcome -> UNC=0 -> undefined
    assert m.brier_skill_score([0.6, 0.6], [1, 1]) is None


def test_log_loss_clips_confident_miss():
    # p=1.0 on a miss would be +inf without clipping; clipping keeps it finite
    assert m.log_loss([1.0], [0]) < 20.0


def test_reliability_table_bins_and_closed_right():
    rows = m.reliability_table([0.05, 1.0], [0, 1])
    assert rows[0]["n"] == 1 and rows[0]["p_bar"] == 0.05   # first bin
    assert rows[-1]["n"] == 1 and rows[-1]["o_bar"] == 1.0  # p==1.0 lands in last bin
