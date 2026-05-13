# Beacon Implementation Tasks Ledger

- feature: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- version: `v1.4.6`
- plan_id: `plan-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces-r1`
- revision_id: `R1`
- progress: `10/10`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.4.6/.machine/execution/implementation-plan-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.progress.json`
- canonical_plan_json: `docs/beacon/v1.4.6/.machine/execution/implementation-plan-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` FR-001 Beacon 必须冻结 `Skill Anatomy v2`
  - tests=TC-ADRIFT46-001,TC-011,TC-012,TC-013,TC-014,TC-015,TC-016,TC-017,TC-018,TC-019
[x] `ITASK-002` FR-002 Beacon 必须把 anti-rationalization 提升为关键 skill 的强制内容
  - tests=TC-ADRIFT46-002,TC-ADRIFT46-003 | depends_on=ITASK-001
[x] `ITASK-003` FR-003 Beacon 必须冻结 support surface 的统一 contract boundary
  - tests=TC-ADRIFT46-010,TC-ADRIFT46-004 | depends_on=ITASK-002
[x] `ITASK-004` FR-004 Beacon 必须引入受治理的 high-risk decision challenge contract
  - tests=TC-ADRIFT46-005,TC-ADRIFT46-006,TC-ADRIFT46-008 | depends_on=ITASK-003
[x] `ITASK-005` FR-005 Beacon 必须把 decision challenge 与 evidence/state/gate 面连接起来
  - tests=TC-ADRIFT46-007 | depends_on=ITASK-004
[x] `ITASK-006` FR-006 Beacon 必须冻结 orchestration constitution
  - tests=TC-ADRIFT46-009 | depends_on=ITASK-005
[x] `ITASK-007` FR-007 Beacon 必须把关键 anti-drift contract 提升为 machine-checkable checks
  - depends_on=ITASK-006
[x] `ITASK-008` FR-008 Beacon 必须保持 philosophy-first，而不是滑向 script-first
  - depends_on=ITASK-007
[x] `ITASK-009` FR-009 Beacon 必须允许把外部开源方法蒸馏为内部 contract，而不是 runtime dependency
  - depends_on=ITASK-008
[x] `ITASK-010` FR-010 Beacon 必须让 `brainstorm -> change/prd` promotion 边界更明确
  - depends_on=ITASK-009
