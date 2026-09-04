---
description: Pre-evaluation research pass — pull fresh data and surface stale mental models before scoring or rating
---

Refresh research context for ticker $ARGUMENTS before any evaluation. Claude's training data is stale relative to today; this command forces explicit fresh-data gathering so scores reflect reality, not 12-month-old mental models.

**This is a mandatory step before /score-stock, /deep-dive, /compare, /rescore-quarterly, /earnings-update, and any subjective rating session.** Skipping it means scoring on stale data — which makes the system miss the buy opportunities it's supposed to surface.

## Why this exists

Claude's training data over-weights coverage from 12-24 months prior. The semi and AI infrastructure space moves fast enough that competitive dynamics, customer wins, product cycles, and regulatory state shift materially in a quarter. Locked ratings based on stale mental models compound into systematically wrong tier rankings.

Verified during 2026-05-18 Layer 6 rating session: fresh research on AMD surfaced META 6 GW deal, MI450 customer wins, and ROCm-7 PyTorch first-class support. None of these were in the original rating proposal. Three D-dimensions shifted from 4 → 5; AMD's TOTAL moved from ~73 to ~76.5.

## Steps

### 1. Articulate current mental model FIRST

Before pulling any data, write 2-4 sentences on what you currently believe about the ticker:
- AI thesis / revenue mix
- Key customers and competitive position
- Most recent reported quarter (per your training)
- Most recent product cycle / roadmap milestone

**The diff between this pre-research mental model and what fresh research surfaces is the value of the exercise.** If you skip articulating it, you'll silently rationalize new info into your existing model.

### 2. Pull latest filings (if not cached or >30 days old)

```bash
python3 scripts/sec_edgar.py $TICKER --forms 10-Q 8-K --limit 4 --since {YYYY-MM-DD 90 days ago}
```

Read the latest 10-Q MD&A section directly. Look specifically for: AI segment revenue, customer mix changes, capex commentary, forward guidance.

If Watchlist row is >30 days old, refresh objective inputs:
```python
from batch_score import compute_inputs
# update the row
```

### 2b. FCF conversion red-flag check (added 2026-06-09)

Earnings-quality screen, run on the same yfinance pull: compute **FCF conversion = TTM FCF ÷ TTM net income**. Flag in the context briefing if **conversion < 60% for 2+ consecutive fiscal years AND receivables + inventory are growing faster than revenue** — that combination is the accrual-games signature (reported profits not turning into cash while working capital balloons).

This is a **qualitative red flag, not a scored metric** — it was deliberately kept out of the Watchlist because it misfires on this universe in both directions:
- High-SBC names mechanically show conversion >100% (SBC adds back to OCF) — the metric *flatters* aggressive non-GAAP names
- Heavy growth-capex names (memory, power, data center buildouts) mechanically show low conversion — penalizes investment, not accounting

So interpret with judgment: a low conversion number only matters if the working-capital condition also holds. Note the finding (or "clean") in the briefing's Section 2.

### 2c. Expectations red-flag check (added 2026-06-12, rule 14)

```bash
python3 scripts/expectations_flag.py $TICKER
```

