# Beacon Implementation Plan

- plan_id: `plan-legacy-project-v152-cutover-r5`
- feature: `legacy-project-v152-cutover`
- version: `v1.5.2`
- revision_id: `R5`
- baseline_hash: `sha256:4f0a1ae7cdd350d973b0dc011c0964023ccf6c8f6bc370776c100f0bc605130c`
- delivery_baseline_id: `impl-delivery-baseline-v1.5.2-legacy-project-v152-cutover-R5`
- delivery_baseline_source_hash: `sha256:9e7bb1c06384b850e56f7f6fb787aab60988565a10cc91f57fe51fb8693c3028`
- plan_hash: `sha256:d7a123056e73bf544b1079ffb9fa2cddd55446d78c7ce1847f14b621fd16128c`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.5.2/features/legacy-project-v152-cutover/truth.md`
- prd: `docs/beacon/archive/v1.5.2/features/legacy-project-v152-cutover/truth.md`
- test_case: `docs/beacon/archive/v1.5.2/features/legacy-project-v152-cutover/tests.md`
- truth: `docs/beacon/archive/v1.5.2/features/legacy-project-v152-cutover/truth.md`
- tests: `docs/beacon/archive/v1.5.2/features/legacy-project-v152-cutover/tests.md`
- tasks: `docs/beacon/archive/v1.5.2/features/legacy-project-v152-cutover/tasks.md`
- evidence: `docs/beacon/archive/v1.5.2/features/legacy-project-v152-cutover/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.5.2/features/legacy-project-v152-cutover`
- revision_delta: `docs/beacon/archive/v1.5.2/.machine/execution/revision-delta-legacy-project-v152-cutover.json`
- story_scenario_map: `docs/beacon/archive/v1.5.2/.machine/qa/legacy-project-v152-cutover.story-scenario-map.json`
- research_projection: `docs/beacon/archive/v1.5.2/.machine/user-story/legacy-project-v152-cutover.json`
- architecture_blueprint: `docs/beacon/archive/v1.5.2/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "legacy-project-v152-cutover" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.5.2`
- run_command: `beacon implement team-run "legacy-project-v152-cutover" --project /Users/apple/Developer/Personal/products/beacon --version v1.5.2`
- dev_run_command: `beacon implement dev-run "legacy-project-v152-cutover" --project /Users/apple/Developer/Personal/products/beacon --version v1.5.2`
- qa_team_command: `beacon qa team-run "legacy-project-v152-cutover" --project /Users/apple/Developer/Personal/products/beacon --version v1.5.2`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.5.2`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.5.2/.machine/execution/git-workflow-legacy-project-v152-cutover.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.5.2/research/legacy-project-v152-cutover.md`
- source_artifact: `docs/beacon/archive/v1.5.2/.machine/user-story/legacy-project-v152-cutover.json`
- section_count: `0`

## Revision Delta
- revision_id: `R5`
- source_revision_id: `R4`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.5.2/.machine/execution/revision-delta-legacy-project-v152-cutover.json`

## Tasks

### ITASK-001 — TASK-001 Add cutover inventory classification for legacy/mixed truth state.
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001, TC-009
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Teach `beacon-change-refreeze` to run cutover preflight before refreeze.
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-002
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Add a human-facing cutover wrapper command/skill for phased migration.
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003, TC-010
- mapped_scenario_ids: SC-004, SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Wire package materialize/validate and truth-map verify into cutover phases.
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Wire governance MD verify/projection drift checks into cutover phases.
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-005
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-006 Detect stale agent-surface skill guidance and route setup/verify.
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-006
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — TASK-007 Enforce fail-closed behavior for freeze/refreeze/implement/QA/release while cutover is blocked.
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-007
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — TASK-008 Preserve and resume the original operator intent after successful cutover.
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008, TC-008
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — TASK-009 Add tests for read-only inventory and dry-run next-command reporting.
- status: `completed`
- mapped_ac_ids: AC-009, AC-010
- mapped_test_ids: TEST-009, TEST-010
- mapped_scenario_ids: SC-AUTO-TC-011, SC-AUTO-TC-012
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — TASK-010 Update skill guidance so research promotion goes through change/refreeze and not direct truth edits.
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

### ITASK-011 — TASK-011 Align `beacon implement plan` with package `tasks.md` while keeping runtime progress in execution artifacts.
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — TASK-012 Add doctor `truth_source_mismatch` diagnostics with exact repair routing.
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — TASK-013 Add QA regressions for truth-cutover routing simplification, root normalization, and change CLI version stability.
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — TASK-014 Update help/doctor route copy so `truth-cutover` is presented as a CLI repair transaction, not a new default public skill.
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
