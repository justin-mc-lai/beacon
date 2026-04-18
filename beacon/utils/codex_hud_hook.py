"""Doctor-managed Codex fixed HUD hook wiring helpers."""

from __future__ import annotations

import json
import shlex
import stat
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict


HUD_HOOK_PLUGIN_NAME = "beacon-fixed-hud"
HUD_HOOK_SUPPORTED_EVENTS = ("UserPromptSubmit", "SessionStart", "SessionResume", "SessionRefresh")
HUD_HOOK_ACTIVATION_SOURCE_ENV = "BEACON_CODEX_HUD_ACTIVATION_SOURCE"
HUD_HOOK_TRUSTED_ACTIVATION_SOURCE = "doctor-managed-dispatch"
DOCTOR_MANAGED_MARKER = "# beacon-doctor-managed: true"
DOCTOR_PROJECT_MARKER = "# beacon-doctor-project-root: "
DOCTOR_VERSION_MARKER = "# beacon-doctor-version: "


class CodexHudHookSetupResult(TypedDict):
    mode: str
    plugin_root: str
    events: list[str]
    files: dict[str, str]
    actions: list[dict[str, str]]
    diagnostics_path: str
    restart_required: bool


class CodexHudHookVerifyResult(TypedDict):
    status: str
    plugin_root: str
    events: list[str]
    checks: list[dict[str, Any]]
    runtime: dict[str, Any]
    diagnostics_path: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def codex_hud_hook_root(project_root: Path) -> Path:
    return project_root / "plugins" / HUD_HOOK_PLUGIN_NAME


def _marketplace_path(project_root: Path) -> Path:
    return project_root / ".agents" / "plugins" / "marketplace.json"


def _plugin_json_path(project_root: Path) -> Path:
    return codex_hud_hook_root(project_root) / ".codex-plugin" / "plugin.json"


def _hooks_json_path(project_root: Path) -> Path:
    return codex_hud_hook_root(project_root) / "hooks.json"


def _dispatch_script_path(project_root: Path) -> Path:
    return codex_hud_hook_root(project_root) / "scripts" / "dispatch.sh"


def _install_doc_path(project_root: Path) -> Path:
    return codex_hud_hook_root(project_root) / "INSTALL.md"


def _user_scope_plugin_root() -> Path:
    return Path.home() / ".codex" / HUD_HOOK_PLUGIN_NAME


def _diagnostics_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "hud-hook"


def _runtime_activation_state_path(project_root: Path) -> Path:
    return _diagnostics_root(project_root) / "runtime-activation.json"


def _runtime_activation_log_path(project_root: Path) -> Path:
    return _diagnostics_root(project_root) / "runtime-activation.jsonl"


