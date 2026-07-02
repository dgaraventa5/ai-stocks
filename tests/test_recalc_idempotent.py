"""Gate for review #8: percentile scoring depends on the whole sheet, so it's
more prone to hidden-state / iteration-order / self-inclusion bugs than absolute
bands. This asserts the full pipeline is deterministic — running it twice on
identical inputs yields identical scores — in both modes.
"""
import recalc_watchlist as rc


def _snapshot(mode):
    return [(x['ticker'], x['Value'], x['Quality'], x['Growth'], x['AI'],
             x['Momentum'], x['Risk'], x['TOTAL'], x['Tier'])
            for x in rc.recalc(mode=mode)]


def test_percentile_recalc_is_idempotent():
    assert _snapshot('percentile') == _snapshot('percentile')


def test_absolute_recalc_is_idempotent():
    assert _snapshot('absolute') == _snapshot('absolute')
