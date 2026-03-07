"""v1.1.0 workflow forced HUD + double confirmation contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app

runner = CliRunner()


SKIP_ALL_BUT_IMPLEMENTATION = "think,user-story,prd,test-case,verify,gate"


def _invoke(args: list[str], *, input_text: str | None = None):
    return runner.invoke(app, args, input=input_text)


def _extract_run_id(stdout: str) -> str:
    for line in stdout.splitlines():
        if line.startswith("Run ID:"):
            return line.split(":", 1)[1].strip()
    return ""


def test_v110_non_interactive_start_should_require_double_confirmation_flags(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Force Confirm Feature",
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.0",
            "--auto",
            "--no-interactive",
            "--skip",
            SKIP_ALL_BUT_IMPLEMENTATION,
        ]
    )
    assert result.exit_code == 2
    assert "requires HUD + double confirmation" in result.stdout

    run_id = _extract_run_id(result.stdout)
    assert run_id

    state_path = tmp_path / ".beacon" / "runs" / run_id / "state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert payload.get("status") == "paused"
    assert payload.get("reason") == "non_interactive_double_confirmation_required"


def test_v110_non_interactive_start_should_execute_with_double_confirmation_flags(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "Force Confirm Feature",
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.0",
            "--auto",
            "--no-interactive",
            "--skip",
            SKIP_ALL_BUT_IMPLEMENTATION,
            "--confirm-execute",
            "--confirm-execute-second",
        ]
    )
    assert result.exit_code == 0

    run_id = _extract_run_id(result.stdout)
    assert run_id

    marker = tmp_path / ".beacon" / "state" / "implementation-force-confirm-feature.json"
    assert marker.exists()



def test_workflow_hud_should_show_project_debug_mode_state(tmp_path: Path):
    enable = _invoke(
        [
            "debug",
            "enable",
            "--project-root",
            str(tmp_path),
            "--run-id",
            "run-debug-hud-001",
            "--no-sync-history",
        ]
    )
    assert enable.exit_code == 0

    planned = _invoke(
        [
            "workflow",
            "start",
            "HUD Debug Feature",
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.0",
        ]
    )
    assert planned.exit_code == 0
    run_id = _extract_run_id(planned.stdout)
    assert run_id

    hud = _invoke(
        [
            "workflow",
            "hud",
            "--project",
            str(tmp_path),
            "--run-id",
            run_id,
            "--json",
        ]
    )
    assert hud.exit_code == 0
    payload = json.loads(hud.stdout)
    debug_block = payload.get("debug", {})
    assert debug_block.get("enabled") is True
    assert debug_block.get("run_id") == "run-debug-hud-001"



def test_debug_mode_should_capture_workflow_interactive_prompt_operations(tmp_path: Path):
    enable = _invoke(
        [
            "debug",
            "enable",
            "--project-root",
            str(tmp_path),
            "--run-id",
            "run-debug-ops-001",
            "--no-sync-history",
        ]
    )
    assert enable.exit_code == 0

    result = _invoke(
        [
            "workflow",
            "start",
            "Debug Prompt Ops",
            "--project",
            str(tmp_path),
            "--version",
            "v1.1.0",
            "--auto",
            "--interactive",
            "--skip",
            SKIP_ALL_BUT_IMPLEMENTATION,
        ],
        input_text="1\ny\nEXECUTE\n",
    )
    assert result.exit_code == 0

    run_id = _extract_run_id(result.stdout)
    assert run_id

    debug_file = tmp_path / ".beacon" / "state" / "debug-feedback" / f"{run_id}.jsonl"
    assert debug_file.exists()
    rows = [
        json.loads(line)
        for line in debug_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(str(row.get("source", "")) == "workflow.interactive.prompt-op" for row in rows)
    assert any("action=second-confirm" in str(row.get("note", "")) for row in rows)
