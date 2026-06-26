"""Resolve due open forecasts (CLAUDE.md rule 17). Weekly via /weekly-scan.

  python3 scripts/resolve_forecasts.py --dry-run    # show what would resolve
  python3 scripts/resolve_forecasts.py              # resolve + append snapshots

yfinance is imported lazily inside the price loader so this module (and the core
forecast_* modules) import cleanly under the deploy-site CI env (openpyxl+pytest).
"""
from __future__ import annotations

import sys
import time
import argparse
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import forecast_store as store
from forecast_resolvers import RESOLVERS


def yfinance_price_loader(ticker: str, start_date: dt.date) -> dict:
    """{date: adj_close} from start_date forward. Lazy yfinance import + throttle."""
    import yfinance as yf
    hist = yf.Ticker(ticker).history(start=start_date.isoformat(), auto_adjust=True)
    time.sleep(0.3)   # serialize, per CLAUDE.md
    if hist is None or hist.empty:
        return {}
    return {idx.date(): float(row["Close"])
            for idx, row in hist.iterrows() if row["Close"] == row["Close"]}  # drop NaN


def resolve_due(today: dt.date, price_loader, dry_run: bool,
                path: Path = store.FORECASTS_PATH) -> list[dict]:
    due = [f for f in store.open_forecasts(path)
           if dt.date.fromisoformat(f["resolution_date"]) <= today]
    results = []
    for f in due:
        resolver = RESOLVERS.get(f["template"])
        if resolver is None:
            store.flag(f'{f["id"]}: no resolver for template {f["template"]}')
            continue
        res = resolver(f, price_loader=price_loader, today=today)
        if res.status == "open":
            continue   # not gradable yet (insufficient bars within grace)
        snap = dict(f, status=res.status, outcome=res.outcome,
                    resolved_date=res.resolved_date,
                    resolution_evidence=res.evidence,
                    resolver_confidence=res.resolver_confidence)
        results.append(snap)
        print(f'{f["id"]}: {res.status}'
              + (f' outcome={res.outcome}' if res.outcome is not None else '')
              + (f' — {res.evidence}' if res.evidence else ''))
        if not dry_run:
            store.append_resolution(snap, path=path)
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    today = dt.date.today()
    results = resolve_due(today, yfinance_price_loader, args.dry_run)
    resolved = sum(1 for r in results if r["status"] == "resolved")
    review = sum(1 for r in results if r["status"] == "needs_review")
    print(f'\n{resolved} resolved, {review} need review'
          + (' (dry run — nothing written)' if args.dry_run else ''))


if __name__ == "__main__":
    main()
