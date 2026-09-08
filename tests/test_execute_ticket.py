"""Executor validation gates (§C of the 2026-08-09 agentic-execution spec).

Every C2 gate has a red test: checksum tamper, expiry, double-execution,
roster allowlist, notional/cash/turnover caps, ACCOUNT_CAP, kill switch,
live-price sanity. Offline: fixture transport, tmp dirs, frozen `now`.
"""
import json

import pytest

import execute_ticket as ex
import trade_ticket as tt

NOW = '2026-08-13T14:00:00Z'
CFG = {'ACCOUNT_CAP': 500.0, 'MAX_ORDER_NOTIONAL': 200.0,
       'MAX_TURNOVER_PCT': 0.5, 'LIMIT_TOL': 0.0075}


class FakeTransport:
    """Records order placements; serves canned portfolio/quotes reads."""

    def __init__(self, cash=500.0, equity=500.0, quotes=None, fail_on=()):
        self._cash, self._equity = cash, equity
        self._quotes = quotes or {}
        self._fail_on = set(fail_on)
        self.placed = []

    def portfolio(self):
        return {'cash': self._cash, 'equity': self._equity}

    def quotes(self, tickers):
        return {t: self._quotes[t] for t in tickers if t in self._quotes}

    def place_equity_order(self, order):
        if order['ticker'] in self._fail_on:
            raise RuntimeError('simulated rejection')
        self.placed.append(order)
        return {'order_id': f"rh-{order['ticker']}-{len(self.placed)}",
                'state': 'queued'}


def make_ticket(tmp_path, orders=None, expires='2026-08-14T20:00:00Z',
                checksum=None, ticket_id='2026-08-12-membership'):
    orders = orders if orders is not None else [
        {'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0,
         'limit_price': 100.75, 'tif': 'day', 'notional_est': 100.0}]
    tk = {'ticket_id': ticket_id, 'created_at': '2026-08-12T21:30:00Z',
          'expires_at': expires,
          'basis_event': {'date': '2026-08-12', 'kind': 'membership',
                          'reason': 'test'},
          'account_equity_at_gen': 500.0, 'account_state_as_of': '2026-08-12',
          'orders': orders, 'untradeable': [], 'suppressed': [], 'skipped': [],
          'checksum': checksum or tt.ticket_checksum(orders)}
    p = tmp_path / 'ticket.json'
    p.write_text(json.dumps(tk))
    return p


@pytest.fixture
def live_dir(tmp_path):
    d = tmp_path / 'live'
    (d / 'receipts').mkdir(parents=True)
    (d / 'executor-config.json').write_text(json.dumps(CFG))
    return d


def run(ticket_path, live_dir, transport=None, roster=('NVDA', 'TSM'),
        **kw):
    transport = transport or FakeTransport(quotes={'NVDA': 100.0, 'TSM': 250.0})
    return ex.run(ticket_path, live_dir=live_dir, roster=set(roster),
                  transport=transport, now=NOW, **kw)


def assert_refused(result, needle):
    assert result['sent'] is False
    assert any(needle in f for f in result['failures']), result['failures']


# ---- C2.1: checksum, expiry, double-execution ----

def test_checksum_tamper_refused(tmp_path, live_dir):
    p = make_ticket(tmp_path, checksum='0' * 64)
    assert_refused(run(p, live_dir, confirm=True), 'checksum')


def test_expired_ticket_refused(tmp_path, live_dir):
    p = make_ticket(tmp_path, expires='2026-08-13T13:59:00Z')  # 1 min ago
    assert_refused(run(p, live_dir, confirm=True), 'expired')


