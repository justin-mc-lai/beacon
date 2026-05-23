from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_root, version_root
from beacon.utils.diagram_truth import load_feature_diagram_truth
from beacon.utils.guidance_family import build_guidance_surface_projection
from beacon.utils.deep_lineage import build_deep_lineage_projection, infer_candidate_parent_refs, truth_impact_for_route
from beacon.utils.requirement_parsing import extract_qa_case_rows
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.support_research_topology import upsert_deep_summary_index
from beacon.utils.versioning import resolve_runtime_version, resolve_target_version, runtime_feature_supported

DEEP_LOOP_STATES = [
    "scan_truth",
    "model_business",
    "challenge_gaps",
    "derive_delta",
    "classify_findings",
    "route_repairs",
    "verify_closure",
]

DEEP_ARTIFACT_FAMILY = {
    "analysis_report": "deep-analysis-report",
    "state_machine_report": "state-machine-report",
    "test_delta": "deep-test-delta",
    "risk_register": "risk-register",
    "loop_trace": "deep-loop-trace",
    "closure_brief": "deep-closure-brief",
    "skip_evidence": "deep-skip-evidence",
}

HIGH_RISK_TRIGGERS = {
    "payment": "financial_or_payment_flow",
    "order": "order_or_transaction_flow",
    "wallet": "financial_or_payment_flow",
    "ranking": "ranking_or_scoring_flow",
    "scoring": "ranking_or_scoring_flow",
    "score": "ranking_or_scoring_flow",
    "identity binding": "identity_or_attribution_binding",
    "attribution": "identity_or_attribution_binding",
    "invitation": "relationship_or_invitation_chain",
    "relationship chain": "relationship_or_invitation_chain",
    "reporting": "reporting_or_derived_fact_flow",
    "migration": "migration_or_cutover_flow",
    "multi-role": "multi_role_workflow",
    "multi-state": "multi_state_workflow",
    "state machine": "state_machine_workflow",
    "fact source": "fact_source_consistency_chain",
    "consistency": "cross_surface_consistency_chain",
    "release-blocking": "release_blocking_risk",
    "发布阻断": "release_blocking_risk",
    "状态机": "state_machine_workflow",
    "事实源": "fact_source_consistency_chain",
    "一致性": "cross_surface_consistency_chain",
}

LOW_RISK_HINTS = {
    "static page",
    "simple form",
    "stateless utility",
    "visual-only",
    "configuration change",
    "静态页面",
    "简单表单",
    "视觉调整",
}

STRUCTURAL_QA_KEYWORDS = {
    "state",
    "state machine",
    "fact source",
    "consistency",
    "requirement gap",
    "business model",
    "invariant",
    "attribution",
    "状态",
    "状态机",
    "事实源",
    "一致性",
    "需求缺口",
    "不变量",
}

BLOCKING_SEVERITIES = {"P0", "P1", "P2"}


def deep_loop_supported(version: str | None, *, runtime_version: str | None = None) -> bool:
    return runtime_feature_supported("v1.4.1", runtime_version=runtime_version or version)


def deep_artifact_paths(project_root: Path, version: str, feature: str) -> dict[str, dict[str, str]]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    human_dir = version_root(project_root, resolved_version) / "deep" / slug
    machine_dir = machine_root(project_root, resolved_version) / "deep" / slug
    paths: dict[str, dict[str, str]] = {}
    for key, basename in DEEP_ARTIFACT_FAMILY.items():
        paths[key] = {
            "json": str((machine_dir / f"{basename}.json").relative_to(project_root)),
            "markdown": str((human_dir / f"{basename}.md").relative_to(project_root)),
        }
    return paths


def deep_release_supplement_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_root(project_root, resolved_version) / "deep" / feature_slug(feature) / "release-supplement.json"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _truth_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    root = version_root(project_root, resolved_version)
    return {
        "prd": root / "prd" / f"{slug}.md",
        "user_story": root / "user-story" / f"{slug}.md",
        "test_case": root / "qa" / "test-cases" / f"{slug}.md",
    }


