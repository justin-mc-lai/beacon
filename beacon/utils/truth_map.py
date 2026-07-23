"""Truth-map resolver center for v1.5.1+ Markdown-first requirement surfaces."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_requirement_file
from beacon.utils.feature_package import (
    _extract_ac_rows,
    _extract_evidence_rows,
    _extract_test_rows,
    _parse_checkboxes,
    _parse_frontmatter,
    _read_text,
    package_paths,
    validate_feature_package,
)
from beacon.utils.project_metadata import resolve_project_metadata_view, verify_project_metadata
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version

TRUTH_MAP_CONTRACT = "beacon-truth-map-v1"
TRUTH_SOURCE_MODEL = "feature_package_authoritative_ready"
TRUTH_SOURCE_MODEL_AUTHORITATIVE = "feature_package_authoritative"
TRUTH_PACKAGE_CONTRACT = "beacon-feature-package-v2"
MACHINE_JSON_ROLE = "generated_state_not_truth"
MACHINE_JSON_GENERATOR = "beacon.truth_map.resolver"
RUNTIME_JSON_ROLE = "runtime_process_record_not_requirement_truth"
VERSION_GOVERNANCE_TRUTH_ROLE = "version_governance_truth"
GENERATED_GOVERNANCE_STATE_ROLE = "generated_governance_state_not_truth"
GOVERNANCE_RESOLVER_MODE = "resolver_first"
TRUTH_CENTER_ROUTE_MODE = "truth_center_resolver"
LEGACY_EXCEPTION_CLASSIFICATION = "v1.5.1_legacy_exception"

FEATURE_SURFACES = ("truth", "tests", "tasks", "evidence")
VERSION_GOVERNANCE_SURFACES = {
    "project_governance": (
        "docs/beacon/governance/project-version-governance.md",
        VERSION_GOVERNANCE_TRUTH_ROLE,
        True,
    ),
    "global_boundaries": ("docs/beacon/global-boundaries.md", "global_governance_truth", True),
    "summary": ("docs/beacon/{version}/SUMMARY.md", VERSION_GOVERNANCE_TRUTH_ROLE, True),
    "execution_boundaries": ("docs/beacon/{version}/execution/boundaries.md", VERSION_GOVERNANCE_TRUTH_ROLE, True),
    "project_skill_blueprint": (
        "docs/beacon/{version}/execution/project-skill-qa-evolution-blueprint.md",
        VERSION_GOVERNANCE_TRUTH_ROLE,
        True,
    ),
    "source_architecture_index": ("docs/beacon/{version}/source-architecture/index.md", VERSION_GOVERNANCE_TRUTH_ROLE, True),
    "release_notes": ("docs/beacon/{version}/release/{version}.md", VERSION_GOVERNANCE_TRUTH_ROLE, True),
}
GENERATED_GOVERNANCE_SURFACES = {
    "version_feature_manifest": (
        "docs/beacon/{version}/.machine/manifest/version-features.json",
        GENERATED_GOVERNANCE_STATE_ROLE,
        False,
    ),
    "project_version_metadata": (
        ".beacon/metadata/project-version-metadata.json",
        GENERATED_GOVERNANCE_STATE_ROLE,
        False,
    ),
    "project_governance_sqlite_projection": (
        "{sqlite_runtime_ledger}",
        GENERATED_GOVERNANCE_STATE_ROLE,
        False,
    ),
    "evidence_manifest": (".beacon/evidence-manifest.json", GENERATED_GOVERNANCE_STATE_ROLE, False),
    "qa_status": (".beacon/qa/status.json", GENERATED_GOVERNANCE_STATE_ROLE, False),
    "release_gate_report": (".beacon/release-gate-report.json", GENERATED_GOVERNANCE_STATE_ROLE, False),
}
TRUTH_CENTER_ENTRYPOINT_INVENTORY = (
    {
        "path": "beacon/commands/prd.py",
        "surface": "prd_command",
        "entrypoint_kind": "truth_read_write_command",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/commands/user_story.py",
        "surface": "user_story_command",
        "entrypoint_kind": "truth_read_write_command",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/commands/test_case.py",
        "surface": "test_case_command",
        "entrypoint_kind": "truth_read_write_command",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/commands/workflow.py",
        "surface": "workflow_command",
        "entrypoint_kind": "lifecycle_gate_routing_surface",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/commands/truth.py",
        "surface": "truth_command",
        "entrypoint_kind": "direct_truth_command_surface",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/commands/gate.py",
        "surface": "gate_command",
        "entrypoint_kind": "gate_input_consumer",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/utils/prd_bootstrap.py",
        "surface": "prd_bootstrap",
        "entrypoint_kind": "bootstrap_truth_writer",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/utils/requirement_clarity.py",
        "surface": "requirement_clarity",
        "entrypoint_kind": "requirement_truth_consumer",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/utils/requirement_deepening.py",
        "surface": "requirement_deepening",
        "entrypoint_kind": "requirement_support_consumer",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/utils/manifest.py",
        "surface": "manifest",
        "entrypoint_kind": "generated_index_surface",
        "classification": "generated_state_exception",
        "exception_kind": "generated_governance_state",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "beacon/utils/acceptance_kit.py",
        "surface": "acceptance_kit",
        "entrypoint_kind": "acceptance_gate_input_consumer",
        "classification": "resolver_routed",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": "skills/beacon/**/SKILL.md",
        "surface": "packaged_skills",
        "entrypoint_kind": "llm_skill_guidance",
        "classification": "resolver_guidance_required",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
    {
        "path": ".agents/skills/**/SKILL.md",
        "surface": "project_agent_skills",
        "entrypoint_kind": "llm_skill_guidance",
        "classification": "resolver_guidance_required",
        "exception_kind": "",
        "fail_closed": True,
        "cutover_version": "v1.5.2",
    },
)


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def truth_map_supported(version: str | None) -> bool:
    """Truth-map is always active under current runtime (docs version is path-only)."""
    _ = version
    return True


def feature_package_ready(project_root: Path, *, version: str, feature: str) -> bool:
    paths = package_paths(project_root, version=version, feature=feature_slug(feature))
    return all(paths[surface].is_file() for surface in FEATURE_SURFACES)


def feature_package_present(project_root: Path, *, version: str, feature: str) -> bool:
    paths = package_paths(project_root, version=version, feature=feature_slug(feature))
    return paths["truth"].is_file()


def truth_map_supported_for_feature(project_root: Path, *, version: str, feature: str) -> bool:
    return truth_map_supported(version) or feature_package_ready(project_root, version=version, feature=feature)


def truth_source_model_for_version(version: str | None) -> str:
    """Active delivery always uses feature-package authority (global-boundaries §2.1).

    Product docs lines (e.g. v0.0.13) must not soft-downgrade to legacy split truth.
    """
    _ = version
    return TRUTH_SOURCE_MODEL_AUTHORITATIVE


def feature_package_authoritative(version: str | None) -> bool:
    """Package authority is always on for the installed runtime (docs version is not a downgrade switch)."""
    _ = version
    return True


def feature_package_authoritative_feature(project_root: Path, *, version: str, feature: str) -> bool:
    """Active runtime package authority; disk presence remains available for diagnostics."""
    if feature_package_authoritative(version):
        return True
    return feature_package_present(project_root, version=version, feature=feature)


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _format_version_path(template: str, version: str) -> str:
    if template == "{sqlite_runtime_ledger}":
        from beacon.utils.runtime_projection_store import runtime_ledger_db_path

        return str(runtime_ledger_db_path())
    return template.format(version=version)


def _governance_surface_spec(surface: str) -> tuple[str, str, bool]:
    if surface in VERSION_GOVERNANCE_SURFACES:
        return VERSION_GOVERNANCE_SURFACES[surface]
    if surface in GENERATED_GOVERNANCE_SURFACES:
        return GENERATED_GOVERNANCE_SURFACES[surface]
    raise ValueError(f"Unknown governance surface: {surface}")


def _surface_filename(surface: str) -> str:
    if surface not in FEATURE_SURFACES:
        raise ValueError(f"Unknown truth surface: {surface}")
    return f"{surface}.md"


def _source_paths(project_root: Path, *, version: str, feature: str) -> dict[str, str]:
    paths = package_paths(project_root, version=version, feature=feature)
    return {surface: _rel(project_root, paths[surface]) for surface in FEATURE_SURFACES}


def _source_hashes(project_root: Path, *, version: str, feature: str) -> dict[str, str]:
    paths = package_paths(project_root, version=version, feature=feature)
    return {surface: _sha256(paths[surface]) for surface in FEATURE_SURFACES}


def resolve_truth_surface(project_root: Path, *, version: str, feature: str, surface: str) -> dict[str, Any]:
    """Resolve one feature-package Markdown surface without consulting JSON projections."""

    slug = feature_slug(feature)
    paths = package_paths(project_root, version=version, feature=slug)
    filename = _surface_filename(surface)
    path = paths[surface]
    exists = path.exists()
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": truth_source_model_for_version(version),
        "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "surface": surface,
        "filename": filename,
        "path": _rel(project_root, path),
        "exists": exists,
        "source_hash": _sha256(path) if exists else "",
        "authority": "markdown_feature_package",
        "json_authority": False,
    }


def resolve_feature_truth(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """Resolve the feature package as the v1.5.1 canonical-ready truth read model."""

    slug = feature_slug(feature)
    paths = package_paths(project_root, version=version, feature=slug)
    truth = _read_text(paths["truth"])
    frontmatter, _body, frontmatter_errors = _parse_frontmatter(truth)
    sources = {
        surface: resolve_truth_surface(project_root, version=version, feature=slug, surface=surface)
        for surface in FEATURE_SURFACES
    }
    canonical_refs = frontmatter.get("canonical_refs") if isinstance(frontmatter.get("canonical_refs"), dict) else {}
    model = truth_source_model_for_version(version)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
        "machine_json_role": MACHINE_JSON_ROLE,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": "resolved" if all(item["exists"] for item in sources.values()) else "blocked",
        "truth_authority": "markdown_feature_package",
        "authority_state": model,
        "authority_flip_allowed": feature_package_authoritative(version),
        "json_authority": False,
        "frontmatter": frontmatter,
        "frontmatter_errors": frontmatter_errors,
        "canonical_refs": canonical_refs,
        "source_paths": _source_paths(project_root, version=version, feature=slug),
        "source_hashes": _source_hashes(project_root, version=version, feature=slug),
        "surfaces": sources,
    }


def resolve_governance_surface(project_root: Path, *, version: str, surface: str) -> dict[str, Any]:
    """Resolve one version governance surface through the truth-map resolver."""

    template, role, required = _governance_surface_spec(surface)
    rel_path = _format_version_path(template, version)
    path = Path(rel_path) if Path(rel_path).is_absolute() else project_root / rel_path
    is_generated = role == GENERATED_GOVERNANCE_STATE_ROLE
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": truth_source_model_for_version(version),
        "resolver_mode": GOVERNANCE_RESOLVER_MODE,
        "version": version,
        "surface": surface,
        "path": rel_path,
        "exists": path.exists(),
        "required": required,
        "role": role,
        "authority": role if not is_generated else GENERATED_GOVERNANCE_STATE_ROLE,
        "truth_authority": not is_generated,
        "json_authority": False,
        "generated_governance_state": is_generated,
        "source_hash": _sha256(path) if path.exists() else "",
    }


def _generated_governance_state_diagnostics(project_root: Path, surface_payload: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    if not surface_payload.get("exists"):
        return diagnostics
    rel_path = str(surface_payload.get("path") or "")
    path = project_root / rel_path
    if path.suffix.lower() != ".json":
        return diagnostics
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        diagnostics.append({"severity": "error", "code": "generated_governance_state_unreadable", "path": rel_path})
        return diagnostics
    authority = str(payload.get("authority") or payload.get("role") or "").strip().lower()
    if payload.get("truth_authority") is True or payload.get("json_authority") is True or authority in {"truth", "authority"}:
        diagnostics.append(
            {
                "severity": "error",
                "code": "generated_governance_state_claims_truth_authority",
                "path": rel_path,
            }
        )
    return diagnostics


def resolve_version_governance(project_root: Path, *, version: str) -> dict[str, Any]:
    """Resolve version-level governance truth and generated governance state."""

    truth_surfaces = {
        surface: resolve_governance_surface(project_root, version=version, surface=surface)
        for surface in VERSION_GOVERNANCE_SURFACES
    }
    generated_surfaces = {
        surface: resolve_governance_surface(project_root, version=version, surface=surface)
        for surface in GENERATED_GOVERNANCE_SURFACES
    }
    diagnostics: list[dict[str, Any]] = []
    for surface, payload in truth_surfaces.items():
        if payload.get("required") and not payload.get("exists"):
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "version_governance_truth_missing",
                    "surface": surface,
                    "path": payload.get("path", ""),
                }
            )
    for payload in generated_surfaces.values():
        diagnostics.extend(_generated_governance_state_diagnostics(project_root, payload))
    has_errors = any(item.get("severity") == "error" for item in diagnostics)
    model = truth_source_model_for_version(version)
    from beacon.utils.project_governance import GOVERNANCE_JSON_REL, GOVERNANCE_MD_REL
    from beacon.utils.runtime_projection_store import runtime_ledger_db_path

    governance_md_rel = str(GOVERNANCE_MD_REL)
    projection_roles = {
        "canonical_commit_surface": governance_md_rel,
        "canonical_role": VERSION_GOVERNANCE_TRUTH_ROLE,
        "sqlite_projection_surface": "project_governance_sqlite_projection",
        "sqlite_projection_role": GENERATED_GOVERNANCE_STATE_ROLE,
        "sqlite_ledger_path": str(runtime_ledger_db_path()),
        "deprecated_legacy_json": str(GOVERNANCE_JSON_REL),
        "write_direction": "governance_md_to_sqlite_only",
    }
    dual_role_offenders = [
        surface
        for surface, payload in generated_surfaces.items()
        if str(payload.get("path") or "").replace("\\", "/") == governance_md_rel
    ]
    if dual_role_offenders:
        diagnostics.append(
            {
                "severity": "error",
                "code": "governance_md_dual_role",
                "surfaces": dual_role_offenders,
                "path": governance_md_rel,
            }
        )
        has_errors = True
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "resolver_mode": GOVERNANCE_RESOLVER_MODE,
        "version": version,
        "status": "blocked" if has_errors else "pass",
        "blocked": has_errors,
        "authority_classification": {
            "feature_truth": "markdown_feature_package",
            "feature_truth_model": model,
            "version_governance_truth": VERSION_GOVERNANCE_TRUTH_ROLE,
            "generated_governance_state": GENERATED_GOVERNANCE_STATE_ROLE,
            "runtime_process_record": RUNTIME_JSON_ROLE,
        },
        "governance_projection_roles": projection_roles,
        "truth_surfaces": truth_surfaces,
        "generated_state_surfaces": generated_surfaces,
        "manifest_authority": False,
        "json_authority": False,
        "diagnostics": diagnostics,
    }


def resolve_truth_read_refs(project_root: Path, *, version: str, feature: str, consumer: str) -> dict[str, Any]:
    """Resolve normal truth read references through truth_center without flipping v1.5.1 authority."""

    slug = feature_slug(feature)
    model = truth_source_model_for_version(version)
    source_refs = _source_paths(project_root, version=version, feature=slug)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "route_mode": TRUTH_CENTER_ROUTE_MODE,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "consumer": consumer,
        "authority_state": model,
        "authority_flip_allowed": feature_package_authoritative(version),
        "source_refs": source_refs,
        "requirement_refs": {
            "source_of_truth_root": f"docs/beacon/{version}/features/{slug}",
            "prd": source_refs["truth"],
            "user_story": source_refs["truth"],
            "test_case": source_refs["tests"],
            "truth": source_refs["truth"],
            "tests": source_refs["tests"],
            "tasks": source_refs["tasks"],
            "evidence": source_refs["evidence"],
        },
        "json_authority": False,
    }


def resolve_truth_write_target(
    project_root: Path,
    *,
    version: str,
    feature: str,
    surface: str,
    producer: str,
) -> dict[str, Any]:
    """Resolve a truth write target through truth_center while keeping CLI validation authoritative."""

    resolved = resolve_truth_surface(project_root, version=version, feature=feature, surface=surface)
    model = truth_source_model_for_version(version)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "route_mode": TRUTH_CENTER_ROUTE_MODE,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "producer": producer,
        "surface": surface,
        "target_path": resolved["path"],
        "authority_state": model,
        "authority_flip_allowed": feature_package_authoritative(version),
        "requires_cli_validation": True,
        "json_authority": False,
    }


def resolve_gate_inputs(project_root: Path, *, version: str, feature: str, gate: str) -> dict[str, Any]:
    """Resolve gate inputs through truth_center and include governance truth classification."""

    slug = feature_slug(feature)
    model = truth_source_model_for_version(version)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "route_mode": TRUTH_CENTER_ROUTE_MODE,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "gate": gate,
        "feature_truth": resolve_feature_truth(project_root, version=version, feature=slug),
        "version_governance": resolve_version_governance(project_root, version=version),
        "authority_state": model,
        "authority_flip_allowed": feature_package_authoritative(version),
        "json_authority": False,
    }


def resolve_legacy_rebuild_targets(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """Reserve legacy triptych rebuild targets behind truth_center fail-closed routing."""

    slug = feature_slug(feature)
    base = f"docs/beacon/{version}"
    model = truth_source_model_for_version(version)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "route_mode": TRUTH_CENTER_ROUTE_MODE,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": "legacy_output_only" if feature_package_authoritative(version) else "reserved_fail_closed",
        "authority_state": model,
        "authority_flip_allowed": feature_package_authoritative(version),
        "legacy_authority": False,
        "source_refs": _source_paths(project_root, version=version, feature=slug),
        "targets": {
            "prd": f"{base}/prd/{slug}.md",
            "user_story": f"{base}/user-story/{slug}.md",
            "test_case": f"{base}/qa/test-cases/{slug}.md",
        },
        "json_authority": False,
    }


def resolve_legacy_absorb_targets(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """Reserve legacy triptych absorb targets behind truth_center fail-closed routing."""

    slug = feature_slug(feature)
    base = f"docs/beacon/{version}"
    model = truth_source_model_for_version(version)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "route_mode": TRUTH_CENTER_ROUTE_MODE,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": "package_truth_target_only" if feature_package_authoritative(version) else "reserved_fail_closed",
        "authority_state": model,
        "authority_flip_allowed": feature_package_authoritative(version),
        "legacy_authority": False,
        "source_refs": {
            "prd": f"{base}/prd/{slug}.md",
            "user_story": f"{base}/user-story/{slug}.md",
            "test_case": f"{base}/qa/test-cases/{slug}.md",
        },
        "targets": _source_paths(project_root, version=version, feature=slug),
        "json_authority": False,
    }


def _inventory_path_exists(project_root: Path, pattern: str) -> bool:
    if "**" in pattern or "*" in pattern:
        return any(project_root.glob(pattern))
    return (project_root / pattern).exists()


def _inventory_entry(project_root: Path, row: dict[str, Any]) -> dict[str, Any]:
    classification = str(row.get("classification") or "").strip()
    routed = classification in {TRUTH_CENTER_ROUTE_MODE, "resolver_routed", "resolver_guidance_required"}
    explicit_exception = classification in {
        LEGACY_EXCEPTION_CLASSIFICATION,
        "generated_state_exception",
        "runtime_process_record_exception",
    }
    return {
        "path": row["path"],
        "surface": row["surface"],
        "entrypoint_kind": row["entrypoint_kind"],
        "classification": classification,
        "exception_kind": row.get("exception_kind", ""),
        "exists": _inventory_path_exists(project_root, str(row["path"])),
        "truth_center_routed": routed,
        "explicit_v151_exception": explicit_exception,
        "fail_closed": bool(row.get("fail_closed")),
        "cutover_version": row.get("cutover_version", "v1.5.2"),
    }


def _inventory_entry_for_version(project_root: Path, row: dict[str, Any], *, version: str) -> dict[str, Any]:
    entry = _inventory_entry(project_root, row)
    if not feature_package_authoritative(version):
        return entry
    if entry["classification"] == LEGACY_EXCEPTION_CLASSIFICATION:
        entry["classification"] = "cutover_required"
        entry["explicit_v151_exception"] = False
        entry["truth_center_routed"] = False
        entry["cutover_violation"] = True
    else:
        entry["cutover_violation"] = False
    return entry


def resolve_truth_entrypoint_inventory(project_root: Path, *, version: str) -> dict[str, Any]:
    """Resolve the AC-026 high-risk truth entrypoint inventory."""

    entries = [_inventory_entry_for_version(project_root, dict(row), version=version) for row in TRUTH_CENTER_ENTRYPOINT_INVENTORY]
    diagnostics: list[dict[str, Any]] = []
    for entry in entries:
        if not entry["exists"]:
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "truth_entrypoint_inventory_missing",
                    "path": entry["path"],
                }
            )
        if not entry["truth_center_routed"] and not entry["explicit_v151_exception"]:
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "truth_entrypoint_legacy_exception_not_allowed"
                    if entry.get("cutover_violation")
                    else "truth_entrypoint_inventory_unclassified",
                    "path": entry["path"],
                    "classification": entry["classification"],
                }
            )
        if entry["explicit_v151_exception"] and (not entry["fail_closed"] or not entry["cutover_version"]):
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "truth_entrypoint_exception_contract_missing",
                    "path": entry["path"],
                }
            )
    has_errors = any(item.get("severity") == "error" for item in diagnostics)
    model = truth_source_model_for_version(version)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "route_mode": TRUTH_CENTER_ROUTE_MODE,
        "version": version,
        "status": "blocked" if has_errors else "pass",
        "blocked": has_errors,
        "authority_state": model,
        "authority_flip_allowed": feature_package_authoritative(version),
        "required_entrypoint_count": len(entries),
        "entries": entries,
        "diagnostics": diagnostics,
    }


def verify_truth_entrypoint_inventory(project_root: Path, *, version: str, strict: bool = False) -> dict[str, Any]:
    """Verify every AC-026 inventory row is present and classified."""

    payload = resolve_truth_entrypoint_inventory(project_root, version=version)
    has_errors = any(item.get("severity") == "error" for item in payload.get("diagnostics", []))
    return {
        **payload,
        "status": "blocked" if has_errors else "pass",
        "blocked": has_errors if strict else bool(payload.get("blocked")),
    }


def verify_governance_truth(project_root: Path, *, version: str, strict: bool = False) -> dict[str, Any]:
    """Verify version governance truth and generated governance state do not become authority."""

    payload = resolve_version_governance(project_root, version=version)
    diagnostics = list(payload.get("diagnostics") or [])
    has_errors = any(item.get("severity") == "error" for item in diagnostics)
    status = "blocked" if has_errors else "pass"
    if strict and has_errors:
        status = "blocked"
    return {
        **payload,
        "status": status,
        "blocked": has_errors,
        "diagnostics": diagnostics,
    }


def _branch_contract_checks(metadata_verdict: dict[str, Any]) -> list[dict[str, Any]]:
    checks = metadata_verdict.get("checks") if isinstance(metadata_verdict.get("checks"), list) else []
    return [
        item
        for item in checks
        if isinstance(item, dict) and str(item.get("name", "") or "").startswith("branch_contract:")
    ]


def _selected_metadata_branch_contract(metadata_view: dict[str, Any]) -> dict[str, Any]:
    selected_service = str(metadata_view.get("selected_service") or "").strip()
    selected_branch = str(metadata_view.get("selected_branch") or "").strip()
    binding = metadata_view.get("selected_service_binding")
    binding = binding if isinstance(binding, dict) else {}
    return {
        "selected_service": selected_service,
        "selected_branch": selected_branch,
        "repo_root": str(binding.get("repo_root") or "").strip(),
    }


def _current_branch_for_selected_service(metadata_verdict: dict[str, Any], selected_service: str) -> str:
    for check in _branch_contract_checks(metadata_verdict):
        if str(check.get("name", "") or "") != f"branch_contract:{selected_service}":
            continue
        details = check.get("details") if isinstance(check.get("details"), dict) else {}
        return str(details.get("current_branch") or "").strip()
    return ""


def _metadata_repair_commands(
    project_root: Path,
    *,
    version: str,
    feature: str,
    metadata_contract: dict[str, Any],
    current_branch: str,
) -> list[str]:
    root = str(project_root)
    selected_service = str(metadata_contract.get("selected_service") or "").strip()
    repo_root = str(metadata_contract.get("repo_root") or "").strip() or root
    commands = [
        f"beacon doctor metadata verify --project-root {root} --version {version} --json",
    ]
    if selected_service and current_branch:
        commands.append(
            " ".join(
                [
                    "beacon doctor metadata update",
                    f"--project-root {root}",
                    f"--service-key {selected_service}",
                    f"--repo-root {repo_root}",
                    f"--version {version}",
                    f"--branch {current_branch}",
                    "--json",
                ]
            )
        )
    commands.append(
        f'beacon implement sync-git-workflow "{feature_slug(feature)}" --project-root {root} --version {version} --force-from-seed --json'
    )
    return commands


def evaluate_implement_version_governance_preflight(
    project_root: Path,
    *,
    version: str,
    feature: str,
    git_workflow: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fail closed before implement planning/execution when version governance branch truth drifts."""

    root = project_root.expanduser().resolve()
    slug = feature_slug(feature)
    if not truth_map_supported(version):
        return {
            "schema_version": "1.0",
            "truth_map_contract": TRUTH_MAP_CONTRACT,
            "feature": feature,
            "feature_slug": slug,
            "version": version,
            "status": "not_applicable",
            "blocked": False,
            "reason_code": "",
            "supported": False,
            "diagnostics": [],
        }
    governance = verify_governance_truth(root, version=version, strict=True)
    metadata_verdict = verify_project_metadata(root, version=version)
    metadata_view = resolve_project_metadata_view(root, version=version)
    metadata_contract = _selected_metadata_branch_contract(metadata_view)
    selected_service = str(metadata_contract.get("selected_service") or "").strip()
    selected_branch = str(metadata_contract.get("selected_branch") or "").strip()
    current_branch = _current_branch_for_selected_service(metadata_verdict, selected_service)
    workflow = git_workflow if isinstance(git_workflow, dict) else {}
    workflow_expected_branch = str(workflow.get("expected_branch") or "").strip()
    repair_commands = _metadata_repair_commands(
        root,
        version=version,
        feature=slug,
        metadata_contract=metadata_contract,
        current_branch=current_branch,
    )
    diagnostics: list[dict[str, Any]] = []
    reason_code = ""

    from beacon.utils.project_governance import governance_md_authoritative

    version_contract = (
        metadata_view.get("version_contract")
        if isinstance(metadata_view.get("version_contract"), dict)
        else {}
    )
    participating = (
        version_contract.get("participating_services")
        if isinstance(version_contract.get("participating_services"), list)
        else []
    )
    per_service = (
        version_contract.get("per_service_canonical_branch")
        if isinstance(version_contract.get("per_service_canonical_branch"), dict)
        else {}
    )
    if governance_md_authoritative(root) and (not participating or not per_service):
        reason_code = "governance_version_not_registered"
        diagnostics.append(
            {
                "severity": "error",
                "code": reason_code,
                "message": (
                    "project-version-governance has no participating_services/"
                    "per_service_canonical_branch for this version"
                ),
                "recommended_command": (
                    f'beacon doctor metadata update --project-root {root} '
                    f'--version {version} --service-key <service> --branch feature/{version} '
                    f'--truth-canonical main --json'
                ),
            }
        )
        blocked = True
        return {
            "schema_version": "1.0",
            "truth_map_contract": TRUTH_MAP_CONTRACT,
            "truth_source_model": TRUTH_SOURCE_MODEL,
            "resolver_mode": GOVERNANCE_RESOLVER_MODE,
            "feature": feature,
            "feature_slug": slug,
            "version": version,
            "status": "blocked",
            "blocked": blocked,
            "reason_code": reason_code,
            "metadata_branch_contract": {
                **metadata_contract,
                "current_branch": current_branch,
            },
            "git_workflow_branch_contract": {
                "expected_branch": workflow_expected_branch,
                "source": str(workflow.get("source") or ""),
                "path": str(workflow.get("path") or ""),
            },
            "version_governance": governance,
            "project_metadata_verification": metadata_verdict,
            "diagnostics": diagnostics,
            "recommended_command": diagnostics[0]["recommended_command"],
            "repair_commands": [diagnostics[0]["recommended_command"], *repair_commands],
        }

    from beacon.utils.version_truth_catalog import evaluate_catalog_delivery_preflight

    catalog_preflight = evaluate_catalog_delivery_preflight(root, version=version)
    if catalog_preflight.get("blocked"):
        reason_code = str(catalog_preflight.get("reason_code") or "version_not_on_active_delivery_plane")
        diagnostics.append(
            {
                "severity": "error",
                "code": reason_code,
                "message": "version is not on the catalog active delivery plane",
                "validation_state": catalog_preflight.get("validation_state", ""),
            }
        )

    if governance.get("blocked") and not reason_code:
        governance_codes = {
            str(item.get("code") or "").strip()
            for item in governance.get("diagnostics", [])
            if isinstance(item, dict)
        }
        reason_code = (
            "implement_version_governance_missing"
            if "version_governance_truth_missing" in governance_codes
            else "implement_version_governance_generated_state_stale"
        )
        diagnostics.append(
            {
                "severity": "error",
                "code": reason_code,
                "message": "version governance resolver did not pass before implement",
            }
        )

    admission_satisfied = False
    try:
        from beacon.utils.workspace_admission import load_admission_contract, validate_workspace_admission

        admission_contract = load_admission_contract(root, version=version)
        if admission_contract.get("require_workspace_admission"):
            admission_validation = validate_workspace_admission(
                root,
                version=version,
                feature=feature,
                cwd=root,
                contract=admission_contract,
            )
            admission_satisfied = bool(admission_validation.get("valid"))
    except Exception:  # noqa: BLE001
        admission_satisfied = False

    if not reason_code and str(metadata_verdict.get("status") or "") == "fail":
        failing_checks = [
            item
            for item in (metadata_verdict.get("checks") or [])
            if isinstance(item, dict) and str(item.get("status") or "") == "fail"
        ]
        branch_failures = [item for item in _branch_contract_checks(metadata_verdict) if item.get("status") == "fail"]
        non_branch_failures = [
            item
            for item in failing_checks
            if not str(item.get("name", "") or "").startswith("branch_contract:")
        ]
        if admission_satisfied and failing_checks and not non_branch_failures:
            failing_checks = []
            branch_failures = []
        if branch_failures:
            reason_code = "implement_metadata_branch_mismatch"
            diagnostics.append(
                {
                    "severity": "error",
                    "code": reason_code,
                    "message": "project metadata branch contract failed before implement",
                    "branch_failures": branch_failures,
                }
            )
        elif non_branch_failures:
            reason_code = "implement_metadata_contract_blocked"
            diagnostics.append(
                {
                    "severity": "error",
                    "code": reason_code,
                    "message": "project metadata contract failed before implement",
                    "metadata_failures": non_branch_failures,
                }
            )

    if (
        not reason_code
        and selected_branch
        and workflow_expected_branch
        and workflow_expected_branch != selected_branch
        # Per-feature worktrees use next_version_feature_branch under runtime_mirror
        # (e.g. selected=beacon/v2.0.0, expected=beacon/v2.0.0/<feature-slug>).
        and not str(workflow_expected_branch).startswith(str(selected_branch).rstrip("/") + "/")
    ):
        reason_code = "implement_git_workflow_metadata_drift"
        diagnostics.append(
            {
                "severity": "error",
                "code": reason_code,
                "message": "git workflow expected branch differs from project metadata selected branch",
                "metadata_selected_branch": selected_branch,
                "git_workflow_expected_branch": workflow_expected_branch,
            }
        )

    blocked = bool(reason_code)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": TRUTH_SOURCE_MODEL,
        "resolver_mode": GOVERNANCE_RESOLVER_MODE,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": reason_code,
        "metadata_branch_contract": {
            **metadata_contract,
            "current_branch": current_branch,
        },
        "git_workflow_branch_contract": {
            "expected_branch": workflow_expected_branch,
            "source": str(workflow.get("source") or ""),
            "path": str(workflow.get("path") or ""),
        },
        "version_governance": governance,
        "catalog_delivery_preflight": catalog_preflight,
        "project_metadata_verification": metadata_verdict,
        "diagnostics": diagnostics,
        "recommended_command": repair_commands[0],
        "repair_commands": repair_commands,
    }


