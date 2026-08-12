"""Pure sizing helpers + the committed-Targets monotonicity gate.
No yfinance — runs in the openpyxl-only deploy CI."""
import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from portfolio_sizing import tier_changes, build_reason, weights_score_monotonic

_REPO = Path(__file__).resolve().parent.parent


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


def test_targets_weights_monotonic():
    """Data gate: the committed Targets sheet's included weights must be monotonic
    in score — a ✓✓✓ name can never be weighted below a ✓✓ name (the MU bug).
    openpyxl only, so it runs in the deploy CI; green once the corrective is committed.
    Scoped to tier sizing: inverse-vol weights (v2 spec A0) are deliberately NOT
    score-ordered — the EW_ROSTER shadow series audits sizing there instead."""
    from portfolio_model import load_pcfg
    if load_pcfg()['sizing']['mode'] == 'inverse_vol':
        pytest.skip('rule-18 monotonicity gate applies to tier sizing only '
                    '(v2 spec A0: the score is no longer the sizer)')
    ws = openpyxl.load_workbook(_REPO / '00-master' / 'portfolio.xlsx')['Targets']
    rows = [(float(r[2]), float(r[8]))
            for r in ws.iter_rows(min_row=3, values_only=True)
            if r[0] and str(r[6]).strip().upper() == 'Y'
            and r[2] is not None and r[8] is not None]
    assert rows, 'no included Targets rows found'
    assert weights_score_monotonic(rows) == []


# ---- tradability filter (spec 2026-08-11) ----------------------------------

def test_is_tradable_us_listings():
    from portfolio_sizing import is_tradable
    assert all(is_tradable(t) for t in ('NVDA', 'BRK-B', 'TSM', 'MELI'))


def test_is_tradable_rejects_exchange_suffixes():
    from portfolio_sizing import is_tradable
    foreign = ('6861.T', '6268.T', 'KGX.DE', '0981.HK', '5347.TWO',
               'AUTO.OL', 'MELE.BR', 'DRO.AX', '2049.TW')
    assert not any(is_tradable(t) for t in foreign)


def test_pcfg_defaults_tradable_only_false(monkeypatch, tmp_path):
    import portfolio_model as pm
    monkeypatch.setattr(pm, 'PCONFIG', tmp_path / 'missing.json')
    assert pm.load_pcfg()['selection']['tradable_only'] is False
