"""Load every site page at phone and desktop width; fail on console errors,
failed requests or sideways page scroll. Needs Playwright (project .venv).
Usage: <venv python> .claude/site_smoke.py [--shots DIR]
"""
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PORT = 8799
PAGES = ['index', 'positions', 'performance', 'watchlist', 'changes', 'scans']
WIDTHS = [375, 1280]

shots = Path(sys.argv[sys.argv.index('--shots') + 1]) if '--shots' in sys.argv else None
server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', str(PORT), '--directory', str(ROOT / 'site')],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
problems = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in WIDTHS:
            page = browser.new_page(viewport={'width': width, 'height': 800})
            current = {}
            page.on('console', lambda m: m.type == 'error' and problems.append(
                f"{current['name']}@{width}: console: {m.text}"))
            page.on('pageerror', lambda e: problems.append(
                f"{current['name']}@{width}: exception: {e}"))
            page.on('response', lambda r: r.status >= 400 and problems.append(
                f"{current['name']}@{width}: {r.status} {r.url}"))
            for name in PAGES:
                current['name'] = name
                page.goto(f'http://localhost:{PORT}/{name}.html', wait_until='networkidle')
                overflow = page.evaluate(
                    'document.documentElement.scrollWidth - document.documentElement.clientWidth')
                if overflow > 0:
                    problems.append(f'{name}@{width}: page scrolls sideways by {overflow}px')
                if shots:
                    shots.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=shots / f'{name}-{width}.png', full_page=True)
            page.close()
        browser.close()
finally:
    server.terminate()

for line in problems:
    print(line)
print(f'{len(PAGES)} pages at {WIDTHS}: {len(problems)} problem(s)')
sys.exit(1 if problems else 0)
