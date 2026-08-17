"""Workflow lifecycle memory loop tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _latest_run_id(project_root: Path) -> str:
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs, "expected workflow run state"
    return runs[-1]


def test_workflow_auto_should_create_lifecycle_memory_loop(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Lifecycle Memory Feature",
            "--auto",
            "--project",
            str(tmp_path),
            "--verify-scope",
            "unit",
            "--verify-unit-command",
            "python3 -c \"print('ok')\"",
            "--implementation-command",
            "python3 -c \"print('impl')\"",
        ]
    )
    assert result.exit_code == 0

    run_id = _latest_run_id(tmp_path)
    lifecycle_path = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    assert lifecycle_path.exists()
    payload = json.loads(lifecycle_path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    assert items

    for stage in ("prd", "user-story", "test-case", "implement", "qa", "release"):
        stage_events = [i for i in items if i.get("run_id") == run_id and i.get("stage") == stage]
        names = {i.get("event") for i in stage_events}
        assert "stage_started" in names
        assert "stage_context_injected" in names
        assert "stage_finished" in names
        assert "memory_writeback" in names

        context_file = tmp_path / ".beacon" / "state" / "workflow-memory" / run_id / f"{stage}-context.json"
        assert context_file.exists(), f"missing context for {stage}"

    # Writebacks should be reflected in the current memory-v1 projection.
    memory_v1 = tmp_path / ".beacon" / "memory" / "memory-v1.json"
    assert memory_v1.exists()
    memory_payload = json.loads(memory_v1.read_text(encoding="utf-8"))
    assert memory_payload.get("items")
