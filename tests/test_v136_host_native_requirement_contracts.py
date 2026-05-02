from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.semantic_runtime import build_semantic_capability_snapshot, ensure_default_host_bridge_env
import beacon.utils.prototype_utils as prototype_utils
import beacon.commands.prototype as prototype_command


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
    monkeypatch.delenv("BEACON_HOST_PROTOTYPE_BRIDGE_CMD", raising=False)
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


def test_v136_prototype_host_capability_should_admit_provider_backed_host_runtime(monkeypatch) -> None:
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv("BEACON_LLM_API_KEY", "test-key")
    monkeypatch.delenv("BEACON_HOST_PROTOTYPE_RESPONSE_JSON", raising=False)
    monkeypatch.delenv("BEACON_HOST_PROTOTYPE_BRIDGE_CMD", raising=False)
    snapshot = build_semantic_capability_snapshot("prototype", disable_env="BEACON_PROTOTYPE_DISABLE_LLM")
    assert snapshot["host_runtime"] == "codex"
    assert snapshot["host_runtime_supported"] is True
    assert snapshot["host_response_available"] is False
    assert snapshot["provider_available"] is True
    assert snapshot["host_transport"] == "provider-bridge"
    assert snapshot["host_semantic_ready"] is True


def test_v136_prototype_host_capability_should_admit_command_bridge(monkeypatch) -> None:
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv("BEACON_HOST_PROTOTYPE_BRIDGE_CMD", f"{sys.executable} -c \"print('{{}}')\"")
    monkeypatch.delenv("BEACON_HOST_PROTOTYPE_RESPONSE_JSON", raising=False)
    monkeypatch.delenv("BEACON_LLM_API_KEY", raising=False)
    snapshot = build_semantic_capability_snapshot("prototype", disable_env="BEACON_PROTOTYPE_DISABLE_LLM")
    assert snapshot["host_runtime"] == "codex"
    assert snapshot["host_runtime_supported"] is True
    assert snapshot["host_bridge_command_available"] is True
    assert snapshot["host_transport"] == "command-bridge"
    assert snapshot["host_semantic_ready"] is True


def test_v136_should_auto_configure_default_prototype_host_bridge_env(monkeypatch) -> None:
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.delenv("BEACON_HOST_PROTOTYPE_BRIDGE_CMD", raising=False)
    command = ensure_default_host_bridge_env("prototype")
    assert command
    assert "prototype host-bridge" in command
    assert command == str(os.environ.get("BEACON_HOST_PROTOTYPE_BRIDGE_CMD", ""))


def test_v136_should_auto_configure_default_requirement_host_bridge_envs(monkeypatch) -> None:
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    for command_name, env_name in (
        ("prd", "BEACON_HOST_PRD_BRIDGE_CMD"),
        ("user-story", "BEACON_HOST_USER_STORY_BRIDGE_CMD"),
        ("test-case", "BEACON_HOST_TEST_CASE_BRIDGE_CMD"),
    ):
        monkeypatch.delenv(env_name, raising=False)
        command = ensure_default_host_bridge_env(command_name)
        assert command
        assert f"{command_name} host-bridge" in command
        assert command == str(os.environ.get(env_name, ""))


