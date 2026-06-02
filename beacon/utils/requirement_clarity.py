"""Requirement clarity gates for v1.3.3+ freeze flows."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file, machine_execution_file
from beacon.utils.diagram_truth import diagram_truth_findings, load_feature_diagram_truth
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_map import feature_package_authoritative, resolve_truth_read_refs
from beacon.utils.support_research_topology import support_topology_diagnostics
from beacon.utils.versioning import (
    normalize_version,
    project_runtime_feature_enabled,
    release_line_key,
    resolve_runtime_version,
    resolve_target_version,
)
from beacon.utils.workflow_memory import append_lifecycle_event, record_stage_writeback, resolve_workflow_run_id

_SECTION_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_BACKTICK_PATH_RE = re.compile(r"`([^`\n]+)`")
_HEADING_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*[.)]?\s*")
_UNRESOLVED_SECTION_TITLES = {
    "open questions",
    "unresolved",
    "unresolved items",
    "pending clarifications",
    "clarifications needed",
    "未决项",
    "待澄清",
    "待确认",
    "疑问",
    "未澄清",
    "需求疑问",
}
_FREEZE_DELIVERABLE_SECTION_TITLES = {
    "冻结交付物",
    "freeze deliverables",
    "frozen deliverables",
}
_ARCHITECTURE_SECTION_TITLES = {
    "architecture",
    "architecture overview",
    "system architecture",
    "架构",
    "系统架构",
    "架构概览",
}
_BUSINESS_FLOW_SECTION_TITLES = {
    "business flow",
    "business workflow",
    "flow",
    "业务流程",
    "流程",
    "业务闭环",
}
_STATE_MACHINE_SECTION_TITLES = {
    "state machine",
    "state-machine",
    "状态机",
    "状态流转",
}
_DECISION_PRIORITY_SECTION_TITLES = {
    "decision priority",
    "decision-priority",
    "priority rules",
    "决策优先级",
    "优先级规则",
}
_INLINE_MARKERS = (
    "TBD",
    "TODO",
    "???",
    "待补充",
    "待明确",
    "待确认",
    "未澄清",
    "待澄清",
    "待定",
)


def requirement_clarity_gate_supported(version: str | None) -> bool:
    normalized_full = normalize_version(version) or "v0.0.0"
    normalized = release_line_key(version) or normalized_full
    if normalized_full != normalized:
        return False
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch)) >= (1, 3, 1)
    except Exception:  # noqa: BLE001
        return False


def _version_root(project_root: Path, version: str, feature: str) -> list[Path]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    base = project_root / "docs" / "beacon" / resolved_version
    if feature_package_authoritative(resolved_version):
        refs = resolve_truth_read_refs(
            project_root,
            version=resolved_version,
            feature=slug,
            consumer="requirement-clarity",
        )["requirement_refs"]
        paths = [
            project_root / refs["truth"],
            project_root / refs["tests"],
            project_root / refs["tasks"],
            project_root / refs["evidence"],
        ]
        research_path = base / "research" / f"{slug}.md"
        if research_path.exists():
            paths.append(research_path)
        return paths
    paths = [
        base / "prd" / f"{slug}.md",
        base / "user-story" / f"{slug}.md",
        base / "qa" / "test-cases" / f"{slug}.md",
    ]
    research_path = base / "research" / f"{slug}.md"
    if research_path.exists():
        paths.append(research_path)
    return paths


def _scan_file(path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not path.exists():
        return findings
    lines = path.read_text(encoding="utf-8").splitlines()
    in_code_fence = False
    current_unresolved_section = ""

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        heading = _SECTION_HEADING_RE.match(stripped)
        if heading:
            title = _normalize_heading_title(str(heading.group(2) or ""))
            current_unresolved_section = title if title in _UNRESOLVED_SECTION_TITLES else ""
            continue

        if current_unresolved_section and stripped:
            if stripped.startswith(("-", "*", "+")) or stripped[0].isdigit():
                findings.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "kind": "unresolved_section_item",
                        "section": current_unresolved_section,
                        "text": stripped,
                    }
                )
                continue

        upper = stripped.upper()
        if any(marker in upper for marker in _INLINE_MARKERS[:3]) or any(marker in stripped for marker in _INLINE_MARKERS[3:]):
            findings.append(
                {
                    "file": str(path),
                    "line": line_no,
                    "kind": "inline_marker",
                    "text": stripped,
                }
            )
            continue

        if stripped.startswith(("-", "*", "+")) and ("?" in stripped or "？" in stripped):
            findings.append(
                {
                    "file": str(path),
                    "line": line_no,
                    "kind": "question_bullet",
                    "text": stripped,
                }
            )
    return findings


def _normalize_heading_title(title: str) -> str:
    text = str(title or "").strip().lower()
    return _HEADING_PREFIX_RE.sub("", text).strip()


def _extract_required_artifacts(path: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    if not path.exists():
        return artifacts

    lines = path.read_text(encoding="utf-8").splitlines()
    current_section = ""
    in_code_fence = False

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        heading = _SECTION_HEADING_RE.match(stripped)
        if heading:
            current_section = _normalize_heading_title(str(heading.group(2) or ""))
            continue

        if current_section not in _FREEZE_DELIVERABLE_SECTION_TITLES:
            continue
        if not stripped:
            continue
        if not (
            stripped.startswith(("-", "*", "+"))
            or stripped[0].isdigit()
            or "`" in stripped
        ):
            continue

        for match in _BACKTICK_PATH_RE.findall(stripped):
            relative = str(match or "").strip()
            if not relative or "/" not in relative:
                continue
            if not (
                relative.startswith("docs/")
                or relative.startswith("skills/")
                or relative.startswith(".beacon/")
            ):
                continue
            artifacts.append({"path": relative, "line": line_no})

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in artifacts:
        rel = str(item.get("path") or "").strip()
        if not rel or rel in seen:
            continue
        seen.add(rel)
        deduped.append(item)
    return deduped


def _extract_heading_titles(path: Path) -> set[str]:
    titles: set[str] = set()
    if not path.exists():
        return titles
    lines = path.read_text(encoding="utf-8").splitlines()
    in_code_fence = False
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        heading = _SECTION_HEADING_RE.match(stripped)
        if not heading:
            continue
        titles.add(_normalize_heading_title(str(heading.group(2) or "")))
    return titles


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(version) or normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _feature_research_path(project_root: Path, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / resolve_target_version(project_root, version) / "research" / f"{feature_slug(feature)}.md"


def _feature_source_architecture_paths(project_root: Path, version: str, feature: str) -> list[Path]:
    base = project_root / "docs" / "beacon" / resolve_target_version(project_root, version) / "source-architecture"
    return [
        base / f"{feature_slug(feature)}.md",
        base / "index.md",
    ]


def _feature_requirement_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    base = project_root / "docs" / "beacon" / resolved_version
    if feature_package_authoritative(resolved_version):
        refs = resolve_truth_read_refs(
            project_root,
            version=resolved_version,
            feature=slug,
            consumer="requirement-clarity",
        )["requirement_refs"]
        return {
            "prd": project_root / refs["prd"],
            "user_story": project_root / refs["user_story"],
            "test_case": project_root / refs["test_case"],
            "research": base / "research" / f"{slug}.md",
        }
    return {
        "prd": base / "prd" / f"{slug}.md",
        "user_story": base / "user-story" / f"{slug}.md",
        "test_case": base / "qa" / "test-cases" / f"{slug}.md",
        "research": base / "research" / f"{slug}.md",
    }


def _research_requirement_clarity_aliases() -> dict[str, set[str]]:
    return {
        "architecture": _ARCHITECTURE_SECTION_TITLES,
        "business_flow": _BUSINESS_FLOW_SECTION_TITLES,
        "state_machine": _STATE_MACHINE_SECTION_TITLES,
        "decision_priority": _DECISION_PRIORITY_SECTION_TITLES,
    }


def _resolve_required_research_sections(diagram_truth: dict[str, Any]) -> list[str]:
    diagram_types = [
        str(item).strip()
        for item in (diagram_truth.get("diagram_types") or [])
        if str(item).strip()
    ] if isinstance(diagram_truth, dict) else []
    complexity_signals = [
        str(item).strip()
        for item in (diagram_truth.get("complexity_signals") or [])
        if str(item).strip()
    ] if isinstance(diagram_truth, dict) else []
    required = bool(diagram_truth.get("required")) or bool(complexity_signals)
    sections = ["architecture", "business_flow"]
    if "state-machine" in diagram_types or required:
        sections.append("state_machine")
    if "decision-priority" in diagram_types:
        sections.append("decision_priority")
    return sections


def _extract_explicit_ac_ids(content: str) -> set[str]:
    ac_ids: set[str] = set()
    for line in str(content or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "|" in stripped:
            match = re.search(r"\b(AC-\d{3,})\b", stripped, flags=re.IGNORECASE)
            if match:
                ac_ids.add(str(match.group(1)).upper())
        for match in re.finditer(r"\b(AC-\d{3,})\b", stripped, flags=re.IGNORECASE):
            ac_ids.add(str(match.group(1)).upper())
    return ac_ids


def _build_requirement_closure_contract(
    project_root: Path,
    *,
    version: str,
    feature: str,
    diagram_truth: dict[str, Any],
) -> dict[str, Any]:
    paths = _feature_requirement_paths(project_root, version, feature)
    prd_text = paths["prd"].read_text(encoding="utf-8") if paths["prd"].exists() else ""
    user_story_text = paths["user_story"].read_text(encoding="utf-8") if paths["user_story"].exists() else ""
    test_case_text = paths["test_case"].read_text(encoding="utf-8") if paths["test_case"].exists() else ""
    research_headings = _extract_heading_titles(paths["research"])
    human_closure_required = bool(diagram_truth.get("required")) or bool(
        [
            str(item).strip()
            for item in (diagram_truth.get("complexity_signals") or [])
            if str(item).strip()
        ]
    )
    required_research_sections = _resolve_required_research_sections(diagram_truth) if human_closure_required else []
    alias_map = _research_requirement_clarity_aliases()
    missing_research_sections = [
        section
        for section in required_research_sections
        if not any(alias in research_headings for alias in alias_map.get(section, set()))
    ]

    prd_ac_ids = _extract_explicit_ac_ids(prd_text)
    user_story_ac_ids = _extract_explicit_ac_ids(user_story_text)
    test_case_ac_ids = _extract_explicit_ac_ids(test_case_text)
    upstream_ac_ids = sorted(prd_ac_ids | user_story_ac_ids)
    missing_test_case_ac_ids = [ac_id for ac_id in upstream_ac_ids if ac_id not in test_case_ac_ids]

    chain_paths = {
        "research": str(paths["research"].relative_to(project_root)),
        "prd": str(paths["prd"].relative_to(project_root)),
        "user_story": str(paths["user_story"].relative_to(project_root)),
        "test_case": str(paths["test_case"].relative_to(project_root)),
    }

    return {
        "required": True,
        "chain_order": ["research", "prd", "user_story", "test_case", "requirement_clarity", "freeze"],
        "human_closure_required": human_closure_required,
        "paths": chain_paths,
        "exists": {
            "research": paths["research"].exists(),
            "prd": paths["prd"].exists(),
            "user_story": paths["user_story"].exists(),
            "test_case": paths["test_case"].exists(),
        },
        "required_research_sections": required_research_sections,
        "missing_research_sections": missing_research_sections if paths["research"].exists() else required_research_sections,
        "ac_projection": {
            "prd_ac_ids": sorted(prd_ac_ids),
            "user_story_ac_ids": sorted(user_story_ac_ids),
            "test_case_ac_ids": sorted(test_case_ac_ids),
            "upstream_ac_ids": upstream_ac_ids,
            "missing_test_case_ac_ids": missing_test_case_ac_ids,
        },
    }


def _build_human_closure_contract(project_root: Path, *, version: str, feature: str, diagram_truth: dict[str, Any]) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    research_path = _feature_research_path(project_root, resolved_version, feature)
    architecture_candidates = _feature_source_architecture_paths(project_root, resolved_version, feature)
    architecture_path = next((path for path in architecture_candidates if path.exists()), architecture_candidates[0])
    complexity_signals = [
        str(item).strip()
        for item in (diagram_truth.get("complexity_signals") or [])
        if str(item).strip()
    ] if isinstance(diagram_truth, dict) else []
    required = bool(diagram_truth.get("required")) or bool(complexity_signals)
    required_sections = _resolve_required_research_sections(diagram_truth)

    research_headings = _extract_heading_titles(research_path)
    missing_sections: list[str] = []
    section_title_map = _research_requirement_clarity_aliases()
    for key in required_sections:
        aliases = section_title_map.get(key, set())
        if not any(alias in research_headings for alias in aliases):
            missing_sections.append(key)

    return {
        "required": required,
        "research_path": str(research_path.relative_to(project_root)),
        "research_exists": research_path.exists(),
        "source_architecture_path": str(architecture_path.relative_to(project_root)),
        "source_architecture_exists": architecture_path.exists(),
        "required_sections": required_sections,
        "missing_sections": missing_sections if research_path.exists() else required_sections,
        "diagram_types": [
            str(item).strip()
            for item in (diagram_truth.get("diagram_types") or [])
            if str(item).strip()
        ] if isinstance(diagram_truth, dict) else [],
        "complexity_signals": complexity_signals,
    }


_VERSION_PROJECTION_TRUTH_FIELDS = (
    "prd_refs",
    "user_story_refs",
    "test_case_refs",
    "coverage_notes",
    "out_of_scope_notes",
)


def _version_projection_truth_contract(
    project_root: Path,
    *,
    version: str,
    feature: str,
    diagram_truth: dict[str, Any],
) -> dict[str, Any]:
    supported = _semver_tuple(version) >= (1, 4, 9)
    paths = _feature_requirement_paths(project_root, version, feature)
    research_path = paths["research"]
    text = research_path.read_text(encoding="utf-8") if research_path.exists() else ""
    lowered = text.lower()
    declared_types = [
        item
        for item in ("business_flow", "state_machine", "three_piece_map")
        if (
            (item == "business_flow" and ("business flow" in lowered or "业务流程" in lowered or "业务闭环" in lowered))
            or (item == "state_machine" and ("state machine" in lowered or "state-machine" in lowered or "状态机" in lowered))
            or (item == "three_piece_map" and ("three-piece" in lowered or "three piece" in lowered or "prd / user story / test case map" in lowered or "三件套" in lowered))
        )
    ]
    required = supported and (bool(diagram_truth.get("required")) or bool(declared_types))
    field_presence = {
        field: (field in lowered or field.replace("_", "-") in lowered)
        for field in _VERSION_PROJECTION_TRUTH_FIELDS
    }
    missing_fields = [field for field, present in field_presence.items() if required and not present]
    required_refs = {
        "prd_refs": str(paths["prd"].relative_to(project_root)),
        "user_story_refs": str(paths["user_story"].relative_to(project_root)),
        "test_case_refs": str(paths["test_case"].relative_to(project_root)),
    }
    missing_ref_targets = [
        key
        for key, rel in required_refs.items()
        if required and field_presence.get(key) and rel not in text
    ]
    return {
        "required": required,
        "supported": supported,
        "projection_types": declared_types,
        "research_path": str(research_path.relative_to(project_root)),
        "research_exists": research_path.exists(),
        "required_fields": list(_VERSION_PROJECTION_TRUTH_FIELDS),
        "field_presence": field_presence,
        "missing_fields": missing_fields,
        "required_refs": required_refs,
        "missing_ref_targets": missing_ref_targets,
        "ready": bool(required) and not missing_fields and not missing_ref_targets,
    }


def build_requirement_clarity_gate_payload(project_root: Path, *, version: str = "auto", feature: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    prd_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{feature_slug(feature)}.md"
    resolved_runtime = resolve_runtime_version(project_root, "auto")
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "runtime_version": resolved_runtime,
        "runtime_capability_line": "v1.3.3",
        "required": project_runtime_feature_enabled(
            project_root,
            "v1.3.3",
            docs_version=resolved_version,
            runtime_version=resolved_runtime,
        ),
        "reason_code": "",
        "blocked": False,
        "status": "pass",
        "findings": [],
        "report_json_path": str(requirement_clarity_json_path(project_root, resolved_version, feature).relative_to(project_root)),
        "report_markdown_path": str(requirement_clarity_markdown_path(project_root, resolved_version, feature).relative_to(project_root)),
        "state_path": str(requirement_clarity_state_path(project_root, feature).relative_to(project_root)),
    }
    if not payload["required"]:
        return payload

    findings: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    for path in _version_root(project_root, resolved_version, feature):
        scanned_files.append(str(path.relative_to(project_root)))
        findings.extend(_scan_file(path))

    diagram_truth = load_feature_diagram_truth(project_root, version=resolved_version, feature=feature)
    payload["diagram_truth"] = diagram_truth
    findings.extend(diagram_truth_findings(project_root, version=resolved_version, feature=feature))
    human_closure_contract = _build_human_closure_contract(
        project_root,
        version=resolved_version,
        feature=feature,
        diagram_truth=diagram_truth,
    )
    requirement_closure_contract = _build_requirement_closure_contract(
        project_root,
        version=resolved_version,
        feature=feature,
        diagram_truth=diagram_truth,
    )
    payload["human_closure_contract"] = human_closure_contract
    payload["requirement_closure_contract"] = requirement_closure_contract
    projection_truth_contract = _version_projection_truth_contract(
        project_root,
        version=resolved_version,
        feature=feature,
        diagram_truth=diagram_truth,
    )
    payload["version_projection_truth_contract"] = projection_truth_contract
    support_topology = support_topology_diagnostics(project_root, version=resolved_version, feature=feature)
    payload["support_write_topology_contract"] = support_topology
    for diagnostic in support_topology.get("diagnostics", []) if isinstance(support_topology.get("diagnostics"), list) else []:
        if not isinstance(diagnostic, dict):
            continue
        findings.append(
            {
                "file": str(project_root / str(diagnostic.get("actual_path") or diagnostic.get("expected_path") or "")),
                "line": 1,
                "kind": "support_write_topology_violation",
                "text": (
                    f"{diagnostic.get('reason_code')}: source_skill={diagnostic.get('source_skill', '')} "
                    f"expected={diagnostic.get('expected_path', '')} actual={diagnostic.get('actual_path', '')}"
                ),
                "reason_code": str(diagnostic.get("reason_code") or ""),
                "source_skill": str(diagnostic.get("source_skill") or ""),
                "expected_path": str(diagnostic.get("expected_path") or ""),
                "actual_path": str(diagnostic.get("actual_path") or ""),
                "repair_route": str(diagnostic.get("repair_route") or "beacon-change-refreeze"),
            }
        )
    if bool(human_closure_contract.get("required")):
        if not bool(human_closure_contract.get("research_exists")):
            findings.append(
                {
                    "file": str(prd_path),
                    "line": 1,
                    "kind": "research_artifact_missing",
                    "text": f"complex feature requires research closure document: {human_closure_contract.get('research_path')}",
                    "path": str(human_closure_contract.get("research_path") or ""),
                }
            )
        if not bool(human_closure_contract.get("source_architecture_exists")):
            findings.append(
                {
                    "file": str(prd_path),
                    "line": 1,
                    "kind": "source_architecture_missing",
                    "text": f"complex feature requires source architecture reference: {human_closure_contract.get('source_architecture_path')}",
                    "path": str(human_closure_contract.get("source_architecture_path") or ""),
                }
            )
        for section in human_closure_contract.get("missing_sections", []) if isinstance(human_closure_contract.get("missing_sections"), list) else []:
            findings.append(
                {
                    "file": str(_feature_research_path(project_root, resolved_version, feature)),
                    "line": 1,
                    "kind": "human_closure_section_missing",
                    "text": f"research closure missing required section: {section}",
                    "section": section,
                }
            )
    chain_exists = requirement_closure_contract.get("exists") if isinstance(requirement_closure_contract.get("exists"), dict) else {}
    human_closure_required = bool(requirement_closure_contract.get("human_closure_required"))
    for stage in ("research", "prd", "user_story", "test_case"):
        if stage == "research" and not human_closure_required:
            continue
        if not bool(chain_exists.get(stage)):
            findings.append(
                {
                    "file": str(prd_path),
                    "line": 1,
                    "kind": "requirement_chain_artifact_missing",
                    "text": f"requirement chain missing required artifact: {stage}",
                    "stage": stage,
                    "path": str((requirement_closure_contract.get("paths") or {}).get(stage, "")),
                }
            )
    ac_projection = requirement_closure_contract.get("ac_projection") if isinstance(requirement_closure_contract.get("ac_projection"), dict) else {}
    for ac_id in ac_projection.get("missing_test_case_ac_ids", []) if isinstance(ac_projection.get("missing_test_case_ac_ids"), list) else []:
        findings.append(
            {
                "file": str(project_root / str((requirement_closure_contract.get("paths") or {}).get("test_case", ""))),
                "line": 1,
                "kind": "test_case_ac_missing",
                "text": f"test-case truth is missing acceptance coverage row: {ac_id}",
                "ac_id": ac_id,
            }
        )
    if bool(projection_truth_contract.get("required")):
        for field in projection_truth_contract.get("missing_fields", []) if isinstance(projection_truth_contract.get("missing_fields"), list) else []:
            findings.append(
                {
                    "file": str(_feature_research_path(project_root, resolved_version, feature)),
                    "line": 1,
                    "kind": "version_projection_truth_binding_missing",
                    "text": f"version projection missing truth binding field: {field}",
                    "field": field,
                }
            )
        for field in projection_truth_contract.get("missing_ref_targets", []) if isinstance(projection_truth_contract.get("missing_ref_targets"), list) else []:
            findings.append(
                {
                    "file": str(_feature_research_path(project_root, resolved_version, feature)),
                    "line": 1,
                    "kind": "version_projection_truth_binding_ref_missing",
                    "text": f"version projection truth binding does not reference required artifact: {field}",
                    "field": field,
                    "expected_ref": str((projection_truth_contract.get("required_refs") or {}).get(field, "")),
                }
            )

    required_artifacts = _extract_required_artifacts(prd_path)
    payload["required_artifacts"] = [str(item.get("path") or "") for item in required_artifacts]
    for artifact in required_artifacts:
        relative = str(artifact.get("path") or "").strip()
        if not relative:
            continue
        if not (project_root / relative).exists():
            findings.append(
                {
                    "file": str(prd_path),
                    "line": int(artifact.get("line") or 0),
                    "kind": "missing_required_artifact",
                    "text": f"missing required artifact: {relative}",
                    "path": relative,
                }
            )

    payload["scanned_files"] = scanned_files
    payload["findings"] = findings
    if findings:
        payload["blocked"] = True
        payload["status"] = "blocked"
        payload["reason_code"] = "requirement_clarity_open"
        payload["recommended_action"] = "resolve_prd_and_user_story_open_questions_before_freeze"
    return payload


def requirement_clarity_json_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_file(project_root, resolved_version, f"requirement-clarity-{feature_slug(feature)}.json")


def requirement_clarity_markdown_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return human_execution_file(project_root, resolved_version, f"requirement-clarity-{feature_slug(feature)}.md")


def requirement_clarity_state_path(project_root: Path, feature: str) -> Path:
    return project_root / ".beacon" / "state" / f"requirement-clarity-{feature_slug(feature)}.json"


def load_requirement_clarity_state(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(requirement_clarity_state_path(project_root, feature), {})
    return payload if isinstance(payload, dict) else {}


def _render_requirement_clarity_markdown(payload: dict[str, Any]) -> str:
    findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
    human_closure = payload.get("human_closure_contract") if isinstance(payload.get("human_closure_contract"), dict) else {}
    lines = [
        "# Requirement Clarity Report",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- required: `{bool(payload.get('required', False))}`",
        f"- status: `{payload.get('status', '')}`",
        f"- reason_code: `{payload.get('reason_code', '')}`",
        "",
        "## Human Closure Contract",
        f"- required: `{bool(human_closure.get('required', False))}`",
        f"- research_path: `{human_closure.get('research_path', '')}`",
        f"- research_exists: `{bool(human_closure.get('research_exists', False))}`",
        f"- source_architecture_path: `{human_closure.get('source_architecture_path', '')}`",
        f"- source_architecture_exists: `{bool(human_closure.get('source_architecture_exists', False))}`",
        f"- required_sections: {', '.join(human_closure.get('required_sections', [])) if isinstance(human_closure.get('required_sections'), list) else 'none' }",
        f"- missing_sections: {', '.join(human_closure.get('missing_sections', [])) if isinstance(human_closure.get('missing_sections'), list) else 'none' }",
        "",
        "## Requirement Closure Contract",
    ]
    requirement_closure = payload.get("requirement_closure_contract") if isinstance(payload.get("requirement_closure_contract"), dict) else {}
    chain_order = requirement_closure.get("chain_order") if isinstance(requirement_closure.get("chain_order"), list) else []
    chain_paths = requirement_closure.get("paths") if isinstance(requirement_closure.get("paths"), dict) else {}
    chain_exists = requirement_closure.get("exists") if isinstance(requirement_closure.get("exists"), dict) else {}
    ac_projection = requirement_closure.get("ac_projection") if isinstance(requirement_closure.get("ac_projection"), dict) else {}
    lines.extend(
        [
            f"- chain_order: {' -> '.join(chain_order) if chain_order else 'none'}",
            f"- human_closure_required: `{bool(requirement_closure.get('human_closure_required', False))}`",
            f"- research_path: `{chain_paths.get('research', '')}` exists=`{bool(chain_exists.get('research', False))}`",
            f"- prd_path: `{chain_paths.get('prd', '')}` exists=`{bool(chain_exists.get('prd', False))}`",
            f"- user_story_path: `{chain_paths.get('user_story', '')}` exists=`{bool(chain_exists.get('user_story', False))}`",
            f"- test_case_path: `{chain_paths.get('test_case', '')}` exists=`{bool(chain_exists.get('test_case', False))}`",
            f"- upstream_ac_ids: {', '.join(ac_projection.get('upstream_ac_ids', [])) if isinstance(ac_projection.get('upstream_ac_ids'), list) else 'none'}",
            f"- missing_test_case_ac_ids: {', '.join(ac_projection.get('missing_test_case_ac_ids', [])) if isinstance(ac_projection.get('missing_test_case_ac_ids'), list) else 'none'}",
            "",
            "## Version Projection Truth Contract",
        ]
    )
    projection_truth = payload.get("version_projection_truth_contract") if isinstance(payload.get("version_projection_truth_contract"), dict) else {}
    lines.extend(
        [
            f"- required: `{bool(projection_truth.get('required', False))}`",
            f"- projection_types: {', '.join(projection_truth.get('projection_types', [])) if isinstance(projection_truth.get('projection_types'), list) else 'none'}",
            f"- missing_fields: {', '.join(projection_truth.get('missing_fields', [])) if isinstance(projection_truth.get('missing_fields'), list) else 'none'}",
            f"- missing_ref_targets: {', '.join(projection_truth.get('missing_ref_targets', [])) if isinstance(projection_truth.get('missing_ref_targets'), list) else 'none'}",
            "",
            "## Support Write Topology Contract",
        ]
    )
    support_topology = payload.get("support_write_topology_contract") if isinstance(payload.get("support_write_topology_contract"), dict) else {}
    lines.extend(
        [
            f"- supported: `{bool(support_topology.get('supported', False))}`",
            f"- status: `{support_topology.get('status', '')}`",
            f"- reason_code: `{support_topology.get('reason_code', '')}`",
            f"- diagnostic_count: `{len(support_topology.get('diagnostics') or []) if isinstance(support_topology.get('diagnostics'), list) else 0}`",
            "",
            "## Scanned Files",
        ]
    )
    for item in payload.get("scanned_files", []) if isinstance(payload.get("scanned_files"), list) else []:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Findings")
    if findings:
        for item in findings:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- `{item.get('kind', '')}` {item.get('file', '')}:{item.get('line', '')} :: {item.get('text', '')}"
            )
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_requirement_clarity_report(
    project_root: Path,
    *,
    version: str,
    feature: str,
    payload: dict[str, Any],
) -> dict[str, str]:
    resolved_version = resolve_target_version(project_root, version)
    json_path = requirement_clarity_json_path(project_root, resolved_version, feature)
    markdown_path = requirement_clarity_markdown_path(project_root, resolved_version, feature)
    write_json(json_path, payload)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_requirement_clarity_markdown(payload), encoding="utf-8")
    return {
        "json": str(json_path.relative_to(project_root)),
        "markdown": str(markdown_path.relative_to(project_root)),
    }


def write_requirement_clarity_writeback(
    project_root: Path,
    *,
    version: str,
    feature: str,
    gate_payload: dict[str, Any],
    report: dict[str, str],
    source: str = "freeze",
    run_id: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    state_path = requirement_clarity_state_path(project_root, feature)
    resolved_run_id = run_id or resolve_workflow_run_id(project_root, version=resolved_version, feature=feature) or ""
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "status": str(gate_payload.get("status", "") or ""),
        "blocked": bool(gate_payload.get("blocked", False)),
        "reason_code": str(gate_payload.get("reason_code", "") or ""),
        "report_json_path": str(report.get("json", "") or ""),
        "report_markdown_path": str(report.get("markdown", "") or ""),
        "finding_count": len(gate_payload.get("findings", []) if isinstance(gate_payload.get("findings"), list) else []),
        "run_id": resolved_run_id,
        "source": source,
        "written_at": now_iso(),
    }
    write_json(state_path, payload)

    if resolved_run_id:
        evidence_ref = [
            str(report.get("json", "") or ""),
            str(report.get("markdown", "") or ""),
            str(state_path.relative_to(project_root)),
        ]
        append_lifecycle_event(
            project_root,
            run_id=resolved_run_id,
            stage="requirement-review",
            event="clarity_synced",
            source=source,
            evidence_ref=evidence_ref,
            details={"status": payload["status"], "finding_count": payload["finding_count"]},
        )
        if not payload["blocked"]:
            record_stage_writeback(
                project_root,
                run_id=resolved_run_id,
                stage="requirement-review",
                feature=feature,
                evidence_ref=evidence_ref,
                status="cleared",
            )
    return {
        **payload,
        "state_path": str(state_path.relative_to(project_root)),
    }


def materialize_requirement_clarity(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    source: str = "doctor.sync-requirement-clarity",
    run_id: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    gate_payload = build_requirement_clarity_gate_payload(project_root, version=resolved_version, feature=feature)
    report = write_requirement_clarity_report(
        project_root,
        version=resolved_version,
        feature=feature,
        payload=gate_payload,
    )
    writeback = write_requirement_clarity_writeback(
        project_root,
        version=resolved_version,
        feature=feature,
        gate_payload=gate_payload,
        report=report,
        source=source,
        run_id=run_id,
    )
    return {
        "gate": gate_payload,
        "report": report,
        "writeback": writeback,
    }