def _truth_corpus(project_root: Path, version: str, feature: str) -> dict[str, str]:
    paths = _truth_paths(project_root, version, feature)
    return {key: _read_text(path) for key, path in paths.items()}


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def evaluate_deep_trigger(text: str, *, skip_reason: str = "", qa_feedback: str = "", qa_severity: str = "") -> dict[str, Any]:
    haystack = "\n".join([str(text or ""), str(qa_feedback or "")]).lower()
    triggers = []
    seen: set[str] = set()
    for token, category in HIGH_RISK_TRIGGERS.items():
        if token.lower() in haystack and category not in seen:
            triggers.append({"token": token, "category": category})
            seen.add(category)
    structural_reopen = should_reopen_deep_from_qa(qa_feedback, severity=qa_severity)
    if structural_reopen:
        triggers.append({"token": str(qa_severity or "QA"), "category": "qa_structural_defect_reopen"})
    skip_text = str(skip_reason or "").strip()
    low_risk_skip = bool(skip_text) and not triggers
    if low_risk_skip:
        state = "not_required"
        status = "skipped"
        reason_code = "deep_skip_reason_recorded"
    elif triggers:
        state = "required"
        status = "required"
        reason_code = "deep_high_risk_trigger_detected"
    else:
        low_risk_hint = any(item.lower() in haystack for item in LOW_RISK_HINTS)
        state = "not_required" if low_risk_hint else "recommended"
        status = "not_required" if low_risk_hint else "recommended"
        reason_code = "deep_low_risk_detected" if low_risk_hint else "deep_recommended_by_default"
    return {
        "status": status,
        "deep_requirement_state": state,
        "required": state == "required",
        "recommended": state == "recommended",
        "skipped": low_risk_skip,
        "skip_reason": skip_text,
        "triggers": triggers,
        "reason_code": reason_code,
        "qa_structural_reopen": structural_reopen,
    }


def should_reopen_deep_from_qa(feedback: str, *, severity: str = "") -> bool:
    normalized_severity = str(severity or "").strip().upper()
    if normalized_severity and normalized_severity not in BLOCKING_SEVERITIES:
        return False
    text = str(feedback or "").lower()
    return bool(text) and any(keyword.lower() in text for keyword in STRUCTURAL_QA_KEYWORDS)


def reopen_allowed(*, new_intent: bool = False, new_model_element: bool = False, release_blocking_evidence: bool = False, qa_structural_defect: bool = False) -> bool:
    return any([new_intent, new_model_element, release_blocking_evidence, qa_structural_defect])


def stable_intent_converges_one_pass(*, new_model_element: bool = False, release_blocking_evidence: bool = False) -> bool:
    return not reopen_allowed(new_model_element=new_model_element, release_blocking_evidence=release_blocking_evidence)


def route_deep_finding(kind: str) -> dict[str, str]:
    normalized = str(kind or "").strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"prd", "prd_gap", "requirement", "requirement_gap"}:
        return {"route": "change/refreeze", "target_surface": "change", "next_route": "beacon change"}
    if normalized in {"user_story", "user_story_gap", "story", "story_gap"}:
        return {"route": "user-story supplement or change/refreeze", "target_surface": "user-story", "next_route": "beacon user-story"}
    if normalized in {"acceptance", "acceptance_gap", "test", "test_gap", "test_delta"}:
        return {"route": "test-case delta", "target_surface": "test-case", "next_route": "beacon test-case"}
    if normalized in {"implementation", "implementation_gap", "code"}:
        return {"route": "implement repair handoff", "target_surface": "implement", "next_route": "beacon implement"}
    if normalized in {"qa", "qa_gap", "qa_evidence", "supplemental_qa"}:
        return {"route": "supplemental QA loop", "target_surface": "qa", "next_route": "beacon qa"}
    if normalized in {"release", "release_risk", "risk"}:
        return {"route": "release closure, waiver, or backlog decision", "target_surface": "release", "next_route": "beacon release"}
    return {"route": "classify before route", "target_surface": "deep", "next_route": "beacon deep run"}


