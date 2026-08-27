#!/usr/bin/env python3
"""v1.6.16 P3 exec-layer tests: gate independent judge.

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.independent_judge import (
    compare_coverage_verdict,
    recalc_coverage_from_scenarios,
    schema_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_recalc_independent() -> None:
    """AC-001: coverage_rate recomputed by independent script from raw scenarios."""
    results = [
        {"scenario_family": "happy", "evidence_ref": "x"},
        {"scenario_family": "negative", "evidence_ref": "x"},
        {"scenario_family": "boundary", "evidence_ref": ""},  # no evidence
    ]
    rate = recalc_coverage_from_scenarios(results, required_families=["happy", "negative", "boundary"])
    assert rate == round(2 / 3, 4), f"expected 2/3, got {rate}"


def test_compare_match() -> None:
    """AC-002: independent == system -> verified."""
    # simulate a system scorecard claiming coverage_rate=1.0 for 3 families
    import json as _json

    scorecard_path = PROJECT_ROOT / ".beacon" / "qa" / "features" / "beacon-v1616-gate-independent-judge" / "scorecard.json"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    _json.dump(
        {
            "coverage_current": {
                "coverage_rate": 1.0,
                "required_scenario_families": ["happy", "negative", "boundary"],
            }
        },
        open(scorecard_path, "w"),
        ensure_ascii=False,
    )
    results = [
        {"scenario_family": "happy", "evidence_ref": "x"},
        {"scenario_family": "negative", "evidence_ref": "x"},
        {"scenario_family": "boundary", "evidence_ref": "x"},
    ]
    r = compare_coverage_verdict(
        PROJECT_ROOT,
        version="v1.6.16",
        feature="beacon-v1616-gate-independent-judge",
        scenario_results=results,
    )
    assert r["status"] == "verified", f"expected verified: {r}"
    assert r["audit"]["match"] is True


def test_compare_deviation_flagged() -> None:
    """AC-002: independent != system -> flagged (deviation exposed)."""
    import json as _json

    scorecard_path = PROJECT_ROOT / ".beacon" / "qa" / "features" / "beacon-v1616-gate-independent-judge" / "scorecard.json"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    # system claims 1.0 but raw evidence only covers happy+negative -> deviation
    _json.dump(
        {
            "coverage_current": {
                "coverage_rate": 1.0,
                "required_scenario_families": ["happy", "negative", "boundary"],
            }
        },
        open(scorecard_path, "w"),
        ensure_ascii=False,
    )
    results = [
        {"scenario_family": "happy", "evidence_ref": "x"},
        {"scenario_family": "negative", "evidence_ref": "x"},
        {"scenario_family": "boundary", "evidence_ref": ""},
    ]
    r = compare_coverage_verdict(
        PROJECT_ROOT,
        version="v1.6.16",
        feature="beacon-v1616-gate-independent-judge",
        scenario_results=results,
    )
    assert r["status"] == "flagged", f"expected flagged: {r}"
    assert r["audit"]["diff"] != 0, "deviation must expose nonzero diff"


def test_audit_record() -> None:
    """AC-003: deviation record is auditable (gate/system/independent/diff)."""
    results = [{"scenario_family": "happy", "evidence_ref": "x"}]
    r = compare_coverage_verdict(
        PROJECT_ROOT,
        version="v1.6.16",
        feature="beacon-v1616-gate-independent-judge",
        scenario_results=results,
        required_families=["happy", "negative", "boundary"],
    )
    audit = r.get("audit") or {}
    assert "gate" in audit and "system_coverage" in audit and "independent_coverage" in audit and "diff" in audit
    assert audit["gate"] == "coverage_rate"


def test_no_verdict_authority() -> None:
    """AC-004: independent judge does not issue pass/fail, only credibility."""
    contract = schema_contract()
    assert contract["authority"]["issues_verdict"] is False
    assert contract["authority"]["only_checks_credibility"] is True


def test_pending_when_data_missing() -> None:
    """AC-004: missing data -> pending, not fabricated match."""
    # use a feature with no scorecard and no raw scenarios
    r = compare_coverage_verdict(
        PROJECT_ROOT,
        version="v1.6.16",
        feature="no-such-feature",
        scenario_results=None,
    )
    assert r["status"] == "pending", f"expected pending: {r}"


def test_fsm_legal_walk() -> None:
    """Domain FSM legal walk: scaffold->computed->compared->verified/flagged."""
    from beacon.utils.truth_fsm import parse_truth_fsm, validate_truth_fsm

    truth_path = PROJECT_ROOT / "docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/truth.md"
    md = truth_path.read_text(encoding="utf-8")
    fsm = parse_truth_fsm(md)
    assert fsm["five_tuple_present"], "five-tuple must be present"
    result = validate_truth_fsm(fsm)
    assert not result["blocked"], f"FSM must validate: {result['findings']}"
    assert "verified" in fsm.get("terminal_states") or "flagged" in fsm.get("terminal_states"), "verified/flagged terminal"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_recalc_independent,
        test_compare_match,
        test_compare_deviation_flagged,
        test_audit_record,
        test_no_verdict_authority,
        test_pending_when_data_missing,
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
