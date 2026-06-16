# 测试：Beacon Loop Goal Closed-Loop Orchestrator v1.6.1

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-072 | TC-LOOP-072 | contract | `rg -q 'AC-072' docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md && rg -q 'beacon-loop goal' docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md && python3 -m pytest tests/test_v161_loop_goal_closed_loop_orchestrator.py::test_truth_ac072_unified_goal_and_scope -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | truth 定义统一 goal + 湖/海；delegate 源码存在。 |
| AC-073 | TC-LOOP-073 | behavior | `python3 -m pytest tests/test_v161_loop_goal_closed_loop_orchestrator.py::test_program_outer_fsm_vitest_gate -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `--mode program` P0–P6 + P4 gate（vitest program-outer-fsm）。 |
| AC-074 | TC-LOOP-074 | contract | `rg -q 'eval-matrix' docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md && rg -q 'formal_verdict_authority=false' docs/beacon/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md && python3 -m pytest tests/test_v161_loop_goal_closed_loop_orchestrator.py::test_truth_ac074_eval_supplement_contract -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | eval supplement 契约 + runtime 模块存在。 |
| AC-075 | TC-LOOP-075 | e2e | `python3 -m pytest tests/test_v161_loop_goal_closed_loop_orchestrator.py::test_e2e_program_sea_vitest_gate -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 海级 program E2E opt-in fixture（vitest e2e-program-sea）。 |

## Upstream inheritance（v1.6.0 R10 — delegated coverage）

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-031 | TC-LOOP-UP-031 | upstream | `rg -q 'AC-031' docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md` | 由 v1.6.0 frozen R10 覆盖；v1.6.1 不得破坏。 |
| AC-068 | TC-LOOP-UP-068 | upstream | `rg -q 'truth_freeze_gate' docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md` | per-lake truth_freeze_gate 仍由 upstream 权威。 |
| AC-069..071 | TC-LOOP-UP-069 | upstream | `rg -q 'AC-069' docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md` | 止血 AC 仍由 v1.6.0 package 覆盖；v1.6.1 不得回归破坏。 |
| AC-071 | TC-LOOP-UP-071 | upstream | `rg -q 'AC-071' docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md` | stop-when 契约由 upstream 覆盖。 |

## v1.6.1 delta coverage

- Formal QA/release 由 `beacon-eval-qa` / `beacon-eval-release` 裁决；矩阵命令须产出 junit 证据。

## State-machine coverage

| Scenario | TC ID | Expected |
|----------|-------|----------|
| 海级跳过 P4 直 spawn delivery | TC-LOOP-073 | invalid transition blocked |
| eval supplement 尝试 gate qa | TC-LOOP-074 | blocked；formal_verdict_authority=false |
