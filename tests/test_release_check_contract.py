from __future__ import annotations

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands import release as release_command
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_release_artifacts(root: Path, *, version: str, coverage_version: str) -> None:
    beacon_dir = root / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    docs_root = root / "docs" / "beacon" / version
    machine_change = docs_root / ".machine" / "change"
    release_dir = docs_root / "change"
    machine_change.mkdir(parents=True, exist_ok=True)
    release_dir.mkdir(parents=True, exist_ok=True)

    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "version": version, "run_id": "run-123"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-123"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": "run-123",
                "entries": [
                    {"path": ".beacon/auto-test-status.json"},
                    {"path": ".beacon/gate-report.json"},
                    {"path": ".beacon/coverage-summary.json"},
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (beacon_dir / "coverage-summary.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-123",
                "version": coverage_version,
                "coverage_rate": 1.0,
                "full_coverage": True,
                "details": {
                    "version": coverage_version,
                    "feature": "",
                    "planned_story": 1,
                    "implemented_story": 1,
                    "story_coverage": 1.0,
                    "total_ac": 1,
                    "tested_ac": 1,
                    "ac_coverage": 1.0,
                    "total_tc": 1,
                    "executed_tc": 1,
                    "tc_coverage": 1.0,
                    "full_coverage": True,
                    "matrix_errors": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (machine_change / f"{version}.json").write_text(
        json.dumps(
            {
                "version": version,
                "current_feature": "feature-a",
                "features": [{"feature": "feature-a"}],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (release_dir / f"{version}.md").write_text("# release\n", encoding="utf-8")


def test_release_check_should_fail_when_coverage_summary_version_drifts(tmp_path: Path):
    version = "v1.3.4"
    _seed_release_artifacts(tmp_path, version=version, coverage_version="v1.1.10")

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])
    assert result.exit_code == 1
    assert "coverage summary version matches release version" in result.stdout
    assert "artifact_version=v1.1.10" in result.stdout


def test_release_check_should_pass_when_coverage_summary_matches_release(tmp_path: Path):
    version = "v1.3.4"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    assert "Release conditions met" in result.stdout


def test_release_check_should_support_project_root_alias_and_json_output(tmp_path: Path):
    version = "v1.3.4"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    result = _invoke(["release", "check", version, "--project-root", str(tmp_path), "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["version"] == version
    assert payload["status"] == "pass"
    assert payload["release_ready"] is True
    assert payload["failed_checks"] == []
    assert any(item["name"] == "coverage summary version matches release version" for item in payload["checks"])


def test_release_check_should_prefer_release_gate_report_over_verify_gate_report(tmp_path: Path, monkeypatch):
    version = "v1.4.5"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)
    monkeypatch.setattr(
        release_command,
        "build_requirement_package_gate",
        lambda *_args, **_kwargs: {"blocked": False},
    )

    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"stage": "verify", "status": "Pass", "version": version, "run_id": "run-verify"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "release-gate-report.json").write_text(
        json.dumps({"stage": "release", "status": "Blocked", "version": version, "run_id": "run-release", "issues": [{"reason_code": "x", "blocked": True}]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    result = _invoke(["release", "check", version, "--project-root", str(tmp_path), "--json"])

    assert result.exit_code == 1, result.stdout
    payload = json.loads(result.stdout)
    gate_check = next(item for item in payload["checks"] if item["name"] == "gate report pass")
    assert gate_check["passed"] is False
    assert gate_check["detail"] == "status=Blocked"


def test_gate_check_release_should_persist_release_gate_report_with_version_and_run_id(tmp_path: Path):
    version = "v1.4.5"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    result = _invoke(["gate", "check", "release", "--project-root", str(tmp_path), "--version", version, "--json"])

    assert result.exit_code in {0, 2}, result.stdout
    payload = json.loads((tmp_path / ".beacon" / "release-gate-report.json").read_text(encoding="utf-8"))
    assert payload["stage"] == "release"
    assert payload["version"] == version
    assert payload["run_id"] == "run-123"


def test_gate_check_release_should_refresh_manifest_for_release_gate_report(tmp_path: Path):
    version = "v1.4.5"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    result = _invoke(["gate", "check", "release", "--project-root", str(tmp_path), "--version", version, "--json"])

    assert result.exit_code in {0, 2}, result.stdout
    report_path = tmp_path / ".beacon" / "release-gate-report.json"
    manifest_path = tmp_path / ".beacon" / "evidence-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = {
        str(item.get("path")): str(item.get("sha256"))
        for item in manifest.get("entries", [])
        if isinstance(item, dict)
    }
    assert ".beacon/release-gate-report.json" in entries
    assert entries[".beacon/release-gate-report.json"] == hashlib.sha256(report_path.read_bytes()).hexdigest()


def test_gate_check_release_should_not_report_transient_release_gate_manifest_mismatch(tmp_path: Path):
    version = "v1.4.5"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    result = _invoke(["gate", "check", "release", "--project-root", str(tmp_path), "--version", version, "--json"])

    assert result.exit_code in {0, 2}, result.stdout
    payload = json.loads(result.stdout)
    reason_codes = [str(item.get("reason_code") or "") for item in payload.get("issues", []) if isinstance(item, dict)]
    assert "evidence_sha256_manifest_mismatch" not in reason_codes


def test_release_check_should_fail_when_v136_scorecard_is_not_release_ready(tmp_path: Path, monkeypatch):
    version = "v1.3.6"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "qa": {"feature": "feature-a"},
            "semantic": {"status": "fail", "reason_code": "semantic_contract_missing"},
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
            },
        },
    )

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])

    assert result.exit_code == 1, result.stdout
    assert "release scorecard ready" in result.stdout
    assert "semantic contract ready" in result.stdout
    assert "semantic_contract_missing" in result.stdout


def test_release_check_should_accept_authoritative_v136_scorecard_when_gate_run_id_and_coverage_summary_lag(
    tmp_path: Path,
    monkeypatch,
):
    version = "v1.3.6"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-gate-lag"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "coverage-summary.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-123",
                "version": version,
                "coverage_rate": 0.3333,
                "full_coverage": False,
                "details": {
                    "version": version,
                    "feature": "",
                    "planned_story": 3,
                    "implemented_story": 1,
                    "story_coverage": 0.3333,
                    "total_ac": 16,
                    "tested_ac": 16,
                    "ac_coverage": 1.0,
                    "total_tc": 23,
                    "executed_tc": 16,
                    "tc_coverage": 0.6957,
                    "full_coverage": False,
                    "matrix_errors": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": True,
            "qa": {"feature": "feature-a", "status": "passed", "evidence_done": True},
            "semantic": {"status": "pass", "reason_code": "semantic_contract_ok"},
            "feature_qa_scorecard": {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "coverage_current": {
                    "required_scenarios": 16,
                    "executed_scenarios": 16,
                    "coverage_rate": 1.0,
                },
            },
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
                "feature_count": 1,
            },
        },
    )

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])

    assert result.exit_code == 0, result.stdout
    assert "authoritative_release_scorecard=true" in result.stdout
    assert "Release conditions met" in result.stdout


