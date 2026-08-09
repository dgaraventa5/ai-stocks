"""Ticket generation wiring (§B1 hook + §B3 file format).

The generator reads ACTUAL holdings from the latest recon snapshot (B2),
prices via an injectable fetcher (offline tests), and writes append-only
ticket files under tracking/live/tickets/. The refresh_targets hook fires it
on every real model event; a hook failure must never break the refresh.
"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip('yfinance')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import generate_trade_ticket as gt
import trade_ticket as tt

EVENT = {'date': '2026-08-13', 'kind': 'membership', 'reason': 'TSM enters'}
PRICES = {'NVDA': 180.0, 'TSM': 250.0}


@pytest.fixture
def live_dir(tmp_path):
    d = tmp_path / 'live'
    (d / 'recon').mkdir(parents=True)
    (d / 'recon' / 'snapshot-2026-08-12.json').write_text(json.dumps({
        'as_of': '2026-08-12', 'cash': 200.0, 'equity': 500.0,
        'positions': {'NVDA': {'shares': 1.6667, 'price': 180.0}},
        'orders': []}))
    return d


def test_generate_writes_ticket_from_snapshot_actuals(live_dir):
    p = gt.generate({'NVDA': 0.5, 'TSM': 0.4}, EVENT, live_dir=live_dir,
                    prices_fn=PRICES.get, now='2026-08-13T21:30:00Z')
    tk = json.loads(p.read_text())
    assert p.name == 'ticket-2026-08-13-membership.json'
    assert tk['ticket_id'] == '2026-08-13-membership'
    assert tk['account_state_as_of'] == '2026-08-12'
    # cash 200 + 1.6667 sh × 180 = 500.006 → rounded 2dp
    assert tk['account_equity_at_gen'] == 500.01
    assert tk['checksum'] == tt.ticket_checksum(tk['orders'])
    by = {o['ticker']: o for o in tk['orders']}
    # NVDA: target 250 vs held 300.006 → sell ~50; TSM: buy 200
    assert by['NVDA']['side'] == 'sell'
    assert by['TSM']['side'] == 'buy'
    assert abs(by['TSM']['notional_est'] - 200.0) < 1.0


def test_generate_refuses_without_snapshot(tmp_path, capsys):
    empty = tmp_path / 'live'
    (empty / 'recon').mkdir(parents=True)
    p = gt.generate({'NVDA': 0.5}, EVENT, live_dir=empty, prices_fn=PRICES.get)
    assert p is None
    assert 'snapshot' in capsys.readouterr().err   # flagged, not fabricated


def test_regenerated_ticket_is_a_new_file(live_dir):
    p1 = gt.generate({'NVDA': 0.5}, EVENT, live_dir=live_dir,
                     prices_fn=PRICES.get, now='2026-08-13T21:30:00Z')
    p2 = gt.generate({'NVDA': 0.6}, EVENT, live_dir=live_dir,
                     prices_fn=PRICES.get, now='2026-08-13T22:00:00Z')
    assert p1 != p2 and p1.exists() and p2.exists()   # append-only (B3)


# ---- §B1 hook inside refresh_targets ----

def _fired_refresh(monkeypatch, tmp_path, hook_calls, hook=None):
    """Run a firing refresh on a temp workbook with the real-run hooks
    (score panel, ticket) redirected at test doubles."""
    from test_refresh_targets import _build_portfolio, _mock_env
    import refresh_targets as rt
    path = tmp_path / 'portfolio.xlsx'
    _build_portfolio(path, [('NVDA', '06 Silicon', 86.0, '✓✓✓')])
    live = [{'ticker': 'NVDA', 'layer': '06 Silicon', 'TOTAL': 86.0,
             'Tier': '✓✓✓'}]
    cfg = {'inception': '2026-05-26', 'events': [{
        'date': '2026-06-18', 'reason': 'seed',
        'allocations': {'NVDA': 500.0, 'TSM': 500.0}, 'cash': 0.0,
        'tiers': {'NVDA': '✓✓✓', 'TSM': '✓✓'}}]}   # TSM exits → fires
    _mock_env(monkeypatch, live, cfg)
    monkeypatch.setattr(rt, 'PORTFOLIO', str(path))
    import score_history
    monkeypatch.setattr(score_history, 'append_snapshot', lambda live_: None)
    monkeypatch.setattr(gt, 'on_model_event',
                        hook or (lambda ev, w: hook_calls.append((ev, dict(w)))))
    return rt.refresh(portfolio=None)     # portfolio=None → real-run hook path


def test_hook_fires_on_real_model_event(monkeypatch, tmp_path):
    calls = []
    rep = _fired_refresh(monkeypatch, tmp_path, calls)
    assert rep['fire'] is True
    assert len(calls) == 1
    ev, weights = calls[0]
    assert ev['kind'] == 'membership'
    assert 'NVDA' in weights


def test_hook_failure_never_breaks_refresh(monkeypatch, tmp_path, capsys):
    def boom(ev, w):
        raise RuntimeError('no snapshot yet')
    rep = _fired_refresh(monkeypatch, tmp_path, [], hook=boom)
    assert rep['fire'] is True                     # refresh completed anyway
    # common.flag prints [FLAG] lines to stdout
    assert 'trade ticket not generated' in capsys.readouterr().out
