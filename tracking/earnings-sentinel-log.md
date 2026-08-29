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

---

## 2026-08-26 — briefing phase (NVDA)

**Detection:** scope 25, `briefing_due: [NVDA @ 2026-08-26 AMC]`, `rescore_due: []`, `flagged: {}`. Unmerged-branch guard: clean (no `earnings/*` branches existed). Branched `earnings/2026-08-26` from `origin/main` @ `1260bd3`.

### Briefed
**NVDA** — Q2 FY2027 (quarter ended 2026-07-26), reported AMC today. Briefing: `per-stock/NVDA/context-2026-08-26.md`; news-log line appended. Primary sources: 8-K acc 0001045810-26-000073 (Items 2.02/9.01), EX-99.1 press release + EX-99.2 CFO Commentary, both saved to `per-stock/NVDA/filings/`. The 10-Q (acc 0001045810-26-000075) was also filed today and is **not** yet parsed — flagged in the briefing's watch items.

**Rule-9 immediate: NOT triggered.** Revenue $96,221M vs ~$92.07B consensus = **+4.5%**; non-GAAP EPS $2.22 vs ~$2.09 = **+6.2%**; gross margin 75.0% vs 74.9% = **+10bps** sequential. All three thresholds (±15% / ±15% / >500bps) clear by wide margins. Basis note recorded in the briefing: GAAP EPS $2.46 against the $2.09 street number would read +17.7%, but street consensus is non-GAAP and the $0.24 gap is $7.8B of equity-securities gains — the correct comparison is $2.22 vs $2.09.

Headline: revenue +18% q/q / +106% y/y; Data Center $89.0B (+117% y/y, now 92.5% of revenue) with ACIE $40.3B (+138% y/y) outgrowing Hyperscale $48.7B (+102% y/y); Edge Computing $7.2B. **Q3 guided $108.0B ±2% assuming zero China Data Center compute**, gross margin 74.0% (−100bps). China Hopper shipments were <1% of Data Center revenue in Q2.

New disclosures that move the risk shape rather than the demand thesis: purchase commitments **$119B → $279B** "primarily related to the procurement of memory" (total future commitments $366B); guarantees **$108.5B** ($105B SB Energy/PORTS-Pike + $3.5B AI-cloud land/power/shell), first tranche effective FY2029, exposure declining as OpenAI pays; PORTS-Pike reframed by the company as revenue-anchoring (≈1.5M GPUs ≈ $150–200B of NVIDIA revenue per infrastructure generation); $36B AI-cloud agreements with revenue-share participation; $20B of third-party DC leases NVDA expects to reassign; $500B+ third-party capital platforms (Apollo/BlackRock/Blackstone/Brookfield/Goldman/KKR) **subject to definitive agreements, i.e. unsigned**; $2.944B Groq payment with "NVIDIA Groq 3 LPX" now in full production; $25B senior notes issued (LT debt $7.5B → $32.4B); DSO 60 days (from 45) and Q2 FCF $21.3B (from $48.6B).

No ratings changed (rule 12). Dimensions surfaced for the next review: **R1** (two-sided — ACIE diversification vs. weaker credits + the OpenAI guarantee), **R3** (the off-balance-sheet load ND/EBITDA cannot see), **D1** (DC at 92.5%), **D2/D3** (memory lock-in vs. the 100bps margin give-back), **D5** (reinforced and now quantified), **R4** (China risk largely realized, so forward sensitivity falls). **Rule 15 checked and does NOT trigger** — GAAP EPS +128% y/y is equity-gain-inflated but non-GAAP EPS grew +120% on the same base, so the YoY change is operating-dominated, not one-time-dominated. Recorded so it is not re-litigated at the rescore.

### Re-scored
**None.** `rescore_due` was empty — by design: rule 31 puts the mechanical re-score on the **first post-reaction close**, i.e. the 2026-08-27 run. State after this run: `NVDA: {briefed: 2026-08-26}`.

**Model event: NONE** (no scoring pass ran). **No ticket generated and none required.** `exit_pending` remains `{}` — no rule-26 clock started; `tracking/performance-config.json` untouched.

### Test gate
`python3 -m pytest tests/ -q` → **386 passed, 1 skipped in 55.06s**. Clean; PR not blocked.

### Flags (surfaced, not fixed)

