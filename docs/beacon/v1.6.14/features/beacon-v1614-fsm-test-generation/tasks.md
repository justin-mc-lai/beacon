---
slug: beacon-v1614-fsm-test-generation
version: v1.6.14
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1614-fsm-test-generation

## Task Ledger

- [ ] TASK-001 Implement AC-001: 从合法 truth FSM 自动生成 legal-walk 测试用例（覆盖从 initial 到 terminal 的合法路径，可达状态全走）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-001.json`
- [ ] TASK-002 Implement AC-002: 生成的用例作为 exec-layer TC 进 tests.md（可执行、断言退出码）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-002.json`
- [ ] TASK-003 Implement AC-003: 每个到达状态生成顶点断言（vertex=验证：进入该状态即断言成功）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-003.json`
- [ ] TASK-004 Implement AC-004: illegal 转换路径不被生成（生成器排除 illegal，产出中无非法路径）。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
