# Beacon Implementation Tasks Ledger

- feature: `beacon-v1617-layering-audit`
- version: `v1.6.17`
- plan_id: `plan-beacon-v1617-layering-audit-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: scanned 阶段：生成 beacon/utils + commands 的 import 依赖图（模块 × 依赖列表）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.17/.machine/execution/implementation-plan-beacon-v1617-layering-audit.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.17/.machine/execution/implementation-plan-beacon-v1617-layering-audit.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: scanned 阶段：生成 beacon/utils + commands 的 import 依赖图（模块 × 依赖列表）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-001.json`
  - tests=TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: sized 阶段：列出所有 >2000 行的 God Module（含行数）（含行数）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-002.json`
  - tests=TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: classified 阶段：识别越界引用（command 层 → 不应依赖的 utils）（command 层 → 不应依赖的 utils... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-003.json`
  - tests=TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: reported 阶段：产出可维护性风险判断（分层缺失/God Module 风险等级）。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-004.json`
  - tests=TC-004,TC-ILLEGAL | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/QA-MATRIX.json`
  - depends_on=ITASK-005
