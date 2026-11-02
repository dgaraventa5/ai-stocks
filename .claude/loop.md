Work on the `improvements` branch only, in `/Users/dom/Hermes/projects/ai-stocks-worktrees/improvements`. If this session is anywhere else, stop and say so. Never push. Never commit to main.

0. Run `git fetch origin && git merge --no-edit origin/main` so the work sits on current code. If the merge conflicts, run `git merge --abort`, report it, and stop this round.
1. Open IMPROVEMENTS.md and take the highest-scored unchecked item in Open that is S or M effort. Skip L items; they need Dom's review.
2. If no such item exists, follow .claude/commands/audit.md to refill the backlog, then stop this round.
3. Implement that one item. If it turns out to need an Off-limits path, leave it undone, add a note under the item for Dom, and take the next one.
4. Invoke the evaluator subagent on it.
5. On PASS: commit with a clear message, staging files by explicit path, and move the item to Done with the commit hash.
   On FAIL: fix it and re-evaluate, at most 2 more times. If it still fails, revert your changes, add a note under the item explaining why, and move on.
6. If you made the same kind of mistake twice, add a one-line rule under "Loop rules" in CLAUDE.md.
7. Report in 2 lines or fewer: what changed, and what's next.