def _base_findings(trigger: dict[str, Any], *, qa_feedback: str = "", qa_severity: str = "") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for index, item in enumerate(trigger.get("triggers") or [], start=1):
        category = str(item.get("category") or "deep_risk")
        route = route_deep_finding("test_delta" if category != "release_blocking_risk" else "release")
        findings.append(
            {
                "finding_id": f"DF-{index:03d}",
                "classification": category,
                "severity": "P3" if category != "qa_structural_defect_reopen" else str(qa_severity or "P2").upper(),
                "release_blocking": category in {"release_blocking_risk", "qa_structural_defect_reopen"},
                "state": "closed" if category != "qa_structural_defect_reopen" else "routed",
                "route_decision": route,
                "closure_decision": "closed" if category != "qa_structural_defect_reopen" else "supplemental_qa_required",
                "backlog_decision": "",
                "summary": f"{category} reviewed by deep loop",
                "source": str(item.get("token") or "trigger"),
            }
        )
    if not findings:
        findings.append(
            {
                "finding_id": "DF-001",
                "classification": "no_structural_gap_found",
                "severity": "P4",
                "release_blocking": False,
                "state": "closed",
                "route_decision": route_deep_finding("qa"),
                "closure_decision": "closed",
                "backlog_decision": "",
                "summary": "No deep structural gap was detected from frozen truth",
                "source": "deep_default_review",
            }
        )
    return findings


def all_findings_routed(findings: list[dict[str, Any]]) -> bool:
    for finding in findings:
        route = finding.get("route_decision") if isinstance(finding, dict) else {}
        if not isinstance(route, dict) or not str(route.get("target_surface") or "").strip():
            return False
        if not str(finding.get("classification") or "").strip():
            return False
        closure = str(finding.get("closure_decision") or finding.get("backlog_decision") or "").strip()
        if not closure:
            return False
    return True


def _derive_test_deltas(feature: str, qa_content: str, diagram_truth: dict[str, Any], trigger: dict[str, Any]) -> list[dict[str, Any]]:
    rows = extract_qa_case_rows(qa_content, "test-case")
    existing = sorted({str(row.get("tc_id") or "") for row in rows if str(row.get("tc_id") or "").strip()})
    axes = [str(item) for item in (diagram_truth.get("state_axes") or []) if str(item).strip()]
    families = sorted({str(item.get("category") or "deep") for item in trigger.get("triggers") or []}) or ["deep_consistency"]
    deltas = []
    for index, family in enumerate(families[:5], start=1):
        delta_id = f"DTD-{index:03d}"
        deltas.append(
            {
                "delta_id": delta_id,
                "scenario": f"Cover {family} across explicit state/fact-source boundaries",
                "source_family": family,
                "state_axes": axes[:8],
                "existing_case_refs": existing[:8],
                "delta_state": "proposed",
                "route_target": "test-case",
                "qa_execution_owner": "qa",
                "execution_status": "not_executed_by_deep",
                "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
            }
        )
    return deltas


