"""tests/test_run_health.py — schedule and failure sorting, offline, stubbed gh."""
import datetime as dt
import json
import subprocess
import types

import run_health as rh

D = dt.date
DAILY = rh.SCHEDULE["daily-watch"]
SUNDAY = rh.SCHEDULE["rating-research"]


def _log(*entries):
    return "# Scheduled run log\n\n" + "\n".join(
        f"- **{d}** ({job}) — text." for d, job in entries)


def test_parse_log_reads_dates_and_jobs_and_ignores_prose():
    runs = rh.parse_log(_log(("2026-10-12", "daily-watch"), ("2026-10-12", "daily-watch"),
                             ("2026-10-17", "weekly-scan")))
    assert runs == {"daily-watch": {D(2026, 10, 12)}, "weekly-scan": {D(2026, 10, 17)}}


def test_empty_weekdays_are_missed_and_weekends_are_not_slots():
    # Fri 10-16 ran, Mon 10-19 ran, Tue 10-20 ran, Wed/Thu did not, Fri ran
    ran = {D(2026, 10, 16), D(2026, 10, 19), D(2026, 10, 20), D(2026, 10, 23)}
    out = rh.audit_job(ran, DAILY, D(2026, 10, 24))
    assert out["missed"] == [D(2026, 10, 21), D(2026, 10, 22)]
    assert out["late"] == [] and out["on_time"] == 4


def test_a_run_before_the_next_slot_is_late_not_missed():
    ran = {D(2026, 10, 18), D(2026, 10, 27), D(2026, 11, 1)}
    out = rh.audit_job(ran, SUNDAY, D(2026, 11, 2))
    assert out["late"] == [(D(2026, 10, 25), D(2026, 10, 27))]
    assert out["missed"] == [] and out["on_time"] == 2


def test_a_job_that_goes_silent_is_missed_up_to_yesterday():
    # the failure this check exists for: the log just stops
    out = rh.audit_job({D(2026, 10, 19)}, DAILY, D(2026, 10, 24))
    assert out["missed"] == [D(2026, 10, 20), D(2026, 10, 21),
                             D(2026, 10, 22), D(2026, 10, 23)]


def test_a_rerun_of_an_on_time_slot_is_not_late():
    ran = {D(2026, 10, 18), D(2026, 10, 25), D(2026, 10, 27), D(2026, 11, 1)}
    out = rh.audit_job(ran, SUNDAY, D(2026, 11, 2))
    assert out == {"on_time": 3, "late": [], "missed": []}


def test_late_reports_the_first_run_after_the_slot():
    ran = {D(2026, 10, 18), D(2026, 10, 27), D(2026, 10, 29), D(2026, 11, 1)}
    out = rh.audit_job(ran, SUNDAY, D(2026, 11, 2))
    assert out["late"] == [(D(2026, 10, 25), D(2026, 10, 27))]


def test_a_run_on_the_next_slot_does_not_cover_the_one_before():
    ran = {D(2026, 10, 18), D(2026, 11, 1)}
    assert rh.audit_job(ran, SUNDAY, D(2026, 11, 2))["missed"] == [D(2026, 10, 25)]


def test_todays_slot_is_not_yet_due():
    assert rh.audit_job({D(2026, 10, 19)}, DAILY, D(2026, 10, 20))["missed"] == []


def test_nothing_before_the_first_run_counts():
    out = rh.audit_job({D(2026, 10, 14)}, DAILY, D(2026, 10, 15))
    assert out == {"on_time": 1, "late": [], "missed": []}


GATE = ("FAILED tests/test_targets_reweight_gate.py::test_targets_reflect_current_scores"
        " - AssertionError: Portfolio weights are stale")
OTHER = "FAILED tests/test_site.py::test_x - AssertionError"


def test_gate_alone_is_by_design():
    assert rh.classify_failure(f"{GATE}\n1 failed, 665 passed") == "by-design"


def test_gate_plus_another_test_is_real():
    assert rh.classify_failure(f"{GATE}\n{OTHER}\n2 failed") == "real"


