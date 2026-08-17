from __future__ import annotations

import json
import subprocess
from pathlib import Path

from beacon.commands import qa as qa_command
from beacon.utils.qa_feature import _previous_evidence_done


def test_v135_sanitize_auto_test_passthrough_args_should_drop_qa_only_options() -> None:
    args = [
        "Beacon Feature",
        "--project",
        "/tmp/project",
        "--version",
        "v1.3.5",
        "--mode",
        "feature-aware",
        "--runtime",
        "file",
        "--host-runtime",
        "codex",
        "--team-mode",
        "--layer-command",
        "contract=python3 -m pytest -q tests/test_v135_change_loop_surface.py",
    ]

    sanitized = qa_command._sanitize_auto_test_passthrough_args(args)

    assert "Beacon Feature" not in sanitized
    assert "--project" not in sanitized
    assert "--version" not in sanitized
    assert "--mode" not in sanitized
    assert "--runtime" not in sanitized
    assert "--host-runtime" not in sanitized
    assert "--team-mode" not in sanitized
    assert sanitized == [
        "--layer-command",
        "contract=python3 -m pytest -q tests/test_v135_change_loop_surface.py",
    ]


def test_v135_run_feature_aware_qa_should_block_when_auto_test_invocation_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    matrix_path = tmp_path / ".beacon" / "qa" / "features" / "feature" / "matrix.qa9.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text('{"entries":[]}\n', encoding="utf-8")

    plan = {
        "schema_version": "1.0",
        "feature": "Beacon Feature",
        "feature_slug": "feature",
        "version": "v1.3.5",
        "status": "rerun_required",
        "implementation_done": True,
        "implementation_run_id": "impl-run-1",
        "reason_codes": ["spec_fingerprint_changed"],
        "targeted_layers": ["contract"],
        "targeted_entries": [{"tc_id": "TC-008", "source_tc_id": "TC-008", "ac_id": "AC-002", "qa_type": "contract"}],
    }
    captured: dict[str, object] = {}

    monkeypatch.setattr(qa_command, "resolve_profile_for_feature", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "evaluate_project_profile_gate", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "build_requirement_package_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "load_current_qa_session", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_command, "build_feature_qa_plan", lambda *args, **kwargs: plan)
    monkeypatch.setattr(qa_command, "qa_team_contract", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_implement_to_qa_handoff", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "materialize_feature_qa_matrix", lambda *args, **kwargs: matrix_path)
    monkeypatch.setattr(qa_command, "detect_host_runtime", lambda value=None: value or "codex")
    monkeypatch.setattr(qa_command, "runtime_readiness_precheck", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "delegation_readiness_precheck", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(qa_command, "_beacon_exec_silent", lambda *args, **kwargs: 2)
    monkeypatch.setattr(
        qa_command,
        "load_qa_status",
        lambda *_args, **_kwargs: {
            "status": "passed",
            "run_id": "stale-run",
            "qa9": {"qa_matrix_path": str(tmp_path / "wrong-matrix.qa9.json")},
        },
    )
    monkeypatch.setattr(
        qa_command,
        "write_feature_qa_status",
        lambda _project_root, *, feature, payload: captured.update({"payload": payload}) or (tmp_path / "feature-status.json"),
    )
    monkeypatch.setattr(qa_command, "_update_evidence_manifest", lambda *args, **kwargs: None)

    exit_code, payload = qa_command._run_feature_aware_qa(
        [
            "Beacon Feature",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.5",
            "--host-runtime",
            "codex",
            "--team-mode",
            "--json",
        ]
    )

    assert exit_code == 2
    assert payload["status"] == "blocked"
    assert "auto_test_invocation_failed" in payload["reason_codes"]
    assert payload["message"] == "auto-test qa9 invocation failed; stale QA status was not accepted"
    auto_test_args = payload["auto_test_args"]
    assert "--host-runtime" not in auto_test_args
    assert "--team-mode" not in auto_test_args
    assert captured["payload"]["status"] == "blocked"


def test_v135_run_feature_aware_qa_should_write_status_when_auto_test_times_out(
    tmp_path: Path,
    monkeypatch,
) -> None:
    matrix_path = tmp_path / ".beacon" / "qa" / "features" / "feature" / "matrix.qa9.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text('{"entries":[]}\n', encoding="utf-8")

    plan = {
        "schema_version": "1.0",
        "feature": "Beacon Feature",
        "feature_slug": "feature",
        "version": "v1.3.5",
        "status": "rerun_required",
        "implementation_done": True,
        "implementation_run_id": "impl-run-1",
        "reason_codes": [],
        "targeted_layers": ["contract"],
        "targeted_entries": [{"tc_id": "TC-008", "source_tc_id": "TC-008", "ac_id": "AC-002", "qa_type": "contract"}],
    }
    captured: dict[str, object] = {}

    monkeypatch.setenv("BEACON_QA_RUNNER_TIMEOUT_SECONDS", "1")
    monkeypatch.setattr(qa_command, "resolve_profile_for_feature", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "evaluate_project_profile_gate", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "build_requirement_package_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "build_requirement_completeness_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "load_current_qa_session", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_command, "build_feature_qa_plan", lambda *args, **kwargs: plan)
    monkeypatch.setattr(qa_command, "qa_team_contract", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_implement_to_qa_handoff", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "materialize_feature_qa_matrix", lambda *args, **kwargs: matrix_path)
    monkeypatch.setattr(qa_command, "detect_host_runtime", lambda value=None: value or "codex")
    monkeypatch.setattr(qa_command, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        qa_command,
        "_beacon_exec_silent",
        lambda *args, **kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired(cmd=["beacon"], timeout=1)),
    )
    monkeypatch.setattr(
        qa_command,
        "write_feature_qa_status",
        lambda _project_root, *, feature, payload: captured.update({"payload": payload}) or (tmp_path / "feature-status.json"),
    )
    monkeypatch.setattr(qa_command, "_update_evidence_manifest", lambda *args, **kwargs: None)

    exit_code, payload = qa_command._run_feature_aware_qa(
        [
            "Beacon Feature",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.5",
            "--json",
        ]
    )

    assert exit_code == 2
    assert payload["status"] == "blocked"
    assert "qa_runner_timeout" in payload["reason_codes"]
    assert payload["command_error_reason"] == "qa_runner_timeout"
    assert captured["payload"]["status"] == "blocked"


def test_v135_run_feature_aware_qa_should_block_when_observed_matrix_is_stale(
    tmp_path: Path,
    monkeypatch,
) -> None:
    matrix_path = tmp_path / ".beacon" / "qa" / "features" / "feature" / "matrix.qa9.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text('{"entries":[]}\n', encoding="utf-8")

    plan = {
        "schema_version": "1.0",
        "feature": "Beacon Feature",
        "feature_slug": "feature",
        "version": "v1.3.5",
        "status": "rerun_required",
        "implementation_done": True,
        "implementation_run_id": "impl-run-1",
        "reason_codes": [],
        "targeted_layers": ["contract"],
        "targeted_entries": [{"tc_id": "TC-008", "source_tc_id": "TC-008", "ac_id": "AC-002", "qa_type": "contract"}],
    }
    captured: dict[str, object] = {}

    monkeypatch.setattr(qa_command, "resolve_profile_for_feature", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "evaluate_project_profile_gate", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_current_qa_session", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_command, "build_feature_qa_plan", lambda *args, **kwargs: plan)
    monkeypatch.setattr(qa_command, "qa_team_contract", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_implement_to_qa_handoff", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "materialize_feature_qa_matrix", lambda *args, **kwargs: matrix_path)
    monkeypatch.setattr(qa_command, "detect_host_runtime", lambda value=None: value or "codex")
    monkeypatch.setattr(qa_command, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(qa_command, "_beacon_exec_silent", lambda *args, **kwargs: 0)
    monkeypatch.setattr(
        qa_command,
        "load_qa_status",
        lambda *_args, **_kwargs: {
            "status": "passed",
            "run_id": "wrong-run",
            "qa9": {"qa_matrix_path": str(tmp_path / "other-feature" / "matrix.qa9.json")},
        },
    )
    monkeypatch.setattr(
        qa_command,
        "write_feature_qa_status",
        lambda _project_root, *, feature, payload: captured.update({"payload": payload}) or (tmp_path / "feature-status.json"),
    )
    monkeypatch.setattr(qa_command, "_update_evidence_manifest", lambda *args, **kwargs: None)

    exit_code, payload = qa_command._run_feature_aware_qa(
        [
            "Beacon Feature",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.5",
            "--json",
        ]
    )

    assert exit_code == 2
    assert payload["status"] == "blocked"
    assert "qa_matrix_mismatch" in payload["reason_codes"]
    assert payload["expected_qa_matrix_path"] == str(matrix_path)
    assert payload["observed_qa_matrix_path"].endswith("other-feature/matrix.qa9.json")
    assert captured["payload"]["status"] == "blocked"


def test_v135_run_feature_aware_qa_should_resolve_matching_summary_when_global_status_is_stale(
    tmp_path: Path,
    monkeypatch,
) -> None:
    matrix_path = tmp_path / ".beacon" / "qa" / "features" / "feature" / "matrix.qa9.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text('{"entries":[]}\n', encoding="utf-8")

    plan = {
        "schema_version": "1.0",
        "feature": "Beacon Feature",
        "feature_slug": "feature",
        "version": "v1.3.5",
        "status": "rerun_required",
        "implementation_done": True,
        "implementation_run_id": "impl-run-1",
        "reason_codes": [],
        "targeted_layers": ["contract"],
        "targeted_entries": [{"tc_id": "TC-008", "source_tc_id": "TC-008", "ac_id": "AC-002", "qa_type": "contract"}],
        "targeted_tc_ids": ["TC-008"],
        "targeted_source_tc_ids": ["TC-008"],
        "targeted_ac_ids": ["AC-002"],
        "targeted_scenario_ids": [],
        "targeted_scenario_families": [],
        "story_sequence": [],
        "story_scenario_map_path": ".beacon/story-scenario-map.json",
        "blocking_artifact_updates": [],
        "execution_mode": "feature-aware",
        "boundary_principles": [],
    }

    stale_status = {
        "status": "passed",
        "run_id": "wrong-run",
        "qa9": {"qa_matrix_path": str(tmp_path / "other-feature" / "matrix.qa9.json")},
    }

    def fake_exec(*_args, **_kwargs):
        summary_path = tmp_path / ".beacon" / "evidence" / "auto-test" / "run-20260423T200000123456" / "summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(
                {
                    "status": "passed",
                    "run_id": "run-20260423T200000123456",
                    "version": "v1.3.5",
                    "execution": {
                        "run_id": "run-20260423T200000123456",
                        "layers": [],
                        "artifacts": [],
                    },
                    "qa9": {
                        "qa_matrix_path": str(matrix_path),
                        "summary": {"cases_total": 1, "passed": 1, "failed": 0},
                        "tc_results": [],
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return 0

    monkeypatch.setattr(qa_command, "resolve_profile_for_feature", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "evaluate_project_profile_gate", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_current_qa_session", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_command, "build_feature_qa_plan", lambda *args, **kwargs: plan)
    monkeypatch.setattr(qa_command, "qa_team_contract", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_implement_to_qa_handoff", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "materialize_feature_qa_matrix", lambda *args, **kwargs: matrix_path)
    monkeypatch.setattr(qa_command, "detect_host_runtime", lambda value=None: value or "codex")
    monkeypatch.setattr(qa_command, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(qa_command, "_beacon_exec_silent", fake_exec)
    monkeypatch.setattr(qa_command, "load_qa_status", lambda *_args, **_kwargs: stale_status)
    monkeypatch.setattr(qa_command, "collect_verification_writeback", lambda **kwargs: (["AC-002", "TEST-008"], [], []))
    monkeypatch.setattr(qa_command, "record_verification_writeback", lambda *args, **kwargs: {})
    acceptance_calls: dict[str, object] = {}
    monkeypatch.setattr(
        qa_command,
        "record_acceptance_writeback",
        lambda *args, **kwargs: acceptance_calls.update({"kwargs": kwargs})
        or {
            "machine_path": "docs/beacon/v1.3.5/.machine/execution/qa-acceptance-feature.json",
            "markdown_path": "docs/beacon/v1.3.5/execution/qa-acceptance-brief-feature.md",
            "acceptance_envelope": {
                "transaction_id": "tx-qa-acceptance-feature",
                "source_hash": "sha256:acceptance",
                "projection_seq": 1,
            },
        },
    )
    monkeypatch.setattr(qa_command, "writeback_feature_matrix_evidence", lambda *args, **kwargs: matrix_path)
    monkeypatch.setattr(qa_command, "build_exhaustiveness_report", lambda *args, **kwargs: {"status": "passed"})
    monkeypatch.setattr(qa_command, "write_exhaustiveness_report", lambda *args, **kwargs: tmp_path / "exhaustiveness.json")
    monkeypatch.setattr(
        qa_command,
        "build_feature_qa_precision_artifacts",
        lambda *args, **kwargs: ([], {}, {"release_ready": True, "stop_reasons": []}, tmp_path / "ac-closure.json", tmp_path / "feature-scorecard.json"),
    )
    monkeypatch.setattr(
        qa_command,
        "generate_spec_fingerprint",
        lambda *args, **kwargs: {"fingerprint_hash": "spec-hash", "generated_at": "2026-04-23T20:00:00+08:00"},
    )
    monkeypatch.setattr(qa_command, "write_qa_status", lambda *args, **kwargs: {"legacy": ".beacon/auto-test-status.json", "canonical": ".beacon/qa/status.json"})
    monkeypatch.setattr(qa_command, "write_coverage_summary", lambda *args, **kwargs: tmp_path / ".beacon" / "coverage-summary.json")
    monkeypatch.setattr(qa_command, "write_feature_qa_status", lambda _project_root, *, feature, payload: tmp_path / "feature-status.json")
    monkeypatch.setattr(qa_command, "_update_evidence_manifest", lambda *args, **kwargs: None)
    monkeypatch.setattr(qa_command, "refresh_evidence_manifest", lambda *args, **kwargs: None)

    exit_code, payload = qa_command._run_feature_aware_qa(
        [
            "Beacon Feature",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.5",
            "--json",
        ]
    )

    assert exit_code == 0
    assert payload["status"] == "passed"
    assert payload["run_id"] == "run-20260423T200000123456"
    assert payload["acceptance_writeback"]["status"] == "completed"
    assert payload["acceptance_writeback"]["transaction_id"] == "tx-qa-acceptance-feature"
    assert acceptance_calls["kwargs"]["accepted_by"] == "qa"
    assert acceptance_calls["kwargs"]["verdict"] == "passed"
    assert ".beacon/coverage-summary.json" in acceptance_calls["kwargs"]["evidence_ref"]


def test_v135_previous_evidence_done_should_reject_zero_coverage_status() -> None:
    previous = {
        "evidence_done": True,
        "current_spec_fingerprint_hash": "spec-1",
        "implementation_run_id": "impl-1",
        "source_matrix_path": "docs/matrix.json",
        "feature_scorecard": {
            "coverage_current": {
                "executed_scenarios": 0,
            }
        },
        "scenario_results_v2": [],
    }

    assert (
        _previous_evidence_done(
            previous,
            spec_hash="spec-1",
            implementation_run_id="impl-1",
            source_matrix_path="docs/matrix.json",
        )
        is False
    )


def test_v135_run_feature_aware_qa_should_refresh_manifest_with_plan_when_reusing_existing_pass(
    tmp_path: Path,
    monkeypatch,
) -> None:
    feature = "Beacon Feature"
    captured_manifest: dict[str, object] = {}

    monkeypatch.setattr(qa_command, "resolve_profile_for_feature", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "evaluate_project_profile_gate", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "build_requirement_package_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_command, "load_current_qa_session", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        qa_command,
        "build_feature_qa_plan",
        lambda *args, **kwargs: {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": "feature",
            "version": "v1.3.10",
            "status": "up_to_date",
            "implementation_done": True,
            "implementation_run_id": "impl-run-1",
            "targeted_entries": [],
        },
    )
    monkeypatch.setattr(qa_command, "qa_team_contract", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "load_implement_to_qa_handoff", lambda *args, **kwargs: {})
    monkeypatch.setattr(qa_command, "detect_host_runtime", lambda value=None: value or "codex")
    monkeypatch.setattr(
        qa_command,
        "load_qa_status",
        lambda *_args, **_kwargs: {
            "status": "passed",
            "run_id": "run-123",
        },
    )
    monkeypatch.setattr(
        qa_command,
        "write_feature_qa_status",
        lambda _project_root, *, feature, payload: tmp_path / ".beacon" / "qa" / "features" / "feature" / "status.json",
    )
    monkeypatch.setattr(qa_command, "write_coverage_summary", lambda *args, **kwargs: tmp_path / ".beacon" / "coverage-summary.json")
    monkeypatch.setattr(
        qa_command,
        "_update_evidence_manifest",
        lambda _project_root, refs, run_id, version: captured_manifest.update(
            {"refs": list(refs), "run_id": run_id, "version": version}
        ),
    )

    exit_code, payload = qa_command._run_feature_aware_qa(
        ["Beacon Feature", "--project", str(tmp_path), "--version", "v1.3.10", "--json"]
    )

    assert exit_code == 0
    assert payload["status"] == "passed"
    assert (
        ".beacon/qa/features/beacon-feature/plan.json"
        in captured_manifest["refs"]
    )


def test_v135_qa_evolve_should_preserve_existing_pass_evidence_when_up_to_date(
    tmp_path: Path,
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}
    feature = "Beacon Feature"
    existing_status = {
        "feature": feature,
        "status": "passed",
        "evidence_done": True,
        "run_id": "run-123",
        "release_ready": True,
        "feature_scorecard": {"release_ready": True},
        "acceptance_writeback": {"status": "completed"},
    }
    plan = {
        "feature": feature,
        "feature_slug": "beacon-feature",
        "version": "v1.3.5",
        "status": "up_to_date",
        "implementation_done": True,
        "evidence_done": True,
        "targeted_entries": [],
    }

    monkeypatch.setattr(qa_command, "_default_feature_qa_ui_runner", lambda *_args, **_kwargs: "playwright")
    monkeypatch.setattr(qa_command, "build_feature_qa_plan", lambda *args, **kwargs: dict(plan))
    monkeypatch.setattr(qa_command, "load_feature_qa_status", lambda *_args, **_kwargs: existing_status)
    monkeypatch.setattr(
        qa_command,
        "write_feature_qa_status",
        lambda _project_root, *, feature, payload: captured.update({"payload": payload}) or (tmp_path / "status.json"),
    )

    qa_command.evolve(
        feature=feature,
        project=str(tmp_path),
        version="v1.3.5",
        mode="feature-aware",
        write_matrix=True,
        json_output=False,
    )

    payload = captured["payload"]
    assert payload["status"] == "up_to_date"
    assert payload["previous_status"] == "passed"
    assert payload["run_id"] == "run-123"
    assert payload["release_ready"] is True
    assert payload["acceptance_writeback"]["status"] == "completed"
