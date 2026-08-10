from __future__ import annotations

import json

from beacon.utils.memory import load_memory_entries
from beacon.utils.runtime import save_run_state
from beacon.utils.workflow_memory import (
    list_workflow_transactions,
    load_lifecycle_events,
    record_stage_writeback,
    write_stage_context,
    workflow_memory_transaction_contract,
)


def _seed_docs(project_root, *, version: str, feature: str) -> None:
    slug = feature.strip().lower().replace(" ", "-")
    base = project_root / "docs" / "beacon" / version
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "user-story" / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")


def test_v136_stage_context_should_include_transaction_lineage_and_requirement_refs(tmp_path) -> None:
    version = "v1.3.6"
    feature = "Memory Transaction Feature"
    run_id = "run-memory-tx-001"
    _seed_docs(tmp_path, version=version, feature=feature)
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": feature,
            "version": version,
            "status": "running",
        },
    )

    context_path = write_stage_context(tmp_path, run_id=run_id, stage="prd", feature=feature)
    payload = json.loads(context_path.read_text(encoding="utf-8"))

    assert payload["version"] == version
    assert payload["requirement_refs"]
    assert f"docs/beacon/{version}/prd/memory-transaction-feature.md" in payload["requirement_refs"]
    assert "decision_trace" in payload
    assert "blockers" in payload
    assert payload["transaction_lineage"]["current_transaction_id"].startswith("tx-wf-")
    assert payload["transaction_lineage"]["projection_seq"].startswith("wf-")

    tx_items = list_workflow_transactions(tmp_path, run_id=run_id, stage="prd", action="stage_context")
    assert len(tx_items) == 1
    assert tx_items[0]["status"] == "applied"
    assert tx_items[0]["sink_checksums"]["context_pack"] not in {"", "missing"}


def test_v136_memory_writeback_should_dual_write_with_shared_transaction_metadata(tmp_path) -> None:
    version = "v1.3.6"
    feature = "Memory Transaction Feature"
    run_id = "run-memory-tx-002"
    _seed_docs(tmp_path, version=version, feature=feature)
    save_run_state(
        tmp_path,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "feature": feature,
            "version": version,
            "status": "running",
        },
    )

    entry = record_stage_writeback(
        tmp_path,
        run_id=run_id,
        stage="qa",
        feature=feature,
        evidence_ref=[f"docs/beacon/{version}/qa/test-cases/memory-transaction-feature.md"],
        status="completed",
    )

    rows = load_memory_entries(tmp_path, mem_type="decision")
    assert rows
    latest = rows[0]
    assert latest["transaction_id"] == entry["transaction_id"]
    assert latest["projection_seq"] == entry["projection_seq"]

    events = load_lifecycle_events(tmp_path, run_id=run_id, stage="qa", event="memory_writeback")
    assert events
    details = events[-1].get("details", {})
    assert details["transaction_id"] == entry["transaction_id"]

    tx_items = list_workflow_transactions(tmp_path, run_id=run_id, stage="qa", action="memory_writeback")
    assert len(tx_items) == 1
    tx = tx_items[0]
    assert tx["transaction_id"] == entry["transaction_id"]
    assert tx["sink_checksums"]["memory_v1"] not in {"", "missing"}
    assert tx["sink_checksums"]["workflow_lifecycle"] not in {"", "missing"}

    contract = workflow_memory_transaction_contract(tmp_path, run_id=run_id)
    assert contract["status"] == "pass"
    assert contract["reason_code"] == "workflow_memory_transaction_ok"
