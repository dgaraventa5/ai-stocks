"""--series-only: the daily site-refresh path must not touch the weekly log."""
import sys

import pytest

# portfolio_model imports yfinance at module level; deploy-site CI installs
# only openpyxl+pytest and must keep passing without it.
pytest.importorskip('yfinance')

import track_performance as tp


def test_series_only_builds_series_and_skips_log(monkeypatch, tmp_path):
    built = []
    monkeypatch.setattr(tp, 'load_cfg', lambda: {'sentinel': True})
    monkeypatch.setattr(tp, 'build_daily_series', lambda cfg: built.append(cfg))
    monkeypatch.setattr(tp, 'mark',
                        lambda cfg: pytest.fail('mark() must not run'))
    log = tmp_path / 'performance-log.md'
    monkeypatch.setattr(tp, 'LOG', log)
    monkeypatch.setattr(sys, 'argv', ['track_performance.py', '--series-only'])

    tp.main()

    assert built == [{'sentinel': True}]
    assert not log.exists()