def test_v136_prototype_host_bridge_command_should_emit_inference(monkeypatch) -> None:
    def _fake_real_inference(**_kwargs):
        return {
            "provider_model": "host-bridge-model",
            "completion": "{}",
            "payload": {
                "prototype_archetype": "admin-workbench",
                "theme": {"primary": "#123456", "secondary": "#0F172A"},
                "pages": [],
                "transitions": [],
            },
            "prompt_tokens": 5,
            "completion_tokens": 7,
        }

    monkeypatch.setattr(prototype_command, "_real_prototype_llm_inference", _fake_real_inference)
    result = _invoke(
        [
            "prototype",
            "host-bridge",
            json.dumps(
                {
                    "request_kind": "prototype-wireframe-compile",
                    "feature": "demo-feature",
                    "version": "v1.3.6",
                    "requested_model": "beacon-prototype-compiler",
                    "documents": [{"type": "prd", "text": "demo"}],
                    "semantic_layer": {"schema_version": "1.0"},
                },
                ensure_ascii=False,
            ),
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["provider_model"] == "host-bridge-model"
    assert payload["payload"]["prototype_archetype"] == "admin-workbench"


def test_v136_prd_should_use_command_bridge_when_available(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    bridge_script = tmp_path / "prd_bridge.py"
    bridge_script.write_text(
        "\n".join(
            [
                "import json, sys",
                "request = json.loads(sys.stdin.read())",
                "assert request['request_kind'] == 'prd-semantic-compile'",
                "print(json.dumps({'markdown': '# PRD：Host Bridge\\n\\n## Context\\n\\n- A\\n\\n## 1. 问题\\n\\n- A\\n\\n## 2. 目标\\n\\n- A\\n\\n## 3. 设计原则\\n\\n- A\\n\\n## 4. 范围\\n\\n- A\\n\\n## 5. 功能需求\\n\\n- A\\n\\n## 6. 边界 / 分层 / 恢复策略\\n\\n- 边界。\\n- 分层。\\n- 恢复。\\n\\n## 7. 风险与缓解\\n\\n- 风险。缓解。\\n\\n## 8. 验收标准\\n\\n- A'}))",
            ]
        ) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv("BEACON_HOST_PRD_BRIDGE_CMD", f"{sys.executable} {bridge_script}")
    result = _invoke(["prd", "create", "Bridge PRD", "--project", str(tmp_path), "--version", "v1.3.6", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["effective_mode"] == "host"
    assert payload["generator_mode"] == "host"
    assert payload["capability_snapshot"]["host_transport"] == "command-bridge"


def test_v136_user_story_should_use_command_bridge_when_available(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    bridge_script = tmp_path / "user_story_bridge.py"
    bridge_script.write_text(
        "\n".join(
            [
                "import json, sys",
                "request = json.loads(sys.stdin.read())",
                "assert request['request_kind'] == 'user-story-semantic-compile'",
                "print(json.dumps({'story': {'title': 'Bridge Story', 'as_a': 'operator', 'i_want': 'to use bridge mode', 'so_that': 'host transport is unified', 'acceptance_criteria': {'functionality': ['f1'], 'data': ['d1'], 'ux': ['u1'], 'performance': ['p1'], 'security': ['s1'], 'compatibility': ['c1'], 'error_handling': ['e1']}, 'story_points': 5, 'priority': 'high', 'status': 'draft', 'created_at': '2026-05-03T00:00:00'}}))",
            ]
        ) + "\n",
        encoding="utf-8",
    )
    _seed_docs(tmp_path)
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv("BEACON_HOST_USER_STORY_BRIDGE_CMD", f"{sys.executable} {bridge_script}")
    result = _invoke(["user-story", "create", "Bridge Story", "--project", str(tmp_path), "--version", "v1.3.6", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["effective_mode"] == "host"
    assert payload["capability_snapshot"]["host_transport"] == "command-bridge"


def test_v136_user_story_host_bridge_should_project_requirement_truth(tmp_path: Path) -> None:
    version = "v1.3.6"
    feature = "Bridge Story Truth"
    _seed_docs(tmp_path, version=version)
    slug = "bridge-story-truth"
    (tmp_path / "docs" / "beacon" / version / "prd" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# PRD：{feature}",
                "",
                "## 5. 功能需求",
                "",
                "- AC-001 管理端页面必须展示订单列表。",
                "- AC-002 接口返回订单金额与库存字段。",
                "- AC-003 异常时必须返回错误提示与恢复动作。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = _invoke(
        [
            "user-story",
            "host-bridge",
            json.dumps(
                {
                    "request_kind": "user-story-semantic-compile",
                    "feature": feature,
                    "version": version,
                    "project_root": str(tmp_path),
                },
                ensure_ascii=False,
            ),
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    story = payload["story"]
    assert story["as_a"] == "operator"
    assert "管理端页面必须展示订单列表。" in story["acceptance_criteria"]["ux"]
    assert "接口返回订单金额与库存字段。" in story["acceptance_criteria"]["data"]
    assert "异常时必须返回错误提示与恢复动作。" in story["acceptance_criteria"]["error_handling"]


def test_v136_test_case_should_use_command_bridge_when_available(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    bridge_script = tmp_path / "test_case_bridge.py"
    bridge_script.write_text(
        "\n".join(
            [
                "import json, sys",
                "request = json.loads(sys.stdin.read())",
                "assert request['request_kind'] == 'test-case-semantic-compile'",
                "print(json.dumps({'entries': [{'tc_id': 'TC-901', 'ac_id': 'AC-001', 'layer': 'unit', 'command': 'pytest -q', 'assertion': 'bridge entry exists', 'evidence_path': '.beacon/evidence/test-results/bridge/TC-901.json', 'status': 'pending', 'source': 'bridge'}]}))",
            ]
        ) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv("BEACON_HOST_TEST_CASE_BRIDGE_CMD", f"{sys.executable} {bridge_script}")
    result = _invoke(["test-case", "create", "Bridge QA", "--project", str(tmp_path), "--version", "v1.3.6", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["effective_mode"] == "host"
    assert payload["capability_snapshot"]["host_transport"] == "command-bridge"
    matrix_path = tmp_path / "docs" / "beacon" / "v1.3.6" / ".machine" / "qa" / "bridge-qa.ac-test-matrix.json"
    matrix_payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    assert matrix_payload["entries"][0]["tc_id"] == "TC-901"


def test_v136_test_case_host_bridge_should_prioritize_qa_rows(tmp_path: Path) -> None:
    result = _invoke(
        [
            "test-case",
            "host-bridge",
            json.dumps(
                {
                    "request_kind": "test-case-semantic-compile",
                    "feature": "Bridge QA Truth",
                    "feature_slug": "bridge-qa-truth",
                    "ui_runner": "browser-use",
                    "ac_items": [{"ac_id": "AC-001", "text": "订单列表可见"}],
                    "qa_case_rows": [
                        {
                            "tc_id": "TC-US001-001",
                            "story_id": "US-001",
                            "case_type": "正向流程",
                            "scenario": "打开订单列表",
                            "steps": "进入页面",
                            "expected_result": "订单列表展示成功",
                            "execution": "agent-browser",
                            "source": "qa:test-cases:host-bridge",
                        }
                    ],
                },
                ensure_ascii=False,
            ),
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["entries"][0]["tc_id"] == "TC-US001-001"
    assert payload["entries"][0]["assertion"] == "订单列表展示成功"


def test_v136_prototype_should_use_command_bridge_before_provider(monkeypatch, tmp_path: Path) -> None:
    feature = _copy_real_v136_sources(tmp_path)
    bridge_script = tmp_path / "prototype_bridge.py"
    bridge_script.write_text(
        "\n".join(
            [
                "import json, sys",
                "request = json.loads(sys.stdin.read())",
                "assert request['command_name'] == 'prototype'",
                "assert request['request_kind'] == 'prototype-wireframe-compile'",
                "print(json.dumps({",
                "  'model': 'codex-host-native',",
                "  'completion': '{}',",
                "  'prompt_tokens': 13,",
                "  'completion_tokens': 21,",
                "  'payload': {",
                "    'prototype_archetype': 'admin-workbench',",
                "    'theme': {'primary': '#123456', 'secondary': '#0F172A'},",
                "    'pages': [",
                "      {",
                "        'page_id': 'home',",
                "        'name': '首页',",
                "        'priority': 'P0',",
                "        'platforms': ['Web', 'PC'],",
                "        'responsibility': '先回答经营判断。',",
                "        'sections': ['经营摘要', '推荐动作'],",
                "        'actions': [{'label': '进入总览', 'trigger': '点击组合入口', 'target': 'management-overview'}],",
                "        'states': [{'id': 'ready', 'label': '正常', 'description': '可读'}],",
                "        'layout': ['+-------------------+', '| COMMAND BRIDGE 首页 |', '+-------------------+'],",
                "        'analysis': {",
                "          'target_user': 'owner',",
                "          'decision_focus': ['先判断整体情况'],",
                "          'layout_rules': ['首屏先给判断'],",
                "          'noise_guardrail': '不要暴露机器投影细节。'",
                "        }",
                "      },",
                "      {",
                "        'page_id': 'management-overview',",
                "        'name': '管理总览',",
                "        'priority': 'P0',",
                "        'platforms': ['Web', 'PC'],",
                "        'responsibility': '密集扫描多项目状态。',",
                "        'sections': ['筛选', '项目列表'],",
                "        'actions': [{'label': '进入项目详情', 'trigger': '点击项目行', 'target': 'project-detail'}],",
                "        'states': [{'id': 'ready', 'label': '可用', 'description': '可读'}],",
                "        'layout': ['+-------------------+', '| COMMAND BRIDGE 总览 |', '+-------------------+'],",
                "        'analysis': {",
                "          'target_user': 'manager',",
                "          'decision_focus': ['确认项目差异'],",
                "          'layout_rules': ['列表优先'],",
                "          'noise_guardrail': '不展示底层事务字段。'",
                "        }",
                "      },",
                "      {",
                "        'page_id': 'project-detail',",
                "        'name': '项目详情',",
                "        'priority': 'P0',",
                "        'platforms': ['Web', 'PC'],",
                "        'responsibility': '展示单项目接力信息。',",
                "        'sections': ['头部摘要', '推荐动作'],",
                "        'actions': [{'label': '返回总览', 'trigger': '点击返回', 'target': 'management-overview'}],",
                "        'states': [{'id': 'ready', 'label': '可接力', 'description': '详情已加载。'}],",
                "        'layout': ['+-------------------+', '| COMMAND BRIDGE 详情 |', '+-------------------+'],",
                "        'analysis': {",
                "          'target_user': '项目 owner',",
                "          'decision_focus': ['当前推进到哪里。'],",
                "          'layout_rules': ['头部先建立上下文。'],",
                "          'noise_guardrail': '不承载底层日志。'",
                "        }",
                "      }",
                "    ],",
                "    'transitions': [",
                "      {'from': 'home', 'to': 'management-overview', 'trigger': '点击组合入口', 'type': 'primary'},",
                "      {'from': 'management-overview', 'to': 'project-detail', 'trigger': '点击项目行', 'type': 'primary'},",
                "      {'from': 'project-detail', 'to': 'management-overview', 'trigger': '点击返回', 'type': 'return'}",
                "    ]",
                "  }",
                "}, ensure_ascii=False))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv("BEACON_HOST_PROTOTYPE_BRIDGE_CMD", f"{sys.executable} {bridge_script}")
    monkeypatch.setenv("BEACON_LLM_API_KEY", "test-key")
    monkeypatch.delenv("BEACON_HOST_PROTOTYPE_RESPONSE_JSON", raising=False)

    def _fail_real_inference(**_kwargs):
        raise AssertionError("provider fallback should not run when command bridge is available")

    monkeypatch.setattr(prototype_utils, "_real_prototype_llm_inference", _fail_real_inference)

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
    assert payload["capability_snapshot"]["host_transport"] == "command-bridge"
    root = tmp_path / "docs" / "beacon" / "v1.3.6" / "prototype" / "beacon-v1-3-6-visual-management-console-and-material-viewer"
    assert "COMMAND BRIDGE 首页" in (root / "pages" / "home.md").read_text(encoding="utf-8")


def test_v136_prototype_should_fallback_to_provider_when_default_host_bridge_cannot_complete(monkeypatch, tmp_path: Path) -> None:
    feature = _copy_real_v136_sources(tmp_path)
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.setenv("BEACON_LLM_API_KEY", "test-key")
    monkeypatch.delenv("BEACON_HOST_PROTOTYPE_RESPONSE_JSON", raising=False)
    monkeypatch.delenv("BEACON_HOST_PROTOTYPE_BRIDGE_CMD", raising=False)

    def _fake_real_inference(**_kwargs):
        return {
            "provider_model": "gpt-5",
            "completion": "{}",
            "payload": {
                "prototype_archetype": "admin-workbench",
                "theme": {"primary": "#123456", "secondary": "#0F172A"},
                "pages": [
                    {
                        "page_id": "home",
                        "name": "首页",
                        "priority": "P0",
                        "platforms": ["Web", "PC"],
                        "responsibility": "先回答经营判断。",
                        "sections": ["经营摘要", "推荐动作"],
                        "actions": [{"label": "进入总览", "trigger": "点击组合入口", "target": "management-overview"}],
                        "states": [{"id": "ready", "label": "正常", "description": "可读"}],
                        "layout": ["+-------------------+", "| PROVIDER HOST 首页 |", "+-------------------+"],
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
                        "sections": ["筛选", "项目列表"],
                        "actions": [{"label": "进入项目详情", "trigger": "点击项目行", "target": "project-detail"}],
                        "states": [{"id": "ready", "label": "可用", "description": "可读"}],
                        "layout": ["+-------------------+", "| PROVIDER HOST 总览 |", "+-------------------+"],
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
                        "sections": ["头部摘要", "推荐动作"],
                        "actions": [{"label": "返回总览", "trigger": "点击返回", "target": "management-overview"}],
                        "states": [{"id": "ready", "label": "可接力", "description": "详情已加载。"}],
                        "layout": ["+-------------------+", "| PROVIDER HOST 详情 |", "+-------------------+"],
                        "analysis": {
                            "target_user": "项目 owner",
                            "decision_focus": ["当前推进到哪里。"],
                            "layout_rules": ["头部先建立上下文。"],
                            "noise_guardrail": "不承载底层日志。",
                        },
                    },
                ],
                "transitions": [
                    {"from": "home", "to": "management-overview", "trigger": "点击组合入口", "type": "primary"},
                    {"from": "management-overview", "to": "project-detail", "trigger": "点击项目行", "type": "primary"},
                    {"from": "project-detail", "to": "management-overview", "trigger": "点击返回", "type": "return"},
                ],
            },
            "prompt_tokens": 11,
            "completion_tokens": 22,
        }

    monkeypatch.setattr(prototype_utils, "_real_prototype_llm_inference", _fake_real_inference)

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
    assert payload["capability_snapshot"]["host_transport"] == "command-bridge"
    root = tmp_path / "docs" / "beacon" / "v1.3.6" / "prototype" / "beacon-v1-3-6-visual-management-console-and-material-viewer"
    assert "PROVIDER HOST 首页" in (root / "pages" / "home.md").read_text(encoding="utf-8")


def test_v136_user_story_should_emit_mode_contract_json(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.delenv("BEACON_HOST_USER_STORY_RESPONSE_JSON", raising=False)
    monkeypatch.delenv("BEACON_HOST_USER_STORY_BRIDGE_CMD", raising=False)

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
    assert payload["effective_mode"] == "host"
    assert payload["fallback_reason"] == ""
    assert payload["capability_snapshot"]["command_name"] == "user-story"
    assert payload["capability_snapshot"]["host_transport"] == "command-bridge"


def test_v136_test_case_should_emit_mode_contract_into_machine_payload(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    monkeypatch.delenv("BEACON_HOST_TEST_CASE_RESPONSE_JSON", raising=False)
    monkeypatch.delenv("BEACON_HOST_TEST_CASE_BRIDGE_CMD", raising=False)

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
    assert payload["effective_mode"] == "host"
    assert payload["fallback_reason"] == ""
    assert payload["capability_snapshot"]["host_transport"] == "command-bridge"

    matrix_path = tmp_path / "docs" / "beacon" / "v1.3.6" / ".machine" / "qa" / "host-native-qa.ac-test-matrix.json"
    matrix_payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    assert matrix_payload["compiler"]["effective_mode"] == "host"
    assert matrix_payload["compiler"]["capability_snapshot"]["command_name"] == "test-case"
