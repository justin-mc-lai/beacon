---
slug: beacon-loop-goal-v166
version: v1.6.7
status: draft
revision_id: R7
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-loop-goal-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Goal Orchestrator v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-LG-001 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_state_init_creates_file -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `loop_goal_state.init()` 创建 `.beacon/state/loop-goal/<run_id>.json`，schema 为 `loop-goal-state.v1`，含 run_id/version/feature/utterance/current_stage |
| AC-002 | TC-LG-002 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_stage_transition_appends_history -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `transition()` 更新 `current_stage` 并追加 `stage_history`，含 `at` 时间戳 |
| AC-003 | TC-LG-003 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_precheck_gate_blocks_unregistered -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Governance precheck blocked 时编排器停止，输出 `reason_code=governance_version_not_registered` |
| AC-004 | TC-LG-004 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_truth_gate_waits_for_frozen -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Truth 阶段后 truth.md status != frozen → 编排器停留在 `truth_routing`，不进入 implement |
| AC-005 | TC-LG-005 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_implement_gate_repair_loop -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Tests fail → 编排器回到 `implement_routing`；最多 3 次 repair loop |
| AC-006 | TC-LG-006 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_qa_gate_repair_loop -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | QA fail → 编排器回到 `implement_routing`；最多 3 次 |
| AC-007 | TC-LG-007 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_release_human_gate_blocks_auto -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 即使 `auto_decide=true`，`release_gate` 阶段编排器停在人工确认门，不能自动通过 |
| AC-008 | TC-LG-008 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_error_recovery_routes_debug -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 任何阶段 blocked → `current_stage=error_recovery`，输出推荐路由 `beacon-gov-debug` |
| AC-009 | TC-LG-009 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_stop_when_halts_delivery -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | stop_when 条件满足 → 编排器停止，输出 `reason_code=stop_when_satisfied` |
| AC-010 | TC-LG-010 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_skill_routing_decision_tree -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | SKILL.md 包含完整决策树，每个阶段到 skill 的映射正确 |
| AC-011 | TC-LG-011 | contract | `python3 -m pytest tests/test_doctor_agent_surface.py::test_verify_agent_surface_v160_should_pass_after_setup tests/test_v160_skill_harness_taxonomy.py::test_v160_skill_package_materialize_should_create_harness_only_package tests/test_v161_agent_eval.py::test_v161_taxonomy_includes_beacon_eval_agent tests/test_v161_agent_eval.py::test_agent_eval_catalog_materialize -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `beacon-loop-goal` 被 v1.6 taxonomy / agent surface expected list / skill inventory / release governance 计为公开 governor skill，公开 skill 总数为 38 |
| AC-012 | TC-LG-012 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_review_routing_public_skill_contract -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | public SKILL.md 的 state machine、decision tree、routing matrix 均显式包含 `review_routing` / `beacon-pln-review` |
| AC-013 | TC-LG-013 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_review_decision_packet_records_outputs -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | planner-review artifact 被记录为 loop-goal outputs 中的 review decision packet |
| AC-014 | TC-LG-014 | negative | `python3 -m pytest tests/test_v166_loop_goal.py -k "review_decision_packet" -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | P0 / user_decision_required / drift route 阻断；**单独 P1 进入 standard_execution_precheck 且写入 continue audit**；不得因仅 P1 停在 error_recovery |
| AC-015 | TC-LG-015 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_standard_execution_precheck_public_skill_contract -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | public SKILL.md 的 state machine、decision tree、routing matrix 均显式包含 `review_verify -> standard_execution_precheck -> implement_routing` |
| AC-016 | TC-LG-016 | negative | `python3 -m pytest tests/test_v166_loop_goal.py::test_uncommitted_canonical_refreeze_blocks_implement -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | refreeze complete 但 canonical branch 未提交时 blocked，`reason_code=canonical_refreeze_not_committed` |
| AC-017 | TC-LG-017 | negative | `python3 -m pytest tests/test_v166_loop_goal.py::test_stale_feature_refreeze_requires_quarantine -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | feature worktree 存在本地 `.machine` revision/projection dirty 时必须记录 scoped stash/archive ref；直接进入 implement blocked |
| AC-018 | TC-LG-018 | negative | `python3 -m pytest tests/test_v166_loop_goal.py::test_truth_baseline_commit_must_be_merged -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | feature branch 未包含 `truth_baseline_commit` 时 blocked，`reason_code=truth_baseline_not_merged` |
| AC-019 | TC-LG-019 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_standard_execution_verification_bundle_required -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | verification bundle 含 truth-map verify、verify-materials strict、git diff check、branch-governance verify、workspace admission；缺任一项 blocked |
| AC-020 | TC-LG-020 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_workspace_admission_ref_recorded_before_implement -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | workspace admission pass 后 artifact ref 写入 loop-goal outputs；缺失时不得进入 `implement_routing` |
| AC-021 | TC-LG-021 | regression | `python3 -m pytest tests/test_v166_loop_goal.py::test_standard_execution_precheck_is_idempotent -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 重复执行 standard execution precheck 返回 pass/up_to_date，不 bump revision、不产生 reason-only refreeze |
| AC-022 | TC-LG-022 | negative | `python3 -m pytest tests/test_v166_truth_canonical_branch.py::test_change_refreeze_chain_blocks_on_feature_branch tests/test_v166_truth_canonical_branch.py::test_freeze_command_blocks_on_feature_branch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | feature 分支上 freeze/refreeze-chain blocked，`reason_code=truth_canonical_branch_mismatch` |
| AC-023 | TC-LG-023 | negative | `python3 -m pytest tests/test_v166_truth_canonical_branch.py -k truth_file_write -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 非 truth_canonical 写 feature package Markdown → blocked；在 main 写不要求 feature worktree cwd |
| AC-024 | TC-LG-024 | contract | `python3 -m pytest tests/test_v166_truth_canonical_branch.py::test_truth_authoring_skills_get_canonical_branch_preamble tests/test_v166_truth_canonical_branch.py::test_delivery_skills_keep_worktree_admission_preamble -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | truth 编写 skill 含 truth_canonical preamble；delivery skill 含 workspace admit |
| AC-025 | TC-LG-025 | contract | `python3 -m pytest tests/test_v166_loop_goal.py -k cli_owned_precheck -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | CLI 产出 verification bundle artifact；无 artifact ref 的 agent 自报 pass 被拒绝 |
| AC-026 | TC-LG-026 | contract | `python3 -m pytest tests/test_v166_truth_canonical_branch.py::test_loop_goal_skill_declares_truth_canonical_gate -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | public SKILL.md Step 2 含 truth_canonical 校验与 `truth_canonical_branch_mismatch` |
| AC-027 | TC-LG-027 | contract | `python3 -m pytest tests/test_v166_loop_goal.py -k human_gate_alignment -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | SKILL/auto-decide 表与 AC-007/AC-014 对齐；release 不可覆盖；P1-only 默认可续跑 |
| AC-028 | TC-LG-028 | contract | `python3 -m pytest tests/test_v166_loop_goal.py -k same_session_continue -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | public SKILL.md 声明同会话立即加载下一 skill，禁止只打印下一步 |
| AC-029 | TC-LG-029 | contract | `python3 -m pytest tests/test_v166_loop_goal.py -k loop_goal_resume -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `beacon status loop-goal --resume` 返回 current_stage + next skill；无状态时不得伪装成功 |
| AC-030 | TC-LG-030 | contract | `python3 -m pytest tests/test_v166_loop_goal.py -k observability_metrics -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | state/status 暴露 human_stops_per_run、stop_reason 分布、p1_continue_count |


| AC-031 | TC-LG-031 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_intent_context_state_outputs -q` | IntentContext.v1 字段写入 state |
| AC-032 | TC-LG-032 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_intent_fork_record_appends -q` | 路由分叉追加 intent_fork |
| AC-033 | TC-LG-033 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_decision_cache_prevents_repeat_ask -q` | decision_cache 去重 AskQuestion |
| AC-034 | TC-LG-034 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_interrupt_semantics_resume_substep -q` | interrupt 回 last_substep |
| AC-035 | TC-LG-035 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_resume_utterance_short_map -q` | 继续/continue 映射 load_next_skill |
| AC-036 | TC-LG-036 | integration | `python3 -m pytest tests/test_v167_loop_goal.py::test_loop_goal_run_cli_entry -q` | beacon loop-goal run 入口存在 |
| AC-037 | TC-LG-037 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_topology_gate_blocks_implement -q` | topology_gate blocked 不进 implement |
| AC-038 | TC-LG-038 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_dual_runtime_resume_parity -q` | host/cli resume 输出一致 |
| AC-039 | TC-LG-039 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_resilient_stop_contract -q` | stop 必含 reason_code + resume_action |
| AC-040 | TC-LG-040 | contract | `python3 -m pytest tests/test_v167_loop_goal.py::test_v2_schema_parity_fixtures -q` | v2 parity fixtures 可加载 |

## Verification Notes

- Test module `tests/test_v166_loop_goal.py` is created in implement phase.
- TC-LG-001/002/003/008/009 用 `tmp_path` project roots，mock state 文件。
- TC-LG-004/005/006/007 模拟阶段产出状态，验证编排器决策逻辑。
- TC-LG-010/012 读取 SKILL.md 内容，验证决策树完整性和 `review_routing` 公开契约。
- TC-LG-013/014 用 deterministic planner-review artifact fixture 验证 state outputs；R6 起 P1-only 必须 continue + audit，P0/user_decision/drift 仍阻断。
- TC-LG-015..021 用 deterministic git/admission fixtures 验证 Standard Execution Flow。
- TC-LG-022..026 验证 truth-on-main 第一性原理闭环。
- TC-LG-027..030 验证人类门重划、同会话续跑、resume CLI、观测指标。

## Must vs Should

| Priority | AC |
|----------|-----|
| Must | AC-001..029 |
| Should | AC-030 |
