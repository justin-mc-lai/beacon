"""Archive governance and historical requirement isolation helpers for v1.3.8."""

from __future__ import annotations

import re
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
    return discover_features(project_root, version=version)


def discover_features(project_root: Path, *, version: str) -> list[str]:
    """List feature slugs from features/*/truth.md (v1.5.2+) with prd/*.md fallback."""
    from beacon.utils.version_truth_catalog import resolve_version_truth_root

    resolved_version = resolve_target_version(project_root, version)
    truth_root = resolve_version_truth_root(project_root, resolved_version)
    features_dir = truth_root / "features"
    if features_dir.is_dir():
        slugs = sorted(
            {
                path.parent.name
                for path in features_dir.glob("*/truth.md")
                if path.is_file() and path.parent.name
            }
        )
        if slugs:
            return slugs
    prd_root = truth_root / "prd"
    if prd_root.is_dir():
        return sorted({path.stem for path in prd_root.glob("*.md") if path.is_file()})
    legacy_prd = project_root / "docs" / "beacon" / resolved_version / "prd"
    if legacy_prd.is_dir():
        return sorted({path.stem for path in legacy_prd.glob("*.md") if path.is_file()})
    return []


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


def _extract_ac_ids_from_truth(truth_path: Path) -> list[str]:
    if not truth_path.is_file():
        return []
    text = truth_path.read_text(encoding="utf-8")
    return sorted(set(re.findall(r"\b(AC-\d{3})\b", text)))


def build_archive_lineage(
    project_root: Path,
    *,
    feature: str,
    from_version: str = "",
    to_version: str = "",
) -> dict[str, Any]:
    from beacon.utils.version_truth_catalog import list_all_catalog_versions, resolve_version_truth_root

    slug = feature_slug(feature)
    versions = list_all_catalog_versions(project_root)
    if not versions:
        versions = _iter_version_roots(project_root)
    hops: list[dict[str, Any]] = []
    for version in versions:
        if from_version and _semver_tuple(version) < _semver_tuple(from_version):
            continue
        if to_version and _semver_tuple(version) > _semver_tuple(to_version):
            continue
        truth_root = resolve_version_truth_root(project_root, version)
        truth_path = truth_root / "features" / slug / "truth.md"
        if not truth_path.is_file():
            truth_path = truth_root / "prd" / f"{slug}.md"
        if not truth_path.is_file():
            continue
        change_path = project_root / "docs" / "beacon" / version / "change" / f"{slug}.md"
        revision_path = project_root / "docs" / "beacon" / version / ".machine" / "execution" / f"{slug}.revision.json"
        revision = read_json(revision_path, {})
        hops.append(
            {
                "version": version,
                "truth_path": _rel(project_root, truth_path),
                "change_path": _rel(project_root, change_path) if change_path.is_file() else "",
                "revision_id": str(revision.get("revision_id") or ""),
                "baseline_hash": str(revision.get("baseline_hash") or ""),
            }
        )
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "from_version": from_version,
        "to_version": to_version,
        "hops": hops,
        "hop_count": len(hops),
        "generated_at": now_iso(),
    }


def build_archive_inventory(
    project_root: Path,
    *,
    version: str = "auto",
    include_archived: bool = False,
) -> dict[str, Any]:
    from beacon.utils.version_truth_catalog import list_active_catalog_versions, list_all_catalog_versions, resolve_version_truth_root

    if include_archived:
        target_versions = list_all_catalog_versions(project_root)
    else:
        target_versions = list_active_catalog_versions(project_root)
    if version not in {"", "auto"}:
        resolved = resolve_target_version(project_root, version)
        target_versions = [resolved]
    rows: list[dict[str, Any]] = []
    for item_version in target_versions:
        truth_root = resolve_version_truth_root(project_root, item_version)
        for slug in discover_features(project_root, version=item_version):
            truth_path = truth_root / "features" / slug / "truth.md"
            if not truth_path.is_file():
                truth_path = truth_root / "prd" / f"{slug}.md"
            rows.append(
                {
                    "version": item_version,
                    "feature_slug": slug,
                    "truth_path": _rel(project_root, truth_path),
                    "ac_ids": _extract_ac_ids_from_truth(truth_path),
                }
            )
    return {
        "schema_version": "1.0",
        "include_archived": include_archived,
        "versions": target_versions,
        "rows": rows,
        "row_count": len(rows),
        "generated_at": now_iso(),
    }
