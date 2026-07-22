---
slug: compat-debt-cut-v1610
version: v1.6.10
status: frozen
revision_id: R1
language: zh
domain_required: false
ux_required: false
canonical_refs:
  prd: docs/beacon/v1.6.10/features/compat-debt-cut-v1610/truth.md
  user_story: docs/beacon/v1.6.10/features/compat-debt-cut-v1610/truth.md
  test_case: docs/beacon/v1.6.10/features/compat-debt-cut-v1610/tests.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
change_reason: "R1: cut soft-compat — feature_package_authoritative always-on; freeze no legacy_split_truth skip"
---

# Requirement Truth: Compat Debt Cut (v1.6.10 R1)

## 人话

去掉「docs 版本旧就降级包权威」的 soft-compat。装上现行 runtime 后，产品线哪怕是 `v0.0.x` 也按 feature package 权威走；freeze 不得再 `legacy_split_truth` 跳过校验。旧 triptych 只能 replan 新包。

- 能做：任何 docs 线 authoritative；缺四件套 fail-closed；v0.0.x 回归
- 不能做：按 docs semver 关掉 package gate；freeze 跳过 validate
- 怎样算完：AC 有 TC；单测绿；本包 TRG 可过

## User Intent

收口 §2.1：docs 版本只是路径命名空间，不是门控降级开关。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
principle: global-boundaries-2.1
```

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-CDC-01 | review | must | AC-CDC-001 | covered |
| INT-CDC-02 | review | must | AC-CDC-002 | covered |
| INT-CDC-03 | review | must | AC-CDC-003 | covered |
| INT-CDC-04 | review | must | AC-CDC-004 | covered |

## First principles

| ID | Constraint |
|----|------------|
| FP-CDC-001 | docs version ≠ capability downgrade |
| FP-CDC-002 | active package authority always on for installed runtime |
| FP-CDC-003 | freeze never skips package validation via legacy_split_truth |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-CDC-001 | `feature_package_authoritative` 对 v0.0.13/v1.4/v1.6 均为 True |
| AC-CDC-002 | `truth_source_model_for_version` 恒为 feature_package_authoritative |
| AC-CDC-003 | freeze 源码不含 `legacy_split_truth` skip |
| AC-CDC-004 | triptych-only / 缺四件套 package integrity 不得 status=skipped |
| AC-CDC-005 | v0.0.x 回归测试存在且通过 |


## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| any | ResolveAuthority | runtime_current | authoritative | feature_package_authoritative |
| authoritative | Freeze | package_ready | frozen | validate_feature_package |
| authoritative | Freeze | package_missing | upgrade_required | block_legacy_split |

## Non-goals

- 删除 archive 历史只读
- 一次删光 gate.py 全部 semver 分叉（另湖）

## Downstream Routes

- implement: truth_map + freeze + truth_integrity
- qa: tests/test_v1610_compat_debt_cut.py + updated legacy tests
