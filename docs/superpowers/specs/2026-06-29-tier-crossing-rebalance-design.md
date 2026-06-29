# Tier-crossing rebalance: make allocations track rescores

**Date:** 2026-06-29
**Status:** Approved (design + spec) — implementation pending
**Author:** Dom + Claude

## Problem

The Positions page shows MU (score 86.4, tier ✓✓✓) at a **7.4%** weight — *below* NVDA
(84.1, ✓✓) at 9.3%. A ✓✓✓ name sits below a ✓✓ name. That tier inversion is
impossible under the live sizing methodology, so the displayed weight is stale.

### Root cause

The site reads its `weight` from the `Target %` column of the `Targets` sheet in
`00-master/portfolio.xlsx` (`export_site_data.py::export_positions`, line 75). That
column is written only by `scripts/refresh_targets.py`, whose `base_weight()`
(line 100) pins ✓✓✓ names to the 12% single-position cap. So the sizing logic Dom
wants **already exists** — it just never ran for MU's promotion.

`refresh_targets.py` rebalances (rewrites weights + logs a model event) **only on a
membership change** (`refresh_targets.py:396`); within-roster weight drift is frozen
on purpose — the hysteresis design that stops a noisy refresh from trading the book
(`portfolio_model.py:11`). MU's 2026-06-26 promotion (✓✓→✓✓✓) was **not** a
membership change, so no rebalance fired.

Worse, the fresh score/tier reached the `Targets` sheet through an **ad-hoc edit**
(commit `6d78941`, "refresh Targets sheet scores from Watchlist") that bypassed
`refresh_targets.py` entirely — updating display scores/tiers without re-weighting.
That produced the internally inconsistent row (✓✓✓ tier, ✓✓-band weight). No
committed script writes only the score columns of `Targets`; this was a manual
openpyxl step in the weekly-scan session.

The system already *detects* the event it fails to *act on*: `refresh_targets.py:293`
flags "tier ✓✓ → ✓✓✓ | allocation 7.4% → X%" — a detector with no actuator.

## Goal

When a held name crosses a tier band on rescore, the portfolio re-weights — both the
displayed target (`Targets` sheet → site) and the tracked model
(`performance-config.json` → Performance series) — in a single consistent snapshot.
Within-tier score drift continues to change nothing (hysteresis preserved).

## Non-goals

- **No** re-weight on within-tier score drift (the rejected "every rescore" option —
  reintroduces noise-trading).
- **No** change to scoring, tier bands, category weights, or the methodology
  (`Sizing Rules` tier table is unchanged).
- **No** new paid data; `refresh_targets.py` already uses yfinance for the freshness
  gate and prices.
- **No** change to CLAUDE.md rule 5: the model auto-rebalances on *material events*
  (now membership **or** tier change), matching the existing convention that Dom
  mirrors each rebalancing refresh in his account. Trade decisions remain Dom's; this
  only extends what counts as a material event.

## Decisions (locked with Dom, 2026-06-29)

1. **Trigger = tier crossing** (or membership change). Within-tier drift frozen.
2. **Freeze the whole snapshot.** Between rebalances, `Targets` score *and* tier *and*
   weight all freeze together and move together on a crossing. The Positions page may
   show a slightly lagged score within a tier; live scores remain on the Watchlist
   page. This makes a tier/weight mismatch structurally impossible to commit.
3. **Apply the corrective rebalance now, dated today (2026-06-29).** Re-weight the
   book to current scores; do not backdate (backdating would retroactively rewrite the
   tracked series, against the high-water-mark/immutability conventions).
4. **WDC exits (Dom, 2026-06-29).** WDC (71.6) is the only holding below the 74.5 exit
   threshold and was flagged "EXIT confirmed" in the 2026-06-26 scan, but the bypass
   left it in the book as `HOLD`. Dom's call: let it exit — the corrective is a plain
   `--resize` re-weighting the remaining **13** names (MU/TSM → ~11.7%). This executes
   the dropped 2026-06-26 exit decision; a membership/trade decision (rule 5) made
   explicitly, not bundled.

## Design

### Invariant (prevents recurrence)

