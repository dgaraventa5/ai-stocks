# 13F-Delta Plan — 2026-08-28

**Purpose:** Scope the 13F follow-up work the 2026-08-28 weekly scan flagged, reconcile the two different fund lists in the repo, and surface two data-integrity issues found while scoping. **Execution requires SEC EDGAR (primary-XML parsing), which is network-blocked from cloud sessions** — this is the plan for an on-network session to run, plus the offline-fixable flags.

---

## 0. Why this plan exists — the two fund lists don't match

There are **two separate, non-overlapping tracked-fund lists** in the repo, and the weekly scan's "worth a `/thirteenf-delta` pass" recommendation conflated them:

| List | Where | Funds | What it does |
|---|---|---|---|
| **`/thirteenf-delta` skill** | `.claude/commands/thirteenf-delta.md` | **Situational Awareness LP (SALP)** only — CIK 0002045724 | Deep-processes holdings → adds a sheet to `13f-tracking.xlsx` → `/score-stock` for new names. Drives the rule-13/14 stress tests. |
| **Weekly-scan fund watch** | `scripts/weekly_scan_runner.py` `TRACKED_FUNDS` + `13f-tracking.xlsx` "Filers to watch" | **6 mega-funds:** Berkshire, Baillie Gifford, Tiger Global, Coatue, Whale Rock, Lone Pine | Checks *filing status* only (has fund X filed its Q2 13F yet?). No holdings processing. "Last 13F pulled" is **blank** for all six — never deep-processed. |

**Consequence:** the divergence pattern the scan flagged (Berkshire/Baillie-Gifford adding GOOGL; Tiger Global + Whale Rock trimming NVDA/AVGO/GOOGL into Cerebras/AMD) is among the **six mega-funds**, none of which the `/thirteenf-delta` skill actually tracks. Running the skill as-written would process **SALP only** and would not touch that divergence. This plan separates the two workstreams.

---

## 1. Workstream A — SALP Q2 2026 (the skill's actual job)

**State:** `13f-tracking.xlsx` has SALP processed through **2026-Q1** (sheet `SALP-2026-Q1`, filed 2026-05-18, period 2026-03-31). SALP's **Q2 2026** 13F-HR (period 2026-06-30) was due ~2026-08-14 and is **not yet in the workbook** — likely filed, not yet pulled.

**Steps (on-network):**
1. Query EDGAR submissions API for CIK 0002045724; confirm a Q2 2026 13F-HR exists and its accession/filing date.
2. Parse the INFORMATION TABLE XML with `lxml` (option rows = notional value of underlying, not premium — per the existing sheet convention).
3. Add sheet `SALP-2026-Q2`; compute deltas vs `SALP-2026-Q1` (new positions, exits, top-10 adds/trims by $ value, and the "Shares Δ vs prior Q" column).
4. **Watch specifically** (SALP drove rules 13 and 14): (a) the bitcoin-miner-pivot / neocloud cohort (rule 13 EV/MW), (b) any *new* put targets vs the Q1 `SMH` put and the rule-14 "biggest put targets = our top-6 names" finding, (c) any new long that isn't on the Watchlist → `/score-stock`.
5. Report per the skill: total $ value, # holdings, top-3 changes, thesis-relevant moves in/out of our Watchlist names.

**Blocked-offline:** all of it (EDGAR XML). No fabrication — if a Q2 filing can't be confirmed, report "not confirmed filed," don't guess (rule 3).

---

## 2. Workstream B — the six mega-fund divergence (decision required first)

The scan surfaced a real, three-weeks-running signal: **tracked funds rotating out of mega-cap AI-compute concentration.** Consolidated from the last two scans (all figures **secondary-aggregator sourced**, NOT primary-XML-verified — rule 1 bars treating them as filing-verified):

- **Berkshire Hathaway** — added ~24.5M GOOGL (~+45% value, ~$28.2B stake).
- **Baillie Gifford** — added NVDA, GOOGL, Axon; trimmed AMZN/MELI/Spotify/Shopify/Netflix.
- **Tiger Global** — trimmed GOOGL ~45%, NVDA ~7%, AVGO ~$690M; new Cerebras (~$660M), AMD (~$392M).
- **Whale Rock** — **cut NVDA ~64%** (1.04M→377K sh); AMD top buy (now top-5); new SNOW/TWLO. *(Corrects last week's "not confirmed filed" — it filed on-time 2026-08-14.)*
- **Coatue** — value $48.63B (up from $29.01B); new SpaceX/Intel/Cerebras/Hut 8.
- **Lone Pine** — top holdings NBIS/ASML/STX; adds incl. GOOGL (+42.8%), TeraWulf.

**Decision required (do NOT execute either path without Dom's call — this changes a governed process):**
- **Option 1 — keep scan-status-only.** These six stay a *filing-status* check in the weekly scan; the divergence is narrative context, not processed into `13f-tracking.xlsx`. Lowest effort; the standing convention.
- **Option 2 — promote to deep processing.** Add the six to the `/thirteenf-delta` skill's tracked list and process their Q2 holdings into `13f-tracking.xlsx` (new sheets), same as SALP. Higher effort; makes the divergence a first-class, diff-able dataset. Only worth it if Dom wants to *act* on cross-fund positioning, not just observe it.

**Recommendation:** Option 1 for now (the divergence is directional/observational and the figures are secondary-sourced), but do a **one-time primary-XML verification pass** on the two sharpest moves — **Whale Rock's ~64% NVDA cut** and **Tiger Global's GOOGL ~45% trim** — once EDGAR is reachable, to confirm the pattern is real before it informs any thinking on our own NVDA/GOOGL/AVGO exposure. If it survives verification and Dom wants it tracked quarterly, promote to Option 2 then.

---

## 3. ⚠️ Data-integrity flags found while scoping (offline-fixable / verify-first)

1. **Baillie Gifford CIK mismatch.** `scripts/weekly_scan_runner.py` uses **`0001048268`** for Baillie Gifford (and reported it "confirmed filed" this week using that CIK); `13f-tracking.xlsx` "Filers to watch" lists **`0001097278`**. These are different entities/registrants. **Before any Baillie Gifford pull, verify which CIK is the correct 13F filer** (both may exist as related registrants; only one files the 13F we want). Whichever is correct, **reconcile the two sources so they match** — a wrong CIK silently checks the wrong entity's filing status. Do not assume the scan's CIK is right just because it returned a result.
2. **"Filers to watch" `Last 13F pulled` is blank for all six.** If Option 2 is ever chosen, that column should be populated as sheets are added, so staleness is visible. No action under Option 1.

---

## 4. Offline vs. on-network split

| Task | Offline now? | Notes |
|---|---|---|
| This plan + the two integrity flags (§3) | ✅ done | Baillie Gifford CIK reconciliation is a code/data edit — can be fixed offline once the correct CIK is confirmed (needs one EDGAR lookup to confirm). |
| SALP Q2 pull + delta (§1) | ❌ EDGAR | The skill's core job. |
| Mega-fund primary verification (§2) | ❌ EDGAR | Whale Rock NVDA cut + Tiger Global GOOGL trim first. |
| Option 1 vs 2 decision (§2) | 🧑 Dom | Governance decision, not a mechanical step. |

**Bottom line:** nothing here can be *executed* against filings from a cloud session. The offline deliverable is this scoped plan + the CIK-mismatch flag (§3.1), which prevents a silent wrong-entity check on the next Baillie Gifford status pull.
