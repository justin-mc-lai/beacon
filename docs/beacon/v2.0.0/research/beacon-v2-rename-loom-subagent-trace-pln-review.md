---
slug: beacon-v2-rename-loom-subagent-trace
version: v2.0.0
status: support_advisory
authority: beacon-pln-review
kind: planner_review
date: 2026-07-18
user_intent: "v2 改名为 loom 立项审核；核实可选 subagent 并行是否已实现并对齐 omx/omc；核实 llm agent trace 排查日志"
---

# Planner Review: Rename → Loom + Subagent 并行 + Agent Trace

## intent_snapshot

| 字段 | 内容 |
|------|------|
| 改名 | 品牌/包/CLI/skill 从 Beacon 进化线 → **Loom**（织多条交付能力线） |
| Subagent | 可选加载子代理，对齐 oh-my-codex / oh-my-claude 类**并行**能力 |
| Trace | LLM agent 运行可排查的 trace/日志 |

## scope_mode

- **海级品牌 rename** + **湖级能力核实**（subagent / trace）
- 本 artifact：**立项审核 + 现状审计**；不写 truth、不改代码、不给 QA/release verdict

---

# Part A — 改名 Loom 立项审核

## 立意适配

| 旧 | 新 |
|----|-----|
| Beacon = 灯塔（单点指引） | **Loom = 织机**（多经线并行织成可交付产品） |
| 一条航线 | 多湖/多卫星/双轨安装 = **多股线** |

与 v2 Rust spine / parallel lakes / goal durable longrun **语义匹配度：高**。

## 建议命名矩阵（GO 候选）

| 面 | 生产轨（保持） | 进化/v2 轨（Loom） |
|----|----------------|---------------------|
| 品牌 | Beacon | **Loom** |
| pip | `beacon` | **`loom`**（或 `loom-ai` 防冲突） |
| CLI | `beacon` | **`loom`** |
| 公共 skill | `$beacon-goal` | **`$loom-goal`** |
| support skill | `$beacon-loop-goal` | **`$loom-loop-goal`**（support only） |
| 子 skill 前缀 | `beacon-*` | Phase-1 **共享**；Phase-2 可选 `loom-*` 镜像 |
| 状态根 | `.beacon/` / 既有 | **`.loom/` 或 `~/.loom/`**（隔离验收） |
| Docs 线 | `docs/beacon/v2.0.0` | 过渡期可保留路径；对外称 Loom v0.x/v2 |

## 与既有合同关系

| 既有锁 | 改名后怎么说 |
|--------|----------------|
| 唯一公共 facade `beacon-goal` | **生产轨**仍唯一；Loom 是**另一安装轨**的唯一 facade，不是第三哲学 |
| AC-V2-PGO-006 保持 `beacon goal` | **Must 保留**兼容；Loom 为**额外**显式轨 |
| DEF-SE-004 不默认 BEACON_V2 | 改名后仍：**不默认**用 Loom 覆盖 `beacon` |
| 并行包 `beacon-v2`（旧 research） | **升级为包名 `loom`**，比 `beacon2` 更贴品牌 |

## 立项切片建议（湖）

**推荐新海拆湖 program 名（对外）**：`loom-parallel-delivery`  
**首批湖（P0）**：

| 湖 | 内容 |
|----|------|
| `loom-brand-surface` | 包名/CLI/skill/状态根命名合同 + 双装验收矩阵 |
| （既有）`beacon-v2-product-goal-orchestrator` | R4：引用 Loom 轨命名；语义仍 goal 单入口 |
| （既有）parallel-install research | 并入 brand-surface，避免三套名（beacon2 / beacon-v2 / loom） |

## Findings — Rename

| ID | Sev | Finding |
|----|-----|---------|
| R-01 | P0 | **GO 推荐采纳 Loom** 作为 v2 进化品牌；立意优于 beacon2 |
| R-02 | P0 | 必须 **双轨并行安装**，禁止 Day-1 替换 `beacon` 包名 |
| R-03 | P0 | skill 与 CLI **成对**：`loom` + `$loom-goal`，禁止只改一边 |
| R-04 | P1 | 状态目录隔离（`.loom` / env）写进 freeze，否则并行验收污染 |
| R-05 | P1 | 仓库路径 `docs/beacon/` 可过渡保留（技术债），对外文档用 Loom |
| R-06 | P2 | 全量 `loom-gen-*` 33 skill 镜像 **延后** |

