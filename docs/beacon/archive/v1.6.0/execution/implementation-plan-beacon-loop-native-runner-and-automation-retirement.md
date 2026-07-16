# Beacon Implementation Plan

- plan_id: `plan-beacon-loop-native-runner-and-automation-retirement-r2`
- feature: `beacon-loop-native-runner-and-automation-retirement`
- version: `v1.6.0`
- revision_id: `R2`
- baseline_hash: `sha256:611e649cb05ae3a2be7537767abd5f572965c1ec3b4075d67a0116676e580cd8`
- delivery_baseline_id: `impl-delivery-baseline-v1.6.0-beacon-loop-native-runner-and-automation-retirement-R2`
- delivery_baseline_source_hash: `sha256:c5521eb66fea66d19f46b15256259661e68e562d68a727960cfa8c5ff547b3a8`
- plan_hash: `sha256:d1eed2338b580f2b3199e072007604b4e0ff6a1ef26d4ae9444fc1b4e9218ae9`
- status: `blocked`

## Source Refs
- user_story: `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md`
- prd: `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md`
- test_case: `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/tests.md`
- truth: `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md`
- tests: `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/tests.md`
- tasks: `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/tasks.md`
- evidence: `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/evidence.md`
- source_of_truth_root: `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement`
- revision_delta: `docs/beacon/archive/v1.6.0/.machine/execution/revision-delta-beacon-loop-native-runner-and-automation-retirement.json`
- story_scenario_map: `docs/beacon/archive/v1.6.0/.machine/qa/beacon-loop-native-runner-and-automation-retirement.story-scenario-map.json`
- research_projection: `docs/beacon/archive/v1.6.0/.machine/user-story/beacon-loop-native-runner-and-automation-retirement.json`
- architecture_blueprint: `docs/beacon/archive/v1.6.0/execution/architecture-blueprint.md`

## Boundary Principles
- `explicit_assumptions`: `显式假设与歧义管理`
- `simplicity_first`: `简单优先`
- `surgical_changes`: `外科手术式改动`
- `goal_driven_execution`: `目标驱动验证闭环`
- `trivial_task_exception`: `trivial task 可以轻量处理，但不能越界`

## Team Mode
- preferred_surface: `implement-team`
- preferred_runner: `codex-subagents`
- plan_command: `beacon implement team-plan "beacon-loop-native-runner-and-automation-retirement" --project-root /Users/apple/Developer/Personal/products/beacon --version v1.6.0`
- run_command: `beacon implement team-run "beacon-loop-native-runner-and-automation-retirement" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.0`
- dev_run_command: `beacon implement dev-run "beacon-loop-native-runner-and-automation-retirement" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.0`
- qa_team_command: `beacon qa team-run "beacon-loop-native-runner-and-automation-retirement" --project /Users/apple/Developer/Personal/products/beacon --version v1.6.0`
- roles: planner, implementation-architect, implementer, reviewer, tester
- execution_order: planner, implementation-architect, implementer, reviewer, tester

## Git Workflow
- mode: `single-repo`
- expected_branch: `beacon/v1.6.0`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- service_directories: .
- git_workflow_ref: `docs/beacon/archive/v1.6.0/.machine/execution/git-workflow-beacon-loop-native-runner-and-automation-retirement.json`

## Diagram Truth
- required: `False`
- ready: `True`
- diagram_types: -
- state_axes: -
- review_gates: -
- qa_coverage_hints: -

## Research Projection
- present: `True`
- source: `research:/Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.0/research/beacon-loop-native-runner-and-automation-retirement.md`
- source_artifact: `docs/beacon/archive/v1.6.0/.machine/user-story/beacon-loop-native-runner-and-automation-retirement.json`
- section_count: `0`

## Revision Delta
- revision_id: `R2`
- source_revision_id: `R1`
- cleanup_required: `True`
- revision_delta_ref: `docs/beacon/archive/v1.6.0/.machine/execution/revision-delta-beacon-loop-native-runner-and-automation-retirement.json`

## Tasks

