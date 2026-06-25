# Refresh Objective Inputs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/refresh-objective` skill that refreshes every objective Watchlist input (for the portfolio, all scored names, or a ticker subset) while leaving all subjective ratings untouched and never silently regressing a deliberate-blank convention.

**Architecture:** A new `scripts/refresh_objective_inputs.py` reuses `compute_inputs()` from `batch_score.py` to fetch values, then runs a pure **guard pipeline** that decides — per cell — whether to write the fresh value, keep the existing one, force a blank, or flag for human ruling. Pure functions (target resolution, guards, MW-staleness) are unit-tested without network; orchestration writes to the workbook and reports score deltas via `recalc_watchlist.py`. A `.claude/commands/refresh-objective.md` wrapper documents the two modes and dry-run discipline.

**Tech Stack:** Python 3, openpyxl (formula-preserving), yfinance (via `compute_inputs`), pytest.

## Global Constraints

- **Spreadsheet:** `00-master/ai_supply_chain_scoring.xlsx`, sheet `Watchlist`. Edit with **openpyxl only** (never pandas `to_excel` — strips formulas).
- **Objective input columns written:** 5 (Fwd P/E), 6 (EV/EBITDA·FCF·MW), 7 (FCF Yield %), 8 (P/S), 11 (ROIC %), 12 (Gross Mgn %), 13 (FCF Mgn %), 14 (ND/EBITDA), 16 (Rev 3y CAGR %), 17 (Rev YoY %), 18 (EPS YoY %), 29 (50DMA %). Plus col 4 (Last Updated).
- **Never write:** col 9 (PEG formula), cols 10/15/19/25/30/35/36/37 (score/TOTAL/Tier formulas), and subjective cols 20–24, 26–28, 31–34, 38.
- **No structural row changes** → do NOT run `rebuild_watchlist_formulas.py`.
- **Reuse, don't duplicate:** import `compute_inputs`, `_is_layer9_capacity`, `_CAPACITY_JSON` from `batch_score.py`; import `pct_days_above_50dma` from `momentum_50dma.py`.
- **Serialize yfinance calls** with `time.sleep(0.3)` between tickers (throttle, per CLAUDE.md).
- **EPS-YoY extreme threshold:** `abs(eps_yoy) >= 300`.
- **MW staleness threshold:** `capacity-mw.json` entry `as_of` older than 90 days.
- **Guard 1 currency:** `info.get('financialCurrency')` present and `!= 'USD'` → blank cols 6, 7, 8 (keep col 5).
- Commit message trailer on every commit: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

---

### Task 1: Target resolution

**Files:**
- Create: `scripts/refresh_objective_inputs.py`
- Test: `tests/test_refresh_objective_inputs.py`

**Interfaces:**
- Consumes: nothing (entry module).
- Produces:
  - `resolve_targets(arg: str | list[str], scoring_path=SCORING_PATH, portfolio_path=PORTFOLIO_PATH) -> list[str]` — returns uppercased tickers. `"portfolio"` → `HOLD` rows of `portfolio.xlsx`→`Targets`; `"all"` → every Watchlist col-1 ticker; a list → those tickers uppercased, filtered to ones present on the Watchlist (unknowns dropped, returned via a module-level `LAST_UNKNOWN` is NOT used — instead print is done by caller; keep this function pure and just drop unknowns).
  - Module constants: `SCORING_PATH = ROOT/'00-master'/'ai_supply_chain_scoring.xlsx'`, `PORTFOLIO_PATH = ROOT/'00-master'/'portfolio.xlsx'`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_refresh_objective_inputs.py
import shutil
from pathlib import Path
from openpyxl import Workbook
import scripts.refresh_objective_inputs as roi


