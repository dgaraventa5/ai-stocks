import datetime as dt
import pytest
import forecast_store as store

TODAY = dt.date(2026, 6, 26)


def _proposal(**over):
    base = dict(
        ticker="AVGO", layer="06", dimension="momentum.rel_strength",
        rating_value=4, template="REL_STRENGTH_1Q",
        claim="AVGO outperforms its Layer-06 peers over 63 trading days",
        probability=0.65, resolution_date="2026-09-29",
        resolution_rule={"benchmark": "layer_cohort_ew",
                         "constituents": ["NVDA", "MU"], "horizon_td": 63},
        status="open",
    )
    base.update(over)
    return base


def test_append_creation_forces_today_and_assigns_id(tmp_path):
    p = tmp_path / "f.jsonl"
    snap = store.append_creation(_proposal(), path=p, today=TODAY)
    assert snap["created_date"] == "2026-06-26"
    assert snap["id"] == "fc_2026-06-26_AVGO_relstr_001"
    assert snap["status"] == "open" and snap["outcome"] is None
    # second forecast same day/ticker/template increments the sequence
    snap2 = store.append_creation(_proposal(), path=p, today=TODAY)
    assert snap2["id"] == "fc_2026-06-26_AVGO_relstr_002"


def test_append_creation_rejects_lookahead(tmp_path):
    p = tmp_path / "f.jsonl"
    with pytest.raises(store.ForecastError, match="look-ahead"):
        store.append_creation(_proposal(resolution_date="2026-06-26"), path=p, today=TODAY)


def test_append_creation_rejects_bad_probability(tmp_path):
    p = tmp_path / "f.jsonl"
    with pytest.raises(store.ForecastError, match="probability"):
        store.append_creation(_proposal(probability=1.0), path=p, today=TODAY)


def test_materialize_last_wins_and_open_excludes_resolved(tmp_path):
    p = tmp_path / "f.jsonl"
    snap = store.append_creation(_proposal(), path=p, today=TODAY)
    assert [f["id"] for f in store.open_forecasts(p)] == [snap["id"]]
    resolved = dict(snap, status="resolved", outcome=1,
                    resolved_date="2026-09-30", resolution_evidence="ev", resolver_confidence="auto")
    store.append_resolution(resolved, path=p)
    assert store.materialize(p)[snap["id"]]["status"] == "resolved"
    assert store.open_forecasts(p) == []


def test_append_resolution_rejects_immutable_change(tmp_path):
    p = tmp_path / "f.jsonl"
    snap = store.append_creation(_proposal(), path=p, today=TODAY)
    tampered = dict(snap, status="resolved", outcome=1, probability=0.99,
                    resolved_date="2026-09-30", resolution_evidence="ev", resolver_confidence="auto")
    with pytest.raises(store.ForecastError, match="immutable field probability"):
        store.append_resolution(tampered, path=p)
