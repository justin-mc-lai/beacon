"""Canonical implementation delivery baseline envelope helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


PROJECTION_FIELDS = ("baseline_id", "transaction_id", "source_hash", "projection_seq")


def implementation_delivery_baseline_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, f"implementation-delivery-baseline-{feature_slug(feature)}.json")


def architecture_blueprint_path(project_root: Path, version: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return human_execution_file(project_root, resolved_version, "architecture-blueprint.md")


def _normalize_string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def _stable_hash(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _field_value(seed: dict[str, Any], *names: str, default: Any = "") -> Any:
    for name in names:
        value = seed.get(name)
        if value not in (None, ""):
            return value
    return default


def build_implementation_delivery_baseline(
    project_root: Path,
    *,
    version: str,
    feature: str,
    revision_id: str = "",
    seed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    source = dict(seed or {})
    slug = feature_slug(feature)
    base_branch = str(_field_value(source, "base_branch", default="main") or "main")
    target_branch = str(_field_value(source, "target_branch", "expected_branch", default=f"beacon/{resolved_version}") or f"beacon/{resolved_version}")
    branch_prefix = str(_field_value(source, "branch_prefix", default=(target_branch.split("/", 1)[0] + "/" if "/" in target_branch else "beacon/")) or "beacon/")
    service_directories = _normalize_string_list(source.get("service_directories")) or _normalize_string_list(source.get("git_roots")) or ["."]
    direct_delivery_services = _normalize_string_list(source.get("direct_delivery_services")) or list(service_directories)
    writable_services = _normalize_string_list(source.get("writable_services")) or list(direct_delivery_services)
    reference_only_services = _normalize_string_list(source.get("reference_only_services")) or ["docs"]
    worktree_root = str(_field_value(source, "worktree_root", default=".") or ".")
    workspace_root = str(_field_value(source, "workspace_root", default=worktree_root) or worktree_root)
    use_git_worktree = bool(source.get("use_git_worktree", False))
    service_branch_map = {service: target_branch for service in direct_delivery_services}
    service_worktree_map = {service: worktree_root for service in direct_delivery_services}
    feature_overlay = {
        "feature": feature,
        "feature_slug": slug,
        "revision_id": revision_id or str(source.get("revision_id", "") or ""),
        "direct_delivery_services": direct_delivery_services,
        "writable_services": writable_services,
        "reference_only_services": reference_only_services,
        "service_branch_map": service_branch_map,
        "service_worktree_map": service_worktree_map,
    }
    source_payload = {
        "version": resolved_version,
        "feature": feature,
        "revision_id": feature_overlay["revision_id"],
        "branch_strategy": str(_field_value(source, "branch_strategy", default="single-branch") or "single-branch"),
        "base_branch": base_branch,
        "default_target_branch": target_branch,
        "branch_prefix": branch_prefix,
        "use_git_worktree": use_git_worktree,
        "worktree_root": worktree_root,
        "workspace_root": workspace_root,
        "direct_delivery_services": direct_delivery_services,
        "writable_services": writable_services,
        "reference_only_services": reference_only_services,
        "service_branch_map": service_branch_map,
        "service_worktree_map": service_worktree_map,
        "feature_overlays": {slug: feature_overlay},
    }
    source_hash = _stable_hash(source_payload)
    baseline_id = f"impl-delivery-baseline-{resolved_version}-{slug}-{feature_overlay['revision_id'] or 'r0'}"
    transaction_id = _stable_hash({"baseline_id": baseline_id, "source_hash": source_hash})[:24].replace("sha256:", "tx-")
    return {
        "schema_version": "1.0",
        "artifact": "implementation_delivery_baseline_envelope",
        "baseline_id": baseline_id,
        "transaction_id": transaction_id,
        "source_hash": source_hash,
        "projection_seq": 1,
        "version": resolved_version,
        "feature": feature,
        "feature_slug": slug,
        "workspace_root": workspace_root,
        "branch_strategy": source_payload["branch_strategy"],
        "base_branch": base_branch,
        "branch_prefix": branch_prefix,
        "default_target_branch": target_branch,
        "use_git_worktree": use_git_worktree,
        "worktree_root": worktree_root,
        "direct_delivery_services": direct_delivery_services,
        "writable_services": writable_services,
        "reference_only_services": reference_only_services,
        "service_branch_map": service_branch_map,
        "service_worktree_map": service_worktree_map,
        "feature_overlays": {slug: feature_overlay},
        "source_payload": source_payload,
        "generated_at": now_iso(),
    }


def projection_metadata(envelope: dict[str, Any], *, project_root: Path | None = None, version: str = "", feature: str = "") -> dict[str, Any]:
    metadata = {field: envelope.get(field) for field in PROJECTION_FIELDS}
    if project_root is not None and version and feature:
        metadata["canonical_envelope_ref"] = str(implementation_delivery_baseline_path(project_root, version, feature).relative_to(project_root))
    metadata["projection_source"] = "implementation_delivery_baseline_envelope"
    return metadata


def _render_architecture_projection(envelope: dict[str, Any]) -> str:
    services = envelope.get("direct_delivery_services") if isinstance(envelope.get("direct_delivery_services"), list) else []
    writable = envelope.get("writable_services") if isinstance(envelope.get("writable_services"), list) else []
    reference = envelope.get("reference_only_services") if isinstance(envelope.get("reference_only_services"), list) else []
    lines = [
        "<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:START -->",
        "## Implementation Delivery Baseline",
        "",
        f"- baseline_id: `{envelope.get('baseline_id', '')}`",
        f"- transaction_id: `{envelope.get('transaction_id', '')}`",
        f"- source_hash: `{envelope.get('source_hash', '')}`",
        f"- projection_seq: `{envelope.get('projection_seq', '')}`",
        f"- version: `{envelope.get('version', '')}`",
        f"- feature: `{envelope.get('feature', '')}`",
        f"- branch_strategy: `{envelope.get('branch_strategy', '')}`",
        f"- base_branch: `{envelope.get('base_branch', '')}`",
        f"- default_target_branch: `{envelope.get('default_target_branch', '')}`",
        f"- branch_prefix: `{envelope.get('branch_prefix', '')}`",
        f"- use_git_worktree: `{bool(envelope.get('use_git_worktree', False))}`",
        f"- worktree_root: `{envelope.get('worktree_root', '')}`",
        f"- workspace_root: `{envelope.get('workspace_root', '')}`",
        "",
        "### Delivery Service Scope",
        f"- direct_delivery_services: {', '.join(services) or '-'}",
        f"- writable_services: {', '.join(writable) or '-'}",
        f"- reference_only_services: {', '.join(reference) or '-'}",
        "",
        "### Plan-Time Gate Contract",
        "- canonical envelope is the only delivery baseline source.",
        "- deterministic implementation contract, git workflow contract, and implementation plan are projections.",
        "- gates must block if projection metadata or service/branch/worktree fields drift.",
        "<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:END -->",
    ]
    return "\n".join(lines) + "\n"


def _replace_projection_block(existing: str, projection: str) -> str:
    start = "<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:START -->"
    end = "<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:END -->"
    if start in existing and end in existing:
        before = existing.split(start, 1)[0].rstrip()
        after = existing.split(end, 1)[1].lstrip()
        return f"{before}\n\n{projection.rstrip()}\n\n{after}".rstrip() + "\n"
    prefix = existing.rstrip() or "# Architecture Blueprint"
    return f"{prefix}\n\n{projection}"


def materialize_implementation_delivery_baseline(
    project_root: Path,
    *,
    version: str,
    feature: str,
    revision_id: str = "",
    seed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    envelope = build_implementation_delivery_baseline(project_root, version=resolved_version, feature=feature, revision_id=revision_id, seed=seed)
    path = implementation_delivery_baseline_path(project_root, resolved_version, feature)
    write_json(path, envelope)
    blueprint_path = architecture_blueprint_path(project_root, resolved_version)
    existing = blueprint_path.read_text(encoding="utf-8") if blueprint_path.exists() else f"# Beacon {resolved_version} Architecture Blueprint\n"
    blueprint_path.parent.mkdir(parents=True, exist_ok=True)
    blueprint_path.write_text(_replace_projection_block(existing, _render_architecture_projection(envelope)), encoding="utf-8")
    return envelope


def load_implementation_delivery_baseline(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    payload = read_json(implementation_delivery_baseline_path(project_root, version, feature), {})
    return payload if isinstance(payload, dict) else {}


def baseline_revision_id(envelope: dict[str, Any]) -> str:
    overlay = envelope.get("feature_overlays")
    if isinstance(overlay, dict):
        for value in overlay.values():
            if isinstance(value, dict):
                revision_id = str(value.get("revision_id", "") or "").strip()
                if revision_id:
                    return revision_id
    return str(envelope.get("revision_id", "") or "").strip()


def validate_projection_against_baseline(
    projection: dict[str, Any],
    envelope: dict[str, Any],
    *,
    projection_name: str,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for field in PROJECTION_FIELDS:
        if str(projection.get(field, "") or "") != str(envelope.get(field, "") or ""):
            issues.append({"projection": projection_name, "field": field, "expected": envelope.get(field), "actual": projection.get(field)})
    comparisons = {
        "base_branch": "base_branch",
        "branch_prefix": "branch_prefix",
        "use_git_worktree": "use_git_worktree",
        "worktree_root": "worktree_root",
    }
    if "target_branch" in projection:
        comparisons["target_branch"] = "default_target_branch"
    if "expected_branch" in projection:
        comparisons["expected_branch"] = "default_target_branch"
    for projection_field, envelope_field in comparisons.items():
        if str(projection.get(projection_field, "") or "") != str(envelope.get(envelope_field, "") or ""):
            issues.append({"projection": projection_name, "field": projection_field, "expected": envelope.get(envelope_field), "actual": projection.get(projection_field)})
    for list_field in ("direct_delivery_services", "writable_services", "reference_only_services"):
        if list_field in projection and _normalize_string_list(projection.get(list_field)) != _normalize_string_list(envelope.get(list_field)):
            issues.append({"projection": projection_name, "field": list_field, "expected": envelope.get(list_field), "actual": projection.get(list_field)})
    return issues
