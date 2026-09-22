import json

import generated_data_pr as gdp


def _pr(**overrides):
    base = {
        "number": 80,
        "headRefName": "automation/performance-series",
        "baseRefName": "main",
        "mergeStateStatus": "CLEAN",
        "files": [{"path": "tracking/performance-series.json"}],
        "statusCheckRollup": [],
    }
    base.update(overrides)
    return base


def test_plan_create_when_no_branch_or_pr_exists():
    plan = gdp.plan_update([], branch_exists=False,
                           desired_sha="new", branch_sha=None)
    assert plan == {"action": "create", "reason": "no existing automation PR"}


def test_plan_blocks_conflicting_or_failed_existing_pr():
    conflict = gdp.plan_update([_pr(mergeStateStatus="DIRTY")], True,
                               desired_sha="new", branch_sha="old")
    failed = gdp.plan_update([_pr(statusCheckRollup=[
        {"name": "test", "conclusion": "FAILURE"}
    ])], True, desired_sha="new", branch_sha="old")

    assert conflict["action"] == "blocked"
    assert conflict["reason"] == "existing PR is DIRTY"
    assert failed["action"] == "blocked"
    assert failed["reason"] == "required check test is FAILURE"


def test_plan_waits_for_identical_open_pr_and_updates_new_data():
    waiting = gdp.plan_update([_pr()], True,
                              desired_sha="same", branch_sha="same")
    update = gdp.plan_update([_pr()], True,
                             desired_sha="new", branch_sha="old")

    assert waiting["action"] == "wait"
    assert update == {"action": "update", "pr": 80,
                      "reason": "new generated data"}


def test_cli_fails_loudly_for_blocked_plan(tmp_path, capsys):
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps({
        "prs": [_pr(mergeStateStatus="DIRTY")],
        "branch_exists": True,
        "desired_sha": "new",
        "branch_sha": "old",
    }))

    assert gdp.main(["--input", str(input_path)]) == 2
    assert json.loads(capsys.readouterr().out)["action"] == "blocked"
