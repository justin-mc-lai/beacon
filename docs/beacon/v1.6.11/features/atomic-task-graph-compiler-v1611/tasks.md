---
slug: atomic-task-graph-compiler-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: atomic-task-graph-compiler-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-DAG-001: Journey/AC/FSM diff 编译为最小可独立验证的 TaskNode · ac=AC-DAG-001 · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/AC-DAG-001.json`
- [ ] TASK-002 Implement AC-DAG-002: 每 TaskNode 绑定 intent、journey、AC、code scope、verification command、evide... · ac=AC-DAG-002 · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/AC-DAG-002.json`
- [ ] TASK-003 Implement AC-DAG-003: 图必须无环；依赖未满足时任务不能进入 ready · ac=AC-DAG-003 · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/AC-DAG-003.json`
- [ ] TASK-004 Implement AC-DAG-004: 无需求落点、重复语义或只为增加数量的任务标记 orphan/padding 并阻断 · ac=AC-DAG-004 · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/AC-DAG-004.json`
- [ ] TASK-005 Implement AC-DAG-005: 图与查询/聚合接口可承载 100+ 节点，不设最低任务数 · ac=AC-DAG-005 · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/AC-DAG-005.json`
- [ ] TASK-006 Implement AC-DAG-006: 每个可委派 TaskNode 声明 `execution_mode`、`required_role`、`delegation_reason... · ac=AC-DAG-006 · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/AC-DAG-006.json`
- [ ] TASK-007 Implement AC-DAG-007: 仅显式 intent-on 才规划 host subagent；host runtime 不可用时必须记录 `single_process... · ac=AC-DAG-007 · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/AC-DAG-007.json`
- [ ] TASK-008 Implement AC-DAG-008: 每个 implementation TaskNode 必须在 dispatch 前绑定 service、shared admission ... · ac=AC-DAG-008 · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/AC-DAG-008.json`
- [ ] TASK-009 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/GATES.json`
- [ ] TASK-010 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/atomic-task-graph-compiler-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
