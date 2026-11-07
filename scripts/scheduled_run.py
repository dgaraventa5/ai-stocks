"""Deterministic helpers for the unattended scheduled reports (CLAUDE.md rule 37).

The scheduled skills (/daily-watch, /weekly-scan, /rating-research) are run by
an LLM session with nobody at the keyboard. Everything that must not be left
to judgment lives here instead:

  preflight      prove the run can work BEFORE it starts — SEC and Yahoo are
                 reachable, the checkout is a clean, current `main`, GitHub is
                 logged in, no earlier scheduled run is still open — and take
                 a lock. Before the checks it finishes an earlier run that
                 committed its work but was cut off before merging (pushes,
                 opens the PR, merges on green CI, returns to main) — one
                 interrupted run must not block every run after it.
                 Any failure exits 1 with a plain reason. A run that
                 cannot reach its data sources stops; it never degrades to a
                 partial report (the 2026-06..09 cloud scans did, for months).
  scan-filings   list recent 8-K / 6-K filings from SEC EDGAR for the watch
                 scope or the whole watchlist. Fetch failures are counted and
                 a high failure rate exits 1 — "no filings" and "could not
                 look" must never read the same.
  branch         create this run's branch (auto/<job>-<date>) from origin/main.
  log            append this run's one-line outcome to the committed run log
                 (tracking/scheduled-run-log.md). Every run logs, quiet or
                 not, so each one ends in a merged record and a missed run is
                 a missing date.
  land           stage ONLY research/score paths, refuse if anything else (or
                 anything under tracking/live/) is staged, commit, push the
                 run's own branch (with retries), open the PR. Re-running it
                 after a failed push resumes from the existing commit.
                 `--hold` (tests failed) opens a draft PR that nothing merges.
  merge          wait for CI on that PR, squash-merge it, sync local main.
  notify         show one macOS notification (Dom, 2026-10-13: the in-app push
                 was skipped because the run's own window counted as active).
  release        drop the lock.

branch/land/merge exist so the unattended session needs no raw git or gh
write permission: the branch name, the staged paths and the PR merged are all
fixed here, not chosen by the model.

Names no order tool and sends nothing to the broker (rule 29). Imports
requests / yfinance / openpyxl lazily (CI minimal-env rule).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / ".cache" / "scheduled-run.lock"
LIVE_DIR = ROOT / "tracking" / "live"
WORKBOOK_LOCK = ROOT / "00-master" / "~$ai_supply_chain_scoring.xlsx"
LOCK_MAX_AGE_HOURS = 4          # a crashed run must not block the next one forever
RUN_BRANCH_PREFIX = "auto/"     # every scheduled run's branch: auto/<job>-<date>
MAX_FETCH_FAILURE_RATE = 0.20   # above this the scan is treated as blocked
FILING_FORMS = {"8-K", "8-K/A", "6-K"}
EARNINGS_ITEM = "2.02"
LAND_PATHS = ["per-stock", "00-master", "tracking"]   # the only stageable roots
PRIVATE_PREFIX = "tracking/live/"
RUN_LOG = ROOT / "tracking" / "scheduled-run-log.md"
RUN_LOG_HEADER = (
    "# Scheduled run log\n\n"
    "One line per scheduled run (rule 37), written by "
    "`scripts/scheduled_run.py log`. Append-only.\n\n")
CI_WAIT_SECONDS = 20 * 60


# ── pure decisions (unit-tested) ────────────────────────────────────────────

def lock_is_live(lock: dict | None, now: dt.datetime,
                 max_age_hours: float = LOCK_MAX_AGE_HOURS) -> bool:
    """A lock blocks a new run only while it is younger than max_age_hours."""
    if not lock or "started" not in lock:
        return False
    try:
        started = dt.datetime.fromisoformat(lock["started"])
    except ValueError:
        return False
    return (now - started) < dt.timedelta(hours=max_age_hours)


# Status files the launchd executor's morning reconciliation rewrites in the
# main checkout every trading day (already sanitized, rule 29). They are not
# someone's unfinished work: the run carries them onto its branch and `land`
# commits them. Blocking on them refused every afternoon run (2026-10-13).
MACHINE_WRITTEN = frozenset({"tracking/live-status.json",
                             "tracking/live-vs-model.json"})


def git_problems(branch: str, modified: list[str], ahead: int) -> list[str]:
    """Why this checkout cannot host an unattended run (empty = fine)."""
    out = []
    modified = [m for m in modified if m not in MACHINE_WRITTEN]
    if branch != "main":
        out.append(f"checkout is on '{branch}', not main — another session is "
                   f"mid-work here")
    if modified:
        shown = ", ".join(modified[:5]) + (" …" if len(modified) > 5 else "")
        out.append(f"{len(modified)} tracked file(s) have uncommitted changes "
                   f"({shown})")
    if ahead:
        out.append(f"local main is {ahead} commit(s) ahead of origin/main "
                   f"(unpushed work)")
    return out


def open_run_prs(prs: list[dict]) -> list[str]:
    """Open PRs left behind by an earlier scheduled run."""
    return [f"#{p['number']} ({p['headRefName']})" for p in prs
            if str(p.get("headRefName", "")).startswith(RUN_BRANCH_PREFIX)]


def filings_in_window(recent: dict, start: dt.date, end: dt.date,
                      forms: set[str] = FILING_FORMS) -> list[dict]:
    """Filter a submissions-JSON `filings.recent` block to forms in [start, end]."""
    out = []
    cols = [recent.get(k, []) for k in
            ("form", "accessionNumber", "filingDate", "primaryDocument", "items")]
    for form, acc, fdate, doc, items in zip(*cols):
        if form not in forms:
            continue
        try:
            d = dt.date.fromisoformat(fdate)
        except (TypeError, ValueError):
            continue
        if start <= d <= end:
            item_list = [i.strip() for i in str(items or "").split(",") if i.strip()]
            out.append({"form": form, "date": fdate, "accession": acc,
                        "doc": doc, "items": item_list,
                        "earnings": EARNINGS_ITEM in item_list})
    return out


def scan_blocked(n_attempted: int, n_failed: int,
                 max_rate: float = MAX_FETCH_FAILURE_RATE) -> bool:
    """True when too many lookups failed for the result to mean anything."""
    if n_attempted == 0:
        return True
    return (n_failed / n_attempted) > max_rate


def staged_violations(paths: list[str]) -> list[str]:
    """Staged files a scheduled run must never commit (empty = fine)."""
    ok_roots = tuple(r + "/" for r in LAND_PATHS)
    return sorted(p for p in paths
                  if p.startswith(PRIVATE_PREFIX) or not p.startswith(ok_roots))


def run_branch(lock: dict | None) -> str | None:
    """The one branch this run may create, push and merge."""
    if not lock or not lock.get("job") or not lock.get("started"):
        return None
    job = "".join(c for c in str(lock["job"]) if c.isalnum() or c == "-")
    return f"{RUN_BRANCH_PREFIX}{job}-{str(lock['started'])[:10]}"


def run_log_line(lock: dict | None, text: str) -> str | None:
    """`- **<date>** (<job>) — <text>` for this run, or None without a lock.
    The text is flattened to one line so the file stays one line per run."""
    if not lock or not lock.get("job") or not lock.get("started"):
        return None
    flat = " ".join(str(text).split())
    if not flat:
        return None
    return f"- **{str(lock['started'])[:10]}** ({lock['job']}) — {flat}"


# Interrupted landings (2026-11-06). The 2026-11-04 run's push was cut off when
# the Mac slept; `land` could not be re-run once its commit existed, the
# checkout stayed on the run branch, and the next two runs refused at
# preflight. Now `land` resumes, pushes retry, and preflight finishes a
# stranded run's landing before it checks anything else.
HOLD_TRAILER = "Scheduled-run: hold"   # a run that chose not to merge (test failure)
PUSH_TIMEOUT = 300
PUSH_RETRY_DELAYS = (15, 60)


def land_action(staged: list[str], ahead: int) -> str:
    """'commit' new work; 'resume' an earlier land whose commit exists but
    never reached its PR; 'nothing' when there is no work at all."""
    if staged:
        return "commit"
    return "resume" if ahead > 0 else "nothing"


def retry(attempt, delays=PUSH_RETRY_DELAYS, sleep=time.sleep) -> tuple[int, str]:
    """Call attempt() until it returns rc 0, sleeping each delay in turn
    between tries. Returns the last (rc, output)."""
    rc, out = attempt()
    for delay in delays:
        if rc == 0:
            break
        sleep(delay)
        rc, out = attempt()
    return rc, out


def ci_state(checks: str) -> str:
    """'fail', 'pass' or 'pending' from `gh pr checks` output."""
    if "fail" in checks:
        return "fail"
    if "pass" in checks and "pending" not in checks:
        return "pass"
    return "pending"


def is_held(message: str) -> bool:
    return HOLD_TRAILER in str(message)


def stranded_plan(branch: str, modified: list[str], ahead: int,
                  pr: dict | None, held: bool) -> tuple[str, str]:
    """What preflight does with a checkout left on an earlier run's branch.

    none    — not on a run branch; the ordinary checks decide.
    open_pr — committed work never reached GitHub: push it and open its PR.
    merge   — its PR is open: merge it once CI passes.
    return  — nothing left to land: go back to main.
    refuse  — a person has to look (the reason says why).
    Only work `land` already committed and vetted is ever landed; uncommitted
    work, a deliberate hold or a closed PR stays with Dom."""
    if not branch.startswith(RUN_BRANCH_PREFIX):
        return "none", ""
    dirty = [m for m in modified if m not in MACHINE_WRITTEN]
    if dirty:
        return "refuse", (f"earlier run {branch} stopped with uncommitted work "
                          f"({', '.join(dirty[:5])})")
    if held:
        return "refuse", f"earlier run {branch} was held on purpose (test failure)"
    if pr:
        state = str(pr.get("state", "")).upper()
        if state == "MERGED":
            return "return", f"#{pr.get('number')} already merged"
        if state != "OPEN":
            return "refuse", f"earlier run's PR #{pr.get('number')} was closed unmerged"
        if pr.get("isDraft"):
            return "refuse", f"earlier run's PR #{pr.get('number')} is held as a draft"
        return "merge", f"#{pr.get('number')} open"
    if ahead <= 0:
        return "return", "run branch has no commits"
    return "open_pr", f"{ahead} commit(s) never reached GitHub"


# ── side-effecting shell ────────────────────────────────────────────────────

def _run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def _read_lock() -> dict | None:
    try:
        return json.loads(LOCK_PATH.read_text())
    except (OSError, ValueError):
        return None


def _check_sec() -> str | None:
    try:
        from common import sec_get
        r = sec_get("https://data.sec.gov/submissions/CIK0001045810.json",
                    host_data_sec=True)
        if "filings" not in r.json():
            return "SEC EDGAR answered but without filing data"
    except Exception as e:                       # noqa: BLE001 — report, don't trace
        return f"SEC EDGAR unreachable ({type(e).__name__}: {str(e)[:120]})"
    return None


def _check_yahoo() -> str | None:
    try:
        import yfinance as yf
        h = yf.Ticker("NVDA").history(period="5d")
        if not len(h):
            return "Yahoo Finance returned no price rows for NVDA"
    except Exception as e:                       # noqa: BLE001
        return f"Yahoo Finance unreachable ({type(e).__name__}: {str(e)[:120]})"
    return None


def preflight(job: str) -> int:
    now = dt.datetime.now()
    problems: list[str] = []

    lock = _read_lock()
    if lock_is_live(lock, now):
        problems.append(f"another scheduled run holds the lock "
                        f"({lock.get('job')} since {lock.get('started')})")

    if WORKBOOK_LOCK.exists():
        problems.append("the scoring workbook is open in Excel — close it")

    recovered: list[str] = []
    if not problems:              # never touch a branch a live run may own
        recovered, stuck = recover_stranded()
        problems += stuck

    _, branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    _, status = _run(["git", "status", "--porcelain", "--untracked-files=no"])
    modified = [ln.split(maxsplit=1)[1] for ln in status.splitlines()
                if len(ln.split(maxsplit=1)) == 2]
    rc, out = _run(["git", "fetch", "origin", "main"], timeout=120)
    if rc:
        problems.append(f"git fetch failed ({out[:120]})")
    _, ahead = _run(["git", "rev-list", "--count", "origin/main..main"])
    problems += git_problems(branch, modified, int(ahead) if ahead.isdigit() else 0)

    rc, out = _run(["gh", "pr", "list", "--state", "open", "--json",
                    "number,headRefName"])
    if rc:
        problems.append(f"GitHub CLI not usable ({out[:120]}) — run `gh auth login`")
    else:
        stuck = open_run_prs(json.loads(out or "[]"))
        if stuck:
            problems.append("an earlier scheduled run's PR is still open: "
                            + ", ".join(stuck))

    for check in (_check_sec, _check_yahoo):
        msg = check()
        if msg:
            problems.append(msg)

    if not problems:                              # only now touch the checkout
        rc, out = _run(["git", "merge", "--ff-only", "origin/main"])
        if rc:
            problems.append(f"could not fast-forward main ({out[:120]})")

    if problems:
        print(json.dumps({"ok": False, "job": job, "problems": problems,
                          "recovered": recovered}, indent=2, ensure_ascii=False))
        return 1

    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(json.dumps({
        "job": job, "started": now.isoformat(timespec="seconds")}, indent=2))
    print(json.dumps({"ok": True, "job": job,
                      "branch": f"{RUN_BRANCH_PREFIX}{job}-{now:%Y-%m-%d}",
                      "date": f"{now:%Y-%m-%d}", "recovered": recovered},
                     indent=2, ensure_ascii=False))
    return 0


def _scope(kind: str) -> list[str]:
    if kind == "watch":
        import earnings_sentinel as es
        return es.build_scope(es._holdings(),
                              es.latest_ranked_rows(es.SCORE_HISTORY))
    from openpyxl import load_workbook
    ws = load_workbook(ROOT / "00-master" / "ai_supply_chain_scoring.xlsx",
                       read_only=True, data_only=True)["Watchlist"]
    out = []
    for (t,) in ws.iter_rows(min_row=2, max_col=1, values_only=True):
        if not t:
            break
        out.append(str(t).strip().upper())
    return out


def scan_filings(scope: str, days: int, out_path: str | None) -> int:
    from common import cik_for, sec_get
    end = dt.date.today()
    start = end - dt.timedelta(days=days)
    tickers = _scope(scope)
    filings, no_cik, failed = [], [], []
    for t in tickers:
        if "." in t:                    # foreign local line: no EDGAR filings
            no_cik.append(t)
            continue
        cik = cik_for(t)
        if not cik:
            no_cik.append(t)
            continue
        try:
            data = sec_get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                           host_data_sec=True).json()
        except Exception as e:                    # noqa: BLE001
            failed.append({"ticker": t, "error": f"{type(e).__name__}: {str(e)[:80]}"})
            continue
        for f in filings_in_window(data.get("filings", {}).get("recent", {}),
                                   start, end):
            acc = f["accession"].replace("-", "")
            f.update(ticker=t, url=(f"https://www.sec.gov/Archives/edgar/data/"
                                    f"{int(cik)}/{acc}/{f['doc']}"))
            filings.append(f)
        time.sleep(0.02)
    attempted = len(tickers) - len(no_cik)
    report = {"scope": scope, "from": start.isoformat(), "to": end.isoformat(),
              "tickers": len(tickers), "attempted": attempted,
              "filings": sorted(filings, key=lambda f: (f["date"], f["ticker"])),
              "earnings": sorted({f["ticker"] for f in filings if f["earnings"]}),
              "no_edgar": no_cik, "failed": failed,
              "blocked": scan_blocked(attempted, len(failed))}
    text = json.dumps(report, indent=2)
    if out_path:
        Path(out_path).write_text(text + "\n")
        print(f"{len(filings)} filings from {attempted} names "
              f"({len(failed)} lookups failed, {len(no_cik)} not on EDGAR) "
              f"→ {out_path}")
    else:
        print(text)
    if report["blocked"]:
        print("SCAN BLOCKED: too many SEC lookups failed — do not report this "
              "window as quiet", file=sys.stderr)
        return 1
    return 0


def _fail(msg: str) -> int:
    print(json.dumps({"ok": False, "problem": msg}, indent=2, ensure_ascii=False))
    return 1


def _current_branch() -> str:
    return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])[1]


def branch() -> int:
    name = run_branch(_read_lock())
    if not name:
        return _fail("no lock — run preflight first")
    rc, out = _run(["git", "checkout", "-b", name, "origin/main"])
    if rc:
        return _fail(f"could not create {name}: {out[:160]}")
    print(json.dumps({"ok": True, "branch": name}))
    return 0


def log(text: str) -> int:
    lock = _read_lock()
    name = run_branch(lock)
    if not name or _current_branch() != name:
        return _fail(f"not on this run's branch ({name}) — run branch first")
    line = run_log_line(lock, text)
    if not line:
        return _fail("nothing to log")
    body = RUN_LOG.read_text() if RUN_LOG.exists() else RUN_LOG_HEADER
    RUN_LOG.write_text(body.rstrip("\n") + "\n" + line + "\n")
    print(json.dumps({"ok": True, "logged": line}, ensure_ascii=False))
    return 0


def _ahead_of_origin() -> int:
    _, n = _run(["git", "rev-list", "--count", "origin/main..HEAD"])
    return int(n) if n.isdigit() else 0


def _push(name: str) -> tuple[int, str]:
    """Push HEAD to the run's branch, retrying: a push cut off by sleep or a
    network blip often lands seconds later, and re-pushing is idempotent."""
    return retry(lambda: _run(["git", "push", "-u", "origin",
                               f"HEAD:refs/heads/{name}"], timeout=PUSH_TIMEOUT))


def _find_pr(name: str) -> dict | None:
    """The newest PR for a run branch, in any state, or None."""
    rc, out = _run(["gh", "pr", "list", "--head", name, "--state", "all",
                    "--json", "number,state,isDraft", "--limit", "1"])
    if rc:
        return None
    try:
        prs = json.loads(out or "[]")
    except ValueError:
        return None
    return prs[0] if prs else None


def _open_pr(name: str, title: str, body: str | None, body_file: str | None,
             draft: bool) -> tuple[int | None, str]:
    """Reuse the branch's open PR or create one. Returns (number, problem)."""
    pr = _find_pr(name)
    if pr and str(pr.get("state", "")).upper() == "OPEN":
        return pr.get("number"), ""
    cmd = ["gh", "pr", "create", "--head", name, "--base", "main",
           "--title", title[:120]]
    cmd += ["--body-file", body_file] if body_file else ["--body", body or title]
    if draft:
        cmd.append("--draft")
    rc, out = retry(lambda: _run(cmd, timeout=120))
    if rc:
        return None, f"PR not created: {out[:160]}"
    pr = _find_pr(name)
    return (pr or {}).get("number"), ""


