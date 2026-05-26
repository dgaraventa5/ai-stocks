---
description: Initial deep-dive on a ticker (designed for /goal mode)
---

Complete an initial deep-dive on $ARGUMENTS. Refer to CLAUDE.md for conventions.

**This command is designed for `/goal` mode.** Run with `/goal` so Claude iterates until all completion criteria are met.

## Completion criteria (goal is met when ALL true)

- [ ] `/per-stock/$ARGUMENTS/` directory exists with subdirectories `filings/` and `transcripts/`
- [ ] `/per-stock/$ARGUMENTS/filings/` contains the latest 10-K and 2 most recent 10-Qs (PDFs from SEC EDGAR)
- [ ] `/per-stock/$ARGUMENTS/transcripts/` contains the last 4 earnings call transcripts as markdown files (`Q{N}-{YYYY}.md`)
- [ ] `/per-stock/$ARGUMENTS/thesis.md` exists, copied from `/templates/per-stock-template.md`, with all 10 sections filled in
- [ ] Every numeric claim in thesis.md cites a specific filing source (filing type + date + section/page)
- [ ] `/per-stock/$ARGUMENTS/financials.xlsx` exists with columns FY-3, FY-2, FY-1, TTM and the standard rows (revenue, gross profit, gross margin %, operating income, operating margin %, FCF, FCF margin %, capex, capex/revenue %, net debt, net debt/EBITDA, share count, share count YoY %)
- [ ] All calculated cells in financials.xlsx are Excel formulas, not Python-hardcoded values
- [ ] `/per-stock/$ARGUMENTS/deep-dive-summary.md` exists with three sections: What I learned / What I couldn't determine / Specific follow-up questions for me

## Execution order

0. **MANDATORY FIRST: Invoke /refresh-context $ARGUMENTS.** Pulls fresh research (WebSearch + WebFetch + EDGAR) and writes briefing to `per-stock/$ARGUMENTS/context-{date}.md`. Read it before starting the deep-dive. Stale mental models would silently bias every thesis.md section. See `.claude/commands/refresh-context.md`.
1. Create folder structure
2. Download filings from EDGAR (rate-limited, 10 req/sec max)
3. Find and save transcripts: try IR page first, then motleyfool.com, then Google search
4. Copy template → thesis.md → fill in section by section
5. Build financials.xlsx
6. Write the 1-page summary

## When goal is met

STOP iterating. Report what was created and any sections of thesis.md where you had to leave a placeholder because data wasn't accessible. Do not keep refining indefinitely.

## Common pitfalls

- Transcripts on motleyfool sometimes have OCR errors — note these
- yfinance share count is often outdated; use the most recent 10-Q cover page
- Some companies report "non-GAAP gross margin" prominently — use GAAP for the financials.xlsx, note the non-GAAP figure in thesis if material
