# Design: `/refresh-objective` — objective-input-only rescore

**Date:** 2026-06-24
**Status:** Approved (design) — pending spec review
**Author:** Dom + Claude

## Problem

A Watchlist score has two kinds of inputs:

- **Objective inputs** — numbers fetched from yfinance/filings with zero judgment
  (Value, Quality, Growth metrics + the 50DMA momentum metric). They go stale fast
  (every earnings print) and refreshing them is mechanical and safe.
- **Subjective ratings** — the 12 cells rated 1–5 by human judgment, backed by
  research (AI Thesis D1–D5, the 3 Momentum 1–5 ratings, Risk R1–R5). They go
  stale slowly and refreshing them *requires* a human in the loop (rule 12).

Today there is **no tool that refreshes objective inputs on existing rows.**
`batch_score.py:compute_inputs()` knows how to fetch every objective input, but
`batch_score.py` is **append-only** — it skips any ticker already on the
Watchlist. Only `momentum_50dma.py` updates existing rows, and just for the one
50DMA metric. So the rule-9 "refresh objective inputs within a week of earnings"
chore is done by hand, row by row.

This skill automates the safe half: refresh every objective input for a target
set of names, leave all subjective ratings untouched, and keep the human in the
loop *only* where genuine judgment is required.

## Goals

- One command to refresh all objective inputs for either **the portfolio** or
  **all scored names** (or an explicit ticker subset).
- Reuse `compute_inputs()` — do not duplicate the fetch logic.
- Never touch the 12 subjective rating cells.
- **Never silently regress a deliberate-blank convention** (foreign-ADR currency,
  EPS-YoY one-offs, negative-EBITDA, ROIC-not-exposed). This is the core safety
  requirement.
- Bump `Last Updated`, recompute TOTALs, and report before/after score + tier
  changes.

## Non-goals

- No subjective rating changes (that stays human-in-loop per rules 9/12).
- No MW-denominator refresh for the Layer-9 cohort (that's a filing read — the
  skill *flags* stale/missing MW but does not edit `capacity-mw.json`).
- No structural row changes, so `rebuild_watchlist_formulas.py` is **not** run.

## Target sets (the two modes)

| Invocation | Target rows |
|---|---|
| `/refresh-objective portfolio` | `HOLD` rows in `00-master/portfolio.xlsx` → `Targets` sheet (currently 14) |
| `/refresh-objective all` | every row on the Watchlist (~167) |
| `/refresh-objective NVDA MU AVGO` | explicit ticker subset |
| add `--dry-run` to any of the above | compute + report + flags, **write nothing** |

The portfolio roster is read from the `Targets` sheet's `Status == HOLD` rows
(column "Status"). Tickers are matched to Watchlist rows by the col-1 ticker.

## What gets written (column map)

`compute_inputs()` (11 metrics) + `momentum_50dma.py` (1 metric) → 12 objective
input cells:

| Col | Header | Source |
|---|---|---|
| 5 | Fwd P/E | `compute_inputs.fwd_pe` |
| 6 | EV/EBITDA (layer-conditional: EV/FCF L10, EV/MW L9) | `compute_inputs.ev_ebitda` |
| 7 | FCF Yield % | `compute_inputs.fcf_yield` |
| 8 | P/S | `compute_inputs.ps` |
| 11 | ROIC % | `compute_inputs.roic` |
| 12 | Gross Mgn % | `compute_inputs.gross_mgn` |
| 13 | FCF Mgn % | `compute_inputs.fcf_mgn` |
| 14 | ND/EBITDA | `compute_inputs.nd_ebitda` |
| 16 | Rev 3y CAGR % | `compute_inputs.rev_3y_cagr` |
| 17 | Rev YoY % | `compute_inputs.rev_yoy` |
| 18 | EPS YoY % | `compute_inputs.eps_yoy` |
| 29 | 50DMA % | `momentum_50dma.pct_days_above_50dma` |
| 4 | Last Updated | set to today on each refreshed row |

