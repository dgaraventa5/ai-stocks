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


def test_pull_request_ci_is_least_privilege_and_concurrency_safe():
    workflow_path = ROOT / ".github/workflows/ci.yml"

    assert workflow_path.exists()
    workflow = workflow_path.read_text()
    assert "pull_request:" in workflow
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


def test_daily_refresh_uses_a_scoped_automation_pr_instead_of_main_push():
    workflow = (ROOT / ".github/workflows/daily-refresh.yml").read_text()

    assert "AI_STOCKS_AUTOMATION_TOKEN" in workflow
    assert "automation/performance-series" in workflow
    assert "scripts/generated_data_pr.py" in workflow
    assert "gh pr create" in workflow
    assert "gh pr merge --auto --squash" in workflow
    assert "git push origin main" not in workflow
    assert "pages deploy" not in workflow
    assert "permissions:\n  contents: read" in workflow


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


def test_daily_refresh_fails_closed_until_required_check_and_auto_merge_exist():
    workflow = (ROOT / ".github/workflows/daily-refresh.yml").read_text()

    assert "/branches/main/protection/required_status_checks" in workflow
    assert "allow_auto_merge" in workflow
    assert "grep -Fx 'test'" in workflow
