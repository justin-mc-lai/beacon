# Beacon v1.4.8 总览

## 版本状态

- `v1.4.8` 当前主题：`material-gate-hardening-and-human-subskill-atomic-writeback`
- 当前版本状态：`planning_only`
- 本版本线用于冻结 Beacon 物料强 gate 与人类面子 skill 原子材料更新契约

## 版本目标

`v1.4.8` 聚焦一条主线：

> 恢复 Beacon 冻结材料和执行材料的强门禁，让每个人类面 skill 调用都能落到明确材料更新、材料义务、truth reopen、execution host 更新、evidence 更新或只读 route-only，不再允许默认 seed 或静默缺文档通过。

## 当前需求包

- Research
  - `docs/beacon/archive/v1.4.8/research/beacon-v1.4.8-execution-material-rigor-and-version-governance-analysis.md`
  - `docs/beacon/archive/v1.4.8/research/beacon-v1.4.8-human-subskill-material-closure-and-gate-contract.md`
  - `docs/beacon/archive/v1.4.8/research/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
  - `docs/beacon/archive/v1.4.8/research/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- Source Architecture
  - `docs/beacon/archive/v1.4.8/source-architecture/index.md`
  - `docs/beacon/archive/v1.4.8/source-architecture/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- Change
  - `docs/beacon/archive/v1.4.8/change/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
  - `docs/beacon/archive/v1.4.8/change/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- PRD
  - `docs/beacon/archive/v1.4.8/prd/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
  - `docs/beacon/archive/v1.4.8/prd/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- User Story
  - `docs/beacon/archive/v1.4.8/user-story/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
  - `docs/beacon/archive/v1.4.8/user-story/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`
- Test Cases
  - `docs/beacon/archive/v1.4.8/qa/test-cases/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
  - `docs/beacon/archive/v1.4.8/qa/test-cases/markdown-first-freeze-truth-and-minimal-machine-state-contract.md`

## 正式子线

- `beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract`
- `markdown-first-freeze-truth-and-minimal-machine-state-contract`

## 冻结边界

本次冻结包括：

- execution host required surface contract
- branch / service / worktree explicit-fact gate
- human subskill material effect registry
- support finding adoption contract
- artifact update obligation gate
- no silent default seed rule
- implement / QA / release fail-closed consumption

本次冻结不包括：

- 直接实现代码修改
- 自动执行 `implement`
- 自动执行 QA 或 release
- 把 support surface 升级为 truth source 或 gate source

## 下一步

冻结完成后，下一跳是：

- `beacon-implement`

但 implement 必须先实现并验证：

- material closure registry
- execution host validator
- explicit-fact gate
- support adoption obligation writer
- fail-closed preflight / QA / release 消费
