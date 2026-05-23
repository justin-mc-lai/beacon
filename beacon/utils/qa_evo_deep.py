"""QA evo-deep contracts for v1.4.10."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json
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


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def default_qa_evo_deep_findings(*, feature: str, version: str) -> list[dict[str, Any]]:
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
                "affected_ac_ids": [],
                "state_or_flow_refs": [],
                "round_memory_refs": [],
                "current_evidence_refs": [],
                "blocked_admissions": [],
                "route_recommendation": DEFAULT_ROUTES["qa_evidence_gap"],
                "release_supplement_input": "",
                "authority_boundary": "routeable_finding_only",
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
    families = {str(item.get("finding_family") or "") for item in findings if isinstance(item, dict)}
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
    return {
        "schema_version": "1.0",
        "status": "blocked" if issues else "pass",
        "blocked": bool(issues),
        "issues": issues,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# QA Evo Deep: {payload['feature']}",
        "",
        f"- version: `{payload['version']}`",
        f"- status: `{payload['status']}`",
        "- verdict_policy: `routeable_findings_only`",
        "- qa_round_memory_policy: `advisory_influence_only_current_evidence_required`",
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
                "",
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
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "status": "ready",
        "generated_at": now_iso(),
        "output_policy": "routeable_findings_only",
        "round_memory_policy": "advisory_influence_only_current_evidence_required",
        "findings": findings if findings is not None else default_qa_evo_deep_findings(feature=feature, version=resolved_version),
        "round_memory": round_memory if round_memory is not None else [build_round_memory_influence()],
    }
    validation = validate_qa_evo_deep_payload(payload)
    payload["validation"] = validation
    if validation["blocked"]:
        payload["status"] = "blocked"
    output_path = qa_evo_deep_path(project_root, version=resolved_version, feature=feature)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(payload), encoding="utf-8")
    machine_path = qa_evo_deep_machine_path(project_root, version=resolved_version, feature=feature)
    write_json(machine_path, payload)
    payload["output_path"] = _rel(project_root, output_path)
    payload["machine_path"] = _rel(project_root, machine_path)
    return payload