1. **[ENVIRONMENT — cost me ~40 minutes, worth a permanent fix] Cold-filesystem stall makes the test gate look hung.** `tests/test_privacy_live_trading.py::test_no_real_identifiers_in_any_tracked_file` reads all 1,107 tracked `*.py/*.md/*.json/...` files; on this run a single file in index range 800–1000 took **~125 seconds** to read cold, and the suite appeared to hang for multiple timeout cycles. After the files were warmed, the identical full suite finished in **55 seconds**. Cause is almost certainly on-demand materialization (iCloud/Desktop) or Spotlight, not the test — note the untracked `.metadata_never_index` sitting in the repo root, which suggests this has been hit before. **Suggested fix for Dom:** keep `.metadata_never_index` (and commit it, or add it to `.gitignore` deliberately), and consider whether `~/Desktop/ai-stocks` should be excluded from iCloud Drive sync. A scheduled 18:30 run that cannot distinguish "hung" from "cold cache" will keep burning its budget on this.
2. **[SENTINEL — good news, closes last run's flag #3] Report-date detection was exact this time.** The 2026-08-13 run flagged that yfinance had returned VST's 10-Q date rather than its release date, firing the briefing at T+6. For NVDA the detected report date (2026-08-26) matched the Item 2.02 8-K date exactly, so the briefing fired at **T+0** as the spec intends. One clean datapoint against one bad one — the lag looks name-specific (Yahoo statement lag on VST) rather than systematic, but it is still worth watching across the next few reporters before calling it resolved.
3. **[WORKSPACE] Dom's uncommitted work was stashed and restored, not discarded.** The working tree held four locally-modified tracked files (`.claude/commands/refresh-context.md`, `tracking/live-status.json`, `tracking/live-vs-model.json`, `tracking/performance-series.json`) that blocked `git checkout -b … origin/main`. They were stashed as `earnings-sentinel 2026-08-26: temp stash of Dom's uncommitted work` and restored onto the original branch at the end of the run — **verify with `git stash list` (should be empty) and `git status`**. None of them were staged or committed on the earnings branch.
4. **[HOUSEKEEPING] The repo has a large backlog of untracked per-stock artifacts** from other sessions (AVAV/BW/HIVE/MPWR/PSIX/PUMP/RCAT/SHAZ/SWKS/SYM/TE/WYFI context files and filings, plus `scripts/litigation_check.py`, `tests/test_litigation_check.py`, `tracking/litigation-sweep-2026-08-24.md`, `tracking/rating-refresh-skipped.md`). **Deliberately not staged** — the task's "stage explicit paths" rule means this run committed only its own NVDA outputs. Flagging so the backlog does not silently ride along in some future run that is less careful.
5. **[HOUSEKEEPING] No Q2 FY27 transcript captured** for NVDA (rule 7); `per-stock/NVDA/transcripts/` still lacks the Q2 FY2027 file. The call was held 5pm ET today, after the release; the briefing is sourced entirely from the primary 8-K exhibits, so nothing in it depends on call color.
6. **[MINOR] Task-prompt drift:** the registered scheduler prompt carries one extra sentence over `docs/ops/earnings-sentinel-task.md` (the instruction to flag drift against the canonical copy). Same as last run — no behavioral difference.

Not applicable this run: no Layer-9 capacity-cohort names (rule 13), no TTM-vs-MRQ divergence check (no objective refresh ran), no briefing-phase deferral (1 name, limit 8).

---

## 2026-08-27 — rescore phase (NVDA)

**Detection:** scope 25, `briefing_due: []`, `rescore_due: [NVDA @ 2026-08-26 AMC]`, `flagged: {}`. Unmerged-branch guard: clean (no `earnings/*` branches unmerged into `origin/main` — 2026-08-26's branch merged as PR #45). Branched `earnings/2026-08-27` from `origin/main` @ `245241a`.

This is the second half of the NVDA Q2 FY2027 event: the briefing ran T+0 on 2026-08-26, this run is the first post-reaction close, exactly as rule 31 specifies.

### Briefed
**None.** `briefing_due` was empty; NVDA was already briefed 2026-08-26 (`per-stock/NVDA/context-2026-08-26.md`). No briefing-phase deferral.

### Re-scored

**NVDA** — chain run once: `refresh_objective_inputs.py NVDA` (dry-run reviewed first) → `momentum_50dma.py NVDA` → `refresh_reverse_dcf.py NVDA` → `recalc_watchlist.py --sync`.

| | Before | After | Δ |
|---|---|---|---|
| TOTAL | 84.02 | **83.87** | −0.15 |
| Tier | ✓✓ | ✓✓ | unchanged |
| Rank (tradable universe) | 1 | **1** | unchanged |

Category detail unchanged except Value 64.77 → 64.02. Objective inputs written: `last_updated` 2026-07-16 → 2026-08-27; `fwd_pe` 16.164 → 15.246; `ev_ebitda` 30.08 → 30.411; `fcf_yield` 2.37 → 2.16; `ps` 19.817 → 21.717; `50dma` 56.7 → 57.5. Reverse-DCF EV/FCF refreshed (1 processed, 0 blank).

**Cohort ripple:** one other name moved — **MPWR** 62.35 → 62.50 (✓ → ✓, no tier change), a Layer-06 percentile re-rank off NVDA's changed Value metrics (rule 20, expected). No other name in the 214-name universe moved by more than 0.005.

**Model event: NONE.** `recalc --sync` reported "membership & tiers unchanged since last rebalance — snapshot frozen, nothing written". **No ticket generated and none required** (rule 29 — a ticket only hooks a real model event). `exit_pending` remains `{}`; `tracking/performance-config.json` byte-untouched. `tracking/score-history.csv` appended 214 rows dated 2026-08-27 (rule 28 panel).

**Rule-9 immediate:** not triggered (established at the briefing — revenue +4.5% / non-GAAP EPS +6.2% vs consensus, gross margin +10bps sequential; all three well inside the thresholds).

### Test gate
`python3 -m pytest tests/ -q` → **386 passed, 1 skipped in 1350.04s (22m30s)**. Clean — PR not blocked. No rule-26 exit-clock caveat applies (no clock started this run).

### Flags (surfaced, not fixed)

1. **[STRUCTURAL — the important one] The mechanical re-score captured none of the reported quarter.** Yahoo's latest statement quarter for NVDA is still **2026-04-30** (Q1 FY27); the quarter just reported (ended 2026-07-26, released 2026-08-26) is **not in yfinance's statements yet**. So every statement-derived input was a no-op: gross margin stayed **74.14%** (the print was 75.0%), FCF margin 46.97%, Rev YoY **85.2%** (the print was +106% y/y), EPS YoY 210.6%, ND/EBITDA −0.24 — all pre-print values. The six inputs that did move are **price/market-cap derived only** (fwd P/E, EV/EBITDA, FCF yield, P/S, 50DMA), which is why the score barely moved and moved *down* despite a beat: the price rose, so the multiples got more expensive against unchanged trailing fundamentals. This is not a bug in this run — the spec anticipates it and makes the weekly scan the rule-9 catch-all — but it means **rule 31's rescore phase currently re-prices the multiple rather than re-scoring the business**, and the "print-to-trade in ~26h" framing overstates what the T+1 pass can actually see. Worth Dom deciding whether the rescore phase should either (a) defer until statement data lands, (b) gate on a freshness check of `quarterly_income_stmt`'s latest column vs. the report date, or (c) be explicitly redefined as a price-input refresh with the fundamentals following on the weekly scan. Option (b) is the cheap one and would make the log honest automatically.
2. **[DATA] ROIC fetch returned no data** for NVDA — script kept the prior value 103.061 (flagged by the refresh script, not silently). Same behavior as the VST run on 2026-08-13; two-for-two suggests the ROIC path is fragile rather than name-specific.
3. **[ENVIRONMENT — recurrence of 2026-08-26 flag #1] The test gate took 22m30s against 55s warm.** Same cold-filesystem stall in `tests/test_privacy_live_trading.py::test_no_real_identifiers_in_any_tracked_file` (reads every tracked text file). The suite passed cleanly, but a scheduled run burns ~22 minutes of wall clock on materialization, not computation. The suggested fix from last run stands and is now a repeat offender: commit `.metadata_never_index` (still sitting untracked in the repo root) or deliberately `.gitignore` it, and consider excluding `~/Desktop/ai-stocks` from iCloud Drive sync.
4. **[WORKSPACE] Dom's uncommitted work was stashed, not discarded — and this run left it stashed.** Four locally-modified tracked files blocked `git checkout -b … origin/main`: `.claude/commands/refresh-context.md`, `tracking/live-status.json`, `tracking/live-vs-model.json`, `tracking/performance-series.json`. Stashed as **`earnings-sentinel 2026-08-27: pre-branch stash of local tracked mods`** off branch `site/ew-roster-label`. Note `tracking/performance-series.json` in that stash is **newer than main** (series through 2026-08-24 vs. main's 2026-08-19) — it is a local daily-refresh result worth keeping, not scratch. **Action for Dom: `git checkout site/ew-roster-label && git stash pop`.** Unlike the 2026-08-26 run this one did *not* auto-restore, because the stash belongs to a different branch (`site/ew-roster-label`, which carries two unpushed site commits) and popping it onto the earnings branch would have mixed unrelated work into this PR.
5. **[HOUSEKEEPING] The untracked backlog from other sessions is unchanged and again deliberately not staged** — AVAV/BW/HIVE/MPWR/PSIX/PUMP/RCAT/SHAZ/SWKS/SYM/TE/WYFI context files and filings, plus `scripts/litigation_check.py`, `tests/test_litigation_check.py`, `tracking/litigation-sweep-2026-08-24.md`, `tracking/rating-refresh-skipped.md`. Third consecutive run flagging this; the MPWR and SHAZ context files in particular cover names that appear in this run's score panel.
6. **[MINOR] Task-prompt drift:** the registered scheduler prompt still carries one extra sentence over `docs/ops/earnings-sentinel-task.md` (the instruction to flag drift against the canonical copy). Same as the last two runs — no behavioral difference.
7. **[MINOR] Wall-clock rolled past midnight** during the test gate. All artifacts are stamped **2026-08-27** (branch, score-history rows, `last_updated`) — the run is the 2026-08-27 run; only the commit timestamp falls on 08-28.

Not applicable this run: no Layer-9 capacity-cohort names (rule 13 — NVDA is Layer 06); no TTM-vs-MRQ quality divergence >10pts (TTM gross margin 74.14% vs the 75.0% print ≈ 0.9pt — though see flag 1: the TTM figure does not yet include the printed quarter, so this check is weaker than it looks); no briefing-phase deferral (0 names due).

### Addendum — 2026-08-28: re-run after Yahoo caught up (Dom-approved, option 1)

Flag 1 above turned out to be **a one-run timing miss, not a structural blind spot** — and the fix is cheap. Re-checked Yahoo the next morning at Dom's request:

- **Statement tables are still stale** — `quarterly_income_stmt` / `_balance_sheet` / `_cashflow` all still top out at **2026-04-30**.
- **The `info` TTM fields have caught up** — `mostRecentQuarter` now reads **2026-07-26**, the printed quarter; `revenueGrowth` 1.059 matches the press release's +106%; TTM revenue moved ~$253.5B → **$302.97B**.

The two Yahoo paths update on **different schedules**, and the one `refresh_objective_inputs.py` actually reads is the one that came current overnight. So the correct diagnosis is a ~1-day lag on the `info` path, not the multi-day/multi-week statement lag assumed in flag 1.

**Re-ran the full chain on the same branch.** Dry run showed 11 changed inputs vs. the 6 of 2026-08-27:

| Input | 2026-08-27 (T+1) | 2026-08-28 (T+2) |
|---|---|---|
| P/S | 21.717 | **17.314** |
| EV/EBITDA | 30.411 | **27.181** |
| Rev YoY % | 85.2 | **105.9** |
| Gross Mgn % | 74.14 | **74.67** |
| FCF Mgn % | 46.97 | **39.30** |
| EPS YoY % | 210.6 | **125.9** |
| ND/EBITDA | −0.24 | **−0.12** |
| Fwd P/E | 15.246 | 14.323 |
| FCF Yield % | 2.16 | 2.27 |
| 50DMA % | 57.5 | 58.3 |

The FCF-margin drop and the ND/EBITDA move are the Q2 facts the briefing flagged arriving in the data — $21.3B quarterly FCF (from $48.6B) and the $25B senior-notes issuance.

**Result:** NVDA **83.87 → 84.22**, tier **✓✓ unchanged**, tradable rank **1 unchanged**. Value 64.02 → 68.03 (P/S re-based on the higher TTM revenue); Quality 94.72 → 92.45 (FCF margin). Four sub-0.35 cohort ripples, no tier crossings: RMBS, AVGO, MRVL, MPWR.

**Model event: still NONE** — `--sync` again reported "membership & tiers unchanged since last rebalance — snapshot frozen, nothing written". **No ticket generated and none required.** `exit_pending` still `{}`; `performance-config.json` byte-untouched. `score-history.csv` gained 214 rows dated 2026-08-28 (the 2026-08-27 rows are retained — the panel is append-only, never rewritten, rule 28). ROIC again returned no data and kept 103.061 (flag 2 now three-for-three).

The projection was computed on a scratch copy before applying and matched the live result to the cent (84.22), so the sheet was never speculatively written.

**Revised recommendation for flag 1.** The gate is smaller than first proposed: have the rescore phase compare `info['mostRecentQuarter']` against the detected report date and defer one run when the quarter has not landed. That single check would have deferred this event exactly one day and captured all 11 inputs on the first try, with no change to rule 31's cadence. Options (a) and (c) from the original flag are over-corrections given the lag is ~1 day, not open-ended. **Still Dom's call** (rules 3/8) — not applied.

**Test gate (addendum run):** `python3 -m pytest tests/ -q` → **386 passed, 1 skipped in 6.15s**. That number settles flag 3: the identical suite took **1350s cold and 6.15s warm — a 219× spread**, which is conclusively filesystem materialization rather than anything in the tests. A scheduled 18:30 run always hits the cold path. Committing `.metadata_never_index` (or excluding `~/Desktop/ai-stocks` from iCloud Drive sync) is now a well-evidenced fix, not a guess.
