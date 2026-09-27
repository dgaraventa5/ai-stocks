import json

import generated_data_pr as gdp


AUTOMATION_BRANCH = "automation/performance-series-v2"


def _pr(**overrides):
    base = {
        "number": 80,
        "headRefName": AUTOMATION_BRANCH,
        "baseRefName": "main",
        "mergeStateStatus": "CLEAN",
        "files": [{"path": "tracking/performance-series.json"}],
        "statusCheckRollup": [],
    }
    base.update(overrides)
    return base


def test_plan_create_when_no_branch_or_pr_exists():
    plan = gdp.plan_update([], branch_exists=False,
                           desired_sha="new", branch_sha=None,
                           automation_branch=AUTOMATION_BRANCH)
    assert plan == {"action": "create", "reason": "no existing automation PR"}


def test_plan_uses_the_configured_automation_branch():
    accepted = gdp.plan_update([_pr()], True, "same", "same",
                               automation_branch=AUTOMATION_BRANCH)
    rejected = gdp.plan_update([_pr()], True, "same", "same",
                               automation_branch="automation/other")

    assert accepted["action"] == "wait"
    assert rejected == {
        "action": "blocked",
        "reason": "automation PR ownership mismatch",
    }


def test_plan_blocks_conflicting_or_failed_existing_pr():
    conflict = gdp.plan_update(
        [_pr(mergeStateStatus="DIRTY")], True,
        desired_sha="new", branch_sha="old",
        automation_branch=AUTOMATION_BRANCH)
    failed = gdp.plan_update(
        [_pr(statusCheckRollup=[
            {"name": "test", "conclusion": "FAILURE"}
        ])], True, desired_sha="new", branch_sha="old",
        automation_branch=AUTOMATION_BRANCH)

    assert conflict["action"] == "blocked"
    assert conflict["reason"] == "existing PR is DIRTY"
    assert failed["action"] == "blocked"
    assert failed["reason"] == "required check test is FAILURE"


def test_plan_waits_for_identical_open_pr_and_updates_new_data():
    waiting = gdp.plan_update(
        [_pr()], True, desired_sha="same", branch_sha="same",
        automation_branch=AUTOMATION_BRANCH)
    update = gdp.plan_update(
        [_pr()], True, desired_sha="new", branch_sha="old",
        automation_branch=AUTOMATION_BRANCH)

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

    assert gdp.main([
        "--input", str(input_path),
        "--automation-branch", AUTOMATION_BRANCH,
    ]) == 2
    assert json.loads(capsys.readouterr().out)["action"] == "blocked"
