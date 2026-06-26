---
name: audit
description: >
  Run a red team / blue team security audit on the current project or
  a specific module. Spawns adversarial sub-agents that probe for
  vulnerabilities and propose fixes. Use when reviewing security before
  deployment, after adding auth/payment code, or on a schedule.
---

# Security Audit Workflow

Run a full adversarial security audit using the Clawness agent pair.

> **Before spawning agents:** this launches several adversarial sub-agents and is
> token-intensive. If you surfaced this proactively (the user mentioned security
> but didn't explicitly ask to run it), first ask: "Want me to run the full red
> team / blue team audit now?" Only proceed once they confirm. If the user
> explicitly invoked `/clawness:audit` or already said yes, skip the
> question and proceed.

## Steps

1. **Scope** — Identify what to audit. If the user specified a module or
   directory, focus there. Otherwise, audit the most security-sensitive
   areas: authentication, authorization, data validation, API endpoints,
   database queries, and secret handling.

2. **Red Team** — Delegate to the `security-red-team` sub-agent:
   "Audit the following files for security vulnerabilities. Check for
   current-month CVEs affecting our stack. Run the full OWASP Top 10
   checklist. Report findings with file:line references."

3. **Blue Team** — Take the red team's findings and delegate to the
   `security-blue-team` sub-agent:
   "Triage these findings. For each confirmed vulnerability, propose
   the exact code fix. Add hardening measures. Search for current
   mitigations for any CVEs mentioned."

4. **Synthesize** — Merge both reports into a single action plan:
   - Critical findings (fix before deploy)
   - Important findings (fix this sprint)
   - Improvements (add to backlog)
   - Overall security posture assessment

If $ARGUMENTS is provided, scope the audit to that path or module.
