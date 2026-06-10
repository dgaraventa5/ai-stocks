"""Regenerate portfolio.xlsx Targets + Reconciliation from live Watchlist scores.

This is the score→portfolio pipeline step that was missing: the Targets sheet
was hand-built 2026-05-18/25 and froze while live scores moved (the portfolio
README referenced this script before it existed). Built 2026-06-09.

Pipeline rules (parameters live on the Sizing Rules sheet — edit there):
  - Hysteresis: non-holdings ENTER at rank <= entry_rank; holdings HOLD until
    rank > exit_rank OR score < 70 (tier drop below ✓✓), and an exit must be
    confirmed on 2 consecutive runs (EXIT PENDING -> EXIT) so a single noisy
    refresh can't trade the portfolio. Entrants admitted in rank order only
    while position count < max_positions.
  - Freshness gate: candidates whose last yfinance trade is >7 days old are
    treated as dead (halted/delisted), excluded, and flagged — a delisted
    name (CTRA, 2026-05) once sat in the live top-20 on frozen data.
  - Manual overrides: Targets rows whose Override col says EXCLUDE stay out
    regardless of rank (kept across refreshes, flagged when their rank would
    otherwise include them). Set INCLUDE to force a name in.
  - Sizing: tier-band linear interpolation on score (Sizing Rules table),
    normalized to (1 - cash buffer), then max-single-position cap, then layer
    cap (default 1.0 = off, per Dom's pure-score-driven preference — layer
    exposure is reported every run so that choice stays visible).

Per CLAUDE.md rule 5: the Reconciliation sheet is a mechanical target-vs-
current diff, not a trade recommendation. Decisions are Dom's.

Usage:
  python3 scripts/refresh_targets.py            # refresh + write
  python3 scripts/refresh_targets.py --dry-run  # print plan, write nothing
"""
from __future__ import annotations

import argparse
import datetime as dt
import time
from copy import copy

import yfinance as yf
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

from common import flag
from portfolio_model import load_cfg, log_rebalance
from recalc_watchlist import recalc

PORTFOLIO = '/Users/dom/Desktop/ai-stocks/00-master/portfolio.xlsx'

HEADER_FILL = PatternFill('solid', fgColor='1F4E78')
HEADER_FONT = Font(bold=True, color='FFFFFF')

# Defaults for parameters added 2026-06-09; written to Sizing Rules if absent
# so they are visible and editable in the workbook, not buried here.
NEW_PARAMS = [
    # Membership is SCORE-threshold-anchored (2026-06-10, Dom): hold the genuine
    # ✓✓ cluster, let the count flex with scores rather than fix it. Hysteresis
    # band entry>=74.5 / exit<73.0 yields ~15 names today. (Rank params retained
    # below only as an inert backstop / historical reference.)
    ('Entry score', 74.5, 'Non-holding ENTERs when score >= this'),
    ('Exit score', 73.0, 'Holding EXITs when score < this (2-run confirm, or immediate on --resize)'),
    ('Exit confirm runs', 2, 'Consecutive refreshes below exit score before EXIT'),
    ('Max positions', 20, 'Hard ceiling backstop; threshold normally binds first'),
    ('Max stale price days', 7, 'Last trade older than this = dead, excluded'),
    ('Layer cap %', 1.0, 'Max weight per layer. 1.0 = off (Dom 2026-06-10: caps '
                         'manage label- not factor-concentration; use single-name '
                         'cap + capex tripwire instead).'),
    ('Entry rank', 15, '(inert) legacy rank backstop'),
    ('Exit rank', 25, '(inert) legacy rank backstop'),
]


def load_params(ws) -> dict:
    """Read scalar params + tier band table from the Sizing Rules sheet."""
    params, tiers = {}, {}
    rows = list(ws.iter_rows(values_only=True))
    for i, row in enumerate(rows):
        if row[0] in ('Cash buffer %', 'Max single position %',
                      'Target position count', 'Portfolio Value ($)',
                      'Entry score', 'Exit score',
                      'Entry rank', 'Exit rank', 'Exit confirm runs',
                      'Max positions', 'Max stale price days', 'Layer cap %'):
            params[row[0]] = row[1]
        if row[0] == 'Tier' and row[1] == 'Score Floor':
            for trow in rows[i + 1:]:
                if trow[0] in ('✓✓✓', '✓✓', '✓', '?', '✗'):
                    tiers[trow[0]] = dict(floor=trow[1], w_floor=trow[2],
                                          w_ceil=trow[3], ceil=trow[4])
    return params | {'tiers': tiers}


def ensure_params(ws) -> None:
    """Append any missing pipeline params to Sizing Rules (idempotent)."""
    present = {row[0].value for row in ws.iter_rows()}
    for name, default, note in NEW_PARAMS:
        if name not in present:
            ws.append([name, default, note + ' (added 2026-06-09)'])


