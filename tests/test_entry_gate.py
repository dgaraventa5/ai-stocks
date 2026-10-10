"""Rule 35 entry gate: research-before-entry."""
import json

import entry_gate as eg


def _brief(root, ticker, date):
    d = root / 'per-stock' / ticker
    d.mkdir(parents=True, exist_ok=True)
    (d / f'context-{date}.md').write_text('x')


def _holds(root, holds):
    (root / '00-master').mkdir(exist_ok=True)
    (root / '00-master' / 'entry-holds.json').write_text(json.dumps(holds))


def test_no_briefing_blocks(tmp_path):
    assert 'no context briefing' in eg.entry_block('AAA', '2026-10-06', tmp_path)


def test_fresh_briefing_allows(tmp_path):
    _brief(tmp_path, 'AAA', '2026-09-10')
    assert eg.entry_block('AAA', '2026-10-06', tmp_path) is None


def test_stale_briefing_blocks_and_newest_file_wins(tmp_path):
    _brief(tmp_path, 'AAA', '2026-08-01')
    assert '> 30d' in eg.entry_block('AAA', '2026-10-06', tmp_path)
    _brief(tmp_path, 'AAA', '2026-10-01')
    assert eg.entry_block('AAA', '2026-10-06', tmp_path) is None


def test_live_hold_blocks_even_with_fresh_briefing(tmp_path):
    _brief(tmp_path, 'AAA', '2026-10-06')
    _holds(tmp_path, {'_meta': {'x': 1},
                      'AAA': {'reason': 'county action', 'expires': '2026-11-15'}})
    why = eg.entry_block('AAA', '2026-10-06', tmp_path)
    assert 'entry hold until 2026-11-15' in why and 'county action' in why
    assert eg.entry_block('AAA', '2026-11-15', tmp_path) is not None  # inclusive


def test_expired_hold_allows(tmp_path):
    _brief(tmp_path, 'AAA', '2026-11-10')
    _holds(tmp_path, {'AAA': {'reason': 'r', 'expires': '2026-11-15'}})
    assert eg.entry_block('AAA', '2026-11-16', tmp_path) is None


def test_hold_without_expiry_or_with_bad_expiry_fails_closed(tmp_path):
    _brief(tmp_path, 'AAA', '2026-10-06')
    _holds(tmp_path, {'AAA': {'reason': 'r'}})
    assert eg.entry_block('AAA', '2026-10-06', tmp_path) is not None
    _holds(tmp_path, {'AAA': {'reason': 'r', 'expires': 'soon'}})
    assert eg.entry_block('AAA', '2026-10-06', tmp_path) is not None


def test_missing_or_corrupt_holds_file_means_no_holds(tmp_path):
    assert eg.load_holds(tmp_path) == {}
    (tmp_path / '00-master').mkdir()
    (tmp_path / '00-master' / 'entry-holds.json').write_text('{not json')
    assert eg.load_holds(tmp_path) == {}
