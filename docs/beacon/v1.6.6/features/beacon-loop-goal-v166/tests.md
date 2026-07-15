---
slug: beacon-loop-goal-v166
version: v1.6.6
status: frozen
revision_id: R2
language: zh
truth_ref: docs/beacon/v1.6.6/features/beacon-loop-goal-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Loop Goal Orchestrator v1.6.6

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-LG-001 | contract | `python3 -m pytest tests/test_v166_loop_goal.py::test_state_init_creates_file -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `loop_goal_state.init()` 创建 `.beacon/state/loop-goal/<run_id>.json`，schema 为 `loop-goal-state.v1`，含 run_id/version/feature/utterance/current_stage |
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

## Verification Notes

- Test module `tests/test_v166_loop_goal.py` is created in implement phase.
- TC-LG-001/002/003/008/009 用 `tmp_path` project roots，mock state 文件。
- TC-LG-004/005/006/007 模拟阶段产出状态，验证编排器决策逻辑。
- TC-LG-010 读取 SKILL.md 内容，验证决策树完整性。

## Must vs Should

| Priority | AC |
|----------|-----|
| Must | AC-001..011 |
