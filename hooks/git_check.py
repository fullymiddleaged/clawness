#!/usr/bin/env python3
"""
Clawness — git presence check (SessionStart).

If the project isn't under version control, this injects a short note into
context so Claude will *ask* the user whether to initialize git. It never runs
`git init` itself — hooks can't interactively prompt, and initializing version
control is the user's call. The note tells Claude to ask and to act only on
explicit confirmation.

Silent when git is present, when git isn't installed, in non-project locations
(home dir / filesystem root), or when disabled via WRIT_NO_GIT_CHECK. Fails open.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

NOTE = (
    "[Clawness] This project is not under version control (no git repository "
    "found). The plan gate blocks unplanned edits, but recovering from a bad "
    "edit relies on git. Early in this session, briefly tell the user and ask "
    "whether they'd like to initialize git for this project. Only run `git init` "
    "(and offer an initial commit — `git init` alone protects nothing until "
    "there's a commit) if the user agrees; never initialize version control "
    "without explicit confirmation. The user can silence this with "
    "WRIT_NO_GIT_CHECK=1."
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if os.environ.get("WRIT_NO_GIT_CHECK"):
        sys.exit(0)

    cwd = payload.get("cwd") or os.getcwd()
    try:
        cwd_path = Path(cwd).resolve()
    except Exception:
        sys.exit(0)

    # Don't nag in non-project locations (home directory or filesystem root).
    try:
        if cwd_path == Path.home().resolve() or cwd_path.parent == cwd_path:
            sys.exit(0)
    except Exception:
        pass

    # Per-project opt-out marker.
    if (cwd_path / ".writ" / "git-check-off").exists():
        sys.exit(0)

    # If git isn't installed, suggesting `git init` is pointless.
    if not shutil.which("git"):
        sys.exit(0)

    # Already inside a work tree (handles a parent-dir .git too)? Stay silent.
    try:
        r = subprocess.run(
            ["git", "-C", str(cwd_path), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip() == "true":
            sys.exit(0)
    except Exception:
        sys.exit(0)

    # No git → inject the note (SessionStart stdout is added to Claude's context).
    print(NOTE)
    sys.exit(0)


if __name__ == "__main__":
    main()
