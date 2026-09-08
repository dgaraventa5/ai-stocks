---
description: Refresh objective Watchlist inputs only (portfolio / all / subset), leaving subjective ratings untouched
---

Refresh the **objective** inputs (Value, Quality, Growth metrics + 50DMA %) for a
set of Watchlist names. Subjective ratings (AI Thesis, Momentum 1–5, Risk R1–R5)
are NEVER touched — those stay human-in-loop (rule 12). This is the automatable
half of rule 9 (earnings-triggered objective refresh).

## Usage

- `/refresh-objective portfolio` — the HOLD rows in `00-master/portfolio.xlsx` → Targets.
- `/refresh-objective all` — every Watchlist row.
- `/refresh-objective NVDA MU AVGO` — explicit subset.

## Process

1. **Always dry-run first** and show the change table + JUDGMENT FLAGS:
   `python3 scripts/refresh_objective_inputs.py <target> --dry-run`
2. Resolve the JUDGMENT FLAGS with Dom — these are the only cells needing
   judgment:
   - **EPS YoY withheld/preserved/STALE** (rule 15): confirm blank vs write per
     filing evidence, then record the ruling in `00-master/eps-yoy-overrides.json`
     (ticker → `quarter_end`, `value` null|ex-item %, `basis`, `source`, `ruled`,
     `audit_row`) as well as the Rating Audit. The script applies a ruling on every
     refresh while yfinance's most-recent quarter matches and flags it STALE after
     the next print — a STALE flag means "re-rule this quarter", never "keep".
   - **MW stale/missing** (rule 13): refresh `capacity-mw.json` if a filing supports it.
3. On approval, run live:
   `python3 scripts/refresh_objective_inputs.py <target>`
   This writes the objective cells, bumps Last Updated, and prints TOTAL/tier deltas.
4. **Cite** any flag resolution in the Rating Audit if it changes a blank decision.

## Guarantees (see spec 2026-06-24-refresh-objective-inputs-design.md)

- Foreign-ADR currency mismatch → P/S, EV/EBITDA, FCF-Yield auto-blanked.
- A failed fetch never clobbers an existing value (protects ROIC etc.).
- Extreme/blank EPS YoY is flagged, never auto-written.
- No structural row change → `rebuild_watchlist_formulas.py` not needed.
