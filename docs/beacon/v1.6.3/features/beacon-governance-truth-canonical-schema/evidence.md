---
slug: beacon-governance-truth-canonical-schema
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-governance-truth-canonical-schema/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：Governance Truth-Canonical Schema v1.6.3

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/v1.6.3/features/beacon-governance-truth-canonical-schema/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.3/features/beacon-governance-truth-canonical-schema/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.3/features/beacon-governance-truth-canonical-schema/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define | truth.md | draft |
| R1 truth.coverage | tests.md | draft |
| R2 planner-review intent-parity | deterministic fallback, 9 generic findings, recommended_route=beacon-gen-change（fallback 噪音，未读 truth；P1 state-machine/scope-mode 张力已由 UD-003 收口） | reviewed |
| R3 占位符扫描 | placeholder_scan | pass |
| R4 weak-assertion 扫描 | soft_tc_scan | pass |
| R4 AC 覆盖完整性 | AC-001..006 全 covered | pass |
| R5 deferral 扫描 | deferral_scan | pass |
| R5 verify-closure | closure_allowed | pass（0 issues） |
| R6 sync-requirement-clarity | blocked | none（0 findings） |

## User Decisions（locked）

- UD-001 scope: 仅 schema 字段化，UD-020 裸码另开
- UD-002 resolver: 保留 per_service_canonical_branch + 新增 truth_canonical/runtime_mirror 双字段
- UD-003 AC-005: 缩到 v1.6.3 单版本，v2.0.0 contract 应用作为 implement 下游

## Source refs

- `docs/beacon/global-boundaries.md` §4.2 — truth-on-main canonical 约束源头
- `docs/beacon/governance/project-version-governance.md` — 待字段化的 contract
- `beacon/utils/project_governance.py` — `_assign_version_kv` 白名单（受影响代码面）

## Diagnostic evidence（planner review baseline）

- `beacon doctor verify-delivery --version v2.0.0` → `execution_git_alignment_schema` WARN, blocked=true, reason_codes: git_branch_target_mismatch / git_branch_prefix_mismatch / git_version_ref_not_satisfied
- `docs/beacon/v2.0.0/.machine/execution/git-alignment.json` — blocked=true 实证
- planner_review_id: pln-review-20260630t034135z

## Implementation/QA evidence

由下游 `beacon-gen-implement` / `beacon-eval-qa` 阶段填充（truth 阶段不留 placeholder）。
