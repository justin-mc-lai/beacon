---
slug: drift-padding-review-gate-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: drift-padding-review-gate-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-REV-001: detector 至少覆盖 intent drift、scope drift、orphan、duplicate、padding、evide... · ac=AC-REV-001 · evidence=`.beacon/evidence/implement/drift-padding-review-gate-v1611/AC-REV-001.json`
- [ ] TASK-002 Implement AC-REV-002: 任一 mandatory finding 使任务进入 drift_suspected→awaiting_human，停止自动执行 · ac=AC-REV-002 · evidence=`.beacon/evidence/implement/drift-padding-review-gate-v1611/AC-REV-002.json`
- [ ] TASK-003 Implement AC-REV-003: 人工选择限定为 continue/rewrite/split/replace/cancel，并保留 rationale/actor/time · ac=AC-REV-003 · evidence=`.beacon/evidence/implement/drift-padding-review-gate-v1611/AC-REV-003.json`
- [ ] TASK-004 Implement AC-REV-004: 无 decision_ref 时不得从 awaiting_human 返回 running/proposed 或进入 cancelled · ac=AC-REV-004 · evidence=`.beacon/evidence/implement/drift-padding-review-gate-v1611/AC-REV-004.json`
- [ ] TASK-005 Implement AC-REV-005: host hook、context monitor 与 subagent finding 只能提供 advisory signal，不能自... · ac=AC-REV-005 · evidence=`.beacon/evidence/implement/drift-padding-review-gate-v1611/AC-REV-005.json`
- [ ] TASK-006 Implement AC-REV-006: 强门与五类人工选择必须由 Beacon canonical policy 持久化并校验 decision_ref；只有 parent/Go... · ac=AC-REV-006 · evidence=`.beacon/evidence/implement/drift-padding-review-gate-v1611/AC-REV-006.json`
- [ ] TASK-007 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/drift-padding-review-gate-v1611/GATES.json`
- [ ] TASK-008 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/drift-padding-review-gate-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
