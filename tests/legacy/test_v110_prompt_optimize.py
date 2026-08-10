"""v1.1.0 prompt optimize contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_prompt_optimize_should_output_boundary_safe_command_pack(tmp_path: Path):
    result = _invoke([
        "prompt",
        "optimize",
        "请先检查 gate 并直接写代码上线",
        "--project-root",
        str(tmp_path),
        "--json",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    pack = payload.get("boundary_safe_command_pack", {})
    assert isinstance(pack, dict)
    assert pack.get("boundary_state") == "mixed_need_confirm"
    fallback_commands = pack.get("fallback_commands", [])
    assert isinstance(fallback_commands, list)
    assert any("--plan-only" in cmd for cmd in fallback_commands)
