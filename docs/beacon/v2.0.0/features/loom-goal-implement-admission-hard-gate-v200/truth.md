---
slug: loom-goal-implement-admission-hard-gate-v200
version: v2.0.0
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "Loom parity of beacon-goal-implement-admission-hard-gate-v169 for dual-track QA/release"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-goal-implement-admission-hard-gate-v200/truth.md
  tests: docs/beacon/v2.0.0/features/loom-goal-implement-admission-hard-gate-v200/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-goal-implement-admission-hard-gate-v200/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-goal-implement-admission-hard-gate-v200/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parity_of: docs/beacon/v1.6.9/features/beacon-goal-implement-admission-hard-gate-v169/truth.md
ux_required: false
design_deferral: "No product UI for this platform lake"
---

# Requirement Truth: loom-goal-implement-admission-hard-gate-v200

## 人话

Loom goal implement admit 硬闸与 Beacon 同 AC。

# Loom parity: Goal Implement Admission Hard Gate

Same UD/AC as v1.6.9. Brand Loom / Rust track public surface; Python admit runtime shared.
Cross-ref: loom-git-worktree-implement-harness (W1 leaf + no main fallback).

## Intent

Loom/v2.0.0 parity of `beacon-goal-implement-admission-hard-gate-v169` — same UD/AC; brand Loom / Rust CLI track.

## Parity

`parity_of: docs/beacon/v1.6.9/features/beacon-goal-implement-admission-hard-gate-v169/truth.md`

## Acceptance Criteria
| AC ID | Description |
|----|-------------|
| AC-GIA-001 | tick --execute @ implement 无 feature → blocked goal_implement_feature_required |
| AC-GIA-002 | require=true 路径复用 run_workspace_admit；pass 后才 ralph |
| AC-GIA-003 | require=false 时 goal_forced_worktree + created/switched |
| AC-GIA-004 | 再次 admit/force → switched + merge 非 conflict |
| AC-GIA-005 | admit/force fail → 不设置 implement_delegate=ralph |
| AC-GIA-006 | execution log 含 implement_admission |
| AC-GIA-007 | 双轨 feature 包 v169+v200 |
| AC-GIA-008 | flow.md + gov-branch 登记 goal 硬闸 |

## Non-goals

- Duplicate Python runtime implementation under a second code path
- Auto-release

