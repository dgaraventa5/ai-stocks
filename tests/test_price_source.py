"""Robinhood-first quote source with yfinance fallback.

US names: authenticated Robinhood MCP quotes (deterministic transport, no
scraping, residential-IP-independent). Foreign local lines + anything
Robinhood lacks: yfinance. Both dead → None + flag, never a guess (rule 3).
"""
import pytest

import price_source as ps


class FakeTransport:
    def __init__(self, quotes=None, fail=False):
        self._quotes = quotes or {}
        self._fail = fail
        self.calls = []

    def quotes(self, tickers):
        self.calls.append(list(tickers))
        if self._fail:
            raise RuntimeError('token expired')
        return {t: self._quotes[t] for t in tickers if t in self._quotes}


def test_us_name_uses_robinhood_not_yfinance(monkeypatch):
    monkeypatch.setattr(ps, '_yf_close', lambda t: pytest.fail('yf called'))
    t = FakeTransport({'NVDA': 224.1})
    assert ps.ref_prices(['NVDA'], transport=t) == {'NVDA': 224.1}


def test_foreign_local_line_goes_straight_to_yfinance(monkeypatch):
    monkeypatch.setattr(ps, '_yf_close', lambda t: 6480.0)
    t = FakeTransport({'NVDA': 224.1})
    out = ps.ref_prices(['6861.T'], transport=t)
    assert out == {'6861.T': 6480.0}
    assert t.calls == []                      # RH never asked about foreign


def test_transport_failure_falls_back_to_yfinance(monkeypatch):
    monkeypatch.setattr(ps, '_yf_close', lambda t: 223.5)
    t = FakeTransport(fail=True)
    assert ps.ref_prices(['NVDA'], transport=t) == {'NVDA': 223.5}


def test_rh_missing_symbol_falls_back_per_name(monkeypatch):
    monkeypatch.setattr(ps, '_yf_close',
                        lambda t: 82.5 if t == 'GMED' else pytest.fail(t))
    t = FakeTransport({'NVDA': 224.1})       # GMED absent from RH answer
    out = ps.ref_prices(['NVDA', 'GMED'], transport=t)
    assert out == {'NVDA': 224.1, 'GMED': 82.5}


def test_both_sources_dead_flags_and_omits(monkeypatch, capsys):
    monkeypatch.setattr(ps, '_yf_close', lambda t: None)
    t = FakeTransport(fail=True)
    out = ps.ref_prices(['NVDA'], transport=t)
    assert out == {}
    assert 'NVDA' in capsys.readouterr().err  # flagged, not guessed


def test_batch_is_one_rh_call(monkeypatch):
    monkeypatch.setattr(ps, '_yf_close', lambda t: pytest.fail('yf called'))
    t = FakeTransport({'NVDA': 224.1, 'TSM': 419.9})
    ps.ref_prices(['NVDA', 'TSM'], transport=t)
    assert len(t.calls) == 1                  # batched, not per-name
