---
slug: goal-closed-loop-program-parallel-subagent
version: v1.6.9
status: support_advisory
authority: beacon-plan
plan_mode: interactive
dual_track_with: v2.0.0
generated_at: 2026-07-20
user_utterance: "强化 program 湖图 → parallel_plan → subagent 在 Goal 内闭环（依赖边、merge 回主星、蒸干完成定义）；v1.6.9\\v2.0.0"
---

# Plan: Goal 内闭环 — program 湖图 → parallel_plan → subagent

## 1. 产品定位（先对齐）

| 主能力（本 plan 目标） | 非主能力（降权） |
|------------------------|------------------|
| **同一 GoalRun** 内：海/湖图 → 并行计划 → 子代理 fan-out → merge 主星 → 蒸干 done_when → verifier | 双轨多版本 `v1.6.8\v2.0.0` 运维同步（ops only） |

并行子代理服务的是 **需求蒸干到可交付**，不是「同时修两条产品线」。

## 2. 现状诊断（代码 + 合同）

### 2.1 已有零件（可用）

| 零件 | 位置 | 状态 |
|------|------|------|
| program feature-graph | `programs/*/feature-graph.json` | 合同/拓扑在 |
| `build_parallel_plan` | `product_goal_runtime` | **只产 JSON 计划** |
| host subagent gate | `host_subagent_gate` | opt-in，默认不 spawn |
| loom optional subagent | `loom_subagent` | 合同强；实现偏 mkdir+spec |
| main-star-satellite | v2 truth | merge 回主星合同 |
| GoalRun done_when | create_goal_run | 粗粒度 domain_fsm/evidence… |
| longrun InjectBundle | goal_steering | 服务 **单会话续跑**，不替代湖并行 |

### 2.2 断链（闭环缺口）— P0

```text
[A] feature-graph.depends_on
        ✗ 未进入 build_parallel_plan
        ✗ 未驱动「可 fan-out 就绪集」
[B] parallel_plan
        ✗ 默认一湖一卫星目录，不读拓扑序
        ✗ 与 program 主轴 waves 不同步
[C] subagent spawn
        ✗ opt-in 后仍常是 isolation marker + worker_spec
        ✗ depends_on 校验逻辑偏「依赖是否在 lakes 列表」，不是「依赖是否已 completed」
[D] merge 回主星
        ✗ 合同有 merge_to_star；缺统一 git merge + 冲突 → stage_blocked
[E] 蒸干完成定义
        ✗ done_when 不按湖聚合
        ✗ 无 lake_done / program_done 状态机
        ✗ 子代理不能 complete GoalRun（正确）但主星也缺「全湖蒸干」自动推进
```

### 2.3 一句话现状

> **有计划、有合同、有 gate；缺「图驱动就绪调度 + 真 merge + 湖级 done」的生命周期胶水。**

## 3. 目标闭环（规范模型）

```text
GoalRun created
  → load program feature-graph (version-scoped)
  → parallel_plan.v2:
        lakes, depends_on, ready_set, waves, satellites[]
  → stage implement (or progressive stages per wave):
        while ready_set non-empty (opt-in subagent):
            spawn satellite worktrees for ready lakes only
            run agent per lake (admit leaf branch)
            on lake_pass → mark completed_lakes
            merge satellite → main_star (git)
            recompute ready_set
        if blocked_streak≥3 → stage_blocked
  → all lakes done_when satisfied → awaiting_verifier
  → verifier refs → completed
  → human release
```

### 3.1 依赖边（Must）

- 源：`programs/<slug>/feature-graph.json` 的 `depends_on` / topology_order  
- fan-out **仅** `ready = lakes whose depends_on ⊆ completed_lakes`  
- 非法：未就绪湖 spawn → `subagent_depends_on_unmet`

### 3.2 merge 回主星（Must）

- 卫星 **禁止** 写 truth_canonical  
- 完成局部验证后 **git merge** 进主星 worktree/branch  
- 冲突 → `stage_blocked` + 可恢复，不 complete

### 3.3 蒸干完成定义（Must）

