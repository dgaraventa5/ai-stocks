"""Trade ticket generation (§B of the 2026-08-09 agentic-execution spec).

Pure-logic tests: share-delta from ACTUAL account state, marketable limits,
dust suppression, untradeable-name renormalization, canonical checksum.
"""
import json

import pytest

import trade_ticket as tt

# CASH_BUFFER_PCT pinned to 0 so these cases isolate limit math, dust,
# renormalization and delta-from-actuals from cash sizing. The buffer's own
# behavior is covered against the real DEFAULTS in the cash-buffer tests below.
CFG = {'MIN_ORDER_NOTIONAL': 25.0, 'LIMIT_TOL': 0.0075,
       'MAX_WEIGHT': 0.12, 'TICKET_TTL_HOURS': 48, 'CASH_BUFFER_PCT': 0.0}


def orders_by_ticker(result):
    return {o['ticker']: o for o in result['orders']}


# ---- share-delta computation (B2) ----

def test_fresh_deployment_buys_at_marketable_limit():
    res = tt.compute_orders(
        target_weights={'NVDA': 0.6, 'TSM': 0.4},
        positions={}, cash=500.0,
        prices={'NVDA': 180.0, 'TSM': 250.0}, cfg=CFG)
    o = orders_by_ticker(res)
    assert res['equity'] == 500.0
    nvda = o['NVDA']
    assert nvda['side'] == 'buy'
    assert nvda['shares'] == 1.6667          # 300 / 180, 4dp fractional
    assert nvda['limit_price'] == 181.35     # 180 * 1.0075
    assert nvda['tif'] == 'day'
    assert abs(nvda['notional_est'] - 300.0) < 0.05
    assert o['TSM']['shares'] == 0.8
    assert o['TSM']['limit_price'] == 251.88  # 250 * 1.0075 rounded


def test_sell_limit_below_reference():
    # 2 sh NVDA @180 (mv 360) + 140 cash = 500 equity; target 40% = 200
    res = tt.compute_orders(
        target_weights={'NVDA': 0.4},
        positions={'NVDA': {'shares': 2.0}}, cash=140.0,
        prices={'NVDA': 180.0}, cfg=CFG)
    o = orders_by_ticker(res)['NVDA']
    assert o['side'] == 'sell'
    assert o['shares'] == 0.8889             # 160 / 180
    assert o['limit_price'] == 178.65        # 180 * 0.9925


def test_delta_from_actuals_tops_up_partial_fill():
    # Target 60% of 500 = 300; actual holding only 150 (partial fill last time)
    res = tt.compute_orders(
        target_weights={'NVDA': 0.6},
        positions={'NVDA': {'shares': 1.0}}, cash=350.0,
        prices={'NVDA': 150.0}, cfg=CFG)
    o = orders_by_ticker(res)['NVDA']
    assert o['side'] == 'buy'
    assert o['shares'] == 1.0                # (300-150)/150


def test_exited_position_fully_sold():
    res = tt.compute_orders(
        target_weights={'NVDA': 0.6},
        positions={'ARM': {'shares': 2.0}, 'NVDA': {'shares': 1.0}},
        cash=100.0,
        prices={'ARM': 100.0, 'NVDA': 150.0}, cfg=CFG)
    o = orders_by_ticker(res)['ARM']
    assert o['side'] == 'sell'
    assert o['shares'] == 2.0                # everything


def test_sells_listed_before_buys():
    res = tt.compute_orders(
        target_weights={'NVDA': 0.6},
        positions={'ARM': {'shares': 2.0}}, cash=300.0,
        prices={'ARM': 100.0, 'NVDA': 150.0}, cfg=CFG)
    sides = [o['side'] for o in res['orders']]
    assert sides == sorted(sides, key=lambda s: s != 'sell')  # sells first


def test_dust_order_suppressed_and_logged():
    # Delta $20 < $25 MIN_ORDER_NOTIONAL
    res = tt.compute_orders(
        target_weights={'NVDA': 0.64},
        positions={'NVDA': {'shares': 3.0}}, cash=200.0,
        prices={'NVDA': 100.0}, cfg=CFG)     # equity 500, target 320, mv 300
    assert res['orders'] == []
    assert len(res['suppressed']) == 1
    sup = res['suppressed'][0]
    assert sup['ticker'] == 'NVDA'
    assert 'dust' in sup['reason']


def test_missing_price_skips_and_flags():
    res = tt.compute_orders(
        target_weights={'NVDA': 0.5, 'AVGO': 0.5},
        positions={}, cash=500.0,
        prices={'NVDA': 100.0}, cfg=CFG)
    assert 'AVGO' not in orders_by_ticker(res)
    assert res['skipped'][0]['ticker'] == 'AVGO'
    assert 'price' in res['skipped'][0]['reason']


