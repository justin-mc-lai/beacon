# Beacon Implementation Plan

- plan_id: `plan-beacon-spec-fingerprint-package-auth-paths-v163-r1`
- feature: `beacon-spec-fingerprint-package-auth-paths-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:20bc74b72bf5c8d4f721566c66cf32e94922f1b27efa9d43123544cad5278255`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-spec-fingerprint-package-auth-paths-v163-R1`
- delivery_baseline_source_hash: `sha256:507cae08b5a304af17437679796208689633a28366526115c5fe63d75af9c6d5`
- plan_hash: `sha256:1bb060497fd48a9e1f017e5ac10ed1b6b3cf5b119633580d73265bfb0444ba65`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/truth.md`
- prd: `docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/truth.md`
- test_case: `docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/tests.md`
- truth: `docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/truth.md`
- tests: `docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/tests.md`
- tasks: `docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/tasks.md`
- evidence: `docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163`
- story_scenario_map: `docs/beacon/v1.6.3/.machine/qa/beacon-spec-fingerprint-package-auth-paths-v163.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.3/.machine/user-story/beacon-spec-fingerprint-package-auth-paths-v163.json`
- architecture_blueprint: `docs/beacon/v1.6.3/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-spec-fingerprint-package-auth-paths-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-spec-fingerprint-package-auth-paths-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-spec-fingerprint-package-auth-paths-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-spec-fingerprint-package-auth-paths-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
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
- git_workflow_ref: `docs/beacon/v1.6.3/.machine/execution/git-workflow-beacon-spec-fingerprint-package-auth-paths-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.3/research/beacon-spec-fingerprint-package-auth-paths-v163.md`
- source_artifact: `docs/beacon/v1.6.3/.machine/user-story/beacon-spec-fingerprint-package-auth-paths-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 ≥v1.5.2 包 fingerprint user_story 层 count>0（扫 features/<slug>/truth.md...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-SF-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 ≥v1.5.2 包 fingerprint prd 层 count>0（**Must**）
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-SF-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 改 truth.md 后 fingerprint hash 改变（spec drift 检测对 truth 有效）（**Must**）
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-SF-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 <v1.5.2 `_find_layer_files` 行为不变（**Must**）
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-SF-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 test_case 层仍扫 `.machine/qa/*.ac-test-matrix.json`（**Must**）
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-SF-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 v1.6.3 release gate 修复后仍 pass（fingerprint 重生成后 expected=actual）（**Mus...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-SF-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 v1.6.2 fingerprint 行为不变（**Must**）
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-SF-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
