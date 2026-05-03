"""Gate strict memory-closure contract tests."""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
gate_module = importlib.import_module("beacon.commands.gate")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write_core_gate_artifacts(project_root: Path) -> None:
    execution = project_root / "docs" / "beacon" / "v1.0.0" / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
    (execution / "terminal.json").write_text('{"status":"Pass","traceability":{}}', encoding="utf-8")

    beacon_state = project_root / ".beacon"
    beacon_state.mkdir(parents=True, exist_ok=True)
    (beacon_state / "raw-command-log.jsonl").write_text('{"cmd":"workflow"}\n', encoding="utf-8")
    (beacon_state / "gate-report.json").write_text(
        json.dumps({"stage": "release", "mode": "strict", "status": "Pass", "issues": []}),
        encoding="utf-8",
    )

    sha = hashlib.sha256((execution / "boundaries.md").read_bytes()).hexdigest()
    (beacon_state / "evidence-manifest.json").write_text(
        json.dumps({"entries": [{"path": "docs/beacon/v1.0.0/execution/boundaries.md", "sha256": sha}]}),
        encoding="utf-8",
    )


def _seed_complete_lifecycle(project_root: Path, *, with_evidence: bool = True) -> None:
    memory_dir = project_root / ".beacon" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    refs = ["docs/beacon/v1.0.0/execution/boundaries.md"] if with_evidence else []
    items = []
    for stage in ("think", "user-story", "prd", "test-case", "implementation", "verify"):
        items.extend(
            [
                {
                    "event_id": f"{stage}-start",
                    "run_id": "run-closure",
                    "stage": stage,
                    "event": "stage_started",
                    "source": "workflow.start",
                    "source_session_id": "run-closure",
                    "evidence_ref": refs,
                    "ts": "2026-01-01T00:00:00Z",
                    "details": {},
                },
                {
                    "event_id": f"{stage}-ctx",
                    "run_id": "run-closure",
                    "stage": stage,
                    "event": "stage_context_injected",
                    "source": "workflow.memory.recall",
                    "source_session_id": "run-closure",
                    "evidence_ref": refs,
                    "ts": "2026-01-01T00:00:01Z",
                    "details": {},
                },
                {
                    "event_id": f"{stage}-finish",
                    "run_id": "run-closure",
                    "stage": stage,
                    "event": "stage_finished",
                    "source": "workflow.start",
                    "source_session_id": "run-closure",
                    "evidence_ref": refs,
                    "ts": "2026-01-01T00:00:02Z",
                    "details": {},
                },
                {
                    "event_id": f"{stage}-wb",
                    "run_id": "run-closure",
                    "stage": stage,
                    "event": "memory_writeback",
                    "source": "workflow.memory.writeback",
                    "source_session_id": "run-closure",
                    "evidence_ref": refs,
                    "ts": "2026-01-01T00:00:03Z",
                    "details": {},
                },
            ]
        )
    (memory_dir / "workflow-lifecycle.json").write_text(
        json.dumps({"schema_version": "1.0", "items": items, "updated_at": "2026-01-01T00:00:04Z"}),
        encoding="utf-8",
    )
    (memory_dir / "workflow-lifecycle.index.json").write_text(
        json.dumps({"schema_version": "1.0", "dedupe_keys": [], "updated_at": "2026-01-01T00:00:04Z"}),
        encoding="utf-8",
    )


