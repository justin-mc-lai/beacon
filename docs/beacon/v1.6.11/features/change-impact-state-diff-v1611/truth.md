---
slug: change-impact-state-diff-v1611
version: v1.6.11
status: frozen
revision_id: R2
language: zh
domain_required: true
domain_kind: platform
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
change_reason: "D3: structured fill patch transaction and complete ChangePlan recovery FSM"
parent_truth: docs/beacon/v1.6.11/features/intent-completeness-engine-v1611/truth.md
inherited_contracts: "docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md; docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md; docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md; docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/change-impact-state-diff-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/change-impact-state-diff-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/change-impact-state-diff-v1611/tests.md
---

# Requirement Truth: L3 Change Impact and State Diff

## 人话

把“要改什么”从一句话变成清晰差异：承诺、接口、数据、状态机和测试分别从什么变成什么。

- 能做：生成五表面 Before→After、合法边、非法边与影响范围
- 不能做：只有新增列表，没有旧行为与迁移语义
- 怎样算完：每条变更有来源意图、旧值、新值、受影响对象和测试落点

## User Intent

让 Change 成为实现可直接消费的差异合同。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
diff_surfaces:
  - promise
  - interface
  - data
  - fsm
  - tests
  - delegation
  - admission
  - lifecycle_trace
  - compatibility
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 读取完整意图树。2. 对照 ContextEnvelope。3. 生成五表面 diff。4. 人工审查状态机和破坏性影响。

## First principles

- 没有 Before 就无法判断兼容性，没有 After 就无法验收。
- 状态机变更必须同时声明新增/删除/非法边。
- diff 只能引用已确认意图。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| ImpactDiff | surface, before, after, source_intent | 单项差异 |
| StateDiff | added_states, removed_states, added_edges, illegal_edges | 状态机差异 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-DIF-01 | user | must | AC-DIF-001 | covered |
| INT-DIF-02 | fsm | must | AC-DIF-002 | covered |
| INT-DIF-03 | trace | must | AC-DIF-003 | covered |
| INT-DIF-04 | review | must | AC-DIF-004 | covered |
| INT-DIF-05 | inherited-surfaces | must | AC-DIF-005 | covered |
| INT-DIF-06 | structured-patch | must | AC-DIF-006 | covered |
| INT-DIF-07 | fill-transaction-fsm | must | AC-DIF-007 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-DIF-001 | Change 输出 promise/interface/data/FSM/test 五表面 Before→After |
| AC-DIF-002 | FSM diff 明确 old/new states、合法边、illegal 边、超时/失败/取消恢复边 |
| AC-DIF-003 | 每条 diff 绑定 source intent、affected code scope 与 planned TC |
| AC-DIF-004 | 删除、破坏兼容或高风险状态变更必须进入 state_diff_review 人工确认 |
| AC-DIF-005 | Change diff 必须覆盖 public 1+6 lifecycle 映射、subagent delegation/诚实 fallback、shared worktree admission、Goal run_id/`agent_trace.v1`、Goal completion owner 与 no-compat migration；任一 inherited surface 缺失即阻断 review |
| AC-DIF-006 | Host Agent（skill-authored fill）只能返回 `truth-fill-response.v1` 结构化领域对象/patch；CLI 依据 `truth-fill-transaction.v1` 校验 request hash、base revision、schema、AC/TC/FSM 引用和 allowed paths 后，才可原子地投影四文件，禁止 LLM 自由覆盖 Markdown |
| AC-DIF-007 | 正式 ChangePlan 必须覆盖 `GoalUtteranceCaptured → VersionAndContextResolved → DeterministicScaffoldMaterialized → HostAgentFillRequested → StructuredFillProduced → FillPatchSchemaValidated → CanonicalTruthPatched → TestsTasksEvidenceRegenerated → PackageValidationPassed → TruthReviewPassed → AwaitingHumanAck → Frozen`，并为 schema reject、semantic rewrite、human reject/cancel、timeout 与 retry exhaustion 提供回边或阻断终态 |

## Domain FSM ChangeImpactDiff

| State | From | Guard |
|-------|------|-------|
| queued | — | intent tree complete |
| mapping | queued, blocked, review, stale | inputs current or findings repaired |
| review | mapping | all required surfaces present |
| approved | review | human acknowledgement recorded |
| blocked | mapping | required surface missing |
| stale | approved | upstream revision changed |
| fill_requested | mapping | scaffold and request hashes current |
| fill_validating | fill_requested | structured response produced |
| awaiting_human | review, fill_validating | conflict, reject or high-risk diff |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| queued | map | intent_tree_complete | mapping | compare surfaces |
| mapping | diff_ready | five_surfaces_present | review | publish diff |
| mapping | request_fill | scaffold_current | fill_requested | emit truth-fill-request.v1 |
| fill_requested | response_received | response_nonempty | fill_validating | bind response hash |
| fill_validating | schema_pass | refs_and_paths_valid | mapping | apply transaction and regenerate projections |
| fill_validating | schema_fail | findings_present | awaiting_human | publish reject/rewrite/cancel choices |
| mapping | gap | surface_missing | blocked | attach gap |
| blocked | supplement | intent_or_context_fixed | mapping | recompute |
| review | approve | human_ack | approved | seal change |
| review | reject | findings_present | mapping | revise diff |
| awaiting_human | rewrite | decision_ref | fill_requested | request corrected structured fill |
| awaiting_human | retry | decision_ref_and_retryable | fill_requested | retry host transport |
| awaiting_human | cancel | decision_ref | blocked | abort current fill transaction |
| approved | upstream_stale | revision_changed | stale | invalidate diff |
| stale | remap | inputs_current | mapping | rebuild |

终态：`approved`。

## Illegal transitions

- `queued → approved`
- `mapping → review` with missing surface
- `review → approved` without human_ack
- inherited lifecycle/delegation/admission/trace/no-compat surface omitted
- Host Agent（skill-authored fill）直接写四文件或 patch 越过 allowed paths
- schema/hash 校验失败后仍投影 canonical truth
- `awaiting_human` 无 decision_ref 返回自动执行

## Non-goals

- 在 diff 阶段生成任务数量。
- 自动批准破坏性变更。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] 五表面及继承能力差异获人工确认（`user-confirmation-2026-07-27`）
