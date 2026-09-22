import json

import scheduled_ops as ops


def test_weekly_rating_report_is_bounded_and_order_independent():
    rows = [
        {"tkr": "BBB", "layer": "02", "gate": False, "stale": True,
         "age": 95, "backing": "brief 95d"},
        {"tkr": "AAA", "layer": "01", "gate": True, "stale": False,
         "age": None, "backing": "NONE"},
        {"tkr": "CCC", "layer": "03", "gate": False, "stale": True,
         "age": 120, "backing": "brief 120d"},
    ]

    report = ops.weekly_rating_report(rows, limit=2)
    reordered = ops.weekly_rating_report(list(reversed(rows)), limit=2)

    assert [item["ticker"] for item in report["items"]] == ["AAA", "CCC"]
    assert report["overflow_count"] == 1
    assert report["report_only"] is True
    assert report["dedup_key"] == reordered["dedup_key"]


def test_earnings_report_combines_phases_and_bounds_tickers():
    detector = {
        "briefing_due": [
            {"ticker": "BBB", "report_date": "2026-09-21", "session": "AMC"},
            {"ticker": "AAA", "report_date": "2026-09-21", "session": "BMO"},
        ],
        "rescore_due": [
            {"ticker": "CCC", "report_date": "2026-09-20", "session": "AMC"},
            {"ticker": "AAA", "report_date": "2026-09-21", "session": "BMO"},
        ],
        "flagged": {"DDD": "lookup failed"},
        "scope_size": 25,
    }

    report = ops.earnings_report(detector, limit=2)

    assert [item["ticker"] for item in report["items"]] == ["CCC", "AAA"]
    assert report["items"][1]["phases"] == ["briefing", "rescore"]
    assert report["overflow_count"] == 1
    assert report["flags"] == [{"ticker": "DDD", "message": "lookup failed"}]
    assert report["report_only"] is True


def test_gate_report_deduplicates_and_updates_local_heartbeat(tmp_path):
    state_path = tmp_path / "state.json"
    report = ops.weekly_rating_report([
        {"tkr": "AAA", "layer": "01", "gate": True, "stale": False,
         "age": None, "backing": "NONE"},
    ])

    first = ops.gate_report("weekly-rating", report, state_path,
                            now="2026-09-22T10:00:00Z")
    second = ops.gate_report("weekly-rating", report, state_path,
                             now="2026-09-22T10:05:00Z")
    state = ops.load_local_state(state_path)

    assert first == report
    assert second is None
    assert state["jobs"]["weekly-rating"]["last_success_at"] == (
        "2026-09-22T10:05:00Z")
    assert state["jobs"]["weekly-rating"]["dedup_key"] == report["dedup_key"]


def test_health_report_alerts_on_stale_jobs_failed_checks_and_conflicts():
    state = {
        "schema_version": 1,
        "jobs": {
            "weekly-rating": {"last_success_at": "2026-09-01T10:00:00Z"},
            "earnings-sentinel": {"last_success_at": "2026-09-21T22:30:00Z"},
        },
    }
    prs = [{
        "number": 80,
        "headRefName": "automation/performance-series",
        "mergeStateStatus": "DIRTY",
        "updatedAt": "2026-09-21T00:00:00Z",
        "statusCheckRollup": [{"name": "test", "conclusion": "FAILURE"}],
    }]

    report = ops.health_report(
        state,
        prs,
        now="2026-09-22T12:00:00Z",
        max_age_hours={"weekly-rating": 192, "earnings-sentinel": 48},
        pr_stale_hours=6,
    )
    codes = {alert["code"] for alert in report["alerts"]}

    assert codes == {"stale_run", "blocked_pr", "failed_check", "stale_pr"}
    assert report["status"] == "actionable"
    assert report["report_only"] is True


def test_cli_fixture_mode_is_report_only_and_idempotent(tmp_path, capsys):
    fixture = tmp_path / "weekly.json"
    state = tmp_path / "state.json"
    fixture.write_text(json.dumps({"rows": [
        {"tkr": "AAA", "layer": "01", "gate": True, "stale": False,
         "age": None, "backing": "NONE"},
    ]}))
    argv = ["weekly-rating", "--fixture", str(fixture), "--state", str(state),
            "--now", "2026-09-22T10:00:00Z"]

    assert ops.main(argv) == 0
    first = capsys.readouterr().out
    assert json.loads(first)["report_only"] is True

    assert ops.main(argv) == 0
    assert capsys.readouterr().out == ""
