from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def test_init_project_mode_takeover_should_write_onboarding_artifacts(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "init",
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.8",
            "--project-mode",
            "takeover",
            "--apply",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["project_mode"] == "takeover"

    execution = tmp_path / "docs" / "beacon" / "v1.1.8" / "execution"
    assert (execution / "architecture-blueprint.md").exists()
    assert (execution / "version-evolution-blueprint.md").exists()
    assert (execution / "implementation-archive-index.md").exists()
    assert (execution / "project-lifecycle-onboarding.md").exists()

    onboarding_state = json.loads(
        (tmp_path / ".beacon" / "state" / "project-onboarding.json").read_text(encoding="utf-8")
    )
    assert onboarding_state["project_mode"] == "takeover"
    assert onboarding_state["lifecycle_adoption_level"] == 2
    assert onboarding_state["next_recommended_stage"] == "architecture-current-state"


def test_init_context_guidance_should_include_progressive_disclosure(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "init",
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.8",
            "--apply",
        ],
    )
    assert result.exit_code == 0, result.stdout
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "Read progressively in this order" in agents
    assert "execution/architecture-blueprint.md" in agents
    assert "For greenfield projects" in agents
    assert "For takeover projects" in agents
