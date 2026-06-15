# Beacon Implementation Tasks Ledger

- feature: `beacon-loop-native-runner-and-automation-retirement`
- version: `v1.6.0`
- plan_id: `plan-beacon-loop-native-runner-and-automation-retirement-r2`
- revision_id: `R2`
- progress: `17/41`
- status: `blocked`
- next_task: `ITASK-001` TASK-001 从 Beacon command catalog、CLI factory、help、intent routing 和 skill routing 中移除 active `automation` surface。
- blocked_tasks: `24`

## Recovery
- progress_json: `docs/beacon/v1.6.0/.machine/execution/implementation-plan-beacon-loop-native-runner-and-automation-retirement.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.0/.machine/execution/implementation-plan-beacon-loop-native-runner-and-automation-retirement.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[-] `ITASK-001` TASK-001 从 Beacon command catalog、CLI factory、help、intent routing 和 skill routing 中移除 active `automation` surface。
  - blocked=verification_failed | tests=TEST-001,TC-001,TC-002 | next
[-] `ITASK-002` TASK-002 删除或改造 `beacon/commands/automation.py`，确保旧 automation queue/job 业务不可继续执行。
  - blocked=verification_failed | tests=TEST-002,TEST-028,TC-003 | depends_on=ITASK-001
[-] `ITASK-003` TASK-003 删除或迁移 `beacon/utils/automation_*.py` 中只服务旧 automation 的业务逻辑。
  - blocked=verification_failed | tests=TEST-003,TC-004,TC-005 | depends_on=ITASK-002
[-] `ITASK-004` TASK-004 删除或退役 `automation/jobs/`、`automation/launchd/`、`automation/beacon-automation-queue.json` 和旧 automation 文档入口。
  - blocked=verification_failed | tests=TEST-004,TC-006 | depends_on=ITASK-003
[-] `ITASK-005` TASK-005 新增 `packages/beacon-loop` TypeScript package，并配置独立 build/test/bin。
  - blocked=verification_failed | tests=TEST-013,TEST-006,TC-008,TC-015 | depends_on=ITASK-004
[-] `ITASK-006` TASK-006 实现 `beacon-loop goal "<goal>"` CLI，且不实现 `beacon-loop lfg` alias。
  - blocked=verification_failed | tests=TEST-005,TC-007 | depends_on=ITASK-005
[-] `ITASK-007` TASK-007 实现 Beacon resolver adapter，启动前调用 `beacon truth-map resolve ... --json`。
  - blocked=verification_failed | tests=TEST-030 | depends_on=ITASK-006
[-] `ITASK-008` TASK-008 实现 resolver blocked fail-closed，并推荐 `beacon-gen-change`。
  - blocked=verification_failed | tests=TEST-007,TC-009 | depends_on=ITASK-007
[-] `ITASK-009` TASK-009 实现 `.beacon/loop/runs/<run-id>/` runtime package 写入（MVP 单次 iteration）。
  - blocked=verification_failed | tests=TEST-029 | depends_on=ITASK-008
[-] `ITASK-010` TASK-010 实现 git clean preflight、branch/worktree isolation 和 dirty worktree 阻断。
  - blocked=verification_failed | tests=TEST-009,TC-011 | depends_on=ITASK-009
[-] `ITASK-011` TASK-011 MVP runner orchestrator（单次 iteration；待 Phase A 升级为真多轮）。
  - blocked=verification_failed | tests=TEST-010,TC-012 | depends_on=ITASK-010
[-] `ITASK-012` TASK-012 实现 success commit、failure rollback、commit failure repair state（MVP）。
  - blocked=verification_failed | tests=TEST-011,TEST-008,TC-010,TC-013 | depends_on=ITASK-011
[-] `ITASK-013` TASK-013 实现 `status`、`stop`、`resume`、`review`、`import-evidence`、`doctor` 子命令（MVP stub 待加强）。
  - blocked=verification_failed | tests=TEST-012,TC-014 | depends_on=ITASK-012
[-] `ITASK-014` TASK-014 实现 codex agent adapter（MVP fixture 路径；待 Phase A 真多轮）。
  - blocked=verification_failed | tests=TEST-014,TC-016 | depends_on=ITASK-013
[-] `ITASK-015` TASK-015 实现 Beacon evidence import adapter。
  - blocked=verification_failed | tests=TEST-015,TC-017 | depends_on=ITASK-014
[-] `ITASK-016` TASK-016 确保 `beacon-loop` 不输出 QA/release verdict。
  - blocked=verification_failed | tests=TEST-016 | depends_on=ITASK-015
[-] `ITASK-017` TASK-017 MVP tests（待扩展 TC-018..TC-035）。
  - blocked=verification_failed | tests=TEST-017 | depends_on=ITASK-016
[-] `ITASK-018` TASK-018 更新文档，明确双 CLI、`goal` 命名、automation retirement。
  - blocked=verification_failed | tests=TEST-018 | depends_on=ITASK-017
[-] `ITASK-019` TASK-019 实现 `Orchestrator` 多轮 loop（max-iterations / max-tokens / stop-when / cap_reached）。
  - blocked=verification_failed | tests=TEST-019 | depends_on=ITASK-018
[-] `ITASK-020` TASK-020 实现 `notes.md` 跨轮 prompt 注入与 iteration 编号递增。
  - blocked=verification_failed | tests=TEST-020 | depends_on=ITASK-019
[-] `ITASK-021` TASK-021 实现 graceful stop 与 `--force` stop（真进程/子进程中断）。
  - blocked=verification_failed | tests=TEST-021 | depends_on=ITASK-020
[-] `ITASK-022` TASK-022 实现 consecutive failure limit、no-op failure、retryable hard error backoff。
  - blocked=verification_failed | tests=TEST-022 | depends_on=ITASK-021
[-] `ITASK-023` TASK-023 加强 `resume`：从 repair/stop/cap 状态恢复并继续 N+1 iteration。
  - blocked=verification_failed | tests=TEST-023 | depends_on=ITASK-022
[-] `ITASK-024` TASK-024 实现丰富 exit summary / `summary.md`（AC-021）。
  - blocked=verification_failed | tests=TEST-024,TEST-025,TEST-026,TEST-027 | depends_on=ITASK-023
[x] `ITASK-025` TASK-025 codex adapter 真多轮路径（非仅 `BEACON_LOOP_TEST_AGENT_RESULT` 单次）。
  - depends_on=ITASK-024
[x] `ITASK-026` TASK-026 新增 orchestrator/resume/stop/state transition tests（TC-018..TC-023, TC-034, TC-035）。
  - depends_on=ITASK-025
[x] `ITASK-027` TASK-027 实现 `.beacon/loop/ledger/loop-runs.db` 与 runs 索引写入。
  - depends_on=ITASK-026
[x] `ITASK-028` TASK-028 实现 `beacon-loop runs query` / `runs show` / `runs diagnose`。
  - depends_on=ITASK-027
[x] `ITASK-029` TASK-029 实现 `runtime-set` / `runtime-list` / `runtime-remove`。
  - depends_on=ITASK-028
[x] `ITASK-030` TASK-030 实现 `analyze` / `learn` 站外产物到 `.beacon/loop/index/`。
  - depends_on=ITASK-029
[x] `ITASK-031` TASK-031 扩展 `doctor --diagnose` 分桶与 repair route。
  - depends_on=ITASK-030
[x] `ITASK-032` TASK-032 ledger/runtime/diagnose tests（TC-024..TC-028）。
  - depends_on=ITASK-031
[x] `ITASK-033` TASK-033 实现 `current-branch`、`beacon-loop/<run-id>` branch 模式与非法组合阻断。
  - depends_on=ITASK-032
[x] `ITASK-034` TASK-034 实现 `~/.beacon-loop/config.yml` 加载与 CLI 覆盖。
  - depends_on=ITASK-033
[x] `ITASK-035` TASK-035 实现 claude adapter（contract + integration tier）。
  - depends_on=ITASK-034
[x] `ITASK-036` TASK-036 实现 `acp:<target>` adapter（contract + integration tier）。
  - depends_on=ITASK-035
[x] `ITASK-037` TASK-037 branch/config/adapter tests（TC-029..TC-032）。
  - depends_on=ITASK-036
[x] `ITASK-038` TASK-038 实现 scripted E2E：goal -> multi-iteration candidate -> import-evidence -> beacon qa run 驱动。
  - depends_on=ITASK-037
[x] `ITASK-039` TASK-039 更新 `evidence.md` implementation index（仍不写 verdict）。
  - depends_on=ITASK-038
[x] `ITASK-040` TASK-040 `beacon qa run` + release gate 重新验收本 feature。
  - depends_on=ITASK-039
[x] `ITASK-041` Cleanup superseded surfaces from R1
  - depends_on=ITASK-040

## Blockers
- TASK-001 从 Beacon command catalog、CLI factory、help、intent routing 和 skill routing 中移除 active `automation` surface。
- TASK-002 删除或改造 `beacon/commands/automation.py`，确保旧 automation queue/job 业务不可继续执行。
- TASK-003 删除或迁移 `beacon/utils/automation_*.py` 中只服务旧 automation 的业务逻辑。
- TASK-004 删除或退役 `automation/jobs/`、`automation/launchd/`、`automation/beacon-automation-queue.json` 和旧 automation 文档入口。
- TASK-005 新增 `packages/beacon-loop` TypeScript package，并配置独立 build/test/bin。
- TASK-006 实现 `beacon-loop goal "<goal>"` CLI，且不实现 `beacon-loop lfg` alias。
- TASK-007 实现 Beacon resolver adapter，启动前调用 `beacon truth-map resolve ... --json`。
- TASK-008 实现 resolver blocked fail-closed，并推荐 `beacon-gen-change`。
- TASK-009 实现 `.beacon/loop/runs/<run-id>/` runtime package 写入（MVP 单次 iteration）。
- TASK-010 实现 git clean preflight、branch/worktree isolation 和 dirty worktree 阻断。
- TASK-011 MVP runner orchestrator（单次 iteration；待 Phase A 升级为真多轮）。
- TASK-012 实现 success commit、failure rollback、commit failure repair state（MVP）。
- TASK-013 实现 `status`、`stop`、`resume`、`review`、`import-evidence`、`doctor` 子命令（MVP stub 待加强）。
- TASK-014 实现 codex agent adapter（MVP fixture 路径；待 Phase A 真多轮）。
- TASK-015 实现 Beacon evidence import adapter。
- TASK-016 确保 `beacon-loop` 不输出 QA/release verdict。
- TASK-017 MVP tests（待扩展 TC-018..TC-035）。
- TASK-018 更新文档，明确双 CLI、`goal` 命名、automation retirement。
- TASK-019 实现 `Orchestrator` 多轮 loop（max-iterations / max-tokens / stop-when / cap_reached）。
- TASK-020 实现 `notes.md` 跨轮 prompt 注入与 iteration 编号递增。
- TASK-021 实现 graceful stop 与 `--force` stop（真进程/子进程中断）。
- TASK-022 实现 consecutive failure limit、no-op failure、retryable hard error backoff。
- TASK-023 加强 `resume`：从 repair/stop/cap 状态恢复并继续 N+1 iteration。
- TASK-024 实现丰富 exit summary / `summary.md`（AC-021）。
