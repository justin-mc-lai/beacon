# Beacon Implementation Tasks Ledger

- feature: `beacon-version-resolve-fail-closed-v163`
- version: `v1.6.3`
- plan_id: `plan-beacon-version-resolve-fail-closed-v163-r1`
- revision_id: `R1`
- progress: `7/7`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-version-resolve-fail-closed-v163.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.3/.machine/execution/implementation-plan-beacon-version-resolve-fail-closed-v163.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `project_hooks.py:543` 不再含硬编码 `v1.6.1` 字面量；改用 `resolve_target_version...
  - tests=TC-VR-001
[x] `ITASK-002` AC-002 version=`auto`/空/`latest` 时 eval_version 解析为 docs 实际版本（如 v1.6.3），非 v1...
  - tests=TC-VR-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 post-release hook payload 含 `runtime_version`/`docs_version`/`drift`...
  - tests=TC-VR-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 `resolve_target_version` 解析失败/抛异常时 hook fail-closed block，reason_code...
  - tests=TC-VR-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 `agent_eval_kit.is_live_runner_admitted` 运行时用 resolve 版本，不依赖硬编码 `AGEN...
  - tests=TC-VR-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 现有 post-release hook 在 runtime==docs（正常）场景仍 pass，不误 block（**Must**）
  - tests=TC-VR-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 runtime≠docs（双版本合法推进）时 `drift=true` 但**不** block（仅记录）（**Must**，UD-006）
  - tests=TC-VR-007 | depends_on=ITASK-006
