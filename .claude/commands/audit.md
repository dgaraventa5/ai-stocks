---
description: Audit the project and refill the IMPROVEMENTS.md backlog
---

Audit this project and update IMPROVEMENTS.md. Read Goals and Off-limits in CLAUDE.md first, plus `.claude/off-limits.txt`.

Run from `/Users/dom/Hermes/projects/ai-stocks-worktrees/improvements`, on the `improvements` branch. The audit changes nothing except IMPROVEMENTS.md. Subagents must not modify files, run scripts that write project data, read `tracking/live/`, or call a Robinhood tool.

Launch these subagents in parallel. Each returns at most 5 findings. Every finding must include evidence (command output, file:line, metric, or screenshot) and a proposed fix:

1. **Bugs & breakage:** `python3 -m pytest tests -q`, `python3 -m compileall -q scripts`, `python3 scripts/export_site_data.py && python3 scripts/check_site.py`; unhandled errors, bare excepts that hide failures, code that reports success after a failed lookup, TODO/FIXME comments. The repo has no lint or type-check.
2. **User experience:** run `/Users/dom/Hermes/projects/ai-stocks/.venv/bin/python .claude/site_smoke.py --shots <scratch dir>`, then walk the site's core flows with Playwright at 375px and 1280px: positions, performance chart, watchlist filtering and sorting, scans. Look for console errors, broken layouts, unclear or stale figures, accessibility gaps.
3. **Performance:** slowest tests (`python3 -m pytest tests -q --durations=10`), size of `site/data/*.json`, page load time, repeated network calls or missing throttling in data scripts.
4. **Code health:** churn hotspots from `git log --since="6 months ago" --name-only --pretty=format: -- '*.py' '*.js' '*.yml' | grep -v '^$' | sort | uniq -c | sort -rn | head -15`, duplicated logic, files over 400 lines, untested scripts, outdated or vulnerable packages in `requirements.txt`, one-off migration scripts that can be retired.
5. **Goal alignment:** what is missing or weak against Goals? Look for places where the pipeline can fail silently, where "could not look" reads as "nothing happened", where the freshness of an input or briefing is not visible, and where a thesis break could go unnoticed.

Then triage. Drop findings with no evidence. Drop anything already in Open, Done, or Rejected. Findings with evidence that touch Off-limits, match `.claude/off-limits.txt`, need a file deleted, or need something only Dom can do go in Needs Dom instead of Open, each as one line ending in the decision or action needed. Skip anything already in Needs Dom. Score the rest as impact (1–3) × confidence (1–3) ÷ effort (S=1, M=2, L=3). Add at most 10 new items to Open, sorted by score, each with a checkable "Done when" condition. Report what you added in 5 lines or fewer.
