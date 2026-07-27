---
slug: cancel-replan-next-ready-v1611
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
change_reason: "D3: fill reject recovery, timeout/failure handling and closure-ready branch"
parent_truth: docs/beacon/v1.6.11/features/drift-padding-review-gate-v1611/truth.md
inherited_contracts: "docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md; docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md; docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/cancel-replan-next-ready-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/cancel-replan-next-ready-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/cancel-replan-next-ready-v1611/tests.md
---

# Requirement Truth: L7 Cancel, Replan and Next Ready

## 人话

人工说“不行”后，系统不能卡死，也不能假装原任务完成；它要取消或替换当前任务，重算依赖，再继续下一个真正可做的任务。

- 能做：cancel/supersede/replacement、依赖传播、ready set 重算
- 不能做：取消后继续完成，或依赖被删仍放行下游
- 怎样算完：每次决定都得到一致的新图、阻断原因或下一个 ready task

## User Intent

实现“不行就取消当前任务，接着执行和优化下一个”的可审计语义。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
scheduler_owner: GoalRun
implementation_admission: shared_real_git_worktree
refreeze_policy: invalidate_admission_and_ready_set
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 接收人工 rewrite/split/replace/cancel。2. 关闭旧任务。3. 建替代边或标路径阻断。4. 重算 ready set。5. 调度下一任务。

## First principles

- cancelled 不是 done，superseded 不是 failed。
- required dependency 被取消时必须替代或 block。
- 重排必须保持已验证证据，不得无理由重做。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| ReplacementLink | old_task, new_tasks, decision_ref | 替代关系 |
| ReadySetRevision | graph_revision, cause, task_ids | 重算结果 |
| DependencyImpact | downstream, disposition, reason | 取消传播 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-RPL-01 | user | must | AC-RPL-001 | covered |
| INT-RPL-02 | dependency | must | AC-RPL-002 | covered |
| INT-RPL-03 | scheduler | must | AC-RPL-003 | covered |
| INT-RPL-04 | evidence | must | AC-RPL-004 | covered |
| INT-RPL-05 | safety | must | AC-RPL-005 | covered |
| INT-RPL-06 | admission | must | AC-RPL-006 | covered |
| INT-RPL-07 | refreeze | must | AC-RPL-007 | covered |
| INT-RPL-08 | fill-recovery | must | AC-RPL-008 | covered |
| INT-RPL-09 | closure-ready | must | AC-RPL-009 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-RPL-001 | rewrite/split/replace/cancel 分别产生 proposed replacement、superseded children、cancelled link 或纯取消 |
| AC-RPL-002 | required dependency 取消后必须存在 replacement，否则下游 path=blocked |
| AC-RPL-003 | 每次图变更原子地重算 ready set，只调度依赖满足且 admission pass 的任务 |
| AC-RPL-004 | 已 verified/done 任务的有效证据在语义未失效时保留；受 refreeze 影响则标 stale |
| AC-RPL-005 | cancelled/superseded/blocked 不得转换为 done，Goal 聚合必须区分统计 |
| AC-RPL-006 | Goal scheduler 只能 dispatch 当前 ready set 中且 shared admission pass 的 implementation TaskNode；每次 dispatch 记录 admission/worktree/cwd/HEAD refs，direct/goal/team/ralph 不得分叉准入语义 |
| AC-RPL-007 | Truth refreeze 或 main reconcile 变化必须原子地使旧 graph revision、ready set 与 admission refs stale；重新编译并在真实 worktree reconcile 新 frozen revision 后才能继续 dispatch |
| AC-RPL-008 | Host fill/schema validation/TaskRun 遇到 timeout、retryable failure、non-retryable failure 或 human reject 时，必须分别进入 retry_wait、blocked 或 cancelled/replacement 路径；重试耗尽后不得自旋，必须发布 reason_code 与 next-ready/rewrite route |
| AC-RPL-009 | ready set 为空时必须区分 `open_work_exists` 与 `no_open_work`：前者 blocked 并列出阻断项，后者进入 `closure_ready` 交给 L8 verifier；不得把“无可运行任务”统一当成死循环或完成 |

## Domain FSM CancelReplan

| State | From | Guard |
|-------|------|-------|
| decision_received | — | human choice valid |
| rewriting_graph | decision_received, blocked | choice applied or replacement supplied |
| recomputing | rewriting_graph | required replacement edges satisfied |
| dispatchable | recomputing | current ready candidates exist |
| blocked | rewriting_graph, recomputing | dependency gap or no ready candidate |
| complete | dispatchable | shared admission pass and next task handed off |
| retry_wait | decision_received, rewriting_graph | retryable host/task failure |
| closure_ready | recomputing | no open work remains |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| decision_received | apply | choice_valid | rewriting_graph | close old task |
| rewriting_graph | replacement_ready | required_edges_satisfied | recomputing | persist new revision |
| rewriting_graph | dependency_gap | required_missing | blocked | block downstream path |
| blocked | provide_replacement | replacement_valid | rewriting_graph | link replacement |
| recomputing | ready_found | candidates_present | dispatchable | publish ready set |
| recomputing | none_ready | open_work_exists | blocked | publish blockers |
| recomputing | none_ready | no_open_work | closure_ready | hand off convergence verification |
| dispatchable | dispatch | admission_pass | complete | hand off next task |
| decision_received | retryable_failure | retry_budget_remaining | retry_wait | record timeout/failure |
| retry_wait | retry_due | inputs_current | rewriting_graph | retry fill or task |
| retry_wait | retry_exhausted | limit_hit | blocked | publish rewrite/cancel/next-ready route |
| decision_received | non_retryable_failure | reason_present | blocked | require rewrite/replace/cancel |

终态：`complete`、`closure_ready`；`blocked` 需新 replacement、rewrite 或外部解除。

## Illegal transitions

- cancelled task → done
- required dependency cancellation with downstream ready
- graph revision change without ready-set recompute
- Goal scheduler bypassing shared worktree admission
- refreeze 后复用旧 ready set 或 admission ref
- timeout/non-retryable failure 在无预算或无人工决定时自动重试
- `no_open_work` 被错误归类为 blocked 死循环或直接 Goal complete

## Non-goals

- 自动忽略人工取消决定。
- 无限制重试失败任务。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] replacement、shared admission 与 refreeze invalidation 获确认（`user-confirmation-2026-07-27`）
