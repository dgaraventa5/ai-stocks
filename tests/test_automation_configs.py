import json
from pathlib import Path
import plistlib


ROOT = Path(__file__).resolve().parents[1]


def test_daily_refresh_validates_before_commit_and_push():
    workflow = (ROOT / ".github/workflows/daily-refresh.yml").read_text()

    test_step = "- name: Validate generated data"
    commit_step = "- name: Commit series if changed"

    assert test_step in workflow
    assert "python -m pytest tests -q" in workflow
    assert workflow.index(test_step) < workflow.index(commit_step)


def test_pull_request_ci_is_least_privilege_and_dispatchable():
    workflow_path = ROOT / ".github/workflows/ci.yml"

    assert workflow_path.exists()
    workflow = workflow_path.read_text()
    assert "pull_request:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "concurrency:" in workflow
    assert "cancel-in-progress: true" in workflow
    assert "python -m pytest tests -q" in workflow


def test_launchd_executor_keeps_open_run_and_drops_close_writer():
    plist_path = ROOT / "launchd/com.dom.aistocks.executor.plist"
    with plist_path.open("rb") as handle:
        config = plistlib.load(handle)

    intervals = config["StartCalendarInterval"]
    assert intervals == [
        {"Weekday": weekday, "Hour": 6, "Minute": 35}
        for weekday in range(1, 6)
    ]


def test_hermes_context_is_bounded_and_carries_safety_rules():
    context_path = ROOT / ".hermes.md"

    assert context_path.exists()
    context = context_path.read_text()
    assert len(context) <= 20_000
    for required in (
        "origin/main",
        ".venv/bin/python -m pytest tests -q",
        "tracking/live/",
        "execute_ticket.py",
        "--confirm",
        "launchd",
        "scheduled",
        "CLAUDE.md",
    ):
        assert required in context


def test_daily_refresh_uses_builtin_token_and_explicit_dispatches():
    workflow = (ROOT / ".github/workflows/daily-refresh.yml").read_text()

    assert "AI_STOCKS_AUTOMATION_TOKEN" not in workflow
    assert "GH_TOKEN: ${{ github.token }}" in workflow
    assert "automation/performance-series" in workflow
    assert "scripts/generated_data_pr.py" in workflow
    assert "gh pr create" in workflow
    assert "gh pr merge --auto --squash" in workflow
    assert "git push origin main" not in workflow
    assert "permissions:\n  actions: write\n  contents: write\n  pull-requests: write" in workflow
    assert "/actions/workflows/ci.yml/dispatches" in workflow
    assert "/actions/workflows/deploy-site.yml/dispatches" in workflow
    assert "gh run watch \"$test_run_id\" --exit-status" in workflow
    assert "headSha" in workflow
    assert "workflow_dispatch" in workflow
    assert "timeout-minutes: 30" in workflow


def test_hermes_cron_proposals_are_paused_script_only_and_order_safe():
    definition_path = ROOT / "automation/hermes/cron-definitions.json"
    definitions = json.loads(definition_path.read_text())

    assert {job["name"] for job in definitions["jobs"]} == {
        "ai-stocks-weekly-rating-report",
        "ai-stocks-earnings-sentinel-report",
        "ai-stocks-ops-health",
    }
    for job in definitions["jobs"]:
        assert job["paused"] is True
        assert job["no_agent"] is True
        assert job["deliver"] == "telegram"
        assert job["workdir"] == "/Users/dom/Hermes/projects/ai-stocks"
        wrapper = (ROOT / "automation/hermes" / job["source_script"]).read_text()
        for forbidden in ("execute_ticket", "--confirm", "git push", "gh pr"):
            assert forbidden not in wrapper


def test_daily_refresh_fails_closed_without_admin_read_permission():
    workflow = (ROOT / ".github/workflows/daily-refresh.yml").read_text()

    assert "AUTOMATION_CUTOVER_ENABLED: ${{ vars.AUTOMATION_CUTOVER_ENABLED }}" in workflow
    assert "AUTOMATION_CUTOVER_ENABLED is not true" in workflow
    # GITHUB_TOKEN cannot request Administration permission. Configuration is
    # verified at cutover; runtime operations and exact-SHA checks fail closed.
    assert "/branches/main/protection" not in workflow
    assert "/actions/permissions/workflow" not in workflow


def test_docs_require_no_personal_credential_secret():
    design = (ROOT / "docs/ops/scheduled-automation-v1.md").read_text()

    assert "AI_STOCKS_AUTOMATION_TOKEN" not in design
    assert "fine-grained PAT" not in design
    assert "GITHUB_TOKEN" in design
