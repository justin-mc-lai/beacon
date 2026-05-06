"""Requirement deepening helpers for Beacon v1.3.12+."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, resolve_target_version

_DIMENSION_ORDER = [
    "actors",
    "capability_differences",
    "state_machine",
    "happy_paths",
    "negative_paths",
    "boundary_conditions",
    "exceptions",
    "recovery_paths",
    "risks",
    "open_questions",
]
_STORY_CANDIDATE_FAMILIES = [
    "primary_actor_goal",
    "secondary_or_opposing_role",
    "state_transition",
    "exception_recovery",
    "permission_or_constraint",
    "governance_extension",
]
_COVERAGE_FAMILIES = [
    "happy",
    "negative",
    "boundary",
    "exception",
    "recovery",
    "compatibility",
    "permission",
    "stale-data-or-drift",
    "downgrade-or-fallback",
]


def requirement_deepening_supported(version: str | None) -> bool:
    normalized = normalize_version(version) or ""
    if not normalized.startswith("v"):
        return False
    try:
        major, minor, patch = [int(part) for part in normalized[1:].split(".")]
    except Exception:  # noqa: BLE001
        return False
    return (major, minor, patch) >= (1, 3, 12)


def requirement_dir(project_root: Path, version: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return project_root / "docs" / "beacon" / resolved_version / ".machine" / "requirement"


def requirement_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    root = requirement_dir(project_root, resolved_version)
    return {
        "dir": root,
        "envelope": root / f"{slug}.envelope.json",
        "candidate_ledger": root / f"{slug}.candidate-ledger.json",
        "decision_log": root / f"{slug}.supplement-decision-log.json",
        "freeze_contract": root / f"{slug}.freeze-contract.json",
        "completeness": root / f"{slug}.completeness.json",
        "supplement_task": root / f"{slug}.supplement-task.json",
        "re_freeze_transaction": root / f"{slug}.re-freeze-transaction.json",
    }


def _snippet_lines(text: str, *, limit: int = 8) -> list[str]:
    rows: list[str] = []
    for raw in str(text or "").splitlines():
        stripped = raw.strip().strip("-*")
        if not stripped or stripped.startswith("#") or stripped.startswith("| ---"):
            continue
        rows.append(stripped)
        if len(rows) >= limit:
            break
    return rows


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = str(text or "").lower()
    return any(token in lowered for token in needles)


def _source_ref(label: str, relative_path: str) -> str:
    return f"{label}:{relative_path}" if relative_path else label


def build_requirement_envelope(
    *,
    feature: str,
    version: str,
    prd_content: str,
    user_story_content: str,
    qa_content: str,
    prd_source: str,
    user_story_source: str,
    qa_source: str,
) -> dict[str, Any]:
    prd_lines = _snippet_lines(prd_content, limit=14)
    us_lines = _snippet_lines(user_story_content, limit=10)
    qa_lines = _snippet_lines(qa_content, limit=10)
    corpus = "\n".join([feature, prd_content, user_story_content, qa_content])

    actor_seed = []
    if _contains_any(corpus, ("owner", "operator", "admin", "运营", "管理")):
        actor_seed.append("operator")
    if _contains_any(corpus, ("user", "customer", "buyer", "用户", "顾客")):
        actor_seed.append("user")
    if not actor_seed:
        actor_seed = ["user", "operator"]

    open_questions = []
    for row in prd_lines + us_lines:
        if "?" in row or "？" in row or _contains_any(row, ("待", "open question", "unresolved", "clarif")):
            open_questions.append(row)
    if not open_questions:
        open_questions = ["Requirement package must keep accepted/rejected/deferred decisions queryable."]

    dimensions = {
        "actors": [
            {
                "name": actor,
                "source_truth_ref": prd_source,
                "rationale": "derived from PRD and current requirement package",
            }
            for actor in actor_seed
        ],
        "capability_differences": [
            {
                "name": "role-specific capability differences",
                "source_truth_ref": prd_source,
                "rationale": "v1.3.12 requires role and capability variance discovery",
            }
        ],
        "state_machine": [
            {
                "name": "draft -> supplemented -> refrozen -> delivery-consumed",
                "source_truth_ref": prd_source,
                "rationale": "requirement deepening adds explicit human-loop refreeze semantics",
            }
        ],
        "happy_paths": [
            {
                "name": "PRD deepened into story/test-case and consumed by implement/qa",
                "source_truth_ref": prd_source,
                "rationale": "main requirement closure path",
            }
        ],
        "negative_paths": [
            {
                "name": "host deepening unavailable and rule fallback used",
                "source_truth_ref": prd_source,
                "rationale": "downgrade path must stay auditable",
            }
        ],
        "boundary_conditions": [
            {
                "name": "no new public lifecycle stage or command",
                "source_truth_ref": prd_source,
                "rationale": "global boundary constraint",
            }
        ],
        "exceptions": [
            {
                "name": "manual markdown patch without decision trail",
                "source_truth_ref": user_story_source,
                "rationale": "must fail closed for silent truth mutation",
            }
        ],
        "recovery_paths": [
            {
                "name": "decision_log -> writeback_projection -> truth_refreeze",
                "source_truth_ref": prd_source,
                "rationale": "formal recovery/writeback contract",
            }
        ],
        "risks": [
            {
                "name": "scope creep from uncontrolled LLM expansion",
                "source_truth_ref": prd_source,
                "rationale": "accepted/rejected/deferred decisions required",
            }
        ],
        "open_questions": [
            {
                "name": item,
                "source_truth_ref": prd_source,
                "rationale": "carry unresolved clarification into machine-readable envelope",
            }
            for item in open_questions[:4]
        ],
    }
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "generated_at": now_iso(),
        "sources": {
            "prd": prd_source,
            "user_story": user_story_source,
            "qa": qa_source,
        },
        "dimensions": dimensions,
        "source_excerpt": {
            "prd": prd_lines,
            "user_story": us_lines,
            "qa": qa_lines,
        },
    }


def build_story_candidates(
    envelope: dict[str, Any],
    *,
    existing_ac_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    existing_text = "\n".join(
        f"{item.get('text', '')}\n" + "\n".join(str(detail) for detail in (item.get("details") or []))
        for item in existing_ac_items
        if isinstance(item, dict)
    ).lower()
    candidates: list[dict[str, Any]] = []
    for index, family in enumerate(_STORY_CANDIDATE_FAMILIES, start=1):
        keywords = family.replace("_", " ")
        status = "candidate_missing"
        if any(token in existing_text for token in keywords.split()):
            status = "already_frozen"
        candidates.append(
            {
                "candidate_id": f"SC-{index:03d}",
                "candidate_kind": "story",
                "family": family,
                "status": status,
                "title": f"{family.replace('_', ' ')} story",
                "source_truth_ref": str(envelope.get("sources", {}).get("prd") or "prd"),
                "rationale": f"deepening requires explicit {family.replace('_', ' ')} coverage",
                "writeback_target": "user-story.acceptance-criteria",
            }
        )
    return candidates


def build_coverage_candidates(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    prd_source = str(envelope.get("sources", {}).get("prd") or "prd")
    for index, family in enumerate(_COVERAGE_FAMILIES, start=1):
        candidates.append(
            {
                "candidate_id": f"CC-{index:03d}",
                "candidate_kind": "coverage",
                "family": family,
                "status": "candidate_missing",
                "source_truth_ref": prd_source,
                "rationale": f"coverage family {family} must be explicitly expanded from requirement truth",
                "risk_family": family,
                "writeback_target": "qa/test-cases.executable-matrix",
            }
        )
    return candidates


def build_candidate_ledger(
    *,
    feature: str,
    version: str,
    revision_id: str,
    story_candidates: list[dict[str, Any]],
    coverage_candidates: list[dict[str, Any]],
    compiler: dict[str, Any],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    fallback_reason = str(compiler.get("fallback_reason") or "")
    for index, candidate in enumerate(story_candidates + coverage_candidates, start=1):
        entries.append(
            {
                "gap_id": f"GAP-{index:03d}",
                "gap_type": "story" if candidate.get("candidate_kind") == "story" else "coverage",
                "source_truth_ref": str(candidate.get("source_truth_ref") or ""),
                "candidate_kind": str(candidate.get("candidate_kind") or ""),
                "candidate_payload": candidate,
                "rationale": str(candidate.get("rationale") or ""),
                "confidence": "medium" if fallback_reason else "high",
                "human_decision": "deferred" if fallback_reason else "accepted",
                "decision_reason": "rule fallback remains auditable" if fallback_reason else "seeded by requirement freeze package",
                "writeback_target": str(candidate.get("writeback_target") or ""),
                "resolved_at": None if fallback_reason else now_iso(),
                "revision_id": revision_id,
            }
        )
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "revision_id": revision_id,
        "generated_at": now_iso(),
        "entries": entries,
    }


def build_completeness_payload(
    *,
    feature: str,
    version: str,
    revision_id: str,
    compiler: dict[str, Any],
    coverage_candidates: list[dict[str, Any]],
    decision_log_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    fallback_reason = str(compiler.get("fallback_reason") or "")
    effective_mode = str(compiler.get("effective_mode") or "")
    unresolved = [
        entry for entry in decision_log_entries if str(entry.get("human_decision") or "") in {"deferred", "rejected"}
    ]
    verdict = "pass"
    if fallback_reason or effective_mode == "rule":
        verdict = "pass_with_downgrade"
    if any(str(entry.get("human_decision") or "") == "rejected" for entry in decision_log_entries):
        verdict = "blocked"
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "revision_id": revision_id,
        "completeness_verdict": verdict,
        "unresolved_gap_count": len(unresolved),
        "high_risk_unresolved_categories": [],
        "downgrade_fallback_status": fallback_reason or "none",
        "role_state_risk_coverage": {
            "actors": "covered",
            "capability_differences": "covered",
            "state_machine": "covered",
            "boundary_conditions": "covered",
            "exceptions": "covered",
            "recovery_paths": "covered",
            "risks": "covered",
            "coverage_families": [item.get("family") for item in coverage_candidates],
        },
        "readiness": {
            "freeze_ready": verdict in {"pass", "pass_with_downgrade"},
            "prototype_ready": verdict in {"pass", "pass_with_downgrade"},
            "implement_ready": verdict in {"pass", "pass_with_downgrade"},
            "release_ready": verdict == "pass",
        },
        "generated_at": now_iso(),
    }


def _default_freeze_contract(
    *,
    feature: str,
    version: str,
    revision_id: str,
    compiler: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "version": version,
        "feature": feature,
        "revision_id": revision_id,
        "status": "freeze-ready",
        "human_supplement_contract": {
            "allowed_decisions": ["accepted", "rejected", "deferred"],
            "required_fields": [
                "gap_id",
                "source_truth_ref",
                "candidate_kind",
                "rationale",
                "human_decision",
                "decision_reason",
                "writeback_target",
                "revision_id",
            ],
            "writeback_flow": [
                "decision_log",
                "writeback_projection",
                "truth_refreeze",
            ],
        },
        "blocking_rules": [
            "high_severity_unresolved_gap",
            "critical_coverage_family_missing",
            "host_downgrade_without_explicit_fallback_contract",
            "truth_writeback_without_machine_decision_trail",
        ],
        "freeze_verdict": "pass_with_downgrade" if str(compiler.get("fallback_reason") or "") else "pass",
        "implementation_verdict": "pending",
        "qa_execution_verdict": "pending",
        "updated_at": now_iso(),
    }


def _candidate_families(candidates: list[dict[str, Any]], *, limit: int = 6) -> list[str]:
    families: list[str] = []
    for item in candidates:
        family = str((item or {}).get("family") or "").strip()
        if family and family not in families:
            families.append(family)
        if len(families) >= limit:
            break
    return families


def _build_human_loop_handoff(
    *,
    feature: str,
    version: str,
    target_artifact: str,
    completeness: dict[str, Any],
    story_candidates: list[dict[str, Any]],
    coverage_candidates: list[dict[str, Any]],
    compiler: dict[str, Any],
) -> dict[str, Any]:
    missing_dimensions = [str(item).strip() for item in (completeness.get("missing_dimensions") or []) if str(item).strip()]
    high_risk = [str(item).strip() for item in (completeness.get("high_risk_unresolved_categories") or []) if str(item).strip()]
    unresolved_gap_count = int(completeness.get("unresolved_gap_count") or 0)
    downgrade = str(completeness.get("downgrade_fallback_status") or "none").strip()
    focus_areas: list[str] = []
    if target_artifact == "user-story":
        if any(item in missing_dimensions for item in ("actors", "capability_differences", "state_machine", "boundary_conditions", "exceptions", "recovery_paths", "risks", "open_questions")):
            focus_areas.append("补齐 user-story 里的角色 / 状态机 / 边界 / 异常 / 恢复 / 风险")
        if high_risk:
            focus_areas.append("处理 user-story 中未解决的高风险 gap")
        if unresolved_gap_count > 0:
            focus_areas.append("把 deferred / rejected 决策回填为可追踪故事")
        candidate_family_names = _candidate_families(story_candidates)
        writeback_target = f"docs/beacon/{version}/user-story/{feature_slug(feature)}.md"
        recommended_command = f'beacon user-story create "{feature}" --project <project-root> --version {version} --json'
        recommended_route = "beacon-user-story"
        candidate_kind = "story"
    elif target_artifact == "test-case":
        if any(item in missing_dimensions for item in ("happy_paths", "negative_paths", "boundary_conditions", "exceptions", "recovery_paths", "risks", "open_questions")):
            focus_areas.append("补齐 test-case 里的 happy / negative / boundary / exception / recovery 覆盖")
        if high_risk:
            focus_areas.append("处理 test-case 中未解决的高风险 gap")
        if unresolved_gap_count > 0:
            focus_areas.append("把 deferred / rejected 决策回填为可执行测试")
        candidate_family_names = _candidate_families(coverage_candidates)
        writeback_target = f"docs/beacon/{version}/qa/test-cases/{feature_slug(feature)}.md"
        recommended_command = f'beacon test-case create "{feature}" --project <project-root> --version {version} --json'
        recommended_route = "beacon-test-case"
        candidate_kind = "coverage"
    else:
        candidate_family_names = []
        writeback_target = ""
        recommended_command = ""
        recommended_route = "beacon-change" if str(completeness.get("completeness_verdict") or "") == "blocked" else "beacon-brainstorm"
        candidate_kind = ""

    if not focus_areas and downgrade not in {"", "none"}:
        focus_areas.append("显式确认 host downgrade 的 fallback contract")
    if not focus_areas:
        focus_areas.append("复核 requirement completeness 的补料方向")
    open_questions = [
        f"{item} 是否需要补成 machine-readable supplement candidate？"
        for item in candidate_family_names[:4]
    ]
    if not open_questions:
        open_questions = [
            "哪些 gap 需要接受 / 拒绝 / 延后决策？",
            "是否需要重新冻结并再验收？",
        ]
    return {
        "feature": feature,
        "version": version,
        "target_artifact": target_artifact,
        "candidate_kind": candidate_kind,
        "candidate_families": candidate_family_names,
        "candidate_payload": {
            "focus_areas": focus_areas,
            "open_questions": open_questions,
            "missing_dimensions": missing_dimensions,
            "high_risk_unresolved_categories": high_risk,
        },
        "source_truth_ref": f"docs/beacon/{version}/prd/{feature_slug(feature)}.md" if feature else "",
        "writeback_target": writeback_target,
        "rationale": str(completeness.get("completeness_verdict") or compiler.get("fallback_reason") or "requirement supplement required"),
        "confidence": "medium",
        "human_decision": "pending",
        "audit_trail_required": True,
        "recommended_route": recommended_route,
        "recommended_command": recommended_command,
        "recommended_mode": "requirement-convergence",
    }


def _build_re_freeze_transaction(
    *,
    feature: str,
    version: str,
    revision_id: str,
    supplement_task: dict[str, Any],
    candidate_ledger: dict[str, Any],
    decision_log: dict[str, Any],
    completeness: dict[str, Any],
    paths: dict[str, Path],
) -> dict[str, Any]:
    entries = [item for item in (candidate_ledger.get("entries") or []) if isinstance(item, dict)]
    accepted = [item for item in entries if str(item.get("human_decision") or "") == "accepted"]
    rejected = [item for item in entries if str(item.get("human_decision") or "") == "rejected"]
    deferred = [item for item in entries if str(item.get("human_decision") or "") == "deferred"]
    refreeze_required = bool(supplement_task.get("target_artifact")) or bool(deferred) or bool(rejected)
    revalidate_required = refreeze_required or str(completeness.get("completeness_verdict") or "") != "pass"
    machine_mirror_paths = {key: str(path) for key, path in paths.items()}
    return {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "revision_id": revision_id,
        "accepted_candidates": [str(item.get("gap_id") or "") for item in accepted if str(item.get("gap_id") or "").strip()],
        "rejected_candidates": [str(item.get("gap_id") or "") for item in rejected if str(item.get("gap_id") or "").strip()],
        "deferred_candidates": [str(item.get("gap_id") or "") for item in deferred if str(item.get("gap_id") or "").strip()],
        "writeback_targets": sorted(
            {
                str(item.get("writeback_target") or "")
                for item in entries
                if str(item.get("writeback_target") or "").strip()
            }
        ),
        "machine_mirror_paths": machine_mirror_paths,
        "refreeze_required": refreeze_required,
        "revalidate_required": revalidate_required,
        "decision_count": len(decision_log.get("entries") or []),
        "generated_at": now_iso(),
    }


def load_requirement_completeness(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    path = requirement_paths(project_root, version, feature)["completeness"]
    return read_json(path, {}) if path.exists() else {}


def build_requirement_completeness_gate(
    project_root: Path,
    *,
    version: str,
    feature: str,
    target_stage: str,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    if not requirement_deepening_supported(resolved_version):
        return {
            "schema_version": "1.0",
            "enabled": False,
            "status": "pass",
            "blocked": False,
            "reason_code": "",
            "target_stage": target_stage,
            "feature": feature,
            "version": resolved_version,
            "recommended_command": "",
        }

    def _status_payload(
        *,
        status: str,
        reason_code: str = "",
        summary: str = "",
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "blocked": status == "blocked",
            "reason_code": reason_code,
            "summary": summary,
            "details": details or {},
        }

    paths = requirement_paths(project_root, resolved_version, feature)
    completeness = read_json(paths["completeness"], {})
    freeze_contract = read_json(paths["freeze_contract"], {})
    decision_log = read_json(paths["decision_log"], {})
    candidate_ledger = read_json(paths["candidate_ledger"], {})
    if not completeness:
        missing_paths = {key: str(path.relative_to(project_root)) for key, path in paths.items() if key != "dir"}
        stage_gates = {
            "artifact_read_model": _status_payload(
                status="blocked",
                reason_code="requirement_completeness_missing",
                summary="requirement completeness artifact missing",
                details={"paths": missing_paths},
            ),
            "decision_traceability": _status_payload(
                status="blocked",
                reason_code="requirement_decision_log_missing",
                summary="human supplement decision trail unavailable",
            ),
            "coverage_closure": _status_payload(
                status="blocked",
                reason_code="requirement_coverage_closure_unknown",
                summary="role/state/risk coverage cannot be evaluated",
            ),
            "downgrade_control": _status_payload(
                status="blocked",
                reason_code="requirement_downgrade_state_unknown",
                summary="host fallback state unavailable",
            ),
            "stage_admission": _status_payload(
                status="blocked",
                reason_code="requirement_completeness_missing",
                summary=f"{target_stage} admission blocked until completeness artifact is generated",
            ),
        }
        recommended_command = f'beacon test-case create "{feature}" --project {project_root} --version {resolved_version}'
        return {
            "schema_version": "1.0",
            "enabled": True,
            "status": "blocked",
            "blocked": True,
            "reason_code": "requirement_completeness_missing",
            "target_stage": target_stage,
            "feature": feature,
            "version": resolved_version,
            "paths": missing_paths,
            "recommended_command": recommended_command,
            "next_action": "human_review",
            "stage_gates": stage_gates,
            "human_loop_handoff": {
                "action": "human_review",
                "reason": "requirement_completeness_missing",
                "recommended_command": recommended_command,
                "focus_areas": [
                    "generate machine-readable completeness artifact",
                    "rebuild user-story and test-case supplement trace",
                ],
            },
            "completeness": {},
            "freeze_contract": freeze_contract,
        }

    verdict = str(
        completeness.get("completeness_verdict")
        or freeze_contract.get("freeze_verdict")
        or "pass"
    ).strip().lower()
    readiness = completeness.get("readiness") if isinstance(completeness.get("readiness"), dict) else {}
    stage_key = {
        "prototype": "prototype_ready",
        "qa": "implement_ready",
        "release": "release_ready",
    }.get(str(target_stage or "").strip().lower(), "freeze_ready")
    stage_ready = bool(readiness.get(stage_key, verdict in {"pass", "pass_with_downgrade"}))
    unresolved_gap_count = int(completeness.get("unresolved_gap_count") or 0)
    high_risk = [str(item).strip() for item in (completeness.get("high_risk_unresolved_categories") or []) if str(item).strip()]
    downgrade = str(completeness.get("downgrade_fallback_status") or "none").strip()
    coverage_payload = completeness.get("role_state_risk_coverage") if isinstance(completeness.get("role_state_risk_coverage"), dict) else {}
    coverage_families = coverage_payload.get("coverage_families") if isinstance(coverage_payload, dict) else []
    coverage_families = [str(item).strip() for item in (coverage_families or []) if str(item).strip()]
    coverage_dimension_statuses = {
        name: str(coverage_payload.get(name) or "").strip().lower()
        for name in _DIMENSION_ORDER
    }
    missing_dimensions = [
        name
        for name, dimension_status in coverage_dimension_statuses.items()
        if dimension_status not in {"covered", "pass", "complete", "completed"}
    ]
    decision_count = len(decision_log.get("entries") or []) if isinstance(decision_log, dict) else 0
    candidate_count = len(candidate_ledger.get("entries") or []) if isinstance(candidate_ledger, dict) else 0

    decision_traceability_status = "pass"
    decision_traceability_reason = ""
    if candidate_count > 0 and decision_count == 0:
        decision_traceability_status = "blocked"
        decision_traceability_reason = "requirement_decision_trace_missing"
    elif candidate_count > 0 and decision_count < candidate_count:
        decision_traceability_status = "pass_with_downgrade"
        decision_traceability_reason = "requirement_decision_trace_partial"

    coverage_closure_status = "pass"
    coverage_closure_reason = ""
    if any(item in {"critical-coverage-family-missing", "critical-role-state-gap"} for item in high_risk) or missing_dimensions:
        coverage_closure_status = "blocked"
        coverage_closure_reason = "requirement_coverage_closure_blocked"
    elif unresolved_gap_count > 0 or len(coverage_families) < 5:
        coverage_closure_status = "pass_with_downgrade"
        coverage_closure_reason = "requirement_coverage_closure_downgraded"

    downgrade_control_status = "pass" if downgrade in {"", "none"} else "pass_with_downgrade"
    downgrade_control_reason = "" if downgrade_control_status == "pass" else "requirement_host_downgrade_active"

    unresolved_gap_status = "pass"
    unresolved_gap_reason = ""
    if high_risk or verdict == "blocked":
        unresolved_gap_status = "blocked"
        unresolved_gap_reason = "requirement_unresolved_high_risk"
    elif unresolved_gap_count > 0:
        unresolved_gap_status = "pass_with_downgrade"
        unresolved_gap_reason = "requirement_unresolved_gap_pending"

    stage_admission_status = "blocked" if (verdict == "blocked" or not stage_ready) else ("pass_with_downgrade" if verdict == "pass_with_downgrade" else "pass")
    stage_admission_reason = ""
    if verdict == "blocked":
        stage_admission_reason = "requirement_completeness_blocked"
    elif not stage_ready:
        stage_admission_reason = f"requirement_{stage_key}_blocked"
    elif verdict == "pass_with_downgrade":
        stage_admission_reason = "requirement_completeness_downgraded"

    stage_gates = {
        "artifact_read_model": _status_payload(
            status="pass",
            summary="requirement completeness artifacts are readable",
            details={"paths": {key: str(path.relative_to(project_root)) for key, path in paths.items() if key != "dir"}},
        ),
        "decision_traceability": _status_payload(
            status=decision_traceability_status,
            reason_code=decision_traceability_reason,
            summary="human supplement decisions remain auditable",
            details={"decision_count": decision_count, "candidate_count": candidate_count},
        ),
        "coverage_closure": _status_payload(
            status=coverage_closure_status,
            reason_code=coverage_closure_reason,
            summary="role/state/risk coverage closure is evaluated from machine materials",
            details={
                "coverage_family_count": len(coverage_families),
                "coverage_families": coverage_families,
                "missing_dimensions": missing_dimensions,
            },
        ),
        "unresolved_gap_governance": _status_payload(
            status=unresolved_gap_status,
            reason_code=unresolved_gap_reason,
            summary="unresolved gaps are classified before downstream delivery",
            details={
                "unresolved_gap_count": unresolved_gap_count,
                "high_risk_unresolved_categories": high_risk,
            },
        ),
        "downgrade_control": _status_payload(
            status=downgrade_control_status,
            reason_code=downgrade_control_reason,
            summary="host fallback and downgrade state remain explicit",
            details={"downgrade_fallback_status": downgrade},
        ),
        "stage_admission": _status_payload(
            status=stage_admission_status,
            reason_code=stage_admission_reason,
            summary=f"{target_stage} admission evaluated against completeness readiness",
            details={"target_stage": target_stage, "stage_ready": stage_ready, "stage_key": stage_key},
        ),
    }

    blocked = verdict == "blocked" or not stage_ready
    status = "blocked" if blocked else ("pass_with_downgrade" if verdict == "pass_with_downgrade" else "pass")
    reason_code = ""
    if verdict == "blocked":
        reason_code = "requirement_completeness_blocked"
    elif not stage_ready:
        reason_code = f"requirement_{stage_key}_blocked"
    elif verdict == "pass_with_downgrade":
        reason_code = "requirement_completeness_downgraded"

    recommended_command = ""
    if blocked:
        recommended_command = "beacon-change"
    elif status == "pass_with_downgrade":
        recommended_command = f'beacon {target_stage} {"status" if target_stage == "prototype" else "run"} "{feature}"'

    focus_areas: list[str] = []
    if missing_dimensions:
        focus_areas.append("补齐 role/state/risk coverage missing dimensions")
    if high_risk:
        focus_areas.append("处理 high-risk unresolved categories")
    if unresolved_gap_count > 0:
        focus_areas.append("补齐 deferred/rejected requirement decisions")
    if downgrade not in {"", "none"}:
        focus_areas.append("显式确认 host downgrade 的 fallback contract")
    if not focus_areas and status == "pass_with_downgrade":
        focus_areas.append("复核 requirement completeness downgrade 的影响范围")

    return {
        "schema_version": "1.0",
        "enabled": True,
        "status": status,
        "blocked": blocked,
        "reason_code": reason_code,
        "target_stage": target_stage,
        "feature": feature,
        "version": resolved_version,
        "stage_ready": stage_ready,
        "paths": {key: str(path.relative_to(project_root)) for key, path in paths.items() if key != "dir"},
        "unresolved_gap_count": unresolved_gap_count,
        "high_risk_unresolved_categories": high_risk,
        "downgrade_fallback_status": downgrade,
        "coverage_families": coverage_families,
        "decision_count": decision_count,
        "candidate_count": candidate_count,
        "coverage_dimension_statuses": coverage_dimension_statuses,
        "missing_dimensions": missing_dimensions,
        "stage_gates": stage_gates,
        "recommended_command": recommended_command,
        "next_action": "human_review" if blocked else ("human_review" if status == "pass_with_downgrade" else target_stage),
        "human_loop_handoff": {
            "action": "human_review" if blocked or status == "pass_with_downgrade" else target_stage,
            "reason": reason_code or "requirement_completeness_pass",
            "recommended_command": recommended_command,
            "focus_areas": focus_areas,
        },
        "completeness": completeness,
        "freeze_contract": freeze_contract,
    }


def sync_requirement_deepening_artifacts(
    project_root: Path,
    *,
    version: str,
    feature: str,
    prd_content: str,
    user_story_content: str,
    qa_content: str,
    prd_source: str,
    user_story_source: str,
    qa_source: str,
    compiler: dict[str, Any],
    revision_id: str = "R1",
    target_artifact: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    if not requirement_deepening_supported(resolved_version):
        return {}

    paths = requirement_paths(project_root, resolved_version, feature)
    envelope = build_requirement_envelope(
        feature=feature,
        version=resolved_version,
        prd_content=prd_content,
        user_story_content=user_story_content,
        qa_content=qa_content,
        prd_source=prd_source,
        user_story_source=user_story_source,
        qa_source=qa_source,
    )
    existing_ac_items = []
    try:
        from beacon.utils.requirement_parsing import build_feature_ac_items

        existing_ac_items = build_feature_ac_items(
            user_story_content=user_story_content,
            prd_content=prd_content,
            qa_content=qa_content,
            user_story_source=user_story_source,
            prd_source=prd_source,
            qa_source=qa_source,
        )
    except Exception:  # noqa: BLE001
        existing_ac_items = []
    story_candidates = build_story_candidates(envelope, existing_ac_items=existing_ac_items)
    coverage_candidates = build_coverage_candidates(envelope)
    ledger = build_candidate_ledger(
        feature=feature,
        version=resolved_version,
        revision_id=revision_id,
        story_candidates=story_candidates,
        coverage_candidates=coverage_candidates,
        compiler=compiler,
    )
    decision_log = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "revision_id": revision_id,
        "generated_at": now_iso(),
        "entries": [
            {
                "gap_id": item["gap_id"],
                "source_truth_ref": item["source_truth_ref"],
                "candidate_kind": item["candidate_kind"],
                "human_decision": item["human_decision"],
                "decision_reason": item["decision_reason"],
                "writeback_target": item["writeback_target"],
            }
            for item in ledger.get("entries", [])
            if isinstance(item, dict)
        ],
    }
    completeness = build_completeness_payload(
        feature=feature,
        version=resolved_version,
        revision_id=revision_id,
        compiler=compiler,
        coverage_candidates=coverage_candidates,
        decision_log_entries=decision_log["entries"],
    )
    freeze_contract = read_json(paths["freeze_contract"], {})
    if not freeze_contract:
        freeze_contract = _default_freeze_contract(
            feature=feature,
            version=resolved_version,
            revision_id=revision_id,
            compiler=compiler,
        )
    else:
        freeze_contract["updated_at"] = now_iso()
        freeze_contract["revision_id"] = revision_id

    supplement_task = _build_human_loop_handoff(
        feature=feature,
        version=resolved_version,
        target_artifact=target_artifact,
        completeness=completeness,
        story_candidates=story_candidates,
        coverage_candidates=coverage_candidates,
        compiler=compiler,
    )
    human_loop_handoff = {
        "action": "human_review" if supplement_task.get("target_artifact") else "freeze",
        "reason": str(supplement_task.get("rationale") or freeze_contract.get("freeze_verdict") or "requirement supplement required"),
        "recommended_command": str(supplement_task.get("recommended_command") or ""),
        "focus_areas": list((supplement_task.get("candidate_payload") or {}).get("focus_areas") or []),
    }
    re_freeze_transaction = _build_re_freeze_transaction(
        feature=feature,
        version=resolved_version,
        revision_id=revision_id,
        supplement_task=supplement_task,
        candidate_ledger=ledger,
        decision_log=decision_log,
        completeness=completeness,
        paths=paths,
    )

    write_json(paths["envelope"], envelope)
    write_json(paths["candidate_ledger"], ledger)
    write_json(paths["decision_log"], decision_log)
    write_json(paths["freeze_contract"], freeze_contract)
    write_json(paths["completeness"], completeness)
    write_json(paths["supplement_task"], supplement_task)
    write_json(paths["re_freeze_transaction"], re_freeze_transaction)
    return {
        "paths": {key: str(path.relative_to(project_root)) for key, path in paths.items() if key != "dir"},
        "envelope": envelope,
        "story_candidates": story_candidates,
        "coverage_candidates": coverage_candidates,
        "candidate_ledger": ledger,
        "decision_log": decision_log,
        "completeness": completeness,
        "freeze_contract": freeze_contract,
        "supplement_task": supplement_task,
        "human_loop_handoff": human_loop_handoff,
        "re_freeze_transaction": re_freeze_transaction,
    }
