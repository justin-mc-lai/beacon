---
slug: contract-baseline-convergence-v1611
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
baseline_commit: 30b9adffc8ec5442a7691a88faf64a251d97b98f
truth_map_contract: beacon-truth-map-v1
participating_services: beacon
git_canonical_branch: main
previous_revision: R1
change_reason: "D3: CLI deterministic scaffold plus Host Agent (skill-authored fill) full-package fill under feature-package authority"
parent_truth: docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md
inherited_contracts: "docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md; docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md"
canonical_refs:
  prd: docs/beacon/v1.6.11/features/contract-baseline-convergence-v1611/truth.md
  user_story: docs/beacon/v1.6.11/features/contract-baseline-convergence-v1611/truth.md
  test_case: docs/beacon/v1.6.11/features/contract-baseline-convergence-v1611/tests.md
---

# Requirement Truth: L0 Contract Baseline Convergence

## 人话

先把 Beacon 自己的版本、上下文和合同测试基线对齐，后面的“大目标拆解”才不会建立在漂移事实之上。

- 能做：固定 runtime/docs 双轴、主分支 commit、已知合同失败与重现命令
- 不能做：把旧包兼容当成功、把 planning-only 当已发布 runtime
- 怎样算完：上下文/版本治理通过严格校验，合同基线可重现并有明确分类

## User Intent

为 v1.6.11 建立单一、可审计、可复现的计划与合同基线。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: full_parity
program: beacon-plan-goal-task-closure-v1611
runtime: v1.6.10
docs_target: v1.6.11
truth_canonical: main
compatibility: no_old_shape_soft_compat
scope_ack_ref: user-confirmation-2026-07-27
```

## 用户旅程

1. 维护者声明新版本。2. 系统核对 runtime/docs 双轴。3. 绑定主分支与测试基线。4. 漂移先阻断再继续。

## First principles

- 基线不可信，后续 diff 与任务图都不可信。
- active package 只接受 v1.6.10+ 形状。
- 已知失败必须分类为预存漂移、目标内修复或明确 deferral。

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| BaselineSnapshot | commit, runtime, docs_version, test_command | 一次不可变基线 |
| ContractFinding | test_id, reason, owner, disposition | 可追踪失败 |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-BAS-01 | user | must | AC-BAS-001 | covered |
| INT-BAS-02 | audit | must | AC-BAS-002 | covered |
| INT-BAS-03 | boundaries | must | AC-BAS-003 | covered |
| INT-BAS-04 | delivery | must | AC-BAS-004 | covered |
| INT-BAS-05 | no-compat | must | AC-BAS-005 | covered |
| INT-BAS-06 | lineage | must | AC-BAS-006 | covered |
| INT-BAS-07 | scaffold-authority | must | AC-BAS-007 | covered |
| INT-BAS-08 | semantic-authority | must | AC-BAS-008 | covered |
| INT-BAS-09 | authenticated-freeze | must | AC-BAS-009 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-BAS-001 | 版本上下文明确记录 runtime=v1.6.10、docs=v1.6.11 planning-only，且严格校验通过 |
| AC-BAS-002 | 基线固定 main commit、Plan/Goal/Truth 关键入口与历史真相引用 |
| AC-BAS-003 | 合同测试基线记录命令、通过数、失败数与逐项 disposition；不得用降低 gate 消除失败 |
| AC-BAS-004 | Truth refreeze 时旧 tests/tasks/evidence 被标 stale，禁止跨 revision 复用 |
| AC-BAS-005 | 旧 package、旧 Goal ledger、缺 Matrix/exec TC/`ac=`/`evidence=` 的 active shape 必须 fail-closed，并返回 `package_shape_upgrade_required` 或等价 reason code；不得加入 legacy reader、soft skip 或 compatibility adapter |
| AC-BAS-006 | 旧冻结 Truth 保持只读 lineage；仍有效的语义只能通过 `parent_truth`/`inherited_contracts` 进入当前 shape，并经 plan → truth/change → Truth Review → freeze new revision 向前迁移 |
| AC-BAS-007 | `beacon truth init`/等价 CLI 只负责确定性创建 `features/<slug>/{truth,tests,tasks,evidence}.md` scaffold、协议版本与占位状态；scaffold 未经 Host Agent（skill-authored fill）全包填充与 review 不得被标记 `package_maturity=filled` 或推荐 freeze |
| AC-BAS-008 | 旧 PRD/User Story semantic compiler、host-response/command-bridge/provider transport 作为受治理的语义输入能力被复用，但当前 `feature_package_authoritative` 四文件仍是唯一 requirement truth；不得恢复平行 `prd/`、`user-story/`、`qa/test-cases/` canonical 写入 |
| AC-BAS-009 | 每个 R2 freeze 必须绑定最终四文件 baseline hash、package-validation report/hash、Truth Review report/hash、human scope ack 与 promotion receipt；任一 hash 漂移或 receipt 仅声明 `status=complete` 时 Program freeze 必须阻断 |

## Domain FSM BaselineConvergence

| State | From | Guard |
|-------|------|-------|
| unbound | — | version not captured |
| resolving | unbound, blocked | version declared or authority repaired |
| current | resolving, stale | all refs consistent and new refs bound |
| blocked | resolving | authority mismatch or old shape detected |
| stale | current | truth revision changed |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| unbound | capture | version_declared | resolving | read authorities |
| resolving | verify_pass | refs_consistent | current | seal snapshot |
| resolving | drift_found | mismatch | blocked | attach finding |
| blocked | repair | authority_updated | resolving | rerun checks |
| current | truth_refrozen | revision_changed | stale | invalidate dependents |
| stale | recapture | new_refs_bound | current | seal new snapshot |

终态：`current`。

## Illegal transitions

- `unbound → current`
- `blocked → current` without rerun
- `stale → current` while old evidence remains current
- old-shape package 通过降低 gate 进入 current
- 新 revision 直接覆盖或改写旧 frozen Truth
- scaffold 未填充即进入 freeze
- 旧 PRD/User Story 文档重新成为 active canonical truth
- promotion receipt 未绑定最终四文件 hash、validation 与 review 证据却被聚合为完成

## Non-goals

- 在本湖实现 L1–L8。
- 将合同失败静默改成允许。

## Freeze readiness

- [ ] Truth Review Gate pass
- [x] 用户确认 no-compat、lineage 与前向迁移语义（`user-confirmation-2026-07-27`）
