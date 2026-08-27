# Beacon Implementation Tasks Ledger

- feature: `beacon-v1616-gate-independent-judge`
- version: `v1.6.16`
- plan_id: `plan-beacon-v1616-gate-independent-judge-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: computed 阶段：coverage_rate 等关键 gate 值可由独立脚本重算（独立于系统判定逻辑）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-gate-independent-judge.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-gate-independent-judge.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: computed 阶段：coverage_rate 等关键 gate 值可由独立脚本重算（独立于系统判定逻辑）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-001.json`
  - tests=TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: compared 阶段：独立判定与系统判定比对：一致 → 标记可信；不一致 → 暴露偏差。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-002.json`
  - tests=TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: flagged 阶段：偏差记录可审计（gate/系统值/独立值/diff）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-003.json`
  - tests=TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: verified 判定：独立裁判不改变 gate 业务规则，不判 pass/fail，只核验系统值可信度。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-004.json`
  - tests=TC-004 | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/QA-MATRIX.json`
  - depends_on=ITASK-005
