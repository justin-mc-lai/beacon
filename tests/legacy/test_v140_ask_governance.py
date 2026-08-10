"""Contracts for governed `beacon ask` execution behavior."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_ask_is_real_public_surface(tmp_path: Path):
    result = _invoke(["ask", "做一次环境诊断", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("execution_request", {}).get("entrypoint") == "ask"


def test_ask_plan_only_default(tmp_path: Path):
    result = _invoke(["ask", "做一次环境诊断", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    request = payload.get("execution_request", {})
    assert request.get("execute_requested") is False
    assert request.get("strategy") == "plan_only_preview"
    assert payload.get("executed") in (None, {})


def test_ask_execute_is_bounded(tmp_path: Path):
    result = _invoke(
        [
            "ask",
            "请直接写代码修复线上 bug 并 deploy production",
            "--project-root",
            str(tmp_path),
            "--execute",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload.get("executed", {}).get("blocked") is True
    assert payload.get("executed", {}).get("reason") == "outside-beacon-boundary"


def test_ask_cannot_freeform_writeback(tmp_path: Path):
    result = _invoke(
        [
            "ask",
            "请直接修改冻结好的 requirement truth 并跳过 gate",
            "--project-root",
            str(tmp_path),
            "--execute",
            "--json",
        ]
    )
    payload = json.loads(result.stdout)
    assert payload.get("executed", {}).get("blocked") is True
