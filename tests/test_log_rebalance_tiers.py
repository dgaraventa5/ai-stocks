import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytest.importorskip('yfinance')   # portfolio_model imports yfinance at module load
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import datetime as dt_module
import portfolio_model as pm


def test_log_rebalance_stores_tiers(monkeypatch):
    cfg = {'inception': '2026-05-26',
           'events': [{'date': '2026-06-18', 'reason': 'seed',
                       'allocations': {'MU': 700.0}, 'cash': 0.0}]}
    # mark() hits the network; stub it to a fixed value with no missing names.
    monkeypatch.setattr(pm, 'mark', lambda c: (10000.0, {}, []))
    monkeypatch.setattr(pm, 'save_cfg', lambda c: None)   # don't touch disk
    # Mock dt.date.today() to return a fixed date
    mock_date = MagicMock()
    mock_date.today.return_value = dt_module.date(2026, 6, 29)
    monkeypatch.setattr(pm, 'dt', type('MockDT', (), {'date': mock_date})())

    ev = pm.log_rebalance(cfg, {'MU': 0.5, 'TSM': 0.5}, 'tier: MU ✓✓→✓✓✓',
                          {'MU': '✓✓✓', 'TSM': '✓✓'})

    assert ev['tiers'] == {'MU': '✓✓✓', 'TSM': '✓✓'}
    assert cfg['events'][-1]['tiers'] == {'MU': '✓✓✓', 'TSM': '✓✓'}
