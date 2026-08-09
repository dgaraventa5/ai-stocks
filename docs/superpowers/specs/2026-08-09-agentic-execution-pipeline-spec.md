# Spec: Agentic execution pipeline — Robinhood MCP, trade tickets, auto-reconciliation

**Date:** 2026-08-09
**Status:** Proposal — nothing trades until Dom completes Phase 0 and approves the Phase 2 go-live checklist (§F)
**Depends on:** portfolio construction v2 (rank selection + inverse-vol sizing, live 2026-08-07)

## 0. Goal and the one fixed boundary

Goal: **agentic portfolio management with minimal manual interaction.** The model
already makes every decision (rank selection N=15/M=18, inverse-vol sizes, exit
clocks, hysteresis). Today the output dies in a spreadsheet; this pipeline carries
it to a real Robinhood Agentic account and back.

Target steady state: **Dom's total manual work is one command per rebalance event**
(historically ~1–3×/month) **and zero manual bookkeeping.** Everything else —
signal, ticket, reconciliation, performance tracking, anomaly halt — is automated.

**Execution boundary (invariant — treat like the site privacy gate):**
- Claude (any session, any mode) uses the Robinhood MCP **read tools only**
  (positions, balances, orders, history). Claude never calls an order-placement
  tool. This is an Anthropic platform rule, not a project preference; designing
  around it is out of scope.
- The submit step belongs to a **deterministic, non-LLM executor script that Dom
  runs** (§C). No LLM sits between the ticket and the order. This is deliberately
  *better* than "another AI agent executes": the executor cannot misread a news
  page, hallucinate a ticker, or reinterpret instructions — it can only transmit
  a validated ticket or refuse.

Risk posture (Dom, 2026-08-09): Agentic account funded **only with capital Dom is
fully prepared to lose**; the account cap is set in Phase 0 and enforced by the
executor (§C3). No margin, no options, no crypto — long equities from the
watchlist only.

## A. Robinhood MCP connection

- Endpoint: `https://agent.robinhood.com/mcp/trading` (Robinhood agentic trading,
  supports Claude Code as a first-class client).
- Phase 0 (Dom, one-time, desktop required): create the Agentic account inside the
  primary individual account, fund it with the risk-capital cap, and add the MCP
  server to this project (`claude mcp add --transport http robinhood
  https://agent.robinhood.com/mcp/trading`), completing OAuth interactively.
- **Tool-usage policy in this repo:** read tools (accounts, positions, balances,
  orders, transactions) are approved for Claude in any session. Order/write tools
  are never called by Claude; they are exercised only by `execute_ticket.py` run
  by Dom. If a future permissions config can deny write tools to Claude at the
  harness level, do it (belt and suspenders).
- **Open question O1:** whether the OAuth session survives headless/cron runs.
  If not, reconciliation (§D) runs in Dom-attended sessions + weekly-scan instead
  of the daily cron, and the spec's cadence degrades gracefully (flag, don't fake).

## B. Trade ticket generation (automated, Claude-side)

### B1. Hook

`refresh_targets.refresh()` already fires discrete rebalance events
(`log_rebalance(..., kind=...)`, freeze-safe). Add a post-event step: whenever a
real run fires (`fire=True`, any `kind` except shadow-only updates), call
`scripts/generate_trade_ticket.py` with the new target weights.

### B2. Share-delta computation

- Current holdings: from the latest reconciliation snapshot (§D), i.e. **actual
  account state**, never assumed from the previous event (partial fills and drift
  must not compound).
- Account equity: live from MCP read tools at generation time (cash + positions).
- Delta per name: `target_weight × equity − current_market_value`, converted to
  fractional shares at the reference price. Orders below `MIN_ORDER_NOTIONAL`
  ($25 default) are suppressed (dust guard) and logged.
- Reference price: last close from the existing price path; order type is a
  **marketable limit** — buy at ref × (1 + `LIMIT_TOL`), sell at ref × (1 −
  `LIMIT_TOL`), `LIMIT_TOL = 0.75%` default, time-in-force DAY. Never market
  orders (a halted/gapping name fills a market order at the worst print).

### B3. Ticket format

`tracking/live/tickets/ticket-{YYYY-MM-DD}-{event_kind}.json` (gitignored — see §E):

