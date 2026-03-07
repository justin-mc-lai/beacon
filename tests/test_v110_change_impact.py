"""v1.1.0 change-impact contracts."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.commands.workflow import _consume_change_impact_task
from beacon.utils.v110_baseline import record_baseline_snapshot


def _seed_docs(root: Path) -> None:
    (root / "docs" / "beacon" / "v1.1.0" / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.1.0" / "prd").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "v1.1.0" / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)

    (root / "docs" / "beacon" / "v1.1.0" / "user-story" / "feature.md").write_text("# US\n", encoding="utf-8")
    (root / "docs" / "beacon" / "v1.1.0" / "prd" / "feature.md").write_text("# PRD\n", encoding="utf-8")
    (root / "docs" / "beacon" / "v1.1.0" / "qa" / "test-cases" / "feature.ac-test-matrix.json").write_text(
        json.dumps({"schema_version": "1.0", "entries": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_spec_change_should_enqueue_doc_chain_updates(tmp_path: Path):
    _seed_docs(tmp_path)

    record_baseline_snapshot(
        tmp_path,
        run_id="run-change-impact-001",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="completed",
    )

    prd_path = tmp_path / "docs" / "beacon" / "v1.1.0" / "prd" / "feature.md"
    prd_path.write_text("# PRD\n\n- changed\n", encoding="utf-8")

    second = record_baseline_snapshot(
        tmp_path,
        run_id="run-change-impact-002",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="running",
    )

    payload = second.get("change_impact", {})
    assert payload.get("doc_chain_update_required") is True
    changed_layers = payload.get("changed_layers", [])
    assert "prd" in changed_layers
    tasks = [str(item.get("task", "")) for item in payload.get("tasks", []) if isinstance(item, dict)]
    assert "regenerate-prd" in tasks


def test_change_impact_should_be_consumed_when_stage_completed(tmp_path: Path):
    _seed_docs(tmp_path)

    record_baseline_snapshot(
        tmp_path,
        run_id="run-change-impact-consume-001",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="completed",
    )

    prd_path = tmp_path / "docs" / "beacon" / "v1.1.0" / "prd" / "feature.md"
    prd_path.write_text("# PRD\n\n- changed\n", encoding="utf-8")

    record_baseline_snapshot(
        tmp_path,
        run_id="run-change-impact-consume-002",
        version="v1.1.0",
        feature="Debug Loop",
        workflow_status="running",
    )

    impact_path = tmp_path / ".beacon" / "state" / "change-impact" / "run-change-impact-consume-002.json"
    payload_before = json.loads(impact_path.read_text(encoding="utf-8"))
    task_before = next(item for item in payload_before.get("tasks", []) if item.get("task") == "regenerate-prd")
    assert task_before.get("status") == "pending"
    assert payload_before.get("doc_chain_update_required") is True

    _consume_change_impact_task(
        tmp_path,
        run_id="run-change-impact-consume-002",
        stage="prd",
    )

    payload_after = json.loads(impact_path.read_text(encoding="utf-8"))
    task_after = next(item for item in payload_after.get("tasks", []) if item.get("task") == "regenerate-prd")
    assert task_after.get("status") == "completed"
    assert payload_after.get("doc_chain_update_required") is False
