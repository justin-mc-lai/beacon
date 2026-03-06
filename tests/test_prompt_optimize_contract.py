"""Contracts for prompt optimize and intent routing behavior."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_prompt_optimize_should_route_requirement_text_to_in_scope_command(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "请帮我做登录需求澄清，并进入规范化产物流程",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") in {"think", "prd", "test-case"}
    assert payload.get("boundary", {}).get("in_scope") is True
    assert str(payload.get("recommended_command", "")).startswith("beacon ")


def test_prompt_optimize_should_route_user_story_intent(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "请生成用户故事并整理验收标准",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "user-story"
    args = payload.get("recommended_args", [])
    assert args[:2] == ["user-story", "create"]


def test_prompt_optimize_should_block_outside_boundary_execute(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "请直接写代码修复线上 bug 并 deploy production",
            "--project-root",
            str(tmp_path),
            "--execute",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "outside-boundary"
    assert payload.get("executed", {}).get("blocked") is True


def test_prompt_optimize_should_mark_mixed_boundary_state(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "请先检查 gate 状态并直接写代码修复线上 bug",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("boundary", {}).get("state") == "mixed_need_confirm"


def test_prompt_optimize_execute_should_block_low_confidence_by_threshold(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "做一次环境诊断",
            "--project-root",
            str(tmp_path),
            "--execute",
            "--min-confidence",
            "1.0",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload.get("executed", {}).get("blocked") is True
    assert payload.get("executed", {}).get("reason") == "low-confidence"


def test_prompt_optimize_execute_should_run_recommended_command(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "做一次环境诊断并输出结果",
            "--project-root",
            str(tmp_path),
            "--execute",
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "doctor"
    executed = payload.get("executed", {})
    assert executed.get("exit_code") == 0
    args = executed.get("args", [])
    assert args and args[0] == "doctor"


def test_prompt_optimize_should_apply_project_router_config_overrides(tmp_path: Path):
    config_dir = tmp_path / ".beacon"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "intent-router.json").write_text(
        json.dumps(
            {
                "intent_command_templates": {
                    "status": ["workflow", "status", "--project", "{project_root}"],
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    result = _invoke(
        [
            "prompt",
            "optimize",
            "查看当前状态看板",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "status"
    assert payload.get("recommended_args", [])[:2] == ["workflow", "status"]


def test_prompt_optimize_should_write_router_history_event(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "做一次环境诊断",
            "--project-root",
            str(tmp_path),
        ]
    )
    assert result.exit_code == 0
    history = tmp_path / ".beacon" / "memory" / "prompt-router-history.jsonl"
    assert history.exists()
    lines = [line for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 1
    payload = json.loads(lines[-1])
    assert payload.get("intent") == "doctor"


def test_ask_command_should_route_and_execute_by_default(tmp_path: Path):
    result = _invoke(["ask", "做一次环境诊断", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "doctor"
    assert payload.get("executed", {}).get("exit_code") == 0
