"""Fill tracking/hyperscaler-capex.xlsx with quarterly capex from SEC filings.

The demand behind the whole thesis is what the five big cloud buyers spend on
data centers, and the tracker for it sat empty from the day it was built. This
reads each company's cash-flow capex line from SEC companyfacts (free XBRL),
turns the year-to-date figures into single quarters (Q4 = full year - 9 months,
xbrl_periods.quarterly_from_facts), and writes one value per calendar quarter.
Guidance stays with /capex-update, which reads the calls.

  python3 scripts/hyperscaler_capex.py           # print what would change
  python3 scripts/hyperscaler_capex.py --write   # save the workbook

Values are USD millions. A quarter is filed under the calendar quarter its
period ends in, so Oracle's quarter ending in August sits in Q3 and Microsoft's
fiscal Q1 (ending September) also sits in Q3. Every value is cited in the
Sources sheet (rule 1): a computed quarter names both filings. Exits nonzero
if any company could not be read, or is two or more quarters behind the
newest (a sign its filings moved to a new XBRL tag), so "could not look"
never reads as "nothing new".
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "tracking" / "hyperscaler-capex.xlsx"
SHEET = "Capex by quarter"
SOURCES = "Sources"
SOURCE_HEADER = ("Ticker", "Quarter", "Capex $M", "Basis",
                 "Period start", "Period end", "Accession", "Form", "Filed",
                 "Less: period start", "Less: period end", "Less: accession",
                 "Less: filed", "XBRL tag")
LAG_QUARTERS = 2     # a company this far behind the newest quarter is flagged

# Each company's cash-flow capex line, as tagged in its filings.
TAGS = {
    "MSFT": "PaymentsToAcquirePropertyPlantAndEquipment",  # Additions to property and equipment
    "GOOGL": "PaymentsToAcquirePropertyPlantAndEquipment",
    "META": "PaymentsToAcquirePropertyPlantAndEquipment",
    "AMZN": "PaymentsToAcquireProductiveAssets",           # Purchases of property and equipment, incl. internal-use software
    "ORCL": "PaymentsToAcquirePropertyPlantAndEquipment",
}
FIRST_QUARTER = "2024-Q1"
FAILED = "error"


def quarter_label(end: dt.date) -> str:
    return f"{end.year}-Q{(end.month - 1) // 3 + 1}"


def next_label(label: str) -> str:
    year, q = int(label[:4]), int(label[-1])
    return f"{year + 1}-Q1" if q == 4 else f"{year}-Q{q + 1}"


def _is_quarter(days: int) -> bool:
    from xbrl_periods import QUARTER_MAX_DAYS, QUARTER_MIN_DAYS
    return QUARTER_MIN_DAYS <= days <= QUARTER_MAX_DAYS


def _trace(usd_facts) -> dict[str, tuple[dict, dict | None]]:
    """{period end: (fact, subtracted fact or None)}, the same arithmetic as
    xbrl_periods.quarterly_from_facts but keeping the facts used, so a
    computed quarter can cite both filings behind it."""
    direct: dict[str, dict] = {}
    ladders: dict[str, dict[str, dict]] = {}
    for f in sorted(usd_facts or [], key=lambda f: str(f.get("filed") or "")):
        try:
            start = dt.date.fromisoformat(str(f["start"]))
            end = dt.date.fromisoformat(str(f["end"]))
            float(f["val"])
        except (KeyError, TypeError, ValueError):
            continue
        days = (end - start).days
        if days <= 0:
            continue
        ladders.setdefault(f["start"], {})[f["end"]] = f
        if _is_quarter(days):
            direct[f["end"]] = f
    out: dict[str, tuple[dict, dict | None]] = {}
    for start, by_end in ladders.items():
        prev_end, prev = dt.date.fromisoformat(start), None
        for end_iso, f in sorted(by_end.items()):
            end = dt.date.fromisoformat(end_iso)
            if _is_quarter((end - prev_end).days):
                out[end_iso] = (f, prev)
            prev_end, prev = end, f
    out.update({e: (f, None) for e, f in direct.items()})
    return out


def quarterly_capex(usd_facts) -> dict[str, dict]:
    """XBRL fact list -> {quarter label: row}, value in $M.

    A reported quarter cites its one filing. A computed quarter (year-to-date
    minus the prior year-to-date, so Q4 = full year - 9 months) cites both.
    Raises if the trace ever disagrees with xbrl_periods, the shared
    definition."""
    from xbrl_periods import quarterly_from_facts
    expected = quarterly_from_facts(usd_facts)
    traced = _trace(usd_facts)
    if set(traced) != set(expected):
        raise ValueError("trace and xbrl_periods found different quarters: "
                         f"{sorted(set(traced) ^ set(expected))}")
    out = {}
    for end_iso, (f, less) in traced.items():
        val = float(f["val"]) - (float(less["val"]) if less else 0.0)
        if not abs(val - expected[end_iso]) <= 0.5:
            raise ValueError(f"trace disagrees with xbrl_periods at {end_iso}")
        label = quarter_label(dt.date.fromisoformat(end_iso))
        if label < FIRST_QUARTER:
            continue
        # Two period ends in one calendar quarter would be a calendar change;
        # keep the later one, which is the newest data.
        if label in out and out[label]["end"] > end_iso:
            continue
        less = less or {}
        out[label] = {"value": round(val / 1e6, 1),
                      "basis": "difference" if less else "reported",
                      "start": f["start"], "end": end_iso,
                      "accn": f.get("accn", ""), "form": f.get("form", ""),
                      "filed": f.get("filed", ""),
                      "less_start": less.get("start", ""),
                      "less_end": less.get("end", ""),
                      "less_accn": less.get("accn", ""),
                      "less_filed": less.get("filed", "")}
    return out


def fetch(ticker: str):
    """Quarterly capex for one company, or FAILED."""
    from common import cik_for, sec_get                  # lazy (CI minimal-env)
    try:
        cik = cik_for(ticker)
        data = sec_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                       host_data_sec=True).json()
        facts = data["facts"]["us-gaap"][TAGS[ticker]]["units"]["USD"]
        quarters = quarterly_capex(facts)
        return quarters if quarters else FAILED
    except Exception:                                    # noqa: BLE001
        return FAILED
    finally:
        time.sleep(0.1)


def _columns(ws) -> dict[str, int]:
    return {ws.cell(1, c).value: c for c in range(2, ws.max_column + 1)
            if ws.cell(1, c).value}


def _set_formulas(ws, c: int) -> bool:
    """TOTAL only when all five companies have reported, so a half-filled
    quarter never reads as a collapse in spending (rule 4: formulas, not
    values). Returns True if a formula changed."""
    from openpyxl.utils import get_column_letter
    col = get_column_letter(c)
    want = {7: f'=IF(COUNT({col}2:{col}6)<5,"",SUM({col}2:{col}6))'}
    if c >= 6:
        prior = get_column_letter(c - 4)
        want[8] = f'=IF(OR({col}7="",{prior}7=""),"",{col}7/{prior}7-1)'
    changed = False
    for r, formula in want.items():
        if ws.cell(r, c).value != formula:
            ws.cell(r, c).value = formula
            changed = True
    return changed


def _rows(ws) -> dict[str, int]:
    return {ws.cell(r, 1).value: r for r in range(2, 7)}


def apply(wb, data: dict[str, dict]) -> tuple[list[str], bool]:
    """Write fetched quarters into the workbook. Returns the value-change
    lines and whether anything at all (values, formulas, sources) changed."""
    ws = wb[SHEET]
    cols, rows = _columns(ws), _rows(ws)
    newest = max((q for qs in data.values() for q in qs), default=None)
    while newest and max(cols) < newest:
        label = next_label(max(cols))
        c = ws.max_column + 1
        ws.cell(1, c).value = label
        cols[label] = c
    dirty = False
    for c in cols.values():
        dirty |= _set_formulas(ws, c)
    changes = []
    for t, quarters in sorted(data.items()):
        for label, q in sorted(quarters.items()):
            if label not in cols:
                continue
            cell = ws.cell(rows[t], cols[label])
            if cell.value != q["value"]:
                verb = "new" if cell.value is None else f"CHANGED from {cell.value}"
                changes.append(f"  {t} {label}: {q['value']:,.1f} ({verb}; "
                               f"{q['form']} {q['accn']})")
                cell.value = q["value"]
    # Blank fields are stored as empty cells, which read back as None, so a
    # rerun with the same data compares equal and the file is not re-saved.
    rows_out = [tuple(v if v != "" else None for v in (
                    t, label, q["value"], q["basis"], q["start"], q["end"],
                    q["accn"], q["form"], q["filed"], q["less_start"],
                    q["less_end"], q["less_accn"], q["less_filed"], TAGS[t]))
                for t, quarters in data.items() for label, q in quarters.items()]
    kept = []
    if SOURCES in wb.sheetnames:            # keep citations for unread companies
        old = list(wb[SOURCES].iter_rows(min_row=2, values_only=True))
        if wb[SOURCES].cell(1, 1).value and tuple(
                c.value for c in wb[SOURCES][1]) != SOURCE_HEADER:
            old = []                          # an older layout: rebuild it all
        kept = [tuple(r) for r in old if r and r[0] not in data]
        key = lambda r: tuple(str(v) for v in r)
        if old and sorted(rows_out + kept, key=key) == sorted(
                (tuple(r) for r in old), key=key):
            return changes, dirty or bool(changes)
        del wb[SOURCES]
    src = wb.create_sheet(SOURCES)
    src.append(SOURCE_HEADER)
    for row in sorted(rows_out + kept, key=lambda r: tuple(str(v) for v in r)):
        src.append(row)
    return changes, True


def report(fetch_one=fetch, xlsx=XLSX, write=False) -> int:
    from openpyxl import load_workbook
    data, failed = {}, []
    for t in TAGS:
        got = fetch_one(t)
        if got == FAILED:
            failed.append(t)
        else:
            data[t] = got
    wb = load_workbook(xlsx)
    changes, dirty = apply(wb, data)
    print(f"=== Hyperscaler capex from SEC filings ({len(data)} of {len(TAGS)} read) ===")
    for t, quarters in sorted(data.items()):
        last = max(quarters)
        print(f"  {t}: latest {last} {quarters[last]['value']:,.1f} $M "
              f"(period ending {quarters[last]['end']})")
    newest = max((max(q) for q in data.values()), default=None)
    lagging = []
    for t, quarters in sorted(data.items()):
        behind, label = 0, max(quarters)
        while label < newest:
            label, behind = next_label(label), behind + 1
        if behind >= LAG_QUARTERS:
            lagging.append(f"{t} (latest {max(quarters)})")
    complete = [lab for lab in sorted({q for qs in data.values() for q in qs})
                if len(data) == len(TAGS) and all(lab in qs for qs in data.values())]
    for lab in complete[-2:]:
        total = sum(qs[lab]["value"] for qs in data.values())
        prior = lab.replace(lab[:4], str(int(lab[:4]) - 1), 1)
        line = f"  Combined {lab}: {total:,.1f} $M"
        if prior in complete:
            line += f", {total / sum(qs[prior]['value'] for qs in data.values()) - 1:+.0%} on {prior}"
        print(line)
    print(f"\n{len(changes)} cell(s) {'written' if write else 'would change'}:")
    print("\n".join(changes) if changes else "  none")
    if failed:
        print(f"COULD NOT READ: {', '.join(failed)}", file=sys.stderr)
    if lagging:
        print(f"NO RECENT QUARTER: {', '.join(lagging)}; check for a changed "
              f"XBRL tag", file=sys.stderr)
    if write and dirty:
        wb.save(xlsx)
    return 1 if failed or lagging else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="save the workbook")
    args = ap.parse_args(argv)
    return report(write=args.write)


if __name__ == "__main__":
    sys.exit(main())
