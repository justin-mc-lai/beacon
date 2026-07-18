---
slug: beacon-goal-durable-supervisor-v167
version: v1.6.7
status: frozen
revision_id: R1
language: zh
change_reason: "P0 durable supervisor for product-goal: opt-in supervise, 2min heartbeat, execution.jsonl, tick-exec, host_interrupt/resume; P2 sqlite FTS memory (not zvec core)"
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
ux_required: false
design_deferral: "CLI-only durable supervisor; no product UI surface"
---

# Requirement Truth: Goal Durable Supervisor v1.6.7 (R1)

## Overview

补齐 `$beacon-goal` / Product Goal Runtime 的 **长程耐久能力**：在宿主 agent 会话中断、上下文填满、implement/QA 多小时空窗时，仍能通过 **磁盘账本 + 执行日志 + checkpoint + opt-in supervisor** 续跑到 verifier complete。

**不**削弱：

- 唯一公共入口仍是 `beacon-goal`（loop 仍 support）
- complete 仍要 verifier
- release 仍 human gate
- supervisor **不得**自证 QA/release 绿灯

## User Intent（一行）

一句话 goal 开跑后，可 opt-in 挂 supervisor；心跳与日志落盘；中断可 resume 到 last_substep；tick 可驱动 implement/qa 工人；上下文满时只注入 checkpoint 摘要。

## User Decisions（locked — 2026-07-18）

| ID | Decision | Value |
|----|----------|-------|
| UD-DGS-001 | Supervisor 启动 | **opt-in**：`beacon goal supervise --run-id <id>`（**不得**在 `goal run` 后默认常驻） |
| UD-DGS-002 | 心跳间隔 | **默认 120 秒（2 分钟）**；可配置 `heartbeat_interval_sec` ≥ 30 |
| UD-DGS-003 | P2 记忆检索 | **先 sqlite FTS**；zvec **非 P0 依赖**（P2 可选插件，非权威） |
| UD-DGS-004 | 日志路径 | `.beacon/state/product-goal/<run_id>/execution.jsonl` 追加写 |
| UD-DGS-005 | Checkpoint | `.beacon/state/product-goal/<run_id>/checkpoint.json` |
| UD-DGS-006 | tick 语义 | `beacon goal tick --execute` **可**驱动当前 stage 工人（qa/ralph）；无 `--execute` 仍只改账本（兼容） |
| UD-DGS-007 | 中断语义 | **统一** `host_interrupted` ≠ `stage_blocked`；resume → `last_substep` |
| UD-DGS-008 | 公共入口 | 不新增第二主编排；supervise 是 goal 子命令，不是 `$beacon-loop-goal` 并列入口 |
| UD-DGS-009 | complete/release | **禁止** supervisor 绕过 verifier / 人工 release |
| UD-DGS-010 | 上下文打包 | resume 只注入 digest + 路径；禁止整段 chat 当权威 |

## Public CLI surface（Must）

| 命令 | 作用 |
|------|------|
| `beacon goal supervise --run-id <id> [--interval-sec 120] [--once]` | opt-in 监督循环；默认 interval=120；`--once` 单轮巡检 |
| `beacon goal heartbeat --run-id <id> --summary "..." [--substep s]` | 写 heartbeat 到 history + execution.jsonl |
| `beacon goal checkpoint --run-id <id> --next-action "..." [--substep s]` | 更新 checkpoint pack |
| `beacon goal resume-pack --run-id <id> [--json]` | 打印/输出 resume 注入包（digest only） |
| `beacon goal tick --run-id <id> [--execute]` | 推进 stage；`--execute` 时按 stage 调工人 |
| `beacon goal status --run-id <id>` | 含 stall/last_heartbeat_at/supervisor_attached |

兼容保留：`attach-verifier` / `complete` / `delegate-ralph` 语义不因本湖变松。

## Domain Model

| Entity | Key | Precedence / notes |
|--------|-----|-------------------|
| GoalRun | run_id | 产品目标账本权威；stages/done_when/verifier |
| SupervisorSession | run_id + session_id | opt-in 附着；默认 detached |
| Heartbeat | run_id + ts | 追加；默认间隔 120s |
| ExecutionLog | run_id + seq | JSONL 追加；不可覆写 |
| Checkpoint | run_id | last_substep + next_action；resume 输入 |
| WorkerJob | run_id + stage + job_id | tick --execute / supervise 派发的 qa|ralph|none |
| MemoryIndex (P2) | run_id | **sqlite FTS** 对 summary；**非** complete 权威 |

