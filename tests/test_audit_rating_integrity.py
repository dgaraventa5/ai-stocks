"""tests/test_audit_rating_integrity.py — rule-12 gate, offline, fictional data."""
import datetime as dt
import types

import pytest
from openpyxl import Workbook

import audit_rating_integrity as ari

BASELINE = 1000


def _thesis(root, ticker, size):
    d = root.path / "per-stock" / ticker
    d.mkdir(parents=True, exist_ok=True)
    (d / "thesis.md").write_text("x" * size)


def _briefing(root, ticker, days_old):
    d = root.path / "per-stock" / ticker
    d.mkdir(parents=True, exist_ok=True)
    day = dt.date.today() - dt.timedelta(days=days_old)
    (d / f"context-{day.isoformat()}.md").write_text("briefing")


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A one-sheet-pair workbook plus an empty per-stock tree."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Watchlist"
    ws.cell(row=1, column=1, value="Ticker")
    wb.create_sheet("Rating Audit").append(["Date", "Ticker"])
    template = tmp_path / "template.md"
    template.write_text("x" * BASELINE)
    monkeypatch.setattr(ari, "ROOT", tmp_path)
    monkeypatch.setattr(ari, "TEMPLATE", template)
    monkeypatch.setattr(ari, "XLSX", tmp_path / "book.xlsx")

    def add(*tickers, rated=True):
        for t in tickers:
            r = ws.max_row + 1
            ws.cell(row=r, column=1, value=t)
            ws.cell(row=r, column=3, value="01 Power")
            if rated:
                ws.cell(row=r, column=ari.AI_COLS[0], value=3)
        wb.save(tmp_path / "book.xlsx")

    return types.SimpleNamespace(path=tmp_path, add=add)


def _row(rows, ticker):
    return next(r for r in rows if r["tkr"] == ticker)


# ---- populated-thesis threshold ---------------------------------------------

def test_thesis_needs_400_bytes_beyond_the_template(repo):
    _thesis(repo, "AAA", BASELINE + 400)
    _thesis(repo, "BBB", BASELINE + 399)
    assert ari.thesis_populated("AAA", BASELINE) is True
    assert ari.thesis_populated("BBB", BASELINE) is False


def test_missing_thesis_is_not_populated(repo):
    assert ari.thesis_populated("NOPE", BASELINE) is False


# ---- gate / stale / expired -------------------------------------------------

def test_no_research_at_all_is_a_gate_violation(repo):
    repo.add("AAA")
    row = _row(ari.audit(), "AAA")
    assert row["gate"] is True and row["expired"] is False


def test_briefing_inside_the_window_is_backed_and_not_expired(repo):
    repo.add("AAA")
    _briefing(repo, "AAA", 90)
    row = _row(ari.audit(), "AAA")
    assert row["gate"] is False and row["expired"] is False


def test_only_briefing_past_the_window_is_expired_not_gated(repo):
    repo.add("AAA")
    _briefing(repo, "AAA", 91)
    row = _row(ari.audit(), "AAA")
    assert row["expired"] is True
    assert row["gate"] is False          # the hard gate is unchanged


def test_populated_thesis_is_never_expired(repo):
    repo.add("AAA")
    _thesis(repo, "AAA", BASELINE + 400)
    _briefing(repo, "AAA", 200)
    assert _row(ari.audit(), "AAA")["expired"] is False


def test_window_follows_stale_days(repo):
    repo.add("AAA")
    _briefing(repo, "AAA", 40)
    assert _row(ari.audit(stale_days=30), "AAA")["expired"] is True
    assert _row(ari.audit(stale_days=60), "AAA")["expired"] is False


def test_unrated_name_is_ignored(repo):
    repo.add("AAA", rated=False)
    assert ari.audit() == []


# ---- split -------------------------------------------------------------------

def test_split_puts_each_name_in_one_group_held_first():
    rows = [dict(tkr=t, expired=True) for t in ("AAA", "BBB", "CCC")]
    rows.append(dict(tkr="DDD", expired=False))
    assert ari.split_expired(rows, held={"AAA"}, top={"AAA", "BBB"}) == {
        "held": ["AAA"], "top": ["BBB"], "rest": ["CCC"]}


# ---- CLI ---------------------------------------------------------------------

def _run(monkeypatch, *argv):
    monkeypatch.setattr("sys.argv", ["audit_rating_integrity.py", *argv])
    return ari.main()


@pytest.fixture
def groups(monkeypatch):
    monkeypatch.setattr(ari, "_held_and_top", lambda: ({"AAA"}, {"BBB"}))


def test_summary_prints_the_split(repo, groups, monkeypatch, capsys):
    repo.add("AAA", "BBB", "CCC")
    for t in ("AAA", "BBB", "CCC"):
        _briefing(repo, t, 100)
    assert _run(monkeypatch, "--summary") == 0
    assert "3 EXPIRED (held 1, top 25 1, rest 1)" in capsys.readouterr().out


def test_expired_alone_does_not_change_the_exit_code(repo, groups, monkeypatch):
    repo.add("AAA")
    _briefing(repo, "AAA", 100)
    assert _run(monkeypatch, "--summary") == 0
    assert _run(monkeypatch) == 0


def test_gate_violation_still_exits_nonzero(repo, groups, monkeypatch):
    repo.add("AAA")
    assert _run(monkeypatch, "--summary") == 1
    assert _run(monkeypatch) == 1


def test_unreadable_groups_keep_the_count_and_the_exit_code(repo, monkeypatch, capsys):
    def boom():
        raise OSError("no workbook")

    monkeypatch.setattr(ari, "_held_and_top", boom)
    repo.add("AAA")
    _briefing(repo, "AAA", 100)
    assert _run(monkeypatch, "--summary") == 0
    assert "1 EXPIRED (split unavailable: OSError)" in capsys.readouterr().out
