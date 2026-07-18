---
slug: beacon-goal-durable-supervisor-v167
version: v1.6.7
status: frozen
revision_id: R1
---

# Tasks: Goal Durable Supervisor

## P0 — CLI + runtime

- [x] TASK-DGS-01 扩展 `product_goal_runtime` / `goal_durable_supervisor`：heartbeat / checkpoint / execution.jsonl / stall（AC-DGS-002..006,011）
- [x] TASK-DGS-02 CLI：`goal supervise|heartbeat|checkpoint|resume-pack` + `tick --execute`（AC-DGS-001,007）
- [x] TASK-DGS-03 complete/release 门禁不变量回归（AC-DGS-008,009）
- [x] TASK-DGS-04 更新 `skills/beacon/beacon-goal/SKILL.md` resume-pack + supervise opt-in（AC-DGS-010,013）
- [x] TASK-DGS-05 契约测试 `tests/test_v167_goal_durable_supervisor.py`（AC-DGS-014 全表）

## P1 — supervisor poll loop

- [x] TASK-DGS-06 supervise 轮询：interval 默认 120s；可 `--once`；可 plan ralph/qa 工人
- [x] TASK-DGS-07 status 输出 stall / supervisor / resume_pack_preview（enrich_goal_status）

## P2 — sqlite FTS

- [x] TASK-DGS-08 `goal memory reindex|search` sqlite FTS；非权威（AC-DGS-012）

## Non-tasks

- zvec 集成（defer）
- 默认 daemon / launchd 安装（out of scope）
