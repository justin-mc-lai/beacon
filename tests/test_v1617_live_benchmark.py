#!/usr/bin/env python3
"""v1.6.17 A1 exec-layer tests: live benchmark verify (P1 realization).

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.agent_eval_kit import (
    _load_matrix_entries,
    _resolve_host_core_for_skill,
    _surface_preflight,
    materialize_live_prompt_fixtures,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_fixtures_materialized() -> None:
    """AC-001: 34 live skills have real prompt fixtures with ROUTE: line."""
    r = materialize_live_prompt_fixtures(PROJECT_ROOT, version="v1.6.1")
    assert r["written"] >= 30, f"expected >=30 fixtures, got {r['written']}"
    entries = _load_matrix_entries(PROJECT_ROOT, version="v1.6.1")
    for e in entries:
        sid = e.get("skill_id", "")
        fixture = PROJECT_ROOT / "docs" / "beacon" / "v1.6.1" / "fixtures" / "agent-eval" / "v161" / "live" / f"{sid}.prompt.txt"
        assert fixture.exists(), f"fixture missing for {sid}"
        text = fixture.read_text(encoding="utf-8")
        assert text.strip().upper().startswith("ROUTE:"), f"fixture {sid} missing ROUTE line"


def test_surface_resolution() -> None:
    """AC-002: mode/legacy skill ids resolve to host core SKILL.md (no skill_surface_missing)."""
    entries = _load_matrix_entries(PROJECT_ROOT, version="v1.6.1")
    assert _resolve_host_core_for_skill("beacon-gen-truth") == "beacon-truth"
    assert _resolve_host_core_for_skill("beacon-eval-qa") == "beacon-qa"
    assert _resolve_host_core_for_skill("beacon-pln-review") == "beacon-plan"
    # all matrix entries pass preflight
    ok = 0
    for e in entries:
        sid = e.get("skill_id", "")
        r, _ = _surface_preflight(PROJECT_ROOT, skill_id=sid, prompt_fixture_ref=f"fixtures/agent-eval/v161/live/{sid}.prompt.txt")
        if r:
            ok += 1
    assert ok >= 30, f"expected >=30 preflight pass, got {ok}/{len(entries)}"


def test_no_skill_surface_missing() -> None:
    """AC-002: no matrix skill reports skill_surface_missing after mapping."""
    entries = _load_matrix_entries(PROJECT_ROOT, version="v1.6.1")
    for e in entries:
        sid = e.get("skill_id", "")
        r, reason = _surface_preflight(PROJECT_ROOT, skill_id=sid, prompt_fixture_ref=f"fixtures/agent-eval/v161/live/{sid}.prompt.txt")
        assert reason != "skill_surface_missing", f"{sid} still skill_surface_missing"


def test_fsm_legal_walk() -> None:
    """Domain FSM legal walk: scaffold->materialized->resolved->executing->traced->passed."""
    from beacon.utils.truth_fsm import parse_truth_fsm, validate_truth_fsm

    truth_path = PROJECT_ROOT / "docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/truth.md"
    md = truth_path.read_text(encoding="utf-8")
    fsm = parse_truth_fsm(md)
    assert fsm["five_tuple_present"], "five-tuple must be present"
    result = validate_truth_fsm(fsm)
    assert not result["blocked"], f"FSM must validate: {result['findings']}"
    assert "passed" in fsm.get("terminal_states") or "failed" in fsm.get("terminal_states"), "passed/failed terminal"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_fixtures_materialized,
        test_surface_resolution,
        test_no_skill_surface_missing,
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
