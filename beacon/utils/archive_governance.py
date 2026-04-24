"""Archive governance and historical requirement isolation helpers for v1.3.8."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, release_line_key, resolve_target_version


ARCHIVE_STATUSES: tuple[str, ...] = (
    "active",
    "superseded",
    "archived-learnable",
    "archived-reference-only",
)
_ARCHIVED_STATUSES = {"archived-learnable", "archived-reference-only"}


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def archive_governance_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 3, 8)


def archive_machine_dir(project_root: Path, version: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / ".machine" / "archive"


def archive_plan_path(project_root: Path, version: str) -> Path:
    return archive_machine_dir(project_root, version) / "archive-plan.json"


def archive_index_path(project_root: Path, version: str) -> Path:
    return archive_machine_dir(project_root, version) / "archive-index.json"


def archive_feature_metadata_path(project_root: Path, version: str, feature: str) -> Path:
    return archive_machine_dir(project_root, version) / f"feature-archive-{feature_slug(feature)}.json"


def _rel(project_root: Path, path: Path) -> str:
    return str(path.relative_to(project_root))


def _normalize_status(value: str) -> str:
    text = str(value or "").strip().lower()
    if text not in ARCHIVE_STATUSES:
        return "active"
    return text


def _iter_version_roots(project_root: Path) -> list[str]:
    root = project_root / "docs" / "beacon"
    versions: list[str] = []
    if not root.exists():
        return versions
    for child in root.iterdir():
        normalized = normalize_version(child.name)
        if child.is_dir() and normalized:
            versions.append(normalized)
    return sorted(set(versions), key=_semver_tuple)


def _feature_names(project_root: Path, *, version: str) -> list[str]:
    prd_root = project_root / "docs" / "beacon" / version / "prd"
    if not prd_root.exists():
        return []
    return sorted({path.stem for path in prd_root.glob("*.md")})


def _existing_feature_refs(project_root: Path, *, version: str, feature: str) -> list[str]:
    slug = feature_slug(feature)
    candidates = [
        project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md",
        project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.md",
        project_root / "docs" / "beacon" / version / ".machine" / "execution" / f"implementation-plan-{slug}.json",
        project_root / "docs" / "beacon" / version / ".machine" / "execution" / f"technical-implementation-{slug}.json",
        project_root / "docs" / "beacon" / version / ".machine" / "execution" / f"implementation-summary-{slug}.json",
    ]
    refs: list[str] = []
    for path in candidates:
        if path.exists():
            refs.append(_rel(project_root, path))
    return refs


def load_feature_archive_metadata(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    path = archive_feature_metadata_path(project_root, version, feature)
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def build_feature_archive_metadata(
    project_root: Path,
    *,
    version: str,
    feature: str,
    archive_status: str = "",
    reason: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    existing = load_feature_archive_metadata(project_root, version=resolved_version, feature=feature)
    slug = feature_slug(feature)
    effective_status = _normalize_status(archive_status or str(existing.get("status", "") or "active"))
    source_refs = _existing_feature_refs(project_root, version=resolved_version, feature=feature)
    learnable_refs = source_refs if effective_status == "archived-learnable" else []
    excluded_refs = source_refs if effective_status in _ARCHIVED_STATUSES else []
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "status": effective_status,
        "reason": str(reason or existing.get("reason", "") or "").strip(),
        "active_delivery": effective_status == "active",
        "source_refs": source_refs,
        "learnable_archive_refs": learnable_refs,
        "excluded_from_current_delivery_refs": excluded_refs,
        "archived_at": now_iso() if effective_status in _ARCHIVED_STATUSES else "",
        "generated_at": now_iso(),
    }


def load_feature_archive_boundary(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    metadata = load_feature_archive_metadata(project_root, version=resolved_version, feature=feature)
    if not metadata:
        metadata = build_feature_archive_metadata(project_root, version=resolved_version, feature=feature)
    status = _normalize_status(str(metadata.get("status", "") or "active"))
    return {
        **metadata,
        "status": status,
        "archived": status in _ARCHIVED_STATUSES,
        "learnable": status == "archived-learnable",
        "reference_only": status == "archived-reference-only",
        "plan_ref": _rel(project_root, archive_plan_path(project_root, resolved_version)),
        "index_ref": _rel(project_root, archive_index_path(project_root, resolved_version)),
        "feature_metadata_ref": _rel(project_root, archive_feature_metadata_path(project_root, resolved_version, feature)),
    }


def build_archive_index(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    features = _feature_names(project_root, version=resolved_version)
    rows = [load_feature_archive_boundary(project_root, version=resolved_version, feature=item) for item in features]
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "current_version_truth_root": f"docs/beacon/{resolved_version}",
        "features": [
            {
                "feature": str(row.get("feature", "") or ""),
                "feature_slug": str(row.get("feature_slug", "") or ""),
                "status": str(row.get("status", "") or "active"),
                "reason": str(row.get("reason", "") or ""),
                "active_delivery": bool(row.get("active_delivery", False)),
                "feature_metadata_ref": str(row.get("feature_metadata_ref", "") or ""),
            }
            for row in rows
        ],
        "generated_at": now_iso(),
    }


def build_archive_plan(
    project_root: Path,
    *,
    version: str,
    feature: str = "",
    archive_status: str = "",
    reason: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    all_versions = _iter_version_roots(project_root)
    features = _feature_names(project_root, version=resolved_version)
    archive_rows = [load_feature_archive_boundary(project_root, version=resolved_version, feature=item) for item in features]
    planned_feature = (
        build_feature_archive_metadata(
            project_root,
            version=resolved_version,
            feature=feature,
            archive_status=archive_status,
            reason=reason,
        )
        if feature
        else {}
    )
    if feature and feature_slug(feature) not in {feature_slug(item) for item in features}:
        archive_rows.append(load_feature_archive_boundary(project_root, version=resolved_version, feature=feature))
    learnable_refs = sorted(
        {
            ref
            for row in archive_rows
            if isinstance(row, dict)
            for ref in row.get("learnable_archive_refs", [])
            if str(ref).strip()
        }
    )
    excluded_refs = sorted(
        {
            ref
            for row in archive_rows
            if isinstance(row, dict)
            for ref in row.get("excluded_from_current_delivery_refs", [])
            if str(ref).strip()
        }
    )
    if planned_feature:
        learnable_refs = sorted(set([*learnable_refs, *planned_feature.get("learnable_archive_refs", [])]))
        excluded_refs = sorted(set([*excluded_refs, *planned_feature.get("excluded_from_current_delivery_refs", [])]))
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "current_version_truth_root": f"docs/beacon/{resolved_version}",
        "archived_version_roots": [f"docs/beacon/{item}" for item in all_versions if item != resolved_version],
        "active_feature_set": [
            str(row.get("feature_slug", "") or "")
            for row in archive_rows
            if isinstance(row, dict) and str(row.get("status", "") or "active") == "active"
        ],
        "archived_feature_set": [
            str(row.get("feature_slug", "") or "")
            for row in archive_rows
            if isinstance(row, dict) and str(row.get("status", "") or "") in _ARCHIVED_STATUSES
        ],
        "learnable_archive_refs": learnable_refs,
        "excluded_from_current_delivery_refs": excluded_refs,
        "requested_feature": feature,
        "requested_feature_slug": feature_slug(feature) if feature else "",
        "requested_status": _normalize_status(archive_status) if archive_status else "",
        "requested_reason": str(reason or "").strip(),
        "planned_feature_archive": planned_feature,
        "generated_at": now_iso(),
    }


def materialize_archive_governance(
    project_root: Path,
    *,
    version: str,
    feature: str = "",
    archive_status: str = "",
    reason: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    plan = build_archive_plan(
        project_root,
        version=resolved_version,
        feature=feature,
        archive_status=archive_status,
        reason=reason,
    )
    machine_dir = archive_machine_dir(project_root, resolved_version)
    machine_dir.mkdir(parents=True, exist_ok=True)
    write_json(archive_plan_path(project_root, resolved_version), plan)
    index = build_archive_index(project_root, version=resolved_version)
    write_json(archive_index_path(project_root, resolved_version), index)
    feature_ref = ""
    feature_payload: dict[str, Any] = {}
    if feature:
        feature_payload = build_feature_archive_metadata(
            project_root,
            version=resolved_version,
            feature=feature,
            archive_status=archive_status,
            reason=reason,
        )
        feature_path = archive_feature_metadata_path(project_root, resolved_version, feature)
        write_json(feature_path, feature_payload)
        feature_ref = _rel(project_root, feature_path)
    return {
        "schema_version": "1.0",
        "status": "materialized",
        "version": resolved_version,
        "plan_ref": _rel(project_root, archive_plan_path(project_root, resolved_version)),
        "index_ref": _rel(project_root, archive_index_path(project_root, resolved_version)),
        "feature_ref": feature_ref,
        "plan": plan,
        "index": index,
        "feature_archive": feature_payload,
    }


def load_archive_read_model(project_root: Path, *, version: str, feature: str = "") -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    plan = read_json(archive_plan_path(project_root, resolved_version), {})
    index = read_json(archive_index_path(project_root, resolved_version), {})
    if not plan:
        plan = build_archive_plan(project_root, version=resolved_version)
    if not index:
        index = build_archive_index(project_root, version=resolved_version)
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "plan": plan,
        "index": index,
        "feature": load_feature_archive_boundary(project_root, version=resolved_version, feature=feature) if feature else {},
    }
