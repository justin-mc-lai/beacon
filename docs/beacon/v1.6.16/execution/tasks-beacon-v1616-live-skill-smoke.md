# Beacon Implementation Tasks Ledger

- feature: `beacon-v1616-live-skill-smoke`
- version: `v1.6.16`
- plan_id: `plan-beacon-v1616-live-skill-smoke-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: executing 阶段：eval benchmark 在 local_admitted tier 下对 37 个 skill 全量执行 ... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-live-skill-smoke.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-live-skill-smoke.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: executing 阶段：eval benchmark 在 local_admitted tier 下对 37 个 skill 全量执行 ... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-001.json`
  - tests=TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: traced→passed 后：live_skill_pass 从 1/37 提升到 ≥ 30/37（真实执行通过率）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-002.json`
  - tests=TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: traced 阶段：每个执行过的 skill 落盘 host_behavior 执行 trace（含 status/reason_code... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-003.json`
  - tests=TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: failed 判定：执行结果不伪造，失败 skill 标 fail + reason_code，不折算为 pass。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-004.json`
  - tests=TC-004,TC-ILLEGAL | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/QA-MATRIX.json`
  - depends_on=ITASK-005
