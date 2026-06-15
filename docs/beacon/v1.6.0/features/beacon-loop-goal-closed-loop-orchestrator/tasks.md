# 任务：Beacon Loop Goal Closed-Loop Orchestrator

## Phase E — Intent capture + review + delivery-state 骨架（AC-031..AC-033）

- [x] TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。evidence: capture.ts, classify.ts exist
- [x] TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。evidence: rules.ts exists
- [x] TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。evidence: feature-resolve.ts, feature-slug.ts exist
- [x] TASK-044 新增 `packages/beacon-loop/src/delivery/state.ts` 与 `delivery-state.json` 读写。evidence: state.ts exists
- [x] TASK-045 实现 planner review subprocess 适配器，写入 `review-artifact.json`（AC-033）。evidence: review.ts exists
- [x] TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。evidence: orchestrator.js mode dispatch
- [x] TASK-047 CLI：`--strict-interrupt`（opt-in）、`--ack-intent-drift`；`--ask-on` deprecated。evidence: CLI flags in orchestrator
- [x] TASK-048 测试 TC-031..TC-033、TC-038 骨架。evidence: beacon-loop.test.mjs, delivery-orchestrator.test.mjs pass

## Phase F — Truth fill 子链 + freeze gate（AC-034..AC-035）

- [x] TASK-049 实现 `truth_gap_scan`：resolve + review parity 缺口合成。evidence: orchestrator.ts truth_gap_scan
- [x] TASK-050 实现 `truth_fill` 子链编排器，记录 `truth-promotion.json`（beacon gen-* CLI 序列）。evidence: truth-fill.ts exists
- [x] TASK-051 实现 `truth_freeze_gate`：frozen 前 block `implement_loop`（AC-035）。evidence: truth-frozen.ts + harness-checkpoint.ts
- [x] TASK-052 `execute-only` 模式：强制 `--feature` + resolve pass。evidence: mode dispatch in orchestrator
- [x] TASK-053 测试 TC-034、TC-035、TC-038b。evidence: delivery-orchestrator.test.mjs pass

## Phase G — Delivery evaluator chain + QA repair（AC-036..AC-037）

- [x] TASK-054 `--mode delivery` 自动链：import-evidence → beacon qa → beacon release（subprocess + JSON 解析）。evidence: eval-chain.ts + orchestrator.js closure_verdict
- [x] TASK-055 输出 payload：`closure_verdict`、`beacon_qa_verdict_ref`、`beacon_release_verdict_ref`。evidence: orchestrator.js verdict refs
- [x] TASK-056 实现 `repair_from_qa`：qa findings 注入 notes，回灌 `implement_loop`。evidence: phase-controller.ts repair_from_qa
- [x] TASK-057 测试 TC-036、TC-037。evidence: delivery-orchestrator.test.mjs pass

## Phase H — Resume + E2E + 并行 review（AC-038..AC-039, D-009）

- [x] TASK-058 `resume` 扩展：恢复 `delivery-state`（含 `user_decision_pending`、`repair_from_qa`）。evidence: state.ts resume logic
- [x] TASK-059 非法转移 guard 与 TC-038a..d。evidence: delivery-orchestrator.test.mjs illegal transition tests
- [x] TASK-060 scripted E2E `e2e-delivery-closed-loop.mjs`（AC-039 / TC-039）。evidence: e2e-cli.test.ts, e2e.test.ts exist
- [x] TASK-061 实现 AC-041：review lane 真并行（`execution_mode=parallel_subagent_review`）。evidence: review.ts parallel mode
- [x] TASK-062 更新 `evidence.md`；parent 回归 TC-040、TC-041。evidence: evidence.md updated
- [x] TASK-063 `beacon qa run` + release gate 正式验收本 feature（R1 AC-031..039）。evidence: QA passed per truth.md

## Phase I — R2 green-light intent + lifecycle auto-route（AC-040..AC-042）

- [x] TASK-064 实现 LLM intent tie-break adapter + `intent-tiebreak.json` 落盘（AC-040）。
- [x] TASK-065 默认 green-light：`orchestrator` 移除 ambiguous→`user_decision_pending`；hard stop 白名单。
- [x] TASK-066 CLI：`--strict-interrupt` opt-in；deprecate `--auto-decide deferrals` 作为 ambiguous 门控。
- [x] TASK-067 实现 AC-042：`recommended_route` / Beacon lifecycle auto-route；无 AskUser UI。
- [x] TASK-068 测试 TC-042..TC-044；更新 deferral ledger 运行时校验（rejected D-009..011）。
- [x] TASK-069 R2 implement evidence + `beacon-eval-qa` 正式验收 AC-040..042。

## Phase J — R3 gnhf worker + harness implement runner（AC-043..AC-052）

