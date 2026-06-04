# Beacon Implementation Plan

- plan_id: `plan-real-project-qa-evidence-binding-and-markdown-matrix-fail-closed-r2`
- feature: `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`
- version: `v1.4.9`
- revision_id: `R2`
- baseline_hash: `sha256:a8614520c1e4ced250e746005ffda519502886d03ccaec829b28c5e97b8a0065`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.9-real-project-qa-evidence-binding-and-markdown-matrix-fail-closed-R2`
- delivery_baseline_source_hash: `sha256:6d0a16e6258a72a10d26cdfa896c5243453160efaa900380127ce141e447443d`
- plan_hash: `sha256:9c423090298235ceeed0f33a90c6a6b6535916365cf49bea8a14d1c31189bed9`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.9/user-story/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- prd: `docs/beacon/archive/v1.4.9/prd/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- test_case: `docs/beacon/archive/v1.4.9/qa/test-cases/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- revision_delta: `docs/beacon/archive/v1.4.9/.machine/execution/revision-delta-real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.json`
- ac_matrix: `docs/beacon/archive/v1.4.9/.machine/qa/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.9/.machine/qa/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.9/.machine/qa/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.9/.machine/user-story/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.json`
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
- plan_command: `beacon implement team-plan "real-project-qa-evidence-binding-and-markdown-matrix-fail-closed" --project-root . --version v1.4.9`
- run_command: `beacon implement team-run "real-project-qa-evidence-binding-and-markdown-matrix-fail-closed" --project . --version v1.4.9`
- dev_run_command: `beacon implement dev-run "real-project-qa-evidence-binding-and-markdown-matrix-fail-closed" --project . --version v1.4.9`
- qa_team_command: `beacon qa team-run "real-project-qa-evidence-binding-and-markdown-matrix-fail-closed" --project . --version v1.4.9`
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
- git_workflow_ref: `docs/beacon/archive/v1.4.9/.machine/execution/git-workflow-real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.9/research/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- source_artifact: `docs/beacon/archive/v1.4.9/.machine/user-story/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.json`
- section_count: `1`
- decision_priority: Markdown QA truth beats generated fallback. / Explicit implementation evidence beats missing runtime state only after controlled import. / Project runner profile beats generic fallback command.

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.9/.machine/execution/revision-delta-real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.json`

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-RPQA-001, TC-RPQA-002, TC-RPQA-003, TC-RPQA-004
- mapped_scenario_ids: SC-001, SC-002, SC-003, SC-004
- mapped_qa_case_ids: TC-RPQA-001, TC-RPQA-002, TC-RPQA-003, TC-RPQA-004
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker

### ITASK-002 — FR-002 AC-001
- status: `completed`
- mapped_ac_ids: AC-004, AC-003, AC-005
- mapped_test_ids: TC-RPQA-006, TC-RPQA-005, TC-RPQA-007
- mapped_scenario_ids: SC-005, SC-006, SC-007
- mapped_qa_case_ids: TC-RPQA-005, TC-RPQA-006, TC-RPQA-007
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker

### ITASK-003 — FR-003 AC-002
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker

### ITASK-004 — FR-004 AC-002
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker

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
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker

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
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker

### ITASK-007 — FR-007 AC-005
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: implementation_evidence, markdown_matrix, runner_profile, qa_outcome, admission_blocker
