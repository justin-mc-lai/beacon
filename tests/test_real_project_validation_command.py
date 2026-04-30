from __future__ import annotations

import json
import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
report_module = importlib.import_module("beacon.commands.report")


def _seed_docs(root: Path, version: str) -> None:
    docs = root / "docs" / "beacon" / version
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "release").mkdir(parents=True, exist_ok=True)
    docs.joinpath("SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    docs.joinpath("execution", "index.md").write_text("# Execution\n", encoding="utf-8")
    docs.joinpath("release", f"{version}.md").write_text("# Release\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("Use docs/beacon/global-boundaries.md\n", encoding="utf-8")
    (root / "skills" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "skills" / "beacon" / "SKILL.md").write_text("# Skill\n", encoding="utf-8")


def test_report_real_project_validation_should_surface_latest_feature_overlay(monkeypatch, tmp_path: Path) -> None:
    version = "v1.3.9"
    feature = "Beacon v1.3.9 execution projection convergence and QA acceptance dual-write"
    _seed_docs(tmp_path, version)

    def fake_run(_root: Path, args: list[str]) -> dict:
        command = " ".join(args)
        payload = {"status": "pass"}
        if args[:3] == ["gate", "check", "prototype"]:
            payload = {"status": "Pass", "issues": []}
        elif args[:3] == ["gate", "check", "release"]:
            payload = {"status": "Pass", "issues": []}
        elif args[:2] == ["release", "check"]:
            payload = {"status": "pass", "release_ready": True, "failed_checks": []}
        elif args[:2] == ["release", "scorecard"]:
            payload = {"version": version, "release_ready": True}
        return {
            "command": command,
            "exit_code": 0,
            "stdout": json.dumps(payload, ensure_ascii=False),
            "stderr": "",
            "json": payload,
        }

    monkeypatch.setattr(report_module, "_run_real_project_validation_command", fake_run)
    monkeypatch.setattr(report_module, "_git_status_lines", lambda _root: [])
    monkeypatch.setattr(
        report_module,
        "build_release_scorecard",
        lambda _root, version: {
            "version": version,
            "release_ready": True,
            "gate": {"status": "Pass", "blocked_count": 0, "reason_codes": []},
            "qa": {
                "feature": feature,
                "status": "passed",
                "evidence_done": True,
                "release_ready": True,
                "execution_mode": "feature-aware",
                "project_profile_gate_status": "pass",
                "acceptance_transaction_status": "pass",
            },
            "acceptance": {"status": "pass", "source": "qa_acceptance_envelope"},
            "feature_qa_scorecard": {
                "continue_decision": "ready_for_release",
                "review_required_count": 0,
                "needs_replay_count": 0,
                "unresolved_closure_outcomes": [],
            },
            "prompt_boundary": {"required": True, "status": "pass", "blocked": False, "surface": "host_prompt"},
            "change_documents": {
                "status": "pass",
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "feature_count": 1,
                "includes_current_feature": True,
            },
            "host_native_delivery": {"status": "pass", "reason_codes": []},
        },
    )

    result = runner.invoke(
        app,
        [
            "real-project-validation",
            "--project-root",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["recommendation"] == "safe to use on this project"
    assert f"release check {version} --project-root {tmp_path} --json" in payload["executed_commands"]
    check_ids = {item["id"]: item["status"] for item in payload["latest_feature_overlay"]["checks"]}
    assert check_ids["acceptance_projection_transaction_dual_write"] == "pass"
    assert check_ids["prototype_auto_template_downgrade_guard"] == "pass"
    assert check_ids["prompt_boundary_gate_release_convergence"] == "pass"
    assert check_ids["archive_governance_support_surface"] == "pass"
    assert check_ids["canonical_delivery_baseline_convergence"] == "pass"


def test_report_real_project_validation_should_classify_blockers_vs_defects(monkeypatch, tmp_path: Path) -> None:
    version = "v1.3.9"
    feature = "Feature"
    _seed_docs(tmp_path, version)

    def fake_run(_root: Path, args: list[str]) -> dict:
        if args[:3] == ["gate", "check", "release"]:
            payload = {"status": "Blocked", "issues": [{"reason_code": "coverage_incomplete", "blocked": True}]}
            return {
                "command": " ".join(args),
                "exit_code": 2,
                "stdout": json.dumps(payload, ensure_ascii=False),
                "stderr": "",
                "json": payload,
            }
        if args[:2] == ["archive", "plan"]:
            return {
                "command": " ".join(args),
                "exit_code": 1,
                "stdout": "",
                "stderr": "Traceback: crash",
                "json": {},
            }
        return {
            "command": " ".join(args),
            "exit_code": 0,
            "stdout": json.dumps({"status": "pass"}),
            "stderr": "",
            "json": {"status": "pass"},
        }

    monkeypatch.setattr(report_module, "_run_real_project_validation_command", fake_run)
    monkeypatch.setattr(report_module, "_git_status_lines", lambda _root: [" M docs/beacon/v1.3.9/SUMMARY.md"])
    monkeypatch.setattr(
        report_module,
        "build_release_scorecard",
        lambda _root, version: {
            "version": version,
            "release_ready": False,
            "gate": {"status": "Blocked", "blocked_count": 1, "reason_codes": ["coverage_incomplete"]},
            "qa": {"feature": feature, "status": "blocked", "evidence_done": False, "release_ready": False, "acceptance_transaction_status": "blocked"},
            "feature_qa_scorecard": {"continue_decision": "continue", "review_required_count": 1, "needs_replay_count": 0, "unresolved_closure_outcomes": ["coverage"]},
            "prompt_boundary": {"required": True, "status": "pass", "blocked": False},
            "change_documents": {"status": "blocked", "markdown_exists": True, "json_exists": True, "version_match": True, "includes_current_feature": True},
            "host_native_delivery": {"status": "pass", "reason_codes": []},
        },
    )

    result = runner.invoke(
        app,
        [
            "real-project-validation",
            "--project-root",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["worktree_dirty"] is True
    assert payload["recommendation"] == "blocked until Beacon defect is fixed"
    blocker_names = {item["name"] for item in payload["surfaces"]["project_state_blockers"]}
    defect_names = {item["name"] for item in payload["surfaces"]["beacon_defects"]}
    assert "gate_release" in blocker_names
    assert "archive_plan" in defect_names


def test_report_real_project_validation_should_treat_unsupported_public_contract_as_defect(monkeypatch, tmp_path: Path) -> None:
    version = "v1.3.9"
    feature = "Feature"
    _seed_docs(tmp_path, version)

    def fake_run(_root: Path, args: list[str]) -> dict:
        if args[:2] == ["release", "check"]:
            return {
                "command": " ".join(args),
                "exit_code": 2,
                "stdout": "",
                "stderr": "No such option: --json",
                "json": {},
            }
        return {
            "command": " ".join(args),
            "exit_code": 0,
            "stdout": json.dumps({"status": "pass"}),
            "stderr": "",
            "json": {"status": "pass"},
        }

    monkeypatch.setattr(report_module, "_run_real_project_validation_command", fake_run)
    monkeypatch.setattr(report_module, "_git_status_lines", lambda _root: [])
    monkeypatch.setattr(
        report_module,
        "build_release_scorecard",
        lambda _root, version: {
            "version": version,
            "release_ready": True,
            "gate": {"status": "Pass", "blocked_count": 0, "reason_codes": []},
            "qa": {"feature": feature, "status": "passed", "evidence_done": True, "release_ready": True, "acceptance_transaction_status": "pass"},
            "feature_qa_scorecard": {"continue_decision": "ready_for_release", "review_required_count": 0, "needs_replay_count": 0, "unresolved_closure_outcomes": []},
            "prompt_boundary": {"required": True, "status": "pass", "blocked": False},
            "change_documents": {"status": "pass", "markdown_exists": True, "json_exists": True, "version_match": True, "includes_current_feature": True},
            "host_native_delivery": {"status": "pass", "reason_codes": []},
        },
    )

    result = runner.invoke(
        app,
        [
            "real-project-validation",
            "--project-root",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    defect_names = {item["name"] for item in payload["surfaces"]["beacon_defects"]}
    assert "release_check" in defect_names
    assert payload["recommendation"] == "blocked until Beacon defect is fixed"


def test_report_real_project_validation_should_include_metadata_contract_and_human_failures_as_blockers(
    monkeypatch,
    tmp_path: Path,
) -> None:
    version = "v1.3.9"
    feature = "Feature"
    _seed_docs(tmp_path, version)

    def fake_run(_root: Path, args: list[str]) -> dict:
        command = " ".join(args)
        if args[:3] == ["doctor", "metadata", "verify"]:
            payload = {
                "schema_version": "1.0",
                "action": "doctor-metadata-verify",
                "result": {"status": "fail", "checks": [{"name": "version_contract", "status": "fail"}]},
            }
            return {
                "command": command,
                "exit_code": 2,
                "stdout": json.dumps(payload, ensure_ascii=False),
                "stderr": "",
                "json": payload,
            }
        if args[:3] == ["doctor", "metadata", "show"]:
            payload = {"schema_version": "1.0", "action": "doctor-metadata-show", "result": {"resolved_metadata_view": {}}}
            return {
                "command": command,
                "exit_code": 0,
                "stdout": json.dumps(payload, ensure_ascii=False),
                "stderr": "",
                "json": payload,
            }
        if args[:2] == ["test-case", "gate"]:
            return {
                "command": command,
                "exit_code": 1,
                "stdout": "\nTest Coverage Gate: Feature\n========================================\n✓ PASS: Test file exists\n✗ FAIL: AC matrix not found: /tmp/demo.ac-test-matrix.json\n",
                "stderr": "",
                "json": {},
            }
        return {
            "command": command,
            "exit_code": 0,
            "stdout": json.dumps({"status": "pass"}, ensure_ascii=False),
            "stderr": "",
            "json": {"status": "pass"},
        }

    monkeypatch.setattr(report_module, "_run_real_project_validation_command", fake_run)
    monkeypatch.setattr(report_module, "_git_status_lines", lambda _root: [])
    monkeypatch.setattr(
        report_module,
        "build_release_scorecard",
        lambda _root, version: {
            "version": version,
            "release_ready": True,
            "gate": {"status": "Pass", "blocked_count": 0, "reason_codes": []},
            "qa": {"feature": feature, "status": "passed", "evidence_done": True, "release_ready": True, "acceptance_transaction_status": "pass"},
            "feature_qa_scorecard": {"continue_decision": "ready_for_release", "review_required_count": 0, "needs_replay_count": 0, "unresolved_closure_outcomes": []},
            "prompt_boundary": {"required": True, "status": "pass", "blocked": False},
            "change_documents": {"status": "pass", "markdown_exists": True, "json_exists": True, "version_match": True, "includes_current_feature": True},
            "host_native_delivery": {"status": "pass", "reason_codes": []},
        },
    )

    result = runner.invoke(
        app,
        [
            "real-project-validation",
            "--project-root",
            str(tmp_path),
            "--version",
            version,
            "--feature",
            feature,
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    blocker_names = {item["name"] for item in payload["surfaces"]["project_state_blockers"]}
    defect_names = {item["name"] for item in payload["surfaces"]["beacon_defects"]}
    assert "doctor_metadata_verify" in blocker_names
    assert "test_case_gate" in blocker_names
    assert "test_case_gate" not in defect_names
    check_ids = {item["id"]: item["status"] for item in payload["latest_feature_overlay"]["checks"]}
    assert check_ids["project_metadata_governance_contract"] == "blocked"


def test_report_real_project_validation_runner_should_allow_context_version_drift(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class DummyCompleted:
        returncode = 0
        stdout = "{}"
        stderr = ""

    def fake_run(cmd, cwd=None, capture_output=None, text=None, check=None, env=None):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        captured["env"] = dict(env or {})
        return DummyCompleted()

    monkeypatch.setattr(report_module.subprocess, "run", fake_run)
    result = report_module._run_real_project_validation_command(tmp_path, ["prototype", "list"])
    assert result["exit_code"] == 0
    assert captured["cwd"] == tmp_path
    assert captured["env"]["BEACON_ALLOW_CONTEXT_VERSION_DRIFT"] == "1"
