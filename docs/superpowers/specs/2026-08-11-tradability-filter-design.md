# Tradability filter for portfolio selection — design

**Date:** 2026-08-11
**Status:** Approved by Dom 2026-08-11
**Problem:** 19 foreign-listed names (Tokyo/HK/Taiwan/Germany/Oslo/Brussels/ASX,
mostly the Layer-11 robotics build-out on local lines per rule 27) are ranked in
the same selection universe as US listings, but cannot be traded on Robinhood or
Fidelity. One is in the live model portfolio today — 6861.T (Keyence), rank 12,
8.61% target — a weight the execution pipeline can permanently never fill. More
foreign names float near the cutoff (6268.T at rank 28), so this recurs.

## Decisions (Dom, 2026-08-11)

1. **Scope:** foreign names stay on the Watchlist, fully scored — excluded from
   portfolio *selection* only. Removing them from the Watchlist would shift
   rule-20 cohort percentiles for the surviving Layer-11/semi names; keeping
   them scored but unselectable is the clean cut.
2. **Shadows:** BAND_TOP/NEXT/TAIL filter to tradable-only too. The bands exist
   to inform the ~2027-02 raise-N decision for the *real* portfolio; comparing
   against unbuyable names would contaminate that decision. Forward-only seam,
   normally-dated shadow event, prior days never rewritten.
3. **Definition of untradable:** deterministic — a ticker containing an
   exchange-suffix dot (`6861.T`, `KGX.DE`, `0981.HK`, …). No maintained list,
   no network dependency. All 19 current foreign names match; US listings never
   contain a dot.

## Design

### Config
`tracking/portfolio-config.json` → `selection.tradable_only: true`.
`portfolio_model.load_pcfg` defaults it to `false` when absent, so the flag is
a reversible switch and pre-change behavior is exactly reproducible (same
pattern as the v2 mode switches).

### Predicate
`portfolio_sizing.is_tradable(ticker)` — pure, unit-testable, no I/O:
`'.' not in ticker`. Lives in portfolio_sizing.py so the openpyxl-only deploy
CI can test it.

### Selection (refresh_targets.py)
When `tradable_only` is on, the `live` list is filtered to tradable names
before ranking (both rank mode and score mode), so:
- entry/exit ranks are computed over the buyable universe only;
- foreign names can never ENTER;
- a **currently-held untradable name exits immediately** via the same branch as
  dead/delisted names (status `EXIT (untradable)`), NOT the 2-run exit-confirm
  clock. Rationale: the clock guards against acting on score *noise*;
  tradability is a *constraint* and cannot mean-revert next refresh. Precedent:
  the CTRA delisted-name handling.

This fires one `membership` rebalance event (reason names the constraint)
exiting 6861.T; inverse-vol sizing renormalizes the freed 8.61% across the
remaining names under the 12%/3% cap/floor.

### Shadows
`_update_band_shadows` ranks the same filtered universe. The changed rosters
append a shadow event dated the day of the change — the seam is visible in
config history; nothing is backfilled or rewritten. EW_ROSTER needs no change:
it mirrors the model's own events and therefore self-filters.

### Deliberately unchanged
- Watchlist membership and all scoring (cohorts intact, rule 24 untouched).
- `tracking/score-history.csv` ranks stay full-universe (research panel, not
  the book).
- The friend-facing site.
- Executor/ticket path: the real account holds 0 shares of 6861.T, so the exit
  event produces no sell; share deltas still come from recon actuals (rule 29).
- Sizing Rules sheet params (N=15 / M=18) — ranks just run over fewer names.

### Verified ripple (live ranks, 2026-08-11)
With 6861.T filtered, everyone below shifts up one: META lands at rank 15
(already held → HOLD), AMZN at 16 (outside entry ≤ 15 → stays out). Portfolio
goes 16 → 15 names with no surprise entrants.

## Testing
- Unit: `is_tradable` on US/`.T`/`.DE`/`.HK`/`.TWO`/`.OL`/`.BR`/`.AX` forms.
- Selection: filtered ranking excludes suffixed tickers; held untradable name
  exits immediately (no pending clock entry); `tradable_only: false`
  reproduces prior behavior byte-for-byte on a fixture workbook.
- Shadows: band rosters contain no suffixed tickers when the flag is on.
- Existing gates untouched: rule-25 monotonicity, privacy, cohort drift.

## Non-goals
- No ADR-swap of foreign tickers (rule 19/27 chose local lines for data
  quality; that stands).
- No Robinhood tradability API dependency in refresh_targets (stays offline).
- No Watchlist column, site change, or scoring change.
