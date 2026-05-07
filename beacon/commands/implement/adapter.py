"""Skill adapter integration for implement command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.implement_adapters import (
    build_default_task_prompt,
    detect_adapter,
    discover_skill_adapters,
    format_template,
    load_beacon_config,
    resolve_adapter,
    resolve_default_runner,
)


def discover_adapters(project_root: Path) -> list[dict[str, Any]]:
    """Discover available skill adapters."""
    return [{"name": key, **value} for key, value in discover_skill_adapters(project_root).items()]


def resolve_adapter_for_feature(
    project_root: Path,
    *,
    feature: str,
    runner: str | None = None,
) -> dict[str, Any] | None:
    """Resolve adapter for a specific feature."""
    adapters = discover_adapters(project_root)

    if runner:
        # Find adapter by runner name
        for adapter in adapters:
            if adapter.get("name") == runner:
                return adapter

    # Use default adapter resolution
    adapter_id, adapter = resolve_adapter(project_root, runner or resolve_default_runner(project_root))
    if adapter_id is None:
        return None
    return {"name": adapter_id, **adapter}


def build_adapter_context(
    project_root: Path,
    *,
    feature: str,
    version: str,
    requirements: dict[str, Any],
) -> dict[str, Any]:
    """Build context for adapter execution."""
    return {
        "feature": feature,
        "version": version,
        "project_root": str(project_root),
        "requirements": requirements,
    }


def execute_adapter(
    adapter: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Execute skill adapter with given context."""
    # Build task prompt
    template = adapter.get("template", "")
    prompt = format_template(template, context) if template else build_default_task_prompt(context)

    # Execute adapter
    skill = adapter.get("skill", "")
    adapter_type = adapter.get("adapter_type", "")

    result = {
        "adapter_id": adapter.get("name", ""),
        "adapter_type": adapter_type,
        "skill": skill,
        "prompt": prompt,
        "success": False,
    }

    # Adapter execution logic would go here
    # For now, return the structure

    return result


def resolve_host_runtime_for_adapter(
    *,
    adapter_id: str,
    adapter: dict[str, Any],
    explicit_host_runtime: str | None,
) -> str:
    """Resolve host runtime for adapter."""
    if explicit_host_runtime:
        return explicit_host_runtime

    runtime_family = str(adapter.get("runtime_family", "") or "").strip().lower()

    if adapter_id == "codex-subagents" or runtime_family == "codex-native":
        return "codex"

    if runtime_family == "claude-code" or adapter_id == "gstack":
        return "claude-code"

    return "file"


def requires_host_native_prechecks(
    *,
    adapter_id: str,
    adapter: dict[str, Any],
    mode: str,
) -> bool:
    """Check if adapter requires host-native prechecks."""
    adapter_type = str(adapter.get("adapter_type", "") or "").strip().lower()
    runtime_family = str(adapter.get("runtime_family", "") or "").strip().lower()

    if adapter_type == "handoff":
        return False

    return bool(
        mode in {"team", "ralph"}
        or adapter_id == "codex-subagents"
        or runtime_family == "claude-code"
    )
