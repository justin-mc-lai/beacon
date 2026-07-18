---
slug: beacon-goal-agent-driver-v167
version: v1.6.7
status: support_advisory
authority: beacon-pln-review
kind: planner_review
proposed_lake: beacon-goal-agent-driver-v167
depends_on: beacon-goal-durable-supervisor-v167
user_intent: "auto re-launch agent Driver without typing 继续; also sync to v2 truth"
---

# Planner Review: v1.6.7 AgentDriver（自动再拉起 agent）

## architecture

v1.6.7 已有 **Durable Supervisor 底座**（心跳/JSONL/checkpoint/resume-pack/tick --execute）。  
缺的是 **AgentDriver**：在 host turn 结束后 **自动 requeue 下一轮 agent**，用户不必每轮打「继续」。

```text
beacon goal run "..." --longrun
        │
        ▼
GoalRun ledger + SupervisorSession (已有)
        │
        ▼
┌──── AgentDriver (本 lake 新增，Python v1.6.7) ────┐
│  while not terminal:                               │
│    pack = resume-pack digest                       │
│    spawn host agent turn (codex/claude/bridge)     │
│    wait exit / timeout                             │
│    heartbeat + checkpoint                          │
│    if budget/blocker/release_pending: halt         │
│    else requeue                                    │
└────────────────────────────────────────────────────┘
```

### 与已有能力关系

| 已有 (durable-supervisor) | Driver 新增 |
|---------------------------|-------------|
| 磁盘状态、stall 检测 | 读状态后 **真的 spawn 下一轮** |
| resume-pack 输出 digest | **注入**到 agent stdin/prompt 文件 |
| tick --execute 计划派工 | 在 turn 内执行；Driver 负责 turn 循环 |
| supervise --once | Driver 可内部调 supervise_once |

## business flow

1. 用户：`beacon goal run "目标" --longrun` 或 `$beacon-goal`+长跑意图  
2. 创建 GoalRun；**本 run** attach supervisor + start driver  
3. Driver 写 prompt 文件 = resume-pack digest + next_action + frozen truth paths  
4. 按 `BEACON_HOST_GOAL_BRIDGE_CMD` 或内置 adapter 拉起 codex/claude CLI  
5. Turn 结束 → 解析退出码/可选 JSON 结果 → heartbeat/checkpoint  
6. 非终态 → 自动下一 turn；终态 → 停在 awaiting_verifier / blocked / release_pending  
7. 用户/CI 挂 verifier → complete；release 人工  

无 `--longrun`：行为保持现状（supervise 仍 opt-in，不自动 spawn agent）。

## state machine

**AgentDriver**（v1.6.7 落地）:

| State | Meaning |
|-------|---------|
| idle | 无 longrun |
| arming | 装载 checkpoint |
| turn_active | 子进程 agent 运行中 |
| turn_ended | 子进程退出 |
| requeue | 准备下一 turn |
| halt_budget | max_turns/token 耗尽 |
| halt_terminal | completed path / blocked≥3 / user stop / release_pending |

非法：turn_ended→completed 无 verifier；auto release；budget 耗尽却 complete。

## 技术选型（v1.6.7 怎么做 — 稳）

### 推荐：P0 Python AgentDriver（不阻塞等 Rust v2）

| 组件 | 实现 |
|------|------|
| CLI | `beacon goal run --longrun`；`beacon goal driver run\|status\|stop` |
| 循环 | `goal_agent_driver.py`：同步 loop 或后台 `subprocess`+pidfile（**opt-in 本 run**，非系统 daemon 默认） |
| Host 适配 | **Bridge 优先**：`BEACON_HOST_GOAL_BRIDGE_CMD` 模板，stdin/文件喂 prompt；退出码 0=ok |
| 内置 fallback | 可选 `codex exec` / `claude -p` 探测（失败则 bridge 必填） |
| Prompt 文件 | `.beacon/state/product-goal/<run_id>/turn-<n>.prompt.md` = resume-pack + next_action |
| 结果回写 | agent 可选写 `turn-<n>.result.json`；无则仅靠 exit + 用户/子 skill 写 heartbeat |
| 预算 | `max_agent_turns` 默认 32；`turn_timeout_sec` 默认 3600 |
| 并发 | 单 run 单 driver（锁文件）；多 lake 仍走 satellite，不并行多 driver 同 run |

### 为什么稳

- 复用 **已绿** 的 durable-supervisor 账本与测试  
- 不改 host 产品内部；只 **spawn CLI**  
- 与 loop-goal 的 `cli_agent` 语义对齐，但不引入第二公共入口  
- v2 再把同一合同迁到 Rust Spine（parity AC 已写）

### 不推荐（P0）

| 方案 | 原因 |
|------|------|
| 只改 skill 文案「请同会话 continue」 | host 不 enforce，已验证会断 |
| 系统级 launchd 默认常驻 | 与 opt-in 决策冲突；权限/多项目乱 |
| zvec 驱动 agent | 向量库不能 spawn turn |
| 去掉 verifier 假装不中断 | 假交付 |

## 推荐立项切片（v1.6.7）

**湖名**：`beacon-goal-agent-driver-v167`（依赖 `beacon-goal-durable-supervisor-v167`）

| Slice | 内容 | 优先级 |
|-------|------|--------|
| S1 | `--longrun` + Driver 状态机 + pid/lock | P0 |
| S2 | resume-pack → turn prompt 文件 | P0 |
| S3 | host bridge spawn/wait/timeout | P0 |
| S4 | auto-requeue + budget halt | P0 |
| S5 | skill 长跑意图 → longrun=true | P0 |
| S6 | 契约测试 + 非法路径 | P0 |
| S7 | 可选 codex/claude 内置 adapter | P1 |

## Route

```text
User GO
  → beacon-gen-change v1.6.7 freeze beacon-goal-agent-driver-v167
  → beacon-gen-implement
  → beacon-eval-qa
  → release human gate
并行：v2 需求真相已含 longrun 湖；实现可后于 v1 Driver 或并行 parity
```

## Findings

| ID | Sev | Finding |
|----|-----|---------|
| F-01 | P0 | v1.6.7 durable 已解决「状态不断」；「自动再拉 agent」仍缺 Driver |
| F-02 | P0 | 一键 = `run --longrun` + Driver requeue，不是无限单 turn |
| F-03 | P0 | Bridge 适配最稳；skill-only continue 不够 |
| F-04 | P1 | result.json 约定可提高闭环质量，但非第一天必须 |
| F-05 | P0 | v2 已有 `beacon-v2-goal-durable-longrun`；须 **显式 full parity 表** 对齐 AC-DGS-001..014 |

## One-line

v1.6.7 用 **Python AgentDriver + host bridge + 已有 resume-pack** 即可做到自动再拉起；v2 用 Rust Spine 同合同；都不得自证 complete。

## three-piece map / version projection truth bindings

prd_refs: `docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/truth.md`
user_story_refs: `docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/truth.md`
test_case_refs: `docs/beacon/v1.6.7/features/beacon-goal-agent-driver-v167/tests.md`
coverage_notes: AC-GAD-001..014 + legal/illegal walks; depends durable-supervisor; v2 parity longrun.
out_of_scope_notes: default system daemon; Rust Spine (v2); zvec orchestrator; second public entry.