def _wait_ci(pr: int) -> str:
    """'pass', 'fail' or 'pending' (CI still running at the deadline)."""
    deadline = time.time() + CI_WAIT_SECONDS
    while True:
        _, checks = _run(["gh", "pr", "checks", str(pr)])
        state = ci_state(checks)
        if state != "pending" or time.time() > deadline:
            return state
        time.sleep(10)


def _merge_pr(pr: int) -> str:
    """Squash-merge once CI passes. Returns a problem, or '' on success."""
    state = _wait_ci(pr)
    if state == "fail":
        return f"CI failed on PR #{pr} — left open"
    if state != "pass":
        return f"CI did not finish on PR #{pr} — left open"
    rc, out = retry(lambda: _run(["gh", "pr", "merge", str(pr), "--squash",
                                  "--delete-branch"], timeout=180))
    return f"merge failed: {out[:160]}" if rc else ""


def _return_to_main(name: str) -> str:
    """Leave a landed run branch for an up-to-date main. Returns a problem or ''.
    The executor's reconciliation files ride along (MACHINE_WRITTEN)."""
    _run(["git", "fetch", "origin", "main"], timeout=120)
    rc, _ = _run(["git", "merge-base", "--is-ancestor", "main", "origin/main"])
    if rc:
        return "local main has commits origin/main does not (unpushed work)"
    rc, out = _run(["git", "checkout", "-B", "main", "origin/main"])
    if rc:
        return f"could not return to main: {out[:120]}"
    _run(["git", "branch", "-D", name])
    return ""


