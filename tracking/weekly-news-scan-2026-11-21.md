# Weekly News Scan — 2026-11-21

Scheduled (unattended) run, rule 37. Window 2026-11-13 → 2026-11-21.
SEC: 67 filings from 193 names, 0 lookups failed, 23 names not on EDGAR (foreign local listings / OTC ADRs). News backstop: 32 names, 0 failed. 60 unlogged filings were read by three parallel readers (SEC calls serialized); 7 were already in news-logs.

## Missing data (read first)

- **CLSK** — EV/MW input stale: `capacity-mw.json` as-of 2026-06-30 (144 days, >90). Needs a MW refresh (inbox ask).
- **SHAZ** — Q3 8-K (11-16) disclosed ~$9.6B contract value and 212 MW expected in 2027; its `capacity-mw.json` entry is probably out of date (inbox ask). Not flagged by the refresh, found in the filing.
- No other tradable name has a "BLANK, data gap", "no statement FCF" or stale EV/MW flag this week.
- **Untradeable benchmarks (rule 30, no follow-up):** 9880.HK, 2590.HK, 2252.HK, DRO.AX EPS YoY blank (no quarterly net income on Yahoo); 6383.T, KGX.DE, DRO.AX no statement FCF; TOELY momentum blank (last trade 2026-10-07).

## Mental model before the scan (Step 0, ✓✓/✓✓✓ holdings)

- **MU / SNDK (✓✓✓)** — Memory is supply-constrained through 2027 on HBM and enterprise SSD; both priced on long-term agreements. The risk is a NAND/DRAM cycle turn.
- **FIX / EME** — Data-center mechanical and electrical contractors with record backlogs (FIX $17.8B, EME RPO $18.6B at Q3).
- **TSM** — Sole leading-edge foundry for every AI accelerator; risks are Taiwan and export rules.
- **NVDA** — Q3 FY27 beat and raised (rev $115.8B, Q4 guide $130B). The overhang is governance: CEO resignation, the SEC/California AG probes and the shareholder suits. R4 2→1 proposal open.
- **CRDO / ANET / ALAB** — AI networking (AECs, Ethernet fabrics, PCIe/UALink switches), each concentrated in a few hyperscalers.
- **MSFT / META** — The largest AI capex spenders, with returns showing up in Azure growth and ad growth.
- **AVGO** — Custom-XPU franchise (Google, Meta) plus AI Ethernet.
- **VRT / NVT** — Data-center power and cooling with backlog-led growth.
- **PLTR** — AI-platform adoption showing up as hypergrowth in US commercial revenue.
- **ASML** — EUV monopoly; 2027–28 supply described as short of demand.
- **WDC / STX** — HDD duopoly sold out on LTAs.

**What the scan changed:** the governance and price shock this week landed on NVDA, and the NAND outlook (TrendForce) moved against SNDK. No customer, capacity or guidance data changed for any other holding.

## ⚠️ Material events

