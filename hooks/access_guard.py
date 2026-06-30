#!/usr/bin/env python3
"""
Clawness — access guard hook (PreToolUse).

Forces a human decision on tool calls that look like exfiltration, destruction,
or a scope-escape, even when the user has broadly allow-listed the tool — the
in-session companion to the plan gate. Decision logic lives in
``clawness/guard.py``; this script is just the stdin/stdout wrapper.

Wire in .claude-plugin/plugin.json:
  PreToolUse matcher "Bash|Write|Edit|MultiEdit|NotebookEdit|Read"

Output: emits hookSpecificOutput.permissionDecision = "deny" | "ask" to block or
prompt; otherwise exits 0 (defer to the normal permission flow). Coexists with
plan_gate (separate PreToolUse entry); Claude Code resolves multiple hooks as
deny > ask > allow. Fails OPEN on any error so a guard bug never breaks a session.
Opt out with CLAW_NO_ACCESS_GUARD=1.
"""

import json
import os
import sys
from pathlib import Path

# stdin/stdout arrive as UTF-8; on Windows they default to cp1252 and would
# mangle non-ASCII paths in the payload or reason. Pin UTF-8.
for _stream in (sys.stdin, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from clawness.guard import (
        ALLOW,
        ASK,
        DENY,
        already_asked,
        classify_tool_call,
        dedup_key,
        record_ask,
    )
    from clawness.plan import find_project_root
except Exception:
    sys.exit(0)


def main() -> None:
    if os.environ.get("CLAW_NO_ACCESS_GUARD"):
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    try:
        tool_name = payload.get("tool_name", "") or ""
        tool_input = payload.get("tool_input") or {}
        session_id = payload.get("session_id", "") or ""
        cwd = payload.get("cwd") or None
        root = find_project_root(Path(cwd) if cwd else None)

        decision, reason = classify_tool_call(tool_name, tool_input, root)
        if decision == ALLOW or not reason:
            sys.exit(0)

        # Ask at most once per target per session, so a confirmed-OK out-of-project
        # write or known-host upload doesn't re-prompt on every repeat. Denies are
        # never suppressed.
        if decision == ASK:
            key = dedup_key(tool_name, tool_input)
            if already_asked(root, session_id, key):
                sys.exit(0)
            record_ask(root, session_id, key)
    except Exception:
        sys.exit(0)  # fail open

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
