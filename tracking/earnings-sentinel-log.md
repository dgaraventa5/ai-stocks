# Earnings sentinel — run log

Append-only. One dated section per event run; quiet runs log a line only when
names were flagged. Written by the `earnings-sentinel` scheduled task
(docs/ops/earnings-sentinel-task.md). Spec:
docs/superpowers/specs/2026-08-13-earnings-sentinel-design.md.

---

## 2026-08-13 — first event run

**Detected:** scope 25, `briefing_due` = [VST (report 2026-08-10, BMO)], `rescore_due` = [VST]. Both phases fired in the same run (see date-lag flag below). Unmerged-branch guard: clean. Branch `earnings/2026-08-13` from `origin/main`.

### Briefed
**⚠️ RULE-9 IMMEDIATE — VST** (GAAP EPS $0.76 vs ~$1.63 consensus = **−53.4% surprise**). Briefing: `per-stock/VST/context-2026-08-13.md`; 5 lines appended to `per-stock/VST/news-log.md`.

The surprise is **non-operating**, not an operating miss: GAAP net income carries a **$472M unrealized loss on hedges expected to settle in future years**, and the YoY net-income decline is attributed to a **$488M increase in unrealized MTM derivative losses**, "mostly offset by higher realized prices and capacity revenue" (8-K 2026-08-07, EX-99.1, p.2). Ongoing Ops Adjusted EBITDA **$1,767M, +31.0% YoY**, roughly in line with the ~$1.76B consensus; generation earnings +68% to $994M. 2026 guidance reaffirmed ($6.8–7.6B EBITDA / $3.925–4.725B FCFbG). Gross-margin sequential check: +70bps on the fuel-margin basis — **no** 500bps flag.

Substantive items: Helix Digital Infrastructure (KKR/KIA/NVIDIA/Vistra, >$10B committed, Vistra up to $1B as founding investor **and preferred power partner**) — announced 2026-06-11, previously only in the 2026-08-07 weekly scan, now in VST's news log; **FERC approval received for Cogentrix** (close still H2 2026, no Item 2.01); FERC June co-location order favorable. Counterweight: **2027 midpoint-opportunity range $7.4–7.8B "trending towards the lower end"** on softer ERCOT forwards (battery-storage build-out + a **data-center interconnection-queue audit**) — the first negative datapoint on the ERCOT demand leg, and the most thesis-relevant item out of this print.

No ratings changed (rule 12). Dimensions surfaced for the next review: **D5** (Helix + ~3,809 MW hyperscaler PPAs argue for the top of the supplier scale), **M1** (2027 low-end guide pressures revisions), **R4** (two-sided: FERC co-location favorable vs. the ERCOT queue audit).

### Re-scored
| Ticker | Before (2026-08-11) | After (2026-08-13) | Δ |
|---|---|---|---|
| VST | 70.65 · rank 23 · ✓✓ | **64.70 · rank 69 · ✓** | **−5.95, −46 ranks, one tier** |

Four Layer-01 peers moved ≤0.16 pts (BE, BWXT, CMI, PSIX) — expected rule-20/24 cohort-percentile ripple from VST's changed inputs, not independent moves.

Input deltas written: Fwd P/E 14.117→14.124 · EV/EBITDA 10.875→10.788 · FCF Yield 3.51→4.59 · P/S 2.645→2.558 · Gross Mgn 38.64→38.31 · FCF Mgn 9.27→11.74 · ND/EBITDA 2.93→3.02 · **Rev YoY 43.4→−5.5** · 50DMA 44.2→45.0 · EV/FCF (reverse-DCF) 40.14→31.80. Category effect: Value 67.4→71.6 and Quality 60.9→58.7, but **Growth collapsed to 22.5** — the entire tier miss is the revenue line.

**Model event: NONE.** `recalc --sync` → "membership & tiers unchanged since last rebalance — snapshot frozen, nothing written". VST is not held (it sat at tradable rank 22, outside both N=15 entry and M=18 exit), so the drop has no portfolio effect. **No ticket generated and none required.** `exit_pending` remains `{}` — no rule-26 clock started.

### Test gate
`python3 -m pytest tests/ -q` → **337 passed, 1 skipped**. Clean; PR not blocked.

### Flags (surfaced, not fixed)

1. **[METHODOLOGY — needs Dom's ruling] Rev YoY is MTM-contaminated for hedge-heavy IPPs.** The −5.5% MRQ revenue YoY that caused the entire 6-point / one-tier drop is GAAP operating revenues, which for Vistra **include unrealized MTM on commodity derivatives**. Backing out the $488M YoY increase in unrealized MTM losses gives ≈$4,505M vs $4,250M ≈ **+6% YoY**; six-month revenue was **+18.0%** and adjusted EBITDA **+31%**. So the input is correct as *defined* (MRQ GAAP revenue YoY, consistent with the prior 43.4% which matched Q1) but arguably garbage as a *growth signal* — the same family as rule 15 (EPS YoY blanked when one-time-dominated), rule 10 and rule 13. Rule 15 covers EPS YoY only; there is no revenue-YoY equivalent. **Not applied** — rules 3 and 8 put a methodology change in Dom's hands. The score above stands as computed.
2. **[TOOLING] `refresh_objective_inputs.py --dry-run` cannot preview value changes.** It reported `touched cols: []`; the live run then changed 8 input columns and moved VST a full tier. `touched` is only computed inside `if not dry_run:` (scripts/refresh_objective_inputs.py:370) so a dry run *always* reports an empty list — it surfaces judgment flags only. The task's step-4 review gate ("review output for obviously-corrupt values") is therefore structurally blind to exactly the kind of change it exists to catch.
3. **[SENTINEL] Report-date lag — yfinance returned the 10-Q date, not the release date.** Detection said 2026-08-10; the Item 2.02 8-K and press release are dated **2026-08-07** (10-Q filed 08-10). The T+0 briefing phase therefore fired at T+6, and both phases collapsed into one run. Still inside the rule-9 one-week window, but if this is systematic rather than name-specific it erodes the sentinel's whole timing premise (spec assumes ~26h/~41h print-to-trade). Worth measuring across the next few reporters.
4. **[DATA] ROIC fetch returned no data** — prior value 7 kept (script flag). **EPS YoY** was already deliberately blank and was preserved, so the rule-15 question is moot for VST this cycle.
5. **[MINOR] Task-prompt drift:** the registered prompt carries one extra sentence over `docs/ops/earnings-sentinel-task.md` (the instruction to flag drift against the canonical copy). No behavioral difference.
6. **[HOUSEKEEPING] No Q2-2026 transcript** captured for VST (rule 7); `per-stock/VST/transcripts/` still lacks `Q2-2026.md`. Call color in the briefing is sourced from a secondary summary, with the press release as the primary source of record.

Not applicable this run: no Layer-9 capacity-cohort names (rule 13), no TTM-vs-MRQ quality divergence >10pts (TTM FCF margin 11.74% vs H1 6.7% ≈ 5pts), no briefing-phase deferral (1 name, limit 8).