def recover_stranded() -> tuple[list[str], list[str]]:
    """Finish an earlier run that committed its work but was cut off before
    it merged (sleep, network). Returns (what was done, problems)."""
    done: list[str] = []
    branch = _current_branch()
    if not branch.startswith(RUN_BRANCH_PREFIX):
        return done, []
    _, status = _run(["git", "status", "--porcelain", "--untracked-files=no"])
    modified = [ln.split(maxsplit=1)[1] for ln in status.splitlines()
                if len(ln.split(maxsplit=1)) == 2]
    rc, out = _run(["git", "fetch", "origin", "main"], timeout=120)
    if rc:
        return done, [f"git fetch failed ({out[:120]})"]
    _, msg = _run(["git", "log", "-1", "--format=%B"])
    pr = _find_pr(branch)
    action, why = stranded_plan(branch, modified, _ahead_of_origin(), pr,
                                is_held(msg))
    if action == "refuse":
        return done, [why]
    number = (pr or {}).get("number")
    if action == "open_pr":
        rc, out = _push(branch)
        if rc:
            return done, [f"could not push earlier run {branch}: {out[:120]}"]
        title = msg.strip().splitlines()[0] if msg.strip() else branch
        body = (msg.strip() + "\n\nLanded by the next scheduled run's preflight: "
                "the original run committed this work but was cut off before "
                "it merged.")
        number, problem = _open_pr(branch, title, body, None, draft=False)
        if problem or not number:
            return done, [problem or f"PR for {branch} not found after create"]
        done.append(f"pushed {branch} and opened #{number}")
        action = "merge"
    if action == "merge":
        problem = _merge_pr(number)
        if problem:
            return done, [f"earlier run {branch}: {problem}"]
        done.append(f"merged #{number}")
    problem = _return_to_main(branch)
    if problem:
        return done, [problem]
    done.append(f"returned from {branch} to main")
    return done, []


