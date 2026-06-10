# 任务：Beacon Loop Goal Closed-Loop Orchestrator

## Phase E — Intent capture + review + delivery-state 骨架（AC-031..AC-033）

- [ ] TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。
- [ ] TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
- [ ] TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。
- [ ] TASK-044 新增 `packages/beacon-loop/src/delivery/state.ts` 与 `delivery-state.json` 读写。
- [ ] TASK-045 实现 planner review subprocess 适配器，写入 `review-artifact.json`（AC-033）。
- [ ] TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。
- [ ] TASK-047 CLI：`--ask-on`、`--auto-decide deferrals`、`--ack-intent-drift`。
- [ ] TASK-048 测试 TC-031..TC-033、TC-038 骨架。

## Phase F — Truth fill 子链 + freeze gate（AC-034..AC-035）

- [ ] TASK-049 实现 `truth_gap_scan`：resolve + review parity 缺口合成。
- [ ] TASK-050 实现 `truth_fill` 子链编排器，记录 `truth-promotion.json`（beacon gen-* CLI 序列）。
- [ ] TASK-051 实现 `truth_freeze_gate`：frozen 前 block `implement_loop`（AC-035）。
- [ ] TASK-052 `execute-only` 模式：强制 `--feature` + resolve pass。
- [ ] TASK-053 测试 TC-034、TC-035、TC-038b。

## Phase G — Delivery evaluator chain + QA repair（AC-036..AC-037）

- [ ] TASK-054 `--mode delivery` 自动链：import-evidence → beacon qa → beacon release（subprocess + JSON 解析）。
- [ ] TASK-055 输出 payload：`closure_verdict`、`beacon_qa_verdict_ref`、`beacon_release_verdict_ref`。
- [ ] TASK-056 实现 `repair_from_qa`：qa findings 注入 notes，回灌 `implement_loop`。
- [ ] TASK-057 测试 TC-036、TC-037。

## Phase H — Resume + E2E + 并行 review（AC-038..AC-039, D-009）

- [ ] TASK-058 `resume` 扩展：恢复 `delivery-state`（含 `user_decision_pending`、`repair_from_qa`）。
- [ ] TASK-059 非法转移 guard 与 TC-038a..d。
- [ ] TASK-060 scripted E2E `e2e-delivery-closed-loop.mjs`（AC-039 / TC-039）。
- [ ] TASK-061 defer D-009: review lane 并行化评估与实现。
- [ ] TASK-062 更新 `evidence.md`；parent 回归 TC-040、TC-041。
- [ ] TASK-063 `beacon qa run` + release gate 正式验收本 feature。

## 边界

- 任务台账不是 implementation completion。
- loop 不得直接修改 `features/*/truth.md`；truth_fill 只经 Beacon CLI。
- 只有通过 `tests.md`、Beacon QA 和 release gate 后，才能将本 feature status 从 `draft` 升为 `frozen`。
