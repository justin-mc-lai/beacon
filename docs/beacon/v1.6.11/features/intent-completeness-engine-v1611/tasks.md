---
slug: intent-completeness-engine-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: intent-completeness-engine-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-INT-001: 引擎递归展开 actor、goal、journey、failure、state、constraint、non-goal 七类节点 · ac=AC-INT-001 · evidence=`.beacon/evidence/implement/intent-completeness-engine-v1611/AC-INT-001.json`
- [ ] TASK-002 Implement AC-INT-002: 每条 must 意图必须落到 Journey/AC/Non-goal/approved Deferral，missing 阻断 Change · ac=AC-INT-002 · evidence=`.beacon/evidence/implement/intent-completeness-engine-v1611/AC-INT-002.json`
- [ ] TASK-003 Implement AC-INT-003: 递归停止依据是语义闭合、重复或用户批准延期，不得以达到任务数量停止 · ac=AC-INT-003 · evidence=`.beacon/evidence/implement/intent-completeness-engine-v1611/AC-INT-003.json`
- [ ] TASK-004 Implement AC-INT-004: 歧义、冲突或高影响默认值必须进入人工确认，并保留 decision_ref · ac=AC-INT-004 · evidence=`.beacon/evidence/implement/intent-completeness-engine-v1611/AC-INT-004.json`
- [ ] TASK-005 Implement AC-INT-005: ContextEnvelope 中继承的 Goal owner、intent-on subagent、真实 worktree admiss... · ac=AC-INT-005 · evidence=`.beacon/evidence/implement/intent-completeness-engine-v1611/AC-INT-005.json`
- [ ] TASK-006 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/intent-completeness-engine-v1611/GATES.json`
- [ ] TASK-007 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/intent-completeness-engine-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
