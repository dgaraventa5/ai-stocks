# Forecast Calibration Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn frozen subjective ratings into dated, falsifiable probability forecasts, resolve them mechanically against free data, and grade the rater's calibration (Brier / Murphy / skill-vs-base-rate) — diagnostic only, never fed back into the score.

**Architecture:** A small subsystem of stdlib/openpyxl-only core modules (store, metrics, cohorts, resolvers) that are CI-safe and unit-testable, plus three thin CLIs (`log_forecast`, `resolve_forecasts`, `calibration_report`). The log is a single append-only snapshot file `tracking/forecasts.jsonl`; resolution appends a new snapshot of the same id rather than editing a line. Price data is injected into resolvers so they test on synthetic series; yfinance and matplotlib are imported lazily.

**Tech Stack:** Python 3, openpyxl (Watchlist I/O), yfinance (prices, lazy), matplotlib (optional reliability PNG, lazy), pytest.

**Design spec:** `docs/superpowers/specs/2026-06-26-forecast-calibration-loop-design.md`

## Global Constraints

- **CI import floor:** `deploy-site.yml` runs `python -m pytest tests -q` with **only `openpyxl pytest`** installed. Every new module and test must import and pass under that. **No new module may import `common`, `yfinance`, `pandas`, `matplotlib`, or `requests` at module top** (`common` pulls `requests`). yfinance is imported lazily inside the price loader; matplotlib lazily inside the chart function.
- **Flat modules**, `scripts/forecast_*.py`, matching the existing catalog (`momentum_50dma.py`). CLIs begin with `sys.path.insert(0, str(Path(__file__).resolve().parent))` like `refresh_objective_inputs.py`.
- **Append-only log:** never edit a line; `created_date`, `ticker`, `layer`, `dimension`, `rating_value`, `template`, `probability`, `resolution_date`, `resolution_rule` are immutable; `created_date` is set to today at log time (backdating impossible); `resolution_date` must lie entirely after `created_date` (no look-ahead).
- **Boundary (CLAUDE.md rule 17):** no feedback into Total Score or weights; no new Watchlist columns; no paid data; not surfaced on the friend-facing site.
- **Citations & gaps:** every resolution carries a cited evidence string (rule 1); ambiguous resolutions go to `needs_review`, never guessed (rule 3).
- **Tests:** rely on `tests/conftest.py` (already inserts `scripts/` on `sys.path`); build synthetic workbooks in `tmp_path`; inject `price_loader` and `today`; pass explicit `path=` to store functions.
- **Branch first:** the repo is on `main`. Execution must start on a feature branch (or worktree via superpowers:using-git-worktrees). Commit messages end with the project's Co-Authored-By trailer.

---

### Task 1: Pre-flight — branch + verify Watchlist headers

**Files:**
- None created. Recon + branch only.

- [ ] **Step 1: Create the feature branch**

```bash
cd /Users/dom/Desktop/ai-stocks
git checkout -b feat/forecast-calibration-loop
```

- [ ] **Step 2: Verify the Watchlist header assumptions this plan hard-codes**

Run:
```bash
python3 - <<'PY'
from openpyxl import load_workbook
ws = load_workbook("00-master/ai_supply_chain_scoring.xlsx", read_only=True)["Watchlist"]
print("col1:", ws.cell(1,1).value, "| col3:", ws.cell(1,3).value)
hits = [(c, ws.cell(1,c).value) for c in range(1, ws.max_column+1)
        if ws.cell(1,c).value and "strength" in str(ws.cell(1,c).value).lower()]
print("strength header(s):", hits)
PY
```
Expected: `col1: Ticker | col3: Layer` and exactly one strength header (around col 27, e.g. `Relative Strength` / `Rel. Strength`). If `col1`/`col3` differ, update `TICKER_COL`/`LAYER_COL` in Task 4 before coding. The strength column is located at runtime by the `"strength"` predicate, so its exact text/position doesn't need pinning.

- [ ] **Step 3: Confirm portfolio resolves**

Run:
```bash
python3 -c "import sys; sys.path.insert(0,'scripts'); from refresh_objective_inputs import resolve_targets; print(resolve_targets('portfolio'))"
```
Expected: a list of ~14 HOLD tickers (e.g. `['TSM','NVDA','SNDK',...]`). This is what Phase-1 seeding will iterate.

- [ ] **Step 4: Commit the branch point (no-op marker)**

No file changes yet; proceed to Task 2. (No commit.)

---

### Task 2: `forecast_store.py` — the append-only snapshot log

**Files:**
- Create: `scripts/forecast_store.py`
- Test: `tests/test_forecast_store.py`

**Interfaces:**
- Consumes: nothing (stdlib only).
- Produces:
  - `ROOT: Path`, `FORECASTS_PATH: Path`
  - `class ForecastError(ValueError)`
  - `flag(msg: str) -> None`
  - `load_snapshots(path=FORECASTS_PATH) -> list[dict]`
  - `materialize(path=FORECASTS_PATH) -> dict[str, dict]` (last snapshot per id)
  - `open_forecasts(path=FORECASTS_PATH) -> list[dict]`
  - `append_creation(snap: dict, path=FORECASTS_PATH, *, today: datetime.date|None=None) -> dict`
  - `append_resolution(snap: dict, path=FORECASTS_PATH) -> dict`
  - `IMMUTABLE_FIELDS: tuple[str,...]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_forecast_store.py
import datetime as dt
import pytest
import forecast_store as store

TODAY = dt.date(2026, 6, 26)


def _proposal(**over):
    base = dict(
        ticker="AVGO", layer="06", dimension="momentum.rel_strength",
        rating_value=4, template="REL_STRENGTH_1Q",
        claim="AVGO outperforms its Layer-06 peers over 63 trading days",
        probability=0.65, resolution_date="2026-09-29",
        resolution_rule={"benchmark": "layer_cohort_ew",
                         "constituents": ["NVDA", "MU"], "horizon_td": 63},
        status="open",
    )
    base.update(over)
    return base


def test_append_creation_forces_today_and_assigns_id(tmp_path):
    p = tmp_path / "f.jsonl"
    snap = store.append_creation(_proposal(), path=p, today=TODAY)
    assert snap["created_date"] == "2026-06-26"
    assert snap["id"] == "fc_2026-06-26_AVGO_relstr_001"
    assert snap["status"] == "open" and snap["outcome"] is None
    # second forecast same day/ticker/template increments the sequence
    snap2 = store.append_creation(_proposal(), path=p, today=TODAY)
    assert snap2["id"] == "fc_2026-06-26_AVGO_relstr_002"


def test_append_creation_rejects_lookahead(tmp_path):
    p = tmp_path / "f.jsonl"
    with pytest.raises(store.ForecastError, match="look-ahead"):
        store.append_creation(_proposal(resolution_date="2026-06-26"), path=p, today=TODAY)


def test_append_creation_rejects_bad_probability(tmp_path):
    p = tmp_path / "f.jsonl"
    with pytest.raises(store.ForecastError, match="probability"):
        store.append_creation(_proposal(probability=1.0), path=p, today=TODAY)


def test_materialize_last_wins_and_open_excludes_resolved(tmp_path):
    p = tmp_path / "f.jsonl"
    snap = store.append_creation(_proposal(), path=p, today=TODAY)
    assert [f["id"] for f in store.open_forecasts(p)] == [snap["id"]]
    resolved = dict(snap, status="resolved", outcome=1,
                    resolved_date="2026-09-30", resolution_evidence="ev", resolver_confidence="auto")
    store.append_resolution(resolved, path=p)
    assert store.materialize(p)[snap["id"]]["status"] == "resolved"
    assert store.open_forecasts(p) == []


def test_append_resolution_rejects_immutable_change(tmp_path):
    p = tmp_path / "f.jsonl"
    snap = store.append_creation(_proposal(), path=p, today=TODAY)
    tampered = dict(snap, status="resolved", outcome=1, probability=0.99,
                    resolved_date="2026-09-30", resolution_evidence="ev", resolver_confidence="auto")
    with pytest.raises(store.ForecastError, match="immutable field probability"):
        store.append_resolution(tampered, path=p)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_forecast_store.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'forecast_store'`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/forecast_store.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_forecast_store.py -q`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/forecast_store.py tests/test_forecast_store.py
git commit -m "feat(calibration): append-only snapshot log with immutability + no-look-ahead guards"
```

