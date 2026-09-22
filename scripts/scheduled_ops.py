"""Deterministic, report-only collectors for scheduled operations.

These helpers never modify workbooks, ratings, portfolios, tickets, orders, Git,
or GitHub. They produce bounded JSON reports with stable deduplication keys for
script-only Hermes cron delivery.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

SCHEMA_VERSION = 1
DEFAULT_LIMIT = 2


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)


def _dedup_key(kind: str, payload: Any) -> str:
    body = _canonical_json({"kind": kind, "payload": payload})
    return hashlib.sha256(body.encode()).hexdigest()


def weekly_rating_report(rows: list[dict], limit: int = DEFAULT_LIMIT) -> dict:
    """Return a bounded, stable report of the stalest subjective-rating rows."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    def sort_key(row: dict) -> tuple[int, int, str]:
        age = row.get("age")
        age_rank = int(age) if age is not None else 10 ** 9
        return (0 if row.get("gate") else 1, -age_rank,
                str(row.get("tkr", "")))

    ordered = sorted(rows, key=sort_key)
    all_items = [
        {
            "ticker": str(row["tkr"]),
            "layer": str(row.get("layer", "")),
            "reason": "gate" if row.get("gate") else
                      "stale" if row.get("stale") else "rotation",
            "age_days": row.get("age"),
            "backing": row.get("backing"),
        }
        for row in ordered
    ]
    payload = {"items": all_items, "limit": limit}
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "weekly-rating-report",
        "status": "actionable" if all_items else "quiet",
        "report_only": True,
        "items": all_items[:limit],
        "overflow_count": max(0, len(all_items) - limit),
        "dedup_key": _dedup_key("weekly-rating-report", payload),
    }