def _append_release_event(project_root: Path, *, with_evidence: bool = True) -> None:
    lifecycle_path = project_root / ".beacon" / "memory" / "workflow-lifecycle.json"
    payload = json.loads(lifecycle_path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    refs = ["docs/beacon/v1.0.0/execution/boundaries.md"] if with_evidence else []
    items.append(
        {
            "event_id": "release-recorded",
            "run_id": "release:v1.2.3",
            "stage": "release",
            "event": "release_decision_recorded",
            "source": "release.create",
            "source_session_id": "release:v1.2.3",
            "evidence_ref": refs,
            "ts": "2026-01-01T00:00:05Z",
            "details": {"action": "create", "version": "v1.2.3"},
        }
    )
    payload["items"] = items
    lifecycle_path.write_text(json.dumps(payload), encoding="utf-8")


def _gate_release_payload(project_root: Path) -> dict:
    result = _invoke(
        ["gate", "check", "release", "--mode", "strict", "--json", "--project-root", str(project_root)]
    )
    assert result.stdout
    start = result.stdout.find("{")
    assert start >= 0
    return json.loads(result.stdout[start:])


def test_gate_release_should_flag_memory_lifecycle_missing(tmp_path: Path):
    _write_core_gate_artifacts(tmp_path)
    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "memory_lifecycle_missing" in reason_codes


def test_gate_release_should_flag_memory_evidence_missing(tmp_path: Path):
    _write_core_gate_artifacts(tmp_path)
    _seed_complete_lifecycle(tmp_path, with_evidence=False)
    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "memory_evidence_missing" in reason_codes


def test_gate_release_should_flag_feedback_unsynced(tmp_path: Path):
    _write_core_gate_artifacts(tmp_path)
    _seed_complete_lifecycle(tmp_path, with_evidence=True)
    feedback_dir = tmp_path / ".beacon" / "state" / "requirement-feedback"
    feedback_dir.mkdir(parents=True, exist_ok=True)
    (feedback_dir / "run-closure.json").write_text(
        json.dumps({"run_id": "run-closure", "feedback": [{"type": "compat", "note": "needs sync"}]}),
        encoding="utf-8",
    )
    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "memory_feedback_unsynced" in reason_codes


def test_gate_release_should_flag_release_memory_profile_missing(tmp_path: Path):
    _write_core_gate_artifacts(tmp_path)
    _seed_complete_lifecycle(tmp_path, with_evidence=True)
    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "release_memory_profile_invalid" in reason_codes


def test_gate_release_should_accept_release_memory_profile_with_evidence(tmp_path: Path):
    _write_core_gate_artifacts(tmp_path)
    _seed_complete_lifecycle(tmp_path, with_evidence=True)
    _append_release_event(tmp_path, with_evidence=True)
    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "release_memory_profile_invalid" not in reason_codes


def test_gate_release_should_block_when_workflow_memory_transaction_failed(tmp_path: Path):
    _write_core_gate_artifacts(tmp_path)
    _seed_complete_lifecycle(tmp_path, with_evidence=True)
    tx_root = tmp_path / ".beacon" / "state" / "workflow-memory" / "run-closure"
    tx_root.mkdir(parents=True, exist_ok=True)
    (tx_root / "transactions.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "items": [
                    {
                        "transaction_id": "tx-wf-run-closure-release-memory_writeback-deadbeef",
                        "run_id": "run-closure",
                        "stage": "release",
                        "action": "memory_writeback",
                        "source_hash": "deadbeef",
                        "projection_seq": "wf-deadbeef",
                        "status": "failed_transaction",
                        "sink_checksums": {"memory_v1": "missing", "workflow_lifecycle": "missing"},
                        "committed_at": "",
                        "occurred_at": "2026-01-01T00:00:05Z",
                    }
                ],
                "updated_at": "2026-01-01T00:00:05Z",
            }
        ),
        encoding="utf-8",
    )
    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "workflow_memory_failed_transaction" in reason_codes


def test_gate_release_should_allow_authoritative_acceptance_without_workflow_memory(tmp_path: Path, monkeypatch):
    _write_core_gate_artifacts(tmp_path)
    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": True,
            "acceptance": {"source": "qa_acceptance_envelope"},
            "acceptance_transaction": {"status": "pass"},
        },
    )

    assert gate_module.check_memory_closure(tmp_path, gate_module.GateMode.STRICT, "release", "v1.0.0") == []
    assert gate_module.check_release_memory_profile(tmp_path, gate_module.GateMode.STRICT, "release", "v1.0.0") == []