---

### Task 3: `forecast_metrics.py` — Brier / Murphy / BSS / log loss

**Files:**
- Create: `scripts/forecast_metrics.py`
- Test: `tests/test_forecast_metrics.py`

**Interfaces:**
- Consumes: nothing (stdlib `math` only).
- Produces:
  - `DEFAULT_BINS: list[tuple[float,float]]`
  - `brier(ps, outs) -> float`
  - `base_rate(outs) -> float`
  - `uncertainty(outs) -> float`
  - `reliability_table(ps, outs, bins=DEFAULT_BINS) -> list[dict]` (each `{bin,n,p_bar,o_bar}`)
  - `murphy_decomposition(ps, outs, bins=DEFAULT_BINS) -> dict` (`REL,RES,UNC,BS_reconstructed,table`)
  - `brier_skill_score(ps, outs) -> float|None`
  - `log_loss(ps, outs, eps=1e-6) -> float`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_forecast_metrics.py
import forecast_metrics as m


def test_brier_known_value():
    # all p=0.5, half outcomes 1 -> every term 0.25
    assert abs(m.brier([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0]) - 0.25) < 1e-12


def test_murphy_identity_holds_for_discrete_forecasts():
    # forecasts placed at distinct bin centers -> zero within-bin spread -> exact identity
    ps = [0.2, 0.2, 0.8, 0.8]
    outs = [0, 0, 1, 1]
    d = m.murphy_decomposition(ps, outs)
    assert abs((d["REL"] - d["RES"] + d["UNC"]) - m.brier(ps, outs)) < 1e-12
    assert abs(d["BS_reconstructed"] - m.brier(ps, outs)) < 1e-12


def test_bss_sign_and_undefined():
    # a discriminating forecaster beats the base-rate null
    assert m.brier_skill_score([0.2, 0.2, 0.8, 0.8], [0, 0, 1, 1]) > 0
    # all-same outcome -> UNC=0 -> undefined
    assert m.brier_skill_score([0.6, 0.6], [1, 1]) is None


def test_log_loss_clips_confident_miss():
    # p=1.0 on a miss would be +inf without clipping; clipping keeps it finite
    assert m.log_loss([1.0], [0]) < 20.0


def test_reliability_table_bins_and_closed_right():
    rows = m.reliability_table([0.05, 1.0], [0, 1])
    assert rows[0]["n"] == 1 and rows[0]["p_bar"] == 0.05   # first bin
    assert rows[-1]["n"] == 1 and rows[-1]["o_bar"] == 1.0  # p==1.0 lands in last bin
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_forecast_metrics.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'forecast_metrics'`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/forecast_metrics.py
"""Calibration metrics: Brier, Murphy REL/RES/UNC, Brier Skill Score, log loss,
reliability table. Pure Python (no numpy) — CI-safe. See design spec §8.

p_i = forecast probability, o_i in {0,1} = outcome, N = count, o_bar = base rate.
"""
from __future__ import annotations

import math

DEFAULT_BINS = [(i / 10, (i + 1) / 10) for i in range(10)]  # [0,.1)...[.9,1.0]


def brier(ps, outs) -> float:
    n = len(ps)
    return sum((p - o) ** 2 for p, o in zip(ps, outs)) / n


def base_rate(outs) -> float:
    return sum(outs) / len(outs)


def uncertainty(outs) -> float:
    o = base_rate(outs)
    return o * (1 - o)


def _bin_index(p, bins) -> int:
    for i, (lo, hi) in enumerate(bins):
        if lo <= p < hi:
            return i
        if i == len(bins) - 1 and p == hi:   # last bin closed on the right (p==1.0)
            return i
    return len(bins) - 1


def reliability_table(ps, outs, bins=DEFAULT_BINS) -> list[dict]:
    rows = []
    for i, (lo, hi) in enumerate(bins):
        idx = [j for j in range(len(ps)) if _bin_index(ps[j], bins) == i]
        if not idx:
            rows.append({"bin": (lo, hi), "n": 0, "p_bar": None, "o_bar": None})
            continue
        n = len(idx)
        rows.append({"bin": (lo, hi), "n": n,
                     "p_bar": sum(ps[j] for j in idx) / n,
                     "o_bar": sum(outs[j] for j in idx) / n})
    return rows


def murphy_decomposition(ps, outs, bins=DEFAULT_BINS) -> dict:
    n = len(ps)
    o = base_rate(outs)
    table = reliability_table(ps, outs, bins)
    rel = sum(r["n"] * (r["p_bar"] - r["o_bar"]) ** 2 for r in table if r["n"]) / n
    res = sum(r["n"] * (r["o_bar"] - o) ** 2 for r in table if r["n"]) / n
    unc = o * (1 - o)
    return {"REL": rel, "RES": res, "UNC": unc,
            "BS_reconstructed": rel - res + unc, "table": table}


def brier_skill_score(ps, outs):
    unc = uncertainty(outs)
    if unc == 0:
        return None   # all-same-outcome -> BSS undefined
    return 1 - brier(ps, outs) / unc


def log_loss(ps, outs, eps=1e-6) -> float:
    n = len(ps)
    total = 0.0
    for p, o in zip(ps, outs):
        p = min(max(p, eps), 1 - eps)
        total += o * math.log(p) + (1 - o) * math.log(1 - p)
    return -total / n
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_forecast_metrics.py -q`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/forecast_metrics.py tests/test_forecast_metrics.py
git commit -m "feat(calibration): Brier/Murphy/BSS/log-loss metrics with exact decomposition identity"
```

---

### Task 4: `forecast_cohorts.py` — frozen peer basket

**Files:**
- Create: `scripts/forecast_cohorts.py`
- Test: `tests/test_forecast_cohorts.py`

**Interfaces:**
- Consumes: openpyxl; the Watchlist tab of `00-master/ai_supply_chain_scoring.xlsx`.
- Produces:
  - `SCORING_PATH: Path`, `MIN_PEERS: int`, `TICKER_COL=1`, `LAYER_COL=3`
  - `read_watchlist_rows(scoring_path=SCORING_PATH) -> list[tuple[str,str]]` (ticker, layer_num)
  - `build_frozen_cohort(ticker, scoring_path=SCORING_PATH, rows=None) -> tuple[str, dict]` returns `(layer_num, rule)` where `rule = {"benchmark","constituents","horizon_td"}`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_forecast_cohorts.py
from openpyxl import Workbook
import forecast_cohorts as c


def _scoring(tmp_path, names_layers):
    wb = Workbook()
    ws = wb.active
    ws.title = "Watchlist"
    ws.append(["Ticker", "Company", "Layer"])
    for t, lay in names_layers:
        ws.append([t, f"{t} Inc", lay])
    p = tmp_path / "scoring.xlsx"
    wb.save(p)
    return p


def test_cohort_groups_by_layer_and_excludes_self(tmp_path):
    p = _scoring(tmp_path, [("AVGO", "06 Silicon"), ("NVDA", "06 Silicon"),
                            ("MU", "06 Silicon"), ("ALAB", "06 Silicon"),
                            ("SNDK", "06 Silicon"), ("WDC", "06 Silicon"),
                            ("FIX", "03 DC")])
    layer, rule = c.build_frozen_cohort("AVGO", scoring_path=p)
    assert layer == "06"
    assert rule["benchmark"] == "layer_cohort_ew"
    assert "AVGO" not in rule["constituents"]
    assert rule["constituents"] == ["ALAB", "MU", "NVDA", "SNDK", "WDC"]  # sorted, self excluded
    assert rule["horizon_td"] == 63


def test_thin_layer_falls_back_to_smh(tmp_path):
    p = _scoring(tmp_path, [("TSM", "05 Fabs"), ("UMC", "05 Fabs"), ("GFS", "05 Fabs")])
    layer, rule = c.build_frozen_cohort("TSM", scoring_path=p)
    assert layer == "05"
    assert rule["benchmark"] == "SMH"
    assert rule["constituents"] == ["SMH"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_forecast_cohorts.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'forecast_cohorts'`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/forecast_cohorts.py
