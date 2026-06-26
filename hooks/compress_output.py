#!/usr/bin/env python3
"""
PostToolUse hook for Bash — compresses verbose tool output before
Claude's next turn sees it.

How it works:
  - Fires after every Bash tool call
  - If output is short (<80 lines), does nothing
  - If output is long, drops noise, extracts errors/failures, and
    replaces the result with a compressed summary via updatedToolOutput
  - Claude sees the summary instead of wading through noise

Configure in settings.json under hooks.PostToolUse with matcher "Bash".
"""

from __future__ import annotations

import json
import re
import sys


# Lines below this threshold pass through unchanged
SHORT_THRESHOLD = 80

# Max lines in the compressed output
MAX_COMPRESSED = 40

# Patterns that indicate errors/failures — always kept.
# Note: no bare "warn" here — it matched benign "npm warn" noise and
# promoted it into the errors section. Use specific, bounded patterns.
ERROR_PATTERNS = re.compile(
    r"(?i)(\berror\b|\bfailed\b|\bfailure\b|exception|traceback|panic|"
    r"\bfatal\b|\bERR!\b|errno|✗|✖|ENOENT|EACCES|EPERM|SyntaxError|"
    r"TypeError|ReferenceError|ModuleNotFoundError|"
    r"cannot find|not found|permission denied|"
    r"build error|compile error|type error|"
    r"\bassert\b|assertion)",
)

# Patterns that are pure noise — dropped before anything else is considered.
NOISE_PATTERNS = re.compile(
    r"(?i)(^\s*$|^npm warn|^npm notice|"
    r"^downloading |^installing |"
    r"^\s*[\-=]{10,}\s*$|"          # separator lines
    r"^\s*\d+\s+passing\b|"          # "42 passing" summary
    r"^[\s│├└─┬┤]*$)",              # tree-drawing characters only
)

# Commands known to be verbose — get extra compression
VERBOSE_COMMANDS = re.compile(
    r"(?i)(npm test|npm run|npx jest|npx vitest|pytest|"
    r"npx next build|npx tsc|eslint|cargo test|cargo build|"
    r"go test|make |gradle |mvn |pip install|"
    r"git log(?!\s+--oneline)|git diff(?!\s+--stat))",
)


def compress(output: str, command: str) -> str | None:
    """
    Compress long tool output. Returns compressed string or None if
    the output is short enough to pass through unchanged.
    """
    raw_lines = output.splitlines()

    if len(raw_lines) <= SHORT_THRESHOLD:
        return None

    # Drop pure-noise lines up front so head/tail/error context is signal,
    # not npm-warn spam and separator bars.
    lines = [ln for ln in raw_lines if not NOISE_PATTERNS.search(ln)]
    if not lines:
        lines = raw_lines  # everything was "noise" — keep something to show

    is_verbose_cmd = bool(VERBOSE_COMMANDS.search(command))

    # Phase 1: extract error lines with surrounding context
    error_lines: list[str] = []
    context_radius = 2

    for i, line in enumerate(lines):
        if ERROR_PATTERNS.search(line):
            start = max(0, i - context_radius)
            end = min(len(lines), i + context_radius + 1)
            for j in range(start, end):
                if lines[j] not in error_lines:
                    error_lines.append(lines[j])

    # Phase 2: keep first few and last few lines for context
    head = lines[:5]
    tail = lines[-5:]

    # Phase 3: build compressed output
    body: list[str] = []
    if head:
        body.append("--- start ---")
        body.extend(head)

    if error_lines:
        body.append("")
        body.append(f"--- errors/warnings ({len(error_lines)} lines) ---")
        body.extend(error_lines[:MAX_COMPRESSED])
        if len(error_lines) > MAX_COMPRESSED:
            body.append(f"  ... {len(error_lines) - MAX_COMPRESSED} more error lines truncated")
    elif is_verbose_cmd:
        body.append("")
        body.append("--- no errors detected ---")

    if tail and tail != head:
        body.append("")
        body.append("--- end ---")
        body.extend(tail)

    # Count only the actual output lines we kept, not the section headers.
    kept = len(head) + len(error_lines[:MAX_COMPRESSED]) + (len(tail) if tail != head else 0)

    parts = [
        f"[clawness: compressed {len(raw_lines)} lines → {kept} kept "
        f"({len(raw_lines) - len(lines)} noise lines dropped)]",
        "",
    ]
    parts.extend(body)
    return "\n".join(parts)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = event.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = ""
    tool_input = event.get("tool_input", {})
    if isinstance(tool_input, dict):
        command = tool_input.get("command", "")

    # Keep the original response object so we can return a replacement that
    # matches the tool's output shape (Claude Code requires this).
    raw_response = event.get("tool_response", "")
    if isinstance(raw_response, dict):
        combined = str(raw_response.get("stdout", "")) + str(raw_response.get("stderr", ""))
    elif isinstance(raw_response, str):
        combined = raw_response
    else:
        combined = str(raw_response)

    compressed = compress(combined, command)

    if compressed is None:
        # Short output — pass through unchanged.
        sys.exit(0)

    # Replace the tool result Claude sees. `updatedToolOutput` substitutes the
    # output (additionalContext would only *append*, leaving the full verbose
    # result in context and defeating the purpose).
    #
    # The replacement MUST match the tool's output shape. Bash returns an
    # object {stdout, stderr, interrupted, isImage, ...}; we preserve every
    # original field and only swap stdout (clearing stderr, since it's folded
    # into the compressed view). If the response was a bare string, we return
    # a string. Replacing built-in tool output requires Claude Code >= 2.1.121.
    if isinstance(raw_response, dict):
        updated = dict(raw_response)
        updated["stdout"] = compressed
        updated["stderr"] = ""
        updated_output = updated
    else:
        updated_output = compressed

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": updated_output,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