def test_release_check_should_accept_authoritative_scorecard_when_manifest_and_coverage_run_id_lag(
    tmp_path: Path,
    monkeypatch,
):
    version = "v1.3.8"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    (tmp_path / ".beacon" / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": "run-stale",
                "entries": [
                    {"path": ".beacon/auto-test-status.json"},
                    {"path": ".beacon/gate-report.json"},
                    {"path": ".beacon/coverage-summary.json"},
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "coverage-summary.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-stale",
                "version": version,
                "coverage_rate": 1.0,
                "full_coverage": True,
                "details": {
                    "version": version,
                    "feature": "feature-a",
                    "planned_story": 1,
                    "implemented_story": 1,
                    "story_coverage": 1.0,
                    "total_ac": 1,
                    "tested_ac": 1,
                    "ac_coverage": 1.0,
                    "total_tc": 1,
                    "executed_tc": 1,
                    "tc_coverage": 1.0,
                    "full_coverage": True,
                    "matrix_errors": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": True,
            "gate": {
                "status": "Pass",
                "blocked_count": 0,
                "run_id": "run-123",
                "artifact_version": version,
                "version_match": True,
                "reason_codes": [],
            },
            "qa": {"feature": "feature-a", "status": "passed", "evidence_done": True},
            "semantic": {"status": "pass", "reason_code": ""},
            "feature_qa_scorecard": {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "coverage_current": {
                    "required_scenarios": 1,
                    "executed_scenarios": 1,
                    "coverage_rate": 1.0,
                },
            },
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
                "feature_count": 1,
            },
            "prompt_boundary": {
                "required": True,
                "status": "pass",
                "blocked": False,
                "classification": "in_scope_implementation",
                "reason_code": "",
                "surface": "host_prompt",
            },
        },
    )

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])

    assert result.exit_code == 0, result.stdout
    assert "evidence manifest run_id matches test artifacts" in result.stdout
    assert "coverage summary run_id matches test artifacts" in result.stdout
    assert "authoritative_release_scorecard=true" in result.stdout


