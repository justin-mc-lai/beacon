"""Integration tests for beacon init context-file behavior."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(tmp_path: Path, args: list[str]):
    result = runner.invoke(app, ["init", "--project", str(tmp_path), *args])
    assert result.exit_code == 0, result.stdout
    return result, json.loads(result.stdout)


def test_init_defaults_create_managed_context_blocks(tmp_path: Path):
    _, payload = _invoke(tmp_path, ["--apply"])

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "<!-- BEACON:START -->" in claude
    assert "<!-- BEACON:START -->" in agents

    context_actions = [a for a in payload["actions"] if a.get("scope") == "context"]
    assert context_actions
    assert all(a.get("context_setup") == "true" for a in context_actions)


def test_init_second_run_is_idempotent(tmp_path: Path):
    _invoke(tmp_path, ["--apply"])
    first_claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    first_agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")

    _invoke(tmp_path, ["--apply"])
    second_claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    second_agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")

    assert first_claude == second_claude
    assert first_agents == second_agents


def test_init_force_refreshes_managed_block_content(tmp_path: Path):
    _invoke(tmp_path, ["--apply"])
    claude_path = tmp_path / "CLAUDE.md"
    stale_content = (
        "# CLAUDE\n\n"
        "<!-- BEACON:START -->\n"
        "<!-- BEACON:VERSION:stale -->\n"
        "old guidance\n"
        "<!-- BEACON:END -->\n"
    )
    claude_path.write_text(stale_content, encoding="utf-8")

    _invoke(tmp_path, ["--apply", "--force"])
    refreshed = claude_path.read_text(encoding="utf-8")

    assert refreshed != stale_content
    assert "<!-- BEACON:START -->" in refreshed
    assert "<!-- BEACON:VERSION:stale -->" not in refreshed


def test_init_dry_run_does_not_write_context_files(tmp_path: Path):
    _invoke(tmp_path, ["--dry-run"])

    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / "AGENTS.md").exists()


def test_init_without_context_guidance_preserves_compatibility_behavior(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("# Existing\n\nkeep me\n", encoding="utf-8")

    _invoke(tmp_path, ["--apply", "--without-context-guidance"])

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")

    assert claude == "# Existing\n\nkeep me\n"
    assert "<!-- BEACON-MANAGED -->" in agents
    assert "<!-- BEACON:START -->" not in agents
