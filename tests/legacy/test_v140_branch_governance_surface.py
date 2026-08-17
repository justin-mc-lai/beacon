from __future__ import annotations

from pathlib import Path

from beacon.command_catalog import CORE_COMMANDS, SUPPORTED_SUBCOMMANDS


ROOT = Path(__file__).resolve().parents[1]


def test_toolkit_skill_tier() -> None:
    host_skill = ROOT / "skills" / "beacon" / "SKILL.md"
    text = host_skill.read_text(encoding="utf-8")
    assert "`beacon-toolkit-branch-governance`" in text
    assert "doctor branch-governance show" in text

    subskill = ROOT / "skills" / "beacon" / "beacon-toolkit-branch-governance" / "SKILL.md"
    subskill_text = subskill.read_text(encoding="utf-8")
    assert "name: beacon-toolkit-branch-governance" in subskill_text
    assert "Keep this skill outside the main workflow by default." in subskill_text


def test_no_new_public_command() -> None:
    assert "branch-governance" not in SUPPORTED_SUBCOMMANDS


def test_not_new_lifecycle_stage() -> None:
    assert "branch-governance" not in CORE_COMMANDS


def test_alongside_existing_toolkits() -> None:
    assert (ROOT / "skills" / "beacon" / "beacon-toolkit-metadata" / "SKILL.md").exists()
    assert (ROOT / "skills" / "beacon" / "beacon-toolkit-lighthouse" / "SKILL.md").exists()
    assert (ROOT / "skills" / "beacon" / "beacon-toolkit-branch-governance" / "SKILL.md").exists()
    assert (ROOT / "skills" / "beacon" / "beacon-toolkit-automation" / "SKILL.md").exists()