### ITASK-001 — TASK-001 从 Beacon command catalog、CLI factory、help、intent routing 和 skill routing 中移除 active `automation` surface。
- status: `blocked`
- mapped_ac_ids: AC-001
- mapped_test_ids: TEST-001, TC-001, TC-002
- mapped_scenario_ids: SC-001, SC-002
- mapped_qa_case_ids: -
- depends_on: -
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-002 — TASK-002 删除或改造 `beacon/commands/automation.py`，确保旧 automation queue/job 业务不可继续执行。
- status: `blocked`
- mapped_ac_ids: AC-002, AC-028
- mapped_test_ids: TEST-002, TEST-028, TC-003
- mapped_scenario_ids: SC-AUTO-TC-003
- mapped_qa_case_ids: -
- depends_on: ITASK-001
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-003 — TASK-003 删除或迁移 `beacon/utils/automation_*.py` 中只服务旧 automation 的业务逻辑。
- status: `blocked`
- mapped_ac_ids: AC-003
- mapped_test_ids: TEST-003, TC-004, TC-005
- mapped_scenario_ids: SC-AUTO-TC-004, SC-AUTO-TC-005
- mapped_qa_case_ids: -
- depends_on: ITASK-002
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-004 — TASK-004 删除或退役 `automation/jobs/`、`automation/launchd/`、`automation/beacon-automation-queue.json` 和旧 automation 文档入口。
- status: `blocked`
- mapped_ac_ids: AC-004
- mapped_test_ids: TEST-004, TC-006
- mapped_scenario_ids: SC-AUTO-TC-006
- mapped_qa_case_ids: -
- depends_on: ITASK-003
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-005 — TASK-005 新增 `packages/beacon-loop` TypeScript package，并配置独立 build/test/bin。
- status: `blocked`
- mapped_ac_ids: AC-013, AC-006
- mapped_test_ids: TEST-013, TEST-006, TC-008, TC-015
- mapped_scenario_ids: SC-AUTO-TC-008, SC-AUTO-TC-015
- mapped_qa_case_ids: -
- depends_on: ITASK-004
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-006 — TASK-006 实现 `beacon-loop goal "<goal>"` CLI，且不实现 `beacon-loop lfg` alias。
- status: `blocked`
- mapped_ac_ids: AC-005
- mapped_test_ids: TEST-005, TC-007
- mapped_scenario_ids: SC-AUTO-TC-007
- mapped_qa_case_ids: -
- depends_on: ITASK-005
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-007 — TASK-007 实现 Beacon resolver adapter，启动前调用 `beacon truth-map resolve ... --json`。
- status: `blocked`
- mapped_ac_ids: AC-030
- mapped_test_ids: TEST-030
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-006
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-008 — TASK-008 实现 resolver blocked fail-closed，并推荐 `beacon-gen-change`。
- status: `blocked`
- mapped_ac_ids: AC-007
- mapped_test_ids: TEST-007, TC-009
- mapped_scenario_ids: SC-AUTO-TC-009
- mapped_qa_case_ids: -
- depends_on: ITASK-007
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-009 — TASK-009 实现 `.beacon/loop/runs/<run-id>/` runtime package 写入（MVP 单次 iteration）。
- status: `blocked`
- mapped_ac_ids: AC-029
- mapped_test_ids: TEST-029
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-008
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-010 — TASK-010 实现 git clean preflight、branch/worktree isolation 和 dirty worktree 阻断。
- status: `blocked`
- mapped_ac_ids: AC-009
- mapped_test_ids: TEST-009, TC-011
- mapped_scenario_ids: SC-AUTO-TC-011
- mapped_qa_case_ids: -
- depends_on: ITASK-009
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-011 — TASK-011 MVP runner orchestrator（单次 iteration；待 Phase A 升级为真多轮）。
- status: `blocked`
- mapped_ac_ids: AC-010
- mapped_test_ids: TEST-010, TC-012
- mapped_scenario_ids: SC-AUTO-TC-012
- mapped_qa_case_ids: -
- depends_on: ITASK-010
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-012 — TASK-012 实现 success commit、failure rollback、commit failure repair state（MVP）。
- status: `blocked`
- mapped_ac_ids: AC-011, AC-008
- mapped_test_ids: TEST-011, TEST-008, TC-010, TC-013
- mapped_scenario_ids: SC-AUTO-TC-010, SC-AUTO-TC-013
- mapped_qa_case_ids: -
- depends_on: ITASK-011
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-013 — TASK-013 实现 `status`、`stop`、`resume`、`review`、`import-evidence`、`doctor` 子命令（MVP stub 待加强）。
- status: `blocked`
- mapped_ac_ids: AC-012
- mapped_test_ids: TEST-012, TC-014
- mapped_scenario_ids: SC-AUTO-TC-014
- mapped_qa_case_ids: -
- depends_on: ITASK-012
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-014 — TASK-014 实现 codex agent adapter（MVP fixture 路径；待 Phase A 真多轮）。
- status: `blocked`
- mapped_ac_ids: AC-014
- mapped_test_ids: TEST-014, TC-016
- mapped_scenario_ids: SC-AUTO-TC-016
- mapped_qa_case_ids: -
- depends_on: ITASK-013
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-015 — TASK-015 实现 Beacon evidence import adapter。
- status: `blocked`
- mapped_ac_ids: AC-015
- mapped_test_ids: TEST-015, TC-017
- mapped_scenario_ids: SC-AUTO-TC-017
- mapped_qa_case_ids: -
- depends_on: ITASK-014
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-016 — TASK-016 确保 `beacon-loop` 不输出 QA/release verdict。
- status: `blocked`
- mapped_ac_ids: AC-016
- mapped_test_ids: TEST-016
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-015
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-017 — TASK-017 MVP tests（待扩展 TC-018..TC-035）。
- status: `blocked`
- mapped_ac_ids: AC-017
- mapped_test_ids: TEST-017
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-016
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-018 — TASK-018 更新文档，明确双 CLI、`goal` 命名、automation retirement。
- status: `blocked`
- mapped_ac_ids: AC-018
- mapped_test_ids: TEST-018
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-017
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-019 — TASK-019 实现 `Orchestrator` 多轮 loop（max-iterations / max-tokens / stop-when / cap_reached）。
- status: `blocked`
- mapped_ac_ids: AC-019
- mapped_test_ids: TEST-019
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-018
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-020 — TASK-020 实现 `notes.md` 跨轮 prompt 注入与 iteration 编号递增。
- status: `blocked`
- mapped_ac_ids: AC-020
- mapped_test_ids: TEST-020
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-019
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-021 — TASK-021 实现 graceful stop 与 `--force` stop（真进程/子进程中断）。
- status: `blocked`
- mapped_ac_ids: AC-021
- mapped_test_ids: TEST-021
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-020
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-022 — TASK-022 实现 consecutive failure limit、no-op failure、retryable hard error backoff。
- status: `blocked`
- mapped_ac_ids: AC-022
- mapped_test_ids: TEST-022
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-021
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-023 — TASK-023 加强 `resume`：从 repair/stop/cap 状态恢复并继续 N+1 iteration。
- status: `blocked`
- mapped_ac_ids: AC-023
- mapped_test_ids: TEST-023
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-022
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-024 — TASK-024 实现丰富 exit summary / `summary.md`（AC-021）。
- status: `blocked`
- mapped_ac_ids: AC-024, AC-025, AC-026, AC-027
- mapped_test_ids: TEST-024, TEST-025, TEST-026, TEST-027
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-023
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-025 — TASK-025 codex adapter 真多轮路径（非仅 `BEACON_LOOP_TEST_AGENT_RESULT` 单次）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-024
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-026 — TASK-026 新增 orchestrator/resume/stop/state transition tests（TC-018..TC-023, TC-034, TC-035）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-025
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-027 — TASK-027 实现 `.beacon/loop/ledger/loop-runs.db` 与 runs 索引写入。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-026
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-028 — TASK-028 实现 `beacon-loop runs query` / `runs show` / `runs diagnose`。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-027
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-029 — TASK-029 实现 `runtime-set` / `runtime-list` / `runtime-remove`。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-028
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-030 — TASK-030 实现 `analyze` / `learn` 站外产物到 `.beacon/loop/index/`。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-029
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-031 — TASK-031 扩展 `doctor --diagnose` 分桶与 repair route。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-030
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-032 — TASK-032 ledger/runtime/diagnose tests（TC-024..TC-028）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-031
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-033 — TASK-033 实现 `current-branch`、`beacon-loop/<run-id>` branch 模式与非法组合阻断。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-032
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-034 — TASK-034 实现 `~/.beacon-loop/config.yml` 加载与 CLI 覆盖。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-033
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-035 — TASK-035 实现 claude adapter（contract + integration tier）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-034
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-036 — TASK-036 实现 `acp:<target>` adapter（contract + integration tier）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-035
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-037 — TASK-037 branch/config/adapter tests（TC-029..TC-032）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-036
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-038 — TASK-038 实现 scripted E2E：goal -> multi-iteration candidate -> import-evidence -> beacon qa run 驱动。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-037
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-039 — TASK-039 更新 `evidence.md` implementation index（仍不写 verdict）。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-038
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-040 — TASK-040 `beacon qa run` + release gate 重新验收本 feature。
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-039
- direct_delivery_services: .
- reference_only_services: docs
- target_modules: .
- diagram_review_gates: -

