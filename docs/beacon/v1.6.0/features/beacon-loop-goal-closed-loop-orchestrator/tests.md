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
| AC-043 | TC-045 | contract | `beacon doctor verify-agent-surface --project-root . --agent cursor --strict` | agent surface / using-beacon 含 `beacon-loop goal` launch、steer、hard stop；无 subprocess skill load 要求。 |
| AC-044 | TC-046 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "implement-harness-worker"` | `implement_loop` subprocess 为 `beacon implement run … --runner`；grep/ shim 证明无裸 `codex exec` bypass。 |
| AC-045 | TC-047 | contract | `cd packages/beacon-loop && npm test -- --test-name-pattern "output-schema"` | run 目录存在 `output-schema.json`；adapter 传 `--output-schema`；invalid JSON → iteration failure。 |
| AC-046 | TC-048 | behavior | `cd packages/beacon-loop && npm test -- --test-name-pattern "gnhf-iteration-prompt"` | prompt 含 notes 只读、no-op=false、禁 agent commit；结构对齐 gnhf template 必填节。 |
| AC-047 | TC-049 | negative | `cd packages/beacon-loop && BEACON_LOOP_TEST_AGENT_RESULT=noop npm test -- --test-name-pattern "noop-blocks-qa"` | no-op iteration 后 `delivery-state` 不得进入 `qa_pending`；含 `implement_no_op_blocked`。 |
| AC-048 | TC-050 | contract | `cd packages/beacon-loop && npm test -- --test-name-pattern "harness-worker-route"` | 各 delivery stage 映射 harness worker；`truth-promotion.json` 记录 command + runner id。 |
| AC-049 | TC-051 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "repair-harness-worker"` | `repair_from_qa` 回灌使用同一 implement runner 路径。 |
| AC-050 | TC-052 | regression | `cd packages/beacon-loop && npm test` | AC-044 接入后 parent orchestrator 测试仍 pass（caps/stop/notes/no-op）。 |
| AC-051 | TC-053 | e2e | `cd packages/beacon-loop && BEACON_LOOP_E2E_HARNESS=1 npm test -- --test-name-pattern "e2e-implement-runner-commit"` | 真 implement runner 路径；worktree ≥1 commit 后才 `qa_pending`（可 CI opt-in）。 |
| AC-052 | TC-054 | integration | `cd packages/beacon-loop && node dist/cli.js doctor --project .. --diagnose --json` | doctor 报告 implement runner / codex / schema 分桶与 repair route。 |
| AC-053 | TC-055 | contract | `cd packages/beacon-run && pnpm test -- --test-name-pattern "orchestrator"` | `packages/beacon-run` 自 gnhf fork；`createAgent` 支持 codex/claude/opencode；CLI `beacon-run run` 存在。 |
| AC-054 | TC-056 | behavior | `cd packages/beacon-run && pnpm test -- --test-name-pattern "beacon-phase-prompt"` | iteration prompt 含 Beacon phase、skill boundary digest、`beacon-phase.json` 落盘；无 subprocess Skill MD。 |
| AC-055 | TC-057 | integration | `cd packages/beacon-run && pnpm test -- --test-name-pattern "truth-phase-agent"` | truth phase 使用 agent adapter（非仅 harness 模板）；mock agent 记录 phase=truth。 |
| AC-056 | TC-058 | negative | `cd packages/beacon-run && pnpm test -- --test-name-pattern "no-default-template-truth"` | 默认配置不调用 `prd-bootstrap`；仅 `--truth-bootstrap=fallback` 启用模板链。 |
| AC-057 | TC-059 | contract | `cd packages/beacon-run && pnpm test -- --test-name-pattern "harness-checkpoint"` | 迭代间 harness 调用写入 `truth-promotion.json`（phase、command、exit_code）。 |
| AC-058 | TC-060 | regression | `cd packages/beacon-loop.r3-backup-20260610 && npm test` | R3 备份测试仍 pass；新开发不在 `packages/beacon-loop` 增 AC。 |
| AC-059 | TC-061 | integration | `beacon implement run --help` | CLI 暴露 `--output-schema`；与 beacon-run adapter 契约一致。 |
| AC-060 | TC-062 | e2e | `cd packages/beacon-run && BEACON_RUN_E2E_DRILL=1 pnpm test -- --test-name-pattern "e2e-gum-drill"` | drill repo utterance：truth agent iteration + ≥1 commit + qa invoke；verdict 来自 beacon。 |

## R4 — beacon-run gnhf agent orchestration（AC-053..AC-060）