"""Build a frozen equal-weight peer basket for a ticker from the Watchlist.

The peer list is frozen into resolution_rule at forecast creation so quarterly
roster churn can't retroactively change the benchmark (no membership look-ahead).
Layers with fewer than MIN_PEERS peers fall back to SMH.

openpyxl only (CI-safe). See design spec §6/§7.
"""
from __future__ import annotations

from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
SCORING_PATH = ROOT / "00-master" / "ai_supply_chain_scoring.xlsx"

TICKER_COL = 1
LAYER_COL = 3
HORIZON_TD = 63
MIN_PEERS = 6   # fewer same-layer peers than this -> SMH fallback


def read_watchlist_rows(scoring_path: Path = SCORING_PATH) -> list[tuple[str, str]]:
    """(ticker, layer_num) for every Watchlist row. layer_num = first token of col C."""
    ws = load_workbook(scoring_path, read_only=True)["Watchlist"]
    assert ws.cell(row=1, column=TICKER_COL).value == "Ticker", "Watchlist col A is not Ticker"
    assert ws.cell(row=1, column=LAYER_COL).value == "Layer", "Watchlist col C is not Layer"
    rows = []
    for r in range(2, ws.max_row + 1):
        t = ws.cell(row=r, column=TICKER_COL).value
        layer = ws.cell(row=r, column=LAYER_COL).value
        if t and layer:
            rows.append((str(t).strip().upper(), str(layer).strip().split()[0]))
    return rows


def build_frozen_cohort(ticker: str, scoring_path: Path = SCORING_PATH,
                        rows: list[tuple[str, str]] | None = None) -> tuple[str, dict]:
    """Return (layer_num, frozen benchmark rule) for `ticker`.

    rule = {"benchmark","constituents","horizon_td"} — a layer EW basket, or the
    SMH fallback when the layer is too thin. `rows` is injectable for tests.
    """
    ticker = ticker.upper()
    rows = rows if rows is not None else read_watchlist_rows(scoring_path)
    layer = next((lay for t, lay in rows if t == ticker), None)
    if layer is None:
        raise ValueError(f"{ticker} not found on Watchlist")
    peers = sorted({t for t, lay in rows if lay == layer and t != ticker})
    if len(peers) < MIN_PEERS:
        return layer, {"benchmark": "SMH", "constituents": ["SMH"], "horizon_td": HORIZON_TD}
    return layer, {"benchmark": "layer_cohort_ew", "constituents": peers, "horizon_td": HORIZON_TD}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_forecast_cohorts.py -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/forecast_cohorts.py tests/test_forecast_cohorts.py
git commit -m "feat(calibration): frozen layer-cohort peer basket with SMH thin-layer fallback"
```

---

### Task 5: `forecast_resolvers.py` — REL_STRENGTH_1Q resolver

**Files:**
- Create: `scripts/forecast_resolvers.py`
- Test: `tests/test_forecast_resolvers.py`

**Interfaces:**
- Consumes: stdlib only; a `price_loader(ticker, start_date) -> dict[date, float]` injected by the caller.
- Produces:
  - `@dataclass Resolution(status, outcome, resolved_date, evidence, resolver_confidence)`
  - `resolve_rel_strength_1q(forecast, *, price_loader, today=None) -> Resolution`
  - `RESOLVERS: dict[str, callable]`
  - `resolution_date_for(created: date, horizon_td: int, buffer_days=7) -> date`
  - constants `HORIZON_BUFFER_DAYS`, `GRACE_DAYS`, `MISSING_CONSTITUENT_TOLERANCE`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_forecast_resolvers.py
import datetime as dt
import forecast_resolvers as r

CREATED = dt.date(2026, 6, 26)


def _forecast(benchmark="layer_cohort_ew", constituents=("NVDA", "MU"), res="2026-09-29"):
    return {"ticker": "AVGO", "created_date": CREATED.isoformat(),
            "resolution_date": res,
            "resolution_rule": {"benchmark": benchmark,
                                "constituents": list(constituents), "horizon_td": 3}}


def _ramp(start, step, n=10):
    # 10 daily bars from CREATED; close = start * (1+step)^i
    return {CREATED + dt.timedelta(days=i): start * (1 + step) ** i for i in range(n)}


def _loader(table):
    return lambda ticker, start: table[ticker]


def test_self_beats_cohort_outcome_1():
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.01), "MU": _ramp(100, 0.0)}
    res = r.resolve_rel_strength_1q(_forecast(), price_loader=_loader(table), today=dt.date(2026, 10, 1))
    assert res.status == "resolved" and res.outcome == 1
    assert "AVGO" in res.evidence and res.resolver_confidence == "auto"


def test_self_loses_outcome_0():
    table = {"AVGO": _ramp(100, 0.0), "NVDA": _ramp(100, 0.05), "MU": _ramp(100, 0.05)}
    res = r.resolve_rel_strength_1q(_forecast(), price_loader=_loader(table), today=dt.date(2026, 10, 1))
    assert res.status == "resolved" and res.outcome == 0


def test_smh_fallback_path():
    table = {"AVGO": _ramp(100, 0.05), "SMH": _ramp(100, 0.01)}
    res = r.resolve_rel_strength_1q(_forecast(benchmark="SMH", constituents=("SMH",)),
                                    price_loader=_loader(table), today=dt.date(2026, 10, 1))
    assert res.status == "resolved" and res.outcome == 1 and "SMH" in res.evidence


def test_insufficient_bars_stays_open_then_needs_review():
    table = {"AVGO": _ramp(100, 0.05, n=2), "NVDA": _ramp(100, 0.01, n=2), "MU": _ramp(100, 0.0, n=2)}
    loader = _loader(table)
    f = _forecast()
    # within grace of resolution_date -> stay open
    early = r.resolve_rel_strength_1q(f, price_loader=loader, today=dt.date(2026, 9, 30))
    assert early.status == "open"
    # 30+ days past resolution_date and still short -> needs_review
    late = r.resolve_rel_strength_1q(f, price_loader=loader, today=dt.date(2026, 11, 15))
    assert late.status == "needs_review" and late.outcome is None


def test_degraded_cohort_needs_review():
    table = {"AVGO": _ramp(100, 0.05), "NVDA": {}, "MU": {}}  # both peers missing
    res = r.resolve_rel_strength_1q(_forecast(), price_loader=_loader(table), today=dt.date(2026, 10, 1))
    assert res.status == "needs_review" and "degraded" in res.evidence


def test_resolution_date_for_weekday_math():
    # 3 weekdays forward from Fri 2026-06-26 -> Wed 2026-07-01, +7 buffer -> 2026-07-08
    assert r.resolution_date_for(dt.date(2026, 6, 26), 3) == dt.date(2026, 7, 8)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_forecast_resolvers.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'forecast_resolvers'`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/forecast_resolvers.py
