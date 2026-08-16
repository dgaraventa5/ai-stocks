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


# ---- heartbeat (autonomy improvement #3) ----

def test_heartbeat_stamp_merges_jobs(live_dir):
    ec.heartbeat_stamp(live_dir, 'series', today='2026-08-13')
    ec.heartbeat_stamp(live_dir, 'recon', today='2026-08-14')
    hb = json.loads((live_dir / 'heartbeat.json').read_text())
    assert hb == {'series': '2026-08-13', 'recon': '2026-08-14'}


def test_stale_jobs_flags_old_and_missing(live_dir):
    ec.heartbeat_stamp(live_dir, 'series', today='2026-08-01')
    ec.heartbeat_stamp(live_dir, 'recon', today='2026-08-13')
    stale = ec.stale_jobs(live_dir, ['series', 'recon', 'execute'],
                          today='2026-08-14', max_age_days=3)
    assert 'series' in stale          # 13 days old
    assert 'execute' in stale         # never ran
    assert 'recon' not in stale


# ---- daily runner orchestration (autonomy improvement #1) ----

def test_daily_run_stamps_success_and_isolates_failure(live_dir):
    ran, notes = [], []

    def ok(name):
        return lambda: ran.append(name)

    def boom():
        raise RuntimeError('yahoo hiccup')
    rc = ec.daily_run(live_dir,
                      steps=[('series', boom), ('recon', ok('recon')),
                             ('execute', ok('execute'))],
                      notifier=notes.append, today='2026-08-13')
    assert rc == 1
    assert ran == ['recon', 'execute']            # failure didn't block later steps
    assert any('series' in n and 'yahoo' in n for n in notes)
    hb = json.loads((live_dir / 'heartbeat.json').read_text())
    assert set(hb) == {'recon', 'execute'}        # only successes stamped


def test_ticket_gen_when_model_event_newer_than_newest_ticket(live_dir):
    write_ticket(live_dir / 'tickets', '2026-08-10-tier', '2026-08-12T20:00:00Z')
    (live_dir / 'tickets' / 'ticket-2026-08-10-tier.json').write_text(json.dumps(
        {'ticket_id': '2026-08-10-tier', 'expires_at': '2026-08-12T20:00:00Z',
         'basis_event': {'date': '2026-08-10', 'kind': 'tier'}, 'orders': []}))
    gen_calls = []
    ec.ticket_gen_if_stale(
        live_dir,
        last_event={'date': '2026-08-12', 'kind': 'membership',
                    'reason': 'TSM enters'},
        gen=lambda ev: gen_calls.append(ev))
    assert gen_calls and gen_calls[0]['date'] == '2026-08-12'


def test_ticket_gen_skips_when_ticket_already_covers_event(live_dir):
    (live_dir / 'tickets' / 'ticket-2026-08-12-membership.json').write_text(
        json.dumps({'ticket_id': '2026-08-12-membership',
                    'expires_at': '2026-08-14T20:00:00Z',
                    'basis_event': {'date': '2026-08-12', 'kind': 'membership'},
                    'orders': []}))
    gen_calls = []
    ec.ticket_gen_if_stale(
        live_dir, last_event={'date': '2026-08-12', 'kind': 'membership'},
        gen=lambda ev: gen_calls.append(ev))
    assert gen_calls == []


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


# ---- DarkWake network race (2026-08-12..14: every scheduled recon failed) ----

def test_wait_for_network_true_without_sleeping_when_resolvable():
    slept = []
    ok = ec.wait_for_network(resolver=lambda h: '1.2.3.4',
                             sleeper=slept.append)
    assert ok is True
    assert slept == []


def test_wait_for_network_retries_then_succeeds():
    """launchd fires the job during DarkWake; Wi-Fi reassociates a beat later."""
    calls, slept = [], []
    def resolver(host):
        calls.append(host)
        if len(calls) < 3:
            raise OSError(8, 'nodename nor servname provided, or not known')
        return '1.2.3.4'
    assert ec.wait_for_network(resolver=resolver, sleeper=slept.append) is True
    assert len(calls) == 3
    assert len(slept) == 2          # slept only between attempts


def test_wait_for_network_gives_up_and_does_not_sleep_after_last_attempt():
    slept = []
    def resolver(host):
        raise OSError(8, 'nodename nor servname provided, or not known')
    ok = ec.wait_for_network(attempts=3, resolver=resolver,
                             sleeper=slept.append)
    assert ok is False
    assert len(slept) == 2          # n-1 sleeps for n attempts


def test_recon_skipped_with_clear_message_when_network_down(live_dir,
                                                            monkeypatch):
    """The old failure surfaced as a cryptic urlopen error. Name the cause."""
    monkeypatch.setattr(ec, 'wait_for_network', lambda **kw: False)
    notes = []
    class Boom:
        def positions(self): raise AssertionError('must not touch the network')
    ec._reconcile_via_transport(Boom(), notes.append)
    assert len(notes) == 1
    assert 'network unavailable' in notes[0].lower()
    assert 'darkwake' in notes[0].lower()
