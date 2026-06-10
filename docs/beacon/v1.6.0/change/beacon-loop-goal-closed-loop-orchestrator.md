# Change Record: beacon-loop-goal-closed-loop-orchestrator

- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- change_reason: `goal-delivery-orchestrator-from-utterance-to-stable-closure`
- artifact_role: `change_record_not_requirement_truth`
- truth_source: `false`
- parent_feature: `beacon-loop-native-runner-and-automation-retirement`
- user_decision: `accepted`

## Rationale

用户确认：下一代 `beacon-loop goal "<用户原话>"` 不应仅绑定已冻结 feature truth 后进入 implement loop，而应从**用户目标原话**出发：

1. 洞悉**确定性意图**（`intent-contract`）
2. 自动触发 **planner multi-agent review**
3. 识别并补齐 **Beacon requirement truth**（truth_fill 子链）
4. 编排 **implement → import-evidence → qa → release** 全链
5. 支持长任务 **resume / stop / repair**，稳定交付且不静默 MVP 化

`beacon-loop-native-runner-and-automation-retirement` 已 frozen，覆盖 AC-001..AC-030（runner、harness、E2E import→qa 契约）。该包定义的是 **execution runner**，未定义 **utterance-driven delivery orchestrator**。

Planner review 与 prior 对话已判定：把 plan 意图直接落成 MVP 骨架是漂移根因；本 change 通过 **intent capture + review gate + truth_fill gate + delivery state machine** 在 loop 入口阻断。

## Scope Change

| Before（parent frozen truth） | After（本 feature draft） |
|------------------------------|---------------------------|
| `goal` 必须先 `truth-map resolve` pass | `goal` 可从 utterance 启动；resolve blocked 进入 `truth_fill` |
| `slugify(goal)` 可隐式猜 feature | utterance 与 feature slug **解耦**；feature 由 intent contract + resolver 决定 |
| 闭环止于 import→qa 契约（AC-030） | **delivery 模式**自动 invoke qa/release；QA fail 可回灌 implement |
| runner state machine only | 扩展 **Delivery Loop** state machine（intent→review→truth→implement→eval） |
| 无 intent/review runtime 落点 | 必填 `intent-capture.json`、`intent-contract.json`、`review-artifact.json`、`delivery-state.json` |

## Relationship to Parent Feature

本 feature **扩展** `beacon-loop-native-runner-and-automation-retirement`，不替换其 AC-001..AC-030：

- Parent：TypeScript runner、ledger、harness、agent adapters、implementation loop 语义
- This feature：goal 入口的 **Delivery Orchestrator**（AC-031..AC-039）

实现依赖 parent Phase A-D 能力；本 feature Phase E-H 在 parent 之上叠加。

## Accepted Deferrals

| ID | Capability | Decision | Revisit |
|----|------------|----------|---------|
| D-009 | 并行 review lane 真多进程（非 subprocess 串行） | `accepted` defer | Phase H |
| D-010 | LLM tie-break 意图分类（默认仅规则确定性） | `accepted` defer | v1.6.x patch |
| D-011 | 交互式 `AskUserQuestion` 门控 UI（CLI 先用 flags） | `accepted` defer | v1.6.x patch |

## Non-Deferrals（must land in this feature truth）

- AC-031..AC-039 全部进入 package truth / tests
- Delivery Loop State Model + illegal transition 测试
- Deterministic intent classification contract
- Automatic planner review artifact 落盘
- truth_fill 子链（经 Beacon generator CLI，loop 不直写 truth）
- truth frozen gate before implement_loop
- delivery 模式 qa/release invoke + QA fail 回灌
- E2E utterance → release（verdict 来自 Beacon evaluator）

## Promotion Diff

进入 `features/beacon-loop-goal-closed-loop-orchestrator/` 的新增承诺：

- `Scope Mode` = `full_parity`（delivery orchestrator 层）
- `Intent Contract Schema`
- `Delivery Loop State Model`
- `Orchestrator Modes`（delivery / execute-only / intent-only / review-only）
- `Truth Fill Subchain Contract`
- `Parent Feature Dependency Matrix`
- AC-031..AC-039 与 tests/tasks Phase E-H

## Next Route

1. 用户审阅本 change + truth/tests 草案
2. `beacon change ... --refreeze-chain` 或 `beacon-gen-refreeze` 冻结本 feature package
3. `beacon-gen-implement` Phase E 起（intent capture + delivery-state 骨架）
