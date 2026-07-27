---
slug: change-impact-state-diff-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: change-impact-state-diff-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-DIF-001: Change 输出 promise/interface/data/FSM/test 五表面 Before→After · ac=AC-DIF-001 · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/AC-DIF-001.json`
- [ ] TASK-002 Implement AC-DIF-002: FSM diff 明确 old/new states、合法边、illegal 边、超时/失败/取消恢复边 · ac=AC-DIF-002 · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/AC-DIF-002.json`
- [ ] TASK-003 Implement AC-DIF-003: 每条 diff 绑定 source intent、affected code scope 与 planned TC · ac=AC-DIF-003 · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/AC-DIF-003.json`
- [ ] TASK-004 Implement AC-DIF-004: 删除、破坏兼容或高风险状态变更必须进入 state_diff_review 人工确认 · ac=AC-DIF-004 · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/AC-DIF-004.json`
- [ ] TASK-005 Implement AC-DIF-005: Change diff 必须覆盖 public 1+6 lifecycle 映射、subagent delegation/诚实 fallb... · ac=AC-DIF-005 · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/AC-DIF-005.json`
- [ ] TASK-006 Implement AC-DIF-006: Host LLM 只能返回 `truth-fill-response.v1` 结构化领域对象/patch；CLI 依据 `truth-fi... · ac=AC-DIF-006 · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/AC-DIF-006.json`
- [ ] TASK-007 Implement AC-DIF-007: 正式 ChangePlan 必须覆盖 `GoalUtteranceCaptured → VersionAndContextResolved... · ac=AC-DIF-007 · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/AC-DIF-007.json`
- [ ] TASK-008 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/GATES.json`
- [ ] TASK-009 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/change-impact-state-diff-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
