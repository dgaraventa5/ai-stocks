"""Tests for scripts/dom_inbox.py — the single list of what needs Dom.

Offline and fixture-only: openpyxl is never loaded, and portfolio context is
injected rather than read from the workbook.
"""
import datetime as dt
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import dom_inbox as d  # noqa: E402

TODAY = dt.date(2026, 11, 17)

PROPOSALS = """# Rating proposals

Intro text.

## 2026-10-18 — AAA — D2 Supply Chain Position 5 → 4  (confidence Med)
Event: something.
Why: band 4 fits.
Effect if approved: Total 79.40 → 78.40, rank 8 → 9; membership change: no.
Status: PROPOSED

## 2026-11-10 — BBB — M2 Relative Strength 3 → 2  (confidence High)
Why: lagging.
Effect if approved: Total 70.00 → 69.50, tradable rank 17 → 19; membership change: YES — held, exit clock.
Status: PROPOSED

## 2026-10-20 — CCC — M2 Relative Strength 4 → 2  (confidence High)
Why: old momentum.
Effect if approved: Total 60.00 → 59.00, rank 50 → 52; membership change: no.
Status: PROPOSED

## 2026-11-01 — DDD — R4 Regulatory Risk 3 → 2  (confidence Med)
Why: first.
Status: PROPOSED

## 2026-11-16 — DDD — R4 Regulatory Risk 3 → 2  (confidence Med; update)
Why: second.
Status: PROPOSED — held for the post-print review

## 2026-11-12 — EEE — M1 EPS Revisions 4 → 5  (confidence Low)
Status: APPROVED by Dom 2026-11-12, applied

## 2026-11-15 — FFF — no change
All ratings hold.

_A summary paragraph mentioning 3 → 2 that is not a proposal._
"""


def _props():
    return d.parse_proposals(PROPOSALS)


def test_parse_finds_rating_proposals_only():
    ps = _props()
    assert [(p['ticker'], p['dim']) for p in ps] == [
        ('AAA', 'D2'), ('BBB', 'M2'), ('CCC', 'M2'), ('DDD', 'R4'),
        ('DDD', 'R4'), ('EEE', 'M1')]
    assert ps[0]['old'] == 5 and ps[0]['new'] == 4
    assert ps[0]['confidence'] == 'Med'
    assert ps[0]['status_line'] == 9
    assert [d.is_open(p) for p in ps] == [True, True, True, True, True, False]


def test_effect_bits_reads_score_rank_and_membership():
    ps = _props()
    assert d._effect_bits(ps[0]['effect']) == ('79.40→78.40, rank 8→9', False)
    assert d._effect_bits(ps[1]['effect']) == ('70.00→69.50, rank 17→19', True)


def test_expiry_supersedes_older_duplicate_and_ages_out_momentum():
    plan = {(p['ticker'], p['date']): s for p, s in d.expiry_plan(_props(), TODAY)}
    # older DDD R4 superseded by the newer one; the newer one stays open
    assert plan[('DDD', '2026-11-01')].startswith('SUPERSEDED 2026-11-17 by the 2026-11-16')
    assert ('DDD', '2026-11-16') not in plan
    # CCC M2 is 28 days old: past the 14-day momentum limit
    assert plan[('CCC', '2026-10-20')].startswith('EXPIRED 2026-11-17')
    # AAA D2 is 30 days old: inside the 45-day limit for filing-based ratings
    assert ('AAA', '2026-10-18') not in plan
    # BBB M2 is 7 days old
    assert ('BBB', '2026-11-10') not in plan
    # closed proposals are never touched
    assert ('EEE', '2026-11-12') not in plan


def test_apply_expiry_rewrites_only_status_lines():
    plan = d.expiry_plan(_props(), TODAY)
    out = d.apply_expiry(PROPOSALS, plan)
    before, after = PROPOSALS.split('\n'), out.split('\n')
    assert len(before) == len(after)
    changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    assert len(changed) == len(plan) == 2
    assert all(after[i].startswith('Status: ') for i in changed)
    # a second pass finds nothing more to retire
    assert d.expiry_plan(d.parse_proposals(out), TODAY) == []


