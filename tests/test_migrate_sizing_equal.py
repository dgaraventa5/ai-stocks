"""Equal-weight sizing migration (2026-09-08 flip): the INVVOL_ROSTER shadow
must start exactly where the live inverse-vol book leaves off."""
import sys
from pathlib import Path

import pytest

pytest.importorskip('yfinance')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import migrate_sizing_equal as ms


def _cfg():
    return {'inception': '2026-05-26', 'events': [
        {'date': '2026-09-04', 'kind': 'resize_monthly', 'reason': 'x',
         'allocations': {'NVDA': 600.0, 'TSM': 300.0, 'MU': 100.0},
         'cash': 0.0}]}


def test_seed_shadow_from_last_event_allocations():
    cfg = _cfg()
    ms.seed_invvol_shadow(cfg, '2026-09-07')
    evs = cfg['shadow_events']['INVVOL_ROSTER']
    assert evs == [{'date': '2026-09-07', 'roster': ['MU', 'NVDA', 'TSM'],
                    'weights': {'MU': 0.1, 'NVDA': 0.6, 'TSM': 0.3}}]


def test_seed_is_same_day_idempotent():
    cfg = _cfg()
    ms.seed_invvol_shadow(cfg, '2026-09-07')
    ms.seed_invvol_shadow(cfg, '2026-09-07')
    assert len(cfg['shadow_events']['INVVOL_ROSTER']) == 1


def test_seed_refuses_to_clobber_an_existing_shadow():
    cfg = _cfg()
    cfg['shadow_events'] = {'INVVOL_ROSTER': [
        {'date': '2026-09-01', 'roster': ['NVDA'], 'weights': {'NVDA': 1.0}}]}
    with pytest.raises(ValueError):
        ms.seed_invvol_shadow(cfg, '2026-09-07')
