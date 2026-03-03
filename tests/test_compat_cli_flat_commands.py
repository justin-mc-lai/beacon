"""Compatibility tests for PTK-style flat CLI commands."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from beacon import __toolkit_version__
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_nested_subcommands_still_work_as_baseline():
    """Current nested subcommand style remains executable."""
    result = _invoke(["doctor", "diagnose"])
    assert result.exit_code == 0
    assert "Beacon Doctor" in result.stdout


def test_flat_doctor_json_should_work():
    result = _invoke(["doctor", "--json"])
    assert result.exit_code == 0
    json.loads(result.stdout)


def test_flat_status_board_should_work():
    result = _invoke(["status", "--board"])
    assert result.exit_code == 0
    assert "Status" in result.stdout


def test_flat_report_human_should_work():
    result = _invoke(["report", "--human", "latest"])
    assert result.exit_code == 0
    assert "Run ID" in result.stdout or "Summary" in result.stdout


def test_flat_init_dry_run_should_work():
    result = _invoke(["init", "--dry-run"])
    assert result.exit_code == 0


def test_flat_resume_should_work():
    result = _invoke(["resume", "run-123"])
    assert result.exit_code in (0, 2)
    assert "Missing command" not in result.stdout


def test_flat_gate_stage_should_work():
    result = _invoke(["gate", "think", "--json"])
    assert result.exit_code in (0, 2)
    assert "No such command" not in result.stdout


def test_work_alias_should_exist():
    result = _invoke(["work", "demo-feature"])
    assert result.exit_code in (0, 2)
    assert "No such command" not in result.stdout


def test_global_version_flag_should_work():
    result = _invoke(["--version"])
    assert result.exit_code == 0
    assert __toolkit_version__.lower() in result.stdout.lower()
