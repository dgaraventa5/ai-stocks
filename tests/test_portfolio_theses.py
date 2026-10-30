"""Rule 39 gate: a name cannot sit in the portfolio without a thesis."""
import portfolio_theses as pt


def test_every_portfolio_name_has_a_three_sentence_thesis():
    assert pt.problems() == {}


def test_sentence_count():
    assert pt.sentence_count('One. Two has 2.5 parts. Three!') == 3


def test_problems_flags_template_and_wrong_length(tmp_path, monkeypatch):
    for t, body in (('AAA', '> {Three sentences}'), ('BBB', '> Just one.')):
        d = tmp_path / 'per-stock' / t
        d.mkdir(parents=True)
        (d / 'thesis.md').write_text(f'## 1. One-line thesis\n\n{body}\n\n---\n')
    monkeypatch.setattr(pt, 'portfolio_tickers', lambda root: ['AAA', 'BBB', 'CCC'])
    assert pt.problems(tmp_path) == {'AAA': 'no thesis',
                                     'BBB': '1 sentences, needs 3',
                                     'CCC': 'no thesis'}
