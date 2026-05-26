# Quarterly Update Checklist

Run this every quarter, ~2-3 weeks after the close of each calendar quarter (allows time for 10-Qs to be filed). Process every position in `portfolio.xlsx` and every name with ✓✓ or higher conviction in the Watchlist tab of `00-master/ai_supply_chain_scoring.xlsx`.

**Primary execution:** Run `/goal /rescore-quarterly` in Claude Code. The slash command at `.claude/commands/rescore-quarterly.md` automates most of this. This file is the human-readable checklist version — useful when you're reviewing what Claude produced or running a manual quarterly cycle.

## Per-stock checklist

For each ticker, Claude Code should (or has already done, if running `/rescore-quarterly`):

### Filings
- [ ] Pull latest 10-Q from EDGAR; save to `per-stock/{TICKER}/filings/`
- [ ] Pull any 8-Ks filed since last review
- [ ] Pull any insider transaction forms (Form 4)

### Earnings call
- [ ] Pull latest earnings call transcript; save to `per-stock/{TICKER}/transcripts/`
- [ ] Summarize three things:
  - Management's tone vs. prior quarter (more / less confident)
  - Any change in customer concentration or AI-revenue mix
  - Any change in capex / capacity / lead times

### Financials update
- [ ] Update `per-stock/{TICKER}/financials.xlsx` with the new quarter
- [ ] Flag any of these breaking trend:
  - Gross margin moved >150bps QoQ
  - FCF margin moved >300bps QoQ
  - Net debt changed materially
  - Share count grew (dilution check)
  - Capex guide revised

### Thesis check
- [ ] Re-read `per-stock/{TICKER}/thesis.md`
- [ ] For each of the 10 sections: is anything materially different from when last written?
- [ ] If yes, mark the section as **STALE** and require human review

### Catalyst calendar
- [ ] Update `per-stock/{TICKER}/catalysts-watchlist.md`
- [ ] Add the next 4 quarters of expected events

### News / press
- [ ] Scan press releases since last review
- [ ] Add anything material to `per-stock/{TICKER}/news-log.md`

## Roll-up output

Produce `tracking/quarterly-review-{YYYY}-Q{N}.md` with the following sections:

### 1. Executive summary
- 3-5 bullets on the most important developments across the watchlist
- Hyperscaler capex update: total $ across MSFT/GOOGL/AMZN/META/ORCL, YoY change, vs. prior guide
- Anything thesis-changing at the layer/sector level

### 2. Position-by-position table

| Ticker | Layer | Conviction (prior) | Conviction (now) | Thesis-stale? | Action recommended |
|---|---|---|---|---|---|
| | | | | | Add / Hold / Trim / Exit |

### 3. New names to evaluate
- Companies that appeared in the news as supply chain participants
- Companies that hyperscalers mentioned by name on earnings calls
- New IPOs in the space

### 4. Names to exit / downgrade
- Any with broken thesis tests
- Any where moat eroded
- Any where customer concentration spiked dangerously

### 5. Self-grade on prior quarter
- Which decisions from last quarter look right / wrong now?
- What did I miss?
- What process improvement comes from this?

## Rules for Claude

1. **Cite everything.** Every numeric claim must reference a specific filing line item with date.
2. **Don't recommend actions you can't justify.** "Add" / "Trim" / "Exit" must be tied to a specific change since last review.
3. **Flag uncertainty.** If data is missing or ambiguous, say so — don't paper over it.
4. **Don't editorialize on macro.** Focus on company-specific facts. Macro/thesis discussion belongs in the executive summary, where it's clearly framed as opinion.
5. **Don't touch subjective 1-5 columns.** Those are Dom's. Only update objective inputs and Last Updated.