- [x] TASK-070 更新 agent surface / `using-beacon`：gnhf 级 launch、steer、companion 文档（AC-043）。
- [x] TASK-071 `implement_loop` 改为 subprocess `beacon implement run --runner <runner>`；移除裸 `codex exec` 路径（AC-044）。
- [x] TASK-072 写入 `output-schema.json`；adapter strict parse + `--output-schema`（AC-045）。
- [x] TASK-073 gnhf 级 `iteration-prompt` 模板；no-op=false 语义（AC-046）。
- [x] TASK-074 delivery FSM：`implement_no_op_blocked`；禁止 no-op → `qa_pending`（AC-047）。
- [x] TASK-075 frozen harness worker 路由表 + `truth-promotion.json` worker 记录（AC-048）。
- [x] TASK-076 `repair_from_qa` 复用 implement harness worker（AC-049）。
- [x] TASK-077 parent orchestrator 回归 + doctor implement runner 检查（AC-050、AC-052）。
- [x] TASK-078 真 implement runner E2E opt-in（AC-051 / TC-053）。
- [x] TASK-079 测试 TC-045..TC-054；`beacon change … --refreeze-chain` 冻结 R3 truth package。

## Phase K — R4 beacon-run gnhf fork + agent truth（AC-053..AC-060）

- [x] TASK-080 fork `packages/gnhf` → `packages/beacon-run`；package/bin 重命名；保留 gnhf 测试基线。
- [x] TASK-081 实现 `beacon-phase-prompt` 模块：注入 Beacon 阶段 + skill boundary digest；落盘 `beacon-phase.json`（AC-054）。
- [x] TASK-082 truth phase：默认 agent iteration 路径；`--truth-bootstrap=fallback` 回退模板链（AC-055、AC-056）。
- [x] TASK-083 迭代间 harness checkpoint + `truth-promotion.json` 扩展 phase 字段（AC-057）。
- [x] TASK-084 `beacon-loop goal` 薄委托 `beacon-run` + deprecated 文档（AC-058）。
- [x] TASK-085 Core：`beacon implement run --output-schema` 与 branch preflight doctor 消息（AC-059）。
- [x] TASK-086 drill E2E `e2e-gum-drill` opt-in（AC-060 / TC-062）。
- [x] TASK-087 R4 refreeze（`beacon change --refreeze-chain` complete，R3→R4）。
- [x] TASK-088 Phase K implement + `beacon-eval-qa` 验收 AC-053..060。

## Phase L — R5 worktree harness + clarity + smoke exit（AC-061..AC-064）

- [x] TASK-089 `beacon-run`：`--worktree --beacon` 时 harness `projectRoot = effectiveCwd`；beacon-loop delegate 文档化（AC-061）。
- [x] TASK-090 测试 TC-063：`worktree-harness-project-root`（mock harness，assert truth-promotion path）。
- [x] TASK-091 `requirement_clarity`：拉丁 marker 词界 + frontmatter/path 豁免；TC-064 fixture `go-todo-crud-smoke`（AC-062）。
- [x] TASK-092 `buildPhaseHarnessArgs` / phase-controller：读 target `scope_mode`；smoke truth exit 跳过 sync-materials（AC-063）。
- [x] TASK-093 `beacon-phase.json`：`phase_promoted` + harness 失败日志（AC-064）。
- [x] TASK-094 merge `go-todo-crud-smoke` 材料入主仓；opt-in E2E TC-067（AC-063 回归）。
- [x] TASK-095 R5 refreeze（`beacon change ... --refreeze-chain`）+ `beacon-eval-qa` AC-061..064。

## Phase M — R6/R7 truth_freeze_gate（AC-063 reconcile + AC-068）

- [x] TASK-096 `harness-checkpoint` + `phase-controller`：`truth_freeze_gate` 序列（clarity + freeze + cutover）；smoke 跳过 sync-materials 但不跳过 freeze（AC-063/068）。
- [x] TASK-097 `phase-prompt`：truth allowed 含 `beacon freeze`；generate entry frozen gate（AC-068）。
- [x] TASK-098 `scope-mode`：`minimal_smoke` → smoke；`isFeatureTruthFrozen` 共享检查（AC-063）。
- [x] TASK-099 测试 TC-068..TC-070 + 更新 TC-065 smoke-truth-exit 断言（AC-068）。
- [x] TASK-100 R7/R8 refreeze（`beacon change ... --refreeze-chain` + cutover + `beacon freeze`）；`refreeze_status=complete`。

## Phase N — R10 v1.6.1 止血 Loop Engineering 对齐（AC-069..AC-071）

- [x] TASK-101 闭合 AC-069：`BEACON_RUN_E2E_GO_TODO=1` worktree+freeze E2E；回归 `go-todo-crud-smoke` 不断链。（TC-071 QA passed；live opt-in 见 `packages/beacon-run/e2e/e2e-go-todo-worktree.test.ts`）
- [x] TASK-102 闭合 AC-070：新增 `docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md`；实现 `beacon-loop spine show`（或 `status --spine`）+ TC-072。
- [x] TASK-103 闭合 AC-071：`stop-when` 外部可执行 gate（harness / `--stop-check-cmd`）；`stop_when_unverified` 路径 + TC-073。
- [x] TASK-104 R10 交付闭环：`implementation-first-reconciliation` refreeze + QA `run-20260612T182801183358` + import-evidence `run-20260612T110636Z-c038` + `beacon release check v1.6.0` 产物归档。

## 边界

- 任务台账不是 implementation completion。
- loop 不得直接修改 `features/*/truth.md`；truth_fill 只经 Beacon CLI。
- 只有通过 `tests.md`、Beacon QA 和 release gate 后，才能将本 feature status 从 `draft` 升为 `frozen`。