def test_trading_day_expiry_still_refused_one_minute_past(tmp_path, live_dir):
    """The 2026-09-08 TTL change moved WHERE expires_at lands (close of the
    2nd trading day), not WHETHER it is enforced: a ticket built through
    build_ticket is refused one minute past its own stamp."""
    orders = [{'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0,
               'limit_price': 100.75, 'tif': 'day', 'notional_est': 100.0}]
    res = {'orders': orders, 'untradeable': [], 'suppressed': [],
           'skipped': [], 'equity': 500.0}
    tk = tt.build_ticket(res, basis_event={'date': '2026-09-04',
                                           'kind': 'resize_monthly',
                                           'reason': 'test'},
                         created_at='2026-09-04T22:11:00Z', cfg={},
                         account_state_as_of='2026-09-04')
    assert tk['expires_at'] == '2026-09-09T20:00:00Z'
    p = tmp_path / 'ticket.json'
    p.write_text(json.dumps(tk))
    t = FakeTransport(quotes={'NVDA': 100.0})
    # 09:35 ET Tue after Labor Day (the first live slot): inside the window
    ok = ex.run(p, live_dir=live_dir, roster={'NVDA'}, transport=t,
                now='2026-09-08T13:35:00Z', confirm=True)
    assert ok['failures'] == [] and ok['sent'] is True
    # one minute past expiry: refused, and the receipt from the run above is
    # not what refuses it — check the expiry message explicitly
    late = ex.run(p, live_dir=live_dir, roster={'NVDA'}, transport=t,
                  now='2026-09-09T20:01:00Z', confirm=True)
    assert_refused(late, 'expired')


def test_already_executed_refused(tmp_path, live_dir):
    p = make_ticket(tmp_path)
    (live_dir / 'receipts' / 'receipt-2026-08-12-membership.json').write_text('{}')
    assert_refused(run(p, live_dir, confirm=True), 'already executed')


# ---- C2.2: roster allowlist ----

def test_ticker_outside_roster_refused(tmp_path, live_dir):
    p = make_ticket(tmp_path)
    assert_refused(run(p, live_dir, roster=('TSM',), confirm=True), 'roster')


# ---- C2.3: notional / cash / turnover / account cap ----

def test_per_order_notional_cap_refused(tmp_path, live_dir):
    orders = [{'ticker': 'NVDA', 'side': 'buy', 'shares': 3.0,
               'limit_price': 100.75, 'tif': 'day', 'notional_est': 300.0}]
    p = make_ticket(tmp_path, orders=orders)
    assert_refused(run(p, live_dir, confirm=True), 'MAX_ORDER_NOTIONAL')


def test_buys_over_available_cash_refused(tmp_path, live_dir):
    p = make_ticket(tmp_path)
    t = FakeTransport(cash=50.0, quotes={'NVDA': 100.0})
    assert_refused(run(p, live_dir, transport=t, confirm=True), 'cash')


def test_turnover_cap_refused_and_overridable(tmp_path, live_dir):
    # 2 orders x $150 = $300 = 60% of $500 equity > 50% cap
    orders = [
        {'ticker': 'TSM', 'side': 'sell', 'shares': 0.6, 'limit_price': 248.13,
         'tif': 'day', 'notional_est': 150.0},
        {'ticker': 'NVDA', 'side': 'buy', 'shares': 1.5, 'limit_price': 100.75,
         'tif': 'day', 'notional_est': 150.0},
    ]
    p = make_ticket(tmp_path, orders=orders)
    assert_refused(run(p, live_dir, confirm=True), 'turnover')
    ok = run(p, live_dir, confirm=True, allow_full_turnover=True)
    assert ok['sent'] is True


def test_buys_beyond_account_cap_refused(tmp_path, live_dir):
    p = make_ticket(tmp_path)
    t = FakeTransport(cash=600.0, equity=600.0, quotes={'NVDA': 100.0})
    assert_refused(run(p, live_dir, transport=t, confirm=True), 'ACCOUNT_CAP')


# ---- C2.4: kill switch ----

