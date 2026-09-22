"""Safety planner for the single generated-data pull request."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


AUTOMATION_BRANCH = "automation/performance-series"
BASE_BRANCH = "main"
ALLOWED_PATH = "tracking/performance-series.json"


def plan_update(prs: list[dict], branch_exists: bool,
                desired_sha: str, branch_sha: str | None) -> dict:
    """Return a deterministic action without mutating Git or GitHub."""
    if not prs and not branch_exists:
        return {"action": "create", "reason": "no existing automation PR"}
    if not prs and branch_exists:
        return {"action": "blocked", "reason": "orphan automation branch exists"}
    if len(prs) != 1:
        return {"action": "blocked", "reason": "multiple automation PRs exist"}

    pr = prs[0]
    if pr.get("headRefName") != AUTOMATION_BRANCH or pr.get("baseRefName") != BASE_BRANCH:
        return {"action": "blocked", "reason": "automation PR ownership mismatch"}
    paths = sorted(file["path"] for file in pr.get("files", []))
    if paths != [ALLOWED_PATH]:
        return {"action": "blocked", "reason": "automation PR scope mismatch"}

    merge_state = str(pr.get("mergeStateStatus", "UNKNOWN")).upper()
    if merge_state in {"BLOCKED", "DIRTY"}:
        return {"action": "blocked", "reason": f"existing PR is {merge_state}"}
    failed = {"ACTION_REQUIRED", "CANCELLED", "FAILURE", "STALE", "TIMED_OUT"}
    for check in pr.get("statusCheckRollup", []):
        conclusion = str(check.get("conclusion") or "").upper()
        if conclusion in failed:
            return {"action": "blocked", "reason": (
                f"required check {check.get('name', 'unknown')} is {conclusion}")}
    number = int(pr["number"])
    if desired_sha == branch_sha:
        return {"action": "wait", "pr": number,
                "reason": "identical generated data already has an open PR"}
    return {"action": "update", "pr": number,
            "reason": "new generated data"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    data = json.loads(args.input.read_text())
    plan = plan_update(
        data.get("prs", []), bool(data.get("branch_exists")),
        str(data["desired_sha"]),
        str(data["branch_sha"]) if data.get("branch_sha") is not None else None)
    print(json.dumps(plan, sort_keys=True))
    if args.github_output:
        lines = [f"action={plan['action']}", f"reason={plan['reason']}"]
        if "pr" in plan:
            lines.append(f"pr={plan['pr']}")
        args.github_output.write_text("\n".join(lines) + "\n")
    return 2 if plan["action"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
