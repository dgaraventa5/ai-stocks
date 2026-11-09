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


def test_notification_text_is_an_argument_not_script():
    hostile = 'x" & (do shell script "rm -rf ~") & "\nline two'
    args = sr.notify_args(hostile)
    assert args[0] == "osascript" and args[-2] == "--"
    assert args[-1] == 'x" & (do shell script "rm -rf ~") & " line two'
    assert all("do shell script" not in a for a in args[:-1])
    assert sr.notify_args("   ") is None
    assert len(sr.notify_args("y" * 500)[-1]) == 230


# ── recovery from an interrupted land/merge (2026-11-06) ────────────────────
# The 2026-11-04 run's push was cut off by sleep. `land` could not be re-run
# (its commit already existed), the checkout stayed on the run branch, and the
# next two runs refused at preflight. These pin the fix.

def test_land_resumes_when_its_commit_exists_but_nothing_new_is_staged():
    assert sr.land_action(["per-stock/APP/news-log.md"], 0) == "commit"
    assert sr.land_action(["per-stock/APP/news-log.md"], 1) == "commit"
    assert sr.land_action([], 1) == "resume"
    assert sr.land_action([], 0) == "nothing"


def test_retry_stops_on_first_success_and_gives_up_after_the_delays():
    calls, slept = [], []
    results = iter([(1, "timed out"), (0, "ok"), (0, "never")])

    def attempt():
        calls.append(1)
        return next(results)

    assert sr.retry(attempt, (15, 60), sleep=slept.append) == (0, "ok")
    assert len(calls) == 2 and slept == [15]

    calls.clear(), slept.clear()
    assert sr.retry(lambda: (calls.append(1), (1, "down"))[1], (15, 60),
                    sleep=slept.append) == (1, "down")
    assert len(calls) == 3 and slept == [15, 60]


def test_ci_state_reads_gh_pr_checks_output():
    assert sr.ci_state("test\tpass\t1m2s\thttps://x") == "pass"
    assert sr.ci_state("test\tfail\t1m2s\thttps://x") == "fail"
    assert sr.ci_state("test\tpending\t0\thttps://x") == "pending"
    assert sr.ci_state("") == "pending"          # checks not registered yet


def test_hold_trailer_marks_a_run_that_chose_not_to_merge():
    assert sr.is_held(f"daily-watch: x\n\n{sr.HOLD_TRAILER}\n")
    assert not sr.is_held("daily-watch 2026-11-04: APP Q3 briefed")


BR = "auto/daily-watch-2026-11-04"
MACHINE = ["tracking/live-status.json", "tracking/live-vs-model.json"]


def test_not_on_a_run_branch_means_nothing_to_recover():
    assert sr.stranded_plan("main", [], 0, None, False)[0] == "none"
    assert sr.stranded_plan("feat/x", [], 3, None, False)[0] == "none"


def test_committed_but_unpushed_run_is_pushed_and_opened():
    # the 2026-11-04 case: one commit, no PR, morning recon files modified
    assert sr.stranded_plan(BR, MACHINE, 1, None, False)[0] == "open_pr"


def test_open_pr_from_a_stranded_run_is_merged_when_green():
    pr = {"number": 275, "state": "OPEN", "isDraft": False}
    assert sr.stranded_plan(BR, MACHINE, 1, pr, False)[0] == "merge"


def test_already_merged_or_empty_run_branch_just_returns_to_main():
    merged = {"number": 275, "state": "MERGED", "isDraft": False}
    assert sr.stranded_plan(BR, [], 1, merged, False)[0] == "return"
    assert sr.stranded_plan(BR, MACHINE, 0, None, False)[0] == "return"


def test_unfinished_held_or_closed_runs_still_refuse():
    action, why = sr.stranded_plan(BR, ["tracking/scheduled-run-log.md"], 1,
                                   None, False)
    assert action == "refuse" and "uncommitted" in why
    assert sr.stranded_plan(BR, [], 1, None, True)[0] == "refuse"
    draft = {"number": 9, "state": "OPEN", "isDraft": True}
    assert sr.stranded_plan(BR, [], 1, draft, False)[0] == "refuse"
    closed = {"number": 9, "state": "CLOSED", "isDraft": False}
    assert sr.stranded_plan(BR, [], 1, closed, False)[0] == "refuse"


# ── end to end: replay the 2026-11-04 strand against a real git remote ──────

FAKE_GH = r'''#!{python}
import json, subprocess, sys
from pathlib import Path
state_path = Path({state!r})
st = json.loads(state_path.read_text())
a = sys.argv[1:]
def save(): state_path.write_text(json.dumps(st))
if a[:2] == ["pr", "list"]:
    head = a[a.index("--head") + 1]
    print(json.dumps([p for p in st["prs"] if p["head"] == head][-1:]))
elif a[:2] == ["pr", "create"]:
    head = a[a.index("--head") + 1]
    st["prs"].append({{"number": 100 + len(st["prs"]), "head": head,
                      "state": "OPEN", "isDraft": "--draft" in a}})
    save()
elif a[:2] == ["pr", "checks"]:
    print("test\t" + st["ci"] + "\t1m\thttps://ci")
elif a[:2] == ["pr", "merge"]:
    pr = next(p for p in st["prs"] if p["number"] == int(a[2]))
    subprocess.run(["git", "--git-dir", st["bare"], "update-ref",
                    "refs/heads/main", "refs/heads/" + pr["head"]], check=True)
    pr["state"] = "MERGED"
    save()
else:
    sys.exit("fake gh: unsupported " + " ".join(a))
'''