# ---- untradeable foreign local lines (B3) ----

def test_foreign_local_line_untradeable():
    assert not tt.is_tradeable('6954.T')
    assert not tt.is_tradeable('KGX.DE')
    assert not tt.is_tradeable('0981.HK')
    assert tt.is_tradeable('NVDA')
    assert tt.is_tradeable('BRK')


def test_untradeable_weight_renormalized_with_cap():
    # 6954.T untradeable: its 4% redistributes over A/B, but A hits the 12% cap
    # so B absorbs the rest. Total budget preserved (0.20).
    res = tt.compute_orders(
        target_weights={'AAA': 0.10, 'BBB': 0.06, '6954.T': 0.04},
        positions={}, cash=1000.0,
        prices={'AAA': 10.0, 'BBB': 10.0}, cfg=CFG)
    o = orders_by_ticker(res)
    assert res['untradeable'][0]['ticker'] == '6954.T'
    assert abs(o['AAA']['notional_est'] - 120.0) < 0.5   # capped at 12%
    assert abs(o['BBB']['notional_est'] - 80.0) < 0.5    # absorbs remainder
    assert '6954.T' not in o


# ---- checksum + ticket assembly (B3) ----

def test_checksum_canonical_and_tamper_sensitive():
    orders = [{'ticker': 'NVDA', 'side': 'buy', 'shares': 1.0,
               'limit_price': 100.0, 'tif': 'day', 'notional_est': 100.0}]
    reordered = [dict(reversed(list(orders[0].items())))]
    assert tt.ticket_checksum(orders) == tt.ticket_checksum(reordered)
    tampered = [dict(orders[0], shares=2.0)]
    assert tt.ticket_checksum(orders) != tt.ticket_checksum(tampered)


def test_build_ticket_fields_and_expiry():
    res = tt.compute_orders(
        target_weights={'NVDA': 0.6}, positions={}, cash=500.0,
        prices={'NVDA': 180.0}, cfg=CFG)
    tk = tt.build_ticket(
        res, basis_event={'date': '2026-08-12', 'kind': 'membership',
                          'reason': 'test'},
        created_at='2026-08-12T21:30:00Z', cfg=CFG,
        account_state_as_of='2026-08-12')
    assert tk['ticket_id'] == '2026-08-12-membership'
    assert tk['expires_at'] == '2026-08-14T21:30:00Z'    # +48h
    assert tk['account_equity_at_gen'] == 500.0
    assert tk['account_state_as_of'] == '2026-08-12'
    assert tk['checksum'] == tt.ticket_checksum(tk['orders'])
    # round-trips through JSON
    assert json.loads(json.dumps(tk)) == tk


# ---- cash buffer (2026-08-17: the last order failed on insufficient funds) ----

def test_buys_leave_a_cash_buffer_for_slippage():
    """Full redeploy must not consume ~100% of cash.

    Robinhood places fractional orders as MARKET orders (the limit price is
    advisory), and the executor sends them sequentially, so every prior fill's
    slippage accumulates against the last one. On 2026-08-17 a ticket sized to
    99.98% of cash filled 14 of 15 and the alphabetically-last name came back
    "You can only purchase 0 shares of VRT" — broker-speak for insufficient
    funds. Whichever ticker sorts last is systematically the casualty, so the
    fix belongs in sizing, not in retry.
    """
    cash = 1000.0
    weights = {t: 0.25 for t in ('AAA', 'BBB', 'CCC', 'DDD')}
    prices = {t: 100.0 for t in weights}
    res = tt.compute_orders(weights, {}, cash, prices, dict(tt.DEFAULTS))
    spend = sum(o['shares'] * o['limit_price'] for o in res['orders']
                if o['side'] == 'buy')
    assert spend <= cash * 0.99, f'spent {spend} of {cash} — no slack for slippage'
    assert spend >= cash * 0.95, f'spent only {spend} — buffer is too fat to be useful'


def test_cash_buffer_is_configurable():
    cash = 1000.0
    weights, prices = {'AAA': 1.0}, {'AAA': 100.0}
    cfg = dict(tt.DEFAULTS, CASH_BUFFER_PCT=0.10, MAX_WEIGHT=1.0)
    res = tt.compute_orders(weights, {}, cash, prices, cfg)
    spend = sum(o['shares'] * o['limit_price'] for o in res['orders'])
    assert spend == pytest.approx(900.0, rel=0.01)
