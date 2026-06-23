#!/usr/bin/env python3
"""Beacon workspace admission Write gate (Should — defense-in-depth).

Independent of Trellis hooks: TRELLIS_DISABLE_HOOKS must not disable this script.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path | None:
    current = start.resolve()
    while True:
        if (current / ".git").exists():
            return current
        if current.parent == current:
            return None
        current = current.parent


def _write_target_path(payload: dict) -> Path | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    for key in ("path", "file_path", "target_file"):
        raw = tool_input.get(key)
        if raw:
            return Path(str(raw)).expanduser()
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"permission": "allow"}))
        return 0

    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "")
    if tool_name not in {"Write", "write", "Edit", "edit", "ApplyPatch", "apply_patch"}:
        print(json.dumps({"permission": "allow"}))
        return 0

    cwd_raw = payload.get("cwd") or payload.get("working_directory") or "."
    cwd = Path(str(cwd_raw)).expanduser().resolve()
    target = _write_target_path(payload)
    if target is None:
        print(json.dumps({"permission": "allow"}))
        return 0
    if not target.is_absolute():
        target = (cwd / target).resolve()

    repo_root = _find_repo_root(cwd) or _find_repo_root(target)
    if repo_root is None:
        print(json.dumps({"permission": "allow"}))
        return 0

    sys.path.insert(0, str(repo_root))
    try:
        from beacon.utils.workspace_admission import hook_should_deny_write
    except Exception:  # noqa: BLE001
        print(json.dumps({"permission": "allow"}))
        return 0

    deny, reason = hook_should_deny_write(repo_root, target_path=target, cwd=cwd)
    if deny:
        message = (
            f"Beacon workspace admission blocked this write ({reason}). "
            "Run: beacon workspace admit --project-root . --version <v> --feature <slug> --json"
        )
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": message,
                    "agent_message": message,
                }
            )
        )
        return 0
    print(json.dumps({"permission": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
