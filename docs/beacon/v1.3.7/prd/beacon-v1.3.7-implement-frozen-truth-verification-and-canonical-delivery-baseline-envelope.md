# PRD: Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope

**Feature**: `beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope`  
**Version**: `v1.3.7`  
**Status**: `planning`  
**Date**: `2026-04-23`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Research anchor:
  - `docs/beacon/v1.3.7/research/beacon-v1.3.7-implement-direct-bootstrap-and-conflict-gate-analysis.md`
- Execution anchor:
  - `docs/beacon/v1.3.7/execution/beacon-toolkit-lighthouse-implement-plan-architecture-blueprint-gate.md`
- Current runtime code anchors:
  - `beacon/commands/implement.py`
  - `beacon/utils/implementation_plan.py`
  - `beacon/utils/technical_review_contract.py`

## 1. Problem

Beacon 当前的 `implement` 已经有严格前置条件，但人类入口仍不够极简。

真实约束已经存在：

```text
frozen revision
-> technical review contract
-> implementation plan
-> implement run
```

真正缺的不是“允许跳过 requirement truth”，而是以下两点同时成立的实现方式：

1. 人类在 Codex / Claude 内部可以只通过 `beacon-implement + version + prompt` 进入实现。
2. 系统仍然严格绑定对应版本已冻结的 `prd / user-story / test-case`，不允许 prompt 成为新的 truth source。

如果这条边界不明确，会出现两类风险：

1. prompt 被当成临时需求来源，绕过 frozen requirement truth。
2. `architecture-blueprint`、deterministic contract、git workflow、implementation plan 各自记一份实现前置信息，最后只能互相对表，不能单源闭环。

## 2. Goals

### 2.1 Primary Goal

把 `implement` 收敛成真正的极简实现入口：

```text
frozen requirement truth
-> Codex/Claude beacon-implement(version + prompt)
-> frozen-truth verification
-> canonical delivery baseline envelope
-> projected contracts + plan
-> implementation
```

### 2.2 Expected Result

本线完成后，Beacon 应满足：

1. 对应版本的 `prd / user-story / test-case` 已冻结时，用户可以在 Codex / Claude 内部直接使用 `beacon-implement` 指定 `version` 与 prompt 进入实现。
2. prompt 只作为“实现意图输入”和“冻结需求核实输入”，不作为新的 requirement truth。
3. 系统必须先把 prompt 与已冻结 requirement truth 做核实，再决定继续实现或阻断。
4. `implement plan` 必须先生成 canonical 的 `implementation delivery baseline envelope`。
5. `architecture-blueprint.md`、deterministic implementation contract、git workflow contract、implementation plan 全部由 canonical envelope 单向投影生成。
6. gate 校验 canonical envelope 与各 projection 的一致性，而不是允许多个文档互相对表后都算真相。

## 3. Non-goals

本 PRD 不承担：

- 不允许 implement 直接修改 frozen 的 `prd / user-story / test-case`
- 不允许 prompt 绕过 requirement change / refreeze 流程
- 不新增新的公开一级主命令
- 不把 `architecture-blueprint.md` 升格成可反向驱动 machine truth 的平级真相源
- 不允许多个 contract 各自持有独立实现前置 truth

## 4. Core Product Semantics

### 4.1 Human-facing Minimal Entry

极简入口定义为：

```text
beacon-implement
  + version
  + feature
  + prompt
```

这里的 prompt 语义必须固定为：

- 实现意图补充
- 对 frozen requirement truth 的核实输入

而不是：

- 新增需求
- 扩张 AC
- 扩张测试范围
- 改写 feature boundary

### 4.2 Prompt Classification Gate

系统在真正进入实现前，必须把 prompt 分类为以下四种之一：

1. `in_scope_implementation`
2. `clarification_within_scope`
3. `requirement_change`
4. `truth_conflict`

只有前两类允许继续。

后两类必须阻断，并明确路由到 requirement change / refreeze。

### 4.3 Canonical Delivery Baseline Contract

`implement plan` 前，系统必须先生成 canonical 的 `implementation delivery baseline envelope`。

该 envelope 至少包含：

- `baseline_id`
- `transaction_id`
- `source_hash`
- `projection_seq`
- `version`
- `workspace_root`
- `branch_strategy`
- `base_branch`
- `branch_prefix`
- `default_target_branch`
- `use_git_worktree`
- `worktree_root`
- `direct_delivery_services`
- `writable_services`
- `reference_only_services`
- `service_branch_map`
- `service_worktree_map`
- `feature_overlays`

### 4.4 Projection Rule

以下 artifacts 必须全部由 canonical envelope 单向投影生成：

- `docs/beacon/v1.3.7/execution/architecture-blueprint.md`
- deterministic implementation contract
- git workflow contract
- implementation plan

任何 artifact 都不得反向修改 canonical envelope。

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | 当对应版本的 `prd / user-story / test-case` 已冻结时，用户可以在 Codex / Claude 内部通过 `beacon-implement + version + prompt` 直接进入实现前核实流程。 |
| FR-002 | AC-002 | 系统必须将 prompt 分类为 `in_scope_implementation`、`clarification_within_scope`、`requirement_change`、`truth_conflict` 四类，并且只允许前两类继续。 |
| FR-003 | AC-003 | 当 prompt 被判定为 `requirement_change` 或 `truth_conflict` 时，系统必须阻断 implement，并给出 requirement change / refreeze 路由。 |
| FR-004 | AC-004 | `implement plan` 前必须生成 canonical 的 `implementation delivery baseline envelope`，并使 `architecture-blueprint`、deterministic contract、git workflow、implementation plan 全部成为该 envelope 的单向 projection。 |
| FR-005 | AC-005 | gate 必须校验 canonical envelope 与各 projection 的 `baseline_id`、事务元数据以及 service/branch/worktree 内容一致；发现漂移时阻断。 |

## 6. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | minimal-entry | 在对应版本 requirement truth 已冻结时，用户可在 Codex / Claude 内通过 `beacon-implement + version + prompt` 直接进入实现前核实，而不需要手工重走 requirement 准备流程。 |
| AC-002 | prompt-boundary | prompt 只被当成实现意图输入和 frozen-truth verification 输入；系统能明确区分 scope 内澄清与 requirement 变更。 |
| AC-003 | stop-and-reroute | 当 prompt 暗含新增用户故事、调整 AC、扩展测试范围、改变需求边界或与 frozen truth 冲突时，implement 被阻断，并返回 requirement change / refreeze 指引。 |
| AC-004 | canonical-source | `implement plan` 先生成 canonical envelope，再投影 `architecture-blueprint`、deterministic contract、git workflow、implementation plan，不允许多源并写。 |
| AC-005 | consistency-gate | gate 以 canonical envelope 为唯一对齐源；任一 projection 与 canonical 漂移，或 projection 之间引用不同 baseline，都必须阻断。 |

## 7. Risks

- prompt 分类不稳，可能把 requirement change 误判为 scope 内实现，导致 frozen truth 被绕过。
- canonical envelope 如果不是先提交再投影，仍会退化成多文档对表。
- `architecture-blueprint` 若被误用为上游 truth，会再次违反全局 canonical 单源原则。

## 8. Release Guard

- 只有当 AC-001 到 AC-005 对应测试全部通过，且 gate 对 canonical envelope / projection 一致性判定为通过时，才允许进入 release 评审。
