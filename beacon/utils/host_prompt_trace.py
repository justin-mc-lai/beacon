"""Structured host prompt trace persistence for v1.3.8."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def host_prompt_trace_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 3, 8)


def host_prompt_trace_json_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return (
        project_root
        / "docs"
        / "beacon"
        / resolved_version
        / ".machine"
        / "execution"
        / f"host-prompt-trace-{feature_slug(feature)}.json"
    )


def host_prompt_trace_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return (
        project_root
        / "docs"
        / "beacon"
        / resolved_version
        / "execution"
        / f"host-prompt-trace-{feature_slug(feature)}.md"
    )


def _normalize_list(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for value in values or []:
        text = str(value or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def _render_markdown(payload: dict[str, Any]) -> str:
    latest = payload.get("latest_event") if isinstance(payload.get("latest_event"), dict) else {}
    lines = [
        "# Host Prompt Trace",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- updated_at: `{payload.get('updated_at', '')}`",
        f"- event_count: `{len(payload.get('events', [])) if isinstance(payload.get('events'), list) else 0}`",
        "",
        "## Latest Event",
        f"- surface: `{latest.get('surface', '')}`",
        f"- route_status: `{latest.get('route_status', '')}`",
        f"- mapped_command: `{latest.get('mapped_command', '')}`",
        f"- freeze_status: `{latest.get('freeze_status', '')}`",
        f"- team_phase: `{latest.get('team_phase', '')}`",
        f"- ralph_phase: `{latest.get('ralph_phase', '')}`",
        f"- next_action: `{latest.get('next_action', '')}`",
        "",
        "## Prompt",
        str(latest.get("original_host_prompt", "") or ""),
        "",
        "## Produced Artifacts",
    ]
    artifacts = latest.get("produced_artifacts") if isinstance(latest.get("produced_artifacts"), list) else []
    if artifacts:
        lines.extend(f"- `{item}`" for item in artifacts)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def load_host_prompt_trace(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    path = host_prompt_trace_json_path(project_root, version, feature)
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def record_host_prompt_trace(
    project_root: Path,
    *,
    version: str,
    feature: str,
    original_host_prompt: str,
    surface: str,
    mapped_command: str,
    produced_artifacts: list[str] | None = None,
    route_status: str,
    run_id: str = "",
    freeze_status: str = "",
    team_phase: str = "",
    ralph_phase: str = "",
    stop_state: str = "",
    next_action: str = "",
    reason_code: str = "",
    execution_sequence: list[str] | None = None,
) -> dict[str, Any]:
    if not host_prompt_trace_supported(version):
        return {}
    prompt = str(original_host_prompt or "").strip()
    if not prompt:
        return {}
    resolved_version = resolve_target_version(project_root, version)
    json_path = host_prompt_trace_json_path(project_root, resolved_version, feature)
    markdown_path = host_prompt_trace_markdown_path(project_root, resolved_version, feature)
    existing = load_host_prompt_trace(project_root, version=resolved_version, feature=feature)
    events = existing.get("events") if isinstance(existing.get("events"), list) else []
    event = {
        "captured_at": now_iso(),
        "run_id": str(run_id or "").strip(),
        "surface": str(surface or "").strip(),
        "original_host_prompt": prompt,
        "mapped_command": str(mapped_command or "").strip(),
        "produced_artifacts": _normalize_list(produced_artifacts),
        "route_status": str(route_status or "").strip(),
        "freeze_status": str(freeze_status or "").strip(),
        "team_phase": str(team_phase or "").strip(),
        "ralph_phase": str(ralph_phase or "").strip(),
        "stop_state": str(stop_state or "").strip(),
        "next_action": str(next_action or "").strip(),
        "reason_code": str(reason_code or "").strip(),
        "execution_sequence": _normalize_list(execution_sequence or []),
    }
    updated_events = [item for item in events if isinstance(item, dict)]
    updated_events.append(event)
    updated_events = updated_events[-20:]
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "updated_at": now_iso(),
        "events": updated_events,
        "latest_event": event,
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(json_path, payload)
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return {
        **payload,
        "json_ref": str(json_path.relative_to(project_root)),
        "markdown_ref": str(markdown_path.relative_to(project_root)),
    }
