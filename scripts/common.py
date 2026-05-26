"""Shared utilities for AI-Supply-Chain data fetchers.

Centralizes the SEC EDGAR User-Agent and rate-limit discipline so no
individual script can forget it. Per CLAUDE.md §Data sources:
  - User-Agent: "Dom Researcher dgaraventa5@gmail.com"
  - Rate limit: 10 req/sec, throttle with time.sleep(0.1)
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

import requests

ROOT = Path(__file__).resolve().parent.parent

# SEC requires a contact in the User-Agent. Email pulled from session context.
SEC_USER_AGENT = "Dom Researcher dgaraventa5@gmail.com"

SEC_HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov",
}

DATA_SEC_HEADERS = {**SEC_HEADERS, "Host": "data.sec.gov"}

# Local cache so we don't re-fetch the ticker→CIK map every run.
_TICKER_CACHE = ROOT / ".cache" / "company_tickers.json"


class RateLimiter:
    """Simple serial throttle: enforce a minimum gap between calls.

    Default 0.11s gap → ~9 req/sec, safely under SEC's 10/sec cap.
    """

    def __init__(self, min_interval: float = 0.11):
        self.min_interval = min_interval
        self._last = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last = time.monotonic()


sec_limiter = RateLimiter()


def sec_get(url: str, *, host_data_sec: bool = False, **kwargs) -> requests.Response:
    """GET against sec.gov / data.sec.gov with the right UA + throttle."""
    sec_limiter.wait()
    headers = DATA_SEC_HEADERS if host_data_sec else SEC_HEADERS
    headers = {**headers, **kwargs.pop("headers", {})}
    resp = requests.get(url, headers=headers, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp


def load_ticker_to_cik(force_refresh: bool = False) -> dict[str, str]:
    """Load and cache the SEC ticker→CIK map.

    Returns: {"NVDA": "0001045810", ...} — CIK is zero-padded to 10 digits,
    which is the form most EDGAR endpoints expect.
    """
    if _TICKER_CACHE.exists() and not force_refresh:
        with _TICKER_CACHE.open() as f:
            return json.load(f)

    _TICKER_CACHE.parent.mkdir(parents=True, exist_ok=True)
    resp = sec_get("https://www.sec.gov/files/company_tickers.json")
    raw = resp.json()
    # raw shape: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
    mapping = {
        v["ticker"].upper(): str(v["cik_str"]).zfill(10)
        for v in raw.values()
    }
    with _TICKER_CACHE.open("w") as f:
        json.dump(mapping, f)
    return mapping


def cik_for(ticker: str) -> Optional[str]:
    return load_ticker_to_cik().get(ticker.upper())


def per_stock_dir(ticker: str, *, create: bool = False) -> Path:
    d = ROOT / "per-stock" / ticker.upper()
    if create:
        (d / "filings").mkdir(parents=True, exist_ok=True)
        (d / "transcripts").mkdir(parents=True, exist_ok=True)
    return d


def flag(msg: str) -> None:
    """Standard way to surface a data gap per CLAUDE.md §3 (Flag, don't assume)."""
    print(f"[FLAG] {msg}")
