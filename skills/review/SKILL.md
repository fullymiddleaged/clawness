---
name: review
description: >
  Run an adversarial code review on staged changes or a specific file.
  Spawns the code-critic agent to find bugs, performance issues, and
  missed edge cases. Use before merging PRs or committing.
---

# Adversarial Code Review

Run a thorough code review using the Clawness code-critic agent.

> **Before spawning the agent:** if you surfaced this proactively (the user
> mentioned reviewing/merging but didn't explicitly ask to run it), first ask:
> "Want me to run the adversarial code review now?" Proceed only once they
> confirm. If the user explicitly invoked `/clawness:review` or already
> said yes, skip the question.

## Steps

1. **Identify changes** — If $ARGUMENTS specifies files, review those.
   Otherwise, check for staged git changes (`git diff --cached`).
   If nothing is staged, review the most recently changed files
   (`git diff HEAD~1`).

2. **Delegate to code-critic** — Send the relevant code to the
   `code-critic` sub-agent for adversarial review focusing on:
   - Correctness bugs and logic errors
   - Performance issues (N+1, re-renders, memory leaks)
   - Missing edge cases (null, empty, concurrent, malicious)
   - Maintainability (naming, complexity, duplication)

3. **Report** — Present findings grouped by severity. For each finding,
   include the file, line, problem, and suggested fix.

4. **Offer to fix** — Ask the user if they want to apply any of the
   suggested fixes.
