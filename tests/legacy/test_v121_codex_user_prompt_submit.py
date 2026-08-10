"""v1.2.1 Codex UserPromptSubmit debug guidance contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str], *, input_text: str = ""):
    return runner.invoke(app, args, input=input_text)


def test_codex_user_prompt_submit_should_capture_history_feedback_and_snapshot(tmp_path: Path):
    payload = {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "请帮我梳理登录能力，进入 Beacon 的用户故事和测试用例主链",
        "session_id": "session-001",
        "thread_id": "thread-001",
        "turn_id": "turn-001",
        "transcript_path": "/tmp/transcript.jsonl",
    }

    result = _invoke(
        [
            "debug",
            "codex-user-prompt-submit",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.2.1",
        ],
        input_text=json.dumps(payload, ensure_ascii=False),
    )
    assert result.exit_code == 0, result.stdout
    output = json.loads(result.stdout)

    assert output["status"] == "captured"
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "Recommended Beacon command:" in output["hookSpecificOutput"]["additionalContext"]
    assert "Suggested normalized prompt:" in output["hookSpecificOutput"]["additionalContext"]
    assert output["plan"]["intent"] in {"workflow", "user-story", "test-case"}
    assert output["prompt_adaptation"]["normalized_prompt"]
    assert output["prompt_adaptation"]["needs_clarification"] is True
    assert "target_version" in output["prompt_adaptation"]["missing_fields"]

    history_path = tmp_path / output["history_path"]
    assert history_path.exists()
    history_lines = [line for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    history_payload = json.loads(history_lines[-1])
    assert history_payload["source"] == "codex.user-prompt-submit"
    assert history_payload["normalized_prompt"] == output["prompt_adaptation"]["normalized_prompt"]

    input_audit_path = tmp_path / output["input_audit_path"]
    assert input_audit_path.exists()
    input_audit_lines = [line for line in input_audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    input_audit_payload = json.loads(input_audit_lines[-1])
    assert input_audit_payload["source"] == "codex.user-prompt-submit"
    assert input_audit_payload["hook_event_name"] == "UserPromptSubmit"
    assert input_audit_payload["session_id"] == payload["session_id"]
    assert input_audit_payload["normalized_prompt"] == output["prompt_adaptation"]["normalized_prompt"]

    feedback_path = tmp_path / output["debug_feedback"]["path"]
    assert feedback_path.exists()
    feedback_lines = [line for line in feedback_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    feedback_payload = json.loads(feedback_lines[-1])
    assert feedback_payload["source"] == "debug.codex.user-prompt-submit"
    assert feedback_payload["extra"]["raw_prompt"] == payload["prompt"]
    assert feedback_payload["extra"]["normalized_prompt"] == output["prompt_adaptation"]["normalized_prompt"]

    snapshot_path = tmp_path / output["snapshot_path"]
    assert snapshot_path.exists()
    snapshot_lines = [line for line in snapshot_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    snapshot_payload = json.loads(snapshot_lines[-1])
    assert snapshot_payload["hook_event_name"] == "UserPromptSubmit"
    assert snapshot_payload["prompt"] == payload["prompt"]
    assert snapshot_payload["adaptation"]["normalized_prompt"] == output["prompt_adaptation"]["normalized_prompt"]


def test_codex_user_prompt_submit_should_flag_mixed_boundary_with_split_guidance(tmp_path: Path):
    payload = {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "请先检查 gate 再直接写代码修复线上 bug 并发版",
    }

    result = _invoke(
        [
            "debug",
            "codex-user-prompt-submit",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.2.1",
        ],
        input_text=json.dumps(payload, ensure_ascii=False),
    )
    assert result.exit_code == 0, result.stdout
    output = json.loads(result.stdout)

    assert output["plan"]["boundary"]["state"] == "mixed_need_confirm"
    assert output["prompt_adaptation"]["boundary_state"] == "mixed_need_confirm"
    assert "boundary_split" in output["prompt_adaptation"]["missing_fields"]
    assert "拆成两条输入" in output["hookSpecificOutput"]["additionalContext"]


def test_codex_user_prompt_submit_should_ignore_other_hook_events(tmp_path: Path):
    payload = {
        "hook_event_name": "PostToolUse",
        "prompt": "请检查状态",
    }

    result = _invoke(
        [
            "debug",
            "codex-user-prompt-submit",
            "--project-root",
            str(tmp_path),
        ],
        input_text=json.dumps(payload, ensure_ascii=False),
    )
    assert result.exit_code == 0, result.stdout
    output = json.loads(result.stdout)
    assert output["status"] == "ignored"
    assert output["reason"] == "unsupported_hook_event"
