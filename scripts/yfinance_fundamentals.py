"""Pull fundamentals from yfinance and write to per-stock/{TICKER}/financials.xlsx.

Per CLAUDE.md §3 (Flag, don't assume): missing fields are explicitly noted
in a "Data flags" sheet, not silently coerced. Per §4: history sheets are
left as plain values (already historical, no formulas to drive), but the
"Summary" tab uses formulas to derive ratios so changing the inputs
re-derives the numbers.

Usage:
  python3 scripts/yfinance_fundamentals.py NVDA
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import yfinance as yf
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from common import flag, per_stock_dir

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF")


def _is_missing(v) -> bool:
    if v is None:
        return True
    if isinstance(v, float) and math.isnan(v):
        return True
    return False


def _style_header(ws, row: int = 1) -> None:
    for cell in ws[row]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT


def _write_df(ws, df) -> None:
    """Write a pandas DataFrame to a sheet with the index as the first column."""
    if df is None or df.empty:
        ws.append(["(no data)"])
        return
    # Columns = period end dates (most recent first)
    ws.append(["Line item"] + [str(c.date()) if hasattr(c, "date") else str(c)
                               for c in df.columns])
    _style_header(ws)
    for idx, row in df.iterrows():
        out = [str(idx)] + [None if _is_missing(v) else float(v) for v in row.tolist()]
        ws.append(out)
    # Number format for numeric cells (USD, millions implicit since yfinance returns raw)
    for r in range(2, ws.max_row + 1):
        for c in range(2, ws.max_column + 1):
            ws.cell(row=r, column=c).number_format = "#,##0"
    for c in range(1, ws.max_column + 1):
        ws.column_dimensions[get_column_letter(c)].width = 22 if c == 1 else 16


def build_financials(ticker: str, out_path: Path | None = None) -> Path:
    t = yf.Ticker(ticker)
    info = t.info or {}

    wb = Workbook()

    # ---------- Summary tab (formula-driven ratios) ----------
    s = wb.active
    s.title = "Summary"
    s.append(["Field", "Value", "Source / formula"])
    _style_header(s)

    flags: list[str] = []

    def put(label, value, source):
        if _is_missing(value):
            flags.append(f"{label}: missing from yfinance")
            s.append([label, "(missing — see Data flags)", source])
        else:
            s.append([label, value, source])

    put("Ticker", ticker.upper(), "input")
    put("Name", info.get("longName"), "yfinance info.longName")
    put("Sector", info.get("sector"), "yfinance info.sector")
    put("Industry", info.get("industry"), "yfinance info.industry")
    put("Market cap ($)", info.get("marketCap"), "yfinance info.marketCap")
    put("Enterprise value ($)", info.get("enterpriseValue"), "yfinance info.enterpriseValue")
    put("Trailing P/E", info.get("trailingPE"), "yfinance info.trailingPE")
    put("Forward P/E", info.get("forwardPE"), "yfinance info.forwardPE")
    put("P/S (TTM)", info.get("priceToSalesTrailing12Months"), "yfinance")
    put("Gross margin (TTM)", info.get("grossMargins"), "yfinance info.grossMargins")
    put("Operating margin (TTM)", info.get("operatingMargins"), "yfinance info.operatingMargins")
    put("Net margin (TTM)", info.get("profitMargins"), "yfinance info.profitMargins")
    put("ROE", info.get("returnOnEquity"), "yfinance info.returnOnEquity")
    put("Revenue growth (YoY)", info.get("revenueGrowth"), "yfinance info.revenueGrowth")
    put("Total cash ($)", info.get("totalCash"), "yfinance info.totalCash")
    put("Total debt ($)", info.get("totalDebt"), "yfinance info.totalDebt")
    put("FCF (TTM, $)", info.get("freeCashflow"), "yfinance info.freeCashflow")
    put("Shares outstanding", info.get("sharesOutstanding"), "yfinance info.sharesOutstanding")
    put("Current price ($)", info.get("currentPrice") or info.get("regularMarketPrice"),
        "yfinance info.currentPrice")

    # Derived ratios as formulas, not pasted values (per CLAUDE.md §4).
    # Find row numbers by scanning column A.
    def row_of(label: str) -> int | None:
        for r in range(2, s.max_row + 1):
            if s.cell(row=r, column=1).value == label:
                return r
        return None

    fcf_row = row_of("FCF (TTM, $)")
    mcap_row = row_of("Market cap ($)")
    ev_row = row_of("Enterprise value ($)")
    if fcf_row and mcap_row:
        s.append(["FCF yield", f"=IFERROR(B{fcf_row}/B{mcap_row},\"\")",
                  f"=B{fcf_row}/B{mcap_row}"])
        s.cell(row=s.max_row, column=2).number_format = "0.00%"
    if fcf_row and ev_row:
        s.append(["FCF / EV", f"=IFERROR(B{fcf_row}/B{ev_row},\"\")",
                  f"=B{fcf_row}/B{ev_row}"])
        s.cell(row=s.max_row, column=2).number_format = "0.00%"

    s.column_dimensions["A"].width = 26
    s.column_dimensions["B"].width = 22
    s.column_dimensions["C"].width = 36

    # ---------- Statements ----------
    for sheet_name, df in [
        ("Income stmt (annual)", t.income_stmt),
        ("Income stmt (quarterly)", t.quarterly_income_stmt),
        ("Balance sheet (annual)", t.balance_sheet),
        ("Cash flow (annual)", t.cashflow),
        ("Cash flow (quarterly)", t.quarterly_cashflow),
    ]:
        ws = wb.create_sheet(sheet_name)
        try:
            _write_df(ws, df)
        except Exception as e:
            flags.append(f"{sheet_name}: yfinance returned error — {e}")
            ws.append([f"(error: {e})"])

    # ---------- Data flags ----------
    fl = wb.create_sheet("Data flags")
    fl.append(["Field", "Issue"])
    _style_header(fl)
    if not flags:
        fl.append(["—", "no gaps detected"])
    else:
        for f in flags:
            label, _, issue = f.partition(":")
            fl.append([label.strip(), issue.strip()])
    fl.column_dimensions["A"].width = 30
    fl.column_dimensions["B"].width = 60

    if flags:
        for f in flags:
            flag(f)

    out = out_path or (per_stock_dir(ticker, create=True) / "financials.xlsx")
    wb.save(out)
    print(f"wrote {out}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Pull fundamentals from yfinance.")
    ap.add_argument("ticker")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    build_financials(args.ticker, args.out)


if __name__ == "__main__":
    main()
