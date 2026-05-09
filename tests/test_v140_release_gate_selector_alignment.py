from __future__ import annotations

import importlib
import json
from pathlib import Path

from beacon.commands.gate import GateMode, _resolve_release_contract_run_id, check_release_memory_profile, check_spec_consistency
from beacon.utils.runtime import write_json


VERSION = "v1.4.0"
gate_module = importlib.import_module("beacon.commands.gate")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_v140_release_contract_run_prefers_verify_gate_report_run(tmp_path: Path) -> None:
    _write_json(tmp_path / ".beacon" / "runs" / "run-current" / "state.json", {"run_id": "run-current", "version": VERSION})
    _write_json(tmp_path / ".beacon" / "runs" / "repair-old" / "state.json", {"run_id": "repair-old", "version": VERSION})
    _write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {
            "run_id": "run-current",
            "stage": "verify",
            "version": VERSION,
        },
    )
    _write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "terminal.json",
        {
            "run_id": "repair-old",
            "version": VERSION,
        },
    )
    _write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "source.json",
        {
            "run_id": "repair-old",
            "version": VERSION,
            "project_name": "demo",
            "project_root": ".",
            "workspace_root": ".",
            "repo_url": "https://example.com/repo.git",
            "branch": "main",
            "commit": "abc123",
        },
    )

    assert _resolve_release_contract_run_id(tmp_path, version=VERSION) == "run-current"


def test_v140_release_memory_profile_checks_latest_release_event_only(tmp_path: Path, monkeypatch) -> None:
    old_missing_ref = ".beacon/runs/repair-old/state.json"
    current_ref = ".beacon/gate-report.json"
    _write_json(tmp_path / current_ref, {"status": "Pass"})
    _write_json(
        tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json",
        {
            "schema_version": "1.0",
            "updated_at": "2026-05-08T00:00:00Z",
            "items": [
                {
                    "event_id": "evt-old",
                    "run_id": "release:v1.4.0",
                    "stage": "release",
                    "event": "release_decision_recorded",
                    "source": "workflow.release-profile",
                    "source_session_id": "release:v1.4.0",
                    "evidence_ref": [old_missing_ref],
                    "ts": "2026-05-08T00:00:00Z",
                    "details": {"version": VERSION},
                },
                {
                    "event_id": "evt-new",
                    "run_id": "release:v1.4.0",
                    "stage": "release",
                    "event": "release_decision_recorded",
                    "source": "release.check",
                    "source_session_id": "release:v1.4.0",
                    "evidence_ref": [current_ref],
                    "ts": "2026-05-08T01:00:00Z",
                    "details": {"version": VERSION},
                },
            ],
        },
    )
    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "acceptance": {"source": "qa_status"},
            "acceptance_transaction": {"status": "pass"},
        },
    )

    assert check_release_memory_profile(tmp_path, GateMode.STRICT, "release", VERSION) == []


def test_v140_spec_consistency_uses_current_verify_run_selector(tmp_path: Path) -> None:
    # Current authoritative run is the verify-stage gate report run.
    _write_json(tmp_path / ".beacon" / "runs" / "run-current" / "state.json", {"run_id": "run-current", "version": VERSION})
    _write_json(tmp_path / ".beacon" / "runs" / "repair-old" / "state.json", {"run_id": "repair-old", "version": VERSION})
    _write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {"run_id": "run-current", "stage": "verify", "version": VERSION},
    )
    # Legacy execution surfaces still point at an older repair run.
    _write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "terminal.json",
        {"run_id": "repair-old", "version": VERSION},
    )
    _write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "source.json",
        {
            "run_id": "repair-old",
            "version": VERSION,
            "project_name": "demo",
            "project_root": ".",
            "workspace_root": ".",
            "repo_url": "https://example.com/repo.git",
            "branch": "main",
            "commit": "abc123",
        },
    )
    # Latest baseline belongs to the old run and carries a stale fingerprint.
    write_json(
        tmp_path / ".beacon" / "state" / "baselines" / VERSION / "latest.json",
        {
            "baseline_id": "bl-repair-old-001",
            "run_id": "repair-old",
            "spec_fingerprint": {"fingerprint_hash": "stale-fingerprint"},
        },
    )
    # Current run-scoped fingerprint matches the current auto-test status.
    write_json(
        tmp_path / ".beacon" / "state" / "spec-fingerprints" / VERSION / "run-current.json",
        {
            "run_id": "run-current",
            "version": VERSION,
            "fingerprint_hash": "current-fingerprint",
        },
    )
    write_json(
        tmp_path / ".beacon" / "state" / "spec-fingerprints" / VERSION / "latest.json",
        {
            "run_id": "run-current",
            "version": VERSION,
            "fingerprint_hash": "current-fingerprint",
        },
    )
    _write_json(
        tmp_path / ".beacon" / "auto-test-status.json",
        {
            "status": "passed",
            "version": VERSION,
            "spec_fingerprint_hash": "current-fingerprint",
            "execution": {
                "spec_fingerprint": {
                    "fingerprint_hash": "current-fingerprint",
                }
            },
        },
    )

    issues, verdict = check_spec_consistency(tmp_path, GateMode.STRICT, "release", version=VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "spec_impl_drift_detected" not in reason_codes
    assert verdict["actual_spec_fingerprint"] == "current-fingerprint"
    assert verdict["expected_spec_fingerprint"] == "current-fingerprint"


def test_v140_spec_consistency_blocks_current_verify_run_drift_even_with_old_repair_baseline(tmp_path: Path) -> None:
    _write_json(tmp_path / ".beacon" / "runs" / "run-current" / "state.json", {"run_id": "run-current", "version": VERSION})
    _write_json(tmp_path / ".beacon" / "runs" / "repair-old" / "state.json", {"run_id": "repair-old", "version": VERSION})
    _write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {"run_id": "run-current", "stage": "verify", "version": VERSION},
    )
    _write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "terminal.json",
        {"run_id": "repair-old", "version": VERSION},
    )
    write_json(
        tmp_path / ".beacon" / "state" / "baselines" / VERSION / "latest.json",
        {
            "baseline_id": "bl-repair-old-001",
            "run_id": "repair-old",
            "spec_fingerprint": {"fingerprint_hash": "stale-fingerprint"},
        },
    )
    write_json(
        tmp_path / ".beacon" / "state" / "spec-fingerprints" / VERSION / "run-current.json",
        {
            "run_id": "run-current",
            "version": VERSION,
            "fingerprint_hash": "current-fingerprint",
        },
    )
    _write_json(
        tmp_path / ".beacon" / "auto-test-status.json",
        {
            "status": "passed",
            "version": VERSION,
            "spec_fingerprint_hash": "post-qa-writeback-fingerprint",
            "execution": {
                "spec_fingerprint": {
                    "fingerprint_hash": "post-qa-writeback-fingerprint",
                }
            },
        },
    )

    issues, verdict = check_spec_consistency(tmp_path, GateMode.STRICT, "release", version=VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "spec_impl_drift_detected" in reason_codes
    assert verdict["actual_spec_fingerprint"] == "post-qa-writeback-fingerprint"
    assert verdict["expected_spec_fingerprint"] == "current-fingerprint"
