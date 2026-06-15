# Beacon Implementation Tasks Ledger

- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- plan_id: `plan-beacon-loop-goal-closed-loop-orchestrator-r10`
- revision_id: `R10`
- progress: `64/64`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.0/.machine/execution/implementation-plan-beacon-loop-goal-closed-loop-orchestrator.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.0/.machine/execution/implementation-plan-beacon-loop-goal-closed-loop-orchestrator.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。
  - tests=TC-046
[x] `ITASK-002` TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
  - tests=TC-032 | depends_on=ITASK-001
[x] `ITASK-003` TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。
  - tests=TC-044,TC-040 | depends_on=ITASK-002
[x] `ITASK-004` TASK-044 新增 `packages/beacon-loop/src/delivery/state.ts` 与 `delivery-state.json` 读写。
  - tests=TC-035,TC-039,TEST-001,TC-038,TC-042,TC-045,TC-047 | depends_on=ITASK-003
[x] `ITASK-005` TASK-045 实现 planner review subprocess 适配器，写入 `review-artifact.json`（AC-033）。
  - tests=TC-033 | depends_on=ITASK-004
[x] `ITASK-006` TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。
  - tests=TEST-002,TC-034,TC-037 | depends_on=ITASK-005
[x] `ITASK-007` TASK-047 CLI：`--strict-interrupt`（opt-in）、`--ack-intent-drift`；`--ask-on` deprecated。
  - tests=TC-043,TEST-024 | depends_on=ITASK-006
[x] `ITASK-008` TASK-048 测试 TC-031..TC-033、TC-038 骨架。
  - tests=TEST-012,TEST-014,TC-022 | depends_on=ITASK-007
[x] `ITASK-009` TASK-049 实现 `truth_gap_scan`：resolve + review parity 缺口合成。
  - tests=TC-036,TC-041,TEST-030 | depends_on=ITASK-008
[x] `ITASK-010` TASK-050 实现 `truth_fill` 子链编排器，记录 `truth-promotion.json`（beacon gen-* CLI 序列）。
  - tests=TC-034 | depends_on=ITASK-009
[x] `ITASK-011` TASK-051 实现 `truth_freeze_gate`：frozen 前 block `implement_loop`（AC-035）。
  - tests=TC-040,TC-034 | depends_on=ITASK-010
[x] `ITASK-012` TASK-052 `execute-only` 模式：强制 `--feature` + resolve pass。
  - tests=TEST-027 | depends_on=ITASK-011
[x] `ITASK-013` TASK-053 测试 TC-034、TC-035、TC-038b。
  - tests=TEST-015 | depends_on=ITASK-012
[x] `ITASK-014` TASK-054 `--mode delivery` 自动链：import-evidence → beacon qa → beacon release（subprocess + JSON 解析）。
  - tests=TEST-010 | depends_on=ITASK-013
[x] `ITASK-015` TASK-055 输出 payload：`closure_verdict`、`beacon_qa_verdict_ref`、`beacon_release_verdict_ref`。
  - tests=TEST-006 | depends_on=ITASK-014
[x] `ITASK-016` TASK-056 实现 `repair_from_qa`：qa findings 注入 notes，回灌 `implement_loop`。
  - tests=TEST-007 | depends_on=ITASK-015
[x] `ITASK-017` TASK-057 测试 TC-036、TC-037。
  - tests=TEST-017,TEST-018 | depends_on=ITASK-016
[x] `ITASK-018` TASK-058 `resume` 扩展：恢复 `delivery-state`（含 `user_decision_pending`、`repair_from_qa`）。
  - tests=TC-040 | depends_on=ITASK-017
[x] `ITASK-019` TASK-059 非法转移 guard 与 TC-038a..d。
  - tests=TEST-008 | depends_on=ITASK-018
[x] `ITASK-020` TASK-060 scripted E2E `e2e-delivery-closed-loop.mjs`（AC-039 / TC-039）。
  - tests=TEST-020 | depends_on=ITASK-019
[x] `ITASK-021` TASK-061 实现 AC-041：review lane 真并行（`execution_mode=parallel_subagent_review`）。
  - tests=TC-040 | depends_on=ITASK-020
