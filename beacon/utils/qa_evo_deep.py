"""QA evo-deep contracts for v1.4.10."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.qa_precision import feature_qa_ac_closure_path, feature_qa_scorecard_path
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


FINDING_FAMILIES = (
    "state_machine",
    "business_flow",
    "scenario_combination",
    "permission_boundary",
    "data_source_consistency",
    "cross_surface_closure",
    "repeated_failure",
)

AUTHORITY_BOUNDARIES = (
    "prd_truth",
    "user_story_truth",
    "test_case_truth",
    "freeze_state",
    "qa_verdict",
    "release_verdict",
    "gate_verdict",
)

DEFAULT_ROUTES = {
    "truth_drift": "beacon change/refreeze",
    "implementation_gap": "beacon implement repair",
    "qa_evidence_gap": "beacon qa supplement",
    "release_supplement": "beacon release readiness input",
}


def qa_evo_deep_path(project_root: Path, *, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / "qa" / "evo-deep" / f"{feature_slug(feature)}.md"


def qa_evo_deep_machine_path(project_root: Path, *, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / ".machine" / "qa" / "evo-deep" / f"{feature_slug(feature)}.json"


def load_qa_evo_deep_payload(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    path = qa_evo_deep_machine_path(project_root, version=version, feature=feature)
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _required_source_paths(project_root: Path, *, version: str, feature: str) -> dict[str, Path]:
    slug = feature_slug(feature)
    docs_root = project_root / "docs" / "beacon" / version
    return {
        "prd": docs_root / "prd" / f"{slug}.md",
        "user_story": docs_root / "user-story" / f"{slug}.md",
        "test_case": docs_root / "qa" / "test-cases" / f"{slug}.md",
        "qa_scorecard": feature_qa_scorecard_path(project_root, feature=feature),
        "ac_closure": feature_qa_ac_closure_path(project_root, feature=feature),
    }


def load_qa_evo_deep_source_materials(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    paths = _required_source_paths(project_root, version=version, feature=feature)
    materials: dict[str, Any] = {}
    missing: list[dict[str, str]] = []
    for name, path in paths.items():
        exists = path.exists()
        rel_path = _rel(project_root, path)
        if not exists:
            missing.append({"source": name, "path": rel_path})
            materials[name] = {"path": rel_path, "exists": False}
            continue
        if path.suffix == ".json":
            payload = read_json(path, {})
            materials[name] = {
                "path": rel_path,
                "exists": True,
                "payload": payload if isinstance(payload, dict) else {},
            }
        else:
            text = path.read_text(encoding="utf-8")
            materials[name] = {
                "path": rel_path,
                "exists": True,
                "text": text,
                "text_length": len(text),
            }
    return {
        "schema_version": "1.0",
        "status": "blocked" if missing else "ready",
        "blocked": bool(missing),
        "missing_sources": missing,
        "materials": materials,
    }


def _ac_ids_from_source_materials(source_materials: dict[str, Any]) -> list[str]:
    materials = source_materials.get("materials") if isinstance(source_materials.get("materials"), dict) else {}
    ac_ids: set[str] = set()
    for name in ("user_story", "test_case", "prd"):
        material = materials.get(name) if isinstance(materials.get(name), dict) else {}
        text = str(material.get("text") or "")
        ac_ids.update(match.group(0) for match in re.finditer(r"\bAC-\d{3}\b", text))
    ac_closure = materials.get("ac_closure") if isinstance(materials.get("ac_closure"), dict) else {}
    payload = ac_closure.get("payload") if isinstance(ac_closure.get("payload"), dict) else {}
    reports = payload.get("reports") if isinstance(payload.get("reports"), list) else []
    for item in reports:
        if isinstance(item, dict) and str(item.get("ac_id") or "").strip():
            ac_ids.add(str(item.get("ac_id")).strip())
    return sorted(ac_ids)


def _current_evidence_refs(source_materials: dict[str, Any]) -> list[str]:
    materials = source_materials.get("materials") if isinstance(source_materials.get("materials"), dict) else {}
    refs = [
        str(material.get("path") or "").strip()
        for name, material in materials.items()
        if name in {"qa_scorecard", "ac_closure"} and isinstance(material, dict) and bool(material.get("exists"))
    ]
    return [item for item in refs if item]


def _blocked_admission_findings(*, feature: str, version: str, source_materials: dict[str, Any]) -> list[dict[str, Any]]:
    missing = source_materials.get("missing_sources") if isinstance(source_materials.get("missing_sources"), list) else []
    missing_refs = [
        str(item.get("path") or "").strip()
        for item in missing
        if isinstance(item, dict) and str(item.get("path") or "").strip()
    ]
    return [
        {
            "finding_id": "QED-BLOCKED-001",
            "feature": feature,
            "version": version,
            "source_refs": missing_refs,
            "finding_family": "blocked_admission",
            "risk": "high",
            "affected_ac_ids": [],
            "state_or_flow_refs": [],
            "round_memory_refs": [],
            "current_evidence_refs": [],
            "blocked_admissions": [
                {
                    "reason_code": "qa_evo_deep_source_evidence_missing",
                    "missing_sources": missing,
                    "route_recommendation": DEFAULT_ROUTES["qa_evidence_gap"],
                }
            ],
            "route_recommendation": DEFAULT_ROUTES["qa_evidence_gap"],
            "release_supplement_input": "",
            "authority_boundary": "routeable_finding_only",
        }
    ]


def default_qa_evo_deep_findings(*, feature: str, version: str, source_materials: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    source_materials = source_materials if isinstance(source_materials, dict) else {}
    if bool(source_materials.get("blocked")):
        return _blocked_admission_findings(feature=feature, version=version, source_materials=source_materials)
    ac_ids = _ac_ids_from_source_materials(source_materials)
    evidence_refs = _current_evidence_refs(source_materials)
    findings: list[dict[str, Any]] = []
    for index, family in enumerate(FINDING_FAMILIES, start=1):
        findings.append(
            {
                "finding_id": f"QED-{index:03d}",
                "feature": feature,
                "version": version,
                "source_refs": [
                    f"docs/beacon/{version}/prd/{feature_slug(feature)}.md",
                    f"docs/beacon/{version}/user-story/{feature_slug(feature)}.md",
                    f"docs/beacon/{version}/qa/test-cases/{feature_slug(feature)}.md",
                ],
                "finding_family": family,
                "risk": "medium",
                "affected_ac_ids": ac_ids,
                "state_or_flow_refs": [],
                "round_memory_refs": [],
                "current_evidence_refs": evidence_refs,
                "blocked_admissions": [],
                "route_recommendation": DEFAULT_ROUTES["qa_evidence_gap"],
                "release_supplement_input": "",
                "authority_boundary": "routeable_finding_only",
                "deep_absorption_status": "not_applicable",
            }
        )
    return findings


def build_round_memory_influence(
    *,
    round_id: str = "round-001",
    source_run_id: str = "",
    scenario: str = "historical QA signal",
    outcome: str = "influence_only",
    failure_family: str = "",
) -> dict[str, Any]:
    return {
        "round_id": round_id,
        "source_run_id": source_run_id,
        "scenario": scenario,
        "outcome": outcome,
        "failure_family": failure_family,
        "stability_signal": "advisory",
        "influence_reason": "prior QA round memory can prioritize exploration but cannot satisfy acceptance",
        "current_run_required": True,
        "counts_as_pass_evidence": False,
    }


def validate_qa_evo_deep_payload(payload: dict[str, Any]) -> dict[str, Any]:
    findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
    round_memory = payload.get("round_memory") if isinstance(payload.get("round_memory"), list) else []
    issues: list[dict[str, Any]] = []
    source_materials = payload.get("source_materials") if isinstance(payload.get("source_materials"), dict) else {}
    if bool(source_materials.get("blocked")):
        issues.append(
            {
                "reason_code": "qa_evo_deep_source_evidence_missing",
                "missing_sources": source_materials.get("missing_sources") if isinstance(source_materials.get("missing_sources"), list) else [],
            }
        )
    families = {str(item.get("finding_family") or "") for item in findings if isinstance(item, dict)}
    if "blocked_admission" not in families:
        for required in FINDING_FAMILIES:
            if required not in families:
                issues.append({"reason_code": "qa_evo_deep_finding_family_missing", "finding_family": required})
    for item in round_memory:
        if not isinstance(item, dict):
            continue
        if bool(item.get("counts_as_pass_evidence")):
            issues.append({"reason_code": "qa_round_memory_counts_as_pass", "round_id": str(item.get("round_id") or "")})
    for item in findings:
        if not isinstance(item, dict):
            continue
        boundary = str(item.get("authority_boundary") or "")
        if boundary in AUTHORITY_BOUNDARIES:
            issues.append(
                {
                    "reason_code": "qa_evo_deep_authority_bypass",
                    "finding_id": str(item.get("finding_id") or ""),
                    "authority_boundary": boundary,
                }
            )
        blocked_admissions = item.get("blocked_admissions") if isinstance(item.get("blocked_admissions"), list) else []
        if blocked_admissions or str(item.get("finding_family") or "") == "blocked_admission":
            if not blocked_admissions:
                issues.append(
                    {
                        "reason_code": "qa_evo_deep_blocked_admission_detail_missing",
                        "finding_id": str(item.get("finding_id") or ""),
                    }
                )
            continue
        affected_ac_ids = [str(ac).strip() for ac in (item.get("affected_ac_ids") or []) if str(ac).strip()]
        evidence_refs = [str(ref).strip() for ref in (item.get("current_evidence_refs") or []) if str(ref).strip()]
        if not affected_ac_ids or not evidence_refs:
            issues.append(
                {
                    "reason_code": "qa_evo_deep_empty_skeleton_finding",
                    "finding_id": str(item.get("finding_id") or ""),
                    "missing": [
                        *([] if affected_ac_ids else ["affected_ac_ids"]),
                        *([] if evidence_refs else ["current_evidence_refs"]),
                    ],
                }
            )
    return {
        "schema_version": "1.0",
        "status": "blocked" if issues else "pass",
        "blocked": bool(issues),
        "issues": issues,
    }


def build_deep_absorption_status(
    project_root: Path,
    *,
    version: str,
    feature: str,
    ac_closure: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    deep_payload = load_qa_evo_deep_payload(project_root, version=resolved_version, feature=feature)
    findings = deep_payload.get("findings") if isinstance(deep_payload.get("findings"), list) else []
    if not findings:
        return {
            "schema_version": "1.0",
            "status": "not_applicable",
            "eligible_for_release_supplement": False,
            "findings": [],
            "absorbed_count": 0,
            "deferred_count": 0,
            "blocked_count": 0,
            "not_applicable_count": 0,
        }
    ac_closure = ac_closure if isinstance(ac_closure, dict) else {}
    reports = ac_closure.get("reports") if isinstance(ac_closure.get("reports"), list) else []
    ac_status = {
        str(item.get("ac_id") or "").strip(): str(item.get("closure_status") or "").strip()
        for item in reports
        if isinstance(item, dict) and str(item.get("ac_id") or "").strip()
    }
    absorption_findings: list[dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue
        finding_id = str(item.get("finding_id") or "").strip()
        affected = [str(ac).strip() for ac in (item.get("affected_ac_ids") or []) if str(ac).strip()]
        evidence_refs = [str(ref).strip() for ref in (item.get("current_evidence_refs") or []) if str(ref).strip()]
        blocked_admissions = item.get("blocked_admissions") if isinstance(item.get("blocked_admissions"), list) else []
        if blocked_admissions or str(item.get("finding_family") or "") == "blocked_admission":
            status = "blocked"
        elif not affected or not evidence_refs:
            status = "blocked"
        elif all(ac_status.get(ac) == "accepted" for ac in affected):
            status = "absorbed"
        elif affected:
            status = "deferred"
        else:
            status = "not_applicable"
        absorption_findings.append(
            {
                "finding_id": finding_id,
                "finding_family": str(item.get("finding_family") or ""),
                "affected_ac_ids": affected,
                "current_evidence_refs": evidence_refs,
                "deep_absorption_status": status,
                "release_supplement_eligible": status == "absorbed",
            }
        )
    counts = {
        "absorbed_count": len([item for item in absorption_findings if item["deep_absorption_status"] == "absorbed"]),
        "deferred_count": len([item for item in absorption_findings if item["deep_absorption_status"] == "deferred"]),
        "blocked_count": len([item for item in absorption_findings if item["deep_absorption_status"] == "blocked"]),
        "not_applicable_count": len([item for item in absorption_findings if item["deep_absorption_status"] == "not_applicable"]),
    }
    return {
        "schema_version": "1.0",
        "status": "absorbed" if counts["absorbed_count"] and not counts["deferred_count"] and not counts["blocked_count"] else "advisory_only",
        "eligible_for_release_supplement": bool(counts["absorbed_count"]) and not counts["deferred_count"] and not counts["blocked_count"],
        "findings": absorption_findings,
        **counts,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# QA Evo Deep: {payload['feature']}",
        "",
        f"- version: `{payload['version']}`",
        f"- status: `{payload['status']}`",
        "- verdict_policy: `routeable_findings_only`",
        "- qa_round_memory_policy: `advisory_influence_only_current_evidence_required`",
        f"- source_evidence_status: `{(payload.get('source_materials') or {}).get('status', '')}`",
        "",
        "## Findings",
        "",
    ]
    for finding in payload.get("findings", []):
        lines.extend(
            [
                f"### {finding.get('finding_id', '')} - {finding.get('finding_family', '')}",
                "",
                f"- risk: `{finding.get('risk', '')}`",
                f"- affected_ac_ids: {', '.join(finding.get('affected_ac_ids') or []) or '-'}",
                f"- route_recommendation: `{finding.get('route_recommendation', '')}`",
                f"- authority_boundary: `{finding.get('authority_boundary', '')}`",
                f"- current_evidence_refs: {', '.join(finding.get('current_evidence_refs') or []) or '-'}",
                f"- deep_absorption_status: `{finding.get('deep_absorption_status', '')}`",
                "",
            ]
        )
        blocked_admissions = finding.get("blocked_admissions") if isinstance(finding.get("blocked_admissions"), list) else []
        if blocked_admissions:
            lines.extend(["#### Blocked Admissions", ""])
            for admission in blocked_admissions:
                lines.extend(
                    [
                        f"- reason_code: `{admission.get('reason_code', '')}`",
                        f"  route_recommendation: `{admission.get('route_recommendation', '')}`",
                    ]
                )
    lines.extend(["## Round Memory Influence", ""])
    for item in payload.get("round_memory", []):
        lines.extend(
            [
                f"- round_id: `{item.get('round_id', '')}`",
                f"  scenario: {item.get('scenario', '')}",
                f"  counts_as_pass_evidence: `{bool(item.get('counts_as_pass_evidence'))}`",
                f"  current_run_required: `{bool(item.get('current_run_required'))}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Authority Boundary",
            "",
            "- QA evo-deep cannot modify PRD, user-story, test-case, freeze state, QA verdict, or release verdict.",
            "- Authority bypass attempts must fail closed in requirement clarity or release readiness.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def run_qa_evo_deep(
    project_root: Path,
    *,
    version: str,
    feature: str,
    findings: list[dict[str, Any]] | None = None,
    round_memory: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    source_materials = load_qa_evo_deep_source_materials(project_root, version=resolved_version, feature=feature)
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "status": "ready",
        "generated_at": now_iso(),
        "output_policy": "routeable_findings_only",
        "round_memory_policy": "advisory_influence_only_current_evidence_required",
        "source_materials": source_materials,
        "findings": findings if findings is not None else default_qa_evo_deep_findings(feature=feature, version=resolved_version, source_materials=source_materials),
        "round_memory": round_memory if round_memory is not None else [build_round_memory_influence()],
        "deep_absorption_summary": {
            "status": "pending_formal_qa_absorption",
            "absorbed_count": 0,
            "eligible_for_release_supplement": False,
        },
    }
    validation = validate_qa_evo_deep_payload(payload)
    payload["validation"] = validation
    if validation["blocked"]:
        payload["status"] = "blocked"
    stored_payload = _storage_payload(payload)
    output_path = qa_evo_deep_path(project_root, version=resolved_version, feature=feature)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(payload), encoding="utf-8")
    machine_path = qa_evo_deep_machine_path(project_root, version=resolved_version, feature=feature)
    write_json(machine_path, stored_payload)
    payload["output_path"] = _rel(project_root, output_path)
    payload["machine_path"] = _rel(project_root, machine_path)
    stored_payload["output_path"] = payload["output_path"]
    stored_payload["machine_path"] = payload["machine_path"]
    write_json(machine_path, stored_payload)
    return stored_payload


def _storage_payload(payload: dict[str, Any]) -> dict[str, Any]:
    stored = dict(payload)
    source_materials = stored.get("source_materials") if isinstance(stored.get("source_materials"), dict) else {}
    if source_materials:
        source_copy = dict(source_materials)
        materials = source_copy.get("materials") if isinstance(source_copy.get("materials"), dict) else {}
        stored_materials: dict[str, Any] = {}
        for name, material in materials.items():
            if not isinstance(material, dict):
                continue
            item = dict(material)
            item.pop("text", None)
            if "payload" in item:
                item["payload_summary"] = {
                    "keys": sorted(str(key) for key in item.get("payload", {}).keys()) if isinstance(item.get("payload"), dict) else [],
                }
                item.pop("payload", None)
            stored_materials[str(name)] = item
        source_copy["materials"] = stored_materials
        stored["source_materials"] = source_copy
    return stored
