# Test Cases: beacon-loop-goal-closed-loop-orchestrator

## Overview

**Feature**: beacon-loop-goal-closed-loop-orchestrator
**Test Type**: ALL
**Version**: v1.6.0
**Generated**: 2026-06-10 16:30
**Requested Mode**: auto
**Effective Mode**: markdown
**Fallback Reason**: N/A
**Memory Context**: N/A
**AC Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.ac-test-matrix.json
**QA9 Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.qa9-matrix.json
**Story Scenario Map JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.0/.machine/qa/beacon-loop-goal-closed-loop-orchestrator.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-031 | TC-031 | contract | `cd packages/beacon-loop && npm test -- --test-name-pattern "intent-capture"` | `goal` 启动后在 run 目录生成 `intent-capture.json`（含 verbatim `utterance`）与 `intent-contract.json`。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-031.json` |
| AC-032 | TC-032 | behavior | `cd packages/beacon-loop && npm test -- --test-name-pattern "intent-classify-deterministic"` | 相同 utterance + rules_hash 两次分类产出相同 `intent_class`、`scope_mode`；`rules_hash` 与 classifier 版本一致。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-032.json` |
| AC-033 | TC-033 | integration | `cd packages/beacon-loop && BEACON_LOOP_TEST_REVIEW=fixture npm test -- --test-name-pattern "planner-review-artifact"` | `delivery`/`review-only` 写入 `review-artifact.json`，含 `intent_snapshot`、`scope_mode`、`findings`、`runtime_evidence_only=true`、`formal_verdict_authority=false`。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-033.json` |
| AC-034 | TC-034 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "truth-fill-on-blocked"` | resolve blocked 时进入 `truth_fill`，`truth-promotion.json` 记录 beacon CLI 序列；无 accepted defer 时不写入 implicit mvp scope。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-034.json` |
| AC-035 | TC-035 | negative | `cd packages/beacon-loop && npm test -- --test-name-pattern "frozen-gate-before-implement"` | truth 未 frozen 时 `delivery-state` 不得进入 `implement_loop`；`execute-only` 无 `--feature` 或 resolve fail 时 blocked。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-035.json` |
| AC-036 | TC-036 | integration | `cd packages/beacon-loop && BEACON_LOOP_TEST_EVAL_CHAIN=fixture npm test -- --test-name-pattern "delivery-eval-chain"` | `--mode delivery` 依次 invoke import/qa/release stubs；payload 含 `closure_verdict=not_provided_by_beacon_loop` 与 beacon verdict refs。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-036.json` |
| AC-037 | TC-037 | behavior | `cd packages/beacon-loop && npm test -- --test-name-pattern "qa-fail-repair-loop"` | qa fail fixture 触发 `repair_from_qa` → `implement_loop`；`notes.md` 含 qa finding 摘要；cap 后停止。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-037.json` |
| AC-038 | TC-038 | contract | `cd packages/beacon-loop && npm test -- --test-name-pattern "delivery-state-machine"` | `delivery-state.json` 状态转移符合 truth State Model；非法转移测试失败；`resume` 从 `repair_from_qa`/`user_decision_pending` 恢复。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-038.json` |
| AC-039 | TC-039 | e2e | `cd packages/beacon-loop && BEACON_LOOP_E2E_DELIVERY=1 npm test -- --test-name-pattern "e2e-utterance-to-release"` | scripted E2E：utterance → review → truth frozen fixture → implement → import → qa → release invoke；release verdict 来自 beacon fixture 非 loop。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-039.json` |
| AC-003 | TC-040 | regression | `cd packages/beacon-loop && npm test` | parent `goal` entrypoint 保留；本 feature 扩展 `--mode` 不破坏既有 goal 契约。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-040.json` |
| AC-004 | TC-034 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "truth-fill-on-blocked"` | resolve blocked 时进入 `truth_fill` 而非仅 abort（扩展 parent resolver 行为）。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-034.json` |
| AC-005 | TC-034 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "truth-fill-on-blocked"` | truth gap 与 resolve blocked 共用 truth_fill 子链；parity 缺口有 promotion 记录。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-034.json` |
| AC-016 | TC-040 | regression | `cd packages/beacon-loop && npm test` | parent orchestrator 子状态（含 `implement_loop`）仍 pass；delivery-state 与之合成。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-040.json` |
| AC-021 | TC-040 | regression | `cd packages/beacon-loop && npm test` | parent orchestrator harness 与 ledger 写入契约仍 pass。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-040.json` |
| AC-022 | TC-040 | regression | `cd packages/beacon-loop && npm test` | delivery-state 写入同一 ledger；diagnose 分桶不回归。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-040.json` |
| AC-025 | TC-041 | regression | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | parent diagnose / automation retirement 路由仍 pass。 | `.beacon/evidence/test-results/beacon-loop-goal-closed-loop-orchestrator/{run_id}/TC-041.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-031 | Pending | from AC-031 |
| TC-032 | Pending | from AC-032 |
| TC-033 | Pending | from AC-033 |
| TC-034 | Pending | from AC-034 |
| TC-035 | Pending | from AC-035 |
| TC-036 | Pending | from AC-036 |
| TC-037 | Pending | from AC-037 |
| TC-038 | Pending | from AC-038 |
| TC-039 | Pending | from AC-039 |
| TC-040 | Pending | from AC-003 |
| TC-034 | Pending | from AC-004 |
| TC-034 | Pending | from AC-005 |
| TC-040 | Pending | from AC-016 |
| TC-040 | Pending | from AC-021 |
| TC-040 | Pending | from AC-022 |
| TC-041 | Pending | from AC-025 |
