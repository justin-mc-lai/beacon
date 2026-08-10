"""v1.1.2 prototype intent routing contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_prompt_optimize_should_route_prototype_intent(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "请帮我生成交互原型并快速预览",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "prototype"
    assert payload.get("recommended_args", [])[:2] == ["prototype", "create"]

