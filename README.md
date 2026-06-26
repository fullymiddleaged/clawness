# Clawness

**Install once. Works everywhere. Your AI coding agent gets the right rules for every task — automatically.**

Clawness is a lightweight rule retrieval system for Claude Code. It ships 106 coding rules across 17 domains, 7 adversarial sub-agents, output compression, and a default-on plan-approval gate — all in under 1 MB with zero infrastructure. You install it once, and it silently injects the relevant rules into every Claude Code session across every project on your machine.

Inspired by [infinri/Writ](https://github.com/infinri/Writ), rebuilt from ~2GB of infrastructure to pure Python.

---

## 30-Second Version

```bash
# Plugin install (recommended)
claude plugin marketplace add fullymiddleaged/clawness
claude plugin install clawness@clawness
```

Done. Open Claude Code in any project and start working. Type `/clawness:status` to verify.

---

## What Problem Does This Solve?

You have coding rules: *"always use parameterized SQL," "async I/O end-to-end," "all API responses use the envelope format."*

Without Clawness, you either:
- **Dump all rules into CLAUDE.md** → wastes tokens, dilutes attention on every turn
- **Remember to mention rules manually** → you forget, Claude forgets

With Clawness:
- **106 rules live in YAML files**, organized by domain
- **A hook fires on every prompt**, retrieves only the rules relevant to your current task (under a millisecond on the lexical path)
- **Mandatory rules** (security, testing) appear on every turn, non-negotiably
- **Ranked rules** (Next.js patterns, React hooks, FastAPI conventions) appear only when relevant
- **Output compression** strips noise from long bash output so Claude's context stays clean
- **Adversarial sub-agents** (security red/blue team, code critic, architecture challenger) are available for deeper review

---

## How It Works

```
You type a prompt in Claude Code
        │
        ▼
┌──────────────────────────┐
│  Hook: UserPromptSubmit  │  fires automatically before Claude sees your prompt
│  hooks/claude_hook.py    │
└──────────┬───────────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌─────────┐  ┌──────────┐
│ GLOBAL  │  │ PROJECT  │    global rules from ~/.claude/clawness/rules/
│ rules   │  │ rules    │    project rules from <project>/.writ/rules/
└────┬────┘  └────┬─────┘
     └──────┬─────┘
            ▼
┌──────────────────────────┐
│  BM25 + TF-IDF + RRF    │  hybrid retrieval (+ concept expansion, optional
│  + concepts / vectors   │  model2vec embeddings) picks top rules in <1ms
│  context budget: 4000    │  stops adding rules when token budget is full
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Claude Code             │  sees: mandatory rules (always)
│  (your agent)            │      + relevant ranked rules (per-prompt)
│                          │      + your original prompt
└──────────────────────────┘
```

**Two layers of rules:**
- **Global** (`~/.claude/clawness/rules/`) — installed once, applies to every project
- **Project** (`<your-project>/.writ/rules/`) — optional, layers on top for project-specific conventions. Commit to git so your whole team shares them.

---

## Install

### Option 1: Plugin Install (Recommended)

From any Claude Code session:

```bash
claude plugin marketplace add fullymiddleaged/clawness
claude plugin install clawness@clawness
```

That's it. Skills, agents, hooks, and rules are all registered automatically. Run `/reload-plugins` if you're already in a session.

### Option 2: Manual Install

For more control, or if the plugin system isn't available in your environment.

**Requirements:** Python 3.10+ and Claude Code. No Docker, no Node, no databases. Semantic retrieval (model2vec embeddings) is installed by default and is optional — pass `--no-semantic` to skip it; retrieval falls back to lexical + concept matching.

**Windows (PowerShell):**

```powershell
git clone https://github.com/fullymiddleaged/clawness.git "$env:USERPROFILE\.claude\clawness"
cd "$env:USERPROFILE\.claude\clawness"
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

**macOS / Linux:**

```bash
git clone https://github.com/fullymiddleaged/clawness.git ~/.claude/clawness
cd ~/.claude/clawness
bash install.sh
```

### What the Manual Installer Does (7 steps)

| Step | What | Why |
|------|------|-----|
| 1 | Check Python 3.10+ | Finds `python` / `python3` / `py` |
| 2 | Check dependencies | Installs PyYAML, plus model2vec for semantic retrieval (skip with `--no-semantic`) |
| 3 | Verify files | Confirms rules and hook scripts are present |
| 4 | Lint rules | Validates every `.yml` rule file |
| 5 | Test retrieval | Runs a test query to confirm the engine works |
| 6 | Install agents & skills | Copies to `~/.claude/agents/` and `~/.claude/skills/` |
| 7 | Configure hooks | Adds rule injection, output compression, and the plan gate (on by default) to `settings.json` |

The installer is idempotent — safe to re-run. It won't duplicate hooks or overwrite existing settings.

### Uninstall

**Plugin install** — use Claude Code's own command (the `/plugin` menu's remove is unreliable; use the CLI):

```bash
claude plugin uninstall clawness
claude plugin marketplace remove clawness   # optional — also drops the marketplace
```

Add `--prune` to also clean up dependencies, and `--scope project` if you installed it at project scope.

**Manual install** — don't just delete the folder: that leaves hook entries in `settings.json` pointing at missing scripts, which error on every prompt. Run the uninstaller first (it removes the hooks and the copied agents/skills), then delete the folder:

```bash
# macOS / Linux
bash ~/.claude/clawness/uninstall.sh
rm -rf ~/.claude/clawness

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\clawness\uninstall.ps1"
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\clawness"
```

Left in place on purpose (remove by hand if you want): the `pyyaml` / `model2vec` / `numpy` pip packages (shared with other tools), the model2vec model cache under `~/.cache/huggingface`, and any per-project rules in each project's `.writ/`.

---

## Using It

### The Short Answer

**Just use Claude Code normally.** After installation, the hook fires silently on every prompt. You don't type anything special, you don't reference rules, you don't invoke agents. Claude just sees the relevant rules in its context and follows them.

### What Claude Actually Sees

When you type *"implement the user registration endpoint"*, Claude receives this prepended to the conversation:

```
--- WRIT RULES (9 rules, 0.31ms) ---

# MANDATORY (7)
[ENF-CURRENT-001] (general/error)
  RULE: Always use current best practices for the present month and year...
[ENF-SEC-001] (security/error)
  RULE: All secrets must come from environment variables...
[ENF-SEC-002] (security/error)
  RULE: Always use parameterized queries...
...

# RELEVANT (2)
[FA-PYDANTIC-001] (fastapi/error) score=0.033
  WHEN: Defining request or response shapes for any endpoint.
  RULE: Define Pydantic models for every request body and response...
[GEN-VALIDATE-001] (general/error) score=0.031
  WHEN: Receiving any input from users, APIs, files, or external systems.
  RULE: Validate and sanitize all external input at the boundary...

--- END WRIT RULES ---
```

The mandatory rules always appear. The ranked rules change based on your prompt.

### Verify It's Working

Ask Claude Code directly:

```
> what writ rules do you see in your context?
```

If the hook is active, Claude will describe the rules it received.

### Output Compression

When Claude runs a bash command that produces 100+ lines of output (test suites, builds, long logs), the PostToolUse compression hook fires automatically. It extracts only the error/failure lines with context and provides a summary, keeping Claude's context clean for the next prompt.

### Plan Gate (on by default)

Clawness enforces a plan-first workflow: file edits (`Write`/`Edit`/`MultiEdit`/`NotebookEdit`) are blocked until you've approved a plan. It rides Claude Code's **native plan mode** — present a plan, approve it, and the gate clears itself for the rest of the session. No writ-specific commands are needed in the normal flow.

If Claude tries to edit before a plan is approved, you'll see a deny message explaining what to do. Approve a plan in plan mode and editing proceeds.

To change the behavior:

```bash
clawness plan off       # disable for this project
clawness plan on        # re-enable
clawness plan status    # show current state
clawness plan approve   # manual override (headless / no plan mode)
```

Or set `WRIT_NO_PLAN_GATE=1` to disable it globally via the environment.

**Version control:** the plan gate stops *unplanned* edits, but recovering from a *bad* edit is git's job — Clawness deliberately doesn't reimplement checkpoints. If you open a project that isn't a git repo, a SessionStart check nudges Claude to ask whether you'd like to `git init` (it never initializes without your say-so). Silence it with `WRIT_NO_GIT_CHECK=1`.

---

## Per-Project Setup

Global rules handle security, testing, general best practices, and framework conventions. For project-specific rules (your API format, your database conventions, your naming patterns), use `init`:

```bash
cd ~/projects/my-app
python -m writ_lite.cli init .
```

This scans your project and reports:

```
Project: /home/you/projects/my-app

Detected stack:
  + Node.js project
  + TypeScript
  + Next.js
  + Capacitor (mobile)
  + React
  + Prisma ORM

Recommended rule domains: capacitor, general, nextjs, react, typescript, workflows

Starter project rule:
  id: MY_APP-STACK-001
  domain: my-app
  ...
```

Add `--write` to create the project rules directory:

```bash
python -m writ_lite.cli init . --write
```

This creates `.writ/rules/` in your project. The hook automatically picks up rules from this directory when you're working in the project. **Commit `.writ/` to git** — your whole team gets the same rules.

### Project Rules Directory

```
my-app/
├── .writ/
│   └── rules/
│       ├── _mandatory/           # Project-specific mandatory rules
│       │   └── MYAPP-DEPLOY-001.yml
│       └── my-app/               # Project-specific ranked rules
│           ├── MYAPP-API-001.yml
│           └── MYAPP-DB-001.yml
├── src/
├── package.json
└── ...
```

Rules in `.writ/rules/_mandatory/` are always injected when working in this project. Rules in other subdirectories are ranked as usual.

---

## Writing Rules

### Rule Format

```yaml
id: FA-PYDANTIC-001
domain: fastapi
severity: error          # error | warning | info
tags: [pydantic, model, schema, validation, request, response]
triggers: [BaseModel, schema, model, request, response, body, Field]
when: Defining request or response shapes for any endpoint.
rule: >
  Define Pydantic models for every request body and response. Never
  accept or return raw dicts. Use separate models for create, update,
  and read operations.
violation: "@app.post('/users') async def create(data: dict)"
correct: "@app.post('/users', response_model=UserRead) async def create(data: UserCreate)"
```

### What Each Field Does

| Field | Required | Drives Retrieval? | Purpose |
|-------|----------|-------------------|---------|
| `id` | Yes | Yes | Unique ID, shown in output |
| `domain` | Yes | Yes | Category for filtering |
| `severity` | No | No | `error` / `warning` / `info` |
| `tags` | **Recommended** | **Yes** | Keywords — what topic does this rule cover? |
| `triggers` | **Recommended** | **Yes** | Code tokens that signal relevance |
| `when` | **Recommended** | Yes | When should this rule apply? |
| `rule` | Yes | Yes | The instruction Claude follows |
| `violation` | No | Yes | What NOT to do |
| `correct` | No | Yes | What TO do |

### Tips for Good Rules

**`tags` and `triggers` are the most important fields.** The retriever matches your prompt against these. Think: *what words would someone use when working on a task this rule applies to?*

```yaml
# Bad — too generic
tags: [code]
triggers: [function]

# Good — specific to the actual concept
tags: [database, connection, pooling, timeout, postgres]
triggers: [create_engine, SessionLocal, get_db, connection_pool]
```

**Use `_mandatory/` sparingly.** Every mandatory rule costs tokens on every prompt. Reserve for security gates and testing requirements.

**Run `lint` after adding rules:**

```bash
python -m writ_lite.cli lint
```

---

## Sub-Agents

Clawness ships seven adversarial sub-agents that Claude Code can delegate to. The main ones are below; the full list with model/effort settings is in the [Configuration](#agent-model-configuration) table.

### Security Red Team / Blue Team

When you say *"run a security audit on the auth module"*, the workflow rule tells Claude to:
1. **Delegate to `security-red-team`** — thinks like an attacker, runs OWASP Top 10, searches for CVEs published *this month* affecting your stack
2. **Delegate to `security-blue-team`** — takes the red team report, triages findings, proposes exact code fixes, adds hardening measures
3. **Synthesize** — Claude merges both reports into a prioritized action plan

### Code Critic

For code reviews before merge. Focuses on bugs, performance, edge cases, and maintainability — the things the original author is blind to.

### Architecture Challenger

Devil's advocate for design decisions. Stress-tests assumptions: *what if it's 10x the load? what if this component fails? is there a simpler alternative?*

### Triggering Agents

You can invoke them directly:

```
> have the security-red-team agent review the auth module
> have the code-critic agent review my latest changes
```

Or just describe the task naturally — the workflow rules tell Claude when to reach for them:

```
> run a security audit on this project
> review the code before we merge
> should we use PostgreSQL or MongoDB for this?
```

**Proactive offers.** The agent-spawning skills (`audit`, `review`, `perf`) don't auto-run, because launching several sub-agents is expensive. Instead, when your prompt sounds like a security audit, code review, or performance check, Clawness nudges Claude to *offer* — e.g. "Sounds like you want a security audit — want me to run the red team / blue team now?" — and it only spawns the agents once you say yes. You can always skip the offer and run them directly with `/clawness:audit`, `/clawness:review`, or `/clawness:perf`.

---

## CLI Reference

```bash
# Retrieve rules for a task description
python -m writ_lite.cli query "implement async REST endpoint"
python -m writ_lite.cli query "handle null values" --domain typescript
python -m writ_lite.cli query "set up logging" --top-k 3 --budget 2000

# Scan a project and suggest rules
python -m writ_lite.cli init /path/to/project
python -m writ_lite.cli init . --write    # create .writ/rules/ in this project

# Corpus management
python -m writ_lite.cli stats             # show rule counts by domain
python -m writ_lite.cli lint              # validate all rule files
python -m writ_lite.cli bench             # benchmark retrieval latency

# Plan gate (on by default; normal flow uses native plan mode)
python -m writ_lite.cli plan status       # show gate state
python -m writ_lite.cli plan off          # disable for this project
python -m writ_lite.cli plan approve      # manual override (headless use)

# Emit an AGENTS.md so any agent (not just Claude Code) can use the CLI
python -m writ_lite.cli agents-md --write

# Point at a different rules directory
python -m writ_lite.cli --rules-dir /path/to/rules stats
```

Use `python` on Windows, `python3` on macOS/Linux.

---

## What Ships

| Component | Count | Purpose |
|-----------|-------|---------|
| **Rules** | 106 across 17 domains | Coding standards, injected per-prompt |
| **Agents** | 7 sub-agents | Security red/blue team, code critic, test writer, perf auditor, refactor advisor, architecture challenger |
| **Skills** | 6 slash commands | `/clawness:audit`, `/clawness:review`, `/clawness:test`, `/clawness:perf`, `/clawness:add`, `/clawness:status` |
| **Hooks** | 5 (rule injection, output compression, plan gate, git check, dependency bootstrap) | Automatic context management & workflow enforcement |
| **CLI** | 7 commands | query, init, stats, lint, bench, plan, agents-md |
| **Installers** | bash + PowerShell (with matching uninstallers) | 7-step setup for Windows, macOS, Linux |
| **Plugin manifest** | marketplace + plugin | For `claude plugin install` |

### Rule Domains

| Domain | Rules | Covers |
|--------|-------|--------|
| `general` | 17 | Cross-cutting: abstraction/YAGNI, comments, memory, nesting, magic numbers, immutability, dependency selection, versioning/lockfiles, linting, naming, validation, logging, env config, accessibility, git, performance |
| `nextjs` | 10 | Server/Client components, data fetching, caching, layouts, metadata, Server Actions |
| `fastapi` | 8 | Pydantic v2, dependency injection, async, error handling, CORS, DB sessions |
| `python` | 7 | Async I/O, imports, error handling, type hints, mutable defaults, context managers, pathlib |
| `workflows` | 7 | Multi-agent orchestration (security audit, code review, testing, perf, refactoring, architecture, parallel research) |
| `capacitor` | 6 | Platform detection, permissions, lifecycle, WebView, sync, App Store |
| `css` | 6 | `!important`, relative units, flex/grid layout, custom properties, responsive, focus states |
| `docker` | 6 | Layer caching, multi-stage builds, non-root, secrets, tag pinning, slim images |
| `java` | 6 | Null safety, equals/hashCode, try-with-resources, exceptions, immutability, collections |
| `go` | 5 | Error handling, nil maps, context, goroutine lifecycle, data races |
| `rust` | 5 | unwrap/expect, error handling, clone, unsafe, iterators |
| `sql` | 5 | N+1 queries, indexes, transactions, `SELECT *`, migrations |
| `security` | 5 | XSS, SQLi, auth, secrets, deps *(mandatory)* |
| `react` | 4 | Hooks, state management, list keys, forms |
| `typescript` | 4 | Null safety, async errors, strict mode, Zod |
| `bash` | 4 | Strict mode, quoting, error checking, shellcheck |
| `testing` | 1 | Test coverage for new code *(mandatory)* |

The 7 **mandatory** rules (always injected) are the 5 `security` rules, the 1 `testing` rule, and 1 current-practices rule (counted under `general`).

---

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `WRIT_RULES_DIR` | (next to hook script) | Override global rules directory |
| `WRIT_TOP_K` | `6` | Max ranked rules per prompt |
| `WRIT_BUDGET` | `4000` | Max tokens for the rule block |
| `WRIT_NO_SEMANTIC` | (unset) | Disable model2vec embeddings (lexical + concept only) |
| `WRIT_NO_PLAN_GATE` | (unset) | Disable the plan gate globally |
| `WRIT_NO_GIT_CHECK` | (unset) | Stop offering to `git init` when a project isn't under version control |
| `WRIT_EMBED_MODEL` | `minishlab/potion-base-8M` | model2vec model for semantic retrieval |
| `CLAUDE_CONFIG_DIR` | `~/.claude` | Claude Code's config dir — the installer/uninstaller follow it if you've relocated it |
| `CLAUDE_CODE_SUBAGENT_MODEL` | (none) | Override model for ALL sub-agents |

### Agent Model Configuration

Clawness uses a two-tier model strategy:

- **Orchestrator (your main Claude Code session):** Opus 4.8 — handles planning, synthesis, and coordination
- **Sub-agents (the 7 worker agents):** Sonnet 4.6 — handles focused analysis tasks at ~80% lower cost

Start Claude Code with Opus for orchestration:

```bash
claude --model claude-opus-4-8
```

Sub-agents automatically run on Sonnet 4.6. When the orchestrator delegates to a sub-agent (e.g. the red team), the sub-agent runs on Sonnet 4.6 and returns its findings to Opus for synthesis. You get Opus-quality coordination with Sonnet-speed execution.

| Agent | Default Model | Effort | Max Turns | Why |
|-------|--------------|--------|-----------|-----|
| `security-red-team` | claude-sonnet-4-6 | high | 25 | Thorough vulnerability scanning |
| `security-blue-team` | claude-sonnet-4-6 | high | 25 | Fix proposals need reasoning |
| `code-critic` | claude-sonnet-4-6 | medium | 15 | Read-only code analysis |
| `test-writer` | claude-sonnet-4-6 | medium | 20 | Writes and runs test files |
| `perf-auditor` | claude-sonnet-4-6 | medium | 15 | Performance pattern matching |
| `refactor-advisor` | claude-sonnet-4-6 | medium | 15 | Read-only code smell detection |
| `arch-challenger` | claude-sonnet-4-6 | high | 15 | Architecture stress-testing |

### Changing Model Defaults

**Change a single agent's model** — edit its `.md` file in `~/.claude/agents/`:

```yaml
# Aliases (auto-update when Anthropic releases new versions)
model: haiku        # cheapest — fast lookups, simple tasks
model: sonnet       # balanced — resolves to latest Sonnet
model: opus         # premium — resolves to latest Opus

# Pinned versions (exact model, won't change)
model: claude-haiku-4-5-20251001
model: claude-sonnet-4-6
model: claude-opus-4-8
model: claude-opus-4-6    # older Opus, cheaper
```

**Change ALL sub-agents at once** — set an environment variable:

```bash
# Run all sub-agents on Haiku (cheapest possible)
export CLAUDE_CODE_SUBAGENT_MODEL="claude-haiku-4-5-20251001"

# Or use the latest Sonnet (alias, auto-updates)
export CLAUDE_CODE_SUBAGENT_MODEL="sonnet"
```

**Change the orchestrator model** — this is your main Claude Code session:

```bash
# Start with Opus 4.8 (recommended for orchestration)
claude --model claude-opus-4-8

# Or switch mid-session
/model claude-opus-4-8

# Budget option: Sonnet for everything (orchestrator + sub-agents)
claude --model claude-sonnet-4-6
```

**The `effort:` field** controls reasoning depth independently of model:

```yaml
effort: low         # quick, shallow
effort: medium      # balanced (default for most agents)
effort: high        # thorough (default for security + architecture)
effort: max         # maximum reasoning — expensive, use sparingly
```

**The `maxTurns:` field** caps tool calls per agent run, preventing runaway costs.

### Where Rules Live

| Location | Scope | When Loaded |
|----------|-------|-------------|
| `~/.claude/clawness/rules/` | Global | Every prompt, every project |
| `<project>/.writ/rules/` | Project | Only when working in that project |
| `<project>/.writ/rules/_mandatory/` | Project mandatory | Every prompt while in that project |

> The `~/.claude/clawness/rules/` path applies to a **manual** install. With the **plugin** install, the global rules ship inside the plugin and load from its cache automatically — you don't manage that path. Either way, project rules in `<project>/.writ/rules/` work the same.

---

## How It Compares

| | Writ | Clawness | CLAUDE.md |
|---|---|---|---|
| Rule selection | Hybrid RAG (BM25 + vector + graph) | Hybrid (BM25 + TF-IDF + RRF) | All rules, every turn |
| Token cost per turn | ~200 tokens (selected) | ~200 tokens (selected) | All rules × all turns |
| Infrastructure | Neo4j + Docker + ONNX (~2 GB) | PyYAML (~200 KB) | None |
| Install time | ~5 minutes | ~5 seconds | Copy/paste |
| Mandatory rules | Yes | Yes | Manual discipline |
| Context budget | Yes | Yes | No |
| Output compression | No | Yes (PostToolUse hook) | No |
| Sub-agents | No | 7 adversarial agents | No |
| Per-project rules | No | Yes (.writ/rules/) | Yes (per-directory CLAUDE.md) |

---

## Troubleshooting

**Plugin install: skills/hooks not showing up**
Run `/reload-plugins`, or check `claude plugin list`. The plugin installs its Python deps (PyYAML, and model2vec for semantic) in the background on first session via a SessionStart hook — if retrieval seems lexical-only at first, give it a moment or check the `bootstrap.log` in the plugin's data directory. Run `claude --debug` to see hook activity.

**Hook not firing / Claude doesn't see rules**
Check `~/.claude/settings.json` contains the hook config. Run the installer again — it's idempotent and will report what's already configured vs what it adds.

**PowerShell: "running scripts is disabled"**
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

**"No module named yaml"**
```bash
python -m pip install pyyaml --user
```

**Wrong rules appearing / right rules not appearing**
Test what the retriever sees for your exact prompt:
```bash
python -m writ_lite.cli query "your exact prompt text here"
```
Improve `tags` and `triggers` fields on the rules that should match.

**Too many mandatory rules eating tokens**
Move rules from `_mandatory/` to a ranked domain. Only security gates and test requirements should be mandatory.

**Want to temporarily disable Clawness**
Rename the hook entries in `~/.claude/settings.json` or delete them. Re-run the installer to add them back.

---

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

Inspired by [infinri/Writ](https://github.com/infinri/Writ), which pioneered hybrid-RAG rule retrieval for AI coding agents. Clawness takes the same core ideas and repackages them without the infrastructure.
