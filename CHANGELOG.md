# Changelog

All notable changes to Clawness will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-06-27

### Fixed
- Plugin install failed: `marketplace.json` declared the plugin `source` as a
  second GitHub clone of the same repo. Corrected to `"./"` (the plugin *is* the
  marketplace repo), so install reuses the already-fetched copy — no redundant
  clone, and no install-time clone at all for local marketplaces.
- Manual installer hardcoded a single Python interpreter into the settings.json
  hooks. It now writes the same portable `python3 → python → py` picker as the
  plugin hooks, so hooks run even when only the Windows `py` launcher (or only
  `python3`) is on PATH.

## [0.2.0] - 2026-06-27

### Added
- 7 new rule domains: Go, Rust, Java, SQL, bash, CSS, Docker
- Semantic (model2vec) retrieval, on by default — fuses with BM25 + TF-IDF +
  concept expansion via Reciprocal Rank Fusion; opt out with `CLAW_NO_SEMANTIC`
- Plan-approval gate (default-on, opt-out), riding Claude Code's native plan mode,
  with a `plan` CLI command (`status` / `on` / `off` / `approve` / `reset`)
- SessionStart git-presence check (nudges to `git init`; silence with `CLAW_NO_GIT_CHECK`)
- SessionStart dependency-bootstrap hook (installs PyYAML / model2vec in the background)
- `agents-md` CLI command — emit an AGENTS.md so any agent can drive the CLI
- `meta` domain: 8 rationalization-counter rules that rebut common AI shortcuts
  (skip tests, "too simple", hardcode "temporarily", trust input) — surfaced by
  the retriever when a prompt signals a shortcut
- Vagueness lint: `lint` now rejects unenforceable weasel phrasing in rules
- Retrieval-quality eval harness: `eval` command with a labeled ground-truth set,
  reporting MRR@5 + hit-rate against configurable floors (gates CI)
- Token efficiency: mandatory rules render compactly (~45% smaller fixed block);
  `CLAW_VERBOSE` / `CLAW_COMPACT` knobs; `stats` reports per-turn token estimate

### Changed
- Rule corpus expanded from 57 to 114 rules; now 18 domains total
- Renamed throughout to **Clawness** — package `clawness` (was `writ_lite`),
  env vars `CLAW_*` (were `WRIT_*`), project rules in `.clawness/` (was `.writ/`)
- `clawness` is now installed as a real command (editable `pip install`)
- Plugin distribution via `.claude-plugin` marketplace + plugin manifests (`claude plugin install`)

## [0.1.0] - 2026-06-24

### Added
- Hybrid retrieval engine (BM25 + TF-IDF + Reciprocal Rank Fusion)
- 57 rules across 10 domains: mandatory security, Next.js, FastAPI, Capacitor, React, TypeScript, Python, general, workflows
- 7 adversarial sub-agents: security red/blue team, code critic, test writer, performance auditor, refactor advisor, architecture challenger
- 6 skills (slash commands): `/clawness:audit`, `/clawness:review`, `/clawness:test`, `/clawness:perf`, `/clawness:add`, `/clawness:status`
- UserPromptSubmit hook for automatic rule injection
- PostToolUse hook for bash output compression
- Global rules (~/.claude/clawness/rules/) + project rules (.clawness/rules/) layering
- `clawness init` project scanner with auto-detection for Next.js, FastAPI, Capacitor, React, TypeScript, Python
- `clawness query`, `stats`, `lint`, `bench` CLI commands
- Plugin manifest (.claude-plugin/plugin.json) and marketplace manifest
- PowerShell and bash installers (7-step, idempotent)
- Per-agent model configuration (default: claude-sonnet-4-6 for sub-agents, claude-opus-4-8 recommended for orchestrator)
