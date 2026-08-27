# Beacon Implementation Tasks Ledger

- feature: `beacon-v1615-coverage-type-weighted`
- version: `v1.6.15`
- plan_id: `plan-beacon-v1615-coverage-type-weighted-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: `coverage_rate` 按类型族加权：required_families 缺一类 → 状态 assessed 时 rate < 1... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.15/.machine/execution/implementation-plan-beacon-v1615-coverage-type-weighted.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.15/.machine/execution/implementation-plan-beacon-v1615-coverage-type-weighted.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: `coverage_rate` 按类型族加权：required_families 缺一类 → 状态 assessed 时 rate < 1... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-001.json`
  - tests=TEST-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: 非浏览器（contract/docs/unit）场景在 weighted 阶段展开类型 family（默认 happy+negative+... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-002.json`
  - tests=TEST-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: coverage 输出在 reported 阶段列出 missing_families（缺哪类），供 QA 与自动合入门禁审计。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-003.json`
  - tests=TEST-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: 兼容既有 lake：已通过 QA 的 lake 语义不变，仅覆盖计算方式变化（gated 判定更新），不引入新命令面。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-004.json`
  - tests=TEST-004 | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/QA-MATRIX.json`
  - depends_on=ITASK-005
