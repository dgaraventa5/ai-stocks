# Deploy-cash runbook: investing a new deposit through the execution pipeline

Added 2026-08-14. Applies whenever cash lands in (or leaves) the Robinhood
Agentic account outside the model's own trades — a deposit to deploy, or a
withdrawal. The pipeline treats an *undeclared* equity jump as a possible
executor bug and halts (D3, correctly), so the flow must be declared first.

All steps run on the local machine (attended session — Robinhood MCP OAuth
does not survive headless runs, spec O1). Real dollar amounts stay out of
committed files (§E); they live only under `tracking/live/` and in the
commands you type.

## Steps

1. **Pull account state** (attended Claude session, MCP READ tools only):
   portfolio (cash, equity), positions (shares + price), orders. Write to a
   scratchpad JSON in the shape `reconcile_account.py` expects:

   ```json
   {"as_of": "YYYY-MM-DD", "cash": 0.0, "equity": 0.0,
    "positions": {"TICKER": {"shares": 0.0, "price": 0.0}}, "orders": []}
   ```

2. **Reconcile, declaring the flow** (deposit positive, withdrawal negative):

   ```bash
   python3 scripts/reconcile_account.py --account-json state.json \
       --external-flow <AMOUNT>
   ```

   This appends the flow to the ledger `tracking/live/recon/flows.jsonl`
   (gitignored, append-only, idempotent per date+amount), so the D3
   unexplained-equity check is satisfied for this run **and** for the launchd
   cron's later recon against the same pre-deposit prior snapshot. It also
   divisor-adjusts the live-vs-model baseline so the deposit never prints as
   performance. Expect drift flags (every name is now underweight vs the
   larger equity) — flags, not halts. If a halt IS raised, stop and read
   `tracking/live/trading-halt.flag` before anything else.

3. **Generate the ticket** from the committed Targets and the fresh snapshot:

   ```bash
   python3 scripts/generate_trade_ticket.py
   ```

   A deposit on a near-target book produces a pure-buy ticket (every target
   notional rises with equity). Ticket lands in `tracking/live/tickets/`,
   expires in 48h.

4. **Dry-run the executor**, then confirm:

   ```bash
   python3 scripts/execute_ticket.py --ticket tracking/live/tickets/<T>.json
   python3 scripts/execute_ticket.py --ticket tracking/live/tickets/<T>.json --confirm
   ```

   Run during regular market hours (9:30–16:00 ET) — fractional orders
   transmit as market-type and are only accepted in regular hours.

5. **Reconcile again** after fills (no flag this time — the deposit is in the
   ledger and the new snapshot), or let the cron's recon step do it.

## Gates that may legitimately refuse, and what each means

- **`turnover > cap`** — deploying a deposit that is large relative to
  equity exceeds `MAX_TURNOVER_PCT`. Re-run with `--allow-full-turnover`
  (attended only; the scheduled executor never auto-runs full-turnover
  tickets, by design).
- **`equity > ACCOUNT_CAP`** — the deposit pushed equity past the cap in
  `tracking/live/executor-config.json`. If the deposit was intentional risk
  capital, raise the cap by deliberately editing that file (never a CLI
  flag, C3), then re-run. If you didn't mean to exceed it, withdraw.
- **`notional > MAX_ORDER_NOTIONAL`** — a single order exceeds the per-order
  cap; same deliberate-edit rule if the new account size warrants it.
- **`ticket expired`** — >48h since generation; regenerate (step 3), never
  hand-edit (checksum gate).
- **`kill switch present`** — investigate `trading-halt.flag` first; clear
  it deliberately only once explained.

## Why declaration is explicit (do not "fix" this by auto-detecting)

A deposit and an executor bug look identical from the equity line. The
anomaly gate's value is that it cannot be talked out of a halt by the data
itself — only a human declaration (`--external-flow`, typed by Dom) carries
the information "this money movement was mine." Auto-inferring flows from
cash deltas would silently reclassify exactly the anomalies the gate exists
to catch (same never-weaken standing as the rule-29 boundaries).
