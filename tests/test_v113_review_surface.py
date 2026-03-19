from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_root_help_should_hide_flat_labs_and_bridge_commands():
    result = _invoke(["--help"])
    assert result.exit_code == 0
    stdout = result.stdout
    assert "labs" in stdout
    assert "bridge" in stdout
    assert "analyze" not in stdout
    assert "team" not in stdout
    assert "ralph-bridge" not in stdout


def test_review_help_should_expose_spec_and_quality_subcommands():
    result = _invoke(["review", "--help"])
    assert result.exit_code == 0
    assert "spec" in result.stdout
    assert "quality" in result.stdout


def test_review_spec_should_write_formal_review_artifacts(tmp_path: Path):
    version = "v1.1.3"
    slug = "feature-a"
    root = tmp_path / "docs" / "beacon" / version
    (root / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "prd").mkdir(parents=True, exist_ok=True)
    (root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / "execution").mkdir(parents=True, exist_ok=True)
    (root / "user-story" / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
    (root / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (root / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (root / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json").write_text('{"entries":[]}', encoding="utf-8")
    impl = tmp_path / ".beacon" / "state"
    impl.mkdir(parents=True, exist_ok=True)
    (impl / f"implementation-{slug}.json").write_text("{}", encoding="utf-8")

    result = _invoke(["review", "spec", "feature-a", "--project", str(tmp_path), "--version", version, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["review_type"] == "spec"
    assert payload["status"] == "pass"
    assert (root / "execution" / f"review-spec-{slug}.json").exists()
    assert (root / "execution" / f"review-spec-{slug}.md").exists()

