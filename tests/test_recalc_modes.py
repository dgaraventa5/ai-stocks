"""Regression guard for the P1 go-live: recalc_watchlist now has two modes.

These are structural invariants (not value snapshots, so they survive data
refreshes): the live default is percentile; P1 changes ONLY Value and Quality
(the six style-biased metrics live there), leaving Growth/AI/Momentum/Risk
byte-identical; and the two modes genuinely differ for many names.
"""
import recalc_watchlist as rc


def test_default_mode_is_percentile():
    default = {x['row']: x['TOTAL'] for x in rc.recalc()}
    pct = {x['row']: x['TOTAL'] for x in rc.recalc(mode='percentile')}
    assert default == pct


def test_p1_touches_only_value_and_quality():
    ab = {x['row']: x for x in rc.recalc(mode='absolute')}
    pc = {x['row']: x for x in rc.recalc(mode='percentile')}
    assert set(ab) == set(pc)
    for row in ab:
        for cat in ('Growth', 'AI', 'Momentum', 'Risk'):
            assert ab[row][cat] == pc[row][cat], f'{cat} must be untouched (row {row})'


def test_modes_differ_for_many_names():
    ab = {x['row']: x for x in rc.recalc(mode='absolute')}
    pc = {x['row']: x for x in rc.recalc(mode='percentile')}
    changed = sum(1 for row in ab
                  if ab[row]['Quality'] != pc[row]['Quality']
                  or ab[row]['Value'] != pc[row]['Value'])
    assert changed > 10, f'expected the de-biasing to move many names, got {changed}'


def test_absolute_mode_is_deterministic():
    a = {x['row']: (x['Value'], x['Quality'], x['TOTAL']) for x in rc.recalc(mode='absolute')}
    b = {x['row']: (x['Value'], x['Quality'], x['TOTAL']) for x in rc.recalc(mode='absolute')}
    assert a == b
