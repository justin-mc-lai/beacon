"""State helpers for Beacon Ralph closure control."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.control_plane import record_stage_failure, record_stage_success
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version
from beacon.utils.ralph_boundary import sanitize_ralph_state


def ralph_state_path(project_root: Path, *, feature: str) -> Path:
    return project_root / ".beacon" / "ralph" / f"{feature_slug(feature)}.json"


def load_ralph_state(project_root: Path, *, feature: str) -> dict[str, Any]:
    payload = read_json(ralph_state_path(project_root, feature=feature), {})
    return payload if isinstance(payload, dict) else {}


def save_ralph_state(project_root: Path, *, feature: str, payload: dict[str, Any]) -> Path:
    path = ralph_state_path(project_root, feature=feature)
    cleaned = sanitize_ralph_state(payload if isinstance(payload, dict) else {})
    write_json(path, cleaned)
    return path


def initialize_ralph_state(
    project_root: Path,
    *,
    feature: str,
    version: str,
    run_id: str,
    host_runtime: str,
    runner: str,
) -> dict[str, Any]:
    existing = load_ralph_state(project_root, feature=feature)
    rounds = existing.get("rounds") if isinstance(existing.get("rounds"), list) else []
    payload = {
        "schema_version": "1.1",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "mode": "ralph",
        "active_run_id": run_id,
        "host_runtime": host_runtime,
        "runner": runner,
        "phase": "preflight",
        "status": "active",
        "round_count": len(rounds),
        "failure_streak": int(existing.get("failure_streak", 0) or 0),
        "no_delta_streak": int(existing.get("no_delta_streak", 0) or 0),
        "stop_state": "",
        "current_blocker": "",
        "next_action": "",
        "recommended_command": "",
        "last_round_ref": "",
        "rounds": rounds,
        "updated_at": now_iso(),
    }
    save_ralph_state(project_root, feature=feature, payload=payload)
    return payload


def append_ralph_round(
    project_root: Path,
    *,
    feature: str,
    round_payload: dict[str, Any],
) -> dict[str, Any]:
    state = load_ralph_state(project_root, feature=feature)
    rounds = state.get("rounds") if isinstance(state.get("rounds"), list) else []
    rounds.append(round_payload)
    state["rounds"] = rounds
    state["round_count"] = len(rounds)
    if str(round_payload.get("round_ref", "") or "").strip():
        state["last_round_ref"] = str(round_payload.get("round_ref", "") or "")
    state["updated_at"] = now_iso()
    save_ralph_state(project_root, feature=feature, payload=state)
    return state


def _scorecard_no_delta(feature_scorecard: dict[str, Any]) -> bool:
    if not feature_scorecard:
        return True
    coverage_delta = feature_scorecard.get("coverage_delta")
    if isinstance(coverage_delta, dict):
        return not any(bool(value) for value in coverage_delta.values())
    for key in (
        "new_findings_count",
        "new_boundary_count",
        "new_structure_inference_count",
        "coverage_delta_count",
    ):
        if int(feature_scorecard.get(key, 0) or 0) > 0:
            return False
    return False


def mark_ralph_handoff_required(
    project_root: Path,
    *,
    feature: str,
    run_id: str,
    request_markdown: str,
) -> dict[str, Any]:
    state = load_ralph_state(project_root, feature=feature)
    state.update(
        {
            "active_run_id": run_id,
            "phase": "waiting_for_handoff",
            "status": "waiting_for_handoff",
            "stop_state": "human_blocked",
            "current_blocker": "handoff_required",
            "next_action": "handoff_execute",
            "recommended_command": request_markdown,
            "updated_at": now_iso(),
        }
    )
    save_ralph_state(project_root, feature=feature, payload=state)
    record_stage_failure(
        project_root,
        run_id=run_id,
        stage="ralph",
        attempted_strategy="handoff_required",
        reason_code="handoff_required",
        current_blocker="ralph waiting for handoff execution",
        recommended_command=request_markdown,
    )
    return state


def _normalize_ralph_action(raw_action: str, raw_command: str, *, review_gate_ready: bool, continue_decision: str) -> str:
    action = str(raw_action or "").strip().lower()
    command = str(raw_command or "").strip().lower()
    if continue_decision == "ready_for_release":
        return "release" if review_gate_ready else "review_quality"
    if action == "implement":
        return "implement"
    if action in {"qa-run", "qa-repair"}:
        return "qa"
    if action == "verify-run":
        return "verify"
    if action == "test-case-create":
        return "test-case"
    if "beacon qa " in command:
        return "qa"
    if "beacon verify " in command:
        return "verify"
    if "beacon test-case " in command:
        return "test-case"
    if "beacon review quality" in command:
        return "review_quality"
    if "beacon gate check release" in command or "beacon release check" in command:
        return "release"
    return "human_review"


def _requirement_gate_handoff(payload: dict[str, Any]) -> tuple[str, str, str]:
    if not isinstance(payload, dict) or not payload:
        return "", "", ""
    requirement_gate = (
        payload.get("requirement_completeness_gate")
        if isinstance(payload.get("requirement_completeness_gate"), dict)
        else payload.get("requirement_completeness")
        if isinstance(payload.get("requirement_completeness"), dict)
        else {}
    )
    if not isinstance(requirement_gate, dict) or not requirement_gate:
        return "", "", ""
    if not bool(requirement_gate.get("blocked")) and str(requirement_gate.get("status") or "").strip().lower() != "blocked":
        return "", "", ""
    handoff = requirement_gate.get("human_loop_handoff") if isinstance(requirement_gate.get("human_loop_handoff"), dict) else {}
    reason = str(requirement_gate.get("reason_code") or "requirement_completeness_blocked").strip()
    command = str(handoff.get("recommended_command") or requirement_gate.get("recommended_command") or "").strip()
    next_action = _normalize_ralph_action(
        str(handoff.get("action") or ""),
        command,
        review_gate_ready=False,
        continue_decision=reason,
    )
    if next_action == "":
        next_action = "human_review"
    return reason, next_action, command


def _canonical_review_quality_payload(project_root: Path, *, feature: str, review_quality: dict[str, Any] | None) -> dict[str, Any]:
    payload = review_quality.get("payload") if isinstance(review_quality, dict) and isinstance(review_quality.get("payload"), dict) else {}
    if bool(payload.get("gate_ready", False)):
        return payload
    candidate_paths: list[Path] = []
    review_paths = review_quality.get("paths") if isinstance(review_quality, dict) and isinstance(review_quality.get("paths"), dict) else {}
    json_path = str(review_paths.get("json", "") or "").strip()
    if json_path:
        path = Path(json_path)
        candidate_paths.append(path if path.is_absolute() else project_root / path)
    machine_json = review_quality.get("artifacts", {}).get("json") if isinstance(review_quality, dict) and isinstance(review_quality.get("artifacts"), dict) else ""
    if str(machine_json or "").strip():
        path = Path(str(machine_json).strip())
        candidate_paths.append(path if path.is_absolute() else project_root / path)
    feature_slug_value = feature_slug(feature)
    docs_root = project_root / "docs" / "beacon"
    if docs_root.exists():
        for version_dir in sorted(docs_root.iterdir()):
            if not version_dir.is_dir():
                continue
            version_name = normalize_version(version_dir.name)
            if not version_name:
                continue
            candidate_paths.append(version_dir / ".machine" / "execution" / f"review-quality-{feature_slug_value}.json")
    for path in candidate_paths:
        loaded = read_json(path, {})
        if isinstance(loaded, dict) and loaded:
            return loaded
    return payload if isinstance(payload, dict) else {}


def finalize_ralph_state(
    project_root: Path,
    *,
    feature: str,
    run_id: str,
    review_quality: dict[str, Any] | None,
    auto_qa: dict[str, Any] | None,
    gate_release: dict[str, Any] | None,
) -> dict[str, Any]:
    state = load_ralph_state(project_root, feature=feature)
    review_payload = _canonical_review_quality_payload(project_root, feature=feature, review_quality=review_quality)
    qa_payload = auto_qa.get("payload") if isinstance(auto_qa, dict) and isinstance(auto_qa.get("payload"), dict) else {}
    feature_scorecard = qa_payload.get("feature_scorecard") if isinstance(qa_payload.get("feature_scorecard"), dict) else {}
    continue_decision = str(feature_scorecard.get("continue_decision", "") or "").strip()
    review_gate_ready = bool(review_payload.get("gate_ready", False))
    gate_payload = gate_release.get("payload") if isinstance(gate_release, dict) and isinstance(gate_release.get("payload"), dict) else {}
    gate_pass = str(gate_payload.get("status", "") or "").strip().lower() == "pass"
    qa_requirement_reason, qa_requirement_next_action, qa_requirement_command = _requirement_gate_handoff(qa_payload)
    release_requirement_reason, release_requirement_next_action, release_requirement_command = _requirement_gate_handoff(gate_payload)
    prior_failure_streak = int(state.get("failure_streak", 0) or 0)
    prior_no_delta_streak = int(state.get("no_delta_streak", 0) or 0)
    no_delta_streak = prior_no_delta_streak + 1 if _scorecard_no_delta(feature_scorecard) else 0

    stop_state = "human_blocked"
    next_action = ""
    recommended_command = ""
    current_blocker = ""
    status = "completed"

    if continue_decision == "ready_for_release" and review_gate_ready and gate_pass:
        stop_state = "release_ready"
        next_action = "release"
        recommended_command = f"beacon release check {state.get('version', '')} --project {project_root}"
        current_blocker = ""
        failure_streak = 0
        record_stage_success(project_root, run_id=run_id, stage="ralph")
    else:
        rounds = auto_qa.get("history") if isinstance(auto_qa, dict) and isinstance(auto_qa.get("history"), list) else []
        max_rounds = int(auto_qa.get("max_rounds", 0) or 0) if isinstance(auto_qa, dict) else 0
        repair_handoff = feature_scorecard.get("repair_handoff") if isinstance(feature_scorecard.get("repair_handoff"), dict) else {}
        if max_rounds and len([item for item in rounds if isinstance(item, dict) and str(item.get("step", "")) == "qa-run"]) >= max_rounds:
            stop_state = "budget_exhausted"
            next_action = "human_review"
            current_blocker = "ralph reached max rounds without release_ready"
            failure_streak = prior_failure_streak + 1
        elif qa_requirement_reason:
            stop_state = "human_blocked"
            next_action = qa_requirement_next_action or "human_review"
            recommended_command = qa_requirement_command
            current_blocker = qa_requirement_reason
            failure_streak = prior_failure_streak + 1
        elif continue_decision == "ready_for_release" and review_gate_ready and not gate_pass:
            if release_requirement_reason:
                stop_state = "human_blocked"
                next_action = release_requirement_next_action or "human_review"
                recommended_command = release_requirement_command
                current_blocker = release_requirement_reason
            else:
                stop_state = "human_blocked"
                next_action = "release"
                recommended_command = f"beacon gate check release --project-root {project_root} --version {state.get('version', '')}"
                current_blocker = "gate_release_blocked"
            failure_streak = prior_failure_streak + 1
        elif continue_decision == "ready_for_release" and not review_gate_ready:
            stop_state = "human_blocked"
            next_action = "review_quality"
            recommended_command = f"beacon review quality \"{feature}\" --project {project_root} --version {state.get('version', '')}"
            current_blocker = "review_quality_blocked"
            failure_streak = prior_failure_streak + 1
        else:
            stop_state = "human_blocked"
            recommended_command = str(repair_handoff.get("command", "") or "")
            next_action = _normalize_ralph_action(
                str(repair_handoff.get("action", "") or ""),
                recommended_command,
                review_gate_ready=review_gate_ready,
                continue_decision=continue_decision,
            )
            current_blocker = str(repair_handoff.get("reason", "") or continue_decision or "ralph requires another round")
            failure_streak = prior_failure_streak + 1
        record_stage_failure(
            project_root,
            run_id=run_id,
            stage="ralph",
            attempted_strategy="qa_closure",
            reason_code=continue_decision or "ralph_not_release_ready",
            current_blocker=current_blocker or "ralph did not reach release_ready",
            recommended_command=recommended_command,
        )

    state.update(
        {
            "active_run_id": run_id,
            "phase": "completed",
            "status": status,
            "stop_state": stop_state,
            "current_blocker": current_blocker,
            "next_action": next_action,
            "recommended_command": recommended_command,
            "continue_decision": continue_decision,
            "review_gate_ready": review_gate_ready,
            "gate_release_status": str(gate_payload.get("status", "") or ""),
            "failure_streak": failure_streak,
            "no_delta_streak": no_delta_streak,
            "round_count": len(state.get("rounds", []) if isinstance(state.get("rounds"), list) else []),
            "updated_at": now_iso(),
        }
    )
    save_ralph_state(project_root, feature=feature, payload=state)
    return state
