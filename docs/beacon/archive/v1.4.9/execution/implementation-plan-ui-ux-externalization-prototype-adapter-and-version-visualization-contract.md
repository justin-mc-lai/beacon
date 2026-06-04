# Beacon Implementation Plan

- plan_id: `plan-ui-ux-externalization-prototype-adapter-and-version-visualization-contract-r3`
- feature: `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
- version: `v1.4.9`
- revision_id: `R3`
- baseline_hash: `sha256:2a3971da3e06d284679bcf7888a42a56a6098de9099b3529e1af9df955c4481d`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.9-ui-ux-externalization-prototype-adapter-and-version-visualization-contract-R3`
- delivery_baseline_source_hash: `sha256:56e99d17c34cb7cac644dfbce20482831a9436e4e8d3f03bfa3badbde54b55da`
- plan_hash: `sha256:3d6d208e9850b6381d3b8a3ff3ab5dbc6ae405c3e6318206749d3a74a5ce82d5`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.9/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
- prd: `docs/beacon/archive/v1.4.9/prd/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
- test_case: `docs/beacon/archive/v1.4.9/qa/test-cases/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
- revision_delta: `docs/beacon/archive/v1.4.9/.machine/execution/revision-delta-ui-ux-externalization-prototype-adapter-and-version-visualization-contract.json`
- ac_matrix: `docs/beacon/archive/v1.4.9/.machine/qa/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.9/.machine/qa/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.9/.machine/qa/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.9/.machine/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.json`
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
- plan_command: `beacon implement team-plan "ui-ux-externalization-prototype-adapter-and-version-visualization-contract" --project-root . --version v1.4.9`
- run_command: `beacon implement team-run "ui-ux-externalization-prototype-adapter-and-version-visualization-contract" --project . --version v1.4.9`
- dev_run_command: `beacon implement dev-run "ui-ux-externalization-prototype-adapter-and-version-visualization-contract" --project . --version v1.4.9`
- qa_team_command: `beacon qa team-run "ui-ux-externalization-prototype-adapter-and-version-visualization-contract" --project . --version v1.4.9`
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
- git_workflow_ref: `docs/beacon/archive/v1.4.9/.machine/execution/git-workflow-ui-ux-externalization-prototype-adapter-and-version-visualization-contract.json`

## Diagram Truth
- required: `True`
- ready: `True`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: ui_ux_route, adapter_binding, requirement_visualization, truth_binding
- review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding
- qa_coverage_hints: cover primary and alternate branch-flow paths, cover state transitions, illegal transitions, and recovery paths, cover conflicting conditions using declared decision priority, cover axis combinations across: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.9/research/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
- source_artifact: `docs/beacon/archive/v1.4.9/.machine/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.json`
- section_count: `2`
- architecture: `ui-ux-dev` owns UI/UX execution。 / Beacon owns requirement truth、gate、adapter binding、evidence closure。 / `prototype` owns accepted design result 的 requirement-facing adapter，不拥有设计生成。
- decision_priority: Beacon requirement truth 高于设计输出。 / `ui-ux-dev` 负责 UI/UX execution，Beacon 负责 governance。 / Accepted design result 必须进入 adapter binding，否则不能解锁 implementation。

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.9/.machine/execution/revision-delta-ui-ux-externalization-prototype-adapter-and-version-visualization-contract.json`

## Tasks

### ITASK-001 — FR-001 Beacon 必须停止扩张内部 UI/UX execution
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-UXEXT-001, TC-014, TC-015, TC-016, TC-017, TC-018, TC-019, TC-020, TC-021, TC-022, TC-UXEXT-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-UXEXT-001, TC-UXEXT-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-002 — FR-002 Beacon 必须把 UI/UX execution 请求路由到 `ui-ux-dev`
- status: `completed`
- mapped_ac_ids: AC-012, AC-003
- mapped_test_ids: TC-UXEXT-012, TC-UXEXT-003
- mapped_scenario_ids: SC-003, SC-012
- mapped_qa_case_ids: TC-UXEXT-003, TC-UXEXT-012
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-003 — FR-003 Beacon 不得在 `ui-ux-dev` 缺失时静默 fallback 到内建设计生成
- status: `completed`
- mapped_ac_ids: AC-004, AC-006, AC-005, AC-007, AC-008, AC-009, AC-010
- mapped_test_ids: TC-UXEXT-004, TC-UXEXT-006, TC-UXEXT-005, TC-UXEXT-007, TC-UXEXT-008, TC-UXEXT-009, TC-UXEXT-010
- mapped_scenario_ids: SC-004, SC-005, SC-006, SC-007, SC-008, SC-009, SC-010
- mapped_qa_case_ids: TC-UXEXT-004, TC-UXEXT-005, TC-UXEXT-006, TC-UXEXT-007, TC-UXEXT-008, TC-UXEXT-009, TC-UXEXT-010
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-004 — FR-004 Beacon 必须将 `prototype` 降级为 design-result adapter
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TC-UXEXT-011
- mapped_scenario_ids: SC-011
- mapped_qa_case_ids: TC-UXEXT-011
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-005 — FR-005 Beacon 必须阻断 accepted design result 未绑定 truth 的 implement
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-006 — FR-006 Beacon 必须保留历史 prototype bundle 兼容读取
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-007 — FR-007 Beacon 必须冻结版本级 business flow projection
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-008 — FR-008 Beacon 必须冻结版本级 state-machine projection
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-009 — FR-009 Beacon 必须冻结版本级 PRD / user-story / test-case map
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-010 — FR-010 每个 projection 必须声明 truth bindings
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-011 — FR-011 Requirement clarity 必须阻断缺失 visualization truth bindings
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding

### ITASK-012 — FR-012 Design review 必须保持 support surface 边界
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: implementation must cover the declared branch-flow split points, implementation must preserve the declared state-machine transitions, implementation must preserve decision-priority ordering, implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding
