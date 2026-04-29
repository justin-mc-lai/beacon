# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility-r1`
- feature: `Beacon v1.3.9 agents robustness and host runtime compatibility`
- version: `v1.3.9`
- revision_id: `R1`
- baseline_hash: `sha256:50a177b70475b07947572b1e60088b31af7f19baf28764619c78f6b097ed723d`
- delivery_baseline_id: `impl-delivery-baseline-v1.3.9-beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility-R1`
- delivery_baseline_source_hash: `sha256:e0728f2aae69d55dc63326576c711a83a4667673f78ba700ad60d8e0d1635672`
- plan_hash: `sha256:675f69c4e6eadcd919b4d26650b1745c3cbf87c63bd57bb6b2dd8c9f4e3725c1`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
- prd: `docs/beacon/v1.3.9/prd/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
- test_case: `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
- architecture_blueprint: `docs/beacon/v1.3.9/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "Beacon v1.3.9 agents robustness and host runtime compatibility" --project-root . --version v1.3.9`
- run_command: `beacon implement team-run "Beacon v1.3.9 agents robustness and host runtime compatibility" --project . --version v1.3.9`
- dev_run_command: `beacon implement dev-run "Beacon v1.3.9 agents robustness and host runtime compatibility" --project . --version v1.3.9`
- qa_team_command: `beacon qa team-run "Beacon v1.3.9 agents robustness and host runtime compatibility" --project . --version v1.3.9`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.3.9`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.3.9/.machine/execution/git-workflow-beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available

## Tasks

### ITASK-001 — FR-001 AC-001
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available

### ITASK-002 — FR-002 AC-002
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available

### ITASK-003 — FR-003 AC-003
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available

### ITASK-004 — FR-004 AC-004
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available

### ITASK-005 — FR-005 AC-005
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available

### ITASK-006 — FR-006 AC-006
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available

### ITASK-007 — FR-007 AC-007
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available

### ITASK-008 — FR-008 AC-008
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: host_runtime_axis, codex, claude, lifecycle_surface_axis, implement, qa, release-support, doctor, archive-validation, agent_contract_axis, run-contract, handoff-envelope, guardrail-taxonomy, trace-projection, session-resume, human-surface-axis, minimal-human-surface-preserved, runtime-detail-hidden, explanation-projection-available
