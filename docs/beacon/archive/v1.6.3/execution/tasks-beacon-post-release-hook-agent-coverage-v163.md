# Beacon Implementation Tasks Ledger

- feature: `beacon-post-release-hook-agent-coverage-v163`
- version: `v1.6.3`
- plan_id: `plan-beacon-post-release-hook-agent-coverage-v163-r1`
- revision_id: `R1`
- progress: `7/7`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/archive/v1.6.3/.machine/execution/implementation-plan-beacon-post-release-hook-agent-coverage-v163.progress.json`
- canonical_plan_json: `docs/beacon/archive/v1.6.3/.machine/execution/implementation-plan-beacon-post-release-hook-agent-coverage-v163.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `_run_beacon_post_release_local_install` 的 agent 循环含 trae/claude/code...
  - tests=TEST-001,TC-HK-001
[x] `ITASK-002` AC-002 hook payload 的 `agent_surfaces` 含 5 个 agent 的 setup_status + verify_s...
  - tests=TEST-002,TC-HK-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 任一 agent verify 报 `host_visible_skills_drift` 时 hook block，reason_cod...
  - tests=TEST-003,TC-HK-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 hook 仍调 `install_global_claude_beacon_skills` + `verify_global_claude...
  - tests=TEST-004,TC-HK-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 codex/claude 的 setup/verify 行为不变（仍 force=True + strict=True）（**Must**）
  - tests=TEST-005,TC-HK-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 现有 block reason_codes（setup_failed/verify_failed）语义不变（**Must**）
  - tests=TEST-006,TC-HK-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 循环复用 agent_surface 的全 agent 常量，不新增硬编码（**Must**）
  - tests=TEST-007,TC-HK-007 | depends_on=ITASK-006