def resolve_machine_json_plan(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """Return resolver-owned requirement-derived machine JSON outputs."""

    slug = feature_slug(feature)
    model = truth_source_model_for_version(version)
    outputs = {
        "truth_map_projection": machine_requirement_file(project_root, version, f"{slug}.truth-map.json"),
        "requirement_package_state": machine_requirement_file(project_root, version, f"{slug}.requirement-package.json"),
        "feature_package_validation": machine_requirement_file(project_root, version, "feature-package-validation.json"),
    }
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
        "machine_json_role": MACHINE_JSON_ROLE,
        "generated_by": MACHINE_JSON_GENERATOR,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "source_paths": _source_paths(project_root, version=version, feature=slug),
        "outputs": {name: _rel(project_root, path) for name, path in outputs.items()},
        "runtime_json_exemption": {
            "role": RUNTIME_JSON_ROLE,
            "applies_to": [".beacon/runs/**", ".beacon/qa/**", "runtime/process execution records"],
            "requires_markdown_twin": False,
            "requirement_authority": False,
        },
        "routes": {
            "doctor_rebuild": {
                "status": "legacy_output_only" if feature_package_authoritative(version) else "reserved_fail_closed",
                "command": f"beacon truth-map rebuild-machine {slug} --version {version}",
            },
            "change_absorb": {
                "status": "package_truth_target_only" if feature_package_authoritative(version) else "reserved_fail_closed",
                "command": f"beacon change {slug} --version {version} --reason absorb-legacy-truth-into-feature-package",
            },
        },
    }


