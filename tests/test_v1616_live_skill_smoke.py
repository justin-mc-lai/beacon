#!/usr/bin/env python3
"""v1.6.16 P1 exec-layer tests: full-skill live smoke via local_admitted tier.

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.agent_eval_kit import (
    _live_execution_mode_for_entry,
    is_live_runner_admitted,
    materialize_live_runner_admission,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_admission_materialized() -> None:
    """AC-001: local_admitted admission makes live runner admitted."""
    r = materialize_live_runner_admission(PROJECT_ROOT, version="v1.6.1", default_live_tier="local_admitted")
    assert r["status"] == "pass"
    assert r["admission"]["admitted"] is True
    assert r["admission"]["default_live_tier"] == "local_admitted"


def test_is_admitted_after_materialize() -> None:
    """AC-001: after materializing admission, live runner is admitted."""
    materialize_live_runner_admission(PROJECT_ROOT, version="v1.6.1", default_live_tier="local_admitted")
    assert is_live_runner_admitted(PROJECT_ROOT, version="v1.6.1") is True


def test_full_host_behavior_local_admitted() -> None:
    """AC-001: local_admitted -> every skill is host_behavior (not surface_only)."""
    for skill_id in ("beacon-eval-qa", "beacon-gen-truth", "beacon-pln-program", "beacon-eval-release"):
        mode = _live_execution_mode_for_entry(
            live_tier="local_admitted", skill_id=skill_id, ci_smoke_skill_id="beacon-eval-qa"
        )
        assert mode == "host_behavior", f"{skill_id} should be host_behavior under local_admitted, got {mode}"


def test_ci_default_still_single_smoke() -> None:
    """AC-004 compat: ci_default keeps 1-skill smoke (no behavior change)."""
    smoke = _live_execution_mode_for_entry(live_tier="ci_default", skill_id="beacon-eval-qa", ci_smoke_skill_id="beacon-eval-qa")
    other = _live_execution_mode_for_entry(live_tier="ci_default", skill_id="beacon-gen-truth", ci_smoke_skill_id="beacon-eval-qa")
    assert smoke == "host_behavior"
    assert other == "surface_only"


def test_no_fake_pass() -> None:
    """AC-004: blocked skills must not count as pass."""
    from beacon.utils.agent_eval_kit import _execute_live_per_skill

    traces_dir = PROJECT_ROOT / ".beacon" / "test-traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    entries = [{"skill_id": "beacon-eval-qa"}, {"skill_id": "beacon-gen-truth"}]
    per_skill = _execute_live_per_skill(
        PROJECT_ROOT,
        matrix_entries=entries,
        admitted=False,
        traces_dir=traces_dir,
        live_tier="local_admitted",
        admission={},
    )
    for trace in per_skill:
        assert trace.get("status") == "blocked", "non-admitted must be blocked"
        assert trace.get("reason_code") == "agent_eval_live_runner_not_admitted"


def test_fsm_legal_walk() -> None:
    """Domain FSM legal walk: scaffold->executing->traced->passed/failed."""
    from beacon.utils.truth_fsm import parse_truth_fsm, validate_truth_fsm

    truth_path = PROJECT_ROOT / "docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/truth.md"
    md = truth_path.read_text(encoding="utf-8")
    fsm = parse_truth_fsm(md)
    assert fsm["five_tuple_present"], "five-tuple must be present"
    result = validate_truth_fsm(fsm)
    assert not result["blocked"], f"FSM must validate: {result['findings']}"
    assert "passed" in fsm.get("terminal_states") or "failed" in fsm.get("terminal_states"), "passed/failed must be terminal"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_admission_materialized,
        test_is_admitted_after_materialize,
        test_full_host_behavior_local_admitted,
        test_ci_default_still_single_smoke,
        test_no_fake_pass,
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
