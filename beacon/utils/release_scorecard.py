"""Release scorecard aggregation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.exhaustiveness import load_exhaustiveness_report
from beacon.utils.implementation_plan import (
    implementation_plan_supported,
    list_implementation_git_workflow_contracts,
    load_implementation_plan_progress,
)
from beacon.utils.learning_loop import load_latest_evo_experiment
from beacon.utils.qa_precision import load_feature_qa_scorecard
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload, load_requirement_clarity_state
from beacon.utils.revision_state import load_revision_state
from beacon.utils.technical_review_contract import build_technical_review_gate_payload, load_technical_review_state
from beacon.utils.versioning import normalize_version
from beacon.utils.versioning import release_line_key, resolve_target_version


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _parse_semver_tuple(value: str | None) -> tuple[int, int, int]:
    normalized = release_line_key(value) or normalize_version(value) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _latest_implement_feature(project_root: Path) -> str:
    implement_root = project_root / ".beacon" / "implement"
    if not implement_root.exists():
        return ""
    for state_path in reversed(sorted(implement_root.glob("*/state.json"))):
        payload = _load_json(state_path)
        feature = str(payload.get("feature") or "").strip()
        if feature:
            return feature
    return ""


def build_release_scorecard(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    gate_report = _load_json(project_root / ".beacon" / "gate-report.json")
    qa_status = load_qa_status(project_root)
    feature = str(qa_status.get("feature") or "").strip() or _latest_implement_feature(project_root)
    exhaustiveness = load_exhaustiveness_report(project_root, feature=feature) if feature else {}
    feature_scorecard = load_feature_qa_scorecard(project_root, feature=feature) if feature else {}
    implementation_plan = (
        load_implementation_plan_progress(project_root, version=resolved_version, feature=feature)
        if feature and implementation_plan_supported(resolved_version)
        else {}
    )
    scorecard_state = _load_json(project_root / ".beacon" / "state" / "evo" / "scorecards" / "latest.json")
    latest_experiment = load_latest_evo_experiment(project_root)
    git_workflow_contracts = list_implementation_git_workflow_contracts(project_root, version=resolved_version)
    revision_state = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=False) if feature else {}
    requirement_clarity_gate = build_requirement_clarity_gate_payload(project_root, version=resolved_version, feature=feature) if feature else {}
    requirement_clarity_state = load_requirement_clarity_state(project_root, feature=feature) if feature else {}
    technical_review_gate = (
        build_technical_review_gate_payload(
            project_root,
            version=resolved_version,
            feature=feature,
            revision_id=str(revision_state.get("revision_id", "") or ""),
        )
        if feature
        else {}
    )
    technical_review_state = load_technical_review_state(project_root, feature=feature) if feature else {}
    blocked_count = len(
        [item for item in gate_report.get("issues", []) if isinstance(item, dict) and bool(item.get("blocked"))]
    ) if isinstance(gate_report.get("issues"), list) else 0
    decision_summary = scorecard_state.get("counts") if isinstance(scorecard_state.get("counts"), dict) else {}
    project_profile_gate = qa_status.get("project_profile_gate") if isinstance(qa_status.get("project_profile_gate"), dict) else {}
    project_gate_status = str(project_profile_gate.get("status") or "not_configured")
    legacy_release_ready = (
        str(gate_report.get("status") or "").strip().lower() == "pass"
        and str(qa_status.get("status") or "").strip().lower() == "passed"
        and bool(qa_status.get("evidence_done", False))
        and (not exhaustiveness or str(exhaustiveness.get("status") or "").strip().lower() == "passed")
    )
    release_ready = legacy_release_ready
    if _parse_semver_tuple(resolved_version) >= (1, 1, 10):
        release_ready = (
            legacy_release_ready
            and bool(feature_scorecard)
            and bool(feature_scorecard.get("release_ready", False))
            and project_gate_status in {"pass", "not_configured"}
            and not list(feature_scorecard.get("unresolved_closure_outcomes") or [])
        )
    if _parse_semver_tuple(resolved_version) >= (1, 3, 1):
        release_ready = (
            release_ready
            and bool(feature)
            and not bool(requirement_clarity_gate.get("blocked", False))
            and bool(requirement_clarity_state)
            and not bool(technical_review_gate.get("blocked", False))
            and str(technical_review_state.get("review_status") or "").strip().lower() in {"approved", "accepted"}
            and bool(technical_review_state)
        )
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "release_ready": release_ready,
        "gate": {
            "status": str(gate_report.get("status") or "unknown"),
            "blocked_count": blocked_count,
            "run_id": str(gate_report.get("run_id") or ""),
        },
        "qa": {
            "feature": feature,
            "status": str(qa_status.get("status") or "unknown"),
            "evidence_done": bool(qa_status.get("evidence_done", False)),
            "execution_mode": str(qa_status.get("execution_mode") or "feature-aware"),
            "project_profile_id": str(project_profile_gate.get("profile_id") or ""),
            "project_profile_gate_status": project_gate_status,
        },
        "exhaustiveness": exhaustiveness if isinstance(exhaustiveness, dict) else {},
        "feature_qa_scorecard": feature_scorecard if isinstance(feature_scorecard, dict) else {},
        "implementation_plan": implementation_plan if isinstance(implementation_plan, dict) else {},
        "git_workflow": {
            "count": len(git_workflow_contracts),
            "modes": sorted({str(item.get("mode", "") or "") for item in git_workflow_contracts if str(item.get("mode", "") or "")}),
            "expected_branches": sorted({str(item.get("expected_branch", "") or "") for item in git_workflow_contracts if str(item.get("expected_branch", "") or "")}),
            "service_directories": sorted({service for item in git_workflow_contracts for service in (item.get("service_directories") or []) if str(service).strip()}),
        },
        "requirement_clarity": {
            "status": str(requirement_clarity_gate.get("status") or "not_required"),
            "blocked": bool(requirement_clarity_gate.get("blocked", False)),
            "reason_code": str(requirement_clarity_gate.get("reason_code") or ""),
            "finding_count": int(requirement_clarity_state.get("finding_count") or len(requirement_clarity_gate.get("findings") or [])),
            "state_path": str(requirement_clarity_gate.get("state_path") or requirement_clarity_state.get("state_path") or ""),
            "report_json_path": str(requirement_clarity_gate.get("report_json_path") or ""),
            "report_markdown_path": str(requirement_clarity_gate.get("report_markdown_path") or ""),
        },
        "technical_review": {
            "status": str(technical_review_gate.get("status") or "not_required"),
            "blocked": bool(technical_review_gate.get("blocked", False)),
            "reason_code": str(technical_review_gate.get("reason_code") or ""),
            "review_status": str(technical_review_state.get("review_status") or ""),
            "approved_by": str(technical_review_state.get("approved_by") or ""),
            "state_path": str(technical_review_gate.get("state_path") or technical_review_state.get("state_path") or ""),
            "contract_json_path": str(technical_review_gate.get("contract_json_path") or ""),
            "contract_markdown_path": str(technical_review_gate.get("contract_markdown_path") or ""),
        },
        "learning_scorecard": {
            "main_kpi": str(scorecard_state.get("main_kpi") or "false_complete_rate"),
            "decision_summary": decision_summary,
            "candidate_count": len(scorecard_state.get("candidates", [])) if isinstance(scorecard_state.get("candidates"), list) else 0,
        },
        "latest_experiment": latest_experiment if isinstance(latest_experiment, dict) else {},
    }


def summarize_release_scorecard(scorecard: dict[str, Any] | None) -> dict[str, Any]:
    payload = scorecard if isinstance(scorecard, dict) else {}
    gate = payload.get("gate") if isinstance(payload.get("gate"), dict) else {}
    qa = payload.get("qa") if isinstance(payload.get("qa"), dict) else {}
    exhaustiveness = payload.get("exhaustiveness") if isinstance(payload.get("exhaustiveness"), dict) else {}
    feature_scorecard = payload.get("feature_qa_scorecard") if isinstance(payload.get("feature_qa_scorecard"), dict) else {}
    learning = payload.get("learning_scorecard") if isinstance(payload.get("learning_scorecard"), dict) else {}
    implementation_plan = payload.get("implementation_plan") if isinstance(payload.get("implementation_plan"), dict) else {}
    git_workflow = payload.get("git_workflow") if isinstance(payload.get("git_workflow"), dict) else {}
    requirement_clarity = payload.get("requirement_clarity") if isinstance(payload.get("requirement_clarity"), dict) else {}
    technical_review = payload.get("technical_review") if isinstance(payload.get("technical_review"), dict) else {}
    decisions = learning.get("decision_summary") if isinstance(learning.get("decision_summary"), dict) else {}
    latest_experiment = payload.get("latest_experiment") if isinstance(payload.get("latest_experiment"), dict) else {}
    return {
        "release_ready": bool(payload.get("release_ready", False)),
        "gate_status": str(gate.get("status") or "unknown"),
        "gate_blocked_count": int(gate.get("blocked_count") or 0),
        "qa_status": str(qa.get("status") or "unknown"),
        "qa_execution_mode": str(qa.get("execution_mode") or "feature-aware"),
        "qa_evidence_done": bool(qa.get("evidence_done", False)),
        "qa_project_profile_id": str(qa.get("project_profile_id") or ""),
        "qa_project_profile_gate_status": str(qa.get("project_profile_gate_status") or "not_configured"),
        "exhaustiveness_status": str(exhaustiveness.get("status") or ""),
        "exhaustiveness_score": exhaustiveness.get("score"),
        "exhaustiveness_threshold": exhaustiveness.get("threshold"),
        "release_confidence_min": feature_scorecard.get("release_confidence_min"),
        "release_confidence_avg": feature_scorecard.get("release_confidence_avg"),
        "review_required_count": int(feature_scorecard.get("review_required_count") or 0),
        "needs_replay_count": int(feature_scorecard.get("needs_replay_count") or 0),
        "false_complete_risk": feature_scorecard.get("false_complete_risk"),
        "unresolved_closure_outcomes": list(feature_scorecard.get("unresolved_closure_outcomes") or []),
        "continue_decision": str(feature_scorecard.get("continue_decision") or ""),
        "stop_reasons": list(feature_scorecard.get("stop_reasons") or []),
        "coverage_current": feature_scorecard.get("coverage_current") if isinstance(feature_scorecard.get("coverage_current"), dict) else {},
        "test_case_backfill_required": bool(feature_scorecard.get("test_case_backfill_required", False)),
        "resume_command": str(feature_scorecard.get("resume_command") or ""),
        "main_kpi": str(learning.get("main_kpi") or "false_complete_rate"),
        "main_kpi_score": latest_experiment.get("main_kpi_score"),
        "decision_keep": int(decisions.get("keep") or 0),
        "decision_review": int(decisions.get("review") or 0),
        "decision_discard": int(decisions.get("discard") or 0),
        "candidate_count": int(learning.get("candidate_count") or 0),
        "implementation_plan_status": str(implementation_plan.get("status") or ""),
        "implementation_plan_next_task_id": str(implementation_plan.get("next_task_id") or ""),
        "implementation_plan_blocked_task_ids": list(implementation_plan.get("blocked_task_ids") or []),
        "git_workflow_count": int(git_workflow.get("count") or 0),
        "git_workflow_modes": list(git_workflow.get("modes") or []),
        "git_workflow_expected_branches": list(git_workflow.get("expected_branches") or []),
        "requirement_clarity_status": str(requirement_clarity.get("status") or ""),
        "requirement_clarity_blocked": bool(requirement_clarity.get("blocked", False)),
        "requirement_clarity_finding_count": int(requirement_clarity.get("finding_count") or 0),
        "technical_review_status": str(technical_review.get("status") or ""),
        "technical_review_blocked": bool(technical_review.get("blocked", False)),
        "technical_review_review_status": str(technical_review.get("review_status") or ""),
    }