def resolve_truth_map(project_root: Path, *, version: str, feature: str | None = None) -> dict[str, Any]:
    """Resolve truth-map metadata from static resolver code and Markdown sources."""

    slug = feature_slug(feature) if feature else ""
    model = truth_source_model_for_version(version)
    supported = (
        truth_map_supported_for_feature(project_root, version=version, feature=slug)
        if slug
        else truth_map_supported(version)
    )
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
        "machine_json_role": MACHINE_JSON_ROLE,
        "runtime_json_role": RUNTIME_JSON_ROLE,
        "governance_state_role": GENERATED_GOVERNANCE_STATE_ROLE,
        "governance_resolver_mode": GOVERNANCE_RESOLVER_MODE,
        "version": version,
        "supported": supported,
        "truth_map_json_authority": False,
        "json_authority": False,
        "authority_source": "cli_static_resolver_plus_markdown_feature_package",
        "authority_state": model,
        "authority_flip_allowed": feature_package_authoritative(version),
    }
    if slug:
        payload["feature"] = feature
        payload["feature_slug"] = slug
        payload["feature_truth"] = resolve_feature_truth(project_root, version=version, feature=slug)
        payload["machine_json_plan"] = resolve_machine_json_plan(project_root, version=version, feature=slug)
    if truth_map_supported(version):
        payload["version_governance"] = resolve_version_governance(project_root, version=version)
        payload["entrypoint_inventory"] = resolve_truth_entrypoint_inventory(project_root, version=version)
    return payload


