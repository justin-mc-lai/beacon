# Beacon Implementation Tasks Ledger

- feature: `beacon-gate-truth-model-alignment-v163`
- version: `v1.6.3`
- plan_id: `plan-beacon-gate-truth-model-alignment-v163-r1`
- revision_id: `R1`
- progress: `7/7`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-gate-truth-model-alignment-v163.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-gate-truth-model-alignment-v163.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `check_formal_version_package_closure` 对 `≥v1.5.2` 版本不再要求 `prd/`/`use...
  - tests=TC-GT-001
[x] `ITASK-002` AC-002 `≥v1.5.2` 版本改为校验 `features/<slug>/` 下至少一个 feature 包含 `truth.md`+`test...
  - tests=TC-GT-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 `<v1.5.2` 版本（如 v1.4.10）保持原 `prd/`+`user-story/`+`qa/test-cases/` 顶层目录...
  - tests=TC-GT-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 SUMMARY/execution/boundaries/source-architecture/release 校验对所有版本保留，不因...
  - tests=TC-GT-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 `≥v1.5.2` 版本无任何 feature 包 → critical block，reason_code `feature_packa...
  - tests=TC-GT-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 v1.6.2 实测 `gate check release` 的 `formal_package_closure_missing` 不再因...
  - tests=TC-GT-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 空目录（`prd/` 存在但无 `.md`）不再使 `≥v1.5.2` 版本通过；通过需真实 feature 包（**Must**）
  - tests=TC-GT-007 | depends_on=ITASK-006