def test_kill_switch_refuses_and_prints_why(tmp_path, live_dir, capsys):
    (live_dir / 'trading-halt.flag').write_text('unknown position XYZ 2026-08-12')
    p = make_ticket(tmp_path)
    res = run(p, live_dir, confirm=True)
    assert_refused(res, 'halt')
    assert 'unknown position XYZ' in capsys.readouterr().out


# ---- C2.5: live-price sanity ----

def test_stale_limit_vs_live_quote_refused(tmp_path, live_dir):
    t = FakeTransport(quotes={'NVDA': 110.0})   # limit 100.75 > 3% away
    p = make_ticket(tmp_path)
    assert_refused(run(p, live_dir, transport=t, confirm=True), 'quote')


def test_missing_live_quote_refused(tmp_path, live_dir):
    t = FakeTransport(quotes={})
    p = make_ticket(tmp_path)
    assert_refused(run(p, live_dir, transport=t, confirm=True), 'quote')


# ---- config discipline (C3) ----

def test_missing_executor_config_refused(tmp_path, live_dir):
    (live_dir / 'executor-config.json').unlink()
    p = make_ticket(tmp_path)
    assert_refused(run(p, live_dir, confirm=True), 'executor-config')


def test_config_missing_cap_key_refused(tmp_path, live_dir):
    (live_dir / 'executor-config.json').write_text(
        json.dumps({'MAX_TURNOVER_PCT': 0.5}))
    p = make_ticket(tmp_path)
    assert_refused(run(p, live_dir, confirm=True), 'ACCOUNT_CAP')


# ---- dry-run default + happy path + receipt (C1, C4) ----

def test_dry_run_default_sends_nothing(tmp_path, live_dir):
    p = make_ticket(tmp_path)
    t = FakeTransport(quotes={'NVDA': 100.0})
    res = run(p, live_dir, transport=t)          # no confirm
    assert res['failures'] == []
    assert res['sent'] is False
    assert t.placed == []


def test_confirm_sends_and_writes_receipt(tmp_path, live_dir):
    p = make_ticket(tmp_path)
    t = FakeTransport(quotes={'NVDA': 100.0})
    res = run(p, live_dir, transport=t, confirm=True)
    assert res['sent'] is True
    assert len(t.placed) == 1
    receipt = json.loads(
        (live_dir / 'receipts' / 'receipt-2026-08-12-membership.json').read_text())
    assert receipt['ticket_id'] == '2026-08-12-membership'
    assert receipt['orders'][0]['order_id'] == 'rh-NVDA-1'
    assert receipt['orders'][0]['state'] == 'queued'
    # second run refuses: receipt is the executed-once guard
    again = run(p, live_dir, transport=t, confirm=True)
    assert_refused(again, 'already executed')


def test_partial_transmit_failure_recorded_in_receipt(tmp_path, live_dir):
    orders = [
        {'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0, 'limit_price': 100.75,
         'tif': 'day', 'notional_est': 100.0},
        {'ticker': 'TSM', 'side': 'buy', 'shares': 0.4, 'limit_price': 251.88,
         'tif': 'day', 'notional_est': 100.0},
    ]
    p = make_ticket(tmp_path, orders=orders)
    t = FakeTransport(quotes={'NVDA': 100.0, 'TSM': 250.0}, fail_on={'TSM'})
    res = run(p, live_dir, transport=t, confirm=True)
    assert res['sent'] is True
    receipt = json.loads(
        (live_dir / 'receipts' / 'receipt-2026-08-12-membership.json').read_text())
    states = {o['ticker']: o['state'] for o in receipt['orders']}
    assert states['NVDA'] == 'queued'
    assert states['TSM'] == 'transmit_error'     # flagged, not silently dropped


# ---- 2026-08-12: MCP param typing + failed-transmit re-run ------------------
# The 2026-08-11 ticket had all 10 orders bounce at the MCP schema (-32602:
# quantity/limit_price sent as JSON numbers, schema wants strings). Nothing
# was placed, but the receipt then blocked the legitimate re-run.

