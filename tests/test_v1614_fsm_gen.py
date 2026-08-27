#!/usr/bin/env python3
"""v1.6.14 L2 exec-layer tests: FSM legal-walk generation (AC-001..004).

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.fsm_walk_gen import (
    generate_legal_walks,
    render_legal_walk_tcs,
    vertex_assertions,
)

# Legal FSM: scaffold -> rendered -> validated -> frozen
LEGAL_FSM = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | render | fsm_present | rendered | gen |
| rendered | validate | states_ok | validated | validate |
| validated | digest | behavior_stable | frozen | digest |
| frozen | publish | gate_ok | shipped | ship |

**终态：** shipped
"""

# FSM with an illegal short-circuit: rendered -> frozen declared illegal (validated path remains legal)
ILLEGAL_FSM = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | render | fsm_present | rendered | gen |
| rendered | validate | states_ok | validated | validate |
| validated | freeze | gate_ok | frozen | freeze |
| frozen | publish | gate_ok | shipped | ship |
| rendered | skip_review | bypass | frozen | skip |

**终态：** shipped

## Illegal transitions

- rendered -> frozen (跳过校验冻结)
"""

# Invalid FSM (destination ghost_state not defined, no terminal)
INVALID_FSM = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | render | fsm_present | ghost_state | gen |

**终态：** rendered
"""


def test_walk_legal_paths() -> None:
    result = generate_legal_walks(LEGAL_FSM)
    assert result["valid"], "legal FSM should generate walks"
    assert result["paths"], "expected at least one legal path"
    for path in result["paths"]:
        assert path[0] == "scaffold", "path must start at initial state"
        assert path[-1] == "shipped", "path must reach terminal state"
    assert result["all_reachable_visited"], "all reachable states must be visited"


def test_walk_all_reachable_covered() -> None:
    result = generate_legal_walks(LEGAL_FSM)
    reachable = result["reachable_states"]
    visited = result["visited_states"]
    for state in reachable:
        assert state in visited, f"reachable state {state} not covered by any walk"


def test_vertex_assertion_per_state() -> None:
    path = ["scaffold", "rendered", "shipped"]
    asserts = vertex_assertions(path)
    assert len(asserts) == 3, "one assertion per reached state"
    assert asserts[0] == {"state": "scaffold", "assert": "reached_scaffold", "expect": "ok"}


def test_exec_tc_rendered() -> None:
    tcs = render_legal_walk_tcs(LEGAL_FSM, prefix="TC-FSMW")
    assert tcs, "legal FSM should render exec-layer TCs"
    for tc in tcs:
        assert tc["command"].startswith("python3 -c"), "TC must be executable"
        assert tc["assertion"], "TC must carry an assertion"
        assert tc["vertex_assertions"], "TC must carry per-state vertex assertions"
    # execute the first TC command
    first = tcs[0]
    import subprocess  # noqa: PLC0415

    proc = subprocess.run(first["command"], shell=True, capture_output=True, text=True)
    assert proc.returncode == 0, f"exec TC failed: {proc.stderr}"


def test_illegal_path_excluded() -> None:
    result = generate_legal_walks(ILLEGAL_FSM)
    assert result["valid"], "FSM with illegal slots should still generate legal walks"
    for path in result["paths"]:
        assert not (path.index("rendered") + 1 == path.index("frozen")), (
            f"illegal rendered->frozen edge leaked into path {path}"
        )
    assert ("rendered", "frozen") in result["illegal_edges_excluded"], "illegal edge must be recorded as excluded"


def test_invalid_fsm_rejected() -> None:
    result = generate_legal_walks(INVALID_FSM)
    assert not result["valid"], "invalid FSM must fail closed"
    assert result.get("reason_code") in {"truth_fsm_invalid", "no_terminal_reachable"}


def main() -> int:
    tests = [
        test_walk_legal_paths,
        test_walk_all_reachable_covered,
        test_vertex_assertion_per_state,
        test_exec_tc_rendered,
        test_illegal_path_excluded,
        test_invalid_fsm_rejected,
    ]
    failures = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
