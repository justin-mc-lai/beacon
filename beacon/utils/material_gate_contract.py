"""v1.4.8 material gate and human subskill writeback contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.artifact_update_obligations import blocking_obligations, load_artifact_update_obligations
from beacon.utils.delivery_baseline import (
    architecture_blueprint_path,
    implementation_delivery_baseline_path,
    load_implementation_delivery_baseline,
    validate_architecture_blueprint_projection,
)
from beacon.utils.runtime import read_json
from beacon.utils.story_state import feature_slug
from beacon.utils.technical_review_contract import load_technical_review_contract
from beacon.utils.versioning import release_line_key, resolve_target_version


ALLOWED_MATERIAL_EFFECTS = (
    "writeback_completed",
    "writeback_required",
    "obligation_opened",
    "truth_reopen_required",
    "execution_host_update_required",
    "evidence_update_required",
    "read_only_route_only",
)

MATERIAL_EFFECT_FAMILIES = {
    "host": ("using-beacon", "beacon-help", "beacon-status", "beacon-doctor"),
    "truth": ("beacon-change", "beacon-prd", "beacon-user-story", "beacon-test-case", "beacon-change-refreeze"),
    "execution": ("beacon-prototype", "beacon-implement"),
    "gate": ("beacon-qa", "beacon-release"),
    "support": (
        "beacon-brainstorm",
        "beacon-context-engineering",
        "beacon-source-driven",
        "beacon-doubt-review",
        "beacon-security-review",
        "beacon-performance-review",
        "beacon-documentation-adr",
        "beacon-debug-recovery",
        "beacon-ceo-review",
        "beacon-design-review",
        "beacon-deep",
        "beacon-learn",
    ),
    "toolkit": (
        "beacon-toolkit-branch-governance",
        "beacon-toolkit-automation",
        "beacon-toolkit-lighthouse",
        "beacon-toolkit-metadata",
    ),
    "compatibility": ("beacon-friction-intake", "beacon-real-project-validation", "beacon-archive"),
    "project-local": ("project-local-skill",),
}

READ_ONLY_SUPPORT_SKILLS = {
    "beacon-brainstorm",
    "beacon-context-engineering",
    "beacon-source-driven",
    "beacon-doubt-review",
    "beacon-security-review",
    "beacon-performance-review",
    "beacon-documentation-adr",
    "beacon-debug-recovery",
    "beacon-ceo-review",
    "beacon-design-review",
    "beacon-deep",
    "beacon-learn",
}

WEAK_FACT_SOURCES = {"version_default", "project_config_seed"}


def material_gate_supported(version: str | None) -> bool:
    normalized = release_line_key(version) or ""
    if not normalized:
        return False
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch)) >= (1, 4, 8)
    except Exception:  # noqa: BLE001
        return False


def execution_host_required_surfaces(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    refs = {
        "execution_index": project_root / "docs" / "beacon" / resolved_version / "execution" / "index.md",
        "architecture_blueprint": architecture_blueprint_path(project_root, resolved_version),
        "delivery_baseline": implementation_delivery_baseline_path(project_root, resolved_version, feature),
        "git_workflow": project_root / "docs" / "beacon" / resolved_version / ".machine" / "execution" / f"git-workflow-{slug}.json",
        "technical_review_contract": project_root
        / "docs"
        / "beacon"
        / resolved_version
        / ".machine"
        / "execution"
        / f"deterministic-implementation-contract-{slug}.json",
    }
    surfaces = {
        name: {
            "path": str(path.relative_to(project_root)),
            "exists": path.exists(),
            "required": True,
        }
        for name, path in refs.items()
    }
    missing = [name for name, row in surfaces.items() if not bool(row["exists"])]
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "feature": feature,
        "feature_slug": slug,
        "required": True,
        "status": "blocked" if missing else "pass",
        "blocked": bool(missing),
        "reason_code": "execution_host_required_surface_missing" if missing else "",
        "missing_surfaces": missing,
        "surfaces": surfaces,
    }


def _service_branch_map_complete(baseline: dict[str, Any]) -> bool:
    direct = [str(item).strip() for item in baseline.get("direct_delivery_services", []) if str(item).strip()] if isinstance(baseline.get("direct_delivery_services"), list) else []
    mapping = baseline.get("service_branch_map") if isinstance(baseline.get("service_branch_map"), dict) else {}
    return bool(direct) and all(str(mapping.get(service) or "").strip() for service in direct)


def explicit_delivery_fact_gate(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    contract = load_technical_review_contract(project_root, version=resolved_version, feature=feature)
    baseline = load_implementation_delivery_baseline(project_root, version=resolved_version, feature=feature)
    diagnostics: list[dict[str, Any]] = []
    for field in ("target_branch", "service_directories", "writable_services", "direct_delivery_services", "worktree_root"):
        value = contract.get(field)
        if isinstance(value, list):
            missing = not any(str(item).strip() for item in value)
        else:
            missing = not str(value or "").strip()
        if missing:
            diagnostics.append({"reason_code": "delivery_fact_missing", "field": field})
    if "use_git_worktree" not in contract or not isinstance(contract.get("use_git_worktree"), bool):
        diagnostics.append({"reason_code": "delivery_fact_missing", "field": "use_git_worktree"})
    if not _service_branch_map_complete(baseline):
        diagnostics.append({"reason_code": "delivery_fact_missing", "field": "service_branch_map"})

    source = str(contract.get("source") or baseline.get("source") or "").strip()
    if source in WEAK_FACT_SOURCES:
        diagnostics.append({"reason_code": "weak_fact_source", "field": "source", "value": source})
    if not str(contract.get("approved_by") or "").strip():
        diagnostics.append({"reason_code": "weak_fact_source", "field": "approved_by", "value": ""})
    if not str(contract.get("reviewed_at") or "").strip():
        diagnostics.append({"reason_code": "weak_fact_source", "field": "reviewed_at", "value": ""})

    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "status": "blocked" if diagnostics else "pass",
        "blocked": bool(diagnostics),
        "reason_code": "explicit_delivery_fact_gate_blocked" if diagnostics else "",
        "diagnostics": diagnostics,
        "repair_route": "beacon-toolkit-branch-governance",
    }


def subskill_material_effect_registry() -> dict[str, Any]:
    entries: dict[str, dict[str, Any]] = {}
    for family, skills in MATERIAL_EFFECT_FAMILIES.items():
        for skill in skills:
            default_effect = "read_only_route_only" if skill in READ_ONLY_SUPPORT_SKILLS else "writeback_required"
            if skill == "beacon-toolkit-branch-governance":
                default_effect = "execution_host_update_required"
            entries[skill] = {
                "surface_family": family,
                "allowed_material_effects": list(ALLOWED_MATERIAL_EFFECTS),
                "default_material_effect": default_effect,
                "truth_source": False if family in {"support", "toolkit", "host", "compatibility"} else family == "truth",
                "gate_source": False,
            }
    return {
        "schema_version": "1.0",
        "status": "pass",
        "allowed_material_effects": list(ALLOWED_MATERIAL_EFFECTS),
        "families": {name: list(skills) for name, skills in MATERIAL_EFFECT_FAMILIES.items()},
        "entries": entries,
    }


def validate_subskill_invocation_effect(payload: dict[str, Any]) -> dict[str, Any]:
    skill = str(payload.get("skill") or payload.get("surface") or "").strip()
    effect = str(payload.get("material_effect") or "").strip()
    registry = subskill_material_effect_registry()
    diagnostics: list[dict[str, Any]] = []
    if skill and skill not in registry["entries"]:
        diagnostics.append({"reason_code": "subskill_material_effect_unknown_skill", "skill": skill})
    if effect not in ALLOWED_MATERIAL_EFFECTS:
        diagnostics.append({"reason_code": "subskill_material_effect_invalid", "material_effect": effect})
    target_artifacts = payload.get("target_artifacts") if isinstance(payload.get("target_artifacts"), list) else []
    if effect != "read_only_route_only" and not [item for item in target_artifacts if str(item).strip()]:
        diagnostics.append({"reason_code": "subskill_material_effect_target_missing", "material_effect": effect})
    return {
        "schema_version": "1.0",
        "status": "blocked" if diagnostics else "pass",
        "blocked": bool(diagnostics),
        "reason_code": "subskill_material_effect_unresolved" if diagnostics else "",
        "diagnostics": diagnostics,
    }


def support_finding_adoption_contract(finding: dict[str, Any]) -> dict[str, Any]:
    accepted = bool(finding.get("accepted", False))
    route = str(finding.get("adoption_route") or finding.get("route") or "").strip()
    obligation = finding.get("artifact_update_obligation") if isinstance(finding.get("artifact_update_obligation"), dict) else {}
    allowed_routes = {
        "change",
        "prd",
        "user-story",
        "test-case",
        "prototype",
        "execution-host",
        "technical-review-contract",
        "git-workflow",
        "qa-evidence",
        "release-blocker",
        "artifact_update_obligation",
    }
    adopted = (route in allowed_routes) or bool(obligation.get("required"))
    blocked = accepted and not adopted
    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": "accepted_support_finding_not_adopted" if blocked else "",
        "material_effect": "obligation_opened" if bool(obligation.get("required")) else ("writeback_required" if accepted else "read_only_route_only"),
        "adoption_route": route,
        "allowed_routes": sorted(allowed_routes),
    }


def branch_governance_writeback_targets(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    docs_root = project_root / "docs" / "beacon" / resolved_version
    refs = {
        "git_workflow_markdown": docs_root / "execution" / f"git-workflow-{slug}.md",
        "git_workflow_json": docs_root / ".machine" / "execution" / f"git-workflow-{slug}.json",
        "technical_review_markdown": docs_root / "execution" / f"deterministic-implementation-contract-{slug}.md",
        "technical_review_json": docs_root / ".machine" / "execution" / f"deterministic-implementation-contract-{slug}.json",
        "architecture_blueprint": docs_root / "execution" / "architecture-blueprint.md",
        "service_slice_map": docs_root / "execution" / "service-slice-map.md",
        "metadata_contract": project_root / ".beacon" / "metadata" / "project-version-metadata.json",
    }
    targets = {name: str(path.relative_to(project_root)) for name, path in refs.items()}
    return {
        "schema_version": "1.0",
        "tool": "beacon-toolkit-branch-governance",
        "version": resolved_version,
        "feature": feature,
        "feature_slug": slug,
        "material_effect": "execution_host_update_required",
        "target_artifacts": targets,
        "status": "pass",
    }


def material_gate_diagnostics(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    host_gate = execution_host_required_surfaces(project_root, version=resolved_version, feature=feature)
    fact_gate = explicit_delivery_fact_gate(project_root, version=resolved_version, feature=feature)
    obligation_payload = load_artifact_update_obligations(project_root, feature=feature)
    open_obligations = blocking_obligations(obligation_payload)
    diagnostics: list[dict[str, Any]] = []
    for name in host_gate.get("missing_surfaces", []):
        row = host_gate.get("surfaces", {}).get(name, {})
        diagnostics.append(
            {
                "reason_code": "missing_material",
                "material": name,
                "path": row.get("path", ""),
                "repair_route": "beacon-doctor repair-package",
            }
        )
    for item in fact_gate.get("diagnostics", []):
        reason_code = str(item.get("reason_code") or "")
        diagnostics.append(
            {
                "reason_code": reason_code,
                "field": item.get("field", ""),
                "value": item.get("value", ""),
                "repair_route": fact_gate.get("repair_route", "beacon-toolkit-branch-governance"),
            }
        )
    for item in open_obligations:
        diagnostics.append(
            {
                "reason_code": "artifact_updates_pending",
                "artifact": item.get("artifact", ""),
                "repair_route": "beacon review writeback",
            }
        )
    return {
        "schema_version": "1.0",
        "status": "blocked" if diagnostics else "pass",
        "blocked": bool(diagnostics),
        "reason_code": "material_gate_contract_blocked" if diagnostics else "",
        "diagnostics": diagnostics,
    }


def build_material_gate_preflight(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    if not material_gate_supported(resolved_version):
        return {"schema_version": "1.0", "status": "not_required", "blocked": False, "reason_code": ""}
    host_gate = execution_host_required_surfaces(project_root, version=resolved_version, feature=feature)
    baseline = load_implementation_delivery_baseline(project_root, version=resolved_version, feature=feature)
    blueprint_gate = validate_architecture_blueprint_projection(project_root, version=resolved_version, feature=feature, envelope=baseline)
    fact_gate = explicit_delivery_fact_gate(project_root, version=resolved_version, feature=feature)
    diagnostics = material_gate_diagnostics(project_root, version=resolved_version, feature=feature)
    gates = {
        "execution_host_required_surfaces": host_gate,
        "architecture_blueprint_projection": blueprint_gate,
        "explicit_delivery_facts": fact_gate,
        "diagnostics": diagnostics,
    }
    first_blocked = next((gate for gate in gates.values() if isinstance(gate, dict) and bool(gate.get("blocked"))), {})
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "status": "blocked" if first_blocked else "pass",
        "blocked": bool(first_blocked),
        "reason_code": str(first_blocked.get("reason_code") or "") if first_blocked else "",
        "gates": gates,
    }


def support_and_toolkit_boundary_contract(skill: str) -> dict[str, Any]:
    registry = subskill_material_effect_registry()
    row = registry["entries"].get(str(skill or "").strip(), {})
    family = str(row.get("surface_family") or "")
    bounded = family not in {"truth", "gate"} and not bool(row.get("truth_source")) and not bool(row.get("gate_source"))
    return {
        "schema_version": "1.0",
        "skill": skill,
        "surface_family": family,
        "status": "pass" if bounded else "blocked",
        "blocked": not bounded,
        "truth_source": bool(row.get("truth_source")),
        "gate_source": bool(row.get("gate_source")),
        "new_lifecycle_stage": False,
    }


def read_json_artifact(project_root: Path, rel_path: str) -> dict[str, Any]:
    payload = read_json(project_root / rel_path, {})
    return payload if isinstance(payload, dict) else {}
