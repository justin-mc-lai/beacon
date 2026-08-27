#!/usr/bin/env python3
"""v1.6.16 P2 exec-layer tests: eval external anchor (non self-produced cases).

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.agent_eval_kit import (
    EXTERNAL_CASE_SOURCES,
    external_benchmark_cases,
    load_benchmark_cases_with_external,
    run_agent_eval_benchmark,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_external_cases_present() -> None:
    """AC-001: benchmark case set includes external-source cases (not all built-in)."""
    cases, external = load_benchmark_cases_with_external(include_external=True)
    assert external, "must include external cases"
    assert len(external) >= 3, f"expected >=3 external cases, got {len(external)}"
    # built-in cases preserved
    assert len(cases) > len(external), "built-in cases must be preserved"


def test_provenance_traceable() -> None:
    """AC-002: external cases carry a recognized source_ref; fake provenance rejected."""
    cases, external = load_benchmark_cases_with_external(include_external=True)
    for case in external:
        source_ref = str(case.get("source_ref") or "")
        assert source_ref, f"case {case.get('case_id')} missing source_ref"
        provenance = source_ref.split(":", 1)[0].strip()
        assert provenance in EXTERNAL_CASE_SOURCES, f"case {case.get('case_id')} provenance not recognized"

    # a case claiming external source without recognized provenance is rejected
    from beacon.utils import agent_eval_kit

    original = agent_eval_kit._EXTERNAL_BENCHMARK_CASES
    agent_eval_kit._EXTERNAL_BENCHMARK_CASES = [
        {"case_id": "bad-ext", "tc_id": "TC-EXT-999", "source_ref": "made_up_source:x", "prompt": "p", "expected_route": "r"}
    ]
    try:
        _, external2 = load_benchmark_cases_with_external(include_external=True)
        assert all("made_up_source" not in str(c.get("source_ref") or "") for c in external2), "fake provenance must be rejected"
    finally:
        agent_eval_kit._EXTERNAL_BENCHMARK_CASES = original


def test_external_cases_runnable() -> None:
    """AC-003: external cases are runnable (prompt + expected_route complete)."""
    for case in external_benchmark_cases():
        assert case.get("prompt"), f"{case['case_id']} missing prompt"
        assert case.get("expected_route"), f"{case['case_id']} missing expected_route"
        assert case.get("tc_id"), f"{case['case_id']} missing tc_id"


def test_builtin_preserved() -> None:
    """AC-004: built-in cases preserved (regression compatible)."""
    cases, external = load_benchmark_cases_with_external(include_external=True)
    tc_ids = {c.get("tc_id") for c in cases}
    for ext in external:
        assert ext["tc_id"] in tc_ids, f"external {ext['tc_id']} should be in merged set"
    # built-in TC-006..017 still present
    assert "TC-006" in tc_ids, "built-in TC-006 must remain"


def test_benchmark_runs_with_external() -> None:
    """AC-003: run_agent_eval_benchmark executes with external cases included."""
    payload = run_agent_eval_benchmark(PROJECT_ROOT, version="v1.6.1")
    assert payload.get("status") == "pass", f"benchmark must pass: {payload.get('status')}"
    summary = payload.get("summary") or {}
    assert summary.get("external_case_count", 0) >= 3, "benchmark summary must report external cases"


def test_fsm_legal_walk() -> None:
    """Domain FSM legal walk: scaffold->collected->registered->executed->verified."""
    from beacon.utils.truth_fsm import parse_truth_fsm, validate_truth_fsm

    truth_path = PROJECT_ROOT / "docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/truth.md"
    md = truth_path.read_text(encoding="utf-8")
    fsm = parse_truth_fsm(md)
    assert fsm["five_tuple_present"], "five-tuple must be present"
    result = validate_truth_fsm(fsm)
    assert not result["blocked"], f"FSM must validate: {result['findings']}"
    assert "verified" in fsm.get("terminal_states") or [], "verified must be terminal"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_external_cases_present,
        test_provenance_traceable,
        test_external_cases_runnable,
        test_builtin_preserved,
        test_benchmark_runs_with_external,
        test_fsm_legal_walk,
    ]
    if args.keyword:
        kw = args.keyword.lower()

        def _match(fn) -> bool:
            name = fn.__name__.lower()
            if kw in name:
                return True
            if kw.endswith("or") and len(kw) > 2 and kw[:-2] in name:
                return True
            first = kw.split("_")[0]
            return bool(first) and first in name

        tests = [fn for fn in tests if _match(fn)]
        if not tests:
            print(f"no test matches -k {args.keyword}")
            return 1
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