R4 authoritative rows 已并入上方 **覆盖矩阵**（TC-055..TC-062）。

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-053 | TC-055 | contract | `cd packages/beacon-run && pnpm test` | gnhf orchestrator + multi-agent factory 在 beacon-run 包内可构建可测。 |
| AC-054 | TC-056 | behavior | `cd packages/beacon-run && pnpm test -- --test-name-pattern "beacon-phase-prompt"` | Beacon lifecycle 编入 iteration prompt。 |
| AC-055 | TC-057 | integration | `cd packages/beacon-run && pnpm test -- --test-name-pattern "truth-phase-agent"` | truth 阶段走 agent 而非纯模板 CLI。 |
| AC-056 | TC-058 | negative | `cd packages/beacon-run && pnpm test -- --test-name-pattern "no-default-template-truth"` | 默认禁用模板 truth_fill。 |
| AC-057 | TC-059 | contract | `cd packages/beacon-run && pnpm test -- --test-name-pattern "harness-checkpoint"` | harness 检查点记账。 |
| AC-058 | TC-060 | regression | R3 backup npm test | beacon-loop 冻结为参考实现。 |
| AC-059 | TC-061 | integration | `beacon implement run --help` | `--output-schema` 在 Core CLI 可用。 |
| AC-060 | TC-062 | e2e | `BEACON_RUN_E2E_DRILL=1` | gum drill 真项目闭环。 |

## R3 — gnhf + Harness Worker（AC-043..AC-052）

R3 authoritative rows 已并入上方 **覆盖矩阵**（TC-045..TC-054）；本节保留 AC 分组说明。

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-043 | TC-045 | contract | `beacon doctor verify-agent-surface --project-root . --agent cursor --strict` | agent surface / using-beacon 含 `beacon-loop goal` launch、steer、hard stop；无 subprocess skill load 要求。 |
| AC-044 | TC-046 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "implement-harness-worker"` | `implement_loop` subprocess 为 `beacon implement run … --runner`；grep/ shim 证明无裸 `codex exec` bypass。 |
| AC-045 | TC-047 | contract | `cd packages/beacon-loop && npm test -- --test-name-pattern "output-schema"` | run 目录存在 `output-schema.json`；adapter 传 `--output-schema`；invalid JSON → iteration failure。 |
| AC-046 | TC-048 | behavior | `cd packages/beacon-loop && npm test -- --test-name-pattern "gnhf-iteration-prompt"` | prompt 含 notes 只读、no-op=false、禁 agent commit；结构对齐 gnhf template 必填节。 |
| AC-047 | TC-049 | negative | `cd packages/beacon-loop && BEACON_LOOP_TEST_AGENT_RESULT=noop npm test -- --test-name-pattern "noop-blocks-qa"` | no-op iteration 后 `delivery-state` 不得进入 `qa_pending`；含 `implement_no_op_blocked`。 |
| AC-048 | TC-050 | contract | `cd packages/beacon-loop && npm test -- --test-name-pattern "harness-worker-route"` | 各 delivery stage 映射 harness worker；`truth-promotion.json` 记录 command + runner id。 |
| AC-049 | TC-051 | integration | `cd packages/beacon-loop && npm test -- --test-name-pattern "repair-harness-worker"` | `repair_from_qa` 回灌使用同一 implement runner 路径。 |
| AC-050 | TC-052 | regression | `cd packages/beacon-loop && npm test` | AC-044 接入后 parent orchestrator 测试仍 pass（caps/stop/notes/no-op）。 |
| AC-051 | TC-053 | e2e | `cd packages/beacon-loop && BEACON_LOOP_E2E_HARNESS=1 npm test -- --test-name-pattern "e2e-implement-runner-commit"` | 真 implement runner 路径；worktree ≥1 commit 后才 `qa_pending`（可 CI opt-in）。 |
| AC-052 | TC-054 | integration | `cd packages/beacon-loop && node dist/cli.js doctor --project .. --diagnose --json` | doctor 报告 implement runner / codex / schema 分桶与 repair route。 |

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
| AC-019 | TC-022 | regression | `cd packages/beacon-loop && npm test -- --test-name-pattern "consecutive failures"` | parent runner：连续失败 abort；no-op iteration 计 failure；R3 harness worker 路径仍遵守 backoff 语义。 |
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
- **R3 authoritative**：AC-043..AC-052（TC-045..TC-054）已并入覆盖矩阵；refreeze 后 formal QA 必须执行。
- TC-053 真 E2E 可在 CI 设 `BEACON_LOOP_E2E_HARNESS=1` opt-in；不得用 fixture-only 替代 AC-051 closure。
