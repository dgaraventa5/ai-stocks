---
description: Side-by-side comparison of two tickers using the scoring framework
---

Compare $1 and $2 side by side using my scoring framework. Refer to CLAUDE.md.

## Steps

0. **MANDATORY FIRST: Invoke /refresh-context $1 AND /refresh-context $2.** A comparison is only as good as the latest data on both sides. Without fresh research, stale mental models on one or both names will bias the recommendation. See `.claude/commands/refresh-context.md`.

1. **Pull both rows** from `00-master/ai_supply_chain_scoring.xlsx`. If either ticker is missing, run `/score-stock` for that ticker first (then proceed).

2. **For each of the 6 categories**, build a side-by-side table:

| Sub-metric | $1 | $2 | Stronger | Magnitude |
|---|---|---|---|---|
| ... | ... | ... | $1 or $2 | "Material" / "Modest" / "Negligible" |

Categories: Value, Quality, Growth, AI Thesis, Momentum, Risk

3. **Identify the single biggest divergence** — the dimension where they're most different. Explain what that means for which to own.

4. **Make a direct recommendation.** If I could only own one, which and why? Be direct, not hedging. State your reasoning explicitly.

5. **Note any disqualifying factor** in either name (e.g., recent going-concern flag, major customer loss, regulatory overhang).

## Output

Save to `/per-stock/comparisons/$1-vs-$2-{YYYY-MM-DD}.md` and also print the recommendation section to console.
