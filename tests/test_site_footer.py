"""tests/test_site_footer.py — every page carries the shared footer (offline)."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"


def _pages():
    return sorted(p for p in SITE.glob("*.html"))


def test_every_page_has_a_footer_and_calls_render_footer():
    assert len(_pages()) == 6
    for page in _pages():
        html = page.read_text()
        assert 'id="footer"' in html, page.name
        scripts = re.findall(r'src="(js/[a-z]+\.js)"', html)
        own = [s for s in scripts if s != "js/common.js"]
        assert "js/common.js" in scripts and own, page.name
        assert "renderFooter(" in (SITE / own[-1]).read_text(), page.name


def test_only_the_shared_footer_writes_to_the_footer():
    for js in SITE.glob("js/*.js"):
        if js.name != "common.js":
            assert "getElementById('footer')" not in js.read_text(), js.name


def test_footer_states_the_disclaimer_and_data_date():
    common = (SITE / "js" / "common.js").read_text()
    assert "not investment advice" in common and "data as of" in common
    assert "scores as of" in common and "meta.scores_as_of" in common


def test_dashboard_survives_a_missing_scores_date():
    assert "meta.scores_as_of ?? 'n/a'" in (SITE / "js" / "dashboard.js").read_text()
