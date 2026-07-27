---
slug: brownfield-context-resolver-v1611
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
baseline_commit: 30b9adffc8ec5442a7691a88faf64a251d97b98f
truth_map_contract: beacon-truth-map-v1
participating_services: beacon
git_canonical_branch: main
previous_revision: R1
change_reason: "D3: resolve full-package fill inputs, host transport and semantic source hashes"
parent_truth: docs/beacon/v1.6.11/features/contract-baseline-convergence-v1611/truth.md
inherited_contracts: "docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md; docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md; docs/beacon/v1.6.10/features/unified-implement-admission-v1610/truth.md; docs/beacon/v1.6.10/features/trace-lifecycle-binding-v1610/truth.md; docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/brownfield-context-resolver-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/brownfield-context-resolver-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/brownfield-context-resolver-v1611/tests.md
---

# Requirement Truth: L1 Brownfield Context Resolver

## 人话

拆需求前先回答“现在到底是什么”：当前代码、冻结需求、测试和历史变更必须被同一份基线引用。

- 能做：解析 commit、Truth revision、代码入口、测试基线、历史 Change
- 不能做：只读文档不读代码，或只扫代码不认冻结 Truth
- 怎样算完：每个 Change 都有完整 ContextEnvelope，冲突显式阻断

## User Intent

让 Plan 在 brownfield 场景中基于真实主分支上下文，而不是凭空拆任务。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
baseline_commit: 30b9adffc8ec5442a7691a88faf64a251d97b98f
required_authorities:
  - frozen_truth
  - host_subagent_runtime
  - unified_worktree_admission
  - lifecycle_agent_trace
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 用户说出目标。2. resolver 读取治理与版本。3. 定位相关 Truth/代码/测试/Change。4. 冲突时请求人工选择权威。

## First principles

- Truth 定义承诺，代码定义现状，测试定义已验证行为；三者不可互相替代。
- 基线引用必须可重放，不能只保存摘要。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| ContextEnvelope | commit, truth_revisions, inherited_contracts, code_entries, test_baseline, change_refs, subagent_runtime, worktree_governance, lifecycle_trace_authority | Change 输入基线 |
| ContextConflict | surfaces, reason, candidates, decision_ref | 权威冲突 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-CTX-01 | user | must | AC-CTX-001 | covered |
| INT-CTX-02 | brownfield | must | AC-CTX-002 | covered |
| INT-CTX-03 | governance | must | AC-CTX-003 | covered |
| INT-CTX-04 | audit | must | AC-CTX-004 | covered |
| INT-CTX-05 | inheritance | must | AC-CTX-005 | covered |
| INT-CTX-06 | execution-context | must | AC-CTX-006 | covered |
| INT-CTX-07 | fill-context | must | AC-CTX-007 | covered |
| INT-CTX-08 | host-fail-closed | must | AC-CTX-008 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-CTX-001 | ContextEnvelope 同时绑定 commit、Truth revision、代码入口、测试基线、历史 Change |
| AC-CTX-002 | resolver 从用户目标反向定位相关 service/module/test，而非要求用户手工列全 |
| AC-CTX-003 | Truth、代码、测试语义冲突时进入 awaiting_human，并列出候选权威与影响 |
| AC-CTX-004 | 任一基线引用变化都会使下游 intent/diff/task graph 标记 stale |
| AC-CTX-005 | ContextEnvelope 必须解析 `parent_truth` 与 `inherited_contracts`，并把既有 Goal/Plan、subagent、worktree admission、lifecycle trace、Truth authority 的 frozen revision 作为不可静默丢失的输入 |
| AC-CTX-006 | resolver 必须返回 host subagent runtime 可用性、truth canonical、implementation worktree governance、1+6 lifecycle/`agent_trace.v1` 权威；缺失或冲突时 fail-closed，不得猜默认值 |
| AC-CTX-007 | ContextEnvelope 必须包含原始 Goal utterance、目标版本、当前四文件路径与 source hashes、R2 revision、旧 PRD/User Story semantic compiler refs、host transport capability/precedence、Humanizer profile、Program/PAC refs；这些字段共同构成 `truth-fill-request.v1` 输入 |
| AC-CTX-008 | Host semantic transport 不可用、response 为空、source hash 变化或输入权威冲突时必须进入 `awaiting_human`/blocked；不得退化为规则模板、一句一 AC 或空占位后冒充 Host Agent（skill-authored fill）全包填充 |

## Domain FSM ContextResolver

| State | From | Guard |
|-------|------|-------|
| requested | — | goal present |
| resolving | requested, awaiting_human | scan started or decision recorded |
| resolved | resolving, stale | minimum authority set complete |
| awaiting_human | resolving | authorities conflict |
| stale | resolved | source fingerprint changed |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| requested | start | goal_present | resolving | scan authorities |
| resolving | refs_found | minimum_set_complete | resolved | seal envelope |
| resolving | conflict | authorities_disagree | awaiting_human | publish candidates |
| awaiting_human | choose | decision_recorded | resolving | apply authority |
| resolved | source_changed | fingerprint_changed | stale | invalidate downstream |
| stale | refresh | new_refs_complete | resolved | reseal envelope |

终态：`resolved`。

## Illegal transitions

- `requested → resolved` without scan
- `awaiting_human → resolved` without decision_ref
- `stale → resolved` while downstream remains current
- inherited frozen contract missing while envelope reports resolved
- worktree or trace authority unresolved while implementation planning continues
- fill request 缺原始 utterance、四文件 hash、semantic compiler 或 host transport 仍进入 generation
- 空 host response 被规则模板替代并标记 full-package filled

## Non-goals

- 自动改写冲突 Truth。
- 在 resolver 阶段生成实现代码。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] 冲突权威与继承合同策略获人工确认（`user-confirmation-2026-07-27`）
