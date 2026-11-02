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


# ---- transient price failures ----------------------------------------------
RES = dt.date(2026, 7, 8)                      # resolution_date of _seed_open
IN_GRACE = RES + dt.timedelta(days=rf.GRACE_DAYS)
PAST_GRACE = RES + dt.timedelta(days=rf.GRACE_DAYS + 1)


def _peers_down(t, s):
    # the name itself prices, every peer comes back empty (a brief throttle)
    return _ramp(100, 0.05) if t == "AVGO" else {}


def _outage(t, s):
    return {}


def test_degraded_cohort_inside_grace_appends_nothing(tmp_path):
    p = tmp_path / "f.jsonl"
    _seed_open(p)
    before = p.read_text()
    ungraded = []
    results = rf.resolve_due(IN_GRACE, _peers_down, dry_run=False, path=p,
                             ungraded=ungraded)
    assert results == [] and p.read_text() == before
    assert len(store.open_forecasts(p)) == 1 and len(ungraded) == 1


def test_degraded_cohort_past_grace_still_needs_review(tmp_path):
    p = tmp_path / "f.jsonl"
    created = _seed_open(p)
    results = rf.resolve_due(PAST_GRACE, _peers_down, dry_run=False, path=p)
    assert [r["status"] for r in results] == ["needs_review"]
    assert store.materialize(p)[created["id"]]["status"] == "needs_review"


def test_ungraded_argument_is_optional(tmp_path):
    p = tmp_path / "f.jsonl"
    _seed_open(p)
    assert rf.resolve_due(IN_GRACE, _peers_down, dry_run=False, path=p) == []


def _main(monkeypatch, path, today, loader):
    real = rf.resolve_due
    monkeypatch.setattr(rf, "resolve_due", lambda *a, **k: real(*a, path=path, **k))
    monkeypatch.setattr(rf, "yfinance_price_loader", loader)
    monkeypatch.setattr(rf, "_today", lambda: today)
    monkeypatch.setattr("sys.argv", ["resolve_forecasts.py"])
    return rf.main()


def test_full_outage_prints_ungraded_count_and_exits_nonzero(tmp_path, monkeypatch, capsys):
    p = tmp_path / "f.jsonl"
    _seed_open(p)
    assert _main(monkeypatch, p, IN_GRACE, _outage) == 1
    assert "1 could not be graded" in capsys.readouterr().out


def test_clean_run_exits_zero(tmp_path, monkeypatch, capsys):
    p = tmp_path / "f.jsonl"
    _seed_open(p)
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.0), "MU": _ramp(100, 0.0)}
    assert _main(monkeypatch, p, dt.date(2026, 8, 1), lambda t, s: table[t]) == 0
    assert "1 resolved" in capsys.readouterr().out


def test_nothing_due_exits_zero(tmp_path, monkeypatch):
    p = tmp_path / "f.jsonl"
    _seed_open(p)
    assert _main(monkeypatch, p, dt.date(2026, 6, 27), _outage) == 0


def _seed_two(path):
    _seed_open(path)
    snap = dict(ticker="TSM", layer="05", dimension="momentum.rel_strength",
                rating_value=4, template="REL_STRENGTH_1Q",
                claim="TSM vs Layer-05 over 3 td", probability=0.65,
                resolution_date="2026-07-08",
                resolution_rule={"benchmark": "layer_cohort_ew",
                                 "constituents": ["NVDA", "MU"], "horizon_td": 3},
                status="open")
    store.append_creation(snap, path=path, today=CREATED)


def test_outage_past_grace_is_a_failed_run_not_a_success(tmp_path, monkeypatch, capsys):
    p = tmp_path / "f.jsonl"
    _seed_two(p)
    assert _main(monkeypatch, p, PAST_GRACE, _outage) == 1
    assert "0 resolved, 2 need review" in capsys.readouterr().out


def test_one_graded_among_failures_is_a_failed_run(tmp_path, monkeypatch, capsys):
    p = tmp_path / "f.jsonl"
    _seed_two(p)
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.0), "MU": _ramp(100, 0.0)}
    assert _main(monkeypatch, p, IN_GRACE, lambda t, s: table.get(t, {})) == 1
    assert "1 resolved, 0 need review, 1 could not be graded" in capsys.readouterr().out


def test_throttle_that_raises_is_counted_not_a_crash(tmp_path, monkeypatch, capsys):
    p = tmp_path / "f.jsonl"
    _seed_two(p)
    before = p.read_text()

    def raises(t, s):
        raise RuntimeError("Too Many Requests")

    assert _main(monkeypatch, p, IN_GRACE, raises) == 1
    assert "2 could not be graded" in capsys.readouterr().out
    assert p.read_text() == before


def test_throttle_partway_keeps_what_was_graded(tmp_path, monkeypatch):
    p = tmp_path / "f.jsonl"
    _seed_two(p)
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.0), "MU": _ramp(100, 0.0)}

    def loader(t, s):
        if t not in table:
            raise RuntimeError("Too Many Requests")
        return table[t]

    assert _main(monkeypatch, p, IN_GRACE, loader) == 1
    assert len(store.open_forecasts(p)) == 1
    assert [f["ticker"] for f in store.open_forecasts(p)] == ["TSM"]


def test_due_forecast_with_no_resolver_is_a_failed_run(tmp_path, monkeypatch, capsys):
    p = tmp_path / "f.jsonl"
    snap = dict(ticker="AVGO", layer="06", dimension="momentum.rel_strength",
                rating_value=4, template="NOT_BUILT_YET",
                claim="AVGO", probability=0.65, resolution_date="2026-07-08",
                resolution_rule={}, status="open")
    store.append_creation(snap, path=p, today=CREATED)
    assert _main(monkeypatch, p, IN_GRACE, _outage) == 1
    assert "1 could not be graded" in capsys.readouterr().out
