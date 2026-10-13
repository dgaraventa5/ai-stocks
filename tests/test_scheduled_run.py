"""Pure-decision tests for scripts/scheduled_run.py (rule 37). Offline."""
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import scheduled_run as sr  # noqa: E402

NOW = dt.datetime(2026, 10, 12, 15, 45)


def test_fresh_lock_blocks_and_stale_lock_does_not():
    assert sr.lock_is_live({"started": "2026-10-12T15:00:00"}, NOW)
    assert not sr.lock_is_live({"started": "2026-10-12T09:00:00"}, NOW)
    assert not sr.lock_is_live(None, NOW)
    assert not sr.lock_is_live({"started": "garbage"}, NOW)


def test_clean_main_has_no_git_problems():
    assert sr.git_problems("main", [], 0) == []


def test_wrong_branch_dirty_tree_and_unpushed_main_are_each_reported():
    probs = sr.git_problems("feat/x", ["a.py", "b.py"], 2)
    assert len(probs) == 3
    assert "feat/x" in probs[0] and "2 tracked" in probs[1] and "ahead" in probs[2]


def test_only_scheduled_run_prs_count_as_stuck():
    prs = [{"number": 7, "headRefName": "auto/daily-watch-2026-10-09"},
           {"number": 8, "headRefName": "feat/something"}]
    assert sr.open_run_prs(prs) == ["#7 (auto/daily-watch-2026-10-09)"]


def test_filings_filtered_by_form_and_window_and_earnings_flagged():
    recent = {
        "form": ["8-K", "4", "8-K", "6-K", "8-K"],
        "accessionNumber": ["a-1", "a-2", "a-3", "a-4", "a-5"],
        "filingDate": ["2026-10-12", "2026-10-12", "2026-09-01", "2026-10-10", "bad"],
        "primaryDocument": ["x.htm"] * 5,
        "items": ["2.02,9.01", "", "5.02", "", "8.01"],
    }
    out = sr.filings_in_window(recent, dt.date(2026, 10, 9), dt.date(2026, 10, 12))
    assert [f["accession"] for f in out] == ["a-1", "a-4"]
    assert out[0]["earnings"] is True and out[1]["earnings"] is False
    assert out[0]["items"] == ["2.02", "9.01"]


def test_scan_is_blocked_when_lookups_mostly_fail_or_nothing_was_tried():
    assert sr.scan_blocked(0, 0)
    assert sr.scan_blocked(25, 25)
    assert sr.scan_blocked(25, 6)
    assert not sr.scan_blocked(25, 5)
    assert not sr.scan_blocked(200, 3)


def test_only_tickets_created_during_the_run_are_held():
    before = ["ticket-2026-10-12-manual.json"]
    now = ["ticket-2026-10-12-manual.json", "ticket-2026-10-13-membership.json",
           "held-ticket-2026-10-01-membership.json",
           "superseded-ticket-2026-10-05-manual.json"]
    assert sr.new_actionable_tickets(now, before) == [
        "ticket-2026-10-13-membership.json"]


def test_hold_tickets_renames_new_ticket_out_of_the_executor_glob(tmp_path, monkeypatch):
    tdir = tmp_path / "live" / "tickets"
    tdir.mkdir(parents=True)
    (tdir / "ticket-old.json").write_text("{}")
    (tdir / "ticket-new.json").write_text("{}")
    (tdir / "held-ticket-new.json").write_text("{}")       # earlier hold, same name
    lock = tmp_path / "lock.json"
    lock.write_text(json.dumps({"tickets_before": ["ticket-old.json"]}))
    monkeypatch.setattr(sr, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(sr, "LOCK_PATH", lock)
    assert sr.hold_tickets() == 0
    names = sorted(p.name for p in tdir.iterdir())
    assert names == ["held-ticket-new.2.json", "held-ticket-new.json",
                     "ticket-old.json"]
    assert sorted(p.name for p in tdir.glob("ticket-*.json")) == ["ticket-old.json"]


def test_module_never_names_a_broker_write_tool():
    src = (Path(sr.__file__)).read_text()
    assert "place_" not in src and "_order(" not in src


def test_only_research_and_score_paths_may_be_staged():
    ok = ["per-stock/NVDA/news-log.md", "00-master/entry-holds.json",
          "tracking/score-history.csv"]
    assert sr.staged_violations(ok) == []
    bad = ["tracking/live/tickets/ticket-x.json", "scripts/evil.py",
           ".claude/settings.json", "CLAUDE.md", ".github/workflows/x.yml"]
    assert sr.staged_violations(ok + bad) == sorted(bad)


def test_run_branch_is_fixed_by_the_lock_and_sanitized():
    assert sr.run_branch({"job": "daily-watch", "started": "2026-10-12T15:51:00"}) \
        == "auto/daily-watch-2026-10-12"
    assert sr.run_branch({"job": "x:main --force", "started": "2026-10-12T15:51:00"}) \
        == "auto/xmain--force-2026-10-12"
    assert sr.run_branch(None) is None and sr.run_branch({"job": "a"}) is None


def test_run_log_line_is_one_dated_line_per_run():
    lock = {"job": "daily-watch", "started": "2026-10-12T15:45:00"}
    assert (sr.run_log_line(lock, "quiet (scope 25,\n filings 1)")
            == "- **2026-10-12** (daily-watch) — quiet (scope 25, filings 1)")


def test_run_log_line_needs_a_lock_and_some_text():
    assert sr.run_log_line(None, "quiet") is None
    assert sr.run_log_line({"job": "daily-watch"}, "quiet") is None
    assert sr.run_log_line({"job": "x", "started": "2026-10-12T15:45:00"}, "  ") is None


def test_morning_reconciliation_status_files_do_not_block_a_run():
    assert sr.git_problems("main", ["tracking/live-status.json",
                                    "tracking/live-vs-model.json"], 0) == []
    probs = sr.git_problems("main", ["tracking/live-status.json",
                                     "00-master/portfolio.xlsx"], 0)
    assert len(probs) == 1 and "1 tracked" in probs[0] and "portfolio.xlsx" in probs[0]
    assert sr.staged_violations(sorted(sr.MACHINE_WRITTEN)) == []
