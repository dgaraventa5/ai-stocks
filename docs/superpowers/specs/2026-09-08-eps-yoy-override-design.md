# EPS YoY ex-item override for the rule-9 refresh (design)

**Date:** 2026-09-08 · **Status:** proposed, awaiting Dom's review · **Scope:** bounded
(one script, one data file, one test file) · **Rule touched:** 15 (input hygiene),
9 (refresh mechanics). No scoring band, weight, or Watchlist column changes.

## 1. Problem

Rule 15 says: blank the EPS YoY input when a filing documents that the GAAP YoY
change is dominated by a non-operating item. The refresh script
(`scripts/refresh_objective_inputs.py`) enforces this with two guards on the
EPS YoY cell (col 18):

- an existing blank is preserved forever ("likely a documented one-off");
- a fresh value with |YoY| ≥ 300% is withheld for a human ruling.

Both guards lose information across quarters, in opposite directions:

1. **A ruling gets overwritten.** On 2026-06-17 WDAY and ADSK were given
   non-GAAP EPS growth (+19, +31) because the GAAP figure sat on a
   restructuring-depressed base. The 2026-07-16 mechanical refresh saw a
   non-blank cell, a fresh value under 300%, and wrote GAAP +226.5 / +223 back
   over the ruling. Nothing in the sheet records that a ruling ever existed.
2. **A blank never expires.** PANW, SNOW, CRWD, ZS have been blank since
   June. The 2026-09-08 pass re-verified them by reading four press releases;
   the script could not have. A blank made for a one-off in Q1 silently
   survives a clean Q2, Q3, Q4.
3. **A sub-300% garbage value is written.** CRM's +86.9% (a $2,613M
   investment gain) is under the withhold line, so the script wrote it and a
   human had to blank it after the fact. The 300% guard is a magnitude
   heuristic; rule 15 is explicitly not magnitude-based.

Blanking also removes PEG from Value (PEG = Fwd P/E ÷ EPS YoY), so each
ruling moves two inputs, not one.

## 2. Goal

A ruling on EPS YoY, once made and cited, is applied by every refresh until
the quarter it was made for is superseded, and is then re-raised, not
silently kept or silently overwritten. Rulings can be "blank" or "use this
ex-item value". The human still makes every ruling; the script only
remembers and expires them.

Non-goals: no automatic ex-item computation, no non-GAAP scraping, no change
to how the 300% guard decides to withhold, no override for any input other
than EPS YoY (rev YoY manual overrides like FIX 2026-07-27 stay out of scope;
the file shape allows adding a key later, but this spec does not).

## 3. Design

### 3.1 The ruling file

`00-master/eps-yoy-overrides.json`, one entry per ticker, single-writer =
the human session that made the ruling (same standing as capacity-mw.json).

```json
{
  "_meta": {
    "definition": "Rule-15 rulings on the EPS YoY input (Watchlist col 18). value=null means a documented blank; a number means an ex-item YoY % that replaces the yfinance GAAP figure. A ruling applies only while quarter_end matches the name's most recent reported quarter; after the next print it is STALE and the script re-raises it.",
    "updated": "2026-09-08"
  },
  "CRM": {
    "quarter_end": "2026-07-31",
    "value": null,
    "basis": "GAAP +86.9% dominated by $2,613M gains on strategic investments; op income flat",
    "source": "8-K Ex-99.1 filed 2026-08-26, Stmt of Ops + note 3",
    "ruled": "2026-09-07",
    "audit_row": "Rating Audit 2026-09-07 CRM EPS YoY (objective)"
  },
  "WDAY": {
    "quarter_end": "2026-07-31",
    "value": 24.4,
    "basis": "non-GAAP diluted EPS $2.75 vs $2.21; GAAP +177% is a $374M deferred-tax benefit",
    "source": "8-K Ex-99.1 filed 2026-08-27, para 1 + income-tax-effects note",
    "ruled": "2026-09-08",
    "audit_row": "Rating Audit 2026-09-08 WDAY EPS YoY (objective)"
  }
}
```

Field rules:

- `quarter_end` (required, ISO date): the fiscal quarter the ruling is about.
  This is the expiry key.
- `value` (required, number or null): null = blank the cell; number = write
  it. An ex-item number must be computed from the filing and its arithmetic
  stated in `basis` (rule 1).
- `basis`, `source`, `ruled`, `audit_row` (required strings): the citation.
  The script refuses an entry missing any of them (rule 3: a ruling without
  a reason is a guess).

The 2026-09-08 rulings are the seed: CRM, WDAY, INTU, MDB as `null`; PANW,
SNOW, CRWD, ZS as `null` (loss-based, undefined). The Q2 FY27 ex-item values
for CRM (+15.8) and WDAY (+24.4) are NOT seeded; Dom chose to leave the
blanks on 2026-09-08. The example above shows the ex-item shape only.

