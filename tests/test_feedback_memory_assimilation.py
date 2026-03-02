"""Feedback -> memory assimilation tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_run(project_root: Path, run_id: str) -> None:
    run_dir = project_root / ".beacon" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "state.json").write_text(
        json.dumps({"run_id": run_id, "status": "completed"}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_feedback_sync_should_assimilate_to_memory_and_dedupe(tmp_path: Path):
    run_id = "run-001"
    _prepare_run(tmp_path, run_id)

    first = _invoke(["feedback", "sync", run_id, "--project-root", str(tmp_path)])
    assert first.exit_code == 0
    second = _invoke(["feedback", "sync", run_id, "--project-root", str(tmp_path)])
    assert second.exit_code == 0

    feedback_file = tmp_path / ".beacon" / "state" / "requirement-feedback" / f"{run_id}.json"
    assert feedback_file.exists()

    memory_path = tmp_path / ".beacon" / "memory" / "project-insights.json"
    assert memory_path.exists()
    memory_payload = json.loads(memory_path.read_text(encoding="utf-8"))
    rows = [
        item
        for item in memory_payload.get("insights", [])
        if item.get("source") == "feedback.sync" and item.get("source_session_id") == run_id
    ]
    assert len(rows) == 1, "feedback assimilation should avoid duplicate memory entries"

    lifecycle = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    lifecycle_payload = json.loads(lifecycle.read_text(encoding="utf-8"))
    events = [
        item
        for item in lifecycle_payload.get("items", [])
        if item.get("run_id") == run_id and item.get("event") == "feedback_memory_assimilated"
    ]
    assert len(events) == 1, "feedback lifecycle event should be deduped"

