---
slug: beacon-product-goal-runtime-v167
version: v1.6.7
status: frozen
revision_id: R2
language: zh
change_reason: "R2 - parallel subagent + progressive skill load + main-star/satellite worktree pool; host skill beacon-goal"
canonical_refs:
  truth: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/truth.md
  tests: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/tests.md
  tasks: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/tasks.md
  evidence: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json
---

# Requirement Truth: Product Goal Runtime v1.6.7 (R2)

## Overview

**Product Goal Runtime** 是跨 `truth → implement → qa → release` 的 run-until-done 完成机。

### 宿主 Skill 形态（回答「立项 skill 是啥」）

| 角色 | Host-visible skill（拟） | 现状 | 职责 |
|------|-------------------------|------|------|
| **Loop 发现** | `beacon-loop-goal`（既有，角色收窄） | 已有 | 发现/分拣/写入 goal-queue；**不**宣称产品完成 |
| **Goal 完成** | **`beacon-goal`**（新 governor/orchestrator skill） | **本 lake 立项交付** | 啃 queue 项到 done_when；渐进加载 lifecycle skills |
| Program 拆海 | `beacon-pln-program*` | 已有 | 意图→feature-graph/lakes |
| Implement 长跑 | `beacon-gen-implement` + mode ralph | 已有 | 仅实现段；可被 Goal 委托 |

**结论：对外是两个编排面（Loop vs Goal），不是把一切塞进一个 skill。**  
CLI：`beacon goal …` 与 host `$beacon-goal` 共享 state。

## User Intent（一行）

Goal 跨全生命周期跑到可验证交付；支持意图声明的并行 sub-agent；实现阶段可用主星/卫星 worktree 并行啃多个湖并合并回主星。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-PGR-001 | Goal 单位 | **产品交付单位 / lake-feature，非单次 prompt** |
| UD-PGR-002 | Done | **done_when 含 domain_fsm + evidence_chain + continuous qa** |
| UD-PGR-003 | Host parity | **对齐 create_goal/update_goal/blocked≥3** |
| UD-PGR-004 | Inner routers | **阶段路由可调 loop-goal 子步骤；Ralph 仅 implement** |
| UD-PGR-005 | Release | **release 仍 human gate** |
| UD-PGR-006 | Skill 分裂 | **`beacon-loop-goal`=发现；`beacon-goal`=完成**（两个 host skill） |
| UD-PGR-007 | 渐进加载 | **按阶段只加载当前需要的 pln/gen/eval skill，禁止一次塞满 38 skill** |
| UD-PGR-008 | Sub-agent | **用户意图或 program graph 声明 parallel 时，Goal 可 spawn 子代理** |
| UD-PGR-009 | Worktree 模式 | **两种：`single_worktree`（串行）与 `main_star_satellite_pool`（主星+卫星并行）** |
| UD-PGR-010 | 主星/卫星 | **主星持 integration 分支；每卫星一湖一 worktree；完成验后 merge 回主星** |
| UD-PGR-011 | v2 | **合同字段与 v2 Rust orchestrator / BranchContext 对齐（见 v2 program）** |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-PGR-001 | state-schema | product-goal-state.v1 含 objective/done_when/budget/status/stage_pointer/**parallel_plan**/**worktree_mode**（**Must**） |
| AC-PGR-002 | cli-surface | `beacon goal start\|status\|pause\|resume\|complete\|tick`（**Must**） |
| AC-PGR-003 | host-skill | 新增 host-visible **`beacon-goal`** skill 包（governor 编排，不自证完成）（**Must**） |
| AC-PGR-004 | dual-skill | 文档与 inventory：`beacon-loop-goal`≠`beacon-goal`；loop 不得 emit product complete（**Must**） |
| AC-PGR-005 | progressive-load | Goal 决策树按阶段加载 skill（truth→gen-truth；implement→gen-implement；qa→eval-qa…）；禁止默认全量加载（**Must**） |
| AC-PGR-006 | intent-subagent | 用户 utterance / program 含 `subagent`/`parallel`/`主星`/`卫星` 时解析为 parallel_plan（**Must**） |
| AC-PGR-007 | parallel-lakes | parallel_plan 将可并行湖分配给 satellite agents；依赖边尊重 feature-graph（**Must**） |
| AC-PGR-008 | worktree-single | `worktree_mode=single_worktree`：一 goal 一 worktree 串行阶段（**Must**） |
| AC-PGR-009 | worktree-pool | `worktree_mode=main_star_satellite_pool`：主星 integration branch + N 卫星 worktree（每湖一个）（**Must**） |
| AC-PGR-010 | merge-to-star | 卫星完成 implement 本地验证后 PR/merge 回主星；冲突 → blocked 或主星协调 agent（**Must**） |
| AC-PGR-011 | done-audit | complete 前 CLI verifier（tests/qa/domain）；禁止自述（**Must**） |
| AC-PGR-012 | blocked-audit | 同 blocker ≥3 goal turns 才 blocked（**Must**） |
| AC-PGR-013 | release-human | release_gate 永不 auto（**Must**） |
| AC-PGR-014 | v2-parity | state/parallel/worktree 字段进入 v2 schema fixture 并被 v2 program 引用（**Must**） |

## Parallel + Worktree Model

```text
Program feature-graph (lakes)
        │
        ▼
   beacon-goal (Product Goal)
        │
        ├─ progressive skill load per stage
        │
        ├─ mode: single_worktree
        │     one agent walks stages serially
        │
        └─ mode: main_star_satellite_pool
              main-star: integration branch + merge/qa/release
              satellite-i: worktree for lake-i implement (optional local qa smoke)
              merge satellite → main-star when lake AC smoke green
```

### Merge policy (Must)

- Satellite 不得直推 `truth_canonical`（main）需求真相；truth 仍在 main 写。
- Satellite 默认可写 **implement 交付分支**；merge 目标是 **main-star feature integration branch**。
- 主星负责：合入、跨湖回归、qa、release 门。

## Non-Goals

- 不在本 lake 实现完整 multi-agent 框架产品化 UI
- 不取消 harness hard gate（planner 不实现等）
- 不让 satellite 写 package truth

## Dependencies

- domain-fsm-authority（done_when）
- loop-discover-goal-finish（queue handoff）
- git-scope-graph / worktree admission（pool）