| 层级 | done_when |
|------|-----------|
| **Lake** | 该 feature truth AC 有证据映射；implement 变更在主星；非法转移未破 |
| **Wave** | wave 内全部 lake done |
| **Program/Goal** | 全部拓扑湖 done + program done_when（domain_fsm / evidence_chain / continuous_qa 若适用） |
| **GoalRun complete** | 仅 verifier 引用齐全 |

子代理 **永不** 写 GoalRun.completed。

## 4. 双轨 program 建议（v1.6.9 \ v2.0.0）

同一闭环语义，两套版本线 **各自 program**（不是运维双修，是能力双轨交付）。

### 4.1 v1.6.9 — program `beacon-goal-closed-loop-parallel-v169`

| Order | Lake | 角色 |
|-------|------|------|
| 1 | `beacon-goal-graph-driven-parallel-plan-v169` | feature-graph → parallel_plan.v2（deps/ready/waves） |
| 2 | `beacon-goal-subagent-ready-set-scheduler-v169` | 就绪集调度；completed_lakes 账本 |
| 3 | `beacon-goal-satellite-merge-to-star-v169` | 真 merge + 冲突 blocked |
| 4 | `beacon-goal-lake-done-when-v169` | 湖/波次/ program 蒸干定义 + tests |
| 5 | `beacon-plan-goal-deep-integration-v169`（既有） | plan 工件接入 goal 阶段 |
| 6 | `beacon-goal-implement-admission-hard-gate-v169`（既有） | leaf admit 不破 |

### 4.2 v2.0.0 / Loom — program `beacon-goal-closed-loop-parallel-v200`（或挂现有 product-goal-parallel）

| Order | Lake | 角色 |
|-------|------|------|
| 1 | 强化 `beacon-v2-product-goal-orchestrator` | 消费 graph→plan |
| 2 | 强化 `beacon-v2-main-star-satellite-pool` | merge 合同落地 |
| 3 | 强化 `loom-goal-optional-subagent` | ready_set spawn 真执行 |
| 4 | 挂 `beacon-v2-goal-durable-longrun` | 单湖长跑 ≠ 多湖并行；边界写清 |
| 5 | axis regenerate | GoalRun 主轴挂载 |

**边界：** multi-version intent 仅 ops；本 program **不** 以 `v1.6.9\v2.0.0` 为默认 fan-out 轴。

## 5. parallel_plan.v2 建议字段

```json
{
  "schema_version": "parallel_plan.v2",
  "mode": "main_star_satellite_pool",
  "program_slug": "...",
  "depends_on": {"lake-b": ["lake-a"]},
  "topology_order": ["lake-a", "lake-b"],
  "waves": [["lake-a"], ["lake-b"]],
  "completed_lakes": [],
  "ready_lakes": ["lake-a"],
  "main_star": {"worktree": ".", "merge_policy": "satellites_merge_to_star_only"},
  "satellites": [
    {"lake": "lake-a", "worktree": ".beacon/worktrees/satellite/lake-a", "state": "planned"}
  ],
  "done_when": {
    "lake": ["ac_evidence", "merged_to_star"],
    "goal": ["all_lakes_done", "verifier"]
  }
}
```

## 6. 风险与非目标

| 非目标 | 原因 |
|--------|------|
| 默认全量 spawn | 成本与安全；保持 opt-in |
| 卫星写 truth | 破坏 canonical |
| 用 multi-version 替代湖并行 | 产品主轴错误 |
| 子代理 complete GoalRun | 假交付 |

## 7. Route recommendation

| 下一步 | 动作 |
|--------|------|
| 1 | 用户 ack 本 plan（主轴=Goal 内闭环） |
| 2 | `beacon-gen-truth` / change 开 v1.6.9 湖 1–4；v2 以 change 强化既有三湖 |
| 3 | implement：`build_parallel_plan` 读 graph；scheduler；merge helper |
| 4 | tests：deps 未满足不 spawn；merge 冲突 blocked；全湖 done→awaiting_verifier |
| 5 | **禁止** 把 multi-version 升为主 facade |

## 8. 一句话

> **强化的不是双轨修 bug，而是 GoalRun 把 program 湖图变成可调度、可合并、可蒸干的并行子代理闭环。**