def test_a_failure_outside_the_tests_is_real():
    assert rh.classify_failure("Create or locate generated-data PR\nexit 1") == "real"


def test_a_collection_error_is_real():
    assert rh.classify_failure(f"{GATE}\nERROR tests/test_y.py - ImportError") == "real"


def test_a_gate_file_that_will_not_import_is_real():
    log = "ERROR tests/test_targets_reweight_gate.py - ModuleNotFoundError: x"
    assert rh.classify_failure(log) == "real"


def test_a_gate_fixture_error_is_real():
    log = "ERROR tests/test_targets_reweight_gate.py::test_targets_reflect_current_scores"
    assert rh.classify_failure(log) == "real"


def test_the_gate_message_from_another_test_is_real():
    log = "FAILED tests/test_x.py::test_y - AssertionError: Portfolio weights are stale"
    assert rh.classify_failure(log) == "real"


def test_an_error_line_carrying_the_gate_message_is_real():
    log = ("ERROR tests/test_targets_reweight_gate.py::test_targets_reflect_current_scores"
           " - AssertionError: Portfolio weights are stale")
    assert rh.classify_failure(log) == "real"


def test_a_crash_inside_the_gate_test_is_real():
    log = ("FAILED tests/test_targets_reweight_gate.py::test_targets_reflect_current_scores"
           " - FileNotFoundError: portfolio.xlsx")
    assert rh.classify_failure(log) == "real"


def _fake_gh(runs, logs):
    def gh(*args):
        if args[:2] == ("run", "list"):
            return json.dumps(runs)
        log = logs[args[2]]
        if isinstance(log, Exception):
            raise log
        return log
    return gh


def _run(run_id, conclusion="failure"):
    return {"databaseId": run_id, "conclusion": conclusion,
            "createdAt": "2026-10-31T13:44:52Z"}


def test_workflow_failures_sorts_each_failed_run():
    gh = _fake_gh([_run(1), _run(2), _run(3), _run(4, "success")],
                  {"1": GATE, "2": "exit 1",
                   "3": subprocess.CalledProcessError(1, "gh")})
    checked, failures = rh.workflow_failures(40, gh=gh)
    assert checked == 4
    assert [(f["id"], f["label"]) for f in failures] == [
        (1, "by-design"), (2, "real"), (3, "unknown")]
    assert {f["date"] for f in failures} == {"2026-10-31"}


