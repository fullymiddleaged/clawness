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

## Steps

1. **Check global rules + token cost** — Run:
   ```bash
   clawness stats
   ```
   Report the global rule count, domains, semantic on/off, and the
   `Tokens / turn` line (the per-turn cost injected into context).

2. **Check project rules** — Look for `.clawness/rules/` in the current
   directory (walk up to git root). If found, run:
   ```bash
   clawness --rules-dir .clawness/rules stats
   ```
   Report project-specific rules.

3. **Check agents** — List files in `~/.claude/agents/` that were
   installed by Clawness.

4. **Check hooks** — Read `~/.claude/settings.json` and report whether
   the UserPromptSubmit (rule injection) and PostToolUse (output
   compression) hooks are configured.

5. **Test query** — Run a sample retrieval to confirm everything works:
   ```bash
   clawness query "test query" --top-k 3
   ```

6. **Summary** — Report:
   - Global rules: N across M domains
   - Tokens / turn: ~N (and how to tune: `CLAW_TOP_K`, `CLAW_VERBOSE`, `CLAW_COMPACT`)
   - Project rules: N (or "none — run `clawness init .` to set up")
   - Agents: list of installed agents
   - Hooks: active / inactive
   - Retrieval: working / not working