def base_weight(score: float, tiers: dict) -> float:
    """Linear interpolation of weight within the score's tier band."""
    for t in tiers.values():
        if t['floor'] <= score <= t['ceil']:
            span = t['ceil'] - t['floor']
            frac = (score - t['floor']) / span if span else 0
            return t['w_floor'] + frac * (t['w_ceil'] - t['w_floor'])
    return 0.0


def cap_and_normalize(weights: dict[str, float], layers: dict[str, str],
                      budget: float, max_single: float,
                      layer_cap: float) -> dict[str, float]:
    """Scale to budget, then iteratively enforce single + layer caps."""
    w = dict(weights)
    for _ in range(20):
        total = sum(w.values())
        if not total:
            return w
        w = {t: v / total * budget for t, v in w.items()}
        over = {t: max_single for t, v in w.items() if v > max_single + 1e-9}
        # Layer cap: shave members of an over-cap layer proportionally.
        by_layer: dict[str, float] = {}
        for t, v in w.items():
            by_layer[layers[t]] = by_layer.get(layers[t], 0) + v
        for lay, lv in by_layer.items():
            if lv > layer_cap * budget + 1e-9:
                scale = layer_cap * budget / lv
                for t in w:
                    if layers[t] == lay:
                        over[t] = min(over.get(t, w[t]), w[t] * scale)
        if not over:
            return w
        # Freeze capped names, renormalize the rest into the leftover budget.
        fixed = sum(over.values())
        rest = {t: v for t, v in w.items() if t not in over}
        rest_total = sum(rest.values())
        if not rest_total:
            return over
        w = over | {t: v / rest_total * (budget - fixed) for t, v in rest.items()}
    return w


def last_trade_age_days(ticker: str) -> int | None:
    hist = yf.Ticker(ticker).history(period='1mo', auto_adjust=True)
    if hist is None or hist.empty:
        return None
    return (dt.date.today() - hist.index[-1].date()).days


def current_price(ticker: str) -> float | None:
    hist = yf.Ticker(ticker).history(period='5d', auto_adjust=False)
    if hist is None or hist.empty:
        return None
    return round(float(hist['Close'].iloc[-1]), 2)


