---
name: perf
description: >
  Run a performance audit on the project or a specific module. Checks
  for N+1 queries, unnecessary re-renders, memory leaks, bundle size
  issues, and slow algorithms.
---

# Performance Audit

Analyze code for performance issues using the Clawness perf-auditor agent.

> **Before spawning the agent:** if you surfaced this proactively (the user
> mentioned performance/slowness but didn't explicitly ask to run it), first ask:
> "Want me to run the performance audit now?" Proceed only once they confirm. If
> the user explicitly invoked `/clawness:perf` or already said yes, skip
> the question.

## Steps

1. **Scope** — If $ARGUMENTS specifies a path, audit that. Otherwise,
   focus on the most performance-sensitive areas: database queries,
   API routes, React components, and data processing functions.

2. **Delegate to perf-auditor** — Send the relevant code to the
   `perf-auditor` sub-agent for analysis.

3. **Report** — Present findings ranked by impact with specific
   fix suggestions and expected improvement.