def test_hold_items_window_and_urgency():
    holds = {'_meta': {'x': 1},
             'SOON': {'expires': '2026-11-19', 'reason': 'r'},
             'LATER': {'expires': '2026-11-25', 'reason': 'r'},
             'FAR': {'expires': '2027-02-26', 'reason': 'r'},
             'JUSTLAPSED': {'expires': '2026-11-15', 'reason': 'r'},
             'OLDLAPSE': {'expires': '2026-10-01', 'reason': 'r'},
             'BROKEN': {'expires': 'soon', 'reason': 'r'}}
    items = {i['ticker']: i for i in d.hold_items(holds, TODAY)}
    assert set(items) == {'SOON', 'LATER', 'JUSTLAPSED', 'BROKEN'}
    assert items['SOON']['urgent'] and items['JUSTLAPSED']['urgent']
    assert not items['LATER']['urgent']
    assert 'lapsed' in items['JUSTLAPSED']['title']
    assert items['BROKEN']['urgent']          # unreadable expiry fails closed


def test_eps_ask_closes_itself_once_dom_rules():
    asks = {}
    aid = d.add_ask(asks, 'eps_ruling', 'NRG', '+269% written with no ruling',
                    'weekly scan 2026-11-14', None, dt.date(2026, 11, 14))
    assert aid == 'eps_ruling:NRG'
    assert len(d.ask_items(asks, {})) == 1
    # a ruling dated before the ask does not answer it
    assert len(d.ask_items(asks, {'NRG': {'ruled': '2026-09-01'}})) == 1
    assert d.ask_items(asks, {'NRG': {'ruled': '2026-11-18'}}) == []


def test_add_ask_is_idempotent_and_reopens_after_close():
    asks = {}
    a1 = d.add_ask(asks, 'data_fix', 'CRWV', 'MW stale', None, None, TODAY)
    a2 = d.add_ask(asks, 'data_fix', 'CRWV', 'MW stale (again)', None, None, TODAY)
    assert a1 == a2 and len(asks) == 1
    assert asks[a1]['text'] == 'MW stale (again)'
    d.close_ask(asks, 'ask:' + a1, 'fixed', TODAY)
    assert d.ask_items(asks, {}) == []
    a3 = d.add_ask(asks, 'data_fix', 'CRWV', 'MW stale once more', None, None,
                   TODAY + dt.timedelta(days=30))
    assert a3 != a1 and len(asks) == 2 and asks[a1]['closed']


def test_add_ask_rejects_unknown_kind():
    with pytest.raises(ValueError):
        d.add_ask({}, 'rating', 'X', 't', None, None, TODAY)


def test_priority_order():
    held, ranks = {'HELD'}, {'TOP': 12, 'LOW': 80, 'HELD': 5}
    assert d.priority({'kind': 'rating', 'ticker': 'LOW', 'moves_membership': True}, held, ranks) == 1
    assert d.priority({'kind': 'hold', 'ticker': 'LOW', 'urgent': True}, held, ranks) == 1
    assert d.priority({'kind': 'eps_ruling', 'ticker': 'HELD'}, held, ranks) == 1
    assert d.priority({'kind': 'rating', 'ticker': 'HELD'}, held, ranks) == 2
    assert d.priority({'kind': 'rating', 'ticker': 'TOP'}, held, ranks) == 2
    assert d.priority({'kind': 'rating', 'ticker': 'LOW'}, held, ranks) == 3
    assert d.priority({'kind': 'rating', 'ticker': 'UNRANKED'}, held, ranks) == 3


def _repo(tmp_path, asks=None):
    (tmp_path / 'tracking').mkdir()
    (tmp_path / '00-master').mkdir()
    (tmp_path / 'tracking/rating-proposals.md').write_text(PROPOSALS)
    (tmp_path / '00-master/entry-holds.json').write_text(json.dumps(
        {'SOON': {'expires': '2026-11-19', 'reason': 'guidance cut'}}))
    (tmp_path / '00-master/eps-yoy-overrides.json').write_text('{}')
    (tmp_path / 'tracking/dom-asks.json').write_text(json.dumps(asks or {}))
    return tmp_path


