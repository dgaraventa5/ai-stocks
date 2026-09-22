#!/usr/bin/env python3
"""Hermes no-agent wrapper: stale-run and automation-PR health report."""
from pathlib import Path
import subprocess
import sys

PROJECT = Path("/Users/dom/Hermes/projects/ai-stocks")
COMMAND = [
    str(PROJECT / ".venv/bin/python"),
    str(PROJECT / "scripts/scheduled_ops.py"),
    "health",
    "--limit", "10",
]
result = subprocess.run(COMMAND, cwd=PROJECT, capture_output=True, text=True,
                        timeout=60)
if result.stdout:
    sys.stdout.write(result.stdout)
if result.returncode:
    if result.stderr:
        sys.stderr.write(result.stderr)
    raise SystemExit(result.returncode)
