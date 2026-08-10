from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def test_prd_json_includes_skill_decision_surface(tmp_path: Path):
    result = runner.invoke(
        app,
        ["prd", "create", "sample feature", "--project-root", str(tmp_path), "--version", "v1.4.0", "--mode", "rule", "--json"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["decision_surface"]["stage"] == "prd"
    assert payload["guardrail_contract"]["decision_owner"] == "skill_surface"
    assert payload["guardrail_contract"]["enforcement_owner"] == "python_guardrail"
    assert payload["guardrail_contract"]["fail_closed"] is True


def test_implement_blocked_payload_keeps_fail_closed_and_surface(tmp_path: Path):
    result = runner.invoke(
        app,
        ["implement", "run", "sample feature", "--project", str(tmp_path), "--version", "v1.4.0", "--json"],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["decision_surface"]["stage"] == "implement"
    assert payload["guardrail_contract"]["fail_closed"] is True
    assert payload["guardrail_contract"]["blocked"] is True


def test_qa_blocked_payload_keeps_fail_closed_and_surface(tmp_path: Path):
    result = runner.invoke(
        app,
        ["qa", "run", "sample feature", "--project", str(tmp_path), "--version", "v1.4.0", "--json"],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["decision_surface"]["stage"] == "qa"
    assert payload["guardrail_contract"]["fail_closed"] is True
    assert payload["recommended_command"]


def test_release_blocked_payload_keeps_fail_closed_and_surface(tmp_path: Path):
    result = runner.invoke(
        app,
        ["release", "check", "v1.4.0", "--project", str(tmp_path), "--json"],
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["decision_surface"]["stage"] == "release"
    assert payload["guardrail_contract"]["fail_closed"] is True
