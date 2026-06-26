---
name: status
description: >
  Show the current Clawness configuration: which rules are loaded,
  which agents are available, and how the hook is configured. Use to
  understand what rules Claude is seeing for this project.
---

# Clawness Status

Show the user what's currently active in their Clawness setup.

## Steps

1. **Check global rules** — Run:
   ```bash
   python3 -m writ_lite.cli --rules-dir ~/.claude/clawness/rules stats
   ```
   Report the global rule count and domains.

2. **Check project rules** — Look for `.writ/rules/` in the current
   directory (walk up to git root). If found, run:
   ```bash
   python3 -m writ_lite.cli --rules-dir .writ/rules stats
   ```
   Report project-specific rules.

3. **Check agents** — List files in `~/.claude/agents/` that were
   installed by Clawness.

4. **Check hooks** — Read `~/.claude/settings.json` and report whether
   the UserPromptSubmit (rule injection) and PostToolUse (output
   compression) hooks are configured.

5. **Test query** — Run a sample retrieval against the combined rule set
   to confirm everything works:
   ```bash
   python3 -m writ_lite.cli --rules-dir ~/.claude/clawness/rules query "test query" --top-k 3
   ```

6. **Summary** — Report:
   - Global rules: N across M domains
   - Project rules: N (or "none — run /writ-init to set up")
   - Agents: list of installed agents
   - Hooks: active / inactive
   - Retrieval: working / not working
