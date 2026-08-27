# Beacon Implementation Tasks Ledger

- feature: `beacon-v1616-failure-mode-expansion`
- version: `v1.6.16`
- plan_id: `plan-beacon-v1616-failure-mode-expansion-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: cataloged 阶段：失败模式目录条目 ≥ 20（从 5 扩到 20+）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-failure-mode-expansion.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-failure-mode-expansion.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: cataloged 阶段：失败模式目录条目 ≥ 20（从 5 扩到 20+）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-001.json`
  - tests=TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: verified 阶段：每条条目带 source_ref（v1.6.13-15 真实失败记录）（来自 v1.6.13-15 真实失败记录）... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-002.json`
  - tests=TC-002,TC-ILLEGAL | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: authored 阶段：每条含完整 rubric（症状/判定/通过/拦截）：症状 / 判定规则 / 通过标准 / 拦截标准。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-003.json`
  - tests=TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: cataloged→审查：目录可作为对抗式审查翻车点输入（QA/release 前）。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/AC-004.json`
  - tests=TC-004 | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-failure-mode-expansion/QA-MATRIX.json`
  - depends_on=ITASK-005
