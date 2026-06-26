# Design: Forecast Calibration Loop (Phase 1)

**Date:** 2026-06-26
**Status:** design approved (Dom), ready for implementation plan
**Source spec:** `calibration-loop-spec.md` (Dom, proposal)
**Proposed CLAUDE.md rule:** #17
**Owner:** Dom (human-in-loop on all probabilities and ambiguous resolutions)

---

## 1. Purpose & boundary

Turn each frozen subjective rating into a dated, falsifiable, mechanically-resolvable
probability, then grade those probabilities the way forecasting research grades
forecasters (Brier score + Murphy decomposition + skill vs. base rate). The output is a
**diagnostic about the rater's judgment**, never an input to the score.

This operationalizes the blind spot CLAUDE.md rule 12 already names: *"a ranking system
is self-consistent but not self-correcting … uniform bias across a cohort cancels out of
the sort order and is invisible to relative ranking. Only an absolute standard, applied
from outside, exposes it."* Calibration **is** that outside standard.

### Hard boundary (enforced; do not weaken)
- **Does NOT feed back into the Total Score or category weights.** Auto-reweighting on
  recent data is the overfitting trap flagged in prior reviews — not built.
- **Adds NO scored columns** to the Watchlist tab.
- **No paid data.** Resolution uses the existing free stack only (yfinance prices,
  SEC EDGAR, the repo's cohort/layer structure).
- **Not surfaced on the friend-facing site.** Calibration artifacts stay repo-internal;
  the site exporter (`scripts/export_site_data.py`) gains no new surface.

---

## 2. Decisions locked during brainstorming

1. **Frozen peers.** The rel-strength benchmark is a layer-cohort equal-weight basket
   whose constituent list is **frozen into `resolution_rule` at creation**. Thin layers
   (< 4 peers after excluding self) fall back to a frozen `SMH`. No membership look-ahead.
   (Threshold lowered 6→4 on 2026-06-26 so Layer 05's 4 fab peers form a real cohort — per Dom.)
2. **Batch-seed now.** Phase 1 seeds one `REL_STRENGTH_1Q` forecast per current portfolio
   name today; first outcomes resolve in ~1 quarter.
3. **Single append-only snapshot log.** One file, `tracking/forecasts.jsonl`. Creation
   appends an `open` snapshot; resolution appends a new `resolved`/`needs_review`/`void`
   snapshot of the **same `id`** — lines are never edited. Current state of an `id` = its
   last snapshot. Immutability becomes a property of the data structure, not just a policy.
4. **Flat modules.** New core modules and CLIs live flat in `scripts/` with a `forecast_`
   prefix, matching the existing catalog style (`momentum_50dma.py`, `batch_score.py`).

---

## 3. Architecture & module layout

Pure-logic core modules (CI-safe, unit-testable) + thin CLIs. The CI test environment
installs only `openpyxl` + `pytest` (no yfinance, numpy, or matplotlib), so the grading
and scoring paths must import none of those at module load.

| File | Role | Import-time deps |
|---|---|---|
| `scripts/forecast_store.py` | The log: load / materialize / append / validate; owns immutability + no-look-ahead invariants and `id` assignment | stdlib only |
| `scripts/forecast_cohorts.py` | Build the frozen peer basket from the Watchlist (same `layer_num`, exclude self, SMH fallback for thin layers) | openpyxl |
| `scripts/forecast_resolvers.py` | Template registry + `REL_STRENGTH_1Q` resolver; **price data is injected**, never fetched here | stdlib only (pure) |
| `scripts/forecast_metrics.py` | Brier, Murphy REL/RES/UNC, BSS, log loss, reliability table | stdlib only (pure Python, no numpy) |
| `scripts/log_forecast.py` | CLI → store + cohorts; `--seed-portfolio` mode | openpyxl |
| `scripts/resolve_forecasts.py` | CLI → store + resolvers; provides the yfinance-backed price loader (lazy import); `--dry-run` | yfinance (lazy, inside loader) |
| `scripts/calibration_report.py` | CLI → store + metrics; writes `tracking/calibration-report.md`; optional PNG | matplotlib (lazy, guarded) |

Reused from the existing repo (do not reimplement):
- `scripts/common.py`: `ROOT`, `flag()`, `RateLimiter`, `sec_get`, `SEC_USER_AGENT`.
- `scripts/refresh_objective_inputs.py`: `resolve_targets(arg)` for `portfolio | all | TICKERS`
  (portfolio = Targets sheet rows with `Status == "HOLD"`, intersected with the watchlist).
- yfinance price pattern from `momentum_50dma.py`: `yf.Ticker(t).history(period=…, auto_adjust=True)`,
  `.dropna()`, stale-last-bar freshness gate, `time.sleep(0.3)` throttle.

### Data flow

```
log_forecast.py  --seed-portfolio
   └─ resolve_targets("portfolio") ──▶ forecast_cohorts.build_frozen_cohort(ticker)
   └─ read rel-strength rating (Watchlist) ──▶ default probability (§7 map)
   └─ Dom overrides probabilities
   └─ forecast_store.append(open snapshot)  ─────▶  tracking/forecasts.jsonl

resolve_forecasts.py   (weekly)
   └─ forecast_store.materialize() ──▶ open forecasts with resolution_date ≤ today
   └─ forecast_resolvers.resolve(forecast, price_loader=yfinance_loader)
   └─ forecast_store.append(resolved | needs_review snapshot)

calibration_report.py  (quarterly)
   └─ forecast_store.materialize() ──▶ resolved forecasts
   └─ forecast_metrics.* ──▶ tracking/calibration-report.md  (+ optional .png)
```

---

## 4. The log (`forecast_store.py`)

`tracking/forecasts.jsonl` — one JSON object (full forecast snapshot) per line, append-only.

- **`materialize()`** → `{id: latest_snapshot}` by folding the file, last line per `id` wins.
  State precedence is simply "last write," because resolution always appends after creation.
- **`append_creation(forecast)`** → validates a new `open` snapshot, assigns a stable `id`,
  appends. Rejects if `id` already exists.
- **`append_resolution(snapshot)`** → validates that the `id` exists with an `open` (or
  `needs_review`) state, and that **every immutable field is byte-identical** to the
  creation snapshot, then appends. Immutable fields: `created_date`, `probability`,
  `resolution_date`, `resolution_rule`, `ticker`, `template`, `dimension`, `rating_value`.

### Validation rules (creation)
- `probability` ∈ (0, 1) exclusive.
- `created_date == today()` — set by the store, not the caller → backdating is impossible.
- `resolution_date > created_date` and lies entirely in the future (no-look-ahead).
- `resolution_rule` complete for the template (e.g. `constituents`, `horizon_td`).
- Schema completeness + types. No `jsonschema` dependency — hand-rolled validation, raising
  on the first violation with a `flag()`-style message (CLAUDE.md rule 3: flag, don't assume).

### `id` format
`fc_{created_date}_{ticker}_{template_slug}_{NNN}` — e.g. `fc_2026-06-26_AVGO_relstr_001`.
`NNN` is a per-(date, ticker, template) sequence the store assigns for uniqueness.

### Writes
Always append (open file in `"a"` mode, one `json.dumps` line). No rewrite path exists, so
there is no partial-rewrite corruption risk and no code path that can mutate a prior line.

---

## 5. Forecast schema

Spec schema as-is, with two repo-fit concretizations: `layer` is the 2-char `layer_num`
string, and `resolution_rule.constituents` carries the frozen peer list.

```jsonc
{
  "id": "fc_2026-06-26_AVGO_relstr_001",
  "created_date": "2026-06-26",            // = today() at log time; immutable
  "ticker": "AVGO",
  "layer": "06",                           // 2-char layer_num
  "dimension": "momentum.rel_strength",    // nullable
  "rating_value": 4,                       // the 1–5 rating this is tied to; nullable
  "template": "REL_STRENGTH_1Q",
  "claim": "AVGO total return outperforms its frozen Layer-06 equal-weight peer basket over the next 63 trading days",
  "probability": 0.65,                     // THE forecast; immutable
  "resolution_date": "2026-09-29",         // earliest grading date (see §6); immutable
  "resolution_rule": {                     // frozen at creation; immutable
    "benchmark": "layer_cohort_ew",        // or "SMH" (thin-layer fallback)
    "constituents": ["NVDA", "MU", "ALAB", "SNDK", "..."],  // frozen peer list, self excluded
    "horizon_td": 63
  },
  "status": "open",                        // open | resolved | needs_review | void
  "outcome": null,                         // 1 | 0 | null
  "resolved_date": null,
  "resolution_evidence": null,             // cited: source + returns + dates
  "resolver_confidence": null,             // auto | human_confirmed
  "notes": ""
}
```

Risk templates (future phases) keep `claim` worded as the bad event and `probability` as
P(event) — high (safe) R-rating → low P(event). No silent sign flips.

---

## 6. `REL_STRENGTH_1Q` resolver (`forecast_resolvers.py`)

```python
def resolve_rel_strength_1q(forecast, *, price_loader) -> Resolution
```

- `price_loader(ticker, start_date) -> dict[date, float]` of **adjusted** closes
  (`auto_adjust=True`). Production passes a yfinance-backed loader (lazy import, throttled,
  freshness-gated, defined in `resolve_forecasts.py`); tests pass a synthetic dict. This
  injection seam is what makes the resolver CI-testable on synthetic price series.
- **base bar** = first trading bar with date ≥ `created_date`; **horizon bar** = the bar
  `horizon_td` positions after base. `r = horizon_close / base_close − 1`.
- **cohort return** = mean of constituents' `r` (US equities share a calendar, so bar *i*
  is the same date across names). SMH fallback: just SMH's `r`.
- **outcome** = `1` if `r_self > r_cohort` else `0`.
- **evidence** (cited per rule 1): e.g.
  `"AVGO +12.3% vs Layer-06 EW (12 names) +8.1%, 2026-06-26→2026-09-26 (63 td), yfinance adj close → 1"`.
- **`resolver_confidence`** = `auto`.

### NA / needs_review handling
- `< horizon_td + 1` forward bars for self **and** `resolution_date` not yet past → leave
  `open` (not due). If `resolution_date` is past and still short → `needs_review`.
- Self delisted / no data, or `> 25%` of frozen constituents missing data → `needs_review`
  with a cited reason. Never silently drop or guess.

### `resolution_date` computation (at log time, stdlib only)
`resolution_date` = 63 weekdays forward from `created_date` + a 7-calendar-day holiday
buffer. It is a **scheduling** date ("earliest grading date") and sits deliberately a few
days *after* the actual 63rd-trading-day horizon bar — in the §5/§6 examples the horizon
bar lands ~2026-09-26 while `resolution_date` is 2026-09-29 — so the horizon bar reliably
exists by the time the forecast becomes due. The resolver always re-checks actual bar
count, so a holiday cluster can never force a premature grade. Pure stdlib (no numpy /
market-calendar dependency) so it is CI-importable and unit-testable.

---

## 7. Phase-1 seeding (`log_forecast.py --seed-portfolio`)

1. `resolve_targets("portfolio")` → current HOLD names (~14).
2. For each name: read its **Relative Strength** rating (Watchlist Momentum dimension,
   col AA — exact column resolved via the existing Watchlist reader, not hardcoded), build
   its frozen cohort via `forecast_cohorts.build_frozen_cohort`, and propose a default
   probability from the spec map:

   `5 → 0.80 · 4 → 0.65 · 3 → 0.55 (base rate) · 2 → 0.42 · 1 → 0.28`

   Missing rating → default 0.55 and flag for Dom to set.
3. `--dry-run` prints the proposed set as a table (ticker, layer, rating, default p, claim,
   resolution_date). Claude shows it to Dom in chat.
4. Dom overrides probabilities — **the override is the training signal**, not the mechanical
   map. Overrides supplied via `--apply --overrides overrides.json`.
5. On apply, `forecast_store.append_creation` writes one `open` snapshot per name.

The §7 default map is a starting prior only. Once a dimension accumulates enough resolved
forecasts (~30), replace the prior with the empirically observed per-bucket hit rate.

---

## 8. Metrics (`forecast_metrics.py`)

Pure functions over `(probabilities, outcomes)`; reported **overall + per `dimension` +
per `layer`**.

- **Brier** (headline): `BS = mean((p − o)²)`, computed directly.
- **Murphy decomposition**: bins default to deciles `[0,.1),…,[.9,1]`. Per bin *k*:
  `n_k`, `p̄_k`, `ō_k`.
  `REL = (1/N)Σ n_k(p̄_k − ō_k)²` (lower better),
  `RES = (1/N)Σ n_k(ō_k − ō)²` (higher better),
  `UNC = ō(1 − ō)`.
- **BSS** (null-model check, always reported): `1 − BS/UNC`. `≤ 0` → no skill over forecasting
  the base rate.
- **Log loss** (secondary): `p` clipped to `[1e-6, 1−1e-6]`.
- **Reliability table**: per bin `p̄_k` vs `ō_k`, emitted in the markdown report.

**Identity:** `REL − RES + UNC == BS` holds exactly in the discrete-forecast limit; the only
residual is within-bin forecast spread. The unit test plants forecasts at distinct bin
centers (zero within-bin spread) so the assertion is exact to floating-point tolerance.
The report surfaces the residual if it is materially nonzero on real data.

**Small-N guard:** the report prints N for every cell and refuses to render or
over-interpret a reliability curve below a threshold (~30). Phase 1 (~14 forecasts/quarter,
one template) yields a noisy decomposition for a year+; the report says so explicitly rather
than implying a trustworthy curve.

---

## 9. Reports & charts (`calibration_report.py`)

Writes `tracking/calibration-report.md`:
- Headline BS / BSS / REL / RES / UNC / log loss, with N.
- The reliability table.
- Per-dimension league table and per-layer breakdown.
- The void / needs_review rate (meta-signal: high rate → resolution rules too vague).
- A plain-English "where you're miscalibrated" section.
- An explicit base-rate-null beat test ("BSS = … → {beats / does not beat} always-base-rate").

Optionally renders `tracking/calibration-curve.png` (reliability diagram, 45° reference)
**only if matplotlib imports** — `plt.switch_backend("Agg")`, `savefig`, `close`. The PNG is
never required; the markdown table is the primary artifact (CI and the daily cron have no
matplotlib).

---

## 10. Workflow integration (Phase 1 only)

- **`.claude/commands/weekly-scan.md`** — new **Step 9: Resolve due forecasts**. Run
  `python3 scripts/resolve_forecasts.py --dry-run` then for real; surface newly resolved
  outcomes, anything in `needs_review`, and the running void rate.
- **`.claude/commands/rescore-quarterly.md`** — new step **Regenerate calibration report**
  (`python3 scripts/calibration_report.py`); review the reliability table/diagram. This is
  the absolute-lens stress test rule 12 asks for.
- **Deferred to Phase 2** (per spec §8): rating-time paired-forecast generation in
  `score-stock` / batch scoring. Phase 1 wires only the weekly/quarterly hooks.

---

## 11. Testing (extends `tests/`)

All core modules CI-safe (no yfinance / matplotlib / numpy at import).

- **`tests/test_forecast_store.py`** — look-ahead rejection; `created_date == today` enforced;
  immutable-field guard rejects a resolution whose immutable field differs; malformed-record
  rejection; `materialize()` last-wins across multiple snapshots of one `id`; `id` uniqueness.
- **`tests/test_forecast_resolvers.py`** — `REL_STRENGTH_1Q` on synthetic price dicts:
  self beats cohort (1), loses (0), insufficient bars (open/NA), SMH fallback path,
  degraded cohort > 25% missing (needs_review). Plus `resolution_date` weekday math.
- **`tests/test_forecast_cohorts.py`** — frozen-cohort construction on a synthetic Watchlist:
  groups by `layer_num`, excludes self, and falls back to a frozen `SMH` when a layer has
  < 4 peers. (openpyxl-based fixture, CI-safe.)
- **`tests/test_forecast_metrics.py`** — BS value on a known set; `REL − RES + UNC == BS`
  identity (discrete forecasts); BSS sign; log-loss clipping; reliability table; N = 0 and
  small-N behavior.

Run via the existing `python -m pytest tests -q`.

---

## 12. CLAUDE.md rule 17 (draft text to add during implementation)

> ### 17. Forecast calibration loop (added 2026-06-26, approved by Dom)
>
> **Context:** Subjective ratings (AI-Thesis, Momentum, Risk R1–R5) are implicit predictions,
> assigned and frozen but never graded against what happened. A ranking system can't see its
> own uniform bias (rule 12); calibration is the external absolute standard that can.
>
> **Rule:** Selected ratings are logged as falsifiable, dated forecasts with a frozen,
> mechanical resolution rule in `tracking/forecasts.jsonl` (single append-only snapshot log).
> Forecasts are resolved on schedule and graded with Brier score, the Murphy
> REL/RES/UNC decomposition, Brier Skill Score vs. the base rate, and a reliability diagram.
>
> **Guarantees (do not weaken — treat like the site privacy gate):** `probability`,
> `created_date`, `resolution_date`, and `resolution_rule` are immutable (a changed mind is a
> new forecast); `created_date` is set to today at log time so backdating is impossible; the
> resolver consumes only post-`created_date` data (no look-ahead); ambiguous resolutions go to
> `needs_review`, never guessed.
>
> **Boundary:** calibration is diagnostic — it does **not** feed back into the Total Score or
> category weights, adds **no** Watchlist columns, uses **no** paid data, and is **not**
> surfaced on the friend-facing site. A dimension proving to be noise is a human decision
> ("stop trusting it / investigate"), never an automatic reweight.
>
> **Cadence:** `/weekly-scan` resolves due forecasts; `/rescore-quarterly` regenerates
> `tracking/calibration-report.md`. Scripts: `log_forecast.py`, `resolve_forecasts.py`,
> `calibration_report.py`.
>
> **Rollout:** Phase 1 = `REL_STRENGTH_1Q` on portfolio names. Phase 2 adds
> `EARNINGS_REACTION` + full watchlist. Phase 3 adds the fundamental templates. Switch
> rating→probability defaults to empirically-learned per-bucket hit rates once each dimension
> has ~30 resolved forecasts.

---

## 13. Scope boundary — explicit non-goals for first delivery

Not built now: `EARNINGS_REACTION` and the four fundamental templates
(`MARGIN_HOLD_1Y`, `GROWTH_PERSIST_2Q`, `NO_LIQUIDITY_EVENT_1Y`, `DISRUPTION_DECEL_1Y`);
rating-time / `score-stock` forecast generation; empirical default-remapping; live-membership
cohorts; any score/weight feedback; any Watchlist column; any site-export surface. The
resolver **registry** is built to accept new templates later; only `REL_STRENGTH_1Q` ships
implemented and tested.

---

## 14. Phased rollout

1. **Phase 1 (now):** `REL_STRENGTH_1Q` on portfolio names. Scripts 1–3 + weekly/quarterly
   hooks + tests + rule 17. First calibration signal in ~1 quarter on pure yfinance data.
2. **Phase 2 (+1 quarter):** add `EARNINGS_REACTION` (market-reaction proxy — documented as
   reaction, not accounting beat); extend to the full watchlist; add rating-time paired
   forecasts.
3. **Phase 3 (+2 quarters):** add the fundamental templates as earlier forecasts resolve.
4. Switch the §7 priors to empirically-learned per-bucket hit rates per dimension at ~30 N.

---

## 15. Acceptance criteria (Phase 1)

- [ ] `tracking/forecasts.jsonl` snapshot log; `forecast_store` rejects look-ahead, malformed
      records, and immutable-field changes on resolution.
- [ ] `REL_STRENGTH_1Q` resolver implemented and unit-tested on synthetic price data.
- [ ] `calibration_report.py` computes BS, REL/RES/UNC (with a test asserting
      `REL − RES + UNC == BS`), BSS, log loss, and the reliability table; writes
      `tracking/calibration-report.md`.
- [ ] Per-dimension and per-layer breakdowns present in the report.
- [ ] `log_forecast.py --seed-portfolio` seeds the portfolio names with Dom-overridden
      probabilities (dry-run → review → apply).
- [ ] `/weekly-scan` resolves due forecasts; `/rescore-quarterly` regenerates the report.
- [ ] CLAUDE.md rule 17 added, documenting the loop, the immutability / no-look-ahead
      guarantees, and the "does not feed back into scores" boundary.
- [ ] All new tests pass under `python -m pytest tests -q` (no yfinance/matplotlib in CI).
- [ ] Phase-1 scope only (portfolio names, one template).

---

*Calibration is the part of the project that makes the rater better, not the model. Build it
so it can say "you're wrong" — that's the only version worth having.*
