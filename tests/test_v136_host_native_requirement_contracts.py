from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path, version: str = "v1.3.6") -> None:
    base = root / "docs" / "beacon" / version
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text(f"# {version}\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution Index\n\n- A\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n\n- A\n", encoding="utf-8")


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


def test_v136_prd_should_prefer_host_semantic_response_when_available(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv(
        "BEACON_HOST_PRD_RESPONSE_JSON",
        json.dumps(
            {
                "markdown": "\n".join(
                    [
                        "# PRD：Beacon Host Native",
                        "",
                        "## Context",
                        "",
                        "- Global boundaries: `docs/beacon/global-boundaries.md`",
                        "",
                        "## 1. 问题",
                        "",
                        "- 当前边界和实现承诺需要重新梳理。",
                        "",
                        "## 2. 目标",
                        "",
                        "- 让宿主原生 LLM 成为默认编排能力。",
                        "",
                        "## 3. 设计原则",
                        "",
                        "- 保持边界清晰。",
                        "- 明确分层职责。",
                        "- 失败后可恢复。",
                        "",
                        "## 4. 范围",
                        "",
                        "- 聚焦 requirement surface。",
                        "",
                        "## 5. 功能需求",
                        "",
                        "- FR-001 统一语义合同。",
                        "",
                        "## 6. 边界 / 分层 / 恢复策略",
                        "",
                        "- 边界需要稳定。",
                        "- 分层需要可解释。",
                        "- 恢复策略需要明确。",
                        "",
                        "## 7. 风险与缓解",
                        "",
                        "- 风险：模板化输出。缓解：引入 host-native 语义编排。",
                        "",
                        "## 8. 验收标准",
                        "",
                        "- 验收时要能看到模式与证据。",
                    ]
                )
            }
        ),
    )

    result = _invoke(
        [
            "prd",
            "create",
            "Beacon Host Native",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.6",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["effective_mode"] == "host"
    assert payload["generator_mode"] == "host"
    assert payload["capability_snapshot"]["host_semantic_ready"] is True


def test_v136_prototype_should_prefer_host_semantic_response_when_available(monkeypatch, tmp_path: Path) -> None:
    feature = _copy_real_v136_sources(tmp_path)
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv(
        "BEACON_HOST_PROTOTYPE_RESPONSE_JSON",
        json.dumps(
            {
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
                            "sections": ["经营摘要", "重点项目", "推荐动作", "状态反馈"],
                            "actions": [{"label": "进入总览", "trigger": "点击组合入口", "target": "management-overview"}],
                            "states": [
                                {"id": "ready", "label": "正常", "description": "可读"},
                                {"id": "loading", "label": "加载中", "description": "加载"},
                                {"id": "error", "label": "错误", "description": "失败"},
                            ],
                            "layout": ["+-------------------+", "| HOST 首页草图 |", "+-------------------+"],
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
                            "priority": "P0",
                            "platforms": ["Web", "PC"],
                            "responsibility": "密集扫描多项目状态。",
                            "sections": ["筛选", "项目列表", "风险摘要", "状态反馈"],
                            "actions": [{"label": "进入项目详情", "trigger": "点击项目行", "target": "project-detail"}],
                            "states": [
                                {"id": "ready", "label": "可用", "description": "可读"},
                                {"id": "error", "label": "错误", "description": "失败"},
                            ],
                            "layout": ["+-------------------+", "| HOST 总览草图 |", "+-------------------+"],
                            "analysis": {
                                "target_user": "manager",
                                "decision_focus": ["确认项目差异"],
                                "layout_rules": ["列表优先"],
                                "noise_guardrail": "不展示底层事务字段。",
                            },
                        },
                        {
                            "page_id": "project-detail",
                            "name": "项目详情",
                            "priority": "P0",
                            "platforms": ["Web", "PC"],
                            "responsibility": "展示单项目接力信息。",
                            "sections": ["头部摘要", "需求闭环", "推荐动作", "状态反馈"],
                            "actions": [{"label": "返回总览", "trigger": "点击返回", "target": "management-overview"}],
                            "states": [
                                {"id": "ready", "label": "可接力", "description": "详情已加载。"},
                                {"id": "error", "label": "错误", "description": "失败"},
                            ],
                            "layout": ["+-------------------+", "| HOST 详情草图 |", "+-------------------+"],
                            "analysis": {
                                "target_user": "项目 owner",
                                "decision_focus": ["当前推进到哪里。"],
                                "layout_rules": ["头部先建立上下文。"],
                                "noise_guardrail": "不承载底层日志。",
                            },
                        },
                        {
                            "page_id": "runtime-center",
                            "name": "运行中心",
                            "priority": "P1",
                            "platforms": ["Web", "PC"],
                            "responsibility": "展示运行态摘要。",
                            "sections": ["模式切换", "session 摘要", "最近 blocker", "状态反馈"],
                            "actions": [{"label": "返回详情", "trigger": "点击返回", "target": "project-detail"}],
                            "states": [
                                {"id": "ready", "label": "可用", "description": "可读。"},
                                {"id": "team-active", "label": "Team 运行", "description": "运行中。"},
                                {"id": "error", "label": "错误", "description": "失败。"},
                            ],
                            "layout": ["+-------------------+", "| HOST 运行中心 |", "+-------------------+"],
                            "analysis": {
                                "target_user": "执行者",
                                "decision_focus": ["确认当前运行模式"],
                                "layout_rules": ["先看模式，再看 blocker"],
                                "noise_guardrail": "不堆原始日志。",
                            },
                        },
                        {
                            "page_id": "recovery-diagnostics",
                            "name": "恢复诊断",
                            "priority": "P2",
                            "platforms": ["Web", "PC"],
                            "responsibility": "解释恢复路径。",
                            "sections": ["truth 来源", "doctor 建议", "恢复步骤", "状态反馈"],
                            "actions": [{"label": "返回详情", "trigger": "点击返回", "target": "project-detail"}],
                            "states": [
                                {"id": "ready", "label": "可用", "description": "可读。"},
                                {"id": "degraded", "label": "降级", "description": "需恢复。"},
                                {"id": "error", "label": "错误", "description": "失败。"},
                            ],
                            "layout": ["+-------------------+", "| HOST 恢复诊断 |", "+-------------------+"],
                            "analysis": {
                                "target_user": "诊断人",
                                "decision_focus": ["是否需要 doctor"],
                                "layout_rules": ["先看 truth，再看操作"],
                                "noise_guardrail": "不暴露底层事务字段。",
                            },
                        },
                        {
                            "page_id": "material-viewer",
                            "name": "项目物料查看器",
                            "priority": "P1",
                            "platforms": ["Web", "PC"],
                            "responsibility": "浏览版本物料。",
                            "sections": ["版本树", "文档列表", "阅读区", "来源路径"],
                            "actions": [{"label": "打开文档", "trigger": "点击文档", "target": "material-document-detail"}],
                            "states": [
                                {"id": "ready", "label": "可浏览", "description": "已加载。"},
                                {"id": "loading", "label": "加载中", "description": "加载。"},
                            ],
                            "layout": ["+-------------------+", "| HOST 物料查看器 |", "+-------------------+"],
                            "analysis": {
                                "target_user": "项目 owner",
                                "decision_focus": ["确认当前文档位置"],
                                "layout_rules": ["左树右文"],
                                "noise_guardrail": "只做只读浏览。",
                            },
                        },
                        {
                            "page_id": "material-document-detail",
                            "name": "物料文档详情",
                            "priority": "P2",
                            "platforms": ["Web", "PC"],
                            "responsibility": "展示文档详情。",
                            "sections": ["文档头部", "面包屑", "正文区", "来源路径"],
                            "actions": [{"label": "返回查看器", "trigger": "点击返回", "target": "material-viewer"}],
                            "states": [
                                {"id": "ready", "label": "已打开", "description": "可阅读。"},
                                {"id": "error", "label": "错误", "description": "未找到来源。"},
                            ],
                            "layout": ["+-------------------+", "| HOST 文档详情 |", "+-------------------+"],
                            "analysis": {
                                "target_user": "项目 owner",
                                "decision_focus": ["确认文档正文"],
                                "layout_rules": ["正文优先"],
                                "noise_guardrail": "不做编辑。",
                            },
                        },
                    ],
                    "transitions": [
                        {"from": "home", "to": "management-overview", "trigger": "点击组合入口", "type": "primary"},
                        {"from": "management-overview", "to": "project-detail", "trigger": "点击项目行", "type": "primary"},
                        {"from": "project-detail", "to": "runtime-center", "trigger": "点击运行摘要", "type": "primary"},
                        {"from": "project-detail", "to": "recovery-diagnostics", "trigger": "点击恢复入口", "type": "primary"},
                        {"from": "project-detail", "to": "material-viewer", "trigger": "点击物料入口", "type": "primary"},
                        {"from": "material-viewer", "to": "material-document-detail", "trigger": "点击文档", "type": "drill-down"},
                        {"from": "material-document-detail", "to": "material-viewer", "trigger": "点击返回", "type": "return"},
                        {"from": "project-detail", "to": "management-overview", "trigger": "点击返回", "type": "return"},
                    ],
                }
            }
        ),
    )

    result = _invoke(
        [
            "prototype",
            "create",
            feature,
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.6",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["effective_mode"] == "host"
    assert payload["generator_mode"] == "host"
    root = tmp_path / "docs" / "beacon" / "v1.3.6" / "prototype" / "beacon-v1-3-6-visual-management-console-and-material-viewer"
    assert "HOST 首页草图" in (root / "pages" / "home.md").read_text(encoding="utf-8")


def test_v136_user_story_should_emit_mode_contract_json(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    monkeypatch.delenv("BEACON_HOST_RUNTIME", raising=False)
    monkeypatch.delenv("BEACON_HOST_USER_STORY_RESPONSE_JSON", raising=False)

    result = _invoke(
        [
            "user-story",
            "create",
            "Host Native Story",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.6",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "rule"
    assert payload["fallback_reason"] == "llm_unavailable"
    assert payload["capability_snapshot"]["command_name"] == "user-story"


def test_v136_test_case_should_emit_mode_contract_into_machine_payload(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    monkeypatch.delenv("BEACON_HOST_RUNTIME", raising=False)
    monkeypatch.delenv("BEACON_HOST_TEST_CASE_RESPONSE_JSON", raising=False)

    result = _invoke(
        [
            "test-case",
            "create",
            "Host Native QA",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.6",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "rule"
    assert payload["fallback_reason"] == "llm_unavailable"

    matrix_path = tmp_path / "docs" / "beacon" / "v1.3.6" / ".machine" / "qa" / "host-native-qa.ac-test-matrix.json"
    matrix_payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    assert matrix_payload["compiler"]["effective_mode"] == "rule"
    assert matrix_payload["compiler"]["capability_snapshot"]["command_name"] == "test-case"
