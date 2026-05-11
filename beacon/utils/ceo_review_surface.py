"""CEO review support-surface helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.change_surface import build_change_command
from beacon.utils.story_state import feature_slug
from beacon.utils.support_surface_transactions import build_support_surface_transaction, write_support_surface_transaction
from beacon.utils.versioning import resolve_target_version


def _doc_path(project_root: Path, version: str, feature: str, folder: str) -> Path:
    return project_root / "docs" / "beacon" / version / folder / f"{feature_slug(feature)}.md"


def _decision_from_inputs(*, decision: str, focus: str, change_intent: str) -> str:
    explicit = str(decision or "").strip().lower()
    if explicit in {"expand", "hold", "reduce", "reframe"}:
        return explicit
    hint = f"{focus} {change_intent}".lower()
    if any(token in hint for token in ("reframe", "wrong problem", "wrong scope", "重构", "重定")):
        return "reframe"
    if any(token in hint for token in ("reduce", "shrink", "narrow", "收缩", "减少")):
        return "reduce"
    if any(token in hint for token in ("expand", "broaden", "widen", "扩展", "扩大")):
        return "expand"
    return "hold"


def run_ceo_review(
    project_root: Path,
    *,
    version: str,
    feature: str,
    focus: str = "full",
    decision: str = "",
    change_intent: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    prd = _doc_path(project_root, resolved_version, feature, "prd")
    story = _doc_path(project_root, resolved_version, feature, "user-story")
    test_case = _doc_path(project_root, resolved_version, feature, "qa/test-cases")
    truth_refs = [path for path in (prd, story, test_case) if path.exists()]
    if not truth_refs:
        payload = build_support_surface_transaction(
            surface="beacon-ceo-review",
            mode=focus or "full",
            version=resolved_version,
            feature=feature,
            status="blocked",
            decision="hold",
            reason_codes=["truth_refs_missing"],
            truth_refs=[],
            evidence_refs=[],
            route_decision={"route": "support-recovery", "target_surface": "beacon-help"},
            next_route={
                "command": "beacon help",
                "why": "CEO review cannot bind to missing requirement truth.",
                "target_surface": "beacon-help",
                "priority": "high",
                "prerequisites": [],
            },
            writeback_targets=[],
            blocked=True,
            blocked_reason="truth_refs_missing",
            operator_visible_summary="CEO review is blocked because no bound PRD/user-story/test-case package was found.",
        )
        receipts = write_support_surface_transaction(project_root, version=resolved_version, payload=payload)
        payload["artifacts"] = receipts
        return payload

    resolved_decision = _decision_from_inputs(decision=decision, focus=focus, change_intent=change_intent)
    if resolved_decision == "hold":
        route = {
            "command": f"beacon implement {json.dumps(feature, ensure_ascii=False)} --project {project_root} --version {resolved_version}",
            "why": "Requirement framing is stable enough to continue implementation planning.",
            "target_surface": "beacon-implement",
            "priority": "medium",
            "prerequisites": ["frozen requirement package remains valid"],
        }
        status = "advisory"
        writebacks: list[str] = []
    else:
        route = {
            "command": build_change_command(
                feature=feature,
                project_root=project_root,
                version=resolved_version,
                reason=change_intent or resolved_decision,
            ),
            "why": "Requirement direction must be updated before implementation truth remains reliable.",
            "target_surface": "beacon-change",
            "priority": "high",
            "prerequisites": ["accepted ceo-review decision"],
        }
        status = "accepted_for_writeback"
        writebacks = ["beacon-change", "beacon-prd", "beacon-user-story", "beacon-test-case"]
    payload = build_support_surface_transaction(
        surface="beacon-ceo-review",
        mode=focus or "full",
        version=resolved_version,
        feature=feature,
        status=status,
        decision=resolved_decision,
        truth_refs=[str(path.relative_to(project_root)) for path in truth_refs],
        evidence_refs=[],
        route_decision={"route": "change/refreeze" if writebacks else "implement", "target_surface": route["target_surface"]},
        next_route=route,
        writeback_targets=writebacks,
        operator_visible_summary=(
            f"CEO review decision is `{resolved_decision}` for focus `{focus or 'full'}`."
            if writebacks
            else "CEO review did not find a version-level reframing blocker."
        ),
    )
    receipts = write_support_surface_transaction(project_root, version=resolved_version, payload=payload)
    payload["artifacts"] = receipts
    return payload
