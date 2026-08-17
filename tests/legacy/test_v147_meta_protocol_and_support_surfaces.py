from __future__ import annotations

from pathlib import Path

from beacon.utils.skill_contracts import PUBLIC_SURFACE_FAMILIES, SUPPORT_SURFACE_MEMBERS, build_skill_contract_report


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "beacon"
VERSION = "v1.4.7"


def _skill_text(skill_dir: str) -> str:
    return (SKILL_ROOT / skill_dir / "SKILL.md").read_text(encoding="utf-8")


def _ref_text(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


def test_beacon_main_skill_is_meta_protocol_not_wrapper_sprawl() -> None:
    text = _skill_text("")
    assert "## Meta-Protocol" in text
    assert "当前问题属于哪个决策面" in text
    assert "## Stable Rules" in text
    assert "## Route-Back Rules" in text
    assert "## Support Surface Constitution" in text
    assert "route by decision surface" in text.lower()
    assert "7+3 surface" not in text
    assert "## Human Surface" not in text
    assert "wrapper/manual/version note" not in text


def test_using_beacon_is_host_route_constitution() -> None:
    text = _skill_text("using-beacon")
    assert "host-native route constitution" in text
    assert "truth = promised outcome, scope, ambiguity, acceptance, frozen package revision" in text
    assert "execution = prototype handoff or implementation work against frozen truth" in text
    assert "verification/gate = evidence closure, acceptance confidence, release judgment" in text
    assert "if a support surface changes accepted scope, promise, or acceptance assumptions, route back through `beacon-change`" in text
    assert "`beacon-context-engineering`" in text
    assert "`beacon-source-driven`" in text
    assert "`beacon-doubt-review`" in text


def test_first_wave_horizontal_support_skills_are_defined() -> None:
    for skill_dir in ("beacon-context-engineering", "beacon-source-driven", "beacon-doubt-review"):
        text = _skill_text(skill_dir)
        assert text.startswith("---\n")
        assert "## Overview" in text
        assert "## Boundary" in text
        assert "## Workflow / Decision Loop" in text
        assert "## Gate Impact" in text


def test_horizontal_support_skills_remain_non_truth_non_gate_non_stage() -> None:
    for skill_dir in ("beacon-context-engineering", "beacon-source-driven", "beacon-doubt-review"):
        text = _skill_text(skill_dir).lower()
        assert "not a truth source" in text
        assert "not a gate source" in text
        assert "not a new lifecycle stage" in text
        assert "route to `beacon-change`" in text or "route back to `beacon-change`" in text


def test_second_wave_horizontal_support_skills_are_defined() -> None:
    for skill_dir in (
        "beacon-security-review",
        "beacon-performance-review",
        "beacon-documentation-adr",
        "beacon-debug-recovery",
    ):
        text = _skill_text(skill_dir)
        assert text.startswith("---\n")
        assert "## Overview" in text
        assert "## Boundary" in text
        assert "## Workflow / Decision Loop" in text
        assert "## Gate Impact" in text


def test_second_wave_horizontal_support_skills_remain_non_truth_non_gate_non_stage() -> None:
    for skill_dir in (
        "beacon-security-review",
        "beacon-performance-review",
        "beacon-documentation-adr",
        "beacon-debug-recovery",
    ):
        text = _skill_text(skill_dir).lower()
        assert "not a truth source" in text
        assert "not a gate source" in text
        assert "not a new lifecycle stage" in text
        assert "route to `beacon-change`" in text or "route back to `beacon-change`" in text


def test_lightweight_reference_package_is_present_and_marked_non_canonical() -> None:
    refs = (
        "requirement-closure-checklist.md",
        "freeze-readiness-checklist.md",
        "qa-layer-checklist.md",
        "release-blocker-taxonomy.md",
        "support-surface-routing-cheatsheet.md",
        "external-lifecycle-mapping.md",
    )
    for ref in refs:
        text = _ref_text(ref)
        assert "non-canonical support reference" in text
    main_skill = _skill_text("")
    assert "## Lightweight References" in main_skill
    assert "These references are non-canonical support material." in main_skill


def test_second_wave_lightweight_references_are_present_and_non_canonical() -> None:
    refs = (
        "research-closure-checklist.md",
        "business-flow-checklist.md",
        "state-machine-checklist.md",
    )
    for ref in refs:
        text = _ref_text(ref)
        assert "non-canonical support reference" in text
    main_skill = _skill_text("")
    assert "research-closure-checklist.md" in main_skill
    assert "business-flow-checklist.md" in main_skill
    assert "state-machine-checklist.md" in main_skill
    assert "research -> prd -> user-story -> test-case -> requirement_clarity -> freeze" in main_skill


def test_requirement_surfaces_align_to_minimal_freeze_contract() -> None:
    prd = _skill_text("beacon-prd")
    user_story = _skill_text("beacon-user-story")
    test_case = _skill_text("beacon-test-case")
    brainstorm = _skill_text("beacon-brainstorm")
    bootstrap = _skill_text("beacon-prd-bootstrap")

    assert "research -> prd -> user-story -> test-case -> requirement_clarity -> freeze" in prd
    assert "test-case -> requirement_clarity -> freeze" in user_story
    assert "research -> prd -> user-story -> test-case -> requirement_clarity -> freeze" in test_case
    assert "prd -> user-story -> test-case -> requirement_clarity -> freeze" in brainstorm
    assert "requirement_clarity" in bootstrap


def test_external_lifecycle_mapping_is_documented_without_mainline_expansion() -> None:
    text = _ref_text("external-lifecycle-mapping.md")
    assert "`agent-skills` = engineering skill library" in text
    assert "`gstack` = specialist software factory" in text
    assert "Beacon = truth / evidence / governance kernel" in text
    assert "prd -> user-story -> test-case -> implement -> qa -> release" in text
    assert "They do not:" in text
    assert "create new Beacon lifecycle stages" in text


def test_support_surface_specialist_packaging_does_not_turn_into_command_sprawl() -> None:
    host_skill = _skill_text("")
    assert "`beacon-context-engineering`" in host_skill
    assert "`beacon-source-driven`" in host_skill
    assert "`beacon-doubt-review`" in host_skill
    assert "`beacon-security-review`" in host_skill
    assert "`beacon-performance-review`" in host_skill
    assert "`beacon-documentation-adr`" in host_skill
    assert "`beacon-debug-recovery`" in host_skill
    assert "support surface" in host_skill.lower()
    assert "dozens of public commands" not in host_skill
    assert PUBLIC_SURFACE_FAMILIES["execution"] == ["prototype", "implement"]


def test_host_and_browser_tooling_story_is_more_readable_but_not_a_new_stage() -> None:
    host_skill = _skill_text("")
    assert "browser-admitted or compatibility paths such as `browser-use` remain optional capability planes" in host_skill
    assert "current planning line for this evolution theme: `docs/beacon/v1.4.7/`" in host_skill
    using = _skill_text("using-beacon")
    assert "external skill repos, plugins, or runtime packs are not Beacon's default prerequisite" in using


def test_route_explainability_distinguishes_truth_from_learning_hints() -> None:
    using = _skill_text("using-beacon")
    assert "route explanation can distinguish frozen truth and learning hint" in using
    assert "`beacon-security-review`" in using
    assert "`beacon-performance-review`" in using
    assert "`beacon-documentation-adr`" in using
    assert "`beacon-debug-recovery`" in using
    host_skill = _skill_text("")
    assert "If any support surface changes accepted scope or promise, it must route back through `beacon-change`." in host_skill
    ref = _ref_text("support-surface-routing-cheatsheet.md")
    assert "If support output changes accepted scope, promise, or acceptance assumptions, route back to `beacon-change`." in ref


def test_root_preservation_rules_hold_under_v147_surface_expansion() -> None:
    host_skill = _skill_text("").lower()
    assert "main chain stays compact" in host_skill
    assert "support surfaces are not new lifecycle stages" in host_skill
    assert "canonical truth remains versioned under `docs/beacon/<version>/`" in host_skill
    assert "qa prompt contract must follow first principles" in host_skill
    report = build_skill_contract_report(
        ROOT,
        skill_dirs=(
            "using-beacon",
            "beacon-brainstorm",
            "beacon-implement",
            "beacon-qa",
            "beacon-release",
            "beacon-context-engineering",
            "beacon-source-driven",
            "beacon-doubt-review",
            "beacon-security-review",
            "beacon-performance-review",
            "beacon-documentation-adr",
            "beacon-debug-recovery",
        ),
    )
    assert report["status"] == "pass"
    assert all(not item["operation_script_smell"] for item in report["reports"])
    assert list(SUPPORT_SURFACE_MEMBERS) == ["brainstorm", "deep", "ceo-review", "design-review", "help", "status", "doctor"]
