"""Model-portfolio state shared by refresh_targets.py and track_performance.py.

Per Dom's 2026-06-09 decision, the MODEL is the portfolio of record (the
Positions sheet is unused). The model is event-sourced in
tracking/performance-config.json:

  events[0]   initial deployment (2026-05-26, $10,000 notional)
  events[n]   a rebalance: the portfolio marked to that day's value, then
              re-allocated across the pipeline's new target weights

refresh_targets.py logs an event automatically whenever MEMBERSHIP changes
(enter/exit) — weight drift within the same names does NOT rebalance the
model, matching the hysteresis philosophy. The standing assumption, accepted
with the model-only decision: Dom mirrors each membership-changing refresh in
his account around the day it runs. If that slips, the model is a strategy
benchmark rather than an account mirror.

Valuation chains automatically: each event's allocations embed all growth
before it, so marking only the latest event prices the whole history.
Returns use dividend-adjusted closes (~total return). Names with no price
data are carried at their event-date value and flagged, never guessed.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import time

from common import ROOT, flag

CONFIG = ROOT / 'tracking' / 'performance-config.json'

_series_cache: dict[str, object] = {}


def load_cfg() -> dict:
    cfg = json.loads(CONFIG.read_text())
    if 'events' not in cfg:
        # Migrate the original flat schema: deployment becomes event 0.
        cfg['events'] = [{
            'date': cfg['inception'],
            'reason': 'initial deployment (trade plan, prices 2026-05-26)',
            'allocations': {t: m['alloc'] for t, m in cfg.pop('model').items()},
            'cash': cfg['cash'],
        }]
    return cfg


def save_cfg(cfg: dict) -> None:
    CONFIG.write_text(json.dumps(cfg, indent=2) + '\n')


PCONFIG = ROOT / 'tracking' / 'portfolio-config.json'

DEFAULT_PCFG = {
    # Construction-v2 params, spec 2026-08-07 §A1/§B1/§C1. Do NOT tune against
    # the 10-week history that motivated the change (spec Non-goals).
    'sizing': {'mode': 'tier', 'lookback': 60, 'sigma_floor': 0.005,
               'max_weight': 0.12, 'min_weight': 0.03, 'drift_band': 0.25},
    'selection': {'mode': 'score'},
    'shadows': {'top': 15, 'next': 25, 'tail': 40},
}


def load_pcfg() -> dict:
    """Construction-v2 config: committed values merged over defaults, so a
    missing file or missing key falls back to current (tier/score) behavior."""
    try:
        raw = json.loads(PCONFIG.read_text())
    except (OSError, ValueError):
        raw = {}
    return {k: {**v, **(raw.get(k) or {})} for k, v in DEFAULT_PCFG.items()}


def _series(ticker: str, earliest: str):
    """Dividend-adjusted close series from `earliest`, cached per run."""
    if ticker not in _series_cache:
        import yfinance as yf  # lazy: keeps the portfolio path offline-importable
        start = (dt.date.fromisoformat(earliest) - dt.timedelta(days=5)).isoformat()
        hist = yf.Ticker(ticker).history(start=start, auto_adjust=True)
        time.sleep(0.2)
        _series_cache[ticker] = (None if hist is None or hist.empty
                                 else hist['Close'].dropna())
    return _series_cache[ticker]


def ret_since(ticker: str, frm: str, earliest: str) -> float | None:
    """Total return from the first close on/after `frm` to the latest close."""
    s = _series(ticker, earliest)
    if s is None:
        return None
    sub = s[s.index.date >= dt.date.fromisoformat(frm)]
    if sub.empty:
        return None
    return float(s.iloc[-1] / sub.iloc[0] - 1)


def mark(cfg: dict) -> tuple[float, dict[str, float], list[str]]:
    """(model value now, per-name P&L since last event, names missing prices)."""
    ev = cfg['events'][-1]
    value = float(ev.get('cash', 0))
    pnl: dict[str, float] = {}
    missing: list[str] = []
    for t, alloc in ev['allocations'].items():
        r = ret_since(t, ev['date'], cfg['inception'])
        if r is None:
            missing.append(t)
            value += alloc          # carried at event-date value
            flag(f'{t}: no price data — carried at last event value')
        else:
            pnl[t] = alloc * r
            value += alloc * (1 + r)
    return value, pnl, missing


def log_rebalance(cfg: dict, weights: dict[str, float], reason: str,
                  tiers: dict[str, str] | None = None) -> dict:
    """Mark the model, re-allocate at today's value, append (or same-day
    replace) the event, and persist. `weights` are fractions of total value
    (summing to 1 - cash buffer, as refresh_targets produces them). `tiers` is
    the per-name tier at rebalance time — the baseline the tier-crossing detector
    compares future runs against."""
    today = dt.date.today().isoformat()
    value, _, missing = mark(cfg)
    if missing:
        flag(f'rebalance marked with carried values for: {", ".join(missing)}')
    alloc = {t: round(w * value, 2) for t, w in weights.items()}
    event = {'date': today, 'reason': reason, 'allocations': alloc,
             'tiers': dict(tiers or {}),
             'cash': round(value - sum(alloc.values()), 2)}
    if cfg['events'] and cfg['events'][-1]['date'] == today:
        cfg['events'][-1] = event       # idempotent same-day re-runs
    else:
        cfg['events'].append(event)
    save_cfg(cfg)
    return event


SERIES = ROOT / 'tracking' / 'performance-series.json'


def ew_roster_events(cfg: dict) -> list[dict]:
    """Chronological [{date, roster}] for the equal-weight benchmark.

    A re-baseline appends a new {date, roster} so the EW series chain-links at
    the splice (old roster before, new roster after) instead of being rewritten
    with hindsight. Legacy configs carrying only the flat `ew_universe` list are
    migrated to a single inception-dated roster."""
    evs = cfg.get('ew_events')
    if not evs:
        return [{'date': cfg['inception'],
                 'roster': list(cfg.get('ew_universe', []))}]
    return sorted(evs, key=lambda e: e['date'])


def chain_linked_growth(events, inception: str, idx):
    """Chain-linked equal-weight growth-of-1 over [{date, roster}] events.

    Extracted from ew_growth (2026-08-07) so the EW benchmark, the EW_ROSTER
    sizing-null shadow (v2 spec A4) and the band shadows (v2 spec C1) share
    one engine. Within each roster period the value is an equal-weight
    (daily-rebalanced at splices) basket of that period's names, re-based to
    the prior period's closing level at the splice — a roster change injects
    NO return on the splice itself and NO look-ahead: dates before a splice
    keep the old roster, the new roster drives returns only after it. The
    trailing ffill never BACKfills, so a shadow whose first event postdates
    inception stays NaN before it (forward-only guarantee, spec C1)."""
    import pandas as pd

    inc_date = dt.date.fromisoformat(inception)

    # growth-of-1 from inception per name, aligned to the calendar;
    # period normalization divides by the anchor value, recovering price ratios.
    def gfull(t):
        s = _series(t, inception)
        if s is None:
            return None
        s = s[s.index.date >= inc_date]
        if s.empty or s.iloc[0] == 0:
            return None
        return (s / s.iloc[0]).reindex(idx).ffill()

    events = sorted(events, key=lambda e: e['date'])
    out = pd.Series(index=idx, dtype=float)
    level = 1.0
    anchor = None                       # prior period's last calendar timestamp
    for i, ev in enumerate(events):
        start = dt.date.fromisoformat(ev['date'])
        end = (dt.date.fromisoformat(events[i + 1]['date'])
               if i + 1 < len(events) else None)
        mask = idx.date >= start
        if end is not None:
            mask &= idx.date < end
        if not mask.any():
            continue
        seg_idx = idx[mask]
        parts = []
        for t in ev['roster']:
            g = gfull(t)
            if g is None:
                continue
            base = g.loc[anchor] if anchor is not None else g.loc[seg_idx[0]]
            if base != base or base == 0:          # NaN (pre-listing) / zero
                continue
            parts.append(g.reindex(seg_idx) / base)
        if not parts:
            continue
        seg = level * pd.concat(parts, axis=1).mean(axis=1)
        out[seg_idx] = seg
        level = float(seg.iloc[-1])
        anchor = seg_idx[-1]
    out = out.ffill()
    return None if out.isna().all() else out


def model_roster_events(cfg: dict) -> list[dict]:
    """[{date, roster}] mirroring the model's actual event history — the
    EW_ROSTER sizing-null (v2 spec A4): same names, same event dates, equal
    weights. MODEL − EW_ROSTER is the standing measure of what the sizing
    rule adds; the permanent tripwire input."""
    return [{'date': ev['date'], 'roster': sorted(ev['allocations'])}
            for ev in cfg['events']]


def ew_growth(cfg: dict, idx=None):
    """Chain-linked equal-weight growth-of-1 series for the EW benchmark
    (see chain_linked_growth for the splice/look-ahead semantics)."""
    inception = cfg['inception']
    if idx is None:
        s = _series('SMH', inception)
        if s is None:
            return None
        s = s[s.index.date >= dt.date.fromisoformat(inception)]
        if s.empty:
            return None
        idx = s.index
    return chain_linked_growth(ew_roster_events(cfg), inception, idx)


def ew_return_since(cfg: dict, frm: str) -> float | None:
    """Chain-linked EW total return from the first close on/after `frm`."""
    ew = ew_growth(cfg)
    if ew is None:
        return None
    sub = ew[ew.index.date >= dt.date.fromisoformat(frm)]
    if sub.empty:
        return None
    return float(ew.iloc[-1] / sub.iloc[0] - 1)


def _may_overwrite_series(out: dict) -> bool:
    """High-water-mark guard: a rebuild may correct historical values but must
    never DROP a trading day already recorded in the committed series.

    Why (2026-06-27): yfinance intermittently serves the latest bar with a NaN
    close (unsettled adjusted close, esp. over weekends). _series does
    ['Close'].dropna(), so a flickering rebuild comes back one bar SHORTER; the
    daily-refresh.yml `git diff --quiet` guard committed that shorter series and
    bounced the dashboard as_of BACKWARD. Refuse the regression here so every
    caller (cron, /update-dashboard, local) is protected; the next run advances
    once Yahoo settles the close. FORCE_SERIES=1 bypasses for deliberate history
    rebuilds (inception/notional/config changes).
    """
    if os.environ.get('FORCE_SERIES') == '1':
        return True
    if not SERIES.exists():
        return True
    try:
        committed = set(json.loads(SERIES.read_text()).get('dates', []))
    except (ValueError, OSError):
        return True
    dropped = committed - set(out['dates'])
    if dropped:
        flag(f"series: rebuild ends {out['as_of']} but committed series records "
             f"{len(dropped)} later/intermediate bar(s) "
             f"({', '.join(sorted(dropped))}) — refusing to drop recorded "
             f"trading day(s) (yfinance latest-close flicker); keeping committed "
             f"series. Set FORCE_SERIES=1 to override for a deliberate rebuild.")
        return False
    return True


def build_daily_series(cfg: dict) -> dict | None:
    """Daily valuation series since inception, written to SERIES.

    Model values are DOLLARS (event-sourced walk: within each event period,
    value = cash + sum(alloc * price/price_at_event_start), missing-price
    names carried flat). Benchmarks are growth-of-1 from inception. The site
    exporter rescales both to the $10k notional base.
    """
    import pandas as pd

    inception = cfg['inception']
    inc_date = dt.date.fromisoformat(inception)

    def growth(t):
        s = _series(t, inception)
        if s is None:
            return None
        s = s[s.index.date >= inc_date]
        return None if s.empty else s / s.iloc[0]

    smh, qqq, spy = growth('SMH'), growth('QQQ'), growth('SPY')
    if smh is None or qqq is None or spy is None:
        flag('series: benchmark price data unavailable — series not built')
        return None
    idx = smh.index

    ew = ew_growth(cfg, idx)
    if ew is None:
        flag('series: no EW universe price data — series not built')
        return None

    model = pd.Series(0.0, index=idx)
    events = cfg['events']
    for i, ev in enumerate(events):
        start = dt.date.fromisoformat(ev['date'])
        end = (dt.date.fromisoformat(events[i + 1]['date'])
               if i + 1 < len(events) else None)
        mask = (idx.date >= start)
        if end is not None:
            mask &= (idx.date < end)
        if not mask.any():
            continue
        seg = pd.Series(float(ev.get('cash', 0)), index=idx[mask])
        for t, alloc in ev['allocations'].items():
            s = _series(t, inception)
            sub = None if s is None else s[s.index.date >= start]
            if sub is None or sub.empty:
                seg += alloc            # carried flat (no price data)
                continue
            seg += alloc * (sub.reindex(idx[mask]).ffill()
                            / sub.iloc[0]).fillna(1.0)
        model[idx[mask]] = seg

    # v2 shadows (spec A4/C1): EW_ROSTER = the sizing-null twin of the model's
    # own event history; BAND_* = forward-only rank-band scouts from
    # cfg['shadow_events'] (maintained by refresh_targets). NaN before a
    # shadow's first event (pre-deploy) becomes JSON null — never backfilled.
    shadows = {}
    ew_roster = chain_linked_growth(model_roster_events(cfg), inception, idx)
    if ew_roster is not None:
        shadows['EW_ROSTER'] = ew_roster
    for name, evs in (cfg.get('shadow_events') or {}).items():
        s = chain_linked_growth(evs, inception, idx)
        if s is not None:
            shadows[name] = s

    def pad(series):
        return [None if v != v else round(float(v), 6) for v in series]

    out = {
        'start': inception,
        'as_of': str(idx[-1].date()),
        'dates': [str(d.date()) for d in idx],
        'model': [round(float(v), 2) for v in model],
        'bench': {
            'SMH': [round(float(v), 6) for v in smh.reindex(idx).ffill()],
            'QQQ': [round(float(v), 6) for v in qqq.reindex(idx).ffill()],
            'SPY': [round(float(v), 6) for v in spy.reindex(idx).ffill()],
            'EW': [round(float(v), 6) for v in ew],
            **{name: pad(s) for name, s in shadows.items()},
        },
    }
    strict = [out['model']] + [out['bench'][k]
                               for k in ('SMH', 'QQQ', 'SPY', 'EW')]
    if any(v != v for series in strict for v in series):
        flag('series: NaN in output — series not written')
        return None
    if not _may_overwrite_series(out):
        return None
    SERIES.write_text(json.dumps(out) + '\n')
    return out
