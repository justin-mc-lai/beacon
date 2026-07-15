---
slug: beacon-qa-methodology-contract-v164
version: v1.6.4
status: frozen
revision_id: R1
language: zh
change_reason: R1 — 第一性原理 + 对抗式审查方法论写入 skill 行为契约（global-boundaries §5 增量 + qa skill 强制 + planner-review adversarial lane）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/truth.md
  user_story: docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/truth.md
  test_case: docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：QA Methodology Contract v1.6.4

## 概述

用户要求两条工作方法论写入 beacon 行为契约：(1) **第一性原理**——动手前回到根本问题，拆到最小可验证单元，每个决定说得出"为什么"；(2) **对抗式审查**——交付前切换成最挑剔审查者，主动列 3-5 翻车点，拿出验证证据，不接受"看起来没问题"。

当前 `global-boundaries §5` 有 skill 哲学边界但无这两条显式条款；planner-review 有 `adversarial-reviewer` lane 但是信号触发式（非交付前强制）；qa skill 无"交付前对抗式审查"强制。

## User Intent（一行）

第一性原理 + 对抗式审查写入 skill 行为契约，交付前强制列翻车点 + 验证证据。

## User Intent Snapshot

- user_prompt: "第一性原理 + 对抗式审查（交付前必做，列 3-5 翻车点，验证证据，不接受看起来没问题）"
- lake_or_ocean: 湖（海级程序已拆，本 feature 单点方法论落地，scope 清晰）
- scope_mode: cross_version_governance（改 global-boundaries §5 cross-version canonical + v1.6.4 skill 落地）
- silent_scope_change_allowed: false
- program_ref: docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 5)

## User Decisions（locked）

- UD-001 cross-version scope：本 feature 改 `global-boundaries.md §5`（cross-version canonical），显式声明 cross-version 性质。UD-3 评估：§5 增条款是**纯增量**（不修改既有条款），v1.6.3 既有 skill 行为不破坏（仅多两条约束，不删除/不改既有）
- UD-002 对抗式审查强制：qa skill 交付前必须列 3-5 翻车点 + 验证证据，缺失 → block（非可选）
- UD-003 第一性原理落地：在 truth.define / implement 入口校准"根本问题 + 最小可验证单元 + 为什么"，非文档装饰

## UD-3 Cross-Version Impact Assessment（v1.6.3）

| 影响面 | v1.6.3 现状 | 本 feature 改动 | 破坏性 |
|---|---|---|---|
| global-boundaries §5 既有条款 | 4 条（哲学/可执行标准/补充规则） | **新增** 2 条（第一性原理 + 对抗式审查），不改既有 | 无（纯增量） |
| v1.6.3 skill 行为 | 按 §5 既有哲学 | 多两条约束（第一性/对抗式），不删除既有 | 无（约束叠加） |
| planner-review adversarial lane | 信号触发式 | 强化"交付前强制"（qa release 前） | 无（v1.6.3 不强制，仅 v1.6.4+ qa release 触发） |
| v1.6.3 release gate | 无对抗式审查强制 | 不改 v1.6.3 gate（仅 v1.6.4+） | 无 |

**结论**：纯增量，v1.6.3 既有行为零破坏。cross-version 改动安全。

## Problem Statement

1. §5 无「第一性原理」显式条款（动手前回到根本问题）。
2. §5 无「对抗式审查」显式条款（交付前列翻车点 + 验证证据）。
3. planner-review adversarial lane 是信号触发，非 qa release 前强制。
4. qa skill 无"交付前对抗式审查"契约强制。

## Non-Goals

- 不改 §5 既有 4 条条款（UD-001 纯增量）。
- 不改 v1.6.3 release gate（UD-3，仅 v1.6.4+ 强制）。
- 不实现 qa 能力本身（Phase 1-4 范围）。
- 不做方法论培训材料（仅行为契约）。

## 受影响代码面

- `docs/beacon/global-boundaries.md`：§5 新增「第一性原理」+「对抗式审查」条款（cross-version canonical，纯增量）。
- `skills/beacon/beacon-eval-qa/SKILL.md`：增"交付前对抗式审查"强制契约。
- `beacon/utils/planner_review_runtime.py`：adversarial lane 强化（qa release 前强制触发，非仅信号触发）。
- `tests/test_v164_qa_methodology_contract.py`：TC-MC-001..004。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | global-boundaries-first-principles | `global-boundaries.md §5` 新增「第一性原理」条款（动手前回到根本问题 + 拆最小可验证单元 + 每个决定说得出为什么）；纯增量不改既有条款（**Must**，UD-001/003） |
| AC-002 | global-boundaries-adversarial | `global-boundaries.md §5` 新增「对抗式审查」条款（交付前最挑剔审查 + 列 3-5 翻车点 + 验证证据 + 不接受看起来没问题）；纯增量（**Must**，UD-002） |
| AC-003 | qa-skill-contract-mandatory | `beacon-eval-qa` SKILL.md 增"交付前对抗式审查"强制契约；缺失翻车点/验证证据 → block（非可选）（**Must**，UD-002） |
| AC-004 | adversarial-lane-mandatory | `planner_review_runtime` adversarial lane 在 qa release 前强制触发（非仅信号触发）；输出含 3-5 翻车点 + 验证证据形状；缺失 → block（**Must**） |

## Deferral Ledger

| ID | 项 | user_decision |
|---|---|---|
| UD-001 | cross-version scope（改 §5）+ 纯增量 | accepted（UD-3 评估：v1.6.3 零破坏） |
| UD-002 | 对抗式审查强制 + block | accepted（preamble §4） |
| UD-003 | 第一性原理落地（入口校准） | accepted |
| UD-004 | 方法论培训材料 | accepted（延后，仅行为契约） |

## State Machine

```
[§5 既有 4 条] --AC-001增量--> [§5 +第一性原理]
[§5 +第一性原理] --AC-002增量--> [§5 +对抗式审查]
[§5 新条款] --AC-003--> [qa skill 契约强制]
[qa skill 契约] --AC-004--> [planner adversarial 强制触发]
[强制触发] --> 交付前列翻车点 + 验证证据 (缺失 block)
```

## Closed Questions

cross-version scope：纯增量（UD-001 + UD-3 评估）。对抗式强制（UD-002）。第一性原理入口校准（UD-003）。培训材料延后（UD-004）。

## Downstream Routes（post-freeze）

- `beacon-gen-implement`：实现 AC-001..004（§5 增条款 + qa skill 契约 + adversarial lane 强化）。
- `beacon-eval-qa`：验证交付前对抗式审查 block + 翻车点 evidence。
- 完成后 v1.6.4 QA 能力增强 5/5 phase 全闭环。
