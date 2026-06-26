"""Resolution templates for forecast calibration (CLAUDE.md rule 17).

Each resolver is deterministic: resolve(forecast, *, price_loader, today) ->
Resolution. Price data is INJECTED (price_loader), never fetched here, so
resolvers unit-test on synthetic series under the CI env (no yfinance). The
yfinance-backed loader lives in resolve_forecasts.py.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

HORIZON_BUFFER_DAYS = 7        # padding on resolution_date past the horizon bar
GRACE_DAYS = 30               # keep retrying an under-filled series this long before needs_review
MISSING_CONSTITUENT_TOLERANCE = 0.25


@dataclass
class Resolution:
    status: str                       # resolved | needs_review | open (not gradable yet)
    outcome: int | None               # 1 | 0 | None
    resolved_date: str | None
    evidence: str | None
    resolver_confidence: str | None   # auto | None


def resolution_date_for(created: dt.date, horizon_td: int,
                        buffer_days: int = HORIZON_BUFFER_DAYS) -> dt.date:
    """horizon_td weekdays forward from created + buffer (stdlib, holiday-naive).
    A scheduling date; the resolver always re-checks actual bar count."""
    d, counted = created, 0
    while counted < horizon_td:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:    # Mon-Fri
            counted += 1
    return d + dt.timedelta(days=buffer_days)


def _horizon_return(prices: dict, created: dt.date, horizon_td: int):
    """Return over the first bar >= created to the bar horizon_td positions later.
    None if insufficient bars or a zero base."""
    bars = sorted((d, c) for d, c in prices.items() if d >= created and c is not None)
    if len(bars) < horizon_td + 1:
        return None
    base, horizon = bars[0][1], bars[horizon_td][1]
    if not base:
        return None
    return horizon / base - 1.0, bars[0][0], bars[horizon_td][0]


def resolve_rel_strength_1q(forecast: dict, *, price_loader, today: dt.date | None = None) -> Resolution:
    today = today or dt.date.today()
    rule = forecast["resolution_rule"]
    horizon = rule["horizon_td"]
    created = dt.date.fromisoformat(forecast["created_date"])
    res_date = dt.date.fromisoformat(forecast["resolution_date"])
    ticker = forecast["ticker"]

    self_calc = _horizon_return(price_loader(ticker, created), created, horizon)
    if self_calc is None:
        if today <= res_date + dt.timedelta(days=GRACE_DAYS):
            return Resolution("open", None, None, None, None)
        return Resolution("needs_review", None, None,
                          f"{ticker}: <{horizon + 1} trading bars by {today} "
                          f"({GRACE_DAYS}d past resolution_date)", None)
    r_self, d0, dh = self_calc

    constituents = rule["constituents"]
    rets, missing = [], []
    for cn in constituents:
        calc = _horizon_return(price_loader(cn, created), created, horizon)
        (rets.append(calc[0]) if calc is not None else missing.append(cn))
    if not rets or len(missing) / len(constituents) > MISSING_CONSTITUENT_TOLERANCE:
        return Resolution("needs_review", None, None,
                          f"cohort degraded: {len(missing)}/{len(constituents)} constituents missing data",
                          None)
    r_bench = sum(rets) / len(rets)
    outcome = 1 if r_self > r_bench else 0
    evidence = (f"{ticker} {r_self * 100:+.1f}% vs {rule['benchmark']} ({len(rets)} names) "
                f"{r_bench * 100:+.1f}%, {d0}→{dh} ({horizon} td), yfinance adj close → {outcome}")
    return Resolution("resolved", outcome, today.isoformat(), evidence, "auto")


RESOLVERS = {"REL_STRENGTH_1Q": resolve_rel_strength_1q}
