---
slug: beacon-global-workspace-git-admission-v162
version: v1.6.4
status: draft
revision_id: R7
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-global-workspace-git-admission-v162/truth.md
parser_contract: beacon-feature-package-v1
---

# Tests: Workspace Admission Nested-Ref Coexistence R7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-023 | TC-R6-001 | unit | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_program_topology_without_git_workflow_resolves_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Frozen program topology without `git-workflow-*.md` resolves lake to program-level aggregation branch/worktree. |
| AC-023 | TC-R6-002 | integration | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_program_topology_without_version_governance_block_resolves_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Absent version governance block still resolves from frozen program topology. |
| AC-024 | TC-R6-003 | unit | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_program_topology_with_git_workflow_resolves_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Explicit `git-workflow-*.md` program-level contract continues to resolve aggregation branch/worktree. |
| AC-025 | TC-R6-004 | integration | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_qa_run_lake_accepts_aggregation_branch_after_admission -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `beacon qa run <lake>` accepts aggregation branch after admission. |
| AC-026 | TC-R6-005 | regression | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_ac022_per_feature_default_unchanged -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | No program-level contract/topology keeps per-feature default. |
| AC-027 | TC-R6-006 | integration | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_soft_admission_still_blocks_wrong_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Soft admission blocks wrong branch with `branch_alignment_required`. |
| AC-028 | TC-R7-001 | unit | `python3 -m pytest tests/test_v164_git_admission_nested_ref_r7.py::test_r7_nested_child_refs_select_non_conflicting_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | When `beacon/<version>/<slug>` children exist, resolver selects `beacon/<version>/_agg` (or governance override), not bare `beacon/<version>`. |
| AC-029 | TC-R7-002 | unit | `python3 -m pytest tests/test_v164_git_admission_nested_ref_r7.py::test_r7_per_feature_deterministic_contract_is_not_program_level -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Per-feature deterministic contract with `target_branch`+`worktree_root` resolves `branch_resolution_mode=per-feature`. |
| AC-030 | TC-R7-003 | unit | `python3 -m pytest tests/test_v164_git_admission_nested_ref_r7.py::test_r7_aggregation_worktree_not_primary_checkout -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Program-level worktree resolves under `.beacon/worktrees/<version>`, not primary checkout. |
| AC-031 | TC-R7-004 | integration | `python3 -m pytest tests/test_v164_git_admission_nested_ref_r7.py::test_r7_nested_ref_conflict_reason_code -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Nested parent/child ref failure emits `aggregation_branch_nested_ref_conflict`. |

## Verification Notes

- R6 coverage remains authoritative for AC-023..AC-027.
- R7 adds focused nested-ref / contract-authority coverage in `tests/test_v164_git_admission_nested_ref_r7.py`.
- Full focused command: `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py tests/test_v164_git_admission_nested_ref_r7.py -q`.

## Must vs Should

| Priority | AC |
|----------|----|
| Must | AC-023..AC-031 |
