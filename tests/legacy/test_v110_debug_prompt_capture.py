"""v1.1.0 debug prompt capture contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.memory import load_memory_entries

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_debug_enable_should_capture_ask_prompt_into_debug_feedback_and_memory(tmp_path: Path):
    enable = _invoke(
        [
            "debug",
            "enable",
            "--project-root",
            str(tmp_path),
            "--run-id",
            "run-debug-001",
            "--no-sync-history",
            "--json",
        ]
    )
    assert enable.exit_code == 0

    result = _invoke(["ask", "做一次环境诊断并输出结果", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    debug_feedback = payload.get("debug_feedback", {})
    assert debug_feedback.get("enabled") is True

    debug_path = tmp_path / debug_feedback.get("path", "")
    assert debug_path.exists()
    lines = [line for line in debug_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines
    event = json.loads(lines[-1])
    assert event.get("goal") == "做一次环境诊断并输出结果"
    assert event.get("intent") == "doctor"

    input_audit = payload.get("input_audit", {})
    audit_path = tmp_path / input_audit.get("path", "")
    assert audit_path.exists()
    audit_lines = [line for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    audit_payload = json.loads(audit_lines[-1])
    assert audit_payload.get("source") == "ask"
    assert audit_payload.get("input_goal") == "做一次环境诊断并输出结果"
    assert audit_payload.get("intent") == "doctor"

    entries = load_memory_entries(tmp_path)
    assert any(str(item.get("source", "")) == "debug.prompt.optimize" for item in entries)


def test_debug_input_audit_should_read_recent_user_input_events(tmp_path: Path):
    ask_result = _invoke(["ask", "做一次环境诊断并输出结果", "--project-root", str(tmp_path), "--json"])
    assert ask_result.exit_code == 0, ask_result.stdout

    result = _invoke(
        [
            "debug",
            "input-audit",
            "--project-root",
            str(tmp_path),
            "--limit",
            "5",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload.get("count") == 1
    assert payload.get("events", [{}])[-1].get("source") == "ask"


def test_debug_sync_prompts_should_import_router_history_into_memory(tmp_path: Path):
    history_path = tmp_path / ".beacon" / "memory" / "prompt-router-history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": "2026-03-07T00:00:00Z",
                        "input_goal": "请生成用户故事",
                        "intent": "user-story",
                        "confidence": 0.86,
                        "boundary_state": "in_scope",
                        "recommended_command": "beacon user-story create ...",
                        "execute_requested": False,
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "ts": "2026-03-07T00:00:01Z",
                        "input_goal": "请检查 gate",
                        "intent": "gate",
                        "confidence": 0.75,
                        "boundary_state": "in_scope",
                        "recommended_command": "beacon gate check release ...",
                        "execute_requested": False,
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = _invoke(
        [
            "debug",
            "sync-prompts",
            "--project-root",
            str(tmp_path),
            "--run-id",
            "run-debug-sync-001",
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("imported") == 2

    debug_file = tmp_path / ".beacon" / "state" / "debug-feedback" / "run-debug-sync-001.jsonl"
    assert debug_file.exists()
    lines = [line for line in debug_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 2

    entries = load_memory_entries(tmp_path)
    assert any(str(item.get("source", "")) == "debug.sync.prompt-history" for item in entries)


def test_debug_confidence_set_should_affect_prompt_execution_policy(tmp_path: Path):
    set_result = _invoke(
        [
            "debug",
            "confidence",
            "set",
            "0.77",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert set_result.exit_code == 0
    payload = json.loads(set_result.stdout)
    assert payload.get("confidence_threshold") == 0.77

    route = _invoke(
        [
            "prompt",
            "optimize",
            "做一次环境诊断",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert route.exit_code == 0
    plan = json.loads(route.stdout)
    assert float(plan.get("execution_policy", {}).get("min_confidence", 0.0)) == 0.77


def test_run_workflow_debug_mode_should_enable_debug_state(tmp_path: Path):
    result = _invoke(
        [
            "run",
            "workflow",
            "--mode",
            "debug",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    run_id = str(payload.get("run_id", "") or "")
    assert run_id.startswith("run-")

    state_path = tmp_path / ".beacon" / "state" / "debug-mode.json"
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state.get("enabled") is True
    assert state.get("run_id") == run_id
