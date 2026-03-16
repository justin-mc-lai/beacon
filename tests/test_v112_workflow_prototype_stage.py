"""v1.1.2 prototype workflow stage contracts."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.workflow_memory import compute_workflow_progress


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _latest_run_id(project_root: Path) -> str:
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs
    return runs[-1]


def test_workflow_start_with_prototype_should_include_optional_stage(tmp_path: Path):
    result = _invoke(["workflow", "start", "Prototype Flow", "--project", str(tmp_path), "--with-prototype"])
    assert result.exit_code == 0
    run_id = _latest_run_id(tmp_path)
    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    assert "prototype" in progress.get("workflow_stages", [])
    assert "prototype" in progress.get("missing_closure_stages", [])


def test_workflow_start_without_prototype_should_keep_default_stage_chain(tmp_path: Path):
    result = _invoke(["workflow", "start", "Normal Flow", "--project", str(tmp_path)])
    assert result.exit_code == 0
    run_id = _latest_run_id(tmp_path)
    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    assert "prototype" not in progress.get("workflow_stages", [])