def land(message: str, body_file: str | None, hold: bool = False) -> int:
    lock = _read_lock()
    name = run_branch(lock)
    if not name or _current_branch() != name:
        return _fail(f"not on this run's branch ({name})")
    _run(["git", "add", "--", *LAND_PATHS])
    _, staged = _run(["git", "diff", "--cached", "--name-only"])
    paths = [p for p in staged.splitlines() if p.strip()]
    bad = staged_violations(paths)
    if bad:
        _run(["git", "reset", "-q"])
        return _fail("refusing to commit: " + ", ".join(bad[:8]))
    action = land_action(paths, _ahead_of_origin())
    if action == "nothing":
        return _fail("nothing to commit")
    if action == "commit":
        full = f"{message}\n\n{HOLD_TRAILER}" if hold else message
        rc, out = _run(["git", "commit", "-q", "-m", full])
        if rc:
            return _fail(f"commit failed: {out[:160]}")
    rc, out = _push(name)
    if rc:
        return _fail(f"push failed after retries: {out[:160]} — re-run land; "
                     f"it resumes from the existing commit")
    number, problem = _open_pr(name, message.splitlines()[0], message, body_file,
                               draft=hold)
    if problem:
        return _fail(problem)
    lock["pr"] = number
    LOCK_PATH.write_text(json.dumps(lock, indent=2))
    print(json.dumps({"ok": True, "pr": number, "files": len(paths),
                      "resumed": action == "resume", "held": hold}))
    return 0


