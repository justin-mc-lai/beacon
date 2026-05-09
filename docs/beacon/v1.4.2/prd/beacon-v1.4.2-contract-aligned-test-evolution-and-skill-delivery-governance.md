# PRD: Beacon v1.4.2 Contract-Aligned Test Evolution and Skill Delivery Governance

**Feature**: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`  
**Version**: `v1.4.2`  
**Date**: `2026-05-09`  
**Status**: `freeze-ready`  
**Track**: `test-governance + skill-delivery + release-contract`  
**Scenario**: `beacon-self-iteration + contract-lane-classification + skill-surface-guidance`  
**Template**: `main PRD / next-version planning`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Current runtime architecture: `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- Previous planning line: `docs/beacon/v1.4.1/SUMMARY.md`
- Deep support surface PRD: `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- Deep test delta sample: `docs/beacon/v1.4.1/deep/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure/deep-test-delta.md`
- Skill QA order rule: `skills/beacon/references/usage-rules.md`

## 1. 问题

Beacon 自迭代已经具备 frozen truth、QA、release、deep delta、version surface governance 等能力，但测试集合在持续演进时仍可能混合当前功能验收、当前 runtime 契约、generated surface 同步、兼容承诺、历史快照与过期假设。缺少契约 lane 会让 full-suite 输出无法解释为明确的交付状态。

## 2. 目标

本需求目标是在不扩张主生命周期的边界下，为 Beacon 建立契约对齐的测试演进治理模型：以 frozen truth 为源头，以 Test Contract Index 为投影，以 QA evidence 和 release gate 为验收闭环，使测试增量、skill 指引、风险缓解和恢复路径都可审计。

## 3. 设计原则

### 3.1 边界优先

- `Test Contract Index` 只能作为 machine projection，不能成为第二 truth root。
- `doctor / qa / release / deep` 承担既有表面内的治理职责，不新增公开主阶段。
- planning line 不能污染 current runtime release line。

### 3.2 分层优先

- 分层保持为 markdown truth -> compiled contract -> test contract index -> QA evidence -> release scorecard -> skill delivery guidance。
- skill 文案只能提供交付指引，不能直接定义 release verdict。
- runtime projection 只能消费契约，不能反向改写 frozen truth。

### 3.3 恢复优先

- 失败必须有 reason code、repair route 和 `beacon help` resume route。
- severe blocker 必须 stop_for_repair，修复后再进入下一轮 QA backfill。
- legacy snapshot drift 默认进入 test evolution backlog，除非被明确提升为 compatibility contract。

### 3.4 风险缓解优先

- generated surface drift、feature release lane failure、planning/runtime conflict 必须被识别为 release-facing 风险。
- 风险缓解方式必须显式记录为 repair、waiver、backlog、compatibility promotion 或 reject。
- unclassified full-suite output 不能被用作 release pass 或 release blocker 的唯一依据。

## 4. 范围

In scope:

- Define `Test Contract Index` as a machine-readable delivery governance projection.
- Define canonical test lanes for Beacon self-iteration.
- Define AC/TC/pytest/evidence mapping expectations.
- Define doctor build/verify ownership for test contract governance.
- Define QA and release consumption of lane status.
- Define skill delivery guidance so agent surfaces route test work by contract lane.
- Define release reason codes for missing, stale, failed, or unclassified test contract evidence.
- Define how `deep` test deltas are adopted without letting deep execute QA or rewrite frozen truth.

Out of scope:

- Creating a new public lifecycle stage.
- Promoting `v1.4.2` to runtime release line.
- Rewriting all historical tests.
- Treating full-suite output as a single release gate without lane classification.
- Letting skill text define release truth independently from machine evidence.
- Letting `Test Contract Index` become a second requirement truth root.

## 5. 功能需求

- FR-001: Beacon must define a Test Contract Index containing identity, truth refs, runtime/docs line, lane membership, AC/TC/test/evidence mapping, status, and reason codes.
- FR-002: Beacon must verify release-facing lane classification and block unsafe unclassified failures.
- FR-003: Beacon must require release-facing tests to map to AC/TC and evidence or declare an explicit generated-surface contract reason.
- FR-004: Doctor support commands must own build/verify behavior for the test contract index.
- FR-005: QA must preserve AC order, evidence pack, coverage current/gap, continue decision, repair handoff, help resume, and next-round backfill.
- FR-006: Release scorecard and strict gate must consume lane status and expose reason codes.
- FR-007: Beacon skill surfaces must guide agents to classify tests by lane.
- FR-008: Deep-derived test deltas must route to test-case or supplemental QA.
- FR-009: Planning-line safety must preserve runtime/package/docs-current version truth.

## Overview

Beacon now has a strong truth-to-delivery chain:

```text
prd
-> user-story
-> test-case
-> implement
-> qa
-> release
```

`v1.4.1` added a support surface for deep analysis and test deltas. That exposed a higher-level product governance gap: once Beacon features evolve, tests must also evolve as a contract-aligned system rather than as a flat pytest collection.

The goal of `v1.4.2` is to make Beacon self-iteration and skill delivery capable of answering:

```text
Which tests protect the current feature?
Which tests protect the current runtime line?
Which failures are generated-surface drift?
Which failures are active compatibility blockers?
Which failures are legacy snapshots or test evolution backlog?
Which evidence is required before release readiness can be claimed?
```

## Scope

In scope:

- Define `Test Contract Index` as a machine-readable delivery governance projection.
- Define canonical test lanes for Beacon self-iteration.
- Define AC/TC/pytest/evidence mapping expectations.
- Define doctor build/verify ownership for test contract governance.
- Define QA and release consumption of lane status.
- Define skill delivery guidance so agent surfaces route test work by contract lane.
- Define release reason codes for missing, stale, failed, or unclassified test contract evidence.
- Define how `deep` test deltas are adopted without letting deep execute QA or rewrite frozen truth.

Out of scope:

- Creating a new public lifecycle stage.
- Promoting `v1.4.2` to runtime release line.
- Rewriting all historical tests.
- Treating full-suite output as a single release gate without lane classification.
- Letting skill text define release truth independently from machine evidence.
- Letting `Test Contract Index` become a second requirement truth root.

## Problem

### 1. Feature evolution currently creates mixed test semantics

Beacon's full test suite contains different kinds of obligations:

- current runtime contracts;
- current feature release-facing tests;
- generated surface sync checks;
- compatibility promises;
- historical snapshot checks;
- old assumptions that need test evolution.

When these are run as a flat suite, failures become ambiguous. A single failure may mean a current release blocker, a generated surface drift, a legacy snapshot mismatch, or an obsolete assumption.

### 2. Single tests can become orphaned from product truth

A single test that is not mapped to AC/TC, lane, evidence path, and release consumption can pass while the product contract remains incomplete. It can also fail without explaining whether the failure blocks release.

### 3. Agent skill delivery can amplify ambiguity

If Beacon skills tell agents to “run tests” or “fix full-suite failures” without lane classification, agents can:

- chase historical snapshot drift before current release blockers;
- treat planning-line docs as runtime release claims;
- claim progress without AC/TC/evidence truth;
- skip the QA first-principles order;
- ask humans to guess the resume path instead of using `beacon help`.

## Goals

### Primary Goals

1. Establish a `Test Contract Index` that maps feature truth to test lanes and evidence.
2. Classify Beacon tests into stable contract lanes.
3. Ensure each release-facing single test is traceable to AC/TC and evidence.
4. Let `doctor` build and verify test contract governance.
5. Let `qa` execute lane-aware evidence capture in AC order.
6. Let `release` consume lane status and block on relevant reason codes.
7. Update skill delivery guidance so Codex, Claude, Cursor, and Windsurf agents use contract-lane test routing.
8. Preserve global boundaries by avoiding new public lifecycle stages.

### Non-Goals

- This feature does not implement a new test runner.
- This feature does not replace pytest.
- This feature does not make deep mandatory for every feature.
- This feature does not rewrite legacy tests automatically.
- This feature does not change current runtime version from `v1.4.0`.

## Product Model

### Contract Chain

```text
Markdown truth
-> compiled feature contract
-> test contract index
-> lane-aware QA evidence
-> release scorecard/gate
-> skill delivery guidance
```

### Canonical Lanes

| Lane | Responsibility | Release Blocking Rule |
| --- | --- | --- |
| `feature_release_facing` | Current feature AC/TC/pytest/evidence closure | Blocks current feature release |
| `current_runtime_contract` | Current runtime version, docs default line, public surface, current docs claims | Blocks runtime/release readiness |
| `generated_surface_sync` | Generated or projected surfaces such as `SKILL.md`, metadata, context files, command tables, agent surfaces | Blocks when drift affects routing, versioning, or delivery truth |
| `compatibility_contract` | Explicitly supported legacy behavior | Blocks only when behavior remains an active support promise |
| `legacy_snapshot` | Historical docs/evidence snapshots | Does not block current feature release by default |

## Functional Requirements

### FR-001: Test Contract Index

Beacon must support a machine-readable index under:

```text
docs/beacon/<version>/.machine/testing/test-contract-index.json
```

The index must include feature identity, runtime/docs line, truth refs, lane membership, AC/TC/test/evidence mapping, status, and reason codes.

### FR-002: Lane Verification

Beacon must verify that release-facing tests are classified into a lane and that unclassified failures cannot be silently interpreted as release blockers or release passes.

### FR-003: AC/TC/Test Mapping

Every release-facing test must map to at least one AC/TC item or declare an explicit generated-surface contract reason.

### FR-004: Doctor Ownership

`doctor` must own build/verify behavior for the test contract index so the capability remains support-surface governance rather than a new lifecycle stage.

### FR-005: QA Consumption

`qa` must preserve the first-principles order:

```text
user story / AC order
-> scenario divergence
-> current-round execution
-> evidence pack
-> coverage_current / coverage_gap
-> continue_decision
-> severe blocker stop_for_repair
-> repair handoff
-> beacon help resume
-> next QA round with test-case backfill
-> release guidance
```

### FR-006: Release Consumption

`release scorecard` and strict gate must consume test contract governance and expose reason codes when the feature release lane, current runtime lane, generated surface lane, or unclassified failure handling is unsafe.

### FR-007: Skill Delivery Governance

Beacon skill surfaces must instruct agents to classify and run tests by lane, use `beacon help` for resume, and avoid claiming release readiness from unclassified full-suite output.

### FR-008: Deep Delta Adoption

Deep-derived test deltas must route to `test-case` or supplemental `qa`. Deep must not execute QA, rewrite frozen truth, or directly mark release readiness.

### FR-009: Planning Line Safety

`v1.4.2` materials must not promote runtime version, package version, docs default line, or current runtime release line.

## Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | index-contract | Beacon defines a Test Contract Index with feature identity, truth refs, runtime/docs line, lane membership, AC/TC/test/evidence mapping, status, and reason codes. |
| AC-002 | lane-taxonomy | Beacon defines canonical lanes for feature release-facing tests, current runtime contracts, generated surface sync, compatibility contracts, and legacy snapshots. |
| AC-003 | release-facing-mapping | Release-facing single tests must map to AC/TC and evidence or declare a generated-surface contract reason. |
| AC-004 | doctor-ownership | Doctor support commands own building and verifying the test contract index; no new public lifecycle stage is introduced. |
| AC-005 | qa-order | QA guidance and execution preserve AC order, evidence pack, coverage current/gap, continue decision, severe blocker stop, repair handoff, `beacon help` resume, and next-round backfill. |
| AC-006 | release-gating | Release scorecard and strict gate consume lane status and block on missing, stale, failed, or unclassified release-facing evidence. |
| AC-007 | generated-surface-sync | Generated skill, metadata, command, context, and agent surfaces are classified under `generated_surface_sync` and can block release when drift affects delivery truth. |
| AC-008 | legacy-classification | Historical snapshot failures are routed to `legacy_snapshot` or test evolution backlog unless explicitly promoted to `compatibility_contract`. |
| AC-009 | skill-delivery | Beacon skills instruct agents to use contract-lane verification and avoid unclassified full-suite release claims. |
| AC-010 | deep-delta-adoption | Deep test deltas are adopted through `test-case` or supplemental `qa`; deep remains a support surface and does not execute QA. |
| AC-011 | planning-line-safety | Freezing v1.4.2 requirements does not change current runtime release line, docs default line, or package version. |
| AC-012 | recovery-routing | When test contract governance blocks delivery, Beacon provides reason codes and repair or resume routes through existing support surfaces. |

## 8. 验收标准

| AC ID | 验收主题 | 验收标准 |
| --- | --- | --- |
| AC-001 | index-contract | Test Contract Index 的身份、truth refs、runtime/docs line、lane、AC/TC/test/evidence、status、reason codes 可被机器校验。 |
| AC-002 | lane-taxonomy | 五类 canonical lanes 被明确声明并用于测试分类。 |
| AC-003 | release-facing-mapping | release-facing single tests 未映射 AC/TC/evidence 时必须阻断或声明 generated-surface contract reason。 |
| AC-004 | doctor-ownership | doctor 表面负责 build/verify，不新增主生命周期阶段。 |
| AC-005 | qa-order | QA 顺序保留 AC order、evidence pack、coverage current/gap、continue decision、repair handoff、help resume 和 backfill。 |
| AC-006 | release-gating | release scorecard 和 strict gate 消费 lane status 并输出阻断 reason codes。 |
| AC-007 | generated-surface-sync | generated surfaces 漂移被归入 `generated_surface_sync` 并可在影响交付 truth 时阻断。 |
| AC-008 | legacy-classification | historical snapshot drift 默认不阻断当前 release，除非被提升为 compatibility contract。 |
| AC-009 | skill-delivery | skills 指导 agent 使用 contract-lane verification，不从未分类 full-suite 输出宣称 ready。 |
| AC-010 | deep-delta-adoption | deep delta 经 test-case 或 supplemental QA 采纳，deep 不执行 QA。 |
| AC-011 | planning-line-safety | v1.4.2 freeze 不改变 v1.4.0 runtime/default/current release truth。 |
| AC-012 | recovery-routing | 阻断时必须提供 reason code 和 repair/resume route。 |

## Freeze Deliverables

- `docs/beacon/v1.4.2/SUMMARY.md`
- `docs/beacon/v1.4.2/execution/index.md`
- `docs/beacon/v1.4.2/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- `docs/beacon/v1.4.2/user-story/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- `docs/beacon/v1.4.2/qa/test-cases/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`

## Release-Facing Reason Codes

- `test_contract_index_missing`
- `test_contract_index_stale`
- `ac_test_mapping_missing`
- `feature_release_lane_missing`
- `feature_release_lane_failed`
- `generated_surface_sync_drift`
- `planning_line_runtime_conflict`
- `unclassified_test_failure`
- `legacy_snapshot_misclassified_as_release_blocker`

## Implementation Notes

The preferred first implementation should be small:

1. Add a utility for test contract index build/verify.
2. Add doctor command wrappers.
3. Add release scorecard consumption.
4. Update skill guidance and iteration governance skill text.
5. Add v1.4.2 contract tests.

## Diagram Truth Layer

### Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### State Axes

- `contract_lane`
- `truth_binding`
- `evidence_status`
- `surface_sync`
- `release_blocking`

### Branch-Flow

```text
feature_change_detected
-> affected_contract_layer_identified
-> test_contract_index_built
-> lane_status_verified
-> qa_evidence_collected
-> release_scorecard_consumes_lane_status
```

```text
full_suite_failure
-> classify_failure
-> feature_release_facing | current_runtime_contract | generated_surface_sync | compatibility_contract | legacy_snapshot
-> block_release | route_to_repair | route_to_test_evolution_backlog
```

### State-Machine

```text
unindexed
-> indexed
-> lane_verified
-> evidence_collected
-> release_consumed
-> closed
```

```text
unclassified_failure
-> classified_blocker
-> repair_routed
-> help_resume
-> next_round_backfill
```

### Decision-Priority

```text
global_boundaries
> frozen_requirement_truth
> test_contract_index
> lane_execution_evidence
> release_scorecard
> unclassified_full_suite_output
```

```text
feature_release_facing_failure
> generated_surface_sync_drift
> current_runtime_contract_drift
> compatibility_contract_failure
> legacy_snapshot_drift
```

## Completion Definition

The feature is ready for implementation when:

- PRD, user-story, and test-case materials are frozen.
- AC IDs in user-story and test-case match.
- `v1.4.2` remains planning-only.
- Beacon freeze writes revision baseline and machine requirement package.
- The next implementation prompt can point to this frozen truth package without changing scope.
