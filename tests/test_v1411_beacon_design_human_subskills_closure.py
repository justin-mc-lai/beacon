from __future__ import annotations

from pathlib import Path

import pytest

from beacon.utils.design_contract import DESIGN_ROUTES, build_design_route_payload, design_route_contract


VERSION = "v1.4.11"
FEATURE = "beacon-design-human-subskills-closure-contract"
AGENT_SKILL_ROOT = Path(".agents/skills")
PACKAGED_SKILL_ROOT = Path("skills/beacon")
DESIGN_SUBSKILLS = {
    "explore": {
        "skill": "beacon-design-explore",
        "upstream": "vibe-to-ui",
        "required_text": ["beacon design route explore", "design direction candidates"],
    },
    "extract": {
        "skill": "beacon-design-extract",
        "upstream": "vibe-to-ui",
        "required_text": ["beacon design route extract", "screenshot", "inference"],
    },
    "system": {
        "skill": "beacon-design-system",
        "upstream": "ui-ux-pro-max",
        "required_text": ["beacon design route system", "component system", "accessibility"],
    },
    "review": {
        "skill": "beacon-design-review",
        "upstream": "impeccable",
        "required_text": ["beacon design route review", "UX findings"],
    },
    "polish": {
        "skill": "beacon-design-polish",
        "upstream": "impeccable",
        "required_text": ["beacon design route polish", "ship-readiness"],
    },
    "library": {
        "skill": "beacon-design-library",
        "upstream": "awesome-design-md",
        "required_text": ["beacon design route library", "reference-only", "not an execution skill"],
    },
    "bootstrap": {
        "skill": "beacon-design-bootstrap",
        "upstream": "upstream-compatibility",
        "required_text": ["beacon design route bootstrap", "capability-admission-only", "release_verdict=false"],
    },
    "simplify": {
        "skill": "beacon-design-simplify",
        "upstream": "beacon-native",
        "required_text": ["beacon design route simplify", "lazy_user_axiom", "core_scenario_extraction", "no external upstream"],
    },
}


pytestmark = [pytest.mark.current_contract]


def _skill_path(root: Path, skill: str) -> Path:
    return root / skill / "SKILL.md"


def _skill_text(root: Path, skill: str) -> str:
    path = _skill_path(root, skill)
    assert path.exists(), f"missing skill file: {path}"
    return path.read_text(encoding="utf-8")


def _assert_skill_exists_in_both_roots(skill: str) -> None:
    assert _skill_path(AGENT_SKILL_ROOT, skill).exists()
    assert _skill_path(PACKAGED_SKILL_ROOT, skill).exists()


def _assert_subskill(intent: str) -> None:
    spec = DESIGN_SUBSKILLS[intent]
    skill = spec["skill"]
    payload = build_design_route_payload(Path("."), VERSION, FEATURE, intent=intent)

    assert payload["route"] == skill
    assert payload["intent"] == intent
    assert payload["upstream"] == spec["upstream"]
    assert payload["boundary"]["support_only"] is True
    assert payload["boundary"]["truth_source"] is False
    assert payload["boundary"]["gate_source"] is False
    assert payload["boundary"]["lifecycle_stage"] is False
    _assert_skill_exists_in_both_roots(skill)

    for root in (AGENT_SKILL_ROOT, PACKAGED_SKILL_ROOT):
        text = _skill_text(root, skill)
        assert f"name: {skill}" in text
        for required in spec["required_text"]:
            assert required in text


def test_aggregate_design_skill_remains_support_only() -> None:
    for root in (AGENT_SKILL_ROOT, PACKAGED_SKILL_ROOT):
        text = _skill_text(root, "beacon-design")

        assert "support-only" in text
        assert "not a truth source" in text
        assert "not a gate source" in text
        assert "not a new lifecycle stage" in text


def test_explore_subskill_maps_to_explore_route() -> None:
    _assert_subskill("explore")


def test_extract_subskill_maps_to_extract_route() -> None:
    _assert_subskill("extract")


def test_system_subskill_maps_to_system_route() -> None:
    _assert_subskill("system")


