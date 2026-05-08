from __future__ import annotations

import importlib
import json
from pathlib import Path
import subprocess


implement_cmd = importlib.import_module("beacon.commands.implement")
qa_cmd = importlib.import_module("beacon.commands.qa")
implement_legacy = implement_cmd._legacy_cli


def _patch_implement_execution_prereqs(monkeypatch, tmp_path: Path, *, adapter_type: str = "command", command: str = "fake-runner"):
    monkeypatch.setattr(implement_legacy, "resolve_target_version", lambda _root, version: version)
    monkeypatch.setattr(implement_legacy, "load_feature_archive_boundary", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(implement_legacy, "_requirement_closure_preflight", lambda *_args, **_kwargs: {"blocked": False})
    monkeypatch.setattr(implement_legacy, "load_beacon_config", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "_branch_guard_inputs", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "generate_run_id", lambda *_args, **_kwargs: "run-exec")
    monkeypatch.setattr(implement_legacy, "evaluate_takeover_baseline_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(
        implement_legacy,
        "_run_branch_preflight",
        lambda **_kwargs: {"blocked": False, "expected_branch": "beacon/v1.4.0", "current_branch": "beacon/v1.4.0"},
    )
    monkeypatch.setattr(implement_legacy, "implementation_plan_supported", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(
        implement_legacy,
        "resolve_adapter",
        lambda *_args, **_kwargs: (
            "fake-runner",
            {"adapter_type": adapter_type, "command": command, "args": []},
        ),
    )
    monkeypatch.setattr(implement_legacy, "_resolve_host_runtime_for_adapter", lambda **_kwargs: "codex")
    monkeypatch.setattr(implement_legacy, "_requires_host_native_prechecks", lambda **_kwargs: False)
    monkeypatch.setattr(
        implement_legacy,
        "_artifacts",
        lambda *_args, **_kwargs: {
            "source_of_truth_root": "docs/beacon/v1.4.0",
            "prd": "docs/beacon/v1.4.0/prd/sample.md",
            "user_story": "docs/beacon/v1.4.0/user-story/sample.md",
            "test_case": "docs/beacon/v1.4.0/qa/test-cases/sample.md",
            "ac_matrix": "docs/beacon/v1.4.0/.machine/sample-ac-matrix.json",
        },
    )
    monkeypatch.setattr(
        implement_legacy,
        "load_or_build_semantic_layer",
        lambda *_args, **_kwargs: {"artifacts": {}, "default_design_bridge": {}},
    )
    monkeypatch.setattr(implement_legacy, "load_revision_delta", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "build_default_task_prompt", lambda **_kwargs: "implement the frozen requirement")
    monkeypatch.setattr(
        implement_legacy,
        "_render_effective_task_prompt",
        lambda **_kwargs: str(_kwargs.get("default_prompt", "")),
    )
    monkeypatch.setattr(implement_legacy, "build_delivery_contract", lambda **_kwargs: {"contract": "ok"})
    monkeypatch.setattr(
        implement_legacy,
        "admit_runtime_skill",
        lambda *_args, **_kwargs: {"status": "pass", "reason_code": "", "artifacts": {}, "contract": {}},
    )


def _patch_qa_status_prereqs(monkeypatch, tmp_path: Path, *, feature: str = "Beacon Feature", version: str = "v1.4.0"):
    monkeypatch.setattr(qa_cmd, "resolve_profile_for_feature", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_cmd, "evaluate_project_profile_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_cmd, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_cmd, "build_requirement_completeness_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_cmd, "load_current_qa_session", lambda *_args, **_kwargs: {"runner_type": "agent-browser"})
    monkeypatch.setattr(qa_cmd, "qa_team_contract", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_cmd, "load_implement_to_qa_handoff", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_cmd, "detect_host_runtime", lambda value=None: value or "codex")
    monkeypatch.setattr(qa_cmd, "write_coverage_summary", lambda *_args, **_kwargs: tmp_path / ".beacon" / "coverage-summary.json")
    monkeypatch.setattr(
        qa_cmd,
        "_update_evidence_manifest",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        qa_cmd,
        "write_feature_qa_status",
        lambda _project_root, *, feature, payload: tmp_path / ".beacon" / "qa" / "features" / "beacon-feature" / "status.json",
    )


def test_qa_metadata_gate_blocked_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    metadata_path = tmp_path / "meta.json"
    metadata_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(qa_cmd, "metadata_machine_path", lambda _root: metadata_path)
    monkeypatch.setattr(qa_cmd, "verify_project_metadata", lambda *_args, **_kwargs: {"status": "fail"})

    code, payload = qa_cmd._run_feature_aware_qa(
        ["sample-feature", "--project", str(tmp_path), "--version", "v1.4.0", "--json"]
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["decision_surface"]["stage"] == "qa"
    assert payload["guardrail_contract"]["fail_closed"] is True
    assert payload["guardrail_contract"]["blocked"] is True


def test_qa_runtime_precheck_blocked_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(qa_cmd, "metadata_machine_path", lambda _root: tmp_path / "missing.json")
    monkeypatch.setattr(qa_cmd, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_cmd, "build_requirement_completeness_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_cmd, "resolve_profile_for_feature", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(qa_cmd, "evaluate_project_profile_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(qa_cmd, "runtime_context_precheck_required", lambda **_kwargs: True)
    monkeypatch.setattr(
        qa_cmd,
        "runtime_readiness_precheck",
        lambda *_args, **_kwargs: {"status": "blocked", "reason_code": "runtime_not_ready", "recommended_command": "beacon doctor"},
    )
    monkeypatch.setattr(
        qa_cmd,
        "delegation_readiness_precheck",
        lambda *_args, **_kwargs: {"status": "pass"},
    )

    code, payload = qa_cmd._run_feature_aware_qa(
        ["sample-feature", "--project", str(tmp_path), "--version", "v1.4.0", "--team-mode", "--json"]
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["decision_surface"]["stage"] == "qa"
    assert payload["guardrail_contract"]["reason_code"] == "runtime_not_ready"
    assert payload["recommended_command"] == "beacon doctor"


def test_implement_takeover_gate_blocked_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(implement_legacy, "load_feature_archive_boundary", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(implement_legacy, "_requirement_closure_preflight", lambda *_args, **_kwargs: {"blocked": False})
    monkeypatch.setattr(implement_legacy, "load_beacon_config", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "_branch_guard_inputs", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "generate_run_id", lambda *_args, **_kwargs: "run-1")
    monkeypatch.setattr(
        implement_legacy,
        "evaluate_takeover_baseline_gate",
        lambda *_args, **_kwargs: {"status": "blocked"},
    )

    code, payload = implement_legacy.run_implement_stage(
        feature="sample-feature",
        project_root=tmp_path,
        version="v1.4.0",
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["decision_surface"]["stage"] == "implement"
    assert payload["guardrail_contract"]["reason_code"] == "takeover_baseline_required"
    assert payload["guardrail_contract"]["fail_closed"] is True


def test_implement_branch_preflight_blocked_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(implement_legacy, "load_feature_archive_boundary", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(implement_legacy, "_requirement_closure_preflight", lambda *_args, **_kwargs: {"blocked": False})
    monkeypatch.setattr(implement_legacy, "load_beacon_config", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "_branch_guard_inputs", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(implement_legacy, "generate_run_id", lambda *_args, **_kwargs: "run-2")
    monkeypatch.setattr(
        implement_legacy,
        "evaluate_takeover_baseline_gate",
        lambda *_args, **_kwargs: {"status": "pass"},
    )
    monkeypatch.setattr(
        implement_legacy,
        "_run_branch_preflight",
        lambda **_kwargs: {
            "blocked": True,
            "recommended_command": "beacon implement check-branch",
            "expected_branch": "beacon/v1.4.0",
            "current_branch": "main",
        },
    )

    code, payload = implement_legacy.run_implement_stage(
        feature="sample-feature",
        project_root=tmp_path,
        version="v1.4.0",
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["decision_surface"]["stage"] == "implement"
    assert payload["guardrail_contract"]["reason_code"] == "implement_branch_guard_blocked"
    assert payload["recommended_command"] == "beacon implement check-branch"


def test_implement_native_skill_execution_unsupported_includes_decision_surface(tmp_path: Path, monkeypatch):
    _patch_implement_execution_prereqs(monkeypatch, tmp_path, adapter_type="native")

    code, payload = implement_legacy.run_implement_stage(
        feature="sample-feature",
        project_root=tmp_path,
        version="v1.4.0",
        skill="project:custom-skill",
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "native_skill_execution_unsupported"
    assert payload["decision_surface"]["stage"] == "implement"
    assert payload["guardrail_contract"]["blocked"] is True
    assert payload["guardrail_contract"]["reason_code"] == "native_skill_execution_unsupported"


def test_implement_native_runner_failed_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    _patch_implement_execution_prereqs(monkeypatch, tmp_path, adapter_type="native")
    monkeypatch.setattr(
        implement_legacy,
        "run_native_implementation",
        lambda *_args, **_kwargs: {"status": "failed", "reason_code": "native_runner_failed", "summary": "failed"},
    )

    code, payload = implement_legacy.run_implement_stage(
        feature="sample-feature",
        project_root=tmp_path,
        version="v1.4.0",
    )

    assert code == 2
    assert payload["status"] == "failed"
    assert payload["decision_surface"]["stage"] == "implement"
    assert payload["guardrail_contract"]["blocked"] is True
    assert payload["guardrail_contract"]["reason_code"] == "native_runner_failed"


def test_implement_runner_timeout_failed_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    _patch_implement_execution_prereqs(monkeypatch, tmp_path)

    def _raise_timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd=["fake-runner"], timeout=5)

    monkeypatch.setattr(implement_legacy.subprocess, "run", _raise_timeout)

    code, payload = implement_legacy.run_implement_stage(
        feature="sample-feature",
        project_root=tmp_path,
        version="v1.4.0",
        timeout_sec=5,
    )

    assert code == 2
    assert payload["status"] == "failed"
    assert payload["reason_code"] == "runner_execution_timeout"
    assert payload["decision_surface"]["stage"] == "implement"
    assert payload["guardrail_contract"]["blocked"] is True
    assert payload["guardrail_contract"]["reason_code"] == "runner_execution_timeout"


def test_implement_runner_result_invalid_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    _patch_implement_execution_prereqs(monkeypatch, tmp_path)

    def _write_invalid_result(command, cwd, capture_output, text, timeout, env):  # noqa: ARG001
        result_path = Path(cwd) / ".beacon/implement/run-exec/result.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps({"status": "completed"}), encoding="utf-8")

        class _Completed:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Completed()

    monkeypatch.setattr(implement_legacy.subprocess, "run", _write_invalid_result)
    monkeypatch.setattr(implement_legacy, "_validate_result", lambda _payload: ["missing changed_files"])

    code, payload = implement_legacy.run_implement_stage(
        feature="sample-feature",
        project_root=tmp_path,
        version="v1.4.0",
    )

    assert code == 2
    assert payload["status"] == "failed"
    assert payload["reason_code"] == "runner_result_invalid"
    assert payload["decision_surface"]["stage"] == "implement"
    assert payload["guardrail_contract"]["blocked"] is True
    assert payload["guardrail_contract"]["reason_code"] == "runner_result_invalid"
    assert payload["problems"] == ["missing changed_files"]


def test_qa_reused_existing_pass_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    feature = "Beacon Feature"
    _patch_qa_status_prereqs(monkeypatch, tmp_path, feature=feature)
    monkeypatch.setattr(
        qa_cmd,
        "build_feature_qa_plan",
        lambda *_args, **_kwargs: {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": "beacon-feature",
            "version": "v1.4.0",
            "status": "needs_run",
            "implementation_done": True,
            "implementation_run_id": "impl-run-1",
            "targeted_entries": [],
        },
    )
    monkeypatch.setattr(
        qa_cmd,
        "load_qa_status",
        lambda *_args, **_kwargs: {"status": "passed", "run_id": "qa-run-1"},
    )

    code, payload = qa_cmd._run_feature_aware_qa(
        [feature, "--project", str(tmp_path), "--version", "v1.4.0", "--json"]
    )

    assert code == 0
    assert payload["status"] == "passed"
    assert payload["decision_surface"]["stage"] == "qa"
    assert payload["guardrail_contract"]["blocked"] is False
    assert payload["guardrail_contract"]["fail_closed"] is True
    assert payload["message"] == "feature has no executable QA matrix entries; reused existing passed QA status"


def test_qa_up_to_date_payload_includes_decision_surface(tmp_path: Path, monkeypatch):
    feature = "Beacon Feature"
    _patch_qa_status_prereqs(monkeypatch, tmp_path, feature=feature)
    monkeypatch.setattr(
        qa_cmd,
        "build_feature_qa_plan",
        lambda *_args, **_kwargs: {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": "beacon-feature",
            "version": "v1.4.0",
            "status": "up_to_date",
            "implementation_done": True,
            "implementation_run_id": "impl-run-1",
            "targeted_entries": ["TC-001"],
            "reason_codes": [],
            "targeted_layers": [],
            "targeted_ac_ids": [],
            "targeted_tc_ids": [],
            "targeted_scenario_ids": [],
            "targeted_scenario_families": [],
        },
    )
    monkeypatch.setattr(
        qa_cmd,
        "load_feature_qa_status",
        lambda *_args, **_kwargs: {"status": "passed", "execution_mode": "feature-aware", "release_ready": True},
    )
    monkeypatch.setattr(qa_cmd, "load_qa_status", lambda *_args, **_kwargs: {"run_id": "qa-run-2"})

    code, payload = qa_cmd._run_feature_aware_qa(
        [feature, "--project", str(tmp_path), "--version", "v1.4.0", "--json"]
    )

    assert code == 0
    assert payload["status"] == "up_to_date"
    assert payload["decision_surface"]["stage"] == "qa"
    assert payload["guardrail_contract"]["blocked"] is False
    assert payload["guardrail_contract"]["fail_closed"] is True
    assert payload["message"] == "feature QA already up to date; no rerun required"
