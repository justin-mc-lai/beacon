---
slug: beacon-plan-host-subagent-voltpack-v1610
version: v1.6.10
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-plan-host-subagent-voltpack-v1610

## Task Ledger

- [x] TASK-001 Implement AC-VP-KW-001: 无关键词无 flag → spawn=false, reason=subagent_default_off · ac=AC-VP-KW-001 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-KW-001.json`
- [x] TASK-002 Implement AC-VP-KW-002: 「启用子代理」+ 架构/代码审查/全面分析 → pack-review，含 architect-reviewer 与 code-reviewer · ac=AC-VP-KW-002 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-KW-002.json`
- [x] TASK-003 Implement AC-VP-KW-003: 仅「并行」→ host_agents=false · ac=AC-VP-KW-003 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-KW-003.json`
- [x] TASK-004 Implement AC-VP-PK-001: `--pack plan-review` 安装恰好 10 角色文件到 host agents dir · ac=AC-VP-PK-001 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-PK-001.json`
- [x] TASK-005 Implement AC-VP-PK-002: 每个角色文件含 cannot_complete_goal / cannot_write_truth（或等价 HARD） · ac=AC-VP-PK-002 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-PK-002.json`
- [x] TASK-006 Implement AC-VP-PK-003: `--pack minimal` 仍可装 6 角色（兼容 v1.6.8） · ac=AC-VP-PK-003 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-PK-003.json`
- [x] TASK-007 Implement AC-VP-GT-001: pack-review gate 返回 roles 包含 core 4 · ac=AC-VP-GT-001 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-GT-001.json`
- [x] TASK-008 Implement AC-VP-GT-002: 否定词覆盖正向词 · ac=AC-VP-GT-002 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-GT-002.json`
- [x] TASK-009 Implement AC-VP-GT-003: 全局 on 无阶段词 → pack-default（search-specialist only） · ac=AC-VP-GT-003 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-GT-003.json`
- [x] TASK-010 Implement AC-VP-RD-001: verify-subagent-runtime：1+6 flat skill（任一 beacon-goal 等）可过 skill_root... · ac=AC-VP-RD-001 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-RD-001.json`
- [x] TASK-011 Implement AC-VP-BD-001: gate_on payload cannot_complete_goal=true · ac=AC-VP-BD-001 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-BD-001.json`
- [x] TASK-012 Implement AC-VP-BD-002: 无第二公共 skill 入口（仍 goal/plan） · ac=AC-VP-BD-002 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-BD-002.json`
- [x] TASK-013 Implement AC-VP-FB-001: planner-review 无 host subagent runtime → single_process_multi_reviewe... · ac=AC-VP-FB-001 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-FB-001.json`
- [x] TASK-014 Implement AC-VP-EX-001: examples 含 plan-review on 路径 · ac=AC-VP-EX-001 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-EX-001.json`
- [x] TASK-015 Implement AC-VP-DF-001: 文档/真相声明全量 VoltAgent dump 为 non-goal · ac=AC-VP-DF-001 · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/AC-VP-DF-001.json`
- [x] TASK-016 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/GATES.json`
- [x] TASK-017 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-plan-host-subagent-voltpack-v1610/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
