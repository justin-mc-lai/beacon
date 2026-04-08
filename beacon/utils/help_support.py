"""Stage-aware help/navigator support helpers for Beacon."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.control_plane import build_resume_contract
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.governance import evaluate_takeover_baseline_gate, load_project_mode
from beacon.utils.implementation_plan import (
    build_implementation_plan_gate_payload,
    implementation_plan_supported,
    load_implementation_plan,
    load_implementation_plan_progress,
)
from beacon.utils.learning_loop import load_learning_plane_contract
from beacon.utils.project_skills import (
    default_project_profile,
    evaluate_project_profile_gate,
    load_feature_profile_binding,
    resolve_profile_for_feature,
)
from beacon.utils.qa_precision import load_feature_qa_scorecard
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime import load_run_state
from beacon.utils.skill_discovery import build_discovery_hint, load_skill_discovery
from beacon.utils.scoring import (
    compute_closure_score,
    compute_quality_score,
    compute_readiness_score,
    compute_test_score,
)
from beacon.utils.story_state import feature_slug, load_story_state, summarize_story_items
from beacon.utils.versioning import describe_project_version_context, normalize_version, resolve_docs_version
from beacon.utils.workflow_memory import compute_workflow_progress, resolve_workflow_run_id


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _auto_test_status(project_root: Path) -> dict[str, Any]:
    return _read_json(project_root / ".beacon" / "auto-test-status.json")


def _infer_current_stage(*, revision_state: dict[str, Any], workflow_progress: dict[str, Any]) -> str:
    stages = workflow_progress.get("stages") if isinstance(workflow_progress.get("stages"), dict) else {}
    next_stage = str(workflow_progress.get("next_stage", "") or "")
    if next_stage:
        return next_stage
    delivery = str(revision_state.get("delivery_status", "") or "")
    if delivery in {"accepted", "released"}:
        return "accepted"
    if str(stages.get("verify", {}).get("status", "") or "") == "failed":
        return "verify"
    return delivery or str(revision_state.get("doc_status", "") or "draft")


def _unique_reasons_in_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


def _profile_binding_source(project_root: Path, *, version: str, feature: str) -> str:
    binding = load_feature_profile_binding(project_root, version=version, feature=feature)
    if binding:
        return "feature_binding"
    if default_project_profile(project_root):
        return "default_profile"
    return "none"


def _supports_skill_discover(version: str) -> bool:
    normalized = normalize_version(version) or ""
    if not normalized.startswith("v"):
        return False
    try:
        major, minor, patch = [int(part) for part in normalized[1:].split(".")]
    except Exception:  # noqa: BLE001
        return False
    return (major, minor, patch) >= (1, 2, 0)


def _stage_local_execution_binding(
    *,
    profile: dict[str, Any] | None,
    revision_state: dict[str, Any],
    workflow_progress: dict[str, Any],
) -> dict[str, str]:
    if not profile:
        return {"stage": "", "skill_id": "", "status": "not_configured"}
    skills = profile.get("skills") if isinstance(profile.get("skills"), dict) else {}
    delivery_status = str(revision_state.get("delivery_status", "") or "")
    doc_status = str(revision_state.get("doc_status", "") or "")
    next_stage = str(workflow_progress.get("next_stage", "") or "")
    stage_candidates: list[str] = []
    if delivery_status in {"implemented", "verifying", "verified"} or next_stage == "verify":
        stage_candidates.append("verify")
    if delivery_status in {"accepted"}:
        stage_candidates.append("review")
    if doc_status == "frozen" and delivery_status in {"", "idle", "draft"}:
        stage_candidates.append("implementation")
    if next_stage:
        stage_candidates.append(next_stage)
    for stage in stage_candidates:
        skill_id = str(skills.get(stage, "") or "").strip()
        if skill_id:
            return {"stage": stage, "skill_id": skill_id, "status": "bound"}
    return {
        "stage": stage_candidates[0] if stage_candidates else "",
        "skill_id": "",
        "status": "not_bound",
    }


def _blocking_reasons(
    *,
    revision_state: dict[str, Any],
    workflow_progress: dict[str, Any],
    coverage: dict[str, Any],
    version_guard: dict[str, Any] | None = None,
    profile_gate: dict[str, Any] | None = None,
    control_plane: dict[str, Any] | None = None,
    feature_scorecard: dict[str, Any] | None = None,
    takeover_gate: dict[str, Any] | None = None,
    implementation_plan_gate: dict[str, Any] | None = None,
) -> list[str]:
    reasons: list[str] = []
    if isinstance(version_guard, dict) and str(version_guard.get("status", "") or "") == "blocked":
        code = str(version_guard.get("reason_code", "") or "").strip()
        if code:
            reasons.append(code)
    if isinstance(takeover_gate, dict) and str(takeover_gate.get("status", "") or "") == "blocked":
        reasons.append("takeover_baseline_required")
        reasons.extend(
            str(item.get("reason_code", "") or "").strip()
            for item in (takeover_gate.get("issues") or [])
            if isinstance(item, dict)
        )
    delivery_status = str(revision_state.get("delivery_status", "") or "")
    if str(revision_state.get("doc_status", "") or "draft") != "frozen":
        reasons.append("revision_not_frozen")
    verify_status = str(workflow_progress.get("stages", {}).get("verify", {}).get("status", "") or "")
    if verify_status == "failed":
        reasons.append("verify_failed")
    if str(revision_state.get("superseded_by", "") or ""):
        reasons.append("revision_superseded")
    if (coverage.get("planned_story", 0) or 0) <= 0:
        reasons.append("missing_user_story")
    if delivery_status == "blocked":
        reasons.append("workflow_blocked")
    gate_issues = profile_gate.get("issues", []) if isinstance(profile_gate, dict) and isinstance(profile_gate.get("issues"), list) else []
    for item in gate_issues:
        if not isinstance(item, dict):
            continue
        code = str(item.get("reason_code", "") or "").strip()
        if code:
            reasons.append(code)
    feature_scorecard = feature_scorecard if isinstance(feature_scorecard, dict) else {}
    if str(feature_scorecard.get("continue_decision") or "").strip() == "stop_for_repair":
        reasons.append("qa_stop_for_repair")
        reasons.extend(
            str(item).strip()
            for item in (feature_scorecard.get("stop_reasons") or [])
            if str(item).strip()
        )
    if isinstance(control_plane, dict) and int(control_plane.get("failure_streak", 0) or 0) > 0:
        reasons.append("control_plane_escalation_active")
    if isinstance(implementation_plan_gate, dict) and bool(implementation_plan_gate.get("blocked")):
        code = str(implementation_plan_gate.get("reason_code", "") or "").strip()
        if code:
            reasons.append(code)
    return _unique_reasons_in_order(reasons)


def _next_step(
    *,
    revision_state: dict[str, Any],
    workflow_progress: dict[str, Any],
    blocked: bool,
    blocking_reasons: list[str],
    feature: str,
    version: str,
    project_root: Path,
    profile_gate: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    control_plane: dict[str, Any] | None = None,
    feature_scorecard: dict[str, Any] | None = None,
    project_mode: str = "greenfield",
    stage_binding: dict[str, str] | None = None,
    implementation_plan_gate: dict[str, Any] | None = None,
    version_guard: dict[str, Any] | None = None,
    discovery_hint: dict[str, Any] | None = None,
) -> dict[str, str]:
    quoted_feature = json.dumps(feature, ensure_ascii=False)
    base = f'--project-root {project_root} --version {version}'
    next_stage = str(workflow_progress.get("next_stage", "") or "")
    run_id = str(workflow_progress.get("run_id", "") or "")
    feature_scorecard = feature_scorecard if isinstance(feature_scorecard, dict) else {}
    stage_binding = stage_binding if isinstance(stage_binding, dict) else {}
    delivery_status = str(revision_state.get("delivery_status", "") or "")

    if project_mode == "takeover" and "takeover_baseline_required" in blocking_reasons:
        return {
            "action": "takeover-baseline",
            "reason": "takeover projects must freeze current-state architecture, service-map, and boundaries before implementation",
            "command": f"beacon doctor advise --project-root {project_root} --version {version} --feature {quoted_feature}",
        }

    if delivery_status in {"accepted", "released"} and (
        bool(feature_scorecard.get("release_ready", False)) or bool(workflow_progress.get("gate_pass", False))
    ):
        return {
            "action": "release-check",
            "reason": "accepted revision is already release-ready under current workflow evidence",
            "command": f"beacon gate check release --project-root {project_root} --version {version}",
        }

    continue_decision = str(feature_scorecard.get("continue_decision") or "").strip()
    if continue_decision == "stop_for_repair":
        stop_reasons = [str(item).strip() for item in (feature_scorecard.get("stop_reasons") or []) if str(item).strip()]
        if any(reason in {"implementation_reopened", "bug_filed"} for reason in stop_reasons):
            return {
                "action": "implement",
                "reason": "qa round found an implementation blocker that must be fixed before the next round",
                "command": f"beacon implement run {quoted_feature} --project {project_root} --version {version} --runner native-single",
            }
        if bool(feature_scorecard.get("test_case_backfill_required")):
            return {
                "action": "test-case-create",
                "reason": "qa round found missing coverage or scenario families that must be backfilled before rerun",
                "command": f"beacon test-case create {quoted_feature} {base}",
            }
        if any(
            reason in {
                "project_profile_gate_blocked",
                "required_evidence_missing",
                "required_case_missing",
                "contract_drift",
            }
            for reason in stop_reasons
        ):
            profile_id = str((profile or {}).get("profile_id", "") or (profile_gate or {}).get("profile_id", "") or "")
            profile_arg = f" --profile {profile_id}" if profile_id else ""
            return {
                "action": "verify-run",
                "reason": "project workflow or evidence gate is still blocking the QA round",
                "command": f"beacon verify run {quoted_feature} {base}{profile_arg}",
            }
        return {
            "action": "qa-resume",
            "reason": "qa stopped for repair; close the blocker and then resume through Beacon help",
            "command": str(feature_scorecard.get("resume_command") or f"beacon help {base} --feature {quoted_feature}"),
        }
    if continue_decision == "continue":
        if bool(feature_scorecard.get("test_case_backfill_required")):
            return {
                "action": "test-case-create",
                "reason": "the next QA round needs additional test cases before rerun",
                "command": f"beacon test-case create {quoted_feature} {base}",
            }
        return {
            "action": "qa-run",
            "reason": "qa coverage is incomplete but no severe blocker requires stopping the round",
            "command": f"beacon qa run {quoted_feature} --project {project_root} --version {version} --json",
        }
    if continue_decision == "ready_for_release":
        return {
            "action": "release-check",
            "reason": "current QA round is ready for release/governance evaluation",
            "command": f"beacon gate check release --project-root {project_root} --version {version}",
        }

    if blocked:
        if "context_version_mismatch" in blocking_reasons:
            recommended_version = str((version_guard or {}).get("recommended_version", "") or "")
            command_version = recommended_version or version
            return {
                "action": "use-context-version",
                "reason": "the requested version conflicts with the current managed context and would write to the wrong docs line",
                "command": f"beacon help --project-root {project_root} --version {command_version} --feature {quoted_feature}",
            }
        if any(
            reason in {
                "implementation_plan_missing",
                "implementation_plan_invalid",
                "implementation_plan_feature_version_mismatch",
                "implementation_plan_revision_mismatch",
                "implementation_plan_baseline_mismatch",
                "implementation_plan_source_refs_incomplete",
            }
            for reason in blocking_reasons
        ):
            if _supports_skill_discover(version) and not profile and bool((discovery_hint or {}).get("recommended", False)):
                return {
                    "action": "skill-discover",
                    "reason": str((discovery_hint or {}).get("reason") or "project skill onboarding is not configured; discover a bounded project profile before implementation planning"),
                    "command": str((discovery_hint or {}).get("command") or f"beacon skill discover --project-root {project_root} --json"),
                }
            return {
                "action": "implement-plan",
                "reason": "implementation requires a compiled plan aligned to the active frozen revision",
                "command": str((implementation_plan_gate or {}).get("recommended_command") or f'beacon implement plan {quoted_feature} --project-root {project_root} --version {version}'),
            }
        if "control_plane_escalation_active" in blocking_reasons and isinstance(control_plane, dict):
            run_id = str(control_plane.get("run_id", "") or "")
            run_arg = f" {run_id}" if run_id else ""
            return {
                "action": "debug-recover",
                "reason": "control plane recorded an active failure streak that requires structured recovery before retry",
                "command": f"beacon debug recover{run_arg} --project-root {project_root}",
            }
        if "contract_drift" in blocking_reasons:
            return {
                "action": "contract-drift-fix",
                "reason": "project-specific contract drift detected between docs, implementation, or downstream service",
                "command": f"beacon doctor advise --project-root {project_root} --version {version} --feature {quoted_feature}",
            }
        if "required_case_missing" in blocking_reasons or "required_evidence_missing" in blocking_reasons:
            profile_id = str((profile or {}).get("profile_id", "") or (profile_gate or {}).get("profile_id", "") or "")
            profile_arg = f" --profile {profile_id}" if profile_id else ""
            return {
                "action": "verify-run",
                "reason": "project profile requires missing verification evidence before accept",
                "command": f"beacon verify run {quoted_feature} {base}{profile_arg}",
            }
        if "revision_superseded" in blocking_reasons or "change_request_pending" in blocking_reasons:
            return {
                "action": "reopen",
                "reason": "current revision is no longer the active baseline",
                "command": f"beacon reopen {quoted_feature} {base} --reason change-request",
            }
        if "revision_not_frozen" in blocking_reasons:
            return {
                "action": "freeze",
                "reason": "implementation requires a frozen revision baseline",
                "command": f"beacon freeze {quoted_feature} {base}",
            }
        if "verify_failed" in blocking_reasons:
            return {
                "action": "review-quality",
                "reason": "verification is failing and quality review / fixes are required",
                "command": f"beacon review quality {quoted_feature} {base}",
            }
        return {
            "action": "doctor-advise",
            "reason": "workflow is blocked and needs diagnostics before continuing",
            "command": f"beacon doctor --json --project-root {project_root}",
        }

    doc_status = str(revision_state.get("doc_status", "") or "")
    if doc_status in {"draft", "refined"}:
        return {
            "action": "freeze",
            "reason": "requirements appear ready to become an implementation baseline",
            "command": f"beacon freeze {quoted_feature} {base}",
        }

    if _supports_skill_discover(version) and not profile and delivery_status in {"", "idle", "draft"} and bool((discovery_hint or {}).get("recommended", False)):
        return {
            "action": "skill-discover",
            "reason": str((discovery_hint or {}).get("reason") or "project skill onboarding can be configured before implementation proceeds"),
            "command": str((discovery_hint or {}).get("command") or f"beacon skill discover --project-root {project_root} --json"),
        }

    if profile:
        profile_id = str((profile or {}).get("profile_id", "") or "")
        gate_status = str((profile_gate or {}).get("status", "") or "")
        if delivery_status in {"implemented", "verifying", "verified"}:
            if gate_status == "blocked" and str(stage_binding.get("skill_id", "") or "").strip():
                return {
                    "action": "verify-run",
                    "reason": "project profile still has missing evidence or required cases",
                    "command": f"beacon verify run {quoted_feature} {base} --profile {profile_id}",
                }
            if gate_status == "blocked":
                return {
                    "action": "doctor-advise",
                    "reason": "project profile is configured but the verify-stage binding is unresolved or still blocked",
                    "command": f"beacon doctor advise --project-root {project_root} --version {version} --feature {quoted_feature}",
                }
            return {
                "action": "review-quality",
                "reason": "project profile verification evidence is satisfied; move into formal quality review",
                "command": f"beacon review quality {quoted_feature} {base}",
            }
        if doc_status == "frozen" and delivery_status in {"", "idle", "draft"} and str(stage_binding.get("skill_id", "") or "").strip():
            return {
                "action": "orchestrate-run",
                "reason": "project profile defines a stage-local implementation surface for this feature",
                "command": f"beacon orchestrate run {quoted_feature} {base} --profile {profile_id} --stage {stage_binding.get('stage') or 'implementation'}",
            }
        if delivery_status in {"accepted"}:
            return {
                "action": "release-check",
                "reason": "accepted revision can move to release readiness evaluation",
                "command": f"beacon gate check release --project-root {project_root} --version {version}",
            }

    if doc_status == "frozen" and delivery_status in {"", "idle", "draft"}:
        if isinstance(implementation_plan_gate, dict) and bool(implementation_plan_gate.get("blocked")):
            return {
                "action": "implement-plan",
                "reason": "implementation requires a compiled plan aligned to the frozen revision baseline",
                "command": str(implementation_plan_gate.get("recommended_command") or f'beacon implement plan {quoted_feature} --project-root {project_root} --version {version}'),
            }
        return {
            "action": "implement",
            "reason": "revision is frozen and ready for native implementation",
            "command": f"beacon implement run {quoted_feature} {base} --runner native-single",
        }

    if delivery_status in {"implemented", "verifying", "verified"} or next_stage == "verify":
        return {
            "action": "review-quality",
            "reason": "implementation exists; next step is verification/review closure",
            "command": f"beacon review quality {quoted_feature} {base}",
        }

    if delivery_status in {"accepted"}:
        return {
            "action": "release-check",
            "reason": "accepted revision can move to release readiness evaluation",
            "command": f"beacon gate check release --project-root {project_root} --version {version}",
        }

    if not run_id:
        return {
            "action": "workflow-start",
            "reason": "no active workflow run found for the requested feature/version",
            "command": f"beacon workflow start {quoted_feature} --project {project_root} --version {version}",
        }

    if next_stage in {"think", "user-story", "prd", "prototype", "test-case"}:
        return {
            "action": "workflow-continue",
            "reason": f"next workflow stage is {next_stage}",
            "command": f"beacon workflow continue --project-root {project_root} --version {version} --run-id {run_id}",
        }

    if delivery_status in {"accepted"}:
        return {
            "action": "release-check",
            "reason": "accepted revision can move to release readiness evaluation",
            "command": f"beacon gate check release --project-root {project_root} --version {version}",
        }
    return {
        "action": next_stage or "status",
        "reason": "follow workflow progression to the next stage",
        "command": f"beacon workflow continue --project-root {project_root} --version {version}",
    }


def build_help_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    version_context = describe_project_version_context(project_root, docs_version=version or None)
    resolved_version = str(version_context.get("docs_version", "") or resolve_docs_version(project_root, version))
    version_guard = version_context.get("context_version_guard") if isinstance(version_context.get("context_version_guard"), dict) else {}
    feature_name = feature or ""
    revision_state = load_revision_state(
        project_root,
        version=resolved_version,
        feature=feature_name,
        create_if_missing=False,
    )
    story_state = load_story_state(
        project_root,
        version=resolved_version,
        feature=feature_name,
        create_if_missing=False,
        revision_id=str(revision_state.get("revision_id", "R1") or "R1"),
    )
    resolved_run_id = (
        resolve_workflow_run_id(project_root, run_id=run_id, version=resolved_version, feature=feature_name) or ""
    )
    workflow_progress = compute_workflow_progress(
        project_root,
        run_id=resolved_run_id or None,
        version=resolved_version,
        feature=feature_name,
    )
    coverage = compute_coverage_metrics(project_root, version=resolved_version, feature=feature_name or None)
    auto_test = _auto_test_status(project_root)
    story_summary = summarize_story_items(story_state)
    project_mode = load_project_mode(project_root)
    takeover_gate = evaluate_takeover_baseline_gate(project_root, version=resolved_version)
    profile = resolve_profile_for_feature(
        project_root,
        version=resolved_version,
        feature=feature_name,
        explicit_profile=None,
    )
    profile_gate = (
        evaluate_project_profile_gate(project_root, version=resolved_version, feature=feature_name)
        if profile
        else {}
    )
    feature_scorecard = load_feature_qa_scorecard(project_root, feature=feature_name) if feature_name else {}
    discovery_state = load_skill_discovery(project_root) if _supports_skill_discover(resolved_version) else None
    discovery_hint = build_discovery_hint(project_root) if _supports_skill_discover(resolved_version) and feature_name else {}
    control_plane = build_resume_contract(project_root, run_id=resolved_run_id or None)
    plan_supported = bool(feature_name and implementation_plan_supported(resolved_version))
    implementation_plan_gate = (
        build_implementation_plan_gate_payload(project_root, version=resolved_version, feature=feature_name, run_id=resolved_run_id)
        if plan_supported
        else {}
    )
    implementation_plan = load_implementation_plan(project_root, version=resolved_version, feature=feature_name) if plan_supported else {}
    implementation_plan_progress = load_implementation_plan_progress(project_root, version=resolved_version, feature=feature_name) if plan_supported else {}
    stage_binding = _stage_local_execution_binding(
        profile=profile,
        revision_state=revision_state,
        workflow_progress=workflow_progress,
    )
    blocking = _blocking_reasons(
        revision_state=revision_state,
        workflow_progress=workflow_progress,
        coverage=coverage,
        version_guard=version_guard,
        profile_gate=profile_gate,
        control_plane=control_plane,
        feature_scorecard=feature_scorecard,
        takeover_gate=takeover_gate,
        implementation_plan_gate=implementation_plan_gate,
    )
    blocked = bool(blocking)
    current_stage = _infer_current_stage(revision_state=revision_state, workflow_progress=workflow_progress)
    profile_binding_source = (
        _profile_binding_source(project_root, version=resolved_version, feature=feature_name)
        if feature_name
        else "none"
    )
    learning_surface = load_learning_plane_contract(project_root)
    execution_surface = {
        "project_mode": project_mode,
        "profile_binding_source": profile_binding_source,
        "profile_id": str((profile or {}).get("profile_id", "") or ""),
        "stage_binding": stage_binding,
        "selected_surface": (
            "takeover-baseline-gate"
            if str(takeover_gate.get("status", "") or "") == "blocked"
            else f"project-profile:{stage_binding.get('stage') or current_stage}"
            if profile and str(stage_binding.get("skill_id", "") or "").strip()
            else "native-default"
        ),
        "native_fallback_allowed": not bool(profile and str(stage_binding.get("skill_id", "") or "").strip()),
        "takeover_gate": takeover_gate,
    }
    next_step = _next_step(
        revision_state=revision_state,
        workflow_progress=workflow_progress,
        blocked=blocked,
        blocking_reasons=blocking,
        feature=feature_name,
        version=resolved_version,
        project_root=project_root,
        profile_gate=profile_gate,
        profile=profile,
        control_plane=control_plane,
        feature_scorecard=feature_scorecard,
        project_mode=project_mode,
        stage_binding=stage_binding,
        implementation_plan_gate=implementation_plan_gate,
        version_guard=version_guard,
        discovery_hint=discovery_hint,
    )
    decision_trace = [
        {
            "step": "version_truth",
            "status": "resolved",
            "docs_version": resolved_version,
            "runtime_version": str(version_context.get("runtime_version", "") or ""),
            "current_runtime_release_line": str(version_context.get("current_runtime_release_line", "") or ""),
            "release_truth_status": str(version_context.get("release_truth_status", "") or ""),
            "version_truth_source": str(version_context.get("version_truth_source", "") or ""),
            "context_guard_status": str(version_guard.get("status", "") or ""),
            "context_guard_recommended_version": str(version_guard.get("recommended_version", "") or ""),
        },
        {
            "step": "project_mode",
            "status": project_mode,
            "takeover_gate_status": str(takeover_gate.get("status", "") or ""),
        },
        {
            "step": "feature_profile_binding",
            "status": "resolved" if profile else "not_configured",
            "profile_id": str((profile or {}).get("profile_id", "") or ""),
            "binding_source": profile_binding_source,
        },
        {
            "step": "skill_discovery",
            "status": "resolved" if discovery_state else "not_configured",
            "selected_template": str((discovery_state or {}).get("selected_template", "") or ""),
            "applied": bool((discovery_state or {}).get("applied", False)),
        },
        {
            "step": "skill_discovery_hint",
            "status": "recommended" if bool((discovery_hint or {}).get("recommended", False)) else "not_recommended",
            "templates": list((discovery_hint or {}).get("templates", [])),
        },
        {
            "step": "stage_local_execution_binding",
            "status": str(stage_binding.get("status", "") or "not_configured"),
            "stage": str(stage_binding.get("stage", "") or ""),
            "skill_id": str(stage_binding.get("skill_id", "") or ""),
        },
        {
            "step": "learning_surface",
            "status": "resolved",
            "subject_surface": learning_surface.get("subject_surface", []),
        },
        {
            "step": "implementation_plan",
            "status": str(implementation_plan_gate.get("status", "not_configured") or "not_configured"),
            "plan_id": str(implementation_plan.get("plan_id", "") or ""),
            "next_task_id": str(implementation_plan_progress.get("next_task_id", "") or ""),
            "reason_code": str(implementation_plan_gate.get("reason_code", "") or ""),
        },
    ]
    scores = {
        "test_score": compute_test_score(coverage, auto_test_status=auto_test, story_summary=story_summary),
        "closure_score": compute_closure_score(
            revision_state=revision_state,
            story_state=story_state,
            workflow_progress=workflow_progress,
        ),
        "readiness_score": compute_readiness_score(
            target_stage=str(next_step.get("action", "status")),
            revision_state=revision_state,
            coverage_metrics=coverage,
            workflow_progress=workflow_progress,
            blocked=blocked,
        ),
        "quality_score": compute_quality_score(
            project_root,
            version=resolved_version,
            feature_slug=feature_slug(feature_name),
            workflow_progress=workflow_progress,
        ),
    }
    return {
        "schema_version": "1.0",
        "docs_version": resolved_version,
        "runtime_version": str(version_context.get("runtime_version", "") or ""),
        "version_context": version_context,
        "context_version_guard": version_guard,
        "feature": feature_name,
        "feature_slug": feature_slug(feature_name),
        "version": resolved_version,
        "run_id": resolved_run_id,
        "project_mode": project_mode,
        "revision_id": str(revision_state.get("revision_id", "") or ""),
        "current_stage": current_stage,
        "doc_status": str(revision_state.get("doc_status", "") or "draft"),
        "delivery_status": str(revision_state.get("delivery_status", "") or "idle"),
        "blocked": blocked,
        "blocking_reasons": blocking,
        "blocked_reason": blocking[0] if blocking else "",
        "next_step": next_step,
        "scores": {k: v.get("score") if isinstance(v, dict) else v for k, v in scores.items()},
        "score_details": scores,
        "control_plane": control_plane,
        "coverage": coverage,
        "story_summary": story_summary,
        "workflow_progress": workflow_progress,
        "run_state": load_run_state(project_root, resolved_run_id) if resolved_run_id else None,
        "project_profile": {
            "profile_id": str((profile or {}).get("profile_id", "") or ""),
            "project": str((profile or {}).get("project", "") or ""),
        }
        if profile
        else None,
        "skill_discovery": discovery_state,
        "skill_discovery_hint": discovery_hint,
        "project_gate": profile_gate,
        "execution_surface": execution_surface,
        "learning_surface": learning_surface,
        "implementation_plan": implementation_plan,
        "implementation_plan_gate": implementation_plan_gate,
        "implementation_plan_progress": implementation_plan_progress,
        "decision_trace": decision_trace,
        "takeover_gate": takeover_gate,
        "feature_scorecard": feature_scorecard if isinstance(feature_scorecard, dict) else {},
    }
