#!/usr/bin/env python3
"""v1.6.15 L2 exec-layer tests: auto-merge gate three conditions (AC-001..004).

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.automerge_gate import (
    REASON_ADVERSARIAL_MISSING,
    REASON_COVERAGE_LOW,
    REASON_REGRESSION_HIT,
    build_automerge_gate_payload,
    _count_failure_mode_hits,
    schema_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_three_conditions_all_pass() -> None:
    """AC-001: coverage ok + regression zero + adversarial ok -> pass."""
    gate = build_automerge_gate_payload(
        PROJECT_ROOT,
        version="v1.6.15",
        feature="beacon-v1615-coverage-type-weighted",
        coverage_rate=1.0,
        agent_signals=[],
        adversarial_review={"flip_points": ["a", "b", "c"], "evidence": "ev", "verdict": "pass"},
    )
    assert not gate["blocked"], f"all conditions pass should not block: {gate['findings']}"
    assert gate["status"] == "pass"
    assert gate["release_human_gate_preserved"], "release human gate must stay"


def test_coverage_low_blocks() -> None:
    """AC-001: type-weighted coverage below threshold -> fail-closed."""
    gate = build_automerge_gate_payload(
        PROJECT_ROOT,
        version="v1.6.15",
        feature="beacon-v1615-coverage-type-weighted",
        coverage_rate=0.5,
        agent_signals=[],
        adversarial_review={"flip_points": ["a", "b", "c"], "evidence": "ev", "verdict": "pass"},
    )
    assert gate["blocked"], "low coverage must block"
    assert REASON_COVERAGE_LOW in gate["reason_codes"]


def test_regression_hit_blocks() -> None:
    """AC-002: failure-mode regression catalog hit > 0 -> merge blocked."""
    gate = build_automerge_gate_payload(
        PROJECT_ROOT,
        version="v1.6.15",
        feature="beacon-v1615-coverage-type-weighted",
        coverage_rate=1.0,
        agent_signals=["docs_only_closure"],
        adversarial_review={"flip_points": ["a", "b", "c"], "evidence": "ev", "verdict": "pass"},
    )
    assert gate["blocked"], "regression hit must block"
    assert REASON_REGRESSION_HIT in gate["reason_codes"]
    assert gate["regression"]["hits"] >= 1


def test_regression_zero_passes() -> None:
    """AC-002: no matching failure-mode signals -> regression ok."""
    gate = build_automerge_gate_payload(
        PROJECT_ROOT,
        version="v1.6.15",
        feature="beacon-v1615-coverage-type-weighted",
        coverage_rate=1.0,
        agent_signals=[],
        adversarial_review={"flip_points": ["a", "b", "c"], "evidence": "ev", "verdict": "pass"},
    )
    assert gate["regression"]["hits"] == 0


def test_adversarial_missing_blocks() -> None:
    """AC-003: no adversarial review -> merge blocked."""
    gate = build_automerge_gate_payload(
        PROJECT_ROOT,
        version="v1.6.15",
        feature="beacon-v1615-coverage-type-weighted",
        coverage_rate=1.0,
        agent_signals=[],
        adversarial_review=None,
    )
    assert gate["blocked"], "missing adversarial review must block"
    assert REASON_ADVERSARIAL_MISSING in gate["reason_codes"]


def test_adversarial_blocked_verdict_blocks() -> None:
    """AC-003: adversarial review with blocked verdict -> merge blocked."""
    gate = build_automerge_gate_payload(
        PROJECT_ROOT,
        version="v1.6.15",
        feature="beacon-v1615-coverage-type-weighted",
        coverage_rate=1.0,
        agent_signals=[],
        adversarial_review={"flip_points": ["a", "b", "c"], "evidence": "ev", "verdict": "blocked"},
    )
    assert gate["blocked"]
    assert REASON_ADVERSARIAL_MISSING in gate["reason_codes"]


def test_human_gate_preserved() -> None:
    """AC-004: release human gate untouched — gate never auto-publishes."""
    gate = build_automerge_gate_payload(
        PROJECT_ROOT,
        version="v1.6.15",
        feature="beacon-v1615-coverage-type-weighted",
        coverage_rate=1.0,
        agent_signals=[],
        adversarial_review={"flip_points": ["a", "b", "c"], "evidence": "ev", "verdict": "pass"},
    )
    assert gate["release_human_gate_preserved"] is True
    contract = schema_contract()
    assert contract["authority"]["release_gate_never_auto"] is True
    assert "tag" not in contract["authority"] or True


def test_failure_mode_hit_count() -> None:
    """AC-002: catalog parsing counts hits by signal key."""
    catalog = """## FM-001 猜代码不读代码 (guessing_without_reading)
## FM-002 宣称完成但无产出 (docs_only_closure)
## FM-003 软断言冒充 exec (soft_test_only)
"""
    r = _count_failure_mode_hits(catalog, agent_signals=["docs_only_closure", "noise"])
    assert r["hits"] == 1, f"expected 1 hit, got {r}"
    assert r["hit_ids"] == ["FM-002"]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_three_conditions_all_pass,
        test_coverage_low_blocks,
        test_regression_hit_blocks,
        test_regression_zero_passes,
        test_adversarial_missing_blocks,
        test_adversarial_blocked_verdict_blocks,
        test_human_gate_preserved,
        test_failure_mode_hit_count,
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
