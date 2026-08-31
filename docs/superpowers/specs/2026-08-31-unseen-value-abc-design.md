# Unseen-value fixes (A/B/C): capitulation flag, acceleration-aware P2, methodology-seam damping

Date: 2026-08-31. Approved by Dom (chat, 2026-08-31: "let's do A, B, C").
CLAUDE.md rule 32.

## 1. The post-mortem that motivated this

Dom kept PLTR and CRM in his Fidelity account after the model exited them;
both became top gainers. Reverse-engineering the exits:

| Name | Exited | Trigger | Return since exit | QQQ same window |
|---|---|---|---|---|
| CRM | 2026-06-10 | 50DMA metric launch (06-09) collapsed Momentum; exit-pending same day, confirmed next | **+53%** | +3% |
| ZS | 2026-06-18 | 76/74.5 threshold experiment (reverted 2026-08-02 as a mistake) | **+50%** | −3.5% |
| PLTR | 2026-07-02 | P1 percentile go-live (on the P1 report's "Would EXIT" list) | **+44%** | +0.2% |

Control group — the same period's other exits were **good**: APP −41%, WDC
−31%, ALAB −28%, RDDT −24%, VRT −23%, ARM −22%, TER −19% (all vs QQQ, since
their exit dates). The exit engine is net-positive; this change fixes three
identified mechanisms, it does not re-tune the system (rule 28).

### Why exactly these three names

All three are software names exited days before a violent software-vs-semis
rotation (since 06-18: IGV +23%, SMH −16%, model −7.8%). Mechanisms:

1. **No home for "priced for death, fundamentals fine."** Rule 14's
   expectations flag is one-sided (catches peak multiple + decelerating
   growth). CRM sat at Fwd P/E ~11 / 10.4% FCF yield with growth intact; the
   fear was penalized three times (Momentum, D1, R5) while the cheapness
   counted once (Value 89.7 at 20% weight).
2. **P2's grounded-growth clamp is acceleration-blind.** PLTR: EV/FCF ~107 ⇒
   implied growth ~30%; actual rev YoY 84.7% (3-yr CAGR 32.9%). The 25% clamp
   (review #1, 2026-07-02) forced grounded=25 < implied ⇒ score 30/100 — the
   metric read "overpriced" for a company out-delivering what the market
   priced. Rule 21 documented the deceleration mirror of this; PLTR was the
   acceleration case.
3. **Methodology-deploy churn.** All three exits fired on methodology-change
   days, not company news; the 2-run clock confirmed within ~a day. The
   reflexivity trap compounds it: price ↑ → Value ↓ → score ↓, so a name
   exited by a deploy that then rallies can never re-enter (ZS, PLTR after
   the threshold revert re-admitted EME/VRT/ALAB/RDDT but not them).

## 2. A — Capitulation flag (`scripts/capitulation_flag.py`)

Mirror of rule 14, same machinery (SEC companyfacts quarterly revenue, 3-yr
P/S percentile, constant-share-count caveat):

- **FLAG:** P/S ≤ 10th percentile of own 3-yr range AND rev YoY ≥ its 3-yr
  median. (Rule 14 fires at ≥ 90th + growth *below* median.)
- **Qualitative red flag, NOT a scored metric.** Surfaced in
  `/refresh-context` Step 2e and weekly-scan Step 7d (run on every exit-side
  name: EXIT PENDING / EXIT / seam-damped). A firing changes nothing
  mechanically.
- **Calibration-first discipline:** `--log-forecast` appends a rule-17
  forecast per firing — dimension `signal.capitulation`, template
  `REL_STRENGTH_1Q` (existing resolver; frozen layer-cohort EW basket, 63
  td), probability 0.55 (deliberately uninformed base rate — the point is to
  learn the hit rate), rating_value null, at most one open forecast per name.
  Any scored version of this signal must first show ~30 resolved forecasts of
  positive calibration evidence.

**Validation:** backtested at the exit dates — CRM 2026-06-10: P/S 0.8th
pctile, YoY 17.9% vs median 14.6% → **fires**. ZS 2026-06-18: 0.1th pctile
but YoY 31.3% vs median 45.2% → correctly does **not** fire (growth genuinely
decelerating; ZS's rally was only knowable in hindsight). The flag catches
the CRM shape, and honestly declines the ZS shape — that asymmetry is the
"intact fundamentals" condition doing its job.

## 3. B — Acceleration-aware grounded growth in P2 (`scripts/reverse_dcf.py`)

- Default unchanged: grounded = clamp(3-yr CAGR, 0, 25).
- **Extension gate:** when BOTH 3-yr CAGR ≥ 30% AND current rev YoY ≥ 30%
  (sustained AND current hypergrowth), grounded = min(max(CAGR, YoY), **40**).
- `recalc_watchlist._assemble` now passes the sheet's Rev YoY (col Q) into
  `reverse_dcf_score(..., rev_yoy_pct=)`. YoY=None reproduces old behavior
  bit-for-bit, so rule-15 EPS blanks and thin names are unaffected.
- Why still a cap: P2 must stay a mispricing signal, not a growth factor
  (the original review-#1 concern is preserved). Why both-inputs gate: a
  decelerating cyclical (low YoY) or a one-quarter spike off a low base
  (low CAGR) keeps the conservative clamp — only names growing ≥30% on both
  the 3-yr and the current view can ground above 25.
- **Constants are priors, not fit parameters.** 30 (gate) and 40 (cap) were
  chosen before measuring PLTR's resulting score band; do not tune them
  against realized returns (rule 28). PLTR lands at 75/100 (gap +9.9pp), not
  a saturated 100 — the framework remains skeptical of hypergrowth pricing,
  just no longer blind to it.

**Deploy impact (2026-08-31, percentile mode, 214 names):** 6 names move,
all up: ALAB +1.50 (rank 15→12), PLTR +1.50 (26→20), CRDO +1.50 (5→4),
SNOW +1.20, NVDA +0.83 (crosses 85 → ✓✓✓; no event in inverse-vol sizing),
FIX +0.33. Zero rank-15/18 boundary crossings ⇒ deploy forces no trades.

## 4. C — Methodology-seam damping (`scripts/refresh_targets.py`)

- `--seam "reason"` stamps `methodology_seam: {date, reason}` into
  `tracking/performance-config.json` (latest stamp wins). **Part of every
  methodology deploy, run before `recalc --sync`.**
- `SEAM_DAYS = 7` (calendar). An exit-pending clock that STARTED inside
  `[seam_date, seam_date+7d)` cannot confirm while today < seam_date+7d: the
  name stays held, keeps its ORIGINAL clock date, and shows
  `EXIT PENDING (seam-damped until …)`.
- Deliberately narrow: clocks predating the seam are data-driven and confirm
  on schedule; `--resize`, dead/delisted, and untradable exits bypass
  unchanged; entries are not damped. `pending_rebalance()` runs the same
  path, so the rule-25 gate stays green during damping (a week of designed
  red would train people to ignore the gate).
- Honest limit: a seam only *delays*. Replayed against June, CRM confirms
  ~06-17 anyway (its momentum couldn't recover in a week) — C's real value
  is stopping same-day methodology whipsaws and giving A's flag a window to
  be heard before the book trades.

## 5. Declined (deliberately)

- **Contrarian/rotation factor** (cross-sector value tilt, mean-reversion
  momentum): factor-timing on n=3 hindsight — the exact overfitting trap
  rules 17/28 exist to block. The pre-registered BAND_NEXT experiment and
  EW_ROSTER tripwire (~2027-02) remain the honest instruments for selection-
  breadth questions.
- **Scoring the capitulation signal now:** must earn calibration evidence
  first (§2).
- **Tuning B's constants to "catch" PLTR at rank ≤15:** would be curve
  fitting; PLTR at rank ~20 post-B is the framework's honest opinion.

## 6. Files

- `scripts/capitulation_flag.py` (new) + `tests/test_capitulation_flag.py`
- `scripts/reverse_dcf.py`, `scripts/recalc_watchlist.py` +
  `tests/test_reverse_dcf.py` (5 new cases)
- `scripts/refresh_targets.py` + `tests/test_refresh_targets.py` (5 new cases)
- `.claude/commands/weekly-scan.md` (Step 7d + output section)
- `.claude/commands/refresh-context.md` Step 2e — **working-tree only in this
  change**: the file carries the 2026-08-24 session's uncommitted
  litigation-check Step 2d; committing it here would half-land that work.
  The 2e hunk rides along when that session's work is committed.
- `CLAUDE.md` rule 32.
