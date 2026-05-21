# Beacon Implementation Tasks Ledger

- feature: `markdown-first-freeze-truth-and-minimal-machine-state-contract`
- version: `v1.4.8`
- plan_id: `plan-markdown-first-freeze-truth-and-minimal-machine-state-contract-r4`
- revision_id: `R4`
- progress: `8/8`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.4.8/.machine/execution/implementation-plan-markdown-first-freeze-truth-and-minimal-machine-state-contract.progress.json`
- canonical_plan_json: `docs/beacon/v1.4.8/.machine/execution/implementation-plan-markdown-first-freeze-truth-and-minimal-machine-state-contract.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` FR-001 Beacon 必须把 Markdown 作为需求冻结唯一 truth
  - tests=TC-MDFIRST-001,TC-012,TC-013,TC-014,TC-015,TC-016,TC-017,TC-018,TC-019,TC-020,TC-MDFIRST-002
[x] `ITASK-002` FR-002 Beacon 必须提供 Markdown strict parser contract
  - tests=TC-MDFIRST-005,TC-MDFIRST-006 | depends_on=ITASK-001
[x] `ITASK-003` FR-003 Beacon 必须将冻结阶段 JSON 收缩为最小状态缓存
  - tests=TC-MDFIRST-003 | depends_on=ITASK-002
[x] `ITASK-004` FR-004 Beacon 必须禁止 fulltext machine mirrors
  - tests=TC-MDFIRST-004 | depends_on=ITASK-003
[x] `ITASK-005` FR-005 Beacon 必须保留 runtime evidence JSON
  - tests=TC-MDFIRST-010 | depends_on=ITASK-004
[x] `ITASK-006` FR-006 Beacon 必须让 gate 从 Markdown 解析 truth
  - tests=TC-MDFIRST-008,TC-MDFIRST-007 | depends_on=ITASK-005
[x] `ITASK-007` FR-007 Beacon 必须用 hash 检测 Markdown truth drift
  - tests=TC-MDFIRST-009 | depends_on=ITASK-006
[x] `ITASK-008` FR-008 Beacon 必须提供 no silent cache fallback
  - depends_on=ITASK-007
