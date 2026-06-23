# Beacon Implementation Plan

- plan_id: `plan-beacon-global-workspace-git-admission-v162-r3`
- feature: `beacon-global-workspace-git-admission-v162`
- version: `v1.6.2`
- revision_id: `R3`
- baseline_hash: `sha256:b1d10720f1b837d42bd72f952039dcf8c4c6ac581ad5467cdb315a307876a406`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.2-beacon-global-workspace-git-admission-v162-R3`
- delivery_baseline_source_hash: `sha256:5fa1f7e145bfc52c743c163e7f96522d80e036d599c5f83c74457ea9c4879ca9`
- plan_hash: `sha256:3bd3e00566df65fe2e0f9f2e1e85d72ae230a121a991b309024ebdf1342d6d22`
- status: `completed`

## Source Refs
- user_story: `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/truth.md`
- prd: `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/truth.md`
- test_case: `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/tests.md`
- truth: `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/truth.md`
- tests: `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/tests.md`
- tasks: `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/tasks.md`
- evidence: `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162`
- revision_delta: `docs/beacon/v1.6.2/.machine/execution/revision-delta-beacon-global-workspace-git-admission-v162.json`
- research_projection: `docs/beacon/v1.6.2/.machine/user-story/beacon-global-workspace-git-admission-v162.json`
- architecture_blueprint: `docs/beacon/v1.6.2/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-global-workspace-git-admission-v162" --project-root /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v1.6.2/beacon-global-workspace-git-admission-v162 --version v1.6.2`
- run_command: `beacon implement team-run "beacon-global-workspace-git-admission-v162" --project /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v1.6.2/beacon-global-workspace-git-admission-v162 --version v1.6.2`
- dev_run_command: `beacon implement dev-run "beacon-global-workspace-git-admission-v162" --project /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v1.6.2/beacon-global-workspace-git-admission-v162 --version v1.6.2`
- qa_team_command: `beacon qa team-run "beacon-global-workspace-git-admission-v162" --project /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v1.6.2/beacon-global-workspace-git-admission-v162 --version v1.6.2`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.2`
- branch_prefix: `beacon/`
- base_branch: `beacon/v1.6.2`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.2/.machine/execution/git-workflow-beacon-global-workspace-git-admission-v162.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v1.6.2/beacon-global-workspace-git-admission-v162/docs/beacon/v1.6.2/research/beacon-global-workspace-git-admission-v162.md`
- source_artifact: `docs/beacon/v1.6.2/.machine/user-story/beacon-global-workspace-git-admission-v162.json`
- section_count: `0`

## Revision Delta
- revision_id: `R3`
- source_revision_id: `R2`
- cleanup_required: `False`
- revision_delta_ref: `docs/beacon/v1.6.2/.machine/execution/revision-delta-beacon-global-workspace-git-admission-v162.json`

## Tasks

### ITASK-001 — AC-001 `beacon workspace admit` 解析 v1.6.2 → `beacon/v1.6.2/<feature>` + work...
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

### ITASK-002 — AC-002 无/脏 admission → `implement run` / `qa run` blocked + stable reason_co...
- status: `completed`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — AC-003 Tier A host skills 含 GIT_ADMISSION Step 0；setup-agent-surface 物化一致（**...
- status: `completed`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — AC-004 Cursor hook：missing/dirty artifact → Write deny；valid → allow（**Shoul...
- status: `completed`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — AC-005 Claude hook parity 同 AC-004（**Should**）
- status: `completed`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — AC-006 verify-agent-surface：缺 preamble **fail**；缺 hook **warn** only（**Shoul...
- status: `completed`
- mapped_ac_ids: AC-006
- mapped_test_ids: TEST-006
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — AC-007 `TRELLIS_DISABLE_HOOKS=1` 后 Beacon admission hook 仍注册（**Should**）
- status: `completed`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — AC-008 governance MD v1.6.2 block + `admission_invalidation: dirty_only`（**M...
- status: `completed`
- mapped_ac_ids: AC-008
- mapped_test_ids: TEST-008
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — AC-009 branch/head/cwd 变化 → invalid；**无 git 变化时时间流逝仍 valid**（**Must**）
- status: `completed`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — AC-010 `check-branch` alias + `dev-run` 先 admit；现有调用方不 break（**Must**）
- status: `completed`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — AC-011 `/beacon-gen-implement v1.6.2 <slug>` → Step 0 admit → worktree 再写（**...
- status: `completed`
- mapped_ac_ids: AC-011
- mapped_test_ids: TEST-011
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — AC-012 upgrade-package 写入 release stub（**Must**，UD-013）
- status: `completed`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — AC-013 version-line 缺失 → upgrade-package repair（**Must**，UD-012）
- status: `completed`
- mapped_ac_ids: AC-013
- mapped_test_ids: TEST-013
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — AC-014 blocked payload 含 repair_commands 序列（**Must**）
- status: `completed`
- mapped_ac_ids: AC-014
- mapped_test_ids: TEST-014
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-015 — AC-015 v1.6.2 upgrade-package 后 verify-materials strict pass（**Must**）
- status: `completed`
- mapped_ac_ids: AC-015
- mapped_test_ids: TEST-015
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