def test_release_check_should_accept_authoritative_feature_qa_when_gate_run_id_and_coverage_summary_lag(
    tmp_path: Path,
    monkeypatch,
):
    version = "v1.4.6"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-stale-gate", "stage": "verify"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "release-gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": version, "run_id": "run-release", "stage": "release"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "version": version, "run_id": "run-qa-current"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "coverage-summary.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-qa-current",
                "version": version,
                "coverage_rate": 0.0,
                "full_coverage": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "evidence-manifest.json").write_text(
        json.dumps(
            {
                "version": version,
                "run_id": "run-qa-current",
                "entries": [
                    {"path": ".beacon/auto-test-status.json"},
                    {"path": ".beacon/release-gate-report.json"},
                    {"path": ".beacon/coverage-summary.json"},
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        release_command,
        "build_requirement_package_gate",
        lambda *_args, **_kwargs: {"blocked": False},
    )
    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "qa": {"feature": "feature-a", "status": "passed", "evidence_done": True, "release_ready": True},
            "semantic": {},
            "feature_qa_scorecard": {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "coverage_current": {
                    "required_scenarios": 16,
                    "executed_scenarios": 16,
                    "coverage_rate": 1.0,
                },
            },
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
                "feature_count": 1,
            },
            "prompt_boundary": {
                "required": True,
                "status": "pass",
                "blocked": False,
                "classification": "in_scope_implementation",
                "reason_code": "",
                "surface": "host_prompt",
            },
        },
    )
    monkeypatch.setattr(
        release_command,
        "acceptance_projection_transaction_contract",
        lambda *_args, **_kwargs: {"status": "pass", "reason_code": ""},
    )

    result = _invoke(["release", "check", version, "--project-root", str(tmp_path), "--json"])

    assert result.exit_code == 1, result.stdout
    payload = json.loads(result.stdout)
    gate_run_id_check = next(item for item in payload["checks"] if item["name"] == "gate report run_id matches auto-test")
    coverage_check = next(item for item in payload["checks"] if item["name"] == "coverage artifact ready")
    assert gate_run_id_check["passed"] is True
    assert coverage_check["passed"] is True
    assert "authoritative_release_scorecard=true" in gate_run_id_check["detail"]
    assert "authoritative_release_scorecard=true" in coverage_check["detail"]
    assert payload["failed_checks"] == ["release scorecard ready"]


