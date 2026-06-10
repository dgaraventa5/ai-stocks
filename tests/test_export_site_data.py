import json

import pytest

import export_site_data as ex


def test_positions_only_included_rows(repo):
    pos = ex.export_positions(repo)
    assert [p['ticker'] for p in pos] == ['NVDA', 'TSM']   # ARM excluded


def test_positions_fields_and_scaling(repo):
    pos = ex.export_positions(repo)
    nvda = pos[0]
    assert nvda == {
        'ticker': 'NVDA', 'company': 'NVIDIA Corp',
        'layer_num': '06', 'layer': 'Silicon',
        'weight': 60.0, 'notional': 6000,
        'score': 83.3, 'tier': '✓✓',
    }
    assert sum(p['notional'] for p in pos) == 10000


def test_positions_schema_surprise_fails_loudly(repo):
    import openpyxl
    wb = openpyxl.load_workbook(repo / '00-master' / 'portfolio.xlsx')
    wb['Targets'].cell(row=2, column=9).value = 'Tgt %'   # renamed column
    wb.save(repo / '00-master' / 'portfolio.xlsx')
    with pytest.raises(SystemExit):
        ex.export_positions(repo)


def test_performance_scaled_to_notional(repo):
    perf = ex.export_performance(repo)
    assert perf['dates'][0] == '2026-05-26'
    assert perf['model'][0] == 10000.0
    # 13386.55 / 13800 * 10000
    assert abs(perf['model'][-1] - 9700.4) < 0.1
    assert perf['bench']['SMH'][0] == 10000.0
    assert abs(perf['bench']['SMH'][-1] - 9800.0) < 0.1


def test_performance_summary_and_monthly(repo):
    perf = ex.export_performance(repo)
    s = perf['summary']
    assert abs(s['total_return'] - (13386.55 / 13800 - 1)) < 1e-6
    assert abs(s['vs_smh'] - (s['total_return'] - (-0.02))) < 1e-6
    assert perf['monthly'][0]['month'] == '2026-05'
    assert perf['as_of'] == '2026-05-28'


def test_performance_missing_series_fails_loudly(repo):
    (repo / 'tracking' / 'performance-series.json').unlink()
    with pytest.raises(SystemExit):
        ex.export_performance(repo)


def test_performance_missing_bench_key_fails_loudly(repo):
    sp = repo / 'tracking' / 'performance-series.json'
    raw = json.loads(sp.read_text())
    del raw['bench']['EW']
    sp.write_text(json.dumps(raw))
    with pytest.raises(SystemExit):
        ex.export_performance(repo)


def test_performance_monthly_chaining_across_months(repo):
    sp = repo / 'tracking' / 'performance-series.json'
    series = {
        'start': '2026-05-26', 'as_of': '2026-06-02',
        'dates': ['2026-05-26', '2026-05-29', '2026-06-01', '2026-06-02'],
        'model': [13800.0, 14076.0, 13938.0, 14214.0],
        'bench': {'SMH': [1.0, 1.02, 1.01, 1.03],
                  'QQQ': [1.0, 1.01, 1.0, 1.02],
                  'EW': [1.0, 1.0, 1.0, 1.0]},
    }
    sp.write_text(json.dumps(series))
    perf = ex.export_performance(repo)
    assert [m['month'] for m in perf['monthly']] == ['2026-05', '2026-06']
    # June chains off May's close, not off inception
    assert perf['monthly'][1]['model'] == round(14214.0 / 14076.0 - 1, 6)
    assert perf['monthly'][1]['SMH'] == round(1.03 / 1.02 - 1, 6)


def test_changes_from_events_and_audit(repo):
    ch = ex.export_changes(repo)
    kinds = {(c['date'], c['type'], c.get('ticker')) for c in ch}
    assert ('2026-05-26', 'inception', None) in kinds
    assert ('2026-06-10', 'add', 'TSM') in kinds
    assert ('2026-06-10', 'drop', 'ARM') in kinds
    rerates = [c for c in ch if c['type'] == 'rerate']
    assert len(rerates) == 1                       # grouped by (date, ticker)
    assert rerates[0]['ticker'] == 'NVDA'
    assert rerates[0]['detail'] == 'D2, D3'
    assert 'Initial baseline' not in json.dumps(ch)   # Type==Initial excluded


def test_changes_no_dollar_amounts(repo):
    text = json.dumps(ex.export_changes(repo))
    for planted in ('824.7', '13800', '900.0', '700.0'):
        assert planted not in text


def test_changes_sorted_newest_first(repo):
    ch = ex.export_changes(repo)
    assert [c['date'] for c in ch] == sorted(
        (c['date'] for c in ch), reverse=True)


def test_theses_extracts_populated_and_nulls_template(repo, capsys):
    th = ex.export_theses(repo, ['NVDA', 'TSM'])
    assert th['NVDA'] == ('The compute layer toll booth: every training run '
                          'pays NVDA.')
    assert th['TSM'] is None
    assert 'TSM' in capsys.readouterr().err     # warned


def test_theses_missing_file_is_null(repo, capsys):
    th = ex.export_theses(repo, ['NVDA', 'XYZ'])
    assert th['XYZ'] is None
    assert 'XYZ' in capsys.readouterr().err


def test_scans_passthrough_and_orphan_warning(repo, capsys):
    scans = ex.export_scans(repo)
    assert scans == [{'date': '2026-06-05',
                      'title': 'Weekly News Scan — 2026-06-05',
                      'url': 'https://www.notion.so/abc123'}]
    assert '2026-05-29' in capsys.readouterr().err   # scan md with no link


def test_main_writes_all_files(repo):
    ex.main(repo)
    names = {p.name for p in (repo / 'site' / 'data').glob('*.json')}
    assert names == {'positions.json', 'performance.json', 'changes.json',
                     'theses.json', 'scans.json', 'meta.json'}
    meta = json.loads((repo / 'site' / 'data' / 'meta.json').read_text())
    assert meta['as_of'] == '2026-05-28'
    assert meta['last_rebalance'] == '2026-06-10'
    assert meta['holdings'] == 2


def test_privacy_no_real_dollars_anywhere(repo):
    """THE regression test: planted real-dollar values must never leak."""
    import re as _re
    from conftest import REAL_DOLLARS
    ex.main(repo)
    for p in (repo / 'site' / 'data').glob('*.json'):
        text = p.read_text()
        for planted in REAL_DOLLARS:
            pattern = r'(?<![\d.])' + _re.escape(planted)
            assert not _re.search(pattern, text), \
                f'{planted} leaked into {p.name}'
