"""Phase-3 scheduled executor wrapper (§C5 of the agentic-execution spec).

Safety posture under scheduling: auto-halt on ANY validation failure (the
kill switch + caps are the only human control left), notification on every
execution, full-turnover tickets NEVER auto-executed, expired/receipted
tickets skipped silently.
"""
import json

import pytest

import executor_cron as ec

NOW = '2026-08-13T14:00:00Z'


def write_ticket(tdir, ticket_id, expires, orders=1):
    p = tdir / f'ticket-{ticket_id}.json'
    p.write_text(json.dumps({
        'ticket_id': ticket_id, 'expires_at': expires,
        'orders': [{'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0,
                    'limit_price': 100.0, 'tif': 'day',
                    'notional_est': 100.0}] * orders}))
    return p


@pytest.fixture
def live_dir(tmp_path):
    d = tmp_path / 'live'
    (d / 'tickets').mkdir(parents=True)
    (d / 'receipts').mkdir()
    return d


# ---- ticket selection ----

def test_picks_newest_unexecuted_unexpired(live_dir):
    write_ticket(live_dir / 'tickets', '2026-08-11-tier', '2026-08-13T20:00:00Z')
    newest = write_ticket(live_dir / 'tickets', '2026-08-12-membership',
                          '2026-08-14T20:00:00Z')
    assert ec.pick_ticket(live_dir, now=NOW) == newest


def test_skips_expired_and_receipted(live_dir):
    write_ticket(live_dir / 'tickets', '2026-08-10-tier', '2026-08-12T20:00:00Z')
    done = write_ticket(live_dir / 'tickets', '2026-08-12-membership',
                        '2026-08-14T20:00:00Z')
    (live_dir / 'receipts' / 'receipt-2026-08-12-membership.json').write_text('{}')
    assert ec.pick_ticket(live_dir, now=NOW) is None
    assert done.exists()   # untouched, just skipped


def test_no_tickets_is_quiet_noop(live_dir):
    notes = []
    rc = ec.cron_run(live_dir, runner=None, notifier=notes.append, now=NOW)
    assert rc == 0 and notes == []


# ---- execution outcomes ----

def test_success_notifies(live_dir):
    write_ticket(live_dir / 'tickets', '2026-08-12-membership',
                 '2026-08-14T20:00:00Z')
    notes = []
    rc = ec.cron_run(live_dir,
                     runner=lambda p: {'failures': [], 'sent': True,
                                       'receipt': 'r'},
                     notifier=notes.append, now=NOW)
    assert rc == 0
    assert any('executed' in n for n in notes)
    assert not (live_dir / 'trading-halt.flag').exists()


def test_any_validation_failure_auto_halts_and_notifies(live_dir):
    write_ticket(live_dir / 'tickets', '2026-08-12-membership',
                 '2026-08-14T20:00:00Z')
    notes = []
    rc = ec.cron_run(live_dir,
                     runner=lambda p: {'failures': ['NVDA: not in roster'],
                                       'sent': False, 'receipt': None},
                     notifier=notes.append, now=NOW)
    assert rc == 1
    halt = (live_dir / 'trading-halt.flag').read_text()
    assert 'scheduled' in halt and 'not in roster' in halt
    assert any('HALT' in n for n in notes)


def test_transport_error_notifies_without_halt(live_dir):
    # Token expiry / network down: nothing was at risk, so no halt — but Dom
    # must hear about it (the pipeline is silently dead otherwise).
    write_ticket(live_dir / 'tickets', '2026-08-12-membership',
                 '2026-08-14T20:00:00Z')

    def boom(p):
        raise SystemExit('No Robinhood MCP token found')
    notes = []
    rc = ec.cron_run(live_dir, runner=boom, notifier=notes.append, now=NOW)
    assert rc == 1
    assert not (live_dir / 'trading-halt.flag').exists()
    assert any('token' in n.lower() for n in notes)


def test_full_turnover_ticket_never_auto_executed(live_dir):
    """The wrapper runs the executor WITHOUT --allow-full-turnover; a
    full-redeploy refusal therefore halts + notifies rather than sneaking a
    high-turnover trade through on a schedule."""
    write_ticket(live_dir / 'tickets', '2026-08-12-membership',
                 '2026-08-14T20:00:00Z')
    notes = []
    rc = ec.cron_run(live_dir,
                     runner=lambda p: {'failures': ['turnover 81% > cap 50%'],
                                       'sent': False, 'receipt': None},
                     notifier=notes.append, now=NOW)
    assert rc == 1
    assert 'turnover' in (live_dir / 'trading-halt.flag').read_text()