"""Resolution templates for forecast calibration (CLAUDE.md rule 17).

Each resolver is deterministic: resolve(forecast, *, price_loader, today) ->
Resolution. Price data is INJECTED (price_loader), never fetched here, so
resolvers unit-test on synthetic series under the CI env (no yfinance). The
yfinance-backed loader lives in resolve_forecasts.py.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

HORIZON_BUFFER_DAYS = 7        # padding on resolution_date past the horizon bar
GRACE_DAYS = 30               # keep retrying an under-filled series this long before needs_review
MISSING_CONSTITUENT_TOLERANCE = 0.25


@dataclass
class Resolution:
    status: str                       # resolved | needs_review | open (not gradable yet)
    outcome: int | None               # 1 | 0 | None
    resolved_date: str | None
    evidence: str | None
    resolver_confidence: str | None   # auto | None


def resolution_date_for(created: dt.date, horizon_td: int,
                        buffer_days: int = HORIZON_BUFFER_DAYS) -> dt.date:
    """horizon_td weekdays forward from created + buffer (stdlib, holiday-naive).
    A scheduling date; the resolver always re-checks actual bar count."""
    d, counted = created, 0
    while counted < horizon_td:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:    # Mon-Fri
            counted += 1
    return d + dt.timedelta(days=buffer_days)


def _horizon_return(prices: dict, created: dt.date, horizon_td: int):
    """Return over the first bar >= created to the bar horizon_td positions later.
    None if insufficient bars or a zero base."""
    bars = sorted((d, c) for d, c in prices.items() if d >= created and c is not None)
    if len(bars) < horizon_td + 1:
        return None
    base, horizon = bars[0][1], bars[horizon_td][1]
    if not base:
        return None
    return horizon / base - 1.0, bars[0][0], bars[horizon_td][0]


def resolve_rel_strength_1q(forecast: dict, *, price_loader, today: dt.date | None = None) -> Resolution:
    today = today or dt.date.today()
    rule = forecast["resolution_rule"]
    horizon = rule["horizon_td"]
    created = dt.date.fromisoformat(forecast["created_date"])
    res_date = dt.date.fromisoformat(forecast["resolution_date"])
    ticker = forecast["ticker"]

    self_calc = _horizon_return(price_loader(ticker, created), created, horizon)
    if self_calc is None:
        if today <= res_date + dt.timedelta(days=GRACE_DAYS):
            return Resolution("open", None, None, None, None)
        return Resolution("needs_review", None, None,
                          f"{ticker}: <{horizon + 1} trading bars by {today} "
                          f"({GRACE_DAYS}d past resolution_date)", None)
    r_self, d0, dh = self_calc

    constituents = rule["constituents"]
    rets, missing = [], []
    for cn in constituents:
        calc = _horizon_return(price_loader(cn, created), created, horizon)
        (rets.append(calc[0]) if calc is not None else missing.append(cn))
    if not rets or len(missing) / len(constituents) > MISSING_CONSTITUENT_TOLERANCE:
        return Resolution("needs_review", None, None,
                          f"cohort degraded: {len(missing)}/{len(constituents)} constituents missing data",
                          None)
    r_bench = sum(rets) / len(rets)
    outcome = 1 if r_self > r_bench else 0
    evidence = (f"{ticker} {r_self * 100:+.1f}% vs {rule['benchmark']} ({len(rets)} names) "
                f"{r_bench * 100:+.1f}%, {d0}→{dh} ({horizon} td), yfinance adj close → {outcome}")
    return Resolution("resolved", outcome, today.isoformat(), evidence, "auto")


RESOLVERS = {"REL_STRENGTH_1Q": resolve_rel_strength_1q}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_forecast_resolvers.py -q`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/forecast_resolvers.py tests/test_forecast_resolvers.py
git commit -m "feat(calibration): REL_STRENGTH_1Q resolver with injectable prices + grace/needs_review handling"
```

---

### Task 6: `resolve_forecasts.py` — weekly resolution CLI

**Files:**
- Create: `scripts/resolve_forecasts.py`
- Test: `tests/test_resolve_forecasts.py`

**Interfaces:**
- Consumes: `forecast_store` (`open_forecasts`, `append_resolution`, `flag`, `FORECASTS_PATH`), `forecast_resolvers.RESOLVERS`. yfinance lazily inside `yfinance_price_loader`.
- Produces:
  - `yfinance_price_loader(ticker, start_date) -> dict[date,float]`
  - `resolve_due(today, price_loader, dry_run, path=store.FORECASTS_PATH) -> list[dict]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_resolve_forecasts.py
import datetime as dt
import forecast_store as store
import resolve_forecasts as rf

CREATED = dt.date(2026, 6, 26)


def _seed_open(path):
    snap = dict(ticker="AVGO", layer="06", dimension="momentum.rel_strength",
                rating_value=4, template="REL_STRENGTH_1Q",
                claim="AVGO vs Layer-06 over 3 td", probability=0.65,
                resolution_date="2026-07-08",
                resolution_rule={"benchmark": "layer_cohort_ew",
                                 "constituents": ["NVDA", "MU"], "horizon_td": 3},
                status="open")
    return store.append_creation(snap, path=path, today=CREATED)


def _ramp(start, step, n=10):
    return {CREATED + dt.timedelta(days=i): start * (1 + step) ** i for i in range(n)}


def test_resolve_due_appends_resolution(tmp_path):
    p = tmp_path / "f.jsonl"
    created = _seed_open(p)
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.0), "MU": _ramp(100, 0.0)}
    loader = lambda t, s: table[t]
    results = rf.resolve_due(dt.date(2026, 8, 1), loader, dry_run=False, path=p)
    assert len(results) == 1 and results[0]["outcome"] == 1
    # the resolution snapshot was appended; state is now resolved, no longer open
    assert store.materialize(p)[created["id"]]["status"] == "resolved"
    assert store.open_forecasts(p) == []


def test_dry_run_writes_nothing(tmp_path):
    p = tmp_path / "f.jsonl"
    _seed_open(p)
    table = {"AVGO": _ramp(100, 0.05), "NVDA": _ramp(100, 0.0), "MU": _ramp(100, 0.0)}
    rf.resolve_due(dt.date(2026, 8, 1), lambda t, s: table[t], dry_run=True, path=p)
    assert len(store.open_forecasts(p)) == 1   # still open
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_resolve_forecasts.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'resolve_forecasts'`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/resolve_forecasts.py
"""Resolve due open forecasts (CLAUDE.md rule 17). Weekly via /weekly-scan.

  python3 scripts/resolve_forecasts.py --dry-run    # show what would resolve
  python3 scripts/resolve_forecasts.py              # resolve + append snapshots

