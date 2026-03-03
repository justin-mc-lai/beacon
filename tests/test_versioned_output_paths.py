"""Versioned output path contract tests."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_think_should_persist_version_scoped_progress_file(tmp_path: Path):
    result = _invoke(["think", "start", "Versioned Think", "--project", str(tmp_path), "--version", "v3.2.1"])
    assert result.exit_code == 0

    assert (tmp_path / ".beacon" / "state" / "think-progress" / "v3.2.1.json").exists()
    # Keep backward compatibility for legacy readers.
    assert (tmp_path / ".beacon" / "state" / "think-progress.json").exists()


def test_user_story_prd_and_test_case_should_write_to_versioned_docs_roots(tmp_path: Path):
    us = _invoke(["user-story", "create", "Versioned Feature", "--project", str(tmp_path), "--version", "v3.2.1"])
    assert us.exit_code == 0
    prd = _invoke(["prd", "create", "Versioned Feature", "--project", str(tmp_path), "--version", "v3.2.1"])
    assert prd.exit_code == 0
    tc = _invoke(["test-case", "create", "Versioned Feature", "--project", str(tmp_path), "--version", "v3.2.1"])
    assert tc.exit_code == 0

    slug = "versioned-feature"
    assert (tmp_path / "docs" / "product" / "v3.2.1" / "user-story" / f"{slug}.md").exists()
    assert (tmp_path / "docs" / "beacon" / "v3.2.1" / "user-story" / f"{slug}.md").exists()
    assert (tmp_path / "docs" / "product" / "v3.2.1" / "prd" / f"{slug}.md").exists()
    assert (tmp_path / "docs" / "beacon" / "v3.2.1" / "prd" / f"{slug}.md").exists()
    assert (tmp_path / "docs" / "product" / "v3.2.1" / "qa" / "test-cases" / f"{slug}.md").exists()
    assert (tmp_path / "docs" / "beacon" / "v3.2.1" / "qa" / "test-cases" / f"{slug}.md").exists()
    assert (
        tmp_path / "docs" / "product" / "v3.2.1" / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json"
    ).exists()
    assert (
        tmp_path / "docs" / "beacon" / "v3.2.1" / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json"
    ).exists()

