---
slug: beacon-test-modernization-v1612
version: v1.6.12
status: frozen
language: zh
package_maturity: filled
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.12/features/beacon-test-modernization-v1612/truth.md
  user_story: docs/beacon/v1.6.12/features/beacon-test-modernization-v1612/truth.md
  test_case: docs/beacon/v1.6.12/features/beacon-test-modernization-v1612/tests.md
humanizer_applied: true
---

# Requirement Truth: beacon-test-modernization-v1612

## 人话

把 696 个存量测试失败按机器分类清单迁移到 v1.6.12 现行规范：先修 20 个上游级联失败，再按批次更新 466 个过期断言、迁移或归档 206 个旧 fixture，历史线测试移入归档，现行线 CI 全绿；v2 未落地能力记录待办。

- 能做： （待补）
- 不能做： （待补）
- 怎样算完： （待补）

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope: 696 pending 存量测试失败（按 disposition 分批）
source: docs/beacon/research/beacon-test-drift-classification-2026-08-06.csv
runtime: v1.6.12 现行规范（不再兼容旧形状/旧 skill/旧 gate 语义）
```

## 用户旅程

1. 本包 plan→truth→freeze 落地
1. 批次1：修复 20 个 fix_upstream_first 级联失败
1. 批次2：迁移 466 个 migrate_assert 断言到现行规范
1. 批次3：迁移/归档 206 个 fixture（103 migrate_or_archive_fixture + 72 migrate_or_archive_assert + 31 migrate_fixture）
1. 批次4：历史线（v1.0–v1.5）归档到 tests/legacy/，现行线 CI 全绿
1. 批次5：v2.x 4 个 defer 项记录并复核

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-01 | user | must | AC-001 | covered |
| INT-02 | user | must | AC-002 | covered |
| INT-03 | user | must | AC-003 | covered |
| INT-04 | user | must | AC-004 | covered |
| INT-05 | user | must | AC-005 | covered |
| INT-06 | user | should | AC-006 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | 分类清单中 20 个 fix_upstream_first 条目修复后，其所属测试文件不再出现级联失败，批次从 implementing 推进到 next_batch |
| AC-002 | 466 个 migrate_assert 条目全部改为现行规范断言并随文件一起通过，批次进入 next_batch |
| AC-003 | 206 个 fixture 条目按 TestDriftBatch 处置完成：迁移后通过，或显式归档（LegacyArchive）并更新清单状态 |
| AC-004 | v1.0–v1.5 历史线测试移入 tests/legacy/（LegacyArchive），默认 pytest 收集不再包含 |
| AC-005 | 默认测试套件（不含 legacy）全量通过后进入 current_line_green，beacon doctor diagnose 无存量兼容失败 |
| AC-006 | v2.x 4 个 defer 条目在 FillBatchQueue 记录 reason_code 与复核计划，不混入现行线验收 |

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| ClassificationRow | nodeid, file, band, category, disposition, status | 失败清单中的一行，迁移批次的输入单位 |
| TestDriftBatch | disposition, rows, acceptance | 按 disposition 分组的迁移批次 |
| LegacyArchive | version_band, test_files, archive_path | v1.0–v1.5 历史线测试归档 |
| CurrentLineCIGate | default_suite_result, legacy_excluded | 现行线 CI 全绿判定 |
| FillBatchQueue | batch_order, done, blocked | 批次推进队列 |

## Domain FSM TestModernization

| State | From | Guard |
|-------|------|-------|
| scaffold_materialized | — | package unfilled |
| filled | scaffold_materialized | host fill applied |
| reviewed | filled | truth review gate pass |
| frozen | reviewed | truth verify pass + freeze revision |
| implementing | frozen | workspace admission pass |
| next_batch | implementing | batch tests pass |
| current_line_green | next_batch, all_batches_done | default suite clean |
| blocked | any non-terminal | missing gate/admission/legacy archive |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold_materialized | host_fill | package_unfilled | filled | apply fill response |
| filled | truth_review | review_gate_pass | reviewed | record review packet |
| reviewed | freeze | truth_verify_pass | frozen | freeze R1 |
| frozen | batch_implement | workspace_admission_pass | implementing | admit worktree + merge main |
| implementing | batch_tests_pass | batch_complete | next_batch | advance disposition batch |
| all_batches_done | legacy_archive | default_suite_clean | current_line_green | CI green |

### invalid / illegal

- scaffold -> frozen
- frozen -> implementing without workspace admission
- legacy delete without archive record
- current_line_green without default suite passing

## Illegal transitions

- TestModernization.scaffold_materialized → frozen（跳过 review/freeze 门禁）
- TestModernization.frozen → implementing 未经过 workspace admission
- TestModernization.legacy_archive 直接删除测试文件而不先归档
- TestModernization.current_line_green 在默认套件未全绿时声明完成

## Non-goals

- 不恢复旧 skill / 旧 split-docs 形状的兼容读取
- 不实现 v2.0 planning 线未落地能力
- 不在本包做 release 判定
- 不修改 version-truth 发布节奏