def merge() -> int:
    lock = _read_lock() or {}
    name, pr = run_branch(lock), lock.get("pr")
    if not name or not pr:
        return _fail("no PR recorded for this run — run land first")
    rc, head = _run(["gh", "pr", "view", str(pr), "--json", "headRefName",
                     "-q", ".headRefName"])
    if rc or head != name:
        return _fail(f"PR #{pr} is not this run's branch ({head!r} != {name!r})")
    problem = _merge_pr(pr)
    if problem:
        return _fail(problem)
    problem = _return_to_main(name)
    if problem:
        return _fail(f"merged, but {problem}")
    print(json.dumps({"ok": True, "merged": pr}))
    return 0


def notify_args(message: str) -> list[str] | None:
    """osascript argv for one macOS notification. The text travels as an
    argument, never inside the script, so it cannot inject AppleScript."""
    line = " ".join(str(message).split())[:230]
    if not line:
        return None
    return ["osascript",
            "-e", "on run argv",
            "-e", 'display notification (item 1 of argv) with title "AI stocks" '
                  'sound name "Submarine"',
            "-e", "end run", "--", line]


def notify(message: str) -> int:
    args = notify_args(message)
    if not args:
        return _fail("empty notification")
    rc, out = _run(args, timeout=20)
    if rc:
        return _fail(f"notification not shown: {out[:160]}")
    print(json.dumps({"ok": True, "notified": args[-1]}, ensure_ascii=False))
    return 0


