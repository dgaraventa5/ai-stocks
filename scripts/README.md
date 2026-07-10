# scripts/

Data-fetching utilities for the AI Supply Chain research project. All scripts
respect the operating rules in `../CLAUDE.md` — particularly:

- SEC EDGAR User-Agent and 10 req/sec rate limit (`common.py` enforces both)
- "Flag, don't assume" — missing data is surfaced via `common.flag()` and the
  `Data flags` sheet in `financials.xlsx`, never silently coerced
- Excel formulas, not hardcoded values, for any derived field

## Install

```bash
pip install -r ../requirements.txt
```

## Files

| Script | Purpose |
|---|---|
| `common.py` | Shared User-Agent, rate limiter, ticker→CIK cache, project paths. Import, don't run. |
| `build_workbooks.py` | One-shot: generate `00-master/portfolio.xlsx`, `tracking/13f-tracking.xlsx`, `tracking/hyperscaler-capex.xlsx`. Re-running overwrites — don't run after entering data. |
| `sec_edgar.py` | Fetch SEC filings (10-K / 10-Q / 8-K / etc.) into `per-stock/{TICKER}/filings/`. |
| `yfinance_fundamentals.py` | Pull fundamentals + statements into `per-stock/{TICKER}/financials.xlsx` with derived ratios as formulas. |
| `parse_13f.py` | Resolve a fund's latest 13F-HR (or a specific accession), parse the information table, print top holdings. |
| `new_ticker.py` | Scaffold `per-stock/{TICKER}/` from templates. Optional flags to chain `yfinance_fundamentals.py` and `sec_edgar.py`. |
| `weekly_scan_runner.py` | Primary weekly scan: pull each ticker's 8-Ks/6-Ks from EDGAR for the window, classify material vs. routine, check tracked-fund 13Fs. Exits to `web_scan.py` if EDGAR egress is blocked. |
| `web_scan.py` | Date-verified, source-filtered web fallback for the weekly scan when EDGAR is blocked. `--plan` emits the full-watchlist query plan (holdings/✓✓ names get filing+press+news queries, the tail gets a filing query, all domain-filtered to SEC/wire sources); `--verify hits.json` date-filters harvested hits to the window, flags undated ones UNVERIFIED, and classifies materiality by keyword. |

## Weekly scan fallback (EDGAR blocked)

When `data.sec.gov` is unreachable (every cloud session since 2026-06-12), the ad-hoc
"search each ticker's news" approach leaks material events — it has no real recency
filter and buries headline-light items (the AVGO CFO change was missed by four scans).
Use the systematic fallback instead:

```bash
python3 scripts/web_scan.py --plan --from 2026-07-03 --to 2026-07-10   # queries to run
# ...run each WebSearch(query, allowed_domains); collect hits into hits.json as
#    [{"ticker","title","url","date","snippet"}, ...]
python3 scripts/web_scan.py --verify hits.json --from 2026-07-03 --to 2026-07-10
```

`--verify` drops out-of-window hits, surfaces undated ones as UNVERIFIED (never assumed
in-window, per CLAUDE.md rule 3), and flags material events via a keyword net covering
leadership/M&A/capacity/guidance/financing/legal/going-concern.

## Common workflows

### Start coverage on a new ticker

```bash
python3 scripts/new_ticker.py NVDA --fetch-financials --fetch-filings
```

Creates `per-stock/NVDA/{thesis.md, news-log.md, catalysts-watchlist.md, filings/*.htm, financials.xlsx}`.

### Pull just the latest 8-K filings

```bash
python3 scripts/sec_edgar.py VRT --forms 8-K --since 2026-01-01
```

### Check what Coatue / Whale Rock owned last quarter

```bash
python3 scripts/parse_13f.py --cik 0001135730 --period 2026-Q1 --top 30
```

### Refresh financials for an existing ticker

```bash
python3 scripts/yfinance_fundamentals.py NVDA
```

Overwrites `per-stock/NVDA/financials.xlsx`. Diff vs. prior quarter in git if
you want to see what changed.

## Notes

- The `.cache/` directory holds the SEC ticker→CIK map (refreshed by deleting it).
- yfinance occasionally returns partial data on small-caps; that's why every
  numeric field in the Summary tab is checked and flagged.
- For 13F XML, namespaces vary by filer (`ns1:` vs. `ns3:` etc.). The parser
  uses namespace-agnostic XPath (`local-name()`) so it works across filers.
