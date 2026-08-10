from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
FEATURE = "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution"
runner = CliRunner()


def test_route_reason_is_visible(tmp_path: Path):
    result = runner.invoke(app, ["ask", "做一次环境诊断", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    explanation = payload.get("route_explanation", {})
    assert explanation.get("primary_reason")
    assert explanation.get("summary")
    assert explanation.get("recommended_route")


def test_learning_hint_usage_is_visible(tmp_path: Path):
    result = runner.invoke(app, ["ask", "做一次环境诊断", "--project-root", str(tmp_path), "--json"])
    payload = json.loads(result.stdout)
    explanation = payload.get("route_explanation", {})
    disclosure = payload.get("learning_disclosure", {})
    assert explanation.get("learning_hint_used") is True
    assert disclosure.get("used") is True


def test_brainstorm_vs_change_reasoning_is_clear(tmp_path: Path):
    result = runner.invoke(
        app,
        ["ask", "冻结后要改需求范围，先帮我判断是否要 change", "--project-root", str(tmp_path), "--json"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    explanation = payload.get("route_explanation", {})
    assert "read-only convergence" in explanation.get("brainstorm_when", "")
    assert "frozen truth" in explanation.get("change_when", "")
    assert explanation.get("recommended_route") == "beacon-change"


def test_action_reason_precedes_command_dump():
    result = runner.invoke(
        app,
        ["help", "--project-root", str(ROOT), "--version", "v1.4.0", "--feature", FEATURE],
    )
    assert result.exit_code == 0
    text = result.stdout
    assert "- why" in text
    assert "- command" in text
    assert text.index("- why") < text.index("- command")