def test_gh_is_called_read_only_for_the_right_workflow(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        if "list" in cmd:
            return types.SimpleNamespace(stdout=json.dumps([_run(7)]))
        return types.SimpleNamespace(stdout=GATE)

    monkeypatch.setattr(rh.subprocess, "run", fake_run)
    checked, failures = rh.workflow_failures(25)
    assert checked == 1 and failures[0]["label"] == "by-design"
    (listing, list_kw), (view, _) = calls
    assert listing[:3] == ["gh", "run", "list"]
    assert listing[listing.index("--workflow") + 1] == "daily-refresh.yml"
    assert listing[listing.index("--limit") + 1] == "25"
    assert view == ["gh", "run", "view", "7", "--log-failed"]
    assert list_kw["check"] is True and list_kw["cwd"] == rh.ROOT


def test_runs_that_died_without_a_test_log_count_as_real():
    # a timeout, a startup failure and a cancelled run never reach the tests
    gh = _fake_gh([_run(1, "timed_out"), _run(2, "startup_failure"),
                   _run(3, "cancelled")], {})
    _, failures = rh.workflow_failures(40, gh=gh)
    assert [f["label"] for f in failures] == ["real", "real", "real"]


def test_unfinished_and_clean_runs_are_not_failures():
    gh = _fake_gh([_run(1, ""), _run(2, None), _run(3, "success"), _run(4, "skipped"),
                   _run(5, "neutral")], {})
    assert rh.workflow_failures(40, gh=gh) == (5, [])


def _paths(monkeypatch, tmp_path, log=None, calibration=False):
    run_log = tmp_path / "log.md"
    if log is not None:
        run_log.write_text(log)
    report = tmp_path / "calibration-report.md"
    if calibration:
        report.write_text("report")
    monkeypatch.setattr(rh, "RUN_LOG", run_log)
    monkeypatch.setattr(rh, "CALIBRATION_REPORT", report)


def test_missing_calibration_report_is_reported(tmp_path, monkeypatch, capsys):
    _paths(monkeypatch, tmp_path, log="")
    assert rh.main(["--no-github"]) == 1
    assert "NONE: calibration-report.md" in capsys.readouterr().out


def test_missing_run_log_is_could_not_check(tmp_path, monkeypatch, capsys):
    _paths(monkeypatch, tmp_path, calibration=True)
    assert rh.main(["--no-github"]) == 1
    assert "COULD NOT CHECK: run log" in capsys.readouterr().out


def test_gh_failure_is_could_not_check(tmp_path, monkeypatch, capsys):
    today = dt.date.today()
    _paths(monkeypatch, tmp_path, calibration=True, log=_log(
        *((today - dt.timedelta(days=1), job) for job in rh.SCHEDULE)))

    def boom(limit):
        raise OSError("no gh")

    monkeypatch.setattr(rh, "workflow_failures", boom)
    assert rh.main([]) == 1
    assert "COULD NOT CHECK: OSError" in capsys.readouterr().out


# ---- exit code: a clean log, then one thing wrong at a time ------------------
TODAY = D(2026, 10, 24)
CLEAN = [(f"2026-10-{d}", "daily-watch") for d in (19, 20, 21, 22, 23)] + [
    ("2026-10-17", "weekly-scan"), ("2026-10-18", "rating-research")]


def _exit(monkeypatch, tmp_path, entries, *, calibration=True, failures=None):
    _paths(monkeypatch, tmp_path, log=_log(*entries), calibration=calibration)
    monkeypatch.setattr(rh, "_today", lambda: TODAY)
    if failures is None:
        return rh.main(["--no-github"])
    monkeypatch.setattr(rh, "workflow_failures", lambda limit: failures)
    return rh.main([])


def test_all_clear_exits_zero(tmp_path, monkeypatch):
    assert _exit(monkeypatch, tmp_path, CLEAN) == 0
    assert _exit(monkeypatch, tmp_path, CLEAN, failures=(40, [])) == 0


def test_a_missed_run_exits_nonzero(tmp_path, monkeypatch):
    entries = [e for e in CLEAN if e[0] != "2026-10-21"]
    assert _exit(monkeypatch, tmp_path, entries) == 1
    assert _exit(monkeypatch, tmp_path, entries, failures=(40, [])) == 1


def test_a_job_with_no_runs_exits_nonzero(tmp_path, monkeypatch, capsys):
    entries = [e for e in CLEAN if e[1] != "weekly-scan"]
    assert _exit(monkeypatch, tmp_path, entries) == 1
    assert "weekly-scan: no runs logged" in capsys.readouterr().out


def test_a_late_run_alone_exits_zero(tmp_path, monkeypatch):
    entries = [e for e in CLEAN if e[1] != "rating-research"] + [
        ("2026-10-04", "rating-research"), ("2026-10-13", "rating-research"),
        ("2026-10-18", "rating-research")]      # Sunday 10-11 ran on Tuesday
    assert _exit(monkeypatch, tmp_path, entries) == 0
    assert _exit(monkeypatch, tmp_path, entries, failures=(40, [])) == 0


def test_no_calibration_report_exits_nonzero(tmp_path, monkeypatch):
    assert _exit(monkeypatch, tmp_path, CLEAN, calibration=False) == 1
    assert _exit(monkeypatch, tmp_path, CLEAN, calibration=False, failures=(40, [])) == 1


def _failure(label):
    return (40, [{"id": 1, "date": "2026-10-23", "label": label}])


def test_a_real_failure_exits_nonzero(tmp_path, monkeypatch):
    assert _exit(monkeypatch, tmp_path, CLEAN, failures=_failure("real")) == 1


def test_an_unknown_failure_exits_nonzero(tmp_path, monkeypatch):
    assert _exit(monkeypatch, tmp_path, CLEAN, failures=_failure("unknown")) == 1


def test_a_by_design_failure_alone_exits_zero(tmp_path, monkeypatch):
    assert _exit(monkeypatch, tmp_path, CLEAN, failures=_failure("by-design")) == 0


def test_no_runs_returned_is_could_not_check(tmp_path, monkeypatch, capsys):
    assert _exit(monkeypatch, tmp_path, CLEAN, failures=(0, [])) == 1
    assert "COULD NOT CHECK: no runs returned" in capsys.readouterr().out


def test_report_names_each_problem(tmp_path, monkeypatch, capsys):
    entries = [e for e in CLEAN if e[1] != "rating-research" and e[0] != "2026-10-21"] + [
        ("2026-10-04", "rating-research"), ("2026-10-13", "rating-research"),
        ("2026-10-18", "rating-research")]
    failures = (40, [{"id": 123, "date": "2026-10-23", "label": "real"}])
    assert _exit(monkeypatch, tmp_path, entries, failures=failures) == 1
    out = capsys.readouterr().out
    assert "daily-watch: 4 on time, 0 late, 1 missed" in out
    assert "rating-research: 2 on time, 1 late, 0 missed" in out
    assert "MISSED: 2026-10-21" in out
    assert "late: 2026-10-11 (ran 2026-10-13)" in out
    assert "last 40 runs: 1 failed (0 by-design, 1 real, 0 unknown)" in out
    assert "2026-10-23 123 real" in out


def test_nothing_is_written(tmp_path, monkeypatch):
    entries = [e for e in CLEAN if e[0] != "2026-10-21"]
    _paths(monkeypatch, tmp_path, log=_log(*entries), calibration=True)
    monkeypatch.setattr(rh, "_today", lambda: TODAY)
    monkeypatch.setattr(rh, "workflow_failures", lambda limit: _failure("real"))
    before = {p.name: p.read_text() for p in tmp_path.iterdir()}

    def refuse(*a, **k):
        raise AssertionError("run_health wrote a file")

    real_open = open

    def read_only_open(file, mode="r", *a, **k):
        if set(mode) & set("wax+"):
            refuse()
        return real_open(file, mode, *a, **k)

    monkeypatch.setattr("builtins.open", read_only_open)
    monkeypatch.setattr(rh.Path, "write_text", refuse)
    monkeypatch.setattr(rh.Path, "write_bytes", refuse)
    assert rh.main([]) == 1
    assert rh.main(["--no-github"]) == 1
    assert {p.name: p.read_text() for p in tmp_path.iterdir()} == before


def test_only_recent_misses_fail_the_check():
    # silent from 10-20: the 10-21 slot is 14 days back, the 10-20 slot is 15
    runs = {"daily-watch": {D(2026, 10, 19), D(2026, 11, 3)},
            "weekly-scan": {D(2026, 11, 1)}, "rating-research": {D(2026, 11, 2)}}
    lines, problem = rh.report_schedule(runs, D(2026, 11, 4))
    text = "\n".join(lines)
    assert problem
    assert "MISSED: 2026-10-21" in text and "MISSED: 2026-10-20" not in text
    assert "1 missed before that" in text


def test_an_old_miss_stops_failing_once_it_ages_out():
    ran = {D(2026, 10, 16)} | {D(2026, 10, 20) + dt.timedelta(days=i) for i in range(25)}
    runs = {"daily-watch": ran, "weekly-scan": {D(2026, 11, 7)},
            "rating-research": {D(2026, 11, 8)}}
    lines, problem = rh.report_schedule(runs, D(2026, 11, 9))
    assert not problem
    assert any("0 missed in the last 14 days, 1 missed before that" in l for l in lines)