def earnings_report(detector: dict, limit: int = DEFAULT_LIMIT) -> dict:
    """Normalize detector output into a bounded report without marking state."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    combined: dict[tuple[str, str], dict] = {}
    for phase, source_key in (("briefing", "briefing_due"),
                              ("rescore", "rescore_due")):
        for event in detector.get(source_key, []):
            key = (str(event["ticker"]), str(event["report_date"]))
            item = combined.setdefault(key, {
                "ticker": key[0],
                "report_date": key[1],
                "session": str(event.get("session", "")),
                "phases": [],
            })
            item["phases"].append(phase)

    phase_order = {"briefing": 0, "rescore": 1}
    all_items = sorted(combined.values(),
                       key=lambda item: (item["report_date"], item["ticker"]))
    for item in all_items:
        item["phases"].sort(key=phase_order.__getitem__)

    all_flags = [
        {"ticker": str(ticker), "message": str(message)}
        for ticker, message in sorted(detector.get("flagged", {}).items())
    ]
    payload = {
        "items": all_items,
        "flags": all_flags,
        "scope_size": int(detector.get("scope_size", 0)),
        "limit": limit,
    }
    actionable = bool(all_items or all_flags)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "earnings-sentinel-report",
        "status": "actionable" if actionable else "quiet",
        "report_only": True,
        "scope_size": payload["scope_size"],
        "items": all_items[:limit],
        "overflow_count": max(0, len(all_items) - limit),
        "flags": all_flags[:limit],
        "flag_overflow_count": max(0, len(all_flags) - limit),
        "dedup_key": _dedup_key("earnings-sentinel-report", payload),
    }


def load_local_state(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "jobs": {}}
    state = json.loads(path.read_text())
    if state.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported scheduled-ops state schema")
    state.setdefault("jobs", {})
    return state


def _write_local_state(path: Path, state: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def gate_report(job: str, report: dict, state_path: Path, now: str) -> dict | None:
    """Record a local heartbeat and emit only new actionable report content."""
    state = load_local_state(state_path)
    job_state = state["jobs"].setdefault(job, {})
    duplicate = job_state.get("dedup_key") == report["dedup_key"]
    actionable = report.get("status") == "actionable"

    job_state.update({
        "dedup_key": report["dedup_key"],
        "last_status": report.get("status", "unknown"),
        "last_success_at": now,
    })
    if actionable and not duplicate:
        job_state["last_actionable_at"] = now
    _write_local_state(state_path, state)
    return report if actionable and not duplicate else None


def _parse_time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def health_report(state: dict, prs: list[dict], now: str,
                  max_age_hours: dict[str, int],
                  pr_stale_hours: int = 6) -> dict:
    """Report stale scheduler heartbeats and unhealthy automation PRs."""
    reference = _parse_time(now)
    alerts: list[dict] = []
    jobs = state.get("jobs", {})
    for job, max_age in sorted(max_age_hours.items()):
        last = jobs.get(job, {}).get("last_success_at")
        if not last:
            alerts.append({"code": "missing_run", "job": job})
            continue
        age_hours = (reference - _parse_time(last)).total_seconds() / 3600
        if age_hours > max_age:
            alerts.append({"code": "stale_run", "job": job,
                           "age_hours": round(age_hours, 1)})

    for pr in sorted(prs, key=lambda item: int(item["number"])):
        number = int(pr["number"])
        merge_state = str(pr.get("mergeStateStatus", "UNKNOWN")).upper()
        if merge_state in {"BLOCKED", "DIRTY"}:
            alerts.append({"code": "blocked_pr", "pr": number,
                           "merge_state": merge_state})
        for check in pr.get("statusCheckRollup", []):
            conclusion = str(check.get("conclusion") or "").upper()
            if conclusion in {"ACTION_REQUIRED", "CANCELLED", "FAILURE",
                              "STALE", "TIMED_OUT"}:
                alerts.append({"code": "failed_check", "pr": number,
                               "check": str(check.get("name", "unknown")),
                               "conclusion": conclusion})
        updated = pr.get("updatedAt")
        if updated:
            age_hours = (reference - _parse_time(str(updated))).total_seconds() / 3600
            if age_hours > pr_stale_hours:
                alerts.append({"code": "stale_pr", "pr": number,
                               "age_hours": round(age_hours, 1)})

    alerts.sort(key=lambda item: _canonical_json(item))
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "scheduled-ops-health",
        "status": "actionable" if alerts else "quiet",
        "report_only": True,
        "alerts": alerts,
        "dedup_key": _dedup_key("scheduled-ops-health", alerts),
    }


def _default_state_path() -> Path:
    home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    return home / "data" / "ai-stocks-scheduled-ops" / "state.json"


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z")


def _real_earnings_detector() -> dict:
    import earnings_sentinel as sentinel

    scope = sentinel.build_scope(
        sentinel._holdings(),
        sentinel.latest_ranked_rows(sentinel.SCORE_HISTORY),
        sentinel.DEFAULT_TOP_N,
    )
    now = sentinel._now()
    calendar = sentinel._fetch_calendar(scope)
    recent = [
        ticker for ticker in scope
        if isinstance(calendar.get(ticker), list)
        and any(
            stamp <= now
            and (now.astimezone(sentinel.ET).date()
                 - stamp.astimezone(sentinel.ET).date()).days
            <= sentinel.MAX_REPORT_AGE_DAYS
            for stamp in calendar.get(ticker, [])
        )
    ]
    latest_close = sentinel._fetch_latest_close(recent)
    output = sentinel.due_events(
        scope, calendar, latest_close, sentinel.load_state(sentinel.STATE_PATH), now)
    output["scope_size"] = len(scope)
    return output


def _gh_open_prs() -> list[dict]:
    fields = ("number,headRefName,baseRefName,mergeStateStatus,updatedAt,"
              "statusCheckRollup,url")
    result = subprocess.run(
        ["gh", "pr", "list", "--state", "open", "--limit", "100",
         "--json", fields],
        check=True, capture_output=True, text=True, timeout=30)
    prefixes = ("automation/", "earnings/", "refresh/ratings")
    return [pr for pr in json.loads(result.stdout)
            if str(pr.get("headRefName", "")).startswith(prefixes)]


def _load_fixture(path: str | None) -> dict | None:
    return json.loads(Path(path).read_text()) if path else None


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--fixture")
    parser.add_argument("--state", type=Path, default=_default_state_path())
    parser.add_argument("--now", default=None)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--no-gate", action="store_true")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic report-only scheduled operations")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("weekly-rating", "earnings-sentinel", "health"):
        _add_common_options(sub.add_parser(name))
    args = parser.parse_args(argv)
    fixture = _load_fixture(args.fixture)
    now = args.now or _now_iso()

    if args.command == "weekly-rating":
        if fixture is None:
            import audit_rating_integrity
            rows = audit_rating_integrity.audit()
        else:
            rows = fixture.get("rows", [])
        report = weekly_rating_report(rows, limit=args.limit)
        job = "weekly-rating"
    elif args.command == "earnings-sentinel":
        detector = fixture if fixture is not None else _real_earnings_detector()
        report = earnings_report(detector, limit=args.limit)
        job = "earnings-sentinel"
    else:
        if fixture is None:
            state = load_local_state(args.state)
            prs = _gh_open_prs()
        else:
            state = fixture.get("state", {"schema_version": SCHEMA_VERSION,
                                           "jobs": {}})
            prs = fixture.get("prs", [])
        report = health_report(
            state, prs, now=now,
            max_age_hours={"weekly-rating": 192, "earnings-sentinel": 48},
            pr_stale_hours=6)
        job = "ops-health"

    emitted = report if args.no_gate else gate_report(job, report, args.state, now)
    if emitted is not None:
        print(json.dumps(emitted, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
