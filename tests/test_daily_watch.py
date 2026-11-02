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
