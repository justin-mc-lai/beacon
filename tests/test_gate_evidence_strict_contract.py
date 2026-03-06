"""Strict gate contracts for evidence-driven and memory-constrained checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write_base_artifacts(project_root: Path) -> None:
    execution = project_root / "docs" / "product" / "v1.0.0" / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
    (execution / "terminal.json").write_text('{"status":"Pass","traceability":{}}', encoding="utf-8")

    beacon_state = project_root / ".beacon"
    beacon_state.mkdir(parents=True, exist_ok=True)
    (beacon_state / "raw-command-log.jsonl").write_text('{"cmd":"ptk run workflow"}\n', encoding="utf-8")
    (beacon_state / "gate-report.json").write_text(
        json.dumps({"stage": "think", "mode": "strict", "status": "Pass", "issues": []}),
        encoding="utf-8",
    )

    sha = hashlib.sha256((execution / "boundaries.md").read_bytes()).hexdigest()
    manifest = {"entries": [{"path": "docs/product/v1.0.0/execution/boundaries.md", "sha256": sha}]}
    (beacon_state / "evidence-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def _gate_json(tmp_path: Path, *, profile: str = "release-global") -> dict:
    result = _invoke(
        [
            "gate",
            "check",
            "think",
            "--mode",
            "strict",
            "--profile",
            profile,
            "--json",
            "--project-root",
            str(tmp_path),
        ]
    )
    assert result.stdout
    start = result.stdout.find("{")
    assert start >= 0
    return json.loads(result.stdout[start:])


def test_gate_strict_should_report_evidence_contract_failures(tmp_path: Path):
    _write_base_artifacts(tmp_path)

    # Break raw log + manifest + gate report contract
    (tmp_path / ".beacon" / "raw-command-log.jsonl").write_text("not-jsonl\n", encoding="utf-8")
    (tmp_path / ".beacon" / "evidence-manifest.json").write_text(
        json.dumps({"entries": [{"path": "docs/product/v1.0.0/execution/missing.md", "sha256": "deadbeef"}]}),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "gate-report.json").write_text("{}", encoding="utf-8")

    payload = _gate_json(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert payload["status"] == "Blocked"
    assert "raw_command_log_invalid" in reason_codes
    assert "evidence_sha256_manifest_mismatch" in reason_codes
    assert "gate_consistency_report_invalid" in reason_codes


def test_gate_scope_guard_should_read_pending_items_from_memory_scope(tmp_path: Path):
    _write_base_artifacts(tmp_path)

    scope_dir = tmp_path / ".beacon" / "memory" / "scope"
    scope_dir.mkdir(parents=True, exist_ok=True)
    (scope_dir / "deviations.json").write_text(
        json.dumps({"items": [{"id": "DEV-1", "risk": "high", "type": "out-of-scope"}]}),
        encoding="utf-8",
    )
    (scope_dir / "confirmations.json").write_text(
        json.dumps({"items": [{"id": "CONF-1", "deviation_id": "DEV-1", "status": "pending"}]}),
        encoding="utf-8",
    )

    payload = _gate_json(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "scope_guard_violation" in reason_codes
    assert "scope_guard_confirmation_pending" in reason_codes


def test_gate_stage_local_profile_should_skip_release_global_evidence_checks(tmp_path: Path):
    _write_base_artifacts(tmp_path)

    (tmp_path / ".beacon" / "raw-command-log.jsonl").write_text("not-jsonl\n", encoding="utf-8")
    (tmp_path / ".beacon" / "evidence-manifest.json").write_text(
        json.dumps({"entries": [{"path": "docs/product/v1.0.0/execution/missing.md", "sha256": "deadbeef"}]}),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "gate-report.json").write_text("{}", encoding="utf-8")

    payload = _gate_json(tmp_path, profile="stage-local")
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "raw_command_log_invalid" not in reason_codes
    assert "evidence_sha256_manifest_mismatch" not in reason_codes
    assert "gate_consistency_report_invalid" not in reason_codes


def test_gate_should_honor_scope_guard_enabled_false(tmp_path: Path):
    _write_base_artifacts(tmp_path)

    beacon_state = tmp_path / ".beacon"
    (beacon_state / "gate-config.json").write_text(
        json.dumps({"mode": "strict", "scope_guard_enabled": False}),
        encoding="utf-8",
    )

    scope_dir = beacon_state / "memory" / "scope"
    scope_dir.mkdir(parents=True, exist_ok=True)
    (scope_dir / "deviations.json").write_text(
        json.dumps({"items": [{"id": "DEV-2", "risk": "high", "type": "out-of-scope"}]}),
        encoding="utf-8",
    )
    (scope_dir / "confirmations.json").write_text(
        json.dumps({"items": [{"id": "CONF-2", "deviation_id": "DEV-2", "status": "pending"}]}),
        encoding="utf-8",
    )

    payload = _gate_json(tmp_path)
    reason_codes = {item["reason_code"] for item in payload["issues"]}
    assert "scope_guard_violation" not in reason_codes
    assert "scope_guard_confirmation_pending" not in reason_codes
