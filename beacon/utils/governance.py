"""Runtime governance helpers for project mode and takeover baseline gates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.versioning import load_project_onboarding_state, resolve_target_version

_TAKEOVER_BASELINE_DOCS = {
    "architecture_blueprint": "execution/architecture-blueprint.md",
    "current_state_service_map": "execution/current-state-service-map.md",
    "refactor_boundaries": "execution/refactor-boundaries.md",
}


def load_project_mode(project_root: Path) -> str:
    payload = load_project_onboarding_state(project_root)
    mode = str(payload.get("project_mode", "") or "").strip().lower()
    return mode if mode in {"greenfield", "takeover"} else "greenfield"


def takeover_baseline_paths(project_root: Path, *, version: str) -> dict[str, Path]:
    resolved_version = resolve_target_version(project_root, version)
    base = project_root / "docs" / "beacon" / resolved_version
    return {key: base / rel for key, rel in _TAKEOVER_BASELINE_DOCS.items()}


def _doc_status(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""
    if not text.strip():
        return ""
    for line in text.splitlines():
        normalized = line.strip()
        if normalized.lower().startswith("- status:"):
            return normalized.split(":", 1)[1].strip().lower()
    return "present"


def _doc_ready(path: Path) -> bool:
    status = _doc_status(path)
    return bool(status) and status != "draft"


def evaluate_takeover_baseline_gate(project_root: Path, *, version: str) -> dict[str, Any]:
    project_mode = load_project_mode(project_root)
    resolved_version = resolve_target_version(project_root, version)
    onboarding = load_project_onboarding_state(project_root)
    docs = takeover_baseline_paths(project_root, version=resolved_version)
    docs_status: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, Any]] = []

    missing_reason_map = {
        "architecture_blueprint": "takeover_architecture_blueprint_missing",
        "current_state_service_map": "takeover_current_state_service_map_missing",
        "refactor_boundaries": "takeover_refactor_boundaries_missing",
    }
    for key, path in docs.items():
        exists = path.exists()
        status = _doc_status(path)
        ready = bool(status) and status != "draft"
        docs_status[key] = {
            "path": str(path.relative_to(project_root)),
            "exists": exists,
            "ready": ready,
            "status": status,
        }
        if project_mode == "takeover" and (not exists or not ready):
            issues.append(
                {
                    "reason_code": missing_reason_map[key],
                    "message": f"takeover baseline document not ready: {path.relative_to(project_root)}",
                    "path": str(path.relative_to(project_root)),
                }
            )

    if project_mode != "takeover":
        return {
            "status": "not_applicable",
            "project_mode": project_mode,
            "version": resolved_version,
            "reason_code": "",
            "issues": [],
            "docs": docs_status,
            "baseline_frozen": True,
            "baseline_frozen_at": "",
        }

    baseline_frozen_at = ""
    for key in (
        "takeover_baseline_frozen_at",
        "current_state_baseline_frozen_at",
        "baseline_frozen_at",
    ):
        value = str(onboarding.get(key, "") or "").strip()
        if value:
            baseline_frozen_at = value
            break
    docs_frozen = bool(docs_status) and all(str(item.get("status", "") or "") == "frozen" for item in docs_status.values())
    baseline_frozen = bool(docs_frozen or baseline_frozen_at or onboarding.get("takeover_baseline_frozen") is True)
    if not baseline_frozen:
        issues.append(
            {
                "reason_code": "takeover_current_state_not_frozen",
                "message": "takeover current-state baseline is not frozen",
            }
        )

    return {
        "status": "blocked" if issues else "pass",
        "project_mode": project_mode,
        "version": resolved_version,
        "reason_code": "takeover_baseline_required" if issues else "",
        "issues": issues,
        "docs": docs_status,
        "baseline_frozen": baseline_frozen,
        "baseline_frozen_at": baseline_frozen_at,
    }
