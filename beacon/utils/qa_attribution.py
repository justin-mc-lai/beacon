"""QA evidence attribution contracts for Beacon v1.4.10."""

from __future__ import annotations

from typing import Any


FAILURE_FAMILIES = (
    "implementation_gap",
    "truth_drift",
    "coverage_gap",
    "execution_lapse",
    "skill_defect",
    "runner_admission_blocker",
    "evidence_insufficient",
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

ROUTE_RECOMMENDATIONS = {
    "implementation_gap": "beacon-implement",
    "truth_drift": "beacon-change",
    "coverage_gap": "beacon-test-case",
    "execution_lapse": "beacon-qa",
    "skill_defect": "beacon-change",
    "runner_admission_blocker": "blocked",
    "evidence_insufficient": "beacon-qa",
}

PROPOSAL_ONLY_FAMILIES = {"skill_defect"}
RELEASE_BLOCKING_FAMILIES = {
    "implementation_gap",
    "truth_drift",
    "coverage_gap",
    "runner_admission_blocker",
    "evidence_insufficient",
}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def normalize_failure_family(value: str) -> str:
    normalized = str(value or "").strip()
    return normalized if normalized in FAILURE_FAMILIES else ""


def route_for_failure_family(failure_family: str) -> str:
    normalized = normalize_failure_family(failure_family)
    return ROUTE_RECOMMENDATIONS.get(normalized, "beacon-qa")


def build_qa_attribution(
    *,
    failure_family: str,
    affected_ac_ids: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    route_recommendation: str = "",
    verdict_boundary: str = "qa_input",
    notes: str = "",
    runner_reached_ac_evaluation: bool = True,
    blocker_reason: str = "",
    admission_surface: str = "",
    authority_boundary: str = "support_evidence_only",
    mutation_attempted: bool = False,
) -> dict[str, Any]:
    normalized_family = normalize_failure_family(failure_family)
    if not normalized_family:
        normalized_family = "evidence_insufficient"
    route = str(route_recommendation or "").strip() or route_for_failure_family(normalized_family)
    payload = {
        "schema_version": "1.0",
        "failure_family": normalized_family,
        "affected_ac_ids": _string_list(affected_ac_ids or []),
        "evidence_refs": _string_list(evidence_refs or []),
        "route_recommendation": route,
        "verdict_boundary": str(verdict_boundary or "qa_input").strip(),
        "notes": str(notes or "").strip(),
        "runner_reached_ac_evaluation": bool(runner_reached_ac_evaluation),
        "blocker_reason": str(blocker_reason or "").strip(),
        "admission_surface": str(admission_surface or "").strip(),
        "authority_boundary": str(authority_boundary or "support_evidence_only").strip(),
        "support_evidence_only": True,
        "runtime_evidence_only": True,
        "truth_authority": False,
        "verdict_authority": False,
        "release_pass_evidence": False,
        "proposal_only": normalized_family in PROPOSAL_ONLY_FAMILIES,
        "mutation_attempted": bool(mutation_attempted),
    }
    payload["validation"] = validate_qa_attribution(payload)
    return payload


def validate_qa_attribution(payload: dict[str, Any]) -> dict[str, Any]:
    item = payload if isinstance(payload, dict) else {}
    issues: list[dict[str, Any]] = []
    family = normalize_failure_family(str(item.get("failure_family") or ""))
    if not family:
        issues.append({"reason_code": "qa_attribution_unknown_failure_family"})
    affected = _string_list(item.get("affected_ac_ids") or [])
    evidence_refs = _string_list(item.get("evidence_refs") or [])
    runner_reached_ac = bool(item.get("runner_reached_ac_evaluation", True))
    if family != "runner_admission_blocker" and not affected:
        issues.append({"reason_code": "qa_attribution_ac_binding_missing"})
    if not evidence_refs:
        issues.append({"reason_code": "qa_attribution_evidence_refs_missing"})
    if family == "runner_admission_blocker":
        if runner_reached_ac and not affected:
            issues.append({"reason_code": "qa_attribution_runner_blocker_ac_context_missing"})
        if not str(item.get("blocker_reason") or "").strip():
            issues.append({"reason_code": "qa_attribution_runner_blocker_reason_missing"})
        if not str(item.get("admission_surface") or "").strip():
            issues.append({"reason_code": "qa_attribution_runner_blocker_surface_missing"})
    expected_route = route_for_failure_family(family)
    actual_route = str(item.get("route_recommendation") or "").strip()
    if family and actual_route != expected_route:
        issues.append(
            {
                "reason_code": "qa_attribution_route_mismatch",
                "expected_route": expected_route,
                "actual_route": actual_route,
            }
        )
    authority_boundary = str(item.get("authority_boundary") or "").strip()
    verdict_boundary = str(item.get("verdict_boundary") or "").strip()
    if authority_boundary in AUTHORITY_BOUNDARIES or verdict_boundary in AUTHORITY_BOUNDARIES:
        issues.append({"reason_code": "qa_attribution_authority_bypass"})
    if bool(item.get("truth_authority")) or bool(item.get("verdict_authority")) or bool(item.get("release_pass_evidence")):
        issues.append({"reason_code": "qa_attribution_authority_bypass"})
    if family == "skill_defect":
        if not bool(item.get("proposal_only")):
            issues.append({"reason_code": "qa_attribution_skill_defect_not_proposal_only"})
        if bool(item.get("mutation_attempted")):
            issues.append({"reason_code": "qa_attribution_skill_mutation_forbidden"})
    status = "blocked" if issues else "pass"
    return {
        "schema_version": "1.0",
        "status": status,
        "blocked": bool(issues),
        "issues": issues,
    }


def coerce_qa_attribution(payload: dict[str, Any]) -> dict[str, Any]:
    item = payload if isinstance(payload, dict) else {}
    family = normalize_failure_family(str(item.get("failure_family") or ""))
    if not family:
        family = "evidence_insufficient"
    coerced = build_qa_attribution(
        failure_family=family,
        affected_ac_ids=_string_list(item.get("affected_ac_ids") or []),
        evidence_refs=_string_list(item.get("evidence_refs") or []),
        route_recommendation=str(item.get("route_recommendation") or "").strip(),
        verdict_boundary=str(item.get("verdict_boundary") or "qa_input").strip(),
        notes=str(item.get("notes") or "").strip(),
        runner_reached_ac_evaluation=bool(item.get("runner_reached_ac_evaluation", True)),
        blocker_reason=str(item.get("blocker_reason") or "").strip(),
        admission_surface=str(item.get("admission_surface") or "").strip(),
        authority_boundary=str(item.get("authority_boundary") or "support_evidence_only").strip(),
        mutation_attempted=bool(item.get("mutation_attempted")),
    )
    for field in ("truth_authority", "verdict_authority", "release_pass_evidence", "proposal_only"):
        if field in item:
            coerced[field] = bool(item.get(field))
    coerced["validation"] = validate_qa_attribution(coerced)
    return coerced


def summarize_qa_attributions(attributions: list[dict[str, Any]] | None) -> dict[str, Any]:
    normalized = [coerce_qa_attribution(item) for item in (attributions or []) if isinstance(item, dict)]
    family_counts = {family: 0 for family in FAILURE_FAMILIES}
    route_counts: dict[str, int] = {}
    blocked_count = 0
    release_blocking_count = 0
    proposal_count = 0
    accepted_count = 0
    for item in normalized:
        family = str(item.get("failure_family") or "")
        if family in family_counts:
            family_counts[family] += 1
        route = str(item.get("route_recommendation") or "")
        if route:
            route_counts[route] = route_counts.get(route, 0) + 1
        validation = item.get("validation") if isinstance(item.get("validation"), dict) else {}
        blocked = bool(validation.get("blocked"))
        if blocked:
            blocked_count += 1
        else:
            accepted_count += 1
        if family in RELEASE_BLOCKING_FAMILIES:
            release_blocking_count += 1
        if bool(item.get("proposal_only")):
            proposal_count += 1
    return {
        "schema_version": "1.0",
        "status": "not_applicable" if not normalized else ("blocked" if blocked_count else "recorded"),
        "support_evidence_only": True,
        "runtime_evidence_only": True,
        "truth_authority": False,
        "verdict_authority": False,
        "release_pass_evidence": False,
        "attribution_count": len(normalized),
        "accepted_count": accepted_count,
        "blocked_count": blocked_count,
        "release_blocking_count": release_blocking_count,
        "proposal_count": proposal_count,
        "family_counts": family_counts,
        "route_counts": route_counts,
        "attributions": normalized,
    }
