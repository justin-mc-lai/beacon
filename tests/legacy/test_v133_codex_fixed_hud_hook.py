"""v1.3.3 Codex fixed HUD hook contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str], *, input_text: str = ""):
    return runner.invoke(app, args, input=input_text)


def test_codex_fixed_hud_should_render_for_user_prompt_submit(tmp_path: Path):
    payload = {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "继续推进 v1.3.3 HUD 闭环",
        "session_id": "session-hud-001",
    }

    result = _invoke(
        [
            "debug",
            "codex-fixed-hud",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--feature",
            "beacon-v1.3.3-minimal-hud-scenarios-and-implementation",
        ],
        input_text=json.dumps(payload, ensure_ascii=False),
    )
    assert result.exit_code == 0, result.stdout
    output = json.loads(result.stdout)

    assert output["status"] == "captured"
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    context = output["hookSpecificOutput"]["additionalContext"]
    assert context.startswith("[beacon-hud]\n")
    hud_lines = context.splitlines()[1:]
    assert 1 <= len(hud_lines) <= 3
    assert output["minimal_hud"]["scenario"]

    input_audit_path = tmp_path / output["input_audit_path"]
    assert input_audit_path.exists()
    rows = [line for line in input_audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    latest = json.loads(rows[-1])
    assert latest["source"] == "codex.fixed-hud-hook"
    assert latest["hook_event_name"] == "UserPromptSubmit"


def test_codex_fixed_hud_should_support_session_refresh_event(tmp_path: Path):
    payload = {
        "hook_event_name": "SessionRefresh",
        "session_id": "session-hud-002",
    }

    result = _invoke(
        [
            "debug",
            "codex-fixed-hud",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--feature",
            "beacon-v1.3.3-minimal-hud-scenarios-and-implementation",
        ],
        input_text=json.dumps(payload, ensure_ascii=False),
    )
    assert result.exit_code == 0, result.stdout
    output = json.loads(result.stdout)

    assert output["status"] == "captured"
    assert output["hookSpecificOutput"]["hookEventName"] == "SessionRefresh"
    assert output["hookSpecificOutput"]["additionalContext"].startswith("[beacon-hud]\n")


def test_codex_fixed_hud_should_degrade_on_invalid_payload_json(tmp_path: Path):
    result = _invoke(
        [
            "debug",
            "codex-fixed-hud",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--feature",
            "beacon-v1.3.3-minimal-hud-scenarios-and-implementation",
        ],
        input_text='{"hook_event_name":',
    )
    assert result.exit_code == 0, result.stdout
    output = json.loads(result.stdout)

    assert output["status"] == "degraded"
    assert output["reason"] == "invalid_payload_json"
    assert output["hookSpecificOutput"]["additionalContext"] == ""
    assert output["parse_error"]


def test_codex_fixed_hud_should_ignore_unsupported_events(tmp_path: Path):
    payload = {
        "hook_event_name": "PostToolUse",
        "session_id": "session-hud-003",
    }
    result = _invoke(
        [
            "debug",
            "codex-fixed-hud",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
        ],
        input_text=json.dumps(payload, ensure_ascii=False),
    )
    assert result.exit_code == 0, result.stdout
    output = json.loads(result.stdout)
    assert output["status"] == "ignored"
    assert output["reason"] == "unsupported_hook_event"
    assert output["hookSpecificOutput"]["additionalContext"] == ""
