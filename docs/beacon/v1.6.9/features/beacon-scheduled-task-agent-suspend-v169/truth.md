---
slug: beacon-scheduled-task-agent-suspend-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO 2026-07-20: UD全接受方案A Project Scheduled Task + agent suspend + 执行日志; dual v1.6.9"
canonical_refs:
  truth: docs/beacon/v1.6.9/features/beacon-scheduled-task-agent-suspend-v169/truth.md
  tests: docs/beacon/v1.6.9/features/beacon-scheduled-task-agent-suspend-v169/tests.md
  tasks: docs/beacon/v1.6.9/features/beacon-scheduled-task-agent-suspend-v169/tasks.md
  evidence: docs/beacon/v1.6.9/features/beacon-scheduled-task-agent-suspend-v169/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
ux_required: false
design_deferral: "No product UI; CLI + project ledger"
plan_ref: docs/beacon/v1.6.9/research/beacon-scheduled-task-agent-suspend-pln-program.md
---

## 人话

项目内定时任务账本 + OS thin wake + 多 agent 执行/挂起 + **每次执行可审计日志**；不新增 public skill；不 auto-release。

# Requirement Truth: Project Scheduled Task + Agent Suspend + Execution Log

## Intent

在项目 `.beacon/tasks/` 维护 **ScheduledTask** 账本；用系统定时（opt-in）仅 thin wake；`beacon task wake` 派发 multi-host agent；支持 suspend/resume；**每次 fire/wake 写入执行日志**（execution record + events.jsonl）。双轨：v1.6.9 Python 主实现，v2.0.0/Loom 同义合同与 parity 文档。

## UD（用户全接受推荐 + 日志强化）

| ID | Value |
|----|-------|
| UD-ST-001 | 公开入口 = CLI `beacon task`（loom: `loom task` 文档同义）；**不**新增 host-visible skill |
| UD-ST-002 | 权威存储 = 项目 `.beacon/tasks/<task_id>/` |
| UD-ST-003 | OS 仅 thin wake：`beacon task wake --task-id <id> --once`；install-timer 需 `--confirm` |
| UD-ST-004 | 永不默认 daemon |
| UD-ST-005 | 永不 auto-release |
| UD-ST-006 | kind 含 implement 写路径时须 workspace admit；否则 fail-closed / readonly |
| UD-ST-007 | host_interrupt / budget / blocker≥3 → suspended；waiting_human 独立态 |
| UD-ST-008 | wake 遇 suspended 默认 `skip_until_resume`（可配 `auto_resume_on_wake`） |
| UD-ST-009 | v1.6.9 先实现；v2.0.0 合同与 CLI 文档 parity |
| **UD-ST-010** | **每次 wake/fire 必须落盘执行日志**：`executions/<exec_id>.json` + append `events.jsonl`；list-logs 可查询 |

## Schema (normative)

`scheduled-task.v1` 字段见 plan research；执行日志 schema:

```json
{
  "schema": "scheduled-task-execution.v1",
  "exec_id": "ex-…",
  "task_id": "st-…",
  "started_at": "ISO-8601",
  "ended_at": "ISO-8601|null",
  "trigger": "wake|timer|manual",
  "host": "codex|claude|bridge|none|dry_run",
  "status": "running|succeeded|failed|skipped|suspended",
  "reason_code": "",
  "agent_exit_code": null,
  "stdout_ref": "relative path or inline truncated",
  "resume_pack_ref": "",
  "goal_run_id": ""
}
```

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-ST-001 | create 后 list/get 可见且落盘 `.beacon/tasks/<id>/task.json` |
| AC-ST-002 | wake --once 无 OS timer 可执行一轮 |
| AC-ST-003 | running→suspended 写 reason_code + resume 字段 |
| AC-ST-004 | resume 后可再 wake；events append-only |
| AC-ST-005 | install-timer 无 --confirm 不改系统 |
| AC-ST-006 | uninstall-timer 后 timer 移除；账本仍在 |
| AC-ST-007 | 无路径 auto-release |
| AC-ST-008 | 不新增 public skill 到 host whitelist |
| AC-ST-009 | host=codex|claude|bridge|dry_run 可创建；dry_run wake 不 spawn 真 agent |
| AC-ST-010 | **每次 wake 产生 execution 记录；task log / executions list 可读** |
| AC-ST-011 | suspended 默认 skip_until_resume；auto_resume_on_wake 可选 |
| AC-ST-012 | 双轨 feature 包 v169 + v200 |

## Non-goals

- 默认 launchd 常驻 / 第二公共编排 skill
- 复活 `beacon automation` 业务面
- 自动 human release
- 完整 RecurringJob 云队列

## Runtime (v1.6.9)

- `beacon/utils/scheduled_task.py`
- `beacon/commands/task.py`
- CLI factory: `beacon task …`

## Parity (v2.0.0)

- 同 UD/AC；文档与测试契约；Python shim 可先服务 `loom task` 别名文档
