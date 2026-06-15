"""Program plan FSM for beacon-harness-program-plan-v161 (v1.6.1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

PROGRAM_PLAN_STATES: Final[tuple[str, ...]] = (
    "program_intent_captured",
    "plan_mode_selected",
    "program_inventory",
    "program_reviewed",
    "feature_graph_ack",
    "lakes_truth_in_progress",
    "lakes_frozen",
    "program_frozen",
    "program_delivery",
    "program_change_open",
    "program_change_review",
    "program_refreeze",
)

VALID_TRANSITIONS: Final[dict[str, tuple[str, ...]]] = {
    "program_intent_captured": ("plan_mode_selected",),
    "plan_mode_selected": ("program_inventory",),
    "program_inventory": ("program_reviewed",),
    "program_reviewed": ("feature_graph_ack",),
    "feature_graph_ack": ("lakes_truth_in_progress",),
    "lakes_truth_in_progress": ("lakes_frozen", "lakes_truth_in_progress"),
    "lakes_frozen": ("program_frozen",),
    "program_frozen": ("program_delivery", "program_change_open"),
    "program_delivery": (),
    "program_change_open": ("program_change_review",),
    "program_change_review": ("program_refreeze",),
    "program_refreeze": ("program_frozen",),
}

INVALID_TRANSITIONS: Final[tuple[tuple[str, str], ...]] = (
    ("program_intent_captured", "lakes_frozen"),
    ("program_intent_captured", "program_inventory"),
    ("program_intent_captured", "program_frozen"),
    ("program_change_open", "program_delivery"),
    ("program_change_open", "program_frozen"),
    ("feature_graph_ack", "program_frozen"),
)

RECOVERY_ROUTES: Final[dict[tuple[str, str], str]] = {
    ("lakes_truth_in_progress", "lakes_frozen"): "beacon doctor verify-truth-integrity",
    ("program_change_open", "program_delivery"): "beacon-pln-review",
    ("program_change_open", "program_frozen"): "beacon-pln-review",
}


@dataclass(frozen=True)
class TransitionResult:
    ok: bool
    from_state: str
    to_state: str
    reason_code: str = ""
    recovery_route: str = ""


def is_valid_transition(from_state: str, to_state: str) -> bool:
    if (from_state, to_state) in INVALID_TRANSITIONS:
        return False
    allowed = VALID_TRANSITIONS.get(from_state, ())
    return to_state in allowed


def transition(from_state: str, to_state: str) -> TransitionResult:
    if from_state not in PROGRAM_PLAN_STATES or to_state not in PROGRAM_PLAN_STATES:
        return TransitionResult(
            ok=False,
            from_state=from_state,
            to_state=to_state,
            reason_code="unknown_state",
        )
    if (from_state, to_state) in INVALID_TRANSITIONS:
        return TransitionResult(
            ok=False,
            from_state=from_state,
            to_state=to_state,
            reason_code="invalid_transition",
            recovery_route=RECOVERY_ROUTES.get((from_state, to_state), ""),
        )
    if to_state not in VALID_TRANSITIONS.get(from_state, ()):
        return TransitionResult(
            ok=False,
            from_state=from_state,
            to_state=to_state,
            reason_code="transition_not_allowed",
            recovery_route=RECOVERY_ROUTES.get((from_state, to_state), ""),
        )
    return TransitionResult(ok=True, from_state=from_state, to_state=to_state)


def tig_block_recovery_state() -> str:
    """Lake TIG block returns program to lakes_truth_in_progress."""
    return "lakes_truth_in_progress"
