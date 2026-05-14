from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "beacon"
ACTIVE_LINE = "v1.4.6"
CORE_SKILLS = [
    "beacon-prd",
    "beacon-user-story",
    "beacon-test-case",
    "beacon-implement",
    "beacon-qa",
    "beacon-release",
]


def _skill_text(skill_dir: str) -> str:
    return (SKILL_ROOT / skill_dir / "SKILL.md").read_text(encoding="utf-8")


def test_no_mixed_old_version_lines():
    for skill_dir in CORE_SKILLS:
        text = _skill_text(skill_dir)
        assert "current v1.3.9 runtime surface" not in text
        assert "v1.3.12 requirement closure docs" not in text


def test_operator_rule_matches_runtime_and_docs():
    for skill_dir in CORE_SKILLS:
        text = _skill_text(skill_dir)
        assert ACTIVE_LINE in text, skill_dir
        assert f"docs/beacon/{ACTIVE_LINE}/" in text or f"docs/beacon/{ACTIVE_LINE}" in text or f"`{ACTIVE_LINE}` docs line" in text


def test_runtime_docs_host_lines_are_consistent():
    for skill_dir in CORE_SKILLS:
        text = _skill_text(skill_dir)
        assert "Compatibility" in text or "compatibility" in text
        assert ACTIVE_LINE in text


def test_test_case_skill_does_not_mix_v145_and_v146_docs_lines() -> None:
    text = _skill_text("beacon-test-case")
    assert "v1.4.5 docs line" not in text
    assert "docs/beacon/v1.4.6/" in text


def test_version_alignment_precedes_surface_thickening():
    for skill_dir in CORE_SKILLS:
        text = _skill_text(skill_dir)
        v14_index = text.index(ACTIVE_LINE)
        inputs_index = text.index("## Inputs Contract")
        assert v14_index < inputs_index, skill_dir
