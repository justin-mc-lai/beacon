"""Design review support-surface helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.change_surface import build_change_command
from beacon.utils.support_surface_transactions import build_support_surface_transaction, write_support_surface_transaction
from beacon.utils.versioning import resolve_target_version


def write_design_review_transaction(
    project_root: Path,
    *,
    version: str,
    feature: str,
    status: str,
    design_verdict: str,
    issues: list[dict[str, Any]],
    prototype_exists: bool,
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    critical = [item for item in issues if str(item.get("severity", "")).lower() == "critical"]
    blocked = bool(critical) and design_verdict != "prototype_not_required"
    blocked_reason = str(critical[0].get("reason_code", "") or "") if critical else ""
    if blocked:
        next_route = {
            "command": "beacon help",
            "why": "Design review found blocking gaps and should route to recovery guidance.",
            "target_surface": "beacon-help",
            "priority": "high",
            "prerequisites": [],
        }
        route_decision = {"route": "support-recovery", "target_surface": "beacon-help"}
        writebacks: list[str] = []
    elif design_verdict == "ready_for_prototype":
        next_route = {
            "command": f'beacon prototype "{feature}" --project-root {project_root} --version {resolved_version}',
            "why": "Design review cleared the feature for formal prototype freeze.",
            "target_surface": "beacon-prototype",
            "priority": "medium",
            "prerequisites": ["design_verdict=ready_for_prototype"],
        }
        route_decision = {"route": "prototype-entry", "target_surface": "beacon-prototype"}
        writebacks = ["beacon-prototype"]
    elif design_verdict == "prototype_not_required":
        next_route = {
            "command": f'beacon implement "{feature}" --project {project_root} --version {resolved_version}',
            "why": "No UI handoff is required, so implementation can proceed.",
            "target_surface": "beacon-implement",
            "priority": "medium",
            "prerequisites": ["prototype not required"],
        }
        route_decision = {"route": "implement", "target_surface": "beacon-implement"}
        writebacks = []
    else:
        next_route = {
            "command": build_change_command(
                feature=feature,
                project_root=project_root,
                version=resolved_version,
                reason="design-review-revision-required",
            ),
            "why": "Design direction or UX evidence needs revision before prototype freeze remains valid.",
            "target_surface": "beacon-change",
            "priority": "high",
            "prerequisites": ["design review revision required"],
        }
        route_decision = {"route": "change/refreeze", "target_surface": "beacon-change"}
        writebacks = ["beacon-change", "beacon-user-story", "beacon-test-case"]
    payload = build_support_surface_transaction(
        surface="beacon-design-review",
        mode="full",
        version=resolved_version,
        feature=feature,
        status="blocked" if blocked else ("accepted_for_writeback" if writebacks else "advisory"),
        decision=design_verdict,
        reason_codes=[str(item.get("reason_code", "") or "") for item in issues if str(item.get("reason_code", "")).strip()],
        truth_refs=[],
        evidence_refs=evidence_refs or [],
        route_decision=route_decision,
        next_route=next_route,
        writeback_targets=writebacks,
        blocked=blocked,
        blocked_reason=blocked_reason,
        operator_visible_summary=(
            "Design review found blocking issues." if blocked else f"Design review verdict is `{design_verdict}`."
        ),
    )
    receipts = write_support_surface_transaction(project_root, version=resolved_version, payload=payload)
    payload["artifacts"] = receipts
    payload["review_status"] = status
    return payload
