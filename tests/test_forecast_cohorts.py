from openpyxl import Workbook
import forecast_cohorts as c


def _scoring(tmp_path, names_layers):
    wb = Workbook()
    ws = wb.active
    ws.title = "Watchlist"
    ws.append(["Ticker", "Company", "Layer"])
    for t, lay in names_layers:
        ws.append([t, f"{t} Inc", lay])
    p = tmp_path / "scoring.xlsx"
    wb.save(p)
    return p


def test_cohort_groups_by_layer_and_excludes_self(tmp_path):
    # 7 layer-06 names so AVGO has 6 peers (>= MIN_PEERS) and gets a real cohort
    p = _scoring(tmp_path, [("AVGO", "06 Silicon"), ("NVDA", "06 Silicon"),
                            ("MU", "06 Silicon"), ("ALAB", "06 Silicon"),
                            ("SNDK", "06 Silicon"), ("WDC", "06 Silicon"),
                            ("TXN", "06 Silicon"), ("FIX", "03 DC")])
    layer, rule = c.build_frozen_cohort("AVGO", scoring_path=p)
    assert layer == "06"
    assert rule["benchmark"] == "layer_cohort_ew"
    assert "AVGO" not in rule["constituents"]
    assert rule["constituents"] == ["ALAB", "MU", "NVDA", "SNDK", "TXN", "WDC"]  # sorted, self excluded
    assert rule["horizon_td"] == 63


def test_four_peer_layer_forms_cohort(tmp_path):
    # real Layer-05 shape: 5 names -> TSM has 4 peers, which meets MIN_PEERS=4
    p = _scoring(tmp_path, [("TSM", "05 Fabs"), ("INTC", "05 Fabs"), ("GFS", "05 Fabs"),
                            ("TSEM", "05 Fabs"), ("UMC", "05 Fabs")])
    layer, rule = c.build_frozen_cohort("TSM", scoring_path=p)
    assert layer == "05"
    assert rule["benchmark"] == "layer_cohort_ew"
    assert rule["constituents"] == ["GFS", "INTC", "TSEM", "UMC"]


def test_thin_layer_falls_back_to_smh(tmp_path):
    # 3 names -> TSM has only 2 peers (< MIN_PEERS) -> SMH fallback
    p = _scoring(tmp_path, [("TSM", "05 Fabs"), ("UMC", "05 Fabs"), ("GFS", "05 Fabs")])
    layer, rule = c.build_frozen_cohort("TSM", scoring_path=p)
    assert layer == "05"
    assert rule["benchmark"] == "SMH"
    assert rule["constituents"] == ["SMH"]
