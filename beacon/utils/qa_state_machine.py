"""Truth→FSM extraction and state coverage for Beacon QA v1.6.4."""

from __future__ import annotations

import re
from typing import Any

_TRANSITION_RE = re.compile(
    r"\[(?P<from>[^\]]+)\]\s*--[^>]+-->\s*\[(?P<to>[^\]]+)\]",
    re.MULTILINE,
)
_UNREACHABLE_RE = re.compile(r"不可达|unreachable", re.IGNORECASE)

REASON_FSM_EXTRACT_FAILED = "fsm_extract_failed"
REASON_UNREACHABLE_STATE_REACHED = "unreachable_state_reached"


def extract_fsm_from_truth(text: str) -> dict[str, Any]:
    body = str(text or "")
    if not body.strip():
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_FSM_EXTRACT_FAILED,
        }
    state_machine_section = ""
    if "## State Machine" in body:
        state_machine_section = body.split("## State Machine", 1)[1].split("\n## ", 1)[0]
    elif "## 状态机" in body:
        state_machine_section = body.split("## 状态机", 1)[1].split("\n## ", 1)[0]
    else:
        state_machine_section = body
    transitions: list[dict[str, str]] = []
    states: set[str] = set()
    for match in _TRANSITION_RE.finditer(state_machine_section):
        source = match.group("from").strip()
        target = match.group("to").strip()
        if source and target and not _UNREACHABLE_RE.search(source) and not _UNREACHABLE_RE.search(target):
            states.add(source)
            states.add(target)
            transitions.append({"from": source, "to": target})
    if not transitions:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_FSM_EXTRACT_FAILED,
        }
    boundary_states = {transitions[0]["from"], transitions[-1]["to"]}
    unreachable: list[str] = []
    if _UNREACHABLE_RE.search(state_machine_section):
        for token in re.findall(r"\[(?P<state>[^\]]+)\]", state_machine_section):
            if "不可达" in token or "unreachable" in token.lower():
                unreachable.append(token.strip("[] "))
    return {
        "schema_version": "1.0",
        "status": "pass",
        "blocked": False,
        "states": sorted(states),
        "transitions": transitions,
        "boundary_states": sorted(boundary_states),
        "unreachable_states": sorted(set(unreachable)),
    }


def build_state_coverage_model(
    fsm: dict[str, Any],
    *,
    covered_transitions: list[tuple[str, str]] | None = None,
    covered_boundary_states: list[str] | None = None,
    reached_unreachable: list[str] | None = None,
) -> dict[str, Any]:
    if bool(fsm.get("blocked")):
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": str(fsm.get("reason_code") or REASON_FSM_EXTRACT_FAILED),
        }
    transitions = fsm.get("transitions") if isinstance(fsm.get("transitions"), list) else []
    covered = {(str(a).strip(), str(b).strip()) for a, b in (covered_transitions or [])}
    transition_gaps = [
        item
        for item in transitions
        if (str(item.get("from") or ""), str(item.get("to") or "")) not in covered
    ]
    boundary_states = set(fsm.get("boundary_states") or [])
    covered_boundary = {str(item).strip() for item in (covered_boundary_states or [])}
    boundary_gaps = sorted(state for state in boundary_states if state not in covered_boundary)
    unreachable = set(fsm.get("unreachable_states") or [])
    reached = {str(item).strip() for item in (reached_unreachable or [])}
    unreachable_hit = sorted(state for state in unreachable if state in reached)
    transition_total = len(transitions)
    transition_covered = transition_total - len(transition_gaps)
    coverage_ratio = round(transition_covered / transition_total, 4) if transition_total else 0.0
    blocked = bool(unreachable_hit)
    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_code": REASON_UNREACHABLE_STATE_REACHED if blocked else "",
        "transition_coverage_ratio": coverage_ratio,
        "transition_gaps": transition_gaps,
        "boundary_states": sorted(boundary_states),
        "boundary_gaps": boundary_gaps,
        "unreachable_states": sorted(unreachable),
        "unreachable_reached": unreachable_hit,
    }


def derive_boundary_test_cases(fsm: dict[str, Any]) -> list[dict[str, str]]:
    if bool(fsm.get("blocked")):
        return []
    transitions = fsm.get("transitions") if isinstance(fsm.get("transitions"), list) else []
    cases: list[dict[str, str]] = []
    if transitions:
        first = transitions[0]
        cases.append({"kind": "initial_entry", "from": str(first.get("from") or ""), "to": str(first.get("to") or "")})
        last = transitions[-1]
        cases.append({"kind": "terminal_exit", "from": str(last.get("from") or ""), "to": str(last.get("to") or "")})
    states = set(fsm.get("states") or [])
    known_targets = {str(item.get("to") or "") for item in transitions}
    for state in sorted(states - known_targets):
        if state not in set(fsm.get("boundary_states") or []):
            cases.append({"kind": "illegal_transition_target", "from": "", "to": state})
    return cases