def test_mcp_order_params_are_strings():
    params = ex.mcp_order_params('123456789', {
        'ticker': 'ANET', 'side': 'buy', 'shares': 0.1785,
        'limit_price': 199.25, 'tif': 'day', 'notional_est': 35.30})
    assert params['quantity'] == '0.1785'          # string, 4dp
    assert params['symbol'] == 'ANET' and params['side'] == 'buy'
    assert params['account_number'] == '123456789'
    # whole-share limit orders: price is a 2dp string
    p2 = ex.mcp_order_params('1', {'ticker': 'MSFT', 'side': 'buy',
                                   'shares': 3.0, 'limit_price': 507.5,
                                   'tif': 'day', 'notional_est': 1522.5})
    assert p2['quantity'] == '3.0000'
    assert p2['limit_price'] == '507.50'


def test_all_failed_receipt_allows_rerun_and_archives(tmp_path, live_dir):
    p = make_ticket(tmp_path)
    rp = live_dir / 'receipts' / 'receipt-2026-08-12-membership.json'
    rp.write_text(json.dumps({
        'ticket_id': '2026-08-12-membership', 'sent_at': '2026-08-13T02:00:00Z',
        'checksum': 'x', 'orders': [
            {'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0, 'state':
             'transmit_error', 'order_id': None, 'error': 'invalid params'}]}))
    t = FakeTransport(quotes={'NVDA': 100.0})
    res = run(p, live_dir, transport=t, confirm=True)
    assert res['sent'] is True and len(t.placed) == 1
    assert json.loads(rp.read_text())['orders'][0]['state'] == 'queued'
    superseded = list((live_dir / 'receipts').glob('*superseded*'))
    assert len(superseded) == 1        # failed attempt archived, not erased


def test_receipt_with_any_placed_order_still_refuses(tmp_path, live_dir):
    p = make_ticket(tmp_path)
    rp = live_dir / 'receipts' / 'receipt-2026-08-12-membership.json'
    rp.write_text(json.dumps({
        'ticket_id': '2026-08-12-membership', 'sent_at': '2026-08-13T02:00:00Z',
        'checksum': 'x', 'orders': [
            {'ticker': 'NVDA', 'state': 'queued', 'order_id': 'rh-1'},
            {'ticker': 'TSM', 'state': 'transmit_error', 'order_id': None,
             'error': 'boom'}]}))
    res = run(p, live_dir, transport=FakeTransport(quotes={'NVDA': 100.0}),
              confirm=True)
    assert_refused(res, 'already executed')


# ---- 2026-08-12: fractional = market-only (Robinhood platform rule) ---------
# place_equity_order schema: "Fractional shares: only on type=market with
# market_hours=regular_hours". Fractional limit orders don't exist — the
# limit stays in the ticket as the quote-sanity reference only.

def test_mcp_params_fractional_is_market_regular_hours():
    o = {'ticker': 'ANET', 'side': 'buy', 'shares': 0.1785,
         'limit_price': 199.25, 'tif': 'day', 'notional_est': 35.30,
         'ref_id': 'abc-123'}
    params = ex.mcp_order_params('123456789', o)
    assert params['type'] == 'market'
    assert 'limit_price' not in params
    assert params['market_hours'] == 'regular_hours'
    assert params['quantity'] == '0.1785'
    assert params['ref_id'] == 'abc-123'


def test_mcp_params_whole_share_keeps_limit():
    o = {'ticker': 'NVDA', 'side': 'buy', 'shares': 2.0,
         'limit_price': 219.11, 'tif': 'day', 'notional_est': 438.22}
    params = ex.mcp_order_params('123456789', o)
    assert params['type'] == 'limit'
    assert params['limit_price'] == '219.11'
    assert params['quantity'] == '2.0000'


