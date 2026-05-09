"""Gate strict memory-closure contract tests."""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.runtime import save_run_state
from beacon.utils.workflow_memory import append_lifecycle_event


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


def test_gate_release_json_should_expose_version_surface_governance_drift(tmp_path: Path, monkeypatch):
    execution = tmp_path / "docs" / "beacon" / "v1.4.0" / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
    (execution / "terminal.json").write_text('{"status":"Pass","traceability":{}}', encoding="utf-8")

    beacon_state = tmp_path / ".beacon"
    beacon_state.mkdir(parents=True, exist_ok=True)
    (beacon_state / "raw-command-log.jsonl").write_text('{"cmd":"workflow"}\n', encoding="utf-8")
    sha = hashlib.sha256((execution / "boundaries.md").read_bytes()).hexdigest()
    (beacon_state / "evidence-manifest.json").write_text(
        json.dumps({"entries": [{"path": "docs/beacon/v1.4.0/execution/boundaries.md", "sha256": sha}]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "qa": {
                "feature": "feature-a",
                "project_profile_gate_status": "pass",
            },
            "acceptance": {
                "source": "qa_status",
                "feature": "feature-a",
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "project_profile_gate_status": "pass",
                "unresolved_closure_outcomes": [],
                "review_required_count": 0,
                "needs_replay_count": 0,
                "release_confidence_min": 0.95,
            },
            "version_surface_governance": {
                "configured": True,
                "status": "fail",
                "blocked": True,
                "reason_code": "version_surface_governance_drift",
                "manifest_path": "beacon/version-truth.json",
                "repair_commands": [
                    f"beacon doctor sync-version-surfaces --project-root {tmp_path}",
                    f"beacon doctor verify-version-surfaces --project-root {tmp_path} --strict",
                ],
                "verify_command": f"beacon doctor verify-version-surfaces --project-root {tmp_path} --strict",
            },
            "acceptance_transaction": {"status": "pass"},
        },
    )

    result = _invoke(
        ["gate", "check", "release", "--mode", "strict", "--json", "--project-root", str(tmp_path), "--version", "v1.4.0"]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "version_surface_governance_drift" in reason_codes
    issue = next(item for item in payload["issues"] if item["reason_code"] == "version_surface_governance_drift")
    assert issue["recommended_command"] == f"beacon doctor sync-version-surfaces --project-root {tmp_path}"
    assert issue["repair"] == [
        f"beacon doctor sync-version-surfaces --project-root {tmp_path}",
        f"beacon doctor verify-version-surfaces --project-root {tmp_path} --strict",
    ]


def test_gate_release_text_should_print_version_surface_governance_repair_route(tmp_path: Path, monkeypatch):
    execution = tmp_path / "docs" / "beacon" / "v1.4.0" / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
    (execution / "terminal.json").write_text('{"status":"Pass","traceability":{}}', encoding="utf-8")

    beacon_state = tmp_path / ".beacon"
    beacon_state.mkdir(parents=True, exist_ok=True)
    (beacon_state / "raw-command-log.jsonl").write_text('{"cmd":"workflow"}\n', encoding="utf-8")
    sha = hashlib.sha256((execution / "boundaries.md").read_bytes()).hexdigest()
    (beacon_state / "evidence-manifest.json").write_text(
        json.dumps({"entries": [{"path": "docs/beacon/v1.4.0/execution/boundaries.md", "sha256": sha}]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "qa": {
                "feature": "feature-a",
                "project_profile_gate_status": "pass",
            },
            "acceptance": {
                "source": "qa_status",
                "feature": "feature-a",
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "project_profile_gate_status": "pass",
                "unresolved_closure_outcomes": [],
                "review_required_count": 0,
                "needs_replay_count": 0,
                "release_confidence_min": 0.95,
            },
            "version_surface_governance": {
                "configured": True,
                "status": "fail",
                "blocked": True,
                "reason_code": "version_surface_governance_drift",
                "manifest_path": "beacon/version-truth.json",
                "repair_commands": [
                    f"beacon doctor sync-version-surfaces --project-root {tmp_path}",
                    f"beacon doctor verify-version-surfaces --project-root {tmp_path} --strict",
                ],
                "verify_command": f"beacon doctor verify-version-surfaces --project-root {tmp_path} --strict",
            },
            "acceptance_transaction": {"status": "pass"},
        },
    )

    result = _invoke(
        ["gate", "check", "release", "--mode", "strict", "--project-root", str(tmp_path), "--version", "v1.4.0"]
    )
    assert result.exit_code == 2, result.stdout
    assert "version_surface_governance_drift" in result.stdout
    assert f"repair: beacon doctor sync-version-surfaces --project-root {tmp_path}" in result.stdout
    assert f"repair: beacon doctor verify-version-surfaces --project-root {tmp_path} --strict" in result.stdout


def test_gate_release_should_fallback_from_gate_report_run_to_repair_workflow_run(tmp_path: Path):
    version = "v1.0.0"
    feature = "repair-feature"
    _write_core_gate_artifacts(tmp_path)

    machine_exec = tmp_path / "docs" / "beacon" / version / ".machine" / "execution"
    machine_exec.mkdir(parents=True, exist_ok=True)
    repair_run_id = "repair-v1.0.0-20260101T000000Z0000"
    (machine_exec / "terminal.json").write_text(
        json.dumps({"run_id": repair_run_id, "status": "Pass"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (machine_exec / "source.json").write_text(
        json.dumps({"run_id": repair_run_id, "version": version, "feature": feature}, ensure_ascii=False),
        encoding="utf-8",
    )

    save_run_state(
        tmp_path,
        repair_run_id,
        {
            "run_id": repair_run_id,
            "workflow": "workflow.start",
            "feature": feature,
            "version": version,
            "status": "completed",
            "started_at": "2026-01-01T00:00:00Z",
            "ended_at": "2026-01-01T00:00:05Z",
        },
    )

    refs = ["docs/beacon/v1.0.0/execution/boundaries.md"]
    for stage in ("prd", "user-story", "test-case", "implement", "qa", "release"):
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_started",
            source="review.accept.sync",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_context_injected",
            source="workflow.memory.recall",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_finished",
            source="review.accept.sync",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="memory_writeback",
            source="workflow.memory.writeback",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )

    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"stage": "release", "mode": "strict", "status": "Pass", "issues": [], "run_id": "run-auto-001"}),
        encoding="utf-8",
    )

    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "memory_lifecycle_missing" not in reason_codes


def test_gate_release_should_ignore_non_release_gate_report_run_id(tmp_path: Path):
    version = "v1.0.0"
    feature = "repair-feature"
    _write_core_gate_artifacts(tmp_path)

    machine_exec = tmp_path / "docs" / "beacon" / version / ".machine" / "execution"
    machine_exec.mkdir(parents=True, exist_ok=True)
    repair_run_id = "repair-v1.0.0-20260101T000000Z0000"
    (machine_exec / "terminal.json").write_text(
        json.dumps({"run_id": repair_run_id, "status": "Pass"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (machine_exec / "source.json").write_text(
        json.dumps({"run_id": repair_run_id, "version": version, "feature": feature}, ensure_ascii=False),
        encoding="utf-8",
    )

    save_run_state(
        tmp_path,
        repair_run_id,
        {
            "run_id": repair_run_id,
            "workflow": "workflow.start",
            "feature": feature,
            "version": version,
            "status": "completed",
            "started_at": "2026-01-01T00:00:00Z",
            "ended_at": "2026-01-01T00:00:05Z",
        },
    )

    refs = ["docs/beacon/v1.0.0/execution/boundaries.md"]
    for stage in ("prd", "user-story", "test-case", "implement", "qa", "release"):
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_started",
            source="review.accept.sync",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_context_injected",
            source="workflow.memory.recall",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_finished",
            source="review.accept.sync",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="memory_writeback",
            source="workflow.memory.writeback",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )

    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"stage": "verify", "mode": "strict", "status": "Blocked", "issues": [], "run_id": "run-auto-001"}),
        encoding="utf-8",
    )

    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "memory_lifecycle_missing" not in reason_codes


def test_gate_release_should_fallback_to_closed_lifecycle_run_without_run_state(tmp_path: Path):
    version = "v1.0.0"
    _write_core_gate_artifacts(tmp_path)

    refs = ["docs/beacon/v1.0.0/execution/boundaries.md"]
    closed_run_id = "repair-v1.0.0-20260101T000000Z0000"
    current_run_id = "run-20260102T000000Z-aaaa"

    for stage in ("prd", "user-story", "test-case", "implement", "qa", "release"):
        append_lifecycle_event(
            tmp_path,
            run_id=closed_run_id,
            stage=stage,
            event="stage_started",
            source="review.accept.sync",
            evidence_ref=refs,
            details={"feature": "feature-a", "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=closed_run_id,
            stage=stage,
            event="stage_context_injected",
            source="workflow.memory.recall",
            evidence_ref=refs,
            details={"feature": "feature-a", "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=closed_run_id,
            stage=stage,
            event="stage_finished",
            source="review.accept.sync",
            evidence_ref=refs,
            details={"feature": "feature-a", "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=closed_run_id,
            stage=stage,
            event="memory_writeback",
            source="workflow.memory.writeback",
            evidence_ref=refs,
            details={"feature": "feature-a", "version": version},
        )

    append_lifecycle_event(
        tmp_path,
        run_id=current_run_id,
        stage="qa",
        event="memory_writeback",
        source="workflow.memory.writeback",
        evidence_ref=refs,
        details={"feature": "feature-b", "version": version},
    )
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"stage": "release", "mode": "strict", "status": "Pass", "issues": [], "run_id": current_run_id}),
        encoding="utf-8",
    )

    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "memory_lifecycle_missing" not in reason_codes


def test_gate_release_should_fallback_to_latest_closed_workflow_run_when_verify_run_is_incomplete(tmp_path: Path):
    version = "v1.0.0"
    feature = "repair-feature"
    _write_core_gate_artifacts(tmp_path)

    machine_exec = tmp_path / "docs" / "beacon" / version / ".machine" / "execution"
    machine_exec.mkdir(parents=True, exist_ok=True)
    repair_run_id = "repair-v1.0.0-20260101T000000Z0000"
    current_verify_run = "run-20260102T000000Z0000"
    (machine_exec / "terminal.json").write_text(
        json.dumps({"run_id": repair_run_id, "status": "Pass"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (machine_exec / "source.json").write_text(
        json.dumps({"run_id": repair_run_id, "version": version, "feature": feature}, ensure_ascii=False),
        encoding="utf-8",
    )

    save_run_state(
        tmp_path,
        repair_run_id,
        {
            "run_id": repair_run_id,
            "workflow": "workflow.start",
            "feature": feature,
            "version": version,
            "status": "completed",
            "started_at": "2026-01-01T00:00:00Z",
            "ended_at": "2026-01-01T00:00:05Z",
        },
    )
    save_run_state(
        tmp_path,
        current_verify_run,
        {
            "run_id": current_verify_run,
            "workflow": "workflow.start",
            "feature": feature,
            "version": version,
            "status": "running",
            "started_at": "2026-01-02T00:00:00Z",
        },
    )

    refs = ["docs/beacon/v1.0.0/execution/boundaries.md"]
    for stage in ("prd", "user-story", "test-case", "implement", "qa", "release"):
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_started",
            source="review.accept.sync",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_context_injected",
            source="workflow.memory.recall",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="stage_finished",
            source="review.accept.sync",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
        append_lifecycle_event(
            tmp_path,
            run_id=repair_run_id,
            stage=stage,
            event="memory_writeback",
            source="workflow.memory.writeback",
            evidence_ref=refs,
            details={"feature": feature, "version": version},
        )
    append_lifecycle_event(
        tmp_path,
        run_id=current_verify_run,
        stage="qa",
        event="stage_started",
        source="qa.run",
        evidence_ref=refs,
        details={"feature": feature, "version": version},
    )

    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"stage": "verify", "mode": "strict", "status": "Blocked", "issues": [], "run_id": current_verify_run}),
        encoding="utf-8",
    )

    payload = _gate_release_payload(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "memory_lifecycle_missing" not in reason_codes
