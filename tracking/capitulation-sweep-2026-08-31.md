# Capitulation-flag seed sweep — 2026-08-31

One-time full-watchlist sweep of `scripts/capitulation_flag.py` (rule 32-A) to
seed the rule-17 calibration sample. Weekly-scan Step 7d only checks exit-side
names (~1-2 firings/month); at that trickle the ~30-resolved-forecast evidence
bar is a year-plus away. This sweep starts the clock on 11 forecasts at once.
Approved by Dom 2026-08-31.

**Result: 214 names swept — 11 flagged (forecast logged for each), 152 clean,
51 skipped.** Forecasts resolve 2026-12-03 (63 trading days) against each
name's frozen layer-cohort EW basket, at the uninformed 0.55 base-rate prior.

## Flagged (P/S ≤ 10th pctile of own 3y range AND rev YoY ≥ 3y median)

| Ticker | P/S | P/S 3y pctile | Rev YoY | 3y median YoY |
|---|---|---|---|---|
| TLN | 3.97 | 0.2 | 36.7% | 36.7% |
| SNPS | 9.46 | 4.0 | 54.4% | 20.2% |
| META | 5.85 | 8.9 | 43.7% | 28.6% |
| AAON | 3.44 | 0.1 | 94.7% | 36.0% |
| INTU | 3.96 | 8.7 | 115.9% | 37.4% |
| RDDT | 8.46 | 4.0 | 105.1% | 90.4% |
| SERV | 55.92 | 2.1 | 635.9% | 619.6% |
| TNC | 0.95 | 7.2 | 11.7% | 5.3% |
| ISRG | 12.73 | 2.8 | 28.4% | 19.9% |
| MBLY | 1.04 | 6.3 | 16.0% | 14.8% |
| ONDS | 29.07 | 5.6 | 1872.0% | 578.7% |

## Interpretation notes (rule 3 — read before trusting any single row)

- **The forecasts grade the mechanical signal as implemented**, warts included
  — a resolved sample tells us whether THIS flag predicts, not whether a
  hand-cleaned version would.
- **INTU (115.9%) and AAON (94.7%) YoY look inflated** vs. those businesses'
  known growth rates — likely XBRL tag-merge artifacts in the quarterly
  decomposition. Verify against the 10-Q before citing either number in a
  briefing.
- **SNPS YoY (54.4%) is acquisition-boosted** (Ansys close) — the flag cannot
  distinguish organic from acquired growth. Same caveat class as above.
