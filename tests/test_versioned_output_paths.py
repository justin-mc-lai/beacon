"""Versioned output path contract tests."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app

from tests.support.fail_closed import assert_missing_prd_truth


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_think_should_persist_version_scoped_progress_file(tmp_path: Path):
    result = _invoke(["think", "start", "Versioned Think", "--project", str(tmp_path), "--version", "v3.2.1"])
    assert result.exit_code == 0

    assert (tmp_path / ".beacon" / "state" / "think-progress" / "v3.2.1.json").exists()
    # Keep backward compatibility for legacy readers.
    assert (tmp_path / ".beacon" / "state" / "think-progress.json").exists()


def test_user_story_should_fail_closed_without_prd_truth(tmp_path: Path):
    us = _invoke(["user-story", "create", "Versioned Feature", "--project", str(tmp_path), "--version", "v3.2.1"])
    assert_missing_prd_truth(us, feature="Versioned Feature")


def test_prd_and_test_case_should_write_to_versioned_docs_roots(tmp_path: Path):
    feature = "Versioned Feature"
    version = "v3.2.1"
    slug = "versioned-feature"

    prd = _invoke(["prd", "create", feature, "--project", str(tmp_path), "--version", version])
    assert prd.exit_code == 0
    us = _invoke(["user-story", "create", feature, "--project", str(tmp_path), "--version", version])
    assert us.exit_code == 0
    tc = _invoke(["test-case", "create", feature, "--project", str(tmp_path), "--version", version])
    assert tc.exit_code == 0

    assert (tmp_path / "docs" / "beacon" / version / "user-story" / f"{slug}.md").exists()
    assert (tmp_path / "docs" / "beacon" / version / "prd" / f"{slug}.md").exists()
    assert (tmp_path / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.md").exists()
    assert (
        tmp_path / "docs" / "beacon" / version / ".machine" / "qa" / f"{slug}.ac-test-matrix.json"
    ).exists()
