# Beacon Implementation Tasks Ledger

- feature: `service-scoped-worktree-pool-v1611`
- version: `v1.6.11`
- plan_id: `plan-service-scoped-worktree-pool-v1611-r1`
- revision_id: `R1`
- progress: `9/9`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.11/.machine/execution/implementation-plan-service-scoped-worktree-pool-v1611.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.11/.machine/execution/implementation-plan-service-scoped-worktree-pool-v1611.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` TASK-001 Implement AC-SSP-001: Rolo/multi-git governance 必须支持显式 `role=primary` root；global service b... · ac=AC-SSP-001 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-001.json`
  - tests=TEST-001
[x] `ITASK-002` TASK-002 Implement AC-SSP-002: Governance parser/render/doctor 必须保留 primary binding 顺序无关语义，metadata ... · ac=AC-SSP-002 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-002.json`
  - depends_on=ITASK-001
[x] `ITASK-003` TASK-003 Implement AC-SSP-003: Workspace pool 必须支持 `workspace-pool-v2` 或等价 schema：一个 feature parent ... · ac=AC-SSP-003 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-003.json`
  - depends_on=ITASK-002
[x] `ITASK-004` TASK-004 Implement AC-SSP-004: Implement admission 对 multi-git/nested child repo 必须为每个 participating... · ac=AC-SSP-004 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-004.json`
  - depends_on=ITASK-003
[x] `ITASK-005` TASK-005 Implement AC-SSP-005: GitScopeGraph/topology gate/write guard 必须以 explicit primary + servic... · ac=AC-SSP-005 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-005.json`
  - depends_on=ITASK-004
[x] `ITASK-006` TASK-006 Implement AC-SSP-006: Rolo v2.3.3/v2.3.4 fixture 必须验证：primary 是 `/Users/apple/Developer/Com... · ac=AC-SSP-006 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-006.json`
  - depends_on=ITASK-005
[x] `ITASK-007` TASK-007 Implement AC-SSP-007: Existing single_repo、dedicated-worktree、pooled feature-level lease 行为... · ac=AC-SSP-007 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-007.json`
  - depends_on=ITASK-006
[x] `ITASK-008` TASK-008 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/GATES.json`
  - depends_on=ITASK-007
[x] `ITASK-009` TASK-009 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/QA-MATRIX.json`
  - depends_on=ITASK-008
