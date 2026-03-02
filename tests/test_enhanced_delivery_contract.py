"""Contract tests for enhanced auto-test / test-case / gate behaviors."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_test_execution_integrity
from beacon.main import app

runner = CliRunner()


def test_auto_test_executes_layer_and_writes_evidence(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "unit",
            "--project",
            str(tmp_path),
            "--unit-command",
            "python3 -c \"print('ok')\"",
        ],
    )
    assert result.exit_code == 0

    status_file = tmp_path / ".beacon" / "auto-test-status.json"
    payload = json.loads(status_file.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["selected_layers"] == ["unit"]
    layers = payload["execution"]["layers"]
    assert len(layers) == 1
    assert layers[0]["layer"] == "unit"
    assert layers[0]["status"] == "passed"


def test_auto_test_ui_key_actions_guard(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "auto-test",
            "create",
            "ui",
            "--project",
            str(tmp_path),
            "--expectation",
            "success",
            "--target-url",
            "/dashboard",
            "--origin-url",
            "/dashboard",
            "--require-ui-actions",
            "--required-ui-action",
            "login",
            "--required-ui-action",
            "submit-form",
            "--ui-action-evidence",
            "login=.beacon/evidence/login.json",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads((tmp_path / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    assert payload["status"] == "failed"
    assert payload["key_action_guard"]["missing_actions"] == ["submit-form"]


def test_test_case_create_generates_ac_matrix(tmp_path: Path):
    feature = "Login Feature"
    slug = "login-feature"

    us_dir = tmp_path / "docs" / "product" / "latest" / "user-story"
    prd_dir = tmp_path / "docs" / "product" / "latest" / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / f"{slug}.md").write_text(
        "| ID | 标准 |\n|----|------|\n| AC-001 | 登录成功 |\n| AC-002 | 注册成功 |\n",
        encoding="utf-8",
    )
    (prd_dir / f"{slug}.md").write_text(
        "| ID | 标准 |\n|----|------|\n| AC-003 | 接口返回 200 |\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["test-case", "create", feature, "--project", str(tmp_path)])
    assert result.exit_code == 0

    matrix_path = tmp_path / "docs" / "product" / "latest" / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json"
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    assert isinstance(payload.get("entries"), list)
    assert len(payload["entries"]) >= 3
    assert {"ac_id", "tc_id", "layer", "command", "assertion", "evidence_path"}.issubset(
        set(payload["entries"][0].keys())
    )


def test_gate_reports_new_reason_when_test_execution_missing(tmp_path: Path):
    issues = check_test_execution_integrity(tmp_path, GateMode.STRICT, "test-case")
    codes = [x.get("reason_code") for x in issues]
    assert "test_execution_missing" in codes
