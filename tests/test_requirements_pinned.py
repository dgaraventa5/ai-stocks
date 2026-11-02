"""CI installs requirements.txt fresh, so an unpinned line drifts away from what
was tested. That gap crashed every daily refresh until 2026-10-15 (df9f347a)."""
from pathlib import Path

LINES = (Path(__file__).resolve().parent.parent / "requirements.txt").read_text().splitlines()


def test_every_requirement_is_pinned_exactly():
    assert LINES
    for line in LINES:
        name, sep, version = line.partition("==")
        assert sep and name.strip() and version.strip(), line
        assert "*" not in version and "," not in version, line


def test_direct_dependencies_are_present():
    names = {line.split("==")[0].lower() for line in LINES}
    assert {"yfinance", "pandas", "openpyxl", "requests",
            "beautifulsoup4", "lxml"} <= names
