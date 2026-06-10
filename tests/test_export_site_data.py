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