def _display_path(path: Path, *, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _normalize_events(events: str | list[str] | tuple[str, ...] | None) -> list[str]:
    raw_items: list[str]
    if isinstance(events, str):
        raw_items = [item.strip() for item in events.split(",")]
    elif isinstance(events, (list, tuple)):
        raw_items = [str(item).strip() for item in events]
    else:
        raw_items = list(HUD_HOOK_SUPPORTED_EVENTS)

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        if not item:
            continue
        if item not in HUD_HOOK_SUPPORTED_EVENTS:
            supported = ", ".join(HUD_HOOK_SUPPORTED_EVENTS)
            raise ValueError(f"unsupported Codex HUD hook event '{item}' (supported: {supported})")
        if item not in seen:
            normalized.append(item)
            seen.add(item)

    if not normalized:
        return list(HUD_HOOK_SUPPORTED_EVENTS)
    return normalized


def _hook_matcher(event_name: str) -> str:
    if event_name == "SessionStart":
        return "startup|resume|refresh|compact"
    return "*"


def _dispatch_command(project_root: Path, *, version: str) -> str:
    repo_root = Path(__file__).resolve().parents[2]
    launcher = repo_root / "skills" / "beacon" / "scripts" / "run_beacon.sh"
    if launcher.exists():
        return (
            f"bash {shlex.quote(str(launcher))} "
            f"debug codex-fixed-hud --project-root {shlex.quote(str(project_root))} "
            f"--version {shlex.quote(version)} --json"
        )
    return (
        "python3 -m beacon.main "
        f"debug codex-fixed-hud --project-root {shlex.quote(str(project_root))} "
        f"--version {shlex.quote(version)} --json"
    )


def _plugin_json(version: str, *, project_root: Path) -> str:
    payload = {
        "name": HUD_HOOK_PLUGIN_NAME,
        "version": str(version or "v1.0.0").lstrip("v"),
        "description": (
            "Doctor-managed Beacon fixed HUD hook wiring for Codex. "
            "Injects 1-3 line HUD context through hookSpecificOutput.additionalContext."
        ),
        "author": {"name": "Beacon CLI"},
        "homepage": "https://github.com/tiann/beacon",
        "repository": "https://github.com/tiann/beacon",
        "license": "MIT",
        "hooks": "./hooks.json",
        "keywords": [
            "beacon",
            "codex",
            "hooks",
            "hud",
            "additionalContext",
            str(project_root),
        ],
        "interface": {
            "displayName": "Beacon Fixed HUD",
            "shortDescription": "Inject Beacon minimal HUD context into Codex.",
            "developerName": "Beacon CLI",
            "category": "Coding",
            "capabilities": ["Read"],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _hooks_json(*, dispatch_script: Path, events: list[str]) -> str:
    hooks: dict[str, list[dict[str, Any]]] = {}
    command = f"bash {shlex.quote(str(dispatch_script))}"
    for event_name in events:
        hooks[event_name] = [
            {
                "matcher": _hook_matcher(event_name),
                "hooks": [
                    {
                        "type": "command",
                        "command": command,
                        "timeout": 10,
                    }
                ],
            }
        ]
    payload = {
        "description": "Beacon v1.3.3 fixed HUD hook wiring for Codex",
        "hooks": hooks,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _dispatch_script(project_root: Path, *, version: str) -> str:
    command = _dispatch_command(project_root, version=version)
    return (
        "#!/usr/bin/env bash\n"
        f"{DOCTOR_MANAGED_MARKER}\n"
        f"{DOCTOR_PROJECT_MARKER}{project_root}\n"
        f"{DOCTOR_VERSION_MARKER}{version}\n"
        "set -euo pipefail\n"
        f'export {HUD_HOOK_ACTIVATION_SOURCE_ENV}="{HUD_HOOK_TRUSTED_ACTIVATION_SOURCE}"\n'
        f"exec {command}\n"
    )


def _install_doc(project_root: Path, *, version: str, events: list[str]) -> str:
    event_text = ", ".join(events)
    return (
        "# Beacon Codex Fixed HUD Hook\n\n"
        "This installation was generated by `beacon doctor setup-codex-hud-hook`.\n\n"
        f"- project_root: `{project_root}`\n"
        f"- version: `{version}`\n"
        f"- events: `{event_text}`\n\n"
        "Restart Codex after applying or changing this wiring.\n"
        "After restart, trigger one of the configured hook events before expecting runtime activation proof.\n"
    )


def _marketplace_entry() -> dict[str, Any]:
    return {
        "name": HUD_HOOK_PLUGIN_NAME,
        "source": {
            "source": "local",
            "path": f"./plugins/{HUD_HOOK_PLUGIN_NAME}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Coding",
    }


def _render_marketplace(existing: dict[str, Any] | None) -> str:
    payload = deepcopy(existing) if isinstance(existing, dict) else {}
    if not isinstance(payload.get("interface"), dict):
        payload["interface"] = {"displayName": "Workspace Plugins"}
    payload["name"] = str(payload.get("name") or "workspace-local")

    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        plugins = []

    entry = _marketplace_entry()
    updated = False
    merged_plugins: list[dict[str, Any]] = []
    for item in plugins:
        if isinstance(item, dict) and str(item.get("name") or "") == HUD_HOOK_PLUGIN_NAME:
            merged_plugins.append(entry)
            updated = True
        elif isinstance(item, dict):
            merged_plugins.append(item)
    if not updated:
        merged_plugins.append(entry)
    payload["plugins"] = merged_plugins
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _write_file(path: Path, content: str, *, executable: bool = False) -> str:
    action = "created"
    if path.exists():
        try:
            current = path.read_text(encoding="utf-8")
        except OSError:
            current = ""
        if current == content:
            action = "unchanged"
        else:
            action = "updated"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return action


def _write_diagnostics(project_root: Path, *, name: str, payload: dict[str, Any]) -> Path:
    target = _diagnostics_root(project_root) / f"{name}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _parse_iso_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _wiring_change_reference(*, paths: list[Path]) -> tuple[str, str]:
    latest_ts: datetime | None = None
    latest_path = ""
    for path in paths:
        if not path.exists():
            continue
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if latest_ts is None or mtime > latest_ts:
            latest_ts = mtime
            latest_path = str(path)
    return (latest_ts.isoformat() if latest_ts else "", latest_path)


def _append_user_scope_shadow_checks(
    checks: list[dict[str, Any]],
    *,
    project_root: Path,
    version: str,
    normalized_events: list[str],
) -> None:
    user_plugin_root = _user_scope_plugin_root().expanduser()
    try:
        same_location = user_plugin_root.resolve() == codex_hud_hook_root(project_root).resolve()
    except OSError:
        same_location = False
    if same_location or not user_plugin_root.exists():
        return

    hooks_json_path = user_plugin_root / "hooks" / "hooks.json"
    dispatch_script_path = user_plugin_root / "hooks" / "dispatch.sh"
    install_doc_path = user_plugin_root / ".codex" / "INSTALL.md"

    checks.append(
        {
            "name": "user_scope_plugin_hooks_json_exists",
            "ok": hooks_json_path.exists(),
            "detail": str(hooks_json_path),
            "required": False,
        }
    )
    if hooks_json_path.exists():
        try:
            hooks_payload = json.loads(hooks_json_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            checks.append(
                {
                    "name": "user_scope_plugin_hooks_json_parse",
                    "ok": False,
                    "detail": str(exc),
                    "required": False,
                }
            )
        else:
            hook_map = hooks_payload.get("hooks") if isinstance(hooks_payload.get("hooks"), dict) else {}
            checks.append(
                {
                    "name": "user_scope_plugin_events_wired",
                    "ok": all(event_name in hook_map for event_name in normalized_events),
                    "detail": ",".join(sorted(str(key) for key in hook_map.keys())),
                    "required": False,
                }
            )

    checks.append(
        {
            "name": "user_scope_plugin_dispatch_script_exists",
            "ok": dispatch_script_path.exists(),
            "detail": str(dispatch_script_path),
            "required": False,
        }
    )
    if dispatch_script_path.exists():
        dispatch_text = dispatch_script_path.read_text(encoding="utf-8")
        checks.extend(
            [
                {
                    "name": "user_scope_plugin_dispatch_targets_project",
                    "ok": (
                        f"{DOCTOR_PROJECT_MARKER}{project_root}" in dispatch_text
                        or f"--project-root {shlex.quote(str(project_root))}" in dispatch_text
                    ),
                    "detail": str(project_root),
                    "required": False,
                },
                {
                    "name": "user_scope_plugin_dispatch_version_matches",
                    "ok": (
                        f"{DOCTOR_VERSION_MARKER}{version}" in dispatch_text
                        or f"--version {shlex.quote(version)}" in dispatch_text
                    ),
                    "detail": version,
                    "required": False,
                },
                {
                    "name": "user_scope_plugin_dispatch_activation_source_export",
                    "ok": (
                        f'export {HUD_HOOK_ACTIVATION_SOURCE_ENV}="{HUD_HOOK_TRUSTED_ACTIVATION_SOURCE}"'
                        in dispatch_text
                    ),
                    "detail": HUD_HOOK_TRUSTED_ACTIVATION_SOURCE,
                    "required": False,
                },
            ]
        )

    checks.append(
        {
            "name": "user_scope_plugin_install_doc_exists",
            "ok": install_doc_path.exists(),
            "detail": str(install_doc_path),
            "required": False,
        }
    )
    if install_doc_path.exists():
        install_doc_text = install_doc_path.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "user_scope_plugin_install_doc_targets_project",
                "ok": f"- project_root: `{project_root}`" in install_doc_text,
                "detail": str(project_root),
                "required": False,
            }
        )


def record_codex_hud_hook_activation(
    project_root: Path,
    *,
    hook_event_name: str,
    payload: dict[str, Any],
    feature: str,
    version: str,
    status: str,
    reason: str,
    activation_source: str,
    additional_context: str,
    minimal_hud: dict[str, Any],
) -> dict[str, Any]:
    project_root = project_root.resolve()
    lines = minimal_hud.get("lines") if isinstance(minimal_hud.get("lines"), list) else []
    trusted_source = activation_source == HUD_HOOK_TRUSTED_ACTIVATION_SOURCE
    record = {
        "schema_version": "1.0",
        "generated_at": _utc_now(),
        "hook_event_name": str(hook_event_name or "").strip(),
        "session_id": str(payload.get("session_id", payload.get("sessionId", "")) or ""),
        "thread_id": str(payload.get("thread_id", payload.get("threadId", "")) or ""),
        "turn_id": str(payload.get("turn_id", payload.get("turnId", "")) or ""),
        "transcript_path": str(payload.get("transcript_path", payload.get("transcriptPath", "")) or ""),
        "feature": str(feature or "").strip(),
        "version": str(version or "").strip(),
        "status": str(status or "").strip() or "unknown",
        "reason": str(reason or "").strip(),
        "activation_source": str(activation_source or "").strip() or "manual",
        "trusted_source": trusted_source,
        "additional_context_present": bool(str(additional_context or "").strip()),
        "minimal_hud_scenario": str(minimal_hud.get("scenario", "") or ""),
        "minimal_hud_line_count": len(lines),
    }
    state_path = _runtime_activation_state_path(project_root)
    log_path = _runtime_activation_log_path(project_root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _append_jsonl(log_path, record)
    return {
        "record": record,
        "state_path": _display_path(state_path, project_root=project_root),
        "log_path": _display_path(log_path, project_root=project_root),
    }


def setup_codex_hud_hook(
    project_root: Path,
    *,
    version: str,
    apply: bool,
    events: str | list[str] | tuple[str, ...] | None = None,
) -> CodexHudHookSetupResult:
    project_root = project_root.resolve()
    normalized_events = _normalize_events(events)
    plugin_root = codex_hud_hook_root(project_root)
    marketplace_path = _marketplace_path(project_root)
    plugin_json_path = _plugin_json_path(project_root)
    hooks_json_path = _hooks_json_path(project_root)
    dispatch_script_path = _dispatch_script_path(project_root)
    install_doc_path = _install_doc_path(project_root)

    existing_marketplace: dict[str, Any] | None = None
    if marketplace_path.exists():
        try:
            loaded = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            loaded = None
        if isinstance(loaded, dict):
            existing_marketplace = loaded

    files = {
        "marketplace_json": _display_path(marketplace_path, project_root=project_root),
        "plugin_json": _display_path(plugin_json_path, project_root=project_root),
        "hooks_json": _display_path(hooks_json_path, project_root=project_root),
        "dispatch_script": _display_path(dispatch_script_path, project_root=project_root),
        "install_doc": _display_path(install_doc_path, project_root=project_root),
    }
    rendered = {
        marketplace_path: _render_marketplace(existing_marketplace),
        plugin_json_path: _plugin_json(version, project_root=project_root),
        hooks_json_path: _hooks_json(dispatch_script=dispatch_script_path, events=normalized_events),
        dispatch_script_path: _dispatch_script(project_root, version=version),
        install_doc_path: _install_doc(project_root, version=version, events=normalized_events),
    }

    actions: list[dict[str, str]] = []
    mode = "apply" if apply else "dry-run"
    if apply:
        for path, content in rendered.items():
            action = _write_file(path, content, executable=path == dispatch_script_path)
            actions.append({"path": _display_path(path, project_root=project_root), "action": action})
    else:
        for path in rendered:
            actions.append(
                {
                    "path": _display_path(path, project_root=project_root),
                    "action": "planned" if not path.exists() else "would_update",
                }
            )

    diagnostics_payload = {
        "schema_version": "1.0",
        "generated_at": _utc_now(),
        "mode": mode,
        "plugin_root": _display_path(plugin_root, project_root=project_root),
        "project_root": str(project_root),
        "version": version,
        "events": normalized_events,
        "files": files,
        "actions": actions,
    }
    diagnostics_path = _write_diagnostics(project_root, name="setup-codex-hud-hook", payload=diagnostics_payload)
    return {
        "mode": mode,
        "plugin_root": _display_path(plugin_root, project_root=project_root),
        "events": normalized_events,
        "files": files,
        "actions": actions,
        "diagnostics_path": str(diagnostics_path.relative_to(project_root)),
        "restart_required": bool(apply),
    }


def verify_codex_hud_hook(
    project_root: Path,
    *,
    version: str,
    events: str | list[str] | tuple[str, ...] | None = None,
) -> CodexHudHookVerifyResult:
    project_root = project_root.resolve()
    normalized_events = _normalize_events(events)
    checks: list[dict[str, Any]] = []

    plugin_root = codex_hud_hook_root(project_root)
    marketplace_path = _marketplace_path(project_root)
    plugin_json_path = _plugin_json_path(project_root)
    hooks_json_path = _hooks_json_path(project_root)
    dispatch_script_path = _dispatch_script_path(project_root)
    install_doc_path = _install_doc_path(project_root)
    runtime_activation_path = _runtime_activation_state_path(project_root)

    plugin_root_ok = plugin_root.exists()
    checks.append(
        {
            "name": "plugin_root_exists",
            "ok": plugin_root_ok,
            "detail": _display_path(plugin_root, project_root=project_root),
        }
    )

    marketplace_ok = marketplace_path.exists()
    checks.append(
        {
            "name": "marketplace_json_exists",
            "ok": marketplace_ok,
            "detail": _display_path(marketplace_path, project_root=project_root),
        }
    )

    plugin_ok = plugin_json_path.exists()
    checks.append(
        {
            "name": "plugin_json_exists",
            "ok": plugin_ok,
            "detail": _display_path(plugin_json_path, project_root=project_root),
        }
    )

    hooks_ok = hooks_json_path.exists()
    checks.append(
        {
            "name": "hooks_json_exists",
            "ok": hooks_ok,
            "detail": _display_path(hooks_json_path, project_root=project_root),
        }
    )

    dispatch_ok = dispatch_script_path.exists()
    checks.append(
        {
            "name": "dispatch_script_exists",
            "ok": dispatch_ok,
            "detail": _display_path(dispatch_script_path, project_root=project_root),
        }
    )

    install_ok = install_doc_path.exists()
    checks.append(
        {
            "name": "install_doc_exists",
            "ok": install_ok,
            "detail": _display_path(install_doc_path, project_root=project_root),
        }
    )

    if marketplace_ok:
        try:
            marketplace_payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            checks.append({"name": "marketplace_json_parse", "ok": False, "detail": str(exc)})
        else:
            plugins = marketplace_payload.get("plugins")
            plugin_entries = plugins if isinstance(plugins, list) else []
            target_entry = next(
                (
                    item
                    for item in plugin_entries
                    if isinstance(item, dict) and str(item.get("name") or "") == HUD_HOOK_PLUGIN_NAME
                ),
                None,
            )
            checks.append(
                {
                    "name": "marketplace_entry_present",
                    "ok": isinstance(target_entry, dict),
                    "detail": HUD_HOOK_PLUGIN_NAME,
                }
            )
            if isinstance(target_entry, dict):
                source = target_entry.get("source") if isinstance(target_entry.get("source"), dict) else {}
                checks.append(
                    {
                        "name": "marketplace_source_path",
                        "ok": str(source.get("path") or "") == f"./plugins/{HUD_HOOK_PLUGIN_NAME}",
                        "detail": str(source.get("path") or ""),
                    }
                )

    if plugin_ok:
        try:
            plugin_payload = json.loads(plugin_json_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            checks.append({"name": "plugin_json_parse", "ok": False, "detail": str(exc)})
        else:
            checks.append(
                {
                    "name": "plugin_name_match",
                    "ok": str(plugin_payload.get("name", "") or "") == HUD_HOOK_PLUGIN_NAME,
                    "detail": str(plugin_payload.get("name", "") or ""),
                }
            )
            checks.append(
                {
                    "name": "plugin_hooks_pointer",
                    "ok": str(plugin_payload.get("hooks", "") or "") == "./hooks.json",
                    "detail": str(plugin_payload.get("hooks", "") or ""),
                }
            )

    if hooks_ok:
        try:
            hooks_payload = json.loads(hooks_json_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            checks.append({"name": "hooks_json_parse", "ok": False, "detail": str(exc)})
        else:
            hook_map = hooks_payload.get("hooks") if isinstance(hooks_payload.get("hooks"), dict) else {}
            wired_events = sorted(str(key) for key in hook_map.keys())
            checks.append(
                {
                    "name": "events_wired",
                    "ok": all(event_name in hook_map for event_name in normalized_events),
                    "detail": ",".join(wired_events),
                }
            )

    if dispatch_ok:
        dispatch_text = dispatch_script_path.read_text(encoding="utf-8")
        checks.extend(
            [
                {
                    "name": "dispatch_managed_marker",
                    "ok": DOCTOR_MANAGED_MARKER in dispatch_text,
                    "detail": DOCTOR_MANAGED_MARKER,
                },
                {
                    "name": "dispatch_project_root",
                    "ok": f"{DOCTOR_PROJECT_MARKER}{project_root}" in dispatch_text,
                    "detail": str(project_root),
                },
                {
                    "name": "dispatch_version",
                    "ok": f"{DOCTOR_VERSION_MARKER}{version}" in dispatch_text,
                    "detail": version,
                },
                {
                    "name": "dispatch_activation_source_export",
                    "ok": f'export {HUD_HOOK_ACTIVATION_SOURCE_ENV}="{HUD_HOOK_TRUSTED_ACTIVATION_SOURCE}"' in dispatch_text,
                    "detail": HUD_HOOK_TRUSTED_ACTIVATION_SOURCE,
                },
            ]
        )

    _append_user_scope_shadow_checks(
        checks,
        project_root=project_root,
        version=version,
        normalized_events=normalized_events,
    )

    wiring_paths = [marketplace_path, plugin_json_path, hooks_json_path, dispatch_script_path, install_doc_path]
    latest_wiring_ts, latest_wiring_path = _wiring_change_reference(paths=wiring_paths)
    runtime_payload: dict[str, Any] = {}
    if runtime_activation_path.exists():
        try:
            loaded_runtime = json.loads(runtime_activation_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            checks.append(
                {
                    "name": "runtime_activation_parse",
                    "ok": False,
                    "detail": str(exc),
                    "required": False,
                }
            )
        else:
            if isinstance(loaded_runtime, dict):
                runtime_payload = loaded_runtime

    runtime_generated_at = str(runtime_payload.get("generated_at", "") or "")
    runtime_source = str(runtime_payload.get("activation_source", "") or "")
    runtime_status = str(runtime_payload.get("status", "") or "")
    runtime_context = bool(runtime_payload.get("additional_context_present", False))
    runtime_session_id = str(runtime_payload.get("session_id", "") or "")
    runtime_event = str(runtime_payload.get("hook_event_name", "") or "")
    runtime_ts = _parse_iso_timestamp(runtime_generated_at)
    latest_wiring_dt = _parse_iso_timestamp(latest_wiring_ts)
    trusted_runtime = runtime_source == HUD_HOOK_TRUSTED_ACTIVATION_SOURCE
    captured_runtime = runtime_status == "captured" and runtime_context
    runtime_fresh = bool(runtime_ts and latest_wiring_dt and runtime_ts >= latest_wiring_dt) if latest_wiring_dt else bool(runtime_ts)

    checks.extend(
        [
            {
                "name": "runtime_activation_recorded",
                "ok": bool(runtime_payload),
                "detail": runtime_generated_at or _display_path(runtime_activation_path, project_root=project_root),
                "required": False,
            },
            {
                "name": "runtime_activation_source_trusted",
                "ok": trusted_runtime,
                "detail": runtime_source or "missing",
                "required": False,
            },
            {
                "name": "runtime_activation_captured",
                "ok": captured_runtime,
                "detail": runtime_status or "missing",
                "required": False,
            },
            {
                "name": "runtime_activation_fresh_since_wiring",
                "ok": runtime_fresh,
                "detail": latest_wiring_ts or latest_wiring_path or "unknown",
                "required": False,
            },
        ]
    )

    blocking_failures = [item for item in checks if item.get("required", True) and not bool(item.get("ok"))]
    warning_failures = [item for item in checks if not item.get("required", True) and not bool(item.get("ok"))]
    shadow_failures = [
        item for item in warning_failures if str(item.get("name", "")).startswith("user_scope_plugin_")
    ]
    if blocking_failures:
        status = "blocked"
    elif warning_failures:
        status = "warn"
    else:
        status = "pass"
    diagnostics_payload = {
        "schema_version": "1.0",
        "generated_at": _utc_now(),
        "status": status,
        "plugin_root": _display_path(plugin_root, project_root=project_root),
        "project_root": str(project_root),
        "version": version,
        "events": normalized_events,
        "checks": checks,
        "runtime": {
            "state": (
                "shadow_risk"
                if shadow_failures
                else ("active" if not warning_failures else "activation_unproven")
            ),
            "latest_wiring_changed_at": latest_wiring_ts,
            "latest_wiring_path": _display_path(Path(latest_wiring_path), project_root=project_root) if latest_wiring_path else "",
            "activation_record_path": _display_path(runtime_activation_path, project_root=project_root),
            "last_activation": runtime_payload,
        },
    }
    diagnostics_path = _write_diagnostics(project_root, name="verify-codex-hud-hook", payload=diagnostics_payload)
    return {
        "status": status,
        "plugin_root": _display_path(plugin_root, project_root=project_root),
        "events": normalized_events,
        "checks": checks,
        "runtime": diagnostics_payload["runtime"],
        "diagnostics_path": str(diagnostics_path.relative_to(project_root)),
    }
