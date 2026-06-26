import datetime as dt
import forecast_store as store
import calibration_report as cr

CREATED = dt.date(2026, 6, 26)


def _resolved(path, ticker, layer, prob, outcome):
    snap = dict(ticker=ticker, layer=layer, dimension="momentum.rel_strength",
                rating_value=4, template="REL_STRENGTH_1Q", claim="c",
                probability=prob, resolution_date="2026-09-29",
                resolution_rule={"benchmark": "SMH", "constituents": ["SMH"], "horizon_td": 63},
                status="open")
    created = store.append_creation(snap, path=path, today=CREATED)
    store.append_resolution(dict(created, status="resolved", outcome=outcome,
                                 resolved_date="2026-09-30", resolution_evidence="ev",
                                 resolver_confidence="auto"), path=path)


def test_build_report_has_sections_and_void_rate(tmp_path):
    p = tmp_path / "f.jsonl"
    _resolved(p, "AVGO", "06", 0.8, 1)
    _resolved(p, "NVDA", "06", 0.2, 0)
    _resolved(p, "APP", "10", 0.6, 0)
    report = cr.build_report(dt.date(2026, 10, 1), path=p)
    assert "# Forecast Calibration Report" in report
    assert "### Overall" in report and "## By dimension" in report and "## By layer" in report
    assert "momentum.rel_strength" in report
    assert "Layer 06" in report and "Layer 10" in report
    assert "Brier" in report and "BSS" in report
    assert "void rate: 0%" in report   # nothing in needs_review/void


def test_empty_log_is_graceful(tmp_path):
    p = tmp_path / "f.jsonl"
    report = cr.build_report(dt.date(2026, 10, 1), path=p)
    assert "No forecasts logged" in report


def test_small_n_warns_not_to_overinterpret(tmp_path):
    p = tmp_path / "f.jsonl"
    _resolved(p, "AVGO", "06", 0.8, 1)
    report = cr.build_report(dt.date(2026, 10, 1), path=p)
    assert "do not over-interpret" in report
