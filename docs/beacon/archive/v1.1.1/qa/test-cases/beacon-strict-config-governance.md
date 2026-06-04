# Test Cases: beacon-strict-config-governance

## Overview

**Feature**: beacon-strict-config-governance  
**Version**: v1.1.1  
**Source**: `docs/beacon/archive/v1.1.1/user-story/beacon-strict-config-governance.md`  
**Memory Context**: `/Users/apple/Developer/Personal/my_skill/beacon/.beacon/state/workflow-memory/run-20260313T014417Z-b758/test-case-context.json`  
**AC Matrix JSON**: `docs/beacon/archive/v1.1.1/qa/test-cases/beacon-strict-config-governance.ac-test-matrix.json`  
**QA9 Matrix JSON**: `docs/beacon/archive/v1.1.1/qa/test-cases/beacon-strict-config-governance.qa9-matrix.json`

---

## AC → TC Mapping

| AC ID | TC ID | Layer | Scenario | Expected |
|------|------|-------|----------|----------|
| AC-001 | TC-001 | unit | strict 模式下无 workspace 配置直接启动 workflow | 返回 BLOCKED + reason code |
| AC-002 | TC-002 | unit | 同一 workspace 下存在多个项目时，按 CLI/env/cwd/default 优先级解析目标项目 | 项目解析结果稳定且可解释 |
| AC-003 | TC-003 | unit | implementation root/include/exclude 配置存在时，超出范围的执行计划被拒绝 | 返回 blocked + scope violation |
| AC-004 | TC-004 | unit | Git branch/tag/commit 与 `version_ref` 不对齐 | `verify-git-alignment --strict` BLOCKED |
| AC-005 | TC-005 | integration | doctor 生成 workspace/config 模板并修复可确定错误 | 模板落盘 + 修复报告生成 |
| AC-006 | TC-006 | integration | setup-agent-md 注入 CLAUDE.md/AGENTS.md/agent.md 生命周期块 | 注入成功且 verify-agent-md 通过 |
| AC-007 | TC-007 | integration | workflow preflight 后输出 config/source/git-alignment 标准元信息 | 三类文件均存在且字段正确 |
| AC-008 | TC-008 | smoke | 新需求物料写入 `docs/beacon/<version>/`，compat 镜像仅自动同步 | docs/beacon 为 source，docs/product 为 mirror |
| AC-009 | TC-009 | smoke | CI 串联 verify-config / verify-git-alignment / verify-agent-md / gate check | 全部通过时允许进入后续阶段 |
| AC-010 | TC-010 | exception | strict 模式下存在多个 P0 问题 | 同时返回明确 reason code、详情和修复命令 |
| AC-011 | TC-011 | regression | 现有 doctor context / version 兼容能力不被新配置治理回归破坏 | 旧 contract 继续通过 |
| AC-012 | TC-012 | integration | brainstorm / analyze 输出统一写入 `docs/beacon/<version>/research/` | research 文档落在统一目录，且不写 compat |
| AC-013 | TC-013 | unit | research 文档具备 type/status/feature/version/convergence_targets/source_of_truth 元信息 | 状态与元数据完整、`source_of_truth=false` |
| AC-014 | TC-014 | contract | workflow / gate 不直接消费 research 文档 | research 不被识别为最终交付主源 |
| AC-015 | TC-015 | integration | research 先收敛到 `user-story / prd` 后再生成 test-case | test-case 来源链路可追溯 |
| AC-016 | TC-016 | integration | execution/delivery-manifest.json 列出受影响项目、repo 与 Git refs | 多项目交付范围可追溯 |
| AC-017 | TC-017 | integration | execution/change-impact.json 记录 changed_layers、tasks 与链路闭环状态 | 主链/交付链收敛状态明确 |
| AC-018 | TC-018 | exception | strict 模式下 manifest 缺失 / refs 缺失 / change-impact 未闭环 | 交付就绪被阻断 |

---

## 执行检查清单

- [ ] 校验无配置/坏配置/冲突配置三类阻断路径
- [ ] 校验 workspace 多项目解析优先级
- [ ] 校验 Git 版本对齐失败与成功路径
- [ ] 校验 agent 初始化文件注入与 verify-agent-md
- [ ] 校验 `execution/config.json`、`source.json`、`git-alignment.json` 结构
- [ ] 校验 docs/beacon source + docs/product compat 镜像策略
- [ ] 校验已有 context/doctor/version contract 无回归
- [ ] 校验 brainstorm / analysis / research 统一进入 research 目录
- [ ] 校验 research 元数据与状态模型
- [ ] 校验 research → user-story / prd → test-case 收敛链路
- [ ] 校验 delivery-manifest.json 中 affected_projects 与 Git refs 完整性
- [ ] 校验 change-impact.json 的 changed_layers / tasks / convergence 状态
- [ ] 校验 strict 模式下 delivery 层缺失交付物时被阻断

---

## 建议自动化命令（规划）

| TC ID | 建议命令 | 备注 |
|------|----------|------|
| TC-001 | `python3 -m pytest -q tests/test_workspace_config_resolution.py` | 新增 strict workspace 阻断用例 |
| TC-004 | `python3 -m pytest -q tests/test_doctor_git_alignment_contract.py` | 新增 Git 对齐 contract |
| TC-005 | `python3 -m pytest -q tests/test_doctor_config_contract.py` | 新增 doctor config contract |
| TC-006 | `python3 -m pytest -q tests/test_init_context_integration.py tests/test_doctor_context_commands.py` | 复用现有上下文注入基础能力并扩展 |
| TC-011 | `python3 -m pytest -q tests/test_doctor_v2_contract.py tests/test_doctor_v2_context_checks.py tests/test_versioned_output_paths.py` | 保证旧 contract 无回归 |
| TC-012 | `python3 -m pytest -q tests/test_research_output_contract.py` | 校验 brainstorm / analyze 的 research 输出路径 |
| TC-013 | `python3 -m pytest -q tests/test_research_metadata_contract.py` | 校验 research 文档元数据与状态字段 |
| TC-014 | `python3 -m pytest -q tests/test_research_source_boundary.py` | 校验 workflow/gate 不直接消费 research |
| TC-015 | `python3 -m pytest -q tests/test_research_convergence_trace.py` | 校验 research 到主链再到 test-case 的来源链路 |
| TC-016 | `python3 -m pytest -q tests/test_delivery_manifest_contract.py` | 校验多项目/多仓库交付 manifest |
| TC-017 | `python3 -m pytest -q tests/test_execution_change_impact_contract.py` | 校验 execution/change-impact.json 结构与状态 |
| TC-018 | `python3 -m pytest -q tests/test_delivery_readiness_blocking.py` | 校验 strict 模式下交付层阻断 |
