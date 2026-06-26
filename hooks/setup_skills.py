#!/usr/bin/env python3
"""
Copy Clawness skills to ~/.claude/skills/.

Each skill is a directory containing SKILL.md. Copies to the user's
global skills directory so they're available as /slash-commands in
every Claude Code session.

Usage:
    python setup_skills.py /path/to/clawness/skills
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
    return _claude_config_dir() / "skills"


def install_skills(source_dir: Path, target_dir: Path | None = None) -> str:
    target_dir = target_dir or default_target()
    target_dir.mkdir(parents=True, exist_ok=True)

    skills = sorted([d for d in source_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
    if not skills:
        return "SKIP: No skills found"

    copied = []
    skipped = []

    for skill_dir in skills:
        dest = target_dir / skill_dir.name
        skill_file = dest / "SKILL.md"
        if skill_file.exists():
            skipped.append(skill_dir.name)
        else:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill_dir / "SKILL.md", skill_file)
            copied.append(skill_dir.name)

    parts = []
    if copied:
        parts.append(f"Installed: {', '.join(copied)}")
    if skipped:
        parts.append(f"Skipped (exist): {', '.join(skipped)}")
    parts.append(f"Location: {target_dir}")

    return "OK: " + " | ".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: setup_skills.py <skills_dir>", file=sys.stderr)
        sys.exit(1)

    source = Path(sys.argv[1])
    if not source.is_dir():
        print(f"ERROR: {source} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = install_skills(source)
    print(result)


if __name__ == "__main__":
    main()
