from __future__ import annotations

import importlib
import json
from pathlib import Path

from beacon.commands.gate import (
    GateMode,
    _resolve_latest_closed_workflow_run_id,
    _resolve_release_contract_run_id,
    _resolve_release_report_run_id,
    check_release_memory_profile,
    check_spec_consistency,
)
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


def test_v140_release_report_run_prefers_current_passed_auto_test_over_stale_contract(tmp_path: Path) -> None:
    _write_json(tmp_path / ".beacon" / "runs" / "run-current" / "state.json", {"run_id": "run-current", "version": VERSION})
    _write_json(tmp_path / ".beacon" / "runs" / "run-old" / "state.json", {"run_id": "run-old", "version": VERSION})
    _write_json(
        tmp_path / ".beacon" / "auto-test-status.json",
        {
            "status": "passed",
            "run_id": "run-current",
            "version": VERSION,
        },
    )
    _write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {
            "run_id": "run-current",
            "stage": "qa",
            "version": VERSION,
            "status": "Pass",
        },
    )
    _write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "terminal.json",
        {
            "run_id": "run-old",
            "version": VERSION,
            "status": "Pass",
        },
    )

    assert _resolve_release_report_run_id(tmp_path, version=VERSION) == "run-current"


def test_v140_release_contract_run_prefers_latest_closed_workflow_over_stale_execution_artifacts(tmp_path: Path) -> None:
    _write_json(
        tmp_path / ".beacon" / "runs" / "run-old" / "state.json",
        {
            "run_id": "run-old",
            "workflow": "workflow.start",
            "version": VERSION,
            "started_at": "2026-05-14T00:00:00Z",
            "ended_at": "2026-05-14T00:05:00Z",
        },
    )
    _write_json(
        tmp_path / ".beacon" / "runs" / "run-new" / "state.json",
        {
            "run_id": "run-new",
            "workflow": "workflow.start",
            "version": VERSION,
            "started_at": "2026-05-14T00:10:00Z",
            "ended_at": "2026-05-14T00:15:00Z",
        },
    )
    _write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {"run_id": "run-old", "stage": "verify", "version": VERSION},
    )
    _write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / "terminal.json",
        {"run_id": "run-old", "version": VERSION},
    )
    lifecycle_items: list[dict[str, object]] = []
    for run_id, prefix in (("run-old", "2026-05-14T00"), ("run-new", "2026-05-14T01")):
        for idx, stage in enumerate(("prd", "user-story", "test-case", "implement", "qa", "release")):
            lifecycle_items.extend(
                [
                    {
                        "event_id": f"{run_id}-{stage}-started",
                        "run_id": run_id,
                        "stage": stage,
                        "event": "stage_started",
                        "source": "test",
                        "source_session_id": run_id,
                        "evidence_ref": [],
                        "ts": f"{prefix}:00:0{idx}Z",
                        "attempt_seq": 1,
                    },
                    {
                        "event_id": f"{run_id}-{stage}-context",
                        "run_id": run_id,
                        "stage": stage,
                        "event": "stage_context_injected",
                        "source": "test",
                        "source_session_id": run_id,
                        "evidence_ref": [],
                        "ts": f"{prefix}:01:0{idx}Z",
                        "attempt_seq": 1,
                    },
                    {
                        "event_id": f"{run_id}-{stage}-finished",
                        "run_id": run_id,
                        "stage": stage,
                        "event": "stage_finished",
                        "source": "test",
                        "source_session_id": run_id,
                        "evidence_ref": [],
                        "ts": f"{prefix}:02:0{idx}Z",
                        "attempt_seq": 1,
                    },
                    {
                        "event_id": f"{run_id}-{stage}-writeback",
                        "run_id": run_id,
                        "stage": stage,
                        "event": "memory_writeback",
                        "source": "test",
                        "source_session_id": run_id,
                        "evidence_ref": [],
                        "ts": f"{prefix}:03:0{idx}Z",
                        "attempt_seq": 1,
                    },
                ]
            )
    _write_json(
        tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json",
        {
            "schema_version": "1.0",
            "updated_at": "2026-05-14T01:10:00Z",
            "items": lifecycle_items,
        },
    )

    assert _resolve_release_contract_run_id(tmp_path, version=VERSION) == "run-new"


