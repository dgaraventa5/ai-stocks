# AI Supply Chain Research

> Systematic, first-principles equity research on AI-infrastructure stocks — a 10-layer supply-chain map and a repeatable 6-category scoring framework.

A personal research repository for developing **independent conviction** on the companies that build, power, and run AI infrastructure. The macro view is the Aschenbrenner *"Situational Awareness"* thesis; this repo does the bottoms-up work to identify and track investable names across the supply chain.

The goal is **not** to chase ideas from 13F filings or social media. It is to do enough first-principles work — read the actual 10-Ks, model the fundamentals, score them consistently — to know *why* a name is or isn't worth owning, and to catch thesis breaks before consensus does.

> ⚠️ **Research, not advice.** This repo produces research, flags opportunities, and surfaces contradictions. It does **not** make trade recommendations. Nothing here is financial advice.

---

## How it works

Every name in the watchlist is scored 0–100 across six weighted categories. Raw metrics are converted to 0–100 sub-scores via calibrated threshold bands (the *Methodology* tab of the scoring workbook), then weighted into a Total Score and Tier.

### Scoring categories

| Category | Weight | What it captures |
|---|---|---|
| **Value** | 20% | Forward P/E, EV/EBITDA, FCF yield, P/S, PEG |
| **Quality** | 20% | Margins, ROIC, balance-sheet strength |
| **Growth** | 15% | Revenue & EPS growth |
| **AI Thesis** | 20% | Directness of AI exposure, moat, durability |
| **Momentum** | 10% | EPS revisions, relative strength, insider activity, 50DMA % |
| **Risk** | 15% | Customer concentration, geography, balance sheet, regulatory, disruption (R1–R5) |

*Weights reweighted 2026-05-25. Some categories swap metrics for specific cohorts — e.g. Layer-10 SaaS uses EV/FCF instead of EV/EBITDA, and the Layer-9 capacity cohort uses EV per secured MW. See [`CLAUDE.md`](CLAUDE.md) for the full rule set.*

### Tiers

| Total Score | Tier | |
|---|---|---|
| 85–100 | ✓✓✓ | Top tier |
| 70–84 | ✓✓ | Strong |
| 55–69 | ✓ | Average |
| 40–54 | ? | Below average |
| 0–39 | ✗ | Avoid |

Objective inputs (margins, FCF, prices) are pulled from data sources and refreshed on an earnings trigger. Subjective ratings (AI Thesis, Momentum, Risk dimensions) follow a documented [rating rubric and audit-log workflow](templates/rating-rubric-and-workflow.md) — every rating decision is logged with rationale, source, and date so past judgment can be debugged.

---

## Repository layout

The supply chain is organized into ten layers, each with its own thematic notes:

| Layer | Folder | Theme |
|---|---|---|
| 1 | [`01-power-generation/`](01-power-generation) | Power generation |
| 2 | [`02-grid-equipment/`](02-grid-equipment) | Grid & electrical equipment |
| 3 | [`03-data-centers/`](03-data-centers) | Data-center build-out |
| 4 | [`04-semi-equipment/`](04-semi-equipment) | Semiconductor equipment |
| 5 | [`05-fabs/`](05-fabs) | Foundries / fabs |
| 6 | [`06-silicon/`](06-silicon) | Silicon (GPUs, accelerators, memory) |
| 7 | [`07-optical-networking/`](07-optical-networking) | Optical & networking |
| 8 | [`08-servers/`](08-servers) | Servers & systems |
| 9 | [`09-cloud/`](09-cloud) | Cloud & neoclouds |
| 10 | [`10-applications/`](10-applications) | Models, software & applications |

Supporting directories:

```
00-master/        Supply-chain map, scoring workbook, portfolio, capacity data
per-stock/        One folder per ticker: thesis, financials, filings, transcripts, news log
tracking/         Weekly scans, quarterly rescores, 13F & hyperscaler-capex trackers
templates/        Per-stock template, rating rubric, update checklists
scripts/          Data-fetching & scoring utilities (see scripts/README.md)
site/             Friend-facing static site (Cloudflare Pages)
tests/            pytest suite (site exporter + performance tracker)
docs/             Design specs & implementation plans
CLAUDE.md         Canonical conventions, data sources, and operating rules
```

