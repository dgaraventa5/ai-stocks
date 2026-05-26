---
description: Find tickers whose Total Score has moved materially since last quarterly rescore
---

Find tickers whose Total Score has moved meaningfully since the last quarterly rescore.

## Steps

1. **Read the baseline.** Open the most recent `/tracking/quarterly-rescore-{prior}.md` to get prior scores.

2. **Compare to current scores** in `00-master/ai_supply_chain_scoring.xlsx`.

3. **Identify movers** — any ticker whose Total Score has changed by more than 10 points (either direction).

4. **For each mover**, decompose the change:
   - Which category contributed most (compare subscores: Value, Quality, Growth, AI Thesis, Momentum, Risk)
   - Which specific input drove it (e.g., "FCF yield went from 1.2% to 4.5% after the latest 10-Q")
   - The underlying business reason (check recent 10-Q, 8-Ks, news log)

5. **Also flag tier changes** even if score change is smaller (e.g., ✓✓ → ✓ is worth noting even at a 7-point drop).

## Output

Save to `/tracking/score-movers-{YYYY-MM-DD}.md`. Aim for 5-15 names total, ranked by magnitude of score change.

For each mover, include:
- Ticker, prior score → current score
- Tier change (if any)
- Single dominant driver (one sentence)
- What to do next (revisit thesis? earnings update? deep-dive?)
