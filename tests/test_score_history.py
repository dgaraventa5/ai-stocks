"""Append-only point-in-time score panel (spec 2026-08-07 Part C2)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import score_history as sh

LIVE = [
    {'ticker': 'AAA', 'TOTAL': 81.25, 'Tier': '✓✓'},
    {'ticker': 'BBB', 'TOTAL': 90.0, 'Tier': '✓✓✓'},
    {'ticker': 'NUL', 'TOTAL': None, 'Tier': None},   # unscored: skipped
]


def test_score_history_append_only(tmp_path, monkeypatch):
    csv = tmp_path / 'score-history.csv'
    monkeypatch.setattr(sh, 'CSV', csv)
    n = sh.append_snapshot(LIVE, when='2026-08-07')
    assert n == 2                                     # exactly one row per scored name
    lines = csv.read_text().splitlines()
    assert lines[0] == 'date,ticker,total_score,rank,tier'
    assert lines[1] == '2026-08-07,BBB,90.00,1,✓✓✓'   # rank 1 = highest score
    assert lines[2] == '2026-08-07,AAA,81.25,2,✓✓'
    before = csv.read_text()
    assert sh.append_snapshot(LIVE, when='2026-08-07') == 0   # re-run: no dupes
    assert csv.read_text() == before                          # ... and no rewrite
    assert sh.append_snapshot(LIVE, when='2026-08-08') == 2   # next pass appends
    assert csv.read_text().startswith(before)                 # strictly append-only
