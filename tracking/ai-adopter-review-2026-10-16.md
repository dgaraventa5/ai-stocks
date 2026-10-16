# AI-adopter progress review — 2026-10-16

Dom's ask: find 10 stocks in the news for applying AI in their own businesses,
pick the most promising tradable ones, and rescore them for their progress.

## The 10

Seven were already on the Watchlist; three are new to Layer 10. All ten are
plain US listings (no exchange suffix, not on `BROKER_UNTRADABLE`), so they pass
the rule-30 tradability filter.

| Ticker | Why it is in the news for AI | Status |
|---|---|---|
| PLTR | AIP/agent deployment ("AI FDE"), revenue +93% Q2 | Watchlist |
| NOW | AI contract value passed $1B; MCP server / Action Fabric GA | Watchlist |
| CRM | Agentforce ARR >$1.5B (definition widened); AIforce/Claudeforce | Watchlist |
| APP | Axon ad model; self-serve ecommerce ads | Watchlist |
| TEM | AI data licensing; agentic Lens; AZ foundation model | Watchlist |
| RDDT | Data licensing to AI labs; Max AI ad campaigns | Watchlist |
| HOOD | Agentic trading accounts (100k+), Robinhood Agents | Watchlist |
| SHOP | Checkout layer for AI shopping agents (Meta Muse, UCP) | **New** |
| LMND | AI-native insurer; claims-cost edge | **New** |
| UPST | AI lending model; 91% of loans fully automated | **New** |

Briefings: `per-stock/{T}/context-2026-10-16.md`.

## Score changes (recalc, percentile mode)

| Ticker | TOTAL before → after | Rank (all) | Tier | Driver |
|---|---|---|---|---|
| PLTR | 73.00 → 74.30 | 17 → 11 | ✓✓ | M2 2→3; peer percentile lift from 3 new Layer-10 names |
| NOW | 59.29 → 64.24 | 122 → 80 | ✓ | M2 1→5, M3 3→5 (CEO $3M buy); R1 up; R3, R4 down |
| CRM | 62.45 → 63.79 | 93 → 86 | ✓ | M2 2→4, R1 4→5, M1 4→3 |
| APP | 70.23 → 70.74 | 30 → 29 | ✓✓ | R1 4→5, R3 5→4 |
| TEM | 55.00 → 52.11 | 161 → 180 | ? | D1 5→3, R3 4→2 (not net cash), R4 3→2 (DOJ civil probe) |
| RDDT | 72.70 → 72.55 | 19 → 20 | ✓✓ | M2 4→3 |
| HOOD | 58.75 → 55.96 | 128 → 152 | ✓ | M2 5→2; M1 4→5; EPS YoY ruled to ex-item 19% |
| SHOP | new → 57.01 | 144 | ✓ | |
| UPST | new → 54.77 | 163 | ? | |
| LMND | new → 42.58 | 206 | ? | |

Portfolio: `refresh_targets --dry-run` FREEZES (no membership or tier change);
rule-25 gate green. RDDT now sits at tradable rank 18, the last rank before exit.

## Rule-15 rulings written (`00-master/eps-yoy-overrides.json`)

TEM blank, NOW blank, HOOD ex-item +19%, SHOP ex-item +30% (pretax proxy). All
for quarter ending 2026-06-30; all go STALE at the Q3 prints (Oct 27 – Nov 3).

## Open questions for Dom

1. **Layer-10 D5 consistency (rule-12 stress test).** Under the supplier lens
   Dom reaffirmed today for TSLA, five agents independently said PLTR, NOW, CRM
   and TEM (all at 3) and APP and HOOD (at 2) read as 1–2. WDAY, ADBE, INTU,
   ADSK and TSLA already sit at 1. I held every D5 rather than move a few names
   on a question that applies to the whole layer. Same for D4 (software capex
   is steady-state; many Layer-10 names carry 4).
2. **NOW R4 = 2** is the literal band for an active DOJ investigation, but it is
   a 2024 matter with no escalation; 3 is defensible.
3. **Insurer / lender inputs.** LMND revenue growth is ~72% a reinsurance
   accounting change and its EV/FCF has a near-zero denominator; UPST's FCF and
   leverage inputs include loan purchases. Both are kept mechanical (no
   convention exists to blank them) and both score low anyway.
4. **ROIC for payments/lending names.** `roic.py` uses yfinance operating
   income, which for SHOP excludes transaction and loan losses (ROIC ~15% vs
   ~11.7% on GAAP). Possible systematic issue for similar names.
5. **HOOD**: *George v. Robinhood* (0:26-cv-62482, S.D. Fla., 2026-09-08) is a
   self-represented securities claim inside the 90-day window. No entry hold
   added; HOOD is far from entry anyway.

## Docket checks

The agents' `litigation_check.py` runs timed out for RDDT, PLTR, NOW and LMND;
all four were re-run in the main session the same day. None found a federal
securities docket in RECAP or a disclosure mismatch (RECAP is incomplete: it
does not list RDDT's known 3:25-cv-05144 class action). LMND shows a run of
individual policyholder suits in Texas federal courts (Aug–Sep 2026), which
read as ordinary claims disputes. No R4 change.
