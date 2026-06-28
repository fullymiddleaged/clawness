"""
Tests for the git-presence SessionStart check, especially nested-repo detection.

Runs under pytest, or standalone:  python tests/test_git_check.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GIT_CHECK = REPO / "hooks" / "git_check.py"

needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def _git_init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)


def _nags(cwd: Path) -> bool:
    """True if git_check injects its 'no version control' note for *cwd*."""
    env = dict(os.environ)
    env.pop("CLAW_NO_GIT_CHECK", None)
    r = subprocess.run(
        [sys.executable, str(GIT_CHECK)],
        input=json.dumps({"cwd": str(cwd)}),
        capture_output=True, text=True, env=env,
    )
    return "not under version control" in r.stdout


@needs_git
def test_no_git_anywhere_nags():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "src").mkdir()
        assert _nags(Path(d)) is True


@needs_git
def test_cwd_at_repo_root_is_silent():
    with tempfile.TemporaryDirectory() as d:
        _git_init(Path(d))
        assert _nags(Path(d)) is False


@needs_git
def test_cwd_below_repo_root_is_silent():
    """git searches upward — a subfolder of a repo must not nag."""
    with tempfile.TemporaryDirectory() as d:
        _git_init(Path(d))
        sub = Path(d) / "src" / "deep"
        sub.mkdir(parents=True)
        assert _nags(sub) is False


@needs_git
def test_workspace_parent_with_child_repo_is_silent():
    """The reported bug: repo lives in a child folder, session opens the parent."""
    with tempfile.TemporaryDirectory() as d:
        _git_init(Path(d) / "myproject")
        assert _nags(Path(d)) is False


@needs_git
def test_deeply_nested_child_repo_is_silent():
    with tempfile.TemporaryDirectory() as d:
        _git_init(Path(d) / "group" / "repo")
        assert _nags(Path(d)) is False


@needs_git
def test_repo_only_inside_skipped_dir_still_nags():
    """A vendored .git under node_modules isn't the project's — still nag."""
    with tempfile.TemporaryDirectory() as d:
        _git_init(Path(d) / "node_modules" / "pkg")
        assert _nags(Path(d)) is True


@needs_git
def test_opt_out_is_silent():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "src").mkdir()
        env = dict(os.environ)
        env["CLAW_NO_GIT_CHECK"] = "1"
        r = subprocess.run(
            [sys.executable, str(GIT_CHECK)],
            input=json.dumps({"cwd": str(d)}),
            capture_output=True, text=True, env=env,
        )
        assert r.stdout.strip() == ""


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok  {name}")
            except Exception as e:  # noqa: BLE001
                print(f"FAIL {name}: {e}")
    print("done")
