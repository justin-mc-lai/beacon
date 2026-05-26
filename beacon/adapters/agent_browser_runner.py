"""Agent-browser adapter for Beacon story-exhaustive browser QA."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from beacon.adapters.browser_runner_common import load_task, write_runner_artifacts


def _resolve_deterministic_command(args: argparse.Namespace) -> tuple[str, str, bool]:
    current_arg = str(args.deterministic_command or args.explicit_project_command or "").strip()
    if current_arg:
        return current_arg, "", False
    legacy_arg = str(args.fallback_cmd or "").strip()
    if legacy_arg:
        return legacy_arg, legacy_arg, True
    current_env = str(
        os.environ.get("BEACON_BROWSER_DETERMINISTIC_COMMAND", "")
        or os.environ.get("BEACON_BROWSER_EXPLICIT_PROJECT_COMMAND", "")
        or ""
    ).strip()
    if current_env:
        return current_env, "", False
    legacy = str(os.environ.get("BEACON_BROWSER_FALLBACK_CMD", "") or "").strip()
    return legacy, legacy, bool(legacy)


def _run_deterministic_command(command: str, cwd: Path) -> int:
    result = subprocess.run(command, cwd=cwd, shell=True, text=True)
    return int(result.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", default="functional", choices=["functional", "compatibility"])
    parser.add_argument("--task", default="", help="Natural language task for agent-browser.")
    parser.add_argument("--task-file", default="", help="Compiled browser task json path.")
    parser.add_argument("--deterministic-command", default="", help="Current deterministic project command.")
    parser.add_argument("--explicit-project-command", default="", help="Alias for --deterministic-command.")
    parser.add_argument("--fallback-cmd", default="", help="Compatibility alias for --deterministic-command.")
    parser.add_argument("--project-root", default=".", help="Project root.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    layer_dir_value = str(os.environ.get("BEACON_LAYER_DIR", "")).strip()
    layer_dir = Path(layer_dir_value) if layer_dir_value else None
    task_file = str(args.task_file or os.environ.get("BEACON_BROWSER_TASK_FILE", "")).strip()
    task, task_payload = load_task(str(args.task or ""), task_file)
    deterministic_command, fallback_cmd, compat_alias_used = _resolve_deterministic_command(args)
    browser_agent_available = False
    command_label = "compatibility alias --fallback-cmd" if compat_alias_used else "deterministic command"

    if not task:
        if deterministic_command:
            print(f"[agent-browser-adapter] no task configured, {command_label}: {deterministic_command}")
            write_runner_artifacts(
                layer_dir=layer_dir,
                project_root=project_root,
                runner="agent-browser",
                task_file=task_file,
                task_text="",
                task_payload=task_payload,
                mode=args.mode,
                status="deterministic-command-no-task",
                fallback_cmd=fallback_cmd,
                deterministic_command=deterministic_command,
                compat_alias_used=compat_alias_used,
                browser_agent_available=browser_agent_available,
                browser_agent_executed=False,
                reason_code="browser_task_missing_deterministic_command_executed",
                repair_route="provide_browser_task",
            )
            return _run_deterministic_command(deterministic_command, cwd=project_root)
        print(
            "[agent-browser-adapter] task missing and no --deterministic-command provided. "
            "Set --task/--task-file or provide deterministic command."
        )
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
            deterministic_command=deterministic_command,
            compat_alias_used=compat_alias_used,
            browser_agent_available=browser_agent_available,
            browser_agent_executed=False,
            reason_code="browser_task_missing_deterministic_command_missing",
            repair_route="provide_browser_task_and_deterministic_command",
        )
        return 2

    # Beacon keeps this adapter deterministic by preferring project-provided commands.
    if deterministic_command:
        print(f"[agent-browser-adapter] task accepted ({args.mode})")
        write_runner_artifacts(
            layer_dir=layer_dir,
            project_root=project_root,
            runner="agent-browser",
            task_file=task_file,
            task_text=task,
            task_payload=task_payload,
            mode=args.mode,
            status="deterministic-command-executed",
            fallback_cmd=fallback_cmd,
            deterministic_command=deterministic_command,
            compat_alias_used=compat_alias_used,
            browser_agent_available=browser_agent_available,
            browser_agent_executed=False,
            reason_code="browser_agent_not_executed_deterministic_command_executed",
            repair_route="configure_browser_agent_execution_to_claim_browser_success",
        )
        return _run_deterministic_command(deterministic_command, cwd=project_root)

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
        deterministic_command=deterministic_command,
        compat_alias_used=compat_alias_used,
        browser_agent_available=browser_agent_available,
        browser_agent_executed=False,
        reason_code="browser_task_present_deterministic_command_missing",
        repair_route="configure_deterministic_command_or_project_browser_executor",
    )
    print(
        "[agent-browser-adapter] task configured but no deterministic command or project browser executor provided. "
        f"task={task}"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
