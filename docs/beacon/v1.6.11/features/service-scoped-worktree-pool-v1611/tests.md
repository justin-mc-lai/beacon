---
slug: service-scoped-worktree-pool-v1611
version: v1.6.11
revision_id: R0
materials_status: current
---

# Tests: Service-scoped Worktree Pool

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-SSP-001 | AC-SSP-001 | `python3 -m pytest -q tests/test_v1611_service_scoped_worktree_pool.py::test_governance_uses_explicit_primary_and_stable_service_roots --tb=no` | multi-git governance contains explicit primary root, service repo roots are stable, and any `.worktrees/feature-*` service binding is reported as migration input rather than accepted as global truth |
| TC-SSP-002 | AC-SSP-002 | `python3 -m pytest -q tests/test_v1611_service_scoped_worktree_pool.py::test_metadata_verify_accepts_multi_git_workspace_and_primary_role --tb=no` | parser/render/doctor preserve role=primary, accept `multi_git_workspace`, and do not derive primary from the first service binding |
| TC-SSP-003 | AC-SSP-003 | `python3 -m pytest -q tests/test_v1611_service_scoped_worktree_pool.py::test_workspace_pool_v2_parent_and_service_lease_lifecycle --tb=no` | admit writes parent + services lease entries, release marks all leases released without deleting directories, and corrupt state fails closed |
| TC-SSP-004 | AC-SSP-004 | `python3 -m pytest -q tests/test_v1611_service_scoped_worktree_pool.py::test_implement_admission_materializes_every_participating_service_worktree --tb=no` | multi-git implement admission creates real service worktrees for all participating writable services using per-service branch, per-service baseline and governed path pattern |
| TC-SSP-005 | AC-SSP-005 | `python3 -m pytest -q tests/test_v1611_service_scoped_worktree_pool.py::test_topology_gate_and_write_guard_reject_parent_only_service_write --tb=no` | GitScopeGraph records explicit primary + service scopes, write guard blocks parent-only service writes, and branch/cwd/head/baseline mismatch blocks dispatch |
| TC-SSP-006 | AC-SSP-006 | `python3 -m pytest -q tests/test_v1611_service_scoped_worktree_pool.py::test_rolo_v233_v234_fixture_topology_resolve --tb=no` | Rolo fixture resolves v2.3.3/v2.3.4 with root primary, exact participating service map, and no first-service `workspace_admission_cwd_mismatch` |
| TC-SSP-007 | AC-SSP-007 | `python3 -m pytest -q tests/test_v165_workspace_pool_lease.py tests/test_v167_git_scope_graph.py tests/test_v1610_unified_implement_admission.py --tb=no` | existing single_repo, dedicated-worktree, feature-level pooled lease, GitScopeGraph and unified implement admission regressions remain green |
| TC-SSP-ILLEGAL | AC-SSP-005 | `python3 -m pytest -q tests/test_v1611_service_scoped_worktree_pool.py::test_illegal_service_pool_transitions_fail_closed --tb=no` | skipped admission, mkdir-only service path, empty gitlink, parent-only write, bad baseline and old-shape compatibility attempts are rejected with reason codes |