## Domain FSM — GoalRun（durable 扩展）

编排态与业务态分离：本 FSM 描述 **目标 run 的耐久生命周期**（不是业务产品 FSM）。

| State | From | Guard | Side effects |
|-------|------|-------|--------------|
| created | — | create_goal_run | state file written |
| running | created, host_interrupted, stage_blocked (streak&lt;3) | not completed | current_stage active |
| stage_active | running | stage ∈ {plan,truth,design,implement,qa,release} | skills progressive load |
| host_interrupted | stage_active, running | host turn end **or** idle ≥ heartbeat_interval without heartbeat while stage needs work | reason_code=`host_interrupted`; last_substep frozen |
| stage_blocked | stage_active | worker fail / gate fail / truth block | reason_code set; blocked_streak++ |
| awaiting_verifier | stage_active(qa done) or tick past work stages | no verifier refs | status awaiting_verifier |
| completed | awaiting_verifier **or** running at complete_gate | verifier.present ∧ refs non-empty **or** force(dev) | completed_at; **no self-cert without refs** |
| blocked | stage_blocked | blocked_streak ≥ 3 | hard stop; human required |
| release_pending | completed path optional | release_human_gate=true | human only; not auto |

### Legal walks（至少覆盖）

1. **W-DGS-LEGAL-01**  
   `created → running → stage_active(implement) → heartbeat* → stage_active(qa) → awaiting_verifier → (verifier) → completed`

2. **W-DGS-LEGAL-02（中断续跑）**  
   `stage_active → host_interrupted → (resume-pack) → stage_active(last_substep) → … → completed`

3. **W-DGS-LEGAL-03（opt-in supervise）**  
   `running + supervise attach → SupervisorSession.active → poll/heartbeat → tick --execute(qa|ralph) → detach|complete path`

4. **W-DGS-LEGAL-04（空闲 stall）**  
   `stage_active(implement) ∧ no heartbeat ≥ 120s → host_interrupted|stall_flag → resume-pack`

### Illegal transitions（Must 有 TC）

| ID | Illegal | Why |
|----|---------|-----|
| I-DGS-001 | `host_interrupted → completed` 无 verifier | 禁止中断直通完成 |
| I-DGS-002 | `stage_blocked → completed` 无修复与 verifier | 禁止带着 blocker complete |
| I-DGS-003 | supervisor marks QA green without scorecard refs | 禁止自证 |
| I-DGS-004 | overwrite execution.jsonl (non-append) | 证据链不可篡改 |
| I-DGS-005 | `goal run` auto-starts supervise without opt-in | 违反 UD-DGS-001 |
| I-DGS-006 | resume injects full chat as sole authority | 违反 UD-DGS-010 |
| I-DGS-007 | memory FTS hit overrides scorecard/verifier | 记忆非权威 |
| I-DGS-008 | second public entry via supervise skill | 违反单入口 |

## Domain FSM — SupervisorSession

| State | From | Guard | Side effects |
|-------|------|-------|--------------|
| detached | — | default | no poll |
| active | detached | `goal supervise` | session_id; interval_sec default 120 |
| polling | active | loop tick | may emit worker jobs |
| waiting_host | polling | needs agent skill load | resume_action=load_next_skill |
| stopped | active, polling, waiting_host | user stop / run completed / blocked≥3 | clean detach |

Illegal: `detached → polling` without active; `stopped → completed` on GoalRun.

## Checkpoint pack schema（Must）

```json
{
  "schema_version": "1.0",
  "run_id": "pgr-...",
  "stage": "implement",
  "last_substep": "string",
  "next_action": "one concrete step ≤240 chars",
  "open_blockers": [{"reason_code": "...", "summary": "..."}],
  "last_heartbeat_at": "ISO-8601",
  "recent_heartbeats": [{"ts": "...", "summary": "..."}],
  "log_path": ".beacon/state/product-goal/<run_id>/execution.jsonl",
  "refs": []
}
```

`beacon goal resume-pack` **只**输出此包 + 指针，不输出完整 execution.jsonl。

## Execution log schema（Must）

每行 JSONL：

