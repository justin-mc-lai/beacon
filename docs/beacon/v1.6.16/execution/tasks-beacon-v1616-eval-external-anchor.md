# Beacon Implementation Tasks Ledger

- feature: `beacon-v1616-eval-external-anchor`
- version: `v1.6.16`
- plan_id: `plan-beacon-v1616-eval-external-anchor-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: collected 阶段：benchmark 案例集引入外部来源案例（真实失败案例/社区标准），不再全内置。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-eval-external-anchor.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-eval-external-anchor.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: collected 阶段：benchmark 案例集引入外部来源案例（真实失败案例/社区标准），不再全内置。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-001.json`
  - tests=TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: verified 阶段：每个外部案例带 source_ref，伪称来源被拒（可追溯来源），伪称外部来源的案例被拒。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-002.json`
  - tests=TC-002,TC-ILLEGAL | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: executed 阶段：外部案例可被 benchmark 执行（prompt + expected_route 完整）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-003.json`
  - tests=TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: registered 兼容：系统内置案例保留（回归兼容），外部案例为增量。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-004.json`
  - tests=TC-004 | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/QA-MATRIX.json`
  - depends_on=ITASK-005
