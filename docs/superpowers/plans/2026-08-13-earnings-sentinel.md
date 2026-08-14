# Earnings Sentinel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the event-driven earnings sentinel (spec `docs/superpowers/specs/2026-08-13-earnings-sentinel-design.md`): a pure detector script + weekday scheduled task that briefs reporting names the evening of the print and re-scores them on the first post-reaction close, feeding the existing execution pipeline.

**Architecture:** One new script `scripts/earnings_sentinel.py` — pure decision functions (scope, session classification, reaction day, due-event selection) with thin I/O wrappers and a JSON-state file — plus a scheduled-task prompt that drives the existing refresh chain, and a CLAUDE.md rule. No execution code changes anywhere.

**Tech Stack:** Python 3 stdlib (csv, json, argparse, zoneinfo, datetime); yfinance imported lazily inside fetch helpers only; pytest with tmp_path fixtures.

## Global Constraints

- **No order/write tools, no execution code.** The sentinel never imports or references `execute_ticket` internals; rule 29 seam is untouched.
- **Lazy heavy imports:** `yfinance`/`pandas` may only be imported inside functions, never at module top level (CI minimal-env runs pytest with only openpyxl+pytest; a module-level import aborts collection and fails the deploy).
- **Fictional fixtures only** — no real account numbers, dollar amounts, or share counts in tests (2026-08-09 privacy rule). Watchlist tickers as strings are fine.
- **Stage explicit paths** in every commit (`git add <paths>`), never `git add -A` (tracking/live/ is not ignored on origin/main).
- **Branch:** work continues on `spec/earnings-sentinel` (already cut from origin/main; carries the spec commit).
- **Timezone:** all wall-clock logic in `America/New_York` (zoneinfo), timezone-aware.
- Rate-limit courtesy on yfinance loops: `time.sleep(0.1)` between tickers.

---

### Task 1: Pure decision core of `earnings_sentinel.py`

**Files:**
- Create: `scripts/earnings_sentinel.py`
- Test: `tests/test_earnings_sentinel.py`

**Interfaces:**
- Consumes: `portfolio_sizing.is_tradable(ticker: str) -> bool` (exists, offline).
- Produces (later tasks rely on these exact names):
  - `ET = zoneinfo.ZoneInfo("America/New_York")`
  - `DEFAULT_TOP_N = 25`, `MAX_REPORT_AGE_DAYS = 5`
  - `build_scope(holdings: list[str], ranked_rows: list[tuple[str, int]], top_n: int = DEFAULT_TOP_N) -> list[str]`
  - `classify_session(report_ts: datetime) -> str` returning `'BMO' | 'AMC'`
  - `reaction_day(report_ts: datetime) -> date`
  - `due_events(scope, calendar, latest_close, state, now) -> dict` with keys `briefing_due`, `rescore_due` (lists of `{"ticker", "report_date", "session"}`) and `flagged` (dict ticker→reason).

- [ ] **Step 1: Write the failing tests**

