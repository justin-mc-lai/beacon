from __future__ import annotations

import json
from pathlib import Path

from beacon import __toolkit_version__
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
    assert onboarding_state["docs_version"] == "v1.1.8"
    assert onboarding_state["next_recommended_stage"] == "architecture-current-state"
    assert payload["docs_version"] == "v1.1.8"
    assert payload["runtime_version"] == __toolkit_version__
    assert payload["version_context"]["version_semantics"]["fields"]["docs_default_line"]["kind"] == "docs"


def test_init_auto_should_use_project_docs_version_but_runtime_v118_for_context(tmp_path: Path):
    # existing project docs line should stay on the project's own version
    existing = tmp_path / "docs" / "beacon" / "v0.1.0"
    (existing / "execution").mkdir(parents=True, exist_ok=True)
    (existing / "SUMMARY.md").write_text("# Existing Summary\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "init",
            "--project",
            str(tmp_path),
            "--version",
            "auto",
            "--runtime-version",
            "v1.1.8",
            "--project-mode",
            "takeover",
            "--apply",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["docs_version"] == "v0.1.0"
    assert payload["version"] == "v0.1.0"
    assert payload["runtime_version"] == "v1.1.8"
    assert payload["version_semantics"]["fields"]["runtime_version"]["kind"] == "runtime"

    assert (tmp_path / "docs" / "beacon" / "v0.1.0" / "execution" / "project-lifecycle-onboarding.md").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.1.8" / "SUMMARY.md").exists()
    onboarding_state = json.loads((tmp_path / ".beacon" / "state" / "project-onboarding.json").read_text(encoding="utf-8"))
    assert onboarding_state["docs_version"] == "v0.1.0"
    assert onboarding_state["runtime_version"] == "v1.1.8"

    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "<!-- BEACON:VERSION:v1.1.8 -->" in agents


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


def test_init_should_create_only_minimal_docs_scaffold_by_default(tmp_path: Path):
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

    version_root = tmp_path / "docs" / "beacon" / "v1.1.8"
    assert version_root.exists()
    assert (version_root / "SUMMARY.md").exists()
    assert (version_root / "execution" / "index.md").exists()
    assert (version_root / "execution" / "architecture-blueprint.md").exists()
    assert not (version_root / "prd").exists()
    assert not (version_root / "user-story").exists()
    assert not (version_root / "qa" / "test-cases").exists()