| Field | Required | Notes |
|-------|----------|-------|
| ts | yes | ISO-8601 |
| run_id | yes | |
| stage | yes | |
| event | yes | heartbeat\|cmd_start\|cmd_end\|host_interrupt\|host_resume\|blocker\|tick\|checkpoint\|supervise_attach\|supervise_detach\|worker_dispatch |
| substep | no | |
| cmd | no | |
| exit_code | no | |
| summary | yes | ≤240 chars |
| refs | no | evidence paths |
| host | no | codex\|claude\|cli |

## tick --execute 行为（Must）

| current_stage | --execute action |
|---------------|------------------|
| plan / truth | no automatic heavy worker; record only + heartbeat optional |
| design | may call design stage helper if not done |
| implement | may `delegate-ralph` / emit resume_action for host implement skill |
| qa | may invoke `beacon qa run` for targeted lake(s) **one at a time** |
| release | **never** auto human-confirm; only status |

Without `--execute`: legacy ledger-only tick.

## Context-full protocol（Must）

新宿主 turn / resume 时注入顺序：

1. utterance + done_when + current_stage  
2. last ≤5 heartbeats  
3. open_blockers  
4. checkpoint.next_action（单步）  
5. log_path / scorecard paths  

禁止：把完整 chat / 完整 JSONL 作为默认注入。

## P2 Memory（sqlite FTS）

| Item | Rule |
|------|------|
| Store | sqlite file under run dir, e.g. `memory.fts.sqlite` |
| Indexed fields | summary, stage, event, substep |
| API | optional `beacon goal memory reindex|search` |
| Authority | **support_advisory only** |
| zvec | deferred; not required |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-DGS-001 | opt-in-supervise | `goal run` 不自动 attach supervise；仅 `goal supervise` 进入 SupervisorSession.active（**Must**） |
| AC-DGS-002 | heartbeat-default | 默认 heartbeat_interval_sec=120；可配置且 ≥30（**Must**） |
| AC-DGS-003 | execution-jsonl | 每次 heartbeat/cmd/tick/supervise 事件 append execution.jsonl（**Must**） |
| AC-DGS-004 | checkpoint | checkpoint.json 含 last_substep + next_action；resume-pack 只吐 digest（**Must**） |
| AC-DGS-005 | stall-detect | stage 需工作时 idle≥interval 无 heartbeat → host_interrupted 或 stall_flag（**Must**） |
| AC-DGS-006 | interrupt-semantics | host_interrupted ≠ stage_blocked；resume 回 last_substep（**Must**） |
| AC-DGS-007 | tick-execute | `tick --execute` 在 implement/qa 可派发工人；无 flag 不派发（**Must**） |
| AC-DGS-008 | no-self-cert | supervisor/tick 不得在无 verifier refs 时 complete（**Must**） |
| AC-DGS-009 | no-auto-release | release 永不被 supervise 自动确认（**Must**） |
| AC-DGS-010 | single-entry | 文档/CLI 不把 supervise 宣传为第二公共入口（**Must**） |
| AC-DGS-011 | append-only-log | 禁止非 append 覆写 execution.jsonl（**Must**） |
| AC-DGS-012 | sqlite-fts-p2 | P2：sqlite FTS reindex/search 可选；结果非 complete 权威（**Should**） |
| AC-DGS-013 | skill-continue | beacon-goal SKILL 声明同会话续跑 + resume-pack 用法（**Must**） |
| AC-DGS-014 | legal-walk-tests | tests.md 含 ≥1 legal walk 与 ≥2 illegal 行（**Must**） |

## Alignment Surface

完成定义 = 上表 AC + Domain FSM 合法路径证据。implement 不得用「写了 docs」代替 CLI 行为与契约测试。

## Non-Goals

- 不替换 Codex/Claude 宿主模型
- 不默认常驻后台 daemon（opt-in supervise；可用 `--once` 或外部 cron 调 supervise）
- 不把 zvec 作为 P0 依赖
- 不自动 human release
- 不删除 loop-goal support 能力
- 不把记忆检索当作 QA 通过证明

## Dependencies

- `beacon-product-goal-runtime-v167`（ledger / stages / verifier）
- `beacon-loop-goal-v166`（interrupt/resume 语义对齐，非并列入口）
- `beacon-ralph-implement-boundary-v167`（implement 工人边界）
- `beacon-loop-discover-goal-finish-v167`（support 角色）

## Planner promotion

- research: `docs/beacon/v1.6.7/research/beacon-goal-durable-supervisor-v167-planner-review.md`
- user confirm: 2026-07-18 — opt-in supervise; interval 120s; P2 sqlite FTS
