"""Pure sizing helpers — no yfinance, runs in the openpyxl-only deploy CI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from portfolio_sizing import tier_changes, build_reason, weights_score_monotonic


def _info(d):
    return {t: {'Tier': tier} for t, tier in d.items()}


def test_tier_changes_detects_crossing():
    info = _info({'MU': '✓✓✓', 'NVDA': '✓✓'})
    last = {'MU': '✓✓', 'NVDA': '✓✓'}
    assert tier_changes(['MU', 'NVDA'], info, last) == [('MU', '✓✓', '✓✓✓')]


def test_tier_changes_ignores_within_tier_and_new_names():
    info = _info({'MU': '✓✓✓', 'APP': '✓✓'})   # APP newly entered (not in last)
    last = {'MU': '✓✓✓'}                          # MU unchanged
    assert tier_changes(['MU', 'APP'], info, last) == []


def test_build_reason_concatenates_membership_and_tier():
    r = build_reason(['APP'], ['WDC'], [('MU', '✓✓', '✓✓✓')], False)
    assert 'membership: +APP, -WDC' in r and 'tier: MU ✓✓→✓✓✓' in r


def test_build_reason_resize_only():
    assert build_reason([], [], [], True) == 'manual resize'


def test_weights_monotonic_flags_inversion():
    # MU (86.4) at 7.44 below NVDA (84.08) at 9.32 — the bug.
    rows = [(87.9, 9.6), (86.4, 7.44), (84.08, 9.32)]
    assert weights_score_monotonic(rows)   # non-empty → violation


def test_weights_monotonic_accepts_sorted():
    rows = [(87.9, 11.7), (86.4, 11.7), (84.08, 9.3), (80.1, 7.5)]
    assert weights_score_monotonic(rows) == []
