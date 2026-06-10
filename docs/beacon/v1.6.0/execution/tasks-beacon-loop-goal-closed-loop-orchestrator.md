# Beacon Implementation Tasks Ledger

- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- plan_id: `plan-beacon-loop-goal-closed-loop-orchestrator-r1`
- revision_id: `R1`
- progress: `23/23`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.0/.machine/execution/implementation-plan-beacon-loop-goal-closed-loop-orchestrator.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.0/.machine/execution/implementation-plan-beacon-loop-goal-closed-loop-orchestrator.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` TASK-041 新增 `packages/beacon-loop/src/intent/capture.ts` 与 `classify.ts`，落盘 `intent-capture.json` / `intent-contract.json`。
  - tests=TC-034
[x] `ITASK-002` TASK-042 实现 `beacon-loop-intent-v1` 规则表与 `rules_hash` 计算（AC-032）。
  - tests=TEST-008 | depends_on=ITASK-001
[x] `ITASK-003` TASK-043 扩展 `startGoal()`：utterance 与 feature slug 解耦；`--feature` 显式化；禁止仅 `slugify(utterance)`。
  - tests=TC-040 | depends_on=ITASK-002
[x] `ITASK-004` TASK-044 新增 `packages/beacon-loop/src/delivery/state.ts` 与 `delivery-state.json` 读写。
  - tests=TC-034 | depends_on=ITASK-003
[x] `ITASK-005` TASK-045 实现 planner review subprocess 适配器，写入 `review-artifact.json`（AC-033）。
  - tests=TEST-009 | depends_on=ITASK-004
[x] `ITASK-006` TASK-046 CLI：`--mode delivery|execute-only|intent-only|review-only`（默认 `delivery`）。
  - tests=TEST-001,TEST-002 | depends_on=ITASK-005
[x] `ITASK-007` TASK-047 CLI：`--ask-on`、`--auto-decide deferrals`、`--ack-intent-drift`。
  - tests=TEST-006 | depends_on=ITASK-006
[x] `ITASK-008` TASK-048 测试 TC-031..TC-033、TC-038 骨架。
  - tests=TEST-007,TEST-014 | depends_on=ITASK-007
[x] `ITASK-009` TASK-049 实现 `truth_gap_scan`：resolve + review parity 缺口合成。
  - tests=TEST-010 | depends_on=ITASK-008
[x] `ITASK-010` TASK-050 实现 `truth_fill` 子链编排器，记录 `truth-promotion.json`（beacon gen-* CLI 序列）。
  - tests=TEST-011 | depends_on=ITASK-009
[x] `ITASK-011` TASK-051 实现 `truth_freeze_gate`：frozen 前 block `implement_loop`（AC-035）。
  - tests=TEST-012,TEST-013,TEST-015 | depends_on=ITASK-010
[x] `ITASK-012` TASK-052 `execute-only` 模式：强制 `--feature` + resolve pass。
  - depends_on=ITASK-011
[x] `ITASK-013` TASK-053 测试 TC-034、TC-035、TC-038b。
  - depends_on=ITASK-012
[x] `ITASK-014` TASK-054 `--mode delivery` 自动链：import-evidence → beacon qa → beacon release（subprocess + JSON 解析）。
  - depends_on=ITASK-013
[x] `ITASK-015` TASK-055 输出 payload：`closure_verdict`、`beacon_qa_verdict_ref`、`beacon_release_verdict_ref`。
  - depends_on=ITASK-014
[x] `ITASK-016` TASK-056 实现 `repair_from_qa`：qa findings 注入 notes，回灌 `implement_loop`。
  - depends_on=ITASK-015
[x] `ITASK-017` TASK-057 测试 TC-036、TC-037。
  - depends_on=ITASK-016
[x] `ITASK-018` TASK-058 `resume` 扩展：恢复 `delivery-state`（含 `user_decision_pending`、`repair_from_qa`）。
  - depends_on=ITASK-017
[x] `ITASK-019` TASK-059 非法转移 guard 与 TC-038a..d。
  - depends_on=ITASK-018
[x] `ITASK-020` TASK-060 scripted E2E `e2e-delivery-closed-loop.mjs`（AC-039 / TC-039）。
  - depends_on=ITASK-019
[x] `ITASK-021` TASK-061 defer D-009: review lane 并行化评估与实现。
  - depends_on=ITASK-020
[x] `ITASK-022` TASK-062 更新 `evidence.md`；parent 回归 TC-040、TC-041。
  - depends_on=ITASK-021
[x] `ITASK-023` TASK-063 `beacon qa run` + release gate 正式验收本 feature。
  - depends_on=ITASK-022
