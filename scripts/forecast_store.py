"""Append-only snapshot log for forecast calibration (CLAUDE.md rule 17).

tracking/forecasts.jsonl holds one JSON object (a full forecast snapshot) per
line. Creation appends an `open` snapshot; resolution appends a new snapshot of
the SAME id (resolved | needs_review | void) — lines are never edited. The
current state of an id is its last snapshot. Immutability is therefore a
property of the file, not just a policy: no code path mutates a prior line.

stdlib only — importable under the deploy-site pytest env (openpyxl+pytest, no
yfinance/requests). See docs/superpowers/specs/2026-06-26-forecast-calibration-loop-design.md.
"""
from __future__ import annotations

import json
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORECASTS_PATH = ROOT / "tracking" / "forecasts.jsonl"

STATUSES = {"open", "resolved", "needs_review", "void"}
IMMUTABLE_FIELDS = ("created_date", "ticker", "layer", "dimension", "rating_value",
                    "template", "probability", "resolution_date", "resolution_rule")
REQUIRED_FIELDS = IMMUTABLE_FIELDS + ("id", "claim", "status", "outcome",
                                      "resolved_date", "resolution_evidence",
                                      "resolver_confidence", "notes")
_SLUG = {"REL_STRENGTH_1Q": "relstr"}


class ForecastError(ValueError):
    """Raised when a forecast snapshot violates the log invariants."""


def flag(msg: str) -> None:
    """Surface a data gap (CLAUDE.md rule 3). Local copy so the subsystem never
    imports common (which pulls requests, absent in the deploy-site CI env)."""
    print(f"[FLAG] {msg}")


def load_snapshots(path: Path = FORECASTS_PATH) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open() as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ForecastError(f"{path}:{i}: invalid JSON — {e}")
    return out


def materialize(path: Path = FORECASTS_PATH) -> dict[str, dict]:
    """Current state per id: last snapshot wins (resolution always appends after creation)."""
    state: dict[str, dict] = {}
    for snap in load_snapshots(path):
        fid = snap.get("id")
        if not fid:
            raise ForecastError(f"snapshot missing id: {snap}")
        state[fid] = snap
    return state


def open_forecasts(path: Path = FORECASTS_PATH) -> list[dict]:
    return [s for s in materialize(path).values() if s.get("status") == "open"]


def _validate_shape(snap: dict) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in snap]
    if missing:
        raise ForecastError(f"missing fields: {', '.join(missing)}")
    if snap["status"] not in STATUSES:
        raise ForecastError(f"bad status: {snap['status']!r}")
    p = snap["probability"]
    if not isinstance(p, (int, float)) or isinstance(p, bool) or not (0.0 < p < 1.0):
        raise ForecastError(f"probability must be in (0,1): {p!r}")
    for key in ("created_date", "resolution_date"):
        try:
            dt.date.fromisoformat(snap[key])
        except (TypeError, ValueError):
            raise ForecastError(f"{key} not an ISO date: {snap[key]!r}")
    if not isinstance(snap["resolution_rule"], dict):
        raise ForecastError("resolution_rule must be an object")


def _assign_id(snap: dict, existing_ids: set[str]) -> str:
    slug = _SLUG.get(snap["template"], snap["template"].lower())
    base = f"fc_{snap['created_date']}_{snap['ticker']}_{slug}"
    n = 1
    while f"{base}_{n:03d}" in existing_ids:
        n += 1
    return f"{base}_{n:03d}"


def _append_line(snap: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(snap, sort_keys=True) + "\n")


def append_creation(snap: dict, path: Path = FORECASTS_PATH, *,
                    today: dt.date | None = None) -> dict:
    """Validate a new open forecast, force created_date=today, assign id, append."""
    today = today or dt.date.today()
    snap = dict(snap)
    snap["created_date"] = today.isoformat()          # backdating impossible
    snap.setdefault("status", "open")
    snap.setdefault("outcome", None)
    snap.setdefault("resolved_date", None)
    snap.setdefault("resolution_evidence", None)
    snap.setdefault("resolver_confidence", None)
    snap.setdefault("notes", "")
    if snap["status"] != "open":
        raise ForecastError("append_creation requires status=open")
    res = dt.date.fromisoformat(snap["resolution_date"])
    if res <= today:
        raise ForecastError(f"resolution_date {res} not after created_date {today} (look-ahead)")
    state = materialize(path)
    snap["id"] = _assign_id(snap, set(state))
    _validate_shape(snap)
    _append_line(snap, path)
    return snap


def append_resolution(snap: dict, path: Path = FORECASTS_PATH) -> dict:
    """Append a resolution snapshot for an existing id; immutable fields must match."""
    _validate_shape(snap)
    if snap["status"] == "open":
        raise ForecastError("append_resolution requires a non-open status")
    prior = materialize(path).get(snap["id"])
    if prior is None:
        raise ForecastError(f"no creation snapshot for id {snap['id']}")
    for fld in IMMUTABLE_FIELDS:
        if snap.get(fld) != prior.get(fld):
            raise ForecastError(
                f"immutable field {fld} changed for {snap['id']}: "
                f"{prior.get(fld)!r} -> {snap.get(fld)!r}")
    _append_line(snap, path)
    return snap
