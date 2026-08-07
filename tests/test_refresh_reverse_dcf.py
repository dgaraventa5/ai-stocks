"""CLI argument parsing for refresh_reverse_dcf.py.

Regression: the script used to treat EVERY argv token as a ticker — including
--help, which fetched a "--HELP" quote from yfinance and wrote a junk entry
into 00-master/reverse-dcf.json (observed 2026-08-07). Flags must be parsed,
not uppercased into the data file.
"""
import pytest

import scripts.refresh_reverse_dcf as rrd


def test_tickers_are_uppercased():
    assert rrd.parse_args(["nvda", "Tsm"]) == ["NVDA", "TSM"]


def test_no_args_means_all_watchlist():
    assert rrd.parse_args([]) == []


def test_help_exits_cleanly_with_usage(capsys):
    with pytest.raises(SystemExit) as e:
        rrd.parse_args(["--help"])
    assert e.value.code == 0
    assert "usage" in capsys.readouterr().out.lower()


def test_unknown_flag_is_an_error_not_a_ticker():
    with pytest.raises(SystemExit) as e:
        rrd.parse_args(["--dry-run"])
    assert e.value.code == 2


def test_main_help_does_not_write_json(tmp_path, monkeypatch):
    """The original bug: --help must never reach the fetch/write path."""
    j = tmp_path / "reverse-dcf.json"
    monkeypatch.setattr(rrd, "JSON_PATH", j)
    monkeypatch.setattr(rrd, "_watchlist_tickers", lambda: ["FAKE1"])
    monkeypatch.setattr(rrd, "_ev_over_fcf", lambda t: None)
    with pytest.raises(SystemExit):
        rrd.main(["--help"])
    assert not j.exists()
