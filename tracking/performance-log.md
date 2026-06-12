# Portfolio performance log

Appended by `scripts/track_performance.py`. Model = the portfolio of record
(event-sourced, see performance-config.json). Returns are dividend-adjusted
(~total return), ex-fees/taxes/slippage.

Two lenses per mark:
- **Since inception (2026-05-26)** — the strategy's paper track record. The
  comparison that matters long-run is Model vs Equal-weight universe (isolates
  what score-weighting adds). This return is PAPER, not realized P&L.
- **Since latest rebalance** — the current portfolio measured from its own
  start. This is the like-for-like baseline for a real-money entry made at the
  latest rebalance, and the clean way to read each reconfiguration's effect.

(Intra-session marks from the 2026-06-09/10 build-out were consolidated; weekly
marks accumulate one block per run from here.)

## 2026-06-10

Model: **$13,386** (-3.00% since 2026-05-26) — 16 positions, last rebalance 2026-06-10 (membership change: -AR, -CRM, -EXE, -RRC)

**Since inception (2026-05-26) — strategy paper record:**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | -4.81% | +1.81% |
| QQQ | -4.63% | +1.63% |
| Equal-weight universe (35 names) | -2.62% | -0.37% |

**Since latest rebalance (2026-06-10) — current portfolio from its own start (= a real-money entry baseline):**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | +0.00% | +0.00% |
| QQQ | +0.00% | +0.00% |
| Equal-weight universe | +0.00% | +0.00% |
| **Model** | **+0.00%** | — |

- Top contributors since last rebalance: SNDK +0$, EME +0$, TSM +0$
- Bottom contributors since last rebalance: SNDK +0$, EME +0$, TSM +0$

## 2026-06-10

Model: **$13,386** (-3.00% since 2026-05-26) — 16 positions, last rebalance 2026-06-10 (membership change: -AR, -CRM, -EXE, -RRC)

**Since inception (2026-05-26) — strategy paper record:**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | -5.19% | +2.19% |
| QQQ | -5.01% | +2.01% |
| Equal-weight universe (35 names) | -3.28% | +0.29% |

**Since latest rebalance (2026-06-10) — current portfolio from its own start (= a real-money entry baseline):**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | +0.00% | +0.00% |
| QQQ | +0.00% | +0.00% |
| Equal-weight universe | +0.00% | +0.00% |
| **Model** | **+0.00%** | — |

- Top contributors since last rebalance: SNDK +0$, EME +0$, TSM +0$
- Bottom contributors since last rebalance: SNDK +0$, EME +0$, TSM +0$

## 2026-06-10

Model: **$13,386** (-3.00% since 2026-05-26) — 16 positions, last rebalance 2026-06-10 (membership change: -AR, -CRM, -EXE, -RRC)

**Since inception (2026-05-26) — strategy paper record:**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | -5.19% | +2.19% |
| QQQ | -5.01% | +2.01% |
| Equal-weight universe (35 names) | -3.28% | +0.29% |

**Since latest rebalance (2026-06-10) — current portfolio from its own start (= a real-money entry baseline):**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | +0.00% | +0.00% |
| QQQ | +0.00% | +0.00% |
| Equal-weight universe | +0.00% | +0.00% |
| **Model** | **+0.00%** | — |

- Top contributors since last rebalance: SNDK +0$, EME +0$, TSM +0$
- Bottom contributors since last rebalance: SNDK +0$, EME +0$, TSM +0$

## 2026-06-12

Model: **$14,285** (+3.52% since 2026-05-26) — 16 positions, last rebalance 2026-06-10 (membership change: -AR, -CRM, -EXE, -RRC)

**Since inception (2026-05-26) — strategy paper record:**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | +3.40% | +0.11% |
| QQQ | -0.96% | +4.47% |
| Equal-weight universe (35 names) | +3.22% | +0.30% |

**Since latest rebalance (2026-06-10) — current portfolio from its own start (= a real-money entry baseline):**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | +9.06% | -2.34% |
| QQQ | +4.27% | +2.45% |
| Equal-weight universe | +6.55% | +0.16% |
| **Model** | **+6.71%** | — |

- Top contributors since last rebalance: SNDK +203$, ALAB +120$, MU +117$
- Bottom contributors since last rebalance: MSFT -16$, EQT -5$, PLTR -1$

## 2026-06-12

Model: **$14,225** (+3.08% since 2026-05-26) — 16 positions, last rebalance 2026-06-10 (membership change: -AR, -CRM, -EXE, -RRC)

**Since inception (2026-05-26) — strategy paper record:**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | +3.39% | -0.32% |
| QQQ | -1.05% | +4.13% |
| Equal-weight universe (35 names) | +3.01% | +0.07% |

**Since latest rebalance (2026-06-10) — current portfolio from its own start (= a real-money entry baseline):**

| Benchmark | Return | Model alpha |
|---|---|---|
| SMH | +9.05% | -2.79% |
| QQQ | +4.17% | +2.10% |
| Equal-weight universe | +6.36% | -0.10% |
| **Model** | **+6.26%** | — |

- Top contributors since last rebalance: SNDK +213$, MU +114$, ALAB +102$
- Bottom contributors since last rebalance: MSFT -17$, PLTR -11$, EQT -9$

