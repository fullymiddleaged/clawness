---
name: status
description: >
  Show the current Clawness configuration: which rules are loaded,
  which agents are available, and how the hook is configured. Use to
  understand what rules Claude is seeing for this project.
---

# Clawness Status

Show the user what's currently active in their Clawness setup.

> All commands below use `clawness`. If it isn't on PATH (common for a
> plugin-only install), use the identical `python -m clawness.cli ...`
> (`python3` on macOS/Linux) instead.

Keep this FAST — it's a quick health check, not a full scan. Do **not** run a
test query (it loads the embedding model and is slow); step 1 already proves
retrieval is working at zero cost.

## Steps

1. **Report the rules you already see (no command).** You (Claude) receive the
   Clawness rule block at the top of your context this turn. Summarize it: how
   many mandatory + relevant rules, and a few rule IDs. If you see it, injection
   is working — this alone is the health check.

2. **Show the corpus + token cost.** Run (fast — does not load the model):
   ```bash
   clawness stats
   ```
   Report total rules, domains, whether semantic is available, and the
   `Tokens / turn` line.

3. **Project rules (only if present).** If `.clawness/rules/` exists in the
   project (walk up to the git root), mention it; otherwise skip silently.

**Summary** — keep it to a few lines:
- Rule injection: working (you saw the block) / not seeing rules
- Global rules: N across M domains; ~N tokens/turn (tune with `CLAW_TOP_K`, `CLAW_VERBOSE`, `CLAW_COMPACT`)
- Project rules: N, or "none — `clawness init .` to add some"

> If `clawness` isn't on PATH (plugin-only install), use `python -m clawness.cli ...`.
