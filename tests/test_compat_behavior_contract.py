"""Compatibility tests for core PTK behavior contracts on Beacon."""

from __future__ import annotations

from pathlib import Path
from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_current_run_subcommand_invocation_baseline():
    """Current implementation accepts nested `run workflow <type>`."""
    result = _invoke(["run", "workflow", "workflow", "--mode", "dry-run", "--feature", "demo"])
    assert result.exit_code == 0
    assert "Running workflow in dry-run mode" in result.stdout


def test_run_should_persist_state_artifacts(tmp_path: Path):
    result = _invoke(
        [
            "run",
            "workflow",
            "--mode",
            "dry-run",
            "--feature",
            "demo",
            "--project-root",
            str(tmp_path),
        ]
    )
    assert result.exit_code == 0
    runs_dir = tmp_path / ".beacon" / "runs"
    assert runs_dir.exists()
    assert list(runs_dir.glob("*/state.json"))
    assert list(runs_dir.glob("*/events.jsonl"))


def test_report_machine_should_emit_structured_payload():
    result = _invoke(["report", "--machine", "latest"])
    assert result.exit_code == 0
    text = result.stdout.strip()
    assert text.startswith("{") and '"events"' in text and '"tool_calls"' in text


def test_feedback_sync_should_write_requirement_feedback(tmp_path: Path):
    # Target contract: feedback writes a requirement-feedback artifact under state.
    result = _invoke(["feedback", "sync", "latest", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    expected = tmp_path / ".beacon" / "state" / "requirement-feedback"
    assert expected.exists()


def test_resume_should_return_run_state_json(tmp_path: Path):
    run_dir = tmp_path / ".beacon" / "runs" / "run-001"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "state.json").write_text('{"run_id":"run-001","status":"completed"}', encoding="utf-8")

    result = _invoke(["resume", "run-001", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    assert '"run_id"' in result.stdout and '"status"' in result.stdout
