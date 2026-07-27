---
slug: task-progress-ledger-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: task-progress-ledger-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-LED-001: 每个任务记录 state、attempt、started/updated 时间、executor、verification 与 evide... · ac=AC-LED-001 · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/AC-LED-001.json`
- [ ] TASK-002 Implement AC-LED-002: 每次失败、偏差、人工决定与重试都追加 feedback event，不覆盖历史 · ac=AC-LED-002 · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/AC-LED-002.json`
- [ ] TASK-003 Implement AC-LED-003: 每条 path 聚合 total/completed/blocked/cancelled/superseded/replacement/r... · ac=AC-LED-003 · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/AC-LED-003.json`
- [ ] TASK-004 Implement AC-LED-004: 聚合绑定 graph revision；图变化后旧 snapshot 标 stale 并重新计算 · ac=AC-LED-004 · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/AC-LED-004.json`
- [ ] TASK-005 Implement AC-LED-005: 每个 task/path event 绑定 Goal `run_id`、内部 L0–L8 状态、对应 Beacon 1+6 harness... · ac=AC-LED-005 · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/AC-LED-005.json`
- [ ] TASK-006 Implement AC-LED-006: lifecycle trace append 失败时 task/path 状态转换不得静默成功；必须进入 blocked 或显式 degr... · ac=AC-LED-006 · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/AC-LED-006.json`
- [ ] TASK-007 Implement AC-LED-007: scaffold、fill request/response、schema validation、canonical patch、三投影再... · ac=AC-LED-007 · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/AC-LED-007.json`
- [ ] TASK-008 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/GATES.json`
- [ ] TASK-009 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/task-progress-ledger-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
