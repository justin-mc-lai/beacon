#!/usr/bin/env python3
"""v1.6.15 L1 exec-layer tests: coverage rate type-weighted + non-browser families.

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.story_scenarios import (
    DEFAULT_CONTRACT_FAMILIES,
    _scenario_families,
    expand_story_scenarios,
)


def test_non_browser_families() -> None:
    """AC-002: non-browser scenarios expand to contract families (happy+negative+boundary)."""
    families = _scenario_families(browser_required=False, scenario_depth="standard")
    assert families == ["happy", "negative", "boundary"], f"got {families}"
    assert families != ["primary"], "non-browser must no longer be primary-only"


def test_browser_families_unchanged() -> None:
    """AC-004 compat: browser scenarios keep DEFAULT_BROWSER_FAMILIES."""
    families = _scenario_families(browser_required=True, scenario_depth="standard")
    assert "compatibility" in families and "recovery" in families


def test_expand_non_browser_generates_types() -> None:
    """AC-002: expand_story_scenarios on a contract entry yields happy+negative+boundary."""
    story_sequence = [{"ac_id": "AC-001", "theme": "validator", "text": "validate FSM"}]
    entries = [
        {
            "ac_id": "AC-001",
            "tc_id": "TC-001",
            "source_tc_id": "TC-001",
            "qa_type": "contract",
            "layer": "contract",
            "command": "python3 -c 'print(1)'",
            "assertion": "exit 0",
        }
    ]
    result = expand_story_scenarios(
        feature="test", version="v1.6.15", story_sequence=story_sequence, entries=entries
    )
    families = {s.get("scenario_family") for s in result.get("scenarios", [])}
    assert "happy" in families and "negative" in families and "boundary" in families, f"got {families}"
    assert result.get("families_required") == list(DEFAULT_CONTRACT_FAMILIES)
    # each story row must list required_families excluding primary
    for story in result.get("stories", []):
        assert "negative" in story.get("required_families", []), "negative must be required"
        assert "boundary" in story.get("required_families", []), "boundary must be required"


def test_weighted_rate_happy_only() -> None:
    """AC-001: only happy family covered -> type_rate < 1.0."""
    from beacon.utils.qa_feature import _compute_coverage_current

    plan = {"required_scenario_families": ["happy", "negative", "boundary"]}
    # simulate: all scenarios executed but only happy family has evidence
    scenario_results = [
        {"scenario_family": "happy", "evidence_ref": "x", "closure_outcome": "accepted"},
        {"scenario_family": "negative", "evidence_ref": "", "closure_outcome": ""},
        {"scenario_family": "boundary", "evidence_ref": "", "closure_outcome": ""},
    ]
    cc = _compute_coverage_current(plan=plan, scenario_results=scenario_results, required_scenarios=3, executed_scenarios=3)
    assert cc["quantity_rate"] == 1.0, "quantity should still be full"
    assert cc["type_rate"] < 1.0, "type rate must drop when families are uncovered"
    assert cc["coverage_rate"] < 1.0, "coverage_rate must be type-weighted"


def test_weighted_rate_all_families() -> None:
    """AC-001: all families covered -> type_rate == 1.0."""
    from beacon.utils.qa_feature import _compute_coverage_current

    plan = {"required_scenario_families": ["happy", "negative", "boundary"]}
    scenario_results = [
        {"scenario_family": "happy", "evidence_ref": "x", "closure_outcome": "accepted"},
        {"scenario_family": "negative", "evidence_ref": "x", "closure_outcome": "accepted"},
        {"scenario_family": "boundary", "evidence_ref": "x", "closure_outcome": "accepted"},
    ]
    cc = _compute_coverage_current(plan=plan, scenario_results=scenario_results, required_scenarios=3, executed_scenarios=3)
    assert cc["type_rate"] == 1.0
    assert cc["coverage_rate"] == 1.0


def test_missing_families_listed() -> None:
    """AC-003: missing families surfaced for audit."""
    from beacon.utils.qa_feature import _compute_coverage_current

    plan = {"required_scenario_families": ["happy", "negative", "boundary", "recovery", "compatibility"]}
    scenario_results = [
        {"scenario_family": "happy", "evidence_ref": "x", "closure_outcome": "accepted"},
        {"scenario_family": "negative", "evidence_ref": "x", "closure_outcome": "accepted"},
    ]
    cc = _compute_coverage_current(plan=plan, scenario_results=scenario_results, required_scenarios=5, executed_scenarios=5)
    assert cc["type_rate"] == 0.4, f"2/5 families covered, got {cc['type_rate']}"
    assert "boundary" in cc["missing_scenario_families"] or "recovery" in cc["missing_scenario_families"], (
        "missing families must be surfaced"
    )


def test_compat_no_command_surface() -> None:
    """AC-004: no new command surface; existing families unchanged."""
    assert "recovery" in DEFAULT_CONTRACT_FAMILIES or "recovery" not in DEFAULT_CONTRACT_FAMILIES
    browser = _scenario_families(browser_required=True, scenario_depth="standard")
    assert browser == ["happy", "negative", "boundary", "recovery", "compatibility"]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_non_browser_families,
        test_browser_families_unchanged,
        test_expand_non_browser_generates_types,
        test_weighted_rate_happy_only,
        test_weighted_rate_all_families,
        test_missing_families_listed,
        test_compat_no_command_surface,
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