```json
{
  "ticket_id": "2026-08-12-membership",
  "created_at": "2026-08-12T21:30:00Z",
  "expires_at": "2026-08-14T20:00:00Z",
  "basis_event": {"date": "2026-08-12", "kind": "membership", "reason": "..."},
  "account_equity_at_gen": 0.0,
  "orders": [
    {"ticker": "NVDA", "side": "sell", "shares": 1.2345,
     "limit_price": 181.25, "tif": "day", "notional_est": 223.71}
  ],
  "checksum": "sha256 of canonical orders array"
}
```

- Tickets are **append-only artifacts**: a regenerated ticket is a new file; stale
  ones expire via `expires_at` (48h default) and are refused by the executor.
- Foreign local-line names (rule 27: 6954.T, KGX.DE, …) are **not tradeable on
  Robinhood** — if one enters the roster, the ticket carries it in an
  `untradeable` section (flagged, excluded from orders, weights renormalized over
  the tradeable set with the same cap/floor logic). Flag loudly; don't silently
  drop (rule 3).

## C. Executor (deterministic, Dom-run)

### C1. What it is

`scripts/execute_ticket.py` — a plain Python MCP client (JSON-RPC over HTTP with
the stored OAuth token). **No LLM anywhere in it.** Reads a ticket, validates,
transmits, writes a receipt. Dom's entire interaction:

```bash
python3 scripts/execute_ticket.py --ticket tracking/live/tickets/ticket-2026-08-12-membership.json --confirm
```

Default (no `--confirm`) is dry-run: print the order table and every validation
result, send nothing.

### C2. Validation gates (all must pass; any failure → refuse whole ticket)

1. Checksum matches; ticket not expired; ticket not already executed (receipt
   file absent).
2. Every ticker ∈ current Targets roster (allowlist read from the workbook —
   the executor cannot be pointed at an arbitrary symbol).
3. Per-order notional ≤ `MAX_ORDER_NOTIONAL`; total buy notional ≤ available
   cash; total turnover ≤ `MAX_TURNOVER_PCT` of equity (50% default; a full
   redeploy needs `--allow-full-turnover`).
4. Kill switch absent: if `tracking/live/trading-halt.flag` exists, refuse and
   print why it was raised.
