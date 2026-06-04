# Test Cases: beacon-ui-prototype-lifecycle

## Overview

**Feature**: beacon-ui-prototype-lifecycle  
**Version**: v1.1.2  
**Source**: `docs/beacon/archive/v1.1.2/user-story/beacon-ui-prototype-lifecycle.md`  
**AC Matrix JSON**: `docs/beacon/archive/v1.1.2/qa/test-cases/beacon-ui-prototype-lifecycle.ac-test-matrix.json`  
**QA Matrix JSON**: `docs/beacon/archive/v1.1.2/qa/test-cases/beacon-ui-prototype-lifecycle.qa9-matrix.json`

---

## AC → TC Mapping

| AC ID | TC ID | Layer | Scenario | Expected |
|------|------|-------|----------|----------|
| AC-001 | TC-001 | unit | `prototype` 子命令已注册且帮助信息可见 | CLI help 正常输出 |
| AC-002 | TC-002 | integration | `prototype create` 从 user-story/prd 生成 `index.html` | 单页 HTML 落盘成功 |
| AC-003 | TC-003 | integration | prototype 输出目录位于 `docs/beacon/<version>/prototype/<feature>/` | 路径正确且不写 docs/product |
| AC-004 | TC-004 | integration | create 后生成 `manifest.json` / `source-map.json` / `freeze.json` | 工件齐全 |
| AC-005 | TC-005 | smoke | 生成后的 `index.html` 可在本地打开预览 | 页面可加载 |
| AC-006 | TC-006 | integration | `prototype preview` 输出预览路径或本地 serve 命令 | 用户可快速运行 |
| AC-007 | TC-007 | unit | `freeze` 写入来源指纹；来源变更后状态变 stale | freeze / stale 语义正确 |
| AC-008 | TC-008 | integration | UI 需求启用 workflow prototype 阶段 | workflow 阶段顺序正确 |
| AC-009 | TC-009 | integration | 非 UI 需求执行 workflow 时 prototype 自动 skip | lifecycle 有 skip reason |
| AC-010 | TC-010 | contract | status / hud / report 显示 prototype 状态 | 状态字段完整 |
| AC-011 | TC-011 | exception | `ui_visualization_required=true` 且 prototype 缺失 | gate BLOCKED + reason code |
| AC-012 | TC-012 | exception | prototype 存在但未 freeze 或 stale | gate BLOCKED + reason code |
| AC-013 | TC-013 | unit | prompt/ask 输入“交互原型”等关键词 | 正确路由到 prototype |
| AC-014 | TC-014 | contract | 默认 HTML stack 为 Bootstrap 5.3.x + Bootstrap Icons + Beacon Theme CSS + Alpine.js | renderer / manifest contract 正确 |
| AC-015 | TC-015 | smoke | prototype 页面支持基础导航跳转、Tabs、Modal、Offcanvas、Toast、表单交互 | 关键 UI 交互可工作 |
| AC-016 | TC-016 | smoke | verify 对 prototype 做基础 DOM / console / a11y 检查 | smoke 通过 |
| AC-017 | TC-017 | contract | prototype 页面满足基础语义结构、focus、label、aria-label、reduced-motion 约束 | Web 规范通过 |
| AC-018 | TC-018 | regression | 现有 design / ui-spec / wireframe / workflow contract 不回归 | 旧命令仍正常 |

---

## 执行检查清单

- [ ] 校验 `prototype --help`
- [ ] 校验 create 默认从 `user-story / prd` 推导
- [ ] 校验所有工件写入 `docs/beacon`
- [ ] 校验 `freeze -> stale` 状态切换
- [ ] 校验 workflow 启用 prototype 阶段
- [ ] 校验非 UI 需求 skip prototype
- [ ] 校验 `prompt optimize` prototype 路由
- [ ] 校验 gate 对 missing / not_frozen / stale 阻断
- [ ] 校验 status / hud / report 展示 prototype
- [ ] 校验 HTML 单页可快速本地运行
- [ ] 校验 Bootstrap 组件能力覆盖导航 / 弹窗 / Tabs / Offcanvas / 表单场景
- [ ] 校验 Beacon Theme CSS 已注入，页面不是裸默认组件观感
- [ ] 校验 prototype 页面满足基础可访问性与焦点态要求
- [ ] 校验 design / ui-spec / wireframe 无回归

---

## 建议自动化命令（规划）

| TC ID | 建议命令 | 备注 |
|------|----------|------|
| TC-001 | `python3 -m pytest -q tests/test_v112_prototype_command.py::test_prototype_help` | CLI 注册 |
| TC-002 | `python3 -m pytest -q tests/test_v112_prototype_command.py::test_prototype_create_generates_static_html` | create 产物 |
| TC-003 | `python3 -m pytest -q tests/test_v112_prototype_command.py::test_prototype_outputs_only_under_docs_beacon` | 路径治理 |
| TC-004 | `python3 -m pytest -q tests/test_v112_prototype_contract.py::test_prototype_manifest_and_source_map_contract` | 工件 contract |
| TC-005 | `python3 -m pytest -q tests/test_v112_prototype_preview.py::test_preview_prints_local_entry` | preview |
| TC-007 | `python3 -m pytest -q tests/test_v112_prototype_freeze_contract.py` | freeze / stale |
| TC-008 | `python3 -m pytest -q tests/test_v112_workflow_prototype_stage.py::test_workflow_with_prototype_stage` | workflow 集成 |
| TC-009 | `python3 -m pytest -q tests/test_v112_workflow_prototype_stage.py::test_non_ui_feature_should_skip_prototype` | skip 语义 |
| TC-010 | `python3 -m pytest -q tests/test_v112_status_report_prototype.py` | status / hud / report |
| TC-011 | `python3 -m pytest -q tests/test_v112_gate_prototype_contract.py::test_gate_blocks_when_prototype_missing` | gate reason |
| TC-012 | `python3 -m pytest -q tests/test_v112_gate_prototype_contract.py::test_gate_blocks_when_prototype_not_frozen_or_stale` | freeze / stale 阻断 |
| TC-013 | `python3 -m pytest -q tests/test_v112_prompt_prototype_routing.py` | intent routing |
| TC-014 | `python3 -m pytest -q tests/test_v112_prototype_html_stack.py` | HTML stack contract |
| TC-015 | `python3 -m pytest -q tests/test_v112_prototype_ui_interactions.py` | Bootstrap UI 交互 contract |
| TC-016 | `python3 -m pytest -q tests/test_v112_verify_prototype_smoke.py` | verify smoke |
| TC-017 | `python3 -m pytest -q tests/test_v112_prototype_accessibility_contract.py` | 语义 / a11y contract |
| TC-018 | `python3 -m pytest -q tests/test_beacon.py tests/test_prompt_optimize_contract.py tests/test_workflow_continue_progress.py` | 回归 |

---

## 建议 reason codes

- `prototype_missing`
- `prototype_not_frozen`
- `prototype_stale`
- `prototype_source_untraceable`
- `prototype_html_invalid`
- `prototype_preview_unavailable`
- `prototype_ui_contract_failed`
- `prototype_accessibility_contract_failed`
