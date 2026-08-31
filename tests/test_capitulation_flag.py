"""Capitulation flag (rule 32-A): the mirror of the rule-14 expectations flag.

Pure decision logic + rule-17 forecast logging only — the yfinance/SEC I/O
path is exercised manually (same stance as expectations_flag, which has no
test file at all). Everything imported here is stdlib/openpyxl-safe for the
deploy-site CI env.
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import capitulation_flag as cf
import forecast_store as store


def test_decision_fires_only_at_trough_with_intact_growth():
    # trough multiple + growth at/above its own median -> flag
    assert cf.capitulation_decision(5.0, 13.3, 11.0) is True
    assert cf.capitulation_decision(10.0, 11.0, 11.0) is True   # boundary in
    # trough multiple but growth deteriorated -> priced down for a reason
    assert cf.capitulation_decision(5.0, 8.0, 11.0) is False
    # mid-range multiple -> not capitulation regardless of growth
    assert cf.capitulation_decision(50.0, 20.0, 11.0) is False
    assert cf.capitulation_decision(10.1, 13.3, 11.0) is False  # boundary out


def test_decision_is_not_the_expectations_flag():
    # The rule-14 flag fires at the TOP (pctile >= 90, growth below median);
    # this one must not fire there.
    assert cf.capitulation_decision(95.0, 8.0, 11.0) is False


_ROWS = [('CRM', '10'), ('PLTR', '10'), ('NOW', '10'), ('DDOG', '10'),
         ('SNOW', '10'), ('NVDA', '06')]


def test_log_forecast_appends_open_snapshot(tmp_path):
    path = tmp_path / 'forecasts.jsonl'
    snap = cf.log_capitulation_forecast(
        'CRM', rows=_ROWS, path=path, today=dt.date(2026, 8, 31))
    assert snap is not None
    assert snap['status'] == 'open'
    assert snap['dimension'] == cf.DIMENSION
    assert snap['template'] == 'REL_STRENGTH_1Q'
    assert snap['probability'] == cf.BASE_RATE_PROB
    assert snap['rating_value'] is None
    assert snap['created_date'] == '2026-08-31'
    rule = snap['resolution_rule']
    assert rule['benchmark'] == 'layer_cohort_ew'
    assert 'CRM' not in rule['constituents']          # peer basket excludes self
    assert store.materialize(path)[snap['id']] == snap


def test_log_forecast_dedups_open_same_ticker(tmp_path):
    path = tmp_path / 'forecasts.jsonl'
    first = cf.log_capitulation_forecast(
        'CRM', rows=_ROWS, path=path, today=dt.date(2026, 8, 31))
    dup = cf.log_capitulation_forecast(
        'CRM', rows=_ROWS, path=path, today=dt.date(2026, 9, 2))
    assert first is not None and dup is None          # second refused
    assert len(store.load_snapshots(path)) == 1


def test_log_forecast_allows_new_after_resolution(tmp_path):
    path = tmp_path / 'forecasts.jsonl'
    first = cf.log_capitulation_forecast(
        'CRM', rows=_ROWS, path=path, today=dt.date(2026, 8, 31))
    resolved = dict(first)
    resolved.update(status='resolved', outcome=1,
                    resolved_date='2026-12-01',
                    resolution_evidence='test', resolver_confidence='auto')
    store.append_resolution(resolved, path)
    again = cf.log_capitulation_forecast(
        'CRM', rows=_ROWS, path=path, today=dt.date(2026, 12, 2))
    assert again is not None and again['id'] != first['id']
