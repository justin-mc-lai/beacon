---
slug: beacon-goal-loopx-hybrid-v1612
version: v1.6.12
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-goal-loopx-hybrid-v1612

## Task Ledger

- [ ] TASK-001 Implement AC-001: GoalQuota.should_run 按 健康门禁→operator gate→证据等待→focus 等待→配额 顺序决策；focus... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-goal-loopx-hybrid-v1612/AC-001.json`
- [ ] TASK-002 Implement AC-002: GoalTodo 支持 claim/release/supersede/update；同一 todo 重复 claim 被拒；supers... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-goal-loopx-hybrid-v1612/AC-002.json`
- [ ] TASK-003 Implement AC-003: UserGateCard 输出 question/context/resume_action；决策缓存去重（同 decision_key ... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-goal-loopx-hybrid-v1612/AC-003.json`
- [ ] TASK-004 Implement AC-004: TurnBudget 契约包含 choose→deliver→validate→writeback→spend；交接文本超 16 行/18... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-goal-loopx-hybrid-v1612/AC-004.json`
- [ ] TASK-005 Implement AC-005: patterns/ 目录含 IP-001/002/003/013/016 模式且每条配 canary 测试；ready-score 对 未... · ac=AC-005 · evidence=`.beacon/evidence/implement/beacon-goal-loopx-hybrid-v1612/AC-005.json`
- [ ] TASK-006 Implement AC-006: 生命周期门禁相关测试（truth/freeze/implement/qa/release/admission/双轴）全绿；新模块默认关闭（... · ac=AC-006 · evidence=`.beacon/evidence/implement/beacon-goal-loopx-hybrid-v1612/AC-006.json`
- [ ] TASK-007 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-goal-loopx-hybrid-v1612/GATES.json`
- [ ] TASK-008 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-goal-loopx-hybrid-v1612/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
