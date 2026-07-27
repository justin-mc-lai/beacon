---
slug: drift-padding-review-gate-v1611
version: v1.6.11
status: frozen
revision_id: R2
language: zh
domain_required: true
domain_kind: gate
ux_required: false
ux_deferred: true
package_maturity: filled
materials_status: current
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
program_ref: docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/program-manifest.md
truth_map_contract: beacon-truth-map-v1
participating_services: beacon
git_canonical_branch: main
previous_revision: R1
change_reason: "D3: reject hollow full-package fill and require governed human decisions"
parent_truth: docs/beacon/v1.6.11/features/atomic-task-graph-compiler-v1611/truth.md
inherited_contracts: "docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md; docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/drift-padding-review-gate-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/drift-padding-review-gate-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/drift-padding-review-gate-v1611/tests.md
---

# Requirement Truth: L6 Drift and Padding Review Gate

## 人话

AI 一旦开始偏离目标、重复劳动或为了凑任务数注水，就必须停下来把证据和选择交给人确认。

- 能做：检测 scope drift、orphan、重复语义、低价值拆分和证据不匹配
- 不能做：模型自己判自己没跑偏，或人工未决定就继续
- 怎样算完：命中门禁后只允许 continue/rewrite/split/replace/cancel 五类显式决定

## User Intent

把“发现注水或偏差需要人工确认”变成强状态机门禁。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
finding_sources:
  - canonical_detector
  - host_hook_advisory
  - subagent_advisory
decision_owner: beacon_canonical_policy_plus_human
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 任务运行。2. detector 计算漂移/注水信号。3. 命中阈值暂停。4. 人工查看依据并选择。5. 系统记录决定后恢复或重排。

## First principles

- gate 由可解释 finding 触发，不由模型情绪触发。
- 人工主权包括继续执行，不只是否决。
- host hook 可补充信号，不能成为唯一强门。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| ReviewFinding | kind, score, refs, expected, observed | 偏差证据 |
| HumanDecision | choice, rationale, actor, decided_at | 人工决定 |
| ReviewPolicy | thresholds, mandatory_kinds | 门禁策略 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-REV-01 | user | must | AC-REV-001 | covered |
| INT-REV-02 | anti-padding | must | AC-REV-002 | covered |
| INT-REV-03 | sovereignty | must | AC-REV-003 | covered |
| INT-REV-04 | audit | must | AC-REV-004 | covered |
| INT-REV-05 | boundary | must | AC-REV-005 | covered |
| INT-REV-06 | ownership | must | AC-REV-006 | covered |
| INT-REV-07 | fill-quality | must | AC-REV-007 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-REV-001 | detector 至少覆盖 intent drift、scope drift、orphan、duplicate、padding、evidence mismatch |
| AC-REV-002 | 任一 mandatory finding 使任务进入 drift_suspected→awaiting_human，停止自动执行 |
| AC-REV-003 | 人工选择限定为 continue/rewrite/split/replace/cancel，并保留 rationale/actor/time |
| AC-REV-004 | 无 decision_ref 时不得从 awaiting_human 返回 running/proposed 或进入 cancelled |
| AC-REV-005 | host hook、context monitor 与 subagent finding 只能提供 advisory signal，不能自行暂停、放行、取消任务或关闭 Goal |
| AC-REV-006 | 强门与五类人工选择必须由 Beacon canonical policy 持久化并校验 decision_ref；只有 parent/Goal scheduler 可消费决定并转换任务图 |
| AC-REV-007 | full-package fill 必须检测 placeholder、空域模型、句子级假拆解、AC/TC orphan、FSM hanging state、重复/注水 task、evidence mismatch 与 source-hash drift；命中 mandatory finding 后进入人工 `continue/rewrite/split/replace/cancel`，未经决定不得 patch/freeze |

## Domain FSM DriftReviewGate

| State | From | Guard |
|-------|------|-------|
| observing | —, cleared | task running |
| drift_suspected | observing | mandatory or threshold finding |
| awaiting_human | drift_suspected | finding evidence complete |
| cleared | awaiting_human | continue decision_ref valid |
| rewrite_requested | awaiting_human | rewrite decision_ref valid |
| split_requested | awaiting_human | split decision_ref valid |
| replacement_requested | awaiting_human | replace decision_ref valid |
| cancellation_requested | awaiting_human | cancel decision_ref valid |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| observing | finding | mandatory_or_threshold | drift_suspected | pause task |
| drift_suspected | publish | finding_complete | awaiting_human | show evidence/options |
| awaiting_human | continue | decision_ref | cleared | resume same task |
| awaiting_human | rewrite | decision_ref | rewrite_requested | replace contract |
| awaiting_human | split | decision_ref | split_requested | create children |
| awaiting_human | replace | decision_ref | replacement_requested | cancel and link |
| awaiting_human | cancel | decision_ref | cancellation_requested | cancel and recompute |
| cleared | next_signal | task_running | observing | continue monitoring |

终态：`rewrite_requested`、`split_requested`、`replacement_requested`、`cancellation_requested`；`cleared` 返回运行环。

## Illegal transitions

- `drift_suspected → cleared`
- `awaiting_human → observing` without decision_ref
- mandatory finding 存在时继续自动 dispatch
- subagent finding directly cancelling or clearing a task
- child executor applying a human decision to the canonical graph
- hollow fill 或 source-hash drift 未经 human decision 仍写入 canonical package

## Non-goals

- 让模型单方面否决用户范围。
- 依赖特定宿主 hook 才能工作。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] 人工选择、mandatory finding 与 parent ownership 获确认（`user-confirmation-2026-07-27`）
