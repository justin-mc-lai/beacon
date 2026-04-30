from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_workflow_run(project_root: Path, *, version: str = "v1.1.5", feature: str = "My Feature") -> str:
    result = _invoke(["workflow", "start", feature, "--project", str(project_root), "--version", version])
    assert result.exit_code == 0, result.stdout
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs
    return runs[-1]


def test_help_json_without_run_should_recommend_freeze_before_implementation(tmp_path: Path):
    result = _invoke(["help", "--json", "--project-root", str(tmp_path), "--version", "v1.1.5", "--feature", "My Feature"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["next_step"]["action"] == "freeze"
    assert "beacon freeze" in payload["next_step"]["command"]
    assert isinstance(payload.get("scores"), dict)


def test_help_json_with_planned_workflow_should_recommend_freeze_until_revision_is_frozen(tmp_path: Path):
    run_id = _seed_workflow_run(tmp_path)
    result = _invoke(["help", "--json", "--project-root", str(tmp_path), "--version", "v1.1.5", "--feature", "My Feature", "--run-id", run_id])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["run_id"] == run_id
    assert payload["next_step"]["action"] == "freeze"
    assert "beacon freeze" in payload["next_step"]["command"]
    assert payload["current_stage"] == "prd"


def test_help_human_output_should_include_scores_and_next_step(tmp_path: Path):
    result = _invoke(["help", "--project-root", str(tmp_path), "--version", "v1.1.5", "--feature", "My Feature"])
    assert result.exit_code == 0, result.stdout
    assert "Beacon Help / Next Step" in result.stdout
    assert "test_score" in result.stdout
    assert "command :" in result.stdout
