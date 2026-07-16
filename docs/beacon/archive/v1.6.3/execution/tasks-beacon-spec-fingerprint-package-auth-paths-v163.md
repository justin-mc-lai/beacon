# Beacon Implementation Tasks Ledger

- feature: `beacon-spec-fingerprint-package-auth-paths-v163`
- version: `v1.6.3`
- plan_id: `plan-beacon-spec-fingerprint-package-auth-paths-v163-r1`
- revision_id: `R1`
- progress: `7/7`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/archive/v1.6.3/.machine/execution/implementation-plan-beacon-spec-fingerprint-package-auth-paths-v163.progress.json`
- canonical_plan_json: `docs/beacon/archive/v1.6.3/.machine/execution/implementation-plan-beacon-spec-fingerprint-package-auth-paths-v163.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 ≥v1.5.2 包 fingerprint user_story 层 count>0（扫 features/<slug>/truth.md...
  - tests=TEST-001,TC-SF-001
[x] `ITASK-002` AC-002 ≥v1.5.2 包 fingerprint prd 层 count>0（**Must**）
  - tests=TEST-002,TC-SF-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 改 truth.md 后 fingerprint hash 改变（spec drift 检测对 truth 有效）（**Must**）
  - tests=TEST-003,TC-SF-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 <v1.5.2 `_find_layer_files` 行为不变（**Must**）
  - tests=TEST-004,TC-SF-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 test_case 层仍扫 `.machine/qa/*.ac-test-matrix.json`（**Must**）
  - tests=TEST-005,TC-SF-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 v1.6.3 release gate 修复后仍 pass（fingerprint 重生成后 expected=actual）（**Mus...
  - tests=TEST-006,TC-SF-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 v1.6.2 fingerprint 行为不变（**Must**）
  - tests=TEST-007,TC-SF-007 | depends_on=ITASK-006
