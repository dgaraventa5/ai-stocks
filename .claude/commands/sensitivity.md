---
description: Sensitivity analysis on a ticker's score
---

Run a sensitivity analysis on $ARGUMENTS's Total Score.

## Steps

0. **MANDATORY FIRST: Invoke /refresh-context $ARGUMENTS.** A sensitivity analysis is only useful if the base-case inputs reflect current reality. Sensitizing stale inputs produces stale sensitivities. The /refresh-context briefing should specifically inform Step 5 ("Am I confident enough in this rating to bet money on it?") — for load-bearing inputs, the fresh briefing tells you whether your confidence is up-to-date or based on a 12-month-old mental model. See `.claude/commands/refresh-context.md`.

1. **Read the row** for $ARGUMENTS from `00-master/ai_supply_chain_scoring.xlsx`.

2. **Vary each input one at a time.** Hold all other inputs constant.
   - For subjective 1-5 columns: vary by ±1
   - For numerical inputs: vary by ±20%
   - Observe Total Score change for each variation
   - Tabulate

3. **Identify load-bearing inputs** — the 3 inputs whose variation causes the largest Total Score change.

4. **Identify low-stakes inputs** — the 3 inputs whose variation barely moves the score. (These are inputs where being wrong doesn't matter much.)

5. **For each load-bearing input, ask:** "Am I confident enough in this rating that I'd bet money on it?" If the answer is no for any load-bearing input, the conviction in this score is overstated.

## Output

Save to `/per-stock/$ARGUMENTS/sensitivity-{YYYY-MM-DD}.md` with three sections:
- Load-bearing inputs (with conviction check)
- Low-stakes inputs (so I know where not to obsess)
- Conclusion: is my conviction in this score actually justified, or does it rest on a couple of weak ratings?
