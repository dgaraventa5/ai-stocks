"""tests/test_thesis_watch.py — reading thesis-break triggers, offline."""
import thesis_watch as tw

TEMPLATE = "**Thesis-break trigger:** {what single development would force exit}\n"


def _thesis(tmp_path, ticker, body):
    d = tmp_path / "per-stock" / ticker
    d.mkdir(parents=True)
    (d / "thesis.md").write_text(f"# {ticker}\n\n{body}\n---\n")


def test_trigger_of_reads_the_line():
    text = "**Layer:** x\n**Thesis-break trigger:** Backlog falls two quarters.\n**Other:** y\n"
    assert tw.trigger_of(text) == "Backlog falls two quarters."


def test_template_blank_and_absent_lines_are_not_triggers():
    assert tw.trigger_of(TEMPLATE) is None
    assert tw.trigger_of("**Thesis-break trigger:**\n**Other:** y\n") is None
    assert tw.trigger_of("# no line here\n") is None


def test_load_triggers_handles_a_missing_file(tmp_path):
    _thesis(tmp_path, "AAA", "**Thesis-break trigger:** Loses its top customer.")
    assert tw.load_triggers(["AAA", "BBB"], tmp_path) == {
        "AAA": "Loses its top customer.", "BBB": None}


def test_report_marks_drafts_and_passes_them(capsys):
    code = tw.report({"AAA": "Real trigger.", "BBB": f"Draft one. {tw.DRAFT_MARK}"})
    out = capsys.readouterr().out
    assert code == 0
    assert "2 portfolio names: 0 missing, 1 draft" in out
    assert "AAA: Real trigger." in out and "BBB: DRAFT Draft one." in out
    assert tw.DRAFT_MARK not in out


def test_report_fails_on_a_missing_trigger(capsys):
    assert tw.report({"AAA": None, "BBB": "Real trigger."}) == 1
    assert "AAA: MISSING" in capsys.readouterr().out
