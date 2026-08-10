"""v1.0.3 workflow lifecycle attempt/skipped contracts."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.runtime import save_run_state
from beacon.utils.workflow_memory import append_lifecycle_event, compute_workflow_progress


def test_lifecycle_attempt_metadata_should_increment_and_link_superseded(tmp_path: Path):
    run_id = "run-attempt-001"
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": "Attempt Feature",
            "version": "v1.0.3",
            "status": "running",
        },
    )

    first = append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_started", source="test")
    second = append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_started", source="test")

    assert first.get("attempt_seq") == 1
    assert second.get("attempt_seq") == 2
    assert second.get("attempt_id") == "think@attempt-2"
    assert second.get("supersedes_event_id") == first.get("event_id")


def test_latest_attempt_status_should_win_over_previous_failure(tmp_path: Path):
    run_id = "run-attempt-002"
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": "Recover Feature",
            "version": "v1.0.3",
            "status": "running",
        },
    )

    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_started", source="test")
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_failed", source="test")

    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_started", source="test")
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_context_injected", source="test")
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="stage_finished", source="test")
    append_lifecycle_event(tmp_path, run_id=run_id, stage="think", event="memory_writeback", source="test")

    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    prd = progress.get("stages", {}).get("prd", {})
    assert prd.get("status") == "completed"
    assert prd.get("attempt_seq") == 2
    assert prd.get("retry_count") == 1


def test_stage_skipped_should_be_reported_and_gate_stage_should_exist(tmp_path: Path):
    run_id = "run-attempt-003"
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": "Skip Feature",
            "version": "v1.0.3",
            "status": "running",
        },
    )

    append_lifecycle_event(tmp_path, run_id=run_id, stage="gate", event="stage_skipped", source="test")
    progress = compute_workflow_progress(tmp_path, run_id=run_id)

    assert "release" in progress.get("stages", {})
    release = progress.get("stages", {}).get("release", {})
    assert release.get("status") == "skipped"
    assert progress.get("closure_complete") is False