### ITASK-041 — Cleanup superseded surfaces from R1
- status: `completed`
- mapped_ac_ids: -
- mapped_test_ids: -
- mapped_scenario_ids: -
- mapped_qa_case_ids: -
- depends_on: ITASK-040
- direct_delivery_services: -
- reference_only_services: -
- target_modules: -
- diagram_review_gates: -
- required_cleanup: `True`
- source_revision_id: `R1`
- revision_delta_ref: `docs/beacon/archive/v1.6.0/.machine/execution/revision-delta-beacon-loop-native-runner-and-automation-retirement.json`
- cleanup_surface_labels: AC-001: `beacon automation` 业务代码退役，不再作为 active command surface 暴露或执行旧 queue/job/launchd 业务。, AC-015: `beacon-loop doctor` 能检查 Beacon CLI 可用性、Node runtime、agent backend、git/worktree 能力和 evidence import prerequisites。, AC-003: `beacon-loop goal "<goal>"` 是唯一 goal entrypoint；不存在 `beacon-loop lfg` alias、deprecated alias、compatibility route 或 help hint。, AC-004: `beacon-loop goal` 启动前调用 `beacon truth-map resolve ... --json` 并记录 resolver refs。, AC-010: `beacon-loop import-evidence <run-id>` 调用 Beacon implementation evidence import，并把 runtime evidence candidate 接入 Beacon 可读实现证据面。, AC-009: `beacon-loop resume <run-id>` 从既有 run metadata、notes 和 branch/worktree 状态恢复，而不是创建无关新运行。, AC-011: Beacon QA/release 仍然是唯一 closure verdict；`beacon-loop` output 不得声明 QA pass、release ready 或 feature complete。, AC-012: docs、help、tests、command catalog 和 skill routing 全部使用 `goal` 命名，不出现 active `lfg` route。, AC-006: resolver pass 时，`beacon-loop` 创建 `.beacon/loop/runs/<run-id>/run-package.json`、`prompt.md`、`notes.md`、`output-schema.json`、iteration logs、`evidence.json` 和 `summary.md`。, AC-007: runner 默认使用 branch/worktree isolation，并在 dirty worktree 下 fail closed，除非显式 controlled mode 存在。, AC-014: runtime artifacts 明确标记为 runtime process record，不是 requirement truth，不写 `.machine` requirement projection。, AC-002: 仓库包含 `packages/beacon-loop`，并能独立构建出 `beacon-loop` CLI。, AC-008: 成功 iteration 自动 commit；失败 iteration rollback；commit failure 进入 repair state，且 resume 可继续。, AC-013: 旧 automation tests 被删除或重写为 retirement negative tests；新增 `beacon-loop` CLI/package/runner/evidence tests。