```python
"""tests/test_earnings_sentinel.py — pure logic, no network, fictional data."""
import datetime as dt

from earnings_sentinel import (
    ET, build_scope, classify_session, reaction_day, due_events,
)


def _ts(y, m, d, hh, mm):
    return dt.datetime(y, m, d, hh, mm, tzinfo=ET)


# ---- build_scope -----------------------------------------------------------

RANKED = [("AAA", 1), ("BBB.T", 2), ("CCC", 3), ("DDD", 4)]


def test_scope_is_holdings_union_top_tradable_ranks():
    scope = build_scope(["ZZZ"], RANKED, top_n=2)
    # BBB.T is foreign → excluded from the rank leg; next tradable fills slot
    assert scope == ["AAA", "CCC", "ZZZ"]


def test_scope_dedupes_holdings_already_ranked():
    scope = build_scope(["AAA"], RANKED, top_n=2)
    assert scope == ["AAA", "CCC"]


def test_scope_top_n_counts_tradable_only():
    ranked = [("AAA", 1), ("B.T", 2), ("C.DE", 3), ("DDD", 4), ("EEE", 5)]
    assert build_scope([], ranked, top_n=2) == ["AAA", "DDD"]


# ---- session / reaction day ------------------------------------------------

def test_before_open_report_is_bmo():
    assert classify_session(_ts(2026, 8, 12, 7, 0)) == "BMO"


def test_after_close_report_is_amc():
    assert classify_session(_ts(2026, 8, 11, 16, 30)) == "AMC"


def test_midnight_timestamp_is_unknown_treated_amc():
    # date-only placeholder from the calendar source → conservative
    assert classify_session(_ts(2026, 8, 11, 0, 0)) == "AMC"


def test_reaction_day_bmo_same_day():
    assert reaction_day(_ts(2026, 8, 12, 7, 0)) == dt.date(2026, 8, 12)


def test_reaction_day_amc_next_weekday():
    assert reaction_day(_ts(2026, 8, 11, 16, 30)) == dt.date(2026, 8, 12)


def test_reaction_day_amc_friday_rolls_to_monday():
    assert reaction_day(_ts(2026, 8, 14, 16, 30)) == dt.date(2026, 8, 17)


# ---- due_events ------------------------------------------------------------

NOW_TUE_EVE = _ts(2026, 8, 11, 18, 30)   # Tue 18:30 ET
NOW_WED_EVE = _ts(2026, 8, 12, 18, 30)


def _state(**tickers):
    return {"tickers": tickers}


def test_amc_print_t0_briefing_only():
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 11)},
                     _state(), NOW_TUE_EVE)
    assert out["briefing_due"] == [
        {"ticker": "AAA", "report_date": "2026-08-11", "session": "AMC"}]
    assert out["rescore_due"] == []          # reaction close doesn't exist yet


def test_amc_print_next_evening_rescore_due():
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    st = _state(AAA={"briefed": "2026-08-11"})
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 12)}, st, NOW_WED_EVE)
    assert out["briefing_due"] == []
    assert out["rescore_due"] == [
        {"ticker": "AAA", "report_date": "2026-08-11", "session": "AMC"}]


def test_bmo_print_same_evening_both_due():
    cal = {"AAA": [_ts(2026, 8, 12, 7, 0)]}
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 12)},
                     _state(), NOW_WED_EVE)
    assert len(out["briefing_due"]) == 1 and len(out["rescore_due"]) == 1


def test_fully_processed_report_emits_nothing():
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    st = _state(AAA={"briefed": "2026-08-11", "rescored": "2026-08-11"})
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 12)}, st, NOW_WED_EVE)
    assert out["briefing_due"] == [] and out["rescore_due"] == []


def test_old_report_ignored_at_first_deployment():
    cal = {"AAA": [_ts(2026, 7, 20, 16, 30)]}    # >5 days ago
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 12)},
                     _state(), NOW_WED_EVE)
    assert out["briefing_due"] == [] and out["rescore_due"] == []


def test_future_report_emits_nothing():
    cal = {"AAA": [_ts(2026, 8, 20, 16, 30)]}
    out = due_events(["AAA"], cal, {}, _state(), NOW_WED_EVE)
    assert out["briefing_due"] == [] and out["rescore_due"] == []
    assert "AAA" not in out["flagged"]


def test_new_quarter_fires_even_when_prior_quarter_processed():
    # state carries last quarter's report; a fresh print supersedes it
    cal = {"AAA": [_ts(2026, 5, 12, 16, 30), _ts(2026, 8, 11, 16, 30)]}
    st = _state(AAA={"briefed": "2026-05-12", "rescored": "2026-05-12"})
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 11)}, st, NOW_TUE_EVE)
    assert out["briefing_due"] == [
        {"ticker": "AAA", "report_date": "2026-08-11", "session": "AMC"}]


def test_missing_calendar_is_flagged_not_guessed():
    out = due_events(["AAA"], {"AAA": []}, {}, _state(), NOW_WED_EVE)
    assert "AAA" in out["flagged"]


def test_holiday_no_new_close_defers_rescore():
    # reaction day passed on the calendar but latest close is still older
    cal = {"AAA": [_ts(2026, 8, 11, 16, 30)]}
    st = _state(AAA={"briefed": "2026-08-11"})
    out = due_events(["AAA"], cal, {"AAA": dt.date(2026, 8, 11)}, st, NOW_WED_EVE)
    assert out["rescore_due"] == []
    assert "AAA" not in out["flagged"]       # quiet defer, not an error
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_earnings_sentinel.py -v`
Expected: FAIL — `ModuleNotFoundError: earnings_sentinel` (conftest.py already puts `scripts/` on the path for `test_executor_cron`-style imports; confirm by checking `tests/conftest.py`, and if it doesn't, add the same sys.path line the existing conftest uses).

- [ ] **Step 3: Implement the pure core**

```python
"""Earnings sentinel — detection only (spec 2026-08-13-earnings-sentinel-design).

Pure decision functions + a JSON state file. NO side effects on any workbook;
the scheduled task drives all refreshes and calls back --mark on completion.
Never imports yfinance/pandas at module level (CI minimal-env rule).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import time
import zoneinfo
from pathlib import Path

from portfolio_sizing import is_tradable

ET = zoneinfo.ZoneInfo("America/New_York")
DEFAULT_TOP_N = 25
MAX_REPORT_AGE_DAYS = 5     # older unprocessed reports fall to the weekly cadence
_OPEN = dt.time(9, 30)

_REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = _REPO_ROOT / "tracking" / "earnings-sentinel-state.json"
SCORE_HISTORY = _REPO_ROOT / "tracking" / "score-history.csv"


def build_scope(holdings, ranked_rows, top_n=DEFAULT_TOP_N):
    """Holdings ∪ top-N tradable ranks (spec §3). Sorted, deduped."""
    tradable = [t for t, _ in sorted(ranked_rows, key=lambda r: r[1])
                if is_tradable(t)]
    return sorted(set(tradable[:top_n]) | set(holdings))


def classify_session(report_ts: dt.datetime) -> str:
    """BMO iff a real pre-open time; midnight = date-only placeholder → AMC
    (conservative: waits one extra close rather than re-scoring pre-reaction)."""
    t = report_ts.astimezone(ET).time()
    return "BMO" if dt.time(0, 0) < t < _OPEN else "AMC"


def _next_weekday(d: dt.date) -> dt.date:
    d += dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def reaction_day(report_ts: dt.datetime) -> dt.date:
    """First regular session whose close reflects the print (spec §4.3)."""
    d = report_ts.astimezone(ET).date()
    return d if classify_session(report_ts) == "BMO" else _next_weekday(d)


def due_events(scope, calendar, latest_close, state, now):
    """Spec §4.4. calendar: {t: [ET-aware datetimes]}; latest_close: {t: date}."""
    out = {"briefing_due": [], "rescore_due": [], "flagged": {}}
    tickers_state = state.get("tickers", {})
    for t in scope:
        dates = calendar.get(t)
        if not dates:
            out["flagged"][t] = "no earnings date available (rule 3: flagged, not guessed)"
            continue
        past = [ts for ts in dates if ts <= now]
        if not past:
            continue                      # next report is in the future
        report = max(past)
        rdate = report.astimezone(ET).date()
        if (now.astimezone(ET).date() - rdate).days > MAX_REPORT_AGE_DAYS:
            continue                      # pre-sentinel history / weekly cadence
        session = classify_session(report)
        ev = {"ticker": t, "report_date": rdate.isoformat(), "session": session}
        st = tickers_state.get(t, {})
        if st.get("briefed") != ev["report_date"]:
            out["briefing_due"].append(ev)
        if st.get("rescored") != ev["report_date"]:
            lc = latest_close.get(t)
            if lc is not None and lc >= reaction_day(report):
                out["rescore_due"].append(ev)
            # else: reaction close not printed yet (incl. holidays) — quiet defer
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_earnings_sentinel.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/earnings_sentinel.py tests/test_earnings_sentinel.py
git commit -m "feat: earnings sentinel pure decision core (scope, session, due events)"
```

---

### Task 2: State file + `--mark` CLI

**Files:**
- Modify: `scripts/earnings_sentinel.py` (append)
- Test: `tests/test_earnings_sentinel.py` (append)

**Interfaces:**
- Produces:
  - `load_state(path: Path) -> dict` — `{"tickers": {}}` when the file is absent.
  - `mark(path: Path, phase: str, ticker: str, report_date: str) -> None` — phase ∈ `{"briefed", "rescored"}`, atomic-enough write (write full JSON, indent=2).
  - CLI: `python3 scripts/earnings_sentinel.py --mark briefed AAA 2026-08-11`

- [ ] **Step 1: Write the failing tests (append to test file)**

```python
# ---- state / mark ----------------------------------------------------------
from earnings_sentinel import load_state, mark


def test_load_state_missing_file(tmp_path):
    assert load_state(tmp_path / "state.json") == {"tickers": {}}


def test_mark_roundtrip(tmp_path):
    p = tmp_path / "state.json"
    mark(p, "briefed", "AAA", "2026-08-11")
    mark(p, "rescored", "AAA", "2026-08-11")
    mark(p, "briefed", "BBB", "2026-08-12")
    st = load_state(p)
    assert st["tickers"]["AAA"] == {"briefed": "2026-08-11",
                                    "rescored": "2026-08-11"}
    assert st["tickers"]["BBB"] == {"briefed": "2026-08-12"}


def test_mark_rejects_bad_phase(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        mark(tmp_path / "s.json", "executed", "AAA", "2026-08-11")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_earnings_sentinel.py -v -k "state or mark"`
Expected: FAIL — ImportError on `load_state`.

- [ ] **Step 3: Implement**

```python
def load_state(path: Path = STATE_PATH) -> dict:
    path = Path(path)
    if not path.exists():
        return {"tickers": {}}
    return json.loads(path.read_text())


def mark(path: Path, phase: str, ticker: str, report_date: str) -> None:
    if phase not in ("briefed", "rescored"):
        raise ValueError(f"unknown phase {phase!r}")
    path = Path(path)
    state = load_state(path)
    state.setdefault("tickers", {}).setdefault(ticker, {})[phase] = report_date
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_earnings_sentinel.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/earnings_sentinel.py tests/test_earnings_sentinel.py
git commit -m "feat: earnings sentinel state file + mark"
```

---

### Task 3: Detection I/O and `main()`

**Files:**
- Modify: `scripts/earnings_sentinel.py` (append)
- Test: `tests/test_earnings_sentinel.py` (append)

**Interfaces:**
- Consumes: `generate_trade_ticket._targets_weights() -> (dict[str, float], meta)` — keys of the weights dict are the current holdings roster (reused for DRY; openpyxl-only, offline).
- Produces:
  - `latest_ranked_rows(csv_path: Path) -> list[tuple[str, int]]` — (ticker, rank) rows of the newest date in score-history.csv.
  - `main(argv=None) -> int` — default mode prints the due_events JSON to stdout; `--mark` mode delegates to `mark()` against `STATE_PATH`.
  - Fetch helpers `_fetch_calendar(tickers) -> dict`, `_fetch_latest_close(tickers) -> dict` (lazy yfinance; every network error caught per-ticker and converted to a flag, never a crash).

- [ ] **Step 1: Write the failing tests (append)**

```python
# ---- I/O layer -------------------------------------------------------------
import json as _json

from earnings_sentinel import latest_ranked_rows, main


def test_latest_ranked_rows_uses_newest_date_only(tmp_path):
    p = tmp_path / "score-history.csv"
    p.write_text(
        "date,ticker,total_score,rank,tier\n"
        "2026-08-07,OLD,80.0,1,X\n"
        "2026-08-11,AAA,84.0,1,X\n"
        "2026-08-11,BBB.T,82.0,2,X\n")
    assert latest_ranked_rows(p) == [("AAA", 1), ("BBB.T", 2)]


def test_main_detect_prints_json(tmp_path, monkeypatch, capsys):
    import earnings_sentinel as es
    import datetime as dt
    monkeypatch.setattr(es, "STATE_PATH", tmp_path / "state.json")
    hist = tmp_path / "score-history.csv"
    hist.write_text("date,ticker,total_score,rank,tier\n"
                    "2026-08-11,AAA,84.0,1,X\n")
    monkeypatch.setattr(es, "SCORE_HISTORY", hist)
    monkeypatch.setattr(es, "_holdings", lambda: ["AAA"])
    monkeypatch.setattr(es, "_fetch_calendar",
                        lambda ts: {"AAA": [dt.datetime(2026, 8, 11, 16, 30,
                                                        tzinfo=es.ET)]})
    monkeypatch.setattr(es, "_fetch_latest_close",
                        lambda ts: {"AAA": dt.date(2026, 8, 12)})
    monkeypatch.setattr(es, "_now",
                        lambda: dt.datetime(2026, 8, 12, 18, 30, tzinfo=es.ET))
    assert main([]) == 0
    out = _json.loads(capsys.readouterr().out)
    assert out["rescore_due"][0]["ticker"] == "AAA"


def test_main_mark_updates_state(tmp_path, monkeypatch):
    import earnings_sentinel as es
    monkeypatch.setattr(es, "STATE_PATH", tmp_path / "state.json")
    assert main(["--mark", "briefed", "AAA", "2026-08-11"]) == 0
    from earnings_sentinel import load_state
    assert load_state(tmp_path / "state.json")["tickers"]["AAA"]["briefed"] == "2026-08-11"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_earnings_sentinel.py -v -k "main or ranked"`
Expected: FAIL — ImportError on `latest_ranked_rows` / `main`.

- [ ] **Step 3: Implement**

```python
def latest_ranked_rows(csv_path: Path = SCORE_HISTORY):
    rows = list(csv.DictReader(open(csv_path)))
    if not rows:
        return []
    newest = max(r["date"] for r in rows)
    return [(r["ticker"], int(r["rank"])) for r in rows if r["date"] == newest]


def _holdings() -> list[str]:
    from generate_trade_ticket import _targets_weights   # openpyxl-only, offline
    weights, _meta = _targets_weights()
    return sorted(weights)


def _now() -> dt.datetime:
    return dt.datetime.now(tz=ET)


def _fetch_calendar(tickers):
    import yfinance as yf                                # lazy (CI minimal-env)
    out = {}
    for t in tickers:
        try:
            df = yf.Ticker(t).get_earnings_dates(limit=8)
            out[t] = ([ts.to_pydatetime().astimezone(ET) for ts in df.index]
                      if df is not None and len(df) else [])
        except Exception:
            out[t] = []                                  # → flagged downstream
        time.sleep(0.1)
    return out


def _fetch_latest_close(tickers):
    import yfinance as yf                                # lazy (CI minimal-env)
    out = {}
    for t in tickers:
        try:
            h = yf.Ticker(t).history(period="5d")
            out[t] = h.index[-1].date() if len(h) else None
        except Exception:
            out[t] = None
        time.sleep(0.1)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Earnings sentinel (detection only).")
    ap.add_argument("--mark", nargs=3, metavar=("PHASE", "TICKER", "REPORT_DATE"),
                    help="record a completed phase: briefed|rescored TICKER YYYY-MM-DD")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    args = ap.parse_args(argv)

    if args.mark:
        phase, ticker, report_date = args.mark
        mark(STATE_PATH, phase, ticker, report_date)
        print(f"marked {ticker} {phase} for report {report_date}")
        return 0

    scope = build_scope(_holdings(), latest_ranked_rows(SCORE_HISTORY), args.top_n)
    now = _now()
    calendar = _fetch_calendar(scope)
    # closes are only needed for names with a recent past report
    recent = [t for t in scope
              if any(ts <= now and
                     (now.astimezone(ET).date() - ts.astimezone(ET).date()).days
                     <= MAX_REPORT_AGE_DAYS
                     for ts in calendar.get(t, []))]
    latest_close = _fetch_latest_close(recent)
    out = due_events(scope, calendar, latest_close, load_state(STATE_PATH), now)
    out["scope_size"] = len(scope)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest tests/test_earnings_sentinel.py -v && python3 -m pytest tests/ -q`
Expected: new tests PASS; full suite green (note: pre-existing failures unrelated to this change, if any, get reported — not fixed here).

- [ ] **Step 5: Live smoke test (network, read-only)**

Run: `python3 scripts/earnings_sentinel.py`
Expected: JSON with `scope_size` ≈ 25–30, plausible `briefing_due`/`rescore_due`/`flagged` for today's date. No file written except nothing (state untouched in detect mode — verify `git status` shows no change to tracking/).

- [ ] **Step 6: Commit**

```bash
git add scripts/earnings_sentinel.py tests/test_earnings_sentinel.py
git commit -m "feat: earnings sentinel detection I/O + CLI"
```

---

### Task 4: Scheduled-task prompt, run log seed, CLAUDE.md rule

**Files:**
- Create: `docs/ops/earnings-sentinel-task.md` (the canonical prompt text, versioned in-repo)
- Create: `tracking/earnings-sentinel-log.md` (seed header)
- Modify: `CLAUDE.md` (append rule 31)

**Interfaces:**
- Consumes: the Task 3 CLI (`python3 scripts/earnings_sentinel.py`, `--mark`).
- Produces: the prompt text the orchestrating session registers with the local scheduler (cron `30 18 * * 1-5`, taskId `earnings-sentinel`). Registration itself happens in the main session after this task merges — the scheduler tool is not available to subagents.

- [ ] **Step 1: Write `docs/ops/earnings-sentinel-task.md`**

````markdown
# earnings-sentinel scheduled task — canonical prompt

Registered on the local scheduler: weekdays 18:30 ET (`30 18 * * 1-5`),
taskId `earnings-sentinel`. This file is the versioned source of the prompt;
if it changes, re-register the task.

---

You are running the earnings sentinel for the AI Supply Chain research
project (spec docs/superpowers/specs/2026-08-13-earnings-sentinel-design.md).
Working directory: /Users/dom/Desktop/ai-stocks. Use the REAL current date
(`date +%F`); never hardcode dates. Read CLAUDE.md rules 9, 12, 25, 29, 31
before starting.

STEPS:
1. Detect: `python3 scripts/earnings_sentinel.py` (JSON on stdout). If both
   `briefing_due` and `rescore_due` are empty: append one line
   "<today>: quiet (scope N, flagged: …)" to tracking/earnings-sentinel-log.md
   ONLY if `flagged` is non-empty, then STOP. Most evenings end here.
2. Git setup (only if events exist): `git fetch origin main` then
   `git checkout -b earnings/<today> origin/main` (branching discipline —
   never branch from local main).
3. BRIEFING PHASE — for each name in `briefing_due`, independently:
   - Fetch the press release / 8-K from SEC EDGAR and the transcript if
     published (fall back to WebSearch with the current year in the query).
   - Write per-stock/<TICKER>/context-<today>.md: Headline numbers vs
     consensus / Guidance / DIFF vs prior mental model / Implications for
     ratings (which D/M/R dimensions look affected — do NOT change ratings).
   - Append one line to per-stock/<TICKER>/news-log.md (date + source + summary).
   - If revenue or EPS surprise exceeds ±15% or gross margin moved >500bps
     sequentially, prefix the run-log entry with "⚠️ RULE-9 IMMEDIATE".
   - `python3 scripts/earnings_sentinel.py --mark briefed <TICKER> <report_date>`
4. RESCORE PHASE — if `rescore_due` is non-empty (run once for the whole set):
   - `python3 scripts/refresh_objective_inputs.py <TICKERS> --dry-run`, review
     output for obviously-corrupt values (rule 27 market-cap check), then run
     without --dry-run.
   - `python3 scripts/momentum_50dma.py <TICKERS>`
   - `python3 scripts/refresh_reverse_dcf.py <TICKERS>`
   - `python3 scripts/recalc_watchlist.py --sync`  (auto-chains refresh_targets,
     rule 25; a membership/tier change fires a model event + ticket, rule 29)
   - For each ticker: `python3 scripts/earnings_sentinel.py --mark rescored
     <TICKER> <report_date>`
   - Flag in the run log, do not fix: Layer-9 capacity-cohort names (EV/MW
     denominator needs human MW research, rule 13) and TTM-vs-MRQ divergence
     >10pts on any quality metric (rule 9).
5. Report: append a dated section to tracking/earnings-sentinel-log.md —
   names briefed, names re-scored with before/after Total Score and rank,
   whether a model event fired, whether a ticket was generated OR refused
   (stale/missing recon snapshot), and all flags. If a model event fired or a
   ticket was refused, also notify:
   `osascript -e 'display notification "<one-line summary>" with title
   "Earnings sentinel" sound name "Submarine"'`
6. Commit (stage explicit paths — per-stock/, tracking/earnings-sentinel-*,
   00-master/*.xlsx, tracking/score-history.csv; NEVER `git add -A`), push,
   open a PR titled "Earnings sentinel <today>". If push/PR is blocked
   (headless egress), leave the branch and note it in the run log.
7. You are read-only toward Robinhood (rule 29): never call any order/write
   tool; execution belongs exclusively to Dom's launchd executor.

SUCCESS CRITERIA: quiet exit on no-event days; on event days — sourced
briefings + news-log lines for every reporting name, the mechanical re-score
chain run exactly once, state marked, run log + notification accurate about
whether a ticket exists, no rating changes, no order tools.
````

- [ ] **Step 2: Seed `tracking/earnings-sentinel-log.md`**

```markdown
# Earnings sentinel — run log

Append-only. One dated section per event run; quiet runs log a line only when
names were flagged. Written by the `earnings-sentinel` scheduled task
(docs/ops/earnings-sentinel-task.md). Spec:
docs/superpowers/specs/2026-08-13-earnings-sentinel-design.md.
```

- [ ] **Step 3: Append rule 31 to CLAUDE.md** (after rule 30, before "## Common tools and libraries")

```markdown
### 31. Earnings sentinel: event-driven refresh for portfolio-relevant names (added 2026-08-13, approved by Dom)

Spec: `docs/superpowers/specs/2026-08-13-earnings-sentinel-design.md`. A
weekday 18:30 ET scheduled task (`earnings-sentinel`, prompt versioned at
`docs/ops/earnings-sentinel-task.md`) watches **current holdings ∪ top 25
tradable ranks** and, per `scripts/earnings_sentinel.py` (state:
`tracking/earnings-sentinel-state.json`), fires two phases per report:
**briefing** the evening of the print (context briefing + news-log + rule-9
>15%-surprise flag; ratings untouched per rule 12) and **mechanical re-score**
on the first post-reaction close (objective chain → `recalc --sync` →
rule-25/29 ticket on a real model event; trades execute via Dom's launchd
executor next morning, ~26h/~41h print-to-trade for BMO/AMC reporters).
Reports with no yfinance date, or older than 5 days when first seen, fall to
the weekly scan — which remains the rule-9 catch-all (Yahoo statement lag).
The sentinel session is read-only toward Robinhood (rule 29 unchanged); a
ticket refusal on a stale recon snapshot is notified, never worked around.
```

- [ ] **Step 4: Run the full suite (CLAUDE.md/doc changes must not break anything)**

Run: `python3 -m pytest tests/ -q`
Expected: green (same pre-existing state as Task 3 Step 4).

- [ ] **Step 5: Commit**

```bash
git add docs/ops/earnings-sentinel-task.md tracking/earnings-sentinel-log.md CLAUDE.md
git commit -m "feat: earnings sentinel task prompt, run log, CLAUDE.md rule 31"
```

---

### Post-merge steps (orchestrating session, not a subagent)

1. Push `spec/earnings-sentinel`, open the PR, get Dom's merge.
2. Register the scheduled task with the local scheduler: taskId
   `earnings-sentinel`, cron `30 18 * * 1-5`, prompt = the body of
   `docs/ops/earnings-sentinel-task.md` (below the `---`).
3. First-run watch: confirm the next evening's run exits quiet or produces a
   correct briefing; confirm state file appears only after a real event.
```
