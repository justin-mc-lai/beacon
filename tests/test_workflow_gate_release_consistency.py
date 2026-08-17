"""Workflow terminal consistency contracts for strict release gate."""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.utils.artifact_paths import execution_file_output
from beacon.main import app


gate_module = importlib.import_module("beacon.commands.gate")
runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _extract_json(text: str) -> dict:
    start = text.find("{")
    assert start >= 0
    return json.loads(text[start:])


def test_workflow_auto_should_align_with_release_gate_strict(tmp_path: Path, monkeypatch):
    # Strict release gates for runtime/docs alignment and memory transaction
    # consistency are covered by dedicated gate tests; isolate workflow consistency here.
    monkeypatch.setattr(gate_module, "check_runtime_release_alignment", lambda *_a, **_k: [])
    monkeypatch.setattr(
        gate_module,
        "workflow_memory_transaction_contract",
        lambda *_a, **_k: {"status": "pass", "blocked": False, "reason_code": "workflow_memory_transaction_ok"},
    )
    start = _invoke(
        [
            "workflow",
            "start",
            "Release Consistency Feature",
            "--auto",
            "--project",
            str(tmp_path),
            "--implementation-command",
            "python3 -c \"print('impl')\"",
            "--verify-scope",
            "unit",
            "--verify-unit-command",
            "python3 -c \"print('ok')\"",
        ]
    )
    assert start.exit_code == 0

    gate = _invoke(
        [
            "gate",
            "check",
            "release",
            "--mode",
            "strict",
            "--json",
            "--project-root",
            str(tmp_path),
        ]
    )
    payload = _extract_json(gate.stdout)
    assert payload["status"] == "Pass"
    assert payload["blocked_count"] == 0

    lifecycle = json.loads((tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json").read_text(encoding="utf-8"))
    events = [i for i in lifecycle.get("items", []) if isinstance(i, dict)]
    assert any(
        i.get("stage") == "release" and i.get("event") == "release_decision_recorded"
        for i in events
    )

    manifest = json.loads((tmp_path / ".beacon" / "evidence-manifest.json").read_text(encoding="utf-8"))
    entries = [x for x in manifest.get("entries", []) if isinstance(x, dict)]
    # raw command log is volatile evidence and is intentionally excluded from the manifest
    assert all(x.get("path") != ".beacon/raw-command-log.jsonl" for x in entries)
    assert any(x.get("path") == ".beacon/evidence-signature-chain.json" for x in entries)
    raw_path = tmp_path / ".beacon" / "raw-command-log.jsonl"
    assert raw_path.exists()


def test_release_gate_should_prefer_terminal_run_when_newer_incomplete_run_exists(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(gate_module, "check_runtime_release_alignment", lambda *_a, **_k: [])
    monkeypatch.setattr(
        gate_module,
        "workflow_memory_transaction_contract",
        lambda *_a, **_k: {"status": "pass", "blocked": False, "reason_code": "workflow_memory_transaction_ok"},
    )
    start = _invoke(
        [
            "workflow",
            "start",
            "Release Consistency Feature",
            "--auto",
            "--project",
            str(tmp_path),
            "--implementation-command",
            "python3 -c \"print('impl')\"",
            "--verify-scope",
            "unit",
            "--verify-unit-command",
            "python3 -c \"print('ok')\"",
        ]
    )
    assert start.exit_code == 0

    terminal = json.loads(execution_file_output(tmp_path, "v0.0.1", "terminal.json").read_text(encoding="utf-8"))
    contract_run_id = str(terminal["run_id"])

    lifecycle_path = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    lifecycle = json.loads(lifecycle_path.read_text(encoding="utf-8"))
    items = lifecycle.get("items", [])
    items.append(
        {
            "event_id": "newer-run-think-start",
            "run_id": "run-20990101T000000Z-dead",
            "stage": "think",
            "event": "stage_started",
            "source": "workflow.start",
            "source_session_id": "run-20990101T000000Z-dead",
            "evidence_ref": [],
            "ts": "2099-01-01T00:00:00Z",
            "details": {},
        }
    )
    lifecycle["items"] = items
    lifecycle_path.write_text(json.dumps(lifecycle, ensure_ascii=False, indent=2), encoding="utf-8")

    version = "v0.0.1"
    fp_root = tmp_path / ".beacon" / "state" / "spec-fingerprints" / version
    fp_root.mkdir(parents=True, exist_ok=True)
    bogus_fp = {
        "schema_version": "1.0",
        "run_id": "run-20990101T000000Z-dead",
        "version": version,
        "generated_at": "2099-01-01T00:00:00Z",
        "layers": {},
        "fingerprint_hash": "bogus-fingerprint",
    }
    (fp_root / "run-20990101T000000Z-dead.json").write_text(json.dumps(bogus_fp), encoding="utf-8")
    (fp_root / "latest.json").write_text(json.dumps(bogus_fp), encoding="utf-8")

    baseline_root = tmp_path / ".beacon" / "state" / "baselines" / version
    baseline_root.mkdir(parents=True, exist_ok=True)
    bogus_baseline = {
        "schema_version": "1.0",
        "baseline_id": "bl-run-20990101T000000Z-dead-001",
        "run_id": "run-20990101T000000Z-dead",
        "version": version,
        "feature": "bogus",
        "workflow_status": "running",
        "generated_at": "2099-01-01T00:00:00Z",
        "spec_fingerprint": {"fingerprint_hash": "bogus-fingerprint"},
        "delta_summary": {"changed_layers": [], "doc_chain_update_required": False},
    }
    (baseline_root / "bl-run-20990101T000000Z-dead-001.json").write_text(
        json.dumps(bogus_baseline), encoding="utf-8"
    )
    (baseline_root / "latest.json").write_text(json.dumps(bogus_baseline), encoding="utf-8")

    gate = _invoke(
        [
            "gate",
            "check",
            "release",
            "--mode",
            "strict",
            "--json",
            "--project-root",
            str(tmp_path),
        ]
    )
    payload = _extract_json(gate.stdout)
    assert payload["status"] == "Pass"
    assert payload["blocked_count"] == 0
    assert payload["doc_impl_verdict"]["actual_spec_fingerprint"] != "bogus-fingerprint"
    assert payload["doc_impl_verdict"]["expected_spec_fingerprint"] != "bogus-fingerprint"
    assert contract_run_id == terminal["run_id"]
