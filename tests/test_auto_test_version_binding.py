"""Contracts for auto-test version binding with workflow context."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_auto_test_create_should_persist_explicit_version(tmp_path: Path):
    result = _invoke(
        [
            "auto-test",
            "create",
            "unit",
            "--project",
            str(tmp_path),
            "--version",
            "v7.1.0",
            "--unit-command",
            "python3 -c \"print('ok')\"",
        ]
    )
    assert result.exit_code == 0

    payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert payload.get("version") == "v7.1.0"
    assert payload.get("execution", {}).get("version") == "v7.1.0"


def test_workflow_verify_should_pass_run_version_to_auto_test(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Version Bound Verify",
            "--project",
            str(tmp_path),
            "--auto",
            "--version",
            "v4.2.0",
            "--implementation-command",
            "python3 -c \"print('impl')\"",
            "--verify-scope",
            "unit",
            "--verify-unit-command",
            "python3 -c \"print('ok')\"",
        ]
    )
    assert result.exit_code == 0

    payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert payload.get("version") == "v4.2.0"
    assert payload.get("execution", {}).get("version") == "v4.2.0"
