# Beacon Implementation Plan

- plan_id: `plan-read-only-support-research-write-topology-gate-contract-r3`
- feature: `read-only-support-research-write-topology-gate-contract`
- version: `v1.4.9`
- revision_id: `R3`
- baseline_hash: `sha256:3305b84807ac9950ee5619ccf9d3c57ad87bbc26047a7e75389b39834fd663a5`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.9-read-only-support-research-write-topology-gate-contract-R3`
- delivery_baseline_source_hash: `sha256:87a9f1e6d800c84925f6f25f3c7af6a550b2aeb1f25135f22cd9210a4e8df23f`
- plan_hash: `sha256:c013eb80b394336ac9ce33a7c90c6614914c25baf290ffdeac643acf3fbb1e2a`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.9/user-story/read-only-support-research-write-topology-gate-contract.md`
- prd: `docs/beacon/archive/v1.4.9/prd/read-only-support-research-write-topology-gate-contract.md`
- test_case: `docs/beacon/archive/v1.4.9/qa/test-cases/read-only-support-research-write-topology-gate-contract.md`
- revision_delta: `docs/beacon/archive/v1.4.9/.machine/execution/revision-delta-read-only-support-research-write-topology-gate-contract.json`
- ac_matrix: `docs/beacon/archive/v1.4.9/.machine/qa/read-only-support-research-write-topology-gate-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.9/.machine/qa/read-only-support-research-write-topology-gate-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.9/.machine/qa/read-only-support-research-write-topology-gate-contract.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.9/.machine/user-story/read-only-support-research-write-topology-gate-contract.json`
- architecture_blueprint: `docs/beacon/archive/v1.4.9/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "read-only-support-research-write-topology-gate-contract" --project-root . --version v1.4.9`
- run_command: `beacon implement team-run "read-only-support-research-write-topology-gate-contract" --project . --version v1.4.9`
- dev_run_command: `beacon implement dev-run "read-only-support-research-write-topology-gate-contract" --project . --version v1.4.9`
- qa_team_command: `beacon qa team-run "read-only-support-research-write-topology-gate-contract" --project . --version v1.4.9`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.9`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.4.9/.machine/execution/git-workflow-read-only-support-research-write-topology-gate-contract.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: support_surface_class, write_target, material_effect, adoption_status, version_lineage
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: support_surface_class, write_target, material_effect, adoption_status, version_lineage

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.9/research/read-only-support-research-write-topology-gate-contract.md`
- source_artifact: `docs/beacon/archive/v1.4.9/.machine/user-story/read-only-support-research-write-topology-gate-contract.json`
- section_count: `2`
- architecture: Ordinary support review surfaces write one owned section in `research/<feature>.md`. / `beacon-deep` writes detailed artifacts in `deep/<feature>/`; research stores only `Deep Summary`. / `beacon-learn` writes learning audit in `learning/<feature>.md` or transaction; research stores only `Learning Influence Summary`.
- decision_priority: Version-bound and feature-bound support output must use governed feature topology. / Ordinary support review must upsert one section in `research/<feature>.md`. / `docs/brainstorms/` is not a fallback target. It is allowed only for unbound scratch, external analysis, or explicit scratch output.

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.9/.machine/execution/revision-delta-read-only-support-research-write-topology-gate-contract.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-ROSUP-001, TC-ROSUP-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-ROSUP-001, TC-ROSUP-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-ROSUP-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-ROSUP-003
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-ROSUP-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-ROSUP-004
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-008, AC-005
- mapped_test_ids: TC-ROSUP-008, TC-ROSUP-005
- mapped_scenario_ids: SC-005, SC-008
- mapped_qa_case_ids: TC-ROSUP-005, TC-ROSUP-008
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-ROSUP-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-ROSUP-006
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage

### ITASK-006 — FR-006 AC-006
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-ROSUP-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: TC-ROSUP-007
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage

### ITASK-007 — FR-007 AC-007
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage

### ITASK-008 — FR-008 AC-008
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: support_surface_class, write_target, material_effect, adoption_status, version_lineage
