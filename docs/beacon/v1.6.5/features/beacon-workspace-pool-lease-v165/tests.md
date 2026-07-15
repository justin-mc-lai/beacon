---
slug: beacon-workspace-pool-lease-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.5/features/beacon-workspace-pool-lease-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Workspace Pool Lease v1.6.5

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|---|---|---|---|---|
| AC-001 | TC-WP-001 | contract | `python3 -m pytest tests/test_v165_workspace_pool_lease.py::test_pooled_contract_resolution -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Metadata/admission contract normalizes `pooled` worktree mode and resolves the expected pool path. |
| AC-002 | TC-WP-002 | contract | `python3 -m pytest tests/test_v165_workspace_pool_lease.py::test_admit_reuses_released_pool_entry -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | First admit creates the pool entry, release marks it available, second admit reuses the same worktree path. |
| AC-003 | TC-WP-003 | contract | `python3 -m pytest tests/test_v165_workspace_pool_lease.py::test_pool_entry_schema -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Pool entry includes state, feature, branch, path, holder, lease timestamps, release timestamp, and git head fields. |
| AC-004 | TC-WP-004 | cli | `python3 -m pytest tests/test_v165_workspace_pool_lease.py::test_workspace_release_marks_available_without_delete -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Workspace release changes state to released/available and leaves the worktree directory present. |
| AC-005 | TC-WP-005 | contract | `python3 -m pytest tests/test_v165_workspace_pool_lease.py::test_foreign_active_lease_blocks_admit -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | A different holder cannot acquire an active lease; payload contains `workspace_pool_lease_in_use`. |
| AC-006 | TC-WP-006 | contract | `python3 -m pytest tests/test_v165_workspace_pool_lease.py::test_corrupt_pool_state_fails_closed -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Corrupt pool state blocks with `workspace_pool_state_corrupt` and does not overwrite state. |
| AC-007 | TC-WP-007 | regression | `python3 -m pytest tests/test_v162_workspace_admit.py tests/test_v162_workspace_integration.py tests/test_v165_workspace_pool_lease.py::test_dedicated_mode_remains_compatible -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Existing dedicated admission behavior still passes and pooled code does not change dedicated artifacts. |

## Verification Notes

- Tests use temporary git repositories and do not depend on the developer's current branch.
- Pool state is runtime state, not requirement truth.
- Each test must assert reason codes and state transitions directly.
