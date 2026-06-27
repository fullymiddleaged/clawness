#!/usr/bin/env python3
"""
Clawness — dependency bootstrap (SessionStart, async).

Plugin installation copies files but does not run pip, so this hook ensures
the Python dependencies are present. It is wired as an async SessionStart hook
so it never blocks the session.

Policy:
  - pyyaml is required and installed if missing.
  - model2vec + numpy (semantic retrieval) are installed BY DEFAULT, because
    semantic is the chosen default. Opt out by setting CLAW_NO_SEMANTIC=1.
  - Everything is best-effort: failures are logged, never raised. Until a dep
    is available, retrieval degrades gracefully (lexical/concept, or skipped).
  - A failed install is simply retried on the next session — no lockout — so a
    fixed network/permission issue is picked up immediately.

This script intentionally has no third-party imports of its own.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def data_dir() -> Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.environ.get("CLAW_CACHE_DIR")
    if not base:
        base = str(Path.home() / ".cache" / "clawness")
    p = Path(base)
    try:
        p.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return p


def log(msg: str) -> None:
    try:
        with open(data_dir() / "bootstrap.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}  {msg}\n")
    except Exception:
        pass


def importable(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def pip_install(packages: list[str]) -> bool:
    """Best-effort pip install for the current interpreter. Tries a plain
    install first (works in a venv/conda and in user-writable Pythons), then
    --user (avoids needing admin on a system-wide Python; pip rejects --user
    inside a venv, so plain must come first), then adds --break-system-packages
    (Debian / PEP 668). Returns True on success."""
    base = [sys.executable, "-m", "pip", "install", *packages]
    for extra in ([], ["--user"], ["--user", "--break-system-packages"]):
        try:
            r = subprocess.run(
                base + extra,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=540,
            )
            if r.returncode == 0:
                return True
        except Exception as e:
            log(f"pip error for {packages}: {e}")
    return False


def ensure(name: str, packages: list[str]) -> None:
    """Install *packages* if *name* isn't importable. Best-effort, and simply
    retried on the next session if it fails — until then retrieval degrades
    gracefully (lexical-only, or no rules if pyyaml is the one missing). pip
    fails fast when offline and caches downloads, so re-attempting is cheap."""
    if importable(name):
        return
    log(f"installing {name} ({' '.join(packages)})...")
    ok = pip_install(packages)
    log(
        f"{name} install "
        + ("succeeded" if ok else "failed (will retry next session; falls back gracefully)")
    )


def main() -> None:
    # Drain stdin (SessionStart payload) so the pipe closes cleanly.
    try:
        sys.stdin.read()
    except Exception:
        pass

    log("clawness bootstrap: ensuring Python deps are present "
        "(PyYAML required; model2vec+numpy optional, for semantic search)")

    # Required.
    ensure("yaml", ["pyyaml>=6.0"])

    # Semantic embeddings — on by default, opt out with CLAW_NO_SEMANTIC.
    if not os.environ.get("CLAW_NO_SEMANTIC"):
        ensure("model2vec", ["model2vec>=0.3", "numpy>=1.24"])
    else:
        log("CLAW_NO_SEMANTIC set — skipping model2vec (semantic search off)")

    log("clawness bootstrap: done")

    sys.exit(0)


if __name__ == "__main__":
    main()
