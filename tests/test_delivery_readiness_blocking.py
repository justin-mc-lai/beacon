from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_verify_delivery_should_pass_for_current_v111_execution_artifacts():
    root = Path("/Users/apple/Developer/Personal/my_skill/beacon")
    result = _invoke(["doctor", "verify-delivery", "--project-root", str(root), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "FAIL"
    checks = payload.get("result", {}).get("checks", [])
    git_check = next(item for item in checks if item.get("name") == "execution_git_alignment_schema")
    assert git_check["status"] == "fail"