def _requirement_package_state(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    slug = feature_slug(feature)
    paths = package_paths(project_root, version=version, feature=slug)
    truth_md = _read_text(paths["truth"])
    tests_md = _read_text(paths["tests"])
    tasks_md = _read_text(paths["tasks"])
    evidence_md = _read_text(paths["evidence"])
    frontmatter, _body, frontmatter_errors = _parse_frontmatter(truth_md)
    checkbox_rows, checkbox_errors = _parse_checkboxes(tasks_md)
    model = truth_source_model_for_version(version)
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
        "machine_json_role": MACHINE_JSON_ROLE,
        "generated_by": MACHINE_JSON_GENERATOR,
        "generated_at": now_iso(),
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "truth_authority": False,
        "json_authority": False,
        "source_paths": _source_paths(project_root, version=version, feature=slug),
        "source_hashes": _source_hashes(project_root, version=version, feature=slug),
        "truth_frontmatter": frontmatter,
        "frontmatter_errors": frontmatter_errors,
        "acceptance_criteria": _extract_ac_rows(truth_md),
        "test_rows": _extract_test_rows(tests_md),
        "task_rows": checkbox_rows,
        "checkbox_errors": checkbox_errors,
        "evidence_rows": _extract_evidence_rows(evidence_md),
    }


