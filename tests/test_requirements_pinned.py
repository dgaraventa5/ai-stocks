"""CI installs requirements.txt fresh, so an unpinned line drifts away from what
was tested. That gap crashed every daily refresh until 2026-10-15 (df9f347a)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINES = (ROOT / "requirements.txt").read_text().splitlines()
TEST_LINES = (ROOT / "requirements-test.txt").read_text().splitlines()


def test_every_requirement_is_pinned_exactly():
    assert LINES and TEST_LINES
    for line in LINES + TEST_LINES:
        name, sep, version = line.partition("==")
        assert sep and name.strip() and version.strip(), line
        assert "*" not in version and "," not in version, line


def test_direct_dependencies_are_present():
    names = {line.split("==")[0].lower() for line in LINES}
    assert {"yfinance", "pandas", "openpyxl", "requests",
            "beautifulsoup4", "lxml"} <= names


def test_test_tools_match_the_main_pins():
    assert "openpyxl==3.1.5" in set(TEST_LINES) & set(LINES)
    assert {line.split("==")[0] for line in TEST_LINES} == {"openpyxl", "pytest"}


def test_workflows_install_only_pinned_files():
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        for line in workflow.read_text().splitlines():
            if "pip install" in line:
                words = line.split("pip install", 1)[1].split()
                assert all(w == "-r" or w.endswith(".txt") or "==" in w
                           for w in words), f"{workflow.name}: {line.strip()}"
