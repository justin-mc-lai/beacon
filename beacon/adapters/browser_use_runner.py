"""Browser-use adapter for Beacon auto-test runner policy.

This adapter intentionally prefers explicit project commands to avoid false-positive passes.
Use `--fallback-cmd` to run deterministic local tests when browser-use runtime is unavailable.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def _inject_pytest_junit_arg(command: str) -> str:
    cmd = str(command or "").strip()
    if not cmd:
        return cmd
    junit_path = str(os.environ.get("BEACON_JUNIT_PATH", "")).strip()
    if not junit_path:
        return cmd
    lowered = cmd.lower()
    if "pytest" not in lowered:
        return cmd
    if "--junitxml" in lowered:
        return cmd
    if re.search(r"\bpy(?:thon|thon3)?\s+-m\s+pytest\b", lowered) or "pytest " in lowered:
        return f'{cmd} --junitxml "{junit_path}"'
    return cmd


def _run_fallback(command: str, cwd: Path) -> int:
    resolved_command = _inject_pytest_junit_arg(command)
    result = subprocess.run(
        resolved_command,
        cwd=cwd,
        shell=True,
        text=True,
    )
    return int(result.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", default="functional", choices=["functional", "compatibility"])
    parser.add_argument("--task", default="", help="Natural language task for browser-use.")
    parser.add_argument(
        "--fallback-cmd",
        default="",
        help="Deterministic fallback command when browser-use runtime is not configured.",
    )
    parser.add_argument("--project-root", default=".", help="Project root.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    task = str(args.task or "").strip()
    fallback_cmd = str(args.fallback_cmd or "").strip()

    try:
        import browser_use  # type: ignore # noqa: F401
    except Exception:
        if fallback_cmd:
            print(f"[browser-use-adapter] browser-use unavailable, fallback: {fallback_cmd}")
            return _run_fallback(fallback_cmd, cwd=project_root)
        print(
            "[browser-use-adapter] browser-use package is unavailable and no --fallback-cmd provided. "
            "Provide --functional-command/--compatibility-command with a real executable command."
        )
        return 2

    # Keep default adapter conservative: require explicit task to avoid fake passes.
    if not task:
        if fallback_cmd:
            print(f"[browser-use-adapter] no task configured, fallback: {fallback_cmd}")
            return _run_fallback(fallback_cmd, cwd=project_root)
        print(
            "[browser-use-adapter] browser-use detected but --task missing. "
            "Set BEACON_BROWSER_USE_TASK via custom command wrapper or pass deterministic fallback."
        )
        return 2

    # NOTE: real browser-use task execution should be project-defined due model/provider/runtime differences.
    # To stay deterministic in Beacon core, we delegate to explicit fallback command when present.
    if fallback_cmd:
        print(f"[browser-use-adapter] task accepted ({args.mode}), delegated fallback: {fallback_cmd}")
        return _run_fallback(fallback_cmd, cwd=project_root)

    print(
        "[browser-use-adapter] task configured but no explicit runner command provided. "
        "Use --fallback-cmd or pass --functional-command/--compatibility-command in Beacon."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
