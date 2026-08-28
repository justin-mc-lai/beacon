# Beacon Implementation Tasks Ledger

- feature: `beacon-v1617-live-benchmark-verify`
- version: `v1.6.17`
- plan_id: `plan-beacon-v1617-live-benchmark-verify-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: materialized 阶段：34 个 live skill 的 prompt fixture 文件真实存在（非空、含 ROUTE: 行）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.17/.machine/execution/implementation-plan-beacon-v1617-live-benchmark-verify.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.17/.machine/execution/implementation-plan-beacon-v1617-live-benchmark-verify.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: materialized 阶段：34 个 live skill 的 prompt fixture 文件真实存在（非空、含 ROUTE: 行）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-001.json`
  - tests=TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: resolved 阶段：skill surface 解析修正（mode 子能力映射到主 SKILL.md）：mode 子能力（如 beac... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-002.json`
  - tests=TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: executing 阶段：`beacon eval scorecard --runner live --live-tier local_a... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-003.json`
  - tests=TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: passed 判定：live_skill_pass ≥ 30/37（真实执行），失败 skill 有真实 reason_code（不折算 ... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-004.json`
  - tests=TC-004,TC-ILLEGAL | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/QA-MATRIX.json`
  - depends_on=ITASK-005
