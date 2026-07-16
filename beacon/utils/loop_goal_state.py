"""Loop goal orchestrator state — file-system state for cross-harness sequencing.

Manages the state file at .beacon/state/loop-goal/<run_id>.json that tracks
the current stage, stage history, and outputs of a loop goal run.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "loop-goal-state.v1"

VALID_STAGES = frozenset({
    "idle",
    "governance_precheck",
    "truth_routing",
    "review_routing",
    "standard_execution_precheck",
    "implement_routing",
    "qa_routing",
    "qa_deep_routing",
    "drift_routing",
    "release_gate",
    "done",
    "error_recovery",
})

MAX_REPAIR_LOOPS = 3

RELEASE_HUMAN_GATE_STAGES = frozenset({"release_gate"})
# R6: only P0 blocks by severity. Standalone P1 is advisory continue.
# Intent / scope / parity still stop via user_decision_required or drift routes.
BLOCKING_REVIEW_SEVERITIES = frozenset({"P0"})
DRIFT_REVIEW_ROUTES = frozenset({
    "beacon-gen-truth",
    "beacon-gen-change",
    "beacon-gen-refreeze",
})
IMPLEMENT_READY_REVIEW_ROUTES = frozenset({
    "",
    "continue_delivery",
    "beacon-gen-implement",
    "beacon-pln-friction",
    "beacon-eval-qa",
})
ADVISORY_CONTINUE_SEVERITIES = frozenset({"P1", "P2", "P3"})
REQUIRED_STANDARD_EXECUTION_CHECKS = (
    "truth_map_verify",
    "verify_materials_strict",
    "git_diff_check",
    "branch_governance_verify",
    "workspace_admission",
)
PASSING_CHECK_STATUSES = frozenset({"pass", "passed", "ok", "up_to_date"})

RESUME_SHORT_UTTERANCES = frozenset({"继续", "continue", "resume", "go"})
HOST_INTERRUPT_REASON = "host_turn_interrupted"


def required_standard_execution_checks(version: str) -> tuple[str, ...]:
    from beacon.utils.git_scope_graph import topology_gate_required

    checks = list(REQUIRED_STANDARD_EXECUTION_CHECKS)
    if topology_gate_required(version):
        checks.append("topology_gate")
    return tuple(checks)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _state_dir(project_root: Path) -> Path:
    return project_root.expanduser().resolve() / ".beacon" / "state" / "loop-goal"


def _state_path(project_root: Path, run_id: str) -> Path:
    return _state_dir(project_root) / f"{run_id}.json"


def init(
    project_root: Path,
    *,
    version: str,
    feature: str,
    utterance: str,
    auto_decide: bool = True,
    human_gate_overrides: list[str] | None = None,
) -> dict[str, Any]:
    """Initialize a new loop goal state file.

    Returns the initial state dict.
    """
    root = project_root.expanduser().resolve()
    run_id = f"lg-{uuid.uuid4().hex[:12]}"
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "version": version,
        "feature": feature,
        "utterance": utterance,
        "current_stage": "idle",
        "auto_decide": auto_decide,
        "human_gate_overrides": human_gate_overrides or [],
        "stage_history": [
            {"stage": "idle", "status": "enter", "at": _now_iso()},
        ],
        "outputs": {
            "truth_frozen": False,
            "planner_review_id": None,
            "planner_review_artifact_ref": "",
            "planner_review_recommended_route": "",
            "planner_review_user_decision_required": False,
            "planner_review_highest_severity": "",
            "planner_review_finding_count": 0,
            "standard_execution_flow_status": "not_checked",
            "truth_baseline_commit": None,
            "canonical_refreeze_committed": False,
            "feature_worktree_reconciled": False,
            "stale_feature_refreeze_quarantine_ref": "",
            "verification_bundle_ref": "",
            "workspace_admission_ref": "",
            "tests_pass": False,
            "qa_verdict": None,
            "release_verdict": None,
            "planner_review_continue_audit": {},
            "latest_utterance": utterance,
            "intent_forks": [],
            "decision_cache": [],
            "topology_gate_status": "not_checked",
            "topology_gate_ref": "",
            "last_substep": "",
            "loop_execution_mode": "host_skill",
            "human_stop_metrics": {
                "human_stops_per_run": 0,
                "stop_reason_counts": {},
                "p1_continue_count": 0,
                "pseudo_stall_flag": False,
            },
        },
        "repair_loop_count": 0,
        "stop_when": [],
    }
    _state_dir(root).mkdir(parents=True, exist_ok=True)
    _state_path(root, run_id).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return state


def read_state(project_root: Path, *, run_id: str) -> dict[str, Any]:
    """Read the current state file."""
    path = _state_path(project_root, run_id)
    if not path.is_file():
        return {"status": "blocked", "reason_code": "state_not_found", "run_id": run_id}
    return json.loads(path.read_text(encoding="utf-8"))


def transition(
    project_root: Path,
    *,
    run_id: str,
    to_stage: str,
    status: str = "enter",
    outputs: dict[str, Any] | None = None,
    stop_when: list[str] | None = None,
    release_confirmed: bool = False,
) -> dict[str, Any]:
    """Transition to a new stage, appending to stage_history.

    Validates the target stage and checks stop-when conditions.

    Mechanically enforces the release human gate: leaving ``release_gate`` for
    ``done`` is refused unless ``release_confirmed=True`` (only
    :func:`check_release_gate` sets this). This makes UD-LG-004/AC-007 a
    structural invariant rather than a skill convention.
    """
    root = project_root.expanduser().resolve()
    if to_stage not in VALID_STAGES:
        return {
            "status": "blocked",
            "reason_code": "invalid_stage",
            "findings": [{"message": f"invalid stage: {to_stage}"}],
        }

    state = read_state(root, run_id=run_id)
    if state.get("status") == "blocked":
        return state

    # Check stop-when conditions from PREVIOUS transitions (not the current one)
    existing_stop_when = state.get("stop_when", [])
    if existing_stop_when:
        return {
            "status": "stopped",
            "reason_code": "stop_when_satisfied",
            "current_stage": state.get("current_stage"),
            "stop_when": existing_stop_when,
            "findings": [{"message": "stop-when condition satisfied"}],
        }

    # Merge any new stop_when into the state for FUTURE transitions
    current_stop_when = list(existing_stop_when)
    if stop_when:
        current_stop_when = list(set(current_stop_when + stop_when))

    # Mechanical release human gate: release_gate -> done is refused without
    # explicit human confirmation, regardless of auto_decide.
    if (
        to_stage == "done"
        and state.get("current_stage") in RELEASE_HUMAN_GATE_STAGES
        and not release_confirmed
    ):
        return {
            "status": "blocked",
            "reason_code": "release_requires_human_confirmation",
            "current_stage": state.get("current_stage"),
            "findings": [
                {"message": "release gate requires human confirmation before done"}
            ],
        }

    # Update state
    state["current_stage"] = to_stage
    state["stop_when"] = current_stop_when
    state["stage_history"].append({
        "stage": to_stage,
        "status": status,
        "at": _now_iso(),
    })
    if outputs:
        state["outputs"].update(outputs)

    _state_path(root, run_id).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"status": "pass", "current_stage": to_stage, "run_id": run_id}


def check_stop_when(project_root: Path, *, run_id: str) -> dict[str, Any]:
    """Check if any stop-when condition is satisfied."""
    state = read_state(project_root, run_id=run_id)
    if state.get("status") == "blocked":
        return state
    stop_when = state.get("stop_when", [])
    if stop_when:
        return {
            "status": "stopped",
            "reason_code": "stop_when_satisfied",
            "stop_when": stop_when,
        }
    return {"status": "pass", "stop_when": []}


def check_release_gate(project_root: Path, *, run_id: str, human_confirmed: bool = False) -> dict[str, Any]:
    """Check if the release gate can be passed.

    Release ALWAYS requires human confirmation, regardless of auto_decide.
    """
    state = read_state(project_root, run_id=run_id)
    if state.get("status") == "blocked":
        return state

    if state.get("current_stage") != "release_gate":
        return {
            "status": "blocked",
            "reason_code": "not_at_release_gate",
            "current_stage": state.get("current_stage"),
        }

    if not human_confirmed:
        return {
            "status": "blocked",
            "reason_code": "release_requires_human_confirmation",
            "findings": [{"message": "release gate requires human confirmation"}],
        }

    # Human confirmed — allow transition to done (release_confirmed unlocks the gate)
    return transition(
        project_root,
        run_id=run_id,
        to_stage="done",
        status="release_confirmed",
        release_confirmed=True,
    )


def increment_repair_loop(project_root: Path, *, run_id: str) -> dict[str, Any]:
    """Increment repair loop count. Returns blocked if max exceeded."""
    root = project_root.expanduser().resolve()
    state = read_state(root, run_id=run_id)
    if state.get("status") == "blocked":
        return state

    count = int(state.get("repair_loop_count", 0)) + 1
    state["repair_loop_count"] = count

    if count > MAX_REPAIR_LOOPS:
        state["current_stage"] = "error_recovery"
        state["stage_history"].append({
            "stage": "error_recovery",
            "status": "max_repair_loops_exceeded",
            "at": _now_iso(),
        })
        _state_path(root, run_id).write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return {
            "status": "blocked",
            "reason_code": "max_repair_loops_exceeded",
            "repair_loop_count": count,
            "max": MAX_REPAIR_LOOPS,
            "recommended_route": "beacon-gov-debug",
        }

    _state_path(root, run_id).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"status": "pass", "repair_loop_count": count, "max": MAX_REPAIR_LOOPS}


def _review_artifact_ref(artifact: dict[str, Any]) -> str:
    evidence_paths = artifact.get("evidence_paths")
    if isinstance(evidence_paths, dict):
        runtime_ref = str(evidence_paths.get("runtime") or "").strip()
        if runtime_ref:
            return runtime_ref
    for lane in artifact.get("reviewer_lanes") or []:
        if isinstance(lane, dict):
            runtime_ref = str(lane.get("runtime_evidence_ref") or "").strip()
            if runtime_ref:
                return runtime_ref
    return ""


def _review_findings(artifact: dict[str, Any], synthesis: dict[str, Any]) -> list[dict[str, Any]]:
    findings = artifact.get("findings")
    if isinstance(findings, list):
        return [item for item in findings if isinstance(item, dict)]
    merged = synthesis.get("merged_findings")
    if isinstance(merged, list):
        return [item for item in merged if isinstance(item, dict)]
    return []


def _highest_review_severity(findings: list[dict[str, Any]], synthesis: dict[str, Any]) -> str:
    declared = str(synthesis.get("highest_severity") or "").upper()
    if declared:
        return declared
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    highest = ""
    for finding in findings:
        severity = str(finding.get("severity") or "").upper()
        if severity in order and (not highest or order[severity] < order[highest]):
            highest = severity
    return highest


def _default_human_stop_metrics() -> dict[str, Any]:
    return {
        "human_stops_per_run": 0,
        "stop_reason_counts": {},
        "p1_continue_count": 0,
        "pseudo_stall_flag": False,
    }


def _ensure_human_stop_metrics(outputs: dict[str, Any]) -> dict[str, Any]:
    metrics = outputs.get("human_stop_metrics")
    if not isinstance(metrics, dict):
        metrics = _default_human_stop_metrics()
    else:
        metrics = {
            **_default_human_stop_metrics(),
            **metrics,
            "stop_reason_counts": dict(metrics.get("stop_reason_counts") or {}),
        }
    outputs["human_stop_metrics"] = metrics
    return metrics


def _bump_stop_reason(metrics: dict[str, Any], reason_code: str) -> None:
    metrics["human_stops_per_run"] = int(metrics.get("human_stops_per_run") or 0) + 1
    counts = dict(metrics.get("stop_reason_counts") or {})
    counts[reason_code] = int(counts.get(reason_code) or 0) + 1
    metrics["stop_reason_counts"] = counts


def _review_packet_incomplete(
    review_artifact: dict[str, Any],
    *,
    synthesis: dict[str, Any],
    findings: list[Any],
    recommended_route: str,
) -> bool:
    """Fail-closed when the decision packet lacks minimum routing fields."""
    review_id = review_artifact.get("review_id") or review_artifact.get("id")
    artifact_ref = _review_artifact_ref(review_artifact)
    has_route = bool(recommended_route)
    has_findings = bool(findings)
    has_synthesis_marker = bool(
        synthesis.get("highest_severity")
        or synthesis.get("finding_count") is not None
        or "user_decision_required" in synthesis
        or "recommended_route" in synthesis
    )
    # Empty / placeholder packets cannot authorize implement continue.
    if not review_id and not artifact_ref and not has_route and not has_findings:
        return True
    if not has_route and not has_findings and not has_synthesis_marker:
        return True
    return False



def record_intent_fork(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    utterance_slice: str,
    decision: str,
    reason_code: str = "",
) -> dict[str, Any]:
    """Append an intent fork record at a routing decision point (R7)."""
    root = project_root.expanduser().resolve()
    state = read_state(root, run_id=run_id)
    if state.get("status") == "blocked":
        return state
    outputs = dict(state.get("outputs") or {})
    forks = list(outputs.get("intent_forks") or [])
    forks.append(
        {
            "stage": stage,
            "utterance_slice": utterance_slice,
            "decision": decision,
            "reason_code": reason_code,
            "at": _now_iso(),
        }
    )
    outputs["intent_forks"] = forks
    if utterance_slice:
        outputs["latest_utterance"] = utterance_slice
    state["outputs"] = outputs
    state["outputs"]["last_substep"] = stage
    _state_path(root, run_id).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "pass", "run_id": run_id, "outputs": outputs}


def record_host_interrupt(
    project_root: Path,
    *,
    run_id: str,
    substep: str = "",
) -> dict[str, Any]:
    """Mark a host turn interrupt without treating it as stage_blocked (R7)."""
    root = project_root.expanduser().resolve()
    state = read_state(root, run_id=run_id)
    if state.get("status") == "blocked":
        return state
    outputs = dict(state.get("outputs") or {})
    outputs["last_substep"] = substep or str(state.get("current_stage") or "")
    metrics = _ensure_human_stop_metrics(outputs)
    metrics["human_stops_per_run"] = int(metrics.get("human_stops_per_run") or 0) + 1
    counts = dict(metrics.get("stop_reason_counts") or {})
    counts[HOST_INTERRUPT_REASON] = int(counts.get(HOST_INTERRUPT_REASON) or 0) + 1
    metrics["stop_reason_counts"] = counts
    outputs["human_stop_metrics"] = metrics
    state["outputs"] = outputs
    _state_path(root, run_id).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": "pass",
        "reason_code": HOST_INTERRUPT_REASON,
        "resume_action": "replay_substep",
        "run_id": run_id,
        "last_substep": outputs["last_substep"],
    }


def _decision_cache_hit(outputs: dict[str, Any], decision_key: str) -> bool:
    cache = outputs.get("decision_cache") or []
    return any(
        isinstance(item, dict) and str(item.get("key") or "") == decision_key
        for item in cache
    )


def record_user_decision(
    project_root: Path,
    *,
    run_id: str,
    decision_key: str,
    decision_value: str,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    state = read_state(root, run_id=run_id)
    if state.get("status") == "blocked":
        return state
    outputs = dict(state.get("outputs") or {})
    cache = list(outputs.get("decision_cache") or [])
    cache.append({"key": decision_key, "value": decision_value, "at": _now_iso()})
    outputs["decision_cache"] = cache
    state["outputs"] = outputs
    _state_path(root, run_id).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "pass", "run_id": run_id, "outputs": outputs}

def record_review_decision(
    project_root: Path,
    *,
    run_id: str,
    review_artifact: dict[str, Any],
) -> dict[str, Any]:
    """Record a planner-review decision packet and route fail-closed (R6).

    Blocking stops only for:
    - P0 severity
    - ``user_decision_required=true``
    - drift routes (truth / change / refreeze)
    - incomplete or unhandled packets

    Standalone P1/P2/P3 with an implement-ready route continues to
    ``standard_execution_precheck`` and records a continue audit.
    """
    root = project_root.expanduser().resolve()
    state = read_state(root, run_id=run_id)
    if state.get("status") == "blocked":
        return state

    if not isinstance(review_artifact, dict) or not review_artifact:
        return {
            "status": "blocked",
            "reason_code": "planner_review_packet_incomplete",
            "current_stage": "error_recovery",
            "run_id": run_id,
            "recommended_route": "",
            "outputs": {},
        }

    synthesis = review_artifact.get("synthesis")
    if not isinstance(synthesis, dict):
        synthesis = {}
    findings = _review_findings(review_artifact, synthesis)
    recommended_route = str(
        synthesis.get("recommended_route")
        or review_artifact.get("recommended_route")
        or ""
    ).strip()
    user_decision_required = bool(
        synthesis.get("user_decision_required")
        or review_artifact.get("user_decision_required")
    )
    highest_severity = _highest_review_severity(findings, synthesis)
    outputs = dict(state.get("outputs") or {})
    metrics = _ensure_human_stop_metrics(outputs)
    packet = {
        "planner_review_id": review_artifact.get("review_id"),
        "planner_review_artifact_ref": _review_artifact_ref(review_artifact),
        "planner_review_recommended_route": recommended_route,
        "planner_review_user_decision_required": user_decision_required,
        "planner_review_highest_severity": highest_severity,
        "planner_review_finding_count": int(
            synthesis.get("finding_count")
            if synthesis.get("finding_count") is not None
            else len(findings)
        ),
    }

    continue_audit: dict[str, Any] = {}
    next_stage = "error_recovery"
    reason_code = ""
    overrides = {
        str(item).strip().lower()
        for item in (state.get("human_gate_overrides") or [])
    }
    # Opt-out: auto_decide=false or --human-gate p1 elevates standalone P1 to a stop.
    force_p1_human_gate = (not bool(state.get("auto_decide", True))) or bool(
        overrides.intersection({"p1", "planner_review_p1", "review_p1", "review"})
    )

    if _review_packet_incomplete(
        review_artifact,
        synthesis=synthesis,
        findings=findings,
        recommended_route=recommended_route,
    ):
        next_stage = "error_recovery"
        reason_code = "planner_review_packet_incomplete"
    elif recommended_route in DRIFT_REVIEW_ROUTES:
        next_stage = "drift_routing"
        reason_code = f"planner_review_route_{recommended_route.replace('-', '_')}"
    elif user_decision_required and not _decision_cache_hit(outputs, "planner_review_user_decision"):
        next_stage = "error_recovery"
        reason_code = "planner_review_user_decision_required"
    elif highest_severity in BLOCKING_REVIEW_SEVERITIES:
        next_stage = "error_recovery"
        reason_code = "planner_review_blocking_finding"
    elif (
        highest_severity == "P1"
        and force_p1_human_gate
        and recommended_route in IMPLEMENT_READY_REVIEW_ROUTES
    ):
        next_stage = "error_recovery"
        reason_code = "planner_review_human_gate_p1"
    elif recommended_route in IMPLEMENT_READY_REVIEW_ROUTES:
        next_stage = "standard_execution_precheck"
        reason_code = ""
        if highest_severity in ADVISORY_CONTINUE_SEVERITIES:
            continue_audit = {
                "continued_with_advisory": True,
                "continued_severity": highest_severity,
                "blocking_reason_code": "",
                "recommended_route": recommended_route or "continue_delivery",
            }
            metrics["p1_continue_count"] = int(metrics.get("p1_continue_count") or 0) + (
                1 if highest_severity == "P1" else 0
            )
            # Non-P1 advisory still records audit without inflating p1 counter.
            if highest_severity != "P1":
                continue_audit["advisory_only"] = True
    else:
        next_stage = "error_recovery"
        reason_code = "planner_review_route_unhandled"

    if reason_code:
        _bump_stop_reason(metrics, reason_code)

    packet["planner_review_continue_audit"] = continue_audit
    packet["human_stop_metrics"] = metrics
    outputs.update(packet)
    state["outputs"] = outputs
    state["current_stage"] = next_stage
    state["stage_history"].append({
        "stage": next_stage,
        "status": "review_decision_packet",
        "at": _now_iso(),
        "recommended_route": recommended_route,
        "reason_code": reason_code,
        "continued_with_advisory": bool(continue_audit.get("continued_with_advisory")),
    })
    _state_path(root, run_id).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return {
        "status": "blocked" if reason_code else "pass",
        "reason_code": reason_code,
        "current_stage": next_stage,
        "run_id": run_id,
        "recommended_route": recommended_route,
        "outputs": packet,
        "next_skill": get_skill_for_stage(next_stage),
    }


def _check_passed(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in PASSING_CHECK_STATUSES
    if isinstance(value, dict):
        status = value.get("status")
        if isinstance(status, str):
            return status.strip().lower() in PASSING_CHECK_STATUSES
        if status is True:
            return True
    return False


def _normalise_verification_bundle(bundle: dict[str, Any] | None, *, version: str = "") -> dict[str, Any]:
    if not isinstance(bundle, dict):
        return {}
    keys = required_standard_execution_checks(version) if version else REQUIRED_STANDARD_EXECUTION_CHECKS
    return {key: bundle.get(key) for key in keys if key in bundle}


def _default_verification_bundle_ref(run_id: str) -> str:
    return f".beacon/state/loop-goal/{run_id}.verification-bundle.json"


def _write_verification_bundle(
    project_root: Path,
    *,
    run_id: str,
    bundle: dict[str, Any],
    verification_bundle_ref: str,
    cli_owned: bool = False,
    produced_by: str = "",
) -> str:
    ref = verification_bundle_ref.strip() or _default_verification_bundle_ref(run_id)
    path = Path(ref)
    if not path.is_absolute():
        path = project_root.expanduser().resolve() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, Any] = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing = loaded
        except Exception:  # noqa: BLE001
            existing = {}
    payload = {
        "schema_version": "loop-goal-standard-execution-bundle.v1",
        "run_id": run_id,
        "checks": bundle,
        "required_checks": list(REQUIRED_STANDARD_EXECUTION_CHECKS),
        "updated_at": _now_iso(),
        "cli_owned": bool(cli_owned or existing.get("cli_owned")),
        "produced_by": str(
            produced_by
            or existing.get("produced_by")
            or ("beacon.status.standard-execution-precheck" if cli_owned else "")
        ),
        "verification_bundle": existing.get("verification_bundle") or bundle,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return ref


def _standard_execution_block(
    project_root: Path,
    *,
    run_id: str,
    state: dict[str, Any],
    outputs: dict[str, Any],
    reason_code: str,
) -> dict[str, Any]:
    state["outputs"].update(outputs)
    state["outputs"]["standard_execution_flow_status"] = "blocked"
    state["current_stage"] = "error_recovery"
    state["stage_history"].append({
        "stage": "error_recovery",
        "status": f"blocked:{reason_code}",
        "at": _now_iso(),
        "reason_code": reason_code,
    })
    _state_path(project_root, run_id).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "status": "blocked",
        "reason_code": reason_code,
        "current_stage": "error_recovery",
        "recommended_route": "beacon-gov-debug",
        "run_id": run_id,
        "outputs": state["outputs"],
    }


def record_standard_execution_precheck(
    project_root: Path,
    *,
    run_id: str,
    precheck: dict[str, Any],
) -> dict[str, Any]:
    """Record Standard Execution Flow admission and route fail-closed.

    This helper consumes deterministic preflight results produced by branch
    governance, material verification, diff checks, and workspace admission.
    It does not run git by itself; loop-goal remains a governor and records the
    authoritative results before allowing implementation.
    """
    root = project_root.expanduser().resolve()
    state = read_state(root, run_id=run_id)
    if state.get("status") == "blocked":
        return state

    outputs = {
        "truth_baseline_commit": precheck.get("truth_baseline_commit"),
        "canonical_refreeze_committed": bool(precheck.get("canonical_refreeze_committed")),
        "feature_worktree_reconciled": bool(precheck.get("feature_worktree_reconciled")),
        "stale_feature_refreeze_quarantine_ref": str(
            precheck.get("stale_feature_refreeze_quarantine_ref") or ""
        ),
        "verification_bundle_ref": str(
            precheck.get("verification_bundle_ref") or _default_verification_bundle_ref(run_id)
        ),
        "workspace_admission_ref": str(precheck.get("workspace_admission_ref") or ""),
        "topology_gate_ref": str(precheck.get("topology_gate_ref") or ""),
        "topology_gate_status": str(precheck.get("topology_gate_status") or "not_checked"),
    }

    previous_outputs = state.get("outputs", {})
    if (
        previous_outputs.get("standard_execution_flow_status") == "pass"
        and previous_outputs.get("truth_baseline_commit") == outputs["truth_baseline_commit"]
        and previous_outputs.get("verification_bundle_ref") == outputs["verification_bundle_ref"]
        and previous_outputs.get("workspace_admission_ref") == outputs["workspace_admission_ref"]
    ):
        return {
            "status": "pass",
            "result": "up_to_date",
            "current_stage": state.get("current_stage"),
            "run_id": run_id,
            "outputs": previous_outputs,
        }

    verification_bundle = _normalise_verification_bundle(
        precheck.get("verification_bundle") if isinstance(precheck, dict) else None,
        version=str(state.get("version") or ""),
    )
    workspace_admission = precheck.get("workspace_admission")
    if "workspace_admission" in verification_bundle and not workspace_admission:
        workspace_admission = verification_bundle.get("workspace_admission")

    # AC-025: verification evidence must be CLI-owned. Agent-fabricated pass without
    # a CLI artifact is rejected fail-closed.
    from beacon.utils.standard_execution_precheck import load_cli_owned_bundle

    cli_bundle = load_cli_owned_bundle(root, outputs["verification_bundle_ref"])
    if not cli_bundle:
        return _standard_execution_block(
            root,
            run_id=run_id,
            state=state,
            outputs=outputs,
            reason_code="verification_bundle_not_cli_owned",
        )
    if cli_bundle:
        # Prefer authoritative CLI artifact fields when present.
        if isinstance(cli_bundle.get("verification_bundle"), dict):
            verification_bundle = _normalise_verification_bundle(
                cli_bundle.get("verification_bundle"),
                version=str(state.get("version") or ""),
            )
        if cli_bundle.get("topology_gate_ref"):
            outputs["topology_gate_ref"] = str(cli_bundle.get("topology_gate_ref") or "")
        if cli_bundle.get("topology_gate_status"):
            outputs["topology_gate_status"] = str(cli_bundle.get("topology_gate_status") or "")
        if cli_bundle.get("workspace_admission_ref"):
            outputs["workspace_admission_ref"] = str(cli_bundle.get("workspace_admission_ref") or "")
        if "canonical_refreeze_committed" in cli_bundle:
            outputs["canonical_refreeze_committed"] = bool(cli_bundle.get("canonical_refreeze_committed"))
            precheck = {
                **precheck,
                "canonical_refreeze_committed": bool(cli_bundle.get("canonical_refreeze_committed")),
                "truth_baseline_merged": bool(cli_bundle.get("truth_baseline_merged")),
                "truth_baseline_commit": cli_bundle.get("truth_baseline_commit") or outputs["truth_baseline_commit"],
                "feature_worktree_reconciled": bool(cli_bundle.get("feature_worktree_reconciled", True)),
                "stale_feature_refreeze_detected": bool(cli_bundle.get("stale_feature_refreeze_detected")),
                "stale_feature_refreeze_quarantine_ref": str(
                    cli_bundle.get("stale_feature_refreeze_quarantine_ref") or ""
                ),
                "workspace_admission": (
                    (cli_bundle.get("verification_bundle") or {}).get("workspace_admission")
                    if isinstance(cli_bundle.get("verification_bundle"), dict)
                    else workspace_admission
                ),
            }
            outputs["truth_baseline_commit"] = precheck.get("truth_baseline_commit")
            outputs["stale_feature_refreeze_quarantine_ref"] = str(
                precheck.get("stale_feature_refreeze_quarantine_ref") or ""
            )
            workspace_admission = precheck.get("workspace_admission") or workspace_admission

    if not outputs["canonical_refreeze_committed"]:
        return _standard_execution_block(
            root,
            run_id=run_id,
            state=state,
            outputs=outputs,
            reason_code="canonical_refreeze_not_committed",
        )

    if bool(precheck.get("stale_feature_refreeze_detected")) and not outputs[
        "stale_feature_refreeze_quarantine_ref"
    ]:
        return _standard_execution_block(
            root,
            run_id=run_id,
            state=state,
            outputs=outputs,
            reason_code="stale_feature_refreeze_not_quarantined",
        )

    if not outputs["truth_baseline_commit"] or not bool(precheck.get("truth_baseline_merged")):
        return _standard_execution_block(
            root,
            run_id=run_id,
            state=state,
            outputs=outputs,
            reason_code="truth_baseline_not_merged",
        )

    required_checks = required_standard_execution_checks(str(state.get("version") or ""))
    missing_checks = [
        key for key in required_checks
        if key not in verification_bundle or not _check_passed(verification_bundle.get(key))
    ]
    if missing_checks:
        outputs["verification_bundle_missing_checks"] = missing_checks
        return _standard_execution_block(
            root,
            run_id=run_id,
            state=state,
            outputs=outputs,
            reason_code="verification_bundle_incomplete",
        )

    if not outputs["workspace_admission_ref"]:
        return _standard_execution_block(
            root,
            run_id=run_id,
            state=state,
            outputs=outputs,
            reason_code="workspace_admission_missing",
        )


    if "topology_gate" in required_checks:
        topo = verification_bundle.get("topology_gate")
        if not _check_passed(topo):
            reason_code = "topology_gate_blocked"
            if isinstance(topo, dict):
                reason_code = str(topo.get("reason_code") or reason_code)
            return _standard_execution_block(
                root,
                run_id=run_id,
                state=state,
                outputs=outputs,
                reason_code=reason_code,
            )
        if not outputs.get("topology_gate_ref"):
            return _standard_execution_block(
                root,
                run_id=run_id,
                state=state,
                outputs=outputs,
                reason_code="topology_gate_ref_missing",
            )
        outputs["topology_gate_status"] = "pass"

    if not _check_passed(workspace_admission):
        reason_code = "workspace_admission_blocked"
        if isinstance(workspace_admission, dict):
            reason_code = str(workspace_admission.get("reason_code") or reason_code)
        return _standard_execution_block(
            root,
            run_id=run_id,
            state=state,
            outputs=outputs,
            reason_code=reason_code,
        )

    bundle_ref = _write_verification_bundle(
        root,
        run_id=run_id,
        bundle=verification_bundle,
        verification_bundle_ref=outputs["verification_bundle_ref"],
        cli_owned=bool(precheck.get("cli_owned") or cli_bundle),
        produced_by=str(
            (cli_bundle or {}).get("produced_by")
            or precheck.get("produced_by")
            or ""
        ),
    )
    outputs["verification_bundle_ref"] = bundle_ref
    outputs["standard_execution_flow_status"] = "pass"
    outputs.pop("verification_bundle_missing_checks", None)

    state["outputs"].update(outputs)
    state["current_stage"] = "implement_routing"
    state["stage_history"].append({
        "stage": "implement_routing",
        "status": "standard_execution_precheck_pass",
        "at": _now_iso(),
        "truth_baseline_commit": outputs["truth_baseline_commit"],
    })
    _state_path(root, run_id).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "status": "pass",
        "current_stage": "implement_routing",
        "run_id": run_id,
        "outputs": outputs,
    }


def route_to_error_recovery(
    project_root: Path,
    *,
    run_id: str,
    reason_code: str = "",
) -> dict[str, Any]:
    """Route to error_recovery stage with beacon-gov-debug recommendation."""
    return transition(
        project_root,
        run_id=run_id,
        to_stage="error_recovery",
        status=f"blocked:{reason_code}" if reason_code else "blocked",
    )


def get_skill_for_stage(stage: str) -> str:
    """Return the skill name to load for a given stage."""
    stage_to_skill = {
        "governance_precheck": "CLI:beacon-plan-start",
        "truth_routing": "beacon-gen-truth",
        "review_routing": "beacon-pln-review",
        "standard_execution_precheck": "CLI:beacon-status-standard-execution-precheck",
        "implement_routing": "beacon-gen-implement",
        "qa_routing": "beacon-eval-qa",
        "qa_deep_routing": "beacon-eval-qa-deep",
        "drift_routing": "beacon-gen-change",
        "release_gate": "beacon-eval-release",
        "error_recovery": "beacon-gov-debug",
        "done": "",
        "idle": "",
    }
    return stage_to_skill.get(stage, "")


def build_status(project_root: Path, *, run_id: str = "") -> dict[str, Any]:
    """Build a status view of loop-goal runs.

    With ``run_id`` returns that run's detail (current stage, next skill,
    outputs, repair loop count). Without it lists all runs under
    ``.beacon/state/loop-goal/`` with a compact summary of each.
    """
    root = project_root.expanduser().resolve()
    if run_id:
        state = read_state(root, run_id=run_id)
        if state.get("status") == "blocked":
            return {
                "schema_version": "loop-goal-status.v1",
                "status": "blocked",
                "reason_code": state.get("reason_code", "state_not_found"),
                "run_id": run_id,
            }
        current_stage = str(state.get("current_stage") or "idle")
        outputs = dict(state.get("outputs") or {})
        metrics = outputs.get("human_stop_metrics")
        if not isinstance(metrics, dict):
            metrics = _default_human_stop_metrics()
        return {
            "schema_version": "loop-goal-status.v1",
            "status": "pass",
            "run_id": run_id,
            "feature": state.get("feature"),
            "version": state.get("version"),
            "current_stage": current_stage,
            "next_skill": get_skill_for_stage(current_stage),
            "auto_decide": state.get("auto_decide"),
            "repair_loop_count": state.get("repair_loop_count", 0),
            "outputs": outputs,
            "human_stop_metrics": metrics,
            "stop_when": state.get("stop_when", []),
            "stage_history": state.get("stage_history", []),
        }

    state_dir = _state_dir(root)
    runs: list[dict[str, Any]] = []
    if state_dir.is_dir():
        for path in sorted(state_dir.glob("lg-*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            current_stage = str(data.get("current_stage") or "idle")
            outputs = dict(data.get("outputs") or {})
            metrics = outputs.get("human_stop_metrics")
            if not isinstance(metrics, dict):
                metrics = _default_human_stop_metrics()
            runs.append({
                "run_id": data.get("run_id", path.stem),
                "feature": data.get("feature"),
                "version": data.get("version"),
                "current_stage": current_stage,
                "next_skill": get_skill_for_stage(current_stage),
                "repair_loop_count": data.get("repair_loop_count", 0),
                "human_stop_metrics": metrics,
            })
    return {
        "schema_version": "loop-goal-status.v1",
        "status": "pass",
        "run_count": len(runs),
        "runs": runs,
    }


def build_resume(project_root: Path, *, run_id: str = "", utterance: str = "") -> dict[str, Any]:
    """Resume helper for ``beacon status loop-goal --resume``.

    Returns actionable ``current_stage`` + ``next_skill``. Refuses no-op success
    when there is no runnable stage/skill (AC-029).
    """
    root = project_root.expanduser().resolve()
    utterance_slice = str(utterance or "").strip().lower()
    if not run_id:
        listed = build_status(root, run_id="")
        runs = list(listed.get("runs") or [])
        if not runs:
            return {
                "schema_version": "loop-goal-resume.v1",
                "status": "blocked",
                "reason_code": "loop_goal_resume_no_runs",
                "resume_action": "none",
            }
        # Prefer the latest run id (sorted glob order ends with newest uuid suffix).
        run_id = str(runs[-1].get("run_id") or "")
        if not run_id:
            return {
                "schema_version": "loop-goal-resume.v1",
                "status": "blocked",
                "reason_code": "loop_goal_resume_no_runs",
                "resume_action": "none",
            }

    status = build_status(root, run_id=run_id)
    if status.get("status") == "blocked":
        return {
            "schema_version": "loop-goal-resume.v1",
            "status": "blocked",
            "reason_code": status.get("reason_code") or "state_not_found",
            "run_id": run_id,
            "resume_action": "none",
        }

    current_stage = str(status.get("current_stage") or "idle")
    next_skill = str(status.get("next_skill") or "")
    outputs = dict(status.get("outputs") or {})
    metrics = status.get("human_stop_metrics") or outputs.get("human_stop_metrics") or {}

    if current_stage == "done":
        return {
            "schema_version": "loop-goal-resume.v1",
            "status": "pass",
            "reason_code": "loop_goal_already_done",
            "run_id": run_id,
            "current_stage": current_stage,
            "next_skill": "",
            "resume_action": "none",
            "human_stop_metrics": metrics,
        }

    if current_stage == "release_gate":
        return {
            "schema_version": "loop-goal-resume.v1",
            "status": "pass",
            "reason_code": "await_human_confirmation",
            "run_id": run_id,
            "feature": status.get("feature"),
            "version": status.get("version"),
            "current_stage": current_stage,
            "next_skill": next_skill,
            "resume_action": "await_human_confirmation",
            "same_session_continue_required": False,
            "human_stop_metrics": metrics,
            "outputs": outputs,
        }

    if current_stage in {"idle", ""} or not next_skill:
        return {
            "schema_version": "loop-goal-resume.v1",
            "status": "blocked",
            "reason_code": "loop_goal_resume_noop_forbidden",
            "run_id": run_id,
            "current_stage": current_stage,
            "next_skill": next_skill,
            "resume_action": "none",
            "human_stop_metrics": metrics,
        }

    return {
        "schema_version": "loop-goal-resume.v1",
        "status": "pass",
        "reason_code": "",
        "run_id": run_id,
        "feature": status.get("feature"),
        "version": status.get("version"),
        "current_stage": current_stage,
        "next_skill": next_skill,
        "resume_action": "load_next_skill",
        "same_session_continue_required": True,
        "human_stop_metrics": metrics,
        "outputs": outputs,
        "repair_loop_count": status.get("repair_loop_count", 0),
    }
