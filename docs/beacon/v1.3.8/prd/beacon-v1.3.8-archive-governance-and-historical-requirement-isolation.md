# PRD: Beacon v1.3.8 Archive Governance and Historical Requirement Isolation

**Feature**: `beacon-v1.3.8-archive-governance-and-historical-requirement-isolation`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Context

- Parent line:
  - `docs/beacon/v1.3.8/prd/beacon-v1.3.8-truth-lifecycle-governance.md`
- Research anchor:
  - `docs/beacon/v1.3.8/research/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-analysis.md`

## 1. Problem

Beacon 现在已经能区分 current release line 与 historical release line，也能在 revision 级别表达 `superseded_by`，但还缺一条正式 archive governance 线。

缺口体现在：

- 历史 requirement package 仍容易继续影响当前决策
- 历史 technical archive 仍容易被误读为当前 active truth
- memory / brainstorm / implement / help / status 读取历史材料时，没有统一 archive 状态语义
- 人类没有一个显式的 `archive` 命令去执行“正式退出当前 delivery plane”的治理动作
- skill 面上也没有与之对应的 `beacon:beacon-archive` 路由面

所以问题不是“历史资料太多”，而是“历史资料没有正式退出当前生效面”，并且这个退出动作还没有正式的人类命令与 skill 承载。

## 2. Goals

### 2.1 Primary Goal

建立 machine-readable archive governance，让 Beacon 明确区分：

- active truth
- superseded truth
- archived-learnable
- archived-reference-only

### 2.2 Expected Result

本线完成后，Beacon 应满足：

1. 存在顶层 support command `beacon archive`，而不是把 archive 藏在隐式内部逻辑里。
2. 存在 `beacon:beacon-archive` skill，负责路由 `plan/apply/status/explain`。
3. 存在版本级 archive plan 和 archive index，以及 feature-level archive metadata。
4. 主要消费面在读取历史材料时能识别 archive boundary。
5. 历史 requirement 可追溯，但不再继续污染当前 implement / QA / release 路径。

## 3. Non-goals

- 不物理删除历史 requirement 文档
- 不让 archive 成为新的主生命周期 stage
- 不用 archive 替代现有 release / change / revision 机制
- 不把 archive 混入 `beacon-brainstorm` 的 read-only sidecar 边界
- 不把 archive 降级成 `toolkit` 式纯分析能力

## 4. Core Product Semantics

### 4.1 Archive Status Model

最小状态模型：

- `active`
- `superseded`
- `archived-learnable`
- `archived-reference-only`

### 4.2 Version Archive Governance

版本级至少需要：

- current version truth root
- archived version roots
- active feature set
- archived feature set
- learnable archive refs
- excluded-from-current-delivery refs

### 4.3 Human Support Surface

Beacon 必须把 archive 定位为 support command，而不是新的主生命周期 stage。

目标人类面应收敛成：

```text
primary lifecycle:
prd -> user-story -> test-case -> prototype -> implement -> qa -> release

support:
help -> status -> doctor -> archive
```

### 4.4 Archive Command Routing

最小人类子命令集：

- `beacon archive plan`
- `beacon archive apply`
- `beacon archive status`
- `beacon archive explain`

对应最小 skill 面：

- `beacon:beacon-archive`

### 4.5 Brainstorm Boundary

`beacon-brainstorm` 只负责 archive 前的策略思考、第一性原理追问、范围收敛与方案比较。

真正的归档动作与正式 archive truth 写入必须通过：

- `beacon archive ...`
- `beacon:beacon-archive`

### 4.6 Archive Consumption

下列消费面应读取 archive boundary：

