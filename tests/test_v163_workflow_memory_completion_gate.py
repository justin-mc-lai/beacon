"""Tests for beacon-workflow-memory-completion-gate-v163 (P0-2).

Covers:
- no-run-resolved warns (informational, not blocked)
- run-without-transaction fails closed (blocked)
- gate blocks on missing transaction when a run exists
- fresh project (no run) not blocked
- existing failed_transaction/drift/pass semantics preserved
- status distinguishes reason codes
"""
from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.workflow_memory import (
    workflow_memory_transaction_contract,
    workflow_transaction_path,
)
from beacon.utils.runtime import runs_dir


def _make_run(tmp_path: Path, run_id: str, *, workflow: str = "workflow.start") -> None:
    """Create a run state so resolve_workflow_run_id finds it."""
    state_path = runs_dir(tmp_path) / run_id / "state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"workflow": workflow, "version": "v1.6.3", "status": "running"}),
        encoding="utf-8",
    )


def _make_transaction(tmp_path: Path, run_id: str, item: dict) -> None:
    path = workflow_transaction_path(tmp_path, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": "1.0", "items": [item], "updated_at": "2026-06-25T00:00:00Z"}),
        encoding="utf-8",
    )


# ---- AC-001 no run warns ----

def test_no_run_resolved_warns(tmp_path: Path) -> None:
    """No run directory at all -> warn, not blocked, no_run_resolved reason."""
    # fresh project: no runs/
    contract = workflow_memory_transaction_contract(tmp_path, version="v1.6.3")
    assert contract["status"] == "warn"
    assert contract["blocked"] is False
    assert contract["reason_code"] == "workflow_memory_no_run_resolved"


# ---- AC-002 run without transaction fails ----

def test_run_without_transaction_fails(tmp_path: Path) -> None:
    """Run exists but no transaction journal -> fail closed."""
    _make_run(tmp_path, "run-test-001")
    contract = workflow_memory_transaction_contract(
        tmp_path, run_id="run-test-001", version="v1.6.3"
    )
    assert contract["status"] == "fail"
    assert contract["blocked"] is True
    assert contract["reason_code"] == "workflow_memory_transaction_missing"


# ---- AC-005 existing semantics preserved ----

def test_existing_semantics_preserved(tmp_path: Path) -> None:
    """failed_transaction -> fail; drift -> fail; ok -> pass."""
    _make_run(tmp_path, "run-sem-001")
    # failed_transaction
    _make_transaction(
        tmp_path, "run-sem-001",
        {"status": "failed_transaction", "transaction_id": "t1", "source_hash": "h", "projection_seq": 1},
    )
    c = workflow_memory_transaction_contract(tmp_path, run_id="run-sem-001", version="v1.6.3")
    assert c["status"] == "fail" and c["reason_code"] == "workflow_memory_failed_transaction"

    # drift (missing metadata)
    _make_transaction(
        tmp_path, "run-sem-001",
        {"status": "ok", "transaction_id": "", "source_hash": "", "projection_seq": 0, "sink_checksums": {}},
    )
    c = workflow_memory_transaction_contract(tmp_path, run_id="run-sem-001", version="v1.6.3")
    assert c["status"] == "fail" and c["reason_code"] == "workflow_memory_transaction_drift"


# ---- AC-007 pass when ok ----

def test_pass_when_transaction_ok(tmp_path: Path) -> None:
    _make_run(tmp_path, "run-ok-001")
    _make_transaction(
        tmp_path, "run-ok-001",
        {
            "status": "ok",
            "transaction_id": "t1",
            "source_hash": "h",
            "projection_seq": 1,
            "sink_checksums": {"a": "cksum"},
        },
    )
    c = workflow_memory_transaction_contract(tmp_path, run_id="run-ok-001", version="v1.6.3")
    assert c["status"] == "pass"
    assert c["blocked"] is False
    assert c["reason_code"] == "workflow_memory_transaction_ok"


# ---- AC-006 status distinguishes ----

def test_status_distinguishes_reason_codes(tmp_path: Path) -> None:
    """no-run vs run-without-tx have different reason_codes."""
    no_run = workflow_memory_transaction_contract(tmp_path, version="v1.6.3")
    _make_run(tmp_path, "run-dist-001")
    with_tx_missing = workflow_memory_transaction_contract(
        tmp_path, run_id="run-dist-001", version="v1.6.3"
    )
    assert no_run["reason_code"] != with_tx_missing["reason_code"]
    assert no_run["reason_code"] == "workflow_memory_no_run_resolved"
    assert with_tx_missing["reason_code"] == "workflow_memory_transaction_missing"


# ---- AC-003 / AC-004 contract status feeds gate (gate.py:1054 wires fail->block) ----

def test_gate_blocks_on_missing_transaction(tmp_path: Path) -> None:
    """AC-003: a run-without-transaction contract returns fail/blocked, which
    gate.py:1054 turns into a blocked release issue (UD-003). We assert the
    contract surface the gate consumes; full gate integration requires a
    closure-complete run which is out of scope for this unit test."""
    _make_run(tmp_path, "run-gate-001")
    contract = workflow_memory_transaction_contract(
        tmp_path, run_id="run-gate-001", version="v1.6.3"
    )
    # gate.py:1054 checks `status == "fail"` -> blocked issue
    assert contract["status"] == "fail"
    assert contract["blocked"] is True
    assert contract["reason_code"] == "workflow_memory_transaction_missing"


def test_fresh_project_not_blocked(tmp_path: Path) -> None:
    """AC-004: a fresh project with no run yields warn (not fail), so gate.py:1054
    does NOT emit a blocked transaction issue (no false block on fresh projects)."""
    contract = workflow_memory_transaction_contract(tmp_path, version="v1.6.3")
    assert contract["status"] == "warn"
    assert contract["blocked"] is False
    # gate only blocks on "fail"; warn is informational
    assert contract["reason_code"] == "workflow_memory_no_run_resolved"