## recommended_route — Rename

```text
User GO: brand=Loom, cli=loom, skill=$loom-goal, dual-install=yes
  → beacon-gen-change v2.0.0
     湖: loom-brand-surface (+ optional merge parallel-install)
  → freeze 命名 + 双装验收矩阵 + 状态隔离
  → implement packaging（后序，非本 review）
```

**本 review 不自动改名实现。**

---

# Part B — 可选 Subagent / 并行：是否已实现？对齐 omx/omc？

## 审计结论（大白话）

| 层级 | 状态 | 说明 |
|------|------|------|
| **合同（v1.6.7 / v2 truth）** | ✅ 有 | parallel_plan、主星卫星、一湖一卫星、依赖边 |
| **Plan 数据结构** | ✅ 已实现 | `build_parallel_plan` / 意图词触发 |
| **真正 spawn 子代理跑 goal 湖** | ⚠️ **未接到 product-goal 主路径** | 只生成 plan JSON，**不**自动 tmux/codex fan-out |
| **QA / implement team** | ✅ 部分 | `spawn_tmux_workers` 用于 qa-team / implement-native |
| **对齐 oh-my-codex / oh-my-claude 级并行** | ❌ **未对齐** | 缺 host-native 多 agent 编排、自动 worktree 生命周期、持续并行交付 OS |

## 证据

### 已有（Beacon）

1. **`product_goal_runtime.build_parallel_plan`**
   - 模式：`single_worktree` | `main_star_satellite_pool`
   - 意图词：`parallel` / `subagent` / `多湖` / `卫星` / `worktree pool`
   - 输出卫星路径：`.beacon/worktrees/satellite/<lake>`
   - 合并策略：`satellites_merge_to_star_only`；卫星 `may_write_truth_on_main=false`
   - **测试**：`tests/test_v167_product_goal.py::test_main_star_satellite_pool` 绿

2. **`subagent_runtime.py`**
   - tmux session、worker spec/result JSON、team HUD
   - **调用方**：`qa.py` team、`implement_native.py` —— **不是** `beacon goal run` 主循环

3. **渐进 skill 加载**
   - `PROGRESSIVE_SKILLS` 按 stage 加载（plan/truth/implement/qa/release）
   - = 可选加载 **skill 包**，≠ 可选 spawn **子 agent 进程**

4. **Doctor**
   - `beacon doctor verify-subagent-runtime --host-runtime codex|claude`

### 缺口（相对 omx / omc / gstack）

| 能力（对标） | omx/omc/gstack 类 | Beacon 现状 |
|--------------|-------------------|-------------|
| Host 原生并行 subagent | 强（多会话/多 agent） | 弱；tmux 仅 team 面 |
| 每任务 fresh context | 强 | driver resume-pack 有；卫星未自动打包 |
| 并行写隔离 worktree | 强 | **plan 有路径，创建/合并未自动化接 goal** |
| 依赖图调度 fan-out | 中 | 合同有 depends_on；runtime **未 enforce spawn** |
| 可选开关 | 常见 | 意图/flag 有；**无「opt-in spawn」完整实现** |

### v2 合同位置

- AC-V2-PGO-004：`parallel_plan` 驱动 sub-agent（**Must**）—— **合同有，生产路径未完成**
- AC-V2-MSS-*：主星卫星 —— **合同+plan 有，执行器未闭环**

## Findings — Subagent

| ID | Sev | Finding |
|----|-----|---------|
| S-01 | P0 | **不能声称** v2/goal 已具备 omx/omc 级并行 subagent |
| S-02 | P0 | 当前是 **「并行计划 + 部分 team spawn」**，不是 **「goal 可选加载子代理全链路」** |
| S-03 | P1 | 应对齐点：worktree 创建→spec→spawn→result→merge_to_star→evidence |
| S-04 | P1 | 与 Loom 命名可同湖交付：`loom` 轨上先做 **opt-in subagent** 验收，不绑死 v1 生产 |
| S-05 | P2 | Planner-review 已诚实：无 subagent 时 `single_process_multi_reviewer` fallback |

## recommended_route — Subagent

```text
change 湖: loom-goal-optional-subagent（或 v2 main-star-satellite implement slice）
  Must:
  - beacon goal run --worktree-mode main_star_satellite_pool 真正创建 satellite worktree
  - opt-in flag: --subagent / 意图词 → spawn（tmux 或 host bridge）
  - 依赖图：未满足 depends_on 的湖不 fan-out
  - 禁止卫星写主 truth
  - 合并只回主星 + evidence
  Parity fixture vs omx/omc: 行为清单，不 1:1 抄产品
```

