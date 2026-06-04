# Test Cases: Explicit Version Canonical Branch Worktree Preflight Gate

**Feature**: `explicit-version-canonical-branch-worktree-preflight-gate`
**Version**: `v1.4.10`
**Status**: `refreeze-input`
**Date**: `2026-05-25`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-EXVER-BRANCH-001 | preflight | `python3 -m pytest -q tests/test_v1410_explicit_version_branch_preflight.py -k "explicit_version_loads_execution_materials_before_mutation"` | Explicit version implement preflight loads `docs/beacon/<version>/execution/` before mutation is allowed. | `.beacon/evidence/test-results/explicit-version-canonical-branch-worktree-preflight-gate/TC-EXVER-BRANCH-001.json` |
| AC-002 | TC-EXVER-BRANCH-002 | contract | `python3 -m pytest -q tests/test_v1410_explicit_version_branch_preflight.py -k "branch_governance_git_workflow_and_deterministic_contract_are_sources"` | Branch governance, git workflow, and deterministic implementation contract materials are considered contract sources. | `.beacon/evidence/test-results/explicit-version-canonical-branch-worktree-preflight-gate/TC-EXVER-BRANCH-002.json` |
| AC-003 | TC-EXVER-BRANCH-003 | preflight | `python3 -m pytest -q tests/test_v1410_explicit_version_branch_preflight.py -k "target_service_branch_and_worktree_are_validated"` | Target service current branch and worktree are checked against the canonical service entry. | `.beacon/evidence/test-results/explicit-version-canonical-branch-worktree-preflight-gate/TC-EXVER-BRANCH-003.json` |
| AC-004 | TC-EXVER-BRANCH-004 | per-service | `python3 -m pytest -q tests/test_v1410_explicit_version_branch_preflight.py -k "per_service_expected_branch_resolves_map"` | `expected_branch=per-service` resolves the service branch/worktree map and does not pass as a literal branch. | `.beacon/evidence/test-results/explicit-version-canonical-branch-worktree-preflight-gate/TC-EXVER-BRANCH-004.json` |
| AC-005 | TC-EXVER-BRANCH-005 | fail-closed | `python3 -m pytest -q tests/test_v1410_explicit_version_branch_preflight.py -k "canonical_mismatch_blocks_before_code_edit_or_commit"` | Canonical branch/worktree mismatch blocks code edit and commit. | `.beacon/evidence/test-results/explicit-version-canonical-branch-worktree-preflight-gate/TC-EXVER-BRANCH-005.json` |
| AC-006 | TC-EXVER-BRANCH-006 | gate-order | `python3 -m pytest -q tests/test_v1410_explicit_version_branch_preflight.py -k "origin_master_ancestry_pass_does_not_override_canonical_mismatch"` | Passing `origin/master` ancestry cannot mark preflight pass when canonical branch/worktree mismatches. | `.beacon/evidence/test-results/explicit-version-canonical-branch-worktree-preflight-gate/TC-EXVER-BRANCH-006.json` |
| AC-007 | TC-EXVER-BRANCH-007 | regression | `python3 -m pytest -q tests/test_v1410_explicit_version_branch_preflight.py -k "rolo_v200_marketing_services_on_v135_branch_block"` | Rolo v2.0.0 `marketing_sys` and `marketing_primary_fe` on `feature/v1.3.5-truth-engine-cutover` block and recommend `feature/v2.0.0-all` worktrees. | `.beacon/evidence/test-results/explicit-version-canonical-branch-worktree-preflight-gate/TC-EXVER-BRANCH-007.json` |
| AC-008 | TC-EXVER-BRANCH-008 | output | `python3 -m pytest -q tests/test_v1410_explicit_version_branch_preflight.py -k "blocked_output_names_expected_branch_and_worktree"` | Blocked output includes reason codes and expected canonical branch/worktree recommendations. | `.beacon/evidence/test-results/explicit-version-canonical-branch-worktree-preflight-gate/TC-EXVER-BRANCH-008.json` |

## Explicit Non Coverage

- These tests do not execute Rolo service code changes.
- These tests do not repair wrong-branch commits.
- These tests do not replace formal implementation, QA, release, or deployment validation.
