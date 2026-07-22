---
slug: trace-lifecycle-binding-v1610
version: v1.6.10
materials_status: current
task_source: acceptance_criteria
---

# Tasks: trace-lifecycle-binding-v1610

## Task Ledger

- [ ] TASK-001 Implement AC-TRC-001: 提供 `record_lifecycle_stage_trace`（或等价）封装 `record_governed_iteration`，... · ac=AC-TRC-001 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-001.json`
- [ ] TASK-002 Implement AC-TRC-002: `beacon truth review` 在写出报告后 append ≥1 条 `gate_verdict`（或 decision）事件... · ac=AC-TRC-002 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-002.json`
- [ ] TASK-003 Implement AC-TRC-003: `beacon freeze` 成功路径 append ≥1 条事件，payload 含 status/revision 摘要（非全文） · ac=AC-TRC-003 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-003.json`
- [ ] TASK-004 Implement AC-TRC-004: 事件含 `harness`；feature 已知时含 `feature_slug`；schema 为 `agent_trace.v1` · ac=AC-TRC-004 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-004.json`
- [ ] TASK-005 Implement AC-TRC-005: goal driver turn 调用 trace 时不再 bare `except: pass`；失败写入 driver state 或... · ac=AC-TRC-005 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-005.json`
- [ ] TASK-006 Implement AC-TRC-006: payload/汇总禁止 `full_chat` 作为权威；aggregate 继续 strip full_chat · ac=AC-TRC-006 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-006.json`
- [ ] TASK-007 Implement AC-TRC-007: `qa run` 结束时 append `gate_verdict`（final status 摘要） · ac=AC-TRC-007 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-007.json`
- [ ] TASK-008 Implement AC-TRC-008: 模拟 lifecycle 后 `agent_trace_coverage` 不为 missing（至少 1 个 valid run） · ac=AC-TRC-008 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-008.json`
- [ ] TASK-009 Implement AC-TRC-009: 本 package 金样 shape：人话 + Intent Matrix + FSM 五元组 + illegal + AC + Non-... · ac=AC-TRC-009 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-009.json`
- [ ] TASK-010 Implement AC-TRC-010: 每 AC 在 tests.md 有 ≥1 TC · ac=AC-TRC-010 · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/AC-TRC-010.json`
- [ ] TASK-011 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/GATES.json`
- [ ] TASK-012 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/trace-lifecycle-binding-v1610/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
