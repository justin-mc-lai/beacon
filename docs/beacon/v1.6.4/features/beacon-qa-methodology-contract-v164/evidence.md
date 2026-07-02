---
slug: beacon-qa-methodology-contract-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：QA Methodology Contract v1.6.4

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-methodology-contract-v164/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define + acceptance | truth.md | draft |
| R1 truth.coverage | tests.md | draft |

## Source refs

- program feature-graph：docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 5)
- 用户方法论原话：第一性原理 + 对抗式审查（交付前必做，列 3-5 翻车点，验证证据）

## UD-3 Cross-Version Impact Assessment

- §5 既有 4 条条款不改，纯增量新增 2 条
- v1.6.3 skill 行为零破坏（约束叠加，不删除/不改既有）
- v1.6.3 release gate 不改（仅 v1.6.4+ 强制对抗式审查）
- 结论：cross-version 改动安全

## Diagnostic evidence（gap baseline）

- global-boundaries §5 无「第一性原理」/「对抗式审查」显式条款
- planner-review adversarial lane 信号触发式（非 qa release 前强制）
- qa skill 无"交付前对抗式审查"契约

## Implementation/QA evidence

由下游 `beacon-gen-implement` / `beacon-eval-qa` 阶段填充（truth 阶段不留 placeholder）。
