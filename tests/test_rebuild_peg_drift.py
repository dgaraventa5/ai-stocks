"""PEG(9) drift-repair regression (2026-09-08).

The hole this guards: PEG is a per-row Watchlist formula, but nothing repaired it
after a structural row change. batch_score.append_row wrote it once at append
time, and rebuild_watchlist_formulas.py did not own it — so openpyxl row
deletions (which do NOT rewrite formula references, CLAUDE.md rule 10) drifted
PEG by +1 on 110 rows. Worse, check_drift only inspected column 10, so the
rebuild reported "0 rows with drifted formula refs" while leaving all 110 broken.

Live scores were never affected (recalc_watchlist recomputes PEG in Python), but
the workbook itself showed every company its neighbour's PEG.

Only openpyxl + rebuild are imported here, deliberately: this must keep running
in the minimal deploy CI, which has no yfinance/pandas.
"""
import sys
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import rebuild_watchlist_formulas as rebuild  # noqa: E402

PEG_COL = 9


def _fill(template: str, r: int) -> str:
    """Same substitution main() uses: {F} is the layer-conditional col-F band
    (rule 10/13), {r} the row. NOT str.format — the templates contain literal
    Excel braces-free text but {F} is not a format field."""
    return (template.replace("{F}", rebuild.f_segment_for("06 AI Compute Silicon"))
                    .replace("{r}", str(r)))


def _sheet(n_rows: int = 4):
    """Minimal Watchlist: ticker in col 1, layer in col 3 (rebuild reads both)."""
    wb = Workbook()
    ws = wb.active
    ws.cell(row=1, column=1, value="Ticker")
    for r in range(2, 2 + n_rows):
        ws.cell(row=r, column=1, value=f"T{r}")
        ws.cell(row=r, column=3, value="06 AI Compute Silicon")
    return ws


def test_rebuild_owns_peg():
    """PEG must stay in the rebuilt set — dropping it reopens the 110-row bug."""
    assert PEG_COL in rebuild.COLS, "PEG(9) fell out of rebuild.COLS"


def test_check_drift_detects_drifted_peg():
    """A PEG referencing the row BELOW must be reported, not silently passed.

    This is the exact shape seen in the live workbook (row 86 held E87/R87) and
    the case the old col-10-only check_drift missed.
    """
    ws = _sheet()
    for r in range(2, 6):
        ws.cell(row=r, column=PEG_COL, value=_fill(rebuild.PEG, r))
    assert rebuild.check_drift(ws) == [], "clean sheet reported as drifted"

    ws.cell(row=4, column=PEG_COL, value=_fill(rebuild.PEG, 5))  # off by +1
    drifted = rebuild.check_drift(ws)
    assert [d[0] for d in drifted] == [4], f"PEG drift on row 4 not caught: {drifted}"


def test_check_drift_ignores_cross_sheet_refs():
    """TOTAL references Weights!$B$4..$B$9 — absolute refs to another sheet must
    not be mistaken for row drift (that would make every row a false positive)."""
    ws = _sheet()
    for r in range(2, 6):
        for col, template in rebuild.COLS.items():
            ws.cell(row=r, column=col, value=_fill(template, r))
    assert rebuild.check_drift(ws) == [], "cross-sheet refs misread as row drift"
