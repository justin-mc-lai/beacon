---
slug: intent-completeness-engine-v1611
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
change_reason: "D3: Host Agent (skill-authored fill) recursively fills complete feature-package semantics"
parent_truth: docs/beacon/v1.6.11/features/brownfield-context-resolver-v1611/truth.md
inherited_contracts: "docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md; docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md; docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md; docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/intent-completeness-engine-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/intent-completeness-engine-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/intent-completeness-engine-v1611/tests.md
---

# Requirement Truth: L2 Intent Completeness Engine

## 人话

把一句大目标拆到“没有沉默遗漏”：角色、旅程、成功、失败、边界、状态、非目标和延后项都必须有落点。

- 能做：递归展开 must/should 意图并生成覆盖树
- 不能做：用任务数量冒充拆解完整，或静默忽略异常路径
- 怎样算完：每条 must 落到 Journey/AC/Non-goal/approved Deferral

## User Intent

确保大目标拆全，而不是只拆出看起来很多的任务。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
must_inherit:
  - goal_owner
  - intent_on_subagent
  - real_worktree_admission
  - public_1plus6_trace
  - no_compat_refreeze
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 读取 ContextEnvelope。2. 抽取目标与约束。3. 按角色/旅程/失败/状态递归展开。4. 用户确认歧义与 deferral。

## First principles

- 完整性由意图覆盖证明，不由条目数量证明。
- 每次递归必须产生新语义或停止理由。
- should 可延期，must 不可沉默丢失。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| IntentNode | id, parent, strength, actor, outcome | 递归意图节点 |
| CoverageLanding | intent_id, kind, ref, status | 需求落点 |
| Deferral | id, reason, owner, approval_ref | 经批准延期 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-INT-01 | user | must | AC-INT-001 | covered |
| INT-INT-02 | vision | must | AC-INT-002 | covered |
| INT-INT-03 | anti-padding | must | AC-INT-003 | covered |
| INT-INT-04 | sovereignty | must | AC-INT-004 | covered |
| INT-INT-05 | inherited-truth | must | AC-INT-005 | covered |
| INT-INT-06 | full-package-fill | must | AC-INT-006 | covered |
| INT-INT-07 | anti-false-completeness | must | AC-INT-007 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-INT-001 | 引擎递归展开 actor、goal、journey、failure、state、constraint、non-goal 七类节点 |
| AC-INT-002 | 每条 must 意图必须落到 Journey/AC/Non-goal/approved Deferral，missing 阻断 Change |
| AC-INT-003 | 递归停止依据是语义闭合、重复或用户批准延期，不得以达到任务数量停止 |
| AC-INT-004 | 歧义、冲突或高影响默认值必须进入人工确认，并保留 decision_ref |
| AC-INT-005 | ContextEnvelope 中继承的 Goal owner、intent-on subagent、真实 worktree admission、1+6 trace 与 no-compat refreeze 能力必须提升为 must IntentNode 并有 Journey/AC 落点；任何一项不得在拆解中静默消失或降级为 should |
| AC-INT-006 | Host Agent（skill-authored fill）必须一次生成可校验的完整领域对象：人话 L0、User Intent Snapshot、角色/旅程/失败路径、Intent Coverage Matrix、AC、Domain Model、FSM 五元组、illegal transitions、Non-goals，以及 tests/tasks/evidence 的投影输入；输出合同为 `truth-fill-response.v1` |
| AC-INT-007 | “按句拆分→一句一 AC”、`domain_required=false`、固定数量扩写、重复改写或未产生 Journey/FSM/exec-layer TC 输入的结果必须标记 `semantic_incomplete`/`padding_suspected` 并阻断 full-package filled |

## Domain FSM IntentCompleteness

| State | From | Guard |
|-------|------|-------|
| seeded | — | context envelope resolved |
| expanding | seeded, awaiting_human, stale | baseline current and decision refs valid |
| awaiting_human | expanding | high-impact ambiguity found |
| complete | expanding | no missing must intents |
| stale | complete | baseline changed |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| seeded | expand | baseline_resolved | expanding | create child intents |
| expanding | gap_found | new_semantics | expanding | recurse |
| expanding | ambiguity | high_impact | awaiting_human | request decision |
| awaiting_human | decide | decision_ref | expanding | apply decision |
| expanding | coverage_complete | no_missing_must | complete | seal intent tree |
| complete | upstream_stale | baseline_changed | stale | invalidate coverage |
| stale | rebuild | baseline_current | expanding | regenerate tree |

终态：`complete`。

## Illegal transitions

- `seeded → complete`
- `expanding → complete` with missing must
- `awaiting_human → expanding` without decision_ref
- inherited frozen capability omitted or weakened to should
- 只完成 prose/AC 而未覆盖 Journey、FSM、illegal、TC/task/evidence 输入却标记 complete
- 通过重复语句或固定任务数量满足 completeness

## Non-goals

- 强制生成至少 100 个意图或任务。
- 用模型自信度替代用户决策。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] 用户确认继承能力均为 must，且不存在待决延期（`user-confirmation-2026-07-27`）
