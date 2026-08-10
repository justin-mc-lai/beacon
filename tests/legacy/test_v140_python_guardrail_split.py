from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "docs" / "beacon" / "v1.4.0" / "prd" / "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md"
runner = CliRunner()


def test_python_four_duties_only():
    text = PRD.read_text(encoding="utf-8")
    assert "1. 事实采集" in text
    assert "2. schema 校验" in text
    assert "3. contract / projection 写入" in text
    assert "4. gate 阻断与 verdict 写入" in text


def test_explanation_moves_to_skill_surface():
    text = PRD.read_text(encoding="utf-8")
    assert "每个核心 skill 的主要判断协议应优先写在 skill surface 中" in text
    assert "而不是只藏在 Python fallback 内" in text


def test_python_remains_fail_closed_guardrail(tmp_path: Path):
    result = runner.invoke(
        app,
        ["ask", "请直接写代码修复线上 bug 并 deploy production", "--project-root", str(tmp_path), "--execute", "--json"],
    )
    payload = json.loads(result.stdout)
    assert payload.get("executed", {}).get("blocked") is True
    assert payload.get("executed", {}).get("reason") == "outside-beacon-boundary"


def test_not_a_language_migration_project():
    text = PRD.read_text(encoding="utf-8")
    assert "当前要减的不是 Python 语言本身" in text
