# 任务：Beacon Loop Native Runner and Automation Retirement

## MVP 骨架（已完成，待 full parity 重新验收）

- [x] TASK-001 从 Beacon command catalog、CLI factory、help、intent routing 和 skill routing 中移除 active `automation` surface。
- [x] TASK-002 删除或改造 `beacon/commands/automation.py`，确保旧 automation queue/job 业务不可继续执行。
- [x] TASK-003 删除或迁移 `beacon/utils/automation_*.py` 中只服务旧 automation 的业务逻辑。
- [x] TASK-004 删除或退役 `automation/jobs/`、`automation/launchd/`、`automation/beacon-automation-queue.json` 和旧 automation 文档入口。
- [x] TASK-005 新增 `packages/beacon-loop` TypeScript package，并配置独立 build/test/bin。
- [x] TASK-006 实现 `beacon-loop goal "<goal>"` CLI，且不实现 `beacon-loop lfg` alias。
- [x] TASK-007 实现 Beacon resolver adapter，启动前调用 `beacon truth-map resolve ... --json`。
- [x] TASK-008 实现 resolver blocked fail-closed，并推荐 `beacon-gen-change`。
- [x] TASK-009 实现 `.beacon/loop/runs/<run-id>/` runtime package 写入（MVP 单次 iteration）。
- [x] TASK-010 实现 git clean preflight、branch/worktree isolation 和 dirty worktree 阻断。
- [x] TASK-011 MVP runner orchestrator（单次 iteration；待 Phase A 升级为真多轮）。
- [x] TASK-012 实现 success commit、failure rollback、commit failure repair state（MVP）。
- [x] TASK-013 实现 `status`、`stop`、`resume`、`review`、`import-evidence`、`doctor` 子命令（MVP stub 待加强）。
- [x] TASK-014 实现 codex agent adapter（MVP fixture 路径；待 Phase A 真多轮）。
- [x] TASK-015 实现 Beacon evidence import adapter。
- [x] TASK-016 确保 `beacon-loop` 不输出 QA/release verdict。
- [x] TASK-017 MVP tests（待扩展 TC-018..TC-035）。
- [x] TASK-018 更新文档，明确双 CLI、`goal` 命名、automation retirement。

## Phase A — Orchestrator 与真 resume/stop（AC-016..AC-021, AC-008..AC-009 加强）

- [x] TASK-019 实现 `Orchestrator` 多轮 loop（max-iterations / max-tokens / stop-when / cap_reached）。
- [x] TASK-020 实现 `notes.md` 跨轮 prompt 注入与 iteration 编号递增。
- [x] TASK-021 实现 graceful stop 与 `--force` stop（真进程/子进程中断）。
- [x] TASK-022 实现 consecutive failure limit、no-op failure、retryable hard error backoff。
- [x] TASK-023 加强 `resume`：从 repair/stop/cap 状态恢复并继续 N+1 iteration。
- [x] TASK-024 实现丰富 exit summary / `summary.md`（AC-021）。
- [x] TASK-025 codex adapter 真多轮路径（非仅 `BEACON_LOOP_TEST_AGENT_RESULT` 单次）。
- [x] TASK-026 新增 orchestrator/resume/stop/state transition tests（TC-018..TC-023, TC-034, TC-035）。

## Phase B — Run ledger 与 harness 诊断（AC-022..AC-025）

- [x] TASK-027 实现 `.beacon/loop/ledger/loop-runs.db` 与 runs 索引写入。
- [x] TASK-028 实现 `beacon-loop runs query` / `runs show` / `runs diagnose`。
- [x] TASK-029 实现 `runtime-set` / `runtime-list` / `runtime-remove`。
- [x] TASK-030 实现 `analyze` / `learn` 站外产物到 `.beacon/loop/index/`。
- [x] TASK-031 扩展 `doctor --diagnose` 分桶与 repair route。
- [x] TASK-032 ledger/runtime/diagnose tests（TC-024..TC-028）。

## Phase C — Branch modes、config、多 agent（AC-026..AC-029）

- [x] TASK-033 实现 `current-branch`、`beacon-loop/<run-id>` branch 模式与非法组合阻断。
- [x] TASK-034 实现 `~/.beacon-loop/config.yml` 加载与 CLI 覆盖。
- [x] TASK-035 实现 claude adapter（contract + integration tier）。
- [x] TASK-036 实现 `acp:<target>` adapter（contract + integration tier）。
- [x] TASK-037 branch/config/adapter tests（TC-029..TC-032）。

## Phase D — Closed-loop E2E（AC-030）

- [x] TASK-038 实现 scripted E2E：goal -> multi-iteration candidate -> import-evidence -> beacon qa run 驱动。
- [x] TASK-039 更新 `evidence.md` implementation index（仍不写 verdict）。
- [ ] TASK-040 `beacon qa run` + release gate 重新验收本 feature。

## 边界

任务台账不是 implementation completion。只有通过 `tests.md` 覆盖矩阵、Beacon QA 和 release gate 后，才能进入 closure。
