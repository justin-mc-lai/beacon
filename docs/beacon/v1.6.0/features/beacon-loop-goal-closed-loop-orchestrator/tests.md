# 测试：Beacon Loop Goal Closed-Loop Orchestrator

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-031 | TC-031 | contract | `cd packages/beacon-loop && npm test -- --test-name-pattern "intent-capture"` | `goal` 启动后在 run 目录生成 `intent-capture.json`（含 verbatim `utterance`）与 `intent-contract.json`。 |
| AC-032 | TC-032 | behavior | `cd packages/beacon-loop && npm test -- --test-name-pattern "intent-classify-deterministic"` | 相同 utterance + rules_hash 两次分类产出相同 `intent_class`、`scope_mode`；`rules_hash` 与 classifier 版本一致。 |
| AC-033 | TC-033 | integration | `cd packages/beacon-loop && BEACON_LOOP_TEST_REVIEW=fixture npm test -- --test-name-pattern "planner-review-artifact"` | `delivery`/`review-only` 写入 `review-artifact.json`，含 `intent_snapshot`、`scope_mode`、`findings`、`runtime_evidence_only=true`、`formal_verdict_authority=false`。 |
| AC-034 | TC-034 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "truth-fill-on-blocked"` | resolve blocked 时进入 `truth_fill`，`truth-promotion.json` 记录 beacon CLI 序列；无 accepted defer 时不写入 implicit mvp scope。 |
| AC-035 | TC-035 | negative | `cd packages/beacon-loop && npm test -- --test-name-pattern "frozen-gate-before-implement"` | truth 未 frozen 时 `delivery-state` 不得进入 `implement_loop`；`execute-only` 无 `--feature` 或 resolve fail 时 blocked。 |
| AC-036 | TC-036 | integration | `cd packages/beacon-loop && BEACON_LOOP_TEST_EVAL_CHAIN=fixture npm test -- --test-name-pattern "delivery-eval-chain"` | `--mode delivery` 依次 invoke import/qa/release stubs；payload 含 `closure_verdict=not_provided_by_beacon_loop` 与 beacon verdict refs。 |
| AC-037 | TC-037 | behavior | `cd packages/beacon-loop && npm test -- --test-name-pattern "qa-fail-repair-loop"` | qa fail fixture 触发 `repair_from_qa` → `implement_loop`；`notes.md` 含 qa finding 摘要；cap 后停止。 |
| AC-038 | TC-038 | contract | `cd packages/beacon-loop && npm test -- --test-name-pattern "delivery-state-machine"` | `delivery-state.json` 状态转移符合 truth State Model；非法转移测试失败；`resume` 从 `repair_from_qa`/`user_decision_pending` 恢复。 |
| AC-039 | TC-039 | e2e | `cd packages/beacon-loop && BEACON_LOOP_E2E_DELIVERY=1 npm test -- --test-name-pattern "e2e-utterance-to-release"` | scripted E2E：utterance → review → truth frozen fixture → implement → import → qa → release invoke；release verdict 来自 beacon fixture 非 loop。 |
| AC-040 | TC-042 | behavior | `cd packages/beacon-loop && BEACON_LOOP_TEST_TIEBREAK=fixture npm test -- --test-name-pattern "llm-tiebreak-green-light"` | 规则 `ambiguous=true` 时写 `intent-tiebreak.json` 且 `delivery-state` 进入 `truth_gap_scan`（非 `user_decision_pending`）；默认 mode 无 `--strict-interrupt`。 |
| AC-041 | TC-043 | integration | `cd packages/beacon-loop && BEACON_LOOP_TEST_REVIEW=parallel-fixture npm test -- --test-name-pattern "parallel-review-lanes"` | review runtime parallel 模式；`review-artifact.json` 含 per-lane refs。 |
| AC-042 | TC-044 | behavior | `cd packages/beacon-loop && npm test -- --test-name-pattern "lifecycle-auto-route"` | P1 finding 默认 continue；`recommended_route` 驱动下一状态；无 AskUser subprocess。 |

## 非法转移测试（TC-038 子集）

| TC ID | From | To | Expected |
|-------|------|-----|----------|
| TC-038a | `intent_capture` | `implement_loop` | blocked |
| TC-038b | `truth_gap_scan` | `implement_loop`（truth 未 frozen） | blocked |
| TC-038c | `implement_loop` | `terminal_closed` | blocked |
| TC-038d | `qa_pending` | `terminal_closed`（无 release invoke） | blocked |

## Parent 依赖覆盖（parent feature frozen truth）

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-003 | TC-040 | regression | `cd packages/beacon-loop && npm test` | parent `goal` entrypoint 保留；本 feature 扩展 `--mode` 不破坏既有 goal 契约。 |
| AC-004 | TC-034 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "truth-fill-on-blocked"` | resolve blocked 时进入 `truth_fill` 而非仅 abort（扩展 parent resolver 行为）。 |
| AC-005 | TC-034 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "truth-fill-on-blocked"` | truth gap 与 resolve blocked 共用 truth_fill 子链；parity 缺口有 promotion 记录。 |
| AC-016 | TC-040 | regression | `cd packages/beacon-loop && npm test` | parent orchestrator 子状态（含 `implement_loop`）仍 pass；delivery-state 与之合成。 |
| AC-021 | TC-040 | regression | `cd packages/beacon-loop && npm test` | parent orchestrator harness 与 ledger 写入契约仍 pass。 |
| AC-022 | TC-040 | regression | `cd packages/beacon-loop && npm test` | delivery-state 写入同一 ledger；diagnose 分桶不回归。 |
| AC-025 | TC-041 | regression | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py` | parent diagnose / automation retirement 路由仍 pass。 |

## Parent 回归

| TC ID | Layer | Command | Assertion |
|-------|-------|---------|-----------|
| TC-040 | regression | `cd packages/beacon-loop && npm test` | 本 feature 不破坏 parent AC-001..AC-030 已有测试（26+ cases）。 |
| TC-041 | regression | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py` | automation retirement 与 goal entrypoint 契约仍 pass。 |

## 验证说明

- Benchmark/runtime evidence 不能替代 formal `beacon-eval-qa` 或 release verdict。
- TC-033/036/039 允许 test fixture 模拟 beacon/planner subprocess；生产路径必须调用真实 CLI。
- 本包 R2 refreeze 后 AC-040..AC-042 进入 authoritative coverage；R1 实现仅覆盖 AC-031..AC-039，R2 implement 前 TC-042..044 可 blocked/pending。
