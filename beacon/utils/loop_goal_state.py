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
    "implement_routing",
    "qa_routing",
    "release_gate",
    "done",
    "error_recovery",
})

MAX_REPAIR_LOOPS = 3

RELEASE_HUMAN_GATE_STAGES = frozenset({"release_gate"})


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
            "tests_pass": False,
            "qa_verdict": None,
            "release_verdict": None,
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
) -> dict[str, Any]:
    """Transition to a new stage, appending to stage_history.

    Validates the target stage and checks stop-when conditions.
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

    # Check release human gate
    if to_stage in RELEASE_HUMAN_GATE_STAGES:
        auto = state.get("auto_decide", False)
        overrides = state.get("human_gate_overrides", [])
        # Release gate ALWAYS requires human confirmation, even with auto_decide
        # The transition TO release_gate is allowed, but the transition FROM
        # release_gate to done requires human confirmation.
        pass  # Transition to release_gate is allowed; check happens on leaving

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

    # Human confirmed — allow transition to done
    return transition(project_root, run_id=run_id, to_stage="done", status="release_confirmed")


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
        "implement_routing": "beacon-gen-implement",
        "qa_routing": "beacon-eval-qa",
        "release_gate": "beacon-eval-release",
        "error_recovery": "beacon-gov-debug",
        "done": "",
        "idle": "",
    }
    return stage_to_skill.get(stage, "")
