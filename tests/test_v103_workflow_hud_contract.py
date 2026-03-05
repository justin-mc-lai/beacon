"""v1.0.3 workflow HUD interaction contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERIFY_PASS_ARGS = [
    "--implementation-command",
    "python3 -c \"print('impl')\"",
    "--verify-scope",
    "unit",
    "--verify-unit-command",
    "python3 -c \"print('ok')\"",
]


def _invoke(args: list[str], *, input_text: str | None = None):
    return runner.invoke(app, args, input=input_text)


def _latest_run_id(project_root: Path) -> str:
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs
    return runs[-1]


def test_start_interactive_should_render_hud_before_prompt(tmp_path: Path):
    result = _invoke(
        ["workflow", "start", "HUD Start Contract", "--auto", "--interactive", "--project", str(tmp_path), *VERIFY_PASS_ARGS],
        input_text="5\n",
    )
    assert result.exit_code == 0
    hud_idx = result.stdout.find("WORKFLOW HUD")
    prompt_idx = result.stdout.find("Select action [1-6]:")
    assert hud_idx >= 0
    assert prompt_idx >= 0
    assert hud_idx < prompt_idx


def test_continue_interactive_should_render_hud_before_prompt(tmp_path: Path):
    planned = _invoke(["workflow", "start", "HUD Continue Contract", "--project", str(tmp_path)])
    assert planned.exit_code == 0
    run_id = _latest_run_id(tmp_path)

    continued = _invoke(
        ["workflow", "continue", "--run-id", run_id, "--project", str(tmp_path), "--interactive"],
        input_text="5\n",
    )
    assert continued.exit_code == 0
    hud_idx = continued.stdout.find("WORKFLOW HUD")
    prompt_idx = continued.stdout.find("Select action [1-6]:")
    assert hud_idx >= 0
    assert prompt_idx >= 0
    assert hud_idx < prompt_idx


def test_feedback_apply_action_should_record_event_and_return_hud(tmp_path: Path):
    result = _invoke(
        ["workflow", "start", "HUD Feedback Contract", "--auto", "--interactive", "--project", str(tmp_path), *VERIFY_PASS_ARGS],
        input_text="4\ny\n5\n",
    )
    assert result.exit_code == 0
    run_id = _latest_run_id(tmp_path)

    # feedback apply returns to HUD loop (at least two HUD renders in output)
    assert result.stdout.count("WORKFLOW HUD") >= 2

    lifecycle_path = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    payload = json.loads(lifecycle_path.read_text(encoding="utf-8"))
    events = [
        item
        for item in payload.get("items", [])
        if item.get("run_id") == run_id and item.get("event") == "feedback_apply_triggered"
    ]
    assert events


def test_interactive_decision_should_write_memory_entry(tmp_path: Path):
    result = _invoke(
        ["workflow", "start", "HUD Memory Contract", "--auto", "--interactive", "--project", str(tmp_path), *VERIFY_PASS_ARGS],
        input_text="1\nn\n5\n",
    )
    assert result.exit_code == 0
    run_id = _latest_run_id(tmp_path)

    memory_v1 = tmp_path / ".beacon" / "memory" / "memory-v1.json"
    payload = json.loads(memory_v1.read_text(encoding="utf-8"))
    rows = [
        item
        for item in payload.get("items", [])
        if item.get("type") == "decision"
        and item.get("source") == "workflow.interactive"
        and item.get("source_session_id") == run_id
    ]
    assert rows


def test_no_interactive_should_not_prompt_next_step_menu(tmp_path: Path):
    result = _invoke(
        [
            "workflow",
            "start",
            "HUD No Interactive Contract",
            "--auto",
            "--no-interactive",
            "--project",
            str(tmp_path),
            *VERIFY_PASS_ARGS,
        ]
    )
    assert result.exit_code == 0
    assert "Select action [1-6]:" not in result.stdout
