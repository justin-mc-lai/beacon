# Beacon Implementation Tasks Ledger

- feature: `beacon-freeze-integrity-drift-repair-v163`
- version: `v1.6.3`
- plan_id: `plan-beacon-freeze-integrity-drift-repair-v163-r1`
- revision_id: `R1`
- progress: `7/7`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-freeze-integrity-drift-repair-v163.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-freeze-integrity-drift-repair-v163.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 feature 包 `parser_contract` 为 resolver 声明版本（v1 或 v2）时通过；仅未知版本报 `parse...
  - tests=TC-FI-001,TC-FI-002,TC-FI-003
[x] `ITASK-002` AC-002 evidence 含 `gate_truth` 子串（路径/文件名）**不**触发 `evidence_forbidden_gate_tr...
  - tests=TC-FI-010,TC-FI-011 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 tests.md 行 Layer=integration + `pytest` command 不被 `soft_test_asserti...
  - tests=TC-FI-020,TC-FI-021 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 `evidence_authority_table_missing` 与 `evidence_invalid_authority` 的 d...
  - tests=TC-FI-030,TC-FI-031 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 已冻结 v1.6.2 feature 包修复后仍 pass validation（**Must**）
  - tests=TC-FI-040 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 已冻结的 `beacon-gate-truth-model-alignment-v163` 包修复后仍 pass validation（*...
  - tests=TC-FI-050 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 真实 forbidden field 违规（authority=source_of_truth）与真实 weak-assertion（无...
  - tests=TC-FI-060 | depends_on=ITASK-006
