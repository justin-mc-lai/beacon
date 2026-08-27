# Beacon Implementation Plan

- plan_id: `plan-beacon-v1614-fsm-mermaid-validate-r1`
- feature: `beacon-v1614-fsm-mermaid-validate`
- version: `v1.6.14`
- revision_id: `R1`
- baseline_hash: `sha256:b4329ece4cefd2ab70032a8f6e91409622b3dedab86f319b589b34eb39e6a27b`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.14-beacon-v1614-fsm-mermaid-validate-R1`
- delivery_baseline_source_hash: `sha256:dc1aea04c8d7f29f4ece7193caeada66806d70162a208d3c049b6985df07c6b9`
- plan_hash: `sha256:25e883074fe1226259b94c7fa2bcc3c5e69875c9033f9e3b082c7e0b0e6982d7`
- status: `planned`

## Source Refs
- user_story: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/truth.md`
- prd: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/truth.md`
- test_case: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/tests.md`
- truth: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/truth.md`
- tests: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/tests.md`
- tasks: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/tasks.md`
- evidence: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/evidence.md`
- source_of_truth_root: `docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate`
- story_scenario_map: `docs/beacon/v1.6.14/.machine/qa/beacon-v1614-fsm-mermaid-validate.story-scenario-map.json`
- research_projection: `docs/beacon/v1.6.14/.machine/user-story/beacon-v1614-fsm-mermaid-validate.json`
- architecture_blueprint: `docs/beacon/v1.6.14/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-v1614-fsm-mermaid-validate" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- run_command: `beacon implement team-run "beacon-v1614-fsm-mermaid-validate" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- dev_run_command: `beacon implement dev-run "beacon-v1614-fsm-mermaid-validate" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- qa_team_command: `beacon qa team-run "beacon-v1614-fsm-mermaid-validate" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.14`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.14/beacon-v1614-fsm-mermaid-validate`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/v1.6.14/.machine/execution/git-workflow-beacon-v1614-fsm-mermaid-validate.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `False`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/v1.6.14/research/beacon-v1614-fsm-mermaid-validate.md`
- source_artifact: `docs/beacon/v1.6.14/.machine/user-story/beacon-v1614-fsm-mermaid-validate.json`
- section_count: `0`

## Tasks

### ITASK-001 — TASK-001 Implement AC-001: truth 生成/冻结时，FSM 段自动附带 `stateDiagram-v2` mermaid 块（状态+转移），文档可渲染。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-001.json`
- status: `planned`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001
- mapped_scenario_ids: SC-001
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 Implement AC-002: FSM 机器校验：校验器可解析 truth FSM 表，检查 状态存在 / 转移合法 / illegal 转换被拒，输出结构化 findi... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-002.json`
- status: `planned`
- mapped_ac_ids: AC-002
- mapped_test_ids: TEST-002, TC-002
- mapped_scenario_ids: SC-002
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 Implement AC-003: FSM 行为变化可检测：同一 FSM 的 states/transitions 变化产生不同 behavior digest，仅措辞变化不... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-003.json`
- status: `planned`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-003
- mapped_scenario_ids: SC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 Implement AC-004: FSM 校验进入 freeze 门禁：FSM 不合法（如非法转移未声明）→ freeze fail-closed（reason_code ... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-004.json`
- status: `planned`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-004
- mapped_scenario_ids: SC-004
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/GATES.json`
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/QA-MATRIX.json`
- status: `planned`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -
