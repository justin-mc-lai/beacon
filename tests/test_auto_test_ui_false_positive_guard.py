"""PTK-aligned UI false-positive guard tests for beacon auto-test."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.auto_test import evaluate_ui_false_positive_guard
from beacon.main import app


runner = CliRunner()


def test_ui_success_expectation_should_fail_when_origin_mismatch():
    result = evaluate_ui_false_positive_guard(
        expectation="success",
        target_url="http://127.0.0.1:8952/admin/dashboard",
        origin_url="http://127.0.0.1:8952/admin/login",
        snapshot_text="",
        strict_ui_assertion=False,
        assertion_count=1,
    )

    assert result["status"] == "failed"
    assert result["reason_code"] == "ui_expectation_success_mismatch"
    assert result["origin_vs_target"] == "mismatch"


def test_ui_error_expectation_should_pass_on_redirect_to_login():
    result = evaluate_ui_false_positive_guard(
        expectation="error",
        target_url="/admin/dashboard",
        origin_url="/admin/login",
        snapshot_text="",
        strict_ui_assertion=False,
        assertion_count=1,
    )

    assert result["status"] == "passed"
    assert result["reason_code"] == "ui_expectation_error_redirect"
    assert result["origin_vs_target"] == "mismatch"


def test_ui_strict_should_block_without_assertion():
    result = evaluate_ui_false_positive_guard(
        expectation="success",
        target_url="/admin/dashboard",
        origin_url="/admin/dashboard",
        snapshot_text="dashboard ok",
        strict_ui_assertion=True,
        assertion_count=0,
    )

    assert result["status"] == "blocked"
    assert result["reason_code"] == "ui_assertion_missing_strict"


def test_ui_success_should_block_when_origin_unknown():
    result = evaluate_ui_false_positive_guard(
        expectation="success",
        target_url="/admin/dashboard",
        origin_url="",
        snapshot_text="",
        strict_ui_assertion=False,
        assertion_count=1,
    )

    assert result["status"] == "blocked"
    assert result["reason_code"] == "ui_origin_target_unknown"


def test_auto_test_create_persists_ui_guard_status(tmp_path: Path):
    cmd = [
        "auto-test",
        "create",
        "ui",
        "--project",
        str(tmp_path),
        "--expectation",
        "success",
        "--target-url",
        "/admin/dashboard",
        "--origin-url",
        "/admin/login",
        "--ui-assertion",
        "url_contains:/admin/dashboard",
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0

    status_file = tmp_path / ".beacon" / "auto-test-status.json"
    payload = json.loads(status_file.read_text(encoding="utf-8"))
    assert payload["status"] == "failed"
    assert payload["ui_guard"]["reason_code"] == "ui_expectation_success_mismatch"


def test_ui_unknown_without_real_command_should_block_by_default(tmp_path: Path):
    cmd = [
        "auto-test",
        "create",
        "ui",
        "--project",
        str(tmp_path),
    ]
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0

    status_file = tmp_path / ".beacon" / "auto-test-status.json"
    payload = json.loads(status_file.read_text(encoding="utf-8"))
    assert payload["status"] == "blocked"
    assert payload["ui_guard"]["reason_code"] == "ui_real_execution_required"


def test_ui_unknown_without_real_command_can_pass_in_debug_mode(tmp_path: Path):
    cmd = [
        "auto-test",
        "create",
        "ui",
        "--project",
        str(tmp_path),
    ]
    result = runner.invoke(app, cmd, env={"BEACON_DEBUG": "1"})
    assert result.exit_code == 0

    status_file = tmp_path / ".beacon" / "auto-test-status.json"
    payload = json.loads(status_file.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["ui_guard"]["reason_code"] == "ui_expectation_unknown_skipped"
