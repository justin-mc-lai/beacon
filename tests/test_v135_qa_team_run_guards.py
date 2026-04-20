from __future__ import annotations

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