def test_review_subskill_maps_to_review_route() -> None:
    _assert_subskill("review")


def test_polish_subskill_maps_to_polish_route() -> None:
    _assert_subskill("polish")


def test_library_subskill_is_reference_only() -> None:
    _assert_subskill("library")
    payload = build_design_route_payload(Path("."), VERSION, FEATURE, intent="library")

    assert payload["boundary"]["reference_only"] is True


def test_bootstrap_subskill_is_capability_admission_only() -> None:
    _assert_subskill("bootstrap")
    payload = build_design_route_payload(Path("."), VERSION, FEATURE, intent="bootstrap")

    assert payload["boundary"]["capability_admission_only"] is True


def test_all_design_subskills_declare_support_boundaries() -> None:
    required = [
        "not a truth source",
        "not a gate source",
        "not a new lifecycle stage",
        "not a release verdict",
    ]
    for spec in DESIGN_SUBSKILLS.values():
        for root in (AGENT_SKILL_ROOT, PACKAGED_SKILL_ROOT):
            text = _skill_text(root, spec["skill"])
            for item in required:
                assert item in text


def test_accepted_design_facts_have_truth_binding_routes() -> None:
    required = [
        "beacon prototype adapt",
        "beacon change",
        "--refreeze-chain",
        "beacon implement",
    ]
    for spec in DESIGN_SUBSKILLS.values():
        for root in (AGENT_SKILL_ROOT, PACKAGED_SKILL_ROOT):
            text = _skill_text(root, spec["skill"])
            for item in required:
                assert item in text


def test_installed_subskills_match_design_contract_routes() -> None:
    contract = design_route_contract(Path("."), VERSION, feature=FEATURE)
    expected_skill_names = {route["route"] for route in contract["routes"].values()}

    assert set(DESIGN_SUBSKILLS) == set(contract["routes"])
    assert expected_skill_names == {spec["skill"] for spec in DESIGN_SUBSKILLS.values()}
    for skill in expected_skill_names:
        _assert_skill_exists_in_both_roots(skill)


def test_design_runtime_routes_are_not_expanded() -> None:
    assert set(DESIGN_ROUTES) == {"explore", "extract", "system", "review", "polish", "library", "bootstrap", "simplify"}
    assert len(DESIGN_ROUTES) == 8

def test_simplify_subskill_maps_to_simplify_route() -> None:
    _assert_subskill("simplify")
    payload = build_design_route_payload(Path("."), VERSION, FEATURE, intent="simplify")
    assert payload["upstream"] == "beacon-native"


def test_simplify_route_has_five_first_principles_capabilities() -> None:
    payload = build_design_route_payload(Path("."), VERSION, FEATURE, intent="simplify")
    expected = [
        "lazy_user_axiom",
        "core_scenario_extraction",
        "engineer_abstraction_detection",
        "information_deduplication",
        "complexity_burden_score",
    ]
    assert payload["capabilities"] == expected
    assert len(payload["capabilities"]) == 5


def test_simplify_subskill_declares_support_boundaries() -> None:
    required = [
        "not a truth source",
        "not a gate source",
        "not a new lifecycle stage",
        "not a release verdict",
    ]
    for root in (AGENT_SKILL_ROOT, PACKAGED_SKILL_ROOT):
        text = _skill_text(root, "beacon-design-simplify")
        for item in required:
            assert item in text
        assert "beacon-native" in text
        assert "no external upstream" in text


def test_simplify_skill_md_contains_operator_command() -> None:
    for root in (AGENT_SKILL_ROOT, PACKAGED_SKILL_ROOT):
        text = _skill_text(root, "beacon-design-simplify")
        assert "beacon design route simplify" in text
        assert "lazy_user_axiom" in text
        assert "first principles" in text.lower() or "First Principles" in text


def test_simplify_route_in_design_routes_and_subskill_installed() -> None:
    assert "simplify" in DESIGN_ROUTES
    assert DESIGN_ROUTES["simplify"]["route"] == "beacon-design-simplify"
    assert DESIGN_ROUTES["simplify"]["upstream"] == "beacon-native"
    _assert_skill_exists_in_both_roots("beacon-design-simplify")

