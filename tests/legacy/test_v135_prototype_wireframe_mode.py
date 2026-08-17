from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _copy_real_v136_sources(tmp_path: Path) -> str:
    version = "v1.3.6"
    feature = "beacon-v1.3.6-visual-management-console-and-material-viewer"
    targets = {
        ROOT / "docs" / "beacon" / version / "user-story" / "beacon-v1.3.6-visual-management-console-and-material-viewer.md":
            tmp_path / "docs" / "beacon" / version / "user-story" / "beacon-v1.3.6-visual-management-console-and-material-viewer.md",
        ROOT / "docs" / "beacon" / version / "prd" / "beacon-v1-3-6-visual-management-console-and-material-viewer.md":
            tmp_path / "docs" / "beacon" / version / "prd" / "beacon-v1-3-6-visual-management-console-and-material-viewer.md",
        ROOT / "docs" / "beacon" / version / "qa" / "test-cases" / "beacon-v1.3.6-visual-management-console-and-material-viewer.md":
            tmp_path / "docs" / "beacon" / version / "qa" / "test-cases" / "beacon-v1.3.6-visual-management-console-and-material-viewer.md",
    }
    for source, target in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return feature


def test_v135_prototype_should_freeze_real_v136_management_console_wireframe(tmp_path: Path):
    feature = _copy_real_v136_sources(tmp_path)
    version = "v1.3.6"

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    create_payload = json.loads(create.stdout)
    assert create_payload["prototype_mode"] == "wireframe"

    bind = _invoke(["prototype", "bind", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert bind.exit_code == 0, bind.stdout

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["overall_status"] == "pass"

    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    assert json.loads(freeze.stdout)["status"] == "frozen"

    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["gate_ready"] is True

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "beacon-v1-3-6-visual-management-console-and-material-viewer"
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    expected_pages = {
        "home",
        "management-overview",
        "project-detail",
        "runtime-center",
        "recovery-diagnostics",
        "material-viewer",
        "material-document-detail",
    }
    assert expected_pages.issubset(set(plan["required_pages"]))
    for page_id in expected_pages:
        assert (root / "pages" / f"{page_id}.md").exists(), page_id

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=version)
    assert issues == []


def test_v135_prototype_auto_mode_should_fallback_to_rule_when_llm_unavailable(tmp_path: Path, monkeypatch):
    feature = _copy_real_v136_sources(tmp_path)
    version = "v1.3.6"
    monkeypatch.delenv("BEACON_LLM_API_KEY", raising=False)
    monkeypatch.delenv("BEACON_PROTOTYPE_DISABLE_LLM", raising=False)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    payload = json.loads(create.stdout)
    assert payload["requested_mode"] == "auto"
    assert payload["generator_mode"] == "rule"
    assert payload["fallback_reason"] == "llm_unavailable"

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "beacon-v1-3-6-visual-management-console-and-material-viewer"
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    assert plan["compiler"]["requested_mode"] == "auto"
    assert plan["compiler"]["generator_mode"] == "rule"
    assert plan["compiler"]["fallback_reason"] == "llm_unavailable"


def test_v135_prototype_llm_mode_should_materialize_llm_generated_layout(tmp_path: Path, monkeypatch):
    feature = _copy_real_v136_sources(tmp_path)
    version = "v1.3.6"
    monkeypatch.setenv("BEACON_LLM_API_KEY", "dummy-key")

    from beacon.utils import prototype_utils

    def _fake_llm_inference(*, feature: str, version: str, docs, model: str, semantic_layer=None):
        return {
            "provider_model": "fake-prototype-model",
            "completion": "{}",
            "prompt_tokens": 123,
            "completion_tokens": 45,
            "payload": {
                "prototype_archetype": "admin-workbench",
                "theme": {"primary": "#123456", "secondary": "#0F172A"},
                "pages": [
                    {
                        "page_id": "home",
                        "name": "首页",
                        "priority": "P0",
                        "platforms": ["Web", "PC"],
                        "responsibility": "先回答经营判断，并给出重点项目下钻入口。",
                        "sections": ["指标条", "重点介入区", "项目摘要表", "下一步建议"],
                        "actions": [
                            {"label": "查看总览", "trigger": "点击项目组合入口", "target": "management-overview"},
                            {"label": "查看重点项目", "trigger": "点击重点项目卡片", "target": "project-detail"},
                        ],
                        "states": [
                            {"id": "ready", "label": "正常总览", "description": "默认展示经营判断。"},
                            {"id": "loading", "label": "加载中", "description": "首页数据正在汇总。"},
                            {"id": "error", "label": "错误", "description": "摘要聚合失败。"},
                        ],
                        "layout": [
                            "+-------------------------------+",
                            "| LLM 首页草图 | 指标 | 介入项 |",
                            "+-------------------------------+",
                        ],
                        "analysis": {
                            "target_user": "CEO / owner",
                            "decision_focus": ["今天先盯哪些项目。", "哪里需要我介入。"],
                            "layout_rules": ["首屏先看经营指标。", "介入项必须早于明细表。"],
                            "noise_guardrail": "首页不暴露机器原始日志。",
                        },
                    },
                    {
                        "page_id": "management-overview",
                        "name": "管理总览",
                        "priority": "P0",
                        "platforms": ["Web", "PC"],
                        "responsibility": "密集扫描多项目状态。",
                        "sections": ["筛选条", "项目注册表"],
                        "actions": [{"label": "进入项目详情", "trigger": "点击项目行", "target": "project-detail"}],
                        "states": [{"id": "ready", "label": "可用", "description": "总览已加载。"}],
                        "layout": ["+---+", "| 总览 |", "+---+"],
                        "analysis": {
                            "target_user": "管理者",
                            "decision_focus": ["谁健康，谁阻塞。"],
                            "layout_rules": ["先筛选，再扫描表格。"],
                            "noise_guardrail": "不展开 runtime 原文。",
                        },
                    },
                    {
                        "page_id": "project-detail",
                        "name": "项目详情",
                        "priority": "P0",
                        "platforms": ["Web", "PC"],
                        "responsibility": "展示单项目接力信息。",
                        "sections": ["头部摘要", "需求闭环", "推荐动作"],
                        "actions": [{"label": "返回总览", "trigger": "点击返回", "target": "management-overview"}],
                        "states": [{"id": "ready", "label": "可接力", "description": "详情已加载。"}],
                        "layout": ["+---+", "| 详情 |", "+---+"],
                        "analysis": {
                            "target_user": "项目 owner",
                            "decision_focus": ["当前推进到哪里。"],
                            "layout_rules": ["头部先建立上下文。"],
                            "noise_guardrail": "不承载底层日志。",
                        },
                    },
                ],
                "transitions": [
                    {"from": "home", "to": "management-overview", "trigger": "点击项目组合入口", "type": "primary"},
                    {"from": "home", "to": "project-detail", "trigger": "点击重点项目卡片", "type": "primary"},
                    {"from": "management-overview", "to": "project-detail", "trigger": "点击项目行", "type": "primary"},
                ],
            },
        }

    monkeypatch.setattr(prototype_utils, "_real_prototype_llm_inference", _fake_llm_inference)

    create = _invoke(
        [
            "prototype",
            "create",
            feature,
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--mode",
            "llm",
            "--json",
        ]
    )
    assert create.exit_code == 0, create.stdout
    payload = json.loads(create.stdout)
    assert payload["requested_mode"] == "llm"
    assert payload["generator_mode"] == "llm"
    assert payload["fallback_reason"] == ""

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "beacon-v1-3-6-visual-management-console-and-material-viewer"
    page_text = (root / "pages" / "home.md").read_text(encoding="utf-8")
    assert "LLM 首页草图" in page_text
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    assert plan["compiler"]["generator_mode"] == "llm"
    assert plan["compiler"]["llm_trace"]["provider_model"] == "fake-prototype-model"


def test_v135_prototype_llm_mode_should_fail_without_api_key(tmp_path: Path, monkeypatch):
    feature = _copy_real_v136_sources(tmp_path)
    version = "v1.3.6"
    monkeypatch.delenv("BEACON_LLM_API_KEY", raising=False)
    monkeypatch.delenv("BEACON_PROTOTYPE_DISABLE_LLM", raising=False)

    create = _invoke(
        [
            "prototype",
            "create",
            feature,
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--mode",
            "llm",
            "--json",
        ]
    )
    assert create.exit_code == 2
    assert "BEACON_LLM_API_KEY" in create.stdout


def test_v135_prototype_auto_mode_should_fallback_when_llm_contract_invalid(tmp_path: Path, monkeypatch):
    feature = _copy_real_v136_sources(tmp_path)
    version = "v1.3.6"
    monkeypatch.setenv("BEACON_LLM_API_KEY", "dummy-key")

    from beacon.utils import prototype_utils

    def _invalid_llm_inference(*, feature: str, version: str, docs, model: str, semantic_layer=None):
        return {
            "provider_model": "fake-prototype-model",
            "completion": "{}",
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "payload": {
                "pages": [
                    {
                        "page_id": "home",
                        "name": "首页",
                        "sections": ["只有一个区块"],
                        "states": [{"id": "ready", "label": "可用", "description": "ok"}],
                        "actions": [],
                        "layout": ["+--+"],
                    }
                ],
                "transitions": [],
            },
        }

    monkeypatch.setattr(prototype_utils, "_real_prototype_llm_inference", _invalid_llm_inference)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    payload = json.loads(create.stdout)
    assert payload["requested_mode"] == "auto"
    assert payload["generator_mode"] == "rule"
    assert payload["fallback_reason"] == "llm_contract_validation_failed"


def test_v135_prototype_llm_mode_should_generate_semantic_shell_when_layout_missing(tmp_path: Path, monkeypatch):
    feature = _copy_real_v136_sources(tmp_path)
    version = "v1.3.6"
    monkeypatch.setenv("BEACON_LLM_API_KEY", "dummy-key")

    from beacon.utils import prototype_utils

    def _shell_only_llm_inference(*, feature: str, version: str, docs, model: str, semantic_layer=None):
        return {
            "provider_model": "fake-prototype-model",
            "completion": "{}",
            "prompt_tokens": 12,
            "completion_tokens": 8,
            "payload": {
                "prototype_archetype": "admin-workbench",
                "pages": [
                    {
                        "page_id": "home",
                        "name": "首页",
                        "sections": ["经营摘要", "重点项目", "推荐动作", "状态反馈"],
                        "actions": [{"label": "进入总览", "trigger": "点击组合入口", "target": "management-overview"}],
                        "states": [
                            {"id": "ready", "label": "正常", "description": "可读"},
                            {"id": "loading", "label": "加载中", "description": "加载"},
                        ],
                        "analysis": {
                            "target_user": "owner",
                            "decision_focus": ["先判断整体情况"],
                            "layout_rules": ["首屏先给判断"],
                            "noise_guardrail": "不要暴露机器投影细节。",
                        },
                    },
                    {
                        "page_id": "management-overview",
                        "name": "管理总览",
                        "sections": ["筛选", "项目列表", "风险摘要", "状态反馈"],
                        "actions": [{"label": "返回首页", "trigger": "点击返回", "target": "home"}],
                        "states": [
                            {"id": "ready", "label": "可用", "description": "可读"},
                            {"id": "error", "label": "错误", "description": "失败"},
                        ],
                        "analysis": {
                            "target_user": "manager",
                            "decision_focus": ["确认项目差异"],
                            "layout_rules": ["列表优先"],
                            "noise_guardrail": "不展示底层事务字段。",
                        },
                    },
                ],
                "transitions": [
                    {"from": "home", "to": "management-overview", "trigger": "点击组合入口", "type": "primary"},
                    {"from": "management-overview", "to": "home", "trigger": "点击返回", "type": "return"},
                ],
            },
        }

    monkeypatch.setattr(prototype_utils, "_real_prototype_llm_inference", _shell_only_llm_inference)

    create = _invoke(
        [
            "prototype",
            "create",
            feature,
            "--project",
            str(tmp_path),
            "--version",
            version,
            "--mode",
            "llm",
            "--json",
        ]
    )
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / "beacon-v1-3-6-visual-management-console-and-material-viewer"
    page_text = (root / "pages" / "home.md").read_text(encoding="utf-8")
    assert "页头：首页" in page_text
    assert "操作区：进入总览" in page_text