Asks "what's priced in?" — the one question the scoring rubric structurally cannot ask (Value bands are absolute; Momentum *rewards* relative strength; so the Total Score peaks exactly where consensus expectations are highest — surfaced by the 2026-06-12 SALP 13F stress test, where our top 6 names were 5 of the fund's 6 biggest put targets).

**The flag fires when:** current P/S sits ≥90th percentile of the name's own 3-year range AND current revenue YoY growth is *below* its 3-year median — i.e., peak multiple on decelerating growth.

This is a **qualitative red flag, not a scored metric**: a name at its 3-year-high multiple can deserve it (genuine inflection — the briefing must make that argument explicitly), and a name at its 3-year-low can be cheap for a reason. The flag's job is to force the briefing to address embedded expectations head-on instead of letting "great business" silently stand in for "great forward return."

The script self-skips with a stated reason on foreign filers (no quarterly us-gaap XBRL) and names using unmapped revenue tags (some crypto miners) — when it skips, note the skip + reason in Section 2; eyeball P/S vs its own history manually if the name is rating-critical.

### 2d. Litigation / docket check (added 2026-08-24, after the BW miss)

```bash
python3 scripts/litigation_check.py $TICKER
```

**Why this step exists.** On 2026-08-24 the rating refresh found that BW's subjective ratings rested on research that knew nothing about a pending securities-fraud class action naming the company, its Chairman/CEO and its CFO (*Cho v. Babcock & Wilcox Enterprises*, 5:26-cv-00886, N.D. Ohio, filed 2026-04-14) alleging the flagship $2.4B AI-datacenter contract was a related-party deal with BW's own ~19% shareholder on both sides.

The reason the pipeline missed it is the point: **the case appears in none of BW's periodic filings.** The FY2025 10-K predates the complaint; both 10-Qs filed afterwards say "no new litigation to disclose." So Step 2's filings pull and the rule-9 earnings refresh both came back clean — twice — on a name whose central thesis premise was being contested in federal court. A filings-only view was complete and still wrong. This step goes outside the filing chain, to the court's own docket index.

**What it reports:**
- **SECURITIES dockets** (nature of suit 850 / Exchange Act cause) — the R4 input.
- **IP/patent dockets** — lower prominence, but they bear on **D3 moat**. The first live run surfaced ten active MPWR patent suits against Vicor and Reed Semiconductor.
- **⚠️ DISCLOSURE MISMATCH** — a *pending* securities docket filed before the newest cached 10-K/10-Q went out, where that filing contains no litigation language. This is the BW blind spot, and it is the part worth having: plaintiff-firm press releases already spam "a case exists"; nobody tells you the company's own filings are silent about it.

**Interpretation discipline — a qualitative red flag, NOT a scored metric** (same standing as 2b and 2c):

- A complaint is an **allegation**. Plaintiff firms file reflexively after any sharp drawdown, and most securities class actions settle small or are dismissed. A hit is not established wrongdoing, and it is not automatically an R4 downgrade — read what is actually alleged.
- **Distinguish a filed case from a solicitation.** "Law firm investigates possible breaches of fiduciary duty" press releases are marketing and carry near-zero information. A docket number is evidence; a press release is not. This step exists partly because that distinction is easy to get backwards in either direction.
- **A MISMATCH is not an accusation of improper disclosure.** Reg S-K Item 103 covers *material* pending proceedings and ASC 450 covers reasonably-possible material losses — management may legitimately judge a matter immaterial. Report the dates, read the filing's Item 1, and let the briefing reason. Do not draw a legal conclusion.
- **Check the as-of date.** A 10-Q's "no new litigation" sentence is scoped to **period end**, not filing date. A complaint filed between period end and filing date produces an apparent mismatch that is literally accurate — that is exactly the difference between BW's Q1 10-Q (accurate) and its Q2 10-Q (conflicting). The script prints both dates for this reason.
- **Absence is weak evidence.** RECAP mirrors PACER and is not guaranteed complete. Record a clean run as **"no federal docket found in RECAP,"** never as "no litigation."

The script self-skips with a stated reason when CourtListener is unreachable or rate-limits (HTTP 429), and reports honestly when no local filing is cached for the cross-check (run `sec_edgar.py` first). When it skips, note the skip + reason in the briefing — a skip is not a clean result.

**Highest-value on:** names where one counterparty carries most of the backlog or revenue, related-party or affiliate-heavy structures, recent sharp drawdowns against good reported numbers, and any name whose thesis rests on a single contract. That is the profile where a filings-only view is most likely to be complete and still wrong.

### 3. WebSearch with current year in the query

The current year is **mandatory** in search queries — Claude's bias is to assume "latest" means 2024 or 2025. Always include the actual current year.

Run these searches (minimum):
- `"$TICKER Q{n} {current_year} earnings results"` — captures actual reported numbers, headline beats/misses
- `"$TICKER AI revenue {current_year}"` — captures AI mix progression
- `"$TICKER customer wins {current_year}"` — captures hyperscaler / large customer announcements
- `"$TICKER {layer-specific_term} {current_year}"` — layer-specific dynamic (ROCm/CUDA, custom silicon, HBM, optical, etc.)

Add searches based on what your mental model is uncertain about. If you're not sure about competitive position, search competitors. If unsure about regulatory state, search "$TICKER DOJ FTC investigation {current_year}".

### 4. WebFetch latest earnings call transcript (best-effort)

Try fetching from:
- `https://www.fool.com/earnings/call-transcripts/{year}/{month}/{day}/{ticker}-{q}-{year}-earnings-call-transcript/`
- `https://seekingalpha.com/article/...` (often paywalled — best-effort)

Prompt the WebFetch tool: "Extract the key business updates: AI revenue mix, customer wins, capex, guidance, competitive commentary, any mention of new product cycle or significant strategic shifts."

### 5. Write briefing to per-stock/{TICKER}/context-{YYYY-MM-DD}.md

Sections:
1. **Pre-research mental model** (from Step 1 — quote it verbatim)
2. **Latest filing highlights** (key quotes from 10-Q MD&A, 8-K disclosures) — record the 2b / 2c / 2d results here, including any **skip + reason** (a skip is not a clean result)
3. **WebSearch findings** (top 3-5 findings with source URLs)
4. **Earnings transcript highlights** (if fetched)
5. **DIFF: what changed since my training** — explicit list
6. **Implications for ratings** — which D/M/R dimensions are affected and how (don't pre-decide ratings, just flag)

### 6. Report back

Surface:
- The 3-5 most material findings
- Which rating dimensions are likely affected
- Any thesis-break signals (severe regulatory escalation, customer loss, product cycle issue)
- Any **pending securities docket or disclosure mismatch** from Step 2d, stated as what it is: a filed allegation, with the docket number — never as established wrongdoing, and never conflated with a plaintiff-firm "investigation" press release

## Do not

- Skip Step 1 (mental model articulation) — the diff is the entire point
- Use search queries without the current year — Claude defaults to older years
- Lock any rating before completing Step 5 (the briefing file)
- Pre-decide what the ratings should be during the research pass — the rating session is separate
- Use only one search query — diversify across earnings, customers, competitive, regulatory
- Record a clean Step-2d run as "no litigation" — it means "no federal docket found in RECAP"
- Treat a Step-2d hit as proven misconduct, or a plaintiff-firm "investigation" press release as a filed case

## When NOT to run this

- During `/weekly-scan` (already news-focused, would be redundant)
- During `/13f-delta` (fund-tracking, not stock-rating)
- During pure data refresh (yfinance input update only, no rating change)

## Sources discipline

Every finding written to the context briefing must cite a URL. The briefing becomes part of the audit trail — future-Dom should be able to retrace why a rating moved.
