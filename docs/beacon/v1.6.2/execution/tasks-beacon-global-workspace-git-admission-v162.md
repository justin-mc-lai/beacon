# Beacon Implementation Tasks Ledger

- feature: `beacon-global-workspace-git-admission-v162`
- version: `v1.6.2`
- plan_id: `plan-beacon-global-workspace-git-admission-v162-r3`
- revision_id: `R3`
- progress: `15/15`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.2/.machine/execution/implementation-plan-beacon-global-workspace-git-admission-v162.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.2/.machine/execution/implementation-plan-beacon-global-workspace-git-admission-v162.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 `beacon workspace admit` 解析 v1.6.2 → `beacon/v1.6.2/<feature>` + work...
  - tests=TEST-001
[x] `ITASK-002` AC-002 无/脏 admission → `implement run` / `qa run` blocked + stable reason_co...
  - tests=TEST-002 | depends_on=ITASK-001
[x] `ITASK-003` AC-003 Tier A host skills 含 GIT_ADMISSION Step 0；setup-agent-surface 物化一致（**...
  - tests=TEST-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 Cursor hook：missing/dirty artifact → Write deny；valid → allow（**Shoul...
  - tests=TEST-004 | depends_on=ITASK-003
[x] `ITASK-005` AC-005 Claude hook parity 同 AC-004（**Should**）
  - tests=TEST-005 | depends_on=ITASK-004
[x] `ITASK-006` AC-006 verify-agent-surface：缺 preamble **fail**；缺 hook **warn** only（**Shoul...
  - tests=TEST-006 | depends_on=ITASK-005
[x] `ITASK-007` AC-007 `TRELLIS_DISABLE_HOOKS=1` 后 Beacon admission hook 仍注册（**Should**）
  - tests=TEST-007 | depends_on=ITASK-006
[x] `ITASK-008` AC-008 governance MD v1.6.2 block + `admission_invalidation: dirty_only`（**M...
  - tests=TEST-008 | depends_on=ITASK-007
[x] `ITASK-009` AC-009 branch/head/cwd 变化 → invalid；**无 git 变化时时间流逝仍 valid**（**Must**）
  - tests=TEST-009 | depends_on=ITASK-008
[x] `ITASK-010` AC-010 `check-branch` alias + `dev-run` 先 admit；现有调用方不 break（**Must**）
  - tests=TEST-010 | depends_on=ITASK-009
[x] `ITASK-011` AC-011 `/beacon-gen-implement v1.6.2 <slug>` → Step 0 admit → worktree 再写（**...
  - tests=TEST-011 | depends_on=ITASK-010
[x] `ITASK-012` AC-012 upgrade-package 写入 release stub（**Must**，UD-013）
  - tests=TEST-012 | depends_on=ITASK-011
[x] `ITASK-013` AC-013 version-line 缺失 → upgrade-package repair（**Must**，UD-012）
  - tests=TEST-013 | depends_on=ITASK-012
[x] `ITASK-014` AC-014 blocked payload 含 repair_commands 序列（**Must**）
  - tests=TEST-014 | depends_on=ITASK-013
[x] `ITASK-015` AC-015 v1.6.2 upgrade-package 后 verify-materials strict pass（**Must**）
  - tests=TEST-015 | depends_on=ITASK-014
