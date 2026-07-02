"""QA defect repair loop contracts for Beacon v1.6.4."""

from __future__ import annotations

from typing import Any

from beacon.utils.qa_attribution import (
    FAILURE_FAMILIES,
    RELEASE_BLOCKING_FAMILIES,
    ROUTE_RECOMMENDATIONS,
    normalize_failure_family,
    route_for_failure_family,
)

REASON_REGRESSION_SKIPPED = "regression_skipped"
REASON_REPAIR_CHAIN_BROKEN = "repair_chain_broken"


def classify_defect(*, failure_family: str) -> dict[str, Any]:
    normalized = normalize_failure_family(failure_family)
    if not normalized:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "defect_classification_failed",
        }
    return {
        "schema_version": "1.0",
        "status": "pass",
        "blocked": False,
        "defect_classification": {
            "family": normalized,
            "reason_code": normalized,
        },
        "repair_route": route_for_failure_family(normalized),
        "release_blocking": normalized in RELEASE_BLOCKING_FAMILIES,
    }


def build_repair_loop_verdict(
    *,
    defect_finding: dict[str, Any] | None = None,
    fix_evidence: dict[str, Any] | None = None,
    regression_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    finding = defect_finding if isinstance(defect_finding, dict) else {}
    family = normalize_failure_family(str(finding.get("failure_family") or ""))
    if not family:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "defect_classification_failed",
            "repair_route": "",
            "defect_classification": {},
            "regression_required": False,
        }
    repair_route = route_for_failure_family(family)
    classification = {"family": family, "reason_code": family}
    regression_required = family in RELEASE_BLOCKING_FAMILIES
    fix_ok = bool(fix_evidence)
    regression_ok = bool(regression_evidence and regression_evidence.get("executed"))
    missing_segments: list[str] = []
    if not finding:
        missing_segments.append("defect")
    if regression_required and not fix_ok:
        missing_segments.append("fix")
    if regression_required and not regression_ok:
        missing_segments.append("regression")
    blocked = bool(missing_segments)
    reason_code = ""
    if blocked:
        if regression_required and not fix_ok:
            reason_code = REASON_REPAIR_CHAIN_BROKEN
        elif regression_required and not regression_ok:
            reason_code = REASON_REGRESSION_SKIPPED
        else:
            reason_code = REASON_REPAIR_CHAIN_BROKEN
    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": reason_code,
        "repair_route": repair_route,
        "defect_classification": classification,
        "regression_required": regression_required,
        "closure_chain": {
            "defect": bool(finding),
            "fix": fix_ok,
            "regression": regression_ok,
            "missing_segments": missing_segments,
        },
        "release_blocking": family in RELEASE_BLOCKING_FAMILIES,
        "supported_families": list(FAILURE_FAMILIES),
        "route_recommendations": dict(ROUTE_RECOMMENDATIONS),
    }