def test_v140_release_contract_run_falls_back_to_latest_closed_workflow_run(tmp_path: Path) -> None:
    _write_json(
        tmp_path / ".beacon" / "runs" / "run-closed" / "state.json",
        {
            "run_id": "run-closed",
            "workflow": "workflow.start",
            "version": VERSION,
            "started_at": "2026-05-14T00:00:00Z",
            "ended_at": "2026-05-14T00:10:00Z",
        },
    )
    _write_json(
        tmp_path / ".beacon" / "gate-report.json",
        {
            "run_id": "run-verify-only",
            "stage": "verify",
            "version": VERSION,
        },
    )
    lifecycle_path = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    _write_json(
        lifecycle_path,
        {
            "schema_version": "1.0",
            "updated_at": "2026-05-14T00:10:00Z",
            "items": [
                {
                    "event_id": f"{stage}-started",
                    "run_id": "run-closed",
                    "stage": stage,
                    "event": "stage_started",
                    "source": "test",
                    "source_session_id": "run-closed",
                    "evidence_ref": [],
                    "ts": f"2026-05-14T00:00:0{idx}Z",
                }
                for idx, stage in enumerate(("prd", "user-story", "test-case", "implement", "qa", "release"))
            ]
            + [
                {
                    "event_id": f"{stage}-context",
                    "run_id": "run-closed",
                    "stage": stage,
                    "event": "stage_context_injected",
                    "source": "test",
                    "source_session_id": "run-closed",
                    "evidence_ref": [],
                    "ts": f"2026-05-14T00:01:0{idx}Z",
                }
                for idx, stage in enumerate(("prd", "user-story", "test-case", "implement", "qa", "release"))
            ]
            + [
                {
                    "event_id": f"{stage}-finished",
                    "run_id": "run-closed",
                    "stage": stage,
                    "event": "stage_finished",
                    "source": "test",
                    "source_session_id": "run-closed",
                    "evidence_ref": [],
                    "ts": f"2026-05-14T00:02:0{idx}Z",
                }
                for idx, stage in enumerate(("prd", "user-story", "test-case", "implement", "qa", "release"))
            ]
            + [
                {
                    "event_id": f"{stage}-writeback",
                    "run_id": "run-closed",
                    "stage": stage,
                    "event": "memory_writeback",
                    "source": "test",
                    "source_session_id": "run-closed",
                    "evidence_ref": [],
                    "ts": f"2026-05-14T00:03:0{idx}Z",
                }
                for idx, stage in enumerate(("prd", "user-story", "test-case", "implement", "qa", "release"))
            ]
            + [
                {
                    "event_id": "verify-only",
                    "run_id": "run-verify-only",
                    "stage": "qa",
                    "event": "memory_writeback",
                    "source": "test",
                    "source_session_id": "run-verify-only",
                    "evidence_ref": [],
                    "ts": "2026-05-14T00:20:00Z",
                }
            ],
        },
    )

    assert _resolve_release_contract_run_id(tmp_path, version=VERSION) == "run-closed"


