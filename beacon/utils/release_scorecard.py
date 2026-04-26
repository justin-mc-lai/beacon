"""Release scorecard aggregation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import change_docs_file, change_file_output
from beacon.utils.delivery_kernel import load_delivery_read_model
from beacon.utils.evidence_manifest import validate_evidence_manifest
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
from beacon.utils.semantic_runtime import evaluate_semantic_contract
from beacon.utils.story_state import feature_slug
from beacon.utils.technical_review_contract import build_technical_review_gate_payload, load_technical_review_state
from beacon.utils.prototype_support import version_requires_prototype
from beacon.utils.versioning import (
    project_runtime_feature_enabled,
    resolve_runtime_version,
    resolve_target_version,
    runtime_feature_supported,
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _state_sort_key(path: Path, payload: dict[str, Any]) -> tuple[str, str, str, str, str, str, int, str]:
    return (
        str(payload.get("frozen_at") or ""),
        str(payload.get("accepted_at") or ""),
        str(payload.get("completed_at") or ""),
        str(payload.get("updated_at") or ""),
        str(payload.get("created_at") or ""),
        str(payload.get("written_at") or ""),
        path.stat().st_mtime_ns if path.exists() else 0,
        path.name,
    )


def _latest_implement_feature(project_root: Path, *, version: str | None = None) -> str:
    implement_root = project_root / ".beacon" / "implement"
    if not implement_root.exists():
        return ""
    candidates: list[tuple[Path, dict[str, Any]]] = []
    for state_path in implement_root.glob("*/state.json"):
        payload = _load_json(state_path)
        payload_version = str(payload.get("version") or "").strip()
        if version and payload_version and payload_version != version:
            continue
        if str(payload.get("feature") or "").strip():
            candidates.append((state_path, payload))
    for state_path, payload in sorted(candidates, key=lambda item: _state_sort_key(item[0], item[1]), reverse=True):
        feature = str(payload.get("feature") or "").strip()
        if feature:
            return feature
    return ""


def _latest_revision_feature(project_root: Path, *, version: str) -> str:
    revision_root = project_root / "docs" / "beacon" / version / ".machine" / "execution"
    if not revision_root.exists():
        return ""
    candidates: list[tuple[Path, dict[str, Any]]] = []
    for state_path in revision_root.glob("*.revision.json"):
        payload = _load_json(state_path)
        if str(payload.get("feature") or "").strip():
            candidates.append((state_path, payload))
    for state_path, payload in sorted(candidates, key=lambda item: _state_sort_key(item[0], item[1]), reverse=True):
        feature = str(payload.get("feature") or "").strip()
        if feature:
            return feature
    return ""


def _resolve_scorecard_feature(project_root: Path, *, version: str, qa_status: dict[str, Any]) -> str:
    feature = str(qa_status.get("feature") or "").strip()
    if feature:
        return feature
    return _latest_revision_feature(project_root, version=version) or _latest_implement_feature(
        project_root,
        version=version,
    )


def _version_change_status(project_root: Path, *, version: str, current_feature: str) -> dict[str, Any]:
    markdown_path = change_docs_file(project_root, version, f"{version}.md")
    json_path = change_file_output(project_root, version, f"{version}.json")
    payload = _load_json(json_path)
    payload_version = str(payload.get("version") or "").strip()
    features = payload.get("features") if isinstance(payload.get("features"), list) else []
    feature_slugs = sorted(
        {
            str(item.get("feature_slug") or "").strip()
            for item in features
            if isinstance(item, dict) and str(item.get("feature_slug") or "").strip()
        }
    )
    current_feature_slug = feature_slug(current_feature) if str(current_feature or "").strip() else ""
    includes_current_feature = (not current_feature_slug) or current_feature_slug in feature_slugs
    markdown_exists = markdown_path.exists()
    json_exists = json_path.exists()
    version_match = bool(payload) and payload_version == version
    status = "pass" if markdown_exists and json_exists and version_match and includes_current_feature else "blocked"
    if not markdown_exists and not json_exists and not payload:
        status = "missing"
    return {
        "status": status,
        "markdown_path": str(markdown_path.relative_to(project_root)),
        "json_path": str(json_path.relative_to(project_root)),
        "markdown_exists": markdown_exists,
        "json_exists": json_exists,
        "version_match": version_match,
        "feature_count": int(payload.get("feature_count") or len(feature_slugs) or 0),
        "feature_slugs": feature_slugs,
        "current_feature_slug": current_feature_slug,
        "includes_current_feature": includes_current_feature,
    }


def _feature_change_payload(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    if not feature:
        return {}
    path = change_file_output(project_root, version, f"{feature_slug(feature)}.json")
    payload = _load_json(path)
    if not payload:
        return {}
    payload_version = str(payload.get("version") or "").strip()
    if payload_version and payload_version != version:
        return {}
    return payload


def _revision_binding(revision_state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(revision_state, dict) or not revision_state:
        return {
            "status": "missing",
            "reason_code": "revision_missing",
            "revision_id": "",
            "source_revision_id": "",
            "superseded_by": "",
            "doc_status": "",
            "delivery_status": "",
            "gate_bound_to_latest_revision": False,
        }
    doc_status = str(revision_state.get("doc_status") or "")
    superseded_by = str(revision_state.get("superseded_by") or "")
    if superseded_by:
        status = "superseded"
        reason_code = "revision_superseded"
    elif doc_status != "frozen":
        status = "reopened"
        reason_code = "revision_not_frozen"
    else:
        status = "bound"
        reason_code = ""
    return {
        "status": status,
        "reason_code": reason_code,
        "revision_id": str(revision_state.get("revision_id") or ""),
        "source_revision_id": str(revision_state.get("source_revision_id") or ""),
        "superseded_by": superseded_by,
        "doc_status": doc_status,
        "delivery_status": str(revision_state.get("delivery_status") or ""),
        "gate_bound_to_latest_revision": status == "bound",
    }


def _delivery_type(revision_state: dict[str, Any], feature_change: dict[str, Any]) -> str:
    revision_id = str(revision_state.get("revision_id") or "")
    source_revision_id = str(revision_state.get("source_revision_id") or "")
    if not source_revision_id and revision_id in {"", "R1"}:
        return "initial"
    added = [str(item).strip() for item in (feature_change.get("added") or []) if str(item).strip()]
    removed = [str(item).strip() for item in (feature_change.get("removed") or []) if str(item).strip()]
    fixed = [str(item).strip() for item in (feature_change.get("fixed") or []) if str(item).strip()]
    if fixed and not added and not removed:
        return "hotfix"
    return "revised"


def _semantic_gate_required(project_root: Path, *, version: str, runtime_version: str, feature: str) -> bool:
    return (
        bool(str(feature or "").strip())
        and project_runtime_feature_enabled(
            project_root,
            "v1.3.6",
            docs_version=version,
            runtime_version=runtime_version,
        )
        and version_requires_prototype(project_root, version)
    )


def build_release_scorecard(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    resolved_runtime = resolve_runtime_version(project_root, "auto")
    gate_report = _load_json(project_root / ".beacon" / "gate-report.json")
    evidence_manifest = validate_evidence_manifest(project_root)
    qa_status = load_qa_status(project_root)
    gate_version = str(gate_report.get("version") or "").strip()
    gate_version_match = not gate_version or gate_version == resolved_version
    qa_version = str(qa_status.get("version") or "").strip()
    qa_version_match = not qa_version or qa_version == resolved_version
    if not qa_version_match:
        qa_status = {}
    feature = _resolve_scorecard_feature(project_root, version=resolved_version, qa_status=qa_status)
    exhaustiveness = load_exhaustiveness_report(project_root, feature=feature) if feature else {}
    feature_scorecard = load_feature_qa_scorecard(project_root, feature=feature) if feature else {}
    implementation_plan = (
        load_implementation_plan_progress(project_root, version=resolved_version, feature=feature)
        if feature and implementation_plan_supported(resolved_version)
        else {}
    )
    scorecard_state = _load_json(project_root / ".beacon" / "state" / "evo" / "scorecards" / "latest.json")
    latest_experiment = load_latest_evo_experiment(project_root)
    if isinstance(latest_experiment, dict):
        experiment_version = str(latest_experiment.get("version") or "").strip()
        if experiment_version and experiment_version != resolved_version:
            latest_experiment = {}
    git_workflow_contracts = list_implementation_git_workflow_contracts(project_root, version=resolved_version)
    revision_state = load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=False) if feature else {}
    revision_binding = _revision_binding(revision_state)
    feature_change = _feature_change_payload(project_root, version=resolved_version, feature=feature) if feature else {}
    delivery_type = _delivery_type(revision_state, feature_change) if feature else ""
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
    change_documents = _version_change_status(project_root, version=resolved_version, current_feature=feature)
    semantic = (
        evaluate_semantic_contract(project_root, version=resolved_version, feature=feature)
        if _semantic_gate_required(project_root, version=resolved_version, runtime_version=resolved_runtime, feature=feature)
        else {}
    )
    semantic_pass = (not semantic) or str(semantic.get("status") or "").strip().lower() == "pass"
    blocked_count = len(
        [item for item in gate_report.get("issues", []) if isinstance(item, dict) and bool(item.get("blocked"))]
    ) if isinstance(gate_report.get("issues"), list) else 0
    gate_status = str(gate_report.get("status") or "unknown")
    gate_reason_codes = sorted(
        {
            str(item.get("reason_code") or "").strip()
            for item in (gate_report.get("issues") if isinstance(gate_report.get("issues"), list) else [])
            if isinstance(item, dict) and str(item.get("reason_code") or "").strip()
        }
    )
    if bool(evidence_manifest.get("blocked")):
        gate_status = "Blocked"
        blocked_count = max(blocked_count, int(evidence_manifest.get("blocked_count") or 0))
        gate_reason_codes = sorted(
            {
                *gate_reason_codes,
                *[
                    str(item.get("reason_code") or "").strip()
                    for item in (evidence_manifest.get("issues") if isinstance(evidence_manifest.get("issues"), list) else [])
                    if isinstance(item, dict) and str(item.get("reason_code") or "").strip()
                ],
            }
        )
    gate_pass = gate_status.strip().lower() == "pass"
    decision_summary = scorecard_state.get("counts") if isinstance(scorecard_state.get("counts"), dict) else {}
    project_profile_gate = qa_status.get("project_profile_gate") if isinstance(qa_status.get("project_profile_gate"), dict) else {}
    if not project_profile_gate and isinstance(feature_scorecard, dict):
        project_profile_gate = {
            "status": str(feature_scorecard.get("project_profile_gate_status") or "not_configured"),
            "profile_id": str(feature_scorecard.get("project_profile_id") or ""),
        }
    project_gate_status = str(project_profile_gate.get("status") or "not_configured")
    qa_passed = str(qa_status.get("status") or "").strip().lower() == "passed"
    feature_scorecard_release_ready = bool(feature_scorecard.get("release_ready", False))
    feature_scorecard_continue_decision = str(feature_scorecard.get("continue_decision") or "").strip()
    qa_evidence_done = bool(qa_status.get("evidence_done", False))
    exhaustiveness_pass = (not exhaustiveness) or str(exhaustiveness.get("status") or "").strip().lower() == "passed"
    feature_scorecard_authoritative = (
        bool(feature_scorecard)
        and feature_scorecard_release_ready
        and feature_scorecard_continue_decision == "ready_for_release"
        and not list(feature_scorecard.get("unresolved_closure_outcomes") or [])
    )
    legacy_release_ready = (
        gate_pass
        and qa_passed
        and qa_evidence_done
        and exhaustiveness_pass
        and gate_version_match
        and qa_version_match
    )
    release_ready = legacy_release_ready
    if runtime_feature_supported("v1.1.10", runtime_version=resolved_runtime):
        release_ready = (
            gate_pass
            and qa_passed
            and (qa_evidence_done or feature_scorecard_release_ready or feature_scorecard_continue_decision == "ready_for_release")
            and bool(feature_scorecard)
            and feature_scorecard_release_ready
            and project_gate_status in {"pass", "not_configured"}
            and not list(feature_scorecard.get("unresolved_closure_outcomes") or [])
            and (exhaustiveness_pass or feature_scorecard_authoritative)
            and gate_version_match
            and qa_version_match
        )
    if project_runtime_feature_enabled(
        project_root,
        "v1.3.3",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    ):
        release_ready = (
            release_ready
            and bool(feature)
            and bool(revision_binding.get("gate_bound_to_latest_revision", False))
            and semantic_pass
            and not bool(requirement_clarity_gate.get("blocked", False))
            and bool(requirement_clarity_state)
            and not bool(technical_review_gate.get("blocked", False))
            and str(technical_review_state.get("review_status") or "").strip().lower() in {"approved", "accepted"}
            and bool(technical_review_state)
            and bool(change_documents.get("markdown_exists", False))
            and bool(change_documents.get("json_exists", False))
            and bool(change_documents.get("version_match", False))
            and bool(change_documents.get("includes_current_feature", False))
        )
    if (
        runtime_feature_supported("v1.1.10", runtime_version=resolved_runtime)
        and gate_pass
        and feature_scorecard_authoritative
        and bool(revision_binding.get("gate_bound_to_latest_revision", False))
        and semantic_pass
        and project_gate_status in {"pass", "not_configured"}
        and bool(change_documents.get("markdown_exists", False))
        and bool(change_documents.get("json_exists", False))
        and bool(change_documents.get("version_match", False))
        and bool(change_documents.get("includes_current_feature", False))
    ):
        release_ready = True
    release_delivery_read_model = load_delivery_read_model(
        project_root,
        version=resolved_version,
        feature=feature,
        release_payload={
            "release_ready": release_ready,
            "gate": {
                "status": gate_status,
            },
            "qa": {
                "status": str(qa_status.get("status") or "unknown"),
            },
            "semantic": semantic if isinstance(semantic, dict) else {},
            "revision_binding": revision_binding,
            "risk_flags": [str(semantic.get("reason_code") or "").strip()] if semantic and not semantic_pass else [],
        },
    ) if feature else {
        "schema_version": "1.0",
        "feature": "",
        "version": resolved_version,
        "contract": {},
        "implement": {"delivery_contract": {}},
        "qa": {"delivery_contract": {}},
        "release": {
            "gate_status": gate_status,
            "release_ready": release_ready,
            "semantic": semantic if isinstance(semantic, dict) else {},
            "revision_binding": revision_binding,
        },
        "traceability": {"requirement_binding": {}, "requirement_refs": [], "runtime_refs": []},
        "risk_flags": [str(semantic.get("reason_code") or "").strip()] if semantic and not semantic_pass else [],
    }
    prompt_boundary = (
        ((release_delivery_read_model.get("implement") or {}).get("prompt_boundary"))
        if isinstance(release_delivery_read_model.get("implement"), dict)
        else {}
    )
    prompt_boundary = prompt_boundary if isinstance(prompt_boundary, dict) else {}
    prompt_boundary_ok = (not prompt_boundary) or (
        (not bool(prompt_boundary.get("required", False)))
        or (
            str(prompt_boundary.get("status") or "").strip().lower() == "pass"
            and not bool(prompt_boundary.get("blocked", False))
        )
    )
    if project_runtime_feature_enabled(
        project_root,
        "v1.3.7",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    ):
        release_ready = release_ready and prompt_boundary_ok
        release_section = (
            release_delivery_read_model.get("release")
            if isinstance(release_delivery_read_model.get("release"), dict)
            else {}
        )
        if isinstance(release_section, dict):
            release_section["release_ready"] = release_ready
    host_native_reason_codes = list(release_delivery_read_model.get("risk_flags") or [])
    if semantic and not semantic_pass:
        host_native_reason_codes.append(str(semantic.get("reason_code") or "semantic_not_ready"))
    host_native_delivery = {
        "schema_version": "1.0",
        "implement": (release_delivery_read_model.get("implement") or {}).get("delivery_contract", {}),
        "qa": (release_delivery_read_model.get("qa") or {}).get("delivery_contract", {}),
        "semantic": semantic if isinstance(semantic, dict) else {},
        "status": (
            "pass"
            if release_ready
            else "blocked"
            if list(release_delivery_read_model.get("risk_flags") or [])
            else "warn"
        ),
        "reason_codes": sorted({code for code in host_native_reason_codes if str(code).strip()}),
        "traceability": dict(release_delivery_read_model.get("traceability") or {}),
    }
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "runtime_version": resolved_runtime,
        "release_ready": release_ready,
        "gate": {
            "status": gate_status,
            "blocked_count": blocked_count,
            "run_id": str(gate_report.get("run_id") or ""),
            "artifact_version": gate_version,
            "version_match": gate_version_match,
            "reason_codes": gate_reason_codes,
        },
        "qa": {
            "feature": feature,
            "status": str(qa_status.get("status") or "unknown"),
            "evidence_done": bool(qa_status.get("evidence_done", False)),
            "execution_mode": str(qa_status.get("execution_mode") or "feature-aware"),
            "project_profile_id": str(project_profile_gate.get("profile_id") or ""),
            "project_profile_gate_status": project_gate_status,
            "artifact_version": qa_version,
            "version_match": qa_version_match,
        },
        "delivery": {
            "type": delivery_type,
            "revision_id": str(revision_state.get("revision_id") or ""),
            "source_revision_id": str(revision_state.get("source_revision_id") or ""),
        },
        "semantic": semantic if isinstance(semantic, dict) else {},
        "revision_binding": revision_binding,
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
        "prompt_boundary": prompt_boundary,
        "change_documents": change_documents,
        "learning_scorecard": {
            "main_kpi": str(scorecard_state.get("main_kpi") or "false_complete_rate"),
            "decision_summary": decision_summary,
            "candidate_count": len(scorecard_state.get("candidates", [])) if isinstance(scorecard_state.get("candidates"), list) else 0,
        },
        "latest_experiment": latest_experiment if isinstance(latest_experiment, dict) else {},
        "evidence_manifest": evidence_manifest,
        "delivery_read_model": release_delivery_read_model,
        "host_native_delivery": host_native_delivery,
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
    prompt_boundary = payload.get("prompt_boundary") if isinstance(payload.get("prompt_boundary"), dict) else {}
    change_documents = payload.get("change_documents") if isinstance(payload.get("change_documents"), dict) else {}
    delivery = payload.get("delivery") if isinstance(payload.get("delivery"), dict) else {}
    semantic = payload.get("semantic") if isinstance(payload.get("semantic"), dict) else {}
    revision_binding = payload.get("revision_binding") if isinstance(payload.get("revision_binding"), dict) else {}
    decisions = learning.get("decision_summary") if isinstance(learning.get("decision_summary"), dict) else {}
    latest_experiment = payload.get("latest_experiment") if isinstance(payload.get("latest_experiment"), dict) else {}
    host_native_delivery = payload.get("host_native_delivery") if isinstance(payload.get("host_native_delivery"), dict) else {}
    return {
        "release_ready": bool(payload.get("release_ready", False)),
        "gate_status": str(gate.get("status") or "unknown"),
        "gate_blocked_count": int(gate.get("blocked_count") or 0),
        "gate_reason_codes": list(gate.get("reason_codes") or []),
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
        "prompt_boundary_required": bool(prompt_boundary.get("required", False)),
        "prompt_boundary_status": str(prompt_boundary.get("status") or ""),
        "prompt_boundary_blocked": bool(prompt_boundary.get("blocked", False)),
        "prompt_boundary_classification": str(prompt_boundary.get("classification") or ""),
        "prompt_boundary_reason_code": str(prompt_boundary.get("reason_code") or ""),
        "prompt_boundary_surface": str(prompt_boundary.get("surface") or ""),
        "delivery_type": str(delivery.get("type") or ""),
        "delivery_revision_id": str(delivery.get("revision_id") or ""),
        "delivery_source_revision_id": str(delivery.get("source_revision_id") or ""),
        "semantic_status": str(semantic.get("status") or ""),
        "semantic_reason_code": str(semantic.get("reason_code") or ""),
        "release_revision_binding_status": str(revision_binding.get("status") or ""),
        "release_revision_binding_reason": str(revision_binding.get("reason_code") or ""),
        "release_revision_current": bool(revision_binding.get("gate_bound_to_latest_revision", False)),
        "change_documents_status": str(change_documents.get("status") or ""),
        "change_documents_markdown_exists": bool(change_documents.get("markdown_exists", False)),
        "change_documents_json_exists": bool(change_documents.get("json_exists", False)),
        "change_documents_version_match": bool(change_documents.get("version_match", False)),
        "change_documents_feature_count": int(change_documents.get("feature_count") or 0),
        "change_documents_includes_current_feature": bool(change_documents.get("includes_current_feature", False)),
        "host_native_delivery_status": str(host_native_delivery.get("status") or ""),
        "host_native_delivery_reason_codes": list(host_native_delivery.get("reason_codes") or []),
    }
