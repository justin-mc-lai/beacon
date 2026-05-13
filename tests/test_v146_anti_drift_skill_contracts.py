from __future__ import annotations

from pathlib import Path

from beacon.utils.ceo_review_surface import run_ceo_review
from beacon.utils.skill_contracts import (
    ANTI_RATIONALIZATION_SKILLS,
    HOST_VISIBLE_SKILLS,
    SKILL_ANATOMY_V2_SECTIONS,
    build_skill_contract_report,
    public_surface_family_contract,
    support_surface_constitution,
)
from beacon.utils.support_surface_projection import build_support_surface_projection


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "beacon"
VERSION = "v1.4.6"
FEATURE = "beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces"


def _skill_text(skill_dir: str) -> str:
    return (SKILL_ROOT / skill_dir / "SKILL.md").read_text(encoding="utf-8")


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_feature_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/prd/{FEATURE}.md", "# prd\n")
    _write(root, f"docs/beacon/{VERSION}/user-story/{FEATURE}.md", "# story\n")
    _write(root, f"docs/beacon/{VERSION}/qa/test-cases/{FEATURE}.md", "# test\n")


def test_skill_anatomy_v2_is_frozen_for_key_surfaces() -> None:
    for skill_dir in HOST_VISIBLE_SKILLS:
        text = _skill_text(skill_dir)
        for section in SKILL_ANATOMY_V2_SECTIONS:
            assert section in text, f"{skill_dir} missing {section}"


def test_key_execution_and_entry_skills_require_anti_rationalization() -> None:
    for skill_dir in ANTI_RATIONALIZATION_SKILLS:
        text = _skill_text(skill_dir)
        assert "## Common Rationalizations" in text


def test_support_surface_constitution_is_unified_and_bounded() -> None:
    constitution = support_surface_constitution()
    assert constitution["members"] == ["brainstorm", "deep", "ceo-review", "design-review", "help", "status", "doctor"]
    assert constitution["boundaries"]["not_truth_source"] is True
    assert constitution["boundaries"]["not_gate_source"] is True
    assert constitution["boundaries"]["not_new_lifecycle_stage"] is True


def test_high_risk_challenge_outputs_bind_back_to_evidence_state_or_gate(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)
    payload = run_ceo_review(tmp_path, version=VERSION, feature=FEATURE, decision="reframe")

    assert payload["truth_refs"]
    assert payload["route_decision"]["target_surface"] == "beacon-change"
    assert payload["state_impact"]["writes_transaction_state"] is True
    assert payload["gate_impact"]["blocks_execution"] is True


def test_public_surface_family_has_clear_handoff_boundaries() -> None:
    families = public_surface_family_contract()
    assert families["families"]["truth"] == ["prd", "user-story", "test-case", "change"]
    assert families["families"]["execution"] == ["prototype", "implement"]
    assert families["families"]["support"] == ["brainstorm", "deep", "ceo-review", "design-review", "help", "status", "doctor"]
    assert families["families"]["gate"] == ["qa", "release"]
    assert "beacon-change" in families["handoff_rules"]["support_to_truth"]


def test_anti_drift_contracts_are_machine_checkable() -> None:
    report = build_skill_contract_report(ROOT)
    assert report["status"] == "pass"
    assert report["failure_count"] == 0


def test_philosophy_first_contract_does_not_regress_to_step_scripts() -> None:
    report = build_skill_contract_report(ROOT)
    assert all(not item["operation_script_smell"] for item in report["reports"])


def test_external_skill_methods_are_absorbed_without_runtime_dependency() -> None:
    text = _skill_text("using-beacon").lower()
    assert "do not require external skill repos" in text or "external" in text
    assert "default prerequisite" in text


def test_brainstorm_and_change_promotion_boundary_remains_explicit() -> None:
    brainstorm = _skill_text("beacon-brainstorm")
    change = _skill_text("beacon-change")
    assert "if accepted scope changes, route to `beacon-change`" in brainstorm
    assert "`beacon-change` is the host-visible router for post-freeze requirement revisions" in change


def test_anti_drift_upgrade_does_not_create_a_new_lifecycle_stage(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)
    projection = build_support_surface_projection(tmp_path, version=VERSION, feature=FEATURE)
    constitution = projection["support_surface_constitution"]
    assert constitution["boundaries"]["not_new_lifecycle_stage"] is True
