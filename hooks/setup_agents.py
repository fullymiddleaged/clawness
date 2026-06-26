#!/usr/bin/env python3
"""
Copy Clawness agent definitions to ~/.claude/agents/.

Called by install.ps1 and install.sh. Safe to re-run:
- Creates ~/.claude/agents/ if it doesn't exist
- Copies .md files from the source agents/ directory
- Skips files that already exist (preserves user customizations)
- Reports what was copied vs skipped

Usage:
    python setup_agents.py /path/to/clawness/agents
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _claude_config_dir() -> Path:
    v = os.environ.get("CLAUDE_CONFIG_DIR")
    if v:
        first = v.split(",")[0].strip()
        if first:
            return Path(first).expanduser()
    return Path.home() / ".claude"


def default_target() -> Path:
    return _claude_config_dir() / "agents"


def install_agents(source_dir: Path, target_dir: Path | None = None) -> str:
    target_dir = target_dir or default_target()
    target_dir.mkdir(parents=True, exist_ok=True)

    agents = sorted(source_dir.glob("*.md"))
    if not agents:
        return f"SKIP: No .md files found in {source_dir}"

    copied = []
    skipped = []

    for agent_file in agents:
        dest = target_dir / agent_file.name
        if dest.exists():
            skipped.append(agent_file.name)
        else:
            shutil.copy2(agent_file, dest)
            copied.append(agent_file.name)

    parts = []
    if copied:
        parts.append(f"Installed: {', '.join(copied)}")
    if skipped:
        parts.append(f"Skipped (already exist): {', '.join(skipped)}")
    parts.append(f"Location: {target_dir}")

    return "OK: " + " | ".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: setup_agents.py <agents_dir>", file=sys.stderr)
        sys.exit(1)

    source = Path(sys.argv[1])
    if not source.is_dir():
        print(f"ERROR: {source} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = install_agents(source)
    print(result)


if __name__ == "__main__":
    main()
