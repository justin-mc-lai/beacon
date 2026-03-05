"""v1.0.3 workflow interactive HUD and closure contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.runtime import save_run_state
from beacon.utils.workflow_memory import append_lifecycle_event, compute_workflow_progress


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


def _invoke(args: list[str], *, input_text: str | None = None):
    return runner.invoke(app, args, input=input_text)


def _latest_run_id(project_root: Path) -> str:
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs
    return runs[-1]


def _extract_json(stdout: str) -> dict:
    start = stdout.find("{")
    assert start >= 0, stdout
    return json.loads(stdout[start:])


def test_workflow_hud_command_should_emit_required_sections_and_snapshot(tmp_path: Path):
    planned = _invoke(["workflow", "start", "HUD Feature", "--project", str(tmp_path)])
    assert planned.exit_code == 0
    run_id = _latest_run_id(tmp_path)

    hud = _invoke(["workflow", "hud", "--project", str(tmp_path), "--run-id", run_id, "--json"])
    assert hud.exit_code == 0
    payload = _extract_json(hud.stdout)
    for key in ("workflow_progress", "stage_status", "blockers", "quality", "memory"):
        assert key in payload
    assert payload["run_id"] == run_id

    snapshot = tmp_path / ".beacon" / "state" / "workflow-hud" / f"{run_id}.json"
    assert snapshot.exists()


def test_workflow_auto_skip_should_not_mark_completed_without_closure(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Skip Gate Feature",
            "--auto",
            "--skip",
            "gate",
            "--project",
            str(tmp_path),
            *IMPLEMENTATION_ARGS,
            *VERIFY_PASS_ARGS,
        ]
    )
    assert result.exit_code == 0
    run_id = _latest_run_id(tmp_path)
    state = json.loads((tmp_path / ".beacon" / "runs" / run_id / "state.json").read_text(encoding="utf-8"))
    assert state.get("status") != "completed"
    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    assert progress.get("closure_complete") is False


def test_interactive_reject_then_pause_should_record_lifecycle(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Interactive Pause Feature",
            "--auto",
            "--interactive",
            "--project",
            str(tmp_path),
            *IMPLEMENTATION_ARGS,
            *VERIFY_PASS_ARGS,
        ],
        input_text="1\nn\n5\n",
    )
    assert result.exit_code == 0
    run_id = _latest_run_id(tmp_path)
    run_state = json.loads((tmp_path / ".beacon" / "runs" / run_id / "state.json").read_text(encoding="utf-8"))
    assert run_state.get("status") == "paused"
    assert "1) 执行 next_stage（single-step）" in result.stdout
    lifecycle = json.loads((tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json").read_text(encoding="utf-8"))
    events = [row for row in lifecycle.get("items", []) if row.get("run_id") == run_id]
    names = {row.get("event") for row in events}
    assert "human_checkpoint_rejected" in names
    assert "workflow_paused" in names


def test_resume_continue_should_match_workflow_continue_non_interactive(tmp_path: Path):
    planned_a = _invoke(["workflow", "start", "Resume A", "--project", str(tmp_path)])
    planned_b = _invoke(["workflow", "start", "Resume B", "--project", str(tmp_path)])
    assert planned_a.exit_code == 0
    assert planned_b.exit_code == 0
    runs = sorted(
        [p.name for p in (tmp_path / ".beacon" / "runs").iterdir() if p.is_dir() and (p / "state.json").exists()]
    )
    run_a, run_b = runs[-2], runs[-1]

    res_a = _invoke(
        ["resume", "continue", "--run-id", run_a, "--project-root", str(tmp_path), "--no-interactive", "--no-hud"]
    )
    res_b = _invoke(["workflow", "continue", "--project", str(tmp_path), "--run-id", run_b, "--no-interactive", "--no-hud"])
    assert res_a.exit_code == 0
    assert res_b.exit_code == 0

    progress_a = compute_workflow_progress(tmp_path, run_id=run_a)
    progress_b = compute_workflow_progress(tmp_path, run_id=run_b)
    assert progress_a.get("stages", {}).get("think", {}).get("status") == "completed"
    assert progress_b.get("stages", {}).get("think", {}).get("status") == "completed"


def test_failed_stage_should_be_recoverable_in_progress_computation(tmp_path: Path):
    run_id = "run-retry-demo"
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": "Retry Feature",
            "version": "v1.0.3",
            "status": "running",
        },
    )
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_failed", source="test")
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_started", source="test")
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_context_injected", source="test")
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_finished", source="test")
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="memory_writeback", source="test")

    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    think = progress.get("stages", {}).get("think", {})
    assert think.get("status") == "completed"
    assert think.get("retry_count") == 1
