"""Mark the model portfolio against benchmarks; append to the performance log.

The feedback loop for the score->portfolio pipeline (built 2026-06-09).
Answers the question the scoring system can't answer about itself: does
score-weighted buying beat (a) the sector, (b) the market, (c) naive
equal-weighting of the same universe?

  Model   the portfolio of record (Dom decision 2026-06-09): event-sourced in
          tracking/performance-config.json, rolled forward automatically by
          refresh_targets.py whenever membership changes. See
          portfolio_model.py for the standing execution assumption.
  SMH/QQQ ETF benchmarks from the 2026-05-26 inception.
  EW      equal-weight buy-and-hold of every score>=70 name in the 2026-05-25
          Targets snapshot (35 names, point-in-time, CTRA excluded). The
          honest comparison: if score-weighting doesn't beat this, the
          scoring precision isn't adding portfolio value.

Returns use dividend-adjusted closes (approximately total return), ex-fees/
taxes/slippage. Per CLAUDE.md: yfinance serialized; gaps flagged, not guessed.

Usage:
  python3 scripts/track_performance.py            # append to performance-log.md
  python3 scripts/track_performance.py --dry-run  # print only
"""
from __future__ import annotations

import argparse
import datetime as dt

from common import ROOT
from portfolio_model import build_daily_series, load_cfg, mark, ret_since

LOG = ROOT / 'tracking' / 'performance-log.md'


def main() -> None:
    ap = argparse.ArgumentParser(description='Mark model portfolio vs benchmarks')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--series-only', action='store_true',
                    help='rebuild tracking/performance-series.json and exit; '
                         'no log append (daily site-refresh path)')
    args = ap.parse_args()

    cfg = load_cfg()
    if args.series_only:
        build_daily_series(cfg)
        return
    inception, capital = cfg['inception'], cfg['capital']
    today = dt.date.today().isoformat()

    value, pnl, missing = mark(cfg)
    model_ret = value / capital - 1
    last_event = cfg['events'][-1]

    def bench(frm):
        """(smh, qqq, ew) returns measured from date `frm`."""
        ew = [r for t in cfg['ew_universe']
              if (r := ret_since(t, frm, inception)) is not None]
        return (ret_since('SMH', frm, inception),
                ret_since('QQQ', frm, inception),
                (sum(ew) / len(ew) if ew else None), len(ew))

    # Two lenses: since INCEPTION (strategy paper record) and since the LATEST
    # REBALANCE (how the current portfolio does from its own start — added
    # 2026-06-10 so each reconfiguration's effect can be read cleanly, and so a
    # real-money entry at the latest rebalance has a like-for-like baseline).
    smh, qqq, ew_ret, n_ew = bench(inception)
    reb_date = last_event['date']
    reb_value = sum(last_event['allocations'].values()) + last_event.get('cash', 0)
    model_reb_ret = value / reb_value - 1 if reb_value else None
    r_smh, r_qqq, r_ew, _ = bench(reb_date)

    top = sorted(pnl.items(), key=lambda kv: -kv[1])[:3]
    bot = sorted(pnl.items(), key=lambda kv: kv[1])[:3]

    def fmt(v):
        return '—' if v is None else f'{v:+.2%}'

    def alpha(m, b):
        return fmt(m - b) if (m is not None and b is not None) else '—'

    block = [
        f'## {today}',
        '',
        f'Model: **${value:,.0f}** ({fmt(model_ret)} since {inception}) — '
        f'{len(last_event["allocations"])} positions, last rebalance '
        f'{last_event["date"]} ({last_event["reason"]})',
        '',
        f'**Since inception ({inception}) — strategy paper record:**',
        '',
        '| Benchmark | Return | Model alpha |',
        '|---|---|---|',
        f'| SMH | {fmt(smh)} | {alpha(model_ret, smh)} |',
        f'| QQQ | {fmt(qqq)} | {alpha(model_ret, qqq)} |',
        f'| Equal-weight universe ({n_ew} names) | {fmt(ew_ret)} | '
        f'{alpha(model_ret, ew_ret)} |',
        '',
        f'**Since latest rebalance ({reb_date}) — current portfolio from its own '
        f'start (= a real-money entry baseline):**',
        '',
        '| Benchmark | Return | Model alpha |',
        '|---|---|---|',
        f'| SMH | {fmt(r_smh)} | {alpha(model_reb_ret, r_smh)} |',
        f'| QQQ | {fmt(r_qqq)} | {alpha(model_reb_ret, r_qqq)} |',
        f'| Equal-weight universe | {fmt(r_ew)} | {alpha(model_reb_ret, r_ew)} |',
        f'| **Model** | **{fmt(model_reb_ret)}** | — |',
        '',
        f'- Top contributors since last rebalance: '
        + ', '.join(f'{t} {v:+,.0f}$' for t, v in top),
        f'- Bottom contributors since last rebalance: '
        + ', '.join(f'{t} {v:+,.0f}$' for t, v in bot),
    ]
    if missing:
        block.append(f'- FLAG: carried at last event value (no price data): '
                     f'{", ".join(missing)}')
    text = '\n'.join(block) + '\n\n'

    print(text)
    if not args.dry_run:
        build_daily_series(cfg)
        if not LOG.exists():
            LOG.write_text(
                '# Portfolio performance log\n\n'
                'Appended by `scripts/track_performance.py`. Model = the '
                'portfolio of record (event-sourced, see performance-config'
                '.json). Returns are dividend-adjusted (~total return), '
                'ex-fees/taxes/slippage. The comparison that matters long-run '
                'is Model vs Equal-weight universe — that isolates what '
                'score-weighting adds.\n\n')
        with LOG.open('a') as f:
            f.write(text)
        print(f'appended to {LOG}')


if __name__ == '__main__':
    main()
