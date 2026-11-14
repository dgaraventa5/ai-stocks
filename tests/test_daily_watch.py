"""The daily watch is a prompt, so these guard its wording (rule 37). Offline."""
import re
from pathlib import Path

DOC = (Path(__file__).resolve().parent.parent
       / ".claude" / "commands" / "daily-watch.md").read_text()
DETECT = DOC.split("## 2. Detect")[1].split("## 3.")[0]


def test_quiet_day_needs_clean_lookups():
    quiet = re.search(r"\*\*Quiet day\*\* = (.+?)\. Branch", DOC, re.S).group(1)
    quiet = " ".join(quiet.split())
    assert "`flagged` empty" in quiet
    assert "the sentinel and `scan-filings` both exit 0" in quiet


def test_detect_commands_keep_their_own_exit_codes():
    fences = re.findall(r"```bash\n(.*?)```", DETECT, re.S)
    assert [len(f.strip().splitlines()) for f in fences] == [1, 1, 1]


def test_blocked_sentinel_is_unchecked_and_skips_the_rescore():
    text = " ".join(DETECT.split())
    assert "`blocked: true`" in text
    assert "UNCHECKED, never as quiet, and skip step 4" in text


def test_flags_reach_the_report():
    assert "every `flagged` name with its reason" in DOC


def test_news_watch_is_the_dated_feed_and_gates_a_quiet_day():
    # 2026-11-12: a standard-mode WebSearch with a date in the query logged
    # NVDA's CEO story as "no dated in-window news" for two weeks.
    text = " ".join(DETECT.split())
    assert "python3 scripts/news_watch.py --days 2" in text
    assert "**UNCHECKED, never quiet**" in text
    assert "Never use a `standard`-mode WebSearch with a date in the query" in text
    quiet = re.search(r"\*\*Quiet day\*\* = (.+?)\. Branch", DOC, re.S).group(1)
    assert "`news_watch.py` exits 0" in " ".join(quiet.split())
    assert "news I items / M names" in DOC