def test_v140_latest_closed_run_should_use_memory_closure_contract(tmp_path: Path) -> None:
    _write_json(
        tmp_path / ".beacon" / "runs" / "run-closed" / "state.json",
        {
            "run_id": "run-closed",
            "workflow": "workflow.start",
            "version": VERSION,
            "started_at": "2026-05-14T00:00:00Z",
            "ended_at": "2026-05-14T00:10:00Z",
        },
    )
    lifecycle_items: list[dict[str, object]] = []
    for idx, stage in enumerate(("prd", "user-story", "test-case", "implement", "qa", "release")):
        lifecycle_items.extend(
            [
                {
                    "event_id": f"{stage}-started",
                    "run_id": "run-closed",
                    "stage": stage,
                    "event": "stage_started",
                    "source": "test",
                    "source_session_id": "run-closed",
                    "evidence_ref": [],
                    "ts": f"2026-05-14T00:00:0{idx}Z",
                    "attempt_seq": 1,
                },
                {
                    "event_id": f"{stage}-context",
                    "run_id": "run-closed",
                    "stage": stage,
                    "event": "stage_context_injected",
                    "source": "test",
                    "source_session_id": "run-closed",
                    "evidence_ref": [],
                    "ts": f"2026-05-14T00:01:0{idx}Z",
                    "attempt_seq": 1,
                },
                {
                    "event_id": f"{stage}-finished",
                    "run_id": "run-closed",
                    "stage": stage,
                    "event": "stage_finished",
                    "source": "test",
                    "source_session_id": "run-closed",
                    "evidence_ref": [],
                    "ts": f"2026-05-14T00:02:0{idx}Z",
                    "attempt_seq": 1,
                },
                {
                    "event_id": f"{stage}-writeback",
                    "run_id": "run-closed",
                    "stage": stage,
                    "event": "memory_writeback",
                    "source": "test",
                    "source_session_id": "run-closed",
                    "evidence_ref": [],
                    "ts": f"2026-05-14T00:03:0{idx}Z",
                    "attempt_seq": 1,
                },
            ]
        )
    lifecycle_items.extend(
        [
            {
                "event_id": "qa-retry-started",
                "run_id": "run-closed",
                "stage": "qa",
                "event": "stage_started",
                "source": "test",
                "source_session_id": "run-closed",
                "evidence_ref": [],
                "ts": "2026-05-14T00:04:00Z",
                "attempt_seq": 2,
            },
            {
                "event_id": "qa-retry-context",
                "run_id": "run-closed",
                "stage": "qa",
                "event": "stage_context_injected",
                "source": "test",
                "source_session_id": "run-closed",
                "evidence_ref": [],
                "ts": "2026-05-14T00:04:10Z",
                "attempt_seq": 2,
            },
            {
                "event_id": "qa-retry-finished",
                "run_id": "run-closed",
                "stage": "qa",
                "event": "stage_finished",
                "source": "test",
                "source_session_id": "run-closed",
                "evidence_ref": [],
                "ts": "2026-05-14T00:04:20Z",
                "attempt_seq": 2,
            },
        ]
    )
    _write_json(
        tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json",
        {
            "schema_version": "1.0",
            "updated_at": "2026-05-14T00:10:00Z",
            "items": lifecycle_items,
        },
    )

    assert _resolve_latest_closed_workflow_run_id(tmp_path, version=VERSION) == "run-closed"


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


def test_release_memory_profile_does_not_fallback_to_historical_release_event(tmp_path: Path, monkeypatch) -> None:
    _write_json(tmp_path / ".beacon" / "gate-report.json", {"status": "Pass"})
    _write_json(
        tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json",
        {
            "schema_version": "1.0",
            "updated_at": "2026-05-21T00:00:00Z",
            "items": [
                {
                    "event_id": "evt-v147",
                    "run_id": "release:v1.4.7",
                    "stage": "release",
                    "event": "release_decision_recorded",
                    "source": "release.check",
                    "source_session_id": "release:v1.4.7",
                    "evidence_ref": ["docs/beacon/v1.4.7/.machine/change/v1.4.7.json"],
                    "ts": "2026-05-20T00:00:00Z",
                    "details": {"version": "v1.4.7"},
                }
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

    issues = check_release_memory_profile(tmp_path, GateMode.STRICT, "release", "v1.4.8")

    assert [item["reason_code"] for item in issues] == ["release_decision_missing_for_version"]
    assert issues[0]["details"] == {"version": "v1.4.8"}


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


def test_v140_spec_consistency_should_prefer_acceptance_run_fingerprint_for_release(tmp_path: Path, monkeypatch) -> None:
    feature = "feature-a"
    _write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"qa-acceptance-{feature}.json",
        {"feature": feature, "version": VERSION, "run_id": "run-acceptance", "verdict": "passed"},
    )
    write_json(
        tmp_path / ".beacon" / "state" / "spec-fingerprints" / VERSION / "run-acceptance.json",
        {
            "run_id": "run-acceptance",
            "version": VERSION,
            "fingerprint_hash": "acceptance-fingerprint",
        },
    )
    _write_json(
        tmp_path / ".beacon" / "auto-test-status.json",
        {
            "status": "passed",
            "version": VERSION,
            "spec_fingerprint_hash": "acceptance-fingerprint",
            "execution": {"spec_fingerprint": {"fingerprint_hash": "acceptance-fingerprint"}},
        },
    )
    monkeypatch.setattr(
        gate_module,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "acceptance": {
                "source": "qa_acceptance_envelope",
                "feature": feature,
                "acceptance_envelope_path": f"docs/beacon/{VERSION}/.machine/execution/qa-acceptance-{feature}.json",
            }
        },
    )

    issues, verdict = check_spec_consistency(tmp_path, GateMode.STRICT, "release", version=VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "spec_impl_drift_detected" not in reason_codes
    assert verdict["expected_spec_fingerprint"] == "acceptance-fingerprint"
