"""Compatibility tests for gate/evidence behavior."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_gate_check_json_contract_has_required_fields(tmp_path: Path):
    result = _invoke(["gate", "check", "think", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code in (0, 2)
    # Output contains log lines + JSON; parse from first "{"
    start = result.stdout.find("{")
    assert start >= 0
    payload = json.loads(result.stdout[start:])
    for key in ("stage", "mode", "status", "issues", "blocked_count"):
        assert key in payload


def test_gate_force_writes_risk_log(tmp_path: Path):
    result = _invoke(["gate", "check", "think", "--mode", "strict", "--force", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    risk_path = tmp_path / ".beacon" / "risks.json"
    assert risk_path.exists()
    risks = json.loads(risk_path.read_text(encoding="utf-8"))
    assert isinstance(risks, list) and len(risks) >= 1


def test_gate_flat_stage_syntax_should_work(tmp_path: Path):
    result = _invoke(["gate", "think", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code in (0, 2)
    assert "No such command" not in result.stdout


def test_gate_root_should_run_all_stages(tmp_path: Path):
    result = _invoke(["gate", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code in (0, 2)
    payload = json.loads(result.stdout)
    assert payload.get("stage_count") == 5
    assert len(payload.get("results", [])) == 5


def test_gate_normal_mode_should_emit_warn_when_non_blocking_issues_exist(tmp_path: Path):
    result = _invoke(["gate", "check", "think", "--mode", "normal", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    start = result.stdout.find("{")
    payload = json.loads(result.stdout[start:])
    assert payload["status"] == "Warn"
    assert len(payload.get("issues", [])) >= 1


def test_gate_auto_profile_should_default_to_stage_local_for_non_release_stage(tmp_path: Path):
    beacon_state = tmp_path / ".beacon"
    beacon_state.mkdir(parents=True, exist_ok=True)
    (beacon_state / "raw-command-log.jsonl").write_text("not-jsonl\n", encoding="utf-8")
    (beacon_state / "evidence-manifest.json").write_text('{"entries":[]}', encoding="utf-8")
    (beacon_state / "gate-report.json").write_text("{}", encoding="utf-8")

    result = _invoke(["gate", "check", "think", "--mode", "strict", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code in (0, 2)
    start = result.stdout.find("{")
    payload = json.loads(result.stdout[start:])
    reason_codes = {item["reason_code"] for item in payload.get("issues", [])}
    assert payload.get("profile") == "stage-local"
    assert "raw_command_log_invalid" not in reason_codes


def test_gate_should_honor_docs_product_execution_path(tmp_path: Path):
    version = "v1.0.0"
    execution = tmp_path / "docs" / "product" / version / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / "boundaries.md").write_text("# ok\n", encoding="utf-8")
    (execution / "terminal.json").write_text('{"status":"Pass","traceability":{}}', encoding="utf-8")
    beacon_state = tmp_path / ".beacon"
    beacon_state.mkdir(parents=True, exist_ok=True)
    (beacon_state / "raw-command-log.jsonl").write_text("", encoding="utf-8")
    (beacon_state / "evidence-manifest.json").write_text('{"entries":[]}', encoding="utf-8")
    (beacon_state / "gate-report.json").write_text("{}", encoding="utf-8")

    result = _invoke(["gate", "check", "think", "--mode", "strict", "--json", "--project-root", str(tmp_path)])
    start = result.stdout.find("{")
    payload = json.loads(result.stdout[start:])
    reason_codes = {i["reason_code"] for i in payload["issues"]}
    assert "boundaries_missing" not in reason_codes
    assert "terminal_artifact_missing" not in reason_codes


def test_reason_code_catalog_contains_core_expected_items():
    result = _invoke(["gate", "list"])
    assert result.exit_code == 0
    for code in ("blocking_open_question_exists", "boundaries_missing", "terminal_artifact_missing"):
        assert code in result.stdout
