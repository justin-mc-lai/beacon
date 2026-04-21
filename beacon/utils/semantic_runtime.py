"""Shared host-native semantic runtime helpers for Beacon requirement commands."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from beacon.utils.subagent_readiness import detect_host_runtime

_SUPPORTED_HOSTS = {"codex", "claude"}
_SUPPORTED_REQUESTED_MODES = {"auto", "llm", "rule"}


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def normalize_requested_mode(value: str) -> str:
    requested_mode = str(value or "auto").strip().lower()
    if requested_mode not in _SUPPORTED_REQUESTED_MODES:
        raise ValueError("mode must be auto/llm/rule")
    return requested_mode


def _command_env_key(command_name: str) -> str:
    return str(command_name or "").strip().upper().replace("-", "_")


def _host_response_env_names(command_name: str) -> tuple[list[str], list[str]]:
    command_key = _command_env_key(command_name)
    json_names = []
    file_names = []
    if command_key:
        json_names.append(f"BEACON_HOST_{command_key}_RESPONSE_JSON")
        file_names.append(f"BEACON_HOST_{command_key}_RESPONSE_FILE")
    json_names.append("BEACON_HOST_SEMANTIC_RESPONSE_JSON")
    file_names.append("BEACON_HOST_SEMANTIC_RESPONSE_FILE")
    return json_names, file_names


def host_response_source(command_name: str) -> dict[str, Any]:
    json_names, file_names = _host_response_env_names(command_name)
    for env_name in json_names:
        raw = str(os.environ.get(env_name, "") or "").strip()
        if raw:
            return {
                "available": True,
                "source": "env_json",
                "env_name": env_name,
                "path": "",
                "raw": raw,
            }
    for env_name in file_names:
        raw_path = str(os.environ.get(env_name, "") or "").strip()
        if not raw_path:
            continue
        path = Path(raw_path)
        if not path.exists():
            continue
        return {
            "available": True,
            "source": "file_json",
            "env_name": env_name,
            "path": str(path),
            "raw": path.read_text(encoding="utf-8"),
        }
    return {
        "available": False,
        "source": "none",
        "env_name": "",
        "path": "",
        "raw": "",
    }


def load_host_response_json(command_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    source = host_response_source(command_name)
    if not bool(source.get("available")):
        return {}, source
    raw = str(source.get("raw") or "").strip()
    if not raw:
        return {}, source
    try:
        payload = json.loads(raw)
    except Exception:  # noqa: BLE001
        return {}, source
    return payload if isinstance(payload, dict) else {}, source


def build_semantic_capability_snapshot(
    command_name: str,
    *,
    disable_env: str,
    host_runtime: str | None = None,
) -> dict[str, Any]:
    resolved_host_runtime = detect_host_runtime(host_runtime)
    response = host_response_source(command_name)
    host_response_available = bool(response.get("available"))
    host_bridge_declared = _truthy(os.environ.get("BEACON_HOST_SEMANTIC_BRIDGE")) or host_response_available
    provider_available = bool(str(os.environ.get("BEACON_LLM_API_KEY", "") or "").strip())
    llm_disabled = _truthy(os.environ.get(disable_env))
    return {
        "schema_version": "1.0",
        "command_name": command_name,
        "host_runtime": resolved_host_runtime,
        "host_bridge_declared": host_bridge_declared,
        "host_response_available": host_response_available,
        "host_response_source": str(response.get("source") or "none"),
        "host_response_path": str(response.get("path") or ""),
        "host_semantic_ready": resolved_host_runtime in _SUPPORTED_HOSTS and host_response_available,
        "provider_available": provider_available,
        "provider_key_present": provider_available,
        "llm_disabled": llm_disabled,
        "disable_env": disable_env,
    }


def build_mode_contract(
    *,
    requested_mode: str,
    effective_mode: str,
    fallback_reason: str,
    capability_snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "requested_mode": requested_mode,
        "effective_mode": effective_mode,
        "generator_mode": effective_mode,
        "fallback_reason": fallback_reason,
        "capability_snapshot": capability_snapshot,
    }


def llm_unavailable_message(command_label: str) -> str:
    return f"{command_label} semantic compile requires host semantic response or BEACON_LLM_API_KEY."