yfinance is imported lazily inside the price loader so this module (and the core
forecast_* modules) import cleanly under the deploy-site CI env (openpyxl+pytest).
"""
from __future__ import annotations

import sys
import time
import argparse
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import forecast_store as store
from forecast_resolvers import RESOLVERS


def yfinance_price_loader(ticker: str, start_date: dt.date) -> dict:
    """{date: adj_close} from start_date forward. Lazy yfinance import + throttle."""
    import yfinance as yf
    hist = yf.Ticker(ticker).history(start=start_date.isoformat(), auto_adjust=True)
    time.sleep(0.3)   # serialize, per CLAUDE.md
    if hist is None or hist.empty:
        return {}
    return {idx.date(): float(row["Close"])
            for idx, row in hist.iterrows() if row["Close"] == row["Close"]}  # drop NaN


def resolve_due(today: dt.date, price_loader, dry_run: bool,
                path: Path = store.FORECASTS_PATH) -> list[dict]:
    due = [f for f in store.open_forecasts(path)
           if dt.date.fromisoformat(f["resolution_date"]) <= today]
    results = []
    for f in due:
        resolver = RESOLVERS.get(f["template"])
        if resolver is None:
            store.flag(f'{f["id"]}: no resolver for template {f["template"]}')
            continue
        res = resolver(f, price_loader=price_loader, today=today)
        if res.status == "open":
            continue   # not gradable yet (insufficient bars within grace)
        snap = dict(f, status=res.status, outcome=res.outcome,
                    resolved_date=res.resolved_date,
                    resolution_evidence=res.evidence,
                    resolver_confidence=res.resolver_confidence)
        results.append(snap)
        print(f'{f["id"]}: {res.status}'
              + (f' outcome={res.outcome}' if res.outcome is not None else '')
              + (f' — {res.evidence}' if res.evidence else ''))
        if not dry_run:
            store.append_resolution(snap, path=path)
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    today = dt.date.today()
    results = resolve_due(today, yfinance_price_loader, args.dry_run)
    resolved = sum(1 for r in results if r["status"] == "resolved")
    review = sum(1 for r in results if r["status"] == "needs_review")
    print(f'\n{resolved} resolved, {review} need review'
          + (' (dry run — nothing written)' if args.dry_run else ''))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_resolve_forecasts.py -q`
Expected: PASS (2 tests). (Imports cleanly without yfinance because the loader's import is lazy.)

- [ ] **Step 5: Commit**

```bash
git add scripts/resolve_forecasts.py tests/test_resolve_forecasts.py
git commit -m "feat(calibration): weekly resolve_forecasts CLI with lazy yfinance loader"
```

---

### Task 7: `log_forecast.py` — forecast logging + Phase-1 seeding

**Files:**
- Create: `scripts/log_forecast.py`
- Test: `tests/test_log_forecast.py`

**Interfaces:**
- Consumes: `forecast_store`, `forecast_cohorts` (`build_frozen_cohort`, `read_watchlist_rows`), `forecast_resolvers.resolution_date_for`, `refresh_objective_inputs.resolve_targets` + `SCORING_PATH`/`PORTFOLIO_PATH`.
- Produces:
  - `build_proposals(today, scoring_path=SCORING_PATH, portfolio_path=PORTFOLIO_PATH) -> list[dict]`
  - `print_table(proposals) -> None`
  - constants `DEFAULT_PROB`, `BASE_RATE_PROB`, `DIMENSION`, `TEMPLATE`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_log_forecast.py
import datetime as dt
from openpyxl import Workbook
import log_forecast as lf

TODAY = dt.date(2026, 6, 26)


def _scoring(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Watchlist"
    headers = ["Ticker", "Company", "Layer"] + [None] * 23 + ["Rel Str"]  # col 27 (AA)
    ws.append(headers)
    # 6 Layer-06 names so AVGO gets a real cohort; ratings drive default prob
    data = [("AVGO", 4), ("NVDA", 5), ("MU", 3), ("ALAB", 2), ("SNDK", 1), ("WDC", 4)]
    for t, rating in data:
        row = [t, f"{t} Inc", "06 Silicon"] + [None] * 23 + [rating]
        ws.append(row)
    p = tmp_path / "scoring.xlsx"
    wb.save(p)
    return p


def test_build_proposals_maps_rating_to_default_prob(tmp_path, monkeypatch):
    p = _scoring(tmp_path)
    monkeypatch.setattr(lf, "resolve_targets", lambda *a, **k: ["AVGO", "NVDA"])
    proposals = lf.build_proposals(TODAY, scoring_path=p)
    by_ticker = {x["ticker"]: x for x in proposals}
    assert by_ticker["AVGO"]["probability"] == lf.DEFAULT_PROB[4]   # rating 4 -> 0.65
    assert by_ticker["NVDA"]["probability"] == lf.DEFAULT_PROB[5]   # rating 5 -> 0.80
    a = by_ticker["AVGO"]
    assert a["template"] == "REL_STRENGTH_1Q" and a["dimension"] == "momentum.rel_strength"
    assert a["layer"] == "06" and a["rating_value"] == 4
    assert "AVGO" not in a["resolution_rule"]["constituents"]
    assert dt.date.fromisoformat(a["resolution_date"]) > TODAY   # no look-ahead


def test_missing_rating_defaults_to_base_rate(tmp_path, monkeypatch):
    p = _scoring(tmp_path)
    monkeypatch.setattr(lf, "resolve_targets", lambda *a, **k: ["MU"])
    # blank MU's rating
    from openpyxl import load_workbook
    wb = load_workbook(p); ws = wb["Watchlist"]
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value == "MU":
            ws.cell(r, 27).value = None
    wb.save(p)
    proposals = lf.build_proposals(TODAY, scoring_path=p)
    assert proposals[0]["probability"] == lf.BASE_RATE_PROB
    assert proposals[0]["rating_value"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_log_forecast.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'log_forecast'`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/log_forecast.py
"""Append validated forecasts to tracking/forecasts.jsonl (CLAUDE.md rule 17).

Phase 1 seeds the portfolio in one pass:

  python3 scripts/log_forecast.py --seed-portfolio --dry-run        # propose + print
  python3 scripts/log_forecast.py --seed-portfolio --apply \
        --overrides /path/overrides.json                            # write (Dom's probs)

overrides.json: {"AVGO": 0.60, "NVDA": 0.72}  (ticker -> probability; the override
is the training signal, not the rating-derived default).

