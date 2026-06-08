from __future__ import annotations

import json
from pathlib import Path

from beacon import __version__


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HOST_SKILLS = (
    "beacon-planner-brainstorm",
    "beacon-planner-source-driven",
    "beacon-generator-truth-package",
    "beacon-generator-implementation",
    "beacon-evaluator-qa",
    "beacon-evaluator-release",
    "beacon-governor-router",
    "beacon-governor-doctor",
)
OLD_HOST_ALIASES = (
    "using-beacon",
    "beacon-prd",
    "beacon-user-story",
    "beacon-test-case",
    "beacon-implement",
    "beacon-qa",
    "beacon-release",
    "beacon-brainstorm",
)


def test_v131_host_skill_pack_should_exist_under_packaged_beacon_root():
    base = ROOT / "skills" / "beacon"
    for name in PUBLIC_HOST_SKILLS:
        skill_path = base / name / "SKILL.md"
        assert skill_path.exists(), f"missing host skill: {name}"
        text = skill_path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert f"name: {name}" in text
        assert "description:" in text
        assert "Beacon v1.6.0 共享 Preamble" in text
        assert "HARD GATE:" in text
    for old_name in OLD_HOST_ALIASES:
        assert not (base / old_name / "SKILL.md").exists(), f"old alias should not exist: {old_name}"


def test_codex_install_doc_should_target_packaged_beacon_skill_root():
    install_doc = ROOT / ".codex" / "INSTALL.md"
    assert install_doc.exists()
    text = install_doc.read_text(encoding="utf-8")
    assert "/absolute/path/to/beacon/skills/beacon" in text
    assert "~/.agents/skills/beacon" in text
    assert 'ln -s /absolute/path/to/beacon/skills/beacon ~/.codex/skills/beacon' not in text
    assert "beacon-planner-*" in text
    assert "beacon-generator-*" in text
    assert "beacon-evaluator-*" in text
    assert "beacon-governor-*" in text


def test_claude_plugin_metadata_should_exist_for_beacon_host_pack():
    plugin = ROOT / ".claude-plugin" / "plugin.json"
    assert plugin.exists()
    payload = json.loads(plugin.read_text(encoding="utf-8"))
    assert payload["name"] == "beacon"
    assert payload["version"] == __version__
    assert "skills" in " ".join(payload.get("keywords", []))


def test_packaged_beacon_metadata_should_match_current_package_version():
    metadata = ROOT / "skills" / "beacon" / "metadata.json"
    assert metadata.exists()
    payload = json.loads(metadata.read_text(encoding="utf-8"))
    assert payload["name"] == "beacon"
    assert payload["version"] == "v1.6.0"
    assert payload["source_kind"] == "migrated_v160_harness_taxonomy_preserve_skill_content"


def test_v131_docs_should_reference_host_skill_pack_and_public_skill_names():
    summary = (ROOT / "docs" / "beacon" / "v1.6.0" / "SUMMARY.md").read_text(encoding="utf-8")
    index_doc = (ROOT / "docs" / "beacon" / "v1.6.0" / "execution" / "index.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs" / "beacon" / "v1.6.0" / "execution" / "architecture-blueprint.md").read_text(encoding="utf-8")
    boundaries = (ROOT / "docs" / "beacon" / "v1.6.0" / "execution" / "boundaries.md").read_text(encoding="utf-8")

    assert "skill harness taxonomy" in summary.lower()
    assert "project-skill-qa-evolution-blueprint.md" in index_doc
    assert "host-visible skills" in architecture
    assert "`skills/beacon/`: packaged host-visible skills." in architecture
    assert "beacon-<harness>-<function>" in boundaries
    assert "Old host-visible skill aliases are not part of the v1.6.0 skill package." in boundaries


def test_packaged_beacon_skill_should_describe_v131_host_visible_subskills():
    text = (ROOT / "skills" / "beacon" / "SKILL.md").read_text(encoding="utf-8")
    assert "This package is the canonical `skills/beacon/` host-visible Beacon skill package for Codex and Claude." in text
    assert "v1.6.0 is a breaking skill-surface migration" in text
    assert "## Harness Routing" in text
    assert "## Hard Gates" in text
    for name in PUBLIC_HOST_SKILLS:
        assert f"`{name}`" in text
    for old_name in OLD_HOST_ALIASES:
        assert not (ROOT / "skills" / "beacon" / old_name).exists()
