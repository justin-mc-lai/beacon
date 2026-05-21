"""Implementation-first reconciliation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from beacon.utils.artifact_paths import machine_change_file, machine_execution_file
from beacon.utils.change_surface import build_change_command
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


def implementation_writeback_ledger_path(project_root: Path, *, version: str, feature: str) -> Path:
    return machine_execution_file(project_root, version, f"implementation-writeback-ledger-{feature_slug(feature)}.json")


def reconciliation_artifact_path(project_root: Path, *, version: str, feature: str) -> Path:
    return machine_change_file(project_root, version, f"{feature_slug(feature)}-reconciliation.json")


def load_implementation_writeback_ledger(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    path = implementation_writeback_ledger_path(project_root, version=version, feature=feature)
    payload = read_json(
        path,
        {
            "schema_version": "1.0",
            "artifact": "implementation_writeback_ledger",
            "feature": feature,
            "feature_slug": feature_slug(feature),
            "version": version,
            "entries": [],
        },
    )
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("artifact", "implementation_writeback_ledger")
    payload.setdefault("feature", feature)
    payload.setdefault("feature_slug", feature_slug(feature))
    payload.setdefault("version", version)
    payload.setdefault("entries", [])
    return payload


def append_implementation_writeback_event(
    project_root: Path,
    *,
    version: str,
    feature: str,
    revision_id: str,
    run_id: str,
    implemented_item_ids: Iterable[str] | None = None,
    changed_files: Iterable[str] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    ledger = load_implementation_writeback_ledger(project_root, version=resolved_version, feature=feature)
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), list) else []
    entry = {
        "recorded_at": now_iso(),
        "revision_id": str(revision_id or ""),
        "run_id": str(run_id or ""),
        "implemented_item_ids": [str(item).strip().upper() for item in (implemented_item_ids or []) if str(item).strip()],
        "changed_files": [str(item).strip() for item in (changed_files or []) if str(item).strip()],
    }
    entries.append(entry)
    ledger["entries"] = entries
    ledger["last_recorded_at"] = entry["recorded_at"]
    write_json(implementation_writeback_ledger_path(project_root, version=resolved_version, feature=feature), ledger)
    return entry


def load_reconciliation_artifact(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    payload = read_json(reconciliation_artifact_path(project_root, version=version, feature=feature), {})
    return payload if isinstance(payload, dict) else {}


def build_reconciliation_payload(
    project_root: Path,
    *,
    version: str,
    feature: str,
    revision_state: dict[str, Any],
    implementation_artifacts: list[dict[str, Any]],
    detected_at: str | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    current_revision_id = str(revision_state.get("revision_id", "") or "")
    source_revision_id = str(revision_state.get("source_revision_id", "") or "")
    return {
        "schema_version": "1.0",
        "artifact": "implementation_first_reconciliation",
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "status": "required",
        "reason_code": "implementation_first_reconciliation_required",
        "recovery_kind": "implementation_first_reconciliation",
        "delivery_mode": "recovery_not_normal_delivery",
        "drift_detected_at": str(detected_at or now_iso()),
        "detected_revision_id": current_revision_id,
        "source_revision_id": source_revision_id,
        "implementation_artifacts": implementation_artifacts,
        "missing_truth_surfaces": ["prd", "user-story", "qa/test-cases"],
        "recovery_reason": "implementation evidence exists on earlier revision lineage and must be reconciled through beacon-change without erasing provenance",
        "truth_surfaces_backfilled": [
            f"docs/beacon/{resolved_version}/prd/{slug}.md",
            f"docs/beacon/{resolved_version}/user-story/{slug}.md",
            f"docs/beacon/{resolved_version}/qa/test-cases/{slug}.md",
        ] if str(revision_state.get("doc_status", "") or "") == "frozen" else [],
        "re_freeze_status": "completed" if str(revision_state.get("doc_status", "") or "") == "frozen" else "pending",
        "reprojection_targets": [
            f"docs/beacon/{resolved_version}/user-story/{slug}.md",
            f"docs/beacon/{resolved_version}/qa/test-cases/{slug}.md",
            "qa_proof",
            "release_facing_proof",
        ],
        "provenance": {
            "post_hoc_writeback_occurred": True,
            "preserve_drift_history": True,
            "current_revision_id": current_revision_id,
            "current_delivery_status": str(revision_state.get("delivery_status", "") or ""),
        },
        "change_route": {
            "action": "beacon-change",
            "command": build_change_command(
                feature=feature,
                project_root=project_root,
                version=resolved_version,
                reason="implementation-first-reconciliation",
            ),
        },
    }


def record_implementation_first_reconciliation(
    project_root: Path,
    *,
    version: str,
    feature: str,
    revision_state: dict[str, Any],
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    ledger = load_implementation_writeback_ledger(project_root, version=resolved_version, feature=feature)
    current_revision_id = str(revision_state.get("revision_id", "") or "")
    implementation_artifacts = [
        {
            "revision_id": str(item.get("revision_id", "") or ""),
            "run_id": str(item.get("run_id", "") or ""),
            "recorded_at": str(item.get("recorded_at", "") or ""),
            "implemented_item_ids": [str(v) for v in (item.get("implemented_item_ids") or []) if str(v).strip()],
            "changed_files": [str(v) for v in (item.get("changed_files") or []) if str(v).strip()],
        }
        for item in (ledger.get("entries") or [])
        if isinstance(item, dict) and str(item.get("revision_id", "") or "") and str(item.get("revision_id", "") or "") != current_revision_id
    ]
    existing = load_reconciliation_artifact(project_root, version=resolved_version, feature=feature)
    payload = build_reconciliation_payload(
        project_root,
        version=resolved_version,
        feature=feature,
        revision_state=revision_state,
        implementation_artifacts=implementation_artifacts,
        detected_at=str(existing.get("drift_detected_at", "") or now_iso()),
    )
    write_json(reconciliation_artifact_path(project_root, version=resolved_version, feature=feature), payload)
    return payload


def detect_implementation_first_reconciliation_needed(
    project_root: Path,
    *,
    version: str,
    feature: str,
    revision_state: dict[str, Any],
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    if (
        not feature
        or str(revision_state.get("doc_status", "") or "") != "frozen"
        or not str(revision_state.get("source_revision_id", "") or "")
    ):
        return {"required": False, "reason_code": "", "artifact_path": "", "artifact": {}}

    ledger = load_implementation_writeback_ledger(project_root, version=resolved_version, feature=feature)
    current_revision_id = str(revision_state.get("revision_id", "") or "")
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), list) else []
    has_current_implementation = any(
        isinstance(item, dict)
        and str(item.get("revision_id", "") or "") == current_revision_id
        and str(item.get("run_id", "") or "").strip()
        for item in entries
    )
    if has_current_implementation:
        return {"required": False, "reason_code": "", "artifact_path": "", "artifact": {}}

    has_prior_implementation = any(
        isinstance(item, dict)
        and str(item.get("revision_id", "") or "")
        and str(item.get("revision_id", "") or "") != current_revision_id
        for item in entries
    )
    if not has_prior_implementation:
        return {"required": False, "reason_code": "", "artifact_path": "", "artifact": {}}

    artifact = record_implementation_first_reconciliation(
        project_root,
        version=resolved_version,
        feature=feature,
        revision_state=revision_state,
    )
    path = reconciliation_artifact_path(project_root, version=resolved_version, feature=feature)
    return {
        "required": True,
        "reason_code": "implementation_first_reconciliation_required",
        "artifact_path": str(path.relative_to(project_root)),
        "artifact": artifact,
    }
