"""Top-N selection with rank hysteresis (spec 2026-08-07 Part B)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from portfolio_sizing import rank_by_score, topn_membership


def _ranked(n):
    return [f'T{i:02d}' for i in range(1, n + 1)]   # T01 = rank 1 ...


def test_topn_entry_exit_hysteresis():
    ranked = _ranked(30)
    # outsiders at ranks 14-15 enter; incumbent at 17 stays; incumbent at 19
    # crosses the exit line; outsider at 16 does not enter (dead-band).
    prior = set(_ranked(13)) | {'T17', 'T19'}
    include, entered, exit_crossers = topn_membership(prior, ranked, n=15, m=18)
    assert entered == ['T14', 'T15']                  # outsiders in top-15 enter
    assert 'T16' not in include                       # dead-band outsider stays out
    assert 'T17' in include and 'T17' not in entered  # dead-band incumbent holds
    assert exit_crossers == ['T19']                   # below M -> exit crossing
    assert 'T19' not in include
    assert include == _ranked(15) + ['T17']           # rank order preserved


def test_tie_break():
    live = [{'ticker': 'AAA', 'TOTAL': 80.0}, {'ticker': 'BBB', 'TOTAL': 80.0},
            {'ticker': 'CCC', 'TOTAL': 90.0}]
    # incumbency breaks the AAA/BBB tie in BBB's favor
    assert rank_by_score(live, prior={'BBB'}) == ['CCC', 'BBB', 'AAA']
    # no incumbents: deterministic (ticker) order, higher score still first
    assert rank_by_score(live, prior=set()) == ['CCC', 'AAA', 'BBB']


def test_rank_stability():
    """A methodology reshuffle produces a membership DIFF through the normal
    event path (entered/exit_crossers), never a silent resort: unchanged
    incumbents inside M are still included, every change is enumerated."""
    ranked_before = _ranked(30)
    prior = set(ranked_before[:15])
    inc0, ent0, ex0 = topn_membership(prior, ranked_before, 15, 18)
    assert (ent0, ex0) == ([], [])                    # steady state: no diff
    reshuffled = list(reversed(ranked_before))        # en-masse rank flip
    inc1, ent1, ex1 = topn_membership(prior, reshuffled, 15, 18)
    assert set(ent1) == {f'T{i:02d}' for i in range(16, 31)}   # every entry enumerated
    assert set(ex1) == {f'T{i:02d}' for i in range(1, 13)}     # every exit enumerated
    assert set(inc1) == (prior - set(ex1)) | set(ent1)         # diff-complete