Every score / tier / weight in the `Targets` sheet comes from the **same**
`refresh_targets` snapshot. A test asserts it: for every included row, the `Target %`
must lie within the band of its `Tier` (per the `Sizing Rules` table). The MU
state (✓✓✓ tier + ✓✓-band weight) becomes uncommittable.

### Components

1. **Store tier-at-rebalance** (`portfolio_model.py`). Each event in
   `performance-config.json` gains a `tiers` map `{ticker: "✓✓✓"}` recorded at
   rebalance time. `log_rebalance(cfg, weights, reason, tiers)` writes it. The
   detector compares against the *last rebalance's* tiers, not the last *run's*.

2. **Tier-crossing detector** (`refresh_targets.py`, in `refresh()`). After computing
   `include`/`info`, set
   `tier_changed = any(t in last_tiers and info[t]['Tier'] != last_tiers[t]
   for t in include)` where `last_tiers = cfg['events'][-1].get('tiers', {})`.

3. **Rebalance gate** (`refresh_targets.py:396`, modified). Fire on
   `set(include) != prior_model OR tier_changed OR resize`. Build the reason string
   from membership deltas and/or tier deltas (reuse the existing
   `"tier ✓✓ → ✓✓✓"` flag text). Pass current tiers to `log_rebalance`.

4. **Freeze-snapshot write gating** (`refresh_targets.py`, modified). The `Targets`
   and `Reconciliation` sheets and the README "Last built" stamp are rewritten **only
   when a rebalance fires** (or `--dry-run`/`--resize` as today). A no-arg run that
   finds no membership/tier change writes **nothing** to the workbook — the snapshot
   stays frozen. This makes the script idempotent and safe to run on every scan. Flags
   still print on non-firing runs (e.g. "NVDA 84.1 within ✓✓, no crossing").

5. **`--resize` forces a rebalance.** Extend `--resize` ("intentional re-sizing") to
   force the rebalance gate true — re-weight all included names to current
   `base_weight` and log an event — even with no membership/tier change. This is how
   the one-time corrective rebalance is applied, and the general "re-size the book
   now" escape hatch.

6. **Close the bypass** (docs). The weekly-scan / rescore workflow runs
   `python3 scripts/refresh_targets.py` after a rescore instead of hand-editing scores
   into `Targets`. `refresh_targets.py` becomes the **single writer** of the `Targets`
   sheet. Documented in the weekly-scan skill and CLAUDE.md (rule 9/12 neighborhood).

### Data flow

```
rescore writes Watchlist
  → refresh_targets.py runs (weekly-scan step / manual)
    → recalc() reads fresh scores+tiers (no network)
    → detector compares each held tier vs last event's tiers
    → if membership OR tier changed (or --resize):
        rewrite Targets (score+tier+weight, one snapshot)
        log_rebalance(): mark model to today's value, re-allocate at fresh weights,
                         store tiers, append event dated today
      else:
        no workbook write (frozen snapshot); print flags only
  → export_site_data.py reads Targets → site shows score-consistent weights
```

### Corrective rebalance (one-time, today)

Applied via `python3 scripts/refresh_targets.py --resize` — **the corrective must be
forced.** The last event (2026-06-18) predates the `tiers` field, so the detector has
no baseline and a no-flags run would *not* see MU's crossing. `--resize` forces the
gate, re-weights, and stores `tiers`; the detector is live from that event onward.