def rebuild_machine_json(project_root: Path, *, version: str, feature: str, strict: bool = False) -> dict[str, Any]:
    """Regenerate requirement-derived machine JSON from resolver-selected Markdown."""

    slug = feature_slug(feature)
    model = truth_source_model_for_version(version)
    plan = resolve_machine_json_plan(project_root, version=version, feature=slug)
    validation = validate_feature_package(project_root, version=version, feature=slug, write_report=True)
    if strict and validation.get("blocked"):
        return {
            "schema_version": "1.0",
            "truth_map_contract": TRUTH_MAP_CONTRACT,
            "feature": feature,
            "feature_slug": slug,
            "version": version,
            "status": "blocked",
            "blocked": True,
            "reason_code": "feature_package_validation_failed",
            "validation": validation,
            "written": [],
        }

    truth_map_projection = resolve_truth_map(project_root, version=version, feature=slug)
    truth_map_projection.update(
        {
            "machine_json_role": MACHINE_JSON_ROLE,
            "generated_by": MACHINE_JSON_GENERATOR,
            "generated_at": now_iso(),
            "truth_authority": False,
            "source_paths": _source_paths(project_root, version=version, feature=slug),
            "source_hashes": _source_hashes(project_root, version=version, feature=slug),
        }
    )
    requirement_state = _requirement_package_state(project_root, version=version, feature=slug)

    outputs = plan["outputs"]
    truth_map_path = project_root / outputs["truth_map_projection"]
    requirement_path = project_root / outputs["requirement_package_state"]
    write_json(truth_map_path, truth_map_projection)
    write_json(requirement_path, requirement_state)

    written = [outputs["truth_map_projection"], outputs["requirement_package_state"]]
    if validation.get("report_path"):
        written.append(str(validation["report_path"]))
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
        "machine_json_role": MACHINE_JSON_ROLE,
        "generated_by": MACHINE_JSON_GENERATOR,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": "rebuilt",
        "blocked": False,
        "validation_status": validation.get("status"),
        "source_paths": _source_paths(project_root, version=version, feature=slug),
        "source_hashes": _source_hashes(project_root, version=version, feature=slug),
        "plan": plan,
        "written": written,
    }


