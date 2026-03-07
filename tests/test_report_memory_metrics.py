"""Report/status/resume memory metrics tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERIFY_PASS_ARGS = [
    "--implementation-command",
    "python3 -c \"print('impl')\"",
    "--verify-scope",
    "unit",
    "--verify-unit-command",
    "python3 -c \"print('ok')\"",
]


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _latest_run_id(project_root: Path) -> str:
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs
    return runs[-1]


def _extract_run_id(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("Run ID:"):
            return line.split(":", 1)[1].strip()
    return ""


def test_report_status_resume_should_expose_memory_metrics(tmp_path: Path):
    result = _invoke(["workflow", "start", "Metrics Feature", "--auto", "--project", str(tmp_path), *VERIFY_PASS_ARGS])
    assert result.exit_code == 0
    run_id = _latest_run_id(tmp_path)

    machine = _invoke(["report", "--project-root", str(tmp_path), "--machine", "latest"])
    assert machine.exit_code == 0
    payload = json.loads(machine.stdout)
    assert "memory_metrics" in payload
    assert isinstance(payload["memory_metrics"], dict)
    assert "coverage_metrics" in payload

    board = _invoke(["status", "--board", "--project-root", str(tmp_path)])
    assert board.exit_code == 0
    assert "memory.closure_complete" in board.stdout
    assert "coverage.story" in board.stdout

    resumed = _invoke(["resume", run_id, "--project-root", str(tmp_path)])
    assert resumed.exit_code == 0
    resumed_payload = json.loads(resumed.stdout)
    assert "memory_metrics" in resumed_payload


def test_memory_metrics_default_run_should_prefer_workflow_run_over_release_run(tmp_path: Path):
    result = _invoke(["workflow", "start", "Metrics Feature", "--auto", "--project", str(tmp_path), *VERIFY_PASS_ARGS])
    assert result.exit_code == 0

    # Add a later release event run-id to emulate mixed lifecycle streams.
    release = _invoke(["release", "create", "v1.2.3", "--project", str(tmp_path)])
    assert release.exit_code == 0

    machine = _invoke(["report", "--project-root", str(tmp_path), "--machine", "latest"])
    assert machine.exit_code == 0
    payload = json.loads(machine.stdout)
    metrics = payload.get("memory_metrics", {})
    selected = str(metrics.get("run_id", ""))
    assert selected.startswith("run-"), f"expected workflow run-id, got {selected}"


def test_report_should_support_version_filtered_memory_progress(tmp_path: Path):
    run_a = _invoke(
        ["workflow", "start", "Feature A", "--auto", "--version", "v1.0.0", "--project", str(tmp_path)]
        + VERIFY_PASS_ARGS
    )
    assert run_a.exit_code == 0
    run_a_id = _extract_run_id(run_a.stdout) or _latest_run_id(tmp_path)

    run_b = _invoke(
        ["workflow", "start", "Feature B", "--auto", "--version", "v1.0.1", "--project", str(tmp_path)]
        + VERIFY_PASS_ARGS
    )
    assert run_b.exit_code == 0
    run_b_id = _extract_run_id(run_b.stdout) or _latest_run_id(tmp_path)

    machine = _invoke(
        ["report", "--project-root", str(tmp_path), "--machine", "--version", "v1.0.0", "latest"]
    )
    assert machine.exit_code == 0
    payload = json.loads(machine.stdout)
    assert payload.get("workflow_progress", {}).get("version") == "v1.0.0"
    if run_a_id and run_b_id and run_a_id != run_b_id:
        assert payload.get("run_id") == run_a_id


def test_status_board_should_show_next_stage_with_version_filter(tmp_path: Path):
    result = _invoke(["workflow", "start", "Feature C", "--project", str(tmp_path), "--version", "v2.0.0"])
    assert result.exit_code == 0

    board = _invoke(["status", "--board", "--project-root", str(tmp_path), "--version", "v2.0.0"])
    assert board.exit_code == 0
    assert "memory.next_stage: think" in board.stdout


def test_status_should_use_same_resolved_run_for_terminal_status_and_progress(tmp_path: Path):
    run_a = _invoke(
        ["workflow", "start", "Stable Feature", "--auto", "--version", "v3.0.0", "--project", str(tmp_path)]
        + VERIFY_PASS_ARGS
        + ["--confirm-execute", "--confirm-execute-second"]
    )
    assert run_a.exit_code == 0

    run_b = _invoke(["workflow", "start", "Latest Incomplete", "--version", "v3.0.1", "--project", str(tmp_path)])
    assert run_b.exit_code == 0

    board = _invoke(["status", "--board", "--project-root", str(tmp_path), "--version", "v3.0.0", "--verbose"])
    assert board.exit_code == 0
    assert "workflow.version: v3.0.0" in board.stdout
    assert "gate.terminal_status: completed" in board.stdout


def test_report_should_write_summary_into_requested_version_execution_dir(tmp_path: Path):
    started = _invoke(
        [
            "workflow",
            "start",
            "Report Version",
            "--auto",
            "--project",
            str(tmp_path),
            "--version",
            "v2.3.4",
            "--confirm-execute",
            "--confirm-execute-second",
            *VERIFY_PASS_ARGS,
        ]
    )
    assert started.exit_code == 0

    machine = _invoke(
        [
            "report",
            "--project-root",
            str(tmp_path),
            "--machine",
            "--version",
            "v2.3.4",
            "--write-summary",
            "latest",
        ]
    )
    assert machine.exit_code == 0

    summary_path = tmp_path / "docs" / "beacon" / "v2.3.4" / "execution" / "summary.json"
    legacy_path = tmp_path / "docs" / "beacon" / "v1.0.0" / "execution" / "summary.json"
    assert summary_path.exists()
    assert not legacy_path.exists()


def test_report_default_mode_should_not_write_summary_files(tmp_path: Path):
    started = _invoke(
        [
            "workflow",
            "start",
            "Report No Side Effect",
            "--auto",
            "--project",
            str(tmp_path),
            "--version",
            "v2.5.0",
            "--confirm-execute",
            "--confirm-execute-second",
            *VERIFY_PASS_ARGS,
        ]
    )
    assert started.exit_code == 0

    machine = _invoke(["report", "--project-root", str(tmp_path), "--machine", "--version", "v2.5.0", "latest"])
    assert machine.exit_code == 0

    summary_path = tmp_path / "docs" / "beacon" / "v2.5.0" / "execution" / "summary.json"
    assert not summary_path.exists()
