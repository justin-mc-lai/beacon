from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGED_SKILL = ROOT / "skills" / "beacon" / "beacon-change-refreeze" / "SKILL.md"
AGENT_SKILL = ROOT / ".agents" / "skills" / "beacon-change-refreeze" / "SKILL.md"
SKILL_PATHS = (PACKAGED_SKILL, AGENT_SKILL)


def _skill_text(path: Path = PACKAGED_SKILL) -> str:
    return path.read_text(encoding="utf-8")


def test_change_refreeze_skill_files_exist() -> None:
    for path in SKILL_PATHS:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").startswith("---\n")


def test_change_refreeze_skill_declares_refreeze_chain_command() -> None:
    for path in SKILL_PATHS:
        text = _skill_text(path)
        assert "beacon change ... --refreeze-chain" in text
        assert "--refreeze-chain" in text


def test_change_refreeze_skill_declares_full_closure_chain() -> None:
    for path in SKILL_PATHS:
        text = _skill_text(path)
        assert "change -> prd -> user-story -> test-case -> requirement_clarity -> freeze" in text


def test_change_refreeze_skill_declares_non_stage_non_truth_non_gate() -> None:
    for path in SKILL_PATHS:
        text = _skill_text(path).lower()
        assert "not a lifecycle stage" in text
        assert "not a truth source" in text
        assert "not a gate source" in text


def test_change_refreeze_skill_does_not_execute_delivery_or_direct_truth_writes() -> None:
    for path in SKILL_PATHS:
        text = _skill_text(path)
        assert "does not execute implementation, QA, release, or direct canonical truth writes" in text
        assert "does not write canonical PRD, user-story, or test-case truth directly" in text


def test_change_refreeze_skill_supports_stable_human_matching() -> None:
    for path in SKILL_PATHS:
        text = _skill_text(path)
        for marker in [
            "change 一键冻结",
            "change refreeze",
            "重新冻结",
            "refreeze-chain",
            "post-freeze requirement closure",
        ]:
            assert marker in text


def test_deep_and_change_docs_route_to_change_refreeze_skill() -> None:
    docs = [
        ROOT / "skills" / "beacon" / "beacon-deep" / "SKILL.md",
        ROOT / ".agents" / "skills" / "beacon-deep" / "SKILL.md",
        ROOT / "skills" / "beacon" / "beacon-change" / "SKILL.md",
        ROOT / ".agents" / "skills" / "beacon-change" / "SKILL.md",
        ROOT / "docs" / "beacon" / "v1.4.7" / "change" / "beacon-v1.4.7-deep-lightweight-lineage-projection-contract.md",
        ROOT / "docs" / "beacon" / "v1.4.7" / "change" / "beacon-v1.4.7-change-refreeze-one-shot-requirement-closure.md",
    ]
    for path in docs:
        assert "beacon-change-refreeze" in path.read_text(encoding="utf-8"), path


def test_change_refreeze_skill_uses_single_existing_machine_route() -> None:
    for path in SKILL_PATHS:
        text = _skill_text(path)
        assert "does not create a second refreeze implementation" in text
        assert "state changes only occur through `beacon change ... --refreeze-chain`" in text


def test_change_refreeze_skill_is_installed_by_claude_skill_installer() -> None:
    installer = (ROOT / "scripts" / "install_claude_skills.sh").read_text(encoding="utf-8")
    assert '"beacon-change-refreeze"' in installer


def test_main_beacon_skill_routes_one_shot_refreeze_to_stable_skill() -> None:
    text = (ROOT / "skills" / "beacon" / "SKILL.md").read_text(encoding="utf-8")
    assert "`beacon-change-refreeze`" in text
    assert "accepted post-freeze one-shot refreeze closure -> `beacon-change-refreeze`" in text
    assert "`beacon-change-refreeze` remains a change-family support route to `beacon change ... --refreeze-chain`" in text
