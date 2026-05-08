from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "beacon"
CORE_SKILLS = [
    "beacon-prd",
    "beacon-user-story",
    "beacon-test-case",
    "beacon-implement",
    "beacon-qa",
    "beacon-release",
]
REQUIRED_SECTIONS = [
    "## Inputs Contract",
    "## Decision Protocol",
    "## Anti-Inertia Notes",
    "## Learning Notes",
    "## Backstop CLI",
]


def _skill_text(skill_dir: str) -> str:
    return (SKILL_ROOT / skill_dir / "SKILL.md").read_text(encoding="utf-8")


def test_core_skills_are_in_scope():
    for skill_dir in CORE_SKILLS:
        assert (SKILL_ROOT / skill_dir / "SKILL.md").exists(), skill_dir


def test_stable_sections_present():
    for skill_dir in CORE_SKILLS:
        text = _skill_text(skill_dir)
        for section in REQUIRED_SECTIONS:
            assert section in text, f"{skill_dir} missing {section}"


def test_host_readable_contract():
    for skill_dir in CORE_SKILLS:
        text = _skill_text(skill_dir)
        assert "`project-root`" in text or "- project-root" in text
        assert "`version`" in text or "- version" in text
        assert "`feature`" in text or "- feature" in text
        assert "Decision Protocol" in text
        assert "Backstop CLI" in text


def test_skill_surface_cannot_write_truth():
    for skill_dir in CORE_SKILLS:
        text = _skill_text(skill_dir)
        lowered = text.lower()
        assert "freeform write truth" not in lowered
        assert "freeform writeback" not in lowered
        assert "cannot override gate truth" in lowered or "cannot override gate" in lowered or "does not define completion truth" in lowered or "cannot rewrite frozen truth" in lowered
