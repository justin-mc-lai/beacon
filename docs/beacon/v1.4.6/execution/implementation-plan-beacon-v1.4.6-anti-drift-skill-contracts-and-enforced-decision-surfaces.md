# Beacon Implementation Plan

- plan_id: `plan-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces-r1`
- feature: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- version: `v1.4.6`
- revision_id: `R1`
- baseline_hash: `sha256:ea2b377cfba803c97b63c0156e9c399ad0bec00483c43f909fa6fd33d0c35292`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.6-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces-R1`
- delivery_baseline_source_hash: `sha256:e33ff59e0ed6ca40796f0a2feb2c5e9164738fafb584975b8899fc7ae2f5c64f`
- plan_hash: `sha256:ebc9de11d8bdf666c3c173cf30317b129817af808220649f4cd40a63c116f934`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.4.6/user-story/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- prd: `docs/beacon/v1.4.6/prd/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- test_case: `docs/beacon/v1.4.6/qa/test-cases/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- ac_matrix: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.story-scenario-map.json`
- qa9_matrix: `docs/beacon/v1.4.6/.machine/qa/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.qa9-matrix.json`
- research_projection: `docs/beacon/v1.4.6/.machine/user-story/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.json`
- architecture_blueprint: `docs/beacon/v1.4.6/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces" --project-root . --version v1.4.6`
- run_command: `beacon implement team-run "beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces" --project . --version v1.4.6`
- dev_run_command: `beacon implement dev-run "beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces" --project . --version v1.4.6`
- qa_team_command: `beacon qa team-run "beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces" --project . --version v1.4.6`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.6`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.4.6/.machine/execution/git-workflow-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:docs/beacon/v1.4.6/research/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- source_artifact: `docs/beacon/v1.4.6/.machine/user-story/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.json`
- section_count: `0`

## Tasks

### ITASK-001 — FR-001 Beacon 必须冻结 `Skill Anatomy v2`
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-ADRIFT46-001, TC-011, TC-012, TC-013, TC-014, TC-015, TC-016, TC-017, TC-018, TC-019
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-ADRIFT46-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 Beacon 必须把 anti-rationalization 提升为关键 skill 的强制内容
- status: `completed`
- mapped_ac_ids: AC-002, AC-003
- mapped_test_ids: TC-ADRIFT46-002, TC-ADRIFT46-003
- mapped_scenario_ids: SC-002, SC-003
- mapped_qa_case_ids: TC-ADRIFT46-002, TC-ADRIFT46-003
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 Beacon 必须冻结 support surface 的统一 contract boundary
- status: `completed`
- mapped_ac_ids: AC-010, AC-004
- mapped_test_ids: TC-ADRIFT46-010, TC-ADRIFT46-004
- mapped_scenario_ids: SC-004, SC-010
- mapped_qa_case_ids: TC-ADRIFT46-004, TC-ADRIFT46-010
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 Beacon 必须引入受治理的 high-risk decision challenge contract
- status: `completed`
- mapped_ac_ids: AC-005, AC-006, AC-008
- mapped_test_ids: TC-ADRIFT46-005, TC-ADRIFT46-006, TC-ADRIFT46-008
- mapped_scenario_ids: SC-005, SC-006, SC-008
- mapped_qa_case_ids: TC-ADRIFT46-005, TC-ADRIFT46-006, TC-ADRIFT46-008
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 Beacon 必须把 decision challenge 与 evidence/state/gate 面连接起来
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-ADRIFT46-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: TC-ADRIFT46-007
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 Beacon 必须冻结 orchestration constitution
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TC-ADRIFT46-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-ADRIFT46-009
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — FR-007 Beacon 必须把关键 anti-drift contract 提升为 machine-checkable checks
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — FR-008 Beacon 必须保持 philosophy-first，而不是滑向 script-first
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — FR-009 Beacon 必须允许把外部开源方法蒸馏为内部 contract，而不是 runtime dependency
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — FR-010 Beacon 必须让 `brainstorm -> change/prd` promotion 边界更明确
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
