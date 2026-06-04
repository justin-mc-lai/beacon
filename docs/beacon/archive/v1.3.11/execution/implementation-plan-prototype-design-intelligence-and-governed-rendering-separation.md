# Beacon Implementation Plan

- plan_id: `plan-prototype-design-intelligence-and-governed-rendering-separation-r1`
- feature: `prototype-design-intelligence-and-governed-rendering-separation`
- version: `v1.3.11`
- revision_id: `R1`
- baseline_hash: `sha256:9fd8a2af005caa69e4ae7cd53cc06152d485160e8e2dd75cfb73bb8ff4f66979`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.11-prototype-design-intelligence-and-governed-rendering-separation-R1`
- delivery_baseline_source_hash: `sha256:c18319db14d159b5f063e98680391adb0b8c31a10c3e716293af2d2cf067c9fc`
- plan_hash: `sha256:0bbd2dc907030f0bd41e0fa011a0f4862f262605a9418cf58992dda91047e897`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.3.11/user-story/prototype-design-intelligence-and-governed-rendering-separation.md`
- prd: `docs/beacon/archive/v1.3.11/prd/prototype-design-intelligence-and-governed-rendering-separation.md`
- test_case: `docs/beacon/archive/v1.3.11/qa/test-cases/prototype-design-intelligence-and-governed-rendering-separation.md`
- ac_matrix: `docs/beacon/archive/v1.3.11/.machine/qa/prototype-design-intelligence-and-governed-rendering-separation.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.3.11/.machine/qa/prototype-design-intelligence-and-governed-rendering-separation.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.3.11/.machine/qa/prototype-design-intelligence-and-governed-rendering-separation.qa9-matrix.json`
- architecture_blueprint: `docs/beacon/archive/v1.3.11/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "prototype-design-intelligence-and-governed-rendering-separation" --project-root . --version v1.3.11`
- run_command: `beacon implement team-run "prototype-design-intelligence-and-governed-rendering-separation" --project . --version v1.3.11`
- dev_run_command: `beacon implement dev-run "prototype-design-intelligence-and-governed-rendering-separation" --project . --version v1.3.11`
- qa_team_command: `beacon qa team-run "prototype-design-intelligence-and-governed-rendering-separation" --project . --version v1.3.11`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.11`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.3.11/.machine/execution/git-workflow-prototype-design-intelligence-and-governed-rendering-separation.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Tasks

### ITASK-001 — FR-001 Design Intelligence Layer
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-001, TC-026, TC-027, TC-028, TC-029, TC-030, TC-031, TC-032, TC-033, TC-034, TC-035, TC-036, TC-037, TC-038, TC-039, TC-040, TC-041, TC-042, TC-043, TC-044, TC-045, TC-046, TC-047, TC-048, TC-049, TC-050, TC-051, TC-052, TC-053, TC-054, TC-055, TC-056, TC-057, TC-058, TC-059, TC-060, TC-061, TC-062, TC-063, TC-064, TC-065, TC-066, TC-067, TC-068, TC-069, TC-070, TC-071, TC-072, TC-073, TC-074, TC-075, TC-076, TC-077, TC-078, TC-079, TC-080, TC-081, TC-082, TC-083, TC-084, TC-085, TC-086, TC-002
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004, SC-006, SC-008
- mapped_qa_case_ids: TC-001, TC-002, TC-026, TC-027, TC-028, TC-029, TC-030, TC-031, TC-032
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 Design Skill Role Contract
- status: `completed`
- mapped_ac_ids: AC-005, AC-007
- mapped_test_ids: TC-025, TEST-007
- mapped_scenario_ids: SC-009, SC-010, SC-011, SC-012, SC-013
- mapped_qa_case_ids: TC-025
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 Prototype Design Artifact Contract
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003, TC-028
- mapped_scenario_ids: SC-005, SC-006
- mapped_qa_case_ids: TC-003, TC-028
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 Governed Rendering Contract
- status: `completed`
- mapped_ac_ids: AC-009, AC-004
- mapped_test_ids: TEST-009, TC-004, TC-029
- mapped_scenario_ids: SC-007, SC-008
- mapped_qa_case_ids: TC-004, TC-029
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 Production UI Copy Projection
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 First-Screen Projection Rule
- status: `completed`
- mapped_ac_ids: AC-015
- mapped_test_ids: TEST-015
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — FR-007 Prototype Review Gate
- status: `completed`
- mapped_ac_ids: AC-017
- mapped_test_ids: TEST-017
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — FR-008 Implement Consumption Contract
- status: `completed`
- mapped_ac_ids: AC-021, AC-008
- mapped_test_ids: TEST-021, TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — FR-009 Traceability
- status: `completed`
- mapped_ac_ids: AC-023, AC-010, AC-006, AC-011, AC-012, AC-014, AC-016, AC-018, AC-019, AC-020, AC-022, AC-024, AC-025
- mapped_test_ids: TEST-023, TEST-010, TEST-006, TEST-011, TEST-012, TEST-014, TEST-016, TEST-018, TEST-019, TEST-020, TEST-022, TEST-024, TEST-025
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
