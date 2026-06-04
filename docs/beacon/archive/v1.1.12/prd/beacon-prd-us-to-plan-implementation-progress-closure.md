# PRD: Beacon PRD/US-to-Plan Implementation Progress Closure（v1.1.12）

## 1. Problem Statement

Beacon 目前已经能从 `user-story` / `prd` / `qa/test-cases` 拉起 `implement`，也具备 branch preflight、takeover gate、frozen revision gate、summary archive 等实现保护。

但当前实现仍然偏向：

- “读文档后直接执行”
- “跑完后写 summary / writeback”
- “阶段级进度可见，任务级进度不可见”

这会带来几个具体问题：

1. `implement` 只消费 PRD/US 路径，并没有把它们编译成正式的实现计划
2. AC / TEST / PRD 段落与实现任务之间缺少稳定映射
3. 实现过程没有任务级进度模型，无法表达 `planned / in_progress / blocked / completed`
4. status / help / writeback 只能看到阶段级或结果级状态，不能看到“做到哪一项任务”
5. blocked 实现缺少可追踪、可恢复、可复用的计划工件

因此，Beacon 还不能稳定地说：

> 我已经把 PRD 和 user story 转成了可执行实现计划，并且能持续记录实现进度。

## 2. Product Principles

1. PRD / user story are compile inputs, not just prompt text
2. implementation plan is a first-class artifact
3. pre-implement gating must happen before runner execution
4. progress must be task-level, not only run-level
5. writeback must preserve traceability from AC / TEST to task IDs
6. status must expose plan progress without mixing it into unrelated workflow semantics
7. implement remains the execution surface; plan compilation is the governance surface

## 3. Goals

1. 新增 `prd-us-to-plan` 编译层，把 PRD / user-story / test-case 转成正式 implementation plan
2. 定义 implementation-plan 工件模型，至少覆盖任务、依赖、映射、状态、证据与变更文件
3. 在 `implement run` 前增加 plan preflight gate，确保 plan 与 frozen baseline 一致
4. 建立任务级 progress/status 模型，让 implement 过程可追踪、可恢复、可回放
5. 让 writeback 同时回写 story / revision / plan / status 视图
6. 让 status / help 能解释“当前正在执行哪一组实现任务”

## 4. Non-goals

1. 不把 `prd-us-to-plan` 直接变成新的对外业务执行器
2. 不替代现有 `implement` runner 体系
3. 不把 plan 编译等同于代码生成
4. 不要求一次性把所有历史版本包改造成 plan-backed
5. 不把阶段级 workflow 进度废弃掉；它仍然保留

## 5. Functional Requirements

### FR-001 PRD/US-to-Plan Compiler

新增一个编译层，输入至少包括：

- user-story
- prd
- qa/test-cases
- frozen revision state
- baseline hash / version truth

输出一个 implementation plan。

编译结果必须显式表达：

- source refs
- scope boundary
- workstreams
- tasks
- task dependencies
- task to AC mapping
- task to TEST mapping
- expected evidence refs
- status model

### FR-002 Implementation Plan Artifact

新增 machine-readable 与 human-readable 产物：

- `docs/beacon/<version>/execution/implementation-plan-<feature>.md`
- `docs/beacon/<version>/.machine/execution/implementation-plan-<feature>.json`

plan 至少应包含：

- `plan_id`
- `feature`
- `version`
- `revision_id`
- `source_refs`
- `baseline_hash`
- `plan_hash`
- `workstreams[]`
- `tasks[]`

### FR-003 Task Model

每个 task 至少应包含：

- `task_id`
- `title`
- `description`
- `mapped_story_ids`
- `mapped_ac_ids`
- `mapped_test_ids`
- `depends_on`
- `target_modules`
- `status`
- `evidence_refs`
- `changed_files`
- `blocked_reason`
- `started_at`
- `completed_at`

task status 必须至少支持：

- `draft`
- `planned`
- `in_progress`
- `blocked`
- `completed`

### FR-004 Pre-implement Plan Gate

`beacon implement run` 在 runner 解析前必须先校验：

- plan 是否存在
- plan 是否匹配当前 feature / version / revision
- plan baseline hash 是否与 frozen revision 一致
- plan 中的 source refs 是否完整
- task model 是否可解析

若不满足，必须返回结构化 blocked 结果，且不得进入真正的 runner 执行面。

### FR-005 Plan Progress Writeback

implement 执行过程中必须可以回写：

- task started
- task blocked
- task completed
- evidence refs
- changed files
- implementation notes

writeback 不能只停留在 run summary，还必须更新 plan 的 task 状态。

### FR-006 AC/TEST Traceability

plan 必须保留从需求到执行的 traceability：

- PRD section / user-story slice / AC
- TEST case / verify evidence
- implementation task

至少要做到：

- 一个 AC 可以映射到一个或多个 task
- 一个 task 可以覆盖一个或多个 TEST case
- status / writeback 可以反查到具体 task

### FR-007 Status Integration

`beacon status`、`implement status`、`help` 至少应展示：

- current plan id
- plan status
- next task
- blocked task
- completed task count
- total task count
- task-level progress summary

阶段级 workflow 进度保留，但不能取代 task-level 进度。

### FR-008 Compatibility With Existing Implement Surface

现有 `implement` runner、branch preflight、takeover gate、frozen revision gate 必须继续保留。

新增 plan gate 之后：

- 不得破坏 native-single / native-team / adapter runners
- 不得破坏现有 implement summary / technical archive
- 不得破坏现有 story / revision writeback

## 6. Suggested Output Contract

### 6.1 Implementation plan JSON

```json
{
  "schema_version": "1.0",
  "plan_id": "plan-001",
  "feature": "beacon-prd-us-to-plan-implementation-progress-closure",
  "version": "v1.1.12",
  "revision_id": "R1",
  "baseline_hash": "sha256:...",
  "plan_hash": "sha256:...",
  "status": "planned",
  "source_refs": {
    "user_story": "docs/beacon/archive/v1.1.12/user-story/....md",
    "prd": "docs/beacon/archive/v1.1.12/prd/....md",
    "test_case": "docs/beacon/archive/v1.1.12/qa/test-cases/....md"
  },
  "tasks": [
    {
      "task_id": "TASK-001",
      "title": "..."
    }
  ]
}
```

### 6.2 Plan preflight blocked output

```json
{
  "schema_version": "1.0",
  "status": "blocked",
  "blocked": true,
  "reason_code": "implementation_plan_missing",
  "expected_plan": "docs/beacon/archive/v1.1.12/.machine/execution/implementation-plan-....json",
  "recommended_command": "beacon implement plan ..."
}
```

## 7. Success Standard

这条线完成时，Beacon 应能稳定做到：

1. 从 PRD / user-story / test-case 编译出 implementation plan
2. 在 implement 开始前阻断 plan 缺失或 baseline 不一致的情况
3. 让实现过程拥有 task-level 进度，而不仅是 run-level 结果
4. 让 writeback 可反查到 AC / TEST / task 的对应关系
5. 让 status / help 能清楚说明当前实现进度与下一步任务
6. 不破坏现有 implement / workflow / gate 的主链语义

## 8. First-principles Loop

正确链路应是：

```text
user-story + prd + test-case
→ prd-us-to-plan compile
→ implementation plan
→ plan gate
→ implement execution
→ task progress writeback
→ status / review / verify
```

不是：

```text
user-story + prd
→ runner prompt
→ implementation summary only
→ task status unknown
```
