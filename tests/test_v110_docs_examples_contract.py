"""v1.1.0 docs examples smoke contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_docs_examples_should_be_executable(tmp_path: Path):
    readme = Path(__file__).resolve().parents[1] / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert "beacon workflow start" in text
    assert "prompt optimize" in text

    catalog = _invoke([
        "prompt",
        "catalog",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--json",
    ])
    assert catalog.exit_code == 0
    payload = json.loads(catalog.stdout)
    assert isinstance(payload.get("routable_intents"), list)

    ask = _invoke([
        "ask",
        "请生成用户故事并给出验收标准",
        "--project-root",
        str(tmp_path),
        "--json",
    ])
    assert ask.exit_code == 0
    ask_payload = json.loads(ask.stdout)
    assert str(ask_payload.get("recommended_command", "")).strip()