def test_release_check_should_fail_when_v137_prompt_boundary_verdict_is_missing(tmp_path: Path, monkeypatch):
    version = "v1.3.7"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "qa": {"feature": "feature-a", "status": "passed", "evidence_done": True},
            "semantic": {"status": "pass", "reason_code": "semantic_contract_ok"},
            "prompt_boundary": {
                "required": True,
                "status": "missing",
                "blocked": True,
                "classification": "",
                "reason_code": "implement_prompt_boundary_missing",
                "surface": "host_prompt",
            },
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
                "feature_count": 1,
            },
            "feature_qa_scorecard": {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "coverage_current": {
                    "required_scenarios": 1,
                    "executed_scenarios": 1,
                    "coverage_rate": 1.0,
                },
            },
        },
    )

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])

    assert result.exit_code == 1, result.stdout
    assert "implement prompt boundary verdict pass" in result.stdout
    assert "implement_prompt_boundary_missing" in result.stdout


def test_release_check_should_fail_when_scorecard_gate_is_blocked_even_if_gate_report_artifact_passes(
    tmp_path: Path,
    monkeypatch,
):
    version = "v1.3.8"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "gate": {
                "status": "Blocked",
                "blocked_count": 1,
                "run_id": "run-123",
                "artifact_version": version,
                "version_match": True,
                "reason_codes": ["evidence_sha256_manifest_mismatch"],
            },
            "qa": {"feature": "feature-a", "status": "passed", "evidence_done": True},
            "semantic": {"status": "pass", "reason_code": "semantic_contract_ok"},
            "feature_qa_scorecard": {
                "release_ready": False,
                "continue_decision": "qa-repair",
                "coverage_current": {
                    "required_scenarios": 1,
                    "executed_scenarios": 1,
                    "coverage_rate": 1.0,
                },
            },
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
                "feature_count": 1,
            },
            "prompt_boundary": {
                "required": True,
                "status": "pass",
                "blocked": False,
                "classification": "in_scope_implementation",
                "reason_code": "",
                "surface": "host_prompt",
            },
        },
    )

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])

    assert result.exit_code == 1, result.stdout
    assert "gate report pass" in result.stdout
    assert "status=Blocked" in result.stdout


def test_release_check_should_fail_when_version_surface_governance_drift_exists(tmp_path: Path, monkeypatch):
    version = "v1.4.0"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)

    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "qa": {"feature": "feature-a", "status": "passed", "evidence_done": True},
            "semantic": {"status": "pass", "reason_code": ""},
            "feature_qa_scorecard": {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "coverage_current": {
                    "required_scenarios": 1,
                    "executed_scenarios": 1,
                    "coverage_rate": 1.0,
                },
            },
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
                "feature_count": 1,
            },
            "prompt_boundary": {
                "required": True,
                "status": "pass",
                "blocked": False,
                "classification": "in_scope_implementation",
                "reason_code": "",
                "surface": "host_prompt",
            },
            "version_surface_governance": {
                "configured": True,
                "status": "fail",
                "blocked": True,
                "reason_code": "version_surface_governance_drift",
                "manifest_path": "beacon/version-truth.json",
            },
        },
    )

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])

    assert result.exit_code == 1, result.stdout
    assert "version surface governance pass" in result.stdout
    assert "version_surface_governance_drift" in result.stdout
    assert f"repair=beacon doctor sync-version-surfaces --project-root {tmp_path}" in result.stdout
    assert f"verify=beacon doctor verify-version-surfaces --project-root {tmp_path} --strict" in result.stdout


def test_release_check_should_print_browser_blocker_repairs(tmp_path: Path, monkeypatch):
    version = "v1.4.2"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)
    monkeypatch.setattr(
        release_command,
        "build_requirement_package_gate",
        lambda *_args, **_kwargs: {"status": "pass", "reason_code": "", "recommended_command": ""},
    )

    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "qa": {"feature": "feature-a"},
            "semantic": {},
            "browser_release_reason_codes": [
                "protected_surface_session_bridge_missing",
                "browser_evidence_placeholder_only",
            ],
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
                "feature_count": 1,
            },
        },
    )

    result = _invoke(["release", "check", version, "--project", str(tmp_path)])

    assert result.exit_code == 1, result.stdout
    assert "Browser blockers:" in result.stdout
    assert "protected_surface_session_bridge_missing" in result.stdout
    assert "browser_evidence_placeholder_only" in result.stdout
    assert "Recommended command: beacon qa run" in result.stdout


