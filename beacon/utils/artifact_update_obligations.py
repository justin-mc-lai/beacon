"""Formalize implement/review artifact update follow-ups as machine obligations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


def obligations_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "artifact-update-obligations"


def obligations_path(project_root: Path, *, feature: str) -> Path:
    return obligations_root(project_root) / f"{feature_slug(feature)}.json"


def _normalize_obligation(name: str, payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    required = bool(payload.get("required", False))
    if not required:
        return None
    return {
        "artifact": str(name or "").strip(),
        "required": True,
        "reason": str(payload.get("reason", "") or "").strip(),
        "status": str(payload.get("status", "open") or "open").strip().lower() or "open",
        "notes": str(payload.get("notes", "") or "").strip(),
    }


def write_artifact_update_obligations(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    run_id: str,
    updates: dict[str, Any] | None,
    technical_archive_path: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    obligations: list[dict[str, Any]] = []
    if isinstance(updates, dict):
        for name, payload in updates.items():
            normalized = _normalize_obligation(str(name), payload)
            if normalized:
                obligations.append(normalized)

    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "run_id": run_id,
        "generated_at": now_iso(),
        "technical_archive_path": str(technical_archive_path or "").strip(),
        "obligations": obligations,
        "open_count": len([item for item in obligations if str(item.get("status", "open")) == "open"]),
    }
    write_json(obligations_path(project_root, feature=feature), payload)
    return payload


def load_artifact_update_obligations(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(obligations_path(project_root, feature=feature), {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("feature", feature)
    payload.setdefault("feature_slug", feature_slug(feature))
    rows = payload.get("obligations") if isinstance(payload.get("obligations"), list) else []
    payload["obligations"] = [row for row in rows if isinstance(row, dict)]
    payload["open_count"] = len([item for item in payload["obligations"] if str(item.get("status", "open")) == "open"])
    return payload


def blocking_obligations(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    out: list[dict[str, Any]] = []
    for item in payload.get("obligations", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("status", "open") or "open").strip().lower() != "open":
            continue
        artifact = str(item.get("artifact", "") or "").strip().lower()
        if artifact == "acceptance":
            continue
        out.append(item)
    return out


def update_artifact_update_obligation(
    project_root: Path,
    *,
    feature: str,
    artifact: str,
    status: str,
    note: str = "",
) -> dict[str, Any]:
    payload = load_artifact_update_obligations(project_root, feature=feature)
    rows = payload.get("obligations") if isinstance(payload.get("obligations"), list) else []
    changed = False
    for item in rows:
        if not isinstance(item, dict):
            continue
        if str(item.get("artifact", "")).strip() != str(artifact or "").strip():
            continue
        item["status"] = str(status or "completed").strip().lower() or "completed"
        item["updated_at"] = now_iso()
        if note.strip():
            item["notes"] = note.strip()
        changed = True
    if changed:
        payload["updated_at"] = now_iso()
        payload["open_count"] = len([item for item in rows if str(item.get("status", "open")) == "open"])
        write_json(obligations_path(project_root, feature=feature), payload)
    return payload
