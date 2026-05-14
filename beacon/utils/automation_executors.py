"""Capability model for host automation executors."""

from __future__ import annotations

from pathlib import Path
from typing import Any


EXECUTOR_CAPABILITIES: dict[str, dict[str, Any]] = {
    "codex": {
        "executor": "codex",
        "tier": "native",
        "status": "supported",
        "native_scheduler": True,
        "programmatic_execution": True,
        "beacon_runtime_execution": True,
        "host_runtime_value": "codex",
        "prompt_surface": "codex",
        "scheduler_assets": ["codex-automations", "launchd"],
        "notes": "Use Codex Automations or host scheduler; Beacon runtime paths are first-class.",
    },
    "claude": {
        "executor": "claude",
        "tier": "native",
        "status": "supported",
        "native_scheduler": False,
        "programmatic_execution": True,
        "beacon_runtime_execution": True,
        "host_runtime_value": "claude",
        "prompt_surface": "claude",
        "scheduler_assets": ["launchd", "cron", "github-actions"],
        "notes": "Use Claude CLI/SDK or external scheduler; Beacon runtime paths are first-class.",
    },
    "cursor": {
        "executor": "cursor",
        "tier": "native",
        "status": "supported-via-adapter",
        "native_scheduler": False,
        "programmatic_execution": True,
        "beacon_runtime_execution": False,
        "host_runtime_value": "",
        "prompt_surface": "cursor",
        "scheduler_assets": ["cursor-background-agents", "cursor-cli", "launchd"],
        "notes": "Cursor has official CLI/API surfaces, but Beacon implement/qa host_runtime is not yet cursor-native.",
    },
    "windsurf": {
        "executor": "windsurf",
        "tier": "assisted",
        "status": "scaffold-only",
        "native_scheduler": False,
        "programmatic_execution": False,
        "beacon_runtime_execution": False,
        "host_runtime_value": "",
        "prompt_surface": "generic",
        "scheduler_assets": ["launchd"],
        "notes": "Windsurf is currently supported as project-local skills/workflows plus external scheduler guidance only.",
    },
    "trae": {
        "executor": "trae",
        "tier": "experimental",
        "status": "scaffold-only",
        "native_scheduler": False,
        "programmatic_execution": False,
        "beacon_runtime_execution": False,
        "host_runtime_value": "",
        "prompt_surface": "generic",
        "scheduler_assets": ["launchd"],
        "notes": "Trae remains experimental until a stable public execution API/CLI is proven and integrated.",
    },
}

DEFAULT_EXECUTOR = "codex"


def normalize_executor(value: str | None) -> str:
    text = str(value or "").strip().lower()
    if text in EXECUTOR_CAPABILITIES:
        return text
    return DEFAULT_EXECUTOR


def executor_capability(executor: str | None) -> dict[str, Any]:
    normalized = normalize_executor(executor)
    return dict(EXECUTOR_CAPABILITIES[normalized])


def build_executor_capability_matrix() -> list[dict[str, Any]]:
    order = ["codex", "claude", "cursor", "windsurf", "trae"]
    return [executor_capability(name) for name in order]


def scaffold_scheduler_dir(project_root: Path, executor: str | None) -> str:
    normalized = normalize_executor(executor)
    if normalized == "codex":
        return "codex"
    return "generic"