def _git(cwd, *args):
    import subprocess
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def _stranded_checkout(tmp_path, monkeypatch, ci="pass", prs=None, pushed=False):
    bare, work, bin_dir = tmp_path / "origin.git", tmp_path / "work", tmp_path / "bin"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(bare))
    _git(tmp_path, "clone", "-q", str(bare), str(work))
    for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
        _git(work, "config", k, v)
    _git(work, "checkout", "-q", "-B", "main")   # whatever git's default is
    (work / "tracking").mkdir()
    (work / "tracking" / "live-status.json").write_text('{"as_of": "11-03"}\n')
    _git(work, "add", "-A"), _git(work, "commit", "-qm", "base")
    _git(work, "push", "-q", "origin", "main")
    # the 11-04 run: branch, research, commit — then the push never landed
    _git(work, "checkout", "-qb", BR)
    (work / "per-stock").mkdir()
    (work / "per-stock" / "news.md").write_text("APP Q3\n")
    _git(work, "add", "-A"), _git(work, "commit", "-qm", "daily-watch 2026-11-04: APP")
    if pushed:
        _git(work, "push", "-q", "origin", BR)
    # the next morning's reconciliation rewrites its status file
    (work / "tracking" / "live-status.json").write_text('{"as_of": "11-06"}\n')
    state = tmp_path / "gh.json"
    state.write_text(json.dumps({"prs": prs or [], "ci": ci, "bare": str(bare)}))
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH.format(python=sys.executable, state=str(state)))
    gh.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{__import__('os').environ['PATH']}")
    monkeypatch.setattr(sr, "ROOT", work)
    monkeypatch.setattr(sr.time, "sleep", lambda s: None)
    return bare, work, state


def test_preflight_recovery_pushes_merges_and_returns_to_main(tmp_path, monkeypatch):
    bare, work, state = _stranded_checkout(tmp_path, monkeypatch)
    done, problems = sr.recover_stranded()
    assert problems == [], problems
    assert any("opened #100" in d for d in done) and "merged #100" in done
    assert _git(work, "rev-parse", "--abbrev-ref", "HEAD") == "main"
    assert (work / "per-stock" / "news.md").read_text() == "APP Q3\n"
    assert BR not in _git(work, "branch")
    # the reconciliation file the morning wrote survives for the new run to land
    assert "11-06" in (work / "tracking" / "live-status.json").read_text()


def test_preflight_recovery_leaves_a_red_ci_pr_open(tmp_path, monkeypatch):
    _, work, state = _stranded_checkout(tmp_path, monkeypatch, ci="fail")
    done, problems = sr.recover_stranded()
    assert len(problems) == 1 and "CI failed" in problems[0]
    assert _git(work, "rev-parse", "--abbrev-ref", "HEAD") == BR
    assert json.loads(state.read_text())["prs"][0]["state"] == "OPEN"


def test_preflight_recovery_merges_an_already_open_pr(tmp_path, monkeypatch):
    prs = [{"number": 275, "head": BR, "state": "OPEN", "isDraft": False}]
    _, work, state = _stranded_checkout(tmp_path, monkeypatch, prs=prs, pushed=True)
    done, problems = sr.recover_stranded()
    assert problems == [] and done[0] == "merged #275"
    assert _git(work, "rev-parse", "--abbrev-ref", "HEAD") == "main"


def test_preflight_recovery_never_lands_uncommitted_work(tmp_path, monkeypatch):
    _, work, state = _stranded_checkout(tmp_path, monkeypatch)
    (work / "per-stock" / "news.md").write_text("half-written\n")
    done, problems = sr.recover_stranded()
    assert done == [] and "uncommitted" in problems[0]
    assert json.loads(state.read_text())["prs"] == []


def test_rerunning_land_resumes_from_the_existing_commit(tmp_path, monkeypatch, capsys):
    bare, work, state = _stranded_checkout(tmp_path, monkeypatch)
    lock = work / ".cache" / "scheduled-run.lock"
    lock.parent.mkdir()
    lock.write_text(json.dumps({"job": "daily-watch",
                                "started": "2026-11-04T15:57:00"}))
    monkeypatch.setattr(sr, "LOCK_PATH", lock)
    _git(work, "checkout", "--", "tracking/live-status.json")  # nothing staged
    assert sr.land("daily-watch 2026-11-04: APP", None) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["resumed"] is True and out["pr"] == 100
    assert _git(bare, "rev-parse", BR) == _git(work, "rev-parse", "HEAD")
    assert sr.land("daily-watch 2026-11-04: APP", None) == 0   # idempotent
    assert len(json.loads(state.read_text())["prs"]) == 1


def test_held_land_opens_a_draft_that_recovery_refuses(tmp_path, monkeypatch, capsys):
    _, work, state = _stranded_checkout(tmp_path, monkeypatch)
    lock = work / ".cache" / "scheduled-run.lock"
    lock.parent.mkdir()
    lock.write_text(json.dumps({"job": "daily-watch",
                                "started": "2026-11-04T15:57:00"}))
    monkeypatch.setattr(sr, "LOCK_PATH", lock)
    (work / "per-stock" / "more.md").write_text("x\n")
    assert sr.land("daily-watch 2026-11-04: tests red", None, hold=True) == 0
    assert json.loads(state.read_text())["prs"][0]["isDraft"] is True
    _, problems = sr.recover_stranded()
    assert "held" in problems[0]
