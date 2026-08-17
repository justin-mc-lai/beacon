from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.utils.artifact_paths import execution_file_output
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_workflow_start_should_write_v111_execution_governance_artifacts(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Execution Governance Draft",
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
    for name in (
        "config.json",
        "source.json",
        "git-alignment.json",
        "delivery-manifest.json",
        "change-impact.json",
    ):
        assert execution_file_output(tmp_path, "v1.1.1", name).exists(), name

    manifest = json.loads(execution_file_output(tmp_path, "v1.1.1", "delivery-manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("affected_projects")
    assert any(item.get("type") == "config" for item in manifest.get("deliverables", []))

    change_impact = json.loads(execution_file_output(tmp_path, "v1.1.1", "change-impact.json").read_text(encoding="utf-8"))
    tasks = {str(item.get("task", "")) for item in change_impact.get("tasks", []) if isinstance(item, dict)}
    assert "publish-config-draft" in tasks
    assert "publish-source-draft" in tasks
    assert "publish-git-alignment-draft" in tasks
