"""Data check on a model-event ticket (rule 37, 2026-11-01).

Model-event tickets trade at the next 06:35 run. A buy this flags is left off
the ticket for Dom to look at; the sells and the other buys still go. It looks
for the failures of 2026-10-30: a blank EPS cell, a one-off inside EPS YoY, a
score that jumped, and a buy into a name that just fell hard. A lookup that
fails counts as a flag, because "could not check" must never read as "clean".

It never changes a score, a rank or a weight.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / '00-master/ai_supply_chain_scoring.xlsx'
OVERRIDES = ROOT / '00-master/eps-yoy-overrides.json'
SCORE_HISTORY = ROOT / 'tracking/score-history.csv'

COL_REV_YOY, COL_EPS_YOY = 17, 18                   # Watchlist, 1-based
# EPS YoY this large on revenue growth this small reads as a one-off (rule 15)
# and needs a ruling for the current quarter. META on 2026-10-29: +265% on
# revenue about +25%. Real growers like NVDA pass because revenue moved too.
EPS_YOY_RULING_PCT = 100.0
REV_YOY_BACKS_EPS_PCT = 30.0
SCORE_JUMP_PTS = 5.0         # about the 99.5th percentile of panel moves
SCORE_JUMP_DAYS = 7
BUY_DROP_PCT = 15.0
BUY_DROP_BARS = 5


def read_watchlist(xlsx=XLSX) -> dict:
    import openpyxl
    ws = openpyxl.load_workbook(xlsx, data_only=True, read_only=True)['Watchlist']
    out = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:
            out[str(row[0]).strip()] = {'rev_yoy': row[COL_REV_YOY - 1],
                                        'eps_yoy': row[COL_EPS_YOY - 1]}
    return out


def read_overrides(path=OVERRIDES) -> dict:
    return {t: e for t, e in json.loads(Path(path).read_text()).items()
            if not t.startswith('_')}


def score_jumps(rows, tickers, today: dt.date) -> dict:
    """{ticker: (points, days)} for moves of SCORE_JUMP_PTS or more between
    the panel's latest score and its lowest or highest in the window."""
    start = (today - dt.timedelta(days=SCORE_JUMP_DAYS)).isoformat()
    series: dict = {}
    for r in rows:
        if r['ticker'] in tickers and start <= r['date'] <= today.isoformat():
            series.setdefault(r['ticker'], []).append(
                (r['date'], float(r['total_score'])))
    out = {}
    for t, pts in series.items():
        pts.sort()
        last = pts[-1][1]
        worst = max((p[1] for p in pts), key=lambda s: abs(last - s))
        if abs(last - worst) >= SCORE_JUMP_PTS:
            out[t] = round(last - worst, 1)
    return out


def needs_ruling(row: dict) -> bool:
    eps, rev = row['eps_yoy'], row['rev_yoy']
    if eps is None:
        return True
    return abs(float(eps)) >= EPS_YOY_RULING_PCT and (
        rev is None or float(rev) < REV_YOY_BACKS_EPS_PCT)


def _ruling_current(entry, quarter) -> bool:
    return bool(entry) and quarter is not None and (
        entry.get('quarter_end') == quarter.isoformat())


def flagged_buys(buys, watchlist, overrides, jumps, quarters, drops) -> dict:
    """Pure. {ticker: [reasons]}. quarters: {ticker: date|None}; drops:
    {ticker: pct|None}."""
    out = {}
    for t in buys:
        why = []
        row = watchlist.get(t)
        if row is None:
            out[t] = ['not on the Watchlist']
            continue
        if row['rev_yoy'] is None:
            why.append('revenue growth is blank')
        if needs_ruling(row):
            eps = row['eps_yoy']
            if quarters.get(t) is None:
                why.append('could not look up the latest reported quarter')
            elif not _ruling_current(overrides.get(t), quarters[t]):
                shown = 'blank' if eps is None else f'{float(eps):+.0f}%'
                why.append(f'EPS YoY is {shown} with no ruling for this quarter')
        if t in jumps:
            why.append(f'score moved {jumps[t]:+.1f} pts in {SCORE_JUMP_DAYS} days')
        drop = drops.get(t)
        if drop is None:
            why.append('could not look up recent prices')
        elif drop <= -BUY_DROP_PCT:
            why.append(f'fell {abs(drop):.0f}% in {BUY_DROP_BARS} sessions')
        if why:
            out[t] = why
    return out


def _latest_quarter(ticker):
    import yfinance as yf                                # lazy (CI minimal-env)
    from refresh_objective_inputs import _most_recent_quarter
    return _most_recent_quarter(yf.Ticker(ticker).info)


def _recent_drop(ticker):
    import yfinance as yf                                # lazy (CI minimal-env)
    closes = yf.Ticker(ticker).history(period='10d')['Close'].dropna().tail(BUY_DROP_BARS + 1)
    if len(closes) < 2:
        return None
    return (float(closes.iloc[-1]) / float(closes.max()) - 1) * 100


def _lookup(fn, ticker):
    try:
        return fn(ticker)
    except Exception:
        return None


def check_buys(orders: list[dict], today: dt.date | None = None) -> dict:
    """{ticker: [reasons]} for the buys on these orders that must not trade."""
    import csv
    today = today or dt.date.today()
    buys = sorted({o['ticker'] for o in orders if o['side'] == 'buy'})
    with open(SCORE_HISTORY, newline='') as f:
        jumps = score_jumps(csv.DictReader(f), set(buys), today)
    watchlist = read_watchlist()
    quarters = {t: _lookup(_latest_quarter, t) for t in buys
                if t in watchlist and needs_ruling(watchlist[t])}
    drops = {t: _lookup(_recent_drop, t) for t in buys}
    return flagged_buys(buys, watchlist, read_overrides(), jumps, quarters, drops)
