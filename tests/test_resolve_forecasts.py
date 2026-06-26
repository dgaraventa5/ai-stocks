import datetime as dt
import forecast_store as store
import resolve_forecasts as rf

CREATED = dt.date(2026, 6, 26)


def _seed_open(path):
    snap = dict(ticker="AVGO", layer="06", dimension="momentum.rel_strength",
                rating_value=4, template="REL_STRENGTH_1Q",
                claim="AVGO vs Layer-06 over 3 td", probability=0.65,
                resolution_date="2026-07-08",
                resolution_rule={"benchmark": "layer_cohort_ew",
                                 "constituents": ["NVDA", "MU"], "horizon_td": 3},
                status="open")
    return store.append_creation(snap, path=path, today=CREATED)


def _ramp(start, step, n=10):
    return {CREATED + dt.timedelta(days=i): start * (1 + step) ** i for i in range(n)}


def test_resolve_due_appends_resolution(tmp_path):
    p = tmp_path / "f.jsonl"
    created = _seed_open(p)
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.0), "MU": _ramp(100, 0.0)}
    loader = lambda t, s: table[t]
    results = rf.resolve_due(dt.date(2026, 8, 1), loader, dry_run=False, path=p)
    assert len(results) == 1 and results[0]["outcome"] == 1
    # the resolution snapshot was appended; state is now resolved, no longer open
    assert store.materialize(p)[created["id"]]["status"] == "resolved"
    assert store.open_forecasts(p) == []


def test_dry_run_writes_nothing(tmp_path):
    p = tmp_path / "f.jsonl"
    _seed_open(p)
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.0), "MU": _ramp(100, 0.0)}
    rf.resolve_due(dt.date(2026, 8, 1), lambda t, s: table[t], dry_run=True, path=p)
    assert len(store.open_forecasts(p)) == 1   # still open
