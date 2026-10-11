# Forward P/E on a common calendar year — DRAFT rule 36

**Status:** DRAFT for Dom's approval. Nothing here is implemented. Written 2026-10-10.

## Problem

The Fwd P/E input (Watchlist col 5) is yfinance `forwardPE`: price divided by the
consensus EPS for the company's **next fiscal year**. That is a different twelve
months for different companies.

- A December-year company in October 2026: "next fiscal year" is calendar 2027.
- Western Digital, whose fiscal year ended 2026-07-03: "next fiscal year" is the year
  ending mid-2028 — about six months further out.

When earnings are growing fast the later window holds much larger earnings, so the
P/E looks lower for no reason other than the fiscal calendar. WDC printed 13.1 on
its fiscal-2028 estimate ($31.83); on calendar 2027 it is 16.1. This surfaced in the
2026-10-10 WDC review, where the gap was worth 0.6 points and decided whether the
name entered the portfolio.

It is not a one-name quirk: **69 of 214 watchlist names (32%) do not have a December
year-end** (yfinance `nextFiscalYearEnd`, pulled 2026-10-10): Jan 13, Mar 12, Sep 10,
Jun 8, Jul 8, Oct 7, Nov 4, May 3, Feb 2, Apr 2.

## Proposed rule

**Every company's forward P/E uses consensus earnings for the same calendar year.**

1. **Target year T** = the fiscal year yfinance currently treats as "next" for
   December-year companies (2027 today). It rolls when they roll, so December names
   never change.
2. For an off-cycle company, take the two consensus figures yfinance provides —
   current fiscal year (`0y`) and next (`+1y`) — and weight each by the share of
   calendar year T it covers.
   - WDC: fiscal 2027 covers Jan 1–Jul 3 (50.4%), fiscal 2028 the rest (49.6%).
     0.504 × $20.12 + 0.496 × $31.83 = $25.93 → P/E 16.1.
3. **When part of year T falls after the last fiscal year yfinance covers**, use the
   later estimate for that part. This is the cautious direction when earnings are
   growing (the true figure would be higher still) and leaves names like AVGO
   (year ends early November) unchanged.
4. **The rule never lowers a P/E.** If the blended figure would be below the raw one,
   keep the raw one and flag it. One name tripped this in testing (PANW: the two
   consensus figures look like they are on different bases, 88.0 → 57.9), which is a
   data problem the rule should not reward.
5. Skip and flag when either estimate is missing or non-positive; the raw value stays.

PEG (Fwd P/E ÷ EPS growth) follows the cell, as it does today. No band changes: the
Methodology bands were calibrated on December-year names, which this rule does not
touch (rule 8 is respected — this changes an input's definition, not a threshold).

## Measured impact (parked draft workbook, 2026-10-10)

- 62 off-cycle names had both estimates; **41 P/Es rise**, 34 by more than 2%.
- Largest: LITE 31.1 → 38.4, WDC 13.1 → 16.1, STX 15.1 → 18.4, COHR 24.0 → 28.7,
  CRDO 23.2 → 26.2, ORCL 13.2 → 14.8, MU 5.1 → 5.7, SNDK 6.4 → 7.1.
- **Only 7 total scores move**, because the P/E bands are wide:

| Name | Fiscal year ends | P/E | Score | Tradable rank |
|---|---|---|---|---|
| COHR | Jun 30 | 24.0 → 28.7 | 61.21 → 60.46 | 95 → 101 |
| ZS | Jul 31 | 37.8 → 40.8 | 60.29 → 59.69 | 103 → 108 |
| WDC | Jul 3 | 13.1 → 16.1 | 73.41 → 72.81 | 14 → 17 |
| CRDO | May 2 | 23.2 → 26.2 | 81.47 → 80.97 | 4 → 5 |
| KLAC | Jun 30 | 30.2 → 33.4 | 67.25 → 66.75 | 46 → 49 |
| LRCX | Jun 28 | 28.8 → 31.9 | 67.66 → 67.16 | 42 → 46 |
| NXT | Mar 31 | 14.8 → 15.6 | 65.24 → 64.74 | 57 → 67 |

- **Portfolio effect:** one crossing. WDC drops from rank 14 (would enter) to 17
  (would not). No held name crosses rank 18.

Method: rule-24 style before/after on a temp copy of the workbook; P/Es scaled by
(`+1y` estimate ÷ blended estimate) so the 2026-10-06 prices are held constant.

## Implementation sketch (for after approval)

- `scripts/fiscal_calendar.py` (pure): `calendar_year_eps(eps_0y, eps_1y, fy_end, target_year)`.
- `batch_score.compute_inputs`: one extra yfinance read (`earnings_estimate`) for
  names whose `nextFiscalYearEnd` month is not December; target year derived once per
  run from a December-year reference.
- `refresh_objective_inputs.py`: print "calendar-year P/E applied / kept raw (reason)"
  in the judgment flags.
- Tests: December name unchanged; WDC worked example; missing-later-year fallback;
  never-lowers guard; missing estimates.
- Deploy is a methodology change: stamp a seam (rule 32-C) before `recalc --sync`.

## Not addressed here

- **Three-year growth measured from a cycle trough.** WDC's 27% a year starts from
  fiscal 2023, the bottom of the hard-drive cycle. Same family of problem (an input
  that is right but not comparable), harder to fix mechanically, and already noted as
  a known limitation of rule 21 for cyclical names. Left for a separate decision.
- **Foreign filers with no consensus on yfinance** keep the raw value (flagged).

## Proposed CLAUDE.md text (rule 36)

> ### 36. Forward P/E uses the same calendar year for every company (added YYYY-MM-DD, approved by Dom)
>
> yfinance `forwardPE` is price over next-fiscal-year EPS, which is a different twelve
> months for the 32% of names without a December year-end. On fast growers the later
> window flatters the multiple (WDC 13.1 on fiscal 2028 vs 16.1 on calendar 2027).
> **Rule:** off-cycle names blend their `0y` and `+1y` consensus EPS by the share of
> the target calendar year each covers; the target is whatever year December-year
> names are on. Any part of the year beyond `+1y` uses `+1y`. The rule never lowers a
> P/E (kept raw + flagged) and skips on missing or non-positive estimates. Bands are
> unchanged. Code: `scripts/fiscal_calendar.py`. Spec:
> `docs/superpowers/specs/2026-10-10-forward-pe-calendar-year-design.md`.
