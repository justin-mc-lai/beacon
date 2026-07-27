---
slug: cancel-replan-next-ready-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: cancel-replan-next-ready-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-RPL-001: rewrite/split/replace/cancel 分别产生 proposed replacement、superseded chi... · ac=AC-RPL-001 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-001.json`
- [ ] TASK-002 Implement AC-RPL-002: required dependency 取消后必须存在 replacement，否则下游 path=blocked · ac=AC-RPL-002 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-002.json`
- [ ] TASK-003 Implement AC-RPL-003: 每次图变更原子地重算 ready set，只调度依赖满足且 admission pass 的任务 · ac=AC-RPL-003 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-003.json`
- [ ] TASK-004 Implement AC-RPL-004: 已 verified/done 任务的有效证据在语义未失效时保留；受 refreeze 影响则标 stale · ac=AC-RPL-004 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-004.json`
- [ ] TASK-005 Implement AC-RPL-005: cancelled/superseded/blocked 不得转换为 done，Goal 聚合必须区分统计 · ac=AC-RPL-005 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-005.json`
- [ ] TASK-006 Implement AC-RPL-006: Goal scheduler 只能 dispatch 当前 ready set 中且 shared admission pass 的 im... · ac=AC-RPL-006 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-006.json`
- [ ] TASK-007 Implement AC-RPL-007: Truth refreeze 或 main reconcile 变化必须原子地使旧 graph revision、ready set 与 ... · ac=AC-RPL-007 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-007.json`
- [ ] TASK-008 Implement AC-RPL-008: Host fill/schema validation/TaskRun 遇到 timeout、retryable failure、non-... · ac=AC-RPL-008 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-008.json`
- [ ] TASK-009 Implement AC-RPL-009: ready set 为空时必须区分 `open_work_exists` 与 `no_open_work`：前者 blocked 并列出阻... · ac=AC-RPL-009 · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/AC-RPL-009.json`
- [ ] TASK-010 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/GATES.json`
- [ ] TASK-011 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/cancel-replan-next-ready-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
