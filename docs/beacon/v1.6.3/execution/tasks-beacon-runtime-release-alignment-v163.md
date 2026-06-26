# Beacon Implementation Tasks Ledger

- feature: `beacon-runtime-release-alignment-v163`
- version: `v1.6.3`
- plan_id: `plan-beacon-runtime-release-alignment-v163-r1`
- revision_id: `R1`
- progress: `7/7`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-runtime-release-alignment-v163.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-runtime-release-alignment-v163.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 release stage runtime≠docs target → critical block，reason_code `runti...
  - tests=TEST-001,TC-RA-001
[x] `ITASK-002` AC-002 runtime==docs 时 release gate 不因 drift block（**Must**）
  - tests=TEST-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 post-release hook payload 含 `runtime_alignment` 字段（runtime_version/do...
  - tests=TEST-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 runtime≠docs 时 hook `runtime_alignment.recommended_command` 含 `beacon...
  - tests=TEST-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 plan/truth/implement/qa stage 不因 runtime≠docs block（开发期合法）（**Must**）
  - tests=TEST-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 hook 不执行 pip install，只提示（**Must**，UD-004）
  - tests=TEST-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 P0-1 的 `_resolve_eval_version` + resolve failure fail-closed 仍生效（**Mu...
  - tests=TEST-007 | depends_on=ITASK-006