def is_runtime_json_exempt(path: Path | str) -> bool:
    text = str(path)
    return "/.beacon/runs/" in text or "/.beacon/qa/" in text or "/runtime/" in text or "/process/" in text


def _verify_machine_payload(
    project_root: Path,
    *,
    path: Path,
    current_hashes: dict[str, str],
) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    rel = _rel(project_root, path)
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        return [{"severity": "error", "code": "machine_json_unreadable", "path": rel}]
    if payload.get("generated_by") != MACHINE_JSON_GENERATOR:
        diagnostics.append({"severity": "error", "code": "machine_json_not_resolver_generated", "path": rel})
    if payload.get("machine_json_role") != MACHINE_JSON_ROLE:
        diagnostics.append({"severity": "error", "code": "machine_json_role_mismatch", "path": rel})
    if payload.get("truth_map_contract") != TRUTH_MAP_CONTRACT:
        diagnostics.append({"severity": "error", "code": "machine_json_contract_mismatch", "path": rel})
    recorded_hashes = payload.get("source_hashes") if isinstance(payload.get("source_hashes"), dict) else {}
    if recorded_hashes != current_hashes:
        diagnostics.append(
            {
                "severity": "error",
                "code": "machine_json_source_hash_stale",
                "path": rel,
                "expected": current_hashes,
                "actual": recorded_hashes,
            }
        )
    if payload.get("truth_authority") is True or payload.get("json_authority") is True:
        diagnostics.append({"severity": "error", "code": "machine_json_claims_truth_authority", "path": rel})
    return diagnostics