def test_order_ref_id_deterministic_per_logical_order():
    o = {'ticker': 'ANET', 'side': 'buy', 'shares': 0.1785}
    a = ex.order_ref_id('2026-08-11-membership', o)
    b = ex.order_ref_id('2026-08-11-membership', o)
    c = ex.order_ref_id('2026-08-11-membership', {**o, 'ticker': 'AVGO'})
    d = ex.order_ref_id('2026-08-12-membership', o)
    assert a == b                       # same logical order -> same ref_id
    assert len({a, c, d}) == 3          # ticker or ticket changes it
    import uuid
    uuid.UUID(a)                        # valid UUID string


def test_fractional_outside_regular_hours_refused(tmp_path, live_dir):
    orders = [{'ticker': 'NVDA', 'side': 'buy', 'shares': 0.5,
               'limit_price': 100.75, 'tif': 'day', 'notional_est': 50.0}]
    p = make_ticket(tmp_path, orders=orders)
    t = FakeTransport(quotes={'NVDA': 100.0})
    # 02:18 UTC = 10:18pm ET the prior evening — market closed
    res = ex.run(p, live_dir=live_dir, roster={'NVDA'}, transport=t,
                 now='2026-08-13T02:18:00Z', confirm=True)
    assert_refused(res, 'regular market hours')
    assert t.placed == []


def test_fractional_inside_regular_hours_sends(tmp_path, live_dir):
    orders = [{'ticker': 'NVDA', 'side': 'buy', 'shares': 0.5,
               'limit_price': 100.75, 'tif': 'day', 'notional_est': 50.0}]
    p = make_ticket(tmp_path, orders=orders)
    t = FakeTransport(quotes={'NVDA': 100.0})
    # NOW = 14:00 UTC Thu 2026-08-13 = 10:00am ET — market open
    res = run(p, live_dir, transport=t, confirm=True)
    assert res['sent'] is True
    assert t.placed[0]['ref_id'] == ex.order_ref_id(
        '2026-08-12-membership', t.placed[0])


# ---- 2026-08-12: order-ack extraction (receipt lost broker order ids) -------
# The 2026-08-12-manual receipt recorded order_id=None/state='submitted' for
# 10 orders that all reached Robinhood and filled: the ack was nested deeper
# than the d.get('id') lookup expected. The extractor now walks the payload;
# if nothing order-shaped is found, the raw response is preserved in the
# receipt so the true shape is never lost again.

def test_extract_order_ack_top_level():
    ack = ex.extract_order_ack({'id': 'abc', 'state': 'queued'})
    assert ack['id'] == 'abc' and ack['state'] == 'queued'


def test_extract_order_ack_nested_under_data_order():
    r = {'data': {'order': {'id': '6a7c-1', 'state': 'confirmed',
                            'symbol': 'NVDA'}}, 'guide': 'ignore me'}
    ack = ex.extract_order_ack(r)
    assert ack['id'] == '6a7c-1' and ack['state'] == 'confirmed'


def test_extract_order_ack_nested_in_list():
    r = {'data': {'results': [{'order': {'order_id': 'x-9',
                                         'state': 'filled'}}]}}
    ack = ex.extract_order_ack(r)
    assert ack['order_id'] == 'x-9' and ack['state'] == 'filled'


def test_extract_order_ack_absent_returns_empty():
    assert ex.extract_order_ack({'data': {'message': 'ok'}}) == {}
    assert ex.extract_order_ack({}) == {}


def test_receipt_preserves_raw_response_when_ack_missing(tmp_path, live_dir):
    class OpaqueTransport(FakeTransport):
        def place_equity_order(self, order):
            self.placed.append(order)
            return {'order_id': None, 'state': 'submitted',
                    'raw_response': {'data': {'message': 'accepted'}}}

    p = make_ticket(tmp_path)
    t = OpaqueTransport(quotes={'NVDA': 100.0})
    res = run(p, live_dir, transport=t, confirm=True)
    assert res['sent'] is True
    receipt = json.loads(
        (live_dir / 'receipts' / 'receipt-2026-08-12-membership.json').read_text())
    assert receipt['orders'][0]['raw_response'] == {
        'data': {'message': 'accepted'}}


