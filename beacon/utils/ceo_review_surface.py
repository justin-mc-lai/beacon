"""CEO review support-surface helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.change_surface import build_change_command
from beacon.utils.guidance_family import build_guidance_surface_projection
from beacon.utils.story_state import feature_slug
from beacon.utils.support_surface_transactions import build_support_surface_transaction, write_support_surface_transaction
from beacon.utils.versioning import resolve_target_version


def _doc_path(project_root: Path, version: str, feature: str, folder: str) -> Path:
    return project_root / "docs" / "beacon" / version / folder / f"{feature_slug(feature)}.md"


def _feature_truth_refs(project_root: Path, version: str, feature: str) -> list[Path]:
    prd = _doc_path(project_root, version, feature, "prd")
    story = _doc_path(project_root, version, feature, "user-story")
    test_case = _doc_path(project_root, version, feature, "qa/test-cases")
    return [path for path in (prd, story, test_case) if path.exists()]


def _version_package_features(project_root: Path, version: str) -> list[str]:
    change_doc = project_root / "docs" / "beacon" / version / "change" / f"{version}.md"
    if not change_doc.exists():
        return []
    try:
        text = change_doc.read_text(encoding="utf-8")
    except OSError:
        return []
    lines = text.splitlines()
    in_section = False
    features: list[str] = []
    for raw_line in lines:
        line = raw_line.rstrip()
        if re.match(r"^##\s+Feature Packages\s*$", line):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        match = re.match(r"^\s*-\s+`([^`]+)`\s*$", line)
        if match:
            features.append(match.group(1).strip())
    return features


def _resolve_truth_refs(project_root: Path, version: str, feature: str) -> tuple[list[Path], list[str]]:
    direct_refs = _feature_truth_refs(project_root, version, feature)
    if direct_refs:
        return direct_refs, []
    package_features = [item for item in _version_package_features(project_root, version) if item and item != feature]
    if not package_features:
        return [], []
    package_refs: list[Path] = []
    bound_features: list[str] = []
    for package_feature in package_features:
        refs = _feature_truth_refs(project_root, version, package_feature)
        if len(refs) == 3:
            package_refs.extend(refs)
            bound_features.append(package_feature)
    return package_refs, bound_features


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
    truth_refs, package_features = _resolve_truth_refs(project_root, resolved_version, feature)
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
            state_impact={"writes_transaction_state": True, "reopens_requirement_truth": False},
            gate_impact={"blocks_execution": True, "gate_owner": "support-route-only"},
            blocked=True,
            blocked_reason="truth_refs_missing",
            operator_visible_summary="CEO review is blocked because no bound PRD/user-story/test-case package was found.",
        )
        receipts = write_support_surface_transaction(project_root, version=resolved_version, payload=payload)
        payload["artifacts"] = receipts
        payload["guidance_family"] = build_guidance_surface_projection(
            "ceo-review",
            current_loop_layer="challenge",
            missing_evidence=["prd", "user-story", "test-case"],
            target_surface="beacon-help",
            recommended_route="beacon help",
        )
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
        state_impact={"writes_transaction_state": True, "reopens_requirement_truth": bool(writebacks)},
        gate_impact={"blocks_execution": bool(writebacks), "gate_owner": "support-route-only"},
        operator_visible_summary=(
            f"CEO review decision is `{resolved_decision}` for focus `{focus or 'full'}`."
            if writebacks
            else (
                f"CEO review did not find a version-level reframing blocker. Bound version package features: {', '.join(package_features)}."
                if package_features
                else "CEO review did not find a version-level reframing blocker."
            )
        ),
    )
    receipts = write_support_surface_transaction(project_root, version=resolved_version, payload=payload)
    payload["artifacts"] = receipts
    payload["guidance_family"] = build_guidance_surface_projection(
        "ceo-review",
        current_loop_layer="challenge",
        missing_evidence=[],
        target_surface=str(route.get("target_surface", "") or ""),
        recommended_route=str(route.get("command", "") or ""),
    )
    return payload
