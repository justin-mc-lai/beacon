# Beacon Implementation Plan

- plan_id: `plan-beacon-truth-map-center-and-package-cutover-r8`
- feature: `beacon-truth-map-center-and-package-cutover`
- version: `v1.5.1`
- revision_id: `R8`
- baseline_hash: `sha256:b3b506183d36c4c14991da1ac578d9fac62e0d6f2ca1737e08de9474c4fa6980`
- delivery_baseline_id: `impl-delivery-baseline-v1.5.1-beacon-truth-map-center-and-package-cutover-R8`
- delivery_baseline_source_hash: `sha256:9750c2dfffb80262b188b76903e34b075723dae368565f72d424f0e90527ed39`
- plan_hash: `sha256:aec2652dc98d311f42d37d8cf74e60f435ee6e4ef306a724f06191a19edc2008`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.5.1/user-story/beacon-truth-map-center-and-package-cutover.md`
- prd: `docs/beacon/archive/v1.5.1/prd/beacon-truth-map-center-and-package-cutover.md`
- test_case: `docs/beacon/archive/v1.5.1/qa/test-cases/beacon-truth-map-center-and-package-cutover.md`
- revision_delta: `docs/beacon/archive/v1.5.1/.machine/execution/revision-delta-beacon-truth-map-center-and-package-cutover.json`
- ac_matrix: `docs/beacon/archive/v1.5.1/.machine/qa/beacon-truth-map-center-and-package-cutover.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.5.1/.machine/qa/beacon-truth-map-center-and-package-cutover.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.5.1/.machine/qa/beacon-truth-map-center-and-package-cutover.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.5.1/.machine/user-story/beacon-truth-map-center-and-package-cutover.json`
- architecture_blueprint: `docs/beacon/archive/v1.5.1/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-truth-map-center-and-package-cutover" --project-root . --version v1.5.1`
- run_command: `beacon implement team-run "beacon-truth-map-center-and-package-cutover" --project . --version v1.5.1`
- dev_run_command: `beacon implement dev-run "beacon-truth-map-center-and-package-cutover" --project . --version v1.5.1`
- qa_team_command: `beacon qa team-run "beacon-truth-map-center-and-package-cutover" --project . --version v1.5.1`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.5.1`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.5.1/.machine/execution/git-workflow-beacon-truth-map-center-and-package-cutover.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.5.1/research/beacon-truth-map-center-and-package-cutover.md`
- source_artifact: `docs/beacon/archive/v1.5.1/.machine/user-story/beacon-truth-map-center-and-package-cutover.json`
- section_count: `0`

