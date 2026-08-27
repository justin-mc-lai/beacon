# Beacon Implementation Tasks Ledger

- feature: `beacon-v1614-feature-map`
- version: `v1.6.14`
- plan_id: `plan-beacon-v1614-feature-map-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: 每个 feature 有 `feature-map.md` 骨架：entry_points + verification_commands... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.14/.machine/execution/implementation-plan-beacon-v1614-feature-map.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.14/.machine/execution/implementation-plan-beacon-v1614-feature-map.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: 每个 feature 有 `feature-map.md` 骨架：entry_points + verification_commands... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-001.json`
  - tests=TEST-001,TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: 复现路由：map 含 `reproduce[]`（symptom_hint → 定位 steps），模糊 bug 描述可路由到对应 ent... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-002.json`
  - tests=TEST-002,TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: agent 自验证：map 的 verification 命令可被 agent 执行（复用 code2truth 资产），输出可观测信号供断言。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-003.json`
  - tests=TEST-003,TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: 单向投影：map 引用 truth（AC），不反向改 truth；不新增命令面；AC 变化时 map 漂移可检测。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-004.json`
  - tests=TEST-004,TC-004,TC-ILLEGAL | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/QA-MATRIX.json`
  - depends_on=ITASK-005
