"""Factor / risk-statistics analysis of the model-portfolio return series.

Reads tracking/performance-series.json (written by track_performance.py) and
computes, from daily returns:

  per series   cumulative return, annualized vol, max drawdown, best/worst day
  vs benchmark correlation, OLS beta (with std error), annualized alpha, R^2,
               tracking error, information ratio, up/down capture
  model vs EW  the weighting-skill lens: daily spread stats + hit rate — both
               legs hold the same score>=70 universe, so the spread isolates
               what score-weighting adds over naive equal weighting.

Entirely offline (no yfinance) — it only re-reads the committed series.
Statistical honesty: with ~30 trading days the estimates are NOISY; the report
prints n and beta standard errors so nobody over-reads them.

Usage:
  python3 scripts/analyze_factors.py                 # print report
  python3 scripts/analyze_factors.py --out           # also write
                                                     # tracking/factor-analysis-{as_of}.md
"""
from __future__ import annotations

import argparse
import json
import math

from common import ROOT

SERIES = ROOT / 'tracking' / 'performance-series.json'
TRADING_DAYS = 252


def daily_returns(levels: list[float]) -> list[float]:
    return [levels[i] / levels[i - 1] - 1 for i in range(1, len(levels))]


def ann_vol(rets: list[float]) -> float:
    mu = sum(rets) / len(rets)
    var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * math.sqrt(TRADING_DAYS)


def max_drawdown(levels: list[float]) -> float:
    peak, mdd = levels[0], 0.0
    for v in levels:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    return mdd


def ols(y: list[float], x: list[float]) -> dict:
    """OLS y = a + b*x. Returns beta, its std error, daily alpha, R^2, corr."""
    n = len(y)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    syy = sum((yi - my) ** 2 for yi in y)
    beta = sxy / sxx
    alpha = my - beta * mx
    resid_ss = sum((yi - (alpha + beta * xi)) ** 2 for xi, yi in zip(x, y))
    r2 = 1 - resid_ss / syy if syy else 0.0
    beta_se = math.sqrt((resid_ss / (n - 2)) / sxx) if n > 2 else float('nan')
    corr = sxy / math.sqrt(sxx * syy) if sxx and syy else 0.0
    return {'beta': beta, 'beta_se': beta_se, 'alpha_d': alpha, 'r2': r2,
            'corr': corr}


def capture(model: list[float], bench: list[float], up: bool) -> float | None:
    """Up/down capture: compounded model return over bench up (down) days,
    divided by the compounded bench return over the same days."""
    pairs = [(m, b) for m, b in zip(model, bench) if (b > 0) == up and b != 0]
    if not pairs:
        return None
    gm = math.prod(1 + m for m, _ in pairs) - 1
    gb = math.prod(1 + b for _, b in pairs) - 1
    return gm / gb if gb else None


def analyze(data: dict) -> str:
    dates = data['dates']
    model_lv = [v / data['model'][0] for v in data['model']]  # -> multiplier
    bench_lv = data['bench']  # already growth multipliers
    m_ret = daily_returns(model_lv)
    n = len(m_ret)

    pct = lambda v: '—' if v is None else f'{v:+.2%}'
    num = lambda v: '—' if v is None else f'{v:.2f}'

    lines = [
        f'# Factor analysis — model portfolio return series',
        '',
        f'Window: {data["start"]} → {data["as_of"]} '
        f'({len(dates)} sessions, n={n} daily returns). '
        f'**Caveat: n={n} is a short sample — betas/alphas below carry wide '
        f'error bars; treat as descriptive, not predictive.**',
        '',
        '## Series overview',
        '',
        '| Series | Cum. return | Ann. vol | Max drawdown | Best day | Worst day |',
        '|---|---|---|---|---|---|',
    ]

    series = {'Model': (model_lv, m_ret)}
    for k, lv in bench_lv.items():
        series[k] = (lv, daily_returns(lv))
    for name, (lv, rets) in series.items():
        lines.append(
            f'| {name} | {pct(lv[-1] - 1)} | {ann_vol(rets):.1%} | '
            f'{max_drawdown(lv):.2%} | {pct(max(rets))} | {pct(min(rets))} |')

    lines += [
        '',
        '## Model vs each benchmark (daily-return regression)',
        '',
        '| Benchmark | Corr | Beta (±se) | Ann. alpha | R² | '
        'Tracking err (ann.) | Info ratio (ann.) | Up capture | Down capture |',
        '|---|---|---|---|---|---|---|---|---|',
    ]
    for k, (_, b_ret) in series.items():
        if k == 'Model':
            continue
        reg = ols(m_ret, b_ret)
        active = [m - b for m, b in zip(m_ret, b_ret)]
        te = ann_vol(active)
        ir = (sum(active) / n * TRADING_DAYS) / te if te else None
        ann_alpha = (1 + reg['alpha_d']) ** TRADING_DAYS - 1
        lines.append(
            f'| {k} | {reg["corr"]:.2f} | {reg["beta"]:.2f} '
            f'(±{reg["beta_se"]:.2f}) | {pct(ann_alpha)} | {reg["r2"]:.2f} | '
            f'{te:.1%} | {num(ir)} | {num(capture(m_ret, b_ret, True))} | '
            f'{num(capture(m_ret, b_ret, False))} |')

    if 'EW' in bench_lv:
        ew_ret = series['EW'][1]
        spread = [m - e for m, e in zip(m_ret, ew_ret)]
        hit = sum(1 for s in spread if s > 0)
        cum_spread = (model_lv[-1] - 1) - (bench_lv['EW'][-1] - 1)
        worst_i = min(range(n), key=lambda i: spread[i])
        best_i = max(range(n), key=lambda i: spread[i])
        lines += [
            '',
            '## Weighting skill: Model vs Equal-weight universe',
            '',
            'Both legs hold the same score>=70 universe, so this spread is the',
            'cleanest read on what score-weighting adds over naive 1/N.',
            '',
            f'- Cumulative spread (Model − EW): **{pct(cum_spread)}**',
            f'- Daily hit rate (Model beats EW): {hit}/{n} ({hit / n:.0%})',
            f'- Mean daily spread: {pct(sum(spread) / n)}; '
            f'ann. spread vol: {ann_vol(spread):.1%}',
            f'- Best spread day: {dates[best_i + 1]} ({pct(spread[best_i])}); '
            f'worst: {dates[worst_i + 1]} ({pct(spread[worst_i])})',
        ]

    lines += [
        '',
        '## Benchmark cross-correlations (daily returns)',
        '',
    ]
    names = list(series)
    lines.append('| | ' + ' | '.join(names) + ' |')
    lines.append('|---|' + '---|' * len(names))
    for a in names:
        row = [a]
        for b in names:
            row.append(f'{ols(series[a][1], series[b][1])["corr"]:.2f}')
        lines.append('| ' + ' | '.join(row) + ' |')

    return '\n'.join(lines) + '\n'


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', action='store_true',
                    help='also write tracking/factor-analysis-{as_of}.md')
    args = ap.parse_args()

    data = json.loads(SERIES.read_text())
    report = analyze(data)
    print(report)
    if args.out:
        out = ROOT / 'tracking' / f'factor-analysis-{data["as_of"]}.md'
        out.write_text(report)
        print(f'wrote {out}')


if __name__ == '__main__':
    main()
