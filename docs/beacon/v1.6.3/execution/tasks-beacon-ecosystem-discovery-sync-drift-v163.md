# Beacon Implementation Tasks Ledger

- feature: `beacon-ecosystem-discovery-sync-drift-v163`
- version: `v1.6.3`
- plan_id: `plan-beacon-ecosystem-discovery-sync-drift-v163-r1`
- revision_id: `R1`
- progress: `7/7`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-ecosystem-discovery-sync-drift-v163.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-ecosystem-discovery-sync-drift-v163.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `manifest sync` 对 ≥v1.5.2 版本扫到 `features/<slug>/` 下的 feature 包，无需手动 a...
  - tests=TEST-001,TC-EC-001
[x] `ITASK-002` AC-002 `beacon doctor sync-materials` 后 `truth-map verify` 无 `machine_json_s...
  - tests=TEST-002,TC-EC-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 `beacon freeze` 后 `.machine` source hash 与 frozen truth 一致，`truth-map...
  - tests=TEST-003,TC-EC-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 <v1.5.2 版本 manifest sync / sync-materials 行为不变（**Must**）
  - tests=TEST-004,TC-EC-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 v1.6.2 已有 feature 包修复后仍 pass（**Must**）
  - tests=TEST-005,TC-EC-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 v1.6.3 四个已 frozen 包修复后 truth-map verify pass（**Must**）
  - tests=TEST-006,TC-EC-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 `_discover_features`（material_sync）对 ≥v1.5.2 经 manifest 正确发现 features...
  - tests=TEST-007,TC-EC-007 | depends_on=ITASK-006