5. Live-price sanity: refuse any order whose limit is >3% away from the current
   quote (stale ticket in a moving market → regenerate, don't chase).

### C3. Caps live in config, not flags

`tracking/live/executor-config.json`: `ACCOUNT_CAP` (max equity this system may
manage; executor refuses buys that would exceed it), `MAX_ORDER_NOTIONAL`,
`MAX_TURNOVER_PCT`, `LIMIT_TOL`. Changing caps is a deliberate edit, not a CLI
flag typo.

### C4. Receipt

On send, write `tracking/live/receipts/receipt-{ticket_id}.json`: per-order
Robinhood order IDs + statuses. The receipt is what reconciliation verifies
against; its existence is also the executed-once guard (C2.1).

### C5. Phase-3 option: scheduling the executor (Dom-owned decision)

Dom *can* cron the executor to reach zero-touch. Recommendation: **don't, until
Phase 2 has run ≥3 months / ≥6 tickets with zero validation failures and zero
recon anomalies.** The one manual command is the cheapest circuit breaker
available, and this system's trade frequency makes it nearly free. If Phase 3 is
activated anyway: kill-switch + caps become the only human control, so add
push-notification on every execution and auto-halt on ANY validation warning
(not just hard failures). This is a Dom decision to log in the Rating Audit
spirit — dated, reasoned, reversible.

## D. Reconciliation & monitoring (automated, Claude-side, read-only)

`scripts/reconcile_account.py`, run in weekly-scan + (if O1 allows) the daily cron:

1. **Fill verification:** open receipts → poll order status → mark filled /
   partial / expired. Unfilled expired orders get flagged for ticket
   regeneration (next model event or `--regen-unfilled`).
2. **Drift check:** actual weights vs Targets weights; per-name |drift| >
   `DRIFT_ALERT` (5% relative) → flag. This feeds B2's "actuals, not
   assumptions" rule.
3. **Anomaly halt (auto-creates `trading-halt.flag`):** position in a ticker not
   in the roster and not in any receipt (unknown provenance = possible executor
   bug or account misuse); cash negative; equity move vs prior snapshot
   unexplained by market moves of held names (>3σ). Halt stops future executions
   until Dom clears the flag — it never sells anything.
4. **Snapshot:** full account state → `tracking/live/recon/snapshot-{date}.json`
   (gitignored). Committed output is **sanitized only**:
   `tracking/live-status.json` with booleans + relative percentages, zero dollar
   values (see §E).
5. **Bookkeeping:** the existing notional performance series stays as-is (it is
   the model's track record and the site's data source). Add a parallel
   **live-vs-model tracking line**: cumulative return of the real account vs the
   notional model — the implementation-shortfall audit (fills, timing, dust
   suppression). Report in relative % only.

## E. Privacy & repo hygiene (the repo is public)

- **New boundary:** everything containing real dollar amounts, share counts,
  account numbers, or order IDs lives under `tracking/live/` — added to
  `.gitignore` in the same PR that creates it. Tickets, receipts, snapshots,
  executor config: never committed.
- Committed artifacts (`live-status.json`, live-vs-model line) carry **only**
  booleans, dates, and relative percentages. Extend
  `test_privacy_no_real_dollars_anywhere` (or add a sibling
  `test_privacy_live_trading`) to: (a) assert `tracking/live/` is gitignored,
  (b) scan all committed tracking/site files for the new field names and any
  dollar-like values sourced from recon. Never weaken — same standing as the
  site gate.
- The friend-facing site shows nothing from the live pipeline in v1. (The
  live-vs-model relative line is a candidate later — separate decision.)

## F. Rollout phases & acceptance

- **Phase 0 — setup (Dom):** Agentic account created + funded at `ACCOUNT_CAP`;
  MCP connected in Claude Code; read tools verified (Claude lists positions —
  should be empty/cash); O1 answered. *Accept:* recon runs and writes a snapshot.
- **Phase 1 — shadow (1–2 weeks):** ticket generation live on real model events
  (and one forced `--dry-run` full-deploy ticket), executor dry-run only, recon
  running. *Accept:* a full-deploy ticket whose orders Dom has eyeballed against
  the Targets sheet; all tests green; privacy gate green.
- **Phase 2 — live (go-live checklist, Dom approves):** Dom runs the executor on
  the deployment ticket. Steady state: model event → ticket → **one Dom
  command** → auto-recon → auto-bookkeeping. *Accept after first cycle:* fills
  reconciled with zero manual edits to any tracking file.
- **Phase 3 — zero-touch (optional, gated per §C5).**

## G. Governance — CLAUDE.md changes (same PR)

- **Amend rule 5:** the project now produces *executable trade tickets* for the
  Robinhood Agentic account, generated mechanically from the model's rules —
  this is the model's output, not Claude's discretionary advice. Buy/hold/sell
  authority remains: the model decides, Dom executes. Claude still doesn't
  recommend discretionary trades outside the system.
- **New rule 29:** the execution boundary (§0), the `tracking/live/` privacy
  boundary (§E), and "the executor is the only order writer" (rule-18 pattern:
  one writer per artifact). Explicitly: no session — local, cloud, or scheduled —
  may call MCP order tools, and no LLM may be inserted between ticket and order.

## H. Tests

- Ticket generation: golden tickets from fixture weights/equity/prices; dust
  suppression; untradeable-name renormalization; delta-from-actuals (fixture
  snapshot with a partial fill).
- Executor (offline, fixture MCP transport): every C2 gate has a red test;
  checksum tamper; expiry; double-execution; kill switch; turnover cap.
- Recon: anomaly matrix (unknown position → halt; drift → flag not halt);
  sanitized-output shape test.
- Privacy: §E gates. CI note: keep all new imports lazy (deploy-site CI runs a
  minimal env — see memory `reference_ci_minimal_env_lazy_imports`).

## I. Open questions for Dom

- **O1** (§A): headless OAuth survival — **ANSWERED 2026-08-09: no.** Interactive
  sessions connect (`claude mcp list` ✔); headless `claude -p` fails with "OAuth
  session expired and could not be refreshed" (reproduced 2×, interactive check
  passing in between — token refresh appears tied to the interactive/Keychain
  context). Consequence: recon (§D) runs in attended sessions + weekly-scan, not
  the daily cron. Re-test after Claude Code / Robinhood token-handling updates.
- **O2:** `ACCOUNT_CAP` initial value — Dom sets at funding.
- **O3:** when a roster name is untradeable on Robinhood (foreign local lines),
  accept renormalization (§B3) or hold its weight in cash? Spec default:
  renormalize; revisit if L11 foreign names enter the top 15.
- **O4:** does Robinhood's Agentic account support fractional shares on all
  listed names? Verify in Phase 1 dry-run; fall back to whole-share rounding
  with cash remainder if not.