[x] `ITASK-022` TASK-062 更新 `evidence.md`；parent 回归 TC-040、TC-041。
  - tests=TEST-009 | depends_on=ITASK-021
[x] `ITASK-023` TASK-063 `beacon qa run` + release gate 正式验收本 feature（R1 AC-031..039）。
  - tests=TC-031 | depends_on=ITASK-022
[x] `ITASK-024` TASK-064 实现 LLM intent tie-break adapter + `intent-tiebreak.json` 落盘（AC-040）。
  - tests=TEST-013,TEST-023,TEST-026,TEST-028,TEST-029 | depends_on=ITASK-023
[x] `ITASK-025` TASK-065 默认 green-light：`orchestrator` 移除 ambiguous→`user_decision_pending`；hard stop 白名单。
  - tests=TEST-011 | depends_on=ITASK-024
[x] `ITASK-026` TASK-066 CLI：`--strict-interrupt` opt-in；deprecate `--auto-decide deferrals` 作为 ambiguous 门控。
  - depends_on=ITASK-025
[x] `ITASK-027` TASK-067 实现 AC-042：`recommended_route` / Beacon lifecycle auto-route；无 AskUser UI。
  - depends_on=ITASK-026
[x] `ITASK-028` TASK-068 测试 TC-042..TC-044；更新 deferral ledger 运行时校验（rejected D-009..011）。
  - depends_on=ITASK-027
[x] `ITASK-029` TASK-069 R2 implement evidence + `beacon-eval-qa` 正式验收 AC-040..042。
  - depends_on=ITASK-028
[x] `ITASK-030` TASK-070 更新 agent surface / `using-beacon`：gnhf 级 launch、steer、companion 文档（AC-043）。
  - depends_on=ITASK-029
[x] `ITASK-031` TASK-071 `implement_loop` 改为 subprocess `beacon implement run --runner <runner>`；移除裸 `codex exec` 路径（AC-044）。
  - depends_on=ITASK-030
[x] `ITASK-032` TASK-072 写入 `output-schema.json`；adapter strict parse + `--output-schema`（AC-045）。
  - depends_on=ITASK-031
[x] `ITASK-033` TASK-073 gnhf 级 `iteration-prompt` 模板；no-op=false 语义（AC-046）。
  - depends_on=ITASK-032
[x] `ITASK-034` TASK-074 delivery FSM：`implement_no_op_blocked`；禁止 no-op → `qa_pending`（AC-047）。
  - depends_on=ITASK-033
[x] `ITASK-035` TASK-075 frozen harness worker 路由表 + `truth-promotion.json` worker 记录（AC-048）。
  - depends_on=ITASK-034
[x] `ITASK-036` TASK-076 `repair_from_qa` 复用 implement harness worker（AC-049）。
  - depends_on=ITASK-035
[x] `ITASK-037` TASK-077 parent orchestrator 回归 + doctor implement runner 检查（AC-050、AC-052）。
  - depends_on=ITASK-036
[x] `ITASK-038` TASK-078 真 implement runner E2E opt-in（AC-051 / TC-053）。
  - depends_on=ITASK-037
[x] `ITASK-039` TASK-079 测试 TC-045..TC-054；`beacon change … --refreeze-chain` 冻结 R3 truth package。
  - depends_on=ITASK-038
[x] `ITASK-040` TASK-080 fork `packages/gnhf` → `packages/beacon-run`；package/bin 重命名；保留 gnhf 测试基线。
  - depends_on=ITASK-039
[x] `ITASK-041` TASK-081 实现 `beacon-phase-prompt` 模块：注入 Beacon 阶段 + skill boundary digest；落盘 `beacon-phase.json`（AC-054）。
  - depends_on=ITASK-040
[x] `ITASK-042` TASK-082 truth phase：默认 agent iteration 路径；`--truth-bootstrap=fallback` 回退模板链（AC-055、AC-056）。
  - depends_on=ITASK-041
[x] `ITASK-043` TASK-083 迭代间 harness checkpoint + `truth-promotion.json` 扩展 phase 字段（AC-057）。
  - depends_on=ITASK-042
[x] `ITASK-044` TASK-084 `beacon-loop goal` 薄委托 `beacon-run` + deprecated 文档（AC-058）。
  - depends_on=ITASK-043
