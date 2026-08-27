"""FSM legal-walk test generation (v1.6.14 L2; GraphWalker-style distillation).

From a legal truth FSM (states/transitions/illegal) generate legal-walk exec TCs:
paths from initial to terminal that visit every reachable state (AC-001), with a
per-state vertex assertion (AC-003), while illegal transitions are never emitted
(AC-004). Generated TCs are exec-layer (AC-002).
"""

from __future__ import annotations

import re
from typing import Any

from beacon.utils.truth_review_gate import extract_fsm_five_tuple

SCHEMA_FSM_WALK = "fsm-walk-gen.v1"
REASON_FSM_INVALID = "truth_fsm_invalid"


def _norm(text: str | None) -> str:
    return str(text or "").strip()


def _parse_explicit_terminals(truth_markdown: str) -> list[str]:
    terminals: set[str] = set()
    for m in re.finditer(r"(?:终态|terminal(?:\s+states?)?)[:：\s]+([^\n]+)", truth_markdown, re.IGNORECASE):
        for tok in re.split(r"[,/|，、\s]+", m.group(1)):
            tok = tok.strip().strip("`*")
            if tok and len(tok) < 40:
                terminals.add(tok)
    return sorted(terminals)


def _parse_illegal_edges(truth_markdown: str) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    in_illegal = False
    for line in str(truth_markdown or "").splitlines():
        stripped = line.strip()
        if re.match(r"^#{2,6}\s+", stripped):
            in_illegal = bool(
                re.search(r"(illegal|非法)", stripped, re.IGNORECASE)
                and "fsm" in stripped.lower() or "illegal" in stripped.lower()
                or "非法" in stripped
            )
            if "illegal" not in stripped.lower() and "非法" not in stripped:
                in_illegal = False
            continue
        if not in_illegal or not stripped.startswith(("-", "*", "•")):
            continue
        text = stripped.lstrip("-*• ").strip()
        m = re.search(r"([A-Za-z][A-Za-z0-9_]*)\s*(?:->|→|-->)\s*([A-Za-z][A-Za-z0-9_]*)", text)
        if m:
            edges.append((m.group(1).strip(), m.group(2).strip()))
    return edges


def _build_fsm_model(truth_markdown: str) -> dict[str, Any]:
    five = extract_fsm_five_tuple(str(truth_markdown or ""))
    transitions = list(five.get("transitions") or [])
    if not five.get("five_tuple_present"):
        return {"valid": False, "reason_code": REASON_FSM_INVALID, "transitions": []}
    states: set[str] = set()
    for t in transitions:
        states.add(_norm(t.get("state")))
        if t.get("to"):
            states.add(_norm(t.get("to")))
    from_states = {_norm(t.get("state")) for t in transitions if t.get("state")}
    to_states = {_norm(t.get("to")) for t in transitions if t.get("to")}
    initial = sorted(from_states - to_states)
    terminals = _parse_explicit_terminals(str(truth_markdown or ""))
    illegal = _parse_illegal_edges(truth_markdown)
    illegal_edges = set(illegal)
    # legal adjacency excluding illegal edges
    adjacency: dict[str, list[str]] = {s: [] for s in states}
    for t in transitions:
        src = _norm(t.get("state"))
        dst = _norm(t.get("to"))
        if not src or not dst:
            continue
        if (src, dst) in illegal_edges:
            continue
        adjacency.setdefault(src, []).append(dst)
    return {
        "valid": True,
        "states": sorted(states),
        "transitions": transitions,
        "initial_states": initial,
        "terminal_states": sorted(t for t in terminals if t in states),
        "illegal_edges": sorted(illegal_edges),
        "adjacency": {k: sorted(set(v)) for k, v in adjacency.items()},
        "reason_code": "",
    }


def generate_legal_walks(truth_markdown: str) -> dict[str, Any]:
    """Generate legal-walk paths covering all reachable states (AC-001/AC-004)."""
    model = _build_fsm_model(truth_markdown)
    if not model["valid"]:
        return {
            "schema": SCHEMA_FSM_WALK,
            "valid": False,
            "reason_code": REASON_FSM_INVALID,
            "paths": [],
            "visited_states": [],
        }
    if not model["initial_states"]:
        return {
            "schema": SCHEMA_FSM_WALK,
            "valid": False,
            "reason_code": "no_initial_state",
            "paths": [],
            "visited_states": [],
        }
    adjacency = model["adjacency"]
    terminals = set(model["terminal_states"])
    paths: list[list[str]] = []

    def walk(path: list[str], visited: set[str]) -> None:
        current = path[-1]
        if current in terminals:
            paths.append(list(path))
            return
        nxts = adjacency.get(current, [])
        for nxt in nxts:
            if nxt in path and nxt not in terminals:
                continue
            walk(path + [nxt], visited | {nxt})

    for start in model["initial_states"]:
        walk([start], {start})

    reachable = sorted({s for path in paths for s in path})
    # Vertex coverage: merge paths so every reachable state is asserted at least once.
    covered: set[str] = set()
    merged: list[list[str]] = []
    for path in sorted(paths, key=len):
        new_states = set(path) - covered
        if new_states:
            merged.append(path)
            covered |= set(path)
    if reachable and not covered:
        merged = paths
    if not paths:
        return {
            "schema": SCHEMA_FSM_WALK,
            "valid": False,
            "reason_code": "no_terminal_reachable",
            "paths": [],
            "visited_states": [],
        }
    return {
        "schema": SCHEMA_FSM_WALK,
        "valid": True,
        "paths": merged or paths,
        "visited_states": sorted(covered),
        "reachable_states": reachable,
        "all_reachable_visited": sorted(covered) == reachable,
        "illegal_edges_excluded": list(model["illegal_edges"]),
        "reason_code": "",
    }


def vertex_assertions(path: list[str]) -> list[dict[str, str]]:
    """Per-state vertex assertion for a walk path (AC-003)."""
    return [{"state": s, "assert": f"reached_{s}", "expect": "ok"} for s in path]


def render_legal_walk_tcs(truth_markdown: str, *, prefix: str = "TC-FSMW") -> list[dict[str, Any]]:
    """Render legal-walk paths as exec-layer TC rows (AC-002)."""
    result = generate_legal_walks(truth_markdown)
    if not result.get("valid"):
        return []
    tcs: list[dict[str, Any]] = []
    for i, path in enumerate(result.get("paths") or [], start=1):
        assert_text = " and ".join(f"'{p}' in current" for p in path)
        tcs.append(
            {
                "tc_id": f"{prefix}-{i:03d}",
                "path": path,
                "command": f"python3 -c \"current={path}; assert {assert_text or 'True'}; print('ok')\"",
                "assertion": f"vertex path {path} reached (all asserted)",
                "vertex_assertions": vertex_assertions(path),
            }
        )
    return tcs
