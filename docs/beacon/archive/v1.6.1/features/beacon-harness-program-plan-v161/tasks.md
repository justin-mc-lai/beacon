# 任务：Beacon Harness Program Plan v1.6.1

## Phase A — Docs line + truth freeze（已完成）

- [x] TASK-PBP-A01 创建 `docs/beacon/archive/v1.6.1/` SUMMARY、execution、research promoted。evidence: paths exist
- [x] TASK-PBP-A02 编写 `beacon-harness-program-plan-v161` truth/tests/tasks/evidence。evidence: feature package
- [x] TASK-PBP-A03 编写 `program-plan-contract.md` 与 boundaries。evidence: execution docs
- [x] TASK-PBP-A04 运行 TIG + verify-closure + freeze CLI。evidence: baseline sha256:18283011293002dc3af162dc9dde6571e8f306063fecd0193410607c7ba2e572

## Phase B — Feature graph + sea guard

- [x] TASK-PBP-B01 实现 `beacon program validate-graph`。maps: AC-PBP-004
- [x] TASK-PBP-B02 实现海级单湖 block guard。maps: AC-PBP-005

## Phase C — Program freeze gate

- [x] TASK-PBP-C01 实现 `beacon program freeze` + `program-truth-freeze.json`。maps: AC-PBP-007
- [x] TASK-PBP-C02 汇总每湖 TIG 结果。maps: AC-PBP-008

## Phase D — Change closure

- [x] TASK-PBP-D01 change 路径 append `change-intent-log.jsonl`。maps: AC-PBP-013
- [x] TASK-PBP-D02 change 后 mandatory promotion_diff review hook。maps: AC-PBP-014
- [x] TASK-PBP-D03 refreeze + 结构变更重跑 program freeze。maps: AC-PBP-015

## Phase E — Run + planner triad + CLI

- [x] TASK-PBP-E01 `beacon-run --mode program`（help 暴露 mode via prevent-sleep/truth-bootstrap）。maps: AC-PBP-016
- [x] TASK-PBP-E02 新增 `beacon-pln-program` + auto/interactive 子 skill。maps: AC-PBP-017, AC-PBP-023, AC-PBP-026
- [x] TASK-PBP-E03 实现 `beacon plan start` CLI + `--mode`。maps: AC-PBP-024, AC-PBP-027
- [x] TASK-PBP-E04 agent_surface 物化三 skill 到各 host。maps: AC-PBP-023

## Phase F — State tests

- [x] TASK-PBP-F01 `tests/test_program_plan_state_contract.py`。maps: AC-PBP-022

## Phase G — R3 real program FSM + goal resume（AC-PBP-016, AC-PBP-027, AC-PBP-029, AC-PBP-030）

- [ ] TASK-PBP-G01 `beacon-run --mode program` 真实 P0–P6 FSM + `program-run-state.json`。（TC-PBP-016）
- [x] TASK-PBP-G02 更新 operator docs：`beacon-loop goal` 长任务主入口；`plan start` scaffold only。（`execution/long-task-operator-guide.md` / TC-PBP-027）
- [ ] TASK-PBP-G03 goal/plan 共享 resume 状态文件与 resume 路径。（TC-PBP-029）
- [ ] TASK-PBP-G04 与 `beacon-loop-goal-closed-loop-orchestrator-v161` R1 对接：嵌套 delivery + eval supplement 不 gate qa。（TC-PBP-030）
- [x] TASK-PBP-G05 R3 refreeze（`beacon freeze … --version v1.6.1`）+ 路由 `beacon-gen-implement`。
