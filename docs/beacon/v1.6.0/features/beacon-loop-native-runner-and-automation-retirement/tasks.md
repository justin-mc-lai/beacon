# 任务：Beacon Loop Native Runner and Automation Retirement

## 任务台账

- [x] TASK-001 从 Beacon command catalog、CLI factory、help、intent routing 和 skill routing 中移除 active `automation` surface。
- [x] TASK-002 删除或改造 `beacon/commands/automation.py`，确保旧 automation queue/job 业务不可继续执行。
- [x] TASK-003 删除或迁移 `beacon/utils/automation_*.py` 中只服务旧 automation 的业务逻辑。
- [x] TASK-004 删除或退役 `automation/jobs/`、`automation/launchd/`、`automation/beacon-automation-queue.json` 和旧 automation 文档入口。
- [x] TASK-005 新增 `packages/beacon-loop` TypeScript package，并配置独立 build/test/bin。
- [x] TASK-006 实现 `beacon-loop goal "<goal>"` CLI，且不实现 `beacon-loop lfg` alias。
- [x] TASK-007 实现 Beacon resolver adapter，启动前调用 `beacon truth-map resolve ... --json`。
- [x] TASK-008 实现 resolver blocked / missing feature package / truth gap fail-closed，并推荐 `beacon-gen-change`。
- [x] TASK-009 实现 `.beacon/loop/runs/<run-id>/` runtime package 写入。
- [x] TASK-010 实现 git clean preflight、branch/worktree isolation 和 dirty worktree 阻断。
- [x] TASK-011 实现 runner orchestrator：iteration prompt、structured output schema、notes、logs、token/iteration caps、stop condition。
- [x] TASK-012 实现 success commit、failure rollback、commit failure repair state。
- [x] TASK-013 实现 `status`、`stop`、`resume`、`review`、`import-evidence`、`doctor` 子命令。
- [x] TASK-014 实现至少 `codex` agent adapter，并保留后续 backend extension boundary。
- [x] TASK-015 实现 Beacon evidence import adapter，桥接 `beacon implement import-evidence`。
- [x] TASK-016 确保 `beacon-loop` 不输出 QA/release verdict，closure 只由 Beacon evaluator/release surfaces 裁决。
- [x] TASK-017 新增/更新 tests：automation retirement、CLI build/help、no-lfg negative、resolver integration、runner commit/rollback/resume、evidence import、doctor。
- [x] TASK-018 更新文档，明确同仓库双 CLI、单 truth、外置 loop 和 `goal` 命名。

## 边界

任务台账不是 implementation completion。只有通过 `tests.md` 覆盖矩阵、Beacon QA 和 release gate 后，才能进入 closure。