def _make_scoring(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Watchlist"
    headers = ["Ticker", "Company", "Layer", "Last Updated", "Fwd P/E"]
    ws.append(headers)
    for t in ["NVDA", "TSM", "MU", "GEV"]:
        ws.append([t, f"{t} Inc", "06 Silicon", None, None])
    p = tmp_path / "scoring.xlsx"
    wb.save(p)
    return p


def _make_portfolio(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Targets"
    ws.append(["Target Portfolio", None, None, None, None, None])
    ws.append(["Ticker", "Layer", "TOTAL", "Tier", "Rank", "Status"])
    ws.append(["NVDA", "06", 84.0, "✓✓", 1, "HOLD"])
    ws.append(["MU", "06", 79.9, "✓✓", 2, "HOLD"])
    ws.append(["XYZ", "06", 70.0, "✓✓", 3, None])  # not HOLD
    p = tmp_path / "portfolio.xlsx"
    wb.save(p)
    return p


def test_resolve_portfolio_returns_hold_tickers(tmp_path):
    sp = _make_scoring(tmp_path)
    pp = _make_portfolio(tmp_path)
    assert roi.resolve_targets("portfolio", scoring_path=sp, portfolio_path=pp) == ["NVDA", "MU"]


def test_resolve_all_returns_every_watchlist_ticker(tmp_path):
    sp = _make_scoring(tmp_path)
    pp = _make_portfolio(tmp_path)
    assert roi.resolve_targets("all", scoring_path=sp, portfolio_path=pp) == ["NVDA", "TSM", "MU", "GEV"]


def test_resolve_subset_drops_unknowns(tmp_path):
    sp = _make_scoring(tmp_path)
    pp = _make_portfolio(tmp_path)
    assert roi.resolve_targets(["nvda", "ZZZZ"], scoring_path=sp, portfolio_path=pp) == ["NVDA"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -v`
Expected: FAIL — `ModuleNotFoundError` / `AttributeError: module ... has no attribute 'resolve_targets'`.

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/refresh_objective_inputs.py
"""Refresh objective Watchlist inputs (portfolio / all / subset) — rule-9 helper.

Subjective rating cells are NEVER touched. Deliberate-blank conventions
(foreign-ADR currency, EPS-YoY one-offs, negative-EBITDA, ROIC) are guarded so
a mechanical refresh cannot silently regress them. See
docs/superpowers/specs/2026-06-24-refresh-objective-inputs-design.md.
"""
from __future__ import annotations

from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
SCORING_PATH = ROOT / "00-master" / "ai_supply_chain_scoring.xlsx"
PORTFOLIO_PATH = ROOT / "00-master" / "portfolio.xlsx"


def _watchlist_tickers(scoring_path) -> list[str]:
    ws = load_workbook(scoring_path, read_only=True)["Watchlist"]
    out = []
    for r in range(2, ws.max_row + 1):
        v = ws.cell(row=r, column=1).value
        if v:
            out.append(str(v).strip().upper())
    return out


def _portfolio_hold_tickers(portfolio_path) -> list[str]:
    ws = load_workbook(portfolio_path, read_only=True)["Targets"]
    header_row = None
    for r in range(1, ws.max_row + 1):
        if ws.cell(row=r, column=1).value == "Ticker":
            header_row = r
            break
    status_col = None
    for c in range(1, ws.max_column + 1):
        if ws.cell(row=header_row, column=c).value == "Status":
            status_col = c
            break
    out = []
    for r in range(header_row + 1, ws.max_row + 1):
        t = ws.cell(row=r, column=1).value
        s = ws.cell(row=r, column=status_col).value
        if t and s and str(s).strip().upper() == "HOLD":
            out.append(str(t).strip().upper())
    return out


def resolve_targets(arg, scoring_path=SCORING_PATH, portfolio_path=PORTFOLIO_PATH) -> list[str]:
    watchlist = _watchlist_tickers(scoring_path)
    if arg == "all":
        return watchlist
    if arg == "portfolio":
        hold = _portfolio_hold_tickers(portfolio_path)
        wlset = set(watchlist)
        return [t for t in hold if t in wlset]
    # explicit subset
    wlset = set(watchlist)
    return [t.strip().upper() for t in arg if t.strip().upper() in wlset]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/refresh_objective_inputs.py tests/test_refresh_objective_inputs.py
git commit -m "feat(refresh): target resolution for objective-input refresh

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: MW-staleness flag (Layer-9 cohort)

**Files:**
- Modify: `scripts/refresh_objective_inputs.py`
- Test: `tests/test_refresh_objective_inputs.py`

**Interfaces:**
- Consumes: `_is_layer9_capacity` and `_CAPACITY_JSON` from `batch_score.py`.
- Produces:
  - `mw_staleness_flag(ticker: str, layer: str | None, today: date, capacity_json=None) -> str | None` — returns a flag string if `layer` is a Layer-9 capacity cohort name AND its `capacity-mw.json` entry is missing OR its `as_of` is >90 days before `today`; else `None`. `capacity_json` overridable for tests (path to a JSON file).

- [ ] **Step 1: Write the failing test**

```python
import json
import datetime as dt
import scripts.refresh_objective_inputs as roi

L9 = "09 Compute-as-a-Service / Neocloud GPU clouds"
TODAY = dt.date(2026, 6, 24)


def _cap(tmp_path, payload):
    p = tmp_path / "capacity-mw.json"
    p.write_text(json.dumps(payload))
    return p


def test_mw_flag_missing_entry(tmp_path):
    cj = _cap(tmp_path, {})
    f = roi.mw_staleness_flag("CRWV", L9, TODAY, capacity_json=cj)
    assert f is not None and "CRWV" in f and "missing" in f.lower()


def test_mw_flag_stale_asof(tmp_path):
    cj = _cap(tmp_path, {"CRWV": {"secured_gross_mw": 300, "as_of": "2026-03-01"}})
    f = roi.mw_staleness_flag("CRWV", L9, TODAY, capacity_json=cj)
    assert f is not None and "stale" in f.lower()


def test_mw_flag_fresh_returns_none(tmp_path):
    cj = _cap(tmp_path, {"CRWV": {"secured_gross_mw": 300, "as_of": "2026-06-01"}})
    assert roi.mw_staleness_flag("CRWV", L9, TODAY, capacity_json=cj) is None


def test_mw_flag_non_l9_returns_none(tmp_path):
    cj = _cap(tmp_path, {})
    assert roi.mw_staleness_flag("NVDA", "06 Silicon", TODAY, capacity_json=cj) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -k mw_flag -v`
Expected: FAIL — `AttributeError: ... 'mw_staleness_flag'`.

- [ ] **Step 3: Write minimal implementation**

Add imports near the top of `scripts/refresh_objective_inputs.py`:

```python
import sys
import json
import datetime as dt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_score import _is_layer9_capacity, _CAPACITY_JSON
```

Add the function:

```python
def mw_staleness_flag(ticker, layer, today, capacity_json=None):
    if not _is_layer9_capacity(layer):
        return None
    path = capacity_json if capacity_json is not None else _CAPACITY_JSON
    try:
        data = json.loads(Path(path).read_text())
    except Exception:
        data = {}
    rec = data.get(ticker)
    if not rec or rec.get("secured_gross_mw") is None:
        return f"{ticker} EV/MW: missing from capacity-mw.json — add it (rule 13)."
    as_of = rec.get("as_of")
    try:
        age = (today - dt.date.fromisoformat(as_of)).days
    except Exception:
        return f"{ticker} EV/MW: capacity-mw.json as_of unparseable ({as_of!r}) — stale, refresh MW."
    if age > 90:
        return f"{ticker} EV/MW: capacity-mw.json as_of {as_of} → {age} days old (>90) → stale, refresh MW."
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -k mw_flag -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/refresh_objective_inputs.py tests/test_refresh_objective_inputs.py
git commit -m "feat(refresh): Layer-9 MW-staleness flag

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Guard pipeline (the "smart" blank-handling)

**Files:**
- Modify: `scripts/refresh_objective_inputs.py`
- Test: `tests/test_refresh_objective_inputs.py`

**Interfaces:**
- Consumes: nothing external (pure function).
- Produces:
  - Column map constant `OBJ_COLS = {"fwd_pe":5, "ev_ebitda":6, "fcf_yield":7, "ps":8, "roic":11, "gross_mgn":12, "fcf_mgn":13, "nd_ebitda":14, "rev_3y_cagr":16, "rev_yoy":17, "eps_yoy":18}` (50DMA col 29 handled separately).
  - `EPS_YOY_EXTREME = 300.0`.
  - `apply_guards(info: dict, fresh: dict, existing: dict) -> tuple[dict, list[str]]` — returns `(writes, flags)` where `writes` maps **input-key → value** for keys that SHOULD be written (a key absent from `writes` means "leave the cell untouched"), and `flags` is a list of human-ruling strings. `info` needs only `financialCurrency`. `fresh` is the `compute_inputs` dict; `existing` maps input-key → current cell value (None/"" if blank). MW-staleness is NOT handled here (it's `mw_staleness_flag`, merged by the caller).

Guard order inside `apply_guards`, per input-key:
1. If `financialCurrency` present and `!= 'USD'`: force `ps`, `ev_ebitda`, `fcf_yield` to blank → emit write `None` for those three keys, plus one flag, and skip guards 5–7 for those three keys.
2. (negative-EBITDA / layer-conditional already applied inside `compute_inputs` → `fresh` already correct; nothing to do here.)
3. For `eps_yoy`: (a) if `existing` blank → do NOT write, flag "preserved blank"; (b) elif `fresh['eps_yoy']` not None and `abs >= 300` → do NOT write, flag "withheld extreme"; (c) else normal.
4. For every remaining key: if `fresh[key]` is None AND `existing[key]` non-blank → do NOT write (keep existing), flag "kept prior on no-data"; else write `fresh[key]`.

- [ ] **Step 1: Write the failing test**

```python
import scripts.refresh_objective_inputs as roi


def _blank_existing():
    return {k: None for k in roi.OBJ_COLS}


def test_guard_currency_blanks_adr_cols():
    info = {"financialCurrency": "TWD"}
    fresh = {"fwd_pe": 23.4, "ev_ebitda": 15.0, "fcf_yield": 3.2, "ps": 8.0,
             "roic": 20.0, "gross_mgn": 55.0, "fcf_mgn": 30.0, "nd_ebitda": 0.5,
             "rev_3y_cagr": 25.0, "rev_yoy": 30.0, "eps_yoy": 40.0}
    writes, flags = roi.apply_guards(info, fresh, _blank_existing())
    assert writes["ps"] is None and writes["ev_ebitda"] is None and writes["fcf_yield"] is None
    assert writes["fwd_pe"] == 23.4  # kept
    assert any("ADR" in f or "currency" in f.lower() for f in flags)


def test_guard_keeps_existing_on_fetched_none():
    info = {"financialCurrency": "USD"}
    fresh = {k: None for k in roi.OBJ_COLS}
    fresh["fwd_pe"] = 40.0
    existing = _blank_existing()
    existing["roic"] = 18.5  # human-curated
    writes, flags = roi.apply_guards(info, fresh, existing)
    assert "roic" not in writes  # untouched, not clobbered with None
    assert writes["fwd_pe"] == 40.0
    assert any("roic" in f.lower() for f in flags)


def test_guard_eps_yoy_preserves_blank():
    info = {"financialCurrency": "USD"}
    fresh = {k: 10.0 for k in roi.OBJ_COLS}
    fresh["eps_yoy"] = 50.0
    existing = {k: 9.0 for k in roi.OBJ_COLS}
    existing["eps_yoy"] = None  # deliberately blank (GEV-style)
    writes, flags = roi.apply_guards(info, fresh, existing)
    assert "eps_yoy" not in writes
    assert any("eps yoy" in f.lower() and "blank" in f.lower() for f in flags)


def test_guard_eps_yoy_withholds_extreme():
    info = {"financialCurrency": "USD"}
    fresh = {k: 10.0 for k in roi.OBJ_COLS}
    fresh["eps_yoy"] = 412.0
    existing = {k: 9.0 for k in roi.OBJ_COLS}
    writes, flags = roi.apply_guards(info, fresh, existing)
    assert "eps_yoy" not in writes
    assert any("412" in f or "extreme" in f.lower() for f in flags)


def test_guard_eps_yoy_normal_writes():
    info = {"financialCurrency": "USD"}
    fresh = {k: 10.0 for k in roi.OBJ_COLS}
    fresh["eps_yoy"] = 80.0
    existing = {k: 9.0 for k in roi.OBJ_COLS}
    writes, flags = roi.apply_guards(info, fresh, existing)
    assert writes["eps_yoy"] == 80.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -k guard -v`
Expected: FAIL — `AttributeError: ... 'apply_guards'` / `'OBJ_COLS'`.

- [ ] **Step 3: Write minimal implementation**

```python
OBJ_COLS = {"fwd_pe": 5, "ev_ebitda": 6, "fcf_yield": 7, "ps": 8,
            "roic": 11, "gross_mgn": 12, "fcf_mgn": 13, "nd_ebitda": 14,
            "rev_3y_cagr": 16, "rev_yoy": 17, "eps_yoy": 18}
DMA_COL = 29
LAST_UPDATED_COL = 4
EPS_YOY_EXTREME = 300.0
_ADR_BLANK_KEYS = ("ps", "ev_ebitda", "fcf_yield")


def _blank(v):
    return v is None or v == ""


def apply_guards(info, fresh, existing):
    writes, flags = {}, []
    cur = info.get("financialCurrency")
    adr = bool(cur) and str(cur).upper() != "USD"
    if adr:
        for k in _ADR_BLANK_KEYS:
            writes[k] = None
        flags.append(f"ADR currency {cur}: blanked P/S, EV/EBITDA, FCF-Yield (USD price vs local financials).")
    for key in OBJ_COLS:
        if adr and key in _ADR_BLANK_KEYS:
            continue  # already forced blank above
        if key == "eps_yoy":
            if _blank(existing.get(key)):
                flags.append("EPS YoY: cell currently blank (likely a documented one-off) — preserved blank, not refilled.")
                continue
            v = fresh.get(key)
            if v is not None and abs(v) >= EPS_YOY_EXTREME:
                flags.append(f"EPS YoY: fresh {v:+.0f}% ≥ {EPS_YOY_EXTREME:.0f}% → withheld as possible one-off (rule 15). Confirm blank or write.")
                continue
            writes[key] = v
            continue
        v = fresh.get(key)
        if v is None and not _blank(existing.get(key)):
            flags.append(f"{key}: fetch returned no data — kept prior value {existing.get(key)}.")
            continue
        writes[key] = v
    return writes, flags
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -k guard -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/refresh_objective_inputs.py tests/test_refresh_objective_inputs.py
git commit -m "feat(refresh): smart blank-handling guard pipeline

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Row read/write helpers (subjective cells untouched)

**Files:**
- Modify: `scripts/refresh_objective_inputs.py`
- Test: `tests/test_refresh_objective_inputs.py`

**Interfaces:**
- Consumes: `OBJ_COLS`, `DMA_COL`, `LAST_UPDATED_COL`.
- Produces:
  - `read_existing(ws, row: int) -> dict` — input-key → current cell value for every key in `OBJ_COLS`.
  - `write_row(ws, row: int, writes: dict, dma_value, today_iso: str) -> list[int]` — writes each key in `writes` to its `OBJ_COLS` column; writes `dma_value` to `DMA_COL` if not None; sets `LAST_UPDATED_COL` to `today_iso`. Returns the sorted list of column indices it wrote. Must NOT touch any column outside `OBJ_COLS ∪ {DMA_COL, LAST_UPDATED_COL}`.

- [ ] **Step 1: Write the failing test**

```python
from openpyxl import Workbook
import scripts.refresh_objective_inputs as roi


def _ws_one_row():
    wb = Workbook()
    ws = wb.active
    # 38 columns; put a sentinel in every subjective col so we can prove they're untouched
    for c in range(1, 39):
        ws.cell(row=2, column=c, value=f"S{c}")
    return ws


def test_write_row_only_touches_objective_and_meta():
    ws = _ws_one_row()
    writes = {"fwd_pe": 41.1, "ps": None}
    touched = roi.write_row(ws, 2, writes, dma_value=78.0, today_iso="2026-06-24")
    assert ws.cell(row=2, column=5).value == 41.1
    assert ws.cell(row=2, column=8).value is None
    assert ws.cell(row=2, column=29).value == 78.0
    assert ws.cell(row=2, column=4).value == "2026-06-24"
    # subjective cols untouched
    for c in (20, 21, 22, 23, 24, 26, 27, 28, 31, 32, 33, 34, 38):
        assert ws.cell(row=2, column=c).value == f"S{c}"
    # score/formula cols untouched
    for c in (9, 10, 15, 19, 25, 30, 35, 36, 37):
        assert ws.cell(row=2, column=c).value == f"S{c}"
    assert set(touched) == {4, 5, 8, 29}


def test_read_existing_pulls_objective_keys():
    ws = _ws_one_row()
    ws.cell(row=2, column=11, value=18.5)
    existing = roi.read_existing(ws, 2)
    assert existing["roic"] == 18.5
    assert set(existing) == set(roi.OBJ_COLS)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -k "write_row or read_existing" -v`
Expected: FAIL — `AttributeError: ... 'write_row'`.

- [ ] **Step 3: Write minimal implementation**

```python
def read_existing(ws, row):
    return {k: ws.cell(row=row, column=c).value for k, c in OBJ_COLS.items()}


def write_row(ws, row, writes, dma_value, today_iso):
    touched = []
    for key, val in writes.items():
        c = OBJ_COLS[key]
        ws.cell(row=row, column=c, value=val)
        touched.append(c)
    if dma_value is not None:
        ws.cell(row=row, column=DMA_COL, value=dma_value)
        touched.append(DMA_COL)
    ws.cell(row=row, column=LAST_UPDATED_COL, value=today_iso)
    touched.append(LAST_UPDATED_COL)
    return sorted(set(touched))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -k "write_row or read_existing" -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/refresh_objective_inputs.py tests/test_refresh_objective_inputs.py
git commit -m "feat(refresh): row read/write helpers, subjective cells untouched

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Orchestration + CLI (`run`, `main`) with `--dry-run`

**Files:**
- Modify: `scripts/refresh_objective_inputs.py`
- Test: `tests/test_refresh_objective_inputs.py`

**Interfaces:**
- Consumes: all prior functions; `compute_inputs` from `batch_score`, `pct_days_above_50dma` from `momentum_50dma`.
- Produces:
  - `refresh(targets: list[str], dry_run: bool, scoring_path=SCORING_PATH, fetcher=None, dma_fetcher=None, today=None) -> dict` — orchestrates fetch → guards → (write|stage) per ticker. `fetcher(ticker, layer) -> (info, fresh_dict)` and `dma_fetcher(ticker) -> float|None` are injectable for tests (default real implementations call yfinance + `compute_inputs` / `pct_days_above_50dma`). Returns a report dict: `{"mode_count": int, "rows": [{ticker, touched, flags}], "flags": [all flags], "wrote": bool}`. When `dry_run`, does not save the workbook. When live, saves and sets Last Updated.
  - `main()` — argparse: positional `target` (`portfolio`/`all`/ticker list), `--dry-run`. Resolves targets, calls `refresh`, prints the change table + JUDGMENT FLAGS block; on a live run also shells `recalc_watchlist.py` and prints TOTAL/tier deltas (capture stdout, print verbatim).

- [ ] **Step 1: Write the failing test** (injected fetchers — no network)

```python
import datetime as dt
from openpyxl import load_workbook
import scripts.refresh_objective_inputs as roi


def test_refresh_dry_run_writes_nothing(tmp_path, monkeypatch):
    # build a scoring workbook with NVDA + a layer in col 3
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "Watchlist"
    ws.append(["Ticker", "Company", "Layer", "Last Updated"] + [None]*34)
    ws.append(["NVDA", "Nvidia", "06 Silicon", "2026-01-01"] + [None]*34)
    sp = tmp_path / "scoring.xlsx"; wb.save(sp)

    def fake_fetch(ticker, layer):
        info = {"financialCurrency": "USD"}
        fresh = {k: 10.0 for k in roi.OBJ_COLS}
        return info, fresh

    rep = roi.refresh(["NVDA"], dry_run=True, scoring_path=sp,
                      fetcher=fake_fetch, dma_fetcher=lambda t: 70.0,
                      today=dt.date(2026, 6, 24))
    # nothing written: Last Updated still original
    ws2 = load_workbook(sp)["Watchlist"]
    assert ws2.cell(row=2, column=4).value == "2026-01-01"
    assert ws2.cell(row=2, column=5).value is None
    assert rep["wrote"] is False


def test_refresh_live_writes_and_bumps_last_updated(tmp_path):
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "Watchlist"
    ws.append(["Ticker", "Company", "Layer", "Last Updated"] + [None]*34)
    ws.append(["NVDA", "Nvidia", "06 Silicon", "2026-01-01"] + [None]*34)
    sp = tmp_path / "scoring.xlsx"; wb.save(sp)

    def fake_fetch(ticker, layer):
        return {"financialCurrency": "USD"}, {k: 10.0 for k in roi.OBJ_COLS}

    roi.refresh(["NVDA"], dry_run=False, scoring_path=sp,
                fetcher=fake_fetch, dma_fetcher=lambda t: 70.0,
                today=dt.date(2026, 6, 24))
    ws2 = load_workbook(sp)["Watchlist"]
    assert ws2.cell(row=2, column=4).value == "2026-06-24"
    assert ws2.cell(row=2, column=5).value == 10.0
    assert ws2.cell(row=2, column=29).value == 70.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -k refresh -v`
Expected: FAIL — `AttributeError: ... 'refresh'`.

- [ ] **Step 3: Write minimal implementation**

```python
import time
import argparse
import subprocess

import yfinance as yf
sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_score import compute_inputs
from momentum_50dma import pct_days_above_50dma


def _default_fetcher(ticker, layer):
    t = yf.Ticker(ticker)
    info = t.info or {}
    fresh, _gaps = compute_inputs(ticker, t, info, layer=layer)
    return info, fresh


def _layer_of(ws, row):
    return ws.cell(row=row, column=3).value


def refresh(targets, dry_run, scoring_path=SCORING_PATH, fetcher=None,
            dma_fetcher=None, today=None):
    fetcher = fetcher or _default_fetcher
    dma_fetcher = dma_fetcher or pct_days_above_50dma
    today = today or dt.date.today()
    wb = load_workbook(scoring_path, data_only=False)
    ws = wb["Watchlist"]
    rows = {str(ws.cell(row=r, column=1).value).strip().upper(): r
            for r in range(2, ws.max_row + 1) if ws.cell(row=r, column=1).value}
    report = {"mode_count": len(targets), "rows": [], "flags": [], "wrote": False}
    for i, ticker in enumerate(targets):
        row = rows.get(ticker)
        if row is None:
            report["flags"].append(f"{ticker}: not on Watchlist — skipped.")
            continue
        layer = _layer_of(ws, row)
        info, fresh = fetcher(ticker, layer)
        existing = read_existing(ws, row)
        writes, flags = apply_guards(info, fresh, existing)
        mwf = mw_staleness_flag(ticker, layer, today)
        if mwf:
            flags.append(mwf)
        try:
            dma_value = dma_fetcher(ticker)
        except Exception as e:
            dma_value = None
            flags.append(f"{ticker} 50DMA: fetch error — {e}")
        touched = []
        if not dry_run:
            touched = write_row(ws, row, writes, dma_value, today.isoformat())
        report["rows"].append({"ticker": ticker, "touched": touched, "flags": flags})
        report["flags"].extend(f"{ticker}: {f}" for f in flags)
        if not isinstance(fetcher, type(_default_fetcher)) or fetcher is _default_fetcher:
            pass
        time.sleep(0.3) if fetcher is _default_fetcher else None
    if not dry_run:
        wb.save(scoring_path)
        report["wrote"] = True
    return report


def main():
    ap = argparse.ArgumentParser(description="Refresh objective Watchlist inputs.")
    ap.add_argument("target", nargs="+", help="'portfolio', 'all', or ticker(s)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    arg = args.target[0] if args.target[0] in ("portfolio", "all") and len(args.target) == 1 else args.target
    targets = resolve_targets(arg)
    print(f"REFRESH OBJECTIVE INPUTS — {len(targets)} names — {'DRY RUN' if args.dry_run else 'LIVE'}")
    rep = refresh(targets, dry_run=args.dry_run)
    for r in rep["rows"]:
        print(f"  {r['ticker']:<6} touched cols: {r['touched']}")
    if rep["flags"]:
        print("\nJUDGMENT FLAGS (human ruling needed):")
        for f in rep["flags"]:
            print(f"  • {f}")
    if rep["wrote"]:
        print("\nTOTAL changes (after recalc):")
        out = subprocess.run(["python3", str(ROOT / "scripts" / "recalc_watchlist.py")],
                             capture_output=True, text=True)
        print(out.stdout)


if __name__ == "__main__":
    main()
```

> Note: simplify the `time.sleep` throttle line in Step 3 — the conditional in the draft is awkward. Replace the two lines after `report["flags"].extend(...)` with:
> ```python
>         if fetcher is _default_fetcher:
>             time.sleep(0.3)  # throttle real yfinance only
> ```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -k refresh -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Run the full test file**

Run: `python3 -m pytest tests/test_refresh_objective_inputs.py -v`
Expected: all PASS (16 tests across tasks 1–5).

- [ ] **Step 6: Commit**

```bash
git add scripts/refresh_objective_inputs.py tests/test_refresh_objective_inputs.py
git commit -m "feat(refresh): orchestration + CLI with --dry-run

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Live dry-run smoke test on the real workbook

**Files:** none (verification only).

- [ ] **Step 1: Run a real dry-run against the portfolio**

Run: `python3 scripts/refresh_objective_inputs.py portfolio --dry-run`
Expected: prints ~14 rows + any JUDGMENT FLAGS; **git working tree shows no change** to `00-master/ai_supply_chain_scoring.xlsx` (`git status --short 00-master/` is empty for that file).

- [ ] **Step 2: Confirm no workbook mutation**

Run: `git status --short 00-master/ai_supply_chain_scoring.xlsx`
Expected: empty output (dry-run wrote nothing).

- [ ] **Step 3: Spot-check one flag path**

Run: `python3 scripts/refresh_objective_inputs.py TSM --dry-run`
Expected: a flag line noting ADR currency blanking for P/S, EV/EBITDA, FCF-Yield (TSM reports in TWD). If TSM is not flagged, investigate `info['financialCurrency']` before proceeding.

---

### Task 7: Skill wrapper `/refresh-objective`

**Files:**
- Create: `.claude/commands/refresh-objective.md`

**Interfaces:** none (documentation).

- [ ] **Step 1: Write the skill wrapper**

Create `.claude/commands/refresh-objective.md`:

```markdown
---
description: Refresh objective Watchlist inputs only (portfolio / all / subset), leaving subjective ratings untouched
---

Refresh the **objective** inputs (Value, Quality, Growth metrics + 50DMA %) for a
set of Watchlist names. Subjective ratings (AI Thesis, Momentum 1–5, Risk R1–R5)
are NEVER touched — those stay human-in-loop (rule 12). This is the automatable
half of rule 9 (earnings-triggered objective refresh).

## Usage

- `/refresh-objective portfolio` — the HOLD rows in `00-master/portfolio.xlsx` → Targets.
- `/refresh-objective all` — every Watchlist row.
- `/refresh-objective NVDA MU AVGO` — explicit subset.

## Process

1. **Always dry-run first** and show the change table + JUDGMENT FLAGS:
   `python3 scripts/refresh_objective_inputs.py <target> --dry-run`
2. Resolve the JUDGMENT FLAGS with Dom — these are the only cells needing
   judgment:
   - **EPS YoY withheld/preserved** (rule 15): confirm blank vs write per filing evidence.
   - **MW stale/missing** (rule 13): refresh `capacity-mw.json` if a filing supports it.
3. On approval, run live:
   `python3 scripts/refresh_objective_inputs.py <target>`
   This writes the objective cells, bumps Last Updated, and prints TOTAL/tier deltas.
4. **Cite** any flag resolution in the Rating Audit if it changes a blank decision.

## Guarantees (see spec 2026-06-24-refresh-objective-inputs-design.md)

- Foreign-ADR currency mismatch → P/S, EV/EBITDA, FCF-Yield auto-blanked.
- A failed fetch never clobbers an existing value (protects ROIC etc.).
- Extreme/blank EPS YoY is flagged, never auto-written.
- No structural row change → `rebuild_watchlist_formulas.py` not needed.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/commands/refresh-objective.md
git commit -m "feat(skill): /refresh-objective wrapper

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: Cross-reference in CLAUDE.md rule 9

**Files:**
- Modify: `CLAUDE.md` (rule 9 "How to refresh" paragraph)

- [ ] **Step 1: Add the pointer**

In CLAUDE.md rule 9, after the "**How to refresh:**" sentence ("Pull yfinance data and update the Watchlist row."), append:

```
For a scripted objective-only refresh of a set of names, use `/refresh-objective
<portfolio|all|TICKERS>` (dry-run first) — it refreshes every objective input,
guards the deliberate-blank conventions, and leaves subjective ratings untouched.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude): point rule 9 at /refresh-objective

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:**
- Two modes + subset + `--dry-run` → Tasks 1, 5, 6, 7. ✓
- 12 objective cols + Last Updated, no subjective/formula cols → Tasks 3, 4 (with the sentinel test proving untouched cols). ✓
- Guard 1 currency → Task 3. ✓
- Guards 2/3 (neg-EBITDA, L10 EV/FCF) inherited from `compute_inputs` → noted in Task 3 step 3 (nothing to add). ✓
- Guard 4 L9 EV/MW value (inherited) + MW-staleness flag → Task 2. ✓
- Guard 5 fetched-None-never-clobbers → Task 3. ✓
- Guard 6 EPS-YoY preserve/withhold → Task 3. ✓
- Bump Last Updated + recalc + report → Tasks 4, 5. ✓
- Reuse `compute_inputs`/`pct_days_above_50dma` (no duplication) → Task 5. ✓
- Tests on a temp workbook, no network → Tasks 1–5. ✓
- Skill wrapper + CLAUDE.md pointer → Tasks 7, 8. ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code. The one awkward `time.sleep` line is explicitly corrected by the follow-up note in Task 5 Step 3. ✓

**Type consistency:** `OBJ_COLS` keys match `compute_inputs`'s dict keys (`fwd_pe, ev_ebitda, fcf_yield, ps, roic, gross_mgn, fcf_mgn, nd_ebitda, rev_3y_cagr, rev_yoy, eps_yoy`). `apply_guards` returns `(writes, flags)`; `write_row` consumes `writes`; `refresh` wires them. `mw_staleness_flag` and `resolve_targets` signatures consistent across Tasks 1, 2, 5. ✓
