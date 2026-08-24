# Litigation / docket sweep — high-concentration cohort (2026-08-24)

First run of the new `/refresh-context` **Step 2d** check (`scripts/litigation_check.py`)
as a backfill sweep, rather than waiting ~6 months for the rule-12 rotation to reach
all 214 rated names.

**Cohort (32 names), selected objectively from our own ratings — not by hand:**
- **24 names at R1 (Cust Conc) ≤ 2** — the Watchlist's own high-customer-concentration rating.
- **8 Layer-09 miner/neocloud names at R1 = 3** — single-anchor structures where the
  concentration rating understates the counterparty shape.

This is the profile where a filings-only view is most likely to be complete and still
wrong — which is exactly how the BW miss happened.

---

## Headline result

**1 disclosure mismatch (BW) — the one already known. No second BW.**

That is the most useful thing the sweep establishes: the BW pattern is **rare**, not
endemic. Every other name with a pending securities docket discusses litigation in its
own filings. The check is doing its job, and the base rate is low.

**9 of 32 names carry a pending securities docket** — none of it previously recorded in
any briefing.

---

## Pending securities dockets found

| Ticker | Case | Docket | Court | Filed | Own filing mentions litigation? |
|---|---|---|---|---|---|
| **BW** | Cho v. Babcock & Wilcox Enterprises | 5:26-cv-00886 | N.D. Ohio | 2026-04-14 | **NO → ⚠️ MISMATCH** |
| **KEEL** | (captioned *Bitfarms*) | 1:25-cv-02630 | E.D.N.Y. | 2025-05-09 | YES |
| **SWKS** | Cesar Nunez v. Skyworks Solutions | 8:25-cv-00411 | C.D. Cal. | 2025-03-04 | YES |
| **CRWV** | Masaitis v. CoreWeave | 2:26-cv-00355 | D.N.J. | 2026-01-12 | YES |
| **AVAV** | Norrell v. AeroVironment | 1:26-cv-01429 | E.D. Va. | 2026-05-26 | YES |
| **RCAT** | Olsen v. Red Cat Holdings | 2:25-cv-05427 | D.N.J. | 2025-05-23 | YES |
| **SYM** | Decker v. Symbotic | 1:24-cv-12976 | D. Mass. | 2024-12-03 | YES |
| **BTDR** | In re Bitdeer Technologies Group Securities Litigation | 1:25-cv-10069 | S.D.N.Y. | 2025-12-04 | **not checked** — see gaps |
| **HUT** | In re Hut 8 Corp. Securities Litigation | 1:24-cv-00904 | S.D.N.Y. | 2024-02-07 | YES |

Terminated (context only, no live R4 input): SEI (Pirello, terminated 2026-02-18),
SWKS (Tsvetkov; In re Skyworks Derivative), AVAV (Miami Beach Pension, terminated
2026-08-03; Bissing), SYM (Fox, terminated 2025-03-11).

**Every one of these is an allegation.** None is established wrongdoing, all are
contested, and most securities class actions settle small or are dismissed. They are
R4 *inputs*, not R4 verdicts.

## No federal docket found in RECAP (record as "no docket found", NOT "no litigation")

TE · WYFI · SHAZ · ALAB · KTOS · PDYN · NBIS · CIFR · HIVE

## Dockets found, but none securities

- **IP/patent only** (D3 moat input, not R4): CRDO (6), STX (3), CORZ (1), AMBA (1),
  CEVA (1), RIOT (1)
- **Other / low-precision only**: KN (20 — all unrelated; a "Knowles" search returns a
  serial ADA plaintiff's suits and personal bankruptcies), AEVA (1 — "Aeva, LLC", a
  different entity)
- **Clean, filings discuss litigation normally**: MOD, IREN, WULF, CLSK, APLD

---

## Gaps and caveats (do not read this sweep as exhaustive)

1. **BTDR mismatch check incomplete.** Bitdeer is a foreign private issuer (20-F/6-K,
   no 10-Q), so there is no cached periodic filing to cross-check. Its pending S.D.N.Y.
   securities case is real; whether Bitdeer discloses it is **unverified**. Same
   limitation applies to any FPI in the universe.
2. **Absence is weak evidence.** RECAP mirrors PACER without guaranteed completeness.
   Nine "clean" names above mean *no docket surfaced*, not *no litigation*.
3. **State-court and regulatory matters are out of scope entirely** — this is a federal
   docket index. SEC enforcement, state AG actions and arbitration are invisible to it.
4. **Terminated ≠ resolved in the company's favour.** A dismissal and a settlement both
   show as terminated; the docket record does not distinguish them.
5. **Only the newest cached filing is cross-checked.** A case disclosed two quarters ago
   and dropped since would not flag.

## Data-quality issue found (unrelated to litigation, worth fixing)

**CIFR's Watchlist `Company` is "Cipher Digital Inc." — the company is Cipher Mining Inc.**
The sweep searched the wrong name and returned clean; a search on the correct name also
returned clean, so **the CIFR result stands**. But the Watchlist field is wrong and will
mis-key anything else that reads it.

## Three script bugs the sweep exposed (all fixed + regression-tested)

The sweep's real value was as a shakedown of a one-day-old tool. Every one of these
produced a **false clean** — the failure mode that matters:

1. **Former names.** Dockets are captioned under the entity name *at filing*. KEEL
   ("Keel Infrastructure Corp. (fka Bitfarms)") read clean while "Bitfarms" returns a
   pending case. Now searches current **and** former names — rebrands are endemic here
   (miner→AI pivots, de-SPACs). *This found a real case that was otherwise invisible.*
2. **Single-character token debris.** "Nebius Group N.V." → tokens `Nebius, N`; the bare
   `N` returned zero dockets. NBIS read clean for the wrong reason.
3. **Silently empty reports.** Names whose only hits were contract/bankruptcy printed no
   docket line at all — indistinguishable from clean (KN, AEVA). Added a residual bucket,
   capped at 3 with `--all-other`.

Plus: anonymous CourtListener 429s at ~1s spacing (5 names skipped mid-sweep). Added
exponential backoff and a `--delay` default of 4s. The skips were reported honestly
rather than as clean results — that guardrail worked.

---

## What to do with this

- **BW R4** — actionable on verified fact (see `per-stock/BW/context-2026-08-24.md` §5).
- **KEEL, CRWV, AVAV, RCAT, SYM, SWKS, HUT, BTDR** — each has a pending securities
  docket that no briefing records. These are **R4 inputs for the next rating session**,
  not automatic downgrades. Read what is alleged before moving anything.
- **BTDR** — pull a 20-F/6-K and complete the disclosure cross-check.
- **CIFR** — fix the `Company` field in the Watchlist.
- **Backfill remainder** — 182 rated names still unswept. The rule-12 rotation will
  reach them at 8/week; a second sweep tranche could target the next-highest-risk
  profile (recent sharp drawdowns on good reported numbers).