The two outcomes differ only on WDC (decision #4), via existing machinery:

- **Let WDC exit (rules-consistent, recommended):** plain `--resize`. WDC (71.6 < 74.5)
  exits; re-weight the remaining **13** names. Executes the 2026-06-26 "EXIT confirmed"
  decision the bypass dropped.
- **Keep WDC:** set WDC `Override = INCLUDE` in `Targets` first, then `--resize`. WDC is
  forced in and re-weighted to 3.5% (**14** names). Use only if Dom wants to override
  the exit rule.

| Ticker | Score | now (stale) | 14-name (WDC kept) | 13-name (WDC out) |
|---|---|---|---|---|
| MU  | 86.4 ✓✓✓ | 7.4% | **11.2%** | **11.7%** |
| TSM | 87.9 ✓✓✓ | 9.6% | **11.2%** | **11.7%** |
| NVDA| 84.1 ✓✓  | 9.3% | 9.0% | 9.3% |
| SNDK| 80.1 ✓✓  | 7.5% | 7.2% | 7.5% |
| CRDO| 80.0 ✓✓  | 7.5% | 7.2% | 7.4% |
| META| 79.5 ✓✓  | 7.0% | 7.0% | 7.2% |
| AVGO| 79.2 ✓✓  | 7.1% | 6.8% | 7.1% |
| ANET| 78.5 ✓✓  | 6.8% | 6.5% | 6.8% |
| MSFT| 78.4 ✓✓  | 6.2% | 6.5% | 6.7% |
| GOOGL|78.0 ✓✓  | 6.0% | 6.3% | 6.6% |
| ALAB| 77.1 ✓✓  | 6.1% | 5.9% | 6.1% |
| APP | 76.9 ✓✓  | 7.0% | 5.8% | 6.0% |
| FIX | 76.7 ✓✓  | 5.9% | 5.7% | 5.9% |
| WDC | 71.6 ✓✓  | 6.6% | 3.5% | — (exit) |

Either way MU/TSM (✓✓✓) move to the top and the inversion is gone. After this event,
the detector compares future runs against its stored `tiers`.

## Testing

New tests in `tests/` (pytest, matching the existing exporter suite):

- `test_targets_band_consistency` — for every included `Targets` row, `Target %`
  is within its `Tier` band. The regression gate for this whole bug class.
- `test_tier_crossing_triggers_rebalance` — given a prior event with `tiers` and a
  recalc where one held name's tier changed, the gate fires and the reason names the
  tier delta. (Mock `recalc`; no network.)
- `test_within_tier_drift_no_rebalance` — a held name's score moves within its band →
  gate does **not** fire → workbook untouched.
- `test_log_rebalance_stores_tiers` — `log_rebalance` persists the `tiers` map.

Network calls (`last_trade_age_days`, `current_price`, `mark`) are mocked/stubbed in
unit tests, as in the existing `refresh_targets`-adjacent tests.

## Edge cases

- **Legacy events without `tiers`** (all current events): `last_tiers` is `{}` →
  `tier_changed` is `False` (no spurious rebalance). The corrective `--resize` event
  is the first to store `tiers`; detection is live from then on.
- **Membership + tier change in one run**: gate fires once; reason concatenates both.
- **A name promoted then demoted between rebalances**: detection is vs the last
  *rebalance*, so a round-trip that nets to the same tier correctly does **not** fire.
- **`--dry-run`**: unchanged — prints the plan, writes nothing, logs no event.
- **No tier baseline yet:** every current event predates `tiers`, so the *first*
  rebalance after this lands cannot be auto-detected — it must be the forced `--resize`
  corrective. From that event on, `tiers` is stored and auto-detection works. (No
  reconstruction of historical tiers; we start the baseline at the corrective event.)
- **Future below-exit holding + tier crossing in one window:** once a tier baseline
  exists, a no-flags run fires on the crossing while a below-exit name is still
  `EXIT PENDING`, re-weighting it this run and confirming it out next run (two events);
  `--resize` collapses that to one. Both are correct under hysteresis — a timing
  difference, not a correctness one.
- **Two tier crossings same day / idempotent re-run**: `log_rebalance` already
  same-day-replaces the last event (`portfolio_model.py:107`), so re-running is safe.

## Files touched

- `scripts/portfolio_model.py` — `tiers` in event schema; `log_rebalance` signature.
- `scripts/refresh_targets.py` — detector, gate, freeze-snapshot write gating,
  `--resize` forces rebalance.
- `tests/` — four new tests above.
- `CLAUDE.md` + weekly-scan skill — `refresh_targets.py` is the single `Targets`
  writer; run it after rescores; never hand-edit scores into `Targets`.

## Out of scope

Marking the Positions score column live between rebalances; any change to the
Watchlist page; MRQ-adjusted scoring; layer caps.