- `help`
- `status`
- `brainstorm`
- `memory-friction-evolution`
- `implement`
- `gate`

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon 必须定义 machine-readable archive status model，至少包含 `active`、`superseded`、`archived-learnable`、`archived-reference-only`。 |
| FR-002 | AC-002 | Beacon 必须暴露顶层 support command `archive`，其最小子命令为 `plan/apply/status/explain`，且明确不是新的 lifecycle stage。 |
| FR-003 | AC-003 | Beacon 必须提供 `beacon:beacon-archive` skill，负责把 archive 人类命令路由到正式 archive governance 能力。 |
| FR-004 | AC-004 | Beacon 必须支持版本级 archive plan / archive index 与 feature-level archive metadata，并让 `help/status/brainstorm/memory-friction-evolution/implement/gate` 读取统一 archive boundary。 |
| FR-005 | AC-005 | `beacon-brainstorm` 必须保持 read-only pre-archive 策略边界；archive governance 必须保证历史 truth 继续可追溯，但不再默认进入当前 active delivery plane。 |

## 6. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | archive-status | Beacon 存在 machine-readable archive status model。 |
| AC-002 | support-command | Beacon 对外存在 `beacon archive plan/apply/status/explain`，并明确归属 support command，而非新 lifecycle stage。 |
| AC-003 | skill-routing | Beacon 对外存在 `beacon:beacon-archive` skill，负责 archive 命令路由。 |
| AC-004 | archive-consumption | Beacon 存在版本级 archive plan / archive index、feature-level archive metadata，且 `help` / `status` / `brainstorm` / `memory-friction-evolution` / `implement` / `gate` 能识别 archive boundary。 |
| AC-005 | boundary-and-isolation | `beacon-brainstorm` 只负责归档前策略讨论；历史 requirement 与历史 truth 可追溯，但不会继续默认进入当前 active delivery plane。 |

## 7. Freeze Deliverables

- `docs/beacon/v1.3.8/research/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-analysis.md`
- `docs/beacon/v1.3.8/prd/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`

## 8. Risks

- 如果 archive status 只存在 docs 层，不进入 machine-readable contract，LLM 仍会误读历史材料。
- 如果只做 archive contract，不提供正式 `archive` support command，人类仍无法稳定执行归档治理。
- 如果把 archive 能力塞进 `beacon-brainstorm`，会破坏 brainstorm 的 read-only 边界。
- 如果 archive governance 处理不好，容易把“可学习历史”与“已失效 truth”混在一起。

## 9. Diagram Truth Layer

### 9.1 Branch-flow

- `archive plan` 生成候选 archive plan 后，若发现历史 truth 仍被当前 delivery plane 引用，则进入 `blocked-for-isolation` 分支，不允许直接 apply。
- `archive plan` 通过后，进入 `reviewed-plan` 分支；只有 review 通过，才允许执行 `archive apply`。
- `archive apply` 执行时，若归档目标仍需被学习消费，则进入 `archived-learnable` 分支；若只允许追溯与引用，则进入 `archived-reference-only` 分支。
- 任一分支如果发现 active truth 与 archived truth 仍存在默认混读，必须回退到 `blocked-for-isolation`，直到 archive boundary 被重新明确。

### 9.2 State-machine

- `draft-plan` -> `reviewed-plan` -> `applied-archive` -> `published-index`
- `active` -> `superseded` -> `archived-learnable` / `archived-reference-only`
- `blocked-for-isolation` 是显式阻塞态，表示历史 truth 仍未从当前 active delivery plane 中退出
- `published-index` 后，消费面只能通过 archive metadata 读取历史 truth，不能再把它当作 active truth 默认参与 implement / qa / release

### 9.3 Decision-priority

1. current active delivery safety 高于 historical learnability
2. archive boundary correctness 高于 archive convenience
3. explicit archive metadata 高于 runtime 推断
4. archived-reference-only 隔离强度高于 archived-learnable

### 9.4 State Axes

- `ownership`: 当前 truth 是否仍归属于 active delivery plane
- `eligibility`: 历史 truth 是否允许继续进入 implement / qa / release 判定
- `relation`: 当前 feature 与 archived feature 是否仍存在 trace-only、learnable、or active dependency
- `visibility`: 历史 truth 面向 help/status/brainstorm 是 learnable 还是 reference-only

## 10. Release Guard

- 本 requirement line 的冻结前提是：
  - requirement clarity 无 unresolved findings
  - PRD / user-story / test-case 对 AC-001 到 AC-005 一一映射