**Held names**
- **NVDA** — Reuters (11-20, two sources): SEC enforcement staff are examining "potential accounting issues". Scope and start date are unknown, and there is no company statement or 8-K. This widens the WSJ-reported disclosure probe of 11-17. NVDA closed about −14% (~$125.5) on 11-20. Former CEO Huang agreed to appear before Senate Banking (Politico 11-17/18; 12-03 requested, unconfirmed). This supports the open R4 2→1 proposal; no rating was changed.
- **META** — Stipulated Delaware Chancery order (11-18): Meta will not issue its proposed non-voting Class C shares while the consolidated fiduciary suits (10 cases, including CalSTRS) are pending. Trial is set for 2027-04-19..23. Governance only.
- **SNDK / MU** — TrendForce (11-19): 4Q26 NAND contract-price rise cut to +8–13%; 1Q27 −0–5% QoQ; all categories turn down from 2Q27. On 11-20 memory names fell 12–14% in the broad sell-off; no company-specific news. This is not a thesis trigger (SNDK's trigger is gross margin below 75% for two quarters, or a broken LTA), but it is the first credible forecast of NAND price declines.
- **TSM** — A new BIS remote-access rule took effect 11-19 (licences for Indonesia, Malaysia, Singapore, Thailand and Brazil; most of the AI Diffusion Rule rescinded). Nikkei (11-20) says the impact reaches beyond AI chips and that TSMC is suspending some shipments. That detail is paywalled and **unverified**.

**Watchlist, not held**
- **PANW** (rank ~98) — Q1 FY27 revenue $3.44B (+39%); FY guide raised to $14.52–14.57B. Buying Applied Compute for **$4.5B in stock** (HSR pending). 8-K 2.02/3.02, 11-18.
- **RCAT** — Q3 revenue $11.8M (+22%) but gross profit only $65K; **FY26 revenue target withdrawn**. 8-K 2.02, 11-16.
- **SHAZ** — Q3 revenue $9.9M, ~$9.6B total contract value including a $1.32B 5-yr take-or-pay deal with an AI lab; ARR guide $400–450M by Jan 2027; new CFO/COO/CLO; $356M GPU-backed debt. 8-K 2.02/7.01, 11-16.
- **MTZ** — Bought Murphy Corporation for ~$1.25B cash, funded by a new 1-yr $1.25B term loan. 8-K 1.01/2.03, 11-20.
- **AMD** — Closed the ~$8.2B all-stock World Labs purchase (14.98M shares). 8-K/A 3.02, 11-13/16.
- **AAOI** — New $550M at-the-market equity program (large relative to its size). 8-K 1.01, 11-17.
- **TE** — $100M ATM (Roth); CFO also named President. 8-Ks 11-16, 11-18.
- **OKLO** — Take-or-pay enrichment supply with Centrus for 2029–31 deliveries, $35M prepayments. 8-K 1.01, 11-11 (filed 11-17).
- **TEM** — AstraZeneca renewed through 2031, $200M commitment (~$40M/yr). 8-K 1.01, 11-16.
- **MOD** — Investor Day: FY29 revenue target $5.7–7.7B (from $2.1B), data centers +60–80%/yr, $500M buyback; renamed Modexus Solutions (ticker unchanged). 8-Ks 11-16, 11-18.
- **DUK** — North Carolina rate order: ROE 9.8% (10.95% asked); increases $496M (DEC) / $338M (DEP), about half of what was asked; the commission set its own large-load data-center terms (15-yr minimum contracts above 100 MW, 75% minimum bill). 8-K 8.01, 11-17.
- **D** — HSR waiting period expired for the NextEra combination; other approvals pending. 8-K 8.01, 11-20.
- **MDB** — Acquired Firebolt (terms not disclosed). 8-K 7.01, 11-17.
- **BTDR** — CTO resigns effective 11-30, no successor. 6-K 11-16.
- **PSIX** — CFO leaving; outside consultant interim from 11-28. 8-K 5.02, 11-19.
- **PDYN** — Exclusive US rights to IAI loitering munitions; FY26 cash burn at or above the top of its guide. 8-K 7.01, 11-18.
- **GEV** (rank ~25) — SSE: "a few dozen" Haliade-X turbines at Dogger Bank A need repairs; CfD start moved to 2027-07-31; no GEV financial impact quantified (reNEWS/Offshore Magazine, 11-19/20).
- **INTU** — Q1 FY27 guidance cut and Mailchimp sale were already logged 11-19. The rule-35 hold was set 11-19 (expires 2027-03-01).

**Market context.** 11-20: Nasdaq −5.3%, S&P −3.7% (UPI); AVGO −14%, AMD −13%. Cited drivers: AI-capex return doubts, the NVDA SEC report, and Anthropic's post-IPO fall.

## 📊 Earnings refreshed

Every Watchlist name was refreshed (`refresh_objective_inputs.py all`, then reverse-DCF, 50DMA and `recalc --sync`). Score moves were small because the full refresh on 11-20 (#365/#368) had already rebased everything. No name moved more than 5 points. Tier changes: **BE ✓→✓✓** (69.9→70.4, not near entry) and **FIX ✓✓→✓✓✓** (84.6→85.1).

| Ticker | Reported | Score before → after | Note |
|---|---|---|---|
| NVDA | Q3 FY27, 11-17 | 83.0 → 83.3 | Yahoo statements still end 2026-07-31 (BEHIND) |
| POWL | FQ4 FY26, 11-16 | 73.7 → 74.0 | Rev $397M +33%; GM 34.9% (+430bps QoQ, under the 500bp line); book-to-bill 1.8x; backlog $2.7B. Tradable rank 19, one off entry |
| KEYS | FQ4, 11-19 | 70.3 → 72.0 | Rev $1.99B +40%, orders +53%; 📊 possible rule-9 (EPS nearly doubled; consensus not verified); Yahoo BEHIND |
| KLIC | FQ4, 11-18 | 72.1 → 72.0 | Rev $410M +131%; release names Raj Talluri President & CEO (appointment 8-K not seen) |
| P (Everpure) | Q3 FY27, 11-18 | 60.6 → 60.6 | Rev $1.5B +51%; FY guide raised to $5.20–5.21B; Yahoo BEHIND |
| PANW | Q1 FY27, 11-18 | 62.1 → 62.6 | See material events |
| RCAT | Q3, 11-16 | 46.4 → 46.4 | 📊 rule-9: target withdrawn, gross margin ~0.6% vs ~15% in H1 — candidate for `/earnings-update` |
| SHAZ | Q3, 11-16 | 45.6 → 45.8 | 📊 capacity/contract step-up, see missing data |

TTM vs MRQ: POWL's FQ4 margin (34.9%) runs above its trailing average. No MRQ check was run on the others this week.

## 💼 Portfolio pipeline

- **No model event, no ticket.** "membership & tiers unchanged since last rebalance — snapshot frozen". Automatic tickets are OFF anyway (`execution.auto_tickets: false`, Dom 2026-11-20).
- **Exit clocks:** AMZN (tradable rank 61, below exit rank 18) has had a clock running since 2026-11-20. It is **seam-damped until 2026-11-27** (the #365 methodology seam), so the exit can confirm on the first real run after 11-27. With auto tickets off, the sell will not trade on its own.
- **STX:** tradable rank 18 after the refresh, back inside the exit line; no clock is running in config (the Targets sheet still shows the old 11-20 EXIT PENDING text until the next rebalance writes it).
- **On the edge:** POWL rank 19 (74.0) and RDDT rank 20 (73.6) sit just outside entry rank 15; ALAB 16, WDC 17 and STX 18 sit in the dead-band.
- **Flags:** Layer 06 is 26% of the portfolio (no layer cap active).
- **Capitulation check (AMZN):** clean — P/S at the 35th percentile of its 3-yr range, rev YoY 12.1% vs a 12.9% median. Not a capitulation setup.
- **Theses:** every portfolio name has a three-sentence thesis (rule 39).
- **Weekly mark** (`tracking/performance-series.json`, 11-13 → 11-20 closes): model **−15.9%** vs SMH −17.8%, QQQ −10.5%, SPY −8.6%, EW universe −12.0%, EW roster −15.6%. The 11-20 day alone: model −10.2% vs SMH −10.6%, QQQ −5.7%. Since 2026-05-26: model −28.0%, SMH −33.6%, QQQ −16.5%.

## 🔬 Rating integrity

191 rated names: 0 ungated; **1 held/top-25 gate failure: GEV** (rank ~25; briefing older than 90 days); 82 stale (>90 d); 103 briefings expired, none on held names. The Sunday rating-research rotation should take GEV first.

## 🧨 Thesis-break triggers

- **None fired.** NVDA's trigger (FY28 growth outlook cut, or hyperscale DC revenue falling two quarters) did not fire: the 11-17 call raised the FY28 outlook to ~75%. The SEC probe is a governance and legal risk, not this trigger.
- **TSM:** the Nikkei "TSMC suspending some shipments" line under the new BIS rule is unverified and does not meet the trigger (fabs stopped shipping). Watch it.
- **NVT (held) has no trigger** (`thesis_watch.py` exit 1). Inbox ask recorded.

## 🗓️ Inputs behind

- **BEHIND** (Yahoo statements older than the newest earnings 8-K): NVDA (07-31 vs 11-17), AMAT (07-31 vs 11-12), **TER (06-30 vs 10-28, a month)**, KEYS (07-31 vs 11-19), P (07-31 vs 11-18). The SEC fallback did not supply newer quarters; the 10-Qs are likely not filed yet. TER is the one to look at.
- **NOT CHECKABLE, US-listed:** OKLO, NNE, GFS, WYFI (no earnings 8-K under 2.02 or no CIK match). The rest are foreign filers or local listings.

## 🏗️ Hyperscaler capex

No new quarters filed (0 cells written). Combined 2026-Q3 capex for AMZN, GOOGL, META, MSFT and ORCL: $230.4B, +118% on 2025-Q3 (SEC filings via `hyperscaler_capex.py`).

## 🎯 Calibration

No forecasts due (0 resolved, 0 needs_review).

## 🩺 Run health

- **Daily watch ran 4 of 5 weekdays** (11-16, 11-17, 11-18, 11-19). **11-20 missed**: its branch was opened but nothing landed. 11-11 was also missed in the 14-day window.
- daily-refresh.yml: 1 real failure in the last 40 runs (2026-11-13).
- **Heartbeat: `series` job stale (>3 days without a successful run)**, even though the GitHub daily-refresh PRs merged on 11-20/21. The local launchd series job is what is quiet; check it.
- Account reconciliation skipped (unattended run).

## Routine filings

AAON new $250M term loan + revolver extension (11-13); AAON Baird slides (11-16); BWXT $500M 6.5% notes and 2028/29 note refinancing (11-13); QCOM $4.0B notes (11-13); FLEX/Axiom spin credit lines (11-17); HPE Elliott agreement amendment, new director (11-18); SSII CEO salary-in-stock and press release (11-17, 11-19); ONDS resale registration (11-18); AMD bylaws (11-18); EXE $1.0B CP program (11-20); HSAI EGM record date, RSU grant, $100M buyback (6-Ks); SWKS director pay (8-K/A); TSM 9M IFRS statements; VRT dividend $0.25→$0.40; CIEN new Chief Product Officer; D $1.2B notes; MOD vote/name change; POET Q3 (rev $1.03M, cash $774M); SEI acquired-business financials; STM weekly buyback; TTMI unit reorganization; VST TRA notice; SO $2.0B equity units; UMC equipment purchases; NXPI €1B notes and dividend; COHR $2.0B buyback and vote; DUK $875M notes; PLUG investor slides; ORCL, WDC, SNDK annual-meeting votes; SNDK 8-for-1 split effective 11-20; ONTO/FIX buybacks and WDC revolver (already logged).

## New 13F activity

- **Situational Awareness LP (tracked): 13F-HR filed 2026-11-16 (Q3).** `13f-tracking.xlsx` has sheets only through SALP-2026-Q1, so **Q2 and Q3 are both unprocessed**. Run `/thirteenf-delta`.
- Watch-only: Berkshire, Tiger Global, Coatue and Lone Pine filed 13F-HRs on 11-16 (Whale Rock 11-13 was reported last week).

## Could not verify

- Analyst consensus for this week's reporters (company guides used instead).
- KLIC's CEO appointment 8-K.
- Nikkei's TSMC shipment-suspension detail (paywall).
- The SNDK −14% figure for 11-20.
- WIRED's "Huang lying" framing (not found; dropped).
- PDYN's first announcement date for the IAI deal.

## Needs Dom

- New this run: CLSK EV/MW refresh (capacity-mw.json), SHAZ capacity entry, NVT thesis-break trigger.
- Not inbox items but yours to start: `/thirteenf-delta` for SALP Q2+Q3, `/earnings-update RCAT`, the stale `series` heartbeat.
- Inbox: 3 open — https://app.notion.com/p/41cb69da11c0817284b1cb6eb543c7f0
- Notion page: https://app.notion.com/p/41fb69da11c081a1b7a1f83c09dbe43a