`00-master/` holds the working artifacts: [`ai_supply_chain_research_map.md`](00-master/ai_supply_chain_research_map.md) (100+ tickers across the layers), `ai_supply_chain_scoring.xlsx` (the live scoring workbook), `portfolio.xlsx` (positions & sizing), and `capacity-mw.json` (secured power capacity for the Layer-9 cohort).

---

## Data sources

Free tools only — no Bloomberg, FactSet, or paid feeds.

| Source | Used for | Notes |
|---|---|---|
| [SEC EDGAR](https://www.sec.gov/edgar) | Filings — source of truth | 10 req/sec limit + User-Agent header, both enforced in `scripts/common.py` |
| [yfinance](https://github.com/ranaroussi/yfinance) | Fundamentals, market data | TTM data can lag fast-ramp names; statement-based FCF only |
| Company IR pages | Transcripts, decks | Falls back to Motley Fool for transcripts |
| [FRED](https://fred.stlouisfed.org) | Macro / rates / electricity | |
| [EIA](https://www.eia.gov) | Energy & electricity | |
| [13f.info](https://13f.info) | Parsed 13F holdings | For tracking, not idea-sourcing |

---

## Getting started

Requires Python 3.10+.

```bash
# Clone and install dependencies
git clone https://github.com/dgaraventa5/ai-stocks.git
cd ai-stocks
pip install -r requirements.txt
```

Start coverage on a new ticker (scaffolds the folder, pulls financials and recent filings):

```bash
python3 scripts/new_ticker.py NVDA --fetch-financials --fetch-filings
```

This creates `per-stock/NVDA/` with `thesis.md`, `news-log.md`, `catalysts-watchlist.md`, fetched `filings/`, and a `financials.xlsx` whose derived ratios are live Excel formulas.

See [`scripts/README.md`](scripts/README.md) for the full script catalog and common workflows (refreshing fundamentals, parsing a fund's 13F, pulling specific 8-Ks, recalculating the watchlist).

---

## Portfolio site

A password-gated static site for close friends lives in [`site/`](site) and deploys to Cloudflare Pages via [`.github/workflows/deploy-site.yml`](.github/workflows/deploy-site.yml) on every push to `main`.

- **Privacy boundary:** [`scripts/export_site_data.py`](scripts/export_site_data.py) is the *only* path from repo data to `site/data/`. All dollar figures are scaled to a **$10,000 notional base** — real capital, share counts, and cost basis are excluded by design and never leave the repo.
- **Daily freshness:** [`daily-refresh.yml`](.github/workflows/daily-refresh.yml) rebuilds the performance series on weekday crons (targeting ~5pm ET, just after the close), commits if changed, and redeploys.

---

## Tests & CI

```bash
pytest
```

The suite ([`tests/`](tests)) guards the two things that touch the outside world:

- `test_export_site_data.py` — including `test_privacy_no_real_dollars_anywhere`, the regression gate that ensures no real dollar amounts ever reach the published site. **This gate is never weakened.**
- `test_track_performance.py` — the multi-benchmark performance tracker.

Two GitHub Actions workflows run the deploy and the daily refresh.

---

## Operating principles

The full rule set lives in [`CLAUDE.md`](CLAUDE.md). The non-negotiables:

1. **Cite every numeric claim** — filing type + date + section, or URL. No bare numbers.
2. **Flag, don't assume** — missing or contradictory data is surfaced explicitly, never papered over with a guess.
3. **Formulas over hardcoded values** in Excel — workbooks stay live when source data changes.
4. **Don't recommend trades** — the research identifies and flags; the buy/hold/sell decision stays with the human.
5. **Read the actual 10-K** before trusting a data-provider summary.
6. **Default to skepticism** about consensus narratives — the working hypothesis is that most investors are pricing this wrong.

---

*Personal research repository. Not investment advice.*
