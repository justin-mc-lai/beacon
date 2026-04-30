"""Stage-aware help/navigator support helpers for Beacon."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.archive_governance import load_archive_read_model
from beacon.utils.control_plane import build_resume_contract
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.delivery_kernel import build_surface_explanation, load_delivery_read_model
from beacon.utils.governance import evaluate_takeover_baseline_gate, load_project_mode
from beacon.utils.implementation_plan import (
    build_implementation_plan_gate_payload,
    implementation_plan_supported,
    load_implementation_plan,
    load_implementation_plan_progress,
)
from beacon.utils.learning_loop import load_learning_plane_contract
from beacon.utils.material_audit import build_requirement_package_gate
from beacon.utils.minimal_hud import build_minimal_hud
from beacon.utils.host_prompt_trace import load_host_prompt_trace
from beacon.utils.project_skills import (
    default_project_profile,
    evaluate_project_profile_gate,
    load_feature_profile_binding,
    resolve_profile_for_feature,
)
from beacon.utils.project_metadata import metadata_machine_path, resolve_project_metadata_view
from beacon.utils.prototype_support import version_requires_prototype
from beacon.utils.qa_runtime import load_current_qa_session, load_qa_status
from beacon.utils.qa_precision import load_feature_qa_scorecard
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.ralph_runtime import load_ralph_state
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime import load_run_state
from beacon.utils.semantic_runtime import evaluate_semantic_contract
from beacon.utils.skill_discovery import build_discovery_hint, load_skill_discovery
from beacon.utils.scoring import (
    compute_closure_score,
    compute_quality_score,
    compute_readiness_score,
    compute_test_score,
)
from beacon.utils.story_state import feature_slug, load_story_state, summarize_story_items
from beacon.utils.subagent_readiness import delegation_readiness_precheck, detect_host_runtime, runtime_readiness_precheck
from beacon.utils.support_surface_projection import build_support_surface_projection
from beacon.utils.versioning import describe_project_version_context, normalize_version, release_line_key, resolve_docs_version
from beacon.utils.workflow_memory import compute_workflow_progress, resolve_workflow_run_id


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    text = str(release_line_key(version) or normalize_version(version) or version or "").strip().lstrip("v")
    try:
        major, minor, patch = text.split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _preferred_implement_runner(version: str) -> str:
    return "codex-subagents" if _semver_tuple(version) >= (1, 3, 0) else "native-single"


def _preferred_implement_command(*, feature: str, project_root: Path, version: str, base: str) -> str:
    quoted_feature = json.dumps(feature, ensure_ascii=False)
    if _semver_tuple(version) >= (1, 3, 0):
        return f"beacon implement dev-run {quoted_feature} --project {project_root} --version {version}"
    return f"beacon implement run {quoted_feature} {base} --runner {_preferred_implement_runner(version)}"


def _preferred_plan_or_dev_command(*, feature: str, project_root: Path, version: str) -> str:
    quoted_feature = json.dumps(feature, ensure_ascii=False)
    if _semver_tuple(version) >= (1, 3, 0):
        return f"beacon implement dev-run {quoted_feature} --project {project_root} --version {version}"
    return f"beacon implement plan {quoted_feature} --project-root {project_root} --version {version}"


def _preferred_qa_command(*, feature: str, project_root: Path, version: str, base: str) -> str:
    quoted_feature = json.dumps(feature, ensure_ascii=False)
    if _semver_tuple(version) >= (1, 3, 0):
        return f"beacon qa team-run {quoted_feature} --project {project_root} --version {version}"
    return f"beacon qa run {quoted_feature} --project {project_root} --version {version} --json"


_CANONICAL_STAGE_ALIASES = {
    "think": "prd",
    "draft": "prd",
    "refined": "prd",
    "prd": "prd",
    "user-story": "user-story",
    "test-case": "test-case",
    "prototype": "prototype",
    "frozen": "implement",
    "implementation": "implement",
    "implement": "implement",
    "implemented": "qa",
    "verify": "qa",
    "verifying": "qa",
    "verified": "qa",
    "review": "qa",
    "qa": "qa",
    "gate": "release",
    "delivery": "release",
    "accepted": "release",
    "released": "release",
    "release": "release",
}

_CANONICAL_ACTION_ALIASES = {
    "implement-plan": "implement",
    "verify-run": "qa",
    "review-quality": "qa",
    "qa-run": "qa",
    "qa-resume": "qa",
    "release-check": "release",
    "workflow-start": "prd",
}

_CANONICAL_BLOCKING_REASON_ALIASES = {
    "verify_failed": "qa_failed",
    "implementation_reopened": "implement_reopened",
}

_STAGE_SKILL_KEYS = {
    "prd": ("prd", "think"),
    "user-story": ("user-story",),
    "test-case": ("test-case",),
    "prototype": ("prototype",),
    "implement": ("implement", "implementation"),
    "qa": ("qa", "verify", "review"),
    "release": ("release", "delivery", "gate"),
}


def canonicalize_lifecycle_stage(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return _CANONICAL_STAGE_ALIASES.get(text, text)


def canonicalize_lifecycle_action(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return _CANONICAL_ACTION_ALIASES.get(text, canonicalize_lifecycle_stage(text))


def canonicalize_blocking_reason(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return _CANONICAL_BLOCKING_REASON_ALIASES.get(text, text)


def _canonicalize_reason_list(values: list[str]) -> list[str]:
    return _unique_reasons_in_order([canonicalize_blocking_reason(value) for value in values])


def _blocking_reason_matches(values: list[str], *expected: str) -> bool:
    normalized = {
        text
        for text in (
            *(str(value or "").strip() for value in values),
            *(canonicalize_blocking_reason(value) for value in values),
        )
        if text
    }
    expected_normalized = {
        text
        for text in (
            *(str(value or "").strip() for value in expected),
            *(canonicalize_blocking_reason(value) for value in expected),
        )
        if text
    }
    return any(item in normalized for item in expected_normalized)


def _canonicalize_workflow_progress(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    display = dict(payload)
    display["next_stage"] = canonicalize_lifecycle_stage(payload.get("next_stage"))
    display["missing_closure_stages"] = [
        canonicalize_lifecycle_stage(value)
        for value in payload.get("missing_closure_stages", [])
        if canonicalize_lifecycle_stage(value)
    ] if isinstance(payload.get("missing_closure_stages"), list) else []
    return display


def _stage_skill_keys(stage: str) -> tuple[str, ...]:
    canonical = canonicalize_lifecycle_stage(stage)
    keys = _STAGE_SKILL_KEYS.get(canonical, (canonical or stage,))
    return tuple(key for key in keys if key)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _auto_test_status(project_root: Path) -> dict[str, Any]:
    return _read_json(project_root / ".beacon" / "auto-test-status.json")


def _implement_state_recency(payload: dict[str, Any], *, fallback_key: str = "") -> str:
    return str(
        payload.get("generated_at", "")
        or payload.get("updated_at", "")
        or payload.get("implemented_at", "")
        or payload.get("run_id", "")
        or fallback_key
    ).strip()


def _latest_implement_state(project_root: Path, *, feature: str, version: str) -> dict[str, Any]:
    impl_root = project_root / ".beacon" / "implement"
    if not impl_root.exists():
        return {}
    target_slug = feature_slug(feature)
    candidates: list[tuple[str, dict[str, Any]]] = []
    for state_path in sorted(impl_root.glob("*/state.json"), reverse=True):
        payload = _read_json(state_path)
        if str(payload.get("feature_slug", "") or "") != target_slug:
            continue
        payload_version = str(payload.get("version", "") or "").strip()
        if payload_version and payload_version != version:
            continue
        candidates.append((state_path.parent.name, payload))
    if not candidates:
        return {}
    non_handoff = [
        (key, payload)
        for key, payload in candidates
        if str(payload.get("status", "") or "").strip().lower() not in {"handoff_required", "waiting_for_handoff"}
    ]
    pool = non_handoff or candidates
    ordered = sorted(pool, key=lambda item: _implement_state_recency(item[1], fallback_key=item[0]), reverse=True)
    return ordered[0][1]


def _ralph_handoff_is_stale(
    *,
    ralph_state: dict[str, Any] | None,
    implement_state: dict[str, Any] | None,
    feature_scorecard: dict[str, Any] | None,
) -> bool:
    if not isinstance(ralph_state, dict) or not ralph_state:
        return False
    blocker = str(ralph_state.get("current_blocker", "") or "").strip()
    next_action = str(ralph_state.get("next_action", "") or "").strip()
    recommended_command = str(ralph_state.get("recommended_command", "") or "").strip()
    if blocker != "handoff_required" and next_action != "handoff_execute" and "request.md" not in recommended_command:
        return False
    if not isinstance(implement_state, dict) or not implement_state:
        return False
    implement_status = str(implement_state.get("status", "") or "").strip().lower()
    implement_run_id = str(implement_state.get("run_id", "") or "").strip()
    active_run_id = str(ralph_state.get("active_run_id", "") or "").strip()
    continue_decision = str((feature_scorecard or {}).get("continue_decision", "") or "").strip()
    return bool(
        implement_status == "completed"
        and implement_run_id
        and implement_run_id != active_run_id
        and continue_decision in {"continue", "stop_for_repair", "ready_for_release", ""}
    )


def _infer_current_stage(*, revision_state: dict[str, Any], workflow_progress: dict[str, Any]) -> str:
    stages = workflow_progress.get("stages") if isinstance(workflow_progress.get("stages"), dict) else {}
    next_stage = canonicalize_lifecycle_stage(workflow_progress.get("next_stage"))
    if next_stage:
        return next_stage
    delivery = str(revision_state.get("delivery_status", "") or "")
    if delivery == "accepted":
        return "accepted"
    if delivery == "released":
        return "release"
    if delivery in {"implemented", "verifying", "verified"}:
        return "qa"
    if str(stages.get("verify", {}).get("status", "") or "") == "failed":
        return "qa"
    if str(revision_state.get("doc_status", "") or "") == "frozen" and delivery in {"", "idle", "draft"}:
        return "implement"
    return canonicalize_lifecycle_stage(delivery) or canonicalize_lifecycle_stage(revision_state.get("doc_status")) or "prd"


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


def _semantic_gate_required(project_root: Path, *, version: str, feature: str) -> bool:
    return bool(str(feature or "").strip()) and _semver_tuple(version) >= (1, 3, 6) and version_requires_prototype(project_root, version)


def _normalize_intent_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _detect_post_freeze_change_intent(intent_text: str | None) -> bool:
    normalized = _normalize_intent_text(intent_text)
    if not normalized:
        return False
    keywords = (
        "change",
        "scope change",
        "change request",
        "reopen",
        "re-freeze",
        "refreeze",
        "revise",
        "hotfix",
        "adjust",
        "modify",
        "需求调整",
        "改需求",
        "变更",
        "范围调整",
        "补边界",
        "重新冻结",
        "需求补充",
        "recheck",
    )
    return any(keyword in normalized for keyword in keywords)


def _build_change_loop_payload(
    *,
    feature: str,
    version: str,
    project_root: Path,
    revision_state: dict[str, Any],
    change_intent: str | None,
) -> dict[str, Any]:
    intent_text = str(change_intent or "").strip()
    doc_status = str(revision_state.get("doc_status", "") or "")
    source_revision_id = str(revision_state.get("source_revision_id", "") or "")
    superseded_by = str(revision_state.get("superseded_by", "") or "")
    has_post_freeze_context = bool(doc_status == "frozen" or source_revision_id or superseded_by)
    intent_detected = _detect_post_freeze_change_intent(intent_text)
    metadata_path = metadata_machine_path(project_root)
    project_metadata_context = {
        "metadata_ref": str(metadata_path.relative_to(project_root)) if metadata_path.exists() else "",
        "resolved_metadata_view": resolve_project_metadata_view(project_root, version=version),
    }
    ladder = [
        "beacon-change",
        "reopen",
        "doctor metadata verify",
        "doctor metadata update",
        "prd revise",
        "user-story refresh",
        "test-case refresh",
        "prototype refresh",
        "freeze",
        "implement fix",
        "qa delta-run",
        "release recheck",
    ]
    return {
        "intent": intent_text,
        "intent_detected": intent_detected,
        "has_post_freeze_context": has_post_freeze_context,
        "recommended": bool(feature and intent_detected and has_post_freeze_context),
        "route": "beacon-change",
        "reason": (
            "feature is already in a frozen/revisioned state and the request looks like a post-freeze requirement change"
            if feature and intent_detected and has_post_freeze_context
            else ""
        ),
        "ladder": ladder,
        "project_metadata_context": project_metadata_context,
        "reopen_command": (
            f"beacon reopen {json.dumps(feature, ensure_ascii=False)} --project-root {project_root} --version {version} --reason change-request"
            if feature
            else ""
        ),
        "metadata_verify_command": (
            f"beacon doctor metadata verify --project-root {project_root} --version {version} --json"
        ),
        "metadata_update_command": (
            f"beacon doctor metadata update --project-root {project_root} --version {version} --json"
        ),
    }


def _resolve_hud_refs(
    *,
    project_root: Path,
    feature: str,
    implement_state: dict[str, Any],
    ralph_state: dict[str, Any],
) -> dict[str, str]:
    refs: dict[str, str] = {"team_hud_json": "", "team_hud_html": "", "ralph_state_json": ""}
    if feature:
        refs["ralph_state_json"] = str((project_root / ".beacon" / "ralph" / f"{feature_slug(feature)}.json").relative_to(project_root))
    team_execution = implement_state.get("team_execution") if isinstance(implement_state.get("team_execution"), dict) else {}
    hud = team_execution.get("hud") if isinstance(team_execution.get("hud"), dict) else {}
    refs["team_hud_json"] = str(hud.get("json", "") or "")
    refs["team_hud_html"] = str(hud.get("html", "") or "")
    if refs["team_hud_json"] or refs["team_hud_html"]:
        return refs
    team_mode = implement_state.get("team_mode") if isinstance(implement_state.get("team_mode"), dict) else {}
    refs["team_hud_json"] = str(team_mode.get("hud_json", "") or "")
    refs["team_hud_html"] = str(team_mode.get("hud_html", "") or "")
    if not ralph_state and refs["ralph_state_json"]:
        refs["ralph_state_json"] = ""
    return refs


def _supports_skill_discover(version: str) -> bool:
    normalized = release_line_key(version) or normalize_version(version) or ""
    if not normalized.startswith("v"):
        return False
    try:
        major, minor, patch = [int(part) for part in normalized[1:].split(".")]
    except Exception:  # noqa: BLE001
        return False
    return (major, minor, patch) >= (1, 2, 0)


def _resolve_canonical_feature_name(
    *,
    requested_feature: str,
    revision_state: dict[str, Any] | None,
    story_state: dict[str, Any] | None,
) -> str:
    requested = str(requested_feature or "").strip()
    revision_state = revision_state if isinstance(revision_state, dict) else {}
    story_state = story_state if isinstance(story_state, dict) else {}
    candidates = [
        str(story_state.get("title") or "").strip(),
        str(story_state.get("feature") or "").strip(),
        str(revision_state.get("feature") or "").strip(),
        requested,
    ]
    for value in candidates:
        if value:
            return value
    return requested


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
    next_stage = canonicalize_lifecycle_stage(workflow_progress.get("next_stage"))
    stage_candidates: list[str] = []
    if delivery_status in {"implemented", "verifying", "verified"} or next_stage == "qa":
        stage_candidates.append("qa")
    if delivery_status in {"accepted", "released"}:
        stage_candidates.append("release")
    if doc_status == "frozen" and delivery_status in {"", "idle", "draft"}:
        stage_candidates.append("implement")
    if next_stage:
        stage_candidates.append(next_stage)
    for stage in stage_candidates:
        for skill_stage in _stage_skill_keys(stage):
            skill_id = str(skills.get(skill_stage, "") or "").strip()
            if skill_id:
                return {"stage": stage, "skill_id": skill_id, "status": "bound"}
    return {
        "stage": canonicalize_lifecycle_stage(stage_candidates[0]) if stage_candidates else "",
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
    release_summary: dict[str, Any] | None = None,
    takeover_gate: dict[str, Any] | None = None,
    implementation_plan_gate: dict[str, Any] | None = None,
    requirement_clarity_gate: dict[str, Any] | None = None,
    requirement_package_gate: dict[str, Any] | None = None,
    semantic_contract: dict[str, Any] | None = None,
) -> list[str]:
    reasons: list[str] = []
    feature_scorecard = feature_scorecard if isinstance(feature_scorecard, dict) else {}
    release_summary = release_summary if isinstance(release_summary, dict) else {}
    delivery_status = str(revision_state.get("delivery_status", "") or "")
    continue_decision = str(feature_scorecard.get("continue_decision") or "").strip()
    scorecard_release_ready = bool(feature_scorecard.get("release_ready", False))
    profile_gate_pass = isinstance(profile_gate, dict) and str(profile_gate.get("status", "") or "").strip() == "pass"
    freeze_gate_exempt = delivery_status in {"implemented", "verifying", "verified", "accepted", "released"} or continue_decision == "ready_for_release"
    qa_closure_authoritative = scorecard_release_ready or continue_decision == "ready_for_release" or profile_gate_pass

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
    if str(revision_state.get("doc_status", "") or "draft") != "frozen" and not freeze_gate_exempt:
        reasons.append("revision_not_frozen")
    verify_status = str(workflow_progress.get("stages", {}).get("verify", {}).get("status", "") or "")
    if verify_status == "failed":
        reasons.append("verify_failed")
    if str(revision_state.get("superseded_by", "") or ""):
        reasons.append("revision_superseded")
    if (coverage.get("planned_story", 0) or 0) <= 0 and not qa_closure_authoritative:
        reasons.append("missing_user_story")
    if (
        delivery_status in {"implemented", "verifying", "verified", "accepted", "released"}
        and not bool(coverage.get("full_coverage", False))
        and not qa_closure_authoritative
    ):
        reasons.append("coverage_incomplete")
    if delivery_status == "blocked":
        reasons.append("workflow_blocked")
    gate_issues = profile_gate.get("issues", []) if isinstance(profile_gate, dict) and isinstance(profile_gate.get("issues"), list) else []
    for item in gate_issues:
        if not isinstance(item, dict):
            continue
        code = str(item.get("reason_code", "") or "").strip()
        if code:
            reasons.append(code)
    if str(feature_scorecard.get("continue_decision") or "").strip() == "stop_for_repair":
        reasons.append("qa_stop_for_repair")
        reasons.extend(
            str(item).strip()
            for item in (feature_scorecard.get("stop_reasons") or [])
            if str(item).strip()
        )
    if str(release_summary.get("gate_status") or "").strip().lower() == "blocked" and (
        delivery_status in {"implemented", "verifying", "verified", "accepted", "released"}
        or continue_decision == "ready_for_release"
        or scorecard_release_ready
    ):
        reasons.append("release_gate_blocked")
        reasons.extend(
            str(item).strip()
            for item in (release_summary.get("gate_reason_codes") or [])
            if str(item).strip()
        )
    if isinstance(control_plane, dict) and int(control_plane.get("failure_streak", 0) or 0) > 0:
        reasons.append("control_plane_escalation_active")
    if isinstance(requirement_clarity_gate, dict) and bool(requirement_clarity_gate.get("blocked")):
        code = str(requirement_clarity_gate.get("reason_code", "") or "").strip()
        if code:
            reasons.append(code)
    if isinstance(requirement_package_gate, dict) and str(requirement_package_gate.get("status", "") or "") == "blocked":
        code = str(requirement_package_gate.get("reason_code", "") or "").strip()
        if code:
            reasons.append(code)
        reasons.extend(
            str(item).strip()
            for item in (requirement_package_gate.get("failure_categories") or [])
            if str(item).strip()
        )
    implementation_gate_relevant = delivery_status not in {"accepted", "released"} and not qa_closure_authoritative
    if implementation_gate_relevant and isinstance(implementation_plan_gate, dict) and bool(implementation_plan_gate.get("blocked")):
        code = str(implementation_plan_gate.get("reason_code", "") or "").strip()
        if code:
            reasons.append(code)
    if isinstance(semantic_contract, dict) and semantic_contract:
        status = str(semantic_contract.get("status", "") or "").strip().lower()
        code = str(semantic_contract.get("reason_code", "") or "").strip()
        if status not in {"", "pass"} and code:
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
    requirement_clarity_gate: dict[str, Any] | None = None,
    requirement_package_gate: dict[str, Any] | None = None,
    version_guard: dict[str, Any] | None = None,
    discovery_hint: dict[str, Any] | None = None,
    change_loop: dict[str, Any] | None = None,
    semantic_contract: dict[str, Any] | None = None,
) -> dict[str, str]:
    quoted_feature = json.dumps(feature, ensure_ascii=False)
    base = f'--project-root {project_root} --version {version}'
    next_stage = canonicalize_lifecycle_stage(workflow_progress.get("next_stage"))
    run_id = str(workflow_progress.get("run_id", "") or "")
    feature_scorecard = feature_scorecard if isinstance(feature_scorecard, dict) else {}
    stage_binding = stage_binding if isinstance(stage_binding, dict) else {}
    delivery_status = str(revision_state.get("delivery_status", "") or "")
    change_loop = change_loop if isinstance(change_loop, dict) else {}
    semantic_contract = semantic_contract if isinstance(semantic_contract, dict) else {}
    requirement_package_gate = requirement_package_gate if isinstance(requirement_package_gate, dict) else {}

    if any(
        reason in {
            "semantic_contract_missing",
            "semantic_dictionary_missing",
            "semantic_usage_guidelines_missing",
            "semantic_official_language_missing",
            "semantic_default_taste_bridge_drift",
            "semantic_prototype_binding_drift",
        }
        for reason in blocking_reasons
    ):
        return {
            "action": "prototype",
            "reason": "prototype semantic contract is incomplete or drifted and must be regenerated from requirement truth",
            "command": f"beacon prototype create {quoted_feature} --project {project_root} --version {version} --json",
        }
    if "semantic_review_missing" in blocking_reasons:
        return {
            "action": "prototype-review",
            "reason": "semantic review is not ready; re-run prototype review before implementation or release",
            "command": f"beacon prototype review {quoted_feature} --project {project_root} --version {version} --json",
        }

    if bool(change_loop.get("recommended", False)):
        return {
            "action": "beacon-change",
            "reason": str(change_loop.get("reason") or "post-freeze requirement change should route through the change loop"),
            "command": str(change_loop.get("route") or "beacon-change"),
        }

    if project_mode == "takeover" and "takeover_baseline_required" in blocking_reasons:
        return {
            "action": "takeover-baseline",
            "reason": "takeover projects must freeze current-state architecture, service-map, and boundaries before implementation",
            "command": f"beacon doctor advise --project-root {project_root} --version {version} --feature {quoted_feature}",
        }

    if not blocked and delivery_status in {"accepted", "released"} and (
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
        if _blocking_reason_matches(stop_reasons, "implementation_reopened", "implement_reopened", "bug_filed"):
            return {
                "action": "implement",
                "reason": "qa round found an implementation blocker that must be fixed before the next round",
                "command": _preferred_implement_command(feature=feature, project_root=project_root, version=version, base=base),
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
                "action": "qa",
                "reason": "project workflow or evidence gate is still blocking the QA round",
                "command": f"beacon verify run {quoted_feature} {base}{profile_arg}",
            }
        return {
            "action": "qa",
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
            "action": "qa",
            "reason": "qa coverage is incomplete but no severe blocker requires stopping the round",
            "command": _preferred_qa_command(feature=feature, project_root=project_root, version=version, base=base),
        }
    if continue_decision == "ready_for_release" and not blocked:
        return {
            "action": "release-check",
            "reason": "current QA round is ready for release/governance evaluation",
            "command": f"beacon gate check release --project-root {project_root} --version {version}",
        }

    if blocked:
        if "requirement_package_contract_blocked" in blocking_reasons:
            action = str(requirement_package_gate.get("recommended_action", "") or "").strip()
            reason = str(requirement_package_gate.get("recommended_reason", "") or "").strip()
            command = str(requirement_package_gate.get("recommended_command", "") or "").strip()
            if action and command:
                return {
                    "action": action,
                    "reason": reason or "requirement package closure is blocked and must be reconciled before execution continues",
                    "command": command,
                }
        if "release_gate_blocked" in blocking_reasons or any(
            reason.startswith("evidence_sha256_manifest")
            for reason in blocking_reasons
        ):
            return {
                "action": "release-check",
                "reason": "release governance is currently blocked and must be reconciled before publishing",
                "command": f"beacon gate check release --project-root {project_root} --version {version}",
            }
        if "context_version_mismatch" in blocking_reasons:
            recommended_version = str((version_guard or {}).get("recommended_version", "") or "")
            command_version = recommended_version or version
            return {
                "action": "use-context-version",
                "reason": "the requested version conflicts with the current managed context and would write to the wrong docs line",
                "command": f"beacon help --project-root {project_root} --version {command_version} --feature {quoted_feature}",
            }
        if "requirement_clarity_open" in blocking_reasons:
            report_path = ""
            if isinstance(requirement_clarity_gate, dict):
                report_path = str(requirement_clarity_gate.get("report_json_path", "") or "")
            return {
                "action": "requirement-clarity",
                "reason": "requirements still contain unresolved or ambiguous items and must be clarified before freeze",
                "command": report_path or f"beacon doctor sync-requirement-clarity {quoted_feature} --project-root {project_root} --version {version} --json",
            }
        if any(
            reason in {
                "technical_review_contract_missing",
                "technical_review_contract_invalid",
                "implementation_plan_missing",
                "implementation_plan_invalid",
                "implementation_plan_feature_version_mismatch",
                "implementation_plan_revision_mismatch",
                "implementation_plan_baseline_mismatch",
                "implementation_plan_source_refs_incomplete",
                "implementation_plan_cleanup_missing",
                "delivery_baseline_missing",
                "delivery_baseline_projection_drift",
                "architecture_blueprint_projection_missing",
                "architecture_blueprint_projection_drift",
            }
            for reason in blocking_reasons
        ):
            if any(reason in {"technical_review_contract_missing", "technical_review_contract_invalid"} for reason in blocking_reasons):
                contract_path = ""
                replan_command = ""
                if isinstance(implementation_plan_gate, dict):
                    tech_gate = implementation_plan_gate.get("technical_review_gate") if isinstance(implementation_plan_gate.get("technical_review_gate"), dict) else {}
                    contract_path = str(tech_gate.get("contract_json_path", "") or "")
                    recommended = str(implementation_plan_gate.get("recommended_command", "") or "").strip()
                    if recommended.startswith("beacon implement plan "):
                        replan_command = recommended
                if replan_command:
                    return {
                        "action": "implement-plan",
                        "reason": "the frozen revision advanced and implementation projections must be regenerated from the canonical delivery baseline",
                        "command": replan_command,
                    }
                return {
                    "action": "technical-review-contract",
                    "reason": "implementation requires a deterministic technical review contract before planning or coding can proceed",
                    "command": contract_path or f"docs/beacon/{version}/.machine/execution/deterministic-implementation-contract-<feature>.json",
                }
            if _supports_skill_discover(version) and not profile and bool((discovery_hint or {}).get("recommended", False)):
                return {
                    "action": "skill-discover",
                    "reason": str((discovery_hint or {}).get("reason") or "project skill onboarding is not configured; discover a bounded project profile before implementation planning"),
                    "command": str((discovery_hint or {}).get("command") or f"beacon skill discover --project-root {project_root} --json"),
                }
            if "implementation_plan_missing" in blocking_reasons:
                return {
                    "action": "implement-plan",
                    "reason": "implementation requires execution-ready planning aligned to the active frozen revision",
                    "command": _preferred_plan_or_dev_command(feature=feature, project_root=project_root, version=version),
                }
            return {
                "action": "implement",
                "reason": "implementation requires execution-ready planning aligned to the active frozen revision",
                "command": _preferred_plan_or_dev_command(feature=feature, project_root=project_root, version=version),
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
                "action": "qa",
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
        if _blocking_reason_matches(blocking_reasons, "verify_failed", "qa_failed"):
            return {
                "action": "qa",
                "reason": "verification is failing and quality review / fixes are required",
                "command": f"beacon review quality {quoted_feature} {base}",
            }
        if "coverage_incomplete" in blocking_reasons:
            return {
                "action": "qa",
                "reason": "coverage is still incomplete; do not advance to release-check until remaining AC/test evidence is closed",
                "command": _preferred_qa_command(feature=feature, project_root=project_root, version=version, base=base),
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
                    "action": "qa",
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
                "action": "qa",
                "reason": "project profile verification evidence is satisfied; move into formal quality review",
                "command": f"beacon review quality {quoted_feature} {base}",
            }
        if doc_status == "frozen" and delivery_status in {"", "idle", "draft"} and str(stage_binding.get("skill_id", "") or "").strip():
            return {
                "action": str(stage_binding.get("stage") or "implement"),
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
                "action": "implement",
                "reason": "implementation requires execution-ready planning aligned to the frozen revision baseline",
                "command": _preferred_plan_or_dev_command(feature=feature, project_root=project_root, version=version),
            }
        return {
            "action": "implement",
            "reason": "revision is frozen and ready for native implementation",
            "command": _preferred_implement_command(feature=feature, project_root=project_root, version=version, base=base),
        }

    if delivery_status in {"implemented", "verifying", "verified"} or next_stage == "qa":
        return {
            "action": "qa",
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
            "action": "prd",
            "reason": "no active workflow run found for the requested feature/version",
            "command": f"beacon workflow start {quoted_feature} --project {project_root} --version {version}",
        }

    if next_stage in {"prd", "user-story", "prototype", "test-case"}:
        return {
            "action": next_stage,
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
        "action": canonicalize_lifecycle_action(next_stage) or "status",
        "reason": "follow workflow progression to the next stage",
        "command": f"beacon workflow continue --project-root {project_root} --version {version}",
    }


def build_help_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str | None = None,
    run_id: str | None = None,
    change_intent: str | None = None,
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
    feature_name = _resolve_canonical_feature_name(
        requested_feature=feature_name,
        revision_state=revision_state,
        story_state=story_state,
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
    release_scorecard = build_release_scorecard(project_root, version=resolved_version) if feature_name else {}
    release_summary = summarize_release_scorecard(release_scorecard) if release_scorecard else {}
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
    requirement_clarity_gate = (
        build_requirement_clarity_gate_payload(project_root, version=resolved_version, feature=feature_name)
        if feature_name
        else {}
    )
    requirement_package_gate = build_requirement_package_gate(
        project_root,
        version=resolved_version,
        feature=feature_name,
        strict=True,
    )
    semantic_contract = (
        evaluate_semantic_contract(project_root, version=resolved_version, feature=feature_name)
        if _semantic_gate_required(project_root, version=resolved_version, feature=feature_name)
        else {}
    )
    if isinstance(requirement_clarity_gate, dict) and feature_name:
        requirement_clarity_gate["report_json_path"] = f"docs/beacon/{resolved_version}/.machine/execution/requirement-clarity-{feature_slug(feature_name)}.json"
    stage_binding = _stage_local_execution_binding(
        profile=profile,
        revision_state=revision_state,
        workflow_progress=workflow_progress,
    )
    change_loop = _build_change_loop_payload(
        feature=feature_name,
        version=resolved_version,
        project_root=project_root,
        revision_state=revision_state,
        change_intent=change_intent,
    )
    ralph_state = load_ralph_state(project_root, feature=feature_name) if feature_name else {}
    implement_state = _latest_implement_state(project_root, feature=feature_name, version=resolved_version) if feature_name else {}
    blocking = _blocking_reasons(
        revision_state=revision_state,
        workflow_progress=workflow_progress,
        coverage=coverage,
        version_guard=version_guard,
        profile_gate=profile_gate,
        control_plane=control_plane,
        feature_scorecard=feature_scorecard,
        release_summary=release_summary,
        takeover_gate=takeover_gate,
        implementation_plan_gate=implementation_plan_gate,
        requirement_clarity_gate=requirement_clarity_gate,
        requirement_package_gate=requirement_package_gate,
        semantic_contract=semantic_contract,
    )
    scorecard_release_ready = bool(feature_scorecard.get("release_ready", False))
    scorecard_continue_decision = str(feature_scorecard.get("continue_decision", "") or "").strip()
    qa_closure_authoritative = scorecard_release_ready or scorecard_continue_decision == "ready_for_release"
    ralph_handoff_stale = _ralph_handoff_is_stale(
        ralph_state=ralph_state,
        implement_state=implement_state,
        feature_scorecard=feature_scorecard,
    )
    if (
        isinstance(ralph_state, dict)
        and str(ralph_state.get("phase", "") or "").strip()
        and not qa_closure_authoritative
        and not ralph_handoff_stale
    ):
        current_blocker = str(ralph_state.get("current_blocker", "") or "").strip()
        stop_state = str(ralph_state.get("stop_state", "") or "").strip()
        if current_blocker:
            blocking = [current_blocker]
        elif stop_state and stop_state != "release_ready":
            blocking = [stop_state]
    blocked = bool(blocking)
    current_stage = _infer_current_stage(revision_state=revision_state, workflow_progress=workflow_progress)
    release_gate_status = str(release_summary.get("gate_status") or "").strip().lower()
    if feature_name and current_stage != "accepted" and (
        str(feature_scorecard.get("continue_decision") or "").strip() == "ready_for_release"
        or bool(release_summary.get("release_ready", False))
        or release_gate_status == "blocked"
    ):
        current_stage = "release"
    workflow_progress_display = _canonicalize_workflow_progress(workflow_progress)
    blocking_display = _canonicalize_reason_list(blocking)
    profile_binding_source = (
        _profile_binding_source(project_root, version=resolved_version, feature=feature_name)
        if feature_name
        else "none"
    )
    learning_surface = load_learning_plane_contract(project_root)
    qa_status = load_qa_status(project_root)
    current_qa_session = load_current_qa_session(project_root)
    host_runtime = str(implement_state.get("host_runtime", "") or "").strip() or detect_host_runtime(None)
    runtime_precheck = (
        (implement_state.get("subagent_prechecks") or {}).get("runtime_readiness", {})
        if isinstance(implement_state.get("subagent_prechecks"), dict)
        else {}
    )
    if not runtime_precheck:
        runtime_precheck = runtime_readiness_precheck(project_root, host_runtime=host_runtime)
    delegation_precheck = (
        (implement_state.get("subagent_prechecks") or {}).get("delegation_readiness", {})
        if isinstance(implement_state.get("subagent_prechecks"), dict)
        else {}
    )
    if not delegation_precheck and feature_name:
        delegation_precheck = delegation_readiness_precheck(project_root, feature=feature_name, version=resolved_version)
    archive_boundary = load_archive_read_model(project_root, version=resolved_version, feature=feature_name) if feature_name else {}
    feature_archive = archive_boundary.get("feature") if isinstance(archive_boundary.get("feature"), dict) else {}
    host_prompt_trace = load_host_prompt_trace(project_root, version=resolved_version, feature=feature_name) if feature_name else {}
    archive_status = str(feature_archive.get("status", "") or "active")
    if archive_status in {"archived-learnable", "archived-reference-only"}:
        blocking = _unique_reasons_in_order([*blocking, "feature_archived_from_current_delivery"])
        blocked = True
        blocking_display = _canonicalize_reason_list(blocking)
    implement_mode = str(implement_state.get("mode", "") or "")
    freeze_status = "pass" if str(revision_state.get("doc_status", "") or "") == "frozen" else str(revision_state.get("doc_status", "") or "draft")
    team_phase = ""
    if implement_mode == "team":
        team_phase = str(implement_state.get("status", "") or "")
    elif bool((feature_archive or {}).get("active_delivery", False)) and str(revision_state.get("delivery_status", "") or "") in {"implemented", "verifying", "verified"}:
        team_phase = "completed"
    ralph_status = "active" if (str(ralph_state.get("phase", "") or "").strip() and not ralph_handoff_stale) else ""
    if _semver_tuple(resolved_version) >= (1, 3, 8) and team_phase in {"completed", "passed"} and not ralph_status and not qa_closure_authoritative:
        ralph_status = "pending"
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
        "host_runtime": host_runtime,
        "implement_mode": implement_mode,
        "implement_runner": str(implement_state.get("runner", "") or ""),
        "freeze_status": freeze_status,
        "team_phase": team_phase,
        "subagent_runtime_status": str(runtime_precheck.get("status", "") or ""),
        "subagent_delegation_status": str(delegation_precheck.get("status", "") or ""),
        "archive_status": archive_status,
        "archive_reason": str(feature_archive.get("reason", "") or ""),
        "ralph_phase": "" if ralph_handoff_stale else str(ralph_state.get("phase", "") or ""),
        "ralph_status": ralph_status,
        "ralph_stop_state": "" if ralph_handoff_stale else str(ralph_state.get("stop_state", "") or ""),
        "ralph_next_action": "" if ralph_handoff_stale else str(ralph_state.get("next_action", "") or ""),
        "ralph_round_count": 0 if ralph_handoff_stale else int(ralph_state.get("round_count", 0) or 0),
        "ralph_last_round_ref": "" if ralph_handoff_stale else str(ralph_state.get("last_round_ref", "") or ""),
        "ralph_failure_streak": 0 if ralph_handoff_stale else int(ralph_state.get("failure_streak", 0) or 0),
        "ralph_no_delta_streak": 0 if ralph_handoff_stale else int(ralph_state.get("no_delta_streak", 0) or 0),
        "host_prompt_trace_ref": (
            f"docs/beacon/{resolved_version}/.machine/execution/host-prompt-trace-{feature_slug(feature_name)}.json"
            if feature_name and host_prompt_trace
            else ""
        ),
        "host_prompt_trace_status": str(((host_prompt_trace.get("latest_event") or {}) if isinstance(host_prompt_trace, dict) else {}).get("route_status", "") or ""),
        "host_prompt_trace_command": str(((host_prompt_trace.get("latest_event") or {}) if isinstance(host_prompt_trace, dict) else {}).get("mapped_command", "") or ""),
        "qa_execution_mode": str(qa_status.get("execution_mode", "") or ""),
        "qa_current_session_id": str(current_qa_session.get("session_id", "") or ""),
        "qa_runner_type": str(current_qa_session.get("runner_type", "") or ""),
    }
    delivery_read_model = (
        load_delivery_read_model(project_root, version=resolved_version, feature=feature_name)
        if feature_name
        else {}
    )
    delivery_contract = delivery_read_model.get("contract") if isinstance(delivery_read_model.get("contract"), dict) else {}
    if delivery_contract:
        execution_surface["host_runtime"] = str(
            delivery_contract.get("host_runtime") or execution_surface.get("host_runtime") or ""
        )
        execution_surface["implement_mode"] = str(
            delivery_contract.get("effective_mode") or execution_surface.get("implement_mode") or ""
        )
        execution_surface["implement_runner"] = str(
            delivery_contract.get("runner") or execution_surface.get("implement_runner") or ""
        )
        contract_snapshot = delivery_contract.get("capability_snapshot") if isinstance(delivery_contract.get("capability_snapshot"), dict) else {}
        execution_surface["subagent_runtime_status"] = str(
            contract_snapshot.get("subagent_runtime_status") or execution_surface.get("subagent_runtime_status") or ""
        )
        execution_surface["subagent_delegation_status"] = str(
            contract_snapshot.get("subagent_delegation_status") or execution_surface.get("subagent_delegation_status") or ""
        )
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
        requirement_clarity_gate=requirement_clarity_gate,
        requirement_package_gate=requirement_package_gate,
        version_guard=version_guard,
        discovery_hint=discovery_hint,
        change_loop=change_loop,
        semantic_contract=semantic_contract,
    )
    if (
        isinstance(ralph_state, dict)
        and str(ralph_state.get("recommended_command", "") or "").strip()
        and not qa_closure_authoritative
        and not ralph_handoff_stale
    ):
        next_step = {
            "action": canonicalize_lifecycle_action(ralph_state.get("next_action")) or "ralph",
            "reason": canonicalize_blocking_reason(ralph_state.get("current_blocker")) or "follow Ralph controller next step",
            "command": str(ralph_state.get("recommended_command", "") or ""),
        }
    quoted_feature = json.dumps(feature_name, ensure_ascii=False)
    if archive_status in {"archived-learnable", "archived-reference-only"}:
        next_step = {
            "action": "archive",
            "reason": "feature truth is archived and excluded from the current delivery plane",
            "command": f"beacon archive status --project-root {project_root} --version {resolved_version} --feature {quoted_feature} --json",
        }
    elif _semver_tuple(resolved_version) >= (1, 3, 8) and team_phase in {"completed", "passed"} and ralph_status == "pending" and not qa_closure_authoritative:
        next_step = {
            "action": "ralph",
            "reason": "post-freeze execution contract requires Ralph after implement-team before QA/release closure",
            "command": f"beacon implement run {quoted_feature} --project {project_root} --version {resolved_version} --mode ralph",
        }
    plan_counts = implementation_plan_progress.get("counts") if isinstance(implementation_plan_progress.get("counts"), dict) else {}
    progress_total = int(plan_counts.get("total", 0) or 0)
    progress_done = int(plan_counts.get("completed", 0) or 0)
    blocker_level = "blocked" if blocked else "warn" if (
        int(execution_surface.get("ralph_failure_streak", 0) or 0) > 0
        or int(execution_surface.get("ralph_no_delta_streak", 0) or 0) > 0
    ) else "none"
    hud_refs = _resolve_hud_refs(
        project_root=project_root,
        feature=feature_name,
        implement_state=implement_state,
        ralph_state=ralph_state if isinstance(ralph_state, dict) else {},
    )
    minimal_hud_payload = {
        "beacon_version": str(version_context.get("runtime_version", "") or resolved_version),
        "docs_version": resolved_version,
        "feature": feature_name,
        "stage": current_stage,
        "execution": {
            "mode": str(execution_surface.get("implement_mode", "") or ""),
            "elapsed": str(implement_state.get("generated_at", "") or "N/A"),
            "updated_at": str(implement_state.get("generated_at", "") or ""),
            "progress": {
                "done": progress_done,
                "total": progress_total,
                "round": int(execution_surface.get("ralph_round_count", 0) or 0),
            },
            "phase_summary": (
                f"freeze:{freeze_status} team:{team_phase or 'pending'} ralph:{ralph_status or 'idle'}"
            ),
            "circuit_status": "trip" if blocker_level == "blocked" else "warn" if blocker_level == "warn" else "ok",
        },
        "blocker": {
            "level": blocker_level,
            "reason": blocking_display[0] if blocking_display else "",
            "recommended_command": str(next_step.get("command", "") or ""),
        },
        "next_action": str(next_step.get("action", "") or ""),
        "hud_refs": hud_refs,
    }
    minimal_hud = build_minimal_hud(minimal_hud_payload)
    surface_explanation = build_surface_explanation(
        delivery_contract=delivery_contract,
        selected_surface=str(execution_surface.get("selected_surface") or ""),
        blocked=blocked,
        blocking_reasons=blocking,
        diagnostics_status="",
        next_action=str(next_step.get("action", "") or ""),
        next_command=str(next_step.get("command", "") or ""),
        fallback_allowed=bool(execution_surface.get("native_fallback_allowed", False)),
        fallback_reason_code=str(delivery_contract.get("fallback_reason") or ""),
    )
    support_surface_projection = build_support_surface_projection(
        project_root,
        version=resolved_version,
        feature=feature_name,
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
            "stage": canonicalize_lifecycle_stage(stage_binding.get("stage")),
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
        {
            "step": "requirement_package",
            "status": str(requirement_package_gate.get("status", "pass") or "pass"),
            "reason_code": str(requirement_package_gate.get("reason_code", "") or ""),
            "failure_categories": list(requirement_package_gate.get("failure_categories", [])),
            "remediation_mode": str(requirement_package_gate.get("remediation_mode", "") or ""),
        },
        {
            "step": "semantic_contract",
            "status": str(semantic_contract.get("status", "not_required") or "not_required"),
            "reason_code": str(semantic_contract.get("reason_code", "") or ""),
            "artifacts": dict(semantic_contract.get("artifacts", {})) if isinstance(semantic_contract.get("artifacts"), dict) else {},
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
        "version_semantics": version_context.get("version_semantics", {}),
        "context_version_guard": version_guard,
        "feature": feature_name,
        "feature_slug": feature_slug(feature_name),
        "version": resolved_version,
        "run_id": resolved_run_id,
        "project_mode": project_mode,
        "revision_id": str(revision_state.get("revision_id", "") or ""),
        "source_revision_id": str(revision_state.get("source_revision_id", "") or ""),
        "superseded_by": str(revision_state.get("superseded_by", "") or ""),
        "current_stage": current_stage,
        "doc_status": str(revision_state.get("doc_status", "") or "draft"),
        "delivery_status": str(revision_state.get("delivery_status", "") or "idle"),
        "blocked": blocked,
        "blocking_reasons": blocking_display,
        "blocked_reason": blocking_display[0] if blocking_display else "",
        "blocking_reasons_raw": blocking,
        "blocked_reason_raw": blocking[0] if blocking else "",
        "next_step": next_step,
        "lifecycle": {
            "current_stage": current_stage,
            "next_stage": str(workflow_progress_display.get("next_stage", "") or ""),
            "blocking_reasons": blocking_display,
            "blocked_reason": blocking_display[0] if blocking_display else "",
            "next_action": str(next_step.get("action", "") or ""),
        },
        "project_metadata_context": {
            "metadata_ref": str(metadata_machine_path(project_root).relative_to(project_root))
            if metadata_machine_path(project_root).exists()
            else "",
            "resolved_metadata_view": resolve_project_metadata_view(project_root, version=resolved_version),
        },
        "change_loop": change_loop,
        "revision_lineage": {
            "revision_id": str(revision_state.get("revision_id", "") or ""),
            "source_revision_id": str(revision_state.get("source_revision_id", "") or ""),
            "superseded_by": str(revision_state.get("superseded_by", "") or ""),
            "is_latest_revision": not bool(revision_state.get("superseded_by")),
            "is_frozen_baseline": str(revision_state.get("doc_status", "") or "") == "frozen",
        },
        "scores": {k: v.get("score") if isinstance(v, dict) else v for k, v in scores.items()},
        "score_details": scores,
        "release_summary": release_summary,
        "control_plane": control_plane,
        "coverage": coverage,
        "story_summary": story_summary,
        "workflow_progress": workflow_progress,
        "workflow_progress_display": workflow_progress_display,
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
        "delivery_read_model": delivery_read_model,
        "support_surface_projection": support_surface_projection,
        "archive": archive_boundary,
        "host_prompt_trace": host_prompt_trace,
        "surface_explanation": surface_explanation,
        "hud": hud_refs,
        "minimal_hud": {
            **minimal_hud,
            "payload": minimal_hud_payload,
        },
        "ralph": ralph_state,
        "learning_surface": learning_surface,
        "implementation_plan": implementation_plan,
        "implementation_plan_gate": implementation_plan_gate,
        "implementation_plan_progress": implementation_plan_progress,
        "requirement_clarity_gate": requirement_clarity_gate,
        "requirement_package_gate": requirement_package_gate,
        "semantic": semantic_contract,
        "decision_trace": decision_trace,
        "takeover_gate": takeover_gate,
        "feature_scorecard": feature_scorecard if isinstance(feature_scorecard, dict) else {},
    }
