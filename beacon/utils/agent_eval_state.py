"""Agent Eval FSM for beacon-agent-eval-v161 (v1.6.1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

AGENT_EVAL_STATES: Final[tuple[str, ...]] = (
    "EvalRequested",
    "CatalogResolved",
    "CaseSetMaterialized",
    "RunnerAdmission",
    "LaneExecution",
    "ScoreSynthesis",
    "EvidencePersisted",
    "Terminal",
)

PSEUDO_STATES: Final[tuple[str, ...]] = (
    "release_ready",
    "formal_qa_pass",
    "truth_write",
)

VALID_TRANSITIONS: Final[dict[str, tuple[str, ...]]] = {
    "EvalRequested": ("CatalogResolved",),
    "CatalogResolved": ("CaseSetMaterialized",),
    "CaseSetMaterialized": ("RunnerAdmission",),
    "RunnerAdmission": ("LaneExecution",),
    "LaneExecution": ("ScoreSynthesis",),
    "ScoreSynthesis": ("EvidencePersisted",),
    "EvidencePersisted": ("Terminal",),
    "Terminal": (),
}

INVALID_TRANSITIONS: Final[tuple[tuple[str, str], ...]] = (
    ("EvalRequested", "ScoreSynthesis"),
    ("EvalRequested", "Terminal"),
    ("EvalRequested", "LaneExecution"),
    ("ScoreSynthesis", "release_ready"),
    ("simulated", "formal_qa_pass"),
    ("LaneExecution", "truth_write"),
    ("CatalogResolved", "Terminal"),
    ("RunnerAdmission", "ScoreSynthesis"),
)

RECOVERY_ROUTES: Final[dict[tuple[str, str], str]] = {
    ("RunnerAdmission", "LaneExecution"): "beacon eval run --runner replay --split regression-core",
    ("LaneExecution", "ScoreSynthesis"): "beacon eval run --runner replay",
    ("EvalRequested", "ScoreSynthesis"): "beacon eval catalog --materialize",
    ("RunnerAdmission", "Terminal"): "beacon eval run --runner replay --split regression-core",
}

LIVE_BLOCKED_RECOVERY: Final[str] = "beacon eval run --runner replay --split regression-core"


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
    if from_state in PSEUDO_STATES or to_state in PSEUDO_STATES:
        return False
    allowed = VALID_TRANSITIONS.get(from_state, ())
    return to_state in allowed


def transition(from_state: str, to_state: str) -> TransitionResult:
    if from_state in PSEUDO_STATES or to_state in PSEUDO_STATES:
        return TransitionResult(
            ok=False,
            from_state=from_state,
            to_state=to_state,
            reason_code="invalid_transition",
            recovery_route=RECOVERY_ROUTES.get((from_state, to_state), ""),
        )
    if (from_state, to_state) in INVALID_TRANSITIONS:
        return TransitionResult(
            ok=False,
            from_state=from_state,
            to_state=to_state,
            reason_code="invalid_transition",
            recovery_route=RECOVERY_ROUTES.get((from_state, to_state), ""),
        )
    if from_state not in AGENT_EVAL_STATES or to_state not in AGENT_EVAL_STATES:
        return TransitionResult(
            ok=False,
            from_state=from_state,
            to_state=to_state,
            reason_code="unknown_state",
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


def live_blocked_recovery_route() -> str:
    """When live runner is blocked, degrade to replay/simulated with degraded=true."""
    return LIVE_BLOCKED_RECOVERY


def catalog_missing_recovery_route() -> str:
    return "beacon eval catalog --materialize"
