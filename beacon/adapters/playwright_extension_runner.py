"""Playwright Chrome extension runner adapter for Beacon QA."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from beacon.adapters.browser_runner_common import load_task, write_runner_artifacts
from beacon.utils.playwright_extension import (
    HEADLESS_NEW_FLAG,
    build_chrome_launch_args,
    extension_page_url,
    popup_url,
    validate_extension_runner_context,
)


def _resolve_extension_path(args: argparse.Namespace, task_payload: dict) -> str:
    return str(
        args.extension_path
        or os.environ.get("BEACON_EXTENSION_PATH", "")
        or task_payload.get("extension_path")
        or task_payload.get("load_extension")
        or ""
    ).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", default="functional", choices=["functional", "compatibility"])
    parser.add_argument("--task", default="", help="Natural language task.")
    parser.add_argument("--task-file", default="", help="Compiled browser task json path.")
    parser.add_argument("--extension-path", default="", help="Chrome extension unpacked directory.")
    parser.add_argument("--expected-extension-id", default="", help="Expected fixed extension id.")
    parser.add_argument("--project-root", default=".", help="Project root.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    layer_dir_value = str(os.environ.get("BEACON_LAYER_DIR", "")).strip()
    layer_dir = Path(layer_dir_value) if layer_dir_value else None
    task_file = str(args.task_file or os.environ.get("BEACON_BROWSER_TASK_FILE", "")).strip()
    task, task_payload = load_task(str(args.task or ""), task_file)
    extension_path = _resolve_extension_path(args, task_payload if isinstance(task_payload, dict) else {})
    context = validate_extension_runner_context(
        extension_path=extension_path,
        expected_extension_id=str(args.expected_extension_id or "").strip(),
        service_worker_ready=bool(os.environ.get("BEACON_EXTENSION_SW_READY", "1") not in {"0", "false", "False"}),
    )
    launch_args = list(context.get("launch_args") or build_chrome_launch_args(extension_path=extension_path))
    if HEADLESS_NEW_FLAG not in launch_args and "--headless" in launch_args:
        launch_args = [arg for arg in launch_args if arg != "--headless"]
        launch_args.append(HEADLESS_NEW_FLAG)

    if context.get("blocked"):
        write_runner_artifacts(
            layer_dir=layer_dir,
            project_root=project_root,
            runner="playwright-extension",
            task_file=task_file,
            task_text=task,
            task_payload=task_payload if isinstance(task_payload, dict) else {},
            mode=args.mode,
            status="extension-blocked",
            fallback_cmd="",
            deterministic_command=" ".join(launch_args),
            browser_agent_available=False,
            browser_agent_executed=False,
            reason_code=str(context.get("reason_code") or "extension_load_failed"),
            repair_route="fix_extension_package",
        )
        return 2

    extension_id = str(context.get("extension_id") or "")
    target_url = extension_page_url(extension_id, "index.html")
    popup_target = popup_url(extension_id, tab_id=1)
    write_runner_artifacts(
        layer_dir=layer_dir,
        project_root=project_root,
        runner="playwright-extension",
        task_file=task_file,
        task_text=task or f"extension e2e {target_url}",
        task_payload={
            **(task_payload if isinstance(task_payload, dict) else {}),
            "target_url": target_url,
            "extension_path": extension_path,
            "extension_id": extension_id,
            "popup_url": popup_target,
            "service_worker_ready": True,
            "launch_args": launch_args,
        },
        mode=args.mode,
        status="extension-context-ready",
        fallback_cmd="",
        deterministic_command=" ".join(launch_args),
        browser_agent_available=True,
        browser_agent_executed=False,
        reason_code="extension_context_ready",
        repair_route="none",
    )
    print(json.dumps({"extension_id": extension_id, "target_url": target_url, "popup_url": popup_target, "launch_args": launch_args}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