def verify_truth_map(project_root: Path, *, version: str, feature: str, strict: bool = False) -> dict[str, Any]:
    """Verify resolver/package alignment and existing resolver-owned machine JSON freshness."""

    slug = feature_slug(feature)
    diagnostics: list[dict[str, Any]] = []
    resolved = resolve_feature_truth(project_root, version=version, feature=slug)
    validation = validate_feature_package(project_root, version=version, feature=slug, write_report=False)
    model = truth_source_model_for_version(version)

    if not truth_map_supported_for_feature(project_root, version=version, feature=slug):
        diagnostics.append({"severity": "error", "code": "truth_map_unsupported_version", "version": version})
    if resolved.get("status") != "resolved":
        diagnostics.append({"severity": "error", "code": "feature_package_not_resolved"})
    for item in validation.get("diagnostics", []):
        if item.get("severity") == "error":
            diagnostics.append(item)

    plan = resolve_machine_json_plan(project_root, version=version, feature=slug)
    current_hashes = _source_hashes(project_root, version=version, feature=slug)
    checked_machine_json: list[str] = []
    for name, rel_path in plan.get("outputs", {}).items():
        path = project_root / rel_path
        if not path.exists():
            continue
        checked_machine_json.append(rel_path)
        if name == "feature_package_validation":
            validation_payload = read_json(path, {})
            validation_feature = str(
                (validation_payload.get("feature_slug") if isinstance(validation_payload, dict) else "")
                or (validation_payload.get("feature") if isinstance(validation_payload, dict) else "")
                or ""
            ).strip()
            if validation_feature and feature_slug(validation_feature) != slug:
                continue
            validation_hashes = (
                validation_payload.get("source_hashes")
                if isinstance(validation_payload, dict) and isinstance(validation_payload.get("source_hashes"), dict)
                else {}
            )
            if validation_hashes and validation_hashes != current_hashes:
                diagnostics.append(
                    {
                        "severity": "error",
                        "code": "machine_json_source_hash_stale",
                        "path": rel_path,
                        "expected": current_hashes,
                        "actual": validation_hashes,
                    }
                )
            continue
        diagnostics.extend(_verify_machine_payload(project_root, path=path, current_hashes=current_hashes))

    has_errors = any(item.get("severity") == "error" for item in diagnostics)
    status = "blocked" if has_errors else "pass"
    if strict and has_errors:
        status = "blocked"
    return {
        "schema_version": "1.0",
        "truth_map_contract": TRUTH_MAP_CONTRACT,
        "truth_source_model": model,
        "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
        "machine_json_role": MACHINE_JSON_ROLE,
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": status,
        "blocked": has_errors,
        "truth_authority": "markdown_feature_package",
        "json_authority": False,
        "source_paths": _source_paths(project_root, version=version, feature=slug),
        "source_hashes": current_hashes,
        "checked_machine_json": checked_machine_json,
        "runtime_json_exemption": resolve_machine_json_plan(project_root, version=version, feature=slug)["runtime_json_exemption"],
        "validation_status": validation.get("status"),
        "diagnostics": diagnostics,
    }
