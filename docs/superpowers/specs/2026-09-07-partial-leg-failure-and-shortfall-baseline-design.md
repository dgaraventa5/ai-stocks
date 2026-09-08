# Partial-leg execution failures + the live-vs-model baseline artifact

Date: 2026-09-07 (revised 2026-09-08 for PR #57). **Proposed by Claude — NOT
yet approved.** Written at Dom's request after diagnosing the −4.53%
live-vs-model shortfall. Touches the rule-29 execution boundary; nothing here
changes who may transmit an order.

**Overlap check before reading:** two of the four things this investigation
surfaced were already fixed by other sessions — the cash buffer (`66df82b`,
#42, 2026-08-17) and the ticket TTL (`cebd329`, #57, 2026-09-08). Both are
recorded here as closed rather than re-proposed. What remains genuinely open is
§3a/§3b (partial-leg failures report success and are never re-detected) and the
§4 baseline decision.

## 1. What the shortfall investigation actually found

`tracking/live-vs-model.json` reached a −4.53% cumulative shortfall on
2026-09-07 and had run negative for several consecutive observations. The
decomposition is the point: **it is two unrelated things, and one of them is
not a problem at all.**

| Window | Shortfall change | Cause |
|---|---|---|
| 2026-08-09 → 08-17 | **−3.69** (81% of total) | Deployment lag — one-time |
| 2026-08-17 → 09-07 | −0.84 | −0.45 weight mismatch, ~−0.39 friction |

**The deployment lag is an artifact, not underperformance.** The baseline was
struck 2026-08-09 with the account at 100% cash while the model was fully
invested from day zero. Snapshots: 81% invested Aug 12–13, then **27% invested
Aug 14–16** after a declared deposit landed, reaching 96% only on Aug 17. The
model rose +3.27% across that window; live captured almost none of it. Because
the metric is cumulative since baseline, that gap is now permanent.

The `live_vs_model` divisor adjustment (reconcile_account.py) correctly
neutralises the *flow itself* — it does not, and cannot, neutralise the days
the new cash sat uninvested while the model compounded. That is a real cost,
correctly measured; it is just not an ongoing one, and leaving it inside a
single cumulative number means it will contaminate the implementation-shortfall
read forever. §4 addresses that.

## 2. The cash-buffer fix already exists — recorded so it is not re-proposed

The 2026-08-17 ticket committed **99.98% of available cash** across 15 legs
sent alphabetically. The first 14 consumed 94.77%, leaving 5.23% of headroom
for a VRT leg needing 5.21% — a margin of 0.02%. Slippage exhausted buying
power and the broker rejected the last leg:

```
VRT  transmit_error  API error 400: {"detail":"You can only purchase 0 shares of VRT."}
```

**This was diagnosed and fixed the same day.** `CASH_BUFFER_PCT: 0.02` landed
in `trade_ticket.DEFAULTS` in commit `66df82b` ("fix(ticket): reserve a cash
buffer so the last order can still fill", #42), and the comment block in
`compute_orders` already documents the sequential-slippage mechanism and the
requirement that the buffer exceed `LIMIT_TOL`. **No change is proposed here.**

It is recorded because of what it did *not* do: the buffer prevents
**recurrence**, but nothing **repaired** the position gap it left behind. VRT
has sat at ~1.8% against a 5.64% target for three weeks (67% underweight).
That is the subject of §3.

## 3. Partial-leg failures are silent, and unrecoverable from the same ticket

### The defect

In `execute_ticket.py`, a leg that throws at transmit is recorded and printed:

```python
except Exception as e:   # record, never silently drop (rule 3)
    results.append({**o, 'order_id': None, 'state': 'transmit_error', ...})
    print(f"  TRANSMIT ERROR {o['ticker']}: {e}")
```

and the function then returns `{'failures': [], 'sent': True, ...}`. **The run
reports success.** One leg of fifteen never reached the broker and the exit
status, the return value, and every committed artifact say the execution
worked.

It is then unrecoverable from that ticket. The executed-once guard re-runs a
ticket only when *every* order transmit_errored:

```python
all_failed = bool(prior_orders) and all(
    o.get('state') == 'transmit_error' for o in prior_orders)
...
else:   # placed, partial, empty, or unreadable: fail closed
    fails.append(f'already executed — receipt exists: {receipt_path.name}')
```

Failing closed on a partial is **correct** — 14 orders did reach the broker and
re-sending them risks double-execution, which is far worse than an underweight.
The defect is not the guard. The defect is that nothing else picks the failed
leg up, and the operator is not told loudly enough to act.

### Why it stayed broken for three weeks

The system did notice. The monthly drift pass flagged VRT at 67–68% from target
in every recon run, and on 2026-09-04 it correctly generated a remediation
ticket (one order: VRT buy 0.1878 shares). **That ticket was never executed and
expired 2026-09-06** at the 48-hour `TICKET_TTL_HOURS`.

**The reason it expired has since been root-caused and fixed by another
session** (`cebd329`, PR #57, 2026-09-08) — and more precisely than this
investigation had it. The ticket was generated Friday 2026-09-04 at 22:11Z with
`expires_at = created + 48h` (wall-clock). The launchd executor only attempts
execution in its **06:35 PT weekday open-mode run**; the 13:35 PT close-mode run
does series + recon and never executes. So the window contained **no execution
attempt at all**: Friday's slot had passed, the weekend has none, and Monday
2026-09-07 was Labor Day. The first live slot was Tuesday, ~15 hours after
expiry, and the C2.1 gate correctly refused it. Any ticket generated after
Friday 06:35 PT hit this every week; the holiday just widened it. TTL is now
counted in US **trading days** (`scripts/trading_calendar.py`).

That fix removes the *cause* of this particular lapse. It does not change what
happens when a ticket lapses anyway, nor anything in §3a/§3b — `execute_ticket`
still returns `failures: []` on a partial failure on current main.

So four independent mechanisms each did their job partially and the gap
survived all four: the buffer fix prevented recurrence but not repair; the
drift pass detected and generated but could not execute; the TTL expired before
any execution slot existed; and the executor has separately been failing on the
documented DarkWake network issue.

**Cost so far: approximately nothing.** VRT fell ~4% over the window, so the
underweight *added* +0.15pt. That is luck. Had VRT rallied 20% the same defect
would have cost roughly −0.75pt with no additional warning.

### Proposed changes

**3a — A partial failure must not report success.**
`execute_ticket` returns the failed legs in `failures` rather than `[]` when
any order ends in `transmit_error` while others did not, and exits nonzero.
`sent` stays `True` (orders did reach the broker — that must not be
misrepresented). The receipt already records per-leg state and does not change.

**3b — Recon raises an anomaly on an unrepaired failed leg.**
`reconcile_account.py` already computes drift flags. Add a distinct condition:
a ticker whose most recent receipt shows `transmit_error` **and** which remains
outside its drift band at the next recon is an **anomaly**, not a drift flag.
Anomalies are the existing loud channel.

**Deliberately NOT proposed: auto-raising the halt flag.** Per rule 29 the
halt flag stops future executions; raising it for an underweight would block
unrelated correct trades to fix a position that is merely the wrong size. The
signal should be loud, not blocking.

**3c — Do not treat an expired-unexecuted ticket as handled.**
Re-scoped after PR #57. The common cause of lapsing is fixed, so this is no
longer the urgent half — but a ticket that expires with **no receipt** is still
inert, and nothing distinguishes "was executed" from "silently lapsed". The
monthly pass should regenerate rather than assume the prior ticket was
actioned. Cheap: `generate()` is already append-only and writes a NEW file per
regeneration (B3); the only change is the not-handled determination.

**3d — Operational, outside this spec's code:** the launchd DarkWake failure
is independent of the TTL fix and still live in the executor log. It needs its
own fix; noting the dependency so 3a–3c are not mistaken for a complete
solution.

### Immediate remediation (Dom-run, not automated)

The VRT gap is still open. The 2026-09-04 ticket is expired and cannot be
reused. A regenerated top-up needs sizing attention: at the 09-04 numbers the
single VRT order was **92.6% of current cash**, which would re-create a
no-headroom condition — the 2% buffer is computed against *equity*, not against
the cash actually available for a single-leg catch-up ticket. **Flagged, not
fixed:** whether `CASH_BUFFER_PCT` should also floor against available cash on
small single-leg tickets is a real question this spec does not answer.

## 4. The live-vs-model baseline — a decision, not a fix

§1 showed one number carrying two meanings: a permanent one-time deployment
lag, and ongoing implementation shortfall. As long as they are summed, the
metric cannot answer the question it exists to answer — *is live tracking the
model?* — because the honest answer today is "to within about −0.8% since full
deployment," and the artifact reports −4.53%.

Three options, with the trade-off stated rather than a recommendation smuggled
into the framing:

- **(a) Leave it.** The number is the true since-inception experience of real
  capital and deserves to be uncomfortable. Deployment lag is a genuine cost of
  running the system and hiding it is how a paper record drifts from reality.
  Cost: the ongoing-tracking signal stays contaminated indefinitely.
- **(b) Re-baseline at 2026-08-17** (first fully-deployed snapshot). Cleanest
  ongoing signal; **discards a real −3.69% of experienced cost**, which is
  exactly the kind of restatement rule 17 forbids for forecasts and rule 28's
  history seam handles by *never* restating.
- **(c) Report both.** Keep the since-inception series untouched and add a
  second line anchored at first-full-deployment. Nothing is discarded, the
  ongoing signal becomes readable, and the gap between the two lines is itself
  the documented deployment cost. Cost: two numbers to explain, and a second
  anchor date that must be defined precisely (first snapshot at ≥95% invested,
  recorded once and then immutable).

**(c) is consistent with how this repo has handled every prior seam** —
`sizing_migration_invvol` (rule 28) added an event and restated nothing;
forecasts append snapshots rather than editing. It is also the only option that
does not destroy information. **Dom's call.** If (c) is chosen, the second
anchor must be immutable once written, for the same reason `created_date` is in
rule 17: an adjustable baseline can be tuned until the tracking looks good.

## 5. Boundaries (do not weaken)

- Rule 29 is untouched. Claude remains read-only toward Robinhood;
  `execute_ticket.py`, run by Dom, remains the only order writer. Nothing here
  adds an automated transmit path, and 3c generates *tickets*, never orders.
- Fail-closed on partial receipts stays. 3a changes what is **reported**, never
  what is **re-sent**.
- No real dollars, share counts or order IDs enter committed artifacts. Every
  figure in this spec is a percentage or a share count already present in a
  gitignored ticket, quoted here only where it is dimensionless.

## 6. Test plan

- `execute_ticket` partial-failure fixture (14 ok, 1 transmit_error) →
  `failures` non-empty, nonzero exit, `sent` still True, receipt unchanged.
- Same fixture re-run → still refused by the executed-once guard (regression:
  3a must not weaken it).
- All-failed fixture → re-run still allowed (regression on `all_failed`).
- Recon fixture: receipt with a transmit_error leg + that ticker outside its
  drift band → anomaly raised; inside band → no anomaly.
- Expired ticket with no receipt → next generate() writes a new ticket.
- Privacy suite must stay green (`tests/test_privacy_live_trading.py`).