---

# Part C — LLM Agent Trace / 排查日志

## 审计结论

| 通道 | 路径/模块 | 用途 | Goal 长跑是否默认写 |
|------|-----------|------|---------------------|
| **agent_trace.v1** | `.beacon/traces/<run_id>.jsonl` | 结构化 decision/failure/retry/output/tool_call/gate_verdict | ⚠️ **有模块**；**goal 主路径未默认 append** |
| **execution.jsonl** | `.beacon/state/product-goal/<run_id>/execution.jsonl` | durable 心跳/tick/driver 事件 | ✅ **goal longrun/supervise 在用** |
| **checkpoint / resume-pack** | 同 run 目录 | 续跑 digest | ✅ |
| **driver.json** | 同 run 目录 | AgentDriver 状态 | ✅ longrun |
| **Codex HUD hook** | `codex_hud_hook.py` | 宿主 HUD | 可选/宿主侧 |
| **team HUD** | subagents team | 多 worker 面板 | team 面 |
| **workflow-lifecycle index** | memory | run_traces 索引 | 有 API |

## 排查怎么用（现状可用）

```bash
# Goal 长跑证据（权威进度，非完整 LLM 对话）
cat .beacon/state/product-goal/<run_id>/execution.jsonl
beacon goal resume-pack --run-id <id> --json
beacon goal status --run-id <id> --json

# 若某 harness 写了 agent_trace
ls .beacon/traces/
# 结构化事件：decision | failure | retry | output | tool_call | gate_verdict
```

## 缺口

| ID | Sev | Finding |
|----|-----|---------|
| T-01 | P0 | **Goal / Driver 轮次未强制写入 agent_trace.v1**；排 LLM 推理要用宿主日志（codex/claude session） |
| T-02 | P1 | execution.jsonl 是 **编排事件**，不是 full prompt/completion dump（设计如此，防把 chat 当权威） |
| T-03 | P1 | 缺统一 CLI：`beacon goal trace --run-id` 聚合 execution + traces + driver |
| T-04 | P2 | 与 omx 级「全程 agent 轨迹 UI」不对等 |

## recommended_route — Trace

```text
change 湖: loom-goal-trace-bundle（P1）
  - driver 每 turn 写 agent_trace: tool_call + output(exit) + failure
  - 可选 --trace-verbose 写 prompt 路径引用（不写满 chat 进权威）
  - CLI: beacon goal trace --run-id 输出聚合
  - 保持 digest resume-pack 为续跑权威
```

---

# 综合 Findings & Route

| 主题 | 结论 |
|------|------|
| 改名 Loom | **建议 GO 立项**；双轨安装；不覆盖 v1 |
| Subagent 可选并行 | **计划层有、执行层未接 goal**；**未对齐** omx/omc 全量并行 |
| Trace | **durable 日志有**；**LLM 级 agent_trace 未默认挂 goal** |

## 建议用户 GO 包（一次拍板）

1. **品牌**：v2 进化线对外 **Loom**（cli=`loom`，skill=`$loom-goal`）  
2. **安装**：与 `beacon` **并行**，不默认替换  
3. **能力缺口立项**（P0/P1）：  
   - `loom-brand-surface`  
   - `loom-goal-optional-subagent`（接 parallel_plan→spawn→merge）  
   - `loom-goal-trace-bundle`（driver↔agent_trace）  
4. **诚实对外**：当前并行 = plan + team 面；全量 subagent 为 Loom 轨交付目标  

## recommended_route（总）

```text
GO Loom 命名 + 双轨
  → gen-change: loom-brand-surface
  → gen-change: loom-goal-optional-subagent（对齐 omx/omc 行为清单，非抄壳）
  → gen-change: loom-goal-trace-bundle
  → freeze → implement → qa 双装矩阵
  → 人工 release preview wheel `loom`（不碰生产 beacon）
```

## 大白话三句

1. **改名 Loom：立意对，可以立项；要并行装，别盖掉 beacon。**  
2. **子代理并行：合同和 plan 有了，goal 还不会自动拉一窝 agent；跟 omx/omc 还差一截。**  
3. **排查日志：goal 有 execution.jsonl/心跳；完整 LLM trace 要靠宿主或以后把 agent_trace 挂上 driver。**