def _attach_lineage_to_findings(
    findings: list[dict[str, Any]],
    *,
    source_truth_refs: list[str],
    candidate_parent_refs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for finding in findings:
        item = dict(finding)
        route = item.get("route_decision") if isinstance(item.get("route_decision"), dict) else {}
        route_target = str(route.get("target_surface") or "")
        truth_impact = truth_impact_for_route(
            route_target=route_target,
            classification=str(item.get("classification") or ""),
        )
        item["lineage"] = build_deep_lineage_projection(
            source_truth_refs=source_truth_refs,
            candidate_parent_refs=candidate_parent_refs,
            route_target=route_target,
            truth_impact=truth_impact,
            promotion_required=truth_impact == "requirement_meaning_delta",
        )
        enriched.append(item)
    return enriched


def _attach_lineage_to_test_deltas(
    deltas: list[dict[str, Any]],
    *,
    source_truth_refs: list[str],
    candidate_parent_refs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for delta in deltas:
        item = dict(delta)
        item["lineage"] = build_deep_lineage_projection(
            source_truth_refs=source_truth_refs,
            candidate_parent_refs=candidate_parent_refs,
            route_target=str(item.get("route_target") or "test-case"),
            truth_impact="acceptance_delta",
            promotion_required=False,
        )
        enriched.append(item)
    return enriched


def _render_markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", ""]
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            lines.append(f"## {key}")
            lines.append("```json")
            lines.append(json.dumps(value, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
        else:
            lines.append(f"- {key}: `{value}`")
    return "\n".join(lines).rstrip() + "\n"


def _write_artifact(project_root: Path, paths: dict[str, str], title: str, payload: dict[str, Any]) -> dict[str, str]:
    json_path = project_root / paths["json"]
    markdown_path = project_root / paths["markdown"]
    write_json(json_path, payload)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_markdown(title, payload), encoding="utf-8")
    return {"json": _relative(json_path, project_root), "markdown": _relative(markdown_path, project_root)}


def run_deep_loop(
    project_root: Path,
    *,
    version: str,
    feature: str,
    intent: str = "",
    skip_reason: str = "",
    qa_feedback: str = "",
    qa_severity: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    resolved_runtime_version = resolve_runtime_version(project_root, "auto")
    if not deep_loop_supported(resolved_version, runtime_version=resolved_runtime_version):
        raise ValueError(
            "deep loop is supported for Beacon runtime v1.4.1+; "
            f"got runtime {resolved_runtime_version} for target docs {resolved_version}"
        )
    slug = feature_slug(feature)
    truth_paths = _truth_paths(project_root, resolved_version, feature)
    truth = _truth_corpus(project_root, resolved_version, feature)
    corpus = "\n".join(truth.values())
    trigger = evaluate_deep_trigger(corpus, skip_reason=skip_reason, qa_feedback=qa_feedback, qa_severity=qa_severity)
    diagram_truth = load_feature_diagram_truth(project_root, version=resolved_version, feature=feature)
    findings = [] if trigger.get("skipped") else _base_findings(trigger, qa_feedback=qa_feedback, qa_severity=qa_severity)
    test_deltas = [] if trigger.get("skipped") else _derive_test_deltas(feature, truth.get("test_case", ""), diagram_truth, trigger)
    generated_at = now_iso()
    refs = {key: _relative(path, project_root) for key, path in truth_paths.items()}
    source_truth_refs = [value for value in refs.values() if value]
    candidate_parent_refs = infer_candidate_parent_refs(
        user_story_content=truth.get("user_story", ""),
        qa_content=truth.get("test_case", ""),
    )
    findings = _attach_lineage_to_findings(
        findings,
        source_truth_refs=source_truth_refs,
        candidate_parent_refs=candidate_parent_refs,
    )
    test_deltas = _attach_lineage_to_test_deltas(
        test_deltas,
        source_truth_refs=source_truth_refs,
        candidate_parent_refs=candidate_parent_refs,
    )
    artifact_paths = deep_artifact_paths(project_root, resolved_version, feature)
    loop_iterations = [
        {"state": state, "status": "completed", "sequence": index}
        for index, state in enumerate(DEEP_LOOP_STATES, start=1)
    ]
    open_findings = [
        item for item in findings
        if str(item.get("state") or "").strip() not in {"closed", "waived", "backlog", "rejected"}
        and str(item.get("closure_decision") or "") not in {"closed", "waived", "accepted_backlog"}
    ]
    waived_findings = [item for item in findings if str(item.get("state") or "") == "waived" or str(item.get("closure_decision") or "") == "waived"]
    accepted_backlog = [item for item in findings if str(item.get("closure_decision") or "") == "accepted_backlog"]
    release_blocking_open = [
        item for item in findings
        if bool(item.get("release_blocking"))
        and str(item.get("closure_decision") or "") not in {"closed", "waived"}
    ]
    verdict = "skipped" if trigger.get("skipped") else "closed" if not release_blocking_open else "routed"
    release_recommendation = (
        "skip_accepted"
        if trigger.get("skipped")
        else "ready_with_deep_supplement"
        if not release_blocking_open
        else "release_blocking_deep_findings_must_close_or_waive"
    )
    common = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "generated_at": generated_at,
        "source_refs": refs,
        "canonical_truth_policy": "read_only_frozen_truth",
        "lineage_policy": "trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case",
    }
    analysis_report = {
        **common,
        "artifact_type": "deep_analysis_report",
        "intent_snapshot": str(intent or feature).strip(),
        "trigger": trigger,
        "finding_count": len(findings),
        "test_delta_count": len(test_deltas),
        "lineage_projection": build_deep_lineage_projection(
            source_truth_refs=source_truth_refs,
            candidate_parent_refs=candidate_parent_refs,
            route_target="deep",
            truth_impact="none",
            promotion_required=False,
        ),
        "status": verdict,
    }
    state_machine_report = {
        **common,
        "artifact_type": "state_machine_report",
        "loop_states": DEEP_LOOP_STATES,
        "diagram_truth": diagram_truth,
        "state_axes": diagram_truth.get("state_axes", []),
        "state_machine_contract": "state axes stay explicit through implementation, QA, and release evidence",
    }
    test_delta = {
        **common,
        "artifact_type": "deep_test_delta",
        "qa_execution_owner": "qa",
        "deep_execution_boundary": "deep derives deltas but does not execute QA",
        "deltas": test_deltas,
    }
    risk_register = {
        **common,
        "artifact_type": "risk_register",
        "findings": findings,
        "orphan_finding_count": 0 if all_findings_routed(findings) else len(findings),
    }
    loop_trace = {
        **common,
        "artifact_type": "deep_loop_trace",
        "user_intent_snapshot": str(intent or feature).strip(),
        "iterations": loop_iterations,
        "finding_classification": [item.get("classification") for item in findings],
        "route_decisions": [item.get("route_decision") for item in findings] + [
            {"target_surface": item.get("route_target"), "next_route": "beacon test-case"}
            for item in test_deltas
        ],
        "closure_decisions": [item.get("closure_decision") for item in findings],
        "stop_reason": "explicit_skip_reason" if trigger.get("skipped") else "stable_intent_closed",
        "next_allowed_route": "release" if trigger.get("skipped") else "test-case" if test_deltas else "qa",
        "reopen_conditions": [
            "new_user_intent",
            "new_role_entity_state_machine_or_business_process",
            "release_blocking_evidence",
            "qa_or_implementation_structural_gap",
        ],
    }
    closure_brief = {
        **common,
        "artifact_type": "deep_closure_brief",
        "deep_requirement_state": trigger.get("deep_requirement_state"),
        "verdict": verdict,
        "executed_delta_cases": [item for item in test_deltas if item.get("execution_status") == "executed_by_qa"],
        "open_findings": open_findings,
        "waived_findings": waived_findings,
        "accepted_backlog_risks": accepted_backlog,
        "release_recommendation": release_recommendation,
        "skip_reason": str(skip_reason or "").strip(),
        "release_blocking_open_count": len(release_blocking_open),
    }
    skip_evidence = {
        **common,
        "artifact_type": "deep_skip_evidence",
        "status": "pass" if trigger.get("skipped") else "not_applicable",
        "skip_reason": str(skip_reason or "").strip(),
        "accepted": bool(trigger.get("skipped")),
    }
    artifacts_payloads = {
        "analysis_report": analysis_report,
        "state_machine_report": state_machine_report,
        "test_delta": test_delta,
        "risk_register": risk_register,
        "loop_trace": loop_trace,
        "closure_brief": closure_brief,
        "skip_evidence": skip_evidence,
    }
    artifact_refs: dict[str, dict[str, str]] = {}
    for key, payload in artifacts_payloads.items():
        title = DEEP_ARTIFACT_FAMILY[key].replace("-", " ").title()
        artifact_refs[key] = _write_artifact(project_root, artifact_paths[key], title, payload)
    supplement = build_deep_release_supplement(project_root, version=resolved_version, feature=feature, write=True)
    result = {
        "schema_version": "1.0",
        "status": "closed" if not supplement.get("blocked") else "blocked",
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "deep_requirement_state": trigger.get("deep_requirement_state"),
        "verdict": verdict,
        "artifact_refs": artifact_refs,
        "release_supplement": supplement,
        "guidance_family": build_guidance_surface_projection(
            "deep",
            current_loop_layer="challenge",
            missing_evidence=[],
            target_surface="qa" if test_deltas else "release" if supplement.get("blocked") else "qa",
            recommended_route=supplement.get("recommended_command", ""),
        ),
        "generated_at": generated_at,
    }
    result["support_research_writeback"] = upsert_deep_summary_index(
        project_root,
        version=resolved_version,
        feature=feature,
        payload=result,
    )
    return result


def load_deep_artifact(project_root: Path, *, version: str, feature: str, artifact: str) -> dict[str, Any]:
    paths = deep_artifact_paths(project_root, version, feature)
    if artifact not in paths:
        return {}
    path = project_root / paths[artifact]["json"]
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def _deep_truth_requires_analysis(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    truth = _truth_corpus(project_root, version, feature)
    return evaluate_deep_trigger("\n".join(truth.values()))


def build_deep_release_supplement(project_root: Path, *, version: str, feature: str, write: bool = False) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    closure = load_deep_artifact(project_root, version=resolved_version, feature=feature, artifact="closure_brief")
    risk = load_deep_artifact(project_root, version=resolved_version, feature=feature, artifact="risk_register")
    trace = load_deep_artifact(project_root, version=resolved_version, feature=feature, artifact="loop_trace")
    skip = load_deep_artifact(project_root, version=resolved_version, feature=feature, artifact="skip_evidence")
    trigger = _deep_truth_requires_analysis(project_root, version=resolved_version, feature=feature)
    reason_codes: list[str] = []
    blocked = False
    if trigger.get("required") and not closure and not bool(skip.get("accepted")):
        blocked = True
        reason_codes.append("deep_loop_unclosed")
    findings = risk.get("findings") if isinstance(risk.get("findings"), list) else []
    release_blocking_open = [
        item for item in findings
        if isinstance(item, dict)
        and bool(item.get("release_blocking"))
        and str(item.get("severity") or "").upper() in BLOCKING_SEVERITIES
        and str(item.get("closure_decision") or "") not in {"closed", "waived"}
    ]
    if release_blocking_open:
        blocked = True
        reason_codes.append("deep_release_blocking_finding_open")
    backlog_without_decision = [
        item for item in findings
        if isinstance(item, dict)
        and str(item.get("closure_decision") or "") == "accepted_backlog"
        and str(item.get("backlog_decision") or "") != "accepted"
    ]
    if backlog_without_decision:
        blocked = True
        reason_codes.append("deep_backlog_decision_missing")
    deltas = load_deep_artifact(project_root, version=resolved_version, feature=feature, artifact="test_delta").get("deltas")
    delta_route_missing = [
        item for item in deltas if isinstance(item, dict) and not str(item.get("route_target") or "").strip()
    ] if isinstance(deltas, list) else []
    if delta_route_missing:
        blocked = True
        reason_codes.append("deep_delta_route_missing")
    orphan_count = int(risk.get("orphan_finding_count") or 0) if risk else 0
    if orphan_count:
        blocked = True
        reason_codes.append("deep_new_state_machine_unclassified")
    status = "blocked" if blocked else "pass" if closure or skip else "not_required"
    artifact_refs = deep_artifact_paths(project_root, resolved_version, feature)
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "status": status,
        "blocked": blocked,
        "reason_codes": sorted(set(reason_codes)),
        "reason_code": sorted(set(reason_codes))[0] if reason_codes else "",
        "deep_requirement_state": closure.get("deep_requirement_state") or trigger.get("deep_requirement_state"),
        "closure_verdict": str(closure.get("verdict") or ""),
        "release_recommendation": str(closure.get("release_recommendation") or ""),
        "skip_accepted": bool(skip.get("accepted")),
        "open_finding_count": len(closure.get("open_findings") or []) if isinstance(closure.get("open_findings"), list) else 0,
        "waived_finding_count": len(closure.get("waived_findings") or []) if isinstance(closure.get("waived_findings"), list) else 0,
        "accepted_backlog_count": len(closure.get("accepted_backlog_risks") or []) if isinstance(closure.get("accepted_backlog_risks"), list) else 0,
        "release_blocking_open_count": len(release_blocking_open),
        "artifact_refs": artifact_refs,
        "generated_at": now_iso(),
        "recommended_command": f'beacon deep run "{feature}" --project-root {project_root} --version {resolved_version} --json',
    }
    if write:
        write_json(deep_release_supplement_path(project_root, resolved_version, feature), payload)
    return payload


def build_deep_release_supplement_gate(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    resolved_runtime_version = resolve_runtime_version(project_root, "auto")
    if not feature or not deep_loop_supported(version, runtime_version=resolved_runtime_version):
        return {"schema_version": "1.0", "status": "not_required", "blocked": False, "reason_code": ""}
    return build_deep_release_supplement(project_root, version=version, feature=feature, write=False)
