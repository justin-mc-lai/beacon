"""Revision lifecycle helpers for Beacon v1.1.6."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_execution_dir
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.versioning import resolve_target_version
from beacon.utils.story_state import _baseline_hash, feature_slug


def revision_state_file(project_root: Path, version: str, feature: str) -> Path:
    return machine_execution_dir(project_root, version) / f"{feature_slug(feature)}.revision.json"


def _default_revision_state(*, version: str, feature: str, revision_id: str = "R1") -> dict[str, Any]:
    slug = feature_slug(feature)
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "revision_id": revision_id,
        "source_revision_id": "",
        "reason": "draft",
        "doc_status": "draft",
        "delivery_status": "idle",
        "lifecycle_status": "draft",
        "baseline_hash": "",
        "superseded_by": "",
        "created_at": now_iso(),
        "frozen_at": "",
        "accepted_at": "",
    }


def load_revision_state(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    create_if_missing: bool = False,
    revision_id: str = "R1",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    path = revision_state_file(project_root, resolved_version, feature)
    state = read_json(path, _default_revision_state(version=resolved_version, feature=feature, revision_id=revision_id))
    if not isinstance(state, dict):
        state = _default_revision_state(version=resolved_version, feature=feature, revision_id=revision_id)
    state.setdefault("schema_version", "1.0")
    state.setdefault("feature", feature)
    state.setdefault("feature_slug", feature_slug(feature))
    state.setdefault("version", resolved_version)
    state.setdefault("revision_id", revision_id)
    state.setdefault("source_revision_id", "")
    state.setdefault("reason", "draft")
    state.setdefault("doc_status", "draft")
    state.setdefault("delivery_status", "idle")
    state.setdefault("lifecycle_status", state.get("doc_status") or "draft")
    state.setdefault("baseline_hash", "")
    state.setdefault("superseded_by", "")
    state.setdefault("created_at", now_iso())
    state.setdefault("frozen_at", "")
    state.setdefault("accepted_at", "")
    if create_if_missing and not path.exists():
        save_revision_state(project_root, version=resolved_version, feature=feature, state=state)
    return state


def save_revision_state(project_root: Path, *, version: str, feature: str, state: dict[str, Any]) -> Path:
    path = revision_state_file(project_root, version, feature)
    payload = dict(state)
    payload["schema_version"] = "1.0"
    payload["feature"] = feature
    payload["feature_slug"] = feature_slug(feature)
    payload["version"] = version
    payload["lifecycle_status"] = payload.get("delivery_status") or payload.get("doc_status") or payload.get("lifecycle_status") or "draft"
    payload.setdefault("created_at", now_iso())
    write_json(path, payload)
    return path


def freeze_revision_state(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    state = load_revision_state(project_root, version=version, feature=feature, create_if_missing=True)
    resolved_version = str(state.get("version"))
    baseline_hash = _baseline_hash(project_root, resolved_version, feature)
    state["reason"] = "freeze"
    state["doc_status"] = "frozen"
    state["lifecycle_status"] = "frozen"
    state["baseline_hash"] = baseline_hash
    state["frozen_at"] = now_iso()
    save_revision_state(project_root, version=resolved_version, feature=feature, state=state)
    return state


def reopen_revision_state(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    reason: str = "reopen",
) -> tuple[dict[str, Any], dict[str, Any]]:
    current = load_revision_state(project_root, version=version, feature=feature, create_if_missing=True)
    resolved_version = str(current.get("version"))
    current_id = str(current.get("revision_id", "R1") or "R1")
    try:
        current_num = int(current_id.lstrip("R"))
    except Exception:  # noqa: BLE001
        current_num = 1
    new_revision_id = f"R{current_num + 1}"
    current["doc_status"] = "superseded"
    current["lifecycle_status"] = "superseded"
    current["superseded_by"] = new_revision_id
    save_revision_state(project_root, version=resolved_version, feature=feature, state=current)

    nxt = _default_revision_state(version=resolved_version, feature=feature, revision_id=new_revision_id)
    nxt["source_revision_id"] = current_id
    nxt["reason"] = reason
    nxt["doc_status"] = "draft"
    nxt["delivery_status"] = "idle"
    nxt["lifecycle_status"] = "draft"
    save_revision_state(project_root, version=resolved_version, feature=feature, state=nxt)
    return current, nxt
