# Beacon Implementation Plan

- plan_id: `plan-beacon-post-release-hook-agent-coverage-v163-r1`
- feature: `beacon-post-release-hook-agent-coverage-v163`
- version: `v1.6.3`
- revision_id: `R1`
- baseline_hash: `sha256:59e52ff5d186636a8d6901aa29381e3e1c57c8ef81a2777e0cc781c57953c3aa`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.3-beacon-post-release-hook-agent-coverage-v163-R1`
- delivery_baseline_source_hash: `sha256:d16653470c5e6964b8140ac2eb991acc0ec70c717c3d8fc54eb7bfddbecef1f5`
- plan_hash: `sha256:4e82b7eb9249a69983f0c08c3b744da39822a6529e98b3343daa155eb856ba75`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/truth.md`
- prd: `docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/truth.md`
- test_case: `docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/tests.md`
- truth: `docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/truth.md`
- tests: `docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/tests.md`
- tasks: `docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/tasks.md`
- evidence: `docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163`
- story_scenario_map: `docs/beacon/v1.6.3/.machine/qa/beacon-post-release-hook-agent-coverage-v163.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.3/.machine/user-story/beacon-post-release-hook-agent-coverage-v163.json`
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
- plan_command: `beacon implement team-plan "beacon-post-release-hook-agent-coverage-v163" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- run_command: `beacon implement team-run "beacon-post-release-hook-agent-coverage-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- dev_run_command: `beacon implement dev-run "beacon-post-release-hook-agent-coverage-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
- qa_team_command: `beacon qa team-run "beacon-post-release-hook-agent-coverage-v163" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.3`
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
- git_workflow_ref: `docs/beacon/v1.6.3/.machine/execution/git-workflow-beacon-post-release-hook-agent-coverage-v163.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.3/research/beacon-post-release-hook-agent-coverage-v163.md`
- source_artifact: `docs/beacon/v1.6.3/.machine/user-story/beacon-post-release-hook-agent-coverage-v163.json`
- section_count: `0`

## Tasks

### ITASK-001 — AC-001 `_run_beacon_post_release_local_install` 的 agent 循环含 trae/claude/code...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-HK-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 hook payload 的 `agent_surfaces` 含 5 个 agent 的 setup_status + verify_s...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-HK-002
- mapped_scenario_ids: SC-AUTO-TC-HK-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 任一 agent verify 报 `host_visible_skills_drift` 时 hook block，reason_cod...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-HK-003
- mapped_scenario_ids: SC-AUTO-TC-HK-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 hook 仍调 `install_global_claude_beacon_skills` + `verify_global_claude...
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-HK-004
- mapped_scenario_ids: SC-AUTO-TC-HK-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 codex/claude 的 setup/verify 行为不变（仍 force=True + strict=True）（**Must**）
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-HK-005
- mapped_scenario_ids: SC-AUTO-TC-HK-005
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 现有 block reason_codes（setup_failed/verify_failed）语义不变（**Must**）
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-HK-006
- mapped_scenario_ids: SC-AUTO-TC-HK-006
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 循环复用 agent_surface 的全 agent 常量，不新增硬编码（**Must**）
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-HK-007
- mapped_scenario_ids: SC-AUTO-TC-HK-007
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
