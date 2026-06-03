# Beacon Implementation Plan

- plan_id: `plan-markdown-only-project-version-governance-r2`
- feature: `markdown-only-project-version-governance`
- version: `v1.5.2`
- revision_id: `R2`
- baseline_hash: `sha256:899c372fba61aa9338c51242bdbb0971f7a451ed2982adb70985ba759c44f14b`
- delivery_baseline_id: `impl-delivery-baseline-v1.5.2-markdown-only-project-version-governance-R2`
- delivery_baseline_source_hash: `sha256:ffafda62e80df351a9adefee2b70f3a5f94a6df3f6aa70e317461ba9e8e38c83`
- plan_hash: `sha256:bce576aec3a5e17db648f1eb25b96aa8b5bb6601a031d6ecfadebdd667490723`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.5.2/features/markdown-only-project-version-governance/truth.md`
- prd: `docs/beacon/v1.5.2/features/markdown-only-project-version-governance/truth.md`
- test_case: `docs/beacon/v1.5.2/features/markdown-only-project-version-governance/tests.md`
- truth: `docs/beacon/v1.5.2/features/markdown-only-project-version-governance/truth.md`
- tests: `docs/beacon/v1.5.2/features/markdown-only-project-version-governance/tests.md`
- tasks: `docs/beacon/v1.5.2/features/markdown-only-project-version-governance/tasks.md`
- evidence: `docs/beacon/v1.5.2/features/markdown-only-project-version-governance/evidence.md`
- source_of_truth_root: `docs/beacon/v1.5.2/features/markdown-only-project-version-governance`
- revision_delta: `docs/beacon/v1.5.2/.machine/execution/revision-delta-markdown-only-project-version-governance.json`
- story_scenario_map: `docs/beacon/v1.5.2/.machine/qa/markdown-only-project-version-governance.story-scenario-map.json`
- research_projection: `docs/beacon/v1.5.2/.machine/user-story/markdown-only-project-version-governance.json`
- architecture_blueprint: `docs/beacon/v1.5.2/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "markdown-only-project-version-governance" --project-root . --version v1.5.2`
- run_command: `beacon implement team-run "markdown-only-project-version-governance" --project . --version v1.5.2`
- dev_run_command: `beacon implement dev-run "markdown-only-project-version-governance" --project . --version v1.5.2`
- qa_team_command: `beacon qa team-run "markdown-only-project-version-governance" --project . --version v1.5.2`
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
- git_workflow_ref: `docs/beacon/v1.5.2/.machine/execution/git-workflow-markdown-only-project-version-governance.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:docs/beacon/v1.5.2/research/markdown-only-project-version-governance.md`
- source_artifact: `docs/beacon/v1.5.2/.machine/user-story/markdown-only-project-version-governance.json`
- section_count: `0`

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.5.2/.machine/execution/revision-delta-markdown-only-project-version-governance.json`

## Tasks

### ITASK-001 — AC-001 `docs/beacon/governance/project-version-governance.md` is the sole au...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 No governance JSON records under `.beacon/metadata/` (including `proj...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 `beacon-toolkit-metadata`, `beacon-toolkit-branch-governance`, implem...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 `load_project_metadata` (or successor) parses governance MD; it must...
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 Metadata/branch-governance write transactions update governance MD on...
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 When governance MD exists for the active version, `load_execution_bra...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006, TC-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 Metadata and branch-governance toolkit surfaces share one governance...
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — AC-008 `_branch_guard_inputs` derives `expected_branch`, `git_roots`, `parti...
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008, TC-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — AC-009 Monorepo topology with multiple `service_bindings` and `per_service_c...
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009, TC-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — AC-010 `beacon doctor metadata migrate-to-governance-md` (or equivalent) imp...
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010, TC-010
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — AC-011 Material gate / release supplements reference governance MD via resol...
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011, TC-011
- mapped_scenario_ids: SC-011
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — AC-012 truth-map registers `project_governance` (or equivalent) as version g...
- status: `completed`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012, TC-012
- mapped_scenario_ids: SC-012
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — AC-013 Explicit-version implement preflight resolves canonical branch/worktr...
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013, TC-013
- mapped_scenario_ids: SC-013
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
