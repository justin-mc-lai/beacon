# Beacon Implementation Tasks Ledger

- feature: `beacon-v1.4.6-implementation-first-reconciliation-governance`
- version: `v1.4.6`
- plan_id: `plan-beacon-v1.4.6-implementation-first-reconciliation-governance-r1`
- revision_id: `R1`
- progress: `0/5`
- status: `planned`
- next_task: `ITASK-001` FR-001 Beacon 必须定义 implementation-first reconciliation 为异常恢复语义
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.4.6/.machine/execution/implementation-plan-beacon-v1.4.6-implementation-first-reconciliation-governance.progress.json`
- canonical_plan_json: `docs/beacon/v1.4.6/.machine/execution/implementation-plan-beacon-v1.4.6-implementation-first-reconciliation-governance.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` FR-001 Beacon 必须定义 implementation-first reconciliation 为异常恢复语义
  - tests=TC-RECON46-001,TC-006,TC-007,TC-008,TC-009,TC-010,TC-011,TC-012,TC-013,TC-014 | next
[ ] `ITASK-002` FR-002 Reconciliation 必须通过 `beacon-change` 路由
  - tests=TC-RECON46-002 | depends_on=ITASK-001
[ ] `ITASK-003` FR-003 Beacon 必须冻结 reconciliation artifact contract
  - tests=TC-RECON46-003,TC-RECON46-004 | depends_on=ITASK-002
[ ] `ITASK-004` FR-004 补 truth 后必须重新收口受影响 proof
  - tests=TC-RECON46-005 | depends_on=ITASK-003
[ ] `ITASK-005` FR-005 Beacon 不得把 reconciliation 伪装成正常 truth-first 交付
  - depends_on=ITASK-004
