# NVDA — catalysts watchlist

Forward-looking events that could move the thesis. Use the thesis.md §8 table as the canonical list; this file is for lower-priority items and ad-hoc capture.

| Date | Event | Why it matters |
|---|---|---|
| 2026-11-17 | Q3 FY27 print, Kress's first call as interim CEO | Demand/supply-constraint language, Q4 guide, DSO/FCF conversion (2b watch), any customer or export-compliance disclosure. Triggers the post-print refresh. |
| 2026-11-18 → before Thanksgiving | House committee briefing / Huang testimony | Scope of export-compliance questions; whether NVIDIA (not just customers) becomes a target. R4. |
| ~2026-11-19 | Anthropic IPO; reported $10B NVIDIA purchase (unconfirmed) | Circular-financing perimeter. |
| 2026-12-03 | Senate Banking Chair Tim Scott's deadline for Huang + Lutnick testimony | Bipartisan oversight trajectory before gavels change hands. R4. Source: [Newsweek](https://www.newsweek.com/democrats-react-nvidia-jensen-huang-resignation-china-spy-scandal-12708310); `reports/Democratic Congress AI implications.md` |
| Jan 2027 | 120th Congress organizes; Wyden (Finance) / Neal (W&M) H200 probe gains subpoena power | Probe opened 2026-11-12 calls the 25% §232 levy an unconstitutional export tax and ordered Commerce to preserve Nvidia records; expect document subpoenas in Q1 2027. R4. Source: [Wyden–Neal letter](https://www.wyden.senate.gov/imo/media/doc/11122026wydenneallettertolutnickonnvidia.pdf); `reports/Democratic Congress AI implications.md` |
| Lame duck (Nov–Dec 2026) | FY2027 NDAA final conference text | Confirms whether GAIN AI / Chip Security / AI OVERWATCH were dropped again (single-source report). Source: [Nextgov](https://www.nextgov.com/artificial-intelligence/2025/10/ai-export-control-bill-passes-senate-ndaa-amendment/408762/); FY27 drop single-source, [Crypto Briefing](https://cryptobriefing.com/nvidia-chip-restrictions-unlikely-final-ndaa/); `reports/Democratic Congress AI implications.md` |
| Spring–fall 2027 | FY2028 NDAA markup + conference under a Democratic Congress | Likeliest vehicle for *enacted* chip-export constraints; GAIN AI already passed the Senate 77–20 in the FY26 NDAA before dying in conference. Source: [Nextgov](https://www.nextgov.com/artificial-intelligence/2025/10/ai-export-control-bill-passes-senate-ndaa-amendment/408762/); FY27 drop single-source, [Crypto Briefing](https://cryptobriefing.com/nvidia-chip-restrictions-unlikely-final-ndaa/); `reports/Democratic Congress AI implications.md` |
| Open | Wachtell Lipton board investigation findings | Whether secrets or controls were compromised. R4, possibly D3. |
| Open | Permanent CEO named | Strategy continuity; triggers a context refresh. |
| Open | Any BIS/DOJ action naming NVIDIA re Megaspeed/diversion | Would make R4 = 1 arguable and R2 penalty leg live. |
| Open | Beijing H200 import approval (600k units in Hong Kong) | Upside optionality on a $0-China guide. |

## Special-situation watch (opened 2026-11-12, Dom)

Opened after the CEO resignation (`context-2026-11-12.md`). Run by `/special-situation NVDA` (see `.claude/commands/special-situation.md`).

**Schedule (Pacific):**
- **Thu 2026-11-19, 07:00** — one-off post-earnings review (`/special-situation NVDA post-print`), after `/daily-watch` briefs the 11-17 print and re-scores after the 11-18 close. Re-computes the open M1, M2 and R4 proposals on post-print data.
- **Every Monday, 07:00** — biweekly check (`/special-situation NVDA`): researches only when the newest NVDA briefing is 10+ days old, so it works out to about every two weeks and never duplicates a fresh briefing.
- **Any day** — `/daily-watch` covers same-day events for NVDA as a holding (news, 8-Ks, earnings).

**Open items (search each run):** permanent CEO named · Wachtell Lipton board-investigation findings · House testimony / Senate subpoena · any BIS, DOJ or SEC action naming NVIDIA (not just customers) · Megaspeed and SDNY/Supermicro probe outcomes · Beijing H200 import approval · Hu v. NVIDIA (5:26-cv-05496) complaint substance.

**Exit conditions (all must hold):** a permanent CEO is named and has been in post through one earnings call; the board investigation has reported; no congressional or agency action naming NVIDIA is pending. Then Dom retires the watch (disable the `ai-stocks-nvda-watch` task) and NVDA returns to the `/rating-research` rotation.