**Never touched:** col 9 (PEG — a formula), cols 10/15/19/25/30/35/36/37 (score &
TOTAL & Tier formulas — recompute themselves), and every subjective cell:
20 (AI Rev %), 21–24 (Position/Moat/Capacity/Hypersc.), 26–28 (EPS Rev/Rel
Str/Insider), 31–34 (R1–R4), 38 (R5 Disrupt Risk).

## The "smart" blank-handling ruleset

For each objective cell, fetch the fresh value, then apply guards **in order**.
Each guard is either **AUTO** (deterministically detectable → the script acts and
logs it) or **FLAG** (genuine judgment → the script surfaces it and the human
rules in the same run).

| # | Scenario | Detection | Action | Mode |
|---|---|---|---|---|
| 1 | **Foreign-ADR currency mismatch** | `info['financialCurrency']` exists and `!= 'USD'` | Force **P/S (8), EV/EBITDA (6), FCF-Yield (7)** to blank — USD price ÷ local-currency financials is garbage. Fwd P/E (5) & PEG kept (analyst EPS estimates already USD). | **AUTO** + log |
| 2 | **Negative / non-positive EBITDA** | fetched EBITDA ≤ 0 | Blank EV/EBITDA (6) & ND/EBITDA (14) | **AUTO** (already inside `compute_inputs`) |
| 3 | **Layer-10 SaaS** | layer == 10 | Col 6 carries EV/FCF on SaaS bands | **AUTO** (already inside `compute_inputs`) |
| 4 | **Layer-9 capacity cohort** | sub-layer contains "Bitcoin"/"Neocloud" | Col 6 carries EV/MW from `capacity-mw.json`; blank if MW missing | **AUTO** value; **FLAG** if MW missing OR the entry's `as_of` date is older than 90 days |
| 5 | **Fetch returned None, cell has a value** | fresh value is `None`/blank AND existing cell non-blank | **Keep the existing value** — a "no data" never clobbers a real number (protects ROIC and any hand-curated cell). **Exception:** `ev_ebitda` and `nd_ebitda` blank-through on a fresh `None` so that guard-2 (non-positive EBITDA) and guard-3/4 (L10 EV/FCF / L9 EV/MW missing denominator) deliberate blanks win over keep-prior; a flag is emitted when the cell had a prior value. | **AUTO** + log |
| 6 | **EPS-YoY one-off** | (a) cell currently blank; OR (b) fresh `\|EPS YoY\| ≥ 300%` | (a) **preserve the blank**; (b) **leave the cell as-is** (do not write the extreme value — never auto-inflate Growth off a possible one-off) | **FLAG** |
| 7 | Everything else | — | Write the fresh value | **AUTO** |

Guard order matters: 1–4 decide *which metric/representation* a column holds and
can force blanks; 5 protects existing values from a failed fetch; 6 is the
EPS-YoY judgment gate; 7 is the default write.

**Threshold (guard 6b):** `|EPS YoY| ≥ 300%` → flag, don't write. Rationale:
GEV's +1,768% (Prolec divestiture gain) clears it; a name growing 50%→80% does
not. `eps_yoy` is `info['earningsQuarterlyGrowth'] × 100` — a single computed %,
so a true loss→profit sign-flip isn't separately detectable (yfinance returns
`None` or an already-extreme number in that case, which the magnitude test
catches anyway). Per rule 15, the *decision* to blank is documented judgment, not
magnitude — so the script only ever **flags**; it never blanks a previously valid
EPS-YoY on its own.

## Run flow

1. Resolve target tickers (portfolio / all / subset) → Watchlist row numbers.
2. For each ticker (serialized — yfinance throttling, per CLAUDE.md): fetch
   `info`, run `compute_inputs`, apply guards 1–7, stage the cell writes.