[x] `ITASK-045` TASK-085 Core：`beacon implement run --output-schema` 与 branch preflight doctor 消息（AC-059）。
  - depends_on=ITASK-044
[x] `ITASK-046` TASK-086 drill E2E `e2e-gum-drill` opt-in（AC-060 / TC-062）。
  - depends_on=ITASK-045
[x] `ITASK-047` TASK-087 R4 refreeze（`beacon change --refreeze-chain` complete，R3→R4）。
  - depends_on=ITASK-046
[x] `ITASK-048` TASK-088 Phase K implement + `beacon-eval-qa` 验收 AC-053..060。
  - depends_on=ITASK-047
[x] `ITASK-049` TASK-089 `beacon-run`：`--worktree --beacon` 时 harness `projectRoot = effectiveCwd`；beacon-loop delegate 文档化（AC-061）。
  - depends_on=ITASK-048
[x] `ITASK-050` TASK-090 测试 TC-063：`worktree-harness-project-root`（mock harness，assert truth-promotion path）。
  - depends_on=ITASK-049
[x] `ITASK-051` TASK-091 `requirement_clarity`：拉丁 marker 词界 + frontmatter/path 豁免；TC-064 fixture `go-todo-crud-smoke`（AC-062）。
  - depends_on=ITASK-050
[x] `ITASK-052` TASK-092 `buildPhaseHarnessArgs` / phase-controller：读 target `scope_mode`；smoke truth exit 跳过 sync-materials（AC-063）。
  - depends_on=ITASK-051
[x] `ITASK-053` TASK-093 `beacon-phase.json`：`phase_promoted` + harness 失败日志（AC-064）。
  - depends_on=ITASK-052
[x] `ITASK-054` TASK-094 merge `go-todo-crud-smoke` 材料入主仓；opt-in E2E TC-067（AC-063 回归）。
  - depends_on=ITASK-053
[x] `ITASK-055` TASK-095 R5 refreeze（`beacon change ... --refreeze-chain`）+ `beacon-eval-qa` AC-061..064。
  - depends_on=ITASK-054
[x] `ITASK-056` TASK-096 `harness-checkpoint` + `phase-controller`：`truth_freeze_gate` 序列（clarity + freeze + cutover）；smoke 跳过 sync-materials 但不跳过 freeze（AC-063/068）。
  - depends_on=ITASK-055
[x] `ITASK-057` TASK-097 `phase-prompt`：truth allowed 含 `beacon freeze`；generate entry frozen gate（AC-068）。
  - depends_on=ITASK-056
[x] `ITASK-058` TASK-098 `scope-mode`：`minimal_smoke` → smoke；`isFeatureTruthFrozen` 共享检查（AC-063）。
  - depends_on=ITASK-057
[x] `ITASK-059` TASK-099 测试 TC-068..TC-070 + 更新 TC-065 smoke-truth-exit 断言（AC-068）。
  - depends_on=ITASK-058
[x] `ITASK-060` TASK-100 R7/R8 refreeze（`beacon change ... --refreeze-chain` + cutover + `beacon freeze`）；`refreeze_status=complete`。
  - depends_on=ITASK-059
[x] `ITASK-061` TASK-101 闭合 AC-069：`BEACON_RUN_E2E_GO_TODO=1` worktree+freeze E2E；回归 `go-todo-crud-smoke` 不断链。（TC-071 QA passed；live opt-in 见 `packages/beacon-run/e2e/e2e-go-todo-worktree.test.ts`）
  - depends_on=ITASK-060
[x] `ITASK-062` TASK-102 闭合 AC-070：新增 `docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md`；实现 `beacon-loop spine show`（或 `status --spine`）+ TC-072。
  - depends_on=ITASK-061
[x] `ITASK-063` TASK-103 闭合 AC-071：`stop-when` 外部可执行 gate（harness / `--stop-check-cmd`）；`stop_when_unverified` 路径 + TC-073。
  - depends_on=ITASK-062
[x] `ITASK-064` TASK-104 R10 refreeze（`beacon change ... --refreeze-chain`）；`beacon-eval-qa` v1.6.1 止血验收。（QA `run-20260612T182801183358` passed 38/38 AC、41/41 scenario；refreeze 待用户确认是否重跑）
  - depends_on=ITASK-063