def release() -> int:
    LOCK_PATH.unlink(missing_ok=True)
    print("lock released")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight")
    p.add_argument("--job", required=True)
    s = sub.add_parser("scan-filings")
    s.add_argument("--scope", choices=["watch", "all"], default="watch")
    s.add_argument("--days", type=int, default=3)
    s.add_argument("--out")
    sub.add_parser("branch")
    lg = sub.add_parser("log")
    lg.add_argument("--text", required=True)
    ln = sub.add_parser("land")
    ln.add_argument("--message", required=True)
    ln.add_argument("--body-file")
    ln.add_argument("--hold", action="store_true",
                    help="tests failed: open the PR as a draft and do not merge; "
                         "the next preflight refuses until Dom deals with it")
    sub.add_parser("merge")
    nt = sub.add_parser("notify")
    nt.add_argument("--message", required=True)
    sub.add_parser("release")
    a = ap.parse_args(argv)
    if a.cmd == "preflight":
        return preflight(a.job)
    if a.cmd == "scan-filings":
        return scan_filings(a.scope, a.days, a.out)
    if a.cmd == "branch":
        return branch()
    if a.cmd == "log":
        return log(a.text)
    if a.cmd == "land":
        return land(a.message, a.body_file, a.hold)
    if a.cmd == "merge":
        return merge()
    if a.cmd == "notify":
        return notify(a.message)
    return release()


if __name__ == "__main__":
    sys.exit(main())
