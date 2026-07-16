# Beacon Implementation Plan

- plan_id: `plan-version-truth-archive-lineage-r2`
- feature: `version-truth-archive-lineage`
- version: `v1.5.2`
- revision_id: `R2`
- baseline_hash: `sha256:b359f259a7194d7ecac8dc1ad056cf35583b12020f0386dec0fe1f93af400b81`
- delivery_baseline_id: `impl-delivery-baseline-v1.5.2-version-truth-archive-lineage-R2`
- delivery_baseline_source_hash: `sha256:74252c1ef4b49851e0b9bc41733375637df0bde52817e80e9350534951e11685`
- plan_hash: `sha256:1066151fe6de80217ada8aeb08fa9fd7276e6b5b43177d1f7670400fbb786ba8`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/truth.md`
- prd: `docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/truth.md`
- test_case: `docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/tests.md`
- truth: `docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/truth.md`
- tests: `docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/tests.md`
- tasks: `docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/tasks.md`
- evidence: `docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.5.2/features/version-truth-archive-lineage`
- revision_delta: `docs/beacon/archive/v1.5.2/.machine/execution/revision-delta-version-truth-archive-lineage.json`
- ac_matrix: `docs/beacon/archive/v1.5.2/.machine/qa/version-truth-archive-lineage.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.5.2/.machine/qa/version-truth-archive-lineage.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.5.2/.machine/qa/version-truth-archive-lineage.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.5.2/.machine/user-story/version-truth-archive-lineage.json`
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
- plan_command: `beacon implement team-plan "version-truth-archive-lineage" --project-root . --version v1.5.2`
- run_command: `beacon implement team-run "version-truth-archive-lineage" --project . --version v1.5.2`
- dev_run_command: `beacon implement dev-run "version-truth-archive-lineage" --project . --version v1.5.2`
- qa_team_command: `beacon qa team-run "version-truth-archive-lineage" --project . --version v1.5.2`
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
- git_workflow_ref: `docs/beacon/archive/v1.5.2/.machine/execution/git-workflow-version-truth-archive-lineage.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.5.2/research/version-truth-archive-lineage.md`
- source_artifact: `docs/beacon/archive/v1.5.2/.machine/user-story/version-truth-archive-lineage.json`
- section_count: `3`
- architecture: **Canonical write paths**: `version-truth-catalog.md` (truth placement); `project-version-governance.md` (branch); per-feature truth remains `features/<slug>/truth.md` inside each version tree. / **Read projections**: `.machine/version-truth-catalog.json`, per-version `.machine/archive/*`, optional sqlite `source_hash`. / **Modules**: extend `archive_governance.py` + new catalog parser; truth-map / doctor / versioning read catalog before scanning dirs.
- business_flow: Operator triggers cutover or audit need. / `archive catalog plan` diffs active window vs disk layout. / `catalog apply --confirm` commits MD + relocates trees + regenerates projections.
- decision_priority: MD catalog truth_root wins over directory glob discovery. / Explicit `--version` wins for inspect; delivery commands fail-closed on non-active unless `--include-archived`. / Feature `truth.md` wins over prd for discovery on v1.5.2+.

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.5.2/.machine/execution/revision-delta-version-truth-archive-lineage.json`

## Tasks

### ITASK-001 — AC-001 `docs/beacon/governance/version-truth-catalog.md` is the sole commit...
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

### ITASK-002 — AC-002 Catalog lists exactly **3** `validation_state: active` versions; thei...
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

### ITASK-003 — AC-003 Archived versions have `truth_root` under `docs/beacon/archive/<versi...
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

### ITASK-004 — AC-004 `beacon doctor verify-version-truth-catalog --strict` fails closed on...
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

### ITASK-005 — AC-005 Default delivery commands (`implement`, `qa`, `release`, truth-map bu...
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

### ITASK-006 — AC-006 Unified `discover_features(version)` lists `features/*/truth.md` on v...
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

### ITASK-007 — AC-007 `beacon archive lineage <slug> [--from v] [--to v]` returns ordered h...
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

### ITASK-008 — AC-008 `beacon archive inventory [--version auto]` builds feature × AC matri...
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

### ITASK-009 — AC-009 `docs/beacon/archive/INDEX.md` is regenerated on every `catalog apply...
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

### ITASK-010 — AC-010 `beacon archive catalog bootstrap --active v1.5.0,v1.5.1,v1.5.2 --dry...
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

### ITASK-011 — AC-011 `beacon-archive` skill documents decision boundary, four operator ver...
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

### ITASK-012 — AC-012 Merge global-boundaries **§4.1 MD-only catalog and archive plane** an...
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
