# Beacon v1.3.11 总览

## 版本状态

- `v1.3.11` 当前主题已经从 `v1.3.10` 的 metadata / prototype 闭环，正式推进到 `orchestration runtime + PRD freeze anti-drift`。
- 当前版本包含两条互相咬合的需求线：
  - `Beacon orchestration runtime and long-running execution governance`
  - `PRD freeze anti-drift and machine-mirror reconciliation`
- 当前版本材料状态：`requirement-frozen-and-implementation-in-progress`

## 版本目标

`v1.3.11` 当前聚焦解决两组执行治理缺口：

1. 长任务编排缺口
   - Beacon 仍擅长冻结 truth，但还缺少 run-oriented orchestration runtime
   - `team / ralph / real-project-validation / implement / qa / release` 还没有统一 `work item / run / scheduler / runtime board`
2. PRD freeze anti-drift 缺口
   - `PRD markdown` 手工修订后，machine mirror 可能静默滞后
   - `validate` 只看 markdown contract，`audit` 仍只做 legacy 对比
   - transaction 历史缺少 `latest / supersedes` 语义，导致 change-loop 难以稳定判断当前 truth

## 当前需求包

- PRD
  - `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
  - `docs/beacon/v1.3.11/prd/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- Change
  - `docs/beacon/v1.3.11/change/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- User Story
  - `docs/beacon/v1.3.11/user-story/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
  - `docs/beacon/v1.3.11/user-story/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- Test Cases
  - `docs/beacon/v1.3.11/qa/test-cases/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
  - `docs/beacon/v1.3.11/qa/test-cases/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`

## 正式子线

- `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- `beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation`

## 当前冻结判断

- orchestration runtime 主线：`prd-frozen / story-frozen / test-case-seeded / runtime-contract-backed`
- freeze anti-drift 变更线：`change-frozen / story-frozen / test-case-backed / source-implemented`
- 当前版本结论：`还不能进入 release-ready，但版本级 freeze 与关键实现闭环已建立`

## 当前收口结论

- `v1.3.11` 已经正式固定三层架构边界：
  - Requirement Truth Layer
  - Orchestration Runtime Layer
  - Delivery Closure Layer
- `PRD freeze anti-drift` 已经从口头结论升级为正式 change item
- `user-story -> test-case` 已经为两条需求线都补齐版本级 requirement package
- `prd reconcile / extended audit / latest pointer / stale mirror detection` 已进入源码并被测试覆盖
- 当前剩余工作重点不再是 brainstorming，而是把 orchestration runtime 的 scheduler / workspace isolation / repair-resume 继续推到后续子版本实现

## 关键验收锚点

- `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- `docs/beacon/v1.3.11/change/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- `docs/beacon/v1.3.11/user-story/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- `docs/beacon/v1.3.11/qa/test-cases/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- `docs/beacon/v1.3.11/user-story/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- `docs/beacon/v1.3.11/qa/test-cases/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- `docs/beacon/v1.3.11/.machine/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.canonical.json`
- `docs/beacon/v1.3.11/.machine/user-story/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.json`
- `docs/beacon/v1.3.11/.machine/qa/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.ac-test-matrix.json`
- `docs/beacon/v1.3.11/.machine/execution/change-impact.json`
- `beacon/utils/project_skills.py`
- `beacon/commands/prd.py`

## 版本主题图

```text
requirement truth strong
-> orchestration runtime missing
-> work item / run / scheduler / runtime board
-> PRD revise after freeze exposes stale machine mirror
-> anti-drift change loop formalized
-> reconcile / extended audit / latest pointer / stale detection / doctor fallback
-> version-level freeze package convergence
```