# ---- 3a (2026-09-08): a partial transmit failure must not report success ----
# VRT's buy leg was rejected on 2026-08-17 ("You can only purchase 0 shares")
# while the other 14 legs went through. run() returned failures=[] and the run
# reported SUCCESS, so nothing escalated and the position sat 67% underweight
# for three weeks. The receipt recorded it correctly the whole time — the
# defect was purely in what run() reported to its caller.

def _partial_run(tmp_path, live_dir):
    orders = [
        {'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0, 'limit_price': 100.75,
         'tif': 'day', 'notional_est': 100.0},
        {'ticker': 'TSM', 'side': 'buy', 'shares': 0.4, 'limit_price': 251.88,
         'tif': 'day', 'notional_est': 100.0},
    ]
    p = make_ticket(tmp_path, orders=orders)
    t = FakeTransport(quotes={'NVDA': 100.0, 'TSM': 250.0}, fail_on={'TSM'})
    return run(p, live_dir, transport=t, confirm=True), t


def test_partial_transmit_failure_is_reported_as_a_failure(tmp_path, live_dir):
    res, _ = _partial_run(tmp_path, live_dir)
    assert res['failures'], 'a leg that never reached the broker must surface'
    assert any('TSM' in f for f in res['failures']), res['failures']


def test_partial_transmit_failure_keeps_sent_true(tmp_path, live_dir):
    """`sent` must stay True — 1 of 2 orders DID reach the broker, and
    misreporting that would invite a double-execution on re-run."""
    res, _ = _partial_run(tmp_path, live_dir)
    assert res['sent'] is True
    assert res['receipt'] is not None and res['receipt'].exists()


def test_partial_transmit_failure_exits_nonzero(tmp_path, live_dir):
    """main() is `sys.exit(0 if not res['failures'] else 1)`, so a non-empty
    failures list is exactly what makes the scheduled run visibly fail."""
    res, _ = _partial_run(tmp_path, live_dir)
    assert bool(res['failures']) is True


def test_partial_failure_names_every_failed_leg(tmp_path, live_dir):
    orders = [
        {'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0, 'limit_price': 100.75,
         'tif': 'day', 'notional_est': 100.0},
        {'ticker': 'TSM', 'side': 'buy', 'shares': 0.4, 'limit_price': 251.88,
         'tif': 'day', 'notional_est': 100.0},
    ]
    p = make_ticket(tmp_path, orders=orders)
    t = FakeTransport(quotes={'NVDA': 100.0, 'TSM': 250.0},
                      fail_on={'NVDA', 'TSM'})
    res = run(p, live_dir, transport=t, confirm=True)
    assert len(res['failures']) == 2
    assert {'NVDA', 'TSM'} == {f.split(':')[0].split()[-1]
                               for f in res['failures']}


def test_clean_run_still_reports_no_failures(tmp_path, live_dir):
    """Regression: an all-success transmit must stay a clean exit."""
    p = make_ticket(tmp_path)
    res = run(p, live_dir, transport=FakeTransport(quotes={'NVDA': 100.0}),
              confirm=True)
    assert res['failures'] == [] and res['sent'] is True


def test_partial_failure_does_not_weaken_the_executed_once_guard(
        tmp_path, live_dir):
    """3a changes what is REPORTED, never what is RE-SENT. After a partial,
    the same ticket must still be refused — 1 order exists broker-side."""
    _partial_run(tmp_path, live_dir)
    orders = [
        {'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0, 'limit_price': 100.75,
         'tif': 'day', 'notional_est': 100.0},
        {'ticker': 'TSM', 'side': 'buy', 'shares': 0.4, 'limit_price': 251.88,
         'tif': 'day', 'notional_est': 100.0},
    ]
    p2 = make_ticket(tmp_path, orders=orders)
    res2 = run(p2, live_dir, transport=FakeTransport(
        quotes={'NVDA': 100.0, 'TSM': 250.0}), confirm=True)
    assert_refused(res2, 'already executed')


