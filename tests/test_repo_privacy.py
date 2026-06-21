"""Public-repo privacy gate: the repo's own COMMITTED SOURCE files must carry
no real-account dollars — only the $10k notional base.

This complements test_export_site_data.test_privacy_no_real_dollars_anywhere,
which guards the exported site/data OUTPUT. That gate is enough while the repo
is private (only the site is shared). Once the repo itself is public, the
committed INPUTS upstream of the exporter become world-readable too, so they
must already be notional. These tests run against the real repo tree, not the
synthetic conftest fixture.
"""
import json
from pathlib import Path

import openpyxl

import export_site_data as ex

ROOT = Path(__file__).resolve().parent.parent
TRACKING = ROOT / 'tracking'


def _config() -> dict:
    return json.loads((TRACKING / 'performance-config.json').read_text())


def _series() -> dict:
    return json.loads((TRACKING / 'performance-series.json').read_text())


def test_config_capital_is_notional_base():
    """capital IS the $10k notional base, so the exporter scales by 1.0 and
    nothing real-dollar-derived can leak through it."""
    assert _config()['capital'] == ex.NOTIONAL


def test_performance_series_is_notional_not_real_account():
    model = _series()['model']
    assert 9500 <= model[0] <= 10500, f'series starts at {model[0]}, not ~10k'
    # The real account peaked near $14,876; a notional series cannot.
    assert max(model) < 11500, f'series peaks at {max(model)} — looks real'


def test_portfolio_workbook_has_no_real_capital():
    wb = openpyxl.load_workbook(ROOT / '00-master' / 'portfolio.xlsx',
                                data_only=True)
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            for cell in row:
                assert cell not in (13800, 13800.0), \
                    f'real capital 13800 in sheet {ws.title!r}'
                if isinstance(cell, str):
                    assert '13,800' not in cell and '13800' not in cell, \
                        f'real capital in sheet {ws.title!r}: {cell!r}'
