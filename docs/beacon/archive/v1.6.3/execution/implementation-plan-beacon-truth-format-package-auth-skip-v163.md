# Beacon Implementation Plan

- plan_id: `plan-beacon-truth-format-package-auth-skip-v163-r1`
- feature: `beacon-truth-format-package-auth-skip-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:a8f512e1b7e70420f4fd7f4b706885706b9659630f9c72d26376e031a75a9a43`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-truth-format-package-auth-skip-v163-R1`
- delivery_baseline_source_hash: `sha256:f57069d4b2f995705871f43437f5c4f36de7824b8fb86dfe76e9216734ac45e4`
- plan_hash: `sha256:817f8561777c68d555d3d43296c17ab3e7b425d0193e90d8d577bfd9bf710a25`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md`
- prd: `docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md`
- test_case: `docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/tests.md`
- truth: `docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md`
- tests: `docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/tests.md`
- tasks: `docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/tasks.md`
- evidence: `docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163`
- story_scenario_map: `docs/beacon/archive/v1.6.3/.machine/qa/beacon-truth-format-package-auth-skip-v163.story-scenario-map.json`
- research_projection: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-truth-format-package-auth-skip-v163.json`
- architecture_blueprint: `docs/beacon/archive/v1.6.3/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-truth-format-package-auth-skip-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-truth-format-package-auth-skip-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-truth-format-package-auth-skip-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-truth-format-package-auth-skip-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.3`
- branch_prefix: `beacon/`
- base_branch: `beacon/v1.6.3`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.6.3/.machine/execution/git-workflow-beacon-truth-format-package-auth-skip-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.3/research/beacon-truth-format-package-auth-skip-v163.md`
- source_artifact: `docs/beacon/archive/v1.6.3/.machine/user-story/beacon-truth-format-package-auth-skip-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 `compute_feature_paths` 对 ≥v1.5.2 返回 `features/<slug>/{truth,tests}.m...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-TF-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 package-auth 包 manifest status 取自 truth.md frontmatter `status`（froze...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-TF-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 `build_requirement_package_gate` 对 ≥v1.5.2 包不报 `truth_format_non_comp...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-TF-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 <v1.5.2 版本 truth_format 校验行为不变（**Must**）
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-TF-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 v1.6.3 frozen 包 `implement run`/`qa run` 不再因 `truth_format_non_compli...
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-TF-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 v1.6.2 包修复后 `build_requirement_package_gate` 仍 pass（不因路径修复而 break）（**...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-TF-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 package-auth 包仍经 `feature_package.validate_feature_package` 校验（未绕过真校验...
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-TF-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