# ---- 2026-09-08: sell proceeds fund buys (Dom-approved gate change) --------

def _resize_orders(sell_notional=150.0, buy_notional=100.0):
    return [{'ticker': 'TSM', 'side': 'sell', 'shares': sell_notional / 250.0,
             'limit_price': 250.0, 'tif': 'day', 'notional_est': sell_notional},
            {'ticker': 'NVDA', 'side': 'buy', 'shares': buy_notional / 100.0,
             'limit_price': 100.0, 'tif': 'day', 'notional_est': buy_notional}]


def test_buys_funded_by_same_ticket_sells_pass_cash_gate(tmp_path, live_dir):
    """A resize in a fully invested account: idle cash 0, sells 150, buys
    100 — the sells fund the buys. Before 2026-09-08 this was refused."""
    p = make_ticket(tmp_path, _resize_orders())
    tr = FakeTransport(cash=0.0, quotes={'NVDA': 100.0, 'TSM': 250.0})
    res = run(p, live_dir, transport=tr)
    assert res['failures'] == []


def test_sell_proceeds_are_haircut_before_funding_buys(tmp_path, live_dir):
    """Sells are credited at (1 - SELL_PROCEEDS_HAIRCUT), never at par."""
    p = make_ticket(tmp_path, _resize_orders(sell_notional=100.0,
                                             buy_notional=100.0))
    tr = FakeTransport(cash=0.0, quotes={'NVDA': 100.0, 'TSM': 250.0})
    res = run(p, live_dir, transport=tr)
    assert_refused(res, 'sell proceeds')


class FundingTransport(FakeTransport):
    """Cash appears only after a sell has been placed (broker settles the
    market sell before buying power updates)."""

    def __init__(self, cash_after_sell, **kw):
        super().__init__(**kw)
        self._after = cash_after_sell
        self.polls = 0

    def portfolio(self):
        self.polls += 1
        sold = any(o['side'] == 'sell' for o in self.placed)
        return {'cash': self._after if sold else self._cash,
                'equity': self._equity}


def test_buys_wait_for_sell_proceeds_before_sending(tmp_path, live_dir):
    p = make_ticket(tmp_path, _resize_orders())
    tr = FundingTransport(cash_after_sell=150.0, cash=0.0,
                          quotes={'NVDA': 100.0, 'TSM': 250.0})
    slept = []
    res = run(p, live_dir, transport=tr, confirm=True, sleeper=slept.append)
    assert [o['side'] for o in tr.placed] == ['sell', 'buy']
    assert res['failures'] == [] and res['sent'] is True


def test_buys_not_sent_when_funding_never_arrives(tmp_path, live_dir):
    """Sell proceeds never show up: sells stay sent (and receipted), buys are
    recorded as not_sent and reported as failures — never fired blind into a
    broker rejection ('You can only purchase 0 shares', VRT 2026-08-17)."""
    p = make_ticket(tmp_path, _resize_orders())
    tr = FundingTransport(cash_after_sell=0.0, cash=0.0,
                          quotes={'NVDA': 100.0, 'TSM': 250.0})
    slept = []
    res = run(p, live_dir, transport=tr, confirm=True, sleeper=slept.append)
    assert [o['side'] for o in tr.placed] == ['sell']
    assert slept                                   # it actually waited
    assert res['sent'] is True
    assert any('funding' in f for f in res['failures'])
    rec = json.loads(res['receipt'].read_text())
    states = {o['ticker']: o['state'] for o in rec['orders']}
    assert states['NVDA'] == 'not_sent' and states['TSM'] == 'queued'
