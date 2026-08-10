from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "beacon"
CORE_SKILLS = [
    "beacon-gen-truth",
    "beacon-gen-implement",
    "beacon-eval-qa",
    "beacon-eval-release",
    "beacon-pln-source",
    "beacon-gov-doctor",
]
REQUIRED_SECTIONS = [
    "## Beacon v1.6.0 共享 Preamble",
    "HARD GATE:",
    "## 职责",
    "## 边界",
    "## 路由",
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
        assert "resolver-selected truth" in text
        assert "docs/beacon/<version>/research/<feature-slug>.md" in text
        assert "route recommendation" in text


def test_skill_surface_cannot_write_truth():
    for skill_dir in CORE_SKILLS:
        text = _skill_text(skill_dir)
        lowered = text.lower()
        assert "freeform write truth" not in lowered
        assert "freeform writeback" not in lowered
        assert "hard gate" in lowered
        assert "placeholder" in lowered
