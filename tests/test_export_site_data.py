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
