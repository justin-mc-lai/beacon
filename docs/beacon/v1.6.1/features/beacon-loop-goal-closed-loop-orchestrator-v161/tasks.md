# 任务：Beacon Loop Goal Closed-Loop Orchestrator v1.6.1

## Phase A — 统一 goal + scope classify（AC-072）

- [x] TASK-LOOP-A01 `beacon-loop goal` 薄委托 + `--mode program|delivery` + `--program` flags。（TC-LOOP-072）
- [x] TASK-LOOP-A02 湖/海 classifier + UD-007 一次 MCQ 落盘。（TC-LOOP-072）
- [x] TASK-LOOP-A03 operator docs：`goal` 为长任务主入口；`plan start` scaffold only。（`execution/long-task-operator-guide.md`）

## Phase B — program 外层 FSM（AC-073）

- [x] TASK-LOOP-B01 `beacon-run --mode program` P0–P6 + `program-run-state.json`。（TC-LOOP-073）
- [x] TASK-LOOP-B02 P4 ack 门控 per-lake delivery spawn。（TC-LOOP-073）

## Phase C — eval supplement（AC-074）

- [x] TASK-LOOP-C01 `--eval-matrix` / `--eval-scorecard` flags + run-dir artifacts。（TC-LOOP-074）
- [x] TASK-LOOP-C02 `spine show` eval refs；不 gate qa/release。（TC-LOOP-074）

## Phase D — 海级 E2E（AC-075）

- [x] TASK-LOOP-D01 `BEACON_RUN_E2E_PROGRAM=1` fixture。（TC-LOOP-075）

## Phase E — Change closure

- [x] TASK-LOOP-E01 R1 refreeze（`beacon freeze … --version v1.6.1`）+ 路由 `beacon-gen-implement`。

## 边界

- 不得修改 v1.6.0 upstream frozen truth。
- 任务台账不是 implementation completion。