def test_collect_reports_unreadable_portfolio_instead_of_hiding_it(tmp_path, monkeypatch):
    root = _repo(tmp_path)
    c = d.collect(root, TODAY)
    # no portfolio.xlsx / score-history in the fixture: both reads fail loudly
    assert any('held names' in p for p in c['problems'])
    assert any('ranks' in p for p in c['problems'])
    ids = [i['id'] for i in c['items']]
    assert 'rating:2026-11-10:BBB:M2' in ids and 'hold:SOON:2026-11-19' in ids
    assert 'rating:2026-11-12:EEE:M1' not in ids
    # priority 1 first: BBB moves membership, SOON's hold is urgent
    assert {i['id'] for i in c['items'] if i['priority'] == 1} == {
        'rating:2026-11-10:BBB:M2', 'hold:SOON:2026-11-19'}
    assert c['items'][0]['priority'] == 1
    assert c['expirable'] == 2
    md = d.render(c)
    assert '## Decide first (2)' in md and 'Could not check' in md
    assert '**changes the portfolio**' in md


def test_collect_uses_injected_portfolio_context(tmp_path, monkeypatch):
    root = _repo(tmp_path)
    monkeypatch.setattr(d, 'portfolio_context', lambda root: ({'AAA'}, {'CCC': 10}, []))
    c = d.collect(root, TODAY)
    pri = {i['ticker']: i['priority'] for i in c['items']}
    assert pri['AAA'] == 2 and pri['CCC'] == 2 and pri['DDD'] == 3
    assert c['problems'] == []


def test_summary_line():
    assert d.summary_line({'items': [], 'expirable': 0}) == 'Inbox: nothing waiting for you.'
    c = {'items': [{'priority': 1, 'ticker': 'META'}, {'priority': 3, 'ticker': 'X'}],
         'expirable': 4}
    assert d.summary_line(c) == 'Inbox: 2 open, 1 to decide first (META), 4 stale (run expire).'


def _item(iid, **kw):
    base = {'id': iid, 'kind': 'rating', 'title': f'T {iid}', 'priority': 2,
            'ticker': 'T', 'raised': '2026-11-01', 'expires': '2026-12-16',
            'detail': 'why', 'source': 'tracking/rating-proposals.md:8'}
    base.update(kw)
    return base


def test_notion_plan_creates_new_and_closes_resolved():
    c = {'items': [_item('a'), _item('b'), _item('c', priority=1)]}
    plan = d.notion_plan(c, {'_meta': {}, 'a': {'page': 'page-a', 'priority': 2},
                             'c': {'page': 'page-c', 'priority': 3},
                             'gone': {'page': 'page-g', 'priority': 2}})
    assert [r['Inbox ID'] for r in plan['create']] == ['b']
    assert plan['close'] == [{'id': 'gone', 'page': 'page-g'}]
    assert plan['update'] == [{'id': 'c', 'page': 'page-c', 'Priority': '1 Decide first'}]
    assert plan['data_source'] == d.NOTION_DATA_SOURCE


def test_notion_properties_shape_and_text_cap():
    p = d.notion_properties(_item('x', detail='w' * 5000, priority=1))
    assert p['Priority'] == '1 Decide first' and p['State'] == 'Open'
    assert p['date:Raised:start'] == '2026-11-01'
    assert p['date:Stale after:start'] == '2026-12-16'
    assert len(p['Why']) == d.NOTION_TEXT_MAX
    hold = d.notion_properties(_item('h', kind='hold', expires='2026-11-21'))
    assert 'date:Stale after:start' not in hold



def test_links_resolve_from_the_tracking_folder():
    assert d._link('tracking/rating-proposals.md:88') == 'rating-proposals.md#L88'
    assert d._link('tracking/scheduled-run-log.md (2026-11-02)') == 'scheduled-run-log.md'
    assert d._link('00-master/entry-holds.json') == '../00-master/entry-holds.json'
