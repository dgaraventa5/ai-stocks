"""tests/test_parse_form4.py — Form 4 parsing, offline, fictional filings."""
import pytest

pytest.importorskip("lxml")           # deploy CI runs without it

import parse_form4 as pf


def _filing(box="", footnote="", code="S"):
    plan = f"<aff10b5One>{box}</aff10b5One>" if box else ""
    notes = (f'<footnotes><footnote id="F1">{footnote}</footnote></footnotes>'
             if footnote else "")
    return f"""<?xml version="1.0"?>
<ownershipDocument>
  {plan}
  <reportingOwner>
    <reportingOwnerId><rptOwnerName>Example Person</rptOwnerName></reportingOwnerId>
    <reportingOwnerRelationship><isOfficer>1</isOfficer>
      <officerTitle>CFO</officerTitle></reportingOwnerRelationship>
  </reportingOwner>
  <nonDerivativeTable><nonDerivativeTransaction>
    <transactionDate><value>2026-06-01</value></transactionDate>
    <transactionCoding><transactionCode>{code}</transactionCode></transactionCoding>
    <transactionAmounts>
      <transactionShares><value>100</value></transactionShares>
      <transactionPricePerShare><value>10</value></transactionPricePerShare>
      <transactionAcquiredDisposedCode><value>D</value></transactionAcquiredDisposedCode>
    </transactionAmounts>
    <postTransactionAmounts>
      <sharesOwnedFollowingTransaction><value>900</value></sharesOwnedFollowingTransaction>
    </postTransactionAmounts>
  </nonDerivativeTransaction></nonDerivativeTable>
  {notes}
</ownershipDocument>"""


@pytest.mark.parametrize("box", ["1", "true", " 1 "])
def test_ticked_box_with_no_footnote_is_a_plan_sale(tmp_path, box):
    p = tmp_path / "4_2026-06-02_a.xml"
    p.write_text(_filing(box=box))
    assert pf.parse_file(p)[0]["is_10b5"] is True


@pytest.mark.parametrize("box", ["0", "false", ""])
def test_unticked_box_with_no_footnote_is_discretionary(tmp_path, box):
    p = tmp_path / "4_2026-06-02_a.xml"
    p.write_text(_filing(box=box))
    assert pf.parse_file(p)[0]["is_10b5"] is False


def test_footnote_still_marks_a_plan_sale(tmp_path):
    p = tmp_path / "4_2026-06-02_a.xml"
    p.write_text(_filing(footnote="Sold under a Rule 10b5-1 trading plan."))
    assert pf.parse_file(p)[0]["is_10b5"] is True


def _folder(tmp_path, monkeypatch, files):
    d = tmp_path / "filings"
    d.mkdir()
    for name, body in files.items():
        (d / name).write_text(body)
    monkeypatch.setattr(pf, "per_stock_dir", lambda t: tmp_path)


def test_corrupt_file_prints_unchecked_not_a_signal(tmp_path, monkeypatch, capsys):
    _folder(tmp_path, monkeypatch, {"4_2026-06-02_a.xml": "<ownershipDocument"})
    pf.summarize("AAA")
    out = capsys.readouterr().out
    assert "UNCHECKED" in out and "1 of 1" in out
    assert "absence of buying is itself the signal" not in out


def test_one_corrupt_file_among_good_ones_is_unchecked(tmp_path, monkeypatch, capsys):
    _folder(tmp_path, monkeypatch, {"4_2026-06-02_a.xml": _filing(box="1"),
                                    "4_2026-06-03_b.xml": "not xml"})
    pf.summarize("AAA")
    out = capsys.readouterr().out
    assert "UNCHECKED" in out and "1 of 2" in out
    assert "absence of buying is itself the signal" not in out


def test_clean_run_keeps_the_signal_line(tmp_path, monkeypatch, capsys):
    _folder(tmp_path, monkeypatch, {"4_2026-06-02_a.xml": _filing(box="1")})
    pf.summarize("AAA")
    out = capsys.readouterr().out
    assert "absence of buying is itself the signal" in out
    assert "UNCHECKED" not in out
    assert "Discretionary open-market SALES (S, not 10b5-1): 0" in out
