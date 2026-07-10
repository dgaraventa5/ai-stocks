# Factor analysis — model portfolio return series

Window: 2026-05-26 → 2026-07-10 (32 sessions, n=31 daily returns). **Caveat: n=31 is a short sample — betas/alphas below carry wide error bars; treat as descriptive, not predictive.**

## Series overview

| Series | Cum. return | Ann. vol | Max drawdown | Best day | Worst day |
|---|---|---|---|---|---|
| Model | +6.14% | 46.0% | -8.71% | +5.04% | -6.22% |
| SMH | +1.48% | 61.5% | -13.08% | +6.75% | -9.22% |
| QQQ | -0.54% | 29.2% | -7.03% | +3.38% | -4.80% |
| SPY | +0.84% | 15.3% | -4.49% | +1.76% | -2.58% |
| EW | +5.16% | 42.1% | -9.22% | +4.63% | -6.56% |

## Model vs each benchmark (daily-return regression)

| Benchmark | Corr | Beta (±se) | Ann. alpha | R² | Tracking err (ann.) | Info ratio (ann.) | Up capture | Down capture |
|---|---|---|---|---|---|---|---|---|
| SMH | 0.89 | 0.67 (±0.06) | +46.82% | 0.80 | 29.1% | 0.97 | 0.67 | 0.68 |
| QQQ | 0.92 | 1.46 (±0.11) | +80.68% | 0.85 | 22.1% | 2.68 | 1.93 | 1.39 |
| SPY | 0.81 | 2.44 (±0.33) | +48.33% | 0.65 | 34.9% | 1.46 | 3.52 | 2.54 |
| EW | 0.95 | 1.04 (±0.06) | +7.27% | 0.91 | 13.8% | 0.67 | 1.09 | 1.05 |

## Weighting skill: Model vs Equal-weight universe

Both legs hold the same score>=70 universe, so this spread is the
cleanest read on what score-weighting adds over naive 1/N.

- Cumulative spread (Model − EW): **+0.98%**
- Daily hit rate (Model beats EW): 18/31 (58%)
- Mean daily spread: +0.04%; ann. spread vol: 13.8%
- Best spread day: 2026-07-08 (+1.59%); worst: 2026-06-26 (-1.61%)

## Benchmark cross-correlations (daily returns)

| | Model | SMH | QQQ | SPY | EW |
|---|---|---|---|---|---|
| Model | 1.00 | 0.89 | 0.92 | 0.81 | 0.95 |
| SMH | 0.89 | 1.00 | 0.94 | 0.77 | 0.94 |
| QQQ | 0.92 | 0.94 | 1.00 | 0.92 | 0.96 |
| SPY | 0.81 | 0.77 | 0.92 | 1.00 | 0.85 |
| EW | 0.95 | 0.94 | 0.96 | 0.85 | 1.00 |
