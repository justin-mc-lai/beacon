"""Deterministic Beacon design capability contract for v1.4.11+."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


DESIGN_ROUTES: dict[str, dict[str, Any]] = {
    "explore": {
        "route": "beacon-design-explore",
        "upstream": "vibe-to-ui",
        "intent": "explore",
        "capabilities": ["concept_directions", "information_hierarchy", "layout_models", "interaction_model"],
        "truth_candidate_outputs": ["design_direction_delta", "style_notes"],
    },
    "extract": {
        "route": "beacon-design-extract",
        "upstream": "vibe-to-ui",
        "intent": "extract",
        "capabilities": ["screenshot_structure", "reference_structure", "component_breakdown", "inference_split"],
        "truth_candidate_outputs": ["prototype_adapter_input", "component_map_candidate"],
    },
    "system": {
        "route": "beacon-design-system",
        "upstream": "ui-ux-pro-max",
        "intent": "system",
        "capabilities": ["component_system", "tokens", "states", "responsive", "accessibility", "stack_aware_guidance"],
        "truth_candidate_outputs": ["component_system_delta", "state_matrix_delta", "interaction_contract_delta"],
    },
    "review": {
        "route": "beacon-design-review",
        "upstream": "impeccable",
        "intent": "review",
        "capabilities": ["ux_findings", "hierarchy_review", "copy_review", "state_gap_review", "accessibility_review"],
        "truth_candidate_outputs": ["accepted_finding_candidate", "change_refreeze_candidate"],
    },
    "polish": {
        "route": "beacon-design-polish",
        "upstream": "impeccable",
        "intent": "polish",
        "capabilities": ["ship_readiness", "spacing_alignment", "feedback_detail", "trust_detail", "microcopy"],
        "truth_candidate_outputs": ["support_evidence", "promise_changing_delta"],
    },
    "library": {
        "route": "beacon-design-library",
        "upstream": "awesome-design-md",
        "intent": "library",
        "capabilities": ["curated_references", "pattern_examples", "adaptation_guidance"],
        "truth_candidate_outputs": ["reference_notes"],
        "reference_only": True,
    },
    "bootstrap": {
        "route": "beacon-design-bootstrap",
        "upstream": "upstream-compatibility",
        "intent": "bootstrap",
        "capabilities": ["installed_skill_check", "mirror_check", "bootstrap_route_check"],
        "truth_candidate_outputs": ["capability_admission_evidence"],
        "capability_admission_only": True,
    },
    "simplify": {
        "route": "beacon-design-simplify",
        "upstream": "beacon-native",
        "intent": "simplify",
        "capabilities": [
            "lazy_user_axiom",
            "core_scenario_extraction",
            "engineer_abstraction_detection",
            "information_deduplication",
            "complexity_burden_score",
        ],
        "truth_candidate_outputs": [
            "simplicity_audit_findings",
            "reduction_recommendations",
            "core_scenario_map",
            "complexity_burden_report",
        ],
    },
}


UPSTREAM_CAPABILITIES: dict[str, dict[str, Any]] = {
    "vibe-to-ui": {
        "role": "exploration-and-extraction",
        "routes": ["explore", "extract"],
        "execution_kind": "execution-capable",
        "canonical_mirror": "oss-sync/design/skills/vibe-to-ui",
        "installed_skill_names": ["vibe-to-ui"],
    },
    "ui-ux-pro-max": {
        "role": "design-system-baseline",
        "routes": ["system"],
        "execution_kind": "execution-capable",
        "canonical_mirror": "oss-sync/design/skills/ui-ux-pro-max-skill",
        "installed_skill_names": ["ui-ux-pro-max"],
    },
    "impeccable": {
        "role": "review-and-polish",
        "routes": ["review", "polish"],
        "execution_kind": "execution-capable",
        "canonical_mirror": "oss-sync/design/skills/impeccable",
        "installed_skill_names": ["impeccable"],
    },
    "awesome-design-md": {
        "role": "reference-library",
        "routes": ["library"],
        "execution_kind": "reference-only",
        "canonical_mirror": "oss-sync/design/skills/awesome-design-md",
        "installed_skill_names": ["awesome-design-md"],
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def design_truth_paths(project_root: Path, version: str) -> dict[str, str]:
    resolved = resolve_target_version(project_root, version)
    base = project_root / "docs" / "beacon" / resolved
    return {
        "product_truth": "PRODUCT.md",
        "design_truth": "DESIGN.md",
        "version_style": _rel(project_root, base / "design" / "style.md"),
        "component_system": _rel(project_root, base / "design" / "component-system.md"),
        "interaction_contract": _rel(project_root, base / "design" / "interaction-contract.md"),
        "state_matrix": _rel(project_root, base / "design" / "state-matrix.md"),
        "machine_design_projection": _rel(project_root, base / ".machine" / "design"),
    }


def design_truth_contract(project_root: Path, version: str) -> dict[str, Any]:
    resolved = resolve_target_version(project_root, version)
    return {
        "schema_version": "1.0",
        "version": resolved,
        "truth_paths": design_truth_paths(project_root, resolved),
        "truth_authority": {
            "project_level": ["PRODUCT.md", "DESIGN.md"],
            "version_wide": [
                f"docs/beacon/{resolved}/design/style.md",
                f"docs/beacon/{resolved}/design/component-system.md",
                f"docs/beacon/{resolved}/design/interaction-contract.md",
                f"docs/beacon/{resolved}/design/state-matrix.md",
            ],
            "projection_only": [f"docs/beacon/{resolved}/.machine/design"],
            "feature_local_design_product_rejected": True,
        },
        "required_axes": ["page", "component", "state", "interaction", "accessibility", "responsive"],
        "writeback_policy": {
            "accepted_ui_ux_facts_require_truth_binding": True,
            "truth_changing_design_facts_route": "beacon-change-refreeze",
            "support_outputs_are_not_truth": True,
        },
    }


PRODUCT_TRUTH_TEMPLATE = """# Product Truth

