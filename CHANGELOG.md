# Changelog

All notable changes to Clawness will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-24

### Added
- Hybrid retrieval engine (BM25 + TF-IDF + Reciprocal Rank Fusion)
- 57 rules across 10 domains: mandatory security, Next.js, FastAPI, Capacitor, React, TypeScript, Python, general, workflows
- 7 adversarial sub-agents: security red/blue team, code critic, test writer, performance auditor, refactor advisor, architecture challenger
- 6 skills (slash commands): `/clawness:audit`, `/clawness:review`, `/clawness:test`, `/clawness:perf`, `/clawness:add`, `/clawness:status`
- UserPromptSubmit hook for automatic rule injection
- PostToolUse hook for bash output compression
- Global rules (~/.claude/clawness/rules/) + project rules (.writ/rules/) layering
- `clawness init` project scanner with auto-detection for Next.js, FastAPI, Capacitor, React, TypeScript, Python
- `clawness query`, `stats`, `lint`, `bench` CLI commands
- Plugin manifest (.claude-plugin/plugin.json) and marketplace manifest
- PowerShell and bash installers (7-step, idempotent)
- Per-agent model configuration (default: claude-sonnet-4-6 for sub-agents, claude-opus-4-8 recommended for orchestrator)
