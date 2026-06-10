# Portfolio Site — Design Spec

**Date:** 2026-06-10
**Status:** Approved by Dom (brainstorming session)
**Goal:** A light, read-only webapp sharing the AI supply chain portfolio with close friends.

## Decisions made (with rationale)

| Decision | Choice | Why |
|---|---|---|
| Audience model | Pure viewers — nobody writes through the site | Change logging already happens in the repo pipeline; site is a published snapshot |
| Dollar privacy | All dollars indexed to a **$10,000 notional base** | Dollar math stays legible without exposing real account size |
| Access control | One shared password for all friends | Real protection without per-user auth overhead |
| Scope (v1) | Dashboard, Performance, Positions (+thesis snippets), Change log, Weekly scan links | Watchlist explorer (136 names) deferred — most lift, least friend-value |
| Architecture | Python exporter → static JSON → plain static frontend | Matches repo's center of gravity; Python produces data, site consumes it |
| Hosting | Cloudflare Pages (free tier) + Pages Function password gate | $0/month; password enforced server-side, not view-source-able |
| Site structure | Dashboard + sub-pages, headline stats row up front | Dom's pick (structure B with prominent stat row) |
| Visual style | Terminal dark — monospace, dense, dark background | Dom's pick |
| Scan links | Cowork routine appends `{date, url}` to a mapping file; one-time backfill via Notion connector | Notion page URLs can't be derived from titles; routine knows the URL at creation time |
| Frontend stack | Vanilla HTML/CSS/JS + vendored Chart.js. No npm, no framework | 5 read-only views; simplest codebase for a cheaper model to implement and maintain |

## Architecture

```
portfolio.xlsx ─┐
scoring.xlsx ───┤
performance log ┼─► scripts/export_site_data.py ─► site/data/*.json ─► static site
thesis.md files ┤        (privacy boundary,            (committed or
notion-scan-    ┘         $10k scaling here)            CI-generated)
links.json
                  GitHub Action on push ─► run exporter ─► deploy site/ to Cloudflare Pages
```

One-way data flow. The exporter is the **single privacy boundary**: nothing under `site/` reads the workbooks directly, so what friends can see is auditable in one script.

## Components

### 1. Exporter — `scripts/export_site_data.py`

Outputs to `site/data/`:

| File | Source | Contents |
|---|---|---|
| `positions.json` | `00-master/portfolio.xlsx` + scoring Watchlist tab | Per holding: ticker, company name, layer (number + name), weight %, notional $ (weight × 10,000), total score, tier symbol |
| `performance.json` | `tracking/performance-log.md` / track_performance data | Dated series: portfolio value indexed to $10k, SMH, QQQ, equal-weight benchmark; summary stats (total return, vs each benchmark) |
| `changes.json` | Rebalance events (refresh_targets output) + Rating Audit sheet | Per event: date, type (`add` / `drop` / `resize` / `rerate`), ticker, one-line rationale. Structured sources only — not raw git commits |
| `theses.json` | `per-stock/{TICKER}/thesis.md` for current holdings only | Snippet = body text of the "## 1. One-line thesis" section. **Template detection:** if that section still contains template placeholder text (e.g. `{TICKER}`, `{Company Name}`, or the template's instructional boilerplate) or the file is missing ⇒ `null` + exporter warning. Never show boilerplate |
| `scans.json` | `tracking/notion-scan-links.json` | Per scan: date, title, Notion URL |
| `meta.json` | build context | Generated-at timestamp, data as-of date |

Rules:
- **Excluded by design:** real share counts, real dollar values, cost basis. Everything monetary is scaled to the $10k base.
- Fails loudly (nonzero exit) on schema surprises — missing columns, unparseable rows. CI failure means the site stays at its last good version; no silent degradation.
- Uses `openpyxl` (read-only here, so no formula concerns).

### 2. Static site — `site/`

Plain HTML/CSS/JS. One shared stylesheet (`site/css/terminal.css`), Chart.js vendored at `site/js/vendor/chart.umd.js`. Each page loads its JSON with `fetch()` and renders client-side.

Theme: terminal dark — dark background (GitHub-dark palette range), monospace type, green/red for gains/losses, dense tables, colored layer badges.

| Page | Contents |
|---|---|
| `index.html` (Dashboard) | Headline stat row: model value, total return, vs SMH, holdings count, last-updated. Compact performance chart. Top-5 positions. 3 most recent changes. Nav to sub-pages |
| `performance.html` | Full performance chart with benchmark toggles (SMH / QQQ / equal-weight), monthly returns table |
| `positions.html` | All holdings: weight, layer badge, tier, score. Row click expands thesis snippet inline; holdings with `null` thesis show no expander |
| `changes.html` | Full reverse-chronological change log, client-side filter by type |
| `scans.html` | Dated list of weekly scans, each linking out to its Notion page |

### 3. Auth — Cloudflare Pages worker

`site/_worker.js` (Pages "advanced mode" — reliably bundled by `wrangler pages deploy site`): checks a signed cookie; if absent/invalid, serves a styled password form. Password compared against a Cloudflare environment variable (`SITE_PASSWORD`) — never in the repo. Successful login sets a long-lived cookie; friends authenticate once per browser. All routes gated, including `/data/*.json`.

### 4. CI — GitHub Action

`.github/workflows/deploy-site.yml`: on push to `main` → install Python deps → `python scripts/export_site_data.py` → run tests → deploy `site/` to Cloudflare Pages (wrangler). The Cowork routine's Friday commit therefore refreshes the site automatically. Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.

### 5. Notion scan links

- **Mapping file:** `tracking/notion-scan-links.json` — array of `{date, title, url}`.
- **Routine change:** one line added to the Cowork "Weekly scanner" routine instructions (Step 4): after creating the Notion page, append its URL to the mapping file so it lands in the same Step-5 commit.
- **Backfill:** one-time, during implementation — list children of Notion parent page `368b69da11c081968dfdf4e44f6000e0` via the Notion connector, seed the mapping file with existing scan pages.

## Error handling

- Exporter: schema surprise → nonzero exit, CI fails, site unchanged. Missing thesis → `null` + warning (flag, don't assume). Missing scan-link entry for a known scan markdown → warning, scan omitted from `scans.json`.
- Frontend: failed `fetch()` of a JSON file renders an inline "data unavailable" notice rather than a blank page.
- Stale data is visible: dashboard shows `meta.json`'s as-of date.

## Testing

- **Exporter (pytest, fixture workbooks):**
  - No real-dollar value from the fixtures appears anywhere in output JSON (privacy regression test — the critical one).
  - Weights × 10,000 sum to ~$10k; tier symbols map correctly.
  - Template thesis ⇒ `null`; populated thesis ⇒ snippet extracted.
  - Malformed workbook ⇒ nonzero exit.
- **Site smoke check:** script loads each page against exported JSON (real data) and asserts render — no missing-element/console errors.
- CI runs both before deploy.

## Out of scope (v1)

- Watchlist explorer (all 136 scored names)
- Comments, reactions, per-user auth, shadow portfolios
- Rendering scan markdown on-site (links out to Notion instead)
- Custom domain (free `*.pages.dev` URL initially)

## Costs

$0/month on free tiers (Cloudflare Pages + Functions, GitHub Actions within private-repo free minutes). Optional custom domain ~$10–12/year.

## Implementation note

Plan written for execution by a cheaper model: small files, no framework, no build toolchain, explicit per-task verification steps.
