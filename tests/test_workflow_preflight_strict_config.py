from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.utils.artifact_paths import execution_file_output
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_workflow_start_should_materialize_execution_governance_files(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Preflight Governance",
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.1",
            "--auto",
            "--no-interactive",
            "--skip",
            "implementation,verify,gate",
            "--confirm-execute",
            "--confirm-execute-second",
        ]
    )
    assert result.exit_code == 0, result.stdout
    for name in ("config.json", "source.json", "git-alignment.json"):
        assert execution_file_output(tmp_path, "v1.1.1", name).exists()
    config = json.loads(execution_file_output(tmp_path, "v1.1.1", "config.json").read_text(encoding="utf-8"))
    assert config["strict_mode"] is True
