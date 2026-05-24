# Beacon Implementation Plan

- plan_id: `plan-qa-evo-deep-evidence-bound-ac-aware-closure-r3`
- feature: `qa-evo-deep-evidence-bound-ac-aware-closure`
- version: `v1.4.10`
- revision_id: `R3`
- baseline_hash: `sha256:5dd1907cb644e00b1aa245d02d80c66fb7a0ecff53ca7262125f46574d5e1cf8`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.10-qa-evo-deep-evidence-bound-ac-aware-closure-R3`
- delivery_baseline_source_hash: `sha256:0495c5b289b958a2bfe9a0de084ae4f26d3db15eae67efc42558a072ae2a3dfd`
- plan_hash: `sha256:38516850b0d0e022ba5ce9099532ebfdb148299cd91104fe168a6aa99690243f`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.10/user-story/qa-evo-deep-evidence-bound-ac-aware-closure.md`
- prd: `docs/beacon/v1.4.10/prd/qa-evo-deep-evidence-bound-ac-aware-closure.md`
- test_case: `docs/beacon/v1.4.10/qa/test-cases/qa-evo-deep-evidence-bound-ac-aware-closure.md`
- revision_delta: `docs/beacon/v1.4.10/.machine/execution/revision-delta-qa-evo-deep-evidence-bound-ac-aware-closure.json`
- ac_matrix: `docs/beacon/v1.4.10/.machine/qa/qa-evo-deep-evidence-bound-ac-aware-closure.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.10/.machine/qa/qa-evo-deep-evidence-bound-ac-aware-closure.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.10/.machine/qa/qa-evo-deep-evidence-bound-ac-aware-closure.qa9-matrix.json`
- research_projection: `docs/beacon/v1.4.10/.machine/user-story/qa-evo-deep-evidence-bound-ac-aware-closure.json`
- architecture_blueprint: `docs/beacon/v1.4.10/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "qa-evo-deep-evidence-bound-ac-aware-closure" --project-root . --version v1.4.10`
- run_command: `beacon implement team-run "qa-evo-deep-evidence-bound-ac-aware-closure" --project . --version v1.4.10`
- dev_run_command: `beacon implement dev-run "qa-evo-deep-evidence-bound-ac-aware-closure" --project . --version v1.4.10`
- qa_team_command: `beacon qa team-run "qa-evo-deep-evidence-bound-ac-aware-closure" --project . --version v1.4.10`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.10`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.4.10/.machine/execution/git-workflow-qa-evo-deep-evidence-bound-ac-aware-closure.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

## Research Projection
- present: `True`
- source: `research:docs/beacon/v1.4.10/research/qa-evo-deep-evidence-bound-ac-aware-closure.md`
- source_artifact: `docs/beacon/v1.4.10/.machine/user-story/qa-evo-deep-evidence-bound-ac-aware-closure.json`
- section_count: `4`
- architecture: Read frozen requirement truth: / PRD / user-story
- business_flow: Operator runs `beacon qa evo-deep "<feature>" --project . --version <version>`. / Beacon loads frozen requirement truth and current QA evidence for that feature. / If any required source is missing, Beacon returns a blocked admission with the missing surface and route recommendation.
- state_machine: `source_evidence_state` / `finding_binding_state` / `blocked_admission_state`
- decision_priority: Authority bypass blocks first. / Missing source evidence blocks readiness. / Empty AC/evidence binding blocks readiness.

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.4.10/.machine/execution/revision-delta-qa-evo-deep-evidence-bound-ac-aware-closure.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-QAED-BIND-001, TC-QAED-BIND-002, TC-QAED-BIND-003
- mapped_scenario_ids: SC-001, SC-002, SC-003
- mapped_qa_case_ids: TC-QAED-BIND-001, TC-QAED-BIND-002, TC-QAED-BIND-003
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-002 — FR-002 AC-001
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-QAED-BIND-004, TC-QAED-BIND-005
- mapped_scenario_ids: SC-004, SC-005
- mapped_qa_case_ids: TC-QAED-BIND-004, TC-QAED-BIND-005
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-003 — FR-003 AC-002
- status: `completed`
- mapped_ac_ids: AC-005, AC-004, AC-007, AC-006
- mapped_test_ids: TC-QA-ABSORB-001, TC-SKEV-REPLAY-001, TC-SKEV-REPLAY-002, TC-QAED-BIND-006, TC-REL-SUPP-001
- mapped_scenario_ids: SC-006, SC-007, SC-008, SC-009, SC-010
- mapped_qa_case_ids: TC-SKEV-REPLAY-001, TC-SKEV-REPLAY-002, TC-QA-ABSORB-001, TC-REL-SUPP-001, TC-QAED-BIND-006
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-004 — FR-004 AC-003
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-005 — FR-005 AC-003
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-006 — FR-006 AC-004
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-007 — FR-007 AC-004
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-008 — FR-008 AC-005
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-009 — FR-009 AC-006
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary

### ITASK-010 — FR-010 AC-007
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: source_evidence_state, finding_binding_state, blocked_admission_state, skill_eval_replay_state, deep_absorption_state, release_supplement_state, authority_boundary
