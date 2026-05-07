# Beacon Implementation Tasks Ledger

- feature: `beacon-v1.4.0-branch-governance-human-surface-and-implement-gate`
- version: `v1.4.0`
- plan_id: `plan-beacon-v1.4.0-branch-governance-human-surface-and-implement-gate-r1`
- revision_id: `R1`
- progress: `10/10`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.4.0/.machine/execution/implementation-plan-beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.progress.json`
- canonical_plan_json: `docs/beacon/v1.4.0/.machine/execution/implementation-plan-beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` FR-001 新能力必须采用 toolkit 并排命名，而不是新主命令
  - tests=TC-001,TC-033,TC-034,TC-035,TC-036,TC-037,TC-038,TC-039,TC-040,TC-041
[x] `ITASK-002` FR-002 人类面必须展示清楚的 branch 流程图
  - tests=TC-002,TEST-010,TEST-025,TEST-029 | depends_on=ITASK-001
[x] `ITASK-003` FR-003 人类面必须有足够清楚的 git 管理摘要
  - tests=TEST-012 | depends_on=ITASK-002
[x] `ITASK-004` FR-004 必须支持默认 workflow 与本次定制 workflow
  - tests=TC-004 | depends_on=ITASK-003
[x] `ITASK-005` FR-005 metadata/profile 必须沉淀 branch governance 最小模板字段
  - tests=TEST-020,TEST-019 | depends_on=ITASK-004
[x] `ITASK-006` FR-006 `implement` 必须在进入执行前强制消费 branch governance contract
  - tests=TEST-022,TEST-021 | depends_on=ITASK-005
[x] `ITASK-007` FR-007 合规条件满足时，必须支持直接切换到规范 branch / worktree
  - tests=TEST-011,TEST-026,TEST-007 | depends_on=ITASK-006
[x] `ITASK-008` FR-008 merge direction policy 必须正式化，并能阻断非法路径
  - tests=TEST-008,TEST-030,TEST-031,TC-003,TEST-015,TEST-017,TEST-018 | depends_on=ITASK-007
[x] `ITASK-009` FR-009 evidence contract 必须可见且可校验
  - tests=TEST-023 | depends_on=ITASK-008
[x] `ITASK-010` FR-010 关键不合规状态必须 fail-closed
  - tests=TEST-028,TEST-009,TEST-005,TEST-006,TEST-013,TEST-014,TEST-016,TEST-024,TEST-027,TEST-032 | depends_on=ITASK-009
