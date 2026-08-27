# Beacon Implementation Tasks Ledger

- feature: `beacon-v1614-fsm-test-generation`
- version: `v1.6.14`
- plan_id: `plan-beacon-v1614-fsm-test-generation-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: 从合法 truth FSM 自动生成 legal-walk 测试用例（覆盖从 initial 到 terminal 的合法路径，可达状态全走）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.14/.machine/execution/implementation-plan-beacon-v1614-fsm-test-generation.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.14/.machine/execution/implementation-plan-beacon-v1614-fsm-test-generation.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: 从合法 truth FSM 自动生成 legal-walk 测试用例（覆盖从 initial 到 terminal 的合法路径，可达状态全走）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-001.json`
  - tests=TEST-001,TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: 生成的用例作为 exec-layer TC 进 tests.md（可执行、断言退出码）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-002.json`
  - tests=TEST-002,TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: 每个到达状态生成顶点断言（vertex=验证：进入该状态即断言成功）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-003.json`
  - tests=TEST-003,TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: illegal 转换路径不被生成（生成器排除 illegal，产出中无非法路径）。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/AC-004.json`
  - tests=TEST-004,TC-004,TC-ILLEGAL | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-test-generation/QA-MATRIX.json`
  - depends_on=ITASK-005
