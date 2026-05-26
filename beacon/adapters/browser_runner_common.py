"""Shared helpers for browser-native Beacon runner adapters."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _relative_ref(project_root: Path, value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    path = Path(raw)
    if path.is_absolute():
        try:
            return str(path.relative_to(project_root))
        except ValueError:
            return raw
    return raw


def _absolute_ref(project_root: Path, value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    path = Path(raw)
    return str(path if path.is_absolute() else (project_root / path))


def load_task(raw_task: str, task_file: str) -> tuple[str, dict[str, Any]]:
    direct = str(raw_task or "").strip()
    if direct:
        return direct, {}
    file_value = str(task_file or os.environ.get("BEACON_BROWSER_TASK_FILE", "")).strip()
    if not file_value:
        return "", {}
    path = Path(file_value)
    if not path.exists():
        return "", {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return path.read_text(encoding="utf-8", errors="ignore").strip(), {}
    if isinstance(payload, dict):
        text = str(payload.get("instruction") or payload.get("title") or payload.get("assertion") or "").strip()
        return text, payload
    return "", {}


def load_session(project_root: Path, task_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    task_session = task_payload.get("session") if isinstance(task_payload, dict) and isinstance(task_payload.get("session"), dict) else {}
    scopes = task_session.get("scopes") if isinstance(task_session.get("scopes"), list) else []
    if not scopes:
        env_scopes = str(os.environ.get("BEACON_BROWSER_SESSION_SCOPES", "")).strip()
        if env_scopes:
            scopes = [item.strip() for item in env_scopes.split(",") if item.strip()]
    session = {
        "session_id": str(os.environ.get("BEACON_BROWSER_SESSION_ID", "") or task_session.get("session_id") or "").strip(),
        "runner_type": str(os.environ.get("BEACON_BROWSER_SESSION_RUNNER", "") or task_session.get("runner_type") or "").strip(),
        "origin": str(os.environ.get("BEACON_BROWSER_ORIGIN", "") or task_session.get("origin") or "").strip(),
        "manifest_ref": _relative_ref(project_root, str(os.environ.get("BEACON_BROWSER_SESSION_MANIFEST", "") or task_session.get("manifest_ref") or "")),
        "manifest_path": _absolute_ref(project_root, str(os.environ.get("BEACON_BROWSER_SESSION_MANIFEST", "") or task_session.get("manifest_ref") or "")),
        "profile_ref": _relative_ref(project_root, str(os.environ.get("BEACON_BROWSER_PROFILE_REF", "") or task_session.get("profile_ref") or "")),
        "profile_path": _absolute_ref(project_root, str(os.environ.get("BEACON_BROWSER_PROFILE_REF", "") or task_session.get("profile_ref") or "")),
        "cookies_ref": _relative_ref(project_root, str(os.environ.get("BEACON_BROWSER_COOKIES_REF", "") or task_session.get("cookies_ref") or "")),
        "cookies_path": _absolute_ref(project_root, str(os.environ.get("BEACON_BROWSER_COOKIES_REF", "") or task_session.get("cookies_ref") or "")),
        "storage_state_ref": _relative_ref(project_root, str(os.environ.get("BEACON_BROWSER_STORAGE_STATE_REF", "") or task_session.get("storage_state_ref") or "")),
        "storage_state_path": _absolute_ref(project_root, str(os.environ.get("BEACON_BROWSER_STORAGE_STATE_REF", "") or task_session.get("storage_state_ref") or "")),
        "scopes": scopes,
    }
    return {
        key: value
        for key, value in session.items()
        if value is not None and value != "" and value != []
    }


def write_runner_artifacts(
    *,
    layer_dir: Path | None,
    project_root: Path,
    runner: str,
    task_file: str,
    task_text: str,
    task_payload: dict[str, Any] | None,
    mode: str,
    status: str,
    fallback_cmd: str,
    deterministic_command: str = "",
    compat_alias_used: bool = False,
    browser_agent_available: bool = False,
    browser_agent_executed: bool = False,
    reason_code: str = "",
    repair_route: str = "",
) -> None:
    if not isinstance(layer_dir, Path):
        return
    payload = task_payload if isinstance(task_payload, dict) else {}
    session = load_session(project_root, payload)
    layer_dir.mkdir(parents=True, exist_ok=True)

    task_ref = ""
    if task_file:
        task_src = Path(task_file)
        if task_src.exists():
            task_copy = layer_dir / "browser-runner-task.json"
            task_copy.write_text(task_src.read_text(encoding="utf-8"), encoding="utf-8")
            task_ref = _relative_ref(project_root, str(task_copy))

    target_url = str(payload.get("target_url") or session.get("origin") or "/").strip() or "/"
    steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []
    actions = [
        {
            "step_id": index,
            "kind": str(step.get("kind") or "action"),
            "target": str(step.get("target") or ""),
            "status": "captured",
        }
        for index, step in enumerate(steps, start=1)
        if isinstance(step, dict)
    ]
    if not actions and task_text:
        actions = [{"step_id": 1, "kind": "task", "target": task_text, "status": "captured"}]

    url_path = layer_dir / "current-url.txt"
    url_path.write_text(target_url + "\n", encoding="utf-8")
    transcript_path = layer_dir / "action-transcript.json"
    transcript_payload = {
        "schema_version": "1.0",
        "runner": runner,
        "mode": mode,
        "status": status,
        "task": task_text,
        "target_url": target_url,
        "session": session,
        "actions": actions,
        "generated_at": datetime.now().isoformat(),
    }
    transcript_path.write_text(json.dumps(transcript_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    dom_path = layer_dir / "dom-snapshot.json"
    dom_path.write_text(
        json.dumps(
            {
                "runner": runner,
                "mode": mode,
                "status": status,
                "target_url": target_url,
                "session_id": str(session.get("session_id") or ""),
                "scenario_id": str(payload.get("scenario_id") or ""),
                "tc_id": str(payload.get("tc_id") or ""),
                "generated_at": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    network_path = layer_dir / "network-summary.json"
    network_path.write_text(
        json.dumps(
            {
                "runner": runner,
                "mode": mode,
                "status": status,
                "target_url": target_url,
                "requests": [{"method": "GET", "url": target_url}] if target_url and target_url != "/" else [],
                "generated_at": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    command = str(deterministic_command or fallback_cmd or "").strip()
    execution_mode = "deterministic_command" if command else "task-only"
    deterministic_command_configured = bool(command)
    deterministic_command_executed = bool(command) and str(status or "").strip() in {
        "deterministic-command-executed",
        "fallback-executed",
        "fallback-browser-use-unavailable",
        "fallback-no-task",
        "deterministic-command-browser-use-unavailable",
        "deterministic-command-no-task",
    }
    compat_id = "browser-fallback-command-name" if compat_alias_used else ""
    resolved_reason_code = str(reason_code or "").strip()
    if not resolved_reason_code:
        if deterministic_command_executed and not browser_agent_executed:
            resolved_reason_code = "browser_agent_unavailable_deterministic_command_executed"
        elif not command and not browser_agent_executed:
            resolved_reason_code = "browser_agent_unavailable_deterministic_command_missing"
        else:
            resolved_reason_code = "browser_agent_execution_recorded"
    resolved_repair_route = str(repair_route or "").strip()
    if not resolved_repair_route:
        resolved_repair_route = (
            "configure_browser_agent_runtime_and_deterministic_command"
            if not browser_agent_available and not command
            else "configure_browser_agent_runtime"
            if not browser_agent_available
            else "configure_deterministic_command"
            if not command
            else "none"
        )
    browser_agent_repair_route = "configure_browser_agent_runtime" if not browser_agent_available else "none"
    deterministic_command_repair_route = "configure_deterministic_command" if not command else "none"

    console_path = layer_dir / "browser-runner-console.log"
    console_path.write_text(
        "\n".join(
            [
                f"runner={runner}",
                f"mode={mode}",
                f"status={status}",
                f"target_url={target_url}",
                f"session_id={session.get('session_id', '')}",
                f"execution_mode={execution_mode}",
                f"browser_agent_available={str(bool(browser_agent_available)).lower()}",
                f"browser_agent_executed={str(bool(browser_agent_executed)).lower()}",
                f"deterministic_command_configured={str(deterministic_command_configured).lower()}",
                f"deterministic_command_executed={str(deterministic_command_executed).lower()}",
                f"compat_alias_used={str(bool(compat_alias_used)).lower()}",
                f"compat_id={compat_id}",
                f"reason_code={resolved_reason_code}",
                f"repair_route={resolved_repair_route}",
                f"browser_agent_repair_route={browser_agent_repair_route}",
                f"deterministic_command_repair_route={deterministic_command_repair_route}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    artifact_refs = {
        "task_ref": task_ref,
        "url_ref": _relative_ref(project_root, str(url_path)),
        "transcript_ref": _relative_ref(project_root, str(transcript_path)),
        "dom_ref": _relative_ref(project_root, str(dom_path)),
        "network_ref": _relative_ref(project_root, str(network_path)),
        "console_ref": _relative_ref(project_root, str(console_path)),
        "session_manifest_ref": str(session.get("manifest_ref") or ""),
        "profile_ref": str(session.get("profile_ref") or ""),
        "cookies_ref": str(session.get("cookies_ref") or ""),
        "storage_state_ref": str(session.get("storage_state_ref") or ""),
    }

    report_payload = {
        "schema_version": "1.0",
        "runner": runner,
        "mode": mode,
        "status": status,
        "task": task_text,
        "task_file": task_file,
        "feature": str(payload.get("feature") or ""),
        "tc_id": str(payload.get("tc_id") or ""),
        "scenario_id": str(payload.get("scenario_id") or ""),
        "scenario_family": str(payload.get("scenario_family") or ""),
        "target_url": target_url,
        "fallback_cmd": fallback_cmd,
        "deterministic_command": command,
        "execution_mode": execution_mode,
        "browser_agent_requested": True,
        "browser_agent_available": bool(browser_agent_available),
        "browser_agent_executed": bool(browser_agent_executed),
        "deterministic_command_configured": deterministic_command_configured,
        "deterministic_command_executed": deterministic_command_executed,
        "compat_alias_used": bool(compat_alias_used),
        "compat_id": compat_id,
        "reason_code": resolved_reason_code,
        "repair_route": resolved_repair_route,
        "browser_agent_repair_route": browser_agent_repair_route,
        "deterministic_command_repair_route": deterministic_command_repair_route,
        "session": session,
        "actions": actions,
        "artifact_refs": {key: value for key, value in artifact_refs.items() if value},
        "generated_at": datetime.now().isoformat(),
    }
    (layer_dir / "browser-runner-report.json").write_text(
        json.dumps(report_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (layer_dir / "browser-runner-meta.json").write_text(
        json.dumps(
            {
                "runner": runner,
                "mode": mode,
                "status": status,
                "task": task_text,
                "fallback_cmd": fallback_cmd,
                "deterministic_command": command,
                "execution_mode": execution_mode,
                "browser_agent_requested": True,
                "browser_agent_available": bool(browser_agent_available),
                "browser_agent_executed": bool(browser_agent_executed),
                "deterministic_command_configured": deterministic_command_configured,
                "deterministic_command_executed": deterministic_command_executed,
                "compat_alias_used": bool(compat_alias_used),
                "compat_id": compat_id,
                "reason_code": resolved_reason_code,
                "repair_route": resolved_repair_route,
                "browser_agent_repair_route": browser_agent_repair_route,
                "deterministic_command_repair_route": deterministic_command_repair_route,
                "target_url": target_url,
                "session": session,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (layer_dir / "browser-runner-result.json").write_text(
        json.dumps(
            {
                "runner": runner,
                "mode": mode,
                "status": status,
                "task": task_text,
                "execution_mode": execution_mode,
                "browser_agent_requested": True,
                "browser_agent_available": bool(browser_agent_available),
                "browser_agent_executed": bool(browser_agent_executed),
                "deterministic_command_configured": deterministic_command_configured,
                "deterministic_command_executed": deterministic_command_executed,
                "compat_alias_used": bool(compat_alias_used),
                "compat_id": compat_id,
                "reason_code": resolved_reason_code,
                "repair_route": resolved_repair_route,
                "browser_agent_repair_route": browser_agent_repair_route,
                "deterministic_command_repair_route": deterministic_command_repair_route,
                "artifact_refs": {key: value for key, value in artifact_refs.items() if value},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
