"""Compatibility tests for workflow path/version behavior."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.workflow import ensure_output_dirs
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_ensure_output_dirs_creates_dual_docs_roots(tmp_path: Path):
    ensure_output_dirs(tmp_path, "latest")
    assert (tmp_path / "docs" / "beacon" / "latest" / "user-story").exists()
    assert (tmp_path / "docs" / "product" / "latest" / "user-story").exists()
    assert (tmp_path / ".beacon" / "state").exists()


def test_workflow_auto_should_materialize_stage_outputs(tmp_path: Path):
    result = _invoke(["workflow", "start", "登录功能", "--auto", "--project", str(tmp_path)])
    assert result.exit_code == 0
    # At least one stage artifact should exist.
    artifacts = list((tmp_path / "docs").glob("**/*.md"))
    assert artifacts, "workflow auto should create artifacts, but none were generated"


def test_workflow_status_should_detect_product_docs_when_beacon_empty(tmp_path: Path):
    us_dir = tmp_path / "docs" / "product" / "latest" / "user-story"
    us_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / "feature-a.md").write_text("# ok\n", encoding="utf-8")

    result = _invoke(["workflow", "status", "--project", str(tmp_path), "--version", "latest"])
    assert result.exit_code == 0
    assert "user-story: Completed" in result.stdout


def test_workflow_gate_should_pass_when_required_artifacts_exist(tmp_path: Path):
    root = tmp_path / "docs" / "product" / "latest"
    (root / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "prd").mkdir(parents=True, exist_ok=True)
    (root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / "user-story" / "f.md").write_text("ok\n", encoding="utf-8")
    (root / "prd" / "f.md").write_text("ok\n", encoding="utf-8")
    (root / "qa" / "test-cases" / "f.md").write_text("ok\n", encoding="utf-8")
    state = tmp_path / ".beacon" / "state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "think-progress.json").write_text('{"topic":"x"}', encoding="utf-8")

    result = _invoke(["workflow", "gate", "--project", str(tmp_path), "--version", "latest"])
    assert result.exit_code == 0
    assert "GATE RESULT: PASS" in result.stdout