openpyxl only (no yfinance): reads ratings + builds the frozen cohort; never
fetches prices. See design spec §7.
"""
from __future__ import annotations

import sys
import json
import argparse
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openpyxl import load_workbook

import forecast_store as store
import forecast_cohorts as cohorts
from forecast_resolvers import resolution_date_for
from refresh_objective_inputs import resolve_targets, SCORING_PATH, PORTFOLIO_PATH

DIMENSION = "momentum.rel_strength"
TEMPLATE = "REL_STRENGTH_1Q"
HORIZON_TD = 63
RELSTR_COL = 27                              # AA — 'Rel Str' (momentum subjective rating)
RELSTR_HEADER = "Rel Str"
DEFAULT_PROB = {5: 0.80, 4: 0.65, 3: 0.55, 2: 0.42, 1: 0.28}
BASE_RATE_PROB = 0.55


def _relstr_ratings(scoring_path=SCORING_PATH) -> dict:
    ws = load_workbook(scoring_path, read_only=True)["Watchlist"]
    assert ws.cell(1, RELSTR_COL).value == RELSTR_HEADER, \
        f"Watchlist col {RELSTR_COL} is not {RELSTR_HEADER!r} — schema drift, abort"
    out = {}
    for r in range(2, ws.max_row + 1):
        t = ws.cell(r, 1).value
        if not t:
            continue
        v = ws.cell(r, RELSTR_COL).value
        out[str(t).strip().upper()] = int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    return out


def _claim(ticker: str, rule: dict, layer: str) -> str:
    if rule["benchmark"] == "SMH":
        return f"{ticker} total return outperforms SMH over the next {rule['horizon_td']} trading days"
    return (f"{ticker} total return outperforms its frozen Layer-{layer} equal-weight "
            f"peer basket over the next {rule['horizon_td']} trading days")


def build_proposals(today: dt.date, scoring_path=SCORING_PATH, portfolio_path=PORTFOLIO_PATH) -> list[dict]:
    names = resolve_targets("portfolio", scoring_path=scoring_path, portfolio_path=portfolio_path)
    ratings = _relstr_ratings(scoring_path)
    rows = cohorts.read_watchlist_rows(scoring_path)
    res_date = resolution_date_for(today, HORIZON_TD).isoformat()
    proposals = []
    for t in names:
        layer, rule = cohorts.build_frozen_cohort(t, rows=rows)
        rating = ratings.get(t)
        prob = DEFAULT_PROB.get(rating, BASE_RATE_PROB)
        if rating is None:
            store.flag(f"{t}: no Relative Strength rating — default {BASE_RATE_PROB}")
        proposals.append(dict(
            ticker=t, layer=layer, dimension=DIMENSION, rating_value=rating,
            template=TEMPLATE, claim=_claim(t, rule, layer), probability=prob,
            resolution_date=res_date, resolution_rule=rule, status="open"))
    return proposals


def print_table(proposals: list[dict]) -> None:
    print(f'{"Ticker":<7}{"Layer":<6}{"Rating":>7}{"Prob":>7}  Benchmark')
    for p in proposals:
        rating = p["rating_value"] if p["rating_value"] is not None else "—"
        rule = p["resolution_rule"]
        print(f'{p["ticker"]:<7}{p["layer"]:<6}{str(rating):>7}{p["probability"]:>7.2f}  '
              f'{rule["benchmark"]} ({len(rule["constituents"])})')
    if proposals:
        print(f'\nresolution_date: {proposals[0]["resolution_date"]}')


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed-portfolio", action="store_true",
                    help="propose one REL_STRENGTH_1Q forecast per portfolio name")
    ap.add_argument("--dry-run", action="store_true", help="print proposals, write nothing")
    ap.add_argument("--apply", action="store_true", help="write proposals to the log")
    ap.add_argument("--overrides", help="JSON file mapping ticker -> probability")
    args = ap.parse_args()

    if not args.seed_portfolio:
        ap.error("Phase 1 supports only --seed-portfolio")
    if args.dry_run == args.apply:
        ap.error("choose exactly one of --dry-run / --apply")

    today = dt.date.today()
    proposals = build_proposals(today)

    if args.overrides:
        ov = {k.upper(): float(v) for k, v in json.loads(Path(args.overrides).read_text()).items()}
        for p in proposals:
            if p["ticker"] in ov:
                p["probability"] = ov[p["ticker"]]

    print_table(proposals)
    if args.dry_run:
        print("\n(dry run — nothing written)")
        return

    for p in proposals:
        snap = store.append_creation(p, today=today)
        print(f'logged {snap["id"]}  p={snap["probability"]:.2f}')
    print(f'\nwrote {len(proposals)} forecasts to {store.FORECASTS_PATH}')


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_log_forecast.py -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/log_forecast.py tests/test_log_forecast.py
git commit -m "feat(calibration): log_forecast CLI with portfolio seeding + rating-derived default probabilities"
```

---

### Task 8: `calibration_report.py` — quarterly report

**Files:**
- Create: `scripts/calibration_report.py`
- Test: `tests/test_calibration_report.py`

**Interfaces:**
- Consumes: `forecast_store` (`materialize`, `ROOT`, `FORECASTS_PATH`), `forecast_metrics.*`. matplotlib lazily.
- Produces:
  - `build_report(today, path=store.FORECASTS_PATH) -> str`
  - `maybe_render_curve(today, path=store.FORECASTS_PATH) -> bool`
  - constants `REPORT_PATH`, `CURVE_PATH`, `MIN_N_FOR_CURVE`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_calibration_report.py
import datetime as dt
import forecast_store as store
import calibration_report as cr

CREATED = dt.date(2026, 6, 26)


def _resolved(path, ticker, layer, prob, outcome):
    snap = dict(ticker=ticker, layer=layer, dimension="momentum.rel_strength",
                rating_value=4, template="REL_STRENGTH_1Q", claim="c",
                probability=prob, resolution_date="2026-09-29",
                resolution_rule={"benchmark": "SMH", "constituents": ["SMH"], "horizon_td": 63},
                status="open")
    created = store.append_creation(snap, path=path, today=CREATED)
    store.append_resolution(dict(created, status="resolved", outcome=outcome,
                                 resolved_date="2026-09-30", resolution_evidence="ev",
                                 resolver_confidence="auto"), path=path)


def test_build_report_has_sections_and_void_rate(tmp_path):
    p = tmp_path / "f.jsonl"
    _resolved(p, "AVGO", "06", 0.8, 1)
    _resolved(p, "NVDA", "06", 0.2, 0)
    _resolved(p, "APP", "10", 0.6, 0)
    report = cr.build_report(dt.date(2026, 10, 1), path=p)
    assert "# Forecast Calibration Report" in report
    assert "### Overall" in report and "## By dimension" in report and "## By layer" in report
    assert "momentum.rel_strength" in report
    assert "Layer 06" in report and "Layer 10" in report
    assert "Brier" in report and "BSS" in report
    assert "void rate: 0%" in report   # nothing in needs_review/void


def test_empty_log_is_graceful(tmp_path):
    p = tmp_path / "f.jsonl"
    report = cr.build_report(dt.date(2026, 10, 1), path=p)
    assert "No forecasts logged" in report


def test_small_n_warns_not_to_overinterpret(tmp_path):
    p = tmp_path / "f.jsonl"
    _resolved(p, "AVGO", "06", 0.8, 1)
    report = cr.build_report(dt.date(2026, 10, 1), path=p)
    assert "do not over-interpret" in report
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_calibration_report.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'calibration_report'`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/calibration_report.py
"""Generate tracking/calibration-report.md from resolved forecasts (rule 17).