3. Run `momentum_50dma` logic for col 29 on the same target set.
4. **Dry-run:** print the staged change table + JUDGMENT FLAGS block, write
   nothing, exit.
5. **Live run:** write staged cells, set Last Updated (col 4) = today on every
   touched row, save the workbook.
6. Run `recalc_watchlist.py` and print before/after TOTAL + any tier changes.
7. Print the **JUDGMENT FLAGS** block: every cell where guard 4 (missing/stale
   MW) or guard 6 (preserved/withheld EPS-YoY) fired, so the human rules on the
   handful that need it.

## Output (example)

```
REFRESH OBJECTIVE INPUTS — mode=portfolio (14 names) — DRY RUN

Ticker  Fwd P/E   EV/x    FCF Yld   P/S    ...  50DMA%   Last Upd
NVDA    38.2→41.1  ...                            72→78   →2026-06-24
TSM     22.1→23.4  [ADR blank: P/S,EV/EBITDA,FCFy]        →2026-06-24
MU      11.0→10.4  ...                                    →2026-06-24

JUDGMENT FLAGS (human ruling needed):
  • GEV  EPS YoY: fresh +412% ≥ 300% → withheld (rule 15). Confirm blank or write.
  • CRWV EV/MW: capacity-mw.json as-of 2026-03-15 → 101 days old (>90) → stale, refresh MW.

TOTAL changes (after recalc):
  NVDA  84.08 → 84.6  (✓✓, no tier change)
  ...
```

## Implementation shape

- **New script:** `scripts/refresh_objective_inputs.py`
  - `import`s `compute_inputs`, `statement_fcf`, `_secured_mw` (and column
    constants) from `batch_score.py` — reuse, no duplication.
  - Adds: target-set resolution (portfolio Targets sheet / all / subset),
    refresh-existing-row writes, the guard pipeline (1–7), Last Updated bump,
    `--dry-run`.
  - `momentum_50dma` 50DMA refresh invoked for the same target set (import its
    `pct_days_above_50dma`, or shell out to the existing script with ticker args).
  - After write, call `recalc_watchlist.py` to report TOTAL/tier deltas.
- **New skill wrapper:** `.claude/commands/refresh-objective.md` — documents the
  two modes, the dry-run-first discipline, the guard ruleset, and the
  relationship to rules 9/12 (this is the objective half of rule 9; subjective
  refresh remains rule 12).

## Testing

- Unit tests (`tests/test_refresh_objective_inputs.py`):
  - Guard 1: a stubbed `info` with `financialCurrency='TWD'` blanks cols 6/7/8,
    keeps col 5.
  - Guard 5: fetched `None` over an existing value keeps the existing value.
  - Guard 6a: a currently-blank EPS-YoY cell stays blank and is flagged.
  - Guard 6b: a fresh `+412%` EPS-YoY is withheld (cell unchanged) and flagged;
    a fresh `+80%` is written.
  - Target resolution: `portfolio` returns exactly the `HOLD` tickers.
  - Subjective cells (20–28, 31–34, 38) are never written.
  - `--dry-run` writes nothing to the workbook (mtime / value assertions on a
    temp copy).
- Tests operate on a temp copy of the workbook; no network (stub `compute_inputs`
  inputs).

## Risks / open items

- yfinance throttling on the `all` (~167) run — serialize with the existing
  `time.sleep` cadence; the run is slow but that's acceptable (not optimizing for
  speed per CLAUDE.md).
- `info['financialCurrency']` absence: if the key is missing, guard 1 does **not**
  fire (treated as USD) — same conservative behavior as today's manual process;
  the ADR list is small and already flagged in memory.
- recalc-vs-Excel blank-handling divergence (known): `recalc_watchlist.py` sums
  available category parts without renormalizing; Excel blanks TOTAL if a category
  is empty. The report uses recalc numbers and notes this is an approximation of
  the cached Excel TOTAL.