def refresh(dry_run: bool = False, resize: bool = False) -> None:
    today = dt.date.today().isoformat()
    wb = load_workbook(PORTFOLIO, data_only=False)
    sizing, targets, recon = wb['Sizing Rules'], wb['Targets'], wb['Reconciliation']
    positions = wb['Positions']

    ensure_params(sizing)
    p = load_params(sizing)
    # Score-threshold membership (2026-06-10). resize=True drops below-exit names
    # immediately (intentional re-sizing), bypassing the 2-run exit hysteresis.
    entry_score = float(p.get('Entry score', 74.5))
    exit_score = float(p.get('Exit score', 73.0))
    confirm_runs = int(p.get('Exit confirm runs', 2))
    max_positions = int(p.get('Max positions', 20))
    stale_days = int(p.get('Max stale price days', 7))
    layer_cap = float(p.get('Layer cap %', 1.0))
    max_single = float(p['Max single position %'])
    cash = float(p['Cash buffer %'])
    capital = float(p['Portfolio Value ($)'])

    # ---- prior state from existing Targets sheet ----
    hdr = [c.value for c in targets[2]]
    col = {name: i for i, name in enumerate(hdr)}
    prior_include: set[str] = set()
    overrides: dict[str, str] = {}
    exit_pending: dict[str, str] = {}   # ticker -> 'since' date
    notes: dict[str, str] = {}
    for row in targets.iter_rows(min_row=3, values_only=True):
        tkr = row[0]
        if not tkr or tkr == 'TOTAL':
            continue
        if row[col.get('Include?', 5)] == 'Y':
            prior_include.add(tkr)
        note = str(row[col.get('Notes', 8)] or '')
        if note:
            notes[tkr] = note
        ov = str(row[col['Override']] or '') if 'Override' in col else ''
        # Migration: the pre-2026-06-09 sheet encoded manual excludes in Notes.
        # Only applies when the Override column doesn't exist yet — once it
        # does, a blank Override means "no override", even if historical note
        # text ('Manually excluded ...') is retained for the audit trail.
        if 'Override' not in col and ('Manually excluded' in note
                                      or 'DELISTED' in note
                                      or 'investability override' in note):
            ov = 'EXCLUDE'
        if ov:
            overrides[tkr] = ov
        st = str(row[col['Status']] or '') if 'Status' in col else ''
        if st.startswith('EXIT PENDING'):
            exit_pending[tkr] = st.split('since ')[-1].rstrip(')')

    # ---- live scores ----
    live = [x for x in recalc() if x['TOTAL'] is not None]
    live.sort(key=lambda x: -x['TOTAL'])
    rank = {x['ticker']: i + 1 for i, x in enumerate(live)}
    info = {x['ticker']: x for x in live}
    layers = {x['ticker']: (x['layer'] or '')[:2] for x in live}

    # ---- freshness gate on every name that could end up included ----
    candidates = sorted(
        {t for t in info if info[t]['TOTAL'] >= exit_score} | prior_include
        | {t for t, v in overrides.items() if v == 'INCLUDE'})
    dead: set[str] = set()
    for t in candidates:
        age = last_trade_age_days(t)
        time.sleep(0.25)
        if age is None or age > stale_days:
            dead.add(t)
            flag(f'{t}: last trade {"none" if age is None else f"{age}d ago"} '
                 f'— excluded as halted/delisted')

    # ---- membership: hysteresis ----
    include: list[str] = []
    statuses: dict[str, str] = {}
    for t in prior_include:
        if t in dead or overrides.get(t) == 'EXCLUDE':
            statuses[t] = 'EXIT (dead/override)'
            continue
        keep = t in info and info[t]['TOTAL'] >= exit_score
        if keep:
            include.append(t)
            statuses[t] = 'HOLD'
        elif resize:
            # Intentional re-sizing: drop below-threshold names immediately.
            statuses[t] = f'EXIT (resize, score {info[t]["TOTAL"]:.1f} < {exit_score})'
            flag(f'{t}: EXIT (resize — score {info[t]["TOTAL"]:.1f} < exit {exit_score})')
        elif t in exit_pending and exit_pending[t] != today:
            # EXIT PENDING on a PRIOR refresh date → confirmed now. Same-day
            # re-runs don't count as the second look — the confirm exists to
            # require two independent data points, not two script invocations.
            statuses[t] = f'EXIT (pending since {exit_pending[t]}, confirmed)'
            flag(f'{t}: exit confirmed (score {info[t]["TOTAL"]:.1f}, '
                 f'pending since {exit_pending[t]})')
        else:
            include.append(t)   # still held while pending
            statuses[t] = f'EXIT PENDING (score {info[t]["TOTAL"]:.1f}, since {today})'
            flag(f'{t}: below exit score ({info[t]["TOTAL"]:.1f} < {exit_score}) — '
                 f'EXIT PENDING, confirms next refresh')
    for x in live:
        t = x['ticker']
        if t in include or t in statuses or t in dead:
            continue
        if overrides.get(t) == 'EXCLUDE':
            if x['TOTAL'] >= entry_score:
                flag(f'{t}: score {x["TOTAL"]:.1f} would enter but Override=EXCLUDE '
                     f'({notes.get(t, "no note")[:80]})')
            continue
        forced = overrides.get(t) == 'INCLUDE'
        if x['TOTAL'] >= entry_score or forced:
            if len(include) < max_positions:
                include.append(t)
                statuses[t] = ('ENTER (forced)' if forced
                               else f'ENTER (score {x["TOTAL"]:.1f})')
                flag(f'{t}: ENTER (score {x["TOTAL"]:.1f} >= entry {entry_score})')
            else:
                statuses[t] = f'BLOCKED (score {x["TOTAL"]:.1f}, max positions full)'
                flag(f'{t}: score {x["TOTAL"]:.1f} qualifies but max positions '
                     f'({max_positions}) full')

    # ---- sizing ----
    base = {t: base_weight(info[t]['TOTAL'], p['tiers']) for t in include}
    weights = cap_and_normalize(base, layers, 1.0 - cash, max_single, layer_cap)

    by_layer: dict[str, float] = {}
    for t, v in weights.items():
        by_layer[layers[t]] = by_layer.get(layers[t], 0) + v
    for lay, v in sorted(by_layer.items(), key=lambda kv: -kv[1]):
        if v > 0.25:
            flag(f'layer {lay}: {v:.0%} of portfolio (no layer cap active)')

    # ---- prices for the trade plan ----
    prices: dict[str, float] = {}
    for t in include:
        prices[t] = current_price(t)
        time.sleep(0.25)
        if prices[t] is None:
            flag(f'{t}: no current price — Reconciliation row left without shares')

    if dry_run:
        print(f'\n{"Tkr":<7}{"Rank":>5}{"Score":>7}{"Status":<34}{"Wt %":>6}')
        for t in sorted(include, key=lambda t: -weights.get(t, 0)):
            print(f'{t:<7}{rank.get(t, 0):>5}{info[t]["TOTAL"]:>7.1f}'
                  f'{statuses.get(t, ""):<34}{weights.get(t, 0) * 100:>6.1f}')
        print('(dry run — nothing written)')
        return

    # ---- rewrite Targets ----
    targets.delete_rows(1, targets.max_row)
    targets.append([f'Target Portfolio (refreshed {today}, live Watchlist scores)'])
    targets.append(['Ticker', 'Layer', 'TOTAL', 'Tier', 'Rank', 'Status',
                    'Include?', 'Override', 'Target %', 'Notes'])
    for c in targets[2]:
        c.fill, c.font = copy(HEADER_FILL), copy(HEADER_FONT)
    for x in live:
        t = x['ticker']
        if x['TOTAL'] < 55 and t not in include and t not in overrides:
            continue   # keep the sheet to ✓-and-better plus anything tracked
        targets.append([
            t, x['layer'], round(x['TOTAL'], 2), x['Tier'], rank[t],
            statuses.get(t, ''), 'Y' if t in include else 'N',
            overrides.get(t, ''), round(weights.get(t, 0) * 100, 2) or None,
            notes.get(t, ''),
        ])

    # ---- rewrite Reconciliation ----
    has_positions = any(positions.cell(row=r, column=1).value not in (None, 'TOTAL')
                        for r in range(2, positions.max_row + 1))
    recon.delete_rows(1, recon.max_row)
    mode = ('target vs current positions'
            if has_positions else 'fresh deployment — Positions sheet is empty')
    recon.append([f'Mechanical target diff ({mode}) — not a trade '
                  f'recommendation; decisions are Dom\'s (CLAUDE.md rule 5)'])
    recon.append([f'Portfolio: ${capital:,.0f} | Prices as of {today}'])
    recon.append(['Ticker', 'Score', 'Target %', '$ Amount', 'Price', 'Shares',
                  'Round $', 'Delta'])
    for c in recon[3]:
        c.fill, c.font = copy(HEADER_FILL), copy(HEADER_FONT)
    held = {}
    if has_positions:
        for r in range(2, positions.max_row + 1):
            t = positions.cell(row=r, column=1).value
            if t and t != 'TOTAL':
                held[t] = positions.cell(row=r, column=3).value or 0
    cap_row = next(r for r in range(1, sizing.max_row + 1)
                   if sizing.cell(row=r, column=1).value == 'Portfolio Value ($)')
    cap_cell = f"'Sizing Rules'!$B${cap_row}"
    for t in sorted(include, key=lambda t: -weights.get(t, 0)):
        r = recon.max_row + 1
        # Formulas, not pasted values (CLAUDE.md rule 4): editing Target % or
        # capital re-derives dollars and share counts. Fractional shares
        # (Dom decision 2026-06-09) — share price no longer constrains sizing.
        recon.append([
            t, round(info[t]['TOTAL'], 1), round(weights[t] * 100, 2),
            f'=C{r}/100*{cap_cell}', prices.get(t),
            f'=IF(E{r}="","",ROUND(D{r}/E{r},4))',
            f'=IF(E{r}="","",F{r}*E{r})',
            (f'={held.get(t, 0)}-F{r}' if has_positions else 'NEW'),
        ])
    r = recon.max_row + 1
    recon.append(['TOTAL', None, f'=SUM(C4:C{r - 1})', f'=SUM(D4:D{r - 1})',
                  None, None, f'=SUM(G4:G{r - 1})', None])

    # ---- README breadcrumbs ----
    rm = wb['README']
    for row in rm.iter_rows():
        if row[0].value == 'Last built':
            row[1].value = f'{today} (refresh_targets.py — hysteresis pipeline)'

    wb.save(PORTFOLIO)
    print(f'wrote {len(include)} target positions to {PORTFOLIO}')

    # ---- roll the model forward when membership changed ----
    # The model is the portfolio of record (Dom decision 2026-06-09); a
    # membership change here = a rebalance event. Weight drift within the
    # same names does NOT rebalance — matches the hysteresis philosophy.
    cfg = load_cfg()
    prior_model = set(cfg['events'][-1]['allocations'])
    if set(include) != prior_model:
        entered = sorted(set(include) - prior_model)
        exited = sorted(prior_model - set(include))
        reason = ('membership change: '
                  + ', '.join(['+' + t for t in entered]
                              + ['-' + t for t in exited]))
        ev = log_rebalance(cfg, weights, reason)
        print(f'model rebalanced: {reason} — value at rebalance '
              f'${sum(ev["allocations"].values()) + ev["cash"]:,.0f}')
    else:
        print('model membership unchanged — no rebalance event logged')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Refresh portfolio targets from live scores')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--resize', action='store_true',
                    help='intentional re-sizing: drop below-exit-score names '
                         'immediately, bypassing the 2-run exit hysteresis')
    args = ap.parse_args()
    refresh(dry_run=args.dry_run, resize=args.resize)