Quarterly via /rescore-quarterly. matplotlib is optional (lazy, guarded); the
markdown table is the primary artifact (CI and the daily cron have no matplotlib).
"""
from __future__ import annotations

import sys
import argparse
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import forecast_store as store
import forecast_metrics as metrics

REPORT_PATH = store.ROOT / "tracking" / "calibration-report.md"
CURVE_PATH = store.ROOT / "tracking" / "calibration-curve.png"
MIN_N_FOR_CURVE = 30


def _resolved(state) -> list[dict]:
    return [f for f in state.values() if f["status"] == "resolved" and f["outcome"] in (0, 1)]


def _section(label, ps, outs) -> list[str]:
    n = len(ps)
    if n == 0:
        return [f"### {label}", "", "_No resolved forecasts._", ""]
    bs = metrics.brier(ps, outs)
    bss = metrics.brier_skill_score(ps, outs)
    dec = metrics.murphy_decomposition(ps, outs)
    ll = metrics.log_loss(ps, outs)
    lines = [f"### {label}", "",
             f"- N: **{n}**  ·  base rate: {metrics.base_rate(outs):.2f}",
             f"- Brier: **{bs:.4f}**  ·  log loss: {ll:.4f}",
             f"- REL (lower better): {dec['REL']:.4f}  ·  RES (higher better): {dec['RES']:.4f}  ·  UNC: {dec['UNC']:.4f}"]
    if bss is None:
        lines.append("- BSS: undefined (one-sided outcomes)")
    else:
        lines.append(f"- BSS vs base rate: **{bss:.3f}** — "
                     + ("beats the base-rate null ✅" if bss > 0 else "no skill over the base rate ❌"))
    if n < MIN_N_FOR_CURVE:
        lines += ["", f"> ⚠️ N={n} < {MIN_N_FOR_CURVE}: the decomposition is noise — do not over-interpret."]
    lines += ["", "| bin | n | p̄ | ō |", "|---|---|---|---|"]
    for row in dec["table"]:
        if row["n"]:
            lines.append(f'| {row["bin"][0]:.1f}–{row["bin"][1]:.1f} | {row["n"]} '
                         f'| {row["p_bar"]:.2f} | {row["o_bar"]:.2f} |')
    lines.append("")
    return lines


def build_report(today: dt.date, path: Path = store.FORECASTS_PATH) -> str:
    state = store.materialize(path)
    out = ["# Forecast Calibration Report", "", f"_Generated {today.isoformat()}_", ""]
    if not state:
        out.append("No forecasts logged yet.")
        return "\n".join(out) + "\n"
    resolved = _resolved(state)
    review = sum(1 for f in state.values() if f["status"] in ("needs_review", "void"))
    out += [f"Total: {len(state)}  ·  resolved: {len(resolved)}  ·  "
            f"needs_review/void: {review}  ·  void rate: {review / len(state):.0%}", ""]
    ps = [f["probability"] for f in resolved]
    outs = [f["outcome"] for f in resolved]
    out += _section("Overall", ps, outs)
    out += ["## By dimension", ""]
    for dim in sorted({f["dimension"] for f in resolved if f.get("dimension")}):
        sub = [f for f in resolved if f["dimension"] == dim]
        out += _section(dim, [f["probability"] for f in sub], [f["outcome"] for f in sub])
    out += ["## By layer", ""]
    for layer in sorted({f["layer"] for f in resolved}):
        sub = [f for f in resolved if f["layer"] == layer]
        out += _section(f"Layer {layer}", [f["probability"] for f in sub], [f["outcome"] for f in sub])
    return "\n".join(out) + "\n"


def maybe_render_curve(today: dt.date, path: Path = store.FORECASTS_PATH) -> bool:
    resolved = _resolved(store.materialize(path))
    if len(resolved) < MIN_N_FOR_CURVE:
        return False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False
    ps = [f["probability"] for f in resolved]
    outs = [f["outcome"] for f in resolved]
    table = metrics.reliability_table(ps, outs)
    xs = [r["p_bar"] for r in table if r["n"]]
    ys = [r["o_bar"] for r in table if r["n"]]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], "--", color="gray")
    ax.plot(xs, ys, "o-")
    ax.set_xlabel("forecast probability")
    ax.set_ylabel("observed frequency")
    ax.set_title(f"Reliability ({today.isoformat()})")
    fig.savefig(CURVE_PATH, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="print, do not write the file")
    args = ap.parse_args()
    today = dt.date.today()
    report = build_report(today)
    if args.dry_run:
        print(report)
        return
    REPORT_PATH.write_text(report)
    rendered = maybe_render_curve(today)
    print(f"wrote {REPORT_PATH}" + (f" + {CURVE_PATH}" if rendered else " (no PNG)"))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_calibration_report.py -q`
Expected: PASS (3 tests).

- [ ] **Step 5: Run the full suite to confirm nothing regressed**

Run: `python -m pytest tests -q`
Expected: PASS (all prior tests + the new forecast tests).

- [ ] **Step 6: Commit**

```bash
git add scripts/calibration_report.py tests/test_calibration_report.py
git commit -m "feat(calibration): calibration_report with per-dimension/per-layer breakdown + optional reliability PNG"
```

---

### Task 9: Workflow integration — weekly + quarterly hooks

**Files:**
- Modify: `.claude/commands/weekly-scan.md` (add a step after the rating-integrity step)
- Modify: `.claude/commands/rescore-quarterly.md` (add a report-regeneration step)

**Interfaces:**
- Consumes: the three CLIs from Tasks 6–8.
- Produces: nothing in code; documented routine steps.

- [ ] **Step 1: Read the two skill files to find the exact insertion points**

Run:
```bash
grep -n "^### Step\|^## \|^### " .claude/commands/weekly-scan.md
grep -n "^### Step\|^## \|^[0-9]\." .claude/commands/rescore-quarterly.md
```
Expected: weekly-scan ends with the Step 8 rating-integrity step; rescore-quarterly has steps up to the report. Note the heading style used (match it exactly).

- [ ] **Step 2: Add the weekly resolve step**

Append a new step after the final existing step in `.claude/commands/weekly-scan.md` (match the file's heading style; the text below is the content, adjust the heading number to follow the last one):

```markdown
### Step 9: Resolve due forecasts (calibration loop, rule 17)

Run the forecast resolver to grade any forecasts whose `resolution_date` has arrived:

    python3 scripts/resolve_forecasts.py --dry-run
    python3 scripts/resolve_forecasts.py

Report, in the scan output:
- newly **resolved** forecasts (id, outcome, the cited evidence string),
- anything routed to **needs_review** (these need a human-confirmed resolution),
- the running **void/needs_review rate** (a high rate means the resolution rules are too vague — fix the rules, don't fudge the grades).

This never edits a prior line in `tracking/forecasts.jsonl`; resolution appends a new snapshot.
```

- [ ] **Step 3: Add the quarterly report step**

Add to `.claude/commands/rescore-quarterly.md`, just before the final "write the rescore report" step (match heading style):

```markdown
### Regenerate the calibration report (rule 17 — the absolute-lens stress test)

    python3 scripts/calibration_report.py

Review `tracking/calibration-report.md`: the headline Brier / BSS, the reliability table,
and the per-dimension / per-layer breakdown. **BSS ≤ 0 on a dimension means those ratings
add nothing over forecasting the cohort base rate** — surface it for a human decision
(investigate or stop trusting the dimension); do NOT auto-reweight anything. Calibration is
the external standard that catches the uniform cohort bias the sort order hides (rule 12).
```

- [ ] **Step 4: Verify the edits read correctly**

Run: `grep -n "Resolve due forecasts\|Regenerate the calibration report" .claude/commands/weekly-scan.md .claude/commands/rescore-quarterly.md`
Expected: one match in each file.

- [ ] **Step 5: Commit**

```bash
git add .claude/commands/weekly-scan.md .claude/commands/rescore-quarterly.md
git commit -m "docs(calibration): wire weekly resolve + quarterly report into the routines"
```

---

### Task 10: CLAUDE.md rule 17

**Files:**
- Modify: `CLAUDE.md` (append rule 17 after rule 16)

**Interfaces:** documentation only.

- [ ] **Step 1: Confirm rule 16 is the last rule**

Run: `grep -n "^### 1[0-9]\." CLAUDE.md`
Expected: rules up to `### 16.` and no `### 17.` yet.

- [ ] **Step 2: Append rule 17**

Insert immediately after the end of rule 16's section (before the next top-level `## ` heading):

```markdown
### 17. Forecast calibration loop (added 2026-06-26, approved by Dom)

**Context:** Subjective ratings (AI-Thesis, Momentum, Risk R1–R5) are implicit predictions, assigned and frozen but never graded against what happened. A ranking system can't see its own uniform bias (rule 12); calibration is the external absolute standard that can.

**Rule:** Selected ratings are logged as falsifiable, dated forecasts with a frozen, mechanical resolution rule in `tracking/forecasts.jsonl` — a **single append-only snapshot log** (creation appends an `open` snapshot; resolution appends a new snapshot of the same `id`; lines are never edited; the current state of an `id` is its last snapshot). Forecasts are resolved on schedule and graded with Brier score, the Murphy REL/RES/UNC decomposition, Brier Skill Score vs. the base rate, and a reliability diagram.

**Guarantees (do not weaken — treat like the site privacy gate):** `created_date`, `ticker`, `layer`, `dimension`, `rating_value`, `template`, `probability`, `resolution_date`, and `resolution_rule` are immutable (a changed mind is a *new* forecast); `created_date` is set to today at log time so backdating is impossible; the resolver consumes only post-`created_date` data (no look-ahead); ambiguous resolutions go to `needs_review`, never guessed (rule 3); every resolution carries a cited evidence string (rule 1).

**Boundary:** calibration is diagnostic — it does **not** feed back into the Total Score or category weights, adds **no** Watchlist columns, uses **no** paid data, and is **not** surfaced on the friend-facing site. A dimension proving to be noise is a human decision ("stop trusting it / investigate"), never an automatic reweight (the overfitting trap flagged in prior reviews).

**Cadence & scripts:** `/weekly-scan` runs `scripts/resolve_forecasts.py` (resolve due); `/rescore-quarterly` runs `scripts/calibration_report.py` (regenerate `tracking/calibration-report.md`). Seed/log forecasts with `scripts/log_forecast.py`. Core logic: `forecast_store.py` (the log), `forecast_cohorts.py` (frozen peer basket), `forecast_resolvers.py` (template registry), `forecast_metrics.py` (Brier/Murphy/BSS).

**Rollout:** Phase 1 = `REL_STRENGTH_1Q` on portfolio names (frozen layer-cohort EW basket; SMH fallback for thin layers). Phase 2 adds `EARNINGS_REACTION` + full watchlist + rating-time forecasts. Phase 3 adds the fundamental templates. Switch rating→probability defaults from the §4 priors to empirically-learned per-bucket hit rates once each dimension has ~30 resolved forecasts.
```

- [ ] **Step 3: Verify**

Run: `grep -n "^### 17\. Forecast calibration" CLAUDE.md`
Expected: one match.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(calibration): add CLAUDE.md rule 17 (forecast calibration loop)"
```

---

### Task 11: Phase-1 seed run (operational — with Dom in the loop)

**Files:**
- Produces (runtime): `tracking/forecasts.jsonl` (the seeded portfolio forecasts).

**Interfaces:** uses `log_forecast.py` from Task 7. This is an interactive, human-in-loop step — the probability overrides are the training signal (CLAUDE.md rule 17 / design §7), so they must be Dom's, not defaults.

- [ ] **Step 1: Dry-run the seeding to produce the proposal table**

Run: `python3 scripts/log_forecast.py --seed-portfolio --dry-run`
Expected: a table of ~14 portfolio names with layer, rel-strength rating, default probability, and frozen benchmark (cohort size or SMH), plus a single `resolution_date`. No file written.

- [ ] **Step 2: Review with Dom and collect probability overrides**

Present the table to Dom. For each name, Dom confirms the default or overrides the probability (the override is the actual calibration training). Capture overrides as JSON, e.g.:

```bash
cat > /tmp/forecast-overrides.json <<'JSON'
{"AVGO": 0.60, "NVDA": 0.72}
JSON
```
(Only include names Dom changes; the rest keep the rating-derived default.)

- [ ] **Step 3: Apply**

Run: `python3 scripts/log_forecast.py --seed-portfolio --apply --overrides /tmp/forecast-overrides.json`
Expected: one `logged fc_…` line per portfolio name; final `wrote N forecasts to …/tracking/forecasts.jsonl`.

- [ ] **Step 4: Verify the log + confirm no look-ahead slipped in**

Run:
```bash
python3 -c "import sys; sys.path.insert(0,'scripts'); import forecast_store as s; \
fs=list(s.materialize().values()); print('open:', sum(f['status']=='open' for f in fs)); \
print('all future res dates:', all(f['resolution_date']>f['created_date'] for f in fs))"
```
Expected: `open: N` (= portfolio count) and `all future res dates: True`.

- [ ] **Step 5: Dry-run the report on the seeded (still-open) log**

Run: `python3 scripts/calibration_report.py --dry-run`
Expected: report renders with `resolved: 0` and the empty-overall note (nothing resolves until ~1 quarter out). Confirms the report handles the all-open state gracefully.

- [ ] **Step 6: Commit the seeded log**

```bash
git add tracking/forecasts.jsonl
git commit -m "chore(calibration): seed Phase-1 REL_STRENGTH_1Q forecasts for portfolio names"
```

---

## Self-Review

**1. Spec coverage** (design spec §-by-§):
- §1 purpose/boundary → Task 10 (rule 17), enforced by no-feedback/no-column/no-site design throughout.
- §2 locked decisions → frozen peers (Task 4), batch-seed (Task 11), append-only snapshot (Task 2), flat modules (all).
- §3 module layout → Tasks 2–8 (7 files, flat, prefix).
- §4 the log → Task 2.
- §5 schema → Task 2 (`REQUIRED_FIELDS`/`IMMUTABLE_FIELDS`), produced by Task 7.
- §6 resolver (NA/needs_review, trading-day date math) → Task 5.
- §7 seeding + default map → Task 7 + Task 11.
- §8 metrics + identity test + small-N guard → Task 3 + Task 8 (`MIN_N_FOR_CURVE`, warn).
- §9 report + optional PNG → Task 8.
- §10 weekly/quarterly hooks → Task 9.
- §11 tests → Tasks 2–8 each ship tests; cohorts test added (Task 4).
- §12 rule 17 → Task 10.
- §13 non-goals → respected (only REL_STRENGTH_1Q implemented; registry extensible).
- §15 acceptance criteria → all mapped to tasks above.

**2. Placeholder scan:** No "TBD"/"TODO"/"handle edge cases"; every code step shows complete code; every test step shows real assertions.

**3. Type consistency:** `build_frozen_cohort` returns `(layer, rule)` (Task 4) and is consumed that way (Task 7). `Resolution` fields (Task 5) are read in `resolve_due` (Task 6). `read_watchlist_rows` (Task 4) called in Task 7. `store.append_creation(snap, *, today)` / `append_resolution` signatures consistent across Tasks 2, 6, 7, 8. `RESOLVERS` dict (Task 5) consumed in Task 6. `resolution_date_for` (Task 5) consumed in Task 7. Metric function names (`brier`, `murphy_decomposition`, `brier_skill_score`, `log_loss`, `reliability_table`, `base_rate`) consistent across Tasks 3 and 8.

No gaps found.
