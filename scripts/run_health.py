"""Did the scheduled work actually happen? Read-only health check.

The run log only records runs that happened, so a missed run leaves no trace
unless something compares the log to the schedule. daily-refresh.yml goes red
by design when the rule-25 gate fires, which hides real failures among those
that only mean "Dom's pipeline should act". This script does both comparisons
and writes nothing.

  python3 scripts/run_health.py                # all checks
  python3 scripts/run_health.py --no-github    # skip the workflow check

Exits nonzero if a run was missed in the last RECENT_DAYS days, a run failed for
a real reason, the calibration report is missing, or a check could not look. A
log date covers its job; a slot with no run is LATE if one landed before the next
slot, otherwise MISSED. Late alone does not fail the run. Older misses are counted
but do not fail it, because the log is append-only and they can never clear.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN_LOG = ROOT / "tracking" / "scheduled-run-log.md"
CALIBRATION_REPORT = ROOT / "tracking" / "calibration-report.md"
WORKFLOW = "daily-refresh.yml"
GATE_TEST = "tests/test_targets_reweight_gate.py"
CLEAN_CONCLUSIONS = {"success", "skipped", "neutral"}
RECENT_DAYS = 14

# Weekdays each job is scheduled on (docs/ops/scheduled-runs.md), Monday = 0.
SCHEDULE = {"daily-watch": {0, 1, 2, 3, 4}, "weekly-scan": {5}, "rating-research": {6}}

_LOG_LINE = re.compile(r"^- \*\*(\d{4}-\d{2}-\d{2})\*\* \(([a-z-]+)\)")
_TEST_RESULT = re.compile(r"\b(FAILED|ERROR) (tests/\S+)(.*)")
_GATE_FIRED = "AssertionError: Portfolio weights"


def parse_log(text: str) -> dict[str, set[dt.date]]:
    """{job: dates it ran}, from the run log's lines."""
    runs: dict[str, set[dt.date]] = {}
    for line in text.splitlines():
        m = _LOG_LINE.match(line)
        if m:
            runs.setdefault(m.group(2), set()).add(dt.date.fromisoformat(m.group(1)))
    return runs


def _next_slot(day: dt.date, weekdays: set[int]) -> dt.date:
    day += dt.timedelta(days=1)
    while day.weekday() not in weekdays:
        day += dt.timedelta(days=1)
    return day


def audit_job(ran: set[dt.date], weekdays: set[int], today: dt.date) -> dict:
    """Compare a job's runs to its slots, from its first run up to yesterday."""
    out = {"on_time": 0, "late": [], "missed": []}
    if not ran:
        return out
    day = min(ran)
    while day < today:
        if day.weekday() in weekdays:
            following = _next_slot(day, weekdays)
            catch_up = sorted(d for d in ran if day < d < following)
            if day in ran:
                out["on_time"] += 1
            elif catch_up:
                out["late"].append((day, catch_up[0]))
            else:
                out["missed"].append(day)
        day += dt.timedelta(days=1)
    return out


def classify_failure(log_text: str) -> str:
    """'by-design' only if the rule-25 gate's own assertion is all that failed.

    A crash or collection error in the gate file is a real failure.
    """
    results = _TEST_RESULT.findall(log_text)
    fired = results and all(kind == "FAILED" and test.startswith(f"{GATE_TEST}::")
                            and _GATE_FIRED in rest for kind, test, rest in results)
    return "by-design" if fired else "real"


def _gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True,
                          timeout=120, check=True, cwd=ROOT).stdout


def workflow_failures(limit: int, gh=_gh) -> tuple[int, list[dict]]:
    """(runs looked at, failed runs with a label). Raises if gh cannot answer."""
    runs = json.loads(gh("run", "list", "--workflow", WORKFLOW, "--limit", str(limit),
                         "--json", "databaseId,conclusion,createdAt"))
    failures = []
    for run in runs:
        conclusion = run.get("conclusion")
        if not conclusion or conclusion in CLEAN_CONCLUSIONS:   # empty = still running
            continue
        if conclusion != "failure":            # timed out or cancelled: no test log
            label = "real"
        else:
            try:
                label = classify_failure(gh("run", "view", str(run["databaseId"]),
                                            "--log-failed"))
            except (OSError, subprocess.SubprocessError):
                label = "unknown"
        failures.append({"id": run["databaseId"], "date": run["createdAt"][:10],
                         "label": label})
    return len(runs), failures


def report_schedule(runs: dict[str, set[dt.date]], today: dt.date) -> tuple[list[str], bool]:
    lines, problem = [], False
    for job, weekdays in SCHEDULE.items():
        result = audit_job(runs.get(job, set()), weekdays, today)
        if job not in runs:
            lines.append(f"  {job}: no runs logged")
            problem = True
            continue
        cutoff = today - dt.timedelta(days=RECENT_DAYS)
        recent = [slot for slot in result["missed"] if slot >= cutoff]
        older = len(result["missed"]) - len(recent)
        lines.append(f"  {job}: {result['on_time']} on time, "
                     f"{len(result['late'])} late, {len(recent)} missed in the last "
                     f"{RECENT_DAYS} days, {older} missed before that")
        for slot, landed in result["late"]:
            lines.append(f"    late: {slot} (ran {landed})")
        for slot in recent:
            lines.append(f"    MISSED: {slot}")
        problem = problem or bool(recent)
    return lines, problem


def _today() -> dt.date:
    return dt.date.today()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, default=40, help="workflow runs to check")
    ap.add_argument("--no-github", action="store_true", help="skip the workflow check")
    args = ap.parse_args(argv)
    today = _today()
    problem = False

    print(f"=== Run health, {today} ===\n\nScheduled runs ({RUN_LOG.name}):")
    if RUN_LOG.exists():
        lines, found = report_schedule(parse_log(RUN_LOG.read_text()), today)
        print("\n".join(lines))
        problem = problem or found
    else:
        print("  COULD NOT CHECK: run log not found")
        problem = True

    print("\nCalibration report:")
    if CALIBRATION_REPORT.exists():
        print(f"  {CALIBRATION_REPORT.name} present")
    else:
        print(f"  NONE: {CALIBRATION_REPORT.name} has never been written")
        problem = True

    if args.no_github:
        print(f"\n{WORKFLOW}: skipped")
        return 1 if problem else 0

    print(f"\n{WORKFLOW}:")
    try:
        checked, failures = workflow_failures(args.limit)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        print(f"  COULD NOT CHECK: {type(e).__name__}")
        return 1
    if not checked:
        print("  COULD NOT CHECK: no runs returned")
        return 1
    counts = {k: sum(f["label"] == k for f in failures)
              for k in ("by-design", "real", "unknown")}
    print(f"  last {checked} runs: {len(failures)} failed ({counts['by-design']} by-design, "
          f"{counts['real']} real, {counts['unknown']} unknown)")
    for f in failures:
        print(f"    {f['date']} {f['id']} {f['label']}")
    return 1 if problem or counts["real"] or counts["unknown"] else 0


if __name__ == "__main__":
    sys.exit(main())