Status: draft

This file is Beacon project-level product truth. It records durable product facts that apply across versions.

## Product Purpose

Describe what this product is for and what user outcome it protects.

## Target Users

Describe the primary users, operators, and stakeholders.

## Core Product Promises

List the stable product promises that implementation, QA, and release must preserve.

## Non-Goals

List explicit product boundaries and things this project should not promise.

## Truth Update Policy

Update this file only when accepted product facts become project-level truth. Promise-changing facts must route through Beacon change/refreeze before implementation.
"""


def _complete_design_truth_template(product_name: str = "Product", version: str = "v1.6.7") -> str:
    from beacon.utils.design_baseline import render_complete_design_md

    return render_complete_design_md(
        product_name=product_name,
        preset="restrained-product",
        version=version,
        mode="baseline",
    )


# Back-compat name; content is the complete baseline (open-source UI agent principles absorbed).
DESIGN_TRUTH_TEMPLATE = _complete_design_truth_template()


def design_route_contract(project_root: Path, version: str, *, feature: str = "") -> dict[str, Any]:
    resolved = resolve_target_version(project_root, version)
    routes: dict[str, dict[str, Any]] = {}
    for intent, route in DESIGN_ROUTES.items():
        routes[intent] = {
            **route,
            "support_only": True,
            "truth_source": False,
            "gate_source": False,
            "lifecycle_stage": False,
            "command": f'beacon design route {intent} "{feature}" --project {project_root} --version {resolved}'.strip(),
        }
    return {
        "schema_version": "1.0",
        "version": resolved,
        "feature": feature,
        "feature_slug": feature_slug(feature) if feature else "",
        "surface": "beacon-design",
        "status": "ready",
        "route_count": len(routes),
        "routes": routes,
        "upstreams": UPSTREAM_CAPABILITIES,
        "boundary": {
            "support_only": True,
            "truth_source": False,
            "gate_source": False,
            "lifecycle_stage": False,
            "awesome_design_md_reference_only": True,
            "bootstrap_capability_admission_only": True,
        },
        "truth_contract": design_truth_contract(project_root, resolved),
    }


def build_design_route_payload(
    project_root: Path,
    version: str,
    feature: str,
    *,
    intent: str,
) -> dict[str, Any]:
    resolved = resolve_target_version(project_root, version)
    normalized = str(intent or "").strip().lower().replace("_", "-")
    route = DESIGN_ROUTES.get(normalized)
    if not route:
        return {
            "schema_version": "1.0",
            "version": resolved,
            "feature": feature,
            "status": "blocked",
            "reason_code": "unknown_design_route",
            "supported_routes": sorted(DESIGN_ROUTES),
        }
    upstream = str(route["upstream"])
    return {
        "schema_version": "1.0",
        "version": resolved,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "status": "ready",
        "surface": "beacon-design",
        "intent": normalized,
        "route": route["route"],
        "upstream": upstream,
        "upstream_capability": UPSTREAM_CAPABILITIES.get(upstream, {"role": str(route.get("upstream", ""))}),
        "capabilities": list(route.get("capabilities", [])),
        "truth_candidate_outputs": list(route.get("truth_candidate_outputs", [])),
        "truth_contract": design_truth_contract(project_root, resolved),
        "boundary": {
            "support_only": True,
            "truth_source": False,
            "gate_source": False,
            "lifecycle_stage": False,
            "reference_only": bool(route.get("reference_only")),
            "capability_admission_only": bool(route.get("capability_admission_only")),
        },
        "next_routes": {
            "accepted_truth_delta": f'beacon change "{feature}" --project {project_root} --version {resolved} --refreeze-chain',
            "accepted_design_result": f'beacon prototype adapt "{feature}" --project {project_root} --version {resolved} --design-result-ref <accepted-design-result>',
            "implementation_after_binding": f'beacon implement "{feature}" --project {project_root} --version {resolved}',
        },
        "generated_at": _now_iso(),
    }


def build_design_plan(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    resolved = resolve_target_version(project_root, version)
    return {
        "schema_version": "1.0",
        "version": resolved,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "status": "ready",
        "plan_role": "design-truth-candidate-plan",
        "truth_contract": design_truth_contract(project_root, resolved),
        "route_contract": design_route_contract(project_root, resolved, feature=feature),
        "ordered_flow": [
            "detect-ui-ux-impact",
            "select-beacon-design-route",
            "draft-version-wide-design-truth",
            "record-accepted-ui-ux-ledger",
            "bind-prototype-adapter",
            "refreeze-requirements-when-promises-change",
            "allow-implement-qa-release-after-binding",
        ],
    }


def bootstrap_design_capabilities(project_root: Path, version: str) -> dict[str, Any]:
    resolved = resolve_target_version(project_root, version)
    home = Path.home()
    mirror_root = home / "Developer" / "Personal" / "oss-sync" / "design" / "skills"
    installed_roots = [
        home / ".agents" / "skills",
        home / ".codex" / "skills",
        home / ".claude" / "skills",
        project_root / ".agents" / "skills",
        project_root / "skills",
    ]
    upstreams: dict[str, dict[str, Any]] = {}
    for name, data in UPSTREAM_CAPABILITIES.items():
        installed_candidates = [
            root / skill_name
            for root in installed_roots
            for skill_name in data.get("installed_skill_names", [])
        ]
        mirror = mirror_root / ("ui-ux-pro-max-skill" if name == "ui-ux-pro-max" else name)
        upstreams[name] = {
            **data,
            "installed": any((candidate / "SKILL.md").exists() for candidate in installed_candidates),
            "installed_candidates": [str(candidate) for candidate in installed_candidates],
            "mirror": str(mirror),
            "mirror_exists": mirror.exists(),
        }
    status = "ready" if all(item["installed"] or item["mirror_exists"] for item in upstreams.values()) else "partial"
    return {
        "schema_version": "1.0",
        "version": resolved,
        "surface": "beacon-design-bootstrap",
        "status": status,
        "boundary": {
            "capability_admission_only": True,
            "truth_source": False,
            "gate_source": False,
            "release_verdict": False,
        },
        "upstreams": upstreams,
        "bootstrap_hint": "Use ui-ux-dev upstream bootstrap when installed skills and mirrors are missing.",
        "generated_at": _now_iso(),
    }


def _write_design_truth_file(path: Path, content: str, *, force: bool) -> str:
    existed = path.exists()
    if existed and not force:
        return "exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "overwritten" if existed else "written"


def write_version_design_contracts(
    project_root: Path,
    version: str,
    *,
    force: bool = False,
    include_project_truth: bool = False,
) -> dict[str, Any]:
    resolved = resolve_target_version(project_root, version)
    paths = design_truth_paths(project_root, resolved)
    writes: dict[str, str] = {}
    from beacon.utils.design_baseline import (
        VERSION_COMPONENT_SYSTEM_TEMPLATE,
        VERSION_INTERACTION_CONTRACT_TEMPLATE,
        VERSION_STATE_MATRIX_TEMPLATE,
        VERSION_STYLE_TEMPLATE,
    )

    templates = {
        "version_style": VERSION_STYLE_TEMPLATE,
        "component_system": VERSION_COMPONENT_SYSTEM_TEMPLATE,
        "interaction_contract": VERSION_INTERACTION_CONTRACT_TEMPLATE,
        "state_matrix": VERSION_STATE_MATRIX_TEMPLATE,
    }
    for key, rel in paths.items():
        if key not in templates:
            continue
        writes[key] = _write_design_truth_file(project_root / rel, templates[key], force=force)
    if include_project_truth:
        writes["product_truth"] = _write_design_truth_file(
            project_root / paths["product_truth"],
            PRODUCT_TRUTH_TEMPLATE,
            force=force,
        )
        design_body = _complete_design_truth_template(
            product_name=project_root.name or "Product",
            version=resolved,
        )
        writes["design_truth"] = _write_design_truth_file(
            project_root / paths["design_truth"],
            design_body,
            force=force,
        )
    machine_dir = project_root / paths["machine_design_projection"]
    machine_dir.mkdir(parents=True, exist_ok=True)
    projection_path = machine_dir / "design-contract.projection.json"
    projection_payload = {
        "schema_version": "1.0",
        "version": resolved,
        "projection_only": True,
        "truth_contract": design_truth_contract(project_root, resolved),
        "generated_at": _now_iso(),
    }
    projection_path.write_text(json.dumps(projection_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    writes["machine_design_projection"] = _rel(project_root, projection_path)
    return {"schema_version": "1.0", "version": resolved, "status": "ready", "writes": writes, "paths": paths}
