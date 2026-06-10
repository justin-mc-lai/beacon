# 任务：Beacon Loop Goal Closed-Loop Orchestrator

## Phase E — Intent capture + review + delivery-state 骨架（AC-031..AC-033）

- [ ] TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。
- [ ] TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
- [ ] TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。
- [ ] TASK-044 新增 `packages/beacon-loop/src/delivery/state.ts` 与 `delivery-state.json` 读写。
- [ ] TASK-045 实现 planner review subprocess 适配器，写入 `review-artifact.json`（AC-033）。
- [ ] TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。
- [ ] TASK-047 CLI：`--strict-interrupt`（opt-in）、`--ack-intent-drift`；`--ask-on` deprecated。
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
- [ ] TASK-061 实现 AC-041：review lane 真并行（`execution_mode=parallel_subagent_review`）。
- [ ] TASK-062 更新 `evidence.md`；parent 回归 TC-040、TC-041。
- [ ] TASK-063 `beacon qa run` + release gate 正式验收本 feature（R1 AC-031..039）。

## Phase I — R2 green-light intent + lifecycle auto-route（AC-040..AC-042）

- [ ] TASK-064 实现 LLM intent tie-break adapter + `intent-tiebreak.json` 落盘（AC-040）。
- [ ] TASK-065 默认 green-light：`orchestrator` 移除 ambiguous→`user_decision_pending`；hard stop 白名单。
- [ ] TASK-066 CLI：`--strict-interrupt` opt-in；deprecate `--auto-decide deferrals` 作为 ambiguous 门控。
- [ ] TASK-067 实现 AC-042：`recommended_route` / Beacon lifecycle auto-route；无 AskUser UI。
- [ ] TASK-068 测试 TC-042..TC-044；更新 deferral ledger 运行时校验（rejected D-009..011）。
- [ ] TASK-069 R2 implement evidence + `beacon-eval-qa` 正式验收 AC-040..042。

## 边界

- 任务台账不是 implementation completion。
- loop 不得直接修改 `features/*/truth.md`；truth_fill 只经 Beacon CLI。
- 只有通过 `tests.md`、Beacon QA 和 release gate 后，才能将本 feature status 从 `draft` 升为 `frozen`。