## Revision Delta
- revision_id: `R8`
- source_revision_id: `R7`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.5.1/.machine/execution/revision-delta-beacon-truth-map-center-and-package-cutover.json`

## Tasks

### ITASK-001 — AC-001 `beacon.utils.truth_map` exists and exposes resolver APIs for feature...
- status: `completed`
- mapped_ac_ids: AC-001
- mapped_test_ids: TC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: TC-001
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — AC-002 Generated truth-map JSON is marked projection/diagnostic and cannot b...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: TC-002
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 Feature package Markdown carries enough contract markers for v1.5.2 c...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-003
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 Resolver exposes stable constants for source model and parser contracts.
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 New truth consumers call resolver APIs instead of constructing legacy...
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TC-005
- mapped_scenario_ids: SC-005
- mapped_qa_case_ids: TC-005
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 Skill templates instruct LLMs to read truth map and feature package b...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TC-006
- mapped_scenario_ids: SC-006
- mapped_qa_case_ids: TC-006
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 QA must not require an equivalent JSON projection for every Markdown...
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TC-007
- mapped_scenario_ids: SC-007
- mapped_qa_case_ids: TC-007
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — AC-008 Doctor route can rebuild legacy triptych from feature package or repo...
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TC-008
- mapped_scenario_ids: SC-008
- mapped_qa_case_ids: TC-008
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — AC-009 Change route can absorb legacy triptych into feature package or repor...
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TC-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-009
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — AC-010 Verify command fails or warns when resolver output disagrees with pac...
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TC-010
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: TC-010
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — AC-011 Truth-map route can rebuild requirement-derived `.machine` JSON from...
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TC-011
- mapped_scenario_ids: SC-011
- mapped_qa_case_ids: TC-011
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — AC-012 Generated machine JSON is labeled as generated state/evidence, not tr...
- status: `completed`
- mapped_ac_ids: AC-012
- mapped_test_ids: TC-012
- mapped_scenario_ids: SC-012
- mapped_qa_case_ids: TC-012
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — AC-013 Generated machine JSON records resolver contract, source paths, and s...
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TC-013
- mapped_scenario_ids: SC-013
- mapped_qa_case_ids: TC-013
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — AC-014 Runtime/process JSON is allowed without Markdown twins and is not req...
- status: `completed`
- mapped_ac_ids: AC-014
- mapped_test_ids: TC-014
- mapped_scenario_ids: SC-014
- mapped_qa_case_ids: TC-014
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-015 — AC-015 Verify fails closed when `.machine` JSON is stale, non-resolver-gener...
- status: `completed`
- mapped_ac_ids: AC-015
- mapped_test_ids: TC-015
- mapped_scenario_ids: SC-015
- mapped_qa_case_ids: TC-015
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-016 — AC-016 Resolver resolves version governance truth in addition to feature pac...
- status: `completed`
- mapped_ac_ids: AC-016
- mapped_test_ids: TC-016
- mapped_scenario_ids: SC-016
- mapped_qa_case_ids: TC-016
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-017 — AC-017 Resolver classifies feature truth, version governance truth, generate...
- status: `completed`
- mapped_ac_ids: AC-017
- mapped_test_ids: TC-017
- mapped_scenario_ids: SC-017
- mapped_qa_case_ids: TC-017
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-018 — AC-018 Manifest/index/cache JSON is never accepted as truth authority.
- status: `completed`
- mapped_ac_ids: AC-018
- mapped_test_ids: TC-018
- mapped_scenario_ids: SC-018
- mapped_qa_case_ids: TC-018
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-019 — AC-019 Material audit reads through resolver before using manifest or old pa...
- status: `completed`
- mapped_ac_ids: AC-019
- mapped_test_ids: TC-019
- mapped_scenario_ids: SC-019
- mapped_qa_case_ids: TC-019
- depends_on: ITASK-018
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-020 — AC-020 QA, release, and status read governance truth through resolver-first...
- status: `completed`
- mapped_ac_ids: AC-020
- mapped_test_ids: TC-020
- mapped_scenario_ids: SC-020
- mapped_qa_case_ids: TC-020
- depends_on: ITASK-019
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-021 — AC-021 Missing governance truth or drifted generated governance state fails...
- status: `completed`
- mapped_ac_ids: AC-021
- mapped_test_ids: TC-021
- mapped_scenario_ids: SC-021
- mapped_qa_case_ids: TC-021
- depends_on: ITASK-020
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-022 — AC-022 Version governance materials are not moved into `features/<slug>/`.
- status: `completed`
- mapped_ac_ids: AC-022
- mapped_test_ids: TC-022
- mapped_scenario_ids: SC-022
- mapped_qa_case_ids: TC-022
- depends_on: ITASK-021
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-023 — AC-023 Generated governance JSON/state carries non-authority labels or equiv...
- status: `completed`
- mapped_ac_ids: AC-023
- mapped_test_ids: TC-023
- mapped_scenario_ids: SC-023
- mapped_qa_case_ids: TC-023
- depends_on: ITASK-022
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-024 — AC-024 Implement plan/dev-run surfaces verify version governance metadata br...
- status: `completed`
- mapped_ac_ids: AC-024
- mapped_test_ids: TC-024
- mapped_scenario_ids: SC-024
- mapped_qa_case_ids: TC-024
- depends_on: ITASK-023
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-025 — AC-025 v1.5.1 may route normal truth reads, write-target resolution, gate in...
- status: `completed`
- mapped_ac_ids: AC-025
- mapped_test_ids: TC-025
- mapped_scenario_ids: SC-025
- mapped_qa_case_ids: TC-025
- depends_on: ITASK-024
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-026 — AC-026 v1.5.1 tracks high-risk truth read/write entrypoints, including PRD/u...
- status: `completed`
- mapped_ac_ids: AC-026
- mapped_test_ids: TC-026
- mapped_scenario_ids: SC-026
- mapped_qa_case_ids: TC-026
- depends_on: ITASK-025
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
