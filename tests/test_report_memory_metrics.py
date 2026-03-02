"""Report/status/resume memory metrics tests."""

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
    assert runs
    return runs[-1]


def test_report_status_resume_should_expose_memory_metrics(tmp_path: Path):
    result = _invoke(["workflow", "start", "Metrics Feature", "--auto", "--project", str(tmp_path)])
    assert result.exit_code == 0
    run_id = _latest_run_id(tmp_path)

    machine = _invoke(["report", "--project-root", str(tmp_path), "--machine", "latest"])
    assert machine.exit_code == 0
    payload = json.loads(machine.stdout)
    assert "memory_metrics" in payload
    assert isinstance(payload["memory_metrics"], dict)

    board = _invoke(["status", "--board", "--project-root", str(tmp_path)])
    assert board.exit_code == 0
    assert "memory.closure_complete" in board.stdout

    resumed = _invoke(["resume", run_id, "--project-root", str(tmp_path)])
    assert resumed.exit_code == 0
    resumed_payload = json.loads(resumed.stdout)
    assert "memory_metrics" in resumed_payload
