from __future__ import annotations

import json
from pathlib import Path

from beacon import __version__


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HOST_SKILLS = (
    "using-beacon",
    "beacon-prd",
    "beacon-user-story",
    "beacon-test-case",
    "beacon-prototype",
    "beacon-implement",
    "beacon-qa",
    "beacon-release",
    "beacon-help",
    "beacon-status",
    "beacon-doctor",
    "beacon-archive",
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


def test_codex_install_doc_should_target_packaged_beacon_skill_root():
    install_doc = ROOT / ".codex" / "INSTALL.md"
    assert install_doc.exists()
    text = install_doc.read_text(encoding="utf-8")
    assert "/absolute/path/to/beacon/skills/beacon" in text
    assert "~/.agents/skills/beacon" in text
    assert 'ln -s /absolute/path/to/beacon/skills/beacon ~/.codex/skills/beacon' not in text
    assert "using-beacon" in text
    assert "beacon-prd" in text
    assert "beacon-doctor" in text


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
    assert payload["version"] == __version__


def test_v131_docs_should_reference_host_skill_pack_and_public_skill_names():
    summary = (ROOT / "docs" / "beacon" / "v1.3.1" / "SUMMARY.md").read_text(encoding="utf-8")
    index_doc = (ROOT / "docs" / "beacon" / "v1.3.1" / "execution" / "index.md").read_text(encoding="utf-8")
    guide = (ROOT / "docs" / "beacon" / "v1.3.1" / "execution" / "human-minimal-usage-guide.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs" / "beacon" / "v1.3.1" / "execution" / "architecture-blueprint.md").read_text(encoding="utf-8")
    boundaries = (ROOT / "docs" / "beacon" / "v1.3.1" / "execution" / "boundaries.md").read_text(encoding="utf-8")
    blueprint = (ROOT / "docs" / "beacon" / "v1.3.1" / "execution" / "host-skill-pack-blueprint.md").read_text(encoding="utf-8")

    assert "host skill pack" in summary.lower()
    assert "./execution/host-skill-pack-blueprint.md" in summary
    assert "./host-skill-pack-blueprint.md" in index_doc
    assert "using-beacon" in guide
    assert "beacon-prd" in guide
    assert "beacon-doctor" in guide
    assert "host-visible skills" in architecture
    assert "Host-visible public skills" in boundaries
    assert "using-beacon" in blueprint
    assert "beacon-release" in blueprint


def test_packaged_beacon_skill_should_describe_v131_host_visible_subskills():
    text = (ROOT / "skills" / "beacon" / "SKILL.md").read_text(encoding="utf-8")
    assert "This package is the canonical `skills/beacon/` wrapper for Codex and Claude." in text
    assert "The public Codex / Claude surfaces are:" in text
    assert "## Current v1.3.9 Additions" in text
    for name in PUBLIC_HOST_SKILLS:
        assert f"`{name}`" in text


def test_beacon_prototype_skill_should_describe_v1310_ux_closure_contract():
    skill_text = (ROOT / "skills" / "beacon" / "beacon-prototype" / "SKILL.md").read_text(encoding="utf-8")
    assert "design-result adapter" in skill_text
    assert "ui-ux-dev" in skill_text
    assert "prototype adapt" in skill_text
    assert "truth bindings" in skill_text
    assert "legacy requirement-driven wireframe freeze bundles" in skill_text
    assert "legacy `design_context`" in skill_text
    assert "legacy `DESIGN.md`" in skill_text
    assert "apple-inspired-design-md" in skill_text
    assert "ui-ux-pro-max-skill" in skill_text
    assert "awesome-design-md" in skill_text


def test_beacon_prototype_agent_prompt_should_match_v1310_ux_closure_surface():
    agent_yaml = (ROOT / "skills" / "beacon" / "beacon-prototype" / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "Beacon Prototype Adapter" in agent_yaml
    assert "design-result adapter" in agent_yaml
    assert "ui-ux-dev" in agent_yaml
    assert "beacon prototype adapt" in agent_yaml
    assert "truth bindings" in agent_yaml
    assert "Legacy wireframe plus UX PRD closure bundles" in agent_yaml
