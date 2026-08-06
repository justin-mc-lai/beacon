"""Issue #14 batch 2: remaining CLI write commands refuse runtime-named docs on external repos."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon import __toolkit_version__
from beacon.main import app
from beacon.utils.doctor_orchestrator import (
    run_package_upgrade,
    run_version_aggregate_projection_repair,
)

TOOLKIT = str(__toolkit_version__)
runner = CliRunner()


def _external_existing(tmp_path: Path) -> Path:
    docs = tmp_path / "docs" / "beacon" / "v0.0.5"
    docs.mkdir(parents=True)
    (docs / "SUMMARY.md").write_text("# v0.0.5\n", encoding="utf-8")
    return tmp_path


def _poison_onboarding(root: Path) -> None:
    state = root / ".beacon" / "state"
    state.mkdir(parents=True)
    (state / "project-onboarding.json").write_text(
        json.dumps({"docs_version": TOOLKIT, "runtime_version": TOOLKIT}, indent=2) + "\n",
        encoding="utf-8",
    )


def _assert_blocked(result) -> None:
    assert result.exit_code == 2, result.output
    assert "dual-axis" in result.output


def test_plan_start_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["plan", "start", "utterance", "--project", str(root), "--version", TOOLKIT],
    )
    _assert_blocked(result)


def test_freeze_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["freeze", "feature-slug", "--project", str(root), "--version", TOOLKIT],
    )
    _assert_blocked(result)


def test_reopen_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["reopen", "feature-slug", "--project", str(root), "--version", TOOLKIT],
    )
    _assert_blocked(result)


def test_gate_release_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["gate", "release", "--project-root", str(root), "--version", TOOLKIT],
    )
    _assert_blocked(result)


def test_release_create_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["release", "create", TOOLKIT, "--project", str(root)],
    )
    _assert_blocked(result)


def test_archive_plan_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["archive", "plan", "--project-root", str(root), "--version", TOOLKIT],
    )
    _assert_blocked(result)


def test_goal_run_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["goal", "run", "ship the feature", "--project", str(root), "--version", TOOLKIT],
    )
    assert result.exit_code == 2, result.output
    assert "dual_axis_collapse_external" in result.output


def test_materialize_feature_package_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["materialize-feature-package", "demo", "--project", str(root), "--version", TOOLKIT],
    )
    _assert_blocked(result)


def test_brainstorm_auto_blocks_poisoned_onboarding(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    _poison_onboarding(root)
    result = runner.invoke(
        app,
        ["brainstorm", "create", "topic", "--project", str(root)],
    )
    _assert_blocked(result)


def test_evolution_summary_blocks_runtime_docs_version(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = runner.invoke(
        app,
        ["evolution-summary", "create", TOOLKIT, "--project", str(root)],
    )
    _assert_blocked(result)


def test_doctor_package_upgrade_blocks_external_collapse(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = run_package_upgrade(project_root=str(root), version=TOOLKIT, dry_run=True)
    assert result.exit_code == 2
    assert result.payload["status"] == "BLOCKED"
    assert result.payload["reason_code"] == "dual_axis_collapse_external"


def test_doctor_version_aggregate_repair_blocks_external_collapse(tmp_path: Path) -> None:
    root = _external_existing(tmp_path)
    result = run_version_aggregate_projection_repair(
        project_root=str(root),
        version=TOOLKIT,
        feature="demo",
        overwrite_feature_projection=False,
    )
    assert result.exit_code == 2
    assert result.payload["status"] == "BLOCKED"
    assert result.payload["reason_code"] == "dual_axis_collapse_external"
