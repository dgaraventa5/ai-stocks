"""Trade ticket logic — §B of the agentic-execution pipeline spec (2026-08-09).

Pure functions, stdlib only (deploy-site CI runs a minimal env). Share deltas
are computed from ACTUAL account state (the latest reconciliation snapshot),
never from the previous model event — partial fills and drift must not
compound (spec B2). Orders are marketable limits, never market orders.

The CLI wrapper that feeds this from the workbook + live account state is
scripts/generate_trade_ticket.py. This module never touches the network.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json

DEFAULTS = {
    'MIN_ORDER_NOTIONAL': 25.0,   # dust guard (spec B2)
    'LIMIT_TOL': 0.0075,          # marketable-limit tolerance
    'MAX_WEIGHT': 0.12,           # renormalization cap (mirrors sizing cap)
    'TICKET_TTL_HOURS': 48,
    'CASH_BUFFER_PCT': 0.02,      # undeployed slack for slippage (see below)
}


def is_tradeable(ticker: str) -> bool:
    """Foreign local lines (6954.T, KGX.DE, 0981.HK, ... — rule 27) carry an
    exchange suffix after a dot and are not tradeable on Robinhood. Plain US
    symbols have no dot. If a dotted US share class (BRK.B) ever enters the
    roster, revisit — today none is on the watchlist."""
    return '.' not in ticker


def renormalize_weights(weights: dict[str, float], cap: float) -> dict[str, float]:
    """Scale weights to `budget` (their own original total), enforcing the
    per-name cap by freezing capped names and redistributing (same iterative
    shape as refresh_targets.cap_and_normalize)."""
    budget = sum(weights.values())
    w = dict(weights)
    for _ in range(20):
        total = sum(w.values())
        if not total:
            return w
        w = {t: v / total * budget for t, v in w.items()}
        over = {t: cap for t, v in w.items() if v > cap + 1e-9}
        if not over:
            return w
        rest = {t: v for t, v in w.items() if t not in over}
        rest_total = sum(rest.values())
        if not rest_total:
            return over
        fixed = sum(over.values())
        w = over | {t: v / rest_total * (budget - fixed)
                    for t, v in rest.items()}
    return w


def compute_orders(target_weights: dict[str, float],
                   positions: dict[str, dict],
                   cash: float,
                   prices: dict[str, float],
                   cfg: dict) -> dict:
    """Share deltas from actual account state.

    positions: {ticker: {'shares': float}} — actual holdings.
    prices: reference prices (last close) for every target + held name.
    Returns {'orders', 'untradeable', 'suppressed', 'skipped', 'equity'}.
    """
    min_notional = float(cfg.get('MIN_ORDER_NOTIONAL',
                                 DEFAULTS['MIN_ORDER_NOTIONAL']))
    tol = float(cfg.get('LIMIT_TOL', DEFAULTS['LIMIT_TOL']))
    cap = float(cfg.get('MAX_WEIGHT', DEFAULTS['MAX_WEIGHT']))

    untradeable = [{'ticker': t, 'weight': w,
                    'reason': 'foreign local line — not tradeable on Robinhood; '
                              'weight renormalized over tradeable set (spec B3)'}
                   for t, w in sorted(target_weights.items())
                   if not is_tradeable(t)]
    tradeable = {t: w for t, w in target_weights.items() if is_tradeable(t)}
    if untradeable:
        # Preserve the total target budget over the tradeable set, cap intact.
        budget = sum(target_weights.values())
        scaled = {t: w / sum(tradeable.values()) * budget
                  for t, w in tradeable.items()} if tradeable else {}
        tradeable = renormalize_weights(scaled, cap) if scaled else {}

    mv = {t: p['shares'] * prices[t]
          for t, p in positions.items() if t in prices}
    # Deploy against equity MINUS a cash buffer. Robinhood places fractional
    # orders as MARKET orders (limit_price below is advisory) and the executor
    # sends them sequentially, so each fill's slippage accumulates against the
    # orders still to come — the ticker sorting last is systematically the one
    # that runs out of money. Worse, limits are marked up by LIMIT_TOL, so
    # targeting 100% of equity overspends by that tolerance before slippage is
    # even considered. Keep the buffer > LIMIT_TOL. (2026-08-17: a 99.98%
    # ticket filled 14 of 15; VRT came back "You can only purchase 0 shares".)
    buffer_pct = float(cfg.get('CASH_BUFFER_PCT', DEFAULTS['CASH_BUFFER_PCT']))
    equity = cash + sum(mv.values())          # true equity — reported as-is
    deployable = equity * (1.0 - buffer_pct)  # what targets are sized against

    orders, suppressed, skipped = [], [], []
    tickers = sorted(set(tradeable) | set(positions))
    for t in tickers:
        if t not in prices:
            skipped.append({'ticker': t,
                            'reason': 'no reference price — order not generated '
                                      '(rule 3: flagged, not guessed)'})
            continue
        ref = float(prices[t])
        target_notional = tradeable.get(t, 0.0) * deployable
        delta = target_notional - mv.get(t, 0.0)
        if abs(delta) < min_notional:
            if abs(delta) > 1e-9:
                suppressed.append({'ticker': t,
                                   'notional_est': round(abs(delta), 2),
                                   'reason': f'dust: |{delta:.2f}| < '
                                             f'MIN_ORDER_NOTIONAL {min_notional}'})
            continue
        side = 'buy' if delta > 0 else 'sell'
        shares = round(abs(delta) / ref, 4)
        if side == 'sell' and t in positions:
            shares = min(shares, positions[t]['shares'])   # never short
        limit = round(ref * (1 + tol), 2) if side == 'buy' \
            else round(ref * (1 - tol), 2)
        orders.append({'ticker': t, 'side': side, 'shares': shares,
                       'limit_price': limit, 'tif': 'day',
                       'notional_est': round(shares * ref, 2)})
    orders.sort(key=lambda o: (o['side'] != 'sell', o['ticker']))
    return {'orders': orders, 'untradeable': untradeable,
            'suppressed': suppressed, 'skipped': skipped,
            'equity': round(equity, 2)}


def ticket_checksum(orders: list[dict]) -> str:
    """sha256 of the canonical orders array (sorted keys, no whitespace) —
    key order in the source dicts must not matter, values must."""
    canonical = json.dumps(orders, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()


def build_ticket(result: dict, basis_event: dict, created_at: str,
                 cfg: dict, account_state_as_of: str) -> dict:
    ttl = int(cfg.get('TICKET_TTL_HOURS', DEFAULTS['TICKET_TTL_HOURS']))
    created = dt.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    expires = created + dt.timedelta(hours=ttl)
    return {
        'ticket_id': f"{basis_event['date']}-{basis_event['kind']}",
        'created_at': created_at,
        'expires_at': expires.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'basis_event': basis_event,
        'account_equity_at_gen': result['equity'],
        'account_state_as_of': account_state_as_of,
        'orders': result['orders'],
        'untradeable': result['untradeable'],
        'suppressed': result['suppressed'],
        'skipped': result['skipped'],
        'checksum': ticket_checksum(result['orders']),
    }
