"""Contracts for prompt optimize and intent routing behavior."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.intent_router import optimize_prompt_to_plan


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


def test_ask_command_should_route_plan_only_by_default(tmp_path: Path):
    result = _invoke(["ask", "做一次环境诊断并执行健康检查", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "doctor"
    assert payload.get("executed") in (None, {})


def test_ask_command_should_execute_when_flag_enabled(tmp_path: Path):
    result = _invoke(
        ["ask", "做一次环境诊断并执行健康检查", "--project-root", str(tmp_path), "--execute", "--json"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "doctor"
    assert payload.get("executed", {}).get("exit_code") == 0


def test_intent_router_should_not_route_install_upgrade_text_to_user_story(tmp_path: Path):
    plan = optimize_prompt_to_plan(
        "升级安装beacon",
        project_root=tmp_path,
        router_mode="rule",
    )
    assert plan.get("intent") != "user-story"
    assert plan.get("recommended_args", [None])[0] != "user-story"


def test_prompt_optimize_execute_allow_mixed_should_not_be_blocked_by_low_confidence(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "请先检查 gate 状态并直接写代码修复线上 bug",
            "--project-root",
            str(tmp_path),
            "--execute",
            "--allow-mixed",
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("boundary", {}).get("state") == "mixed_need_confirm"
    assert float(payload.get("confidence", 0.0) or 0.0) < float(
        payload.get("execution_policy", {}).get("min_confidence", 0.62)
    )
    executed = payload.get("executed", {})
    assert executed.get("blocked") is not True
    assert executed.get("exit_code") == 0


def test_ask_allow_mixed_should_not_require_allow_low_confidence(tmp_path: Path):
    result = _invoke(
        [
            "ask",
            "请先检查 gate 状态并直接写代码修复线上 bug",
            "--project-root",
            str(tmp_path),
            "--execute",
            "--allow-mixed",
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("boundary", {}).get("state") == "mixed_need_confirm"
    executed = payload.get("executed", {})
    assert executed.get("blocked") is not True
    assert executed.get("exit_code") == 0


def test_prompt_optimize_continue_workflow_should_prioritize_resume_intent(tmp_path: Path):
    result = _invoke(
        [
            "prompt",
            "optimize",
            "继续上次workflow",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload.get("intent") == "resume"
    args = payload.get("recommended_args", [])
    assert args
    assert args[0] in {"resume", "workflow"}
    assert "continue" in args or "resume" in args


def test_intent_router_should_detect_english_out_of_scope_boundaries(tmp_path: Path):
    prompts = [
        "deploy to kubernetes",
        "fix production bug",
        "database migration",
    ]
    for goal in prompts:
        plan = optimize_prompt_to_plan(goal, project_root=tmp_path, router_mode="rule")
        assert plan.get("intent") == "outside-boundary"
        assert plan.get("boundary", {}).get("state") == "out_of_scope"
        assert plan.get("boundary", {}).get("in_scope") is False


def test_prompt_optimize_should_default_non_core_labs_prompts_back_to_think(tmp_path: Path):
    samples = [
        "请做竞品分析",
        "请给我一份 api design 草案",
        "输出一个 ui spec 文档",
        "画一个移动端 wireframe",
        "创建用户 persona",
    ]

    for goal in samples:
        result = _invoke(
            [
                "prompt",
                "optimize",
                goal,
                "--project-root",
                str(tmp_path),
                "--json",
            ]
        )
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload.get("intent") not in {"analyze", "api-design", "ui-spec", "wireframe", "persona"}
        assert payload.get("recommended_args", [None])[0] not in {"analyze", "api-design", "ui-spec", "wireframe", "persona"}


def test_prompt_optimize_should_route_explicit_lab_command_hints(tmp_path: Path):
    samples = {
        "beacon analyze 抖音": "analyze",
        "beacon api-design 订单接口": "api-design",
        "beacon ui-spec 会员中心": "ui-spec",
        "beacon wireframe 登录页": "wireframe",
        "beacon persona 核心用户": "persona",
    }

    for goal, expected_intent in samples.items():
        result = _invoke(
            [
                "prompt",
                "optimize",
                goal,
                "--project-root",
                str(tmp_path),
                "--json",
            ]
        )
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload.get("intent") == expected_intent
        assert payload.get("recommended_args", [None])[0] == expected_intent
