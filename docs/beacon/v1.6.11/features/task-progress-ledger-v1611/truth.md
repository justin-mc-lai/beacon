---
slug: task-progress-ledger-v1611
version: v1.6.11
status: frozen
revision_id: R2
language: zh
domain_required: true
domain_kind: platform
package_maturity: filled
materials_status: current
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
program_ref: docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/program-manifest.md
truth_map_contract: beacon-truth-map-v1
participating_services: beacon
git_canonical_branch: main
previous_revision: R1
change_reason: "D3: append-only full-package fill transaction and projection progress"
parent_truth: docs/beacon/v1.6.11/features/atomic-task-graph-compiler-v1611/truth.md
inherited_contracts: "docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md; docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/task-progress-ledger-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/task-progress-ledger-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/task-progress-ledger-v1611/tests.md
---

# Requirement Truth: L5 Task Progress Ledger

## 人话

每个小任务和每条路径都要持续更新“做了什么、结果怎样、卡在哪里、还剩多少”，不能只报一个笼统百分比。

- 能做：记录 task state、attempt、feedback、evidence 与 path 聚合
- 不能做：用阶段完成代替任务完成，或取消后仍算完成
- 怎样算完：任一时刻都能解释总数、完成、阻塞、取消、替代和剩余

## User Intent

为详细任务清单提供路径级实时进度与反馈闭环。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
owner: GoalRun
trace_contract: agent_trace.v1
public_lifecycle: beacon_1plus6
history: append_only
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 调度任务。2. 记录尝试与反馈。3. 验证证据。4. 向上聚合到 path/lake/program。5. 展示可解释进度。

## First principles

- 进度是状态与证据的投影，不是模型估计。
- cancelled/superseded 必须与 done 分开统计。
- 聚合必须固定 graph revision，防止分母漂移。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| TaskAttempt | run_id, task_id, attempt, state, feedback, evidence_refs, lifecycle_stage, trace_refs | 单次执行 |
| PathProgress | totals, completed, blocked, cancelled, replaced, remaining | 路径聚合 |
| ProgressSnapshot | graph_revision, sequence, generated_at | 可重放快照 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-LED-01 | user | must | AC-LED-001 | covered |
| INT-LED-02 | feedback | must | AC-LED-002 | covered |
| INT-LED-03 | path | must | AC-LED-003 | covered |
| INT-LED-04 | audit | must | AC-LED-004 | covered |
| INT-LED-05 | lifecycle-trace | must | AC-LED-005 | covered |
| INT-LED-06 | fail-closed-trace | must | AC-LED-006 | covered |
| INT-LED-07 | fill-progress | must | AC-LED-007 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-LED-001 | 每个任务记录 state、attempt、started/updated 时间、executor、verification 与 evidence refs |
| AC-LED-002 | 每次失败、偏差、人工决定与重试都追加 feedback event，不覆盖历史 |
| AC-LED-003 | 每条 path 聚合 total/completed/blocked/cancelled/superseded/replacement/remaining |
| AC-LED-004 | 聚合绑定 graph revision；图变化后旧 snapshot 标 stale 并重新计算 |
| AC-LED-005 | 每个 task/path event 绑定 Goal `run_id`、内部 L0–L8 状态、对应 Beacon 1+6 harness/stage 与 `agent_trace.v1` ref；内部账本不得新增公共 lifecycle stage |
| AC-LED-006 | lifecycle trace append 失败时 task/path 状态转换不得静默成功；必须进入 blocked 或显式 degraded finding，并保留可重放失败原因 |
| AC-LED-007 | scaffold、fill request/response、schema validation、canonical patch、三投影再生成、package validation、Truth Review、human ack、freeze 的每个事务步骤都追加 transaction_id、sequence、input/output hash、status、feedback 与 reason_code；重试可回放且不得覆盖旧尝试 |

## Domain FSM TaskProgressLedger

| State | From | Guard |
|-------|------|-------|
| empty | — | no task event recorded |
| recording | empty, blocked, current, stale | valid event or correction available |
| current | recording | event sequence and trace append valid |
| blocked | recording | malformed event or trace append failure |
| stale | current | graph revision changed |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| empty | task_event | graph_current | recording | append event |
| recording | snapshot | sequence_valid | current | aggregate paths |
| recording | malformed_event | schema_invalid | blocked | reject event |
| blocked | repair_event | corrected | recording | append correction |
| current | new_event | graph_same | recording | update aggregate |
| current | graph_changed | revision_new | stale | freeze old snapshot |
| stale | rebuild | graph_current | recording | replay events |

终态：`current`。

## Illegal transitions

- `empty → current` without events
- `recording → current` with sequence gap
- stale snapshot used as current progress
- state transition acknowledged while `agent_trace.v1` append failed silently
- internal L0–L8 state exposed as a new public harness
- fill transaction 跨步骤无 sequence/hash 或重试覆盖旧失败记录

## Non-goals

- 以单一百分比替代明细。
- 删除失败或人工决策历史。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] 路径统计、Goal run 与 trace 绑定获人工确认（`user-confirmation-2026-07-27`）
