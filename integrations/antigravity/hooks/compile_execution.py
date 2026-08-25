#!/usr/bin/env python3
"""Compile repo-locate's portable execution contract into Antigravity args.

Antigravity exposes repo execution controls on ``run_command``. Models do not
reliably copy those controls from skill prose into each call, so this hook
makes the mapping deterministic without moving repo-locate behind MCP or
introducing a background-task state machine.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


WAIT_MS_BEFORE_ASYNC = 180_000


def _is_repo_locate(command_line: str) -> bool:
    """Return True only for commands that invoke the repo-locate wrapper."""
    return "repo-locate.sh" in command_line


def _git_root(path: str) -> str | None:
    candidate = Path(path).expanduser()
    if not candidate.exists():
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    root = proc.stdout.strip()
    return root or None


def _repository_root(data: dict[str, Any], args: dict[str, Any]) -> str | None:
    """Resolve the target repository from native Antigravity context.

    Prefer a model-proposed Cwd when it is valid, then the mounted workspace
    paths supplied by Antigravity. Do not fall back to the hook process cwd:
    for plugin hooks that cwd may be the plugin directory rather than the
    repository being explored.
    """
    candidates: list[str] = []
    cwd = args.get("Cwd")
    if isinstance(cwd, str) and cwd:
        candidates.append(cwd)

    workspace_paths = data.get("workspacePaths", [])
    if isinstance(workspace_paths, list):
        candidates.extend(path for path in workspace_paths if isinstance(path, str))

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if root := _git_root(candidate):
            return root

    # A non-git workspace is still a better semantic cwd than the plugin cwd.
    for candidate in candidates:
        path = Path(candidate).expanduser()
        if path.exists() and path.is_dir():
            return str(path.resolve())
    return None


def compile_call(data: dict[str, Any]) -> dict[str, Any]:
    tool_call = data.get("toolCall", {})
    if not isinstance(tool_call, dict) or tool_call.get("name") != "run_command":
        return {"decision": "allow"}

    args = tool_call.get("args", {})
    if not isinstance(args, dict):
        return {"decision": "allow"}

    command_line = args.get("CommandLine", "")
    if not isinstance(command_line, str) or not _is_repo_locate(command_line):
        return {"decision": "allow"}

    overwritten_args = dict(args)
    if root := _repository_root(data, args):
        overwritten_args["Cwd"] = root
    overwritten_args["WaitMsBeforeAsync"] = WAIT_MS_BEFORE_ASYNC
    overwritten_args["RunPersistent"] = False

    return {
        "decision": "allow",
        "overwrite": {
            "name": "run_command",
            "args": overwritten_args,
        },
    }


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        # Fail open: a hook compatibility issue must not brick all shell calls.
        print(json.dumps({"decision": "allow"}))
        return

    print(json.dumps(compile_call(data)))


if __name__ == "__main__":
    main()
