"""Bounded automation runtime helpers for repeated QA/repair loops."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from beacon.utils.acceptance_kit import build_acceptance_kit_projection
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug

RUNTIME_SCHEMA_VERSION = "1.0"
RUNTIME_CLOSURE_STATES = {
    "active",
    "blocked",
    "release_ready",
    "closed",
    "human_escalation_required",
}
RUNTIME_NEXT_ROUTES = {"qa", "implement", "support_review", "change_refreeze", "release", "human"}
DEFAULT_TRUTH_RECOMPILE_TARGETS = ["user-story", "test-case", "requirement_clarity", "freeze"]


def automation_runtime_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "automation" / "features"


def feature_automation_runtime_path(project_root: Path, *, feature: str) -> Path:
    return automation_runtime_root(project_root) / feature_slug(feature) / "runtime.json"


def load_feature_automation_runtime(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(feature_automation_runtime_path(project_root, feature=feature), {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schema_version", RUNTIME_SCHEMA_VERSION)
    payload.setdefault("feature", str(feature).strip())
    payload.setdefault("feature_slug", feature_slug(feature))
    payload.setdefault("round_number", 0)
    payload.setdefault("previous_round_ref", "")
    payload.setdefault("current_round_ref", "")
    payload.setdefault("closure_state", "active")
    payload.setdefault("next_route", "qa")
    payload.setdefault("terminal_signal", "")
    payload.setdefault("human_takeover_required", False)
    payload.setdefault("active_issue_register", {})
    payload.setdefault("support_review", {})
    payload.setdefault("scenario_discovery", {})
    payload.setdefault("truth_recompiled_pending", False)
    payload.setdefault("truth_recompile_gate", {})
    payload.setdefault("promotion_proof_hooks", {})
    return payload


def write_feature_automation_runtime(project_root: Path, *, feature: str, payload: dict[str, Any]) -> Path:
    path = feature_automation_runtime_path(project_root, feature=feature)
    write_json(path, payload)
    return path


def _fingerprint(parts: list[str]) -> str:
    text = "|".join(str(item or "").strip() for item in parts)
    if not text.strip("|"):
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _runtime_truth_hash(status: dict[str, Any], scorecard: dict[str, Any], *, feature: str, version: str) -> str:
    explicit = str(status.get("truth_hash") or scorecard.get("truth_hash") or "").strip()
    if explicit:
        return explicit
    return _fingerprint(
        [
            version,
            feature,
            str(status.get("story_revision") or ""),
            str(status.get("acceptance_revision") or ""),
        ]
    )


def _runtime_evidence_hash(status: dict[str, Any], scorecard: dict[str, Any]) -> str:
    explicit = str(status.get("implementation_evidence_hash") or scorecard.get("implementation_evidence_hash") or "").strip()
    if explicit:
        return explicit
    return _fingerprint(
        [
            str(status.get("run_id") or ""),
            str(status.get("status") or ""),
            str(scorecard.get("continue_decision") or ""),
            str(scorecard.get("resume_command") or ""),
        ]
    )


def _normalized_active_issue_register(
    *,
    previous: dict[str, Any],
    stop_reasons: list[str],
    targeted_layers: list[str],
    targeted_tc_ids: list[str],
    targeted_scenario_ids: list[str],
    latest_ref: str,
) -> dict[str, Any]:
    previous_register = previous.get("active_issue_register") if isinstance(previous.get("active_issue_register"), dict) else {}
    accepted_fixes = previous_register.get("accepted_fixes") if isinstance(previous_register.get("accepted_fixes"), list) else []
    return {
        "unresolved_stop_reasons": [str(item).strip() for item in stop_reasons if str(item).strip()],
        "accepted_fixes": [str(item).strip() for item in accepted_fixes if str(item).strip()],
        "targeted_rerun_hints": {
            "targeted_layers": [str(item).strip() for item in targeted_layers if str(item).strip()],
            "targeted_tc_ids": [str(item).strip() for item in targeted_tc_ids if str(item).strip()],
            "targeted_scenario_ids": [str(item).strip() for item in targeted_scenario_ids if str(item).strip()],
        },
        "latest_ref": latest_ref,
        "previous_round_ref": str(previous.get("current_round_ref") or ""),
    }


def _support_review_payload(
    *,
    previous: dict[str, Any],
    executor: str,
    reason: str,
    repeat_count: int | None = None,
) -> dict[str, Any]:
    previous_payload = previous.get("support_review") if isinstance(previous.get("support_review"), dict) else {}
    normalized_repeat = repeat_count if repeat_count is not None else int(previous_payload.get("repeat_count") or 0) + 1
    return {
        "required": True,
        "executor": str(executor or "deep").strip() or "deep",
        "reason": str(reason or "structural_failure").strip() or "structural_failure",
        "repeat_count": int(normalized_repeat),
    }


def _scenario_discovery_payload(
    scenario_discovery: dict[str, Any] | None,
) -> dict[str, Any]:
    payload = scenario_discovery if isinstance(scenario_discovery, dict) else {}
    classification = str(payload.get("classification") or "").strip()
    requirement_meaning_delta = bool(payload.get("requirement_meaning_delta", False))
    if classification not in {"closure_supplement", "promotion_candidate"}:
        classification = "closure_supplement" if requirement_meaning_delta else "promotion_candidate"
    evidence_refs = [str(item).strip() for item in (payload.get("evidence_refs") or []) if str(item).strip()]
    finding_count_raw = payload.get("finding_count")
    finding_count = int(finding_count_raw) if str(finding_count_raw or "").strip() else len(evidence_refs)
    requires_truth_reopen = bool(payload.get("requires_truth_reopen", False) or requirement_meaning_delta or classification == "closure_supplement")
    return {
        "classification": classification,
        "requirement_meaning_delta": requirement_meaning_delta,
        "finding_count": finding_count,
        "evidence_refs": evidence_refs,
        "requires_truth_reopen": requires_truth_reopen,
    }


def _promotion_proof_hooks(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    projection = build_acceptance_kit_projection(project_root, version=version, feature=feature) if str(version).strip() else {}
    summary = projection.get("summary") if isinstance(projection.get("summary"), dict) else {}
    real_project_proof = summary.get("real_project_proof") if isinstance(summary.get("real_project_proof"), dict) else {}
    acceptance_present = bool(projection.get("present", False))
    acceptance_layers_passed = bool(summary.get("all_layers_passed", False)) if acceptance_present else False
    real_project_present = bool(real_project_proof.get("evidence_refs")) or str(real_project_proof.get("status") or "").strip().lower() in {"pass", "passed", "ok"}
    missing_hooks: list[str] = []
    if not acceptance_present:
        missing_hooks.append("acceptance_kit")
    elif not acceptance_layers_passed:
        missing_hooks.append("acceptance_layers")
    if not real_project_present:
        missing_hooks.append("real_project_proof")
    return {
        "acceptance_kit_present": acceptance_present,
        "acceptance_layers_passed": acceptance_layers_passed,
        "real_project_proof_present": real_project_present,
        "missing_hooks": missing_hooks,
        "acceptance_kit_reason_code": str(projection.get("reason_code") or ""),
    }


def _qa_route_from_status(
    *,
    qa_status: str,
    continue_decision: str,
    stop_reasons: list[str],
) -> tuple[str, str, str]:
    normalized_status = str(qa_status or "").strip().lower()
    normalized_continue = str(continue_decision or "").strip().lower()
    if normalized_status == "passed" or normalized_continue == "ready_for_release":
        return ("release_ready", "release", "qa_exit_ready_for_release")
    if normalized_continue in {"route_support_review", "support_review", "needs_support_review"}:
        return ("blocked", "support_review", "qa_route_support_review")
    if normalized_continue == "stop_for_repair":
        return ("blocked", "implement", "qa_route_implement_repair")
    if normalized_continue in {"human_escalation", "route_human", "handoff_to_human"}:
        return ("human_escalation_required", "human", "qa_route_human_escalation")
    if normalized_status in {"blocked", "failed"} and stop_reasons:
        return ("human_escalation_required", "human", "qa_route_human_escalation")
    return ("active", "qa", "qa_observation_recorded")


def derive_bounded_runtime_from_qa(
    project_root: Path,
    *,
    feature: str,
    status: dict[str, Any],
    scorecard: dict[str, Any],
) -> dict[str, Any]:
    previous = load_feature_automation_runtime(project_root, feature=feature)
    feature_name = str(status.get("feature") or feature).strip() or str(feature).strip()
    feature_version = str(status.get("version") or scorecard.get("version") or "")
    continue_decision = str(scorecard.get("continue_decision") or status.get("feature_scorecard", {}).get("continue_decision") or "")
    stop_reasons = scorecard.get("stop_reasons") if isinstance(scorecard.get("stop_reasons"), list) else []
    support_review = scorecard.get("support_review") if isinstance(scorecard.get("support_review"), dict) else {}
    scenario_discovery = scorecard.get("scenario_discovery") if isinstance(scorecard.get("scenario_discovery"), dict) else {}
    targeted_rerun = status.get("targeted_rerun") if isinstance(status.get("targeted_rerun"), dict) else {}
    targeted_layers = list(targeted_rerun.get("targeted_layers") or status.get("targeted_layers") or [])
    targeted_tc_ids = list(targeted_rerun.get("targeted_tc_ids") or status.get("targeted_tc_ids") or [])
    targeted_scenario_ids = list(targeted_rerun.get("targeted_scenario_ids") or status.get("targeted_scenario_ids") or [])
    closure_state, next_route, terminal_signal = _qa_route_from_status(
        qa_status=str(status.get("status") or ""),
        continue_decision=continue_decision,
        stop_reasons=[str(item).strip() for item in stop_reasons if str(item).strip()],
    )
    run_id = str(status.get("run_id") or "").strip()
    current_round_ref = f"qa:{run_id or 'observation'}"
    previous_ref = str(previous.get("current_round_ref") or "")
    previous_run_ref = str(previous.get("source", {}).get("run_id") or "")
    round_number = int(previous.get("round_number") or 0)
    if not previous_ref:
        round_number = 0
    elif run_id and run_id != previous_run_ref:
        round_number = round_number + 1
    support_review_payload = _support_review_payload(
        previous=previous,
        executor=str(support_review.get("executor") or "deep"),
        reason=str(support_review.get("reason") or continue_decision or "structural_failure"),
        repeat_count=support_review.get("repeat_count"),
    ) if next_route == "support_review" else {}
    scenario_payload = _scenario_discovery_payload(scenario_discovery)
    if scenario_payload.get("requires_truth_reopen"):
        next_route = "change_refreeze"
        terminal_signal = "qa_route_change_refreeze"
        support_review_payload = {}
    payload = {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "feature": feature_name,
        "feature_slug": feature_slug(feature_name),
        "version": feature_version,
        "closure_state": closure_state if closure_state in RUNTIME_CLOSURE_STATES else "active",
        "next_route": next_route if next_route in RUNTIME_NEXT_ROUTES else "qa",
        "terminal_signal": terminal_signal,
        "round_number": round_number,
        "previous_round_ref": previous_ref,
        "current_round_ref": current_round_ref,
        "truth_hash": _runtime_truth_hash(status, scorecard, feature=feature_name, version=feature_version),
        "implementation_evidence_hash": _runtime_evidence_hash(status, scorecard),
        "human_takeover_required": next_route == "human",
        "support_review": support_review_payload,
        "active_issue_register": _normalized_active_issue_register(
            previous=previous,
            stop_reasons=[str(item).strip() for item in stop_reasons if str(item).strip()],
            targeted_layers=targeted_layers,
            targeted_tc_ids=targeted_tc_ids,
            targeted_scenario_ids=targeted_scenario_ids,
            latest_ref=current_round_ref,
        ),
        "scenario_discovery": scenario_payload,
        "truth_recompiled_pending": False,
        "truth_recompile_gate": {
            "required": False,
            "targets": [],
        },
        "promotion_proof_hooks": _promotion_proof_hooks(project_root, version=feature_version, feature=feature_name),
        "source": {
            "stage": "qa",
            "run_id": run_id,
            "status": str(status.get("status") or ""),
            "continue_decision": continue_decision,
        },
        "updated_at": now_iso(),
    }
    if next_route == "change_refreeze":
        payload["closure_state"] = "blocked"
        payload["scenario_discovery"] = scenario_payload
        payload["truth_recompile_gate"] = {
            "required": bool(scenario_payload.get("requires_truth_reopen")),
            "targets": list(DEFAULT_TRUTH_RECOMPILE_TARGETS) if scenario_payload.get("requires_truth_reopen") else [],
        }
    write_feature_automation_runtime(project_root, feature=feature_name, payload=payload)
    return payload


def record_implement_repair_round(
    project_root: Path,
    *,
    feature: str,
    accepted_fixes: list[str] | None = None,
    human_escalation: bool = False,
    outcome_ref: str = "",
) -> dict[str, Any]:
    previous = load_feature_automation_runtime(project_root, feature=feature)
    previous_register = previous.get("active_issue_register") if isinstance(previous.get("active_issue_register"), dict) else {}
    prior_fixes = previous_register.get("accepted_fixes") if isinstance(previous_register.get("accepted_fixes"), list) else []
    new_fixes = [str(item).strip() for item in (accepted_fixes or []) if str(item).strip()]
    accepted = list(dict.fromkeys([*prior_fixes, *new_fixes]))
    round_number = int(previous.get("round_number") or 0) + 1
    current_round_ref = str(outcome_ref or f"implement:round-{round_number}")
    next_route = "human" if human_escalation else "qa"
    terminal_signal = "implement_route_human_escalation" if human_escalation else "implement_exit_to_qa"
    closure_state = "human_escalation_required" if human_escalation else "active"
    payload = {
        **previous,
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "feature": str(previous.get("feature") or feature).strip() or str(feature).strip(),
        "feature_slug": feature_slug(str(previous.get("feature") or feature)),
        "closure_state": closure_state,
        "next_route": next_route,
        "terminal_signal": terminal_signal,
        "round_number": round_number,
        "previous_round_ref": str(previous.get("current_round_ref") or ""),
        "current_round_ref": current_round_ref,
        "human_takeover_required": human_escalation,
        "active_issue_register": {
            "unresolved_stop_reasons": list(previous_register.get("unresolved_stop_reasons") or []),
            "accepted_fixes": accepted,
            "targeted_rerun_hints": previous_register.get("targeted_rerun_hints") if isinstance(previous_register.get("targeted_rerun_hints"), dict) else {},
            "latest_ref": current_round_ref,
            "previous_round_ref": str(previous.get("current_round_ref") or ""),
        },
        "source": {
            "stage": "implement",
            "outcome_ref": current_round_ref,
        },
        "updated_at": now_iso(),
    }
    write_feature_automation_runtime(project_root, feature=str(previous.get("feature") or feature), payload=payload)
    return payload


def record_support_review_outcome(
    project_root: Path,
    *,
    feature: str,
    outcome: str,
    executor: str = "deep",
    reason: str = "",
    requirement_meaning_delta: bool = False,
    repeat_cap_reached: bool = False,
) -> dict[str, Any]:
    previous = load_feature_automation_runtime(project_root, feature=feature)
    feature_name = str(previous.get("feature") or feature).strip() or str(feature).strip()
    version = str(previous.get("version") or "")
    support_review = _support_review_payload(previous=previous, executor=executor, reason=reason or outcome)
    scenario_discovery = _scenario_discovery_payload(
        {
            "classification": "closure_supplement" if requirement_meaning_delta else "promotion_candidate",
            "requirement_meaning_delta": requirement_meaning_delta,
            "finding_count": 1 if requirement_meaning_delta else 0,
            "requires_truth_reopen": requirement_meaning_delta,
        }
    )
    next_route = "implement"
    terminal_signal = "support_review_deep_route_implement"
    closure_state = "blocked"
    truth_recompiled_pending = False
    truth_gate = {"required": False, "targets": []}
    human_takeover_required = False
    if repeat_cap_reached or str(outcome).strip() == "deep_repeat_cap_reached":
        next_route = "human"
        terminal_signal = "support_review_deep_repeat_cap_reached"
        closure_state = "human_escalation_required"
        human_takeover_required = True
        support_review = {
            **support_review,
            "required": False,
        }
    elif requirement_meaning_delta or str(outcome).strip() in {"deep_route_truth_refreeze", "support_review_deep_route_truth_refreeze"}:
        next_route = "change_refreeze"
        terminal_signal = "support_review_deep_route_truth_refreeze"
        closure_state = "blocked"
        truth_recompiled_pending = True
        truth_gate = {"required": True, "targets": list(DEFAULT_TRUTH_RECOMPILE_TARGETS)}
        support_review = {
            **support_review,
            "required": False,
        }
    else:
        terminal_signal = "deep_exit_no_truth_delta" if str(outcome).strip() == "deep_exit_no_truth_delta" else "support_review_deep_route_implement"
        support_review = {
            **support_review,
            "required": False,
        }
    payload = {
        **previous,
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "feature": feature_name,
        "feature_slug": feature_slug(feature_name),
        "closure_state": closure_state,
        "next_route": next_route,
        "terminal_signal": terminal_signal,
        "human_takeover_required": human_takeover_required,
        "support_review": support_review,
        "scenario_discovery": scenario_discovery,
        "truth_recompiled_pending": truth_recompiled_pending,
        "truth_recompile_gate": truth_gate,
        "promotion_proof_hooks": _promotion_proof_hooks(project_root, version=version, feature=feature_name),
        "source": {
            "stage": "support_review",
            "executor": str(executor or "deep"),
            "outcome": str(outcome).strip(),
        },
        "updated_at": now_iso(),
    }
    write_feature_automation_runtime(project_root, feature=feature_name, payload=payload)
    return payload


def set_truth_recompile_barrier(
    project_root: Path,
    *,
    feature: str,
    pending: bool,
    targets: list[str] | None = None,
) -> dict[str, Any]:
    previous = load_feature_automation_runtime(project_root, feature=feature)
    feature_name = str(previous.get("feature") or feature).strip() or str(feature).strip()
    normalized_targets = [str(item).strip() for item in (targets or DEFAULT_TRUTH_RECOMPILE_TARGETS) if str(item).strip()]
    payload = {
        **previous,
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "feature": feature_name,
        "feature_slug": feature_slug(feature_name),
        "truth_recompiled_pending": bool(pending),
        "truth_recompile_gate": {
            "required": bool(pending),
            "targets": normalized_targets if pending else [],
        },
        "updated_at": now_iso(),
    }
    if pending:
        payload["closure_state"] = "blocked"
        payload["next_route"] = "change_refreeze"
        payload["terminal_signal"] = "truth_recompile_pending"
    write_feature_automation_runtime(project_root, feature=feature_name, payload=payload)
    return payload


def bounded_runtime_round_summary(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    payload = runtime_payload if isinstance(runtime_payload, dict) else {}
    return {
        "feature": str(payload.get("feature") or ""),
        "round_number": int(payload.get("round_number") or 0),
        "closure_state": str(payload.get("closure_state") or "active"),
        "next_route": str(payload.get("next_route") or "qa"),
        "terminal_signal": str(payload.get("terminal_signal") or ""),
        "human_takeover_required": bool(payload.get("human_takeover_required", False)),
        "current_round_ref": str(payload.get("current_round_ref") or ""),
        "previous_round_ref": str(payload.get("previous_round_ref") or ""),
        "truth_recompiled_pending": bool(payload.get("truth_recompiled_pending", False)),
        "support_review_required": bool(((payload.get("support_review") if isinstance(payload.get("support_review"), dict) else {}) or {}).get("required", False)),
        "scenario_discovery_classification": str(((payload.get("scenario_discovery") if isinstance(payload.get("scenario_discovery"), dict) else {}) or {}).get("classification") or ""),
    }
