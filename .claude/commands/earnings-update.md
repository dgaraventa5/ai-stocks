---
description: Process a new earnings release for a ticker
---

$ARGUMENTS just reported earnings. Update the research files per CLAUDE.md.

## Steps

0. **MANDATORY FIRST: Invoke /refresh-context $ARGUMENTS.** Earnings cycles are exactly when the most mental-model staleness shows up — competitive position shifts, customer wins, guidance changes. Fresh research pass before processing the transcript ensures the delta summary captures structural changes, not just headline-vs-prior-guide mechanics. See `.claude/commands/refresh-context.md`.

1. **Pull the new transcript.** Save to `/per-stock/$ARGUMENTS/transcripts/Q{N}-{YYYY}.md`. Markdown format, not PDF.

2. **Read the prior quarter's transcript** from the same folder for comparison.

3. **Write the delta summary.** Save to `/per-stock/$ARGUMENTS/transcripts/Q{N}-{YYYY}-delta.md`. Cover:
   - Management tone shift on AI demand (more / less / unchanged confidence)
   - Customer concentration changes (new wins, losses, % shifts)
   - AI-revenue mix change (if disclosed)
   - Capex / capacity / lead-time changes
   - Forward guidance vs. prior guide (revenue, margin, capex)
   - New risks raised
   - Anything thesis-relevant

4. **Update the scoring spreadsheet.** Re-pull financial inputs for $ARGUMENTS into `00-master/ai_supply_chain_scoring.xlsx` (the new 10-Q is now filed). Update Last Updated. **Do not touch the 1-5 subjective columns.**

5. **Flag stale thesis sections.** Read `/per-stock/$ARGUMENTS/thesis.md`. For any section materially affected by what you just learned, append `[STALE - revisit]` to that section's heading. Do not rewrite the section — that's my job.

6. **Append to news-log.** Add a one-line entry to `/per-stock/$ARGUMENTS/news-log.md`: date, "Q{N} earnings", and a 1-sentence summary.

## Report back

- The delta summary itself
- List of STALE sections raised (sections in thesis.md that now need my attention)
- Financial input deltas in the spreadsheet (which numbers moved most, e.g., "Gross margin: 35% → 38%")
- Whether the new info supports, weakens, or doesn't change the thesis
