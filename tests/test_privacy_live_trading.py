"""§E privacy gates for the live-trading pipeline — same standing as the
site privacy gate (test_privacy_no_real_dollars_anywhere). NEVER weaken.

Boundary: everything with real dollars / share counts / account numbers /
order ids lives under tracking/live/ (gitignored). Committed artifacts carry
only booleans, dates, counts, tickers, and relative percentages.
"""
import json
import subprocess
from pathlib import Path

import pytest

import reconcile_account as ra

REPO = Path(__file__).resolve().parent.parent


# ---- the boundary itself ----

def test_tracking_live_is_gitignored():
    r = subprocess.run(
        ['git', 'check-ignore', '-q', 'tracking/live/tickets/probe.json'],
        cwd=REPO)
    assert r.returncode == 0, 'tracking/live/ must be gitignored (§E)'


def test_nothing_committed_under_tracking_live():
    r = subprocess.run(['git', 'ls-files', 'tracking/live'],
                      cwd=REPO, capture_output=True, text=True)
    assert r.stdout.strip() == '', \
        f'files committed inside the privacy boundary: {r.stdout}'


# ---- sanitizer validators (called by reconcile before every committed write) ----

def test_status_sanitizer_accepts_clean_shape():
    ra.assert_sanitized_status({
        'as_of': '2026-08-13', 'halted': False, 'positions': 3,
        'open_orders': 0, 'drift_flags': ['NVDA'], 'regen_needed': [],
        'anomaly_count': 0})


@pytest.mark.parametrize('poison', [
    {'equity': 512.44},           # dollars
    {'cash': 137.53},
    {'shares': 2.0017},           # share counts
    # FICTIONAL value — never put a real account number in a fixture (§E)
    {'account_number': '123450000'},
    {'order_id': 'rh-abc-1'},
    {'nvda_value': 375.0},        # any unknown field fails closed
])
def test_status_sanitizer_rejects_leaky_fields(poison):
    clean = {'as_of': '2026-08-13', 'halted': False, 'positions': 3,
             'open_orders': 0, 'drift_flags': [], 'regen_needed': [],
             'anomaly_count': 0}
    with pytest.raises(ValueError):
        ra.assert_sanitized_status(clean | poison)


def test_lvm_sanitizer_accepts_relative_percentages_only():
    ra.assert_sanitized_lvm({
        'baseline_date': '2026-08-13',
        'series': [{'date': '2026-08-14', 'live_pct': 2.0,
                    'model_pct': 1.0, 'shortfall_pct': 1.0}]})


@pytest.mark.parametrize('entry', [
    {'date': '2026-08-14', 'live_pct': 2.0, 'model_pct': 1.0,
     'shortfall_pct': 1.0, 'equity': 512.44},
    {'date': '2026-08-14', 'live_pct': 2.0, 'model_pct': 1.0,
     'shortfall_pct': 1.0, 'baseline_equity': 500.0},
])
def test_lvm_sanitizer_rejects_absolute_values(entry):
    with pytest.raises(ValueError):
        ra.assert_sanitized_lvm({'baseline_date': '2026-08-13',
                                 'series': [entry]})


# ---- integration: recon output passes its own gates ----

def test_recon_committed_outputs_pass_sanitizers(tmp_path):
    live = tmp_path / 'live'
    (live / 'recon').mkdir(parents=True)
    series = tmp_path / 'performance-series.json'
    series.write_text(json.dumps({'dates': ['2026-08-13'], 'model': [10000.0]}))
    status, lvm = tmp_path / 'live-status.json', tmp_path / 'live-vs-model.json'
    ra.run({'as_of': '2026-08-13', 'cash': 137.53, 'equity': 512.44,
            'positions': {'NVDA': {'shares': 2.0017, 'price': 187.31}},
            'orders': []},
           live_dir=live, target_weights={'NVDA': 0.75},
           model_series_path=series, status_path=status, lvm_path=lvm)
    ra.assert_sanitized_status(json.loads(status.read_text()))
    ra.assert_sanitized_lvm(json.loads(lvm.read_text()))


# ---- local tripwire: real identifiers must appear NOWHERE in tracked text ----
# tracking/live/private-strings.json (gitignored) holds the REAL account
# numbers/identifiers. This test greps every git-tracked text file for them.
# CI never has the file (skip); Dom's machine always does — so any future
# commit containing a real identifier fails locally before it can be pushed.
# Born of an actual incident (2026-08-09): the real account number was used
# as a fixture value in THIS file and briefly committed to the public repo.

def test_no_real_identifiers_in_any_tracked_file():
    private = REPO / 'tracking' / 'live' / 'private-strings.json'
    if not private.exists():
        pytest.skip('no private-strings.json (CI or fresh clone)')
    secrets = json.loads(private.read_text())['strings']
    assert secrets, 'private-strings.json exists but is empty — seed it'
    tracked = subprocess.run(
        ['git', 'ls-files', '*.py', '*.md', '*.json', '*.yml', '*.yaml',
         '*.html', '*.js', '*.txt', '*.csv', '*.plist'],
        cwd=REPO, capture_output=True, text=True).stdout.splitlines()
    hits = []
    for rel in tracked:
        try:
            text = (REPO / rel).read_text(errors='ignore')
        except OSError:
            continue
        hits += [f'{s[:4]}… in {rel}' for s in secrets if s in text]
    assert not hits, f'REAL identifier(s) in tracked files: {hits}'


# ---- the real committed files, whenever they exist, must stay clean ----

def test_real_committed_live_files_pass_sanitizers():
    status = REPO / 'tracking' / 'live-status.json'
    lvm = REPO / 'tracking' / 'live-vs-model.json'
    if status.exists():
        ra.assert_sanitized_status(json.loads(status.read_text()))
    if lvm.exists():
        ra.assert_sanitized_lvm(json.loads(lvm.read_text()))
