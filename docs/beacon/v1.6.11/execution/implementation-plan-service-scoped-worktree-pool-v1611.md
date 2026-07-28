# Beacon Implementation Plan

- plan_id: `plan-service-scoped-worktree-pool-v1611-r1`
- feature: `service-scoped-worktree-pool-v1611`
- version: `v1.6.11`
- revision_id: `R1`
- baseline_hash: `sha256:d778f85de42ef2e1d125e57aa960224f135fb9e851d74e9d89cdcef68654fb70`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.11-service-scoped-worktree-pool-v1611-R1`
- delivery_baseline_source_hash: `sha256:a37ab411a0e6a88f5b21b840110813d0e5a7048b28c61faaeb81ddaa5f1da007`
- plan_hash: `sha256:ba99ff8e0834ae739f724eaa93306c443d14879cdfa7e1900a2c5cdc6ff09096`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/truth.md`
- prd: `docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/truth.md`
- test_case: `docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/tests.md`
- truth: `docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/truth.md`
- tests: `docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/tests.md`
- tasks: `docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/tasks.md`
- evidence: `docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.11/features/service-scoped-worktree-pool-v1611`
- story_scenario_map: `docs/beacon/v1.6.11/.machine/qa/service-scoped-worktree-pool-v1611.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.11/.machine/user-story/service-scoped-worktree-pool-v1611.json`
- architecture_blueprint: `docs/beacon/v1.6.11/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "service-scoped-worktree-pool-v1611" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.11`
- run_command: `beacon implement team-run "service-scoped-worktree-pool-v1611" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.11`
- dev_run_command: `beacon implement dev-run "service-scoped-worktree-pool-v1611" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.11`
- qa_team_command: `beacon qa team-run "service-scoped-worktree-pool-v1611" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.11`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.11/service-scoped-worktree-pool-v1611`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.11/.machine/execution/git-workflow-service-scoped-worktree-pool-v1611.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.11/research/service-scoped-worktree-pool-v1611.md`
- source_artifact: `docs/beacon/v1.6.11/.machine/user-story/service-scoped-worktree-pool-v1611.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-SSP-001: Rolo/multi-git governance 必须支持显式 `role=primary` root；global service b... · ac=AC-SSP-001 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-001.json`
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Implement AC-SSP-002: Governance parser/render/doctor 必须保留 primary binding 顺序无关语义，metadata ... · ac=AC-SSP-002 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-002.json`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Implement AC-SSP-003: Workspace pool 必须支持 `workspace-pool-v2` 或等价 schema：一个 feature parent ... · ac=AC-SSP-003 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-003.json`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Implement AC-SSP-004: Implement admission 对 multi-git/nested child repo 必须为每个 participating... · ac=AC-SSP-004 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-004.json`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Implement AC-SSP-005: GitScopeGraph/topology gate/write guard 必须以 explicit primary + servic... · ac=AC-SSP-005 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-005.json`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-006 Implement AC-SSP-006: Rolo v2.3.3/v2.3.4 fixture 必须验证：primary 是 `/Users/apple/Developer/Com... · ac=AC-SSP-006 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-006.json`
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — TASK-007 Implement AC-SSP-007: Existing single_repo、dedicated-worktree、pooled feature-level lease 行为... · ac=AC-SSP-007 · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/AC-SSP-007.json`
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

### ITASK-008 — TASK-008 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/GATES.json`
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

### ITASK-009 — TASK-009 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/service-scoped-worktree-pool-v1611/QA-MATRIX.json`
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
