---
slug: beacon-global-workspace-git-admission-v162
version: v1.6.4
status: draft
revision_id: R6
language: zh
truth_ref: docs/beacon/archive/v1.6.4/features/beacon-global-workspace-git-admission-v162/truth.md
parser_contract: beacon-feature-package-v1
---

# Tests: Workspace Admission Program/Lake Branch Governance R6

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-023 | TC-R6-001 | unit | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_program_topology_without_git_workflow_resolves_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Frozen program topology without `git-workflow-*.md` resolves lake `content-hub-foundation` to `branch_resolution_mode=program-level`, `feature_branch=beacon/v0.0.12`, and the program aggregation worktree. |
| AC-023 | TC-R6-002 | integration | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_program_topology_without_version_governance_block_resolves_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | When the version governance block is absent and no `git-workflow-*.md` exists, frozen program topology still resolves the lake to `beacon/v0.0.12` and validates on the aggregation worktree. |
| AC-024 | TC-R6-003 | unit | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_program_topology_with_git_workflow_resolves_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Explicit `git-workflow-*.md` program-level contract continues to resolve the same aggregation branch/worktree. |
| AC-025 | TC-R6-004 | integration | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_qa_run_lake_accepts_aggregation_branch_after_admission -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `beacon qa run <lake>` passes workspace admission on `beacon/v0.0.12`; the controlled downstream block is `implementation_not_recorded`, not `branch_alignment_required`. |
| AC-026 | TC-R6-005 | regression | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_ac022_per_feature_default_unchanged -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | No program-level contract/topology keeps per-feature default `beacon/v9.9.9/demo-feature`. |
| AC-027 | TC-R6-006 | integration | `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py::test_r6_soft_admission_still_blocks_wrong_aggregation_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `require_workspace_admission=false` on wrong current branch blocks with `branch_alignment_required` against aggregation target `beacon/v0.0.12`. |

## Verification Notes

- TC-R6-003 does not issue a QA verdict. It controls downstream QA gates so the assertion stays on workspace admission truth.
- R5 regression coverage remains in `tests/test_v162_delivery_program_branch_r5.py` to ensure delivery-repo program-level behavior is not regressed.
- The full focused contract command is `python3 -m pytest tests/test_v162_delivery_program_branch_r5.py -q`.

## Must vs Should

| Priority | AC |
|----------|----|
| Must | AC-023..AC-027 |
