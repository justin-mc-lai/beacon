---
slug: beacon-git-scope-graph-v167
version: v1.6.7
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-git-scope-graph-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Git Scope Graph v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-GSG-001 | TC-GSG-001 | contract | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_schema_minimum_fields -q` | git-scope-graph.v1 字段齐全 |
| AC-GSG-002 | TC-GSG-002 | regression | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_single_repo_equivalent_to_v166 -q` | single_repo 等价 v1.6.6 admission |
| AC-GSG-003 | TC-GSG-003 | negative | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_monorepo_dirty_service_blocks -q` | monorepo dirty → blocked |
| AC-GSG-004 | TC-GSG-004 | negative | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_multi_git_satellite_blocked -q` | 卫星仓 blocked 汇总 blocked |
| AC-GSG-005 | TC-GSG-005 | regression | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_program_level_profile_sidepilot -q` | program-level profile 回归 |
| AC-GSG-006 | TC-GSG-006 | integration | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_topology_resolve_cli_writes_artifact -q` | topology-resolve 写 artifact |
| AC-GSG-007 | TC-GSG-007 | contract | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_precheck_bundle_includes_topology_gate -q` | verification bundle 含 topology_gate |
| AC-GSG-008 | TC-GSG-008 | contract | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_loop_goal_rejects_missing_topology_ref -q` | 无 topology ref 拒绝 pass |
| AC-GSG-009 | TC-GSG-009 | contract | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_v2_branch_context_parity_fixture -q` | v2 parity fixture 可加载 |
| AC-GSG-010 | TC-GSG-010 | integration | `python3 -m pytest tests/test_v167_git_scope_graph.py::test_git_scopes_ledger_projection -q` | runtime-ledger git_scopes 投影 |

## Verification Notes

- Test module `tests/test_v167_git_scope_graph.py`.
- Fixtures: single_repo, monorepo dirty, multi_git satellite blocked, program-level SidePilot profile.
