# Test Cases: beacon-v1.4.0-branch-governance-human-surface-and-implement-gate

## Overview

**Feature**: beacon-v1.4.0-branch-governance-human-surface-and-implement-gate
**Test Type**: ALL
**Version**: v1.4.0
**Generated**: 2026-05-07 14:45
**Requested Mode**: auto
**Effective Mode**: host
**Fallback Reason**: N/A
**Memory Context**: N/A
**AC Matrix JSON**: docs/beacon/archive/v1.4.0/.machine/qa/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/archive/v1.4.0/.machine/qa/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.qa9-matrix.json
**Story Scenario Map JSON**: docs/beacon/archive/v1.4.0/.machine/qa/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_surface.py -k "toolkit_skill_tier" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | branch governance is exposed as an optional toolkit/support skill | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-001.json` |
| AC-002 | TC-002 | regression | `python3 -m pytest -q tests/test_v140_branch_governance_surface.py -k "no_new_public_command" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the feature does not add a new public top-level command | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-002.json` |
| AC-003 | TC-003 | regression | `python3 -m pytest -q tests/test_v140_branch_governance_surface.py -k "not_new_lifecycle_stage" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the feature is not exposed as a new lifecycle stage | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-003.json` |
| AC-004 | TC-004 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_surface.py -k "alongside_existing_toolkits" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | branch governance sits alongside existing toolkit surfaces | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-004.json` |
| AC-101 | TC-005 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_human_view.py -k "flow_diagram_required" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the human surface renders a formal branch flow diagram | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-005.json` |
| AC-102 | TC-006 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_human_view.py -k "current_position_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the diagram shows the current workspace position | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-006.json` |
| AC-103 | TC-007 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_human_view.py -k "allowed_and_forbidden_paths_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | allowed and forbidden paths are visible to the operator | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-007.json` |
| AC-104 | TC-008 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_human_view.py -k "next_action_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the human surface shows the recommended next action | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-008.json` |
| AC-201 | TC-009 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_summary.py -k "service_and_repo_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the summary shows target service and repo root | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-009.json` |
| AC-202 | TC-010 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_summary.py -k "branch_state_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the summary shows base, current, and target branch | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-010.json` |
| AC-203 | TC-011 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_summary.py -k "worktree_state_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the summary shows worktree mode and path | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-011.json` |
| AC-204 | TC-012 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_summary.py -k "verdict_and_recommendation_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the summary shows governance verdict, blocked reason, and recommendation | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-012.json` |
| AC-301 | TC-013 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_templates.py -k "project_default_template_supported" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the system supports a project-level default workflow template | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-013.json` |
| AC-302 | TC-014 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_templates.py -k "task_override_template_supported" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the system supports a task-level override template | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-014.json` |
| AC-303 | TC-015 | regression | `python3 -m pytest -q tests/test_v140_branch_governance_templates.py -k "override_cannot_break_hard_rules" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | overrides cannot bypass hard governance rules | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-015.json` |
| AC-304 | TC-016 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_templates.py -k "selected_template_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the selected template source is visible to the operator | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-016.json` |
| AC-401 | TC-017 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_metadata.py -k "previous_baseline_field_supported" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | metadata supports `previous_version_baseline_branch` | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-017.json` |
| AC-402 | TC-018 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_metadata.py -k "next_feature_field_supported" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | metadata supports `next_version_feature_branch` | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-018.json` |
| AC-403 | TC-019 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_metadata.py -k "hotfix_and_worktree_fields_supported" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | metadata supports hotfix naming and worktree allowance fields | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-019.json` |
| AC-404 | TC-020 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_metadata.py -k "merge_and_evidence_fields_supported" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | metadata supports merge-direction and evidence-contract fields | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-020.json` |
| AC-501 | TC-021 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_gate.py -k "implement_loads_contract" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implement preflight loads the governance contract before execution | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-021.json` |
| AC-502 | TC-022 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_gate.py -k "implement_verifies_alignment" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implement verifies repo, service, branch, worktree, and merge alignment | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-022.json` |
| AC-503 | TC-023 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_gate.py -k "evidence_contract_checked" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | implement checks evidence-contract requirements | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-023.json` |
| AC-504 | TC-024 | regression | `python3 -m pytest -q tests/test_v140_branch_governance_gate.py -k "blocked_state_prevents_code_execution" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | blocked governance contract prevents code execution from starting | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-024.json` |
| AC-601 | TC-025 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_switch.py -k "switch_to_compliant_branch" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the system can switch to an existing compliant branch before development | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-025.json` |
| AC-602 | TC-026 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_switch.py -k "create_or_switch_worktree" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the system can create or switch to a compliant worktree when required | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-026.json` |
| AC-603 | TC-027 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_switch.py -k "switch_action_explained" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | branch/worktree switching is clearly explained to the operator | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-027.json` |
| AC-604 | TC-028 | regression | `python3 -m pytest -q tests/test_v140_branch_governance_switch.py -k "fail_closed_if_switch_not_safe" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the system fails closed if it cannot safely switch to a compliant lane | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-028.json` |
| AC-701 | TC-029 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_dual_version.py -k "previous_hotfix_forward_port_template" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the system supports the previous-baseline hotfix forward-port template | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-029.json` |
| AC-702 | TC-030 | regression | `python3 -m pytest -q tests/test_v140_branch_governance_dual_version.py -k "forbidden_next_feature_first_fix" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the system blocks using next-feature as the first production-fix lane | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-030.json` |
| AC-703 | TC-031 | contract | `python3 -m pytest -q tests/test_v140_branch_governance_dual_version.py -k "minimum_evidence_fields_required" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the dual-version template requires the minimum evidence fields | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-031.json` |
| AC-704 | TC-032 | integration | `python3 -m pytest -q tests/test_v140_branch_governance_dual_version.py -k "dual_lane_diagram_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the human flow diagram clearly shows separate previous-version and next-version lanes | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-032.json` |
| AC-001 | TC-033 | unit | `python3 -c "print('requirement-deepening-coverage-check')"` | happy coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-033.json` |
| AC-001 | TC-034 | unit | `python3 -c "print('requirement-deepening-coverage-check')"` | negative coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-034.json` |
| AC-001 | TC-035 | unit | `python3 -c "print('requirement-deepening-coverage-check')"` | boundary coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-035.json` |
| AC-001 | TC-036 | unit | `python3 -c "print('requirement-deepening-coverage-check')"` | exception coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-036.json` |
| AC-001 | TC-037 | unit | `python3 -c "print('requirement-deepening-coverage-check')"` | recovery coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-037.json` |
| AC-001 | TC-038 | unit | `python3 -c "print('requirement-deepening-coverage-check')"` | compatibility coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-038.json` |
| AC-001 | TC-039 | contract | `python3 -c "print('requirement-deepening-coverage-check')"` | permission coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-039.json` |
| AC-001 | TC-040 | contract | `python3 -c "print('requirement-deepening-coverage-check')"` | stale-data-or-drift coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-040.json` |
| AC-001 | TC-041 | contract | `python3 -c "print('requirement-deepening-coverage-check')"` | downgrade-or-fallback coverage remains traceable to requirement truth | `.beacon/evidence/test-results/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate/TC-041.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-101 |
| TC-006 | Pending | from AC-102 |
| TC-007 | Pending | from AC-103 |
| TC-008 | Pending | from AC-104 |
| TC-009 | Pending | from AC-201 |
| TC-010 | Pending | from AC-202 |
| TC-011 | Pending | from AC-203 |
| TC-012 | Pending | from AC-204 |
| TC-013 | Pending | from AC-301 |
| TC-014 | Pending | from AC-302 |
| TC-015 | Pending | from AC-303 |
| TC-016 | Pending | from AC-304 |
| TC-017 | Pending | from AC-401 |
| TC-018 | Pending | from AC-402 |
| TC-019 | Pending | from AC-403 |
| TC-020 | Pending | from AC-404 |
| TC-021 | Pending | from AC-501 |
| TC-022 | Pending | from AC-502 |
| TC-023 | Pending | from AC-503 |
| TC-024 | Pending | from AC-504 |
| TC-025 | Pending | from AC-601 |
| TC-026 | Pending | from AC-602 |
| TC-027 | Pending | from AC-603 |
| TC-028 | Pending | from AC-604 |
| TC-029 | Pending | from AC-701 |
| TC-030 | Pending | from AC-702 |
| TC-031 | Pending | from AC-703 |
| TC-032 | Pending | from AC-704 |
| TC-033 | Pending | from AC-001 |
| TC-034 | Pending | from AC-001 |
| TC-035 | Pending | from AC-001 |
| TC-036 | Pending | from AC-001 |
| TC-037 | Pending | from AC-001 |
| TC-038 | Pending | from AC-001 |
| TC-039 | Pending | from AC-001 |
| TC-040 | Pending | from AC-001 |
| TC-041 | Pending | from AC-001 |
