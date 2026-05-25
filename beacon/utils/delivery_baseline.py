"""Canonical implementation delivery baseline envelope helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file
from beacon.utils.implementation_design import build_technical_delta
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


PROJECTION_FIELDS = ("baseline_id", "transaction_id", "source_hash", "projection_seq")
_TECHNICAL_DELTA_MARKER = "BEACON:TECHNICAL-DELTA-BLUEPRINT"
_BASELINE_MARKER = "BEACON:IMPLEMENTATION-DELIVERY-BASELINE"
_HOST_MARKER = "BEACON:IMPLEMENTATION-DELIVERY-HOST"


def implementation_delivery_baseline_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, f"implementation-delivery-baseline-{feature_slug(feature)}.json")


def implementation_delivery_host_path(project_root: Path, version: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, "implementation-delivery-host.json")


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


def _normalize_path_value(value: Any, *, project_root: Path | None = None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    path = Path(text).expanduser()
    if project_root is not None and not path.is_absolute():
        path = project_root / path
    try:
        return str(path.resolve())
    except Exception:  # noqa: BLE001
        return str(path)


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
    depends_on_features = _normalize_string_list(source.get("depends_on_features"))
    worktree_root = str(_field_value(source, "worktree_root", default=".") or ".")
    workspace_root = str(_field_value(source, "workspace_root", default=worktree_root) or worktree_root)
    use_git_worktree = bool(source.get("use_git_worktree", False))
    source_branch_map = source.get("service_branch_map") if isinstance(source.get("service_branch_map"), dict) else {}
    source_worktree_map = source.get("service_worktree_map") if isinstance(source.get("service_worktree_map"), dict) else {}
    service_branch_map = {
        service: str(source_branch_map.get(service) or target_branch)
        for service in direct_delivery_services
    }
    service_worktree_map = {
        service: str(source_worktree_map.get(service) or worktree_root)
        for service in direct_delivery_services
    }
    feature_overlay = {
        "feature": feature,
        "feature_slug": slug,
        "revision_id": revision_id or str(source.get("revision_id", "") or ""),
        "direct_delivery_services": direct_delivery_services,
        "writable_services": writable_services,
        "reference_only_services": reference_only_services,
        "depends_on_features": depends_on_features,
        "service_branch_map": service_branch_map,
        "service_worktree_map": service_worktree_map,
    }
    technical_delta = build_technical_delta(
        project_root,
        version=resolved_version,
        feature=feature,
        direct_delivery_services=direct_delivery_services,
        reference_only_services=reference_only_services,
    )
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
        "depends_on_features": depends_on_features,
        "service_branch_map": service_branch_map,
        "service_worktree_map": service_worktree_map,
        "feature_overlays": {slug: feature_overlay},
        "technical_delta": technical_delta,
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
        "depends_on_features": depends_on_features,
        "service_branch_map": service_branch_map,
        "service_worktree_map": service_worktree_map,
        "feature_overlays": {slug: feature_overlay},
        "technical_delta": technical_delta,
        "source_payload": source_payload,
        "generated_at": now_iso(),
    }


def projection_metadata(envelope: dict[str, Any], *, project_root: Path | None = None, version: str = "", feature: str = "") -> dict[str, Any]:
    metadata = {field: envelope.get(field) for field in PROJECTION_FIELDS}
    if project_root is not None and version and feature:
        metadata["canonical_envelope_ref"] = str(implementation_delivery_baseline_path(project_root, version, feature).relative_to(project_root))
    metadata["projection_source"] = "implementation_delivery_baseline_envelope"
    return metadata


def _managed_block_markers(marker: str, *, slug: str = "") -> tuple[str, str]:
    if slug:
        return (
            f"<!-- {marker}:{slug}:START -->",
            f"<!-- {marker}:{slug}:END -->",
        )
    return (
        f"<!-- {marker}:START -->",
        f"<!-- {marker}:END -->",
    )


def _render_architecture_projection(envelope: dict[str, Any]) -> str:
    start_marker, end_marker = _managed_block_markers(_BASELINE_MARKER, slug=str(envelope.get("feature_slug", "") or ""))
    services = envelope.get("direct_delivery_services") if isinstance(envelope.get("direct_delivery_services"), list) else []
    writable = envelope.get("writable_services") if isinstance(envelope.get("writable_services"), list) else []
    reference = envelope.get("reference_only_services") if isinstance(envelope.get("reference_only_services"), list) else []
    lines = [
        start_marker,
        "## Implementation Delivery Baseline",
        "",
        f"- baseline_id: `{envelope.get('baseline_id', '')}`",
        f"- transaction_id: `{envelope.get('transaction_id', '')}`",
        f"- source_hash: `{envelope.get('source_hash', '')}`",
        f"- projection_seq: `{envelope.get('projection_seq', '')}`",
        f"- version: `{envelope.get('version', '')}`",
        f"- feature: `{envelope.get('feature', '')}`",
        "- lifecycle_role: `pre-implement delivery blueprint projection`",
        "- projection_refresh_trigger: `implement plan against the active frozen revision`",
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
        f"- depends_on_features: {', '.join(_normalize_string_list(envelope.get('depends_on_features'))) or '-'}",
        "",
        "### Plan-Time Gate Contract",
        "- canonical envelope is the only delivery baseline source.",
        "- deterministic implementation contract, git workflow contract, and implementation plan are projections.",
        "- gates must block if projection metadata or service/branch/worktree fields drift.",
        end_marker,
    ]
    return "\n".join(lines) + "\n"


def _host_feature_entry(envelope: dict[str, Any], *, project_root: Path, version: str) -> dict[str, Any]:
    return {
        "feature": str(envelope.get("feature", "") or ""),
        "feature_slug": str(envelope.get("feature_slug", "") or ""),
        "revision_id": baseline_revision_id(envelope),
        "baseline_id": str(envelope.get("baseline_id", "") or ""),
        "transaction_id": str(envelope.get("transaction_id", "") or ""),
        "source_hash": str(envelope.get("source_hash", "") or ""),
        "baseline_ref": str(implementation_delivery_baseline_path(project_root, version, str(envelope.get("feature", "") or "")).relative_to(project_root)),
        "default_target_branch": str(envelope.get("default_target_branch", "") or ""),
        "worktree_root": str(envelope.get("worktree_root", "") or ""),
        "workspace_root": str(envelope.get("workspace_root", "") or ""),
        "direct_delivery_services": _normalize_string_list(envelope.get("direct_delivery_services")),
        "writable_services": _normalize_string_list(envelope.get("writable_services")),
        "reference_only_services": _normalize_string_list(envelope.get("reference_only_services")),
        "depends_on_features": _normalize_string_list(envelope.get("depends_on_features")),
        "updated_at": str(envelope.get("generated_at", "") or ""),
    }


def _load_all_implementation_delivery_baselines(project_root: Path, version: str) -> list[dict[str, Any]]:
    resolved_version = resolve_target_version(project_root, version)
    root = implementation_delivery_host_path(project_root, resolved_version).parent
    baselines: list[dict[str, Any]] = []
    if not root.exists():
        return baselines
    for path in sorted(root.glob("implementation-delivery-baseline-*.json")):
        payload = read_json(path, {})
        if not isinstance(payload, dict) or not payload:
            continue
        if str(payload.get("version", "") or "") != resolved_version:
            continue
        baselines.append(payload)
    return baselines


def build_implementation_delivery_host(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    features = [
        _host_feature_entry(envelope, project_root=project_root, version=resolved_version)
        for envelope in _load_all_implementation_delivery_baselines(project_root, resolved_version)
    ]
    features = sorted(features, key=lambda item: (str(item.get("feature_slug") or ""), str(item.get("revision_id") or "")))
    services_map: dict[str, list[str]] = {}
    for item in features:
        for service in _normalize_string_list(item.get("writable_services")) or _normalize_string_list(item.get("direct_delivery_services")):
            services_map.setdefault(service, [])
            slug = str(item.get("feature_slug") or "")
            if slug and slug not in services_map[service]:
                services_map[service].append(slug)
    source_payload = {
        "version": resolved_version,
        "feature_count": len(features),
        "features": features,
        "services_map": services_map,
    }
    source_hash = _stable_hash(source_payload)
    transaction_id = _stable_hash({"version": resolved_version, "source_hash": source_hash})[:24].replace("sha256:", "tx-")
    return {
        "schema_version": "1.0",
        "artifact": "implementation_delivery_host",
        "version": resolved_version,
        "feature_count": len(features),
        "feature_slugs": [str(item.get("feature_slug") or "") for item in features if str(item.get("feature_slug") or "").strip()],
        "features": features,
        "services_map": services_map,
        "source_hash": source_hash,
        "transaction_id": transaction_id,
        "generated_at": now_iso(),
    }


def load_implementation_delivery_host(project_root: Path, *, version: str) -> dict[str, Any]:
    payload = read_json(implementation_delivery_host_path(project_root, version), {})
    return payload if isinstance(payload, dict) else {}


def _render_host_projection(host: dict[str, Any]) -> str:
    start_marker, end_marker = _managed_block_markers(_HOST_MARKER)
    features = host.get("features") if isinstance(host.get("features"), list) else []
    lines = [
        start_marker,
        "## Implementation Delivery Host",
        "",
        f"- version: `{host.get('version', '')}`",
        f"- feature_count: `{host.get('feature_count', 0)}`",
        f"- transaction_id: `{host.get('transaction_id', '')}`",
        f"- source_hash: `{host.get('source_hash', '')}`",
        "",
        "### Registered Feature Baselines",
    ]
    if features:
        for item in features:
            slug = str(item.get("feature_slug", "") or "").strip()
            branch = str(item.get("default_target_branch", "") or "").strip() or "-"
            services = ", ".join(_normalize_string_list(item.get("writable_services")) or _normalize_string_list(item.get("direct_delivery_services"))) or "-"
            deps = ", ".join(_normalize_string_list(item.get("depends_on_features"))) or "-"
            baseline_ref = str(item.get("baseline_ref", "") or "").strip() or "-"
            lines.append(
                f"- `{slug}` | revision=`{item.get('revision_id', '')}` | branch=`{branch}` | writable_services={services} | depends_on={deps} | baseline_ref=`{baseline_ref}`"
            )
    else:
        lines.append("- none")
    lines.append(end_marker)
    return "\n".join(lines) + "\n"


def _strip_managed_block(text: str, start_marker: str, end_marker: str) -> str:
    if start_marker not in text or end_marker not in text:
        return text
    before = text.split(start_marker, 1)[0].rstrip()
    after = text.split(end_marker, 1)[1].lstrip()
    if before and after:
        return f"{before}\n\n{after}".rstrip() + "\n"
    return (before or after).rstrip() + "\n"


def _extract_managed_block(text: str, start_marker: str, end_marker: str) -> str:
    if start_marker not in text or end_marker not in text:
        return ""
    start = text.index(start_marker)
    end = text.index(end_marker, start) + len(end_marker)
    block = text[start:end]
    return block.rstrip() + "\n"


def _strip_managed_block_variants(text: str, marker: str, *, slug: str = "") -> str:
    updated = text
    for start_marker, end_marker in (
        _managed_block_markers(marker, slug=slug),
        _managed_block_markers(marker),
    ):
        updated = _strip_managed_block(updated, start_marker, end_marker)
    return updated


def _extract_managed_block_variants(text: str, marker: str, *, slug: str = "") -> str:
    for start_marker, end_marker in (
        _managed_block_markers(marker, slug=slug),
        _managed_block_markers(marker),
    ):
        block = _extract_managed_block(text, start_marker, end_marker)
        if block:
            return block
    return ""


def _render_technical_delta_projection(envelope: dict[str, Any]) -> str:
    start_marker, end_marker = _managed_block_markers(_TECHNICAL_DELTA_MARKER, slug=str(envelope.get("feature_slug", "") or ""))
    technical_delta = envelope.get("technical_delta") if isinstance(envelope.get("technical_delta"), dict) else {}
    current_state = technical_delta.get("current_state") if isinstance(technical_delta.get("current_state"), dict) else {}
    refactor = technical_delta.get("refactor_boundaries") if isinstance(technical_delta.get("refactor_boundaries"), dict) else {}
    change_surface = technical_delta.get("change_surface") if isinstance(technical_delta.get("change_surface"), list) else []
    source_refs = technical_delta.get("source_refs") if isinstance(technical_delta.get("source_refs"), dict) else {}
    service_catalog = current_state.get("services") if isinstance(current_state.get("services"), list) else []
    entry_point_groups = current_state.get("entry_point_groups") if isinstance(current_state.get("entry_point_groups"), dict) else {}

    def _append_bullets(title: str, values: list[str]) -> None:
        lines.append(f"- {title}:")
        lines.extend(f"  - {str(item).strip()}" for item in values if str(item).strip())

    lines = [
        start_marker,
        "## Technical Delta Blueprint",
        "",
        f"- project_mode: `{technical_delta.get('project_mode', '')}`",
        f"- feature: `{envelope.get('feature', '')}`",
        f"- version: `{envelope.get('version', '')}`",
        "",
        "### Source Refs",
    ]
    if source_refs:
        for key, value in source_refs.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")

    lines.extend(["", "### Delivery Change Surface"])
    if change_surface:
        for slice_payload in change_surface:
            if not isinstance(slice_payload, dict):
                continue
            title = str(slice_payload.get("title", "") or "").strip()
            heading = str(slice_payload.get("slice_id", "") or "").strip()
            lines.append(f"#### {heading} {title}".strip())
            lines.append(f"- summary: {str(slice_payload.get('description', '') or '').strip() or '-'}")
            lines.append(
                f"- direct_delivery_services: {', '.join(slice_payload.get('direct_delivery_services', [])) or '-'}"
            )
            lines.append(
                f"- reference_only_services: {', '.join(slice_payload.get('reference_only_services', [])) or '-'}"
            )
            change_axes = slice_payload.get("change_axes") if isinstance(slice_payload.get("change_axes"), list) else []
            if change_axes:
                lines.append(f"- change_axes: {', '.join(str(item).strip() for item in change_axes if str(item).strip())}")
            for key, label in (
                ("entry_points", "entry_points"),
                ("implementation_focus", "implementation_focus"),
                ("write_path", "write_path"),
                ("storage_changes", "storage_changes"),
                ("derived_rules", "derived_rules"),
                ("read_path", "read_path"),
                ("downstream_contracts", "downstream_contracts"),
                ("compatibility_notes", "compatibility_notes"),
                ("rollout_notes", "rollout_notes"),
                ("verification_focus", "verification_focus"),
            ):
                values = slice_payload.get(key) if isinstance(slice_payload.get(key), list) else []
                if values:
                    _append_bullets(label, [str(item).strip() for item in values[:6] if str(item).strip()])
            diagram = str(slice_payload.get("call_chain_diagram", "") or "").strip()
            if diagram:
                lines.append("- call_chain_diagram:")
                lines.append("")
                lines.append(diagram)
            lines.append("")
    else:
        lines.append("- none")

    lines.extend(["### Available Entry Surfaces"])
    if entry_point_groups:
        for title, items in entry_point_groups.items():
            values = [str(item).strip() for item in items if str(item).strip()]
            if not values:
                continue
            lines.append(f"- {title}: {' / '.join(values[:4])}")
    else:
        lines.append("- none")

    lines.extend(["### Current Service Facts"])
    if service_catalog:
        for service_payload in service_catalog:
            if not isinstance(service_payload, dict):
                continue
            service_name = str(service_payload.get("service", "") or "").strip()
            if not service_name:
                continue
            lines.append(f"- `{service_name}`")
            summaries = service_payload.get("summary") if isinstance(service_payload.get("summary"), list) else []
            if summaries:
                lines.append(f"  - summary: {' / '.join(str(item).strip() for item in summaries[:3] if str(item).strip())}")
    else:
        lines.append("- none")

    def _list_section(title: str, key: str) -> None:
        values = refactor.get(key) if isinstance(refactor.get(key), list) else []
        lines.extend(["", f"### {title}"])
        if values:
            lines.extend(f"- {str(item).strip()}" for item in values if str(item).strip())
        else:
            lines.append("- none")

    _list_section("Must Change", "must_change")
    _list_section("Can Reuse", "can_reuse")
    _list_section("No-Expand Guardrails", "must_not_change")
    _list_section("Compatibility Rules", "compatibility_rules")
    _list_section("Delivery Constraints", "delivery_constraints")

    handoff = current_state.get("target_handoff") if isinstance(current_state.get("target_handoff"), list) else []
    lines.extend(["", "### Implement Handoff"])
    if handoff:
        lines.extend(f"- {str(item).strip()}" for item in handoff if str(item).strip())
    else:
        lines.append("- none")
    lines.append(end_marker)
    return "\n".join(lines).rstrip() + "\n"


def _render_blueprint_document(existing: str, envelope: dict[str, Any], *, project_root: Path, version: str) -> str:
    slug = str(envelope.get("feature_slug", "") or "")
    host = build_implementation_delivery_host(project_root=project_root, version=version)
    cleaned = _strip_managed_block_variants(existing, _TECHNICAL_DELTA_MARKER, slug=slug)
    cleaned = _strip_managed_block_variants(cleaned, _BASELINE_MARKER, slug=slug)
    cleaned = _strip_managed_block_variants(cleaned, _HOST_MARKER)
    cleaned = cleaned.rstrip()
    if not cleaned:
        cleaned = f"# Beacon {version} Architecture Blueprint"
    parts = [
        cleaned,
        _render_host_projection(host).rstrip(),
        _render_technical_delta_projection(envelope).rstrip(),
        _render_architecture_projection(envelope).rstrip(),
    ]
    return "\n\n".join(part for part in parts if part).rstrip() + "\n"


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
    host_path = implementation_delivery_host_path(project_root, resolved_version)
    write_json(host_path, build_implementation_delivery_host(project_root, version=resolved_version))
    blueprint_path = architecture_blueprint_path(project_root, resolved_version)
    existing = blueprint_path.read_text(encoding="utf-8") if blueprint_path.exists() else f"# Beacon {resolved_version} Architecture Blueprint\n"
    blueprint_path.parent.mkdir(parents=True, exist_ok=True)
    blueprint_path.write_text(
        _render_blueprint_document(existing, envelope, project_root=project_root, version=resolved_version),
        encoding="utf-8",
    )
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
    project_root: Path | None = None,
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
        actual = projection.get(projection_field, "")
        expected = envelope.get(envelope_field, "")
        if projection_field == "worktree_root":
            actual_value = _normalize_path_value(actual, project_root=project_root)
            expected_value = _normalize_path_value(expected, project_root=project_root)
        else:
            actual_value = str(actual or "")
            expected_value = str(expected or "")
        if actual_value != expected_value:
            issues.append({"projection": projection_name, "field": projection_field, "expected": envelope.get(envelope_field), "actual": projection.get(projection_field)})
    for list_field in ("direct_delivery_services", "writable_services", "reference_only_services"):
        if list_field in projection and _normalize_string_list(projection.get(list_field)) != _normalize_string_list(envelope.get(list_field)):
            issues.append({"projection": projection_name, "field": list_field, "expected": envelope.get(list_field), "actual": projection.get(list_field)})
    return issues


def validate_architecture_blueprint_projection(
    project_root: Path,
    *,
    version: str,
    feature: str,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    blueprint_path = architecture_blueprint_path(project_root, resolved_version)
    baseline = envelope if isinstance(envelope, dict) and envelope else load_implementation_delivery_baseline(
        project_root,
        version=resolved_version,
        feature=feature,
    )
    payload: dict[str, Any] = {
        "status": "pass",
        "blocked": False,
        "reason_code": "",
        "path": str(blueprint_path.relative_to(project_root)),
        "feature": feature,
        "version": resolved_version,
        "issues": [],
    }
    if not baseline:
        payload.update(
            {
                "status": "blocked",
                "blocked": True,
                "reason_code": "delivery_baseline_missing",
                "issues": [{"section": "baseline", "message": "canonical implementation delivery baseline missing"}],
            }
        )
        return payload
    if not blueprint_path.exists():
        payload.update(
            {
                "status": "blocked",
                "blocked": True,
                "reason_code": "architecture_blueprint_projection_missing",
                "issues": [{"section": "document", "message": "architecture blueprint document missing"}],
            }
        )
        return payload
    text = blueprint_path.read_text(encoding="utf-8")
    host = build_implementation_delivery_host(project_root, version=resolved_version)
    expected_technical_delta = _render_technical_delta_projection(baseline).strip()
    expected_baseline = _render_architecture_projection(baseline).strip()
    expected_host = _render_host_projection(host).strip()
    slug = str(baseline.get("feature_slug", "") or feature_slug(feature))
    actual_host = _extract_managed_block_variants(text, _HOST_MARKER).strip()
    actual_technical_delta = _extract_managed_block_variants(text, _TECHNICAL_DELTA_MARKER, slug=slug).strip()
    actual_baseline = _extract_managed_block_variants(text, _BASELINE_MARKER, slug=slug).strip()
    missing_sections: list[str] = []
    if not actual_host:
        missing_sections.append("implementation_delivery_host")
    if not actual_technical_delta:
        missing_sections.append("technical_delta_blueprint")
    if not actual_baseline:
        missing_sections.append("implementation_delivery_baseline")
    if missing_sections:
        payload.update(
            {
                "status": "blocked",
                "blocked": True,
                "reason_code": "architecture_blueprint_projection_missing",
                "issues": [
                    {
                        "section": section,
                        "message": f"managed projection block missing: {section}",
                    }
                    for section in missing_sections
                ],
            }
        )
        return payload
    drifted_sections: list[dict[str, Any]] = []
    if actual_host != expected_host:
        drifted_sections.append(
            {
                "section": "implementation_delivery_host",
                "message": "implementation delivery host block drifted from version host registry",
            }
        )
    if actual_technical_delta != expected_technical_delta:
        drifted_sections.append(
            {
                "section": "technical_delta_blueprint",
                "message": "technical delta blueprint drifted from canonical implementation delivery baseline",
            }
        )
    if actual_baseline != expected_baseline:
        drifted_sections.append(
            {
                "section": "implementation_delivery_baseline",
                "message": "implementation delivery baseline block drifted from canonical envelope",
            }
        )
    if drifted_sections:
        payload.update(
            {
                "status": "blocked",
                "blocked": True,
                "reason_code": "architecture_blueprint_projection_drift",
                "issues": drifted_sections,
            }
        )
        return payload
    return payload
