from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

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
    exec_dir = tmp_path / "docs" / "beacon" / "v1.1.1" / "execution"
    for name in ("config.json", "source.json", "git-alignment.json"):
        assert (exec_dir / name).exists()
    config = json.loads((exec_dir / "config.json").read_text(encoding="utf-8"))
    assert config["strict_mode"] is True
