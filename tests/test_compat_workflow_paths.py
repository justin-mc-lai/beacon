"""Compatibility tests for workflow path/version behavior."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.workflow import (
    _matrix_path_candidates,
    _qa9_matrix_path_candidates,
    _stage_output_candidates,
    ensure_output_dirs,
)
from beacon.utils.artifact_paths import machine_qa_file, qa_docs_file
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_ensure_output_dirs_creates_canonical_docs_root_only(tmp_path: Path):
    ensure_output_dirs(tmp_path, "v1.0.0")
    assert (tmp_path / "docs" / "beacon" / "v1.0.0").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.0.0" / "execution").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.0.0" / "user-story").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.0.0" / "prd").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.0.0" / "qa" / "test-cases").exists()
    assert not (tmp_path / "docs" / "product").exists()
    assert (tmp_path / ".beacon" / "state").exists()


def test_stage_output_candidates_should_only_use_beacon_docs(tmp_path: Path):
    candidates = _stage_output_candidates(tmp_path, "test-case", "登录功能", "v1.1.1")
    assert candidates[0] == tmp_path / "docs" / "beacon" / "v1.1.1" / "qa" / "test-cases" / "登录功能.md"
    assert all("docs/product" not in str(path) for path in candidates)
    assert candidates[1] == machine_qa_file(tmp_path, "v1.1.1", "登录功能.ac-test-matrix.json")
    assert candidates[2] == machine_qa_file(tmp_path, "v1.1.1", "登录功能.qa9-matrix.json")


def test_matrix_candidate_lists_should_only_return_beacon_paths(tmp_path: Path):
    ac_candidates = _matrix_path_candidates(tmp_path, "登录功能", "v1.1.1")
    qa9_candidates = _qa9_matrix_path_candidates(tmp_path, "登录功能", "v1.1.1")

    assert ac_candidates == [
        machine_qa_file(tmp_path, "v1.1.1", "登录功能.ac-test-matrix.json"),
        qa_docs_file(tmp_path, "v1.1.1", "登录功能.ac-test-matrix.json"),
    ]
    assert qa9_candidates == [
        machine_qa_file(tmp_path, "v1.1.1", "登录功能.qa9-matrix.json"),
        qa_docs_file(tmp_path, "v1.1.1", "登录功能.qa9-matrix.json"),
    ]


def test_workflow_auto_should_materialize_stage_outputs(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "login-feature",
            "--auto",
            "--project",
            str(tmp_path),
            "--verify-scope",
            "unit",
            "--verify-unit-command",
            "python3 -c \"print('ok')\"",
            "--implementation-command",
            "python3 -c \"print('impl')\"",
        ]
    )
    assert result.exit_code == 0
    # At least one stage artifact should exist.
    artifacts = list((tmp_path / "docs").glob("**/*.md"))
    assert artifacts, "workflow auto should create artifacts, but none were generated"


def test_workflow_status_should_detect_beacon_docs(tmp_path: Path):
    us_dir = tmp_path / "docs" / "beacon" / "v1.0.0" / "user-story"
    us_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / "feature-a.md").write_text("# ok\n", encoding="utf-8")

    result = _invoke(["workflow", "status", "--project", str(tmp_path), "--version", "v1.0.0"])
    assert result.exit_code == 0
    assert "user-story: Completed" in result.stdout


def test_workflow_gate_should_pass_when_required_artifacts_exist(tmp_path: Path):
    root = tmp_path / "docs" / "beacon" / "v1.0.0"
    (root / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "prd").mkdir(parents=True, exist_ok=True)
    (root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / "user-story" / "f.md").write_text("ok\n", encoding="utf-8")
    (root / "prd" / "f.md").write_text("ok\n", encoding="utf-8")
    (root / "qa" / "test-cases" / "f.md").write_text("ok\n", encoding="utf-8")
    state = tmp_path / ".beacon" / "state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "think-progress.json").write_text('{"topic":"x"}', encoding="utf-8")
    (tmp_path / ".beacon" / "gate-config.json").write_text('{"mode":"normal"}', encoding="utf-8")

    result = _invoke(["workflow", "gate", "--project", str(tmp_path), "--version", "v1.0.0"])
    assert result.exit_code == 0
    assert "GATE RESULT: PASS" in result.stdout