- **META and RDDT are current holdings** — a capitulation flag on a held name
  is context for the exit-side review (the flag's original purpose), not a
  buy-more signal.
- **SERV/ONDS-style micro-cap hypergrowth rows** (YoY in the hundreds off tiny
  bases) fire the flag easily; whether the signal means anything there is
  exactly what calibration will show — do not pre-filter them out.
- Share count held constant at today's value (rule-14 machinery) — percentile
  flattered DOWN for heavy diluters.

## Skipped (no forecast, stated reason — a skip is not a clean result)

- XEL — SEC companyfacts: latest XBRL quarter end 2019-09-30 is >200 days stale — check skipped
- CCJ — SEC companyfacts: companyfacts fetch failed (KeyError: 'us-gaap') — transient? retry — check skipped
- OKLO — SEC companyfacts: only 2 quarterly periods in companyfacts — check skipped
- NNE — SEC companyfacts: only 1 quarterly periods in companyfacts — check skipped
- SBGSY — SEC companyfacts: no CIK mapping for ticker — check skipped
- ABBNY — SEC companyfacts: no quarterly periods under any known revenue tag — check skipped
- HTHIY — SEC companyfacts: no quarterly periods under any known revenue tag — check skipped
- ASML — SEC companyfacts: no quarterly periods under any known revenue tag — check skipped
- TOELY — SEC companyfacts: no CIK mapping for ticker — check skipped
- CAMT — SEC companyfacts: latest XBRL quarter end 2021-06-30 is >200 days stale — check skipped
- TSM — SEC companyfacts: companyfacts fetch failed (KeyError: 'us-gaap') — transient? retry — check skipped
- GFS — SEC companyfacts: companyfacts fetch failed (KeyError: 'us-gaap') — transient? retry — check skipped
- TSEM — SEC companyfacts: latest XBRL quarter end 2024-06-30 is >200 days stale — check skipped
- UMC — SEC companyfacts: companyfacts fetch failed (KeyError: 'us-gaap') — transient? retry — check skipped
- POET — SEC companyfacts: no quarterly periods under any known revenue tag — check skipped
- NBIS — SEC companyfacts: no quarterly periods under any known revenue tag — check skipped
- IREN — SEC companyfacts: only 6 quarterly periods in companyfacts — check skipped
- CLSK — SEC companyfacts: latest XBRL quarter end 2024-06-30 is >200 days stale — check skipped
- BTDR — SEC companyfacts: companyfacts fetch failed (KeyError: 'us-gaap') — transient? retry — check skipped
- KEEL — SEC companyfacts: only 4 quarterly periods in companyfacts — check skipped
- CRDO — SEC companyfacts: latest XBRL quarter end 2026-01-31 is >200 days stale — check skipped
- BESIY — SEC companyfacts: no CIK mapping for ticker — check skipped
- WYFI — SEC companyfacts: only 7 quarterly periods in companyfacts — check skipped
- SHAZ — SEC companyfacts: only 4 quarterly periods in companyfacts — check skipped
- HIVE — SEC companyfacts: only 7 quarterly periods in companyfacts — check skipped
- STM — SEC companyfacts: no quarterly periods under any known revenue tag — check skipped
- SPCX — SEC companyfacts: only 2 quarterly periods in companyfacts — check skipped
- ASX — SEC companyfacts: companyfacts fetch failed (KeyError: 'us-gaap') — transient? retry — check skipped
- NTAP — SEC companyfacts: latest XBRL quarter end 2026-01-23 is >200 days stale — check skipped
- 5347.TWO — SEC companyfacts: no CIK mapping for ticker — check skipped
- HHUSF — SEC companyfacts: no CIK mapping for ticker — check skipped
- 0981.HK — SEC companyfacts: no CIK mapping for ticker — check skipped
- 9880.HK — SEC companyfacts: no CIK mapping for ticker — check skipped
- 6954.T — SEC companyfacts: no CIK mapping for ticker — check skipped
- 6506.T — SEC companyfacts: no CIK mapping for ticker — check skipped
- AUTO.OL — SEC companyfacts: no CIK mapping for ticker — check skipped
- 6383.T — SEC companyfacts: no CIK mapping for ticker — check skipped
- KGX.DE — SEC companyfacts: no CIK mapping for ticker — check skipped
- 2590.HK — SEC companyfacts: no CIK mapping for ticker — check skipped
- 2252.HK — SEC companyfacts: no CIK mapping for ticker — check skipped
- 6324.T — SEC companyfacts: no CIK mapping for ticker — check skipped
- 6268.T — SEC companyfacts: no CIK mapping for ticker — check skipped
- 6481.T — SEC companyfacts: no CIK mapping for ticker — check skipped
- 2049.TW — SEC companyfacts: no CIK mapping for ticker — check skipped
- 6861.T — SEC companyfacts: no CIK mapping for ticker — check skipped
- HSAI — SEC companyfacts: no quarterly periods under any known revenue tag — check skipped
- 2498.HK — SEC companyfacts: no CIK mapping for ticker — check skipped
- BSL.DE — SEC companyfacts: no CIK mapping for ticker — check skipped
- AVAV — SEC companyfacts: latest XBRL quarter end 2026-01-31 is >200 days stale — check skipped
- DRO.AX — SEC companyfacts: no CIK mapping for ticker — check skipped
- MELE.BR — SEC companyfacts: no CIK mapping for ticker — check skipped

## Next steps

1. Weekly scans keep running Step 7d (exit-side firings add forecasts; the
   one-open-forecast-per-name guard prevents stacking).
2. `resolve_forecasts.py` (weekly-scan step) grades these on/after 2026-12-03.
3. At ~30 resolved `signal.capitulation` forecasts, `calibration_report.py`
   renders the verdict; any scored version of the flag is a rule-8 proposal
   gated on positive skill vs. the base rate.
