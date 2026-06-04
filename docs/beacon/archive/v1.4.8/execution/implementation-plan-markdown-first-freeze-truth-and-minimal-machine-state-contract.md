# Beacon Implementation Plan

- plan_id: `plan-markdown-first-freeze-truth-and-minimal-machine-state-contract-r4`
- feature: `markdown-first-freeze-truth-and-minimal-machine-state-contract`
- version: `v1.4.8`
- revision_id: `R4`
- baseline_hash: `sha256:4c1f30eac0ccc6cf402b2cffbcb6119429d70753a8ff877d24198ac898178897`
- delivery_baseline_id: `impl-delivery-baseline-v1.4.8-markdown-first-freeze-truth-and-minimal-machine-state-contract-R4`
- delivery_baseline_source_hash: `sha256:316cc83dd7efbdc6c5d8813ec7b86ec3d85d864cc7aa300e679e6b69be44bdf4`
- plan_hash: `sha256:4e7633b508d2a6068be731a43942cb39593571a9bc38c76e8a2ec52ec6740995`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/archive/v1.4.8/user-story/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- prd: `docs/beacon/archive/v1.4.8/prd/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- test_case: `docs/beacon/archive/v1.4.8/qa/test-cases/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- revision_delta: `docs/beacon/archive/v1.4.8/.machine/execution/revision-delta-markdown-first-freeze-truth-and-minimal-machine-state-contract.json`
- ac_matrix: `docs/beacon/archive/v1.4.8/.machine/qa/markdown-first-freeze-truth-and-minimal-machine-state-contract.ac-test-matrix.json`
- story_scenario_map: `docs/beacon/archive/v1.4.8/.machine/qa/markdown-first-freeze-truth-and-minimal-machine-state-contract.story-scenario-map.json`
- qa9_matrix: `docs/beacon/archive/v1.4.8/.machine/qa/markdown-first-freeze-truth-and-minimal-machine-state-contract.qa9-matrix.json`
- research_projection: `docs/beacon/archive/v1.4.8/.machine/user-story/markdown-first-freeze-truth-and-minimal-machine-state-contract.json`
- architecture_blueprint: `docs/beacon/archive/v1.4.8/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "markdown-first-freeze-truth-and-minimal-machine-state-contract" --project-root . --version v1.4.8`
- run_command: `beacon implement team-run "markdown-first-freeze-truth-and-minimal-machine-state-contract" --project . --version v1.4.8`
- dev_run_command: `beacon implement dev-run "markdown-first-freeze-truth-and-minimal-machine-state-contract" --project . --version v1.4.8`
- qa_team_command: `beacon qa team-run "markdown-first-freeze-truth-and-minimal-machine-state-contract" --project . --version v1.4.8`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.4.8`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.4.8/.machine/execution/git-workflow-markdown-first-freeze-truth-and-minimal-machine-state-contract.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:docs/beacon/archive/v1.4.8/research/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- source_artifact: `docs/beacon/archive/v1.4.8/.machine/user-story/markdown-first-freeze-truth-and-minimal-machine-state-contract.json`
- section_count: `2`
- architecture: Markdown truth layer：`research/`、`prd/`、`user-story/`、`qa/test-cases/`、`execution/`、`release/`。 / Minimal machine state layer：只记录 hash、revision、status、diagnostics、transaction pointer。 / Runtime evidence layer：只在 implement / QA / release 运行时写入过程、线程、session、trace、evidence JSON。
- decision_priority: Markdown truth 高于 machine cache。 / Deterministic parser 高于 LLM interpretation。 / Minimal state cache 高于 fulltext mirror。

## Revision Delta
- revision_id: `R4`
- source_revision_id: `R3`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/archive/v1.4.8/.machine/execution/revision-delta-markdown-first-freeze-truth-and-minimal-machine-state-contract.json`

## Tasks

### ITASK-001 — FR-001 Beacon 必须把 Markdown 作为需求冻结唯一 truth
- status: `completed`
- mapped_ac_ids: AC-001, AC-002
- mapped_test_ids: TC-MDFIRST-001, TC-012, TC-013, TC-014, TC-015, TC-016, TC-017, TC-018, TC-019, TC-020, TC-MDFIRST-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: TC-MDFIRST-001, TC-MDFIRST-002
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — FR-002 Beacon 必须提供 Markdown strict parser contract
- status: `completed`
- mapped_ac_ids: AC-005, AC-006
- mapped_test_ids: TC-MDFIRST-005, TC-MDFIRST-006
- mapped_scenario_ids: SC-005, SC-006
- mapped_qa_case_ids: TC-MDFIRST-005, TC-MDFIRST-006
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — FR-003 Beacon 必须将冻结阶段 JSON 收缩为最小状态缓存
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TC-MDFIRST-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: TC-MDFIRST-003
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — FR-004 Beacon 必须禁止 fulltext machine mirrors
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TC-MDFIRST-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: TC-MDFIRST-004
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — FR-005 Beacon 必须保留 runtime evidence JSON
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TC-MDFIRST-010
- mapped_scenario_ids: SC-010
- mapped_qa_case_ids: TC-MDFIRST-010
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — FR-006 Beacon 必须让 gate 从 Markdown 解析 truth
- status: `completed`
- mapped_ac_ids: AC-008, AC-007
- mapped_test_ids: TC-MDFIRST-008, TC-MDFIRST-007
- mapped_scenario_ids: SC-007, SC-008
- mapped_qa_case_ids: TC-MDFIRST-007, TC-MDFIRST-008
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — FR-007 Beacon 必须用 hash 检测 Markdown truth drift
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TC-MDFIRST-009
- mapped_scenario_ids: SC-009
- mapped_qa_case_ids: TC-MDFIRST-009
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — FR-008 Beacon 必须提供 no silent cache fallback
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
