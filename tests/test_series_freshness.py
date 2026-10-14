"""series_freshness: a run that ends with yesterday's bar must be visible
(warning), and the night's last run must fail (2026-10-13: two post-close
runs re-published 2026-10-12 and both reported success)."""
import datetime as dt
import json

import series_freshness as sf

UTC = dt.timezone.utc


def at(s):
    return dt.datetime.fromisoformat(s).replace(tzinfo=UTC)


def test_before_close_expects_prior_session():
    # Tue 2026-10-13 15:00 ET = 19:00 UTC, before the close
    assert sf.last_closed_session(at('2026-10-13T19:00')) == dt.date(2026, 10, 12)


def test_after_close_expects_same_day():
    # Tue 2026-10-13 21:20 ET = 01:20 UTC Wed — the run that missed the bar
    assert sf.last_closed_session(at('2026-10-14T01:20')) == dt.date(2026, 10, 13)


def test_weekend_and_holiday_roll_back():
    assert sf.last_closed_session(at('2026-10-11T12:00')) == dt.date(2026, 10, 9)   # Sunday
    assert sf.last_closed_session(at('2026-09-07T23:00')) == dt.date(2026, 9, 4)    # Labor Day


def test_check_flags_the_observed_miss():
    fresh, msg = sf.check('2026-10-12', at('2026-10-14T01:20'))
    assert not fresh and '2026-10-13' in msg
    assert sf.check('2026-10-13', at('2026-10-14T01:20'))[0]


def _series(tmp_path, as_of):
    p = tmp_path / 's.json'
    p.write_text(json.dumps({'as_of': as_of}))
    return p


def test_main_warns_by_default_and_fails_when_strict(tmp_path, capsys):
    p = _series(tmp_path, '2000-01-03')
    assert sf.main(['--series', str(p)]) == 0
    assert '::warning::' in capsys.readouterr().out
    assert sf.main(['--series', str(p), '--strict']) == 1
    assert '::error::' in capsys.readouterr().out


def test_main_passes_when_current(tmp_path):
    p = _series(tmp_path, '2999-01-01')
    assert sf.main(['--series', str(p), '--strict']) == 0
