"""XBRL period decomposition — the quarterly series behind rules 14 and 32-A.

Regression cover for the 2026-09-07 finding: `expectations_flag` filtered SEC
companyfacts to 70-100 day periods and called the result "quarter-by-quarter",
but **fiscal Q4 is never tagged as a standalone quarterly period** — a 10-K
reports the FY (365-day) frame and nothing else covering Oct-Dec. So every
name's series silently dropped one quarter per year, which made
`rev.shift(4)` compare against five quarters ago (DDOG printed +47.3% YoY
against a reported +36%) and made `rolling(4).sum()` sum four of the last
five quarters instead of a true TTM.

Everything here is stdlib-only so it stays safe for the deploy-site CI env
(which installs only openpyxl + pytest) — the decomposition is deliberately
pandas-free for exactly this reason.
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import xbrl_periods as xp


def _fact(start, end, val, filed='2026-08-06', form='10-Q'):
    return {'start': start, 'end': end, 'val': val, 'filed': filed,
            'form': form}


def _ddog_fy(year, q1, q2, q3, q4, filed_year=None):
    """DDOG-shaped facts for one calendar fiscal year.

    Mirrors the real companyfacts shape: Q1 as a standalone quarter, then
    cumulative H1 / 9M frames, then the FY frame from the 10-K. Q4 exists
    ONLY inside the FY frame — that is the whole bug.
    """
    fy = filed_year or year + 1
    return [
        _fact(f'{year}-01-01', f'{year}-03-31', q1),
        _fact(f'{year}-01-01', f'{year}-06-30', q1 + q2),
        _fact(f'{year}-04-01', f'{year}-06-30', q2),
        _fact(f'{year}-01-01', f'{year}-09-30', q1 + q2 + q3),
        _fact(f'{year}-07-01', f'{year}-09-30', q3),
        _fact(f'{year}-01-01', f'{year}-12-31', q1 + q2 + q3 + q4,
              filed=f'{fy}-02-15', form='10-K'),
    ]


# Real DDOG revenue ($M), FY2025 + Q1/Q2 2026 (8-K Ex-99.1 2026-08-06 and
# prior filings): the exact case that produced the bad +47.3% print.
DDOG_2025 = _ddog_fy(2025, 761.6, 826.8, 885.7, 953.1)
DDOG_2026 = [
    _fact('2026-01-01', '2026-03-31', 1006.4),
    _fact('2026-01-01', '2026-06-30', 1006.4 + 1121.5),
    _fact('2026-04-01', '2026-06-30', 1121.5),
]


def test_q4_is_recovered_from_the_fy_frame():
    """The core bug: Q4 exists only inside the FY frame and must be derived."""
    q = xp.quarterly_from_facts(DDOG_2025)
    assert '2025-12-31' in q, (
        'fiscal Q4 dropped — this is the 2026-09-07 bug: a 10-K tags the '
        'annual period, never a standalone Oct-Dec quarter')
    assert round(q['2025-12-31'], 1) == 953.1   # 3427.2 FY - 2474.1 nine-month


def test_full_year_has_four_consecutive_quarters():
    q = xp.quarterly_from_facts(DDOG_2025)
    ends = sorted(e for e in q if e.startswith('2025'))
    assert ends == ['2025-03-31', '2025-06-30', '2025-09-30', '2025-12-31']


def test_yoy_reconciles_to_the_reported_number():
    """DDOG Q2 2026 was reported +36% YoY; the buggy series printed +47.3%."""
    q = xp.quarterly_from_facts(DDOG_2025 + DDOG_2026)
    ends = sorted(q)
    latest = ends[-1]
    assert latest == '2026-06-30'
    prior = ends[-5]                      # four quarters back, not five
    assert prior == '2025-06-30'
    yoy = (q[latest] / q[prior] - 1) * 100
    assert 35.0 <= yoy <= 36.5, f'expected ~+35.6% (reported +36%), got {yoy:.1f}%'


def test_trailing_four_quarters_is_a_true_ttm():
    """rolling(4) over the fixed series must span exactly 12 months."""
    q = xp.quarterly_from_facts(DDOG_2025 + DDOG_2026)
    ends = sorted(q)[-4:]
    assert ends == ['2025-09-30', '2025-12-31', '2026-03-31', '2026-06-30']
    ttm = sum(q[e] for e in ends)
    assert round(ttm, 1) == round(885.7 + 953.1 + 1006.4 + 1121.5, 1)


def test_directly_tagged_quarter_wins_over_derivation():
    """A reported quarter is evidence; a derived one is arithmetic.

    Here the cumulative ladder implies Q2 = 900.0 while the company tags the
    quarter directly as 826.8. The direct fact must win.
    """
    facts = [
        _fact('2025-01-01', '2025-03-31', 761.6),
        _fact('2025-01-01', '2025-06-30', 761.6 + 900.0),   # implies 900.0
        _fact('2025-04-01', '2025-06-30', 826.8),           # reported
    ]
    q = xp.quarterly_from_facts(facts)
    assert q['2025-06-30'] == 826.8


def test_restatement_prefers_the_later_filing():
    facts = [_fact('2025-01-01', '2025-03-31', 700.0, filed='2025-05-01'),
             _fact('2025-01-01', '2025-03-31', 761.6, filed='2025-11-01')]
    assert xp.quarterly_from_facts(facts)['2025-03-31'] == 761.6


def test_fiscal_year_not_on_calendar_boundary():
    """MDB/PATH-shaped: FY ends 01-31, so quarters end Apr/Jul/Oct/Jan."""
    facts = [
        _fact('2025-02-01', '2025-04-30', 549.0),
        _fact('2025-02-01', '2025-07-31', 549.0 + 591.4),
        _fact('2025-02-01', '2025-10-31', 549.0 + 591.4 + 628.3),
        _fact('2025-02-01', '2026-01-31', 549.0 + 591.4 + 628.3 + 683.0,
              form='10-K', filed='2026-03-01'),
    ]
    q = xp.quarterly_from_facts(facts)
    assert sorted(q) == ['2025-04-30', '2025-07-31', '2025-10-31', '2026-01-31']
    assert round(q['2026-01-31'], 1) == 683.0


def test_53_week_fiscal_year_quarters_still_decompose():
    """A 14-week quarter is 98 days; it must not be discarded as non-quarterly."""
    facts = [
        _fact('2025-01-01', '2025-04-04', 100.0),            # 93d
        _fact('2025-01-01', '2025-07-04', 210.0),            # 184d -> Q2 110
        _fact('2025-01-01', '2025-10-03', 330.0),            # 275d -> Q3 120
        _fact('2025-01-01', '2026-01-09', 470.0,             # 373d -> Q4 140
              form='10-K', filed='2026-02-20'),
    ]
    q = xp.quarterly_from_facts(facts)
    assert round(q['2026-01-09'], 1) == 140.0
    assert round(q['2025-10-03'], 1) == 120.0


def test_ignores_gaps_that_are_not_one_quarter_wide():
    """Differencing must not invent a 'quarter' from a half-year gap."""
    facts = [
        _fact('2025-01-01', '2025-03-31', 100.0),
        _fact('2025-01-01', '2025-12-31', 500.0, form='10-K',
              filed='2026-02-15'),      # 9-month gap: not a quarter
    ]
    q = xp.quarterly_from_facts(facts)
    assert '2025-12-31' not in q
    assert q['2025-03-31'] == 100.0


def test_empty_and_malformed_facts_are_survivable():
    assert xp.quarterly_from_facts([]) == {}
    assert xp.quarterly_from_facts([{'val': 1.0}]) == {}
    assert xp.quarterly_from_facts([{'start': 'x', 'end': 'y', 'val': 1.0}]) == {}


def test_gap_guard_accepts_a_clean_run_of_quarters():
    q = xp.quarterly_from_facts(DDOG_2025 + DDOG_2026)
    ends = [dt.date.fromisoformat(e) for e in sorted(q)]
    assert xp.quarters_are_consecutive(ends)


def test_gap_guard_rejects_a_missing_quarter():
    """The exact shape of the 2026-09-07 bug: Q4 dropped from the series."""
    q = xp.quarterly_from_facts(DDOG_2025 + DDOG_2026)
    ends = [dt.date.fromisoformat(e) for e in sorted(q)
            if e != '2025-12-31']          # drop Q4, as the old code did
    assert not xp.quarters_are_consecutive(ends)


def test_gap_guard_is_trivially_true_for_short_input():
    assert xp.quarters_are_consecutive([])
    assert xp.quarters_are_consecutive([dt.date(2025, 3, 31)])
