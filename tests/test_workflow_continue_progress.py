"""Workflow continue/progress tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.workflow_memory import compute_workflow_progress


runner = CliRunner()
VERIFY_PASS_ARGS = [
    "--verify-scope",
    "unit",
    "--verify-unit-command",
    "python3 -c \"print('ok')\"",
]
IMPLEMENTATION_ARGS = [
    "--implementation-command",
    "python3 -c \"print('impl')\"",
]


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _latest_run_id(project_root: Path) -> str:
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs
    return runs[-1]


def test_workflow_manual_start_should_only_plan_without_stage_execution(tmp_path: Path):
    result = _invoke(["workflow", "start", "Continue Feature", "--project", str(tmp_path)])
    assert result.exit_code == 0

    run_id = _latest_run_id(tmp_path)
    lifecycle = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    payload = json.loads(lifecycle.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    stage_events = [
        item
        for item in items
        if item.get("run_id") == run_id
        and item.get("stage") in ("prd", "user-story", "test-case", "prototype", "implement", "qa", "release")
    ]
    assert stage_events == []

    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    assert progress.get("next_stage") == "prd"
    assert progress.get("closure_complete") is False


def test_workflow_continue_should_execute_single_next_stage(tmp_path: Path):
    planned = _invoke(["workflow", "start", "Continue Feature", "--project", str(tmp_path)])
    assert planned.exit_code == 0
    run_id = _latest_run_id(tmp_path)

    result = _invoke(["workflow", "continue", "--project", str(tmp_path), "--run-id", run_id])
    assert result.exit_code == 0

    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    stages = progress.get("stages", {})
    assert stages.get("prd", {}).get("status") == "completed"
    assert progress.get("next_stage") == "user-story"
    assert progress.get("closure_complete") is False


def test_workflow_continue_auto_should_close_remaining_stages(tmp_path: Path):
    planned = _invoke(["workflow", "start", "Continue Feature", "--project", str(tmp_path)])
    assert planned.exit_code == 0
    run_id = _latest_run_id(tmp_path)

    result = _invoke(
        [
            "workflow",
            "continue",
            "--project",
            str(tmp_path),
            "--run-id",
            run_id,
            "--auto",
            *IMPLEMENTATION_ARGS,
            *VERIFY_PASS_ARGS,
        ]
    )
    assert result.exit_code == 0

    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    assert progress.get("closure_complete") is True
    assert progress.get("next_stage") is None
    assert "NEXT STEP SELECTOR" in result.stdout


def test_workflow_auto_should_block_when_verify_status_is_not_passed(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Verify Failure Feature",
            "--auto",
            "--project",
            str(tmp_path),
            "--verify-scope",
            "unit",
            "--verify-unit-command",
            "python3 -c \"import sys; sys.exit(1)\"",
            *IMPLEMENTATION_ARGS,
        ]
    )
    assert result.exit_code != 0

    run_id = _latest_run_id(tmp_path)
    run_state = json.loads((tmp_path / ".beacon" / "runs" / run_id / "state.json").read_text(encoding="utf-8"))
    assert run_state.get("status") == "blocked"
    assert run_state.get("reason") == "qa_failed"

    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    assert progress.get("stages", {}).get("qa", {}).get("status") == "failed"
