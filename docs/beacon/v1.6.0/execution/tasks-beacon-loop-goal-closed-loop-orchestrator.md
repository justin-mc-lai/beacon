# Beacon Implementation Tasks Ledger

- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- plan_id: `plan-beacon-loop-goal-closed-loop-orchestrator-r3`
- revision_id: `R3`
- progress: `2/39`
- status: `planned`
- next_task: `ITASK-002` TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.0/.machine/execution/implementation-plan-beacon-loop-goal-closed-loop-orchestrator.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.0/.machine/execution/implementation-plan-beacon-loop-goal-closed-loop-orchestrator.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。
  - tests=TC-034,TEST-008,TC-040,TEST-010,TEST-029,TEST-009
[ ] `ITASK-002` TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
  - tests=TEST-013,TC-040,TC-022,TC-041 | depends_on=ITASK-001 | next
[ ] `ITASK-003` TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。
  - tests=TC-040 | depends_on=ITASK-002
[x] `ITASK-004` TASK-044 新增 `packages/beacon-loop/src/delivery/state.ts` 与 `delivery-state.json` 读写。
  - tests=TC-034 | depends_on=ITASK-003
[ ] `ITASK-005` TASK-045 实现 planner review subprocess 适配器，写入 `review-artifact.json`（AC-033）。
  - tests=TEST-014 | depends_on=ITASK-004
[ ] `ITASK-006` TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。
  - tests=TEST-001,TEST-002 | depends_on=ITASK-005
[ ] `ITASK-007` TASK-047 CLI：`--strict-interrupt`（opt-in）、`--ack-intent-drift`；`--ask-on` deprecated。
  - tests=TEST-024 | depends_on=ITASK-006
[ ] `ITASK-008` TASK-048 测试 TC-031..TC-033、TC-038 骨架。
  - tests=TEST-012 | depends_on=ITASK-007
[ ] `ITASK-009` TASK-049 实现 `truth_gap_scan`：resolve + review parity 缺口合成。
  - tests=TEST-006 | depends_on=ITASK-008
[ ] `ITASK-010` TASK-050 实现 `truth_fill` 子链编排器，记录 `truth-promotion.json`（beacon gen-* CLI 序列）。
  - tests=TEST-026 | depends_on=ITASK-009
[ ] `ITASK-011` TASK-051 实现 `truth_freeze_gate`：frozen 前 block `implement_loop`（AC-035）。
  - tests=TEST-028,TEST-015,TEST-017,TEST-018,TEST-020,TEST-023,TEST-027 | depends_on=ITASK-010
[ ] `ITASK-012` TASK-052 `execute-only` 模式：强制 `--feature` + resolve pass。
  - tests=TEST-007 | depends_on=ITASK-011
[ ] `ITASK-013` TASK-053 测试 TC-034、TC-035、TC-038b。
  - tests=TEST-011 | depends_on=ITASK-012
[ ] `ITASK-014` TASK-054 `--mode delivery` 自动链：import-evidence → beacon qa → beacon release（subprocess + JSON 解析）。
  - depends_on=ITASK-013
[ ] `ITASK-015` TASK-055 输出 payload：`closure_verdict`、`beacon_qa_verdict_ref`、`beacon_release_verdict_ref`。
  - depends_on=ITASK-014
[ ] `ITASK-016` TASK-056 实现 `repair_from_qa`：qa findings 注入 notes，回灌 `implement_loop`。
  - depends_on=ITASK-015
[ ] `ITASK-017` TASK-057 测试 TC-036、TC-037。
  - depends_on=ITASK-016
[ ] `ITASK-018` TASK-058 `resume` 扩展：恢复 `delivery-state`（含 `user_decision_pending`、`repair_from_qa`）。
  - depends_on=ITASK-017
[ ] `ITASK-019` TASK-059 非法转移 guard 与 TC-038a..d。
  - depends_on=ITASK-018
[ ] `ITASK-020` TASK-060 scripted E2E `e2e-delivery-closed-loop.mjs`（AC-039 / TC-039）。
  - depends_on=ITASK-019
[ ] `ITASK-021` TASK-061 实现 AC-041：review lane 真并行（`execution_mode=parallel_subagent_review`）。
  - depends_on=ITASK-020
[ ] `ITASK-022` TASK-062 更新 `evidence.md`；parent 回归 TC-040、TC-041。
  - depends_on=ITASK-021
[ ] `ITASK-023` TASK-063 `beacon qa run` + release gate 正式验收本 feature（R1 AC-031..039）。
  - depends_on=ITASK-022
[ ] `ITASK-024` TASK-064 实现 LLM intent tie-break adapter + `intent-tiebreak.json` 落盘（AC-040）。
  - depends_on=ITASK-023
[ ] `ITASK-025` TASK-065 默认 green-light：`orchestrator` 移除 ambiguous→`user_decision_pending`；hard stop 白名单。
  - depends_on=ITASK-024
[ ] `ITASK-026` TASK-066 CLI：`--strict-interrupt` opt-in；deprecate `--auto-decide deferrals` 作为 ambiguous 门控。
  - depends_on=ITASK-025
[ ] `ITASK-027` TASK-067 实现 AC-042：`recommended_route` / Beacon lifecycle auto-route；无 AskUser UI。
  - depends_on=ITASK-026
[ ] `ITASK-028` TASK-068 测试 TC-042..TC-044；更新 deferral ledger 运行时校验（rejected D-009..011）。
  - depends_on=ITASK-027
[ ] `ITASK-029` TASK-069 R2 implement evidence + `beacon-eval-qa` 正式验收 AC-040..042。
  - depends_on=ITASK-028
[ ] `ITASK-030` TASK-070 更新 agent surface / `using-beacon`：gnhf 级 launch、steer、companion 文档（AC-043）。
  - depends_on=ITASK-029
[ ] `ITASK-031` TASK-071 `implement_loop` 改为 subprocess `beacon implement run --runner <runner>`；移除裸 `codex exec` 路径（AC-044）。
  - depends_on=ITASK-030
[ ] `ITASK-032` TASK-072 写入 `output-schema.json`；adapter strict parse + `--output-schema`（AC-045）。
  - depends_on=ITASK-031
[ ] `ITASK-033` TASK-073 gnhf 级 `iteration-prompt` 模板；no-op=false 语义（AC-046）。
  - depends_on=ITASK-032
[ ] `ITASK-034` TASK-074 delivery FSM：`implement_no_op_blocked`；禁止 no-op → `qa_pending`（AC-047）。
  - depends_on=ITASK-033
[ ] `ITASK-035` TASK-075 frozen harness worker 路由表 + `truth-promotion.json` worker 记录（AC-048）。
  - depends_on=ITASK-034
[ ] `ITASK-036` TASK-076 `repair_from_qa` 复用 implement harness worker（AC-049）。
  - depends_on=ITASK-035
[ ] `ITASK-037` TASK-077 parent orchestrator 回归 + doctor implement runner 检查（AC-050、AC-052）。
  - depends_on=ITASK-036
[ ] `ITASK-038` TASK-078 真 implement runner E2E opt-in（AC-051 / TC-053）。
  - depends_on=ITASK-037
[ ] `ITASK-039` TASK-079 测试 TC-045..TC-054；`beacon change … --refreeze-chain` 冻结 R3 truth package。
  - depends_on=ITASK-038