def test_release_check_json_should_include_browser_blocker_repairs(tmp_path: Path, monkeypatch):
    version = "v1.4.2"
    _seed_release_artifacts(tmp_path, version=version, coverage_version=version)
    monkeypatch.setattr(
        release_command,
        "build_requirement_package_gate",
        lambda *_args, **_kwargs: {"status": "pass", "reason_code": "", "recommended_command": ""},
    )

    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "release_ready": False,
            "qa": {"feature": "feature-a"},
            "semantic": {},
            "browser_release_reason_codes": [
                "protected_surface_runner_priority_unavailable",
            ],
            "change_documents": {
                "markdown_exists": True,
                "json_exists": True,
                "version_match": True,
                "includes_current_feature": True,
                "markdown_path": f"docs/beacon/{version}/change/{version}.md",
                "json_path": f"docs/beacon/{version}/.machine/change/{version}.json",
                "current_feature_slug": "feature-a",
                "feature_count": 1,
            },
        },
    )

    result = _invoke(["release", "check", version, "--project", str(tmp_path), "--json"])

    assert result.exit_code == 1, result.stdout
    payload = json.loads(result.stdout)
    assert payload["browser_release_blockers"][0]["reason_code"] == "protected_surface_runner_priority_unavailable"
    assert "attached-session runner" in payload["browser_release_blockers"][0]["summary"]
    assert payload["recommended_command"].startswith("beacon qa run")


def test_release_scorecard_should_print_browser_blockers(tmp_path: Path, monkeypatch):
    version = "v1.4.2"
    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "version": version,
            "release_ready": False,
            "gate": {"status": "Blocked", "blocked_count": 1},
            "qa": {"status": "blocked", "evidence_done": False, "execution_mode": "feature-aware", "feature": "feature-a"},
            "browser_release_reason_codes": [
                "protected_surface_session_bridge_missing",
                "browser_evidence_placeholder_only",
            ],
            "feature_qa_scorecard": {
                "release_confidence_min": 0.4,
                "review_required_count": 1,
                "needs_replay_count": 0,
                "continue_decision": "stop_for_repair",
                "test_case_backfill_required": False,
            },
            "learning_scorecard": {"decision_summary": {"keep": 0, "review": 1, "discard": 0}},
        },
    )

    result = _invoke(["release", "scorecard", version, "--project", str(tmp_path)])

    assert result.exit_code == 0, result.stdout
    assert "Browser release blockers:" in result.stdout
    assert "protected_surface_session_bridge_missing" in result.stdout
    assert "browser_evidence_placeholder_only" in result.stdout
    assert "Recommended command: beacon qa run" in result.stdout


def test_release_scorecard_json_should_preserve_browser_blocker_codes(tmp_path: Path, monkeypatch):
    version = "v1.4.2"
    monkeypatch.setattr(
        release_command,
        "build_release_scorecard",
        lambda *_args, **_kwargs: {
            "version": version,
            "release_ready": False,
            "gate": {"status": "Blocked", "blocked_count": 1},
            "qa": {"status": "blocked", "evidence_done": False, "execution_mode": "feature-aware", "feature": "feature-a"},
            "browser_release_reason_codes": [
                "browser_runner_learning_missing",
            ],
            "learning_scorecard": {"decision_summary": {"keep": 0, "review": 1, "discard": 0}},
        },
    )

    result = _invoke(["release", "scorecard", version, "--project", str(tmp_path), "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["browser_release_reason_codes"] == ["browser_runner_learning_missing"]