### 3.2 Script behaviour

In `apply_guards`, the EPS YoY branch gains a first step. The fetcher already
returns the yfinance `info` dict; `info["mostRecentQuarter"]` (epoch seconds)
is the name's latest reported quarter end. The rule-15 override is checked
before the existing guards (a)–(d):

| Override state | Action | Flag printed |
|---|---|---|
| Entry present, `quarter_end` == most-recent quarter | write `value` (None blanks the cell) | `EPS YoY: rule-15 override applied (value/blank), ruled {ruled}, {source}` |
| Entry present, `quarter_end` < most-recent quarter | fall through to guards (a)–(d) unchanged, but guard (a) no longer preserves silently: a blank cell with a stale override is treated as "ruling expired" | `EPS YoY: override for q/e {quarter_end} is STALE (latest quarter {mrq}) — fresh GAAP {v}; re-rule (write, blank, or ex-item) and update eps-yoy-overrides.json` |
| Entry present, `quarter_end` > most-recent quarter | refuse the entry (typo or yfinance lag), fall through | `EPS YoY: override q/e {quarter_end} is AHEAD of yfinance mostRecentQuarter {mrq} — check the date; ignored this run` |
| `mostRecentQuarter` missing from info | override cannot be dated; fall through | `EPS YoY: override present but yfinance has no mostRecentQuarter — applied nothing; hand-check` |
| No entry | guards (a)–(d) exactly as today | unchanged |

Stale-override handling is the only behavioural change to the existing
guards: today guard (a) preserves any blank forever; with a stale override on
file the blank is flagged as expired instead. A blank with **no** override
entry still gets today's "preserved blank" flag, so nothing regresses for
names never ruled through the file. Over time every documented blank should
gain an entry (the seed covers the current eight).

The file is read once per run via a small loader (`load_eps_overrides(path)`)
with the path injectable for tests, mirroring `mw_staleness_flag`'s
`capacity_json` argument. The loader validates the schema and raises on a
malformed entry so a bad edit fails the run loudly rather than being skipped.

`--dry-run` prints the same flags without writing, as today.

### 3.3 What this does not touch

- Rating Audit rows are still appended by the human session (the file's
  `audit_row` points at them; the script never writes the audit sheet).
- PEG needs no change: it derives from col 18, so the override flows through.
- `recalc_watchlist.py`, the Excel formulas, `rebuild_watchlist_formulas.py`,
  `refresh_targets.py`: untouched.
- The 300% withhold stays. It is the safety net for names with no ruling.
- The earnings sentinel and `/refresh-objective` both call this script, so
  they inherit the behaviour with no prompt changes beyond one line in
  `.claude/commands/refresh-objective.md` step 2 telling the operator to
  record rule-15 rulings in the json as well as the audit sheet.

## 4. Tests (`tests/test_refresh_objective_inputs.py`, extend)

Pure, no network; the fetcher is already injectable.

1. Override with matching quarter and `value: null` → writes None over a
   non-blank cell; flag says "override applied (blank)".
2. Override with matching quarter and a number → writes that number even
   when yfinance's fresh value is ≥ 300% (override beats the withhold).
3. Override with an older `quarter_end` → cell handled by the old guards;
   flag contains "STALE"; a blank cell is NOT silently preserved.
4. Override with a future `quarter_end` → ignored, flag contains "AHEAD".
5. `mostRecentQuarter` absent → override ignored, flag says so; existing
   guards run.
6. Malformed entry (missing `source`) → loader raises; run does not start.
7. No entry → byte-identical behaviour to the current test expectations
   (the existing guard tests keep passing unchanged).
8. Dry-run prints flags and leaves the cell untouched.

## 5. Migration

One-time: seed `eps-yoy-overrides.json` with the eight 2026-09-08 rulings
(`quarter_end` = each name's July-2026 fiscal quarter end, from the cached
Ex-99.1 files). No sheet change; the cells already match the seed.

## 6. Risks and open points

- **yfinance `mostRecentQuarter` lag.** Yahoo sometimes updates
  `earningsQuarterlyGrowth` before `mostRecentQuarter`, or vice versa. The
  AHEAD/STALE flags surface a mismatch rather than guessing; the cost is one
  extra manual look in that window. The weekly scan (rule 9 catch-all)
  covers the case where a stale flag is missed on a sentinel night.
- **Ex-item values are a judgment.** The file makes them visible and
  expiring; it does not make them right. Rule 15's "documented evidence, not
  magnitude" standard applies to every entry, and the `basis` field must
  show the arithmetic.
- **Rule-4 note.** Col 18 is an input cell, not a formula, so writing an
  override there is not a formula-over-value violation.
