# NVDA — catalysts watchlist

Forward-looking events that could move the thesis. Use the thesis.md §8 table as the canonical list; this file is for lower-priority items and ad-hoc capture.

| Date | Event | Why it matters |
|---|---|---|
| 2026-12-02 | House committee chairs' closed-door transcribed interview (general counsel; E&C also asked Kress for a briefing before this date) | Scope of export-compliance questions; whether NVIDIA (not just customers) becomes a target. R4. |
| ~early Dec 2026 | Q3 FY27 10-Q | Whether it discloses the reported SEC inquiry, the Kistenmacher/Vanegas suits, DSO/extended-terms detail, top-customer %. R4, R1, R3. |
| Open | SEC civil probe (WSJ 2026-11-17, unconfirmed) | Company confirmation, Wells notice or subpoena would make R4 = 1 a proposal. |
| Open | *Kistenmacher v. NVIDIA* class action / *Vanegas* derivative (N.D. Cal., ~2026-11-09) | Lead-plaintiff stage, then motion to dismiss. R4. |
| Late Nov 2026 | Anthropic IPO; a secondary source (Leverage Shares, 2026-11-13) says the amended S-1 of 2026-11-10 lists a ~$10B NVIDIA private-placement purchase — not verified against the S-1 | Circular-financing perimeter. |
| Open | Wachtell Lipton board investigation findings | Whether secrets or controls were compromised. R4, possibly D3. |
| Open | Permanent CEO named | Strategy continuity; triggers a context refresh. |
| Open | Any BIS/DOJ action naming NVIDIA re Megaspeed/diversion | Would make R4 = 1 arguable and R2 penalty leg live. |
| Open | Beijing H200 import approval (600k units in Hong Kong) | Upside optionality on a $0-China guide. |

## Resolved

| Date | Event | Outcome |
|---|---|---|
| 2026-11-17 | Q3 FY27 print, Kress's first call as interim CEO | Beat-and-raise; demand outpacing supply; FY28 ~75% growth; Q4 GM 71–72% guided as the trough; TTM FCF conversion 66%, DSO 64. Reviewed in `context-2026-11-19.md`. |

## Special-situation watch (opened 2026-11-12, Dom)

Opened after the CEO resignation (`context-2026-11-12.md`). Run by `/special-situation NVDA` (see `.claude/commands/special-situation.md`).

**Schedule (Pacific):**
- **Thu 2026-11-19, 07:00** — one-off post-earnings review (`/special-situation NVDA post-print`), after `/daily-watch` briefs the 11-17 print and re-scores after the 11-18 close. Re-computes the open M1, M2 and R4 proposals on post-print data.
- **Every Monday, 07:00** — biweekly check (`/special-situation NVDA`): researches only when the newest NVDA briefing is 10+ days old, so it works out to about every two weeks and never duplicates a fresh briefing.
- **Any day** — `/daily-watch` covers same-day events for NVDA as a holding (news, 8-Ks, earnings).

**Open items (search each run):** permanent CEO named · Wachtell Lipton board-investigation findings · House testimony / Senate subpoena (12-02 transcribed interview) · SEC civil probe confirmation · Kistenmacher/Vanegas suits · any BIS, DOJ or SEC action naming NVIDIA (not just customers) · Megaspeed and SDNY/Supermicro probe outcomes · Beijing H200 import approval · Hu v. NVIDIA (5:26-cv-05496) complaint substance.

**Exit conditions (all must hold):** a permanent CEO is named and has been in post through one earnings call; the board investigation has reported; no congressional or agency action naming NVIDIA is pending. Then Dom retires the watch (disable the `ai-stocks-nvda-watch` task) and NVDA returns to the `/rating-research` rotation.
