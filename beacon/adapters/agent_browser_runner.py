"""Agent-browser adapter for Beacon story-exhaustive browser QA."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from beacon.adapters.browser_runner_common import load_task, write_runner_artifacts


def _run_fallback(command: str, cwd: Path) -> int:
    result = subprocess.run(command, cwd=cwd, shell=True, text=True)
    return int(result.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", default="functional", choices=["functional", "compatibility"])
    parser.add_argument("--task", default="", help="Natural language task for agent-browser.")
    parser.add_argument("--task-file", default="", help="Compiled browser task json path.")
    parser.add_argument("--fallback-cmd", default="", help="Fallback deterministic command.")
    parser.add_argument("--project-root", default=".", help="Project root.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    layer_dir_value = str(os.environ.get("BEACON_LAYER_DIR", "")).strip()
    layer_dir = Path(layer_dir_value) if layer_dir_value else None
    task_file = str(args.task_file or os.environ.get("BEACON_BROWSER_TASK_FILE", "")).strip()
    task, task_payload = load_task(str(args.task or ""), task_file)
    fallback_cmd = str(args.fallback_cmd or os.environ.get("BEACON_BROWSER_FALLBACK_CMD", "")).strip()

    if not task:
        if fallback_cmd:
            print(f"[agent-browser-adapter] no task configured, fallback: {fallback_cmd}")
            write_runner_artifacts(
                layer_dir=layer_dir,
                project_root=project_root,
                runner="agent-browser",
                task_file=task_file,
                task_text="",
                task_payload=task_payload,
                mode=args.mode,
                status="fallback-no-task",
                fallback_cmd=fallback_cmd,
            )
            return _run_fallback(fallback_cmd, cwd=project_root)
        print("[agent-browser-adapter] task missing. Set --task/--task-file or BEACON_BROWSER_TASK_FILE.")
        write_runner_artifacts(
            layer_dir=layer_dir,
            project_root=project_root,
            runner="agent-browser",
            task_file=task_file,
            task_text="",
            task_payload=task_payload,
            mode=args.mode,
            status="missing-task",
            fallback_cmd=fallback_cmd,
        )
        return 2

    # Beacon keeps this adapter deterministic by preferring project-provided fallback commands.
    if fallback_cmd:
        print(f"[agent-browser-adapter] task accepted ({args.mode})")
        write_runner_artifacts(
            layer_dir=layer_dir,
            project_root=project_root,
            runner="agent-browser",
            task_file=task_file,
            task_text=task,
            task_payload=task_payload,
            mode=args.mode,
            status="fallback-executed",
            fallback_cmd=fallback_cmd,
        )
        return _run_fallback(fallback_cmd, cwd=project_root)

    write_runner_artifacts(
        layer_dir=layer_dir,
        project_root=project_root,
        runner="agent-browser",
        task_file=task_file,
        task_text=task,
        task_payload=task_payload,
        mode=args.mode,
        status="task-only",
        fallback_cmd=fallback_cmd,
    )
    print(task)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
